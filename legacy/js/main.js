// =====================
// 寿司職人ナビ - メインJS
// =====================

// Google AdSense 自動広告（全ページ共通）
// ※ ca-pub-XXXXXXXXXXXXXXXXXX を自分のパブリッシャーIDに差し替えること
(function() {
  var s = document.createElement('script');
  s.async = true;
  s.src = 'https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-6253147532269621';
  s.setAttribute('crossorigin', 'anonymous');
  document.head.appendChild(s);
})();

document.addEventListener('DOMContentLoaded', () => {

  // ハンバーガーメニュー
  const hamburger = document.querySelector('.hamburger');
  const nav = document.querySelector('nav');
  if (hamburger && nav) {
    hamburger.addEventListener('click', () => {
      nav.classList.toggle('open');
    });
  }

  // スムーススクロール
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        if (nav) nav.classList.remove('open');
      }
    });
  });

  // アフィリエイトリンクのUTMパラメータ自動付与
  document.querySelectorAll('a[data-affiliate]').forEach(link => {
    const base = link.href;
    const source = link.dataset.affiliate;
    link.href = `${base}?utm_source=sushi-navi&utm_medium=affiliate&utm_campaign=${source}`;
    link.setAttribute('target', '_blank');
    link.setAttribute('rel', 'noopener noreferrer nofollow');
  });

  // 目次の自動生成（記事ページ用）
  const tocContainer = document.getElementById('toc');
  if (tocContainer) {
    const headings = document.querySelectorAll('.article-body h2');
    if (headings.length > 0) {
      const ol = document.createElement('ol');
      headings.forEach((h, i) => {
        h.id = `section-${i + 1}`;
        const li = document.createElement('li');
        const a = document.createElement('a');
        a.href = `#section-${i + 1}`;
        a.textContent = h.textContent;
        li.appendChild(a);
        ol.appendChild(li);
      });
      tocContainer.appendChild(ol);
    }
  }

  // スクロールで現れるアニメーション
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll('.card, .affiliate-banner, .compare-table').forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(20px)';
    el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
    observer.observe(el);
  });

  // visible クラス追加でアニメーション発火
  const style = document.createElement('style');
  style.textContent = `.visible { opacity: 1 !important; transform: translateY(0) !important; }`;
  document.head.appendChild(style);

});
