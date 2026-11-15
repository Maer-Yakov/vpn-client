#!/usr/bin/env python3
"""Overlay correct Russian labels on singing-with-instruments illustrations."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SRC = Path("/opt/cursor/artifacts/assets")
OUT = Path(__file__).resolve().parent / "zanyatie-22-assets"
ART = Path("/opt/cursor/artifacts/zanyatie-22-assets")

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
    rgb.save(ART / name, quality=92)
    print("OK", name)


def make_01():
    im = load_base("z22-01-base.jpg")
    draw = ImageDraw.Draw(im)
    cover(draw, (0, 720, 1600, 900), CREAM)
    for i, (t, c) in enumerate([("голос", TEAL), ("ритм", GOLD), ("сигнал", CORAL), ("стоп", LEAF)]):
        pill(draw, 80 + i * 380, 760, 340, 70, t, c, fsize=28)
    save(im, "z22-01-title.jpg")


def make_02():
    im = load_base("z22-02-base.jpg")
    draw = ImageDraw.Draw(im)
    cover(draw, (60, 30, 720, 140), CREAM)
    cover(draw, (880, 30, 1540, 140), CREAM)
    pill(draw, 80, 50, 560, 70, "ШУМ БЕЗ ПЕСНИ ✕", RED, fsize=26)
    pill(draw, 900, 50, 560, 70, "ПЕСНЯ + МЯГКО ✓", TEAL, fsize=26)
    caption_bar(im, "Если не слышно песни — тише и меньше инструментов")
    save(im, "z22-02-doors.jpg")


def make_03():
    im = Image.new("RGBA", (1200, 900), (247, 250, 252, 255))
    draw = ImageDraw.Draw(im)
    rounded_rect(draw, (120, 60, 1080, 840), (255, 252, 245, 255), radius=20)
    rounded_rect(draw, (300, 30, 900, 90), TEAL_D, radius=12)
    draw.text((210, 120), "Мини-фрагмент 90–120 секунд", font=font(30, True), fill=TEAL_D)
    draw.line((220, 180, 980, 180), fill=TEAL, width=3)
    rows = [
        "☐   возраст и цель",
        "☐   сигнал 15–20 сек",
        "☐   показ песни",
        "☐   песня + 1 вид сопровождения",
        "☐   мягкий стоп",
    ]
    for i, t in enumerate(rows):
        y = 230 + i * 100
        rounded_rect(draw, (180, y, 1020, y + 80), SOFT, radius=16)
        draw.text((220, y + 22), t, font=font(26, True), fill=INK)
    save(im, "z22-03-goal.jpg")


def make_04():
    im = load_base("z22-04-base.jpg")
    draw = ImageDraw.Draw(im)
    cover(draw, (0, 0, 1600, 75), CREAM)
    pill(draw, 280, 12, 1040, 50, "Инструменты для пения дошкольников", TEAL_D, fsize=26)
    for i, t in enumerate(["ударные", "звенящие", "мелодические"]):
        pill(draw, 120 + i * 480, 780, 420, 55, t, TEAL if i % 2 == 0 else LEAF, fsize=22)
    save(im, "z22-04-instruments.jpg")


def make_05():
    im = load_base("z22-05-base.jpg")
    draw = ImageDraw.Draw(im)
    cover(draw, (0, 0, 1600, 75), CREAM)
    pill(draw, 280, 12, 1040, 50, "Шесть видов сопровождения", TEAL_D, fsize=28)
    labels = ["пульс", "доля", "припев", "ответ", "остинато", "образ"]
    for i, t in enumerate(labels):
        pill(draw, 40 + i * 260, 780, 240, 55, t, TEAL if i % 2 == 0 else GOLD, fsize=20)
    save(im, "z22-05-types.jpg")


def make_06():
    im = load_base("z22-06-base.jpg")
    draw = ImageDraw.Draw(im)
    cover(draw, (0, 0, 1600, 75), CREAM)
    pill(draw, 280, 12, 1040, 50, "Организация ансамбля", TEAL_D, fsize=28)
    stages = ["место", "показ", "сигнал", "проба", "песня", "инструмент", "стоп"]
    for i, s in enumerate(stages):
        pill(draw, 20 + i * 225, 780, 210, 50, s, TEAL if i % 2 == 0 else LEAF, fsize=16)
    save(im, "z22-06-org.jpg")


def make_07():
    im = load_base("z22-07-base.jpg", size=(1200, 900))
    draw = ImageDraw.Draw(im)
    cover(draw, (0, 0, 1200, 90), CREAM)
    pill(draw, 40, 18, 240, 55, "мягко ✓", LEAF, fsize=26)
    pill(draw, 480, 18, 240, 55, "пауза", GOLD, fsize=26)
    pill(draw, 920, 18, 240, 55, "громче ✕", RED, fsize=24)
    caption_bar(im, "Светофор: мягко / пауза / громче голоса ✕")
    save(im, "z22-07-traffic.jpg")


def make_08():
    im = load_base("z22-08-base.jpg")
    draw = ImageDraw.Draw(im)
    cover(draw, (0, 0, 1600, 75), CREAM)
    pill(draw, 300, 12, 1000, 50, "Разминка к ансамблю", TEAL_D, fsize=28)
    labels = ["эхо", "доля", "сигнал", "тише", "голос+удар"]
    for i, t in enumerate(labels):
        pill(draw, 40 + i * 310, 780, 290, 55, t, TEAL if i % 2 == 0 else GOLD, fsize=18)
    save(im, "z22-08-warmup.jpg")


def make_09():
    im = load_base("z22-09-base.jpg")
    draw = ImageDraw.Draw(im)
    cover(draw, (0, 0, 1600, 80), CREAM)
    pill(draw, 280, 15, 1040, 50, "Алгоритм подбора сопровождения", TEAL_D, fsize=26)
    caption_bar(im, "возраст → знакомая песня → 1 вид → инструмент → сигнал → стоп")
    save(im, "z22-09-select.jpg")


def make_10():
    im = load_base("z22-10-base.jpg")
    draw = ImageDraw.Draw(im)
    cover(draw, (0, 0, 1600, 90), CREAM)
    pill(draw, 260, 18, 1080, 55, "Репертуар: песня → сопровождение", TEAL_D, fsize=26)
    for i, (t, c) in enumerate([("3–5 лет", TEAL), ("4–5 лет", GOLD), ("5–7 лет", LEAF)]):
        pill(draw, 120 + i * 480, 780, 420, 55, t, c, fsize=22)
    save(im, "z22-10-repertoire.jpg")


def make_11():
    im = load_base("z22-11-base.jpg")
    draw = ImageDraw.Draw(im)
    cover(draw, (0, 0, 1600, 80), CREAM)
    pill(draw, 300, 15, 1000, 50, "Микропреподавание · 90–120 сек", TEAL, fsize=26)
    caption_bar(im, "сигнал → песня → сопровождение → стоп")
    save(im, "z22-11-training.jpg")


def make_12():
    im = load_base("z22-12-base.jpg")
    draw = ImageDraw.Draw(im)
    cover(draw, (0, 0, 1600, 80), CREAM)
    pill(draw, 200, 15, 1200, 50, "Первым всегда остаётся мягкий голос", TEAL_D, fsize=26)
    caption_bar(im, "Знакомая песня · 1 вид · сигнал · мало инструментов · стоп")
    save(im, "z22-12-finale.jpg")


def main():
    for fn in [
        make_01, make_02, make_03, make_04, make_05, make_06,
        make_07, make_08, make_09, make_10, make_11, make_12,
    ]:
        fn()
    print("All 12 labeled images ready")


if __name__ == "__main__":
    main()
