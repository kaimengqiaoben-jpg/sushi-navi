# 🍣 寿司職人ナビ - デプロイ手順書

## 現在の完成ファイル一覧

```
sushi-blog/
├── index.html                        ← トップページ
├── about.html                        ← サイト紹介
├── privacy.html                      ← プライバシーポリシー
├── affiliate.html                    ← アフィリエイト開示
├── css/style.css                     ← 全ページ共通スタイル
├── js/main.js                        ← 全ページ共通JS
└── articles/
    ├── sushi-school-compare.html     ← スクール比較（最重要CV記事）
    ├── career-change-beginner.html   ← 未経験転職ガイド
    └── sushi-chef-salary.html        ← 年収記事
```

---

## STEP 1：Vercelで無料公開（所要時間：10分）

### 1-1. GitHubにアップロード

1. https://github.com にアクセスしてアカウント作成（無料）
2. 「New repository」→ リポジトリ名：`sushi-navi` → Create
3. 「uploading an existing file」をクリック
4. `sushi-blog` フォルダ内の全ファイルをドラッグ＆ドロップ
5. 「Commit changes」をクリック

### 1-2. Vercelに接続

1. https://vercel.com にアクセス → 「GitHubでログイン」
2. 「New Project」→ `sushi-navi` を選択 → 「Deploy」
3. 数分でサイトが公開される（URLが発行される）

**→ これで無料で公開完了！**

---

## STEP 2：独自ドメイン取得（任意・所要時間：30分）

### おすすめドメイン候補

| ドメイン | 特徴 | 年額 |
|---|---|---|
| `sushi-shoku-navi.com` | わかりやすい | 約1,500円 |
| `sushishoku-navi.jp` | 日本向け・信頼感 | 約3,000円 |
| `sushi-career.com` | シンプル | 約1,500円 |

### 取得方法
1. お名前.com（https://www.onamae.com）でドメイン購入
2. Vercelの「Domains」設定でドメインを追加
3. お名前.comのDNS設定でVercelのネームサーバーを指定

---

## STEP 3：アフィリエイトASP登録

### 優先登録順

| ASP | 登録URL | 目的 |
|---|---|---|
| A8.net | https://www.a8.net | 料理スクール案件 |
| バリューコマース | https://www.valuecommerce.com | クックビズ（転職） |
| もしもアフィリエイト | https://af.moshimo.com | Amazon |

### 登録後にやること
1. 各ASPで「寿司」「料理スクール」「飲食 転職」で案件検索
2. 提携申請する
3. 発行されたアフィリエイトリンクをHTMLの `href="https://example-..."` の部分に貼り替える

---

## STEP 4：アフィリエイトリンクの貼り替え方

各記事の以下の箇所を実際のアフィリエイトリンクに変更：

```html
<!-- 変更前 -->
<a href="https://example-school-1.com" ...>

<!-- 変更後（A8.netで発行されたリンクに差し替え）-->
<a href="https://px.a8.net/svt/ejp?a8mat=XXXXXX" ...>
```

---

## STEP 5：Google Search Console登録（SEO必須）

1. https://search.google.com/search-console にアクセス
2. サイトのURLを登録
3. サイトマップを送信（sitemap.xml）

---

## 今後追加すべき記事（優先順）

1. `articles/knife-recommend.html` — 包丁おすすめ（Amazon CV）
2. `articles/independent-guide.html` — 独立・開業ガイド
3. `articles/license-guide.html` — 資格・免許ガイド
4. `articles/career-30s.html` — 30代転職成功インタビュー
5. `articles/school-tokyo-sushi.html` — 東京すし和食料理学院レビュー（単体）

---

## 月50万達成ロードマップ

| 時期 | 目標PV | 目標収益 | やること |
|---|---|---|---|
| 1ヶ月目 | 500PV | 0〜3万 | デプロイ・ASP登録・記事5本追加 |
| 2ヶ月目 | 2,000PV | 5〜10万 | 記事10本追加・SNS開始 |
| 3ヶ月目 | 8,000PV | 15〜25万 | 内部リンク最適化・有料note販売 |
| 6ヶ月目 | 30,000PV | 30〜50万 | スクールと直接提携交渉 |
