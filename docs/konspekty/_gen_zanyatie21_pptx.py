#!/usr/bin/env python3
"""Ready-to-show PowerPoint for musical games and songs with movement."""

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
ASSETS = ROOT / "zanyatie-21-assets"
OUT = ROOT / "zanyatie-21-prezentaciya.pptx"
ART = Path("/opt/cursor/artifacts/zanyatie-21-prezentaciya.pptx")

IMG = {
    1: "z21-01-title.jpg",
    2: "z21-02-doors.jpg",
    3: "z21-03-goal.jpg",
    4: "z21-04-spheres.jpg",
    5: "z21-05-forms.jpg",
    6: "z21-06-traffic.jpg",
    7: "z21-07-select.jpg",
    8: "z21-08-stages.jpg",
    9: "z21-09-exercises.jpg",
    10: "z21-10-repertoire.jpg",
    11: "z21-11-training.jpg",
    12: "z21-12-finale.jpg",
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


def footer(slide, n, total=12):
    add_textbox(
        slide, Inches(0.4), Inches(7.15), Inches(12), Inches(0.3),
        f"Игры и песни с движением · Слух · Жест · Роль · Стоп   {n}/{total}",
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

    s = prs.slides.add_slide(blank)
    bg(s, TEAL_DEEP)
    oval(s, Inches(-0.8), Inches(-1.0), Inches(3.0), Inches(3.0), TEAL)
    oval(s, Inches(11.2), Inches(5.2), Inches(2.8), Inches(2.8), CORAL)
    add_textbox(s, Inches(0.5), Inches(0.35), Inches(6.2), Inches(0.35), "ПЕНИЕ · ДВИЖЕНИЕ · ИГРА", size=13, color=GOLD, font="Calibri")
    add_textbox(s, Inches(0.5), Inches(0.85), Inches(6.2), Inches(1.6), "Музыкальные игры\nи песни\nс движением", size=28, bold=True, color=WHITE)
    add_textbox(s, Inches(0.5), Inches(2.8), Inches(6.2), Inches(0.4), "Не хаос под трек — слух, образ, жест и мягкий голос", size=14, color=SAND, font="Calibri")
    add_textbox(s, Inches(0.5), Inches(3.4), Inches(6.2), Inches(0.9), "услышать → показать →\nповторить движением → стоп", size=14, color=WHITE, font="Calibri")
    picture(s, 1, Inches(7.0), Inches(0.6), Inches(5.8), Inches(5.5))
    add_textbox(s, Inches(0.5), Inches(6.5), Inches(12), Inches(0.3), "Ветлугина · Радынова · Буренина · «Ладушки» · «Музыка и движение»", size=12, color=SAND, font="Calibri")

    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Зачем эта тема", "Мост между «просто поём» и «просто двигаемся»")
    picture(s, 2, Inches(0.45), Inches(1.2), Inches(6.6), Inches(4.8))
    table(s, Inches(7.3), Inches(1.2), Inches(5.5), [
        ["Без игры", "С игрой / песней"],
        ["пение «сидя»", "образ и действие"],
        ["движение без слуха", "ответ на музыку"],
        ["длинные объяснения", "короткий показ"],
        ["крик и беготня", "правило + пауза"],
    ], [Inches(2.6), Inches(2.9)], row_h=0.55)
    add_textbox(s, Inches(7.3), Inches(5.1), Inches(5.5), Inches(1.0), "Убрать музыку —\nсмысл меняется?", size=15, bold=True, color=TEAL_DEEP)
    footer(s, 2)

    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Чему учимся сегодня", "Цель и продукт")
    steps = ["Значение", "Три формы", "Подбор материала", "Этапы подготовки", "Упражнения", "Практика"]
    for i, t in enumerate(steps):
        y = Inches(1.2 + i * 0.7)
        oval(s, Inches(0.5), y, Inches(0.45), Inches(0.45), TEAL if i % 2 == 0 else LEAF)
        add_textbox(s, Inches(0.5), y + Inches(0.07), Inches(0.45), Inches(0.3), str(i + 1), size=13, bold=True, color=WHITE, align=PP_ALIGN.CENTER, font="Calibri")
        add_textbox(s, Inches(1.15), y + Inches(0.07), Inches(5.8), Inches(0.4), t, size=15, color=INK)
    picture(s, 3, Inches(7.3), Inches(1.2), Inches(5.5), Inches(5.2))
    footer(s, 3)

    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Значение", "Что развивают игра и песня с движением")
    picture(s, 4, Inches(0.4), Inches(1.15), Inches(6.8), Inches(4.5))
    table(s, Inches(7.4), Inches(1.15), Inches(5.5), [
        ["Сфера", "Что развивается"],
        ["Слух", "начало, темп, характер"],
        ["Голос", "подпевание, мягкость"],
        ["Ритм", "шаг, хлопок, жест"],
        ["Координация", "слово + движение"],
        ["Внимание", "правило, сигнал, роль"],
        ["Общение", "круг, пара, вместе"],
    ], [Inches(2.2), Inches(3.3)], row_h=0.48)
    footer(s, 4)

    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Три формы", "Игра · игра-песня · песня с движением")
    picture(s, 5, Inches(0.4), Inches(1.15), Inches(6.6), Inches(4.6))
    table(s, Inches(7.2), Inches(1.15), Inches(5.7), [
        ["Форма", "Опора"],
        ["Музыкальная игра", "правило + сигнал"],
        ["Игра-песня", "текст = сценарий"],
        ["Песня с движением", "фраза + жест"],
    ], [Inches(2.8), Inches(2.9)], row_h=0.55)
    add_textbox(s, Inches(7.2), Inches(4.0), Inches(5.7), Inches(1.8), "игра → слышать\nигра-песня → образ текста\nпесня+жест → фраза и жест", size=14, color=TEAL_DEEP)
    footer(s, 5)

    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Можно и нельзя", "Светофор безопасной игры")
    picture(s, 6, Inches(0.4), Inches(1.15), Inches(5.8), Inches(5.2))
    card(s, Inches(6.5), Inches(1.2), Inches(3.2), Inches(4.6), GREEN_SOFT, "Можно ✓", [
        "мягкий голос + жест", "короткое правило",
        "повтор и пауза", "посильное движение", "смена роли дозированно",
    ])
    card(s, Inches(9.9), Inches(1.2), Inches(3.0), Inches(4.6), RED_SOFT, "Нельзя ✕", [
        "крик поверх музыки", "длинная лекция",
        "бег без стопа", "сложная «эстрада»", "толчки в кругу",
    ])
    footer(s, 6)

    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Подбор материала", "Беру / не беру")
    picture(s, 7, Inches(0.4), Inches(1.15), Inches(6.8), Inches(4.8))
    card(s, Inches(7.4), Inches(1.2), Inches(2.7), Inches(4.5), LEAF, "Беру ✓", [
        "ясный образ", "короткий повтор", "2–4 движения", "есть задача", "безопасный стоп",
    ])
    card(s, Inches(10.3), Inches(1.2), Inches(2.6), Inches(4.5), RED_SOFT, "Не беру ✕", [
        "длинный текст", "взрослая «эстрада»", "сложная хореография", "просто весёлый трек", "без паузы",
    ])
    footer(s, 7)

    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Этапы подготовки и проведения", "Как готовить и как вести")
    picture(s, 8, Inches(0.4), Inches(1.15), Inches(7.0), Inches(5.0))
    table(s, Inches(7.6), Inches(1.15), Inches(5.3), [
        ["Этап", "Суть"],
        ["Интерес", "образ / вопрос"],
        ["Показ", "голос + жест"],
        ["Правило", "1–2 правила"],
        ["Проба", "фраза + движение"],
        ["Вместе", "соединение"],
        ["Характер", "тихо / бодро"],
        ["Вариация", "смена роли"],
        ["Стоп", "отдых"],
    ], [Inches(2.3), Inches(3.0)], row_h=0.42)
    footer(s, 8)

    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Упражнения-настройки", "20–40 секунд — одна задача")
    picture(s, 9, Inches(0.4), Inches(1.15), Inches(7.0), Inches(5.0))
    table(s, Inches(7.6), Inches(1.15), Inches(5.3), [
        ["Упражнение", "Задача"],
        ["Эхо-жест", "фраза + жест"],
        ["Стоп-игра", "реакция на паузу"],
        ["Тихо — бодро", "характер"],
        ["Кто ведущий", "внимание к показу"],
        ["Голос не кричит", "мягкий эталон"],
    ], [Inches(2.4), Inches(2.9)], row_h=0.5)
    footer(s, 9)

    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Банк материала", "Игры-песни и песни с движением")
    picture(s, 10, Inches(0.4), Inches(1.15), Inches(6.8), Inches(4.8))
    add_lines(s, Inches(7.5), Inches(1.3), Inches(5.3), Inches(5.0), [
        "Игры-песни:",
        "«Каравай», «Заинька»,",
        "«Где ты, зайка?»,",
        "«Мы на луг ходили»",
        "",
        "Песни с движением:",
        "дождик, солнышко,",
        "птички, животные",
        "",
        "Музыкальные игры:",
        "тихо/громко · характер",
    ], size=14, color=TEAL_DEEP)
    footer(s, 10)

    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Практика и чек-лист", "Мини-фрагмент 90–120 секунд")
    picture(s, 11, Inches(0.4), Inches(1.15), Inches(7.0), Inches(5.0))
    table(s, Inches(7.6), Inches(1.15), Inches(5.3), [
        ["Шаг", "Действие"],
        ["1", "назвать форму"],
        ["2", "упражнение / образ"],
        ["3", "показ + движение"],
        ["4", "повтор + можно/нельзя"],
        ["5", "мягкий стоп"],
    ], [Inches(1.0), Inches(4.3)], row_h=0.42)
    card(s, Inches(7.6), Inches(4.5), Inches(5.3), Inches(1.8), TEAL, "Рубрика Да/Нет", [
        "форма · мягкость · жест к фразе", "пауза · безопасность · возраст",
    ])
    footer(s, 11)

    s = prs.slides.add_slide(blank)
    bg(s, TEAL_DEEP)
    oval(s, Inches(-0.5), Inches(-0.6), Inches(2.5), Inches(2.5), TEAL)
    oval(s, Inches(11.5), Inches(5.5), Inches(2.5), Inches(2.5), CORAL)
    add_textbox(s, Inches(0.5), Inches(0.28), Inches(6.0), Inches(0.35), "Итог + творческие задания", size=14, color=GOLD, font="Calibri")
    add_textbox(s, Inches(0.5), Inches(0.7), Inches(6.0), Inches(0.9), "Формула игры\nи песни с движением", size=24, bold=True, color=WHITE)
    add_textbox(s, Inches(0.5), Inches(1.8), Inches(6.0), Inches(1.2), "Услышать.\nПоказать мягко.\nПовторить движением.\nНе кричать. Стоп.", size=15, color=SAND, font="Calibri")
    picture(s, 12, Inches(6.8), Inches(0.35), Inches(6.1), Inches(4.0))
    hw = [
        ("1. Таблица", "значение · 3 формы\nподбор · этапы\nупражнения"),
        ("2. Разбор + эссе", "2 материала\nпочему не хаос"),
        ("3. Сценарий", "настройка + показ\nповтор + стоп"),
    ]
    for i, (t, b) in enumerate(hw):
        rounded(s, Inches(0.4 + i * 4.25), Inches(4.7), Inches(4.0), Inches(1.7), WHITE)
        add_textbox(s, Inches(0.55 + i * 4.25), Inches(4.85), Inches(3.7), Inches(0.35), t, size=14, bold=True, color=TEAL_DEEP)
        add_lines(s, Inches(0.55 + i * 4.25), Inches(5.3), Inches(3.7), Inches(0.9), b.split("\n"), size=12, color=INK, spacing=2)
    add_textbox(s, Inches(0.5), Inches(6.7), Inches(12), Inches(0.3), "Игра начинается с вашего спокойного показа — голосом и телом.", size=13, color=GOLD, align=PP_ALIGN.CENTER, font="Calibri")

    prs.save(str(OUT))
    ART.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(ART))
    print(f"OK pptx={OUT} images={len(IMG)}")


if __name__ == "__main__":
    build()
