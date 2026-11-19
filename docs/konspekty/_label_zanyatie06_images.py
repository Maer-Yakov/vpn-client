#!/usr/bin/env python3
"""Overlay correct Russian labels on lesson-6 base illustrations."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SRC = Path("/opt/cursor/artifacts/assets")
OUT = Path(__file__).resolve().parent / "zanyatie-06-assets"
ART = Path("/opt/cursor/artifacts/zanyatie-06-assets")

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
    path = SRC / name
    im = Image.open(path).convert("RGBA")
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
    """Bottom caption bar with Russian text."""
    draw = ImageDraw.Draw(im)
    w, h = im.size
    bar_h = 110
    rounded_rect(draw, (40, h - bar_h - 30, w - 40, h - 30), fill, radius=24)
    f = font(42, bold=True)
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
    im = load_base("z06-01-base.jpg")
    draw = ImageDraw.Draw(im)
    # cover any leftover badges and redraw Russian ones
    cover(draw, (0, 720, 1600, 900), CREAM)
    labels = [("ухо", TEAL), ("сердце", CORAL), ("руки", LEAF), ("погремушка", GOLD)]
    for i, (t, c) in enumerate(labels):
        pill(draw, 80 + i * 380, 760, 340, 70, t, c, fsize=30)
    save(im, "z06-01-title.jpg")


def make_02():
    im = load_base("z06-02-base.jpg")
    draw = ImageDraw.Draw(im)
    # top title bars over doors
    cover(draw, (80, 40, 720, 160), CREAM)
    cover(draw, (880, 40, 1520, 160), CREAM)
    # also cover mid door text areas if any
    cover(draw, (200, 280, 600, 380), (235, 210, 200, 255))
    cover(draw, (1000, 280, 1400, 380), (200, 230, 235, 255))
    pill(draw, 160, 60, 480, 80, "СТРОЙ ✕", RED, fsize=36)
    pill(draw, 960, 60, 480, 80, "ТЁПЛЫЙ ДИАЛОГ ✓", TEAL, fsize=32)
    pill(draw, 220, 300, 360, 60, "закрыто", RED, fsize=28)
    pill(draw, 1040, 300, 360, 60, "открыто", TEAL, fsize=28)
    caption_bar(im, "Выбираем тёплый диалог, а не строй")
    save(im, "z06-02-doors.jpg")


def make_03():
    # Create clean ritual form programmatically for perfect Russian
    im = Image.new("RGBA", (1200, 900), (247, 250, 252, 255))
    draw = ImageDraw.Draw(im)
    # paper
    rounded_rect(draw, (120, 60, 1080, 840), (255, 252, 245, 255), radius=20)
    # clip
    rounded_rect(draw, (480, 30, 720, 90), TEAL_D, radius=12)
    draw.text((520, 45), "✓", font=font(36, True), fill=WHITE)
    # title
    draw.text((220, 130), "Мягкий ритуал 2–3 минуты", font=font(40, True), fill=TEAL_D)
    draw.line((220, 190, 980, 190), fill=TEAL, width=3)
    rows = [
        "☐   покачивание",
        "☐   потешка",
        "☐   погремушка «спит»",
        "☐   пауза / взгляд",
        "☐   стоп по состоянию",
    ]
    for i, t in enumerate(rows):
        y = 240 + i * 100
        rounded_rect(draw, (200, y, 1000, y + 80), SOFT, radius=16)
        draw.text((240, y + 20), t, font=font(32, True), fill=INK)
    save(im, "z06-03-ritual.jpg")


def make_04():
    im = load_base("z06-04-base.jpg")
    draw = ImageDraw.Draw(im)
    # cover bubble text areas with Russian pills near bubbles
    # place labels around the map
    labels = [
        (80, 80, "Слух", TEAL),
        (1180, 80, "Интонации", GOLD),
        (80, 400, "Жанры", LEAF),
        (1180, 400, "Вместе", CORAL),
        (200, 720, "Контакт", TEAL),
        (1000, 720, "Практика", GOLD),
    ]
    # soft cream strip at bottom for clarity
    cover(draw, (0, 0, 1600, 70), CREAM)
    pill(draw, 400, 10, 800, 50, "Карта темы · 0–1,5 лет", TEAL_D, fsize=28)
    for x, y, t, c in labels:
        # cover possible garbled text under/near
        cover(draw, (x - 10, y - 10, x + 280, y + 70), CREAM)
        pill(draw, x, y, 260, 55, t, c, fsize=26)
    save(im, "z06-04-mindmap.jpg")


def make_05():
    im = load_base("z06-05-base.jpg")
    draw = ImageDraw.Draw(im)
    cover(draw, (0, 0, 1600, 80), CREAM)
    pill(draw, 40, 20, 220, 50, "голос", TEAL, fsize=26)
    pill(draw, 300, 20, 260, 50, "тепло рук", CORAL, fsize=26)
    pill(draw, 600, 20, 220, 50, "отклик", LEAF, fsize=26)
    caption_bar(im, "Звук входит вместе с теплом рук")
    save(im, "z06-05-voice-waves.jpg")


def make_06():
    im = load_base("z06-06-base.jpg")
    draw = ImageDraw.Draw(im)
    # bottom labels
    cover(draw, (0, 720, 1600, 900), CREAM)
    pill(draw, 80, 760, 420, 70, "спокойно ✓", LEAF, fsize=32)
    pill(draw, 590, 760, 420, 70, "игриво ✓", GOLD, fsize=32)
    pill(draw, 1100, 760, 420, 70, "резко ✕", RED, fsize=32)
    save(im, "z06-06-intonations.jpg")


def make_07():
    im = load_base("z06-07-base.jpg")
    draw = ImageDraw.Draw(im)
    # top bars on three cards
    cover(draw, (80, 40, 500, 130), CREAM)
    cover(draw, (560, 40, 1040, 130), CREAM)
    cover(draw, (1100, 40, 1520, 130), CREAM)
    pill(draw, 100, 55, 360, 60, "Колыбельная", TEAL, fsize=28)
    pill(draw, 600, 55, 400, 60, "Потешка", GOLD, fsize=28)
    pill(draw, 1140, 55, 340, 60, "Пестушка", CORAL, fsize=28)
    caption_bar(im, "Главный «учебник» ритма для младенца")
    save(im, "z06-07-genres.jpg")


def make_08():
    im = load_base("z06-08-base.jpg")
    draw = ImageDraw.Draw(im)
    pill(draw, 80, 40, 420, 60, "вместе на коленях ✓", TEAL, fsize=26)
    pill(draw, 1000, 40, 520, 60, "строй / танец по правилам ✕", RED, fsize=24)
    caption_bar(im, "Взрослое тело — безопасный метроном")
    save(im, "z06-08-knees.jpg")


def make_09():
    im = load_base("z06-09-base.jpg")
    caption_bar(im, "Взгляд + голос + касание + пауза")
    save(im, "z06-09-contact.jpg")


def make_10():
    im = load_base("z06-10-base.jpg", size=(1200, 900))
    draw = ImageDraw.Draw(im)
    # cover English Can/Cannot if present
    cover(draw, (0, 0, 1200, 90), CREAM)
    pill(draw, 80, 20, 280, 55, "МОЖНО ✓", LEAF, fsize=28)
    pill(draw, 840, 20, 280, 55, "НЕЛЬЗЯ ✕", RED, fsize=28)
    # bottom bar
    w, h = im.size
    rounded_rect(draw, (40, h - 120, w - 40, h - 30), TEAL_D, radius=24)
    f = font(36, True)
    text = "Светофор мягкости"
    bbox = f.getbbox(text)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((w - tw) / 2, h - 120 + (90 - th) / 2), text, font=f, fill=WHITE)
    save(im, "z06-10-traffic.jpg")


def make_11():
    im = load_base("z06-11-base.jpg")
    draw = ImageDraw.Draw(im)
    cover(draw, (0, 0, 1600, 75), CREAM)
    pill(draw, 350, 12, 900, 50, "Пять мягких блоков практики", TEAL_D, fsize=28)
    # place Russian labels near stations
    labels = [
        (40, 160, "руки"),
        (1280, 160, "ладушки"),
        (40, 520, "качание"),
        (1280, 520, "погремушка"),
        (640, 760, "контрасты"),
    ]
    for x, y, t in labels:
        cover(draw, (x - 5, y - 5, x + 250, y + 55), CREAM)
        pill(draw, x, y, 240, 50, t, TEAL, fsize=24)
    save(im, "z06-11-stations.jpg")


def make_12():
    im = load_base("z06-12-base.jpg")
    draw = ImageDraw.Draw(im)
    cover(draw, (0, 0, 1600, 90), CREAM)
    pill(draw, 120, 20, 420, 55, "правильно ✓", LEAF, fsize=28)
    pill(draw, 980, 20, 420, 55, "нельзя ✕", RED, fsize=28)
    caption_bar(im, "Покачать — не значит растрясти")
    save(im, "z06-12-arms.jpg")


def make_13():
    im = load_base("z06-13-base.jpg")
    draw = ImageDraw.Draw(im)
    cover(draw, (0, 0, 1600, 80), CREAM)
    pill(draw, 500, 15, 600, 50, "Ладушки · голос теплее хлопка", TEAL, fsize=26)
    caption_bar(im, "потешка → жест → повтор → взгляд-пауза")
    save(im, "z06-13-ladushki.jpg")


def make_14():
    im = load_base("z06-14-base.jpg")
    draw = ImageDraw.Draw(im)
    cover(draw, (0, 0, 1600, 80), CREAM)
    pill(draw, 450, 15, 700, 50, "Медленный пульс · маятник", TEAL, fsize=28)
    caption_bar(im, "спокойно → короткий контраст → снова спокойно")
    save(im, "z06-14-pendulum.jpg")


def make_15():
    im = load_base("z06-15-base.jpg")
    draw = ImageDraw.Draw(im)
    cover(draw, (0, 0, 1600, 90), CREAM)
    pill(draw, 120, 20, 400, 55, "звенит ✓", LEAF, fsize=30)
    pill(draw, 1000, 20, 400, 55, "спит ✓", TEAL, fsize=30)
    caption_bar(im, "Учить тишине так же, как звуку")
    save(im, "z06-15-rattle.jpg")


def make_16():
    im = load_base("z06-16-base.jpg")
    draw = ImageDraw.Draw(im)
    cover(draw, (0, 0, 1600, 80), CREAM)
    pill(draw, 400, 15, 800, 50, "Мини-тренинг · 60–70 секунд", TEAL, fsize=28)
    caption_bar(im, "начало → повтор → мягкий стоп")
    save(im, "z06-16-training.jpg")


def make_17():
    # Clean checklist with perfect Russian — draw fresh
    im = Image.new("RGBA", (1600, 900), (247, 250, 252, 255))
    draw = ImageDraw.Draw(im)
    # clipboard body
    rounded_rect(draw, (280, 40, 1320, 860), (255, 252, 245, 255), radius=24)
    rounded_rect(draw, (620, 20, 980, 80), TEAL_D, radius=14)
    draw.text((700, 32), "ЧЕК-ЛИСТ", font=font(28, True), fill=WHITE)
    draw.text((420, 110), "Работа с возрастом 0–1,5 лет", font=font(36, True), fill=TEAL_D)
    # heart + hand icons as circles with short Russian
    draw.ellipse((640, 175, 780, 315), fill=CORAL)
    draw.ellipse((820, 175, 960, 315), fill=LEAF)
    draw.text((670, 225), "сердце", font=font(20, True), fill=WHITE)
    draw.text((855, 225), "ладонь", font=font(20, True), fill=WHITE)
    items = [
        "Понимаю: сенсомоторика и контакт, не номер",
        "Умею читать реакцию на интонацию",
        "Различаю колыбельную, потешку, пестушку",
        "Двигаюсь вместе, не тащу",
        "Держу взгляд, голос, касание",
        "Могу провести ладушки / покачивание мягко",
        "Учу погремушку со «сном» и тишиной",
        "Останавливаюсь при переутомлении",
    ]
    for i, t in enumerate(items):
        y = 300 + i * 65
        rounded_rect(draw, (360, y, 1240, y + 55), SOFT if i % 2 == 0 else (255, 255, 255, 255), radius=12)
        draw.text((390, y + 12), f"☐  {t}", font=font(22, True), fill=INK)
    save(im, "z06-17-checklist.jpg")


def make_18():
    im = load_base("z06-18-base.jpg")
    draw = ImageDraw.Draw(im)
    cover(draw, (0, 0, 1600, 80), CREAM)
    pill(draw, 350, 15, 900, 50, "Ритм начинается с тёплого взрослого", TEAL_D, fsize=28)
    caption_bar(im, "Мягкий голос · короткая форма · право на паузу")
    save(im, "z06-18-finale.jpg")


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
