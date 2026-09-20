// draft記事の扱い: 開発時（astro dev）は表示、本番ビルド（astro build）は非表示。
// getCollection の filter に渡して使う。
export const isVisible = (entry: { data: { draft?: boolean } }) =>
  import.meta.env.PROD ? entry.data.draft !== true : true;

// 記事が1本も無いカテゴリーを除いた一覧を返す（空の一覧ページへの導線を作らないため）。
import { getCollection } from 'astro:content';
import { categoryList } from '../data/categories';

export async function getVisibleCategories() {
  const withCounts = await Promise.all(
    categoryList.map(async (c) => {
      const entries = await getCollection(c.slug as any, isVisible);
      return { ...c, hasArticles: entries.length > 0 };
    })
  );
  return withCounts.filter((c) => c.hasArticles);
}
