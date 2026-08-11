#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import re
import shutil
import subprocess
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parent
FFMPEG = Path("/Users/luca/bin/ffmpeg")
AUDIO = Path("/Users/luca/Desktop/8月9日.mp3")
STORYBOARD = ROOT / "高级动画故事板_12镜头.png"
FRAMES = ROOT / "frames"
RENDER = ROOT / "render"
QC = ROOT / "qc"
ASS = ROOT / "arrow_control_bilingual.ass"
OUT = ROOT / "小红书_飞出去的箭_双语字幕版.mp4"
DESKTOP_OUT = Path("/Users/luca/Desktop/小红书_飞出去的箭_双语字幕版.mp4")

W, H = 1080, 1920
FPS = 30
FONT = "/System/Library/Fonts/STHeiti Medium.ttc"

SOURCE_SCRIPT = (
    "你最累的地方，不是努力。"
    "是你一直想控制那支已经飞出去的箭。"
    "斯多葛哲学里有一个故事。"
    "一个弓箭手，在拉弓之前，可以控制站姿、呼吸、角度和力量。"
    "可箭一旦离弦，风怎么吹，靶子会不会晃，旁人怎么评价，就不再归他管。"
    "很多人的痛苦也在这里。"
    "投完简历之后，反复刷新消息。"
    "发完作品之后，一直盯着数据。"
    "打一场比赛之后，脑子里只剩别人怎么看你。"
    "你以为自己还在努力，其实你是在追一支已经飞出去的箭。"
    "真正厉害的运动员，不是完全不在乎结果。"
    "而是他知道，比赛里唯一能训练的，是下一次动作。"
    "罚球前的呼吸，跑步时的步频，落后时的站位，失误后的回防。"
    "这些，才是还握在手里的东西。"
    "心理学里，这叫把注意力从结果目标，拉回过程目标。"
    "你越想控制结果，焦虑越大。"
    "你越能控制动作，力量越稳。"
    "所以今天别问：为什么还没有回报。"
    "先问：我今天能不能把一个动作做好。"
    "该投的简历投出去，该练的动作练完，该说的话说清楚，该睡的觉睡够。"
    "你不是输给命运。"
    "你只是把太多力气，用在了控制风上。"
    "箭已经飞出去了。"
    "把手收回来。"
    "准备下一次拉弓。"
)


CAPTIONS = [
    (0.47, 2.46, "你最累的地方，不是努力。", "The exhausting part is not effort."),
    (2.88, 5.60, "是你一直想控制那支已经飞出去的箭。", "It is trying to control the arrow after release."),
    (6.22, 8.05, "斯多葛哲学里有一个故事。", "There is a Stoic story."),
    (8.67, 13.30, "一个弓箭手，在拉弓之前，可以控制站姿、呼吸、角度和力量。", "Before release, the archer controls stance, breath, angle, and force."),
    (13.71, 19.59, "可箭一旦离弦，风怎么吹，靶子会不会晃，旁人怎么评价，就不再归他管。", "Once the arrow leaves, wind, target, and judgment are no longer his."),
    (20.02, 21.77, "很多人的痛苦也在这里。", "This is where many people suffer."),
    (22.24, 24.73, "投完简历之后，反复刷新消息。", "After sending resumes, they keep refreshing."),
    (25.36, 27.71, "发完作品之后，一直盯着数据。", "After posting, they keep staring at numbers."),
    (28.25, 31.38, "打一场比赛之后，脑子里只剩别人怎么看你。", "After a game, all they hear is other people's judgment."),
    (31.89, 36.37, "你以为自己还在努力，其实你是在追一支已经飞出去的箭。", "You think you are still working. You are chasing an arrow already gone."),
    (36.85, 40.05, "真正厉害的运动员，不是完全不在乎结果。", "Great athletes do not ignore results."),
    (40.50, 44.09, "而是他知道，比赛里唯一能训练的，是下一次动作。", "They know the only trainable thing is the next action."),
    (44.51, 51.77, "罚球前的呼吸，跑步时的步频，落后时的站位，失误后的回防。这些，才是还握在手里的东西。", "Breath, rhythm, spacing, recovery defense. These are still in your hands."),
    (52.24, 55.77, "心理学里，这叫把注意力从结果目标，拉回过程目标。", "In psychology, this is shifting from outcome goals to process goals."),
    (56.41, 59.72, "你越想控制结果，焦虑越大。", "The more you control results, the more anxious you become."),
    (60.13, 62.34, "你越能控制动作，力量越稳。", "The more you control actions, the steadier your power becomes."),
    (62.87, 66.64, "所以今天别问：为什么还没有回报。", "So today, do not ask why the reward has not arrived."),
    (67.04, 69.25, "先问：我今天能不能把一个动作做好。", "Ask whether you can do one action well today."),
    (69.81, 77.13, "该投的简历投出去，该练的动作练完，该说的话说清楚，该睡的觉睡够。", "Send it. Practice it. Say it clearly. Sleep enough."),
    (77.69, 80.57, "你不是输给命运。你只是把太多力气，", "You did not lose to fate."),
    (81.12, 82.80, "用在了控制风上。", "You spent too much strength trying to control the wind."),
    (82.80, 83.60, "箭已经飞出去了。", "The arrow has already flown."),
    (83.60, 84.53, "把手收回来。准备下一次拉弓。", "Bring your hand back. Prepare the next draw."),
]

