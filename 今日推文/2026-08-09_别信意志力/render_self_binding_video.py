#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import re
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parent
FFMPEG = Path("/Users/luca/bin/ffmpeg")
AUDIO = Path("/Users/luca/Desktop/8月9日 (2).mp3")
FRAMES = ROOT / "frames_hd16"
RENDER = ROOT / "render"
QC = ROOT / "qc"
ASS = ROOT / "self_binding_bilingual.ass"
OUT = ROOT / "小红书_别信意志力_横版16镜头高清版.mp4"
DESKTOP_OUT = Path("/Users/luca/Desktop/小红书_别信意志力_横版16镜头高清版.mp4")
COVER = ROOT / "封面_别信意志力_横版.png"
DESKTOP_COVER = Path("/Users/luca/Desktop/封面_别信意志力_横版.png")

W, H = 1920, 1080
FPS = 30
FONT = "/System/Library/Fonts/STHeiti Medium.ttc"

SOURCE_SCRIPT = (
    "你以为自律，是靠意志力硬扛。"
    "但哲学里有个更残酷的故事。"
    "奥德修斯经过海妖所在的海域时，知道自己一定会被歌声诱惑。"
    "他没有说：我够强，我能忍住。"
    "他做了一件很聪明的事。"
    "让水手把自己绑在桅杆上。"
    "然后命令所有人，不管他怎么喊，都不能把他放下来。"
    "这不是懦弱。"
    "这是清醒。"
    "真正成熟的人，不是假装自己永远理性。"
    "而是提前承认：我也会冲动，我也会分心，我也会在情绪上头的时候做错选择。"
    "体育里也是一样。"
    "真正高水平的运动员，不是每天都靠热血训练。"
    "他靠的是固定时间、固定动作、固定恢复、固定复盘。"
    "因为他知道，比赛不会奖励情绪。"
    "比赛只奖励系统。"
    "普通人最容易输的地方，也不是不努力。"
    "是每天都把自己放在诱惑面前。"
    "手机放在枕边，却怪自己熬夜。"
    "一边说要存钱，一边刷着消费内容。"
    "一边说要成长，一边让情绪决定今天做不做。"
    "你不是没有自控力。"
    "你只是太相信临场发挥。"
    "心理学里有个概念，叫情境设计。"
    "一个人真正的改变，不是等自己突然变强。"
    "而是先把环境改到不容易失败。"
    "想早睡，就别把手机放床边。"
    "想训练，就提前把鞋放门口。"
    "想少内耗，就别在深夜做人生判断。"
    "想变好，就给自己设计一条更容易走对的路。"
    "奥德修斯不是因为意志力强，才活着穿过海妖。"
    "他是因为知道自己会被诱惑，所以提前把自己绑住。"
    "这才是真正的自律。"
    "不是永远不动摇。"
    "而是在清醒的时候，保护那个将来会动摇的自己。"
)

