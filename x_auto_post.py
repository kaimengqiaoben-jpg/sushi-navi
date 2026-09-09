#!/usr/bin/env python3
"""
X（Twitter）自動投稿スクリプト
Playwrightでブラウザを操作してXに投稿します。

使い方:
  python x_auto_post.py --save-session  # 初回: 手動でログインしてセッション保存
  python x_auto_post.py                 # キューの先頭1本を投稿
  python x_auto_post.py --all           # キュー全件を投稿
  python x_auto_post.py --file 01       # 特定ファイルを投稿
  python x_auto_post.py --init-queue    # キュー初期化（articles/*.htmlから生成）

【重要】投稿処理（post_to_x）のセレクタはまだ実際のX画面で検証していません。
note.comの自動投稿を作った際、UIの実物を見ないままセレクタを書いて何度も
外したという経緯があるため、本番投稿前に必ず --file で1件だけ試し、
note_debug*.png のスクリーンショットで動作を確認してください。
"""

import os
import sys
import json
import time
import argparse
import re
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# ===== 設定 =====
BLOG_DIR      = Path(__file__).parent
ARTICLES_DIR  = BLOG_DIR / "articles"
QUEUE_FILE    = BLOG_DIR / "x_post_queue.json"
LOG_FILE      = BLOG_DIR / "x_post_log.txt"
SESSION_FILE  = BLOG_DIR / "x_session.json"

BLOG_BASE_URL = "https://sushi-blog-five.vercel.app"

# 投稿間隔（秒）: 連続投稿でBANされないように
POST_INTERVAL = 90

X_HOME_URL    = "https://x.com/home"
X_LOGIN_URL   = "https://x.com/login"
X_COMPOSE_URL = "https://x.com/compose/post"

# ===== ハッシュタグ =====
COMMON_HASHTAGS = ["寿司職人", "転職", "寿司スクール"]


def log(msg: str):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def load_queue() -> list:
    if not QUEUE_FILE.exists():
        return []
    with open(QUEUE_FILE, encoding="utf-8") as f:
        return json.load(f)


def save_queue(queue: list):
    with open(QUEUE_FILE, "w", encoding="utf-8") as f:
        json.dump(queue, f, ensure_ascii=False, indent=2)


def _extract_title(html_path: Path) -> str:
    text = html_path.read_text(encoding="utf-8")
    m = re.search(r"<title>(.*?)</title>", text, re.DOTALL)
    if not m:
        return html_path.stem
    title = m.group(1)
    # 「｜寿司職人ナビ」等のサイト名部分を除去
    title = title.split("｜")[0].split("|")[0].strip()
    return title


def init_queue():
    """articles/ 配下のブログ記事を走査してキューを初期化"""
    html_files = sorted(ARTICLES_DIR.glob("*.html"))

    queue = []
    for f in html_files:
        queue.append({
            "type": "blog",
            "file": f.name,
            "title": _extract_title(f),
            "url": f"{BLOG_BASE_URL}/articles/{f.name}",
            "status": "pending",
            "posted_url": None,
        })

    save_queue(queue)
    log(f"キュー初期化: {len(queue)}件（ブログ記事のみ。note記事は公開URL確定後に追加予定）")
    return queue


def build_tweet_text(item: dict) -> str:
    hashtags = " ".join(f"#{h}" for h in COMMON_HASHTAGS)
    return f"{item['title']}\n\n{item['url']}\n\n{hashtags}"


def save_session(context, path: Path):
    """ブラウザのセッション（Cookie等）を保存"""
    storage = context.storage_state()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(storage, f, ensure_ascii=False, indent=2)
    log(f"セッション保存完了: {path}")


def do_save_session():
    """手動ログインしてセッションを保存するモード"""
    log("=== セッション保存モード ===")
    log("ブラウザが開きます。手動でXにログインしてください。")
    log("ログインが完了すると自動的に検知してセッションを保存します（キー操作は不要です）。")
    log("最大10分待ちます。")

    with sync_playwright() as p:
        try:
            # Playwright同梱のChromiumで画面が表示されない環境があるため、
            # 端末に実際にインストールされているChromeを優先的に使う。
            browser = p.chromium.launch(headless=False, channel="chrome", args=["--start-maximized"])
        except Exception as e:
            log(f"  Chromeチャネルの起動に失敗（同梱Chromiumにフォールバック）: {e}")
            browser = p.chromium.launch(headless=False, args=["--start-maximized"])
        context = browser.new_context(no_viewport=True)
        page = context.new_page()

        page.goto(X_LOGIN_URL, wait_until="networkidle")
        page.bring_to_front()

        # ログイン完了を自動検知する。外部ログイン等を経由すると認証未完了の
        # 一瞬をURLだけでは誤検知しうるため、保護ページ（ホーム）への実アクセスで
        # 最終確認してから保存する（note_auto_post.pyと同じ方式）。
        logged_in = False
        for _ in range(300):
            time.sleep(2)
            try:
                url = page.url
            except Exception:
                continue
            if "x.com" not in url and "twitter.com" not in url:
                continue
            if "login" in url or "flow" in url:
                continue

            try:
                page.goto(X_HOME_URL, wait_until="networkidle")
                time.sleep(1.5)
            except Exception:
                continue
            if "login" not in page.url:
                logged_in = True
                break
            page.goto(X_LOGIN_URL, wait_until="networkidle")

        if logged_in:
            save_session(context, SESSION_FILE)
            log("セッション保存しました。次回から自動投稿できます。")
        else:
            log(f"タイムアウトしました（現在のURL: {page.url}）。ログインを確認してもう一度お試しください。")

        browser.close()


