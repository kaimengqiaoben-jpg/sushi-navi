# -*- coding: utf-8 -*-
"""既存の公開済みnote記事を編集して上書き保存する。"""
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright
import note_auto_post as m

BLOG_DIR = Path(__file__).parent
SESSION_FILE = BLOG_DIR / "note_session.json"


def parse_title_and_body(filepath: Path, price_marker: str | None, title_strip: str | None = None):
    text = filepath.read_text(encoding="utf-8").strip()
    lines = text.split("\n")
    title = ""
    body_lines = []
    for l in lines:
        if l.startswith("# ") and not title:
            title = l.lstrip("# ").strip()
            if title_strip:
                title = title.replace(title_strip, "").strip()
            continue
        if l.startswith("# "):
            continue
        if price_marker and price_marker in l:
            continue
        body_lines.append(l)
    body = "\n".join(body_lines).strip()
    if "\n---\n" in body:
        _, paid_part = body.split("\n---\n", 1)
        body = paid_part.strip()
    return title, body


def edit_article(page, note_id: str, new_body: str, new_title: str | None = None):
    url = f"https://editor.note.com/notes/{note_id}/edit/"
    page.goto(url, wait_until="domcontentloaded", timeout=60000)
    time.sleep(4)

    # AIポップアップなどを閉じる
    try:
        close_btn = page.locator('button[aria-label="閉じる"]').first
        if close_btn.is_visible(timeout=2000):
            close_btn.click()
            time.sleep(0.5)
    except Exception:
        pass

    if new_title:
        title_el = page.locator('[placeholder="記事タイトル"]').first
        try:
            if title_el.is_visible(timeout=3000):
                title_el.click()
                page.keyboard.press("Control+A")
                page.keyboard.press("Delete")
                time.sleep(0.2)
                title_el.fill(new_title)
                time.sleep(0.5)
        except Exception as e:
            print("タイトル更新失敗:", e)

    body_area = None
    for sel in [".ProseMirror", '[contenteditable="true"]']:
        el = page.locator(sel).first
        try:
            if el.is_visible(timeout=5000):
                body_area = el
                break
        except Exception:
            continue
    if body_area is None:
        print("本文エリアが見つかりません:", note_id)
        return False

    # 既存本文を全選択して削除
    body_area.click()
    page.keyboard.press("Control+A")
    time.sleep(0.3)
    page.keyboard.press("Delete")
    time.sleep(0.5)

    m._type_markdown(page, body_area, new_body)
    time.sleep(1)

    # 「一時保存」は下書きスナップショットのみで公開版に反映されない。
    # 新規投稿と同じ「公開に進む」→確認画面→最終ボタンのフローを通す必要がある。
    opened = m._click_first_visible(page, [
        'button:has-text("公開に進む")',
        'button:has-text("公開設定")',
    ], "公開に進むボタン", timeout=5000)
    if not opened:
        print("公開に進むボタンが見つかりませんでした:", note_id)
        page.screenshot(path=str(BLOG_DIR / f"edit_fail_{note_id}.png"))
        return False
    time.sleep(2)

    # ヘッダーの主要ボタン（「キャンセル」以外）を押して確認画面へ
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
        print("確認画面へ進めませんでした:", note_id)
        page.screenshot(path=str(BLOG_DIR / f"edit_fail_{note_id}.png"))
        return False
    time.sleep(1.5)

    # 最終更新ボタン（新規投稿時と文言が違う可能性があるので広めに探す）
    publish_btn = None
    for sel in ['button:has-text("更新する")', 'button:has-text("投稿する")', 'button:has-text("公開する")', 'button:has-text("更新")']:
        btn = page.locator(sel).first
        try:
            if btn.is_visible(timeout=5000):
                publish_btn = btn
                break
        except Exception:
            continue
    if publish_btn is None:
        print("最終更新ボタンが見つかりませんでした:", note_id)
        page.screenshot(path=str(BLOG_DIR / f"edit_fail_{note_id}.png"))
        return False
    try:
        publish_btn.click(timeout=5000)
    except Exception as e:
        print(f"クリックで例外（成功してる可能性あり）: {e}")
    time.sleep(3)

    print(f"編集・更新完了: {note_id} (現在のURL: {page.url})")
    page.screenshot(path=str(BLOG_DIR / f"edit_done_{note_id}.png"))
    return True


if __name__ == "__main__":
    # 使い方: python edit_note_article.py <note_id> <markdown_file> [price_marker] [title_strip]
    note_id = sys.argv[1]
    md_file = sys.argv[2]
    price_marker = sys.argv[3] if len(sys.argv) > 3 else None
    title_strip = sys.argv[4] if len(sys.argv) > 4 else None
    title, body = parse_title_and_body(BLOG_DIR / md_file, price_marker, title_strip)
    print("new title:", title)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(storage_state=str(SESSION_FILE))
        page = context.new_page()
        page.goto("https://note.com", wait_until="domcontentloaded", timeout=60000)
        time.sleep(2)
        if "login" in page.url:
            print("セッション切れです")
            sys.exit(1)
        edit_article(page, note_id, body, new_title=title)
        browser.close()
