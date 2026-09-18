# -*- coding: utf-8 -*-
"""実写素材をHiggsfield APIで加工・拡張する（完全生成ではなく、実写ベースの加工用途）。

前提:
- console.higgsfield.ai でAPIアカウント作成・USD残高チャージ・APIキー発行が必要（本人対応のみ）。
- HF_API_KEY_ID / HF_API_KEY_SECRET を higgsfield_key.json（gitignore対象）か環境変数で渡す。
- エンドポイント/パラメータ名は公開情報（docs.higgsfield.ai）から分かる範囲での実装であり、
  実際にAPIキーを取得したら docs.higgsfield.ai/docs の最新仕様と突き合わせて要調整。
  ここでは「認証ヘッダ形式: Authorization: Key {id}:{secret}」「ベースURL: https://api.higgsfield.ai」
  「非同期ジョブ（投げてポーリング）」という確認済みの骨格のみ実装している。

使い方:
  python higgsfield_extend.py --input <実写動画 or 画像パス> --prompt "スローモーションで手元を強調" --out <出力パス>
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
        print('higgsfield_key.json の例: {"key_id": "...", "key_secret": "..."}')
        sys.exit(1)
    return key_id, key_secret


def auth_headers():
    key_id, key_secret = load_key()
    return {
        "Authorization": f"Key {key_id}:{key_secret}",
        "Content-Type": "application/json",
    }


def submit_job(input_path: Path, prompt: str) -> str:
    """実写の画像/動画を元に加工ジョブを投げ、ジョブIDを返す。
    NOTE: アップロード方式（署名付きURL経由か直接multipartか）は要検証。
    ここでは直接ファイルをmultipartで送る想定の実装にしてある。"""
    headers = auth_headers()
    headers.pop("Content-Type", None)  # multipartはrequestsに任せる

    with open(input_path, "rb") as f:
        files = {"file": (input_path.name, f)}
        data = {"prompt": prompt}
        resp = requests.post(f"{API_BASE}/v1/image2video", headers=headers, files=files, data=data, timeout=120)

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
    """完了までポーリングし、出力アセットのURLを返す。"""
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="実写素材（動画/画像）のパス")
    parser.add_argument("--prompt", required=True, help="加工内容の指示（例: スローモーション、背景ぼかし等）")
    parser.add_argument("--out", required=True, help="出力先パス")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"入力ファイルが見つかりません: {input_path}")
        sys.exit(1)

    print(f"ジョブ送信中: {input_path.name}")
    job_id = submit_job(input_path, args.prompt)
    print(f"ジョブID: {job_id}")

    url = poll_job(job_id)
    download(url, Path(args.out))


if __name__ == "__main__":
    main()
