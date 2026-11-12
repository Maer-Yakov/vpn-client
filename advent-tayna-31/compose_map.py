#!/usr/bin/env python3
"""Overlay clean Russian labels on the folk adventure map."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ASSETS = Path("/opt/cursor/artifacts/assets")
ROOT = Path(__file__).resolve().parent
SRC = ASSETS / "map-gorod-tihih-fonarey-folk.jpg"
OUT = ROOT / "cards" / "map-gorod-tihih-fonarey.png"
OUT_ARTIFACT = ASSETS / "map-gorod-tihih-fonarey-labeled.jpg"

FONT = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
FONT_UI = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# Approximate positions as fractions of width/height on the generated map.
LABELS = [
    (0.50, 0.07, "Город Тихих Фонарей", 42, True),
    (0.48, 0.28, "Городская башня", 26, False),
    (0.22, 0.34, "Мастерская Луми", 22, False),
    (0.72, 0.33, "Мастерская фонарей", 22, False),
    (0.18, 0.52, "Улица Тихих\nКолокольчиков", 20, False),
    (0.78, 0.52, "Почта Снежка", 22, False),
    (0.50, 0.58, "Река Тишины", 22, False),
    (0.50, 0.68, "Ёлочная площадь", 22, False),
    (0.20, 0.78, "Лес забытых чудес", 22, False),
    (0.78, 0.76, "Библиотека\nвоспоминаний", 20, False),
    (0.35, 0.86, "Дом семьи", 22, False),
    (0.62, 0.86, "Северный холм", 22, False),
    (0.82, 0.22, "Последняя башня", 22, False),
    (0.50, 0.93, "Огоньки 1–31 · семь тайных символов", 18, False),
]


def main() -> None:
    im = Image.open(SRC).convert("RGBA")
    W, H = im.size
    overlay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    for x_f, y_f, text, size, is_title in LABELS:
        font = ImageFont.truetype(FONT if is_title else FONT_UI, size=max(14, int(W * size / 1400)))
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
        # soft parchment label plate to cover garbled AI text
        draw.rounded_rectangle(box, radius=10, fill=(245, 232, 205, 210), outline=(90, 45, 30, 220), width=2)
        yy = y - total_h / 2
        for line in lines:
            tw = draw.textlength(line, font=font)
            fill = (90, 30, 25, 255) if is_title else (40, 35, 30, 255)
            draw.text((x - tw / 2, yy), line, font=font, fill=fill)
            yy += line_h

    out = Image.alpha_composite(im, overlay).convert("RGB")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.save(OUT, quality=95)
    out.save(OUT_ARTIFACT, quality=95)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
