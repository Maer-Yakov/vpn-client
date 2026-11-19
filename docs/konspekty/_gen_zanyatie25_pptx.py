#!/usr/bin/env python3
"""Ready-to-show PowerPoint for artistic song image and preschool artistry."""

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
ASSETS = ROOT / "zanyatie-25-assets"
OUT = ROOT / "zanyatie-25-prezentaciya.pptx"
ART = Path("/opt/cursor/artifacts/zanyatie-25-prezentaciya.pptx")

IMG = {
    1: "z25-01-title.jpg",
    2: "z25-02-doors.jpg",
    3: "z25-03-goal.jpg",
    4: "z25-04-components.jpg",
    5: "z25-05-ages.jpg",
    6: "z25-06-means.jpg",
    7: "z25-07-warmup.jpg",
    8: "z25-08-analysis.jpg",
    9: "z25-09-games.jpg",
    10: "z25-10-limits.jpg",
    11: "z25-11-micro.jpg",
    12: "z25-12-finale.jpg",
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
        f"Художественный образ песни · Голос · Мимика · Жест   {n}/{total}",
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
    add_textbox(s, Inches(0.5), Inches(0.35), Inches(6.2), Inches(0.35), "ДОШКОЛЬНЫЙ ВОЗРАСТ", size=13, color=GOLD, font="Calibri")
    add_textbox(s, Inches(0.5), Inches(0.85), Inches(6.2), Inches(1.8), "Художественный образ\nпесни и артистизм", size=28, bold=True, color=WHITE)
    add_textbox(s, Inches(0.5), Inches(2.9), Inches(6.2), Inches(0.5), "Естественная выразительность — голос, лицо, один жест", size=13, color=SAND, font="Calibri")
    add_textbox(s, Inches(0.5), Inches(3.5), Inches(6.2), Inches(1.0), "настроение → мягкий голос →\nлицо → 1 жест → короткая игра", size=14, color=WHITE, font="Calibri")
    picture(s, 1, Inches(7.0), Inches(0.6), Inches(5.8), Inches(5.5))
    add_textbox(s, Inches(0.5), Inches(6.5), Inches(12), Inches(0.3), "Ветлугина · Радынова · Метлов · «Ладушки» · театрализация в ДОУ", size=12, color=SAND, font="Calibri")

    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Образ или «просто текст»?", "Чем отличается выразительное пение")
    picture(s, 2, Inches(0.45), Inches(1.2), Inches(6.6), Inches(4.8))
    table(s, Inches(7.3), Inches(1.2), Inches(5.5), [
        ["Это", "Не это"],
        ["мягкая выразительность", "крик «для эмоций»"],
        ["1–2 ясных средства", "гора жестов"],
        ["игра и образ", "взрослый театр"],
        ["проживание настроения", "штампы без смысла"],
    ], [Inches(2.8), Inches(2.7)], row_h=0.55)
    add_textbox(s, Inches(7.3), Inches(5.1), Inches(5.5), Inches(1.0), "Артистизм — не громкость\nи не гримаса.", size=15, bold=True, color=TEAL_DEEP)
    footer(s, 2)

    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Чему учимся сегодня", "Цель и продукт")
    steps = ["Образ и артистизм", "Компоненты образа", "Эмоция · мимика · жест · голос", "Анализ песни", "Игры на артистизм", "Микропреподавание"]
    for i, t in enumerate(steps):
        y = Inches(1.2 + i * 0.7)
        oval(s, Inches(0.5), y, Inches(0.45), Inches(0.45), TEAL if i % 2 == 0 else LEAF)
        add_textbox(s, Inches(0.5), y + Inches(0.07), Inches(0.45), Inches(0.3), str(i + 1), size=13, bold=True, color=WHITE, align=PP_ALIGN.CENTER, font="Calibri")
        add_textbox(s, Inches(1.15), y + Inches(0.07), Inches(5.8), Inches(0.4), t, size=15, color=INK)
    picture(s, 3, Inches(7.3), Inches(1.2), Inches(5.5), Inches(5.2))
    footer(s, 3)

    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Компоненты художественного образа", "Из чего складывается образ песни")
    picture(s, 4, Inches(0.4), Inches(1.15), Inches(6.8), Inches(4.5))
    table(s, Inches(7.4), Inches(1.15), Inches(5.5), [
        ["Компонент", "Вопрос"],
        ["Герой", "кто говорит?"],
        ["Настроение", "какое чувство?"],
        ["Музыка", "как звучит?"],
        ["Голос", "как поём?"],
        ["Мимика / жест", "что видно?"],
        ["Игровой приём", "чем помочь?"],
    ], [Inches(2.4), Inches(3.1)], row_h=0.48)
    footer(s, 4)

    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Артистизм по возрасту", "Какой уровень посилен")
    picture(s, 5, Inches(0.4), Inches(1.15), Inches(6.6), Inches(4.6))
    table(s, Inches(7.2), Inches(1.15), Inches(5.7), [
        ["Возраст", "Акцент"],
        ["1,5–3", "настроение + показ"],
        ["3–5", "герой + 1 жест"],
        ["5–7", "мини-роли 20–40 сек"],
    ], [Inches(1.8), Inches(3.9)], row_h=0.7)
    add_textbox(s, Inches(7.2), Inches(4.6), Inches(5.7), Inches(1.5), "Чем младше — тем яснее\nодно настроение.", size=15, bold=True, color=TEAL_DEEP)
    footer(s, 5)

    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Эмоция · мимика · жест · голос", "Связка средств выразительности")
    picture(s, 6, Inches(0.4), Inches(1.15), Inches(6.6), Inches(4.6))
    table(s, Inches(7.2), Inches(1.15), Inches(5.7), [
        ["Средство", "Риск"],
        ["Эмоция", "наигранность"],
        ["Мимика", "гримасы"],
        ["Жест", "хаос движений"],
        ["Голос", "крик «для эмоций»"],
    ], [Inches(2.3), Inches(3.4)], row_h=0.55)
    add_textbox(s, Inches(7.2), Inches(5.0), Inches(5.7), Inches(1.0), "Сначала настроение,\nпотом мягкий голос.", size=14, bold=True, color=TEAL_DEEP)
    footer(s, 6)

    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Практическая разминка", "1–2 минуты до выразительности")
    picture(s, 7, Inches(0.4), Inches(1.15), Inches(7.0), Inches(5.0))
    table(s, Inches(7.6), Inches(1.15), Inches(5.3), [
        ["Упражнение", "Задача"],
        ["Плечи / кисти", "снять зажим"],
        ["Зевота-улыбка", "свобода лица"],
        ["Мягкие гласные", "артикуляция"],
        ["Эхо настроения", "характер"],
        ["Жест-подпись", "1 жест"],
        ["Стоп", "мгновенно мягко"],
    ], [Inches(2.5), Inches(2.8)], row_h=0.48)
    footer(s, 7)

    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Анализ образа песни", "Карточка анализа")
    picture(s, 8, Inches(0.4), Inches(1.15), Inches(7.0), Inches(5.0))
    add_lines(s, Inches(7.6), Inches(1.3), Inches(5.2), Inches(5.0), [
        "О чём / кто герой?",
        "Настроение",
        "Характер музыки",
        "Голос",
        "Мимика + 1 жест",
        "Игровой приём",
        "Риск",
        "",
        "вход → слушание → разбор",
        "→ фраза → средства → стоп",
    ], size=14, color=TEAL_DEEP)
    footer(s, 8)

    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Игры на артистизм", "Банк коротких приёмов")
    picture(s, 9, Inches(0.4), Inches(1.15), Inches(7.0), Inches(5.0))
    table(s, Inches(7.6), Inches(1.15), Inches(5.3), [
        ["Игра", "Задача"],
        ["Угадай настроение", "слух к характеру"],
        ["Жест-герой", "1 жест"],
        ["Эхо в характере", "мягкая выразительность"],
        ["Кто поёт?", "угадать героя"],
        ["Тихий спектакль", "не громкостью"],
        ["Передай образ", "очередь 20–30 сек"],
    ], [Inches(2.6), Inches(2.7)], row_h=0.48)
    footer(s, 9)

    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Можно и нельзя", "Границы артистизма в ДОУ")
    picture(s, 10, Inches(0.4), Inches(1.15), Inches(5.8), Inches(5.2))
    card(s, Inches(6.5), Inches(1.2), Inches(3.2), Inches(4.6), GREEN_SOFT, "Можно ✓", [
        "1 ясное настроение", "1 жест-подпись",
        "мягкий эталон", "короткий прогон", "похвала за ясность",
    ])
    card(s, Inches(9.9), Inches(1.2), Inches(3.0), Inches(4.6), RED_SOFT, "Нельзя ✕", [
        "крик «для эмоций»", "гора жестов",
        "начинать с костюмов", "длинный спектакль", "стыд за «неартистов»",
    ])
    footer(s, 10)

    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Микропреподавание", "Фрагмент 90–120 секунд")
    picture(s, 11, Inches(0.4), Inches(1.15), Inches(7.0), Inches(5.0))
    table(s, Inches(7.6), Inches(1.15), Inches(5.3), [
        ["Шаг", "Действие"],
        ["1", "вход в образ"],
        ["2", "мягкий показ"],
        ["3", "фраза + 1 средство"],
        ["4", "короткий прогон"],
        ["5", "мягкий стоп"],
    ], [Inches(1.0), Inches(4.3)], row_h=0.42)
    card(s, Inches(7.6), Inches(4.5), Inches(5.3), Inches(1.8), TEAL, "Рубрика Да/Нет", [
        "настроение понятно · голос мягкий", "1 жест · коротко · есть стоп",
    ])
    footer(s, 11)

    s = prs.slides.add_slide(blank)
    bg(s, TEAL_DEEP)
    oval(s, Inches(-0.5), Inches(-0.6), Inches(2.5), Inches(2.5), TEAL)
    oval(s, Inches(11.5), Inches(5.5), Inches(2.5), Inches(2.5), CORAL)
    add_textbox(s, Inches(0.5), Inches(0.28), Inches(6.0), Inches(0.35), "Итог + творческие задания", size=14, color=GOLD, font="Calibri")
    add_textbox(s, Inches(0.5), Inches(0.7), Inches(6.0), Inches(1.1), "Формула работы\nнад образом", size=26, bold=True, color=WHITE)
    add_textbox(s, Inches(0.5), Inches(2.0), Inches(6.0), Inches(1.5), "Понятное настроение.\nМягкий голос.\nЛицо.\n1 жест.\nКороткая игра.", size=14, color=SAND, font="Calibri")
    picture(s, 12, Inches(6.8), Inches(0.35), Inches(6.1), Inches(4.0))
    hw = [
        ("1. Таблица + разбор", "компоненты · средства\nкарточка анализа песни"),
        ("2. Эссе + сценарий", "не воспитывать криком\nвход → жест → стоп"),
        ("3. Картотека", "6 позиций\nс предостережением"),
    ]
    for i, (t, b) in enumerate(hw):
        rounded(s, Inches(0.4 + i * 4.25), Inches(4.7), Inches(4.0), Inches(1.7), WHITE)
        add_textbox(s, Inches(0.55 + i * 4.25), Inches(4.85), Inches(3.7), Inches(0.35), t, size=14, bold=True, color=TEAL_DEEP)
        add_lines(s, Inches(0.55 + i * 4.25), Inches(5.3), Inches(3.7), Inches(0.9), b.split("\n"), size=12, color=INK, spacing=2)
    add_textbox(s, Inches(0.5), Inches(6.7), Inches(12), Inches(0.3), "Не сцена ради сцены — а понятная, добрая выразительность.", size=13, color=GOLD, align=PP_ALIGN.CENTER, font="Calibri")

    prs.save(str(OUT))
    ART.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(ART))
    print(f"OK pptx={OUT} images={len(IMG)}")


if __name__ == "__main__":
    build()
