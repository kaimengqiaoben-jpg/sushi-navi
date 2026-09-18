# -*- coding: utf-8 -*-
"""@wyp42 の既存投稿(444件)を一覧化し、レビュー用ファイルを作る。
削除は一切行わない。ここで作る x_posts_review.json を人間（カイムさん/相談の上で私）が
見て、寿司と無関係と判断したものだけ "action": "delete" を付け、
その後 delete_x_posts.py で該当分のみ削除する二段階方式。

前提: x_session.json が用意済みであること。

使い方:
  python scrape_x_posts.py
"""
import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

BLOG_DIR = Path(__file__).parent
SESSION_FILE = BLOG_DIR / "x_session.json"
OUT_FILE = BLOG_DIR / "x_posts_review.json"
PROFILE_URL = "https://x.com/wyp42"

# 寿司/鮨道関連らしさの簡易キーワード判定（あくまで参考フラグ。最終判断は人間が行う）
SUSHI_KEYWORDS = ["寿司", "鮨", "sushi", "SUSHIDO", "職人", "包丁", "シャリ", "ネタ", "板前", "カウンター"]


def load_existing():
    if OUT_FILE.exists():
        data = json.loads(OUT_FILE.read_text(encoding="utf-8"))
        return {item["url"]: item for item in data}
    return {}


def main():
    existing = load_existing()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(storage_state=str(SESSION_FILE))
        page = context.new_page()
        page.goto(PROFILE_URL, wait_until="domcontentloaded", timeout=60000)
        time.sleep(3)

        if "login" in page.url:
            print("セッション切れです。x_session.json を再取得してください")
            browser.close()
            return

        collected = dict(existing)
        stall_count = 0
        last_count = -1

        while stall_count < 6:
            articles = page.locator('article[data-testid="tweet"]').all()
            for art in articles:
                try:
                    link = art.locator('a[href*="/status/"]').first
                    href = link.get_attribute("href")
                    if not href:
                        continue
                    url = f"https://x.com{href}" if href.startswith("/") else href
                    if url in collected:
                        continue
                    text_el = art.locator('div[data-testid="tweetText"]').first
                    text = text_el.inner_text() if text_el.count() > 0 else ""
                    likely_sushi = any(k in text for k in SUSHI_KEYWORDS)
                    collected[url] = {
                        "url": url,
                        "text_snippet": text[:200],
                        "likely_sushi_related": likely_sushi,
                        "action": "keep",  # デフォルトは保持。要削除分だけ後で "delete" に変更する
                    }
                except Exception:
                    continue

            page.mouse.wheel(0, 3000)
            time.sleep(1.5)

            if len(collected) == last_count:
                stall_count += 1
            else:
                stall_count = 0
            last_count = len(collected)
            print(f"収集済み: {len(collected)}件")

        browser.close()

    OUT_FILE.write_text(
        json.dumps(list(collected.values()), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"完了: {len(collected)}件を {OUT_FILE} に保存しました")
    print("寿司と無関係と判断したものだけ action を delete に変更してから delete_x_posts.py を実行してください")


if __name__ == "__main__":
    main()
