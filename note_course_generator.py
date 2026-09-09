#!/usr/bin/env python3
"""
noteサブスクコース「寿司職人転職塾」記事生成スクリプト
月額980円のサブスクマガジン用コンテンツを生成します。

コース構成（全12回・3ヶ月分）:
  Week 1: 自己分析・転職準備
  Week 2: スクール選び実践
  Week 3: 費用・資金調達
  Week 4: 転職活動・面接
  Week 5: 現場の仕事術
  Week 6: 副業・独立準備
  ...
"""

import anthropic
import json
import os
import sys
from datetime import datetime
from pathlib import Path

BLOG_DIR = Path(__file__).parent
NOTE_DIR = BLOG_DIR / "note-articles"

COURSE_CURRICULUM = [
    {
        "week": 1,
        "price": "無料",
        "slug": "week01_self_analysis",
        "title": "【Week1】寿司職人転職の自己分析シート：あなたに向いているルートはどれ？",
        "summary": "転職前に必ず行うべき自己分析。スクール・弟子入り・独立、3ルートのどれが向いているかを診断シートで判定。",
        "content_points": [
            "3ルート（スクール/修行/独立）の向き不向き診断",
            "転職理由の整理ワーク（なぜ今転職したいか）",
            "現在のスキル棚卸しシート（調理経験・接客・語学）",
            "理想の1日スケジュールを描く",
            "次のステップ：スクール無料体験の申し込み手順"
        ]
    },
    {
        "week": 2,
        "price": "980円/月",
        "slug": "week02_school_selection",
        "title": "【Week2】スクール選び完全攻略：見学で必ず聞くべき10の質問",
        "summary": "スクール見学で後悔しない人が必ず聞いていること。失敗事例から学ぶ見学チェックリスト付き。",
        "content_points": [
            "スクール見学で聞くべき10の質問（リスト付き）",
            "講師の経歴確認方法（見分け方）",
            "卒業生の就職先を確認する方法",
            "営業トークに騙されないための判断基準",
            "複数スクールの比較シートの使い方"
        ]
    },
    {
        "week": 3,
        "price": "980円/月",
        "slug": "week03_funding",
        "title": "【Week3】スクール費用を最小化する給付金・ローン完全活用術",
        "summary": "給付金で最大70%オフ。申請手順・注意点・ローンとの組み合わせ方を完全解説。",
        "content_points": [
            "専門実践教育訓練給付金の申請ステップ（図解）",
            "ハローワーク訪問の手順と事前準備",
            "教育ローン審査に通るための準備",
            "給付金+ローン組み合わせシミュレーション（100万円スクールが実質30万に）",
            "申請タイミングで失敗しないための注意点"
        ]
    },
    {
        "week": 4,
        "price": "980円/月",
        "slug": "week04_job_hunting",
        "title": "【Week4】寿司職人転職活動の進め方：履歴書・面接・給与交渉",
        "summary": "料理人専門の転職市場の実態と、採用担当者が見ているポイントを現場目線で解説。",
        "content_points": [
            "寿司店の求人票の読み方（ブラック店の見分け方）",
            "履歴書・職務経歴書で評価されるポイント",
            "面接でよく聞かれる質問と回答例（未経験向け）",
            "試験（実技）がある場合の事前準備",
            "給与交渉のタイミングと言い方"
        ]
    },
    {
        "week": 5,
        "price": "980円/月",
        "slug": "week05_first_year",
        "title": "【Week5】入社1年目を乗り越えるための心構えと仕事術",
        "summary": "転職後に「こんなはずじゃなかった」にならないために。1年目でやること・やってはいけないことを現場経験から。",
        "content_points": [
            "1年目の現実（給料・労働時間・仕事内容）",
            "先輩職人に好かれる立ち回り方",
            "技術習得スピードを上げる自主練習法",
            "続けるか辞めるかの判断基準",
            "2年目に向けたキャリアアップ計画の立て方"
        ]
    },
    {
        "week": 6,
        "price": "980円/月",
        "slug": "week06_side_hustle",
        "title": "【Week6】副業出張寿司で月10万稼ぐ立ち上げロードマップ",
        "summary": "転職と並行して副業でも稼ぐ。出張寿司ビジネスの始め方を0から解説。",
        "content_points": [
            "出張寿司に必要な道具リストと初期費用（30〜50万円の内訳）",
            "最初の集客方法（SNS・ジモティー・Airbnb体験）",
            "料金設定の考え方（相場と利益計算）",
            "衛生管理・食中毒リスクの対策",
            "副業から独立へのステップアップ計画"
        ]
    },
    {
        "week": 7,
        "price": "980円/月",
        "slug": "week07_overseas",
        "title": "【Week7】海外で寿司職人として働く方法【ビザ・求人・年収】",
        "summary": "日本の2〜3倍稼げる海外市場の実態。ビザ取得から現地生活まで完全ガイド。",
        "content_points": [
            "国別年収比較（アメリカ・カナダ・オーストラリア・ドバイ）",
            "料理人向け就労ビザの種類と取り方",
            "英語ゼロから海外就職した実例",
            "海外求人サイト・エージェント一覧",
            "現地生活コストと手取り計算"
        ]
    },
    {
        "week": 8,
        "price": "980円/月",
        "slug": "week08_independent",
        "title": "【Week8】寿司店独立開業の全手順【物件・資金・仕入れ・集客】",
        "summary": "独立に必要な資金・物件選び・仕入れ先・集客まで、開業経験者の視点で整理。",
        "content_points": [
            "開業資金の目安と調達方法（日本政策金融公庫の融資）",
            "物件選びの条件と注意点",
            "食材仕入れ先の選び方（市場・業者・築地）",
            "開業前の許認可・手続き一覧",
            "集客ゼロからのSNS・食べログ攻略"
        ]
    },
    {
        "week": 9,
        "price": "980円/月",
        "slug": "week09_women",
        "title": "【Week9】女性が寿司職人になる方法【差別・働き方・成功事例】",
        "summary": "「女性は寿司を握れない」は昔の話。現代の女性寿司職人のリアルと成功ルート。",
        "content_points": [
            "女性寿司職人の現状（比率・活躍の場）",
            "女性が有利なシーン（接客・繊細な仕事）",
            "差別的な環境を避けるための職場選び",
            "育児と両立している先輩職人のインタビュー",
            "女性向けスクール・サポートがある職場一覧"
        ]
    },
    {
        "week": 10,
        "price": "980円/月",
        "slug": "week10_tax_finance",
        "title": "【Week10】寿司職人・フリーランス料理人のお金管理【節税・確定申告】",
        "summary": "稼いでも税金で持っていかれる前に。料理人が知っておくべき節税と確定申告の基本。",
        "content_points": [
            "フリーランス料理人が使える経費一覧",
            "確定申告の流れ（青色申告推奨の理由）",
            "消費税の仕組みとインボイス登録の判断",
            "老後の備え（個人型確定拠出年金iDeCo活用）",
            "税理士に頼むべきタイミング"
        ]
    },
    {
        "week": 11,
        "price": "980円/月",
        "slug": "week11_sns_marketing",
        "title": "【Week11】寿司職人がSNSで集客する方法【Instagram・TikTok・YouTube】",
        "summary": "フォロワー0から出張寿司・独立店の予約を埋める。料理人向けSNS集客の実践法。",
        "content_points": [
            "料理人が使うべきSNSの優先順位（Instagram>TikTok>YouTube）",
            "バズる寿司コンテンツの作り方",
            "Instagramで予約につながるプロフィール設計",
            "TikTokで職人の手技を見せる動画の撮り方",
            "DM→予約→リピートの導線設計"
        ]
    },
    {
        "week": 12,
        "price": "980円/月",
        "slug": "week12_final_action",
        "title": "【Week12（最終回）】転職塾卒業：今週中に動くべき3つのアクション",
        "summary": "3ヶ月間のまとめ。学んだことを実行に移すための最終アクションプランと個別相談案内。",
        "content_points": [
            "12週間の振り返りチェックリスト",
            "あなたのステージ別・今週やること（まだ悩んでいる人・決断した人・動き始めた人）",
            "よくある後悔トップ5と対策",
            "読者限定：個別LINEコンサル（初回無料）の案内",
            "次のステップ：より深い内容のコンテンツ案内"
        ]
    }
]

