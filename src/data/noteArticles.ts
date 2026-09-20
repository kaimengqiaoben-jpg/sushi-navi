// note有料記事ハブ用データ。SITE_DESIGN.md ⑧「note導線」参照。
//
// 2026-09-10: note.com上の実際の公開状態を確認し、確認できたものだけ url を設定済み。
// アカウント: https://note.com/modern_roses2643
// 2026-09-18: プロフィール名・自己紹介を「鮨道 SUSHIDO」ブランドに更新済み（連携確認・修正済み）。
//
// 注記: 02・03（費用シミュレーション／ブラック店チェックリスト）は投稿時に有料設定が失敗し、
// 実際には無料公開になっている（note_post_log.txt で確認）。price は実際の価格に合わせてある。
// note.com側で200円に設定し直せば price を書き換えるだけで反映される。
//
// url が null の記事は、投稿ログ上「下書きのまま」または「未投稿」（最終公開ボタンが見つからず失敗、
// または一度もキューに入っていない）で、公開URLが確認できていないもの。
// note.comのダッシュボードで実際に公開されていることを確認できたら url を埋めてください。

export interface NoteArticle {
  title: string;
  price: string;
  url: string | null;
  category: 'free' | 'single' | 'membership';
}

export const noteArticles: NoteArticle[] = [
  {
    title: '現役寿司職人が「鮨道」というサイトを始めました',
    price: '無料',
    url: 'https://note.com/modern_roses2643/n/n71a90f2aab8d',
    category: 'free',
  },
  {
    title: '寿司屋で使われる符丁10選【がり・あがり・むらさき…】',
    price: '無料',
    url: 'https://note.com/modern_roses2643/n/n7e5c25c29895',
    category: 'free',
  },
  {
    title: '現役寿司職人が実際に使っている柳刃包丁、3本の使い分け',
    price: '無料',
    url: 'https://note.com/modern_roses2643/n/n75a9d7d261db',
    category: 'free',
  },
  {
    title: '未経験から寿司職人になる方法【完全ロードマップ】',
    price: '無料',
    url: 'https://note.com/modern_roses2643/n/nb173df126476',
    category: 'free',
  },
  {
    title: '寿司職人の1日、実際どう過ぎてるか書きます',
    price: '無料',
    url: 'https://note.com/modern_roses2643/n/neb4d077d8a50',
    category: 'free',
  },
  {
    title: '寿司職人の給料、ステージ別に正直に書きます',
    price: '無料',
    url: 'https://note.com/modern_roses2643/n/n8f2a2d1b5ac5',
    category: 'free',
  },
  {
    title: '「寿司職人は10年修行」って本当なのか、分解してみます',
    price: '無料',
    url: 'https://note.com/modern_roses2643/n/nae6a85b7dd11',
    category: 'free',
  },
  {
    title: '寿司職人なのに、出刃包丁を持ってない理由',
    price: '無料',
    url: 'https://note.com/modern_roses2643/n/n837aaa42c3de',
    category: 'free',
  },
  {
    title: '寿司職人に向いてる人、向いてない人',
    price: '無料',
    url: 'https://note.com/modern_roses2643/n/n7940d5489114',
    category: 'free',
  },
  {
    title: '寿司職人転職完全ガイド｜スクール選び・費用・就職まで',
    price: '500円',
    url: 'https://note.com/modern_roses2643/n/n5912b56150be',
    category: 'single',
  },
  {
    title: '寿司職人として海外移住・海外就職する完全マニュアル',
    price: '1,000円',
    url: 'https://note.com/modern_roses2643/n/nda325c873135',
    category: 'single',
  },
  { title: '寿司職人の面接で落ちない答え方【想定問答10問テンプレート付き】', price: '200円', url: null, category: 'single' },
  {
    title: '寿司スクール費用シミュレーション：給付金使うと実質いくら？',
    price: '無料', // 本来200円想定だったが有料設定が失敗し無料公開中
    url: 'https://note.com/modern_roses2643/n/n6fbdeb14df3a',
    category: 'free',
  },
  {
    title: 'ブラック寿司店を見抜く20のチェックリスト',
    price: '無料', // 本来200円想定だったが有料設定が失敗し無料公開中
    url: 'https://note.com/modern_roses2643/n/nf6aac2eef858',
    category: 'free',
  },
  {
    title: '寿司職人転職の履歴書・職務経歴書テンプレート',
    price: '200円',
    url: 'https://note.com/modern_roses2643/n/ncf9a048ad279',
    category: 'single',
  },
  {
    title: '寿司店入社後の給与交渉マニュアル',
    price: '200円',
    url: 'https://note.com/modern_roses2643/n/nd1593b0f5063',
    category: 'single',
  },
  {
    title: '出張寿司を最速で始める手順書',
    price: '200円',
    url: 'https://note.com/modern_roses2643/n/n55f2e9dad24a',
    category: 'single',
  },
  {
    title: '寿司職人のInstagramフォロワーを3ヶ月で1000人にする投稿戦略',
    price: '200円',
    url: 'https://note.com/modern_roses2643/n/n9ac6e4950dc7',
    category: 'single',
  },
  {
    title: 'ハローワークで給付金を申請する全手順',
    price: '200円',
    url: 'https://note.com/modern_roses2643/n/ndb5bffbb73a7',
    category: 'single',
  },
  {
    title: 'プロのシャリの作り方【酢の割合・温度・米の炊き方】完全レシピ',
    price: '200円',
    url: 'https://note.com/modern_roses2643/n/n3860ab6063d7',
    category: 'single',
  },
  {
    title: '寿司職人の包丁メンテナンス完全ガイド',
    price: '200円',
    url: 'https://note.com/modern_roses2643/n/n238ac2c894e7',
    category: 'single',
  },
  {
    title: '30代から寿司職人になった人のリアル体験談まとめ',
    price: '200円',
    url: 'https://note.com/modern_roses2643/n/nd9b0e541fb03',
    category: 'single',
  },
  {
    title: '主要寿司スクール3校を実際に見学してわかったこと',
    price: '200円',
    url: 'https://note.com/modern_roses2643/n/nf4b4d94bbb5c',
    category: 'single',
  },
  { title: '【12週間コース】寿司職人転職ロードマップ（Week1〜12）', price: '月額980円', url: null, category: 'membership' },
];
