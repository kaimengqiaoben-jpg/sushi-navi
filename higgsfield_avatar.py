# -*- coding: utf-8 -*-
"""顔写真+台本音声からHiggsfieldのSpeech2Video系APIでアバター動画を生成する。
higgsfield_extend.py（実写動画の加工用）とは別用途 — こちらは静止画からの
AI生成のため、生成した動画には必ずAI生成である旨の開示（概要欄・テロップ）を付ける。

前提:
- higgsfield_key.json（またはHF_API_KEY_ID/HF_API_KEY_SECRET環境変数）が必要。
- エンドポイント/パラメータは docs.higgsfield.ai の Speech2Video 仕様と、
  実際のAPIキー取得後に突き合わせて調整すること（現時点では未検証の骨格）。

使い方:
  python higgsfield_avatar.py --photo <顔写真.jpg> --audio <台本音声.mp3> --out <出力.mp4>
"""
import argparse
import json
import sys
import time
from pathlib import Path

import requests

BLOG_DIR = Path(__file__).parent
KEY_FILE = BLOG_DIR / "higgsfield_key.json"
API_BASE = "https://api.higgsfield.ai"


def load_key():
    if KEY_FILE.exists():
        data = json.loads(KEY_FILE.read_text(encoding="utf-8"))
        return data["key_id"], data["key_secret"]
    import os
    key_id = os.environ.get("HF_API_KEY_ID")
    key_secret = os.environ.get("HF_API_KEY_SECRET")
    if not key_id or not key_secret:
        print("APIキーが見つかりません。higgsfield_key.json を用意するか環境変数を設定してください。")
        sys.exit(1)
    return key_id, key_secret


def auth_headers():
    key_id, key_secret = load_key()
    return {"Authorization": f"Key {key_id}:{key_secret}"}


def submit_job(photo_path: Path, audio_path: Path) -> str:
    headers = auth_headers()
    with open(photo_path, "rb") as pf, open(audio_path, "rb") as af:
        files = {
            "image": (photo_path.name, pf),
            "audio": (audio_path.name, af),
        }
        resp = requests.post(f"{API_BASE}/v1/speech2video", headers=headers, files=files, timeout=120)

    if resp.status_code >= 400:
        print(f"送信失敗: {resp.status_code} {resp.text}")
        sys.exit(1)

    body = resp.json()
    job_id = body.get("id") or body.get("job_id")
    if not job_id:
        print(f"ジョブIDが取得できませんでした: {body}")
        sys.exit(1)
    return job_id


def poll_job(job_id: str, interval=5, max_wait=900) -> str:
    headers = auth_headers()
    waited = 0
    while waited < max_wait:
        resp = requests.get(f"{API_BASE}/v1/jobs/{job_id}", headers=headers, timeout=30)
        if resp.status_code >= 400:
            print(f"ステータス取得失敗: {resp.status_code} {resp.text}")
            sys.exit(1)
        body = resp.json()
        status = body.get("status")
        print(f"  ステータス: {status}（{waited}秒経過）")
        if status in ("completed", "succeeded", "done"):
            url = body.get("output_url") or body.get("result_url") or (body.get("outputs") or [None])[0]
            if not url:
                print(f"完了したが出力URLが見つかりません: {body}")
                sys.exit(1)
            return url
        if status in ("failed", "error"):
            print(f"ジョブ失敗: {body}")
            sys.exit(1)
        time.sleep(interval)
        waited += interval
    print("タイムアウトしました")
    sys.exit(1)


def download(url: str, out_path: Path):
    resp = requests.get(url, timeout=120)
    resp.raise_for_status()
    out_path.write_bytes(resp.content)
    print(f"保存完了: {out_path}")
    print("注意: この動画はAI生成です。概要欄・動画内テロップに開示を入れてから投稿してください。")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--photo", required=True, help="顔写真のパス")
    parser.add_argument("--audio", required=True, help="台本を読み上げた音声ファイルのパス")
    parser.add_argument("--out", required=True, help="出力先パス")
    args = parser.parse_args()

    photo_path = Path(args.photo)
    audio_path = Path(args.audio)
    if not photo_path.exists():
        print(f"顔写真が見つかりません: {photo_path}")
        sys.exit(1)
    if not audio_path.exists():
        print(f"音声ファイルが見つかりません: {audio_path}")
        sys.exit(1)

    print(f"ジョブ送信中: {photo_path.name} + {audio_path.name}")
    job_id = submit_job(photo_path, audio_path)
    print(f"ジョブID: {job_id}")

    url = poll_job(job_id)
    download(url, Path(args.out))


if __name__ == "__main__":
    main()