HIGHLIGHTS = [
    "不是努力",
    "飞出去的箭",
    "不再归他管",
    "反复刷新",
    "一直盯着数据",
    "别人怎么看你",
    "下一次动作",
    "还握在手里",
    "过程目标",
    "焦虑越大",
    "力量越稳",
    "一个动作",
    "控制风",
    "下一次拉弓",
]


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if proc.returncode != 0:
        raise subprocess.CalledProcessError(proc.returncode, cmd, proc.stdout, proc.stderr)
    return proc


def audio_duration(path: Path) -> float:
    proc = subprocess.run([str(FFMPEG), "-hide_banner", "-i", str(path)], capture_output=True, text=True)
    match = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", proc.stderr)
    if not match:
        raise RuntimeError(f"Cannot read audio duration: {path}")
    h, m, s = match.groups()
    return int(h) * 3600 + int(m) * 60 + float(s)


def ass_time(value: float) -> str:
    h = int(value // 3600)
    m = int((value % 3600) // 60)
    s = value % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def esc(text: str) -> str:
    return text.replace("{", "").replace("}", "").replace("\n", r"\N")


def normalize(text: str) -> str:
    return re.sub(r"[，。！？；：、“”‘’\s,.!?:;\"']", "", text)


def wrap_cn(text: str, limit: int = 17) -> str:
    text = esc(text)
    if len(text) <= limit:
        return text
    marks = "，。；：、"
    lines: list[str] = []
    rest = text
    while len(rest) > limit:
        cut = -1
        for i in range(min(limit, len(rest) - 1), 8, -1):
            if rest[i] in marks:
                cut = i + 1
                break
        if cut == -1:
            cut = limit
        lines.append(rest[:cut])
        rest = rest[cut:]
    if rest:
        lines.append(rest)
    return r"\N".join(lines[:3])


def wrap_en(text: str, limit: int = 44) -> str:
    words = esc(text).split()
    lines: list[str] = []
    cur: list[str] = []
    for word in words:
        candidate = " ".join(cur + [word])
        if len(candidate) > limit and cur:
            lines.append(" ".join(cur))
            cur = [word]
        else:
            cur.append(word)
    if cur:
        lines.append(" ".join(cur))
    return r"\N".join(lines[:2])


def apply_highlight(text: str) -> str:
    wrapped = wrap_cn(text)
    for word in sorted(HIGHLIGHTS, key=len, reverse=True):
        wrapped = wrapped.replace(word, rf"{{\c&H3CD3FF&\b1}}{word}{{\c&HFFFFFF&\b0}}")
    return wrapped


def crop_storyboard() -> list[Path]:
    FRAMES.mkdir(parents=True, exist_ok=True)
    img = Image.open(STORYBOARD).convert("RGB")
    sw, sh = img.size
    cell_w = sw / 4
    cell_h = sh / 3
    out: list[Path] = []
    for row in range(3):
        for col in range(4):
            pad_x = int(cell_w * 0.01)
            pad_y = int(cell_h * 0.01)
            left = int(col * cell_w + pad_x)
            top = int(row * cell_h + pad_y)
            right = int((col + 1) * cell_w - pad_x)
            bottom = int((row + 1) * cell_h - pad_y)
            frame = img.crop((left, top, right, bottom))
            target = FRAMES / f"frame_{row * 4 + col + 1:02d}.png"
            frame.save(target)
            out.append(target)
    return out


def render_segment(index: int, source: Path, start: float, end: float) -> Path:
    duration = end - start
    out = RENDER / f"seg_{index:02d}.mp4"
    modes = [
        ("1.045+0.020*t/{d}", "iw/2-(iw/{z})/2+10*sin(t*0.42)", "ih/2-(ih/{z})/2-18*t/{d}"),
        ("1.060-0.012*t/{d}", "iw/2-(iw/{z})/2-16*t/{d}", "ih/2-(ih/{z})/2+8*sin(t*0.6)"),
        ("1.050+0.016*t/{d}", "iw/2-(iw/{z})/2+18*t/{d}", "ih/2-(ih/{z})/2"),
        ("1.055+0.012*sin(t*0.45)", "iw/2-(iw/{z})/2", "ih/2-(ih/{z})/2+14*t/{d}"),
    ]
    zoom, x, y = modes[index % len(modes)]
    zoom = zoom.format(d=duration)
    x = x.format(d=duration, z=zoom)
    y = y.format(d=duration, z=zoom)
    overlays = []
    if index in {0, 1, 10}:
        overlays.append(f"drawbox=x='80+820*t/{duration}':y=1460:w=90:h=5:color=0xffd33c@0.62:t=fill")
    if index in {4, 5, 6, 8}:
        overlays.append(f"drawbox=x='920-380*t/{duration}':y='260+50*sin(t)':w=4:h=780:color=0xffd33c@0.24:t=fill")
    overlay_filter = ",".join(overlays)
    if overlay_filter:
        overlay_filter += ","
    vf = (
        f"scale={W}:{H}:force_original_aspect_ratio=increase,"
        f"crop={W}:{H},"
        f"scale='iw*{zoom}':'ih*{zoom}':eval=frame,"
        f"crop={W}:{H}:x='{x}':y='{y}',"
        "eq=contrast=1.045:saturation=1.02,"
        "unsharp=5:5:0.55,"
        f"{overlay_filter}"
        "vignette=PI/5,"
        "noise=alls=2:allf=t+u,"
        "format=yuv420p"
    )
    run([
        str(FFMPEG), "-hide_banner", "-y",
        "-loop", "1", "-t", f"{duration:.3f}",
        "-i", str(source),
        "-vf", vf,
        "-r", str(FPS),
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "17",
        "-pix_fmt", "yuv420p",
        str(out),
    ])
    return out


def build_ass(duration: float) -> None:
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: CN,{FONT},58,&H00FFFFFF,&H00FFFFFF,&H00050505,&H00000000,1,0,0,0,100,100,0,0,1,5,1,2,96,96,520,1
Style: EN,{FONT},27,&H00D8D0BD,&H00D8D0BD,&H00101010,&H00000000,0,0,0,0,100,100,0,0,1,3,0,2,112,112,420,1

[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
"""
    lines = [header]
    for start, end, cn, en in CAPTIONS:
        end = min(end, duration)
        lines.append(f"Dialogue: 0,{ass_time(start)},{ass_time(end)},CN,,0,0,0,,{apply_highlight(cn)}\n")
        lines.append(f"Dialogue: 1,{ass_time(start)},{ass_time(end)},EN,,0,0,0,,{wrap_en(en)}\n")
    ASS.write_text("".join(lines), encoding="utf-8")


def render_contact_sheet(frames: list[Path]) -> Path:
    out = ROOT / "动画镜头总览.jpg"
    inputs: list[str] = []
    for frame in frames:
        inputs.extend(["-i", str(frame)])
    labels = "".join(
        f"[{i}:v]scale=270:480:force_original_aspect_ratio=increase,crop=270:480[v{i}];"
        for i in range(12)
    )
    layout = "0_0|270_0|540_0|810_0|0_480|270_480|540_480|810_480|0_960|270_960|540_960|810_960"
    graph = labels + "".join(f"[v{i}]" for i in range(12)) + f"xstack=inputs=12:layout={layout}"
    run([str(FFMPEG), "-hide_banner", "-y", *inputs, "-filter_complex", graph, "-frames:v", "1", str(out)])
    return out


def main() -> None:
    if not FFMPEG.exists():
        raise FileNotFoundError(FFMPEG)
    if not AUDIO.exists():
        raise FileNotFoundError(AUDIO)
    if not STORYBOARD.exists():
        raise FileNotFoundError(STORYBOARD)

    RENDER.mkdir(parents=True, exist_ok=True)
    QC.mkdir(parents=True, exist_ok=True)
    duration = audio_duration(AUDIO)
    build_ass(duration)

    caption_text = "".join(cn for _, _, cn, _ in CAPTIONS)
    missing = normalize(SOURCE_SCRIPT).replace(normalize(caption_text), "")
    if missing:
        raise RuntimeError(f"Caption text does not match source script. Missing normalized text: {missing}")

    frames = crop_storyboard()
    segment_edges = [0.0, 6.2, 13.7, 20.0, 28.25, 36.85, 44.51, 52.24, 60.13, 67.04, 77.69, 82.80, duration]
    segments = [render_segment(i, frames[i], segment_edges[i], segment_edges[i + 1]) for i in range(12)]

    concat = RENDER / "concat.txt"
    concat.write_text("".join(f"file '{seg.name}'\n" for seg in segments), encoding="utf-8")
    silent = RENDER / "silent.mp4"
    run([
        str(FFMPEG), "-hide_banner", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(concat),
        "-c", "copy",
        str(silent),
    ])

    ass_path = str(ASS).replace("'", r"'\''")
    run([
        str(FFMPEG), "-hide_banner", "-y",
        "-i", str(silent),
        "-i", str(AUDIO),
        "-vf", f"subtitles='{ass_path}':fontsdir='/System/Library/Fonts',format=yuv420p",
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        str(OUT),
    ])

    sheet = render_contact_sheet(frames)
    for sec in [1, 8, 16, 31, 45, 58, 70, 83]:
        run([
            str(FFMPEG), "-hide_banner", "-y",
            "-ss", str(sec),
            "-i", str(OUT),
            "-frames:v", "1",
            str(QC / f"t_{sec:02d}s.jpg"),
        ])

    shutil.copy2(OUT, DESKTOP_OUT)
    manifest = {
        "audio": str(AUDIO),
        "duration_seconds": round(duration, 2),
        "output": str(OUT),
        "desktop_output": str(DESKTOP_OUT),
        "storyboard": str(STORYBOARD),
        "contact_sheet": str(sheet),
        "caption_units": len(CAPTIONS),
        "subtitle_consistency": "caption Chinese text is an exact ordered split of the approved script",
        "qc_frames": [str(p) for p in sorted(QC.glob("*.jpg"))],
    }
    (ROOT / "render_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
