#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent
BASE_PATH = ROOT / "render_arrow_control_video.py"

spec = importlib.util.spec_from_file_location("arrow_base", BASE_PATH)
base = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(base)

base.W = 1920
base.H = 1080
base.ASS = ROOT / "arrow_control_bilingual_horizontal_hd16.ass"
base.OUT = ROOT / "小红书_飞出去的箭_横版16镜头高清版.mp4"
base.DESKTOP_OUT = Path("/Users/luca/Desktop/小红书_飞出去的箭_横版16镜头高清版.mp4")
base.RENDER = ROOT / "render_horizontal_hd16"
base.QC = ROOT / "qc_horizontal_hd16"

HD_FRAMES = [
    ROOT / "frames_hd16/01_archer_dawn.png",
    ROOT / "frames_hd16/02_arrow_release.png",
    ROOT / "frames_hd16/03_phone_anxiety.png",
    ROOT / "frames_hd16/04_creator_laptop.png",
    ROOT / "frames_hd16/05_after_game_bench.png",
    ROOT / "frames_hd16/06_chasing_results.png",
    ROOT / "frames_hd16/07_free_throw.png",
    ROOT / "frames_hd16/08_breath_pause.png",
    ROOT / "frames_hd16/09_process_detail.png",
    ROOT / "frames_hd16/10_notebook_process.png",
    ROOT / "frames_hd16/11_running_stride.png",
    ROOT / "frames_hd16/12_defensive_recovery.png",
    ROOT / "frames_hd16/13_phone_down.png",
    ROOT / "frames_hd16/14_morning_action.png",
    ROOT / "frames_hd16/15_symbolic_montage.png",
    ROOT / "frames_hd16/16_sunrise_court.png",
]


def build_horizontal_ass(duration: float) -> None:
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {base.W}
PlayResY: {base.H}
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: CN,{base.FONT},50,&H00FFFFFF,&H00FFFFFF,&H00050505,&H00000000,1,0,0,0,100,100,0,0,1,5,1,2,220,220,106,1
Style: EN,{base.FONT},24,&H00D8D0BD,&H00D8D0BD,&H00101010,&H00000000,0,0,0,0,100,100,0,0,1,3,0,2,260,260,54,1

[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
"""
    lines = [header]
    for start, end, cn, en in base.CAPTIONS:
        end = min(end, duration)
        lines.append(f"Dialogue: 0,{base.ass_time(start)},{base.ass_time(end)},CN,,0,0,0,,{base.apply_highlight(cn)}\n")
        lines.append(f"Dialogue: 1,{base.ass_time(start)},{base.ass_time(end)},EN,,0,0,0,,{base.wrap_en(en, 64)}\n")
    base.ASS.write_text("".join(lines), encoding="utf-8")


def main() -> None:
    for frame in HD_FRAMES:
        if not frame.exists():
            raise FileNotFoundError(frame)

    duration = base.audio_duration(base.AUDIO)
    build_horizontal_ass(duration)
    base.RENDER.mkdir(parents=True, exist_ok=True)
    base.QC.mkdir(parents=True, exist_ok=True)

    caption_text = "".join(cn for _, _, cn, _ in base.CAPTIONS)
    missing = base.normalize(base.SOURCE_SCRIPT).replace(base.normalize(caption_text), "")
    if missing:
        raise RuntimeError(f"Caption text does not match source script. Missing normalized text: {missing}")

    edges = [
        0.0,
        6.22,
        13.71,
        20.02,
        25.36,
        31.89,
        36.85,
        44.51,
        52.24,
        56.41,
        60.13,
        62.87,
        67.04,
        77.69,
        80.57,
        82.80,
        duration,
    ]
    segments = [
        base.render_segment(i, HD_FRAMES[i], edges[i], edges[i + 1])
        for i in range(len(HD_FRAMES))
    ]

    concat = base.RENDER / "concat.txt"
    concat.write_text("".join(f"file '{seg.name}'\n" for seg in segments), encoding="utf-8")
    silent = base.RENDER / "silent_hd16.mp4"
    base.run([
        str(base.FFMPEG), "-hide_banner", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(concat),
        "-c", "copy",
        str(silent),
    ])

    ass_path = str(base.ASS).replace("'", r"'\''")
    base.run([
        str(base.FFMPEG), "-hide_banner", "-y",
        "-i", str(silent),
        "-i", str(base.AUDIO),
        "-vf", f"subtitles='{ass_path}':fontsdir='/System/Library/Fonts',format=yuv420p",
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "17",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        str(base.OUT),
    ])

    for sec in [1, 6, 12, 18, 26, 34, 42, 50, 58, 66, 74, 83]:
        base.run([
            str(base.FFMPEG), "-hide_banner", "-y",
            "-ss", str(sec),
            "-i", str(base.OUT),
            "-frames:v", "1",
            str(base.QC / f"t_{sec:02d}s.jpg"),
        ])

    shutil.copy2(base.OUT, base.DESKTOP_OUT)
    manifest = {
        "audio": str(base.AUDIO),
        "duration_seconds": round(duration, 2),
        "output": str(base.OUT),
        "desktop_output": str(base.DESKTOP_OUT),
        "format": "1920x1080 landscape, 16 independent HD frames",
        "frames": [str(p) for p in HD_FRAMES],
        "caption_units": len(base.CAPTIONS),
        "subtitle_consistency": "caption Chinese text is an exact ordered split of the approved script",
        "qc_frames": [str(p) for p in sorted(base.QC.glob("*.jpg"))],
    }
    (ROOT / "render_manifest_horizontal_hd16.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
