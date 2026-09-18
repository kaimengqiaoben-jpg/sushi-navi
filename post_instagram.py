# -*- coding: utf-8 -*-
"""instagram-posts/*.json のキャプションと、対応する動画ファイルをInstagramに投稿する（@kaimuha）。

前提:
- instagram-posts/<name>.json の同名動画（例: 01_knife_care.mp4）を同じフォルダに置いておく。
  動画自体はカイムさんが用意（実写、必要に応じて higgsfield_extend.py で加工済みのもの）。
- instagram_session.json はnote/Xと同じく、通常ブラウザでログイン後にDevToolsでcookieを
  コピーして用意する（自動ログインはボット検知で弾かれるため）。
- セレクタはInstagram Web版の実UIに対して未検証。1本テスト投稿してから --all を使うこと。

使い方:
  python post_instagram.py <name.json>   # 対応する動画1本を投稿
  python post_instagram.py --all         # instagram-posts/ 内の未投稿を全部投稿
"""
import argparse
import json
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

BLOG_DIR = Path(__file__).parent
POSTS_DIR = BLOG_DIR / "instagram-posts"
SESSION_FILE = BLOG_DIR / "instagram_session.json"
LOG_FILE = BLOG_DIR / "instagram_post_log.txt"
STATUS_FILE = BLOG_DIR / "instagram_post_status.json"
IG_HOME_URL = "https://www.instagram.com/"

VIDEO_EXTS = [".mp4", ".mov"]


def log(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def load_status():
    if STATUS_FILE.exists():
        return json.loads(STATUS_FILE.read_text(encoding="utf-8"))
    return {}


def save_status(status):
    STATUS_FILE.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding="utf-8")


def find_video(name_stem: str) -> Path | None:
    for ext in VIDEO_EXTS:
        p = POSTS_DIR / f"{name_stem}{ext}"
        if p.exists():
            return p
    return None


def click_first_visible(page, selectors, label, timeout=5000):
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


def post_video(page, video_path: Path, caption: str) -> bool:
    log(f"投稿開始: {video_path.name}")

    page.goto(IG_HOME_URL, wait_until="domcontentloaded", timeout=60000)
    time.sleep(2)

    if not click_first_visible(page, [
        'svg[aria-label="新規投稿"]',
        'svg[aria-label="New post"]',
        'a[href="#"]:has-text("作成")',
    ], "新規投稿ボタン"):
        page.screenshot(path=str(BLOG_DIR / "ig_debug_openfail.png"))
        return False
    time.sleep(1)

    try:
        file_input = page.locator('input[type="file"]').first
        file_input.set_input_files(str(video_path))
    except Exception as e:
        log(f"  ファイル選択失敗: {e}")
        page.screenshot(path=str(BLOG_DIR / "ig_debug_filefail.png"))
        return False
    time.sleep(3)

    # トリミング/フィルター画面を2回スキップ（「次へ」）
    for step in range(2):
        click_first_visible(page, [
            'button:has-text("次へ")',
            'button:has-text("Next")',
        ], f"次へボタン（{step+1}回目）", timeout=8000)
        time.sleep(1.5)

    caption_box = None
    for sel in [
        'div[aria-label="キャプションを入力…"]',
        'div[aria-label="Write a caption…"]',
        'div[contenteditable="true"][role="textbox"]',
    ]:
        try:
            el = page.locator(sel).first
            if el.is_visible(timeout=5000):
                caption_box = el
                break
        except Exception:
            continue
    if caption_box is None:
        log("  キャプション欄が見つかりません")
        page.screenshot(path=str(BLOG_DIR / "ig_debug_captionfail.png"))
        return False

    caption_box.click()
    time.sleep(0.3)
    page.keyboard.type(caption, delay=10)
    time.sleep(1)

    if not click_first_visible(page, [
        'button:has-text("シェア")',
        'button:has-text("Share")',
    ], "シェアボタン", timeout=8000):
        page.screenshot(path=str(BLOG_DIR / "ig_debug_sharefail.png"))
        return False

    time.sleep(5)
    log(f"投稿完了: {video_path.name}")
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", nargs="?", help="投稿定義ファイル名（instagram-posts/内、.json）")
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()

    status = load_status()

    if args.all:
        files = sorted(POSTS_DIR.glob("*.json"))
    elif args.file:
        files = [POSTS_DIR / args.file]
    else:
        print("ファイル名を指定するか --all を使ってください")
        sys.exit(1)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(storage_state=str(SESSION_FILE))
        page = context.new_page()
        page.goto(IG_HOME_URL, wait_until="domcontentloaded", timeout=60000)
        time.sleep(3)
        if "accounts/login" in page.url:
            log("セッション切れです。instagram_session.json を再取得してください")
            sys.exit(1)
        log("セッション確認OK")

        for f in files:
            if status.get(f.name) == "posted":
                continue
            post_def = json.loads(f.read_text(encoding="utf-8"))
            video_path = find_video(f.stem)
            if video_path is None:
                log(f"スキップ: {f.stem} の動画ファイルが見つかりません（instagram-posts/{f.stem}.mp4 を配置してください）")
                status[f.name] = "no_video"
                save_status(status)
                continue
            ok = post_video(page, video_path, post_def["caption"])
            status[f.name] = "posted" if ok else "error"
            save_status(status)
            time.sleep(120)

        browser.close()


if __name__ == "__main__":
    main()
