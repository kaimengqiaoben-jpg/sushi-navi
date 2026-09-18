# -*- coding: utf-8 -*-
"""note.com に無料記事を投稿する（note_auto_post.py の有料版から price/paywall 処理を除いたもの）。"""
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

BLOG_DIR = Path(__file__).parent
FREE_DIR = BLOG_DIR / "note-articles" / "free_new"
SESSION_FILE = BLOG_DIR / "note_session.json"
LOG_FILE = BLOG_DIR / "free_post_log.txt"
NOTE_NEW_URL = "https://note.com/notes/new"
HASHTAGS = ["寿司職人", "鮨道", "SUSHIDO", "未経験転職", "寿司"]

FILES = [
    "01_sushido_start.md",
    "02_sushiya_jargon.md",
    "03_my_knives.md",
]


def log(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def parse(filepath: Path):
    text = filepath.read_text(encoding="utf-8").strip()
    lines = text.split("\n")
    title = ""
    for l in lines:
        if l.startswith("# "):
            title = l.lstrip("# ").strip()
            break
    body_lines = [l for l in lines if not l.startswith("# ") and "※この記事は無料" not in l]
    body = "\n".join(body_lines).strip()
    return {"title": title, "body": body}


def type_markdown(page, element, text):
    page.evaluate(
        """([el, txt]) => { el.focus(); document.execCommand('insertText', false, txt); }""",
        [element.element_handle(), text],
    )
    time.sleep(0.5)


def click_first_visible(page, selectors, label, timeout=3000):
    for sel in selectors:
        try:
            btn = page.locator(sel).first
            if btn.is_visible(timeout=timeout):
                btn.click()
                return True
        except Exception:
            continue
    log(f"  {label}が見つからず")
    return False


def post_one(page, article):
    log(f"投稿開始: {article['title']}")
    try:
        page.goto(NOTE_NEW_URL, wait_until="domcontentloaded", timeout=60000)
    except Exception:
        time.sleep(3)
        page.goto(NOTE_NEW_URL, wait_until="domcontentloaded", timeout=60000)
    time.sleep(3)

    title_ok = False
    for sel in ['[placeholder="記事タイトル"]', 'h1[contenteditable="true"]']:
        el = page.locator(sel).first
        try:
            if el.is_visible(timeout=3000):
                el.click()
                el.fill(article["title"])
                title_ok = True
                break
        except Exception:
            continue
    if not title_ok:
        log("  タイトル入力エリアが見つかりません")
        return None
    time.sleep(1)

    body_area = None
    for sel in [".ProseMirror", '[contenteditable="true"]', '[role="textbox"]']:
        el = page.locator(sel).first
        try:
            if el.is_visible(timeout=3000):
                body_area = el
                break
        except Exception:
            continue
    if body_area is None:
        log("  本文エリアが見つかりません")
        return None
    body_area.click()
    time.sleep(0.5)
    type_markdown(page, body_area, article["body"])
    time.sleep(1)

    # 公開設定を開く（価格は設定しない＝無料のまま）
    opened = click_first_visible(page, [
        'button:has-text("公開に進む")',
        'button:has-text("公開設定")',
        'button:has-text("公開する")',
        'button:has-text("投稿設定")',
    ], "公開設定ボタン", timeout=5000)
    if not opened:
        log("  公開設定が開けませんでした")
        return None
    time.sleep(2)

    # ハッシュタグ
    try:
        for sel in ['input[placeholder*="タグ"]', 'input[placeholder*="tag"]']:
            el = page.locator(sel).first
            if el.is_visible(timeout=2000):
                for tag in HASHTAGS:
                    el.fill(tag)
                    el.press("Enter")
                    time.sleep(0.3)
                log("  タグ入力OK")
                break
    except Exception:
        log("  タグ入力フィールドが見つからず")

    # ヘッダーの主要ボタン（「キャンセル」以外）を押して次画面へ
    proceeded = False
    header_buttons = page.locator("div.fixed.top-0.z-20 button")
    for i in range(header_buttons.count()):
        btn = header_buttons.nth(i)
        txt = btn.inner_text().strip()
        if txt and txt != "キャンセル":
            btn.click()
            proceeded = True
            break
    if not proceeded:
        log("  確認画面へ進めませんでした")
        page.screenshot(path=str(BLOG_DIR / "free_debug_fail.png"))
        return None
    time.sleep(1.5)

    # 最終公開ボタン
    publish_btn = None
    for sel in ['button:has-text("投稿する")', 'button:has-text("公開する")', 'button:has-text("投稿")']:
        btn = page.locator(sel).first
        try:
            if btn.is_visible(timeout=5000):
                publish_btn = btn
                break
        except Exception:
            continue
    if publish_btn is None:
        log("  最終公開ボタンが見つかりませんでした")
        page.screenshot(path=str(BLOG_DIR / "free_debug_fail.png"))
        return None
    try:
        publish_btn.click(timeout=5000)
    except Exception as e:
        log(f"  クリックで例外（公開自体は成功してる可能性あり）: {e}")
    time.sleep(2)

    published = False
    try:
        published = page.locator("text=記事をシェアしてみましょう").first.is_visible(timeout=5000)
    except Exception:
        pass
    if not published:
        log("  投稿完了を確認できませんでした")
        page.screenshot(path=str(BLOG_DIR / "free_debug_fail.png"))
        return None

    time.sleep(2)
    url = page.url
    log(f"投稿完了: {url}")
    try:
        page.wait_for_load_state("networkidle", timeout=10000)
    except Exception:
        pass
    return url


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(storage_state=str(SESSION_FILE))
        page = context.new_page()

        page.goto("https://note.com/notes/new", wait_until="domcontentloaded", timeout=60000)
        time.sleep(2)
        if "login" in page.url:
            log("セッション切れです")
            browser.close()
            return
        log("セッション確認OK")

        for fname in FILES:
            article = parse(FREE_DIR / fname)
            if not article["title"]:
                log(f"  タイトル取得失敗: {fname}")
                continue
            url = post_one(page, article)
            print(f"RESULT\t{fname}\t{url}")
            time.sleep(60)

        browser.close()


if __name__ == "__main__":
    main()
