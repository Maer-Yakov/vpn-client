#!/usr/bin/env python3
"""Build print-ready PDFs for the advent calendar."""

from __future__ import annotations

import shutil
from pathlib import Path

import img2pdf
from PIL import Image

ROOT = Path(__file__).resolve().parent
CARDS = ROOT / "cards"
OUT = ROOT / "print"
OUT.mkdir(exist_ok=True)

# 300 dpi
A5 = (1748, 2480)  # 148×210 mm
A4 = (2480, 3508)  # 210×297 mm
A4_LAND = (3508, 2480)  # 297×210 mm


def fit_on_canvas(
    src: Path,
    size: tuple[int, int],
    bg: tuple[int, int, int] = (255, 255, 255),
    margin_ratio: float = 0.03,
) -> Image.Image:
    im = Image.open(src).convert("RGB")
    W, H = size
    m = int(min(W, H) * margin_ratio)
    box_w, box_h = W - 2 * m, H - 2 * m
    scale = min(box_w / im.width, box_h / im.height)
    nw, nh = int(im.width * scale), int(im.height * scale)
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, bg)
    canvas.paste(im, ((W - nw) // 2, (H - nh) // 2))
    return canvas


def save_temp(im: Image.Image, name: str) -> Path:
    path = OUT / name
    im.save(path, quality=90, optimize=True, dpi=(300, 300))
    return path


def letters() -> list[Path]:
    paths = []
    for n in range(1, 32):
        matches = sorted(CARDS.glob(f"letter-{n:02d}-*.jpg"))
        if not matches:
            raise FileNotFoundError(f"missing letter {n}")
        paths.append(matches[0])
    return paths


def build() -> None:
    temps: list[Path] = []
    try:
        map_src = CARDS / "map-advent.jpg"
        if not map_src.exists():
            map_src = CARDS / "map-gorod-tihih-fonarey.jpg"
        map_page = save_temp(fit_on_canvas(map_src, A4_LAND, margin_ratio=0.02), "_map.jpg")
        temps.append(map_page)

        letter_pages: list[Path] = []
        for i, src in enumerate(letters(), start=1):
            p = save_temp(fit_on_canvas(src, A5, margin_ratio=0.025), f"_letter_{i:02d}.jpg")
            temps.append(p)
            letter_pages.append(p)

        # Combined: map + 31 letters
        combined = ROOT / "tayna-31-ogonyka-print.pdf"
        with open(combined, "wb") as f:
            f.write(img2pdf.convert([str(map_page), *[str(p) for p in letter_pages]], dpi=300))
        shutil.copy(combined, ROOT / "Тайна_31_огонька_печатный.pdf")

        # Letters only A5
        with open(OUT / "letters-a5.pdf", "wb") as f:
            f.write(img2pdf.convert([str(p) for p in letter_pages], dpi=300))

        # Map only
        with open(OUT / "map-a4-landscape.pdf", "wb") as f:
            f.write(img2pdf.convert([str(map_page)], dpi=300))

        # 2-up A4: two letters per portrait page (for home print)
        two_up_pages: list[Path] = []
        srcs = letters()
        for i in range(0, len(srcs), 2):
            page = Image.new("RGB", A4, (255, 255, 255))
            top = fit_on_canvas(srcs[i], (A4[0], A4[1] // 2), margin_ratio=0.04)
            page.paste(top, (0, 0))
            if i + 1 < len(srcs):
                bottom = fit_on_canvas(srcs[i + 1], (A4[0], A4[1] // 2), margin_ratio=0.04)
                page.paste(bottom, (0, A4[1] // 2))
            # cut guide
            from PIL import ImageDraw

            draw = ImageDraw.Draw(page)
            y = A4[1] // 2
            draw.line((40, y, A4[0] - 40, y), fill=(180, 180, 180), width=2)
            p = save_temp(page, f"_two_up_{i // 2 + 1:02d}.jpg")
            temps.append(p)
            two_up_pages.append(p)

        with open(OUT / "letters-a4-2up.pdf", "wb") as f:
            f.write(img2pdf.convert([str(p) for p in two_up_pages], dpi=300))

        print("wrote", combined, f"{combined.stat().st_size / 1e6:.1f} MB")
        print("wrote", OUT / "letters-a5.pdf")
        print("wrote", OUT / "letters-a4-2up.pdf")
        print("wrote", OUT / "map-a4-landscape.pdf")
    finally:
        for p in temps:
            p.unlink(missing_ok=True)


if __name__ == "__main__":
    build()
