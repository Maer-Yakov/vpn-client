#!/usr/bin/env python3
"""Compose Ded Moroz advent letters with reliable fixed layouts."""

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

# Fixed content boxes as fractions of frame size (left, top, right, bottom).
# Scene sits at the bottom of the main parchment. Styles with a lower cartouche
# get a short footer line there (cartouche box).
LAYOUT = {
    "khokhloma": {
        "content": (0.16, 0.13, 0.84, 0.58),
        "scene": (0.17, 0.58, 0.83, 0.90),
        "badge": (0.50, 0.095),
        "cartouche": None,
    },
    "gzhel": {
        "content": (0.16, 0.14, 0.84, 0.56),
        "scene": (0.17, 0.56, 0.83, 0.86),
        "badge": (0.50, 0.10),
        "cartouche": (0.32, 0.90, 0.68, 0.96),
    },
    "dymkovo": {
        "content": (0.17, 0.15, 0.83, 0.56),
        "scene": (0.18, 0.56, 0.82, 0.88),
        "badge": (0.50, 0.11),
        "cartouche": None,
    },
    "gorodets": {
        "content": (0.16, 0.14, 0.84, 0.55),
        "scene": (0.17, 0.55, 0.83, 0.86),
        "badge": (0.50, 0.10),
        "cartouche": None,
    },
    "zhostovo": {
        # Main parchment ends ~0.70; bottom lozenge ~0.885–0.947
        "content": (0.18, 0.135, 0.82, 0.50),
        "scene": (0.20, 0.505, 0.80, 0.695),
        "badge": (0.50, 0.072),
        "cartouche": (0.28, 0.885, 0.72, 0.947),
    },
    "palekh": {
        "content": (0.16, 0.135, 0.84, 0.54),
        "scene": (0.18, 0.545, 0.82, 0.80),
        "badge": (0.50, 0.09),
        "cartouche": (0.30, 0.865, 0.70, 0.945),
    },
    "mezen": {
        "content": (0.15, 0.135, 0.85, 0.55),
        "scene": (0.16, 0.55, 0.84, 0.88),
        "badge": (0.50, 0.095),
        "cartouche": None,
    },
    "filimonovo": {
        "content": (0.16, 0.14, 0.84, 0.55),
        "scene": (0.17, 0.55, 0.83, 0.88),
        "badge": (0.50, 0.10),
        "cartouche": None,
    },
}

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

INK = (45, 32, 22)
INK_SOFT = (95, 75, 55)
ACCENT = (150, 45, 30)
BADGE_FILL = (252, 246, 230)
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


def box_px(fracs: tuple[float, float, float, float], W: int, H: int) -> tuple[int, int, int, int]:
    l, t, r, b = fracs
    return int(W * l), int(H * t), int(W * r), int(H * b)


def crop_scene_art(im: Image.Image) -> Image.Image:
    """Strip baked decorative frames / cream margins from scene artworks."""
    W, H = im.size
    # Scenes are generated with ornate borders; crop to the illustration core.
    x0, y0 = int(W * 0.095), int(H * 0.115)
    x1, y1 = int(W * 0.905), int(H * 0.885)
    return im.crop((x0, y0, x1, y1))


