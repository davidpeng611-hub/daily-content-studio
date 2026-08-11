#!/usr/bin/env python3
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parent
SRC = Path("/Users/luca/.codex/generated_images/019f209f-a090-7332-8799-f279a5332607/call_Q5CfBmr8YQFNp1v6iqYWQjJc.png")
OUT = ROOT / "封面_别追结果_横版.png"
DESKTOP = Path("/Users/luca/Desktop/封面_别追结果_横版.png")

W, H = 1920, 1080

FONTS = [
    "/System/Library/AssetsV2/com_apple_MobileAsset_Font8/86ba2c91f017a3749571a82f2c6d890ac7ffb2fb.asset/AssetData/PingFang.ttc",
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
]


def font(size: int) -> ImageFont.FreeTypeFont:
    for path in FONTS:
        if Path(path).exists():
            return ImageFont.truetype(path, size=size, index=0)
    return ImageFont.load_default()


def fit_cover(img: Image.Image, size: tuple[int, int]) -> Image.Image:
    tw, th = size
    iw, ih = img.size
    scale = max(tw / iw, th / ih)
    resized = img.resize((int(iw * scale), int(ih * scale)), Image.Resampling.LANCZOS)
    rw, rh = resized.size
    left = (rw - tw) // 2
    top = (rh - th) // 2
    return resized.crop((left, top, left + tw, top + th))


def draw_text_with_shadow(draw: ImageDraw.ImageDraw, xy, text, fnt, fill, stroke=5):
    x, y = xy
    draw.text((x + 6, y + 8), text, font=fnt, fill=(0, 0, 0, 180), stroke_width=stroke, stroke_fill=(0, 0, 0, 180))
    draw.text((x, y), text, font=fnt, fill=fill, stroke_width=stroke, stroke_fill=(12, 14, 18, 235))


def main() -> None:
    img = Image.open(SRC).convert("RGB")
    base = fit_cover(img, (W, H))
    base = ImageEnhance.Contrast(base).enhance(1.08)
    base = ImageEnhance.Color(base).enhance(0.88)

    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay, "RGBA")

    # Left-side cinematic dark falloff, preserving the athlete on the right.
    for x in range(W):
        alpha = int(max(0, 205 * (1 - x / 1220)))
        d.line((x, 0, x, H), fill=(0, 0, 0, alpha))
    d.rectangle((0, 0, W, H), fill=(0, 0, 0, 42))
    d.rectangle((0, 0, W, 12), fill=(214, 53, 53, 255))

    title_font = font(176)
    en_font = font(58)
    sub_font = font(58)
    tag_font = font(34)

    d.rounded_rectangle((92, 112, 276, 168), radius=8, fill=(255, 211, 53, 245))
    d.text((112, 122), "体育哲学", font=tag_font, fill=(18, 18, 18, 255))

    draw_text_with_shadow(d, (90, 238), "别追结果", title_font, (255, 255, 255, 255), stroke=6)
    d.text((102, 438), "Outcome Control", font=en_font, fill=(238, 222, 185, 235), stroke_width=2, stroke_fill=(0, 0, 0, 160))

    d.line((98, 536, 620, 536), fill=(255, 211, 53, 245), width=8)
    d.text((102, 575), "箭已经飞出去", font=sub_font, fill=(255, 211, 53, 255), stroke_width=4, stroke_fill=(0, 0, 0, 220))

    # Small brand-like visual anchor, no platform logo.
    d.text((102, 972), "@体育哲学", font=tag_font, fill=(210, 214, 220, 210), stroke_width=2, stroke_fill=(0, 0, 0, 160))

    out = Image.alpha_composite(base.convert("RGBA"), overlay).convert("RGB")
    out = out.filter(ImageFilter.UnsharpMask(radius=1.2, percent=130, threshold=3))
    out.save(OUT, quality=96)
    out.save(DESKTOP, quality=96)
    print(OUT)
    print(DESKTOP)


if __name__ == "__main__":
    main()
