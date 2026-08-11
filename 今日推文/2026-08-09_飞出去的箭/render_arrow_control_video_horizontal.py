#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent
BASE_PATH = ROOT / "render_arrow_control_video.py"

spec = importlib.util.spec_from_file_location("arrow_vertical", BASE_PATH)
base = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(base)


base.W = 1920
base.H = 1080
base.ASS = ROOT / "arrow_control_bilingual_horizontal.ass"
base.OUT = ROOT / "小红书_飞出去的箭_横版双语字幕版.mp4"
base.DESKTOP_OUT = Path("/Users/luca/Desktop/小红书_飞出去的箭_横版双语字幕版.mp4")
base.RENDER = ROOT / "render_horizontal"
base.QC = ROOT / "qc_horizontal"


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


base.build_ass = build_horizontal_ass


def main() -> None:
    base.main()
    manifest_path = ROOT / "render_manifest_horizontal.json"
    source_manifest = ROOT / "render_manifest.json"
    if source_manifest.exists():
        data = json.loads(source_manifest.read_text(encoding="utf-8"))
        data["output"] = str(base.OUT)
        data["desktop_output"] = str(base.DESKTOP_OUT)
        data["format"] = "1920x1080 landscape"
        data["ass"] = str(base.ASS)
        data["qc_frames"] = [str(p) for p in sorted(base.QC.glob("*.jpg"))]
        manifest_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    if base.OUT.exists():
        shutil.copy2(base.OUT, base.DESKTOP_OUT)
    print(base.OUT)
    print(base.DESKTOP_OUT)


if __name__ == "__main__":
    main()