NOTE_ARTICLE_PROMPT = """あなたはnote向けの寿司職人転職コーチです。
以下の情報でnoteサブスクマガジン「寿司職人転職塾」の記事を書いてください。

Week番号: {week}
記事タイトル: {title}
価格帯: {price}
概要: {summary}
盛り込む内容ポイント:
{content_points}

# 執筆ルール
- 文字数：2000〜3000文字
- 読者：寿司職人に転職を考えている20〜40代（未経験〜経験1〜2年）
- トーン：コーチが受講生に語りかけるような温かみのある文体
- マークダウン形式（noteに貼り付けられる形式）
- 冒頭に読者の悩みに寄り添う導入（3〜5行）
- 各ポイントに「アクション」ボックスを設ける（### ✅ アクション という見出しで）
- 末尾にnoteサブスク登録を促すCTA（「次回のWeekXでは〜を解説します」）
- 有料部分は「---ここから先は月額980円で読めます---」という区切り線を入れる（Week1の無料記事は不要）

# 出力
マークダウン形式のみで出力してください。コードブロックなし。
"""

def generate_note_article(curriculum_item):
    client = anthropic.Anthropic()

    content_points_str = "\n".join(f"- {p}" for p in curriculum_item["content_points"])

    prompt = NOTE_ARTICLE_PROMPT.format(
        week=curriculum_item["week"],
        title=curriculum_item["title"],
        price=curriculum_item["price"],
        summary=curriculum_item["summary"],
        content_points=content_points_str
    )

    print(f"  生成中: Week{curriculum_item['week']} {curriculum_item['title'][:30]}...")

    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )

    return message.content[0].text

