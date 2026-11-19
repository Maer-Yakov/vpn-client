#!/usr/bin/env python3
"""Ready-to-show PowerPoint for lesson 8 — singing ages 3–4."""

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

INK = RGBColor(0x1E, 0x2F, 0x3A)
CREAM = RGBColor(0xF7, 0xFA, 0xFC)
SAND = RGBColor(0xE8, 0xF0, 0xF4)
TEAL = RGBColor(0x2A, 0x7A, 0x8C)
TEAL_DEEP = RGBColor(0x1A, 0x5A, 0x6A)
CORAL = RGBColor(0xD4, 0x7A, 0x6A)
GOLD = RGBColor(0xC9, 0xA2, 0x4E)
LEAF = RGBColor(0x5A, 0x8F, 0x7B)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
MUTED = RGBColor(0x5A, 0x6E, 0x78)
SOFT = RGBColor(0xE4, 0xF0, 0xF3)
RED_SOFT = RGBColor(0xC4, 0x5C, 0x5C)
GREEN_SOFT = RGBColor(0x4A, 0x9A, 0x7A)

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "zanyatie-08-assets"
OUT = ROOT / "zanyatie-08-prezentaciya.pptx"
ART = Path("/opt/cursor/artifacts/zanyatie-08-prezentaciya.pptx")

IMG = {
    1: "z08-01-title.jpg",
    2: "z08-02-doors.jpg",
    3: "z08-03-ritual.jpg",
    4: "z08-04-mindmap.jpg",
    5: "z08-05-spheres.jpg",
    6: "z08-06-range.jpg",
    7: "z08-07-traffic.jpg",
    8: "z08-08-stairs.jpg",
    9: "z08-09-show.jpg",
    10: "z08-10-stages.jpg",
    11: "z08-11-stations.jpg",
    12: "z08-12-soft.jpg",
    13: "z08-13-rooster.jpg",
    14: "z08-14-exercises.jpg",
    15: "z08-15-repertoire.jpg",
    16: "z08-16-training.jpg",
    17: "z08-17-checklist.jpg",
    18: "z08-18-finale.jpg",
}


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


def add_lines(slide, left, top, width, height, lines, *, size=14, color=INK, spacing=4):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        p.space_after = Pt(spacing)
        set_run(p, line, size=size, color=color)
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
        slide, Inches(0.4), Inches(7.15), Inches(12), Inches(0.3),
        f"Занятие 8 · Пение 3–4 лет · Мягкий показ · Короткая фраза · Пауза   {n}/{total}",
        size=11, color=MUTED, font="Calibri",
    )


def accent_bar(slide):
    rect(slide, Inches(0), Inches(0), Inches(0.18), Inches(7.5), TEAL)


def title_block(slide, title, subtitle=None):
    accent_bar(slide)
    add_textbox(slide, Inches(0.45), Inches(0.18), Inches(12.5), Inches(0.55), title, size=24, bold=True, color=TEAL_DEEP)
    if subtitle:
        add_textbox(slide, Inches(0.45), Inches(0.72), Inches(12.5), Inches(0.32), subtitle, size=14, color=MUTED, font="Calibri")


def picture(slide, n, left, top, width, height):
    return slide.shapes.add_picture(str(ASSETS / IMG[n]), left, top, width=width, height=height)


def table(slide, left, top, width, rows, col_widths, *, row_h=0.38):
    cols = len(rows[0])
    shape = slide.shapes.add_table(len(rows), cols, left, top, width, Inches(row_h * len(rows)))
    tbl = shape.table
    for i, w in enumerate(col_widths):
        tbl.columns[i].width = w
    for r, row in enumerate(rows):
        for c, val in enumerate(row):
            cell = tbl.cell(r, c)
            cell.text = ""
            p = cell.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.LEFT
            set_run(p, val, size=11 if r else 12, bold=(r == 0), color=WHITE if r == 0 else INK, font="Calibri")
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            fill = cell.fill
            fill.solid()
            fill.fore_color.rgb = TEAL if r == 0 else (SOFT if r % 2 else WHITE)
    return shape


