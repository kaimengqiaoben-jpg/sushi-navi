# -*- coding: utf-8 -*-
from playwright.sync_api import sync_playwright
import time

NEW_NAME = "鮨道 SUSHIDO"
NEW_BIO = (
    "現役の寿司職人が個人で運営する専門メディア「鮨道 SUSHIDO」。"
    "技術・道具・キャリア・海外・経営を実務の言葉で記録。"
    "▶https://sushi-blog-five.vercel.app"
)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(storage_state="note_session.json")
    page = context.new_page()
    page.goto("https://note.com/settings/profile", wait_until="domcontentloaded", timeout=30000)
    time.sleep(2)

    name_input = page.locator('input[type="text"]').first
    name_input.click()
    name_input.fill("")
    name_input.fill(NEW_NAME)

    bio_area = page.locator("textarea").first
    bio_area.click()
    bio_area.fill("")
    bio_area.fill(NEW_BIO)
    time.sleep(0.5)

    save_btn = page.locator('button:has-text("保存")').first
    save_btn.click()
    time.sleep(2)

    page.screenshot(path="note_debug_profile_saved.png", full_page=True)
    print("current URL after save:", page.url)
    print("saved")
    browser.close()
