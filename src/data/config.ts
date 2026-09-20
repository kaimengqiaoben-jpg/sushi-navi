// サイト全体の設定値。ログインが必要でClaudeが取得できない値はここに集約し、
// カイムさんがIDを1個入れるだけで有効になるようにしてある。

// GA4のトラッキングID（例: "G-XXXXXXXXXX"）。
// Google Analyticsで新しいプロパティ（データストリーム: ウェブ、URL は
// https://sushi-blog-five.vercel.app）を作成すると発行される。
// 取得したらここに文字列として貼り付けるだけで、全ページで計測が始まる。
export const GA_MEASUREMENT_ID: string | null = 'G-8Q6G703G6E';

// Amazonアソシエイトのトラッキングタグ。
// 180日間売上が無いと失効する仕組みなので、Amazonアソシエイトの管理画面
// （associates.amazon.co.jp）でステータスを確認してから使うこと。
export const AMAZON_ASSOCIATE_TAG: string | null = 'sushinavi-22';
