#!/usr/bin/env python3
"""Overlay correct Russian labels on song-fairy-tale illustrations."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SRC = Path("/opt/cursor/artifacts/assets")
OUT = Path(__file__).resolve().parent / "zanyatie-23-assets"
ART = Path("/opt/cursor/artifacts/zanyatie-23-assets")

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
    im = load_base("z23-01-base.jpg")
    draw = ImageDraw.Draw(im)
    cover(draw, (0, 720, 1600, 900), CREAM)
    for i, (t, c) in enumerate([("пение", TEAL), ("сюжет", GOLD), ("образ", CORAL), ("кукла", LEAF)]):
        pill(draw, 80 + i * 380, 760, 340, 70, t, c, fsize=28)
    save(im, "z23-01-title.jpg")


def make_02():
    im = load_base("z23-02-base.jpg")
    draw = ImageDraw.Draw(im)
    # cover possible AI English card labels
    cover(draw, (0, 0, 1600, 120), CREAM)
    cover(draw, (0, 720, 1600, 900), CREAM)
    labels = [
        (60, "обычная песня", TEAL),
        (430, "игра-песня", GOLD),
        (800, "театр", CORAL),
        (1170, "песня-сказка ✓", LEAF),
    ]
    for x, t, c in labels:
        pill(draw, x, 30, 340, 60, t, c, fsize=20)
    caption_bar(im, "Музыка и голос главные; кукла — опора внимания")
    save(im, "z23-02-forms.jpg")


def make_03():
    im = Image.new("RGBA", (1200, 900), (247, 250, 252, 255))
    draw = ImageDraw.Draw(im)
    rounded_rect(draw, (120, 60, 1080, 840), (255, 252, 245, 255), radius=20)
    rounded_rect(draw, (260, 30, 940, 90), TEAL_D, radius=12)
    draw.text((320, 45), "Мини-фрагмент 60–90 секунд", font=font(28, True), fill=WHITE)
    draw.text((180, 130), "Песня-сказка · короткий показ", font=font(28, True), fill=TEAL_D)
    draw.line((180, 185, 1020, 185), fill=TEAL, width=3)
    rows = [
        "☐   появление куклы",
        "☐   1–2 фразы",
        "☐   жест / действие",
        "☐   короткий прогон",
        "☐   мягкий стоп",
    ]
    for i, t in enumerate(rows):
        y = 230 + i * 100
        rounded_rect(draw, (180, y, 1020, y + 80), SOFT, radius=16)
        draw.text((220, y + 22), t, font=font(26, True), fill=INK)
    save(im, "z23-03-goal.jpg")


def make_04():
    im = load_base("z23-04-base.jpg")
    draw = ImageDraw.Draw(im)
    cover(draw, (0, 0, 1600, 75), CREAM)
    pill(draw, 280, 12, 1040, 50, "Шесть видов песен-сказок", TEAL_D, fsize=28)
    labels = ["1 герой", "диалог", "цепочка", "событие", "хоровод", "кукла"]
    for i, t in enumerate(labels):
        pill(draw, 40 + i * 260, 780, 240, 55, t, TEAL if i % 2 == 0 else GOLD, fsize=20)
    save(im, "z23-04-types.jpg")


def make_05():
    im = load_base("z23-05-base.jpg")
    draw = ImageDraw.Draw(im)
    cover(draw, (0, 0, 1600, 90), CREAM)
    pill(draw, 260, 18, 1080, 55, "Мост: пение — речь — игра", TEAL_D, fsize=28)
    for i, (t, c) in enumerate([("музыка", TEAL), ("речь", GOLD), ("общение", LEAF)]):
        pill(draw, 120 + i * 480, 780, 420, 55, t, c, fsize=24)
    save(im, "z23-05-bridge.jpg")


def make_06():
    im = load_base("z23-06-base.jpg")
    draw = ImageDraw.Draw(im)
    cover(draw, (0, 0, 1600, 75), CREAM)
    pill(draw, 280, 12, 1040, 50, "Этапы разучивания", TEAL_D, fsize=28)
    stages = ["интерес", "слушание", "образы", "фразы", "роль", "действие", "вместе", "стоп"]
    for i, s in enumerate(stages):
        pill(draw, 15 + i * 198, 780, 188, 50, s, TEAL if i % 2 == 0 else LEAF, fsize=15)
    save(im, "z23-06-steps.jpg")


def make_07():
    im = load_base("z23-07-base.jpg")
    draw = ImageDraw.Draw(im)
    cover(draw, (0, 0, 1600, 75), CREAM)
    pill(draw, 260, 12, 1080, 50, "Творческие упражнения", TEAL_D, fsize=28)
    labels = ["голос", "жест", "эхо", "угадай", "продолжи", "тише", "очередь"]
    for i, t in enumerate(labels):
        pill(draw, 20 + i * 225, 780, 210, 55, t, TEAL if i % 2 == 0 else GOLD, fsize=16)
    save(im, "z23-07-exercises.jpg")


def make_08():
    im = load_base("z23-08-base.jpg")
    draw = ImageDraw.Draw(im)
    cover(draw, (0, 0, 1600, 80), CREAM)
    pill(draw, 300, 15, 1000, 50, "Карточка анализа образа", TEAL_D, fsize=28)
    caption_bar(im, "Контраст — характером и жестом, не силой голоса")
    save(im, "z23-08-analysis.jpg")


def make_09():
    im = load_base("z23-09-base.jpg")
    draw = ImageDraw.Draw(im)
    cover(draw, (0, 0, 1600, 80), CREAM)
    pill(draw, 280, 15, 1040, 50, "Чемоданчик сказки: мало реквизита", TEAL_D, fsize=26)
    pill(draw, 80, 780, 520, 55, "беру ✓", LEAF, fsize=24)
    pill(draw, 1000, 780, 520, 55, "не беру ✕", RED, fsize=24)
    save(im, "z23-09-props.jpg")


def make_10():
    im = load_base("z23-10-base.jpg")
    draw = ImageDraw.Draw(im)
    cover(draw, (0, 0, 1600, 80), CREAM)
    pill(draw, 260, 15, 1080, 50, "Кукла на руку: техника показа", TEAL_D, fsize=26)
    caption_bar(im, "На уровне лица · редкие движения · мягкий голос · убрать")
    save(im, "z23-10-puppet.jpg")


def make_11():
    im = load_base("z23-11-base.jpg")
    draw = ImageDraw.Draw(im)
    cover(draw, (0, 0, 1600, 80), CREAM)
    pill(draw, 280, 15, 1040, 50, "Мини-лаборатория · 60–90 сек", TEAL, fsize=26)
    caption_bar(im, "кукла → фразы → жест → прогон → стоп")
    save(im, "z23-11-lab.jpg")


def make_12():
    im = load_base("z23-12-base.jpg")
    draw = ImageDraw.Draw(im)
    cover(draw, (0, 0, 1600, 80), CREAM)
    pill(draw, 160, 15, 1280, 50, "Сказка начинается с мягкого пения — не с декораций", TEAL_D, fsize=24)
    caption_bar(im, "Мягкое пение · ясный образ · 1 кукла/жест · короткий сюжет · пауза")
    save(im, "z23-12-finale.jpg")


def main():
    for fn in [
        make_01, make_02, make_03, make_04, make_05, make_06,
        make_07, make_08, make_09, make_10, make_11, make_12,
    ]:
        fn()
    print("All 12 labeled images ready")


if __name__ == "__main__":
    main()
