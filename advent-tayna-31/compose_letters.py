#!/usr/bin/env python3
"""Compose advent letter cards: folk frames + Cyrillic text + scene art.

Canonical copy source: letters_data.json (LETTERS.md is generated from it).
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "Pillow is required. Install with: pip install -r requirements.txt"
    ) from exc

ROOT = Path(__file__).resolve().parent
ASSETS = Path(os.environ.get("TAYNA31_ASSETS", ROOT / "assets"))
OUT = ROOT / "cards"
OUT.mkdir(parents=True, exist_ok=True)

FRAME = {
    "khokhloma": ASSETS / "template-khokhloma-frame.jpg",
    "gzhel": ASSETS / "template-gzhel-frame.jpg",
    "palekh": ASSETS / "template-palekh-frame.jpg",
}

# Prefer Liberation/DejaVu (common on Linux); fall back via FONT_CANDIDATES.
FONT_CANDIDATES = {
    "title": [
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
        "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf",
    ],
    "body": [
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
        "/usr/share/fonts/truetype/noto/NotoSerif-Regular.ttf",
    ],
    "ui": [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
    ],
    "ui_bold": [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
    ],
}

INK = (52, 36, 24)
INK_SOFT = (90, 70, 50)
STAR = (180, 90, 30)
BADGE_FILL = (245, 236, 214)
BADGE_STROKE = (120, 40, 30)


def resolve_font(kind: str) -> str:
    for path in FONT_CANDIDATES[kind]:
        if Path(path).exists():
            return path
    raise SystemExit(
        f"No Cyrillic font found for '{kind}'. Install fonts-liberation or fonts-dejavu."
    )


def load_font(kind: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(resolve_font(kind), size=size)


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


def find_parchment_box(im: Image.Image, style: str) -> tuple[int, int, int, int]:
    """Detect the light parchment rectangle inside the ornamental frame.

    For Gzhel (white outer field) we constrain the search to the inner
    portion of the card so bright border pixels are not treated as parchment.
    """
    rgb = im.convert("RGB")
    w, h = rgb.size

    if style == "gzhel":
        x_lo, x_hi = int(w * 0.14), int(w * 0.86)
        y_lo, y_hi = int(h * 0.12), int(h * 0.90)
        threshold = 200
    else:
        x_lo, x_hi = int(w * 0.10), int(w * 0.90)
        y_lo, y_hi = int(h * 0.08), int(h * 0.95)
        threshold = 175

    xs = range(x_lo, x_hi, max(1, (x_hi - x_lo) // 60))
    bright_rows = []
    for y in range(y_lo, y_hi):
        vals = [sum(rgb.getpixel((x, y))) / 3 for x in xs]
        if sum(1 for v in vals if v > threshold) >= len(vals) * 0.55:
            bright_rows.append(y)
    if not bright_rows:
        return int(w * 0.16), int(h * 0.14), int(w * 0.84), int(h * 0.86)

    top, bottom = bright_rows[0], bright_rows[-1]
    mid_y = (top + bottom) // 2
    bright_cols = []
    for x in range(x_lo, x_hi):
        if sum(rgb.getpixel((x, mid_y))) / 3 > threshold:
            bright_cols.append(x)
    if not bright_cols:
        return int(w * 0.16), top, int(w * 0.84), bottom

    # Shrink slightly from detected edges to stay inside parchment.
    left = bright_cols[0] + int(w * 0.01)
    right = bright_cols[-1] - int(w * 0.01)
    return left, top, right, bottom


def scene_path_for(n: int) -> Path:
    jpg = ASSETS / f"scene-{n:02d}.jpg"
    png = ASSETS / f"scene-{n:02d}.png"
    if jpg.exists():
        return jpg
    if png.exists():
        return png
    raise FileNotFoundError(f"missing scene for day {n}: expected {jpg.name}")


def atomic_save_jpeg(im: Image.Image, dest: Path, quality: int = 92) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{dest.stem}.", suffix=".jpg", dir=dest.parent)
    os.close(fd)
    tmp = Path(tmp_name)
    try:
        im.convert("RGB").save(tmp, format="JPEG", quality=quality, optimize=True)
        os.replace(tmp, dest)
    finally:
        tmp.unlink(missing_ok=True)


def compose_one(letter: dict) -> Path:
    style = letter["style"]
    frame_path = FRAME[style]
    if not frame_path.exists():
        raise FileNotFoundError(f"missing frame template: {frame_path}")

    base = Image.open(frame_path).convert("RGBA")
    W, H = base.size
    draw = ImageDraw.Draw(base)

    left, top, right, bottom = find_parchment_box(base, style)
    pad = int((right - left) * 0.06)
    x0, x1 = left + pad, right - pad
    width = x1 - x0

    scene = Image.open(scene_path_for(letter["n"])).convert("RGBA")
    scene_h = int((bottom - top) * 0.28)
    text_bottom = bottom - scene_h - pad // 2
    target_w = width
    ratio = target_w / scene.width
    scene = scene.resize((target_w, max(1, int(scene.height * ratio))), Image.Resampling.LANCZOS)
    if scene.height > scene_h:
        overflow = scene.height - scene_h
        scene = scene.crop((0, overflow // 2, scene.width, overflow // 2 + scene_h))
    sy = bottom - pad // 2 - scene.height
    base.alpha_composite(scene, (x0, sy))
    text_bottom = sy - pad // 3

    badge_r = int(W * 0.055)
    cx, cy = W // 2, max(int(top - badge_r * 0.15), badge_r + 8)
    draw.ellipse(
        (cx - badge_r, cy - badge_r, cx + badge_r, cy + badge_r),
        fill=BADGE_FILL,
        outline=BADGE_STROKE,
        width=max(2, W // 300),
    )
    num_font = load_font("ui_bold", max(18, W // 28))
    num = f"№{letter['n']}"
    nw = draw.textlength(num, font=num_font)
    draw.text((cx - nw / 2, cy - num_font.size * 0.55), num, font=num_font, fill=BADGE_STROKE)

    y = top + pad
    title_font = load_font("title", max(22, W // 22))
    body_font = load_font("body", max(16, W // 34))
    small_font = load_font("ui", max(13, W // 42))
    label_font = load_font("ui_bold", max(14, W // 38))
    sign_font = load_font("title", max(16, W // 32))

    for line in wrap(draw, letter["title"], title_font, width):
        tw = draw.textlength(line, font=title_font)
        draw.text((x0 + (width - tw) / 2, y), line, font=title_font, fill=INK)
        y += int(title_font.size * 1.2)
    y += int(pad * 0.25)

    for line in wrap(draw, letter["greeting"], body_font, width):
        draw.text((x0, y), line, font=body_font, fill=INK)
        y += int(body_font.size * 1.25)
    y += int(pad * 0.2)

    for line in wrap(draw, letter["body"], body_font, width):
        if y + body_font.size > text_bottom - int(H * 0.18):
            break
        draw.text((x0, y), line, font=body_font, fill=INK)
        y += int(body_font.size * 1.28)
    y += int(pad * 0.35)

    draw.text((x0, y), "★ Задание:", font=label_font, fill=STAR)
    y += int(label_font.size * 1.35)
    for line in wrap(draw, letter["task"], body_font, width):
        if y + body_font.size > text_bottom - int(H * 0.10):
            break
        draw.text((x0, y), line, font=body_font, fill=INK)
        y += int(body_font.size * 1.28)
    y += int(pad * 0.3)

    tip_label = "Подсказка для родителей:"
    draw.text((x0, y), tip_label, font=small_font, fill=INK_SOFT)
    y += int(small_font.size * 1.35)
    for line in wrap(draw, letter["tip"], small_font, width):
        if y + small_font.size > text_bottom - int(H * 0.05):
            break
        draw.text((x0, y), line, font=small_font, fill=INK_SOFT)
        y += int(small_font.size * 1.3)

    sig = "Фонарщик Луми"
    sw = draw.textlength(sig, font=sign_font)
    sig_y = min(y + int(pad * 0.35), text_bottom - sign_font.size - 4)
    draw.text((x0 + (width - sw) / 2, sig_y), sig, font=sign_font, fill=BADGE_STROKE)

    out = OUT / f"letter-{letter['n']:02d}-{style}.jpg"
    atomic_save_jpeg(base, out)
    return out


def require_all_assets(data: list[dict]) -> None:
    missing: list[str] = []
    if not ASSETS.is_dir():
        raise SystemExit(
            f"Assets directory not found: {ASSETS}\n"
            "Expected bundled artwork under advent-tayna-31/assets/, "
            "or set TAYNA31_ASSETS."
        )
    for style, path in FRAME.items():
        if not path.exists():
            missing.append(f"frame/{style}: {path.name}")
    for letter in data:
        try:
            scene_path_for(letter["n"])
        except FileNotFoundError as exc:
            missing.append(str(exc))
    if missing:
        raise SystemExit(
            "Incomplete artwork set — refusing partial rebuild:\n  - "
            + "\n  - ".join(missing)
        )


def main() -> None:
    data_path = ROOT / "letters_data.json"
    data = json.loads(data_path.read_text(encoding="utf-8"))
    if len(data) != 31:
        raise SystemExit(f"expected 31 letters in {data_path.name}, got {len(data)}")
    require_all_assets(data)

    made = []
    for letter in data:
        path = compose_one(letter)
        made.append(path.name)
        print("wrote", path)
    if len(made) != 31:
        raise SystemExit(f"expected 31 cards, wrote {len(made)}")
    print(f"done: {len(made)} cards -> {OUT}")


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:  # pragma: no cover
        sys.exit(0)
