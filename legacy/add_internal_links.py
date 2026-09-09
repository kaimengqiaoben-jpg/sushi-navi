"""
内部リンク強化スクリプト
- 各記事のフッター直前に「関連記事」ブロックを追加
- テーマ別に関連性の高い記事をリンク
"""
import os
import re

BASE = "C:/Users/81909/sushi-blog"

# 記事ごとの関連記事定義 (テーマ別に最大4件)
RELATED = {
    "sushi-chef-salary.html": [
        ("career-change-beginner.html", "未経験から寿司職人になる3つのルート"),
        ("independent-guide.html",      "寿司職人として独立・開業する方法"),
        ("career-30s.html",             "30代から寿司職人に転職できる？"),
        ("sushi-school-compare.html",   "寿司スクールおすすめ比較ランキング"),
    ],
    "career-change-beginner.html": [
        ("sushi-chef-salary.html",      "寿司職人の年収はいくら？"),
        ("sushi-school-compare.html",   "寿司スクールおすすめ比較ランキング"),
        ("no-apprenticeship.html",      "修行なしで寿司職人になれる？"),
        ("license-guide.html",          "寿司職人に必要な資格・免許まとめ"),
    ],
    "career-30s.html": [
        ("career-change-beginner.html", "未経験から寿司職人になる3つのルート"),
        ("sushi-chef-salary.html",      "寿司職人の年収はいくら？"),
        ("sushi-school-compare.html",   "寿司スクールおすすめ比較ランキング"),
        ("no-apprenticeship.html",      "修行なしで寿司職人になれる？"),
    ],
    "sushi-school-compare.html": [
        ("school-cost.html",            "寿司スクール費用完全ガイド"),
        ("school-inshokujin.html",      "飲食人大学の評判・口コミ"),
        ("school-sushi-academy.html",   "寿司アカデミーの評判・口コミ"),
        ("school-tokyo-sushi.html",     "東京すし和食料理学院の評判"),
    ],
    "school-cost.html": [
        ("sushi-school-compare.html",   "寿司スクールおすすめ比較ランキング"),
        ("school-inshokujin.html",      "飲食人大学の評判・口コミ"),
        ("school-sushi-academy.html",   "寿司アカデミーの評判・口コミ"),
        ("career-change-beginner.html", "未経験から寿司職人になる3つのルート"),
    ],
    "school-inshokujin.html": [
        ("sushi-school-compare.html",   "寿司スクールおすすめ比較ランキング"),
        ("school-cost.html",            "寿司スクール費用完全ガイド"),
        ("school-sushi-academy.html",   "寿司アカデミーの評判・口コミ"),
        ("school-tokyo-sushi.html",     "東京すし和食料理学院の評判"),
    ],
    "school-sushi-academy.html": [
        ("sushi-school-compare.html",   "寿司スクールおすすめ比較ランキング"),
        ("school-cost.html",            "寿司スクール費用完全ガイド"),
        ("overseas-sushi-chef.html",    "寿司職人として海外就職する方法"),
        ("school-inshokujin.html",      "飲食人大学の評判・口コミ"),
    ],
    "school-tokyo-sushi.html": [
        ("sushi-school-compare.html",   "寿司スクールおすすめ比較ランキング"),
        ("school-cost.html",            "寿司スクール費用完全ガイド"),
        ("school-inshokujin.html",      "飲食人大学の評判・口コミ"),
        ("license-guide.html",          "寿司職人に必要な資格・免許まとめ"),
    ],
    "school-tsuji.html": [
        ("sushi-school-compare.html",   "寿司スクールおすすめ比較ランキング"),
        ("school-cost.html",            "寿司スクール費用完全ガイド"),
        ("license-guide.html",          "寿司職人に必要な資格・免許まとめ"),
        ("career-change-beginner.html", "未経験から寿司職人になる3つのルート"),
    ],
    "school-online.html": [
        ("sushi-school-compare.html",   "寿司スクールおすすめ比較ランキング"),
        ("school-cost.html",            "寿司スクール費用完全ガイド"),
        ("career-change-beginner.html", "未経験から寿司職人になる3つのルート"),
        ("sushi-tools-amazon.html",     "寿司職人の道具・必需品おすすめ20選"),
    ],
    "independent-guide.html": [
        ("sushi-chef-salary.html",      "寿司職人の年収はいくら？"),
        ("license-guide.html",          "寿司職人に必要な資格・免許まとめ"),
        ("delivery-sushi-business.html","出張寿司で副業・独立する方法"),
        ("knife-recommend.html",        "寿司職人が使う包丁おすすめ7選"),
    ],
    "delivery-sushi-business.html": [
        ("independent-guide.html",      "寿司職人として独立・開業する方法"),
        ("license-guide.html",          "寿司職人に必要な資格・免許まとめ"),
        ("sushi-tools-amazon.html",     "寿司職人の道具・必需品おすすめ20選"),
        ("sushi-chef-salary.html",      "寿司職人の年収はいくら？"),
    ],
    "license-guide.html": [
        ("career-change-beginner.html", "未経験から寿司職人になる3つのルート"),
        ("sushi-school-compare.html",   "寿司スクールおすすめ比較ランキング"),
        ("independent-guide.html",      "寿司職人として独立・開業する方法"),
        ("no-apprenticeship.html",      "修行なしで寿司職人になれる？"),
    ],
    "no-apprenticeship.html": [
        ("career-change-beginner.html", "未経験から寿司職人になる3つのルート"),
        ("sushi-school-compare.html",   "寿司スクールおすすめ比較ランキング"),
        ("school-cost.html",            "寿司スクール費用完全ガイド"),
        ("sushi-chef-salary.html",      "寿司職人の年収はいくら？"),
    ],
    "overseas-sushi-chef.html": [
        ("school-sushi-academy.html",   "寿司アカデミーの評判・口コミ"),
        ("career-change-beginner.html", "未経験から寿司職人になる3つのルート"),
        ("sushi-chef-salary.html",      "寿司職人の年収はいくら？"),
        ("license-guide.html",          "寿司職人に必要な資格・免許まとめ"),
    ],
    "daily-work.html": [
        ("sushi-chef-salary.html",      "寿司職人の年収はいくら？"),
        ("career-change-beginner.html", "未経験から寿司職人になる3つのルート"),
        ("knife-recommend.html",        "寿司職人が使う包丁おすすめ7選"),
        ("sushi-tools-amazon.html",     "寿司職人の道具・必需品おすすめ20選"),
    ],
    "knife-recommend.html": [
        ("sushi-tools-amazon.html",     "寿司職人の道具・必需品おすすめ20選"),
        ("daily-work.html",             "寿司職人の1日・仕事内容"),
        ("independent-guide.html",      "寿司職人として独立・開業する方法"),
        ("career-change-beginner.html", "未経験から寿司職人になる3つのルート"),
    ],
    "sushi-tools-amazon.html": [
        ("knife-recommend.html",        "寿司職人が使う包丁おすすめ7選"),
        ("daily-work.html",             "寿司職人の1日・仕事内容"),
        ("career-change-beginner.html", "未経験から寿司職人になる3つのルート"),
        ("school-online.html",          "寿司オンラインスクールおすすめ比較"),
    ],
    "sushi-uniform-amazon.html": [
        ("sushi-tools-amazon.html",     "寿司職人の道具・必需品おすすめ20選"),
        ("knife-recommend.html",        "寿司職人が使う包丁おすすめ7選"),
        ("daily-work.html",             "寿司職人の1日・仕事内容"),
        ("career-change-beginner.html", "未経験から寿司職人になる3つのルート"),
    ],
    "women-sushi-chef.html": [
        ("career-change-beginner.html", "未経験から寿司職人になる3つのルート"),
        ("sushi-chef-salary.html",      "寿司職人の年収はいくら？"),
        ("sushi-school-compare.html",   "寿司スクールおすすめ比較ランキング"),
        ("career-30s.html",             "30代から寿司職人に転職できる？"),
    ],
}

