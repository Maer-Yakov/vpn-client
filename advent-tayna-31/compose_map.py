#!/usr/bin/env python3
"""Overlay clean Russian labels on the folk adventure map."""

from __future__ import annotations

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
SRC = ASSETS / "map-gorod-tihih-fonarey-folk.jpg"
OUT = ROOT / "cards" / "map-advent.jpg"

FONT_CANDIDATES = {
    "title": [
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
        "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf",
    ],
    "ui": [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
    ],
}

LABELS = [
    (0.50, 0.07, "Тайна 31-го огонька", 40, True),
    (0.50, 0.13, "Карта сказочных огоньков", 22, False),
    (0.22, 0.30, "Деревня сказок", 20, False),
    (0.48, 0.34, "Теремок", 20, False),
    (0.72, 0.30, "Лес чудес", 20, False),
    (0.30, 0.55, "Река", 18, False),
    (0.55, 0.58, "Зимовье", 18, False),
    (0.78, 0.55, "Дворец", 18, False),
    (0.50, 0.78, "Площадь огоньков", 20, False),
    (0.50, 0.93, "31 огонёк · Дедушка Мороз и Искорка", 17, False),
]


def resolve_font(kind: str) -> str:
    for path in FONT_CANDIDATES[kind]:
        if Path(path).exists():
            return path
    raise SystemExit(
        f"No Cyrillic font found for '{kind}'. Install fonts-liberation or fonts-dejavu."
    )


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


def main() -> None:
    if not SRC.exists():
        raise SystemExit(f"Map source not found: {SRC}")
    im = Image.open(SRC).convert("RGBA")
    W, H = im.size
    overlay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    for x_f, y_f, text, size, is_title in LABELS:
        font = ImageFont.truetype(
            resolve_font("title" if is_title else "ui"),
            size=max(14, int(W * size / 1400)),
        )
        x, y = int(W * x_f), int(H * y_f)
        lines = text.split("\n")
        line_h = int(font.size * 1.2)
        total_h = line_h * len(lines)
        max_w = max(draw.textlength(line, font=font) for line in lines)
        pad = 8
        box = (
            int(x - max_w / 2 - pad),
            int(y - total_h / 2 - pad / 2),
            int(x + max_w / 2 + pad),
            int(y + total_h / 2 + pad / 2),
        )
        draw.rounded_rectangle(
            box, radius=10, fill=(245, 232, 205, 220), outline=(90, 45, 30, 220), width=2
        )
        yy = y - total_h / 2
        for line in lines:
            tw = draw.textlength(line, font=font)
            fill = (90, 30, 25, 255) if is_title else (40, 35, 30, 255)
            draw.text((x - tw / 2, yy), line, font=font, fill=fill)
            yy += line_h

    atomic_save_jpeg(Image.alpha_composite(im, overlay), OUT)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
