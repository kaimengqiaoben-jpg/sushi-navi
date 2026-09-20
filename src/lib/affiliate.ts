import { AMAZON_ASSOCIATE_TAG } from '../data/config';

// Amazon検索結果への直リンクを作る。個別ASINが未確定の商品はこれで代用する。
export function amazonSearchUrl(query: string): string | undefined {
  if (!AMAZON_ASSOCIATE_TAG) return undefined;
  const params = new URLSearchParams({ k: query, tag: AMAZON_ASSOCIATE_TAG });
  return `https://www.amazon.co.jp/s?${params.toString()}`;
}
