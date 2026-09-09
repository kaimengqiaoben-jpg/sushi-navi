"""
SEO一括修正スクリプト
- canonical タグ追加
- title タグ最適化
- meta description 最適化
- 年号統一 (2025)
"""

import os
import re

BASE_URL = "https://sushi-blog-five.vercel.app"

# ページごとの最適化設定
PAGES = {
    "index.html": {
        "url": "/",
        "title": "寿司職人ナビ｜未経験から寿司職人になる最短ルート【2025年版】",
        "description": "未経験から寿司職人を目指す全ての方へ。スクール比較・費用・転職ガイド・年収・独立方法まで徹底解説。最短ルートで寿司職人になる方法をまとめました。",
    },
    "articles/career-30s.html": {
        "url": "/articles/career-30s.html",
        "title": "30代から寿司職人に転職できる？成功事例と現実を解説｜寿司職人ナビ",
        "description": "30代からの寿司職人転職は可能です。成功事例・年齢の壁・必要な準備・スクール活用法を詳しく解説。30代でも遅くない理由と転職成功のコツをお伝えします。",
    },
    "articles/career-change-beginner.html": {
        "url": "/articles/career-change-beginner.html",
        "title": "未経験から寿司職人になる3つのルート【完全ガイド2025年版】｜寿司職人ナビ",
        "description": "未経験から寿司職人になる方法を3ルート別に比較。スクール・弟子入り・独学のメリット・費用・期間を徹底解説。あなたに合ったルートを見つけましょう。",
    },
    "articles/daily-work.html": {
        "url": "/articles/daily-work.html",
        "title": "寿司職人の1日・仕事内容をリアルに公開【きつい？楽しい？】｜寿司職人ナビ",
        "description": "寿司職人の1日のスケジュール・仕事内容をリアルに公開。仕込みから閉店まで修行中・一人前・独立後の3パターンで解説。きつい部分もすべて正直にお伝えします。",
    },
    "articles/delivery-sushi-business.html": {
        "url": "/articles/delivery-sushi-business.html",
        "title": "出張寿司で副業・独立する方法【月10万円の稼ぎ方2025年版】｜寿司職人ナビ",
        "description": "出張寿司で副業・独立する具体的な方法を解説。必要な道具・資格・集客・料金設定まで完全網羅。月10万円以上稼ぐ実践者のノウハウを公開しています。",
    },
    "articles/independent-guide.html": {
        "url": "/articles/independent-guide.html",
        "title": "寿司職人として独立・開業する方法【費用・手順・成功事例2025】｜寿司職人ナビ",
        "description": "寿司職人が独立・開業するための費用・手順・成功事例を徹底解説。最低資金500万円〜から始められる現代型開業スタイルも紹介。失敗しない独立のポイントを解説。",
    },
    "articles/knife-recommend.html": {
        "url": "/articles/knife-recommend.html",
        "title": "寿司職人が使う包丁おすすめ7選【初心者〜プロ別2025年版】｜寿司職人ナビ",
        "description": "寿司職人が実際に使う包丁を初心者・中級・プロ別に厳選紹介。柳刃包丁・出刃包丁の選び方から手入れ方法まで徹底解説。失敗しない包丁選びのコツをお伝えします。",
    },
    "articles/license-guide.html": {
        "url": "/articles/license-guide.html",
        "title": "寿司職人に必要な資格・免許まとめ【取得方法と費用2025】｜寿司職人ナビ",
        "description": "寿司職人・調理師になるために必要な資格・免許を徹底解説。調理師免許・食品衛生責任者の取得方法・費用・期間をわかりやすく説明します。",
    },
    "articles/no-apprenticeship.html": {
        "url": "/articles/no-apprenticeship.html",
        "title": "修行なしで寿司職人になれる？スクール・回転寿司ルートを解説｜寿司職人ナビ",
        "description": "修行なしで寿司職人になる方法を解説。スクール卒業後すぐ就職・回転寿司チェーン入社など現実的なルートを紹介。修行が必要なケースとの違いも詳しく説明します。",
    },
    "articles/overseas-sushi-chef.html": {
        "url": "/articles/overseas-sushi-chef.html",
        "title": "寿司職人として海外就職・移住する方法【2025年版】｜寿司職人ナビ",
        "description": "寿司職人として海外就職・移住する方法を徹底解説。人気の渡航先・必要なビザ・英語力・給料相場まで完全網羅。海外で活躍する職人のリアルな体験談も掲載。",
    },
    "articles/school-cost.html": {
        "url": "/articles/school-cost.html",
        "title": "寿司スクール費用完全ガイド【相場・安くする方法2025年版】｜寿司職人ナビ",
        "description": "寿司スクールの費用相場を徹底比較。1日5千円〜100万円超まで幅広い価格帯を解説。給付金・補助金を使って安く通う方法も紹介。費用を抑えるコツを伝授します。",
    },
    "articles/school-inshokujin.html": {
        "url": "/articles/school-inshokujin.html",
        "title": "飲食人大学の評判・口コミ・費用を徹底レビュー【2025年版】｜寿司職人ナビ",
        "description": "飲食人大学の評判・口コミ・費用・カリキュラムを徹底レビュー。卒業生の声や他スクールとの比較も掲載。高級店・ホテル就職を目指す方は必読の情報です。",
    },
    "articles/school-online.html": {
        "url": "/articles/school-online.html",
        "title": "寿司オンラインスクールおすすめ比較【2025年版・自宅で学べる】｜寿司職人ナビ",
        "description": "自宅で学べる寿司オンラインスクール・動画講座を徹底比較。副業・趣味・おもてなし用途に人気。費用5〜15万円の格安コースから選べます。無料体験情報も掲載。",
    },
    "articles/school-sushi-academy.html": {
        "url": "/articles/school-sushi-academy.html",
        "title": "寿司アカデミーの評判・口コミ・費用を徹底レビュー【2025年版】｜寿司職人ナビ",
        "description": "寿司アカデミーの評判・口コミ・費用を徹底レビュー。最短1ヶ月・英語対応・海外就職サポートが強み。外国人・海外転職希望者にも人気のスクール情報をまとめました。",
    },
    "articles/school-tokyo-sushi.html": {
        "url": "/articles/school-tokyo-sushi.html",
        "title": "東京すし和食料理学院の評判・口コミ・費用【2025年版】｜寿司職人ナビ",
        "description": "東京すし和食料理学院の評判・口コミ・費用・カリキュラムを徹底レビュー。卒業生の声や他スクールとの比較も掲載。入学を検討中の方は必読の情報です。",
    },
    "articles/school-tsuji.html": {
        "url": "/articles/school-tsuji.html",
        "title": "辻調理師専門学校の評判・口コミ・費用【2025年版】｜寿司職人ナビ",
        "description": "辻調理師専門学校の評判・口コミ・費用を徹底レビュー。老舗の調理師専門学校として資格取得・総合的な調理技術を学びたい方に向いています。他校との比較も掲載。",
    },
    "articles/sushi-chef-salary.html": {
        "url": "/articles/sushi-chef-salary.html",
        "title": "寿司職人の年収はいくら？修行中〜独立後まで全部教えます｜寿司職人ナビ",
        "description": "寿司職人の年収・給料をキャリアステージ別に公開。修行中は月15万でも独立後は月100万も可能。リアルな数字と年収アップのコツを詳しく解説します。",
    },
    "articles/sushi-school-compare.html": {
        "url": "/articles/sushi-school-compare.html",
        "title": "【2025年最新】寿司スクールおすすめ比較ランキング｜費用・期間・就職率｜寿司職人ナビ",
        "description": "寿司スクール15校を徹底比較。費用・期間・就職率・カリキュラムを分析してランキング化。未経験から寿司職人を目指す方必見の完全比較ガイドです。",
    },
    "articles/sushi-tools-amazon.html": {
        "url": "/articles/sushi-tools-amazon.html",
        "title": "寿司職人の道具・必需品おすすめ20選【Amazonで買える】｜寿司職人ナビ",
        "description": "寿司職人が実際に使う道具・必需品をAmazonで買えるものに厳選。包丁・まな板・シャリ桶・調理服など全20選。初心者〜プロ別に選び方も詳しく紹介します。",
    },
    "articles/sushi-uniform-amazon.html": {
        "url": "/articles/sushi-uniform-amazon.html",
        "title": "寿司職人の髪型・整髪料おすすめまとめ【2025年版】｜寿司職人ナビ",
        "description": "寿司職人・和食料理人向けの髪型・整髪料・ヘアケア用品をAmazonから厳選紹介。清潔感と職人らしさを両立するスタイリング方法をわかりやすく解説します。",
    },
    "articles/women-sushi-chef.html": {
        "url": "/articles/women-sushi-chef.html",
        "title": "女性が寿司職人になれる？現役女性シェフのリアルな話【2025年版】｜寿司職人ナビ",
        "description": "女性でも寿司職人になれます。現役女性寿司職人のインタビューと女性が活躍しやすいスクール・職場を紹介。差別・偏見の実態も正直に解説した完全ガイドです。",
    },
}

def fix_file(filepath, page_key, page_data):
    with open(filepath, "r", encoding="utf-8") as f:
        html = f.read()

    canonical_tag = f'  <link rel="canonical" href="{BASE_URL}{page_data["url"]}">'
    new_title = f'  <title>{page_data["title"]}</title>'
    new_desc = f'  <meta name="description" content="{page_data["description"]}">'

    # title タグ置換
    html = re.sub(r'  <title>.*?</title>', new_title, html)

    # description 置換
    html = re.sub(
        r'  <meta name="description" content=".*?".*?>',
        new_desc,
        html
    )

    # canonical タグを追加 (まだない場合)
    if 'rel="canonical"' not in html:
        html = html.replace(
            '  <meta name="description"',
            f'{canonical_tag}\n  <meta name="description"'
        )

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"OK: {page_key}")


base = "C:/Users/81909/sushi-blog"

for page_key, page_data in PAGES.items():
    filepath = os.path.join(base, page_key)
    if os.path.exists(filepath):
        fix_file(filepath, page_key, page_data)
    else:
        print(f"NG: ファイルが見つかりません: {filepath}")

print("\n全ページのSEO修正が完了しました。")
