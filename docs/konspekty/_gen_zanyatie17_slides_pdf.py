#!/usr/bin/env python3
"""Landscape slide-deck PDF twin for lesson 17 presentation."""

from pathlib import Path

from reportlab.lib.pagesizes import landscape
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

W, H = landscape((297 * mm, 210 * mm))  # A4 landscape
OUT = Path(__file__).resolve().parent / "zanyatie-17-prezentaciya.pdf"
ART = Path("/opt/cursor/artifacts/zanyatie-17-prezentaciya.pdf")

TEAL = (0.12, 0.35, 0.32)
TEAL_D = (0.08, 0.25, 0.22)
CORAL = (0.88, 0.48, 0.37)
GOLD = (0.83, 0.64, 0.22)
LEAF = (0.36, 0.55, 0.35)
SKY = (0.30, 0.55, 0.72)
ROSE = (0.77, 0.36, 0.48)
CREAM = (1.0, 0.98, 0.96)
INK = (0.12, 0.16, 0.14)
MUTED = (0.36, 0.42, 0.39)
WHITE = (1, 1, 1)
SAND = (0.95, 0.91, 0.85)


def fonts():
    pdfmetrics.registerFont(TTFont("DejaVu", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
    pdfmetrics.registerFont(TTFont("DejaVuBold", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))


def rgb(c, color):
    c.setFillColorRGB(*color)


def bg(c, color=CREAM):
    rgb(c, color)
    c.rect(0, 0, W, H, fill=1, stroke=0)


def bar(c):
    rgb(c, TEAL)
    c.rect(0, 0, 6 * mm, H, fill=1, stroke=0)


def footer(c, n, total=18):
    rgb(c, MUTED)
    c.setFont("DejaVu", 9)
    c.drawString(14 * mm, 8 * mm, f"Занятие 17 · Игровой подход · Альбом путешествий   {n}/{total}")


def title(c, text, sub=None):
    bar(c)
    rgb(c, TEAL_D)
    c.setFont("DejaVuBold", 22)
    c.drawString(14 * mm, H - 18 * mm, text)
    if sub:
        rgb(c, MUTED)
        c.setFont("DejaVu", 12)
        c.drawString(14 * mm, H - 26 * mm, sub)


def round_rect(c, x, y, w, h, color, r=8):
    rgb(c, color)
    c.roundRect(x, y, w, h, r, fill=1, stroke=0)


def text_box(c, x, y, text, size=12, bold=False, color=INK):
    rgb(c, color)
    c.setFont("DejaVuBold" if bold else "DejaVu", size)
    c.drawString(x, y, text)


def wrapped(c, x, y, text, size=12, bold=False, color=INK, leading=16, max_w=200):
    rgb(c, color)
    c.setFont("DejaVuBold" if bold else "DejaVu", size)
    # simple wrap by spaces
    words = text.split()
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if c.stringWidth(test, "DejaVuBold" if bold else "DejaVu", size) <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    for i, line in enumerate(lines):
        c.drawString(x, y - i * leading, line)
    return len(lines)


def card(c, x, y, w, h, color, title_t, lines, title_white=True):
    round_rect(c, x, y, w, h, color)
    text_box(c, x + 8 * mm, y + h - 12 * mm, title_t, size=14, bold=True, color=WHITE if title_white else INK)
    yy = y + h - 24 * mm
    for line in lines:
        text_box(c, x + 8 * mm, yy, line, size=11, color=WHITE if title_white else INK)
        yy -= 6.5 * mm


def circle(c, x, y, r, color):
    rgb(c, color)
    c.circle(x, y, r, fill=1, stroke=0)


def build():
    fonts()
    c = canvas.Canvas(str(OUT), pagesize=(W, H))
    total = 18

    # 1 title
    bg(c, TEAL_D)
    circle(c, 20 * mm, H - 20 * mm, 35 * mm, TEAL)
    circle(c, W - 15 * mm, 20 * mm, 40 * mm, CORAL)
    circle(c, W - 30 * mm, H - 10 * mm, 25 * mm, GOLD)
    text_box(c, 0, H / 2 + 35 * mm, "ЗАНЯТИЕ 17 · МОДУЛЬ IV", 14, False, GOLD)
    # center manually
    c.setFont("DejaVu", 14)
    rgb(c, GOLD)
    t = "ЗАНЯТИЕ 17 · МОДУЛЬ IV"
    c.drawString((W - c.stringWidth(t, "DejaVu", 14)) / 2, H / 2 + 40 * mm, t)
    c.setFont("DejaVuBold", 28)
    rgb(c, WHITE)
    for i, line in enumerate(["Игровой подход", "в обучении музыкально-ритмическим движениям"]):
        c.drawString((W - c.stringWidth(line, "DejaVuBold", 28)) / 2, H / 2 + 18 * mm - i * 12 * mm, line)
    c.setFont("DejaVu", 16)
    rgb(c, SAND)
    t = "«Альбом путешествий в Страну движений»"
    c.drawString((W - c.stringWidth(t, "DejaVu", 16)) / 2, H / 2 - 18 * mm, t)
    c.setFont("DejaVuBold", 14)
    rgb(c, GOLD)
    t = "Пружинка  ·  Шажок  ·  Прыжок"
    c.drawString((W - c.stringWidth(t, "DejaVuBold", 14)) / 2, H / 2 - 32 * mm, t)
    c.showPage()

    # 2 formula
    bg(c)
    title(c, "Главная формула занятия", "Детство — это прежде всего игра")
    round_rect(c, 40 * mm, H / 2 + 5 * mm, W - 80 * mm, 28 * mm, TEAL)
    c.setFont("DejaVuBold", 26)
    rgb(c, WHITE)
    t = "Что понятно — то выполнимо"
    c.drawString((W - c.stringWidth(t, "DejaVuBold", 26)) / 2, H / 2 + 14 * mm, t)
    steps = [("1", "Интерес", CORAL), ("2", "Понимание", GOLD), ("3", "Проба", LEAF), ("4", "Осознание", SKY), ("5", "Танец", ROSE), ("6", "Туфелька", TEAL)]
    x = 25 * mm
    for num, label, col in steps:
        circle(c, x + 15 * mm, 45 * mm, 16 * mm, col)
        text_box(c, x + 11 * mm, 47 * mm, num, 12, True, WHITE)
        text_box(c, x + 4 * mm, 22 * mm, label, 11, True, INK)
        x += 45 * mm
    footer(c, 2, total)
    c.showPage()

    # 3 problem
    bg(c)
    title(c, "Где уже есть игра — а где её нет")
    items = [
        ("Распевание", "✓ в игре", LEAF),
        ("Пение", "✓ в игре", SKY),
        ("Слушание", "✓ в игре", GOLD),
        ("Дидактика", "✓ в игре", TEAL),
        ("Движения", "✗ выпадает", (0.42, 0.23, 0.23)),
    ]
    x = 12 * mm
    for name, mark, col in items:
        round_rect(c, x, 35 * mm, 52 * mm, 110 * mm, col)
        text_box(c, x + 6 * mm, 125 * mm, name, 13, True, WHITE)
        text_box(c, x + 8 * mm, 55 * mm, mark, 12, True, GOLD if "✓" in mark else CORAL)
        x += 57 * mm
    footer(c, 3, total)
    c.showPage()

    # 4 contrast
    bg(c)
    title(c, "Сухой повтор  vs  Игровое обучение")
    card(c, 12 * mm, 25 * mm, 130 * mm, 140 * mm, (0.42, 0.23, 0.23), "Сухой повтор", [
        "«Поставь ногу сюда»",
        "Ошибка = замечание при всех",
        "Абстрактная «пружинка»",
        "Круг держится словами",
        "Результат далёкий",
        "",
        "→ страх · скука · долгая постановка",
    ])
    card(c, 155 * mm, 25 * mm, 130 * mm, 140 * mm, TEAL, "Игровое обучение", [
        "«Зайчик учит — Прыжок помогает»",
        "Ошибка внутри сюжета",
        "Кукла, которую можно потрогать",
        "Звёздочки-домики на полу",
        "Туфелька за конкретный успех",
        "",
        "→ интерес · понимание · радость",
    ])
    footer(c, 4, total)
    c.showPage()

    # 5 heroes
    bg(c)
    title(c, "Три героя — три кирпичика движения", "Почти все детские танцы = шаги + прыжки на мягкой пружинке")
    heroes = [("Пружинка", "мягкая пружина", ROSE, 55), ("Шажок", "шаги и ход", SKY, 148), ("Прыжок", "прыжки, галоп", CORAL, 241)]
    for name, role, col, x in heroes:
        circle(c, x * mm, 95 * mm, 28 * mm, col)
        t = name
        c.setFont("DejaVuBold", 14)
        rgb(c, WHITE)
        c.drawString(x * mm - c.stringWidth(t, "DejaVuBold", 14) / 2, 92 * mm, t)
        text_box(c, x * mm - 20 * mm, 55 * mm, role, 12, False, INK)
    round_rect(c, 30 * mm, 20 * mm, W - 60 * mm, 22 * mm, SAND)
    text_box(c, 45 * mm, 28 * mm, "Герои — не декорация. Это инструмент анализа движения.", 13, True, TEAL_D)
    footer(c, 5, total)
    c.showPage()

    # 6 table schemas
    bg(c)
    title(c, "Движение = схема героев")
    rows = [
        ("Движение", "Кто помогает"),
        ("Пружинка", "Пружинка"),
        ("Приставной шаг", "Шажок + Пружинка"),
        ("Боковой галоп", "Шажок + Пружинка + Прыжок"),
        ("Поскок", "Шажок + Прыжок (+ Пружинка)"),
        ("Ковырялочка без поскока", "Пружинка + Шажок"),
        ("Ковырялочка на поскоке", "+ Прыжок"),
    ]
    y = H - 45 * mm
    for i, (a, b) in enumerate(rows):
        col = TEAL if i == 0 else (SOFT if i % 2 else WHITE)
        SOFT = (0.91, 0.95, 0.94)
        round_rect(c, 30 * mm, y - 2 * mm, 237 * mm, 14 * mm, TEAL if i == 0 else ((0.91, 0.95, 0.94) if i % 2 else WHITE), r=3)
        text_box(c, 35 * mm, y + 2 * mm, a, 11, i == 0, WHITE if i == 0 else INK)
        text_box(c, 150 * mm, y + 2 * mm, b, 11, i == 0, WHITE if i == 0 else INK)
        y -= 15 * mm
    footer(c, 6, total)
    c.showPage()

    # 7 space
    bg(c)
    title(c, "Разметка зала и Волшебная туфелька")
    card(c, 12 * mm, 25 * mm, 135 * mm, 140 * mm, TEAL, "Танцевальная карусель", [
        "★ звёздочки / домики пар",
        "★ меньше столкновений",
        "★ круг сохраняется легче",
        "★ экономия минут занятия",
        "",
        "Разметка учит пространство",
        "без бесконечных команд",
    ])
    card(c, 158 * mm, 25 * mm, 127 * mm, 140 * mm, GOLD, "Копилка достижений", [
        "Туфелька — успех в движении",
        "Значок — попадание в музыку",
        "Значок — выразительность",
        "«Знайка» — верная схема",
        "",
        "Ребёнок видит свой рост,",
        "а не только замечания",
    ], title_white=False)
    # fix gold card text color - rewrite body in ink via overlay note already ink if title_white False - good
    footer(c, 7, total)
    c.showPage()

    # 8 album map
    bg(c)
    title(c, "Карта Альбома путешествий")
    pages = [
        ("Младшая", "Сказочная поляна", LEAF),
        ("Средняя", "Бабушкина деревня", SKY),
        ("Старшая", "Школа Магистра", CORAL),
        ("Подготовит.", "Город Танцев", GOLD),
    ]
    x = 15 * mm
    for i, (age, place, col) in enumerate(pages):
        round_rect(c, x, 40 * mm, 60 * mm, 110 * mm, col)
        text_box(c, x + 8 * mm, 130 * mm, age, 12, True, WHITE)
        wrapped(c, x + 6 * mm, 100 * mm, place, 16, True, WHITE, 18, 50 * mm)
        if i < 3:
            text_box(c, x + 58 * mm, 90 * mm, "→", 22, True, TEAL_D)
        x += 70 * mm
    footer(c, 8, total)
    c.showPage()

    # 9 junior
    bg(c)
    title(c, "Младшая · Сказочная поляна", "Образ ведёт за собой движение")
    rows = [
        ("Образ", "Движение", "Герой"),
        ("Тропинка", "спокойный / бодрый шаг", "Шажок"),
        ("Бабочки", "пружинка", "Пружинка"),
        ("Зайчик", "прыжки на двух", "Прыжок"),
        ("Машина / лошадка", "топотушки / галопчик", "Шажок + Прыжок"),
        ("Солнышко", "носок → пятка", "Пружинка"),
        ("Дождик / цветочки", "бег, фонарики, кружение", "Пружинка"),
    ]
    y = H - 42 * mm
    for i, row in enumerate(rows):
        round_rect(c, 12 * mm, y - 2 * mm, W - 24 * mm, 13 * mm, TEAL if i == 0 else ((0.91, 0.95, 0.94) if i % 2 else WHITE), r=2)
        xs = [16 * mm, 80 * mm, 200 * mm]
        for x, val in zip(xs, row):
            text_box(c, x, y + 2 * mm, val, 10, i == 0, WHITE if i == 0 else INK)
        y -= 14 * mm
    round_rect(c, 12 * mm, 16 * mm, W - 24 * mm, 14 * mm, SAND, r=4)
    text_box(c, 16 * mm, 20 * mm, "Приём: забыли пружинку → Пружинка «отвернулась» → пригласили → движение с пружинкой", 10, True, TEAL_D)
    footer(c, 9, total)
    c.showPage()

    # 10 middle
    bg(c)
    title(c, "Средняя · Бабушкина деревня")
    card(c, 12 * mm, 25 * mm, 140 * mm, 140 * mm, SKY, "Маршрут страницы", [
        "Кошечка → мягкий шаг",
        "Дорожка → бодрый шаг",
        "+ Прыжок → лёгкие поскоки",
        "Лошадка → прямой галоп",
        "Берёзка → хороводный шаг",
        "Платочек → передача, кружение",
        "У берёзки → притопы, «тарелочки»",
    ])
    card(c, 165 * mm, 25 * mm, 120 * mm, 140 * mm, TEAL, "Секрет поскока", [
        "Шажок + Пружинка = шаг",
        "",
        "+ Прыжок = поскок",
        "",
        "Дети сами собирают схему",
        "и понимают, кого «позвать»",
    ])
    footer(c, 10, total)
    c.showPage()

    # 11 right left
    bg(c)
    title(c, "Правая и левая — через «волшебство»")
    round_rect(c, 12 * mm, 70 * mm, 130 * mm, 85 * mm, SAND)
    text_box(c, 20 * mm, 140 * mm, "1. Стоим рядом", 14, True, TEAL_D)
    for i, line in enumerate(["Лента на правой ноге у обоих", "Правые — с одной стороны"]):
        text_box(c, 20 * mm, 120 * mm - i * 10 * mm, line, 12, False, INK)
    round_rect(c, 155 * mm, 70 * mm, 130 * mm, 85 * mm, TEAL)
    text_box(c, 163 * mm, 140 * mm, "2. Лицом друг к другу", 14, True, WHITE)
    for i, line in enumerate(["«Волшебная палочка!»", "Ленты — с разных сторон"]):
        text_box(c, 163 * mm, 120 * mm - i * 10 * mm, line, 12, False, WHITE)
    wrapped(c, 12 * mm, 45 * mm, "Если начать с одной стороны — «барашки на бревне». С разных — каждой ножке свободно и красиво.", 12, False, INK, 15, W - 30 * mm)
    footer(c, 11, total)
    c.showPage()

    # 12 senior
    bg(c)
    title(c, "Старшая · Школа Магистра")
    blocks = [("Вход", CORAL), ("Поскоки", SKY), ("Сад", LEAF), ("Балетный", TEAL), ("Народный", GOLD), ("Финал", ROSE)]
    x = 10 * mm
    for name, col in blocks:
        round_rect(c, x, 35 * mm, 44 * mm, 120 * mm, col)
        wrapped(c, x + 4 * mm, 130 * mm, name, 12, True, WHITE, 14, 36 * mm)
        x += 48 * mm
    footer(c, 12, total)
    c.showPage()

    # 13 prep
    bg(c)
    title(c, "Подготовительная · Город Танцев", "Сначала движения — потом бал")
    rows = [
        ("Уже знали", "Собираем дальше"),
        ("Приставной шаг", "+ Прыжок = боковой галоп"),
        ("Хороводный шаг", "руки / точка / переменный"),
        ("Пружинящий шаг", "припадание"),
        ("Ковырялочка без поскока", "на поскоке"),
        ("Весёлые ножки", "метелочка, козлик, крылья"),
    ]
    y = H - 42 * mm
    for i, (a, b) in enumerate(rows):
        round_rect(c, 20 * mm, y - 2 * mm, W - 40 * mm, 13 * mm, TEAL if i == 0 else ((0.91, 0.95, 0.94) if i % 2 else WHITE), r=2)
        text_box(c, 25 * mm, y + 2 * mm, a, 10, i == 0, WHITE if i == 0 else INK)
        text_box(c, 130 * mm, y + 2 * mm, b, 10, i == 0, WHITE if i == 0 else INK)
        y -= 14 * mm
    round_rect(c, 20 * mm, 18 * mm, W - 40 * mm, 16 * mm, GOLD)
    text_box(c, 30 * mm, 23 * mm, "Рецепт Полечки: Прыжок + Пружинка + два шага Шажка = Полька!", 12, True, INK)
    footer(c, 13, total)
    c.showPage()

    # 14 algorithm
    bg(c)
    title(c, "Алгоритм ведения страницы", "8–10 минут живого обучения")
    steps = [
        "1. Открыть страницу",
        "2. Вызвать героя",
        "3. Сюжетный мостик",
        "4. Показ + проба",
        "5. Вопрос / схема",
        "6. Повтор в образе",
        "7. Коррекция сюжетом",
        "8. Маленький успех",
        "9. Мостик в танец",
    ]
    for i, t in enumerate(steps):
        row, col = divmod(i, 3)
        x = 12 * mm + col * 95 * mm
        y = 120 * mm - row * 40 * mm
        round_rect(c, x, y, 88 * mm, 32 * mm, TEAL if i % 2 == 0 else LEAF)
        text_box(c, x + 6 * mm, y + 12 * mm, t, 12, True, WHITE)
    footer(c, 14, total)
    c.showPage()

    # 15 do don't
    bg(c)
    title(c, "Делать  /  Не делать")
    card(c, 12 * mm, 25 * mm, 135 * mm, 140 * mm, LEAF, "Делать", [
        "✓ один новый акцент",
        "✓ герой до движения",
        "✓ править сюжетом",
        "✓ держать музыку",
        "✓ давать видимый успех",
        "✓ мостик в танец",
    ])
    card(c, 158 * mm, 25 * mm, 127 * mm, 140 * mm, CORAL, "Не делать", [
        "✗ вся страница без дозировки",
        "✗ термин без образа",
        "✗ стыдить при всех",
        "✗ спектакль без навыка",
        "✗ забывать безопасность",
        "✗ сравнивать детей",
    ])
    footer(c, 15, total)
    c.showPage()

    # 16 blank
    bg(c)
    title(c, "Бланк «Страница альбома»")
    fields = ["Возраст", "Движение", "Герои на схеме", "Сюжет / образ", "Текст ведущего", "Снять страх ошибки", "Показать успех", "Мостик в танец"]
    y = H - 42 * mm
    for i, f in enumerate(fields):
        round_rect(c, 20 * mm, y - 2 * mm, W - 40 * mm, 13 * mm, (0.91, 0.95, 0.94) if i % 2 else WHITE, r=2)
        text_box(c, 25 * mm, y + 2 * mm, f, 11, True, TEAL_D)
        text_box(c, 110 * mm, y + 2 * mm, "________________________________", 11, False, MUTED)
        y -= 14 * mm
    footer(c, 16, total)
    c.showPage()

    # 17 checklist
    bg(c)
    title(c, "Чек-лист готового приёма")
    checks = [
        "Есть образ/сюжет, а не только термин?",
        "Герои реально объясняют состав движения?",
        "Есть поисковый вопрос, а не одна команда?",
        "Пространство размечено / ясно?",
        "Ошибка исправляется без стыда?",
        "Успех ребёнку виден?",
        "Есть мостик в танец?",
        "Игра не съела обучение?",
    ]
    y = H - 42 * mm
    for i, q in enumerate(checks):
        circle(c, 22 * mm, y + 3 * mm, 4 * mm, TEAL if i % 2 == 0 else GOLD)
        text_box(c, 30 * mm, y, f"☐  {q}", 12, False, INK)
        y -= 14 * mm
    footer(c, 17, total)
    c.showPage()

    # 18 finale
    bg(c, TEAL_D)
    circle(c, 20 * mm, 20 * mm, 40 * mm, TEAL)
    circle(c, W - 20 * mm, H - 20 * mm, 35 * mm, CORAL)
    c.setFont("DejaVu", 14)
    rgb(c, GOLD)
    t = "Итог путешествия"
    c.drawString((W - c.stringWidth(t, "DejaVu", 14)) / 2, H / 2 + 45 * mm, t)
    c.setFont("DejaVuBold", 16)
    rgb(c, WHITE)
    lines = [
        "Не страх и повтор уговаривают ребёнка двигаться —",
        "а понятная игра, в которой можно ошибиться,",
        "попробовать снова и увидеть свою туфельку успеха.",
    ]
    y = H / 2 + 20 * mm
    for line in lines:
        c.drawString((W - c.stringWidth(line, "DejaVuBold", 16)) / 2, y, line)
        y -= 10 * mm
    c.setFont("DejaVu", 13)
    rgb(c, SAND)
    t = "Пружинка + Шажок + Прыжок = ключ к осознанному движению"
    c.drawString((W - c.stringWidth(t, "DejaVu", 13)) / 2, y - 10 * mm, t)
    c.setFont("DejaVu", 11)
    rgb(c, (0.85, 0.9, 0.88))
    t = "ДЗ: одна полная страница альбома на 8–10 минут для выбранной группы"
    c.drawString((W - c.stringWidth(t, "DejaVu", 11)) / 2, 28 * mm, t)
    c.showPage()

    c.save()
    ART.write_bytes(OUT.read_bytes())
    print(f"OK {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    build()
