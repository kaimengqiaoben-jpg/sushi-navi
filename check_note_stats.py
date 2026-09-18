# -*- coding: utf-8 -*-
"""公開note記事のスキ数を、ログイン不要でまとめて取得する。"""
import json
import time
from playwright.sync_api import sync_playwright

ARTICLES = [
    ("n6fbdeb14df3a", "02_cost_simulation", "寿司スクール費用シミュレーション"),
    ("nf6aac2eef858", "03_black_shop_check", "ブラック寿司店チェックリスト"),
    ("ncf9a048ad279", "04_resume_template", "履歴書・職務経歴書テンプレート"),
    ("nd1593b0f5063", "05_salary_negotiation", "給与交渉マニュアル"),
    ("n55f2e9dad24a", "06_delivery_sushi_start", "出張寿司を最速で始める手順書"),
    ("n9ac6e4950dc7", "07_instagram_sushi", "Instagramフォロワー戦略"),
    ("ndb5bffbb73a7", "08_subsidy_guide", "ハローワーク給付金申請"),
    ("n3860ab6063d7", "09_shari_recipe", "プロのシャリの作り方"),
    ("n238ac2c894e7", "10_knife_maintenance", "包丁メンテナンスガイド"),
    ("nd9b0e541fb03", "11_30s_career_change", "30代体験談まとめ"),
    ("nf4b4d94bbb5c", "12_school_visit_report", "スクール見学レポート"),
    ("nb173df126476", "01_free_roadmap", "未経験ロードマップ(無料)"),
]

results = []
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    for note_id, file, label in ARTICLES:
        url = f"https://note.com/modern_roses2643/n/{note_id}"
        try:
            page.goto(url, wait_until="networkidle", timeout=30000)
            time.sleep(1.2)
            text = page.inner_text("body")
            lines = [l.strip() for l in text.split("\n") if l.strip()]
            # ヘッダー行（投稿/ログイン/会員登録）を除いた先頭がタイトル
            start = 0
            for i, l in enumerate(lines[:6]):
                if l in ("投稿", "ログイン", "会員登録"):
                    start = i + 1
            real_title = lines[start] if start < len(lines) else ""
            like = None
            date = None
            for j in range(start + 1, min(start + 6, len(lines))):
                if lines[j].isdigit() and like is None:
                    like = int(lines[j])
                if "年" in lines[j] and "月" in lines[j] and date is None:
                    date = lines[j]
            results.append({"id": note_id, "file": file, "real_title": real_title, "like": like, "date": date, "url": url})
            print(note_id, file, "like=", like, "date=", date)
        except Exception as e:
            print(note_id, file, "ERROR", e)
            results.append({"id": note_id, "file": file, "label": label, "like": None, "error": str(e)})
    browser.close()

with open("note_stats_raw.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print("saved note_stats_raw.json")