CAPTIONS = [
    (0.54, 2.70, "你以为自律，是靠意志力硬扛。", "You think discipline means forcing yourself."),
    (3.22, 5.32, "但哲学里有个更残酷的故事。", "But philosophy has a harsher story."),
    (5.94, 8.53, "奥德修斯经过海妖所在的海域时，", "When Odysseus passed the sirens,"),
    (9.00, 11.00, "知道自己一定会被歌声诱惑。", "he knew the song would tempt him."),
    (11.54, 12.34, "他没有说：", "He did not say:"),
    (12.66, 14.03, "我够强，我能忍住。", "I am strong enough."),
    (14.54, 18.40, "他做了一件很聪明的事。", "He made a smarter choice."),
    (18.79, 20.07, "让水手把自己绑在桅杆上。", "He had sailors tie him to the mast."),
    (20.55, 21.55, "然后命令所有人，", "Then he ordered everyone,"),
    (22.04, 24.29, "不管他怎么喊，都不能把他放下来。", "no matter what he shouted, do not release him."),
    (24.90, 28.50, "这不是懦弱。", "That is not weakness."),
    (28.98, 30.05, "这是清醒。", "That is clarity."),
    (30.55, 32.34, "真正成熟的人，不是假装自己永远理性。", "Mature people do not pretend they are always rational."),
    (32.90, 35.78, "而是提前承认：我也会冲动，", "They admit in advance: I can be impulsive,"),
    (36.32, 37.54, "我也会分心，", "I can be distracted,"),
    (37.94, 41.37, "我也会在情绪上头的时候做错选择。", "and I can choose wrong when emotions rise."),
    (42.02, 46.06, "体育里也是一样。", "Sports are the same."),
    (46.43, 50.21, "真正高水平的运动员，不是每天都靠热血训练。", "Elite athletes do not train on passion every day."),
    (50.69, 53.49, "他靠的是固定时间、固定动作、", "They rely on fixed time and fixed moves,"),
    (54.03, 56.48, "固定恢复、固定复盘。", "fixed recovery and fixed review."),
    (56.88, 59.35, "因为他知道，比赛不会奖励情绪。", "Because games do not reward emotion."),
    (59.86, 62.37, "比赛只奖励系统。", "Games reward systems."),
    (62.76, 66.17, "普通人最容易输的地方，也不是不努力。", "Ordinary people do not lose because they do not try."),
    (66.82, 70.05, "是每天都把自己放在诱惑面前。", "They lose by standing in front of temptation every day."),
    (70.57, 73.11, "手机放在枕边，却怪自己熬夜。", "Phone by the pillow, then blaming insomnia."),
    (73.69, 76.78, "一边说要存钱，一边刷着消费内容。", "Saying they want savings while scrolling consumption."),
    (77.20, 79.39, "一边说要成长，", "Saying they want growth,"),
    (79.82, 82.34, "一边让情绪决定今天做不做。", "while letting mood decide the day."),
    (82.90, 83.57, "你不是没有自控力。", "You do not lack self-control."),
    (83.82, 85.38, "你只是太相信临场发挥。", "You trust improvisation too much."),
    (85.84, 88.91, "心理学里有个概念，叫情境设计。", "Psychology calls this situation design."),
    (89.42, 92.78, "一个人真正的改变，不是等自己突然变强。", "Real change is not waiting to become stronger."),
    (93.44, 96.75, "而是先把环境改到不容易失败。", "It is changing the environment so failure becomes harder."),
    (97.15, 100.92, "想早睡，就别把手机放床边。", "Want to sleep early? Keep the phone away."),
    (101.37, 104.00, "想训练，就提前把鞋放门口。", "Want to train? Put the shoes by the door."),
    (104.49, 108.12, "想少内耗，就别在深夜做人生判断。", "Want less mental friction? Do not judge life at midnight."),
    (108.12, 108.12, "想变好，就给自己设计一条更容易走对的路。", "Want to improve? Design an easier right path."),
    (108.12, 108.12, "奥德修斯不是因为意志力强，才活着穿过海妖。", "Odysseus survived not because his willpower was stronger."),
    (108.12, 108.12, "他是因为知道自己会被诱惑，所以提前把自己绑住。", "He survived because he knew he would be tempted."),
    (108.12, 108.12, "这才是真正的自律。", "That is real discipline."),
    (108.12, 108.12, "不是永远不动摇。", "Not never shaking."),
    (108.12, 108.12, "而是在清醒的时候，保护那个将来会动摇的自己。", "But protecting your future wavering self while you are clear."),
]

HIGHLIGHTS = [
    "意志力硬扛",
    "更残酷的故事",
    "绑在桅杆上",
    "不是懦弱",
    "这是清醒",
    "永远理性",
    "提前承认",
    "固定时间",
    "固定动作",
    "固定恢复",
    "固定复盘",
    "比赛只奖励系统",
    "诱惑面前",
    "自控力",
    "临场发挥",
    "情境设计",
    "不容易失败",
    "提前把鞋放门口",
    "真正的自律",
    "保护那个将来会动摇的自己",
]

