#!/usr/bin/env python3
"""
寿司職人ナビ 毎日自動投稿スクリプト
- Claude APIで新記事HTML生成
- sitemap.xmlに追加
- GitHubにpush（Vercel自動デプロイ）
"""

import anthropic
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

BLOG_DIR = Path(__file__).parent
ARTICLES_DIR = BLOG_DIR / "articles"
SITEMAP_PATH = BLOG_DIR / "sitemap.xml"
TOPICS_PATH = BLOG_DIR / "article_topics.json"
BASE_URL = "https://sushi-blog-five.vercel.app"
ADSENSE_CLIENT = "ca-pub-6253147532269621"

ARTICLE_PROMPT = """あなたは寿司職人専門のSEOライターです。
以下の情報で寿司職人転職・スクールに関するSEOブログ記事のHTMLを生成してください。

記事タイトル: {title}
スラッグ: {slug}
ターゲットキーワード: {keywords}

# 要件
- 文字数：2500〜3500文字（本文のみ）
- 構成：H2見出し5〜6個、H3適宜
- ターゲット：未経験から寿司職人を目指す20〜40代
- トーン：親しみやすいが信頼できるプロのアドバイス
- CTAは自然に「寿司スクールへの問い合わせ」か「無料相談」を促す
- FAQ（3〜5問）を記事末尾に追加（FAQPageスキーマ用）

# 出力形式
以下のHTMLテンプレートを使って完全なHTMLページを出力してください（```htmlのコードブロックは不要、HTMLのみ）:

<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}｜寿司職人ナビ</title>
  <link rel="canonical" href="{base_url}/articles/{slug}.html">
  <meta name="description" content="[120〜150文字の説明文]">
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={adsense_client}" crossorigin="anonymous"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;600;700;900&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../css/style.css">
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [/* FAQを配列で */]
  }}
  </script>
</head>
<body>
  <header class="site-header">
    <div class="container">
      <a href="/" class="logo">🍣 寿司職人ナビ</a>
      <nav>
        <a href="/articles/sushi-chef-salary.html">年収</a>
        <a href="/articles/school-cost.html">スクール費用</a>
        <a href="/articles/career-change-beginner.html">転職方法</a>
      </nav>
    </div>
  </header>
  <main class="container article-content">
    <!-- 記事本文をここに -->
  </main>
  <footer class="site-footer">
    <div class="container">
      <p>&copy; 2025 寿司職人ナビ | <a href="/privacy.html">プライバシーポリシー</a></p>
    </div>
  </footer>
</body>
</html>
"""

def load_topics():
    with open(TOPICS_PATH, encoding="utf-8") as f:
        return json.load(f)

def save_topics(data):
    with open(TOPICS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_next_topic(topics_data):
    pending = topics_data.get("pending", [])
    if not pending:
        print("全トピック投稿済みです。article_topics.jsonにトピックを追加してください。")
        return None
    return pending[0]

def generate_article(topic):
    client = anthropic.Anthropic()

    prompt = ARTICLE_PROMPT.format(
        title=topic["title"],
        slug=topic["slug"],
        keywords="、".join(topic["keywords"]),
        base_url=BASE_URL,
        adsense_client=ADSENSE_CLIENT
    )

    print(f"記事生成中: {topic['title']}")

    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )

    return message.content[0].text

def save_article(slug, html_content):
    output_path = ARTICLES_DIR / f"{slug}.html"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"記事保存: {output_path}")
    return output_path

def update_sitemap(slug):
    url = f"{BASE_URL}/articles/{slug}.html"
    today = datetime.now().strftime("%Y-%m-%d")

    with open(SITEMAP_PATH, encoding="utf-8") as f:
        content = f.read()

    new_entry = f"""  <url>
    <loc>{url}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
"""

    # </urlset>の直前に挿入
    content = content.replace("</urlset>", new_entry + "</urlset>")

    with open(SITEMAP_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"サイトマップ更新: {url}")

def git_push(slug, title):
    try:
        subprocess.run(["git", "add", f"articles/{slug}.html", "sitemap.xml", "article_topics.json"],
                      cwd=BLOG_DIR, check=True)
        commit_msg = f"feat: 新記事追加「{title}」({datetime.now().strftime('%Y-%m-%d')})"
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=BLOG_DIR, check=True)
        subprocess.run(["git", "push", "origin", "main"], cwd=BLOG_DIR, check=True)
        print("GitHubにpush完了 → Vercel自動デプロイ開始")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Git操作エラー: {e}")
        return False

def main():
    # APIキーチェック
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("エラー: ANTHROPIC_API_KEY環境変数を設定してください")
        print("  set ANTHROPIC_API_KEY=sk-ant-...")
        sys.exit(1)

    topics_data = load_topics()
    topic = get_next_topic(topics_data)

    if not topic:
        sys.exit(0)

    # 記事生成
    html_content = generate_article(topic)

    # ファイル保存
    save_article(topic["slug"], html_content)

    # サイトマップ更新
    update_sitemap(topic["slug"])

    # トピックをpostedに移動
    topics_data["pending"].pop(0)
    topics_data["posted"].append({
        **topic,
        "posted_date": datetime.now().strftime("%Y-%m-%d")
    })
    save_topics(topics_data)

    # GitHub push
    git_push(topic["slug"], topic["title"])

    print(f"\n完了: {topic['title']}")
    print(f"URL: {BASE_URL}/articles/{topic['slug']}.html")

if __name__ == "__main__":
    main()
