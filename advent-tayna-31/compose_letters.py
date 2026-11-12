#!/usr/bin/env python3
"""Compose advent letter cards: folk frames + Cyrillic text + scene art."""

from __future__ import annotations

import json
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
ASSETS = Path("/opt/cursor/artifacts/assets")
OUT = ROOT / "cards"
OUT.mkdir(parents=True, exist_ok=True)

FRAME = {
    "khokhloma": ASSETS / "template-khokhloma-frame.jpg",
    "gzhel": ASSETS / "template-gzhel-frame.jpg",
    "palekh": ASSETS / "template-khokhloma-frame.jpg",  # fallback until palekh frame exists
}

FONT_TITLE = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
FONT_BODY = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
FONT_UI = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_UI_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

INK = (52, 36, 24)
INK_SOFT = (90, 70, 50)
STAR = (180, 90, 30)
BADGE_FILL = (245, 236, 214)
BADGE_STROKE = (120, 40, 30)


def load_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size=size)


def wrap(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    cur = ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if draw.textlength(trial, font=font) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def find_parchment_box(im: Image.Image) -> tuple[int, int, int, int]:
    """Detect the light parchment rectangle inside the ornamental frame."""
    rgb = im.convert("RGB")
    w, h = rgb.size
    # sample center column brightness to find parchment top/bottom
    xs = range(int(w * 0.25), int(w * 0.75), max(1, w // 80))
    ys = range(int(h * 0.08), int(h * 0.95))
    bright_rows = []
    for y in ys:
        vals = [sum(rgb.getpixel((x, y))) / 3 for x in xs]
        if sum(1 for v in vals if v > 175) >= len(vals) * 0.55:
            bright_rows.append(y)
    if not bright_rows:
        return int(w * 0.12), int(h * 0.12), int(w * 0.88), int(h * 0.88)
    top, bottom = bright_rows[0], bright_rows[-1]
    # find left/right on a mid parchment row
    mid_y = (top + bottom) // 2
    bright_cols = []
    for x in range(int(w * 0.05), int(w * 0.95)):
        if sum(rgb.getpixel((x, mid_y))) / 3 > 175:
            bright_cols.append(x)
    if not bright_cols:
        return int(w * 0.12), top, int(w * 0.88), bottom
    return bright_cols[0], top, bright_cols[-1], bottom


def compose_one(letter: dict) -> Path:
    style = letter["style"]
    frame_path = FRAME[style]
    base = Image.open(frame_path).convert("RGBA")
    W, H = base.size
    draw = ImageDraw.Draw(base)

    left, top, right, bottom = find_parchment_box(base)
    pad = int((right - left) * 0.06)
    x0, x1 = left + pad, right - pad
    width = x1 - x0

    # scene at bottom of parchment
    scene_path = ASSETS / f"scene-{letter['n']:02d}.jpg"
    if not scene_path.exists():
        scene_path = ASSETS / f"scene-{letter['n']:02d}.png"
    scene_h = int((bottom - top) * 0.28)
    text_bottom = bottom - scene_h - pad // 2
    if scene_path.exists():
        scene = Image.open(scene_path).convert("RGBA")
        target_w = width
        ratio = target_w / scene.width
        scene = scene.resize((target_w, int(scene.height * ratio)), Image.Resampling.LANCZOS)
        if scene.height > scene_h:
            # center-crop vertically
            overflow = scene.height - scene_h
            scene = scene.crop((0, overflow // 2, scene.width, overflow // 2 + scene_h))
        # rounded-ish mask by slight alpha fade not required; paste
        sy = bottom - pad // 2 - scene.height
        base.alpha_composite(scene, (x0, sy))
        text_bottom = sy - pad // 3

    # badge number
    badge_r = int(W * 0.055)
    cx, cy = W // 2, max(int(top - badge_r * 0.15), badge_r + 8)
    draw.ellipse((cx - badge_r, cy - badge_r, cx + badge_r, cy + badge_r), fill=BADGE_FILL, outline=BADGE_STROKE, width=max(2, W // 300))
    num_font = load_font(FONT_UI_BOLD, max(18, W // 28))
    num = f"№{letter['n']}"
    nw = draw.textlength(num, font=num_font)
    draw.text((cx - nw / 2, cy - num_font.size * 0.55), num, font=num_font, fill=BADGE_STROKE)

    y = top + pad
    title_font = load_font(FONT_TITLE, max(22, W // 22))
    body_font = load_font(FONT_BODY, max(16, W // 34))
    small_font = load_font(FONT_UI, max(13, W // 42))
    label_font = load_font(FONT_UI_BOLD, max(14, W // 38))
    sign_font = load_font(FONT_TITLE, max(16, W // 32))

    # title
    for line in wrap(draw, letter["title"], title_font, width):
        tw = draw.textlength(line, font=title_font)
        draw.text((x0 + (width - tw) / 2, y), line, font=title_font, fill=INK)
        y += int(title_font.size * 1.2)
    y += int(pad * 0.25)

    # greeting
    for line in wrap(draw, letter["greeting"], body_font, width):
        draw.text((x0, y), line, font=body_font, fill=INK)
        y += int(body_font.size * 1.25)
    y += int(pad * 0.2)

    # body
    for line in wrap(draw, letter["body"], body_font, width):
        if y + body_font.size > text_bottom - int(H * 0.18):
            break
        draw.text((x0, y), line, font=body_font, fill=INK)
        y += int(body_font.size * 1.28)
    y += int(pad * 0.35)

    # task
    draw.text((x0, y), "★ Задание:", font=label_font, fill=STAR)
    y += int(label_font.size * 1.35)
    for line in wrap(draw, letter["task"], body_font, width):
        if y + body_font.size > text_bottom - int(H * 0.10):
            break
        draw.text((x0, y), line, font=body_font, fill=INK)
        y += int(body_font.size * 1.28)
    y += int(pad * 0.3)

    # tip
    tip_label = "Подсказка для родителей:"
    draw.text((x0, y), tip_label, font=small_font, fill=INK_SOFT)
    y += int(small_font.size * 1.35)
    for line in wrap(draw, letter["tip"], small_font, width):
        if y + small_font.size > text_bottom - int(H * 0.05):
            break
        draw.text((x0, y), line, font=small_font, fill=INK_SOFT)
        y += int(small_font.size * 1.3)

    # signature above scene
    sig = "Фонарщик Луми"
    sw = draw.textlength(sig, font=sign_font)
    sig_y = min(y + int(pad * 0.35), text_bottom - sign_font.size - 4)
    draw.text((x0 + (width - sw) / 2, sig_y), sig, font=sign_font, fill=BADGE_STROKE)

    out = OUT / f"letter-{letter['n']:02d}-{style}.png"
    base.convert("RGB").save(out, quality=95)
    return out


def main() -> None:
    data = json.loads((ROOT / "letters_data.json").read_text(encoding="utf-8"))
    made = []
    for letter in data:
        scene = ASSETS / f"scene-{letter['n']:02d}.jpg"
        scene_png = ASSETS / f"scene-{letter['n']:02d}.png"
        if not scene.exists() and not scene_png.exists():
            print(f"skip {letter['n']}: no scene yet")
            continue
        path = compose_one(letter)
        made.append(path.name)
        print("wrote", path)
    print(f"done: {len(made)} cards")


if __name__ == "__main__":
    main()
