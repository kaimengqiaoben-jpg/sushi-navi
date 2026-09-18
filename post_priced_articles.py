# -*- coding: utf-8 -*-
"""note_auto_post.py の post_to_note() を再利用して、200円以外の価格の記事を投稿する。"""
import time
from pathlib import Path
from playwright.sync_api import sync_playwright
import note_auto_post as m

BLOG_DIR = Path(__file__).parent
SESSION_FILE = BLOG_DIR / "note_session.json"

ITEMS = [
    {"file": "02_500yen_transfer_guide.md", "price": 500, "strip": "【500円】"},
    {"file": "03_1000yen_overseas_guide.md", "price": 1000, "strip": "【1,000円】"},
]


def build_article(item):
    filepath = BLOG_DIR / "note-articles" / item["file"]
    text = filepath.read_text(encoding="utf-8")
    lines = text.strip().split("\n")

    title = ""
    for line in lines:
        if line.startswith("# "):
            title = line.lstrip("# ").strip()
            title = title.replace(item["strip"], "").strip()
            break

    body_lines = [l for l in lines if not l.startswith("# ") and "※この記事は有料" not in l]
    body = "\n".join(body_lines).strip()

    if "\n---\n" in body:
        free_part, paid_part = body.split("\n---\n", 1)
    else:
        free_part, paid_part = "", body

    return {
        "title": title,
        "free_body": free_part.strip(),
        "paid_body": paid_part.strip(),
        "price": item["price"],
        "hashtags": m.COMMON_HASHTAGS,
    }


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(storage_state=str(SESSION_FILE))
        page = context.new_page()

        page.goto("https://note.com", wait_until="domcontentloaded", timeout=60000)
        time.sleep(2)
        if "login" in page.url:
            print("セッション切れです")
            browser.close()
            return
        print("セッション確認OK")

        for item in ITEMS:
            article = build_article(item)
            if not article["title"]:
                print("タイトル取得失敗:", item["file"])
                continue
            url = m.post_to_note(page, article)
            print(f"RESULT\t{item['file']}\t{url}")
            time.sleep(60)

        browser.close()


if __name__ == "__main__":
    main()
