#!/usr/bin/env python3
"""Ready-to-show PowerPoint for lesson 6 — rhythm 0–1.5 years."""

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

# Soft infant-care palette (not purple / not terracotta-cream AI default)
INK = RGBColor(0x1E, 0x2F, 0x3A)
CREAM = RGBColor(0xF7, 0xFA, 0xFC)
SAND = RGBColor(0xE8, 0xF0, 0xF4)
TEAL = RGBColor(0x2A, 0x7A, 0x8C)
TEAL_DEEP = RGBColor(0x1A, 0x5A, 0x6A)
CORAL = RGBColor(0xD4, 0x7A, 0x6A)
GOLD = RGBColor(0xC9, 0xA2, 0x4E)
LEAF = RGBColor(0x5A, 0x8F, 0x7B)
SKY = RGBColor(0x5B, 0x9B, 0xB8)
ROSE = RGBColor(0xB8, 0x6B, 0x7E)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
MUTED = RGBColor(0x5A, 0x6E, 0x78)
SOFT = RGBColor(0xE4, 0xF0, 0xF3)
RED_SOFT = RGBColor(0xC4, 0x5C, 0x5C)
GREEN_SOFT = RGBColor(0x4A, 0x9A, 0x7A)

OUT = Path(__file__).resolve().parent / "zanyatie-06-prezentaciya.pptx"
ART = Path("/opt/cursor/artifacts/zanyatie-06-prezentaciya.pptx")


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
    add_textbox(slide, Inches(0.45), Inches(0.22), Inches(12.5), Inches(0.65), title, size=26, bold=True, color=TEAL_DEEP)
    if subtitle:
        add_textbox(slide, Inches(0.45), Inches(0.85), Inches(12.5), Inches(0.35), subtitle, size=15, color=MUTED, font="Calibri")


def card(slide, left, top, width, height, fill, title, body_lines, title_color=WHITE, body_color=WHITE):
    rounded(slide, left, top, width, height, fill)
    add_textbox(slide, left + Inches(0.18), top + Inches(0.12), width - Inches(0.3), Inches(0.38), title, size=15, bold=True, color=title_color)
    add_lines(
        slide,
        left + Inches(0.18),
        top + Inches(0.5),
        width - Inches(0.3),
        height - Inches(0.6),
        body_lines,
        size=12,
        color=body_color,
        spacing=3,
    )


def table(slide, left, top, width, rows, col_widths, *, row_h=0.42):
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


def icon_pill(slide, left, top, label, color):
    rounded(slide, left, top, Inches(2.4), Inches(0.55), color)
    add_textbox(slide, left, top + Inches(0.1), Inches(2.4), Inches(0.4), label, size=13, bold=True, color=WHITE, align=PP_ALIGN.CENTER, font="Calibri")


