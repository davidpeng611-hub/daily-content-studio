from pathlib import Path
import math
import re
import subprocess

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont


ROOT = Path("/Users/luca/Documents/每日口播工作室/今日推文/2026-08-10_你不是懒")
FRAME_DIR = ROOT / "frames_hd16"
QC_DIR = ROOT / "qc"
RENDER_DIR = ROOT / "render"
AUDIO = Path("/Users/luca/Desktop/8月10日.mp3")
FINAL = Path("/Users/luca/Desktop/小红书_第1条_你不是懒_无标点字幕版.mp4")
COVER = Path("/Users/luca/Desktop/封面_第1条_你不是懒.png")

W, H = 1920, 1080
FPS = 24
SUB_Y = 805

PUNCT_RE = re.compile(r"[，。！？；：、“”‘’（）()《》【】\[\]{},.!?:;\"'|#*…—\-]+")


SCRIPT_CN = """
你有没有发现，很多人不是懒。
而是太害怕开始。
因为只要不开始，你就永远可以安慰自己：我只是还没准备好。
古希腊有个故事，叫西西弗斯推石头。
他每天都要把一块巨石推上山顶，可石头又会滚下来。
看起来很荒诞。
但它最残酷的地方是：他明知道结果可能会失败，第二天还是要重新开始。
体育里也是一样。
一个运动员最难的，不是比赛当天爆发。
而是昨天练砸了，今天还敢走进训练馆。
投篮不准，还愿意再投一组。
跑不动了，还愿意重新调整呼吸。
真正毁掉人的，不是失败。
是你为了避免失败，连开始的机会都不给自己。
普通人也是这样。
想做账号，却一直研究设备。
想赚钱，却一直等好机会。
想改变，却一直说自己还没准备好。
可人生很多事，不是准备好了才开始。
是开始之后，你才会慢慢准备好。
所以今天别问：我有没有信心。
先问：我能不能先做一个很小的动作。
发一条笔记。
投一份简历。
练二十分钟。
把房间收拾出一个角落。
真正改变人的，不是宏大的决心。
是你终于停止逃避，推了第一下石头。
评论区告诉我，你现在最不敢开始的那件事是什么？
""".strip()


CAPTIONS = [
    ("你有没有发现 很多人不是懒", "Some people are not lazy"),
    ("而是太害怕开始", "They are afraid to begin"),
    ("因为只要不开始 你就永远可以安慰自己", "If you never begin you can keep the excuse"),
    ("我只是还没准备好", "I am just not ready yet"),
    ("古希腊有个故事 叫西西弗斯推石头", "There is an old story of Sisyphus"),
    ("他每天都要把一块巨石推上山顶", "Every day he pushes a stone uphill"),
    ("可石头又会滚下来", "And every day it rolls back"),
    ("看起来很荒诞", "It looks absurd"),
    ("但它最残酷的地方是", "But the cruel part is this"),
    ("他明知道结果可能会失败", "He knows it may fail"),
    ("第二天还是要重新开始", "And still begins again tomorrow"),
    ("体育里也是一样", "Sport is the same"),
    ("一个运动员最难的 不是比赛当天爆发", "The hardest part is not game day"),
    ("而是昨天练砸了 今天还敢走进训练馆", "It is returning after a bad practice"),
    ("投篮不准 还愿意再投一组", "Missing shots and taking one more set"),
    ("跑不动了 还愿意重新调整呼吸", "Being exhausted and resetting the breath"),
    ("真正毁掉人的 不是失败", "Failure is not what destroys you"),
    ("是你为了避免失败 连开始的机会都不给自己", "It is refusing the chance to start"),
    ("普通人也是这样", "Ordinary life is the same"),
    ("想做账号 却一直研究设备", "You want to create but keep studying gear"),
    ("想赚钱 却一直等好机会", "You want income but keep waiting"),
    ("想改变 却一直说自己还没准备好", "You want change but keep saying not ready"),
    ("可人生很多事 不是准备好了才开始", "Life does not wait for readiness"),
    ("是开始之后 你才会慢慢准备好", "You become ready after starting"),
    ("所以今天别问 我有没有信心", "Do not ask if you have confidence"),
    ("先问 我能不能先做一个很小的动作", "Ask if you can take one small action"),
    ("发一条笔记", "Post one note"),
    ("投一份简历", "Send one resume"),
    ("练二十分钟", "Train for twenty minutes"),
    ("把房间收拾出一个角落", "Clear one corner of your room"),
    ("真正改变人的 不是宏大的决心", "Change is not made by grand resolve"),
    ("是你终于停止逃避", "It begins when you stop avoiding"),
    ("推了第一下石头", "And push the stone once"),
    ("评论区告诉我", "Tell me in the comments"),
    ("你现在最不敢开始的那件事是什么", "What are you most afraid to start"),
]


