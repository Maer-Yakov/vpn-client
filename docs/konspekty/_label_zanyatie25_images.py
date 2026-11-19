#!/usr/bin/env python3
"""Overlay correct Russian labels on artistic song-image illustrations."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SRC = Path("/opt/cursor/artifacts/assets")
OUT = Path(__file__).resolve().parent / "zanyatie-25-assets"
ART = Path("/opt/cursor/artifacts/zanyatie-25-assets")

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
    f = font(32, bold=True)
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
    try:
        rgb.save(ART / name, quality=92)
    except BlockingIOError:
        pass
    print("OK", name)


def make_01():
    im = load_base("z25-01-base.jpg")
    draw = ImageDraw.Draw(im)
    cover(draw, (0, 720, 1600, 900), CREAM)
    for i, (t, c) in enumerate([("образ", TEAL), ("голос", GOLD), ("мимика", CORAL), ("жест", LEAF)]):
        pill(draw, 80 + i * 380, 760, 340, 70, t, c, fsize=28)
    save(im, "z25-01-title.jpg")


def make_02():
    im = load_base("z25-02-base.jpg")
    draw = ImageDraw.Draw(im)
    cover(draw, (60, 30, 720, 140), CREAM)
    cover(draw, (880, 30, 1540, 140), CREAM)
    pill(draw, 80, 50, 560, 70, "ПЛОСКОЕ ПЕНИЕ ✕", RED, fsize=26)
    pill(draw, 900, 50, 560, 70, "ПЕСНЯ В ОБРАЗЕ ✓", TEAL, fsize=26)
    caption_bar(im, "Артистизм — не громкость и не гримаса")
    save(im, "z25-02-doors.jpg")


def make_03():
    im = Image.new("RGBA", (1200, 900), (247, 250, 252, 255))
    draw = ImageDraw.Draw(im)
    rounded_rect(draw, (120, 60, 1080, 840), (255, 252, 245, 255), radius=20)
    rounded_rect(draw, (240, 30, 960, 90), TEAL_D, radius=12)
    draw.text((300, 45), "Мини-фрагмент 90–120 секунд", font=font(28, True), fill=WHITE)
    draw.text((180, 130), "Образ песни · короткий показ", font=font(28, True), fill=TEAL_D)
    draw.line((180, 185, 1020, 185), fill=TEAL, width=3)
    rows = [
        "☐   вход в образ",
        "☐   мягкий показ",
        "☐   фраза + 1 средство",
        "☐   короткий прогон",
        "☐   мягкий стоп",
    ]
    for i, t in enumerate(rows):
        y = 230 + i * 100
        rounded_rect(draw, (180, y, 1020, y + 80), SOFT, radius=16)
        draw.text((220, y + 22), t, font=font(26, True), fill=INK)
    save(im, "z25-03-goal.jpg")


def make_04():
    im = load_base("z25-04-base.jpg")
    draw = ImageDraw.Draw(im)
    cover(draw, (0, 0, 1600, 75), CREAM)
    pill(draw, 260, 12, 1080, 50, "Компоненты художественного образа", TEAL_D, fsize=26)
    labels = ["герой", "настроение", "музыка", "голос", "мимика", "жест", "игра"]
    for i, t in enumerate(labels):
        pill(draw, 20 + i * 225, 780, 210, 55, t, TEAL if i % 2 == 0 else GOLD, fsize=16)
    save(im, "z25-04-components.jpg")


def make_05():
    im = load_base("z25-05-base.jpg")
    draw = ImageDraw.Draw(im)
    cover(draw, (0, 0, 1600, 80), CREAM)
    pill(draw, 280, 15, 1040, 50, "Артистизм по возрасту", TEAL_D, fsize=28)
    for i, (t, c) in enumerate([("1,5–3", TEAL), ("3–5", GOLD), ("5–7", LEAF)]):
        pill(draw, 120 + i * 480, 780, 420, 55, t, c, fsize=22)
    save(im, "z25-05-ages.jpg")


def make_06():
    im = load_base("z25-06-base.jpg")
    draw = ImageDraw.Draw(im)
    cover(draw, (0, 0, 1600, 80), CREAM)
    pill(draw, 220, 15, 1160, 50, "Эмоция · мимика · жест · голос", TEAL_D, fsize=26)
    for i, (t, c) in enumerate([("эмоция", TEAL), ("мимика", GOLD), ("жест", CORAL), ("голос ✓", LEAF)]):
        pill(draw, 60 + i * 385, 780, 360, 55, t, c, fsize=22)
    save(im, "z25-06-means.jpg")


def make_07():
    im = load_base("z25-07-base.jpg")
    draw = ImageDraw.Draw(im)
    cover(draw, (0, 0, 1600, 75), CREAM)
    pill(draw, 280, 12, 1040, 50, "Практическая разминка", TEAL_D, fsize=28)
    labels = ["тело", "лицо", "гласные", "эхо", "жест", "стоп"]
    for i, t in enumerate(labels):
        pill(draw, 40 + i * 260, 780, 240, 55, t, TEAL if i % 2 == 0 else GOLD, fsize=20)
    save(im, "z25-07-warmup.jpg")


def make_08():
    im = load_base("z25-08-base.jpg")
    draw = ImageDraw.Draw(im)
    cover(draw, (0, 0, 1600, 80), CREAM)
    pill(draw, 300, 15, 1000, 50, "Карточка анализа образа песни", TEAL_D, fsize=26)
    caption_bar(im, "вход → слушание → разбор → фраза → средства → прогон → стоп")
    save(im, "z25-08-analysis.jpg")


def make_09():
    im = load_base("z25-09-base.jpg")
    draw = ImageDraw.Draw(im)
    cover(draw, (0, 0, 1600, 75), CREAM)
    pill(draw, 280, 12, 1040, 50, "Банк игр на артистизм", TEAL_D, fsize=28)
    labels = ["настроение", "жест", "эхо", "кто поёт", "тихо", "очередь"]
    for i, t in enumerate(labels):
        pill(draw, 40 + i * 260, 780, 240, 55, t, TEAL if i % 2 == 0 else GOLD, fsize=16)
    save(im, "z25-09-games.jpg")


def make_10():
    im = load_base("z25-10-base.jpg")
    draw = ImageDraw.Draw(im)
    cover(draw, (0, 0, 1600, 80), CREAM)
    pill(draw, 280, 15, 1040, 50, "Границы артистизма в ДОУ", TEAL_D, fsize=26)
    pill(draw, 80, 780, 520, 55, "можно ✓", LEAF, fsize=24)
    pill(draw, 1000, 780, 520, 55, "нельзя ✕", RED, fsize=24)
    save(im, "z25-10-limits.jpg")


def make_11():
    im = load_base("z25-11-base.jpg")
    draw = ImageDraw.Draw(im)
    cover(draw, (0, 0, 1600, 80), CREAM)
    pill(draw, 280, 15, 1040, 50, "Микропреподавание · 90–120 сек", TEAL, fsize=26)
    caption_bar(im, "образ → показ → проба → прогон → стоп")
    save(im, "z25-11-micro.jpg")


def make_12():
    im = load_base("z25-12-base.jpg")
    draw = ImageDraw.Draw(im)
    cover(draw, (0, 0, 1600, 80), CREAM)
    pill(draw, 120, 15, 1360, 50, "Не сцена ради сцены — а понятная, добрая выразительность", TEAL_D, fsize=22)
    caption_bar(im, "Настроение · мягкий голос · лицо · 1 жест · короткая игра")
    save(im, "z25-12-finale.jpg")


def main():
    for fn in [
        make_01, make_02, make_03, make_04, make_05, make_06,
        make_07, make_08, make_09, make_10, make_11, make_12,
    ]:
        fn()
    print("All 12 labeled images ready")


if __name__ == "__main__":
    main()
