# -*- coding: utf-8 -*-
"""実写素材から、顔写真の導入カード+本編字幕付きの短尺動画を作る（Higgsfield不使用、実写のみ）。
ffmpegはimageio-ffmpeg経由のバイナリを使用（別途インストール不要）。

使い方例はファイル末尾のmain()参照。
"""
import subprocess
from pathlib import Path
import imageio_ffmpeg

BLOG_DIR = Path(__file__).parent
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
FONT = "C\\:/Windows/Fonts/NotoSansJP-VF.ttf"  # ffmpegフィルタ内のコロンは要エスケープ


def run(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if result.returncode != 0:
        print("STDERR:", (result.stderr or "")[-3000:])
        raise RuntimeError(f"ffmpeg failed: {' '.join(cmd)}")
    return result


def fit_fontsize(text: str, max_width: int, base=48) -> int:
    """全角文字数から、指定幅に収まるフォントサイズを概算する。"""
    approx_width = len(text) * base
    if approx_width <= max_width:
        return base
    return max(22, int(base * max_width / approx_width))


def make_intro_card(photo_path: Path, text: str, out_path: Path, duration=3, w=720, h=1280):
    """顔写真を使った導入カード（静止画+テキスト、指定秒数の動画にする。1行のみ対応）。"""
    fontsize = fit_fontsize(text, max_width=w - 80, base=54)
    drawtext = (
        f"drawtext=fontfile='{FONT}':text='{text}':fontcolor=white:fontsize={fontsize}:"
        f"box=1:boxcolor=black@0.5:boxborderw=20:x=(w-text_w)/2:y=h-280"
    )
    vf = f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},{drawtext}"
    cmd = [
        FFMPEG, "-y", "-loop", "1", "-i", str(photo_path),
        "-t", str(duration), "-vf", vf,
        "-r", "30", "-pix_fmt", "yuv420p",
        "-an",
        str(out_path),
    ]
    run(cmd)


def make_captioned_clip(src_path: Path, start: float, dur: float, captions: list, out_path: Path, w=720, h=1280):
    """本編クリップを指定区間だけ切り出し、時間指定の字幕を焼き込む。
    captions: [(from_sec, to_sec, text), ...]（クリップ内の相対秒）
    """
    filters = [f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h}"]
    for f, t, text in captions:
        fontsize = fit_fontsize(text, max_width=w - 60, base=48)
        filters.append(
            f"drawtext=fontfile='{FONT}':text='{text}':fontcolor=white:fontsize={fontsize}:"
            f"box=1:boxcolor=black@0.55:boxborderw=18:x=(w-text_w)/2:y=h-260:"
            f"enable='between(t,{f},{t})'"
        )
    vf = ",".join(filters)
    cmd = [
        FFMPEG, "-y", "-ss", str(start), "-i", str(src_path), "-t", str(dur),
        "-vf", vf, "-r", "30", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k",
        str(out_path),
    ]
    run(cmd)


def concat_videos(parts: list, out_path: Path):
    list_file = BLOG_DIR / "_concat_list.txt"
    list_file.write_text("\n".join(f"file '{p.as_posix()}'" for p in parts), encoding="utf-8")
    cmd = [
        FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", str(list_file),
        "-c:v", "libx264", "-c:a", "aac", "-pix_fmt", "yuv420p",
        str(out_path),
    ]
    run(cmd)
    list_file.unlink()


if __name__ == "__main__":
    assets = BLOG_DIR / "youtube-scripts" / "assets"
    out_dir = BLOG_DIR / "youtube-scripts" / "output"
    out_dir.mkdir(exist_ok=True)

    photo = assets / "kaimu_face_01.jpg"
    footage = assets / "neta_01.mp4"

    # --- 動画1: マグロの仕込みショート（顔写真の導入カード + 本編45秒） ---
    intro = out_dir / "_intro.mp4"
    main_clip = out_dir / "_main.mp4"
    make_intro_card(photo, "現役寿司職人の仕込みに密着", intro, duration=3)
    make_captioned_clip(
        footage, start=5, dur=45,
        captions=[
            (0, 3, "マグロを仕込む"),
            (18, 22, "血合いや筋を見ながら切り分けます"),
            (40, 43, "続きは鮨道で"),
            (43, 45, "sushi-blog-five.vercel.app"),
        ],
        out_path=main_clip,
    )
    concat_videos([intro, main_clip], out_dir / "01_maguro_shikomi_short.mp4")
    intro.unlink()
    main_clip.unlink()
    print("完成: 01_maguro_shikomi_short.mp4")

    # --- 動画2: X/Instagram用ティザー（12秒、キャプションのみ） ---
    make_captioned_clip(
        footage, start=8, dur=12,
        captions=[
            (0, 3, "本物の仕込み、見せます"),
            (9, 12, "鮨道 SUSHIDO"),
        ],
        out_path=out_dir / "02_teaser_12s.mp4",
    )
    print("完成: 02_teaser_12s.mp4")
