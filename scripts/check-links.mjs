// 内部リンク整合性チェック（ビルド不要・自己検証用）
// 使い方: node scripts/check-links.mjs
import { readdirSync, readFileSync, statSync, existsSync } from 'node:fs';
import { join, relative } from 'node:path';

const ROOT = new URL('..', import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, '$1');
const CONTENT = join(ROOT, 'src', 'content');
const PAGES = join(ROOT, 'src', 'pages');

function walk(dir) {
  const out = [];
  for (const e of readdirSync(dir)) {
    const p = join(dir, e);
    if (statSync(p).isDirectory()) out.push(...walk(p));
    else out.push(p);
  }
  return out;
}

// 1. 有効なパスの集合を作る
const validPaths = new Set([
  '/', '/articles/', '/glossary/', '/about/', '/note/', '/contact/',
  '/disclosure/', '/privacy/', '/terms/', '/editorial-policy/', '/tools/db/',
  '/technique/', '/career/', '/tools/', '/overseas/', '/management/',
]);

const CATS = ['technique', 'career', 'tools', 'overseas', 'management'];
const contentFiles = walk(CONTENT).filter((f) => /\.(md|mdx)$/.test(f));
const bySlug = {};
const glossaryIds = new Set();
for (const f of contentFiles) {
  const rel = relative(CONTENT, f).replace(/\\/g, '/');
  const [col, ...rest] = rel.split('/');
  const id = rest.join('/').replace(/\.(md|mdx)$/, '');
  if (col === 'glossary') {
    validPaths.add(`/glossary/${id}/`);
    glossaryIds.add(id);
  } else if (CATS.includes(col)) {
    validPaths.add(`/${col}/${id}/`);
    (bySlug[col] ||= new Set()).add(id);
  }
}

// 2. 各記事のリンクと related を検証
let problems = 0;
const linkRe = /\]\((\/[^)]*)\)/g;
const relatedRe = /related:\s*\[([^\]]*)\]/;

for (const f of contentFiles) {
  const rel = relative(ROOT, f).replace(/\\/g, '/');
  const src = readFileSync(f, 'utf8');

  // inline links
  let m;
  while ((m = linkRe.exec(src))) {
    let href = m[1].split('#')[0];
    if (!href.endsWith('/')) href += '/';
    if (href.startsWith('/http')) continue;
    if (!validPaths.has(href)) {
      console.log(`✗ ${rel}\n    リンク切れ: ${m[1]}`);
      problems++;
    }
  }

  // related / relatedTerms slugs
  const isGlossary = rel.includes('/glossary/');
  const rm = src.match(isGlossary ? /relatedTerms:\s*\[([^\]]*)\]/ : relatedRe);
  if (rm) {
    const slugs = rm[1].split(',').map((s) => s.trim().replace(/['"]/g, '')).filter(Boolean);
    for (const s of slugs) {
      if (isGlossary) {
        if (!glossaryIds.has(s)) {
          console.log(`✗ ${rel}\n    relatedTerms の参照先が無い: ${s}`);
          problems++;
        }
      } else {
        const [col, ...rest] = s.split('/');
        const id = rest.join('/');
        if (!bySlug[col]?.has(id)) {
          console.log(`✗ ${rel}\n    related の参照先が無い: ${s}`);
          problems++;
        }
      }
    }
  }
}

// 3. vercel.json のリダイレクト先が有効か
const vj = join(ROOT, 'vercel.json');
if (existsSync(vj)) {
  const { redirects = [] } = JSON.parse(readFileSync(vj, 'utf8'));
  for (const r of redirects) {
    let dest = r.destination;
    if (!dest.endsWith('/')) dest += '/';
    if (!validPaths.has(dest)) {
      console.log(`✗ vercel.json\n    リダイレクト先が無い: ${r.source} -> ${r.destination}`);
      problems++;
    }
  }
}

console.log(`\n--- 記事 ${contentFiles.length}本 / 有効パス ${validPaths.size}件 / 問題 ${problems}件 ---`);
process.exit(problems ? 1 : 0);
