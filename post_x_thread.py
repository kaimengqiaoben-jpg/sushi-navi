# -*- coding: utf-8 -*-
"""x-threads/*.json のスレッドをXに投稿する。
Xのコンポーザーの「+」ボタンで複数ポストを積み上げてから「すべてポストする」で
まとめて投稿する方式（1件ずつ返信で繋ぐより確実）。

使い方:
  python post_x_thread.py <thread_file.json>   # 1本投稿
  python post_x_thread.py --all                # x-threads/ 内の未投稿を全部投稿
"""
import argparse
import json
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

BLOG_DIR = Path(__file__).parent
THREADS_DIR = BLOG_DIR / "x-threads"
SESSION_FILE = BLOG_DIR / "x_session.json"
LOG_FILE = BLOG_DIR / "x_thread_log.txt"
STATUS_FILE = BLOG_DIR / "x_thread_status.json"
X_COMPOSE_URL = "https://x.com/compose/post"


def log(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def load_status():
    if STATUS_FILE.exists():
        return json.loads(STATUS_FILE.read_text(encoding="utf-8"))
    return {}


def save_status(status):
    STATUS_FILE.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding="utf-8")


def click_first_visible(page, selectors, label, timeout=4000):
    for sel in selectors:
        try:
            btn = page.locator(sel).first
            if btn.is_visible(timeout=timeout):
                try:
                    btn.click(timeout=5000)
                except Exception:
                    btn.click(force=True, timeout=5000)
                return True
        except Exception:
            continue
    log(f"  {label}が見つからず")
    return False


def safe_click(el, retries=3):
    """透明なレイヤーに塞がれてクリックが弾かれる場合、Escapeで払ってから強制クリックする。"""
    for attempt in range(retries):
        try:
            el.click(timeout=5000)
            return True
        except Exception:
            try:
                el.page.keyboard.press("Escape")
            except Exception:
                pass
            time.sleep(0.5)
    try:
        el.click(force=True, timeout=5000)
        return True
    except Exception:
        return False


def dismiss_overlays(page):
    """2段階認証の登録を促すバナーなど、コンポーザーを塞ぐオーバーレイを閉じる。"""
    for sel in [
        '[aria-label="Close"]',
        '[aria-label="閉じる"]',
        '[data-testid="app-bar-close"]',
        '[aria-label="Dismiss"]',
    ]:
        try:
            el = page.locator(sel).first
            if el.is_visible(timeout=1500):
                el.click()
                time.sleep(0.5)
        except Exception:
            continue


def post_thread(page, thread: dict) -> bool:
    tweets = thread["tweets"]
    log(f"投稿開始: {thread['title']}（{len(tweets)}件のスレッド）")

    page.goto(X_COMPOSE_URL, wait_until="domcontentloaded", timeout=60000)
    time.sleep(3)
    dismiss_overlays(page)
    page.screenshot(path=str(BLOG_DIR / "x_debug.png"))

    for i, tweet_text in enumerate(tweets):
        # そのポスト用のテキストエリアを探す（tweetTextarea_0, _1, _2 ...の連番）
        box = None
        for sel in [f'[data-testid="tweetTextarea_{i}"]', 'div[role="textbox"]:last-of-type']:
            try:
                el = page.locator(sel).first
                if el.is_visible(timeout=4000):
                    box = el
                    break
            except Exception:
                continue
        if box is None:
            log(f"  {i+1}件目のテキストエリアが見つかりません")
            page.screenshot(path=str(BLOG_DIR / f"x_debug_fail_{i}.png"))
            return False

        dismiss_overlays(page)
        if not safe_click(box):
            log(f"  {i+1}件目のテキストエリアをクリックできません")
            page.screenshot(path=str(BLOG_DIR / f"x_debug_clickfail_{i}.png"))
            return False
        time.sleep(0.3)
        page.keyboard.type(tweet_text, delay=12)
        time.sleep(0.5)

        if i < len(tweets) - 1:
            # 次のポストを追加する「+」ボタン
            added = click_first_visible(page, [
                '[data-testid="addButton"]',
                'button[aria-label*="別のポストを追加"]',
                'button[aria-label*="Add another post"]',
            ], "＋（次のポスト追加）ボタン", timeout=4000)
            if not added:
                page.screenshot(path=str(BLOG_DIR / f"x_debug_addfail_{i}.png"))
                return False
            time.sleep(0.8)

    time.sleep(3)
    dismiss_overlays(page)
    posted = click_first_visible(page, [
        '[data-testid="tweetButton"]',
        '[data-testid="tweetButtonInline"]',
        'div[role="button"]:has-text("Post all")',
        'div[role="button"]:has-text("すべてポストする")',
        'div[role="button"]:has-text("Post")',
        'div[role="button"]:has-text("ポストする")',
    ], "投稿ボタン", timeout=15000)
    if not posted:
        page.screenshot(path=str(BLOG_DIR / "x_debug_postfail.png"))
        return False

    time.sleep(3)
    log(f"投稿完了: {thread['title']}（現在のURL: {page.url}）")
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", nargs="?", help="スレッドファイル名（x-threads/内）")
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()

    status = load_status()

    if args.all:
        files = sorted(THREADS_DIR.glob("*.json"))
    elif args.file:
        files = [THREADS_DIR / args.file]
    else:
        print("ファイル名を指定するか --all を使ってください")
        sys.exit(1)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(storage_state=str(SESSION_FILE))
        page = context.new_page()
        page.goto("https://x.com/home", wait_until="domcontentloaded", timeout=60000)
        time.sleep(3)
        if "login" in page.url or "flow" in page.url:
            log("セッション切れです。--save-session で再ログインしてください")
            sys.exit(1)
        log("セッション確認OK")

        for f in files:
            if status.get(f.name) == "posted":
                continue
            thread = json.loads(f.read_text(encoding="utf-8"))
            ok = post_thread(page, thread)
            status[f.name] = "posted" if ok else "error"
            save_status(status)
            time.sleep(90)

        browser.close()


if __name__ == "__main__":
    main()