def save_note_article(item, content):
    filename = f"week{item['week']:02d}_{item['slug'].split('_', 1)[1]}.md"
    output_path = NOTE_DIR / filename
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  保存: {output_path}")
    return output_path

def main():
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("エラー: ANTHROPIC_API_KEY環境変数を設定してください")
        sys.exit(1)

    # コマンドライン引数でweek番号を指定可能
    target_weeks = None
    if len(sys.argv) > 1:
        target_weeks = [int(w) for w in sys.argv[1:]]
        print(f"指定Week: {target_weeks}")
    else:
        print("全12回を生成します（約5〜10分かかります）")

    NOTE_DIR.mkdir(exist_ok=True)

    generated = []
    for item in COURSE_CURRICULUM:
        if target_weeks and item["week"] not in target_weeks:
            continue

        output_path = NOTE_DIR / f"week{item['week']:02d}_{item['slug'].split('_', 1)[1]}.md"
        if output_path.exists():
            print(f"  スキップ（既存）: Week{item['week']}")
            continue

        content = generate_note_article(item)
        save_note_article(item, content)
        generated.append(item)

    print(f"\n完了: {len(generated)}記事を生成しました")
    print(f"保存先: {NOTE_DIR}")
    print()
    print("=== noteへの投稿手順 ===")
    print("1. note.com にログイン")
    print("2. 「マガジン」→「新しいマガジンを作成」")
    print("3. マガジン名: 寿司職人転職塾")
    print("4. 価格: 月額980円 / 定期購読マガジン")
    print("5. note-articlesフォルダの.mdファイルをWeek順に投稿")
    print("6. Week1のみ無料・全文公開、Week2〜は有料設定")

if __name__ == "__main__":
    main()
