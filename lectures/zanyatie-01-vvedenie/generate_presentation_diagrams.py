#!/usr/bin/env python3
"""Clean educational diagrams for the 14-slide student presentation."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from font_paths import resolve_fonts

OUT = Path(__file__).resolve().parent / "assets"
OUT.mkdir(parents=True, exist_ok=True)
FONTS = resolve_fonts()

# Cool academic palette (avoid cream+terracotta / purple clichés)
BG = (248, 250, 252)
INK = (30, 41, 59)
MUTED = (100, 116, 139)
TEAL = (15, 118, 110)
TEAL_SOFT = (204, 251, 241)
CORAL = (14, 116, 144)  # deep sky as secondary accent
CORAL_SOFT = (224, 242, 254)
WHITE = (255, 255, 255)
LINE = (203, 213, 225)


def font(size: int, bold: bool = False):
    return ImageFont.truetype(str(FONTS["bold" if bold else "regular"]), size)


def rr(draw, box, radius, fill, outline=None, width=3):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def text_center(draw, box, text, fnt, fill=INK):
    x0, y0, x1, y1 = box
    bbox = draw.textbbox((0, 0), text, font=fnt)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((x0 + x1 - tw) / 2, (y0 + y1 - th) / 2), text, font=fnt, fill=fill)


def multiline(draw, cx, cy, lines, fnt, fill=INK, gap=6):
    heights, widths = [], []
    for line in lines:
        b = draw.textbbox((0, 0), line, font=fnt)
        widths.append(b[2] - b[0])
        heights.append(b[3] - b[1])
    total = sum(heights) + gap * (len(lines) - 1)
    y = cy - total / 2
    for i, line in enumerate(lines):
        draw.text((cx - widths[i] / 2, y), line, font=fnt, fill=fill)
        y += heights[i] + gap


def arrow(draw, x0, y0, x1, y1, fill=TEAL, width=5):
    import math

    draw.line((x0, y0, x1, y1), fill=fill, width=width)
    ang = math.atan2(y1 - y0, x1 - x0)
    size = 16
    draw.polygon(
        [
            (x1, y1),
            (x1 - size * math.cos(ang - 0.45), y1 - size * math.sin(ang - 0.45)),
            (x1 - size * math.cos(ang + 0.45), y1 - size * math.sin(ang + 0.45)),
        ],
        fill=fill,
    )


def make_definition():
    img = Image.new("RGB", (1600, 900), BG)
    d = ImageDraw.Draw(img)
    d.text((70, 50), "Музыкально-ритмическое развитие", font=font(40, True), fill=INK)
    d.text((70, 115), "слышать музыку и отвечать на неё движением", font=font(26), fill=MUTED)

    boxes = [
        (120, 280, 480, 620, "Слух", "темп · ритм\nхарактер", TEAL_SOFT, TEAL),
        (560, 280, 920, 620, "Эмоция", "настроение\nпереживание", CORAL_SOFT, CORAL),
        (1000, 280, 1480, 620, "Движение", "жест · шаг\nпластика", TEAL_SOFT, TEAL),
    ]
    for x0, y0, x1, y1, title, body, fill, outline in boxes:
        rr(d, (x0, y0, x1, y1), 28, fill, outline, 4)
        text_center(d, (x0, y0 + 40, x1, y0 + 120), title, font(34, True), outline)
        multiline(d, (x0 + x1) / 2, (y0 + y1) / 2 + 40, body.split("\n"), font(24), MUTED)
    arrow(d, 490, 450, 550, 450)
    arrow(d, 930, 450, 990, 450)
    rr(d, (120, 700, 1480, 820), 20, WHITE, LINE, 2)
    text_center(d, (120, 700, 1480, 820), "характер · темп · динамика · ритм", font(28, True), TEAL)
    img.save(OUT / "p14-scheme-definition.png")


def make_not_only_dance():
    img = Image.new("RGB", (1600, 900), BG)
    d = ImageDraw.Draw(img)
    d.text((70, 45), "Это шире, чем танец к утреннику", font=font(38, True), fill=INK)
    rr(d, (80, 160, 720, 780), 28, (254, 242, 242), (220, 38, 38), 4)
    text_center(d, (80, 200, 720, 280), "Узко", font(30, True), (185, 28, 28))
    multiline(
        d,
        400,
        500,
        ["Только танец", "к утреннику", "", "показ", "заученные движения"],
        font(26),
        (127, 29, 29),
    )
    rr(d, (880, 160, 1520, 780), 28, TEAL_SOFT, TEAL, 4)
    text_center(d, (880, 200, 1520, 280), "Широко", font(30, True), TEAL)
    multiline(
        d,
        1200,
        500,
        [
            "слух и реакция",
            "игра и импровизация",
            "координация",
            "внимание и память",
            "связь с речью",
        ],
        font(26),
        TEAL,
    )
    d.text((70, 820), "Танец — часть пути, но не вся цель", font=font(24, True), fill=MUTED)
    img.save(OUT / "p14-scheme-not-only.png")


def make_chain():
    img = Image.new("RGB", (1600, 900), BG)
    d = ImageDraw.Draw(img)
    d.text((70, 50), "Как работает развитие", font=font(40, True), fill=INK)
    items = [
        ("Музыка", "образ"),
        ("Эмоция", "переживание"),
        ("Движение", "отклик"),
        ("Осмысление", "правило"),
    ]
    x = 70
    for i, (title, sub) in enumerate(items):
        fill = TEAL_SOFT if i % 2 == 0 else CORAL_SOFT
        outline = TEAL if i % 2 == 0 else CORAL
        rr(d, (x, 280, x + 300, 560), 26, fill, outline, 4)
        text_center(d, (x, 330, x + 300, 410), title, font(28, True), outline)
        text_center(d, (x, 430, x + 300, 500), sub, font(22), MUTED)
        if i < 3:
            arrow(d, x + 310, 420, x + 350, 420)
        x += 380
    rr(d, (70, 680, 1530, 820), 20, WHITE, LINE, 2)
    text_center(
        d,
        (70, 680, 1530, 820),
        "Дошкольник понимает музыку через действие и образ",
        font(26, True),
        TEAL,
    )
    img.save(OUT / "p14-scheme-chain.png")


def make_four_spheres():
    img = Image.new("RGB", (1600, 900), BG)
    d = ImageDraw.Draw(img)
    d.text((70, 40), "Ритм развивает четыре сферы", font=font(38, True), fill=INK)
    items = [
        (80, 160, "1", "Координация", "согласованность\nтела и равновесие"),
        (840, 160, "2", "Внимание", "сигнал, пауза,\nпереключение"),
        (80, 520, "3", "Память", "последовательность\nи форма"),
        (840, 520, "4", "Речь", "слог, дыхание,\nфраза"),
    ]
    for x, y, num, title, body in items:
        rr(d, (x, y, x + 680, y + 300), 26, WHITE, TEAL, 4)
        d.ellipse((x + 36, y + 40, x + 116, y + 120), fill=TEAL)
        text_center(d, (x + 36, y + 40, x + 116, y + 120), num, font(30, True), WHITE)
        d.text((x + 150, y + 55), title, font=font(32, True), fill=INK)
        multiline(d, x + 340, y + 190, body.split("\n"), font(24), MUTED)
    # center badge
    d.ellipse((700, 390, 900, 590), fill=TEAL)
    text_center(d, (700, 390, 900, 590), "РИТМ", font(28, True), WHITE)
    img.save(OUT / "p14-scheme-spheres.png")


def make_concepts():
    img = Image.new("RGB", (1600, 1000), BG)
    d = ImageDraw.Draw(img)
    d.text((60, 35), "Четыре понятия — не путать", font=font(36, True), fill=INK)
    headers = ["Понятие", "Суть", "Цель в ДОУ"]
    rows = [
        ["Ритмика", "метод через движение", "освоить музыку"],
        ["Муз.-двигательная\nдеятельность", "вид детской деятельности", "целостное развитие"],
        ["Танец", "художественная форма", "выразительность"],
        ["Хореография", "постановка и техника", "элементы, не профподготовка"],
    ]
    cols = [60, 420, 900, 1540]
    y = 120
    rr(d, (50, y, 1550, y + 70), 14, TEAL, TEAL, 2)
    for i, h in enumerate(headers):
        d.text((cols[i] + 20, y + 20), h, font=font(24, True), fill=WHITE)
    y = 210
    for idx, row in enumerate(rows):
        fill = WHITE if idx % 2 == 0 else TEAL_SOFT
        rr(d, (50, y, 1550, y + 160), 14, fill, LINE, 2)
        for i, cell in enumerate(row):
            lines = cell.split("\n")
            yy = y + 45
            for line in lines:
                d.text((cols[i] + 20, yy), line, font=font(22), fill=INK)
                yy += 32
        y += 175
    img.save(OUT / "p14-scheme-concepts.png")


def make_roles():
    img = Image.new("RGB", (1600, 900), BG)
    d = ImageDraw.Draw(img)
    d.text((70, 40), "Кто что делает", font=font(40, True), fill=INK)
    rr(d, (70, 140, 740, 780), 28, TEAL_SOFT, TEAL, 4)
    text_center(d, (70, 170, 740, 240), "Музыкальный руководитель", font(26, True), TEAL)
    for i, t in enumerate(
        [
            "проектирует занятие",
            "подбирает музыку",
            "ведёт ритмические формы",
            "следит за качеством",
        ]
    ):
        d.text((120, 300 + i * 90), f"•  {t}", font=font(24), fill=INK)

    rr(d, (860, 140, 1530, 780), 28, CORAL_SOFT, CORAL, 4)
    text_center(d, (860, 170, 1530, 240), "Воспитатель", font(26, True), CORAL)
    for i, t in enumerate(
        [
            "закрепляет в группе",
            "наблюдает за детьми",
            "поддерживает интерес",
            "связывает с речью и режимом",
        ]
    ):
        d.text((920, 300 + i * 90), f"•  {t}", font=font(24), fill=INK)

    d.ellipse((730, 400, 870, 540), fill=WHITE, outline=TEAL, width=4)
    multiline(d, 800, 470, ["общее", "дело"], font(20, True), TEAL)
    img.save(OUT / "p14-scheme-roles.png")


def make_reactions():
    img = Image.new("RGB", (1600, 900), BG)
    d = ImageDraw.Draw(img)
    d.text((70, 40), "Упражнения на музыкальную реакцию", font=font(36, True), fill=INK)
    items = [
        ("Старт / стоп", "движение только\nпока звучит музыка"),
        ("Сильная доля", "хлопок или притоп\nтолько на «раз»"),
        ("Динамика", "piano — на носках\nforte — энергичный шаг"),
        ("Темп", "ускорение и\nзамедление по музыке"),
        ("Смена образа", "«капельки» / «ветер»\nпо фразе"),
    ]
    w = 280
    gap = 30
    start = 70
    for i, (title, body) in enumerate(items):
        x = start + i * (w + gap)
        rr(d, (x, 180, x + w, 700), 24, WHITE, TEAL if i % 2 == 0 else CORAL, 4)
        d.ellipse((x + 95, 220, x + 185, 310), fill=TEAL if i % 2 == 0 else CORAL)
        text_center(d, (x + 95, 220, x + 185, 310), str(i + 1), font(28, True), WHITE)
        multiline(d, x + w / 2, 420, title.split(" "), font(22, True), INK)
        multiline(d, x + w / 2, 560, body.split("\n"), font(18), MUTED)
    rr(d, (70, 760, 1530, 860), 18, TEAL_SOFT, TEAL, 3)
    text_center(d, (70, 760, 1530, 860), "Движение = диагностика восприятия", font(26, True), TEAL)
    img.save(OUT / "p14-scheme-reactions.png")


def make_balance():
    img = Image.new("RGB", (1600, 900), BG)
    d = ImageDraw.Draw(img)
    d.text((70, 50), "Баланс хорошего занятия", font=font(40, True), fill=INK)
    steps = [
        ("1", "Восприятие\nи реакция"),
        ("2", "Игра"),
        ("3", "Элементы\nтанца"),
    ]
    x = 180
    for i, (num, title) in enumerate(steps):
        rr(d, (x, 280, x + 320, 560), 26, TEAL_SOFT if i != 2 else CORAL_SOFT, TEAL if i != 2 else CORAL, 4)
        d.ellipse((x + 110, 310, x + 210, 410), fill=TEAL if i != 2 else CORAL)
        text_center(d, (x + 110, 310, x + 210, 410), num, font(32, True), WHITE)
        multiline(d, x + 160, 480, title.split("\n"), font(24, True), INK)
        if i < 2:
            arrow(d, x + 340, 420, x + 380, 420)
        x += 420
    rr(d, (180, 680, 1420, 820), 20, WHITE, LINE, 2)
    text_center(
        d,
        (180, 680, 1420, 820),
        "Не начинайте с постановки «на показ» — сначала слух и реакция",
        font(24, True),
        TEAL,
    )
    img.save(OUT / "p14-scheme-balance.png")


def make_characters_cards():
    img = Image.new("RGB", (1600, 900), BG)
    d = ImageDraw.Draw(img)
    d.text((70, 40), "Характер музыки → качество движения", font=font(36, True), fill=INK)
    cards = [
        ("Марш", "чёткий шаг\nсобранность"),
        ("Плясовая", "лёгкость\nпрыжковость"),
        ("Колыбельная", "плавность\nмягкость"),
        ("Вальс", "кружение\nмягкий «раз»"),
    ]
    for i, (title, body) in enumerate(cards):
        x = 70 + i * 380
        rr(d, (x, 180, x + 340, 760), 26, WHITE, TEAL if i % 2 == 0 else CORAL, 4)
        rr(d, (x + 30, 220, x + 310, 360), 18, TEAL_SOFT if i % 2 == 0 else CORAL_SOFT, None, 0)
        text_center(d, (x + 30, 220, x + 310, 360), title, font(28, True), TEAL if i % 2 == 0 else CORAL)
        multiline(d, x + 170, 520, body.split("\n"), font(26), MUTED)
    img.save(OUT / "p14-scheme-characters.png")


if __name__ == "__main__":
    make_definition()
    make_not_only_dance()
    make_chain()
    make_four_spheres()
    make_concepts()
    make_roles()
    make_reactions()
    make_balance()
    make_characters_cards()
    print("Diagrams saved to", OUT)