def build():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank = prs.slide_layouts[6]

    # ---- 1 TITLE ----
    s = prs.slides.add_slide(blank)
    bg(s, TEAL_DEEP)
    oval(s, Inches(-0.8), Inches(-1.0), Inches(3.2), Inches(3.2), TEAL)
    oval(s, Inches(11.0), Inches(5.0), Inches(3.2), Inches(3.2), CORAL)
    oval(s, Inches(10.8), Inches(-0.7), Inches(2.4), Inches(2.4), GOLD)
    add_textbox(s, Inches(1.0), Inches(1.55), Inches(11), Inches(0.4), "ЗАНЯТИЕ 6 · МОДУЛЬ II", size=16, color=GOLD, align=PP_ALIGN.CENTER, font="Calibri")
    add_textbox(
        s, Inches(0.8), Inches(2.15), Inches(11.7), Inches(1.4),
        "Ритмическое развитие детей\nот рождения до 1,5 лет",
        size=36, bold=True, color=WHITE, align=PP_ALIGN.CENTER,
    )
    add_textbox(
        s, Inches(1.5), Inches(4.0), Inches(10.3), Inches(0.5),
        "Не танец по правилам — телесный диалог",
        size=20, color=SAND, align=PP_ALIGN.CENTER, font="Calibri",
    )
    add_textbox(
        s, Inches(2.0), Inches(4.7), Inches(9.3), Inches(0.4),
        "услышал  →  почувствовал рядом со взрослым  →  оживился / успокоился",
        size=15, color=WHITE, align=PP_ALIGN.CENTER, font="Calibri",
    )
    for i, (lab, col) in enumerate([("ухо", SKY), ("сердце", CORAL), ("руки", LEAF), ("погремушка", GOLD)]):
        icon_pill(s, Inches(2.0 + i * 2.55), Inches(5.5), lab, col)
    add_textbox(s, Inches(1), Inches(6.6), Inches(11.3), Inches(0.3), "Бабаджан · Ветлугина · Картушина «Забавы для малышей»", size=12, color=SAND, align=PP_ALIGN.CENTER, font="Calibri")

    # ---- 2 WHY SPECIAL ----
    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Чем этот возраст особенный", "Самый ранний этаж ритмики")
    table(
        s, Inches(0.5), Inches(1.5), Inches(8.2),
        [
            ["0–1,5 лет", "Позже (3–5+)"],
            ["совместное движение", "больше самостоятельности"],
            ["голос важнее колонки", "запись используется шире"],
            ["нет строя и «стопа по правилу»", "появляются игровые правила"],
            ["контакт = главное условие", "контакт важен, но уже есть задача"],
        ],
        [Inches(4.0), Inches(4.2)],
        row_h=0.55,
    )
    card(s, Inches(9.0), Inches(1.5), Inches(3.8), Inches(2.2), TEAL, "Дверь открыта", ["тёплый диалог", "голос + касание", "короткий повтор"])
    card(s, Inches(9.0), Inches(3.9), Inches(3.8), Inches(2.2), RED_SOFT, "Дверь закрыта", ["номер / строй", "танец по правилам", "давление до отказа"])
    add_textbox(s, Inches(0.5), Inches(6.4), Inches(12), Inches(0.4), "Младенец не готовит номер — он учится быть в ритме рядом со взрослым.", size=15, bold=True, color=TEAL_DEEP)
    footer(s, 2)

    # ---- 3 GOAL ----
    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Чему учимся сегодня", "Цель занятия для студента")
    steps = [
        ("1", "Понять слух и движение младенца"),
        ("2", "Увидеть реакции на интонации"),
        ("3", "Использовать колыбельные, потешки, пестушки"),
        ("4", "Двигаться вместе со взрослым"),
        ("5", "Держать телесный и эмоциональный контакт"),
        ("6", "Провести мягкие игры и контрасты"),
    ]
    for i, (n, t) in enumerate(steps):
        y = Inches(1.4 + i * 0.7)
        oval(s, Inches(0.55), y, Inches(0.5), Inches(0.5), TEAL if i % 2 == 0 else LEAF)
        add_textbox(s, Inches(0.55), y + Inches(0.08), Inches(0.5), Inches(0.35), n, size=14, bold=True, color=WHITE, align=PP_ALIGN.CENTER, font="Calibri")
        add_textbox(s, Inches(1.25), y + Inches(0.08), Inches(7.5), Inches(0.4), t, size=16, color=INK)
    card(s, Inches(9.0), Inches(1.5), Inches(3.8), Inches(2.0), TEAL, "Знает", ["особенности 0–1,5 лет", "границы «можно / нельзя»"])
    card(s, Inches(9.0), Inches(3.7), Inches(3.8), Inches(2.2), CORAL, "Умеет", ["покачивание / ладушки", "погремушка со «сном»", "стоп при переутомлении"])
    footer(s, 3)

    # ---- 4 MAP ----
    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Карта темы", "От слуха — к короткой забаве")
    topics = [
        (TEAL, "1. Слух и движение"),
        (SKY, "2. Интонации"),
        (LEAF, "3. Колыбельная / потешка"),
        (GOLD, "4. Вместе со взрослым"),
        (CORAL, "5. Контакт"),
        (ROSE, "6. Практика игр"),
    ]
    for i, (col, t) in enumerate(topics):
        col_i = i % 3
        row_i = i // 3
        card(s, Inches(0.5 + col_i * 4.2), Inches(1.5 + row_i * 2.0), Inches(3.9), Inches(1.7), col, t, ["ключевой блок занятия"])
    table(
        s, Inches(0.5), Inches(5.6), Inches(12.3),
        [["Слайды", "Блок"], ["5–11", "теория"], ["12–16", "практика"], ["17–18", "чек-лист и итог"]],
        [Inches(3.0), Inches(9.3)],
        row_h=0.35,
    )
    footer(s, 4)

    # ---- 5 HEARING ----
    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Слуховое и двигательное восприятие", "Звук входит вместе с теплом рук")
    table(
        s, Inches(0.5), Inches(1.4), Inches(12.3),
        [
            ["Период", "Слух", "Движение"],
            ["Первые месяцы", "голос, ориентировка на звук", "общие реакции тела"],
            ["Ближе к полугоду", "интерес к погремушке, интонации", "тянется, трясёт, оживляется"],
            ["К 1–1,5 годам", "короткие игровые сигналы", "подражает простым жестам рядом"],
        ],
        [Inches(2.8), Inches(4.7), Inches(4.8)],
        row_h=0.6,
    )
    rounded(s, Inches(0.5), Inches(4.0), Inches(12.3), Inches(1.3), SAND)
    add_textbox(s, Inches(0.8), Inches(4.25), Inches(11.7), Inches(0.4), "голос / звук  →  реакция тела  →  повтор в контакте  →  привычный отклик", size=18, bold=True, color=TEAL_DEEP, align=PP_ALIGN.CENTER)
    add_textbox(s, Inches(0.8), Inches(4.8), Inches(11.7), Inches(0.35), "Даём сенсорный опыт, а не комбинацию. Волны голоса взрослого «входят» через руки.", size=14, color=MUTED, align=PP_ALIGN.CENTER, font="Calibri")
    footer(s, 5)

    # ---- 6 INTONATION ----
    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Реакции на музыкальные интонации", "Интонация — эмоциональное лицо звука")
    table(
        s, Inches(0.45), Inches(1.35), Inches(12.4),
        [
            ["Интонация", "Желаемая реакция", "Чего избегать"],
            ["Мягкая певучая", "спокойствие, контакт", "громкая запись без тепла голоса"],
            ["Светлая игривая", "оживление", "длинная серия до перевозбуждения"],
            ["Тихо / чуть громче", "внимание", "резкие скачки и крик"],
            ["Резкая громкая", "вздрагивание, плач", "использовать «для веселья»"],
        ],
        [Inches(3.0), Inches(4.2), Inches(5.2)],
        row_h=0.55,
    )
    for i, (lab, col) in enumerate([("спокойно ✓", LEAF), ("игриво ✓", GOLD), ("резко ✕", RED_SOFT)]):
        icon_pill(s, Inches(1.5 + i * 3.5), Inches(5.5), lab, col)
    add_textbox(s, Inches(0.5), Inches(6.3), Inches(12), Inches(0.35), "сначала лицо и голос  →  потом предмет  →  потом запись", size=15, bold=True, color=TEAL_DEEP, align=PP_ALIGN.CENTER)
    footer(s, 6)

    # ---- 7 GENRES ----
    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Колыбельные, потешки, пестушки", "Главный «учебник» ритма для младенца")
    table(
        s, Inches(0.45), Inches(1.35), Inches(12.4),
        [
            ["Жанр", "Ритмическая роль", "Как использовать"],
            ["Колыбельная", "медленный пульс, успокоение", "покачивание, тихий голос"],
            ["Потешка", "слоговой ритм, повтор", "жест рук, ладушки"],
            ["Пестушка", "ритм заботы + касание", "поглаживание, пальчики"],
        ],
        [Inches(2.8), Inches(4.6), Inches(5.0)],
        row_h=0.55,
    )
    card(s, Inches(0.5), Inches(4.3), Inches(6.0), Inches(2.2), LEAF, "Беру", ["добрый короткий образ", "2–6 строк на заход", "можно остановиться"])
    card(s, Inches(6.8), Inches(4.3), Inches(6.0), Inches(2.2), RED_SOFT, "Не беру", ["страшилки, резкая динамика", "длинный монолог", "«дожать до конца любой ценой»"])
    footer(s, 7)

    # ---- 8 CO-MOVEMENT ----
    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Движение вместе со взрослым", "Взрослое тело — безопасный метроном")
    table(
        s, Inches(0.45), Inches(1.35), Inches(7.8),
        [
            ["Форма", "Когда уместно"],
            ["На руках / на коленях", "база возраста"],
            ["Лёжа — мягкое ведение рук/ног", "младшие месяцы"],
            ["Сидя с опорой", "вместе хлопаем, качаемся"],
            ["У опоры / с поддержкой", "только при физической готовности"],
        ],
        [Inches(4.0), Inches(3.8)],
        row_h=0.55,
    )
    card(s, Inches(8.5), Inches(1.35), Inches(4.3), Inches(3.6), TEAL, "Принципы", [
        "приглашать, не тащить",
        "ритм задаёт взрослый",
        "коротко (часто 20–40 сек)",
        "плач / отворот = стоп",
        "или упрощение",
        "",
        "✗ не требовать топать",
        "  под марш в строю",
    ])
    add_textbox(s, Inches(0.5), Inches(5.5), Inches(12), Inches(0.9), "Картинка к слайду: взрослый и младенец на коленях «топ-топ»; рядом запрет строя.", size=14, color=MUTED, font="Calibri")
    footer(s, 8)

    # ---- 9 CONTACT ----
    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Телесная чувствительность и контакт", "Без взгляда и тепла ритм не приживается")
    table(
        s, Inches(0.45), Inches(1.4), Inches(12.4),
        [
            ["Есть контакт", "Нет контакта"],
            ["осмысленное оживление / успокоение", "вздрагивание, отворот, плач"],
            ["повтор приятен", "стимул как давление"],
            ["можно чуть усложнить", "нужно упростить / остановиться"],
        ],
        [Inches(6.2), Inches(6.2)],
        row_h=0.6,
    )
    rounded(s, Inches(0.5), Inches(4.0), Inches(12.3), Inches(2.2), SAND)
    add_textbox(s, Inches(0.8), Inches(4.3), Inches(11.7), Inches(0.45), "взгляд + голос + касание + пауза  =  эмоциональная безопасность", size=20, bold=True, color=TEAL_DEEP, align=PP_ALIGN.CENTER)
    add_textbox(
        s, Inches(0.8), Inches(5.1), Inches(11.7), Inches(0.7),
        "Вывод теории: ритм 0–1,5 лет = мягкий слух + совместное тело + голос + повтор + безопасность.",
        size=15, color=INK, align=PP_ALIGN.CENTER, font="Calibri",
    )
    footer(s, 9)

    # ---- 10 CAN / CANNOT ----
    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Можно и нельзя в 0–1,5 лет", "Границы мягкости")
    card(s, Inches(0.45), Inches(1.35), Inches(6.1), Inches(4.6), GREEN_SOFT, "Можно ✓", [
        "петь, качать, гладить в ритме",
        "короткие потешки и ладушки",
        "мягкий контраст тихо / чуть громче",
        "погремушка с ритуалом «спит»",
        "остановиться по состоянию ребёнка",
    ])
    card(s, Inches(6.8), Inches(1.35), Inches(6.1), Inches(4.6), RED_SOFT, "Нельзя ✕", [
        "трясти, подбрасывать",
        "долбить до отказа",
        "крик, хлопок у уха",
        "долгий хаотичный шум",
        "«танец по правилам», строй",
    ])
    add_textbox(s, Inches(0.5), Inches(6.2), Inches(12), Inches(0.4), "Право на паузу — профессиональный навык, не слабость.", size=16, bold=True, color=TEAL_DEEP, align=PP_ALIGN.CENTER)
    footer(s, 10)

    # ---- 11 PRACTICE OVERVIEW ----
    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Обзор практики", "Пять мягких блоков")
    blocks = [
        (TEAL, "Игры на руках", "ритм через тело взрослого"),
        (SKY, "Ладушки / пальчики", "слог + мелкий жест"),
        (LEAF, "Покачивания", "медленный пульс, смена состояния"),
        (GOLD, "Погремушки", "звук ↔ тишина"),
        (CORAL, "Сигналы и контрасты", "услышать разницу без перегруза"),
    ]
    for i, (col, t, b) in enumerate(blocks):
        card(s, Inches(0.4 + i * 2.55), Inches(1.5), Inches(2.4), Inches(3.8), col, t, [b, "", "одна задача", "обязательный стоп"])
    add_textbox(s, Inches(0.5), Inches(5.7), Inches(12), Inches(0.7), "В каждой пробе — одна задача и обязательный стоп. Пять станций вокруг младенца на руках.", size=15, color=MUTED, align=PP_ALIGN.CENTER, font="Calibri")
    footer(s, 11)

    # ---- 12 HANDS ----
    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Практика 1. Игры на руках", "Покачать — не значит растрясти")
    table(
        s, Inches(0.45), Inches(1.4), Inches(8.0),
        [
            ["Шаг", "Действие"],
            ["1", "устойчиво взять, поддержать голову (модель младшего)"],
            ["2", "тихий напев + мягкое качание"],
            ["3", "чуть оживлённый напев + лёгкий «топ-топ» без подпрыгивания"],
            ["4", "стоп: прижать, снизить голос, пауза"],
        ],
        [Inches(1.0), Inches(7.0)],
        row_h=0.6,
    )
    card(s, Inches(8.7), Inches(1.4), Inches(4.1), Inches(3.6), CORAL, "Безопасность", [
        "не трясти",
        "не подбрасывать",
        "читать «плач» модели",
        "стоп сразу",
        "",
        "✓ правильная поддержка",
        "✕ подбрасывание",
    ])
    footer(s, 12)

    # ---- 13 LADUSHKI ----
    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Практика 2. Ладушки и пальчиковые игры", "Голос теплее хлопка")
    table(
        s, Inches(0.45), Inches(1.35), Inches(12.4),
        [
            ["Хорошо", "Плохо"],
            ["голос слышнее хлопка", "хлопки глушат слово"],
            ["темп удобен малышу", "гонка «успеть всё»"],
            ["2–3 повтора", "долбить до отказа"],
            ["пауза посмотреть в глаза", "лицо в сторону / в телефон"],
        ],
        [Inches(6.2), Inches(6.2)],
        row_h=0.55,
    )
    rounded(s, Inches(0.5), Inches(4.4), Inches(12.3), Inches(1.8), SAND)
    add_textbox(s, Inches(0.8), Inches(4.7), Inches(11.7), Inches(0.4), "потешка  →  жест на ударных слогах  →  повтор  →  взгляд-пауза", size=18, bold=True, color=TEAL_DEEP, align=PP_ALIGN.CENTER)
    add_textbox(s, Inches(0.8), Inches(5.4), Inches(11.7), Inches(0.4), "Не требовать идеального попадания ладошек.", size=14, color=MUTED, align=PP_ALIGN.CENTER, font="Calibri")
    footer(s, 13)

    # ---- 14 ROCKING ----
    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Практика 3. Покачивания под музыку", "Медленный пульс и мягкий контраст")
    table(
        s, Inches(0.45), Inches(1.4), Inches(12.4),
        [
            ["Вариант", "Содержание"],
            ["На руках", "колыбельная"],
            ["На коленях", "«кач-кач»"],
            ["Лёжа (модель)", "лёгкое ведение без резкости"],
            ["Контраст", "20 сек спокойно → 10 сек чуть бодрее → снова спокойно"],
        ],
        [Inches(3.2), Inches(9.2)],
        row_h=0.55,
    )
    add_textbox(s, Inches(0.5), Inches(5.0), Inches(12), Inches(0.4), "спокойный пульс  →  короткий контраст  →  возврат к спокойствию", size=18, bold=True, color=TEAL_DEEP, align=PP_ALIGN.CENTER)
    add_textbox(s, Inches(0.5), Inches(5.7), Inches(12), Inches(0.4), "«Бодрее» ≠ «громко». Маятник-качание — визуальный якорь слайда.", size=14, color=MUTED, align=PP_ALIGN.CENTER, font="Calibri")
    footer(s, 14)

    # ---- 15 RATTLE ----
    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Практика 4. Погремушка и звуковые контрасты", "Учить тишине так же, как звуку")
    table(
        s, Inches(0.45), Inches(1.3), Inches(7.5),
        [
            ["Шаг", "Действие"],
            ["1", "показать лицом и голосом"],
            ["2", "тихо потрясти в ритме слогов"],
            ["3", "«погремушка спит»"],
            ["4", "снова короткий звук → сон"],
            ["5", "вместе слегка потрясти"],
        ],
        [Inches(1.0), Inches(6.5)],
        row_h=0.48,
    )
    card(s, Inches(8.2), Inches(1.3), Inches(4.6), Inches(2.4), LEAF, "Можно", ["мягкий контраст 2 качеств", "3–5 коротких смен", "стоп при переутомлении"])
    card(s, Inches(8.2), Inches(3.9), Inches(4.6), Inches(2.2), RED_SOFT, "Нельзя", ["крик / хлопок у уха", "длинная «дискотека»", "«ещё разок» через силу"])
    footer(s, 15)

    # ---- 16 MINI-TRAINING ----
    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Мини-тренинг студента", "60–70 секунд мягкого ритуала")
    table(
        s, Inches(0.45), Inches(1.3), Inches(7.0),
        [
            ["Шаг", "Действие"],
            ["1", "выбрать форму (руки / ладушки / качание / погремушка)"],
            ["2", "одна потешка или напев"],
            ["3", "начало → повтор → мягкий стоп"],
            ["4", "одно «можно» и одно «нельзя»"],
        ],
        [Inches(1.0), Inches(6.0)],
        row_h=0.55,
    )
    card(s, Inches(7.7), Inches(1.3), Inches(5.1), Inches(4.5), TEAL, "Рубрика Да/Нет", [
        "Контакт лица и голоса",
        "Движения мягкие",
        "Длительность короткая",
        "Есть пауза / стоп",
        "Нет резкости и «танца по правилам»",
        "Понятно, зачем младенцу",
    ])
    footer(s, 16)

    # ---- 17 CHECKLIST ----
    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Чек-лист работы с 0–1,5 лет", "Перед тем как идти к возрасту 1,5–3")
    checks = [
        "1. Понимаю: сенсомоторика и контакт, не номер?",
        "2. Умею читать реакцию на интонацию?",
        "3. Различаю колыбельную, потешку, пестушку?",
        "4. Двигаюсь вместе, не тащу?",
        "5. Держу взгляд, голос, касание?",
        "6. Могу провести ладушки / покачивание мягко?",
        "7. Учу погремушку со «сном» и тишиной?",
        "8. Останавливаюсь при переутомлении?",
    ]
    for i, t in enumerate(checks):
        col = i // 4
        row = i % 4
        rounded(s, Inches(0.45 + col * 6.4), Inches(1.35 + row * 1.0), Inches(6.1), Inches(0.85), SOFT if i % 2 == 0 else SAND)
        add_textbox(s, Inches(0.7 + col * 6.4), Inches(1.55 + row * 1.0), Inches(5.7), Inches(0.5), t, size=14, color=INK, font="Calibri")
    add_textbox(s, Inches(0.5), Inches(5.7), Inches(12), Inches(0.5), "ГОЛОС   ↔   КАСАНИЕ   ↔   ПАУЗА", size=22, bold=True, color=TEAL_DEEP, align=PP_ALIGN.CENTER)
    footer(s, 17)

    # ---- 18 SUMMARY ----
    s = prs.slides.add_slide(blank)
    bg(s, TEAL_DEEP)
    oval(s, Inches(-0.6), Inches(-0.8), Inches(2.8), Inches(2.8), TEAL)
    oval(s, Inches(11.2), Inches(5.2), Inches(2.8), Inches(2.8), CORAL)
    add_textbox(s, Inches(0.8), Inches(0.5), Inches(11.7), Inches(0.6), "Итог + домашнее задание", size=16, color=GOLD, align=PP_ALIGN.CENTER, font="Calibri")
    add_textbox(s, Inches(0.8), Inches(1.1), Inches(11.7), Inches(0.7), "Ритм начинается с тёплого взрослого", size=30, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    add_textbox(
        s, Inches(1.5), Inches(2.0), Inches(10.3), Inches(1.0),
        "Мягкий голос.  Короткая форма.  Право на паузу.\nТогда ритм младенца растёт правильно.",
        size=18, color=SAND, align=PP_ALIGN.CENTER, font="Calibri",
    )
    # homework as three light cards
    hw = [
        ("1. Таблица на 1 стр.", "слух · двигательный ответ\nроль взрослого · 2 примера\nможно / нельзя"),
        ("2. Ритуал 2–3 мин", "покачивание + потешка\n+ погремушка с тишиной\n(для 8–12 мес.)"),
        ("3. Мини-эссе", "почему контакт важнее\nидеального жеста"),
    ]
    for i, (t, b) in enumerate(hw):
        rounded(s, Inches(0.7 + i * 4.15), Inches(3.4), Inches(3.9), Inches(2.4), WHITE)
        add_textbox(s, Inches(0.9 + i * 4.15), Inches(3.55), Inches(3.5), Inches(0.4), t, size=15, bold=True, color=TEAL_DEEP)
        add_lines(s, Inches(0.9 + i * 4.15), Inches(4.1), Inches(3.5), Inches(1.5), b.split("\n"), size=13, color=INK, spacing=4)
    add_textbox(s, Inches(0.8), Inches(6.2), Inches(11.7), Inches(0.4), "Сохраните мягкость — и ритмическое развитие начнётся с правильного этажа.", size=14, color=GOLD, align=PP_ALIGN.CENTER, font="Calibri")
    add_textbox(s, Inches(0.8), Inches(6.7), Inches(11.7), Inches(0.3), "Бабаджан · Ветлугина · Картушина", size=12, color=SAND, align=PP_ALIGN.CENTER, font="Calibri")

    prs.save(str(OUT))
    ART.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(ART))
    print(f"OK pptx={OUT}")


if __name__ == "__main__":
    build()
