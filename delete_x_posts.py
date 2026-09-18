# -*- coding: utf-8 -*-
"""x_posts_review.json で "action": "delete" とマークされた投稿だけを削除する。
scrape_x_posts.py で一覧化 → 人間がレビューして action を書き換える → 本スクリプトで実行、
という二段階方式の最終段階。ここでのみ実際の削除（＝取り消し不可）を行う。

使い方:
  python delete_x_posts.py            # 対象を表示するだけ（確認用、実際には削除しない）
  python delete_x_posts.py --execute  # 実際に削除する
"""
import argparse
import json
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

BLOG_DIR = Path(__file__).parent
SESSION_FILE = BLOG_DIR / "x_session.json"
REVIEW_FILE = BLOG_DIR / "x_posts_review.json"
LOG_FILE = BLOG_DIR / "x_delete_log.txt"


def log(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def delete_post(page, url: str) -> bool:
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    time.sleep(2)

    menu_btn = page.locator('[data-testid="caret"]').first
    if not menu_btn.is_visible(timeout=5000):
        log(f"  メニューボタンが見つかりません: {url}")
        return False
    menu_btn.click()
    time.sleep(0.5)

    delete_item = page.locator('[data-testid="Dropdown"] >> text=削除').first
    if not delete_item.is_visible(timeout=3000):
        delete_item = page.locator('[data-testid="Dropdown"] >> text=Delete').first
    if not delete_item.is_visible(timeout=3000):
        log(f"  削除メニューが見つかりません: {url}")
        return False
    delete_item.click()
    time.sleep(0.5)

    confirm_btn = page.locator('[data-testid="confirmationSheetConfirm"]').first
    if not confirm_btn.is_visible(timeout=3000):
        log(f"  削除確認ボタンが見つかりません: {url}")
        return False
    confirm_btn.click()
    time.sleep(1.5)
    log(f"  削除完了: {url}")
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true", help="実際に削除を実行する")
    args = parser.parse_args()

    if not REVIEW_FILE.exists():
        print(f"{REVIEW_FILE} が見つかりません。先に scrape_x_posts.py を実行してください")
        sys.exit(1)

    items = json.loads(REVIEW_FILE.read_text(encoding="utf-8"))
    targets = [i for i in items if i.get("action") == "delete"]

    print(f"削除対象: {len(targets)}件 / 全{len(items)}件")
    for t in targets:
        print(f"  - {t['url']}  「{t['text_snippet'][:40]}」")

    if not args.execute:
        print("\n--execute を付けずに実行したため、確認のみで削除は行っていません。")
        return

    if not targets:
        print("削除対象がありません")
        return

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(storage_state=str(SESSION_FILE))
        page = context.new_page()
        page.goto("https://x.com/home", wait_until="domcontentloaded", timeout=60000)
        time.sleep(2)
        if "login" in page.url:
            log("セッション切れです。x_session.json を再取得してください")
            sys.exit(1)

        for t in targets:
            ok = delete_post(page, t["url"])
            t["action"] = "deleted" if ok else "delete_failed"
            time.sleep(3)

        browser.close()

    REVIEW_FILE.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    print("完了。x_posts_review.json を更新しました")


if __name__ == "__main__":
    main()
