#!/usr/bin/env python3
"""Ready-to-show PowerPoint for lesson 17 — Album of Journeys."""

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import nsmap
from pptx.util import Emu, Inches, Pt

# Palette — fairy-tale journey (not purple/cream AI defaults)
INK = RGBColor(0x1F, 0x2A, 0x24)
CREAM = RGBColor(0xFF, 0xFB, 0xF5)
SAND = RGBColor(0xF3, 0xE8, 0xD8)
TEAL = RGBColor(0x1F, 0x7A, 0x6E)
TEAL_DEEP = RGBColor(0x14, 0x5A, 0x52)
CORAL = RGBColor(0xE0, 0x7A, 0x5F)
GOLD = RGBColor(0xD4, 0xA3, 0x37)
LEAF = RGBColor(0x5B, 0x8C, 0x5A)
SKY = RGBColor(0x4C, 0x8D, 0xB8)
ROSE = RGBColor(0xC4, 0x5D, 0x7A)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
MUTED = RGBColor(0x5C, 0x6B, 0x63)
SOFT = RGBColor(0xE8, 0xF3, 0xF0)

OUT = Path(__file__).resolve().parent / "zanyatie-17-prezentaciya.pptx"
ART = Path("/opt/cursor/artifacts/zanyatie-17-prezentaciya.pptx")


def set_run(p, text, *, size=18, bold=False, color=INK, font="Georgia"):
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = font
    return run


def add_textbox(slide, left, top, width, height, text, *, size=18, bold=False, color=INK, align=PP_ALIGN.LEFT, font="Georgia"):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    set_run(p, text, size=size, bold=bold, color=color, font=font)
    return box


def add_lines(slide, left, top, width, height, lines, *, size=16, color=INK, bold_first=False, spacing=6):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        p.space_after = Pt(spacing)
        set_run(p, line, size=size, bold=(bold_first and i == 0), color=color)
    return box


def fill_shape(shape, color):
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()


def rounded(slide, left, top, width, height, color):
    sh = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    fill_shape(sh, color)
    return sh


def oval(slide, left, top, width, height, color):
    sh = slide.shapes.add_shape(MSO_SHAPE.OVAL, left, top, width, height)
    fill_shape(sh, color)
    return sh


def rect(slide, left, top, width, height, color):
    sh = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    fill_shape(sh, color)
    return sh


def bg(slide, color=CREAM):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color


def footer(slide, n, total=18):
    add_textbox(
        slide,
        Inches(0.4),
        Inches(7.15),
        Inches(8.5),
        Inches(0.3),
        f"Занятие 17 · Игровой подход · Альбом путешествий   {n}/{total}",
        size=11,
        color=MUTED,
        font="Calibri",
    )


def accent_bar(slide):
    rect(slide, Inches(0), Inches(0), Inches(0.18), Inches(7.5), TEAL)


def title_block(slide, title, subtitle=None):
    accent_bar(slide)
    add_textbox(slide, Inches(0.45), Inches(0.25), Inches(12.5), Inches(0.7), title, size=28, bold=True, color=TEAL_DEEP)
    if subtitle:
        add_textbox(slide, Inches(0.45), Inches(0.9), Inches(12.5), Inches(0.4), subtitle, size=16, color=MUTED, font="Calibri")


def card(slide, left, top, width, height, fill, title, body_lines, title_color=WHITE, body_color=WHITE):
    rounded(slide, left, top, width, height, fill)
    add_textbox(slide, left + Inches(0.2), top + Inches(0.15), width - Inches(0.35), Inches(0.4), title, size=16, bold=True, color=title_color)
    add_lines(
        slide,
        left + Inches(0.2),
        top + Inches(0.55),
        width - Inches(0.35),
        height - Inches(0.7),
        body_lines,
        size=13,
        color=body_color,
        spacing=4,
    )