RELATED_BLOCK_STYLE = """
<style>
.related-articles { background: #f9f9f9; border-top: 3px solid var(--primary, #c0392b); padding: 32px 0; margin-top: 40px; }
.related-articles h2 { font-size: 1.1rem; font-weight: 700; margin-bottom: 16px; color: var(--primary, #c0392b); }
.related-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; }
.related-card { background: #fff; border: 1px solid #e0e0e0; border-radius: 8px; padding: 16px; text-decoration: none; color: inherit; display: block; transition: box-shadow 0.2s; }
.related-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
.related-card-label { font-size: 0.75rem; color: var(--primary, #c0392b); font-weight: 700; margin-bottom: 6px; }
.related-card-title { font-size: 0.9rem; font-weight: 600; line-height: 1.4; }
</style>
"""


def build_related_block(links):
    cards = ""
    for filename, title in links:
        cards += f"""    <a href="{filename}" class="related-card">
      <div class="related-card-label">関連記事</div>
      <div class="related-card-title">{title}</div>
    </a>\n"""

    return f"""
{RELATED_BLOCK_STYLE}
<div class="related-articles">
  <div style="max-width:860px; margin:0 auto; padding:0 20px;">
    <h2>関連記事</h2>
    <div class="related-grid">
{cards}    </div>
  </div>
</div>
"""


def add_related_to_file(filepath, links):
    with open(filepath, "r", encoding="utf-8") as f:
        html = f.read()

    # すでに関連記事ブロックがある場合はスキップ
    if "related-articles" in html:
        print(f"SKIP (already has related): {os.path.basename(filepath)}")
        return

    block = build_related_block(links)
    html = html.replace("<footer>", block + "<footer>")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"OK: {os.path.basename(filepath)}")


articles_dir = os.path.join(BASE, "articles")

for filename, links in RELATED.items():
    filepath = os.path.join(articles_dir, filename)
    if os.path.exists(filepath):
        add_related_to_file(filepath, links)
    else:
        print(f"NG: {filename}")

print("\n内部リンク追加完了")