FRAME_PATHS = [
    FRAMES / "01_ship_mist.png",
    FRAMES / "02_siren_song.png",
    FRAMES / "03_tied_to_mast.png",
    FRAMES / "04_struggle.png",
    FRAMES / "05_phone_bed.png",
    FRAMES / "06_phone_close.png",
    FRAMES / "07_gym_dawn.png",
    FRAMES / "08_prepared_gear.png",
    FRAMES / "09_free_throw.png",
    FRAMES / "10_runner.png",
    FRAMES / "11_phone_living_room.png",
    FRAMES / "12_clean_desk.png",
    FRAMES / "13_waves_window.png",
    FRAMES / "14_recovery.png",
    FRAMES / "15_ship_sunrise.png",
    FRAMES / "16_tie_shoes.png",
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


def wrap_cn(text: str, limit: int = 24) -> str:
    text = esc(text)
    if len(text) <= limit:
        return text
    marks = "，。；：、"
    lines: list[str] = []
    rest = text
    while len(rest) > limit:
        cut = -1
        for i in range(min(limit, len(rest) - 1), 9, -1):
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


def wrap_en(text: str, limit: int = 62) -> str:
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


def timed_captions(duration: float) -> list[tuple[float, float, str, str]]:
    usable_start = 0.54
    usable_end = max(usable_start + 1.0, duration - 0.18)
    items = [(cn, en) for _, _, cn, en in CAPTIONS]
    weights = [max(4.0, len(normalize(cn)) * 1.0) for cn, _ in items]
    total = sum(weights)
    cursor = usable_start
    out: list[tuple[float, float, str, str]] = []
    for i, ((cn, en), weight) in enumerate(zip(items, weights)):
        if i == len(items) - 1:
            end = usable_end
        else:
            end = cursor + (usable_end - usable_start) * weight / total
        end = max(end, cursor + 1.05)
        end = min(end, usable_end)
        out.append((cursor, end, cn, en))
        cursor = min(end + 0.06, usable_end)
    return out


def build_ass(duration: float) -> None:
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: CN,{FONT},50,&H00FFFFFF,&H00FFFFFF,&H00050505,&H00000000,1,0,0,0,100,100,0,0,1,3,0,2,220,220,104,1
Style: EN,{FONT},23,&H00D8D0BD,&H00D8D0BD,&H00101010,&H00000000,0,0,0,0,100,100,0,0,1,2,0,2,260,260,52,1

[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
"""
    lines = [header]
    for start, end, cn, en in timed_captions(duration):
        if start >= duration:
            continue
        end = min(end, duration)
        lines.append(f"Dialogue: 0,{ass_time(start)},{ass_time(end)},CN,,0,0,0,,{apply_highlight(cn)}\n")
        lines.append(f"Dialogue: 1,{ass_time(start)},{ass_time(end)},EN,,0,0,0,,{wrap_en(en)}\n")
    ASS.write_text("".join(lines), encoding="utf-8")


def render_segment(index: int, source: Path, start: float, end: float) -> Path:
    duration = max(0.1, end - start)
    out = RENDER / f"seg_{index:02d}.mp4"
    pans = [
        ("(iw-ow)*(0.12+0.22*t/{d})", "(ih-oh)*0.42"),
        ("(iw-ow)*(0.72-0.20*t/{d})", "(ih-oh)*0.40"),
        ("(iw-ow)*0.50", "(ih-oh)*(0.16+0.18*t/{d})"),
        ("(iw-ow)*0.44", "(ih-oh)*(0.64-0.18*t/{d})"),
    ]
    x, y = pans[index % len(pans)]
    x = x.format(d=duration)
    y = y.format(d=duration)
    overlay = ""
    if index in {1, 3, 5, 12}:
        overlay = ",drawbox=x=0:y=0:w=iw:h=ih:color=0x0b1520@0.06:t=fill"
    vf = (
        f"scale={W + 180}:{H + 102}:force_original_aspect_ratio=increase,"
        f"crop={W}:{H}:x='{x}':y='{y}',"
        "eq=contrast=1.04:saturation=1.03,"
        f"{overlay},"
        "vignette=PI/7,"
        "format=yuv420p"
    ).replace(",,", ",")
    run([
        str(FFMPEG), "-hide_banner", "-y",
        "-loop", "1", "-t", f"{duration:.3f}",
        "-i", str(source),
        "-vf", vf,
        "-r", str(FPS),
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        str(out),
    ])
    return out


def make_cover() -> None:
    src = Image.open(FRAME_PATHS[3]).convert("RGB").resize((W, H), Image.Resampling.LANCZOS)
    src = src.filter(ImageFilter.UnsharpMask(radius=1.3, percent=115, threshold=3))
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rectangle((0, 0, W, H), fill=(0, 0, 0, 45))
    draw.rounded_rectangle((118, 158, 848, 504), radius=28, fill=(5, 8, 12, 92), outline=(255, 255, 255, 88), width=3)
    title_font = ImageFont.truetype(FONT, 118)
    sub_font = ImageFont.truetype(FONT, 42)
    en_font = ImageFont.truetype(FONT, 44)
    def shadow_text(x: int, y: int, text: str, font: ImageFont.FreeTypeFont, fill: tuple[int, int, int, int]) -> None:
        for dx, dy in [(-3, 3), (3, 3), (0, 5)]:
            draw.text((x + dx, y + dy), text, font=font, fill=(0, 0, 0, 190))
        draw.text((x, y), text, font=font, fill=fill)
    shadow_text(156, 204, "别信意志力", title_font, (255, 255, 255, 255))
    shadow_text(160, 342, "SYSTEM OVER WILLPOWER", en_font, (255, 211, 60, 255))
    shadow_text(160, 424, "真正厉害的人 会提前把自己绑住", sub_font, (238, 238, 238, 255))
    final = Image.alpha_composite(src.convert("RGBA"), overlay).convert("RGB")
    final.save(COVER, quality=96)
    shutil.copy2(COVER, DESKTOP_COVER)


def render_contact_sheet(frames: list[Path]) -> Path:
    out = QC / "16镜头总览.jpg"
    thumbs = []
    for frame in frames:
        img = Image.open(frame).convert("RGB")
        img.thumbnail((480, 270), Image.Resampling.LANCZOS)
        canvas = Image.new("RGB", (480, 270), (0, 0, 0))
        canvas.paste(img, ((480 - img.width) // 2, (270 - img.height) // 2))
        thumbs.append(canvas)
    sheet = Image.new("RGB", (1920, 1080), (10, 10, 10))
    for i, thumb in enumerate(thumbs):
        sheet.paste(thumb, ((i % 4) * 480, (i // 4) * 270))
    sheet.save(out, quality=92)
    return out


def main() -> None:
    if not FFMPEG.exists():
        raise FileNotFoundError(FFMPEG)
    if not AUDIO.exists():
        raise FileNotFoundError(AUDIO)
    for frame in FRAME_PATHS:
        if not frame.exists():
            raise FileNotFoundError(frame)
    RENDER.mkdir(parents=True, exist_ok=True)
    QC.mkdir(parents=True, exist_ok=True)

    duration = audio_duration(AUDIO)
    build_ass(duration)
    caption_text = "".join(cn for _, _, cn, _ in CAPTIONS if _ is not None)
    source_norm = normalize(SOURCE_SCRIPT)
    caption_norm = normalize(caption_text)
    if source_norm != caption_norm:
        raise RuntimeError(
            "Caption text does not match source script.\n"
            f"source={source_norm}\ncaption={caption_norm}"
        )

    edges = [0.0, 5.94, 12.66, 20.55, 28.98, 36.32, 46.43, 54.03, 62.76, 70.57, 77.20, 85.84, 93.44, 100.92, 104.49, 106.30, duration]
    edges = [min(x, duration) for x in edges]
    segments = [render_segment(i, FRAME_PATHS[i], edges[i], edges[i + 1]) for i in range(16) if edges[i + 1] > edges[i]]

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
        "-crf", "17",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        str(OUT),
    ])

    make_cover()
    sheet = render_contact_sheet(FRAME_PATHS)
    for sec in [1, 7, 15, 24, 34, 44, 55, 66, 77, 88, 99, 107]:
        if sec >= duration:
            continue
        run([
            str(FFMPEG), "-hide_banner", "-y",
            "-ss", str(sec),
            "-i", str(OUT),
            "-frames:v", "1",
            str(QC / f"t_{sec:03d}s.jpg"),
        ])

    shutil.copy2(OUT, DESKTOP_OUT)
    manifest = {
        "audio": str(AUDIO),
        "duration_seconds": round(duration, 2),
        "output": str(OUT),
        "desktop_output": str(DESKTOP_OUT),
        "cover": str(COVER),
        "desktop_cover": str(DESKTOP_COVER),
        "format": "1920x1080 landscape, 16 independent HD generated frames",
        "frames": [str(p) for p in FRAME_PATHS],
        "caption_units": len(CAPTIONS),
        "subtitle_consistency": "Chinese captions exactly match approved narration after punctuation normalization",
        "contact_sheet": str(sheet),
        "qc_frames": [str(p) for p in sorted(QC.glob("t_*.jpg"))],
    }
    (ROOT / "render_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
