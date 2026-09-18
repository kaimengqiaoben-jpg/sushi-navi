# -*- coding: utf-8 -*-
"""既存Xアカウント(@wyp42)の表示名・Bioを鮨道ブランドに更新する。
ハンドル(@wyp42)自体は変更しない（既存フォロワー・過去の言及リンクを維持するため）。

前提: x_session.json が用意済みであること（通常ブラウザでログイン後にcookieを
DevToolsでコピーして取得。note.comと同じ手順）。
"""
from playwright.sync_api import sync_playwright
import time

NEW_NAME = "kaimu｜鮨道 SUSHIDO"
NEW_BIO = (
    "現役寿司職人｜江戸前・カウンター8席｜道具と技術のリアルを発信｜"
    "鮨道 SUSHIDO運営 ▶https://sushi-blog-five.vercel.app"
)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(storage_state="x_session.json")
    page = context.new_page()
    page.goto("https://x.com/settings/profile", wait_until="domcontentloaded", timeout=30000)
    time.sleep(2)

    if "login" in page.url:
        print("セッション切れです。x_session.json を再取得してください")
        browser.close()
        raise SystemExit(1)

    name_input = page.locator('input[name="displayName"]').first
    name_input.click()
    name_input.fill("")
    name_input.type(NEW_NAME, delay=15)
    time.sleep(0.3)

    bio_area = page.locator('textarea[name="description"]').first
    bio_area.click()
    bio_area.fill("")
    bio_area.type(NEW_BIO, delay=10)
    time.sleep(0.5)

    page.screenshot(path="x_debug_profile_before_save.png", full_page=True)

    save_btn = page.locator('button:has-text("保存")').first
    if not save_btn.is_visible(timeout=3000):
        save_btn = page.locator('button:has-text("Save")').first
    save_btn.click()
    time.sleep(2)

    page.screenshot(path="x_debug_profile_saved.png", full_page=True)
    print("current URL after save:", page.url)
    print("saved")
    browser.close()