def run(cmd):
    subprocess.run(cmd, check=True)


def probe_duration(path: Path) -> float:
    result = subprocess.run([
        "/Users/luca/bin/ffmpeg",
        "-hide_banner",
        "-i",
        str(path),
    ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out = result.stdout.decode("utf-8", errors="ignore")
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", out)
    if not m:
        raise RuntimeError("Could not read audio duration")
    h, mnt, s = int(m.group(1)), int(m.group(2)), float(m.group(3))
    return h * 3600 + mnt * 60 + s


def font(size: int, weight: str = "regular"):
    candidates = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/Library/Fonts/Arial Unicode.ttf",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    ]
    for p in candidates:
        if Path(p).exists():
            return ImageFont.truetype(p, size=size, index=0)
    return ImageFont.load_default()


FONT_CN = font(56)
FONT_EN = font(25)
FONT_COVER_BIG = font(118)
FONT_COVER_EN = font(46)
FONT_COVER_SMALL = font(42)


def clean_display(text: str) -> str:
    text = PUNCT_RE.sub(" ", text)
    return re.sub(r"\s+", " ", text).strip()


def normalize(text: str) -> str:
    return re.sub(r"\s+", "", clean_display(text)).lower()


def assert_caption_consistency():
    source = normalize(SCRIPT_CN)
    caps = normalize("".join(cn for cn, _ in CAPTIONS))
    if source != caps:
        raise AssertionError(f"Caption text mismatch source={len(source)} captions={len(caps)}")
    visible = "".join(clean_display(cn) + clean_display(en) for cn, en in CAPTIONS)
    bad = PUNCT_RE.findall(visible)
    if bad:
        raise AssertionError(f"Subtitle punctuation remains: {bad[:10]}")


def wrap_text(draw, text, fnt, max_width):
    words = list(text) if re.search(r"[\u4e00-\u9fff]", text) else text.split()
    lines, line = [], ""
    for w in words:
        trial = line + w if re.search(r"[\u4e00-\u9fff]", text) else (line + " " + w).strip()
        if draw.textbbox((0, 0), trial, font=fnt)[2] <= max_width:
            line = trial
        else:
            if line:
                lines.append(line)
            line = w
    if line:
        lines.append(line)
    return lines[:2]


def draw_centered(draw, lines, y, fnt, fill, stroke=3, gap=8):
    yy = y
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=fnt, stroke_width=stroke)
        x = (W - (bbox[2] - bbox[0])) // 2
        draw.text((x, yy), line, font=fnt, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0, 215))
        yy += (bbox[3] - bbox[1]) + gap
    return yy


def cover_shadow(draw, xy, text, fnt, fill, stroke):
    draw.text(xy, text, font=fnt, fill=fill, stroke_width=stroke, stroke_fill=(20, 20, 20, 230))


