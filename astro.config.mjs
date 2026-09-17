// @ts-check
import { defineConfig } from 'astro/config';

import tailwindcss from '@tailwindcss/vite';
import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';

// https://astro.build/config
// NOTE: 2026-09-17時点、sushido.jp は未取得のため実際の公開URL（Vercelデフォルトドメイン）を使用。
// sushido.jp を取得してVercelにカスタムドメイン接続したら、ここを 'https://sushido.jp' に戻すこと
// （canonical/sitemap/OGP/RSSが全部このURLを基準に生成される）。
export default defineConfig({
  site: 'https://sushi-blog-five.vercel.app',
  vite: {
    plugins: [tailwindcss()]
  },

  integrations: [mdx(), sitemap()]
});
