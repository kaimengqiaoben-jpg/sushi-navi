# -*- coding: utf-8 -*-
"""threads-posts/*.json のスレッドをThreadsに投稿する。
Threadsのコンポーザーの「+」（スレッドに追加）ボタンで複数ポストを積み上げてから
まとめて投稿する方式（post_x_thread.py と同じ考え方）。

注意: セレクタはThreadsの実UIに対して未検証。threads_session.json を用意して
1本だけテスト投稿してから --all を使うこと。

使い方:
  python post_threads.py <thread_file.json>   # 1本投稿
  python post_threads.py --all                # threads-posts/ 内の未投稿を全部投稿
"""
import argparse
import json
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

BLOG_DIR = Path(__file__).parent
THREADS_DIR = BLOG_DIR / "threads-posts"
SESSION_FILE = BLOG_DIR / "threads_session.json"
LOG_FILE = BLOG_DIR / "threads_post_log.txt"
STATUS_FILE = BLOG_DIR / "threads_post_status.json"
THREADS_HOME_URL = "https://www.threads.com/"
THREADS_COMPOSE_URL = "https://www.threads.com/intent/post"


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
                btn.click()
                return True
        except Exception:
            continue
    log(f"  {label}が見つからず")
    return False


def post_thread(page, thread: dict) -> bool:
    posts = thread["posts"]
    log(f"投稿開始: {thread['title']}（{len(posts)}件のスレッド）")

    page.goto(THREADS_COMPOSE_URL, wait_until="networkidle", timeout=60000)
    time.sleep(2)
    page.screenshot(path=str(BLOG_DIR / "threads_debug.png"))

    for i, post_text in enumerate(posts):
        box = None
        for sel in [
            f'[data-testid="PostComposer_TextArea_{i}"]',
            'div[contenteditable="true"][role="textbox"]:last-of-type',
            'div[role="textbox"]:last-of-type',
        ]:
            try:
                el = page.locator(sel).first
                if el.is_visible(timeout=4000):
                    box = el
                    break
            except Exception:
                continue
        if box is None:
            log(f"  {i+1}件目のテキストエリアが見つかりません")
            page.screenshot(path=str(BLOG_DIR / f"threads_debug_fail_{i}.png"))
            return False

        box.click()
        time.sleep(0.3)
        page.keyboard.type(post_text, delay=12)
        time.sleep(0.5)

        if i < len(posts) - 1:
            added = click_first_visible(page, [
                '[aria-label="Add to thread"]',
                '[aria-label*="スレッドに追加"]',
                'svg[aria-label="Add to thread"]',
                'div[role="button"]:has-text("+")',
            ], "＋（スレッドに追加）ボタン", timeout=4000)
            if not added:
                page.screenshot(path=str(BLOG_DIR / f"threads_debug_addfail_{i}.png"))
                return False
            time.sleep(0.8)

    time.sleep(1)
    posted = click_first_visible(page, [
        '[aria-label="Post"]',
        'div[role="button"]:has-text("Post")',
        'div[role="button"]:has-text("投稿")',
    ], "投稿ボタン", timeout=5000)
    if not posted:
        page.screenshot(path=str(BLOG_DIR / "threads_debug_postfail.png"))
        return False

    time.sleep(3)
    log(f"投稿完了: {thread['title']}（現在のURL: {page.url}）")
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", nargs="?", help="スレッドファイル名（threads-posts/内）")
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
        page.goto(THREADS_HOME_URL, wait_until="domcontentloaded", timeout=60000)
        time.sleep(3)
        if "login" in page.url:
            log("セッション切れです。threads_session.json を再取得してください")
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