def make_cover(first_image: Path):
    img = Image.open(first_image).convert("RGB")
    img = crop_cover(img, 1080, 1440)
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    d.rectangle((0, 0, 1080, 1440), fill=(0, 0, 0, 76))
    d.rounded_rectangle((86, 104, 994, 304), radius=32, outline=(255, 255, 255, 170), width=3, fill=(0, 0, 0, 55))
    cover_shadow(d, (118, 130), "你不是懒", FONT_COVER_BIG, (255, 255, 255, 255), 5)
    cover_shadow(d, (124, 260), "START BEFORE READY", FONT_COVER_EN, (235, 207, 108, 255), 3)
    cover_shadow(d, (118, 1180), "你只是害怕开始之后 发现自己不行", FONT_COVER_SMALL, (255, 255, 255, 245), 4)
    img = Image.alpha_composite(img.convert("RGBA"), overlay)
    img.save(COVER)


def crop_cover(img: Image.Image, target_w: int, target_h: int) -> Image.Image:
    sw, sh = img.size
    scale = max(target_w / sw, target_h / sh)
    nw, nh = int(sw * scale), int(sh * scale)
    img = img.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - target_w) // 2
    top = (nh - target_h) // 2
    return img.crop((left, top, left + target_w, top + target_h))


def load_scene(path: Path):
    img = Image.open(path).convert("RGB")
    sw, sh = img.size
    scale = max(W / sw, H / sh)
    nw, nh = int(sw * scale), int(sh * scale)
    img = img.resize((nw, nh), Image.Resampling.LANCZOS)
    return img


def scene_frame(img, progress, idx):
    base_scale = 1.0 + 0.055 * progress
    if idx % 3 == 1:
        base_scale = 1.055 - 0.045 * progress
    if idx % 4 == 2:
        base_scale = 1.015 + 0.035 * math.sin(progress * math.pi)
    sw, sh = img.size
    cw, ch = int(W / base_scale), int(H / base_scale)
    max_x, max_y = max(0, sw - cw), max(0, sh - ch)
    drift = math.sin((progress + idx * 0.17) * math.pi)
    x = int(max_x * (0.45 + 0.10 * drift))
    y = int(max_y * (0.50 + 0.08 * math.cos((progress + idx * 0.11) * math.pi)))
    frame = img.crop((x, y, x + cw, y + ch)).resize((W, H), Image.Resampling.LANCZOS)
    frame = ImageEnhance.Contrast(frame).enhance(1.06)
    frame = ImageEnhance.Color(frame).enhance(0.96)
    return frame.convert("RGBA")


