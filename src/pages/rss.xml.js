import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';
import { isVisible } from '../lib/content';
import { categories } from '../data/categories';

const CATS = ['technique', 'career', 'tools', 'overseas', 'management'];

export async function GET(context) {
  const all = (
    await Promise.all(
      CATS.map(async (slug) => {
        const entries = await getCollection(slug, isVisible);
        return entries.map((e) => ({
          title: e.data.title,
          description: e.data.description,
          pubDate: e.data.publishedAt,
          link: `/${slug}/${e.id}/`,
          categories: [categories[slug].label],
        }));
      })
    )
  ).flat();

  all.sort((a, b) => b.pubDate.valueOf() - a.pubDate.valueOf());

  return rss({
    title: '鮨道 SUSHIDO',
    description: '現役寿司職人が、板場から書く。技術・道具・キャリア・海外・経営の専門メディア。',
    site: context.site,
    items: all,
    customData: `<language>ja</language>`,
  });
}
