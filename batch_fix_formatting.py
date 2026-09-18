# -*- coding: utf-8 -*-
"""formatting bugだけの記事を一括で編集し直す（本文再入力、タイトルはファイルの内容をそのまま使う）。"""
import time
from pathlib import Path
from playwright.sync_api import sync_playwright
import note_auto_post as m
import edit_note_article as e

BLOG_DIR = Path(__file__).parent
SESSION_FILE = BLOG_DIR / "note_session.json"

ITEMS = [
    ("nb173df126476", "note-articles/01_free_roadmap.md", "この記事は無料", None),
    ("ncf9a048ad279", "note-articles/200yen/04_resume_template.md", "この記事は200円", "｜200円"),
    ("nd1593b0f5063", "note-articles/200yen/05_salary_negotiation.md", "この記事は200円", "｜200円"),
    ("n55f2e9dad24a", "note-articles/200yen/06_delivery_sushi_start.md", "この記事は200円", "｜200円"),
    ("n9ac6e4950dc7", "note-articles/200yen/07_instagram_sushi.md", "この記事は200円", "｜200円"),
    ("ndb5bffbb73a7", "note-articles/200yen/08_subsidy_guide.md", "この記事は200円", "｜200円"),
    ("n3860ab6063d7", "note-articles/200yen/09_shari_recipe.md", "この記事は200円", "｜200円"),
    ("n238ac2c894e7", "note-articles/200yen/10_knife_maintenance.md", "この記事は200円", "｜200円"),
    ("n71a90f2aab8d", "note-articles/free_new/01_sushido_start.md", "この記事は無料", None),
    ("n7e5c25c29895", "note-articles/free_new/02_sushiya_jargon.md", "この記事は無料", None),
    ("n75a9d7d261db", "note-articles/free_new/03_my_knives.md", "この記事は無料", None),
]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(storage_state=str(SESSION_FILE))
    page = context.new_page()
    page.goto("https://note.com", wait_until="domcontentloaded", timeout=60000)
    time.sleep(2)
    if "login" in page.url:
        print("セッション切れです")
        raise SystemExit(1)
    print("セッション確認OK")

    for note_id, md_file, marker, title_strip in ITEMS:
        title, body = e.parse_title_and_body(BLOG_DIR / md_file, marker, title_strip)
        print(f"--- {note_id} ({md_file}) ---")
        ok = e.edit_article(page, note_id, body, new_title=title)
        print("結果:", ok)
        time.sleep(45)

    browser.close()
print("全件完了")