def _click_first_visible(page, selectors: list, label: str, timeout=3000) -> bool:
    """セレクタリストから最初に見つかったボタンをクリック"""
    for selector in selectors:
        try:
            btn = page.locator(selector).first
            if btn.is_visible(timeout=timeout):
                btn.click()
                return True
        except Exception:
            continue
    log(f"  {label}が見つからず（スキップ）")
    return False


def post_to_x(page, item: dict) -> str:
    """Xに1件投稿して投稿後のURLを返す

    【未検証】ここのセレクタはX公式Webアプリの一般的なdata-testid命名規則
    （tweetTextarea_0 / tweetButtonInline 等）を基に書いたもので、実際の
    画面で動作確認していない。初回実行時は必ず1件だけ試し、
    x_debug*.png を見て調整すること。
    """
    text = build_tweet_text(item)
    log(f"  投稿開始: {item['title']}")

    page.goto(X_COMPOSE_URL, wait_until="networkidle")
    time.sleep(2)
    page.screenshot(path=str(BLOG_DIR / "x_debug.png"))
    log(f"  現在のURL: {page.url}")

    # ===== 本文入力 =====
    body_area = None
    for selector in [
        '[data-testid="tweetTextarea_0"]',
        'div[role="textbox"][aria-label*="ポスト"]',
        'div[role="textbox"][aria-label*="post"]',
        'div[role="textbox"]',
    ]:
        try:
            el = page.locator(selector).first
            if el.is_visible(timeout=3000):
                body_area = el
                break
        except Exception:
            continue

    if body_area is None:
        log("  本文入力エリアが見つかりません。スキップします。")
        page.screenshot(path=str(BLOG_DIR / "x_debug_textarea_fail.png"))
        return ""

    body_area.click()
    time.sleep(0.3)
    page.keyboard.type(text, delay=15)
    time.sleep(1)

    # ===== 投稿ボタン =====
    posted = _click_first_visible(page, [
        '[data-testid="tweetButtonInline"]',
        '[data-testid="tweetButton"]',
        'button:has-text("ポストする")',
        'button:has-text("Post")',
    ], "投稿ボタン", timeout=5000)

    if not posted:
        log("  投稿ボタンが見つかりませんでした")
        page.screenshot(path=str(BLOG_DIR / "x_debug_post_fail.png"))
        return ""

    time.sleep(3)
    current_url = page.url
    log(f"  投稿完了: {current_url}")
    return current_url


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true", help="全件投稿")
    parser.add_argument("--file", type=str, help="ファイル名の一部（例: career-30s）")
    parser.add_argument("--init-queue", action="store_true", help="キュー初期化")
    parser.add_argument("--save-session", action="store_true", help="手動ログインしてセッション保存")
    args = parser.parse_args()

    if args.save_session:
        do_save_session()
        return

    if args.init_queue:
        init_queue()
        return

    if not SESSION_FILE.exists():
        print("セッションが保存されていません。先に以下を実行してください:")
        print("  python x_auto_post.py --save-session")
        sys.exit(1)

    queue = load_queue()
    if not queue:
        queue = init_queue()

    if args.file:
        targets = [
            item for item in queue
            if args.file in item["file"] and item["status"] == "pending"
        ]
    elif args.all:
        targets = [item for item in queue if item["status"] == "pending"]
    else:
        pending = [item for item in queue if item["status"] == "pending"]
        targets = pending[:1]

    if not targets:
        log("投稿対象がありません（全件投稿済みか、キューが空です）")
        return

    log(f"投稿対象: {len(targets)}件")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, channel="chrome")
        context = browser.new_context(storage_state=str(SESSION_FILE))
        page = context.new_page()

        page.goto(X_HOME_URL, wait_until="networkidle")
        time.sleep(2)
        if "login" in page.url:
            log("セッション切れです。--save-session で再ログインしてください")
            browser.close()
            sys.exit(1)
        log("セッション確認OK")

        for i, item in enumerate(targets):
            url = post_to_x(page, item)

            for q in queue:
                if q["file"] == item["file"]:
                    q["status"] = "posted" if url else "error"
                    q["posted_url"] = url
                    break
            save_queue(queue)

            if i < len(targets) - 1:
                log(f"  次の投稿まで{POST_INTERVAL}秒待機...")
                time.sleep(POST_INTERVAL)

        browser.close()

    log("=== 全投稿完了 ===")
    posted = [q for q in queue if q["status"] == "posted"]
    log(f"投稿済み: {len(posted)}件")


if __name__ == "__main__":
    main()
