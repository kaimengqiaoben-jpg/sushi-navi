# -*- coding: utf-8 -*-
"""実写素材から「気になる→見せる→満足感」の構成でバズ狙いのショート動画を量産する。
Higgsfield不使用。make_video.pyのヘルパーを流用し、スロー再生・テンポの速い
キャプション・モンタージュ（複数カットの繋ぎ）を追加。
"""
import subprocess
from pathlib import Path
import imageio_ffmpeg

from make_video import FFMPEG, FONT, run, fit_fontsize, concat_videos

BLOG_DIR = Path(__file__).parent


def hook_text_clip(base_clip: Path, text: str, out_path: Path, duration=1.5, w=720, h=1280, fontsize=64):
    """最初の1〜2秒だけ表示する、でかい文字のフックカード（動画の最初のフレームを静止画として使う）。"""
    frame_png = BLOG_DIR / "_hookframe.png"
    run([FFMPEG, "-y", "-i", str(base_clip), "-frames:v", "1", str(frame_png)])
    fs = fit_fontsize(text, max_width=w - 60, base=fontsize)
    drawtext = (
        f"drawtext=fontfile='{FONT}':text='{text}':fontcolor=yellow:fontsize={fs}:"
        f"box=1:boxcolor=black@0.7:boxborderw=24:x=(w-text_w)/2:y=(h-text_h)/2:borderw=3:bordercolor=black"
    )
    vf = f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},{drawtext}"
    run([
        FFMPEG, "-y", "-loop", "1", "-i", str(frame_png), "-t", str(duration),
        "-vf", vf, "-r", "30", "-pix_fmt", "yuv420p", "-an", str(out_path),
    ])
    frame_png.unlink()


def slow_clip(src: Path, start: float, dur: float, out_path: Path, speed=0.5, captions=None, w=720, h=1280):
    """指定区間をスロー再生にして書き出す（speed=0.5で半分の速さ=2倍の尺）。"""
    captions = captions or []
    filters = [f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h}", f"setpts={1/speed}*PTS"]
    for f, t, text in captions:
        fs = fit_fontsize(text, max_width=w - 60, base=48)
        filters.append(
            f"drawtext=fontfile='{FONT}':text='{text}':fontcolor=white:fontsize={fs}:"
            f"box=1:boxcolor=black@0.55:boxborderw=18:x=(w-text_w)/2:y=h-260:"
            f"enable='between(t,{f},{t})'"
        )
    vf = ",".join(filters)
    cmd = [
        FFMPEG, "-y", "-ss", str(start), "-i", str(src), "-t", str(dur),
        "-vf", vf, "-af", f"atempo={speed}",
        "-r", "30", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k",
        str(out_path),
    ]
    run(cmd)


def quick_clip(src: Path, start: float, dur: float, out_path: Path, captions=None, w=720, h=1280, mute=False):
    from make_video import make_captioned_clip
    make_captioned_clip(src, start, dur, captions or [], out_path, w, h)
    if mute:
        muted = out_path.with_suffix(".muted.mp4")
        run([FFMPEG, "-y", "-i", str(out_path), "-an", "-c:v", "copy", str(muted)])
        muted.replace(out_path)


if __name__ == "__main__":
    assets = BLOG_DIR / "youtube-scripts" / "assets"
    out_dir = BLOG_DIR / "youtube-scripts" / "output"
    out_dir.mkdir(exist_ok=True)
    footage = assets / "neta_01.mp4"

    # --- 動画A: スロー再生ASMR系(満足感型) ---
    hook = out_dir / "_a_hook.mp4"
    main = out_dir / "_a_main.mp4"
    quick_clip(footage, start=8, dur=2, out_path=hook, captions=[])
    hook_text_clip(hook, "包丁1本の仕事", hook, duration=1.2)
    slow_clip(footage, start=8, dur=10, out_path=main, speed=0.5, captions=[
        (0, 3, "スローで見る、プロの一太刀"),
        (16, 20, "鮨道 SUSHIDO"),
    ])
    concat_videos([hook, main], out_dir / "A_slow_satisfying.mp4")
    hook.unlink()
    main.unlink()
    print("完成: A_slow_satisfying.mp4")

    # --- 動画B: 早いカット割り(好奇心型モンタージュ) ---
    c1 = out_dir / "_b1.mp4"
    c2 = out_dir / "_b2.mp4"
    c3 = out_dir / "_b3.mp4"
    hookB = out_dir / "_b_hook.mp4"
    quick_clip(footage, start=0, dur=1.5, out_path=hookB, captions=[])
    hook_text_clip(hookB, "寿司屋のマグロ\nこうやって仕込まれてる", hookB, duration=1.8, fontsize=52)
    quick_clip(footage, start=2, dur=4, out_path=c1, captions=[(0, 4, "届いた塊をまず開ける")])
    quick_clip(footage, start=10, dur=4, out_path=c2, captions=[(0, 4, "血合いと筋を見極めて切る")])
    quick_clip(footage, start=38, dur=5, out_path=c3, captions=[(0, 3, "並べて完成"), (3, 5, "鮨道 SUSHIDO")])
    concat_videos([hookB, c1, c2, c3], out_dir / "B_curiosity_montage.mp4")
    for f in [hookB, c1, c2, c3]:
        f.unlink()
    print("完成: B_curiosity_montage.mp4")

    # --- 動画C: 質問フック+回答型 ---
    hookC = out_dir / "_c_hook.mp4"
    mainC = out_dir / "_c_main.mp4"
    quick_clip(footage, start=25, dur=1.5, out_path=hookC, captions=[])
    hook_text_clip(hookC, "なぜこの大きさで\n仕入れるか知ってますか？", hookC, duration=2.2, fontsize=48)
    quick_clip(footage, start=25, dur=20, out_path=mainC, captions=[
        (0, 4, "大きい塊のまま仕入れます"),
        (5, 9, "空気に触れる面を減らして"),
        (10, 14, "鮮度と食感を守るためです"),
        (17, 20, "続きは鮨道で"),
    ])
    concat_videos([hookC, mainC], out_dir / "C_question_payoff.mp4")
    hookC.unlink()
    mainC.unlink()
    print("完成: C_question_payoff.mp4")
