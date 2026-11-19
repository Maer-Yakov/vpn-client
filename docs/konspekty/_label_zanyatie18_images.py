#!/usr/bin/env python3
"""Overlay correct Russian labels on lesson-18 base illustrations."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SRC = Path("/opt/cursor/artifacts/assets")
OUT = Path(__file__).resolve().parent / "zanyatie-18-assets"
ART = Path("/opt/cursor/artifacts/zanyatie-18-assets")

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

TEAL = (42, 122, 140, 240)
TEAL_D = (26, 90, 106, 255)
CORAL = (212, 122, 106, 240)
LEAF = (90, 143, 123, 240)
GOLD = (201, 162, 78, 240)
RED = (196, 92, 92, 240)
WHITE = (255, 255, 255, 255)
INK = (30, 47, 58, 255)
CREAM = (247, 250, 252, 245)
SOFT = (232, 240, 244, 250)


def font(size, bold=False):
    return ImageFont.truetype(FONT_B if bold else FONT, size)


def load_base(name, size=(1600, 900)):
    im = Image.open(SRC / name).convert("RGBA")
    return im.resize(size, Image.Resampling.LANCZOS)


def rounded_rect(draw, xy, fill, radius=18):
    draw.rounded_rectangle(xy, radius=radius, fill=fill)


def pill(draw, x, y, w, h, text, fill, fsize=28):
    rounded_rect(draw, (x, y, x + w, y + h), fill, radius=h // 2)
    f = font(fsize, bold=True)
    bbox = f.getbbox(text)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((x + (w - tw) / 2, y + (h - th) / 2 - 2), text, font=f, fill=WHITE)


def caption_bar(im, text, fill=TEAL_D):
    draw = ImageDraw.Draw(im)
    w, h = im.size
    bar_h = 110
    rounded_rect(draw, (40, h - bar_h - 30, w - 40, h - 30), fill, radius=24)
    f = font(36, bold=True)
    bbox = f.getbbox(text)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((w - tw) / 2, h - bar_h - 30 + (bar_h - th) / 2 - 2), text, font=f, fill=WHITE)
    return im


def cover(draw, xy, fill=CREAM):
    draw.rectangle(xy, fill=fill)


def save(im, name):
    OUT.mkdir(parents=True, exist_ok=True)
    ART.mkdir(parents=True, exist_ok=True)
    rgb = im.convert("RGB")
    rgb.save(OUT / name, quality=92)
    rgb.save(ART / name, quality=92)
    print("OK", name)


def make_01():
    im = load_base("z18-01-base.jpg")
    draw = ImageDraw.Draw(im)
    cover(draw, (0, 720, 1600, 900), CREAM)
    for i, (t, c) in enumerate([("ухо", TEAL), ("голос", GOLD), ("ладушки", CORAL), ("платочек", LEAF)]):
        pill(draw, 80 + i * 380, 760, 340, 70, t, c, fsize=30)
    save(im, "z18-01-title.jpg")


def make_02():
    im = load_base("z18-02-base.jpg")
    draw = ImageDraw.Draw(im)
    cover(draw, (60, 30, 720, 140), CREAM)
    cover(draw, (880, 30, 1540, 140), CREAM)
    pill(draw, 100, 50, 520, 70, "КОНЦЕРТНЫЙ НОМЕР ✕", RED, fsize=26)
    pill(draw, 920, 50, 560, 70, "ЛАСКОВОЕ ПЕНИЕ РЯДОМ ✓", TEAL, fsize=24)
    caption_bar(im, "Выбираем отклик голосом, а не номер")
    save(im, "z18-02-doors.jpg")


def make_03():
    im = Image.new("RGBA", (1200, 900), (247, 250, 252, 255))
    draw = ImageDraw.Draw(im)
    rounded_rect(draw, (120, 60, 1080, 840), (255, 252, 245, 255), radius=20)
    rounded_rect(draw, (420, 30, 780, 90), TEAL_D, radius=12)
    draw.text((250, 120), "Мини-пение 80–100 секунд", font=font(34, True), fill=TEAL_D)
    draw.line((220, 180, 980, 180), fill=TEAL, width=3)
    rows = [
        "☐   интерес / упражнение 15–25 сек",
        "☐   показ фразы + подхват",
        "☐   можно / нельзя для 1–3 лет",
        "☐   мягкий стоп и похвала",
        "☐   это для яслей, не копия 3–4",
    ]
    for i, t in enumerate(rows):
        y = 230 + i * 100
        rounded_rect(draw, (180, y, 1020, y + 80), SOFT, radius=16)
        draw.text((220, y + 22), t, font=font(26, True), fill=INK)
    save(im, "z18-03-goal.jpg")


def make_04():
    im = load_base("z18-04-base.jpg")
    draw = ImageDraw.Draw(im)
    cover(draw, (0, 0, 1600, 75), CREAM)
    pill(draw, 300, 12, 1000, 50, "Пение развивает шесть сфер", TEAL_D, fsize=28)
    for i, t in enumerate(["слух", "речь", "дыхание", "эмоции", "общение", "память"]):
        pill(draw, 40 + i * 260, 780, 240, 55, t, TEAL if i % 2 == 0 else LEAF, fsize=22)
    save(im, "z18-04-spheres.jpg")


def make_05():
    im = load_base("z18-05-base.jpg")
    draw = ImageDraw.Draw(im)
    cover(draw, (0, 0, 1600, 90), CREAM)
    pill(draw, 280, 18, 1040, 55, "Три ступени внутри 1–3 лет", TEAL_D, fsize=28)
    for i, (t, c) in enumerate([("1–1,5 · слушание", TEAL), ("1,5–2 · звук/слог", GOLD), ("2–3 · фраза", LEAF)]):
        pill(draw, 80 + i * 500, 780, 460, 55, t, c, fsize=22)
    save(im, "z18-05-ages.jpg")


def make_06():
    im = load_base("z18-06-base.jpg", size=(1200, 900))
    draw = ImageDraw.Draw(im)
    cover(draw, (0, 0, 1200, 90), CREAM)
    pill(draw, 40, 18, 240, 55, "мягко ✓", LEAF, fsize=26)
    pill(draw, 480, 18, 240, 55, "пауза", GOLD, fsize=26)
    pill(draw, 920, 18, 240, 55, "крик ✕", RED, fsize=26)
    caption_bar(im, "Светофор бережного пения")
    save(im, "z18-06-traffic.jpg")


def make_07():
    im = load_base("z18-07-base.jpg")
    draw = ImageDraw.Draw(im)
    cover(draw, (0, 0, 1600, 75), CREAM)
    pill(draw, 300, 12, 1000, 50, "Семь задач обучения пению", TEAL_D, fsize=28)
    caption_bar(im, "интерес → слушание → звук/слог → фраза → мини-репертуар")
    save(im, "z18-07-tasks.jpg")


def make_08():
    im = load_base("z18-08-base.jpg")
    draw = ImageDraw.Draw(im)
    cover(draw, (0, 0, 1600, 75), CREAM)
    pill(draw, 280, 12, 1040, 50, "Этапы: интерес → слушание → подхват → стоп", TEAL_D, fsize=24)
    stages = ["интерес", "слушание", "узнавание", "подхват", "игра", "стоп"]
    for i, t in enumerate(stages):
        pill(draw, 40 + i * 260, 780, 240, 55, t, TEAL if i % 2 == 0 else LEAF, fsize=20)
    save(im, "z18-08-stages.jpg")


def make_09():
    im = load_base("z18-09-base.jpg")
    draw = ImageDraw.Draw(im)
    cover(draw, (0, 0, 1600, 75), CREAM)
    pill(draw, 280, 12, 1040, 50, "Упражнения 15–30 секунд", TEAL_D, fsize=28)
    labels = ["слушание", "дыхание", "мягкий звук", "подражание", "подхват", "ладушки"]
    for i, t in enumerate(labels):
        pill(draw, 40 + i * 260, 780, 240, 55, t, TEAL if i % 2 == 0 else GOLD, fsize=18)
    save(im, "z18-09-exercises.jpg")


def make_10():
    im = load_base("z18-10-base.jpg")
    draw = ImageDraw.Draw(im)
    cover(draw, (0, 0, 1600, 90), CREAM)
    pill(draw, 80, 20, 400, 55, "беру ✓", LEAF, fsize=30)
    pill(draw, 1080, 20, 400, 55, "не беру ✕", RED, fsize=30)
    caption_bar(im, "Репертуар — педагогическое решение")
    save(im, "z18-10-repertoire.jpg")


def make_11():
    im = load_base("z18-11-base.jpg")
    draw = ImageDraw.Draw(im)
    cover(draw, (0, 0, 1600, 80), CREAM)
    pill(draw, 300, 15, 1000, 50, "Мини-тренинг · 80–100 секунд", TEAL, fsize=28)
    caption_bar(im, "интерес → показ → подхват → стоп")
    save(im, "z18-11-training.jpg")


def make_12():
    im = load_base("z18-12-base.jpg")
    draw = ImageDraw.Draw(im)
    cover(draw, (0, 0, 1600, 80), CREAM)
    pill(draw, 220, 15, 1160, 50, "Пение начинается с вашего мягкого «рядом»", TEAL_D, fsize=24)
    caption_bar(im, "Ласковый голос · слушание · короткий подхват · пауза")
    save(im, "z18-12-finale.jpg")


def main():
    make_01()
    make_02()
    make_03()
    make_04()
    make_05()
    make_06()
    make_07()
    make_08()
    make_09()
    make_10()
    make_11()
    make_12()
    print("All 12 labeled images ready")


if __name__ == "__main__":
    main()
