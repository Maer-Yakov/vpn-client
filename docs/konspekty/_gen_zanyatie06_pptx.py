#!/usr/bin/env python3
"""Ready-to-show PowerPoint for lesson 6 — with planned illustrations."""

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
SKY = RGBColor(0x5B, 0x9B, 0xB8)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
MUTED = RGBColor(0x5A, 0x6E, 0x78)
SOFT = RGBColor(0xE4, 0xF0, 0xF3)
RED_SOFT = RGBColor(0xC4, 0x5C, 0x5C)
GREEN_SOFT = RGBColor(0x4A, 0x9A, 0x7A)

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "zanyatie-06-assets"
OUT = ROOT / "zanyatie-06-prezentaciya.pptx"
ART = Path("/opt/cursor/artifacts/zanyatie-06-prezentaciya.pptx")

IMG = {
    1: "z06-01-title.jpg",
    2: "z06-02-doors.jpg",
    3: "z06-03-ritual.jpg",
    4: "z06-04-mindmap.jpg",
    5: "z06-05-voice-waves.jpg",
    6: "z06-06-intonations.jpg",
    7: "z06-07-genres.jpg",
    8: "z06-08-knees.jpg",
    9: "z06-09-contact.jpg",
    10: "z06-10-traffic.jpg",
    11: "z06-11-stations.jpg",
    12: "z06-12-arms.jpg",
    13: "z06-13-ladushki.jpg",
    14: "z06-14-pendulum.jpg",
    15: "z06-15-rattle.jpg",
    16: "z06-16-training.jpg",
    17: "z06-17-checklist.jpg",
    18: "z06-18-finale.jpg",
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
        slide,
        Inches(0.4),
        Inches(7.15),
        Inches(12),
        Inches(0.3),
        f"Занятие 6 · Ритм 0–1,5 лет · Голос · Касание · Пауза   {n}/{total}",
        size=11,
        color=MUTED,
        font="Calibri",
    )


def accent_bar(slide):
    rect(slide, Inches(0), Inches(0), Inches(0.18), Inches(7.5), TEAL)


def title_block(slide, title, subtitle=None):
    accent_bar(slide)
    add_textbox(slide, Inches(0.45), Inches(0.18), Inches(12.5), Inches(0.55), title, size=24, bold=True, color=TEAL_DEEP)
    if subtitle:
        add_textbox(slide, Inches(0.45), Inches(0.72), Inches(12.5), Inches(0.32), subtitle, size=14, color=MUTED, font="Calibri")


