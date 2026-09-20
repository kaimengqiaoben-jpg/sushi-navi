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

// Google AdSenseのパブリッシャーID。
// 審査待ちの間もタグ自体は出しておいて問題ない（審査に必要な場合もある）。
// AdSenseの管理画面（adsense.google.com）で
// このサイト（sushi-blog-five.vercel.app、または取得後はsushido.jp）を
// 「サイト」に追加して審査状況を確認すること。
export const ADSENSE_CLIENT_ID: string | null = 'ca-pub-6253147532269621';

// お問い合わせフォームの送信先（Formspree）。
// 1. https://formspree.io で無料アカウント作成（メールアドレス1つでOK、公開されない）
// 2. 「New Form」でフォームを作成すると、確認メールが届く→リンクをクリックして認証
// 3. ダッシュボードに表示される「Form ID」（例: xanyzabc のような文字列。
//    エンドポイントは https://formspree.io/f/xanyzabc という形）をここに設定
export const CONTACT_FORM_ID: string | null = 'xjykykpg';