def cover_image(im: Image.Image, box: tuple[int, int, int, int]) -> Image.Image:
    """Scale image to fully cover the box (center-crop), no letterbox bars."""
    x0, y0, x1, y1 = box
    bw, bh = max(1, x1 - x0), max(1, y1 - y0)
    scale = max(bw / im.width, bh / im.height)
    nw, nh = max(1, int(im.width * scale)), max(1, int(im.height * scale))
    resized = im.resize((nw, nh), Image.Resampling.LANCZOS)
    left = max(0, (nw - bw) // 2)
    top = max(0, (nh - bh) // 2)
    return resized.crop((left, top, left + bw, top + bh))


def atomic_save_jpeg(im: Image.Image, dest: Path, quality: int = 93) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{dest.stem}.", suffix=".jpg", dir=dest.parent)
    os.close(fd)
    tmp = Path(tmp_name)
    try:
        im.convert("RGB").save(tmp, format="JPEG", quality=quality, optimize=True)
        os.replace(tmp, dest)
    finally:
        tmp.unlink(missing_ok=True)


def frame_path_for(style: str) -> Path:
    for ext in (".jpg", ".png"):
        path = FRAMES / f"frame-{style}{ext}"
        if path.exists():
            return path
    raise FileNotFoundError(f"missing frame template: frame-{style}")


def scene_path_for(n: int) -> Path:
    for ext in (".jpg", ".png"):
        path = SCENES / f"scene-{n:02d}{ext}"
        if path.exists():
            return path
    raise FileNotFoundError(f"missing scene for day {n}")


def draw_centered(draw, text, font, cx, y, fill):
    tw = draw.textlength(text, font=font)
    draw.text((cx - tw / 2, y), text, font=font, fill=fill)
    return y + int(font.size * 1.2)


def compose_one(letter: dict) -> Path:
    style = letter["style"]
    layout = LAYOUT[style]
    base = Image.open(frame_path_for(style)).convert("RGBA")
    W, H = base.size
    draw = ImageDraw.Draw(base)

    # --- scene: cover-fill bottom parchment band (no white side bars) ---
    sx0, sy0, sx1, sy1 = box_px(layout["scene"], W, H)
    scene = crop_scene_art(Image.open(scene_path_for(letter["n"])).convert("RGBA"))
    covered = cover_image(scene, (sx0, sy0, sx1, sy1))
    # soft rounded plate + thin border
    plate = Image.new("RGBA", (sx1 - sx0, sy1 - sy0), (245, 232, 210, 255))
    base.alpha_composite(plate, (sx0, sy0))
    base.alpha_composite(covered.convert("RGBA"), (sx0, sy0))
    draw = ImageDraw.Draw(base)
    draw.rectangle((sx0, sy0, sx1 - 1, sy1 - 1), outline=(120, 70, 40, 200), width=2)

    # --- badge centered on frame medallion ---
    bx_f, by_f = layout["badge"]
    cx, cy = int(W * bx_f), int(H * by_f)
    badge_r = int(W * 0.058)
    draw.ellipse(
        (cx - badge_r - 3, cy - badge_r - 3, cx + badge_r + 3, cy + badge_r + 3),
        fill=(210, 170, 70, 255),
    )
    draw.ellipse(
        (cx - badge_r, cy - badge_r, cx + badge_r, cy + badge_r),
        fill=BADGE_FILL,
        outline=BADGE_STROKE,
        width=max(3, W // 220),
    )
    num_font = load_font("ui_bold", max(22, W // 24))
    num = f"№{letter['n']}"
    nw = draw.textlength(num, font=num_font)
    nh = num_font.size
    draw.text((cx - nw / 2, cy - nh * 0.55), num, font=num_font, fill=BADGE_STROKE)

    # --- text content ---
    x0, y0, x1, y1 = box_px(layout["content"], W, H)
    pad = int((x1 - x0) * 0.04)
    tx0, tx1 = x0 + pad, x1 - pad
    width = tx1 - tx0
    y = y0 + pad // 2
    cx_text = (tx0 + tx1) // 2

    title_font = load_font("title", max(24, W // 20))
    body_font = load_font("body", max(16, W // 34))
    small_font = load_font("ui", max(12, W // 42))
    label_font = load_font("ui_bold", max(14, W // 36))
    sign_font = load_font("title", max(15, W // 32))

    date_line = f"{letter['n']} декабря"
    y = draw_centered(draw, date_line, small_font, cx_text, y, INK_SOFT)

    for line in wrap(draw, letter["title"], title_font, width):
        y = draw_centered(draw, line, title_font, cx_text, y, INK)
    y += int(pad * 0.15)

    teaser = letter.get("teaser") or ""
    task_lines = wrap(draw, letter["task"], body_font, width)
    tip_lines = wrap(draw, letter["tip"], small_font, width)
    # Put "Завтра" into bottom cartouche when available to free parchment space
    use_cartouche = layout.get("cartouche") is not None and bool(teaser)
    teaser_lines = [] if use_cartouche else (wrap(draw, teaser, body_font, width) if teaser else [])
    sig = letter.get("signature", "Дедушка Мороз и Искорка")

    reserved = (
        int(label_font.size * 1.3)
        + len(task_lines) * int(body_font.size * 1.26)
        + int(pad * 0.2)
        + (int(label_font.size * 1.15) + len(teaser_lines) * int(body_font.size * 1.22) if teaser_lines else 0)
        + int(small_font.size * 1.25)
        + len(tip_lines) * int(small_font.size * 1.22)
        + int(sign_font.size * 1.45)
        + pad // 2
    )
    story_limit = y1 - reserved

    # Greeting + sender always print; only the story may be omitted if space is tight.
    for block, required in (
        (letter["greeting"], True),
        (letter["from"], True),
        (letter["story"], False),
    ):
        lines = wrap(draw, block, body_font, width)
        need = len(lines) * int(body_font.size * 1.26) + int(pad * 0.12)
        if (not required) and y + need > story_limit:
            continue
        for line in lines:
            draw.text((tx0, y), line, font=body_font, fill=INK)
            y += int(body_font.size * 1.26)
        y += int(pad * 0.12)

    y = max(y + int(pad * 0.08), y1 - reserved)

    draw.text((tx0, y), "★ Задание:", font=label_font, fill=ACCENT)
    y += int(label_font.size * 1.3)
    for line in task_lines:
        draw.text((tx0, y), line, font=body_font, fill=INK)
        y += int(body_font.size * 1.26)
    y += int(pad * 0.12)

    if teaser_lines:
        draw.text((tx0, y), "Завтра:", font=label_font, fill=INK_SOFT)
        y += int(label_font.size * 1.15)
        for line in teaser_lines:
            draw.text((tx0, y), line, font=body_font, fill=INK)
            y += int(body_font.size * 1.22)
        y += int(pad * 0.1)

    draw.text((tx0, y), "Родителям:", font=small_font, fill=INK_SOFT)
    y += int(small_font.size * 1.25)
    for line in tip_lines:
        draw.text((tx0, y), line, font=small_font, fill=INK_SOFT)
        y += int(small_font.size * 1.22)

    sw = draw.textlength(sig, font=sign_font)
    sig_y = min(max(y + int(pad * 0.15), sy0 - sign_font.size - 6), sy0 - sign_font.size - 3)
    draw.text((cx_text - sw / 2, sig_y), sig, font=sign_font, fill=ACCENT)

    # --- bottom cartouche: teaser or lantern cue ---
    if layout.get("cartouche"):
        cx0, cy0, cx1, cy1 = box_px(layout["cartouche"], W, H)
        cart_font = load_font("ui_bold", max(11, W // 48))
        if teaser and use_cartouche:
            label = "Завтра: "
            # Fit teaser into cartouche; shorten gracefully if needed
            full = label + teaser
            lines = wrap(draw, full, cart_font, cx1 - cx0 - 8)
            if len(lines) > 2:
                lines = wrap(draw, label + teaser, cart_font, cx1 - cx0 - 8)[:2]
                if len(lines) == 2 and not lines[1].endswith("…"):
                    # trim second line
                    while lines[1] and draw.textlength(lines[1] + "…", font=cart_font) > (cx1 - cx0 - 8):
                        lines[1] = lines[1][:-1]
                    lines[1] = lines[1].rstrip(".,;:") + "…"
            line_h = int(cart_font.size * 1.2)
            total_h = len(lines) * line_h
            ty = cy0 + max(2, ((cy1 - cy0) - total_h) // 2)
            for line in lines:
                lw = draw.textlength(line, font=cart_font)
                draw.text(((cx0 + cx1) / 2 - lw / 2, ty), line, font=cart_font, fill=INK)
                ty += line_h
        else:
            footer = f"Зажги огонёк №{letter['n']} на карте"
            fw = draw.textlength(footer, font=cart_font)
            draw.text(
                ((cx0 + cx1) / 2 - fw / 2, (cy0 + cy1) / 2 - cart_font.size * 0.55),
                footer,
                font=cart_font,
                fill=INK,
            )

    out = OUT / f"letter-{letter['n']:02d}-{style}.jpg"
    atomic_save_jpeg(base, out)
    return out


def require_all_assets(data: list[dict]) -> None:
    missing = []
    for letter in data:
        try:
            frame_path_for(letter["style"])
            scene_path_for(letter["n"])
        except FileNotFoundError as exc:
            missing.append(str(exc))
    if missing:
        raise SystemExit("Incomplete artwork:\n  - " + "\n  - ".join(missing))


def main() -> None:
    data = json.loads((ROOT / "letters_data.json").read_text(encoding="utf-8"))
    if len(data) != 31:
        raise SystemExit(f"expected 31 letters, got {len(data)}")
    require_all_assets(data)
    for letter in data:
        if len(letter["task"]) < 20:
            raise SystemExit(f"task too short for day {letter['n']}")
        path = compose_one(letter)
        print("wrote", path)
    print("done: 31 cards")


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:  # pragma: no cover
        sys.exit(0)