def picture(slide, n, left, top, width, height):
    path = ASSETS / IMG[n]
    return slide.shapes.add_picture(str(path), left, top, width=width, height=height)


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
            if r == 0:
                fill.fore_color.rgb = TEAL
            elif r % 2:
                fill.fore_color.rgb = SOFT
            else:
                fill.fore_color.rgb = WHITE
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

    # ---- 1 TITLE ----
    s = prs.slides.add_slide(blank)
    bg(s, TEAL_DEEP)
    oval(s, Inches(-0.8), Inches(-1.0), Inches(3.0), Inches(3.0), TEAL)
    oval(s, Inches(11.2), Inches(5.2), Inches(2.8), Inches(2.8), CORAL)
    add_textbox(s, Inches(0.5), Inches(0.35), Inches(6.2), Inches(0.35), "ЗАНЯТИЕ 6 · МОДУЛЬ II", size=14, color=GOLD, font="Calibri")
    add_textbox(s, Inches(0.5), Inches(0.85), Inches(6.2), Inches(1.4), "Ритмическое развитие детей\nот рождения до 1,5 лет", size=30, bold=True, color=WHITE)
    add_textbox(s, Inches(0.5), Inches(2.5), Inches(6.2), Inches(0.4), "Не танец по правилам — телесный диалог", size=16, color=SAND, font="Calibri")
    add_textbox(s, Inches(0.5), Inches(3.15), Inches(6.2), Inches(0.7), "услышал → почувствовал рядом\nсо взрослым → оживился / успокоился", size=14, color=WHITE, font="Calibri")
    picture(s, 1, Inches(7.0), Inches(0.6), Inches(5.8), Inches(5.5))
    add_textbox(s, Inches(0.5), Inches(6.5), Inches(12), Inches(0.3), "Бабаджан · Ветлугина · Картушина «Забавы для малышей»", size=12, color=SAND, font="Calibri")

    # ---- 2 ----
    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Чем этот возраст особенный", "Самый ранний этаж ритмики")
    picture(s, 2, Inches(0.45), Inches(1.2), Inches(6.6), Inches(4.8))
    table(
        s, Inches(7.3), Inches(1.2), Inches(5.5),
        [
            ["0–1,5 лет", "Позже (3–5+)"],
            ["совместное движение", "самостоятельность"],
            ["голос важнее колонки", "запись шире"],
            ["нет строя", "игровые правила"],
            ["контакт = главное", "контакт + задача"],
        ],
        [Inches(2.7), Inches(2.8)],
        row_h=0.55,
    )
    add_textbox(s, Inches(7.3), Inches(5.0), Inches(5.5), Inches(1.2), "Младенец не готовит номер —\nон учится быть в ритме рядом\nсо взрослым.", size=15, bold=True, color=TEAL_DEEP)
    footer(s, 2)

    # ---- 3 ----
    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Чему учимся сегодня", "Цель занятия для студента")
    steps = [
        "1. Понять слух и движение младенца",
        "2. Увидеть реакции на интонации",
        "3. Использовать колыбельные, потешки, пестушки",
        "4. Двигаться вместе со взрослым",
        "5. Держать телесный и эмоциональный контакт",
        "6. Провести мягкие игры и контрасты",
    ]
    for i, t in enumerate(steps):
        y = Inches(1.2 + i * 0.7)
        oval(s, Inches(0.5), y, Inches(0.45), Inches(0.45), TEAL if i % 2 == 0 else LEAF)
        add_textbox(s, Inches(0.5), y + Inches(0.07), Inches(0.45), Inches(0.3), str(i + 1), size=13, bold=True, color=WHITE, align=PP_ALIGN.CENTER, font="Calibri")
        add_textbox(s, Inches(1.15), y + Inches(0.07), Inches(5.8), Inches(0.4), t[3:], size=15, color=INK)
    picture(s, 3, Inches(7.3), Inches(1.2), Inches(5.5), Inches(5.2))
    footer(s, 3)

    # ---- 4 ----
    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Карта темы", "От слуха — к короткой забаве")
    picture(s, 4, Inches(0.4), Inches(1.15), Inches(8.4), Inches(5.5))
    table(
        s, Inches(9.0), Inches(1.3), Inches(3.9),
        [["Слайды", "Блок"], ["5–11", "теория"], ["12–16", "практика"], ["17–18", "чек-лист и итог"]],
        [Inches(1.5), Inches(2.4)],
        row_h=0.55,
    )
    add_lines(s, Inches(9.0), Inches(4.0), Inches(3.9), Inches(2.5), [
        "1. Слух и движение",
        "2. Интонации",
        "3. Колыбельная / потешка",
        "4. Вместе со взрослым",
        "5. Контакт",
        "6. Практика игр",
    ], size=14, color=TEAL_DEEP)
    footer(s, 4)

    # ---- 5 ----
    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Слуховое и двигательное восприятие", "Звук входит вместе с теплом рук")
    picture(s, 5, Inches(0.4), Inches(1.15), Inches(6.8), Inches(4.5))
    table(
        s, Inches(7.4), Inches(1.15), Inches(5.5),
        [
            ["Период", "Слух / движение"],
            ["Первые месяцы", "голос → общие реакции"],
            ["~полгода", "погремушка → оживление"],
            ["1–1,5 года", "сигналы → подражание"],
        ],
        [Inches(2.2), Inches(3.3)],
        row_h=0.55,
    )
    rounded(s, Inches(7.4), Inches(4.0), Inches(5.5), Inches(2.2), SAND)
    add_textbox(s, Inches(7.6), Inches(4.25), Inches(5.1), Inches(1.7), "голос / звук → реакция тела\n→ повтор в контакте\n→ привычный отклик\n\nДаём сенсорный опыт,\nа не комбинацию.", size=14, bold=True, color=TEAL_DEEP)
    footer(s, 5)

    # ---- 6 ----
    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Реакции на музыкальные интонации", "Интонация — эмоциональное лицо звука")
    picture(s, 6, Inches(0.4), Inches(1.15), Inches(6.6), Inches(4.6))
    table(
        s, Inches(7.2), Inches(1.15), Inches(5.7),
        [
            ["Интонация", "Реакция"],
            ["Мягкая певучая", "спокойствие"],
            ["Светлая игривая", "оживление"],
            ["Тихо / чуть громче", "внимание"],
            ["Резкая громкая ✕", "плач"],
        ],
        [Inches(2.9), Inches(2.8)],
        row_h=0.5,
    )
    add_textbox(s, Inches(7.2), Inches(4.9), Inches(5.7), Inches(1.2), "сначала лицо и голос\n→ потом предмет\n→ потом запись", size=15, bold=True, color=TEAL_DEEP)
    footer(s, 6)

    # ---- 7 ----
    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Колыбельные, потешки, пестушки", "Главный «учебник» ритма для младенца")
    picture(s, 7, Inches(0.4), Inches(1.15), Inches(7.0), Inches(4.5))
    table(
        s, Inches(7.6), Inches(1.15), Inches(5.3),
        [
            ["Жанр", "Как"],
            ["Колыбельная", "качать, тихо"],
            ["Потешка", "жест, ладушки"],
            ["Пестушка", "касание"],
        ],
        [Inches(2.5), Inches(2.8)],
        row_h=0.5,
    )
    card(s, Inches(7.6), Inches(3.6), Inches(2.5), Inches(2.5), LEAF, "Беру", ["добрый образ", "2–6 строк", "можно стоп"])
    card(s, Inches(10.3), Inches(3.6), Inches(2.6), Inches(2.5), RED_SOFT, "Не беру", ["страшилки", "длинный текст", "дожать любой ценой"])
    footer(s, 7)

    # ---- 8 ----
    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Движение вместе со взрослым", "Взрослое тело — безопасный метроном")
    picture(s, 8, Inches(0.4), Inches(1.15), Inches(7.2), Inches(5.0))
    table(
        s, Inches(7.85), Inches(1.15), Inches(5.0),
        [
            ["Форма", "Когда"],
            ["На руках / коленях", "база"],
            ["Лёжа — мягко", "младшие месяцы"],
            ["Сидя с опорой", "хлопаем, качаемся"],
            ["У опоры", "только при готовности"],
        ],
        [Inches(2.7), Inches(2.3)],
        row_h=0.48,
    )
    add_lines(s, Inches(7.85), Inches(4.0), Inches(5.0), Inches(2.2), [
        "• приглашать, не тащить",
        "• ритм задаёт взрослый",
        "• коротко (20–40 сек)",
        "• плач / отворот = стоп",
        "• ✕ не топать в строю",
    ], size=14, color=TEAL_DEEP)
    footer(s, 8)

    # ---- 9 ----
    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Телесная чувствительность и контакт", "Без взгляда и тепла ритм не приживается")
    picture(s, 9, Inches(0.4), Inches(1.15), Inches(6.8), Inches(4.8))
    table(
        s, Inches(7.4), Inches(1.15), Inches(5.5),
        [
            ["Есть контакт", "Нет контакта"],
            ["оживление / покой", "вздрагивание, плач"],
            ["повтор приятен", "стимул = давление"],
            ["чуть усложнить", "упростить / стоп"],
        ],
        [Inches(2.7), Inches(2.8)],
        row_h=0.55,
    )
    rounded(s, Inches(7.4), Inches(4.0), Inches(5.5), Inches(2.2), SAND)
    add_textbox(s, Inches(7.6), Inches(4.3), Inches(5.1), Inches(1.6), "взгляд + голос +\nкасание + пауза\n=\nэмоциональная безопасность", size=15, bold=True, color=TEAL_DEEP, align=PP_ALIGN.CENTER)
    footer(s, 9)

    # ---- 10 ----
    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Можно и нельзя в 0–1,5 лет", "Границы мягкости · светофор")
    picture(s, 10, Inches(0.4), Inches(1.15), Inches(5.8), Inches(5.2))
    card(s, Inches(6.5), Inches(1.2), Inches(3.2), Inches(4.6), GREEN_SOFT, "Можно ✓", [
        "петь, качать, гладить",
        "короткие потешки",
        "мягкий контраст",
        "погремушка «спит»",
        "стоп по состоянию",
    ])
    card(s, Inches(9.9), Inches(1.2), Inches(3.0), Inches(4.6), RED_SOFT, "Нельзя ✕", [
        "трясти, подбрасывать",
        "долбить до отказа",
        "крик / хлопок у уха",
        "долгий хаос-шум",
        "танец по правилам",
    ])
    add_textbox(s, Inches(6.5), Inches(6.1), Inches(6.4), Inches(0.4), "Право на паузу — профессиональный навык.", size=14, bold=True, color=TEAL_DEEP)
    footer(s, 10)

    # ---- 11 ----
    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Обзор практики", "Пять мягких блоков")
    picture(s, 11, Inches(0.4), Inches(1.15), Inches(8.2), Inches(5.3))
    add_lines(s, Inches(8.9), Inches(1.3), Inches(4.0), Inches(5.0), [
        "1. Игры на руках",
        "2. Ладушки / пальчики",
        "3. Покачивания",
        "4. Погремушки",
        "5. Сигналы и контрасты",
        "",
        "В каждой пробе —",
        "одна задача",
        "и обязательный стоп.",
    ], size=15, color=TEAL_DEEP)
    footer(s, 11)

    # ---- 12 ----
    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Практика 1. Игры на руках", "Покачать — не значит растрясти")
    picture(s, 12, Inches(0.4), Inches(1.15), Inches(7.0), Inches(5.0))
    table(
        s, Inches(7.6), Inches(1.15), Inches(5.3),
        [
            ["Шаг", "Действие"],
            ["1", "устойчиво взять, голова"],
            ["2", "тихий напев + качание"],
            ["3", "лёгкий топ-топ без прыжка"],
            ["4", "стоп: прижать, пауза"],
        ],
        [Inches(1.0), Inches(4.3)],
        row_h=0.55,
    )
    add_textbox(s, Inches(7.6), Inches(4.5), Inches(5.3), Inches(1.5), "не трясти · не подбрасывать\nчитать «плач» модели · стоп", size=15, bold=True, color=CORAL)
    footer(s, 12)

    # ---- 13 ----
    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Практика 2. Ладушки и пальчиковые игры", "Голос теплее хлопка")
    picture(s, 13, Inches(0.4), Inches(1.15), Inches(6.8), Inches(4.8))
    table(
        s, Inches(7.4), Inches(1.15), Inches(5.5),
        [
            ["Хорошо", "Плохо"],
            ["голос слышнее хлопка", "хлопки глушат слово"],
            ["темп удобен малышу", "гонка «успеть всё»"],
            ["2–3 повтора", "долбить до отказа"],
            ["пауза — взгляд", "лицо в телефон"],
        ],
        [Inches(2.7), Inches(2.8)],
        row_h=0.5,
    )
    add_textbox(s, Inches(7.4), Inches(4.5), Inches(5.5), Inches(1.5), "потешка → жест на ударных\n→ повтор → взгляд-пауза\n\nНе требовать идеальных ладошек.", size=14, bold=True, color=TEAL_DEEP)
    footer(s, 13)

    # ---- 14 ----
    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Практика 3. Покачивания под музыку", "Медленный пульс и мягкий контраст")
    picture(s, 14, Inches(0.4), Inches(1.15), Inches(7.0), Inches(5.0))
    table(
        s, Inches(7.6), Inches(1.15), Inches(5.3),
        [
            ["Вариант", "Содержание"],
            ["На руках", "колыбельная"],
            ["На коленях", "«кач-кач»"],
            ["Лёжа", "мягкое ведение"],
            ["Контраст", "20с → 10с бодрее → покой"],
        ],
        [Inches(2.0), Inches(3.3)],
        row_h=0.55,
    )
    add_textbox(s, Inches(7.6), Inches(4.6), Inches(5.3), Inches(1.4), "спокойный пульс → короткий\nконтраст → возврат к покою\n\n«Бодрее» ≠ «громко».", size=14, bold=True, color=TEAL_DEEP)
    footer(s, 14)

    # ---- 15 ----
    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Практика 4. Погремушка и звуковые контрасты", "Учить тишине так же, как звуку")
    picture(s, 15, Inches(0.4), Inches(1.15), Inches(6.8), Inches(4.8))
    table(
        s, Inches(7.4), Inches(1.15), Inches(5.5),
        [
            ["Шаг", "Действие"],
            ["1", "показать лицом и голосом"],
            ["2", "тихо потрясти в ритме"],
            ["3", "«погремушка спит»"],
            ["4", "короткий звук → сон"],
            ["5", "вместе слегка потрясти"],
        ],
        [Inches(1.0), Inches(4.5)],
        row_h=0.45,
    )
    card(s, Inches(7.4), Inches(4.6), Inches(2.6), Inches(1.7), LEAF, "Можно", ["3–5 коротких смен", "стоп при усталости"])
    card(s, Inches(10.2), Inches(4.6), Inches(2.7), Inches(1.7), RED_SOFT, "Нельзя", ["крик у уха", "дискотека"])
    footer(s, 15)

    # ---- 16 ----
    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Мини-тренинг студента", "60–70 секунд мягкого ритуала")
    picture(s, 16, Inches(0.4), Inches(1.15), Inches(7.0), Inches(5.0))
    table(
        s, Inches(7.6), Inches(1.15), Inches(5.3),
        [
            ["Шаг", "Действие"],
            ["1", "выбрать форму"],
            ["2", "одна потешка / напев"],
            ["3", "начало → повтор → стоп"],
            ["4", "можно + нельзя"],
        ],
        [Inches(1.0), Inches(4.3)],
        row_h=0.48,
    )
    card(s, Inches(7.6), Inches(4.0), Inches(5.3), Inches(2.3), TEAL, "Рубрика Да/Нет", [
        "контакт · мягкость · краткость",
        "пауза · без резкости",
        "понятно, зачем младенцу",
    ])
    footer(s, 16)

    # ---- 17 ----
    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Чек-лист работы с 0–1,5 лет", "Перед возрастом 1,5–3")
    picture(s, 17, Inches(0.4), Inches(1.15), Inches(6.5), Inches(5.0))
    checks = [
        "1. Сенсомоторика и контакт, не номер",
        "2. Читаю реакцию на интонацию",
        "3. Различаю жанры",
        "4. Вместе, не тащу",
        "5. Взгляд, голос, касание",
        "6. Ладушки / качание мягко",
        "7. Погремушка со «сном»",
        "8. Стоп при переутомлении",
    ]
    for i, t in enumerate(checks):
        y = Inches(1.2 + i * 0.55)
        rounded(s, Inches(7.1), y, Inches(5.8), Inches(0.48), SOFT if i % 2 == 0 else SAND)
        add_textbox(s, Inches(7.3), y + Inches(0.08), Inches(5.4), Inches(0.35), t, size=13, color=INK, font="Calibri")
    add_textbox(s, Inches(0.5), Inches(6.3), Inches(12), Inches(0.4), "ГОЛОС  ↔  КАСАНИЕ  ↔  ПАУЗА", size=18, bold=True, color=TEAL_DEEP, align=PP_ALIGN.CENTER)
    footer(s, 17)

    # ---- 18 ----
    s = prs.slides.add_slide(blank)
    bg(s, TEAL_DEEP)
    oval(s, Inches(-0.5), Inches(-0.6), Inches(2.5), Inches(2.5), TEAL)
    oval(s, Inches(11.5), Inches(5.5), Inches(2.5), Inches(2.5), CORAL)
    add_textbox(s, Inches(0.5), Inches(0.3), Inches(6.0), Inches(0.35), "Итог + домашнее задание", size=14, color=GOLD, font="Calibri")
    add_textbox(s, Inches(0.5), Inches(0.75), Inches(6.0), Inches(0.7), "Ритм начинается\nс тёплого взрослого", size=26, bold=True, color=WHITE)
    add_textbox(s, Inches(0.5), Inches(1.7), Inches(6.0), Inches(0.8), "Мягкий голос.\nКороткая форма.\nПраво на паузу.", size=16, color=SAND, font="Calibri")
    picture(s, 18, Inches(6.8), Inches(0.4), Inches(6.1), Inches(4.0))
    hw = [
        ("1. Таблица", "слух · ответ · роль\nпримеры · можно/нельзя"),
        ("2. Ритуал 2–3 мин", "качание + потешка\n+ погремушка (8–12 мес.)"),
        ("3. Мини-эссе", "почему контакт важнее\nидеального жеста"),
    ]
    for i, (t, b) in enumerate(hw):
        rounded(s, Inches(0.4 + i * 4.25), Inches(4.7), Inches(4.0), Inches(1.7), WHITE)
        add_textbox(s, Inches(0.55 + i * 4.25), Inches(4.85), Inches(3.7), Inches(0.35), t, size=14, bold=True, color=TEAL_DEEP)
        add_lines(s, Inches(0.55 + i * 4.25), Inches(5.3), Inches(3.7), Inches(0.9), b.split("\n"), size=12, color=INK, spacing=2)
    add_textbox(s, Inches(0.5), Inches(6.7), Inches(12), Inches(0.3), "Сохраните мягкость — и ритмическое развитие начнётся с правильного этажа.", size=13, color=GOLD, align=PP_ALIGN.CENTER, font="Calibri")

    prs.save(str(OUT))
    ART.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(ART))
    print(f"OK pptx={OUT} images={len(IMG)}")


if __name__ == "__main__":
    build()
