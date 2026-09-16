// draft記事の扱い: 開発時（astro dev）は表示、本番ビルド（astro build）は非表示。
// getCollection の filter に渡して使う。
export const isVisible = (entry: { data: { draft?: boolean } }) =>
  import.meta.env.PROD ? entry.data.draft !== true : true;
