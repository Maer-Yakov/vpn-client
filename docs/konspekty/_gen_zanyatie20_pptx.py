#!/usr/bin/env python3
"""Ready-to-show PowerPoint for singing ages 5–7."""

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
ASSETS = ROOT / "zanyatie-20-assets"
OUT = ROOT / "zanyatie-20-prezentaciya.pptx"
ART = Path("/opt/cursor/artifacts/zanyatie-20-prezentaciya.pptx")

IMG = {
    1: "z20-01-title.jpg",
    2: "z20-02-doors.jpg",
    3: "z20-03-goal.jpg",
    4: "z20-04-spheres.jpg",
    5: "z20-05-ages.jpg",
    6: "z20-06-traffic.jpg",
    7: "z20-07-tasks.jpg",
    8: "z20-08-stages.jpg",
    9: "z20-09-exercises.jpg",
    10: "z20-10-repertoire.jpg",
    11: "z20-11-training.jpg",
    12: "z20-12-finale.jpg",
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
        f"Пение 5–7 лет · Мягкий эталон · Фраза · Унисон · Пауза   {n}/{total}",
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
    add_textbox(s, Inches(0.5), Inches(0.35), Inches(6.2), Inches(0.35), "СТАРШИЙ ДОШКОЛЬНЫЙ ВОЗРАСТ", size=13, color=GOLD, font="Calibri")
    add_textbox(s, Inches(0.5), Inches(0.85), Inches(6.2), Inches(1.5), "Пение с детьми\nот 5–7 лет\nв детском саду", size=28, bold=True, color=WHITE)
    add_textbox(s, Inches(0.5), Inches(2.8), Inches(6.2), Inches(0.4), "Не сила голоса — мягкий эталон, фраза, унисон и пауза", size=14, color=SAND, font="Calibri")
    add_textbox(s, Inches(0.5), Inches(3.4), Inches(6.2), Inches(0.8), "мягкий показ → фраза →\nвыразительность → унисон → пауза", size=14, color=WHITE, font="Calibri")
    picture(s, 1, Inches(7.0), Inches(0.6), Inches(5.8), Inches(5.5))
    add_textbox(s, Inches(0.5), Inches(6.5), Inches(12), Inches(0.3), "Ветлугина · Метлов · Радынова · «Ладушки» · Орлова / Бекина", size=12, color=SAND, font="Calibri")

    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Чем пение в 5–7 лет особенное", "От подхвата — к выразительности и унисону")
    picture(s, 2, Inches(0.45), Inches(1.2), Inches(6.6), Inches(4.8))
    table(s, Inches(7.3), Inches(1.2), Inches(5.5), [
        ["3–5 лет", "5–7 лет"],
        ["больше подхват", "больше самостоятельный повтор"],
        ["короткая фраза", "куплет–припев возможен"],
        ["характер намечается", "характер и динамика"],
        ["сильная опора на взрослого", "дети держат увереннее"],
    ], [Inches(2.7), Inches(2.8)], row_h=0.55)
    add_textbox(s, Inches(7.3), Inches(5.1), Inches(5.5), Inches(1.0), "Увереннее — не значит\nгромче любой ценой.", size=15, bold=True, color=TEAL_DEEP)
    footer(s, 2)

    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Чему учимся сегодня", "Цель и продукт")
    steps = ["Значение пения", "Особенности 5–7 лет", "Задачи обучения", "Приёмы и этапы", "Упражнения", "Репертуар"]
    for i, t in enumerate(steps):
        y = Inches(1.2 + i * 0.7)
        oval(s, Inches(0.5), y, Inches(0.45), Inches(0.45), TEAL if i % 2 == 0 else LEAF)
        add_textbox(s, Inches(0.5), y + Inches(0.07), Inches(0.45), Inches(0.3), str(i + 1), size=13, bold=True, color=WHITE, align=PP_ALIGN.CENTER, font="Calibri")
        add_textbox(s, Inches(1.15), y + Inches(0.07), Inches(5.8), Inches(0.4), t, size=15, color=INK)
    picture(s, 3, Inches(7.3), Inches(1.2), Inches(5.5), Inches(5.2))
    footer(s, 3)

    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Значение пения", "Развитие и готовность к школе")
    picture(s, 4, Inches(0.4), Inches(1.15), Inches(6.8), Inches(4.5))
    table(s, Inches(7.4), Inches(1.15), Inches(5.5), [
        ["Сфера", "Что развивается"],
        ["Слух", "интонация, унисон"],
        ["Голос", "фраза, выразительность"],
        ["Речь", "дикция, дыхание"],
        ["Эмоции", "характер, настроение"],
        ["Общение", "петь вместе"],
        ["К школе", "самоконтроль, слух"],
    ], [Inches(2.2), Inches(3.3)], row_h=0.48)
    footer(s, 4)

    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Возрастные особенности 5–7 лет", "Что реально доступно голосу")
    picture(s, 5, Inches(0.4), Inches(1.15), Inches(6.6), Inches(4.6))
    table(s, Inches(7.2), Inches(1.15), Inches(5.7), [
        ["Особенность", "Для педагога"],
        ["Диапазон шире", "без крайних пиков"],
        ["Фраза длиннее", "работа над фразой"],
        ["Интонация точнее", "мягкий повтор"],
        ["Внимание устойчивее", "куплет–припев"],
        ["Любят выразительность", "характер, динамика"],
        ["Риск форсирования", "особенно на праздниках"],
    ], [Inches(2.7), Inches(3.0)], row_h=0.48)
    footer(s, 5)

    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Можно и нельзя для голоса", "Светофор бережного пения")
    picture(s, 6, Inches(0.4), Inches(1.15), Inches(5.8), Inches(5.2))
    card(s, Inches(6.5), Inches(1.2), Inches(3.2), Inches(4.6), GREEN_SOFT, "Можно ✓", [
        "мягкий естественный звук", "фразы, характер, унисон",
        "удобная поза, паузы", "посильная песня", "мягкое уточнение",
    ])
    card(s, Inches(9.9), Inches(1.2), Inches(3.0), Inches(4.6), RED_SOFT, "Нельзя ✕", [
        "крик, давить горлом", "соло «как у взрослых»",
        "долгое пение без отдыха", "шлягер с высоким пиком", "стыдить за интонацию",
    ])
    footer(s, 6)

    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Задачи обучения пению", "Восемь проверяемых задач")
    picture(s, 7, Inches(0.4), Inches(1.15), Inches(7.0), Inches(5.0))
    add_lines(s, Inches(7.7), Inches(1.3), Inches(5.2), Inches(5.0), [
        "1. Желание петь вместе",
        "2. Мягкое звукообразование",
        "3. Точность интонации",
        "4. Слушать начало / конец",
        "5. Дикция и дыхание во фразе",
        "6. Характер песни",
        "7. Посильный репертуар",
        "8. Беречь голос",
        "",
        "желание → мягкий звук",
        "→ фраза/унисон → характер",
    ], size=14, color=TEAL_DEEP)
    footer(s, 7)

    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Приёмы и этапы разучивания", "Как вести песню в 5–7 лет")
    picture(s, 8, Inches(0.4), Inches(1.15), Inches(7.0), Inches(5.0))
    table(s, Inches(7.6), Inches(1.15), Inches(5.3), [
        ["Этап", "Суть"],
        ["Интерес", "образ / установка"],
        ["Показ", "педагог поёт"],
        ["Смысл", "характер, вопросы"],
        ["Фразы", "короткий повтор"],
        ["Вместе", "соединение"],
        ["Выразительность", "динамика / образ"],
        ["Унисон", "слушать друг друга"],
        ["Стоп", "отдых голоса"],
    ], [Inches(2.3), Inches(3.0)], row_h=0.42)
    footer(s, 8)

    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Упражнения для певческих навыков", "20–40 секунд — одна задача")
    picture(s, 9, Inches(0.4), Inches(1.15), Inches(7.0), Inches(5.0))
    table(s, Inches(7.6), Inches(1.15), Inches(5.3), [
        ["Навык", "Упражнение"],
        ["Дыхание", "платочек; фраза на выдохе"],
        ["Мягкая атака", "«мм», «ау», «ля»"],
        ["Интонация", "попевка / ступеньки"],
        ["Унисон", "споём одинаково"],
        ["Дикция", "потешка шёпотом→голос"],
        ["Характер", "ласково / бодро"],
    ], [Inches(2.2), Inches(3.1)], row_h=0.5)
    footer(s, 9)

    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Подбор песенного репертуара", "Беру / не беру для 5–7 лет")
    picture(s, 10, Inches(0.4), Inches(1.15), Inches(6.8), Inches(4.8))
    card(s, Inches(7.4), Inches(1.2), Inches(2.7), Inches(4.5), LEAF, "Беру ✓", [
        "песня старшей группы", "ясный образ", "мягкая мелодия", "куплет–припев", "есть цель",
    ])
    card(s, Inches(10.3), Inches(1.2), Inches(2.6), Inches(4.5), RED_SOFT, "Не беру ✕", [
        "взрослый шлягер", "чуждый текст", "высокий пик", "широкие скачки", "просто из интернета",
    ])
    footer(s, 10)

    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Практика и чек-лист", "Мини-фрагмент 90–120 секунд")
    picture(s, 11, Inches(0.4), Inches(1.15), Inches(7.0), Inches(5.0))
    table(s, Inches(7.6), Inches(1.15), Inches(5.3), [
        ["Шаг", "Действие"],
        ["1", "упражнение 20–30 сек"],
        ["2", "показ 1–2 фраз + повтор"],
        ["3", "характер или унисон"],
        ["4", "можно + нельзя"],
        ["5", "мягкий стоп"],
    ], [Inches(1.0), Inches(4.3)], row_h=0.42)
    card(s, Inches(7.6), Inches(4.5), Inches(5.3), Inches(1.8), TEAL, "Рубрика Да/Нет", [
        "мягкость · фразы · характер/унисон", "пауза · без крика · для 5–7 лет",
    ])
    footer(s, 11)

    s = prs.slides.add_slide(blank)
    bg(s, TEAL_DEEP)
    oval(s, Inches(-0.5), Inches(-0.6), Inches(2.5), Inches(2.5), TEAL)
    oval(s, Inches(11.5), Inches(5.5), Inches(2.5), Inches(2.5), CORAL)
    add_textbox(s, Inches(0.5), Inches(0.28), Inches(6.0), Inches(0.35), "Итог + творческие задания", size=14, color=GOLD, font="Calibri")
    add_textbox(s, Inches(0.5), Inches(0.7), Inches(6.0), Inches(0.9), "Формула пения\n5–7 лет", size=26, bold=True, color=WHITE)
    add_textbox(s, Inches(0.5), Inches(1.8), Inches(6.0), Inches(1.2), "Мягкий эталон.\nПосильная песня.\nФраза и выразительность.\nУнисон без крика.", size=15, color=SAND, font="Calibri")
    picture(s, 12, Inches(6.8), Inches(0.35), Inches(6.1), Inches(4.0))
    hw = [
        ("1. Таблица", "значение · 5–7 лет\nзадачи · этапы\nупражнения · репертуар"),
        ("2. Разбор + эссе", "этапы + дозировка\nпочему не крик/фонограмма"),
        ("3. Сценарий", "упражнение + фразы\nхарактер/унисон + стоп"),
    ]
    for i, (t, b) in enumerate(hw):
        rounded(s, Inches(0.4 + i * 4.25), Inches(4.7), Inches(4.0), Inches(1.7), WHITE)
        add_textbox(s, Inches(0.55 + i * 4.25), Inches(4.85), Inches(3.7), Inches(0.35), t, size=14, bold=True, color=TEAL_DEEP)
        add_lines(s, Inches(0.55 + i * 4.25), Inches(5.3), Inches(3.7), Inches(0.9), b.split("\n"), size=12, color=INK, spacing=2)
    add_textbox(s, Inches(0.5), Inches(6.7), Inches(12), Inches(0.3), "Берегите голос — пение 5–7 лет начнётся с правильного эталона.", size=13, color=GOLD, align=PP_ALIGN.CENTER, font="Calibri")

    prs.save(str(OUT))
    ART.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(ART))
    print(f"OK pptx={OUT} images={len(IMG)}")


if __name__ == "__main__":
    build()
