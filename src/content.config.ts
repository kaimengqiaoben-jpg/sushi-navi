import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

// SITE_DESIGN.md ⑪ 記事のfrontmatter設計 に対応するスキーマ
const articleSchema = z.object({
  title: z.string(),
  description: z.string(),
  category: z.enum(['technique', 'career', 'tools', 'overseas', 'management']),
  tags: z.array(z.string()).default([]),
  publishedAt: z.coerce.date(),
  updatedAt: z.coerce.date(),
  author: z.string().default('kaimu'),
  hero: z.string().optional(),
  heroAlt: z.string().optional(),
  type: z.enum(['pillar', 'review', 'guide', 'experience', 'glossary']).default('guide'),
  draft: z.boolean().default(false),
  faq: z
    .array(
      z.object({
        q: z.string(),
        a: z.string(),
      })
    )
    .optional(),
  products: z
    .array(
      z.object({
        name: z.string(),
        asin: z.string().optional(),
        url: z.string().optional(),
        price: z.string().optional(),
      })
    )
    .optional(),
  related: z.array(z.string()).default([]),
  noteLink: z.string().optional(),
});

const makeArticleCollection = (dir: string) =>
  defineCollection({
    loader: glob({ pattern: '**/*.{md,mdx}', base: `./src/content/${dir}` }),
    schema: articleSchema,
  });

const technique = makeArticleCollection('technique');
const career = makeArticleCollection('career');
const tools = makeArticleCollection('tools');
const overseas = makeArticleCollection('overseas');
const management = makeArticleCollection('management');

const glossary = defineCollection({
  loader: glob({ pattern: '**/*.{md,mdx}', base: './src/content/glossary' }),
  schema: z.object({
    term: z.string(),
    reading: z.string().optional(),
    description: z.string(),
    relatedTerms: z.array(z.string()).default([]),
    publishedAt: z.coerce.date(),
    updatedAt: z.coerce.date(),
  }),
});

export const collections = {
  technique,
  career,
  tools,
  overseas,
  management,
  glossary,
};