def table(slide, left, top, width, rows, col_widths, header=True):
    cols = len(rows[0])
    shape = slide.shapes.add_table(len(rows), cols, left, top, width, Inches(0.42 * len(rows)))
    tbl = shape.table
    for i, w in enumerate(col_widths):
        tbl.columns[i].width = w
    for r, row in enumerate(rows):
        for c, val in enumerate(row):
            cell = tbl.cell(r, c)
            cell.text = ""
            p = cell.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.LEFT
            set_run(p, val, size=12 if r else 13, bold=(r == 0 or (header and r == 0)), color=WHITE if r == 0 else INK, font="Calibri")
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            # background
            fill = cell.fill
            fill.solid()
            if r == 0:
                fill.fore_color.rgb = TEAL
            elif r % 2:
                fill.fore_color.rgb = SOFT
            else:
                fill.fore_color.rgb = WHITE
    return shape


def hero_badge(slide, left, top, color, name, role):
    oval(slide, left, top, Inches(1.55), Inches(1.55), color)
    add_textbox(slide, left, top + Inches(0.45), Inches(1.55), Inches(0.45), name, size=14, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    add_textbox(slide, left - Inches(0.15), top + Inches(1.65), Inches(1.85), Inches(0.7), role, size=12, color=INK, align=PP_ALIGN.CENTER, font="Calibri")


def build():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank = prs.slide_layouts[6]

    # ---- 1 TITLE ----
    s = prs.slides.add_slide(blank)
    bg(s, TEAL_DEEP)
    # decorative circles
    oval(s, Inches(-0.8), Inches(-1.0), Inches(3.2), Inches(3.2), TEAL)
    oval(s, Inches(11.2), Inches(5.2), Inches(3.0), Inches(3.0), CORAL)
    oval(s, Inches(10.5), Inches(-0.6), Inches(2.2), Inches(2.2), GOLD)
    add_textbox(s, Inches(1.0), Inches(1.8), Inches(11), Inches(0.5), "ЗАНЯТИЕ 17 · МОДУЛЬ IV", size=16, color=GOLD, align=PP_ALIGN.CENTER, font="Calibri")
    add_textbox(s, Inches(1.0), Inches(2.4), Inches(11), Inches(1.2), "Игровой подход\nв обучении музыкально-ритмическим движениям", size=34, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    add_textbox(s, Inches(1.0), Inches(4.5), Inches(11), Inches(0.5), "«Альбом путешествий в Страну движений»", size=22, color=SAND, align=PP_ALIGN.CENTER)
    add_textbox(s, Inches(1.0), Inches(5.3), Inches(11), Inches(0.4), "Пружинка  ·  Шажок  ·  Прыжок", size=18, color=GOLD, align=PP_ALIGN.CENTER)
    add_textbox(s, Inches(1.0), Inches(6.3), Inches(11), Inches(0.35), "для студентов — будущих воспитателей дошкольников", size=14, color=SOFT, align=PP_ALIGN.CENTER, font="Calibri")

    # ---- 2 FORMULA ----
    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Главная формула занятия", "Детство — это прежде всего игра")
    rounded(s, Inches(1.5), Inches(2.0), Inches(10.3), Inches(1.6), TEAL)
    add_textbox(s, Inches(1.7), Inches(2.35), Inches(9.9), Inches(1.0), "Что понятно — то выполнимо", size=36, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    steps = [
        ("1", "Интерес", CORAL),
        ("2", "Понимание", GOLD),
        ("3", "Проба\nбез страха", LEAF),
        ("4", "Осознание", SKY),
        ("5", "Танец", ROSE),
        ("6", "Туфелька\nуспеха", TEAL),
    ]
    x = 0.55
    for num, label, col in steps:
        oval(s, Inches(x), Inches(4.2), Inches(1.7), Inches(1.7), col)
        add_textbox(s, Inches(x), Inches(4.55), Inches(1.7), Inches(0.35), num, size=14, bold=True, color=WHITE, align=PP_ALIGN.CENTER, font="Calibri")
        add_textbox(s, Inches(x), Inches(4.95), Inches(1.7), Inches(0.7), label, size=13, bold=True, color=WHITE, align=PP_ALIGN.CENTER, font="Calibri")
        x += 2.1
    footer(s, 2)

    # ---- 3 PROBLEM ----
    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Где уже есть игра — а где её нет", "Музыкальное занятие глазами ребёнка")
    items = [
        ("Распевание", "образ, этюд", LEAF, True),
        ("Пение", "значки, старание", SKY, True),
        ("Слушание", "иллюстрации", GOLD, True),
        ("Дидактика", "фланелеграф", TEAL, True),
        ("Движения", "часто сухой\n«повтори за мной»", CORAL, False),
    ]
    x = 0.5
    for title, body, col, ok in items:
        rounded(s, Inches(x), Inches(2.0), Inches(2.3), Inches(3.6), col if ok else RGBColor(0x6B, 0x3A, 0x3A))
        add_textbox(s, Inches(x + 0.1), Inches(2.3), Inches(2.1), Inches(0.8), title, size=18, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        add_textbox(s, Inches(x + 0.1), Inches(3.4), Inches(2.1), Inches(1.2), body, size=14, color=WHITE, align=PP_ALIGN.CENTER, font="Calibri")
        add_textbox(s, Inches(x + 0.1), Inches(4.8), Inches(2.1), Inches(0.5), "✓ в игре" if ok else "✗ выпадает", size=16, bold=True, color=GOLD if ok else CORAL, align=PP_ALIGN.CENTER)
        x += 2.5
    footer(s, 3)

    # ---- 4 CONTRAST ----
    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Сухой повтор  vs  Игровое обучение")
    card(
        s,
        Inches(0.5),
        Inches(1.6),
        Inches(5.8),
        Inches(4.8),
        RGBColor(0x6B, 0x3A, 0x3A),
        "Сухой повтор",
        [
            "«Поставь ногу сюда»",
            "Ошибка = замечание при всех",
            "Абстрактная «пружинка»",
            "Круг держится словами",
            "Результат далёкий и туманный",
            "",
            "→ страх · скука · долгая постановка",
        ],
    )
    card(
        s,
        Inches(6.9),
        Inches(1.6),
        Inches(5.8),
        Inches(4.8),
        TEAL,
        "Игровое обучение",
        [
            "«Зайчик учит — Прыжок помогает»",
            "Ошибка внутри сюжета, без стыда",
            "Кукла, которую можно потрогать",
            "Звёздочки-домики на полу",
            "Туфелька за конкретный успех",
            "",
            "→ интерес · понимание · радость",
        ],
    )
    footer(s, 4)

    # ---- 5 HEROES ----
    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Три героя — три кирпичика движения", "Почти все детские танцы = шаги + прыжки на мягкой пружинке")
    hero_badge(s, Inches(1.8), Inches(2.2), ROSE, "Пружинка", "мягкая «пружина»\nв ногах")
    hero_badge(s, Inches(5.9), Inches(2.2), SKY, "Шажок", "любые шаги\nи продвижения")
    hero_badge(s, Inches(10.0), Inches(2.2), CORAL, "Прыжок", "прыжки, поскоки,\nгалоп")
    rounded(s, Inches(1.5), Inches(5.3), Inches(10.3), Inches(1.2), SAND)
    add_textbox(
        s,
        Inches(1.7),
        Inches(5.55),
        Inches(9.9),
        Inches(0.8),
        "Герои — не декорация.\nЭто инструмент, которым ребёнок анализирует движение.",
        size=18,
        bold=True,
        color=TEAL_DEEP,
        align=PP_ALIGN.CENTER,
    )
    footer(s, 5)

    # ---- 6 SCHEMAS ----
    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Движение = схема героев", "Фланелеграф вместо сухой команды")
    table(
        s,
        Inches(1.2),
        Inches(1.7),
        Inches(10.8),
        [
            ["Движение", "Кто помогает"],
            ["Пружинка", "Пружинка"],
            ["Приставной шаг", "Шажок + Пружинка"],
            ["Боковой галоп", "Шажок + Пружинка + Прыжок"],
            ["Поскок", "Шажок + Прыжок (+ Пружинка)"],
            ["Ковырялочка без поскока", "Пружинка + Шажок"],
            ["Ковырялочка на поскоке", "+ Прыжок"],
        ],
        [Inches(5.2), Inches(5.6)],
    )
    add_textbox(s, Inches(1.2), Inches(6.5), Inches(10.8), Inches(0.4), "Вопрос детям: «Кто помогает выполнить это движение?» → выставили кукол → попробовали", size=14, color=MUTED, font="Calibri")
    footer(s, 6)

    # ---- 7 SPACE + BADGE ----
    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Разметка зала и Волшебная туфелька", "Пространство и мотивация тоже могут быть игрой")
    card(
        s,
        Inches(0.5),
        Inches(1.7),
        Inches(5.9),
        Inches(4.6),
        TEAL,
        "Танцевальная карусель",
        [
            "★ звёздочки / домики пар",
            "★ своё место — меньше столкновений",
            "★ круг сохраняется легче",
            "★ экономия драгоценных минут",
            "",
            "Разметка учит пространство\nбез бесконечных словесных команд",
        ],
    )
    card(
        s,
        Inches(6.8),
        Inches(1.7),
        Inches(5.9),
        Inches(4.6),
        GOLD,
        "Копилка достижений",
        [
            "Туфелька — за успех в движении",
            "Значок — за попадание в музыку",
            "Значок — за выразительность",
            "«Знайка» — за верную схему героев",
            "",
            "Ребёнок видит свой рост,\nа не только замечания",
        ],
        title_color=INK,
        body_color=INK,
    )
    footer(s, 7)

    # ---- 8 ALBUM MAP ----
    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Карта Альбома путешествий", "От поляны — к Городу Танцев")
    pages = [
        ("Младшая", "Сказочная\nполяна", LEAF, "первые шаги\nи пружинка"),
        ("Средняя", "Бабушкина\nдеревня", SKY, "поскоки,\nплаточек"),
        ("Старшая", "Школа\nМагистра", CORAL, "осознание\nи точность"),
        ("Подготовит.", "Город\nТанцев", GOLD, "полька,\nвальс, бал"),
    ]
    x = 0.7
    for i, (age, place, col, sense) in enumerate(pages):
        rounded(s, Inches(x), Inches(2.0), Inches(2.7), Inches(4.2), col)
        add_textbox(s, Inches(x + 0.1), Inches(2.25), Inches(2.5), Inches(0.4), age, size=14, bold=True, color=WHITE, align=PP_ALIGN.CENTER, font="Calibri")
        add_textbox(s, Inches(x + 0.1), Inches(2.9), Inches(2.5), Inches(1.0), place, size=22, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        add_textbox(s, Inches(x + 0.15), Inches(4.3), Inches(2.4), Inches(1.2), sense, size=15, color=WHITE, align=PP_ALIGN.CENTER, font="Calibri")
        if i < 3:
            add_textbox(s, Inches(x + 2.55), Inches(3.6), Inches(0.5), Inches(0.4), "→", size=28, bold=True, color=TEAL_DEEP, align=PP_ALIGN.CENTER)
        x += 3.15
    footer(s, 8)

    # ---- 9 JUNIOR ----
    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Младшая группа · Сказочная поляна", "Образ ведёт за собой движение")
    table(
        s,
        Inches(0.6),
        Inches(1.6),
        Inches(12.0),
        [
            ["Образ", "Движение", "Герой"],
            ["Тропинка", "спокойный / бодрый шаг", "Шажок"],
            ["Бабочки", "пружинка", "Пружинка"],
            ["Зайчик", "прыжки на двух", "Прыжок"],
            ["Машина / лошадка", "топотушки / галопчик", "Шажок + Прыжок"],
            ["Солнышко", "носок → пятка (+ пружинка)", "Пружинка"],
            ["Дождик / цветочки", "бег, притопы, фонарики, кружение", "Пружинка"],
        ],
        [Inches(3.2), Inches(5.2), Inches(3.6)],
    )
    rounded(s, Inches(0.6), Inches(6.35), Inches(12.0), Inches(0.55), SAND)
    add_textbox(s, Inches(0.8), Inches(6.42), Inches(11.6), Inches(0.4), "Приём: забыли пружинку → Пружинка «отвернулась» → пригласили снова → движение с пружинкой", size=14, bold=True, color=TEAL_DEEP, font="Calibri")
    footer(s, 9)

    # ---- 10 MIDDLE ----
    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Средняя группа · Бабушкина деревня", "Мягкость, поскок, народный колорит")
    left_items = [
        "Кошечка → мягкий шаг",
        "Дорожка → бодрый шаг",
        "+ Прыжок → лёгкие поскоки",
        "Лошадка → прямой галоп",
        "Берёзка → хороводный шаг",
        "Платочек → передача, кружение",
        "У берёзки → носок–пятка, притопы, «тарелочки»",
    ]
    card(s, Inches(0.5), Inches(1.6), Inches(6.2), Inches(5.0), SKY, "Маршрут страницы", left_items)
    card(
        s,
        Inches(7.1),
        Inches(1.6),
        Inches(5.6),
        Inches(5.0),
        TEAL,
        "Секрет поскока",
        [
            "Шажок + Пружинка = шаг",
            "",
            "+ Прыжок = поскок / динамика",
            "",
            "Дети сами собирают схему",
            "и понимают, кого «позвать»",
            "",
            "Страница готовит к парности\nи народным элементам",
        ],
    )
    footer(s, 10)

    # ---- 11 RIGHT/LEFT ----
    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Правая и левая — через «волшебство»", "Ленточки сильнее абстрактной лекции")
    # two scenes
    rounded(s, Inches(0.5), Inches(1.7), Inches(5.9), Inches(3.6), SAND)
    add_textbox(s, Inches(0.7), Inches(1.9), Inches(5.5), Inches(0.4), "1. Стоим рядом", size=18, bold=True, color=TEAL_DEEP)
    add_lines(
        s,
        Inches(0.7),
        Inches(2.5),
        Inches(5.5),
        Inches(2.5),
        [
            "Мальчик и девочка бок о бок",
            "Яркая лента на правой ноге у обоих",
            "Видно: правые — с одной стороны",
        ],
        size=16,
    )
    rounded(s, Inches(6.9), Inches(1.7), Inches(5.9), Inches(3.6), TEAL)
    add_textbox(s, Inches(7.1), Inches(1.9), Inches(5.5), Inches(0.4), "2. Встали лицом друг к другу", size=18, bold=True, color=WHITE)
    add_lines(
        s,
        Inches(7.1),
        Inches(2.5),
        Inches(5.5),
        Inches(2.5),
        [
            "«Волшебная палочка»!",
            "Ленты оказались с разных сторон",
            "В паре правые/левые — напротив",
        ],
        size=16,
        color=WHITE,
    )
    add_textbox(
        s,
        Inches(0.5),
        Inches(5.6),
        Inches(12.3),
        Inches(1.0),
        "Если начать с одной стороны лицом друг к другу — «как барашки на бревне» или «машинки, которые не разъедутся».\nНачать с разных сторон — каждой ножке свободно, красиво и удобно.",
        size=15,
        color=INK,
        font="Calibri",
    )
    footer(s, 11)

    # ---- 12 SENIOR ----
    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Старшая группа · Школа Магистра", "Игра сохраняется — появляется урок")
    blocks = [
        ("Вход", "ветер-ветерок,\nстремительный шаг", CORAL),
        ("Поскоки", "лёгкий\nи сильный", SKY),
        ("Сад", "всадники,\nобразные руки", LEAF),
        ("Балетный\nакцент", "приставной\nШажок+Пружинка", TEAL),
        ("Народный\nкласс", "ковырялочка\nбез поскока", GOLD),
        ("Финал", "хлопки-браво\n→ Город Танцев", ROSE),
    ]
    x = 0.45
    for title, body, col in blocks:
        rounded(s, Inches(x), Inches(2.0), Inches(2.0), Inches(4.3), col)
        add_textbox(s, Inches(x + 0.08), Inches(2.3), Inches(1.85), Inches(1.0), title, size=15, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        add_textbox(s, Inches(x + 0.08), Inches(3.6), Inches(1.85), Inches(2.0), body, size=13, color=WHITE, align=PP_ALIGN.CENTER, font="Calibri")
        x += 2.15
    footer(s, 12)

    # ---- 13 PREP ----
    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Подготовительная · Город Танцев", "Сначала движения — потом бал")
    table(
        s,
        Inches(0.6),
        Inches(1.55),
        Inches(12.0),
        [
            ["Уже знали", "Собираем дальше"],
            ["Приставной шаг", "+ Прыжок = боковой галоп"],
            ["Хороводный шаг", "руки / точка / переменный"],
            ["Пружинящий шаг", "припадание"],
            ["Ковырялочка без поскока", "ковырялочка на поскоке"],
            ["Весёлые ножки", "метелочка, козлик, крылья"],
            ["Обычные хлопки", "синкопированные хлопки"],
        ],
        [Inches(5.5), Inches(6.5)],
    )
    rounded(s, Inches(0.6), Inches(6.2), Inches(12.0), Inches(0.7), GOLD)
    add_textbox(s, Inches(0.8), Inches(6.32), Inches(11.6), Inches(0.5), "Рецепт Полечки:  Прыжок + Пружинка + два шага Шажка  =  Полька готова!", size=18, bold=True, color=INK, align=PP_ALIGN.CENTER)
    footer(s, 13)

    # ---- 14 ALGORITHM ----
    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Алгоритм ведения страницы", "8–10 минут живого обучения")
    steps = [
        "Открыть страницу / назвать место",
        "Вызвать героя",
        "Короткий сюжетный мостик",
        "Показ + проба",
        "Поисковый вопрос / схема",
        "Повтор в образе",
        "Коррекция через сюжет",
        "Маленький успех",
        "Мостик дальше / в танец",
    ]
    for i, t in enumerate(steps):
        row, col = divmod(i, 3)
        x = 0.55 + col * 4.2
        y = 1.7 + row * 1.65
        rounded(s, Inches(x), Inches(y), Inches(3.9), Inches(1.4), TEAL if i % 2 == 0 else LEAF)
        add_textbox(s, Inches(x + 0.15), Inches(y + 0.2), Inches(0.6), Inches(0.5), f"{i+1}", size=24, bold=True, color=GOLD)
        add_textbox(s, Inches(x + 0.75), Inches(y + 0.35), Inches(2.9), Inches(0.8), t, size=15, bold=True, color=WHITE)
    footer(s, 14)

    # ---- 15 DO / DON'T ----
    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Делать  /  Не делать", "Чтобы игра не съела обучение")
    card(
        s,
        Inches(0.5),
        Inches(1.7),
        Inches(5.9),
        Inches(4.8),
        LEAF,
        "Делать",
        [
            "✓ один новый акцент за раз",
            "✓ герой до движения",
            "✓ править сюжетом",
            "✓ держать музыку",
            "✓ давать видимый успех",
            "✓ оставлять мостик в танец",
        ],
    )
    card(
        s,
        Inches(6.9),
        Inches(1.7),
        Inches(5.9),
        Inches(4.8),
        CORAL,
        "Не делать",
        [
            "✗ валить всю страницу без дозировки",
            "✗ термин без образа",
            "✗ стыдить при всех",
            "✗ превращать в спектакль без навыка",
            "✗ забывать безопасность пространства",
            "✗ сравнивать детей друг с другом",
        ],
    )
    footer(s, 15)

    # ---- 16 STUDENT BLANK ----
    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Бланк «Страница альбома»", "Спроектируйте свою игровую страницу")
    table(
        s,
        Inches(0.8),
        Inches(1.55),
        Inches(11.6),
        [
            ["Поле", "Ваш ответ"],
            ["Возраст", ""],
            ["Движение", ""],
            ["Герои на схеме", ""],
            ["Игровой сюжет / образ", ""],
            ["Текст ведущего (2–4 фразы)", ""],
            ["Как снять страх ошибки", ""],
            ["Как показать успех", ""],
            ["Мостик в танец", ""],
        ],
        [Inches(4.5), Inches(7.1)],
    )
    footer(s, 16)

    # ---- 17 CHECKLIST ----
    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Чек-лист готового приёма", "Перед тем как считать метод рабочим")
    checks = [
        "Есть образ/сюжет, а не только термин?",
        "Герои реально объясняют состав движения?",
        "Есть поисковый вопрос, а не одна команда?",
        "Пространство размечено / ясно?",
        "Ошибка исправляется без стыда?",
        "Успех ребёнку виден (туфелька/факт)?",
        "Есть мостик в танец/композицию?",
        "Игра не съела обучение?",
    ]
    for i, q in enumerate(checks):
        y = 1.55 + i * 0.6
        rounded(s, Inches(0.7), Inches(y), Inches(0.45), Inches(0.45), TEAL if i % 2 == 0 else GOLD)
        add_textbox(s, Inches(0.7), Inches(y + 0.05), Inches(0.45), Inches(0.35), "☐", size=16, color=WHITE, align=PP_ALIGN.CENTER)
        add_textbox(s, Inches(1.35), Inches(y + 0.05), Inches(11.2), Inches(0.4), q, size=16, color=INK, font="Calibri")
    footer(s, 17)

    # ---- 18 FINALE ----
    s = prs.slides.add_slide(blank)
    bg(s, TEAL_DEEP)
    oval(s, Inches(-1.0), Inches(5.0), Inches(3.5), Inches(3.5), TEAL)
    oval(s, Inches(11.0), Inches(-1.0), Inches(3.5), Inches(3.5), CORAL)
    add_textbox(s, Inches(1.0), Inches(1.6), Inches(11.3), Inches(0.5), "Итог путешествия", size=18, color=GOLD, align=PP_ALIGN.CENTER, font="Calibri")
    add_textbox(
        s,
        Inches(1.0),
        Inches(2.3),
        Inches(11.3),
        Inches(1.8),
        "Не страх и повтор уговаривают ребёнка двигаться —\nа понятная игра, в которой можно ошибиться,\nпопробовать снова и увидеть свою туфельку успеха.",
        size=24,
        bold=True,
        color=WHITE,
        align=PP_ALIGN.CENTER,
    )
    add_textbox(
        s,
        Inches(1.0),
        Inches(4.5),
        Inches(11.3),
        Inches(0.6),
        "Пружинка + Шажок + Прыжок = ключ к осознанному движению",
        size=18,
        color=SAND,
        align=PP_ALIGN.CENTER,
    )
    add_textbox(
        s,
        Inches(1.0),
        Inches(5.5),
        Inches(11.3),
        Inches(0.8),
        "ДЗ: одна полная страница альбома на 8–10 минут\nдля выбранной группы — с текстом ведущего, схемой героев и мостиком в танец",
        size=14,
        color=SOFT,
        align=PP_ALIGN.CENTER,
        font="Calibri",
    )
    add_textbox(s, Inches(1.0), Inches(6.6), Inches(11.3), Inches(0.35), "Занятие 17 · готовая презентация", size=12, color=MUTED, align=PP_ALIGN.CENTER, font="Calibri")

    prs.save(str(OUT))
    ART.write_bytes(OUT.read_bytes())
    print(f"OK {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    build()
