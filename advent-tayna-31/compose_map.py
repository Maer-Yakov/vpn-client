#!/usr/bin/env python3
"""Compose fairy-tale map with programmatically numbered lanterns 1–31."""

from __future__ import annotations

import json
import math
import os
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
SRC_CANDIDATES = [
    ASSETS / "map-31-path-clean.jpg",
    ASSETS / "map-31-path-blank.jpg",
    ASSETS / "map-31-skazok-blank.jpg",
    ASSETS / "map-31-skazok-source.jpg",
    ASSETS / "map-gorod-tihih-fonarey-folk.jpg",
]
OUT = ROOT / "cards" / "map-advent.jpg"

FONT_CANDIDATES = {
    "title": [
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    ],
    "ui": [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ],
}


def resolve_font(kind: str) -> str:
    for path in FONT_CANDIDATES[kind]:
        if Path(path).exists():
            return path
    raise SystemExit(f"No font for {kind}")


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


def short_title(title: str) -> str:
    mapping = {
        "Петушок и бобовое зёрнышко": "Петушок",
        "Пузырь, соломинка и лапоть": "Пузырь и лапоть",
        "Лисичка-сестричка и волк": "Лисичка и волк",
        "Волк и семеро козлят": "Семеро козлят",
        "Бычок — чёрный бочок, белые копытца": "Бычок",
        "Крошечка-Хаврошечка": "Хаврошечка",
        "По щучьему велению": "По щучьему…",
        "Финист — Ясный сокол": "Финист",
        "Сестрица Алёнушка и братец Иванушка": "Алёнушка",
        "Иван-царевич и Серый волк": "Иван и волк",
        "Василиса Прекрасная": "Василиса",
        "Снегурушка и лиса": "Снегурушка",
    }
    return mapping.get(title, title)


def lantern_positions(n: int = 31) -> list[tuple[float, float]]:
    """
    Smooth S-curve from bottom-left (day 1) to upper palace approach (day 31).
    Coordinates are normalized fractions of image size; leave room for title + legend.
    """
    # Hand-tuned waypoints along the illustrated snowy path (blank map).
    waypoints = [
        (0.14, 0.68),  # start bottom-left (above legend)
        (0.26, 0.66),
        (0.38, 0.64),
        (0.50, 0.60),
        (0.62, 0.56),
        (0.70, 0.50),
        (0.66, 0.44),
        (0.54, 0.40),
        (0.42, 0.38),
        (0.30, 0.34),
        (0.26, 0.28),
        (0.36, 0.24),
        (0.48, 0.21),
        (0.58, 0.19),
        (0.66, 0.17),  # approach palace
    ]
    # Resample waypoints to n evenly spaced points by arc length
    seg_lens = []
    for i in range(len(waypoints) - 1):
        x0, y0 = waypoints[i]
        x1, y1 = waypoints[i + 1]
        seg_lens.append(math.hypot(x1 - x0, y1 - y0))
    total = sum(seg_lens) or 1.0
    targets = [total * i / (n - 1) for i in range(n)]
    pts: list[tuple[float, float]] = []
    for dist in targets:
        acc = 0.0
        for i, sl in enumerate(seg_lens):
            if acc + sl >= dist - 1e-9 or i == len(seg_lens) - 1:
                t = 0.0 if sl == 0 else (dist - acc) / sl
                t = min(1.0, max(0.0, t))
                x0, y0 = waypoints[i]
                x1, y1 = waypoints[i + 1]
                pts.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t))
                break
            acc += sl
    return pts


def main() -> None:
    src = next((p for p in SRC_CANDIDATES if p.exists()), None)
    if src is None:
        raise SystemExit("Map source not found")
    letters = json.loads((ROOT / "letters_data.json").read_text(encoding="utf-8"))
    if len(letters) != 31:
        raise SystemExit("expected 31 letters")

    im = Image.open(src).convert("RGBA")
    W, H = im.size
    overlay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    title_font = ImageFont.truetype(resolve_font("title"), size=max(26, W // 30))
    ui_font = ImageFont.truetype(resolve_font("ui"), size=max(13, W // 72))
    num_font = ImageFont.truetype(resolve_font("ui"), size=max(12, W // 78))
    small_font = ImageFont.truetype(resolve_font("ui"), size=max(11, W // 90))

    # Title plate
    title = "Тайна 31-го огонька"
    subtitle = "Карта сказок · зажги 31 огонёк"
    tw = draw.textlength(title, font=title_font)
    sw = draw.textlength(subtitle, font=ui_font)
    box_w = max(tw, sw) + 48
    box = (int((W - box_w) / 2), int(H * 0.025), int((W + box_w) / 2), int(H * 0.12))
    draw.rounded_rectangle(box, radius=14, fill=(245, 232, 205, 235), outline=(90, 45, 30, 230), width=3)
    draw.text(((W - tw) / 2, box[1] + 6), title, font=title_font, fill=(90, 30, 25, 255))
    draw.text(((W - sw) / 2, box[1] + 8 + title_font.size), subtitle, font=ui_font, fill=(50, 40, 30, 255))

    # Soft path underline so sequence is obvious
    pts = lantern_positions(31)
    path_xy = [(int(W * x), int(H * y)) for x, y in pts]
    if len(path_xy) >= 2:
        draw.line(path_xy, fill=(255, 210, 120, 90), width=max(6, W // 120))

    r = max(13, W // 58)
    for i, (x, y) in enumerate(path_xy, start=1):
        draw.ellipse((x - r - 5, y - r - 5, x + r + 5, y + r + 5), fill=(255, 200, 80, 110))
        draw.ellipse((x - r, y - r, x + r, y + r), fill=(255, 240, 200, 255), outline=(140, 65, 20, 255), width=2)
        label = str(i)
        nw = draw.textlength(label, font=num_font)
        draw.text((x - nw / 2, y - num_font.size * 0.55), label, font=num_font, fill=(90, 35, 15, 255))

    # Legend — 6 columns so all 31 titles fit without clipping
    legend_top = int(H * 0.78)
    draw.rounded_rectangle(
        (int(W * 0.025), legend_top, int(W * 0.975), int(H * 0.985)),
        radius=12,
        fill=(245, 232, 205, 245),
        outline=(90, 45, 30, 230),
        width=2,
    )
    cols = 6
    col_w = int(W * 0.93 / cols)
    legend_font = ImageFont.truetype(resolve_font("ui"), size=max(10, W // 100))
    row_h = int(legend_font.size * 1.55)
    x0 = int(W * 0.04)
    y0 = legend_top + 10
    for i, letter in enumerate(letters):
        c = i % cols
        rr = i // cols
        label = f"{letter['n']:02d}. {short_title(letter['title'])}"
        draw.text((x0 + c * col_w, y0 + rr * row_h), label, font=legend_font, fill=(40, 30, 25, 255))

    atomic_save_jpeg(Image.alpha_composite(im, overlay), OUT)
    print("wrote", OUT, "from", src.name)


if __name__ == "__main__":
    main()