def card(slide, left, top, width, height, fill, title, body_lines):
    rounded(slide, left, top, width, height, fill)
    add_textbox(slide, left + Inches(0.15), top + Inches(0.1), width - Inches(0.25), Inches(0.35), title, size=14, bold=True, color=WHITE)
    add_lines(slide, left + Inches(0.15), top + Inches(0.45), width - Inches(0.25), height - Inches(0.55), body_lines, size=12, color=WHITE, spacing=3)


def build():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank = prs.slide_layouts[6]

    # 1
    s = prs.slides.add_slide(blank)
    bg(s, TEAL_DEEP)
    oval(s, Inches(-0.8), Inches(-1.0), Inches(3.0), Inches(3.0), TEAL)
    oval(s, Inches(11.2), Inches(5.2), Inches(2.8), Inches(2.8), CORAL)
    add_textbox(s, Inches(0.5), Inches(0.35), Inches(6.2), Inches(0.35), "ЗАНЯТИЕ 8 · МОДУЛЬ II", size=14, color=GOLD, font="Calibri")
    add_textbox(s, Inches(0.5), Inches(0.85), Inches(6.2), Inches(1.5), "Пение с детьми\nмладшего дошкольного\nвозраста", size=28, bold=True, color=WHITE)
    add_textbox(s, Inches(0.5), Inches(2.7), Inches(6.2), Inches(0.4), "Не хор «любой ценой» — желание подхватить", size=15, color=SAND, font="Calibri")
    add_textbox(s, Inches(0.5), Inches(3.3), Inches(6.2), Inches(0.7), "услышал → подхватил рядом\nсо взрослым → повторил фразу", size=14, color=WHITE, font="Calibri")
    picture(s, 1, Inches(7.0), Inches(0.6), Inches(5.8), Inches(5.5))
    add_textbox(s, Inches(0.5), Inches(6.5), Inches(12), Inches(0.3), "Ветлугина · Дзержинская · Метлов · «Ладушки»", size=12, color=SAND, font="Calibri")

    # 2
    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Чем пение в 3–4 года особенное", "Подхватывать песню — не сдавать номер")
    picture(s, 2, Inches(0.45), Inches(1.2), Inches(6.6), Inches(4.8))
    table(s, Inches(7.3), Inches(1.2), Inches(5.5), [
        ["3–4 года", "Позже (5–7)"],
        ["узкий диапазон", "диапазон шире"],
        ["показ педагога обязателен", "больше самостоятельности"],
        ["игра и образ важнее «нот»", "точнее интонация"],
        ["риск крика высок", "лучше держат мягкий звук"],
    ], [Inches(2.7), Inches(2.8)], row_h=0.55)
    add_textbox(s, Inches(7.3), Inches(5.1), Inches(5.5), Inches(1.0), "Важнее желание петь,\nчем идеальная нота.", size=15, bold=True, color=TEAL_DEEP)
    footer(s, 2)

    # 3
    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Чему учимся сегодня", "Цель занятия для студента")
    steps = [
        "Понять значение пения",
        "Увидеть особенности голоса 3–4 лет",
        "Сформулировать задачи обучения",
        "Освоить приёмы и этапы разучивания",
        "Подобрать упражнения",
        "Отобрать посильный репертуар",
    ]
    for i, t in enumerate(steps):
        y = Inches(1.2 + i * 0.7)
        oval(s, Inches(0.5), y, Inches(0.45), Inches(0.45), TEAL if i % 2 == 0 else LEAF)
        add_textbox(s, Inches(0.5), y + Inches(0.07), Inches(0.45), Inches(0.3), str(i + 1), size=13, bold=True, color=WHITE, align=PP_ALIGN.CENTER, font="Calibri")
        add_textbox(s, Inches(1.15), y + Inches(0.07), Inches(5.8), Inches(0.4), t, size=15, color=INK)
    picture(s, 3, Inches(7.3), Inches(1.2), Inches(5.5), Inches(5.2))
    footer(s, 3)

    # 4
    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Карта темы", "От значения пения — к репертуару")
    picture(s, 4, Inches(0.4), Inches(1.15), Inches(8.4), Inches(5.5))
    table(s, Inches(9.0), Inches(1.3), Inches(3.9), [
        ["Слайды", "Блок"], ["5–11", "теория"], ["12–16", "практика"], ["17–18", "чек-лист и итог"],
    ], [Inches(1.5), Inches(2.4)], row_h=0.55)
    add_lines(s, Inches(9.0), Inches(4.0), Inches(3.9), Inches(2.5), [
        "1. Значение пения", "2. Возраст 3–4 лет", "3. Задачи обучения",
        "4. Приёмы и этапы", "5. Упражнения", "6. Репертуар",
    ], size=14, color=TEAL_DEEP)
    footer(s, 4)

    # 5
    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Значение пения в развитии ребёнка", "Мост между слухом, речью и игрой")
    picture(s, 5, Inches(0.4), Inches(1.15), Inches(6.8), Inches(4.5))
    table(s, Inches(7.4), Inches(1.15), Inches(5.5), [
        ["Сфера", "Что развивается"],
        ["Слух", "высота, темп, динамика"],
        ["Речь", "словарь, дикция"],
        ["Дыхание", "спокойный выдох"],
        ["Эмоции", "радость через голос"],
        ["Социальность", "петь вместе"],
        ["Память", "короткая мелодия"],
    ], [Inches(2.2), Inches(3.3)], row_h=0.48)
    footer(s, 5)

    # 6
    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Возрастные особенности 3–4 лет", "Детский голос и поведение в пении")
    picture(s, 6, Inches(0.4), Inches(1.15), Inches(6.6), Inches(4.6))
    table(s, Inches(7.2), Inches(1.15), Inches(5.7), [
        ["Особенность", "Для педагога"],
        ["Диапазон узкий", "без широких скачков"],
        ["Фраза короткая", "1–2 строки"],
        ["Интонация неточна", "показ и повтор"],
        ["Внимание короткое", "короткий куплет"],
        ["Любят образ", "жест / игрушка"],
        ["Легко форсируют", "мягкий звук, паузы"],
    ], [Inches(2.7), Inches(3.0)], row_h=0.48)
    footer(s, 6)

    # 7
    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Можно и нельзя для голоса", "Границы бережности")
    picture(s, 7, Inches(0.4), Inches(1.15), Inches(5.8), Inches(5.2))
    card(s, Inches(6.5), Inches(1.2), Inches(3.2), Inches(4.6), GREEN_SOFT, "Можно ✓", [
        "мягкий естественный звук", "петь вместе со взрослым",
        "короткая песня с повтором", "жест и игрушка-образ", "удобная поза",
    ])
    card(s, Inches(9.9), Inches(1.2), Inches(3.0), Inches(4.6), RED_SOFT, "Нельзя ✕", [
        "крик, давить горлом", "соло «как на сцене»",
        "длинный куплетный номер", "долбить без паузы", "сложная хореография",
    ])
    footer(s, 7)

    # 8
    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Задачи обучения пению", "Что проверяем в младшей группе")
    picture(s, 8, Inches(0.4), Inches(1.15), Inches(7.0), Inches(5.0))
    add_lines(s, Inches(7.7), Inches(1.3), Inches(5.2), Inches(5.0), [
        "1. Желание петь вместе",
        "2. Мягкое звукообразование",
        "3. Слушать начало и конец фразы",
        "4. Интонация через показ",
        "5. Слово + мелодия + жест",
        "6. Небольшой посильный репертуар",
        "7. Беречь голос: паузы",
        "",
        "желание → мягкий звук",
        "→ фраза → репертуар",
    ], size=15, color=TEAL_DEEP)
    footer(s, 8)

    # 9
    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Методические приёмы", "Как вести пение в 3–4 года")
    picture(s, 9, Inches(0.4), Inches(1.15), Inches(6.8), Inches(4.8))
    table(s, Inches(7.4), Inches(1.15), Inches(5.5), [
        ["Приём", "Как"],
        ["Выразительный показ", "лицом к детям"],
        ["Совместное пение", "педагог ведёт"],
        ["Игровой образ", "петушок / кукла"],
        ["Жест / платочек", "опора внимания"],
        ["Вопрос–ответ", "короткая фраза"],
        ["Повтор фразы", "2–4 раза + пауза"],
    ], [Inches(2.8), Inches(2.7)], row_h=0.48)
    footer(s, 9)

    # 10
    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Этапы разучивания песни", "От интереса — к игровому закреплению")
    picture(s, 10, Inches(0.4), Inches(1.15), Inches(7.2), Inches(5.0))
    table(s, Inches(7.85), Inches(1.15), Inches(5.0), [
        ["Этап", "Суть"],
        ["1. Интерес", "игрушка / вопрос"],
        ["2. Показ", "педагог поёт"],
        ["3. Смысл", "2–3 вопроса"],
        ["4. Фразы", "короткий повтор"],
        ["5. Вместе", "соединение"],
        ["6. Игра", "жест / другой день"],
        ["7. Стоп", "отдых голоса"],
    ], [Inches(2.0), Inches(3.0)], row_h=0.45)
    footer(s, 10)

    # 11
    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Обзор практики", "Упражнения и репертуар")
    picture(s, 11, Inches(0.4), Inches(1.15), Inches(8.2), Inches(5.3))
    add_lines(s, Inches(8.9), Inches(1.5), Inches(4.0), Inches(4.5), [
        "Блок 1. Упражнения",
        "дыхание · атака · слух",
        "дикция · динамика",
        "",
        "Блок 2. Репертуар",
        "диапазон · длина · текст",
        "образ · темп",
        "",
        "Вердикт:",
        "беру / не беру",
    ], size=15, color=TEAL_DEEP)
    footer(s, 11)

    # 12
    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Практика 1. Мягкий звук vs форсирование", "Первый инструмент — собственный голос")
    picture(s, 12, Inches(0.4), Inches(1.15), Inches(7.0), Inches(5.0))
    table(s, Inches(7.6), Inches(1.15), Inches(5.3), [
        ["Признак", "Мягко", "Форс"],
        ["Лицо", "свободно", "напряжено"],
        ["Звук", "льётся", "давит"],
        ["Дыхание", "спокойно", "судорожно"],
        ["Ребёнку", "заражает", "учит кричать"],
    ], [Inches(1.6), Inches(1.8), Inches(1.9)], row_h=0.55)
    add_textbox(s, Inches(7.6), Inches(5.0), Inches(5.3), Inches(1.0), "тихо «мм» → крик (стоп!) → снова мягко", size=14, bold=True, color=TEAL_DEEP)
    footer(s, 12)

    # 13
    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Практика 2. Этапы на конкретной песне", "Модель разучивания")
    picture(s, 13, Inches(0.4), Inches(1.15), Inches(7.0), Inches(5.0))
    table(s, Inches(7.6), Inches(1.15), Inches(5.3), [
        ["Этап", "Действие"],
        ["Интерес", "игрушка / вопрос"],
        ["Показ", "поёт целиком"],
        ["Смысл", "2–3 вопроса"],
        ["Фразы", "повтор коротко"],
        ["Вместе", "соединение"],
        ["Игра", "жест «клювик»"],
        ["Стоп", "похвала, пауза"],
    ], [Inches(1.8), Inches(3.5)], row_h=0.45)
    footer(s, 13)

    # 14
    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Практика 3. Банк упражнений", "20–40 секунд — одна задача")
    picture(s, 14, Inches(0.4), Inches(1.15), Inches(7.0), Inches(5.0))
    table(s, Inches(7.6), Inches(1.15), Inches(5.3), [
        ["Навык", "Упражнение"],
        ["Дыхание", "платочек / одуванчик"],
        ["Мягкая атака", "«ммм» / «ау»"],
        ["Интонация", "повтор высоты"],
        ["Дикция", "потешка шёпотом→голос"],
        ["Динамика", "тихо — чуть громче"],
        ["Слух", "рука на конце песни"],
    ], [Inches(2.2), Inches(3.1)], row_h=0.5)
    footer(s, 14)

    # 15
    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Практика 4. Подбор репертуара", "Песня — педагогическое решение")
    picture(s, 15, Inches(0.4), Inches(1.15), Inches(6.8), Inches(4.8))
    card(s, Inches(7.4), Inches(1.2), Inches(2.7), Inches(4.5), LEAF, "Беру ✓", [
        "короткая с повтором", "близкий образ", "мягкая мелодия", "понятный текст", "в диапазоне",
    ])
    card(s, Inches(10.3), Inches(1.2), Inches(2.6), Inches(4.5), RED_SOFT, "Не беру ✕", [
        "длинный шлягер", "взрослый текст", "широкие скачки", "высокий пик", "страшилки",
    ])
    footer(s, 15)

    # 16
    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Мини-тренинг студента", "90–100 секунд мини-пения")
    picture(s, 16, Inches(0.4), Inches(1.15), Inches(7.0), Inches(5.0))
    table(s, Inches(7.6), Inches(1.15), Inches(5.3), [
        ["Шаг", "Действие"],
        ["1", "упражнение 20–30 сек"],
        ["2", "показ 1 фразы + повтор"],
        ["3", "можно + нельзя"],
        ["4", "мягкий стоп"],
    ], [Inches(1.0), Inches(4.3)], row_h=0.48)
    card(s, Inches(7.6), Inches(4.0), Inches(5.3), Inches(2.3), TEAL, "Рубрика Да/Нет", [
        "образ · мягкость · краткость", "повтор · пауза · без крика", "понятно, зачем детям 3–4 лет",
    ])
    footer(s, 16)

    # 17
    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Чек-лист пения в младшей группе", "Перед репертуаром средней группы")
    picture(s, 17, Inches(0.4), Inches(1.15), Inches(6.5), Inches(5.0))
    checks = [
        "1. Значение пения для 3–4 лет",
        "2. Особенности голоса и риск крика",
        "3. Задачи обучения пению",
        "4. Показ и совместное пение",
        "5. Этапы: интерес → фразы → стоп",
        "6. Банк коротких упражнений",
        "7. Посильная песня",
        "8. Паузы обязательны",
    ]
    for i, t in enumerate(checks):
        y = Inches(1.2 + i * 0.55)
        rounded(s, Inches(7.1), y, Inches(5.8), Inches(0.48), SOFT if i % 2 == 0 else SAND)
        add_textbox(s, Inches(7.3), y + Inches(0.08), Inches(5.4), Inches(0.35), t, size=13, color=INK, font="Calibri")
    add_textbox(s, Inches(0.5), Inches(6.3), Inches(12), Inches(0.4), "МЯГКИЙ ПОКАЗ  ↔  КОРОТКАЯ ФРАЗА  ↔  ПАУЗА", size=16, bold=True, color=TEAL_DEEP, align=PP_ALIGN.CENTER)
    footer(s, 17)

    # 18
    s = prs.slides.add_slide(blank)
    bg(s, TEAL_DEEP)
    oval(s, Inches(-0.5), Inches(-0.6), Inches(2.5), Inches(2.5), TEAL)
    oval(s, Inches(11.5), Inches(5.5), Inches(2.5), Inches(2.5), CORAL)
    add_textbox(s, Inches(0.5), Inches(0.3), Inches(6.0), Inches(0.35), "Итог + домашнее задание", size=14, color=GOLD, font="Calibri")
    add_textbox(s, Inches(0.5), Inches(0.75), Inches(6.0), Inches(0.9), "Пение начинается\nс желания подхватить", size=26, bold=True, color=WHITE)
    add_textbox(s, Inches(0.5), Inches(1.9), Inches(6.0), Inches(0.9), "Мягкий голос педагога.\nКороткая понятная песня.\nЭтапы без спешки.", size=15, color=SAND, font="Calibri")
    picture(s, 18, Inches(6.8), Inches(0.4), Inches(6.1), Inches(4.0))
    hw = [
        ("1. Таблица", "значение · голос 3–4\nзадачи · этапы\nупражнения · репертуар"),
        ("2. Разбор песни", "этапы + дозировка\nв минутах"),
        ("3. Мини-эссе", "почему мягкий показ\nважнее громкого давления"),
    ]
    for i, (t, b) in enumerate(hw):
        rounded(s, Inches(0.4 + i * 4.25), Inches(4.7), Inches(4.0), Inches(1.7), WHITE)
        add_textbox(s, Inches(0.55 + i * 4.25), Inches(4.85), Inches(3.7), Inches(0.35), t, size=14, bold=True, color=TEAL_DEEP)
        add_lines(s, Inches(0.55 + i * 4.25), Inches(5.3), Inches(3.7), Inches(0.9), b.split("\n"), size=12, color=INK, spacing=2)
    add_textbox(s, Inches(0.5), Inches(6.7), Inches(12), Inches(0.3), "Берегите детский голос — и пение начнётся с правильного этажа.", size=13, color=GOLD, align=PP_ALIGN.CENTER, font="Calibri")

    prs.save(str(OUT))
    ART.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(ART))
    print(f"OK pptx={OUT} images={len(IMG)}")


if __name__ == "__main__":
    build()
