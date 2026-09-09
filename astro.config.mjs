// @ts-check
import { defineConfig } from 'astro/config';

import tailwindcss from '@tailwindcss/vite';
import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';

// https://astro.build/config
// NOTE: site は sushido.jp 取得後にそのまま有効化される想定（現状は仮値）。
// ドメイン確定後、Vercel側のカスタムドメイン設定と合わせて変更不要。
export default defineConfig({
  site: 'https://sushido.jp',
  vite: {
    plugins: [tailwindcss()]
  },

  integrations: [mdx(), sitemap()]
});
