// note有料記事ハブ用データ。SITE_DESIGN.md ⑧「note導線」参照。
//
// TODO(カイムさん): 各記事の url を note.com 上の「公開URL」（https://note.com/ユーザー名/n/xxxxxxxx の形式）に置き換えてください。
// note_post_queue.json にある editor.note.com/notes/.../publish/ は編集画面のURLで、
// 公開ページのURLではないため、そのままここには使えません。
// note.com のダッシュボードから「記事を見る」で開くURLをコピーしてください。

export interface NoteArticle {
  title: string;
  price: string;
  url: string | null;
  category: 'free' | 'single' | 'membership';
}

export const noteArticles: NoteArticle[] = [
  { title: '未経験から寿司職人になる方法【完全ロードマップ】', price: '無料', url: null, category: 'free' },
  { title: '寿司職人転職完全ガイド｜スクール選び・費用・就職まで', price: '500円', url: null, category: 'single' },
  { title: '寿司職人として海外移住・海外就職する完全マニュアル', price: '1,000円', url: null, category: 'single' },
  { title: '寿司職人の面接で落ちない答え方【想定問答10問テンプレート付き】', price: '200円', url: null, category: 'single' },
  { title: '寿司スクール費用シミュレーション：給付金使うと実質いくら？', price: '200円', url: null, category: 'single' },
  { title: 'ブラック寿司店を見抜く20のチェックリスト', price: '200円', url: null, category: 'single' },
  { title: '寿司職人転職の履歴書・職務経歴書テンプレート', price: '200円', url: null, category: 'single' },
  { title: '寿司店入社後の給与交渉マニュアル', price: '200円', url: null, category: 'single' },
  { title: '出張寿司を最速で始める手順書', price: '200円', url: null, category: 'single' },
  { title: '寿司職人のInstagramフォロワーを3ヶ月で1000人にする投稿戦略', price: '200円', url: null, category: 'single' },
  { title: 'ハローワークで給付金を申請する全手順', price: '200円', url: null, category: 'single' },
  { title: 'プロのシャリの作り方【酢の割合・温度・米の炊き方】完全レシピ', price: '200円', url: null, category: 'single' },
  { title: '寿司職人の包丁メンテナンス完全ガイド', price: '200円', url: null, category: 'single' },
  { title: '30代から寿司職人になった人のリアル体験談まとめ', price: '200円', url: null, category: 'single' },
  { title: '主要寿司スクール3校を実際に見学してわかったこと', price: '200円', url: null, category: 'single' },
  { title: '【12週間コース】寿司職人転職ロードマップ（Week1〜12）', price: '月額980円', url: null, category: 'membership' },
];