def add_vignette_and_grain(frame, t):
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    for i in range(80):
        alpha = int(2.3 * i)
        d.rounded_rectangle((i * 9, i * 5, W - i * 9, H - i * 5), radius=0, outline=(0, 0, 0, max(0, alpha // 5)))
    if int(t * 2) % 13 == 0:
        d.rectangle((0, 0, W, H), fill=(255, 240, 210, 7))
    return Image.alpha_composite(frame, overlay)


def caption_at(t, timed):
    for start, end, cn, en in timed:
        if start <= t < end:
            return cn, en
    return timed[-1][2], timed[-1][3]


def timed_captions(duration):
    usable_start, usable_end = 0.25, max(1.0, duration - 0.55)
    usable = usable_end - usable_start
    weights = [max(7, len(normalize(cn))) for cn, _ in CAPTIONS]
    total = sum(weights)
    cur = usable_start
    out = []
    for i, ((cn, en), wgt) in enumerate(zip(CAPTIONS, weights)):
        seg = usable * (wgt / total)
        if i < 4:
            seg = min(seg * 0.9, 2.3)
        if i in {26, 27, 28, 29, 32}:
            seg = max(seg, 1.25)
        nxt = cur + seg
        out.append((cur, nxt, clean_display(cn), clean_display(en)))
        cur = nxt
    # Stretch all segments proportionally to fill exact usable time.
    last = out[-1][1]
    factor = usable / (last - usable_start)
    stretched = []
    cur = usable_start
    for start, end, cn, en in out:
        seg = (end - start) * factor
        stretched.append((cur, cur + seg, cn, en))
        cur += seg
    return stretched


def render_video():
    assert_caption_consistency()
    frame_paths = sorted(FRAME_DIR.glob("*.png"))
    if len(frame_paths) != 16:
        raise AssertionError(f"Need exactly 16 images found {len(frame_paths)}")
    duration = probe_duration(AUDIO)
    scenes = [load_scene(p) for p in frame_paths]
    timed = timed_captions(duration)
    total_frames = int(math.ceil(duration * FPS))
    scene_len = duration / len(scenes)

    silent = RENDER_DIR / "silent_video.mp4"
    cmd = [
        "/Users/luca/bin/ffmpeg",
        "-y",
        "-f",
        "rawvideo",
        "-pix_fmt",
        "rgb24",
        "-s",
        f"{W}x{H}",
        "-r",
        str(FPS),
        "-i",
        "-",
        "-an",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-preset",
        "medium",
        "-crf",
        "18",
        str(silent),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for n in range(total_frames):
        t = n / FPS
        scene_idx = min(len(scenes) - 1, int(t / scene_len))
        local = (t - scene_idx * scene_len) / scene_len
        frame = scene_frame(scenes[scene_idx], local, scene_idx)
        frame = add_vignette_and_grain(frame, t)
        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(overlay)

        cn, en = caption_at(t, timed)
        cn_lines = wrap_text(d, cn, FONT_CN, 1500)
        en_lines = wrap_text(d, en.upper(), FONT_EN, 1320)
        accent = (242, 205, 92, 255) if any(k in cn for k in ["开始", "失败", "石头", "行动"]) else (255, 255, 255, 250)
        yy = draw_centered(d, cn_lines, SUB_Y, FONT_CN, accent, stroke=4, gap=8)
        draw_centered(d, en_lines, yy + 4, FONT_EN, (232, 232, 232, 225), stroke=2, gap=4)

        frame = Image.alpha_composite(frame, overlay).convert("RGB")
        proc.stdin.write(frame.tobytes())
    proc.stdin.close()
    ret = proc.wait()
    if ret != 0:
        raise RuntimeError(f"ffmpeg render failed {ret}")

    run([
        "/Users/luca/bin/ffmpeg",
        "-y",
        "-i",
        str(silent),
        "-i",
        str(AUDIO),
        "-map",
        "0:v:0",
        "-map",
        "1:a:0",
        "-c:v",
        "copy",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-shortest",
        str(FINAL),
    ])
    make_cover(frame_paths[0])
    write_qc(timed, duration)
    silent.unlink(missing_ok=True)


def write_qc(timed, duration):
    (ROOT / "subtitle_timing_no_punctuation.txt").write_text(
        "\n".join(f"{s:05.2f}-{e:05.2f} {cn} / {en}" for s, e, cn, en in timed),
        encoding="utf-8",
    )
    thumbs = []
    frame_paths = sorted(FRAME_DIR.glob("*.png"))
    for p in frame_paths:
        img = Image.open(p).convert("RGB").resize((320, 180), Image.Resampling.LANCZOS)
        thumbs.append(img)
    sheet = Image.new("RGB", (1280, 720), (20, 20, 20))
    for i, img in enumerate(thumbs):
        x = (i % 4) * 320
        y = (i // 4) * 180
        sheet.paste(img, (x, y))
    sheet.save(QC_DIR / "16镜头总览.jpg", quality=92)
    for sec in [1, 8, 21, 42, 63, max(1, int(duration) - 3)]:
        out = QC_DIR / f"frame_{sec:03d}s.jpg"
        run([
            "/Users/luca/bin/ffmpeg",
            "-y",
            "-ss",
            str(sec),
            "-i",
            str(FINAL),
            "-frames:v",
            "1",
            "-q:v",
            "2",
            str(out),
        ])


if __name__ == "__main__":
    render_video()
