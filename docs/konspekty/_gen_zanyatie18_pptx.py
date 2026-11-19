#!/usr/bin/env python3
"""Ready-to-show PowerPoint for lesson 18 — singing ages 1–3."""

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
ASSETS = ROOT / "zanyatie-18-assets"
OUT = ROOT / "zanyatie-18-prezentaciya.pptx"
ART = Path("/opt/cursor/artifacts/zanyatie-18-prezentaciya.pptx")

IMG = {
    1: "z18-01-title.jpg",
    2: "z18-02-doors.jpg",
    3: "z18-03-goal.jpg",
    4: "z18-04-spheres.jpg",
    5: "z18-05-ages.jpg",
    6: "z18-06-traffic.jpg",
    7: "z18-07-tasks.jpg",
    8: "z18-08-stages.jpg",
    9: "z18-09-exercises.jpg",
    10: "z18-10-repertoire.jpg",
    11: "z18-11-training.jpg",
    12: "z18-12-finale.jpg",
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
        f"Занятие 18 · Пение 1–3 лет · Слушание · Подхват · Пауза   {n}/{total}",
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
    add_textbox(s, Inches(0.5), Inches(0.35), Inches(6.2), Inches(0.35), "ЗАНЯТИЕ 18 · ПЕНИЕ РАННЕГО ВОЗРАСТА", size=13, color=GOLD, font="Calibri")
    add_textbox(s, Inches(0.5), Inches(0.85), Inches(6.2), Inches(1.6), "Пение с детьми\nот года до 3 лет\nв детском саду", size=28, bold=True, color=WHITE)
    add_textbox(s, Inches(0.5), Inches(2.8), Inches(6.2), Inches(0.4), "Не «весь куплет» — слушание и мягкий подхват", size=14, color=SAND, font="Calibri")
    add_textbox(s, Inches(0.5), Inches(3.4), Inches(6.2), Inches(0.8), "услышал → откликнулся →\nподхватил звук / слог / конец", size=14, color=WHITE, font="Calibri")
    picture(s, 1, Inches(7.0), Inches(0.6), Inches(5.8), Inches(5.5))
    add_textbox(s, Inches(0.5), Inches(6.5), Inches(12), Inches(0.3), "Ветлугина · Бабаджан · Дзержинская · Метлов · «Ладушки»", size=12, color=SAND, font="Calibri")

    # 2
    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Чем пение до 3 лет особенное", "Слушать и подхватывать — не сдавать номер")
    picture(s, 2, Inches(0.45), Inches(1.2), Inches(6.6), Inches(4.8))
    table(s, Inches(7.3), Inches(1.2), Inches(5.5), [
        ["1–3 года", "3–4 и позже"],
        ["взрослый несёт мелодию", "дети чаще подпевают"],
        ["слушание + звукоподражание", "разучивание по фразам"],
        ["попытка 20–60 сек", "песня чуть длиннее"],
        ["высокий риск крика", "контроль лучше"],
    ], [Inches(2.7), Inches(2.8)], row_h=0.55)
    add_textbox(s, Inches(7.3), Inches(5.1), Inches(5.5), Inches(1.0), "Важнее желание откликаться,\nчем идеальная нота.", size=15, bold=True, color=TEAL_DEEP)
    footer(s, 2)

    # 3
    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Чему учимся сегодня", "Цель и продукт занятия")
    steps = [
        "Значение пения для 1–3 лет",
        "Особенности внутри возраста",
        "Задачи обучения пению",
        "Приёмы и этапы разучивания",
        "Короткие упражнения",
        "Посильный репертуар",
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
    title_block(s, "Значение пения в развитии ребёнка", "Мост между речью, слухом и контактом")
    picture(s, 4, Inches(0.4), Inches(1.15), Inches(6.8), Inches(4.5))
    table(s, Inches(7.4), Inches(1.15), Inches(5.5), [
        ["Сфера", "Что развивается"],
        ["Слух", "голос, начало/конец"],
        ["Речь", "слоги, звукоподражания"],
        ["Дыхание", "спокойный выдох"],
        ["Эмоции", "«со мной поют»"],
        ["Общение", "контакт, доверие"],
        ["Память", "знакомая потешка"],
    ], [Inches(2.2), Inches(3.3)], row_h=0.48)
    footer(s, 4)

    # 5
    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Возрастные особенности внутри 1–3 лет", "Один возраст — три ступени")
    picture(s, 5, Inches(0.4), Inches(1.15), Inches(6.6), Inches(4.6))
    table(s, Inches(7.2), Inches(1.15), Inches(5.7), [
        ["Возраст", "Что доступно"],
        ["1–1,5", "слушание, улыбка, «а-а»"],
        ["1,5–2", "звук, конец слога"],
        ["2–3", "короткая фраза, повтор"],
        ["Голос", "узкий диапазон"],
        ["Фраза", "взрослый держит мелодию"],
        ["Внимание", "20–60 сек + пауза"],
    ], [Inches(2.0), Inches(3.7)], row_h=0.48)
    footer(s, 5)

    # 6
    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Можно и нельзя для голоса малыша", "Светофор бережного пения")
    picture(s, 6, Inches(0.4), Inches(1.15), Inches(5.8), Inches(5.2))
    card(s, Inches(6.5), Inches(1.2), Inches(3.2), Inches(4.6), GREEN_SOFT, "Можно ✓", [
        "мягкий звук взрослого", "слушать и подхватывать",
        "короткая потешка", "игрушка и ладушки", "пауза и смена",
    ])
    card(s, Inches(9.9), Inches(1.2), Inches(3.0), Inches(4.6), RED_SOFT, "Нельзя ✕", [
        "крик, давить горлом", "соло «как на сцене»",
        "длинный куплет", "долбить без паузы", "сложная хореография",
    ])
    footer(s, 6)

    # 7
    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Задачи обучения пению", "Семь простых задач до 3 лет")
    picture(s, 7, Inches(0.4), Inches(1.15), Inches(7.0), Inches(5.0))
    add_lines(s, Inches(7.7), Inches(1.3), Inches(5.2), Inches(5.0), [
        "1. Интерес к голосу взрослого",
        "2. Слушание короткой песни",
        "3. Звукоподражание и подпевание",
        "4. Голос + образ + жест",
        "5. Небольшой посильный репертуар",
        "6. Беречь голос: коротко + пауза",
        "7. Готовить почву после 3 лет",
        "",
        "интерес → слушание",
        "→ звук/слог → фраза",
    ], size=15, color=TEAL_DEEP)
    footer(s, 7)

    # 8
    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Приёмы и этапы разучивания", "Как вести пение в 1–3 года")
    picture(s, 8, Inches(0.4), Inches(1.15), Inches(7.0), Inches(5.0))
    table(s, Inches(7.6), Inches(1.15), Inches(5.3), [
        ["Этап", "Суть"],
        ["1. Интерес", "игрушка / жест"],
        ["2. Показ", "дети слушают"],
        ["3. Узнавание", "кто / что"],
        ["4. Подхват", "звук · слог · конец"],
        ["5. Игра", "закрепление"],
        ["6. Стоп", "отдых голоса"],
    ], [Inches(2.0), Inches(3.3)], row_h=0.48)
    footer(s, 8)

    # 9
    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Упражнения для певческих навыков", "15–30 секунд — одна задача")
    picture(s, 9, Inches(0.4), Inches(1.15), Inches(7.0), Inches(5.0))
    table(s, Inches(7.6), Inches(1.15), Inches(5.3), [
        ["Навык", "Упражнение"],
        ["Слушание", "игрушка «спит»"],
        ["Дыхание", "подуть на платочек"],
        ["Мягкий звук", "тихое «а-а» / «мм»"],
        ["Подражание", "«мяу», «ку-ку»"],
        ["Подхват", "последний слог"],
        ["Жест + голос", "ладушки"],
    ], [Inches(2.2), Inches(3.1)], row_h=0.5)
    footer(s, 9)

    # 10
    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Подбор песенного репертуара", "Беру / не беру для 1–3 лет")
    picture(s, 10, Inches(0.4), Inches(1.15), Inches(6.8), Inches(4.8))
    card(s, Inches(7.4), Inches(1.2), Inches(2.7), Inches(4.5), LEAF, "Беру ✓", [
        "короткая с повтором", "близкий образ", "мягкая мелодия", "понятный текст", "петь на коврике",
    ])
    card(s, Inches(10.3), Inches(1.2), Inches(2.6), Inches(4.5), RED_SOFT, "Не беру ✕", [
        "длинный шлягер", "взрослый текст", "широкие скачки", "крикливый пик", "сцена и строй",
    ])
    footer(s, 10)

    # 11
    s = prs.slides.add_slide(blank)
    bg(s)
    title_block(s, "Практика и чек-лист студента", "Мини-фрагмент 80–100 секунд")
    picture(s, 11, Inches(0.4), Inches(1.15), Inches(7.0), Inches(5.0))
    table(s, Inches(7.6), Inches(1.15), Inches(5.3), [
        ["Шаг", "Действие"],
        ["1", "интерес / упражнение"],
        ["2", "показ + подхват"],
        ["3", "можно + нельзя"],
        ["4", "мягкий стоп"],
    ], [Inches(1.0), Inches(4.3)], row_h=0.48)
    card(s, Inches(7.6), Inches(4.0), Inches(5.3), Inches(2.3), TEAL, "Рубрика Да/Нет", [
        "образ · мягкость · краткость", "пауза · без крика", "это именно для 1–3 лет",
    ])
    footer(s, 11)

    # 12
    s = prs.slides.add_slide(blank)
    bg(s, TEAL_DEEP)
    oval(s, Inches(-0.5), Inches(-0.6), Inches(2.5), Inches(2.5), TEAL)
    oval(s, Inches(11.5), Inches(5.5), Inches(2.5), Inches(2.5), CORAL)
    add_textbox(s, Inches(0.5), Inches(0.28), Inches(6.0), Inches(0.35), "Итог + творческие задания", size=14, color=GOLD, font="Calibri")
    add_textbox(s, Inches(0.5), Inches(0.7), Inches(6.0), Inches(0.9), "Формула пения\nдо 3 лет", size=26, bold=True, color=WHITE)
    add_textbox(s, Inches(0.5), Inches(1.8), Inches(6.0), Inches(1.1), "Ласковый голос педагога.\nСлушание.\nКороткий подхват.\nПауза.", size=15, color=SAND, font="Calibri")
    picture(s, 12, Inches(6.8), Inches(0.35), Inches(6.1), Inches(4.0))
    hw = [
        ("1. Таблица", "значение · 1–1,5/1,5–2/2–3\nзадачи · этапы\nупражнения · репертуар"),
        ("2. Разбор потешки", "этапы + дозировка\nв секундах"),
        ("3. Эссе + режим", "почему слушание важнее\n«всего куплета» + 2 мин"),
    ]
    for i, (t, b) in enumerate(hw):
        rounded(s, Inches(0.4 + i * 4.25), Inches(4.7), Inches(4.0), Inches(1.7), WHITE)
        add_textbox(s, Inches(0.55 + i * 4.25), Inches(4.85), Inches(3.7), Inches(0.35), t, size=14, bold=True, color=TEAL_DEEP)
        add_lines(s, Inches(0.55 + i * 4.25), Inches(5.3), Inches(3.7), Inches(0.9), b.split("\n"), size=12, color=INK, spacing=2)
    add_textbox(s, Inches(0.5), Inches(6.7), Inches(12), Inches(0.3), "Берегите голос малыша — пение начнётся с вашего мягкого «рядом».", size=13, color=GOLD, align=PP_ALIGN.CENTER, font="Calibri")

    prs.save(str(OUT))
    ART.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(ART))
    print(f"OK pptx={OUT} images={len(IMG)}")


if __name__ == "__main__":
    build()
