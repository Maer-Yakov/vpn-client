#!/usr/bin/env python3
"""Overlay correct Russian labels on lesson-8 base illustrations."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SRC = Path("/opt/cursor/artifacts/assets")
OUT = Path(__file__).resolve().parent / "zanyatie-08-assets"
ART = Path("/opt/cursor/artifacts/zanyatie-08-assets")

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
    f = font(40, bold=True)
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
    im = load_base("z08-01-base.jpg")
    draw = ImageDraw.Draw(im)
    cover(draw, (0, 720, 1600, 900), CREAM)
    for i, (t, c) in enumerate([("нота", TEAL), ("ухо", GOLD), ("голос", CORAL), ("платочек", LEAF)]):
        pill(draw, 80 + i * 380, 760, 340, 70, t, c, fsize=30)
    save(im, "z08-01-title.jpg")


def make_02():
    im = load_base("z08-02-base.jpg")
    draw = ImageDraw.Draw(im)
    cover(draw, (60, 30, 720, 140), CREAM)
    cover(draw, (880, 30, 1540, 140), CREAM)
    pill(draw, 100, 50, 520, 70, "КОНЦЕРТНЫЙ НОМЕР ✕", RED, fsize=28)
    pill(draw, 920, 50, 560, 70, "МЯГКОЕ ПЕНИЕ ВМЕСТЕ ✓", TEAL, fsize=26)
    caption_bar(im, "Выбираем желание подхватить, а не номер")
    save(im, "z08-02-doors.jpg")


def make_03():
    im = Image.new("RGBA", (1200, 900), (247, 250, 252, 255))
    draw = ImageDraw.Draw(im)
    rounded_rect(draw, (120, 60, 1080, 840), (255, 252, 245, 255), radius=20)
    rounded_rect(draw, (480, 30, 720, 90), TEAL_D, radius=12)
    draw.text((220, 130), "Мини-пение 90 секунд", font=font(40, True), fill=TEAL_D)
    draw.line((220, 190, 980, 190), fill=TEAL, width=3)
    rows = [
        "☐   упражнение 20–30 сек",
        "☐   показ 1 фразы песни",
        "☐   повтор детей",
        "☐   можно / нельзя",
        "☐   мягкий стоп",
    ]
    for i, t in enumerate(rows):
        y = 240 + i * 100
        rounded_rect(draw, (200, y, 1000, y + 80), SOFT, radius=16)
        draw.text((240, y + 20), t, font=font(30, True), fill=INK)
    save(im, "z08-03-ritual.jpg")


def make_04():
    im = load_base("z08-04-base.jpg")
    draw = ImageDraw.Draw(im)
    cover(draw, (0, 0, 1600, 70), CREAM)
    pill(draw, 400, 10, 800, 50, "Карта темы · пение 3–4 лет", TEAL_D, fsize=28)
    labels = [
        (60, 120, "Значение", TEAL),
        (1220, 120, "Возраст", GOLD),
        (60, 400, "Задачи", LEAF),
        (1220, 400, "Этапы", CORAL),
        (180, 720, "Упражнения", TEAL),
        (1040, 720, "Репертуар", GOLD),
    ]
    for x, y, t, c in labels:
        cover(draw, (x - 8, y - 8, x + 280, y + 60), CREAM)
        pill(draw, x, y, 260, 52, t, c, fsize=24)
    save(im, "z08-04-mindmap.jpg")


def make_05():
    im = load_base("z08-05-base.jpg")
    draw = ImageDraw.Draw(im)
    cover(draw, (0, 0, 1600, 75), CREAM)
    pill(draw, 350, 12, 900, 50, "Пение развивает шесть сфер", TEAL_D, fsize=28)
    for i, t in enumerate(["слух", "речь", "дыхание", "эмоции", "общение", "память"]):
        pill(draw, 40 + i * 260, 780, 240, 55, t, TEAL if i % 2 == 0 else LEAF, fsize=22)
    save(im, "z08-05-spheres.jpg")


def make_06():
    im = load_base("z08-06-base.jpg")
    draw = ImageDraw.Draw(im)
    cover(draw, (0, 0, 1600, 90), CREAM)
    pill(draw, 80, 20, 520, 55, "узкий диапазон ✓", TEAL, fsize=28)
    pill(draw, 980, 20, 520, 55, "крик ✕", RED, fsize=28)
    caption_bar(im, "3–4 года: короткая фраза, без широких скачков")
    save(im, "z08-06-range.jpg")


def make_07():
    im = load_base("z08-07-base.jpg", size=(1200, 900))
    draw = ImageDraw.Draw(im)
    cover(draw, (0, 0, 1200, 90), CREAM)
    pill(draw, 60, 20, 280, 55, "МОЖНО ✓", LEAF, fsize=28)
    pill(draw, 860, 20, 280, 55, "НЕЛЬЗЯ ✕", RED, fsize=28)
    w, h = im.size
    rounded_rect(draw, (40, h - 120, w - 40, h - 30), TEAL_D, radius=24)
    f = font(36, True)
    text = "Светофор голоса"
    bbox = f.getbbox(text)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((w - tw) / 2, h - 120 + (90 - th) / 2), text, font=f, fill=WHITE)
    save(im, "z08-07-traffic.jpg")


def make_08():
    im = load_base("z08-08-base.jpg")
    draw = ImageDraw.Draw(im)
    cover(draw, (0, 0, 1600, 75), CREAM)
    pill(draw, 350, 12, 900, 50, "Лестница певческих задач", TEAL_D, fsize=28)
    caption_bar(im, "желание → мягкий звук → фраза → репертуар → пауза")
    save(im, "z08-08-stairs.jpg")


def make_09():
    im = load_base("z08-09-base.jpg")
    draw = ImageDraw.Draw(im)
    cover(draw, (0, 0, 1600, 80), CREAM)
    pill(draw, 350, 15, 900, 50, "Главный приём — выразительный показ", TEAL, fsize=26)
    caption_bar(im, "педагог ведёт — дети подхватывают")
    save(im, "z08-09-show.jpg")


def make_10():
    im = load_base("z08-10-base.jpg")
    draw = ImageDraw.Draw(im)
    cover(draw, (0, 0, 1600, 75), CREAM)
    pill(draw, 300, 12, 1000, 50, "Этапы разучивания песни", TEAL_D, fsize=28)
    stages = ["интерес", "показ", "смысл", "фразы", "вместе", "игра", "стоп"]
    for i, t in enumerate(stages):
        pill(draw, 30 + i * 225, 780, 210, 50, t, TEAL if i % 2 == 0 else LEAF, fsize=18)
    save(im, "z08-10-stages.jpg")


def make_11():
    im = load_base("z08-11-base.jpg")
    draw = ImageDraw.Draw(im)
    cover(draw, (0, 0, 1600, 90), CREAM)
    pill(draw, 80, 20, 520, 55, "разминка голоса", TEAL, fsize=28)
    pill(draw, 980, 20, 520, 55, "полка песен", GOLD, fsize=28)
    caption_bar(im, "Два практических блока занятия")
    save(im, "z08-11-stations.jpg")


def make_12():
    im = load_base("z08-12-base.jpg")
    draw = ImageDraw.Draw(im)
    cover(draw, (0, 0, 1600, 90), CREAM)
    pill(draw, 80, 20, 480, 55, "мягкое пение ✓", LEAF, fsize=28)
    pill(draw, 1040, 20, 480, 55, "форсирование ✕", RED, fsize=28)
    caption_bar(im, "Первый инструмент педагога — собственный голос")
    save(im, "z08-12-soft.jpg")


def make_13():
    im = load_base("z08-13-base.jpg")
    draw = ImageDraw.Draw(im)
    cover(draw, (0, 0, 1600, 80), CREAM)
    pill(draw, 400, 15, 800, 50, "Модель: интерес → фраза → жест", TEAL, fsize=26)
    caption_bar(im, "Разучивание короткой песни младшей группы")
    save(im, "z08-13-rooster.jpg")


def make_14():
    im = load_base("z08-14-base.jpg")
    draw = ImageDraw.Draw(im)
    cover(draw, (0, 0, 1600, 75), CREAM)
    pill(draw, 350, 12, 900, 50, "Банк упражнений 20–40 секунд", TEAL_D, fsize=28)
    labels = ["дыхание", "атака", "высота", "дикция", "динамика", "конец"]
    for i, t in enumerate(labels):
        pill(draw, 40 + i * 260, 780, 240, 55, t, TEAL if i % 2 == 0 else GOLD, fsize=22)
    save(im, "z08-14-exercises.jpg")


def make_15():
    im = load_base("z08-15-base.jpg")
    draw = ImageDraw.Draw(im)
    cover(draw, (0, 0, 1600, 90), CREAM)
    pill(draw, 80, 20, 400, 55, "беру ✓", LEAF, fsize=30)
    pill(draw, 1080, 20, 400, 55, "не беру ✕", RED, fsize=30)
    caption_bar(im, "Репертуар — педагогическое решение")
    save(im, "z08-15-repertoire.jpg")


def make_16():
    im = load_base("z08-16-base.jpg")
    draw = ImageDraw.Draw(im)
    cover(draw, (0, 0, 1600, 80), CREAM)
    pill(draw, 350, 15, 900, 50, "Мини-тренинг · 90–100 секунд", TEAL, fsize=28)
    caption_bar(im, "упражнение → фраза → стоп")
    save(im, "z08-16-training.jpg")


def make_17():
    im = Image.new("RGBA", (1600, 900), (247, 250, 252, 255))
    draw = ImageDraw.Draw(im)
    rounded_rect(draw, (280, 40, 1320, 860), (255, 252, 245, 255), radius=24)
    rounded_rect(draw, (620, 20, 980, 80), TEAL_D, radius=14)
    draw.text((700, 32), "ЧЕК-ЛИСТ", font=font(28, True), fill=WHITE)
    draw.text((420, 110), "Пение в младшей группе (3–4 года)", font=font(32, True), fill=TEAL_D)
    draw.ellipse((700, 170, 800, 270), fill=CORAL)
    draw.ellipse((820, 170, 920, 270), fill=LEAF)
    draw.text((720, 205), "нота", font=font(18, True), fill=WHITE)
    draw.text((835, 205), "тише", font=font(18, True), fill=WHITE)
    items = [
        "Понимаю значение пения для 3–4 лет",
        "Знаю особенности голоса и риск крика",
        "Могу назвать задачи обучения пению",
        "Владею показом и совместным пением",
        "Веду этапы: интерес → показ → фразы → стоп",
        "Есть банк коротких упражнений",
        "Умею отобрать посильную песню",
        "Берегу голос: паузы обязательны",
    ]
    for i, t in enumerate(items):
        y = 300 + i * 65
        rounded_rect(draw, (360, y, 1240, y + 55), SOFT if i % 2 == 0 else (255, 255, 255, 255), radius=12)
        draw.text((390, y + 12), f"☐  {t}", font=font(22, True), fill=INK)
    save(im, "z08-17-checklist.jpg")


def make_18():
    im = load_base("z08-18-base.jpg")
    draw = ImageDraw.Draw(im)
    cover(draw, (0, 0, 1600, 80), CREAM)
    pill(draw, 280, 15, 1040, 50, "Пение начинается с желания подхватить", TEAL_D, fsize=26)
    caption_bar(im, "Мягкий голос · короткая песня · этапы без спешки")
    save(im, "z08-18-finale.jpg")


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
    make_13()
    make_14()
    make_15()
    make_16()
    make_17()
    make_18()
    print("All 18 labeled images ready")


if __name__ == "__main__":
    main()
