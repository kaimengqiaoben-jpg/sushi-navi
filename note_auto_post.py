#!/usr/bin/env python3
"""
note.com 自動投稿スクリプト
Playwrightでブラウザを操作してnoteに記事を自動投稿します。

使い方:
  python note_auto_post.py --save-session  # 初回: 手動でログインしてセッション保存
  python note_auto_post.py                 # キューの先頭1本を投稿
  python note_auto_post.py --all           # キュー全件を投稿
  python note_auto_post.py --file 01       # 特定ファイルを投稿
  python note_auto_post.py --init-queue    # キュー初期化
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# ===== 設定 =====
BLOG_DIR      = Path(__file__).parent
NOTE_200_DIR  = BLOG_DIR / "note-articles" / "200yen"
QUEUE_FILE    = BLOG_DIR / "note_post_queue.json"
LOG_FILE      = BLOG_DIR / "note_post_log.txt"
SESSION_FILE  = BLOG_DIR / "note_session.json"

# 投稿間隔（秒）: 連続投稿でBANされないように
POST_INTERVAL = 60

# noteのURL
NOTE_NEW_URL  = "https://note.com/notes/new"
NOTE_LOGIN_URL = "https://note.com/login"

# ===== ハッシュタグ =====
COMMON_HASHTAGS = [
    "寿司職人", "転職", "寿司スクール", "未経験転職", "飲食業転職", "料理人"
]


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


def init_queue():
    """200円記事フォルダを走査してキューを初期化"""
    md_files = sorted([
        f for f in NOTE_200_DIR.glob("*.md")
        if not f.name.startswith("note_")  # ガイドファイルは除外
    ])

    queue = []
    for f in md_files:
        queue.append({
            "file": f.name,
            "status": "pending",
            "posted_url": None
        })

    save_queue(queue)
    log(f"キュー初期化: {len(queue)}件")
    return queue


def parse_markdown(filepath: Path) -> dict:
    """マークダウンからタイトル・本文・有料ラインを取得"""
    text = filepath.read_text(encoding="utf-8")
    lines = text.strip().split("\n")

    # タイトル（# で始まる行）
    title = ""
    for line in lines:
        if line.startswith("# "):
            title = line.lstrip("# ").strip()
            # 「｜200円」を除去してnoteのタイトルにする
            title = title.replace("｜200円", "").strip()
            break

    # 「※この記事は200円です。」の行を除去
    body_lines = [l for l in lines if "※この記事は200円" not in l]
    # タイトル行を除去（noteのタイトルは別に設定）
    body_lines = [l for l in body_lines if not l.startswith("# ")]
    body = "\n".join(body_lines).strip()

    # 有料ラインを「---」で分割
    if "\n---\n" in body:
        free_part, paid_part = body.split("\n---\n", 1)
    else:
        free_part = ""
        paid_part = body

    return {
        "title": title,
        "free_body": free_part.strip(),
        "paid_body": paid_part.strip(),
        "price": 200,
        "hashtags": COMMON_HASHTAGS,
    }


def save_session(context, path: Path):
    """ブラウザのセッション（Cookie等）を保存"""
    storage = context.storage_state()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(storage, f, ensure_ascii=False, indent=2)
    log(f"セッション保存完了: {path}")


def do_save_session():
    """手動ログインしてセッションを保存するモード"""
    log("=== セッション保存モード ===")
    log("ブラウザが開きます。手動でnote.comにログインしてください。")
    log("ログインが完了すると自動的に検知してセッションを保存します（キー操作は不要です）。")
    log("最大10分待ちます。")

    with sync_playwright() as p:
        # 以前は端末インストール済みChrome（channel="chrome"）を優先していたが、
        # この環境では実Chromeがnote.comへの遷移でハング（commitすら30秒でタイムアウト）
        # したため、確実に遷移できるPlaywright同梱Chromiumを使う。
        browser = p.chromium.launch(headless=False, args=["--start-maximized"])
        context = browser.new_context(no_viewport=True)
        page = context.new_page()

        page.goto(NOTE_LOGIN_URL, wait_until="domcontentloaded", timeout=60000)
        page.bring_to_front()

        # ログイン完了（/login から離れる）を自動検知する。Enterキー操作は不要。
        # Google等の外部ログインを経由する場合、コールバック処理中に一瞬
        # /login を含まないnote.comのURLになる瞬間があり、そこで即座に
        # セッション保存すると認証未完了のCookieを保存してしまう。
        # そのため、URL条件が満たされてもすぐには保存せず、保護ページに
        # 実際にアクセスできるかで最終確認してから保存する。
        logged_in = False
        for _ in range(300):
            time.sleep(2)
            try:
                url = page.url
            except Exception:
                continue
            if "note.com" not in url or "login" in url:
                continue

            # 認証が本当に完了しているか、保護ページへのアクセスで確認する
            try:
                page.goto("https://note.com/notes?tab=draft", wait_until="domcontentloaded", timeout=60000)
                time.sleep(1.5)
            except Exception:
                continue
            if "login" not in page.url:
                logged_in = True
                break
            # まだ未認証だった場合はログインページに戻して待機を続ける
            page.goto(NOTE_LOGIN_URL, wait_until="domcontentloaded", timeout=60000)

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


def post_to_note(page, article: dict) -> str:
    """noteに1記事を投稿して公開URLを返す"""

    log(f"  投稿開始: {article['title']}")

    # 新規記事ページ（直前の記事の公開後リダイレクトと稀に競合するため1回だけ再試行する）
    try:
        page.goto(NOTE_NEW_URL, wait_until="domcontentloaded", timeout=60000)
    except Exception:
        time.sleep(3)
        page.goto(NOTE_NEW_URL, wait_until="domcontentloaded", timeout=60000)
    time.sleep(3)

    # スクリーンショット保存（デバッグ用）
    page.screenshot(path=str(BLOG_DIR / "note_debug.png"))
    log(f"  現在のURL: {page.url}")

    # ===== タイトル入力 =====
    title_ok = False
    for selector in [
        '[placeholder="記事タイトル"]',
        'h1[contenteditable="true"]',
        'div[contenteditable="true"][class*="title"]',
        'textarea[placeholder*="タイトル"]',
        'input[placeholder*="タイトル"]',
        '.title-input',
        '[data-cy="title"]',
        '[contenteditable][class*="title"]',
    ]:
        try:
            el = page.locator(selector).first
            if el.is_visible(timeout=3000):
                el.click()
                el.fill(article["title"])
                time.sleep(0.5)
                title_ok = True
                log(f"  タイトル入力OK（{selector}）")
                break
        except Exception:
            continue

    if not title_ok:
        log("  タイトル入力エリアが見つかりません。スキップします。")
        page.screenshot(path=str(BLOG_DIR / "note_debug_title_fail.png"))
        return ""

    time.sleep(1)

    # ===== 本文入力（無料部分）=====
    body_area = None
    for selector in ['.ProseMirror', '[contenteditable="true"]', '.note-editor', '[role="textbox"]']:
        try:
            el = page.locator(selector).first
            if el.is_visible(timeout=3000):
                body_area = el
                break
        except Exception:
            continue

    if body_area is None:
        log("  本文エリアが見つかりません。スキップします。")
        return ""

    body_area.click()
    time.sleep(0.5)

    if article["free_body"]:
        _type_markdown(page, body_area, article["free_body"])

    # ===== 有料ライン挿入 =====
    # 「有料エリア指定」はブロック追加メニュー（＋/メニューを開く）の中にある。
    # クリック後は現在の空段落がpaywall-line自体に置き換わるため、
    # そのすぐ下をクリックして新しい段落にカーソルを移さないと
    # 有料部分の文章が有料ラインより前に入ってしまう。
    paid_line_ok = False
    try:
        page.keyboard.press("Enter")
        time.sleep(0.5)
        menu_opened = _click_first_visible(page, [
            'button[aria-label="メニューを開く"]',
        ], "＋ブロック追加メニュー", timeout=3000)
        if menu_opened:
            time.sleep(0.6)
            paid_line_ok = _click_first_visible(page, [
                'button:has-text("有料エリア指定")',
            ], "有料エリア指定メニュー項目", timeout=2000)
        if paid_line_ok:
            time.sleep(1)
            pw_box = page.locator('paywall-line').first.bounding_box()
            if pw_box:
                page.mouse.click(pw_box['x'] + pw_box['width'] / 2, pw_box['y'] + pw_box['height'] + 30)
                time.sleep(0.5)
            else:
                paid_line_ok = False
    except Exception as e:
        log(f"  有料ライン挿入エラー（スキップ）: {e}")

    if not paid_line_ok:
        log("  有料ラインが設定できませんでした（本文として続けて入力します）")

    # ===== 有料部分を入力 =====
    _type_markdown(page, body_area, article["paid_body"])
    time.sleep(1)

    # ===== 公開設定ボタン =====
    opened = _click_first_visible(page, [
        'button:has-text("公開に進む")',
        'button:has-text("公開設定")',
        'button:has-text("公開する")',
        'button:has-text("投稿設定")',
        '[data-cy="publish-button"]',
        'button[class*="publish"]',
    ], "公開設定ボタン", timeout=5000)

    if not opened:
        log("  公開設定が開けませんでした。スキップします。")
        return ""
    time.sleep(2)

    # ===== 有料設定（価格）=====
    try:
        price_el = page.locator('text=価格').first.locator('xpath=following::input[1]')
        if price_el.is_visible(timeout=2000):
            price_el.fill(str(article["price"]))
            time.sleep(0.5)
            log(f"  価格{article['price']}円設定OK")
    except Exception:
        log("  価格入力フィールドが見つからず")

    # ===== ハッシュタグ =====
    try:
        for sel in ['input[placeholder*="タグ"]', 'input[placeholder*="tag"]', '[data-cy="tag-input"]']:
            el = page.locator(sel).first
            if el.is_visible(timeout=2000):
                for tag in article["hashtags"]:
                    el.fill(tag)
                    el.press("Enter")
                    time.sleep(0.3)
                log("  タグ入力OK")
                break
    except Exception:
        log("  タグ入力フィールドが見つからず")

    # ===== 有料ライン確認画面へ進む =====
    # 公開設定パネルのヘッダーには「キャンセル」と、状況に応じて文言が変わる
    # プライマリボタン（有料エリア設定 / 公開設定 など）の2つしかない。
    # 「キャンセル」以外のボタンを選ぶことで文言変更に影響されないようにする。
    proceeded = False
    header_buttons = page.locator('div.fixed.top-0.z-20 button')
    for i in range(header_buttons.count()):
        btn = header_buttons.nth(i)
        text = btn.inner_text().strip()
        if text and text != "キャンセル":
            btn.click()
            proceeded = True
            break

    if not proceeded:
        log("  有料ライン確認画面へ進めませんでした")
        page.screenshot(path=str(BLOG_DIR / "note_debug_publish_fail.png"))
        return ""
    time.sleep(1.5)

    # ===== 最終公開ボタン =====
    # 「投稿する」はクリック自体は成功して記事も公開されるのに、直後のDOM変化
    # （シェアモーダル表示）でPlaywrightのclick()が例外を投げることがある。
    # _click_first_visibleの汎用except節はこれを「ボタンが見つからなかった」と
    # 誤判定してしまう（実際にnote.comへの投稿で6件中6件がこれで誤って
    # error扱いになったことがある）。そのためここだけクリック結果を信用せず、
    # 公開後にしか出ない「シェアモーダル」の出現で実際の成否を確認する。
    publish_btn = None
    for sel in [
        'button:has-text("投稿する")',
        'button:has-text("公開する")',
        'button:has-text("投稿")',
        '[data-cy="final-publish"]',
    ]:
        try:
            btn = page.locator(sel).first
            if btn.is_visible(timeout=5000):
                publish_btn = btn
                break
        except Exception:
            continue

    if publish_btn is None:
        log("  最終公開ボタンが見つかりませんでした")
        page.screenshot(path=str(BLOG_DIR / "note_debug_publish_fail.png"))
        return ""

    try:
        publish_btn.click(timeout=5000)
    except Exception as e:
        log(f"  最終公開ボタンのクリックで例外（公開自体は成功している可能性があるため続行）: {e}")

    time.sleep(2)

    published = False
    try:
        published = page.locator("text=記事をシェアしてみましょう").first.is_visible(timeout=5000)
    except Exception:
        published = False

    if not published:
        log("  投稿完了を確認できませんでした（公開後のシェア画面が出ませんでした）")
        page.screenshot(path=str(BLOG_DIR / "note_debug_publish_fail.png"))
        return ""

    time.sleep(2)
    current_url = page.url
    log(f"  投稿完了: {current_url}")

    # 公開後、記事ページへのクライアント側リダイレクトが遅れて発生することがあり、
    # 次の記事のgoto()と衝突して失敗するため、ここで完全に収まるまで待つ。
    try:
        page.wait_for_load_state("networkidle", timeout=10000)
    except Exception:
        pass
    time.sleep(2)

    return current_url


def _type_markdown(page, element, text: str):
    """マークダウンテキストを入力エリアに入力。

    以前は execCommand('insertText') で一括挿入していたが、これだと
    noteエディタの「##→見出し」「**text**→太字」等のライブ変換
    （1文字ずつのキー入力を監視している）が発火せず、記号がそのまま
    文字として残ってしまうバグがあった（2026-09投稿分で発覚）。
    real keyboard入力（1行ずつ Enter を挟みながら type）に変更し、
    ライブ変換を正しく発火させる。
    """
    element.click()
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if line:
            page.keyboard.type(line, delay=8)
        if i < len(lines) - 1:
            page.keyboard.press("Enter")
        time.sleep(0.03)
    time.sleep(0.5)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true", help="全件投稿")
    parser.add_argument("--file", type=str, help="ファイル番号（例: 01）")
    parser.add_argument("--init-queue", action="store_true", help="キュー初期化")
    parser.add_argument("--save-session", action="store_true", help="手動ログインしてセッション保存")
    args = parser.parse_args()

    # セッション保存モード
    if args.save_session:
        do_save_session()
        return

    # キュー初期化
    if args.init_queue:
        init_queue()
        return

    # セッションファイル確認
    if not SESSION_FILE.exists():
        print("セッションが保存されていません。先に以下を実行してください:")
        print("  python note_auto_post.py --save-session")
        sys.exit(1)

    # 投稿対象ファイルを決定
    queue = load_queue()
    if not queue:
        queue = init_queue()

    if args.file:
        targets = [
            item for item in queue
            if item["file"].startswith(args.file) and item["status"] == "pending"
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
        browser = p.chromium.launch(headless=False)
        # 保存済みセッションを読み込む
        context = browser.new_context(storage_state=str(SESSION_FILE))
        page = context.new_page()

        # ログイン確認
        page.goto("https://note.com", wait_until="domcontentloaded", timeout=60000)
        time.sleep(2)
        if "login" in page.url or "signin" in page.url:
            log("セッション切れです。--save-session で再ログインしてください")
            browser.close()
            sys.exit(1)
        log("セッション確認OK")

        # 投稿処理
        for i, item in enumerate(targets):
            filepath = NOTE_200_DIR / item["file"]
            if not filepath.exists():
                log(f"  ファイルが見つかりません: {filepath}")
                continue

            article = parse_markdown(filepath)
            if not article["title"]:
                log(f"  タイトルが取得できませんでした: {filepath}")
                continue

            url = post_to_note(page, article)

            # キューを更新
            for q in queue:
                if q["file"] == item["file"]:
                    q["status"] = "posted" if url else "error"
                    q["posted_url"] = url
                    break
            save_queue(queue)

            # 投稿間隔（最後の1件以外）
            if i < len(targets) - 1:
                log(f"  次の投稿まで{POST_INTERVAL}秒待機...")
                time.sleep(POST_INTERVAL)

        browser.close()

    log("=== 全投稿完了 ===")
    posted = [q for q in queue if q["status"] == "posted"]
    log(f"投稿済み: {len(posted)}件")
    for q in posted:
        if q["posted_url"]:
            log(f"  {q['file']} → {q['posted_url']}")


if __name__ == "__main__":
    main()
