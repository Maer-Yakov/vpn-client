#!/usr/bin/env python3
"""Compose Ded Moroz advent letters with Russian applied-art frames."""

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
FRAMES = ASSETS / "frames"
SCENES = ASSETS / "scenes"
OUT = ROOT / "cards"
OUT.mkdir(parents=True, exist_ok=True)

STYLES = (
    "khokhloma",
    "gzhel",
    "dymkovo",
    "gorodets",
    "zhostovo",
    "palekh",
    "mezen",
    "filimonovo",
)

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
    rgb = im.convert("RGB")
    w, h = rgb.size
    # Bright-border crafts need a tighter inner search window.
    if style in {"gzhel", "dymkovo", "gorodets", "filimonovo", "mezen"}:
        x_lo, x_hi = int(w * 0.15), int(w * 0.85)
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
    bright_cols = [x for x in range(x_lo, x_hi) if sum(rgb.getpixel((x, mid_y))) / 3 > threshold]
    if not bright_cols:
        return int(w * 0.16), top, int(w * 0.84), bottom
    left = bright_cols[0] + int(w * 0.01)
    right = bright_cols[-1] - int(w * 0.01)
    return left, top, right, bottom


def scene_path_for(n: int) -> Path:
    for ext in (".jpg", ".png"):
        path = SCENES / f"scene-{n:02d}{ext}"
        if path.exists():
            return path
    raise FileNotFoundError(f"missing scene for day {n}")


def frame_path_for(style: str) -> Path:
    path = FRAMES / f"frame-{style}.jpg"
    if not path.exists():
        path = FRAMES / f"frame-{style}.png"
    if not path.exists():
        raise FileNotFoundError(f"missing frame template: frame-{style}")
    return path


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
    base = Image.open(frame_path_for(style)).convert("RGBA")
    W, H = base.size
    draw = ImageDraw.Draw(base)

    left, top, right, bottom = find_parchment_box(base, style)
    pad = int((right - left) * 0.055)
    x0, x1 = left + pad, right - pad
    width = x1 - x0

    scene = Image.open(scene_path_for(letter["n"])).convert("RGBA")
    scene_h = int((bottom - top) * 0.26)
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
    cx = W // 2
    cy = max(int(top - badge_r * 0.1), badge_r + 8)
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
    body_font = load_font("body", max(15, W // 36))
    small_font = load_font("ui", max(12, W // 44))
    label_font = load_font("ui_bold", max(13, W // 40))
    sign_font = load_font("title", max(15, W // 34))

    date_line = f"{letter['n']} декабря"
    for line in wrap(draw, date_line, small_font, width):
        tw = draw.textlength(line, font=small_font)
        draw.text((x0 + (width - tw) / 2, y), line, font=small_font, fill=INK_SOFT)
        y += int(small_font.size * 1.25)

    for line in wrap(draw, letter["title"], title_font, width):
        tw = draw.textlength(line, font=title_font)
        draw.text((x0 + (width - tw) / 2, y), line, font=title_font, fill=INK)
        y += int(title_font.size * 1.15)
    y += int(pad * 0.15)

    for block in (letter["greeting"], letter["from"], letter["story"]):
        for line in wrap(draw, block, body_font, width):
            if y + body_font.size > text_bottom - int(H * 0.20):
                break
            draw.text((x0, y), line, font=body_font, fill=INK)
            y += int(body_font.size * 1.26)
        y += int(pad * 0.12)

    draw.text((x0, y), "★ Задание:", font=label_font, fill=STAR)
    y += int(label_font.size * 1.3)
    for line in wrap(draw, letter["task"], body_font, width):
        if y + body_font.size > text_bottom - int(H * 0.14):
            break
        draw.text((x0, y), line, font=body_font, fill=INK)
        y += int(body_font.size * 1.26)
    y += int(pad * 0.15)

    if letter.get("teaser"):
        for line in wrap(draw, letter["teaser"], body_font, width):
            if y + body_font.size > text_bottom - int(H * 0.11):
                break
            draw.text((x0, y), line, font=body_font, fill=INK)
            y += int(body_font.size * 1.26)
        y += int(pad * 0.12)

    draw.text((x0, y), "Родителям:", font=small_font, fill=INK_SOFT)
    y += int(small_font.size * 1.3)
    for line in wrap(draw, letter["tip"], small_font, width):
        if y + small_font.size > text_bottom - int(H * 0.05):
            break
        draw.text((x0, y), line, font=small_font, fill=INK_SOFT)
        y += int(small_font.size * 1.28)

    sig = letter.get("signature", "Дедушка Мороз и Искорка")
    sw = draw.textlength(sig, font=sign_font)
    sig_y = min(y + int(pad * 0.25), text_bottom - sign_font.size - 4)
    draw.text((x0 + (width - sw) / 2, sig_y), sig, font=sign_font, fill=BADGE_STROKE)

    out = OUT / f"letter-{letter['n']:02d}-{style}.jpg"
    atomic_save_jpeg(base, out)
    return out


def require_all_assets(data: list[dict]) -> None:
    missing: list[str] = []
    if not FRAMES.is_dir() or not SCENES.is_dir():
        raise SystemExit(
            f"Assets missing under {ASSETS}. Need frames/ and scenes/ "
            "(or set TAYNA31_ASSETS)."
        )
    for letter in data:
        style = letter["style"]
        try:
            frame_path_for(style)
        except FileNotFoundError as exc:
            missing.append(str(exc))
        try:
            scene_path_for(letter["n"])
        except FileNotFoundError as exc:
            missing.append(str(exc))
    if missing:
        raise SystemExit("Incomplete artwork — refusing partial rebuild:\n  - " + "\n  - ".join(missing))


def main() -> None:
    data = json.loads((ROOT / "letters_data.json").read_text(encoding="utf-8"))
    if len(data) != 31:
        raise SystemExit(f"expected 31 letters, got {len(data)}")
    require_all_assets(data)
    made = []
    for letter in data:
        path = compose_one(letter)
        made.append(path.name)
        print("wrote", path)
    print(f"done: {len(made)} cards")


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:  # pragma: no cover
        sys.exit(0)
