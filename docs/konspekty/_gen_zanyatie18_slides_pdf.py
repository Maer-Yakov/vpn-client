#!/usr/bin/env python3
"""Landscape slide-deck PDF twin for lesson 18 presentation."""

from pathlib import Path

from reportlab.lib.pagesizes import landscape
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

W, H = landscape((297 * mm, 210 * mm))
ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "zanyatie-18-assets"
OUT = ROOT / "zanyatie-18-prezentaciya.pdf"
ART = Path("/opt/cursor/artifacts/zanyatie-18-prezentaciya.pdf")

TEAL = (0.16, 0.48, 0.55)
TEAL_D = (0.10, 0.35, 0.42)
CORAL = (0.83, 0.48, 0.42)
GOLD = (0.79, 0.64, 0.31)
LEAF = (0.35, 0.56, 0.48)
CREAM = (0.97, 0.98, 0.99)
INK = (0.12, 0.18, 0.23)
MUTED = (0.35, 0.43, 0.47)
WHITE = (1, 1, 1)
SAND = (0.91, 0.94, 0.96)
SOFT = (0.89, 0.94, 0.95)
RED = (0.77, 0.36, 0.36)
GREEN = (0.29, 0.60, 0.48)

IMG = {i: ASSETS / name for i, name in [
    (1, "z18-01-title.jpg"), (2, "z18-02-doors.jpg"), (3, "z18-03-goal.jpg"),
    (4, "z18-04-spheres.jpg"), (5, "z18-05-ages.jpg"), (6, "z18-06-traffic.jpg"),
    (7, "z18-07-tasks.jpg"), (8, "z18-08-stages.jpg"), (9, "z18-09-exercises.jpg"),
    (10, "z18-10-repertoire.jpg"), (11, "z18-11-training.jpg"), (12, "z18-12-finale.jpg"),
]}


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


def footer(c, n, total=12):
    rgb(c, MUTED)
    c.setFont("DejaVu", 9)
    c.drawString(14 * mm, 8 * mm, f"Занятие 18 · Пение 1–3 лет · Слушание · Подхват · Пауза   {n}/{total}")


def title(c, text, sub=None):
    bar(c)
    rgb(c, TEAL_D)
    c.setFont("DejaVuBold", 18)
    c.drawString(14 * mm, H - 15 * mm, text)
    if sub:
        rgb(c, MUTED)
        c.setFont("DejaVu", 10)
        c.drawString(14 * mm, H - 22 * mm, sub)


def round_rect(c, x, y, w, h, color, r=8):
    rgb(c, color)
    c.roundRect(x, y, w, h, r, fill=1, stroke=0)


def draw_img(c, n, x, y, w, h):
    path = IMG[n]
    if path.exists():
        c.drawImage(str(path), x, y, width=w, height=h, preserveAspectRatio=True, anchor="c")


def text_block(c, x, y, lines, *, size=11, color=INK, leading=5.5 * mm, bold=False):
    rgb(c, color)
    c.setFont("DejaVuBold" if bold else "DejaVu", size)
    for i, line in enumerate(lines):
        c.drawString(x, y - i * leading, line)


def table_simple(c, x, y, rows, col_w, row_h=9 * mm):
    for r, row in enumerate(rows):
        xx = x
        for i, cell in enumerate(row):
            fill = TEAL if r == 0 else (SOFT if r % 2 else WHITE)
            round_rect(c, xx, y - (r + 1) * row_h, col_w[i], row_h - 1.2 * mm, fill, r=3)
            rgb(c, WHITE if r == 0 else INK)
            c.setFont("DejaVuBold" if r == 0 else "DejaVu", 9)
            c.drawString(xx + 2.5 * mm, y - (r + 1) * row_h + 3 * mm, cell[:42])
            xx += col_w[i]


def card(c, x, y, w, h, color, title_t, lines):
    round_rect(c, x, y, w, h, color, r=8)
    rgb(c, WHITE)
    c.setFont("DejaVuBold", 11)
    c.drawString(x + 3 * mm, y + h - 8 * mm, title_t)
    c.setFont("DejaVu", 9)
    for i, line in enumerate(lines):
        c.drawString(x + 3 * mm, y + h - 16 * mm - i * 6 * mm, line)


def build():
    fonts()
    c = canvas.Canvas(str(OUT), pagesize=(W, H))

    # 1
    bg(c, TEAL_D)
    rgb(c, GOLD)
    c.setFont("DejaVu", 11)
    c.drawString(14 * mm, H - 18 * mm, "ЗАНЯТИЕ 18 · ПЕНИЕ РАННЕГО ВОЗРАСТА")
    rgb(c, WHITE)
    c.setFont("DejaVuBold", 26)
    c.drawString(14 * mm, H - 35 * mm, "Пение с детьми")
    c.drawString(14 * mm, H - 48 * mm, "от года до 3 лет")
    c.drawString(14 * mm, H - 61 * mm, "в детском саду")
    rgb(c, SAND)
    c.setFont("DejaVu", 11)
    c.drawString(14 * mm, H - 78 * mm, "Не «весь куплет» — слушание и мягкий подхват")
    rgb(c, WHITE)
    c.drawString(14 * mm, H - 92 * mm, "услышал → откликнулся → подхватил")
    draw_img(c, 1, W - 145 * mm, 25 * mm, 130 * mm, 100 * mm)
    rgb(c, SAND)
    c.setFont("DejaVu", 9)
    c.drawString(14 * mm, 14 * mm, "Ветлугина · Бабаджан · Дзержинская · Метлов · «Ладушки»")
    c.showPage()

    # 2
    bg(c)
    title(c, "Чем пение до 3 лет особенное", "Слушать и подхватывать — не сдавать номер")
    draw_img(c, 2, 12 * mm, 28 * mm, 145 * mm, 105 * mm)
    table_simple(c, 165 * mm, H - 30 * mm, [
        ["1–3 года", "3–4 и позже"],
        ["взрослый несёт мелодию", "дети чаще подпевают"],
        ["слушание + звукоподражание", "разучивание по фразам"],
        ["попытка 20–60 сек", "песня чуть длиннее"],
        ["высокий риск крика", "контроль лучше"],
    ], [55 * mm, 55 * mm])
    text_block(c, 165 * mm, 45 * mm, ["Важнее желание откликаться,", "чем идеальная нота."], size=12, color=TEAL_D, bold=True)
    footer(c, 2)
    c.showPage()

    # 3
    bg(c)
    title(c, "Чему учимся сегодня", "Цель и продукт занятия")
    steps = [
        "Значение пения для 1–3 лет",
        "Особенности внутри возраста",
        "Задачи обучения пению",
        "Приёмы и этапы разучивания",
        "Короткие упражнения",
        "Посильный репертуар",
    ]
    for i, t in enumerate(steps):
        y = H - 40 * mm - i * 18 * mm
        round_rect(c, 14 * mm, y, 8 * mm, 8 * mm, TEAL if i % 2 == 0 else LEAF, r=4)
        rgb(c, WHITE)
        c.setFont("DejaVuBold", 10)
        c.drawCentredString(18 * mm, y + 2.2 * mm, str(i + 1))
        rgb(c, INK)
        c.setFont("DejaVu", 12)
        c.drawString(26 * mm, y + 2.2 * mm, t)
    draw_img(c, 3, 165 * mm, 28 * mm, 115 * mm, 110 * mm)
    footer(c, 3)
    c.showPage()

    # 4
    bg(c)
    title(c, "Значение пения в развитии ребёнка", "Мост между речью, слухом и контактом")
    draw_img(c, 4, 12 * mm, 30 * mm, 145 * mm, 100 * mm)
    table_simple(c, 165 * mm, H - 30 * mm, [
        ["Сфера", "Что развивается"],
        ["Слух", "голос, начало/конец"],
        ["Речь", "слоги, звукоподражания"],
        ["Дыхание", "спокойный выдох"],
        ["Эмоции", "«со мной поют»"],
        ["Общение", "контакт, доверие"],
        ["Память", "знакомая потешка"],
    ], [35 * mm, 75 * mm], row_h=12 * mm)
    footer(c, 4)
    c.showPage()

    # 5
    bg(c)
    title(c, "Возрастные особенности внутри 1–3 лет", "Один возраст — три ступени")
    draw_img(c, 5, 12 * mm, 30 * mm, 145 * mm, 100 * mm)
    table_simple(c, 165 * mm, H - 30 * mm, [
        ["Возраст", "Что доступно"],
        ["1–1,5", "слушание, улыбка, «а-а»"],
        ["1,5–2", "звук, конец слога"],
        ["2–3", "короткая фраза, повтор"],
        ["Голос", "узкий диапазон"],
        ["Фраза", "взрослый держит мелодию"],
        ["Внимание", "20–60 сек + пауза"],
    ], [30 * mm, 80 * mm], row_h=12 * mm)
    footer(c, 5)
    c.showPage()

    # 6
    bg(c)
    title(c, "Можно и нельзя для голоса малыша", "Светофор бережного пения")
    draw_img(c, 6, 12 * mm, 28 * mm, 120 * mm, 110 * mm)
    card(c, 145 * mm, 45 * mm, 65 * mm, 95 * mm, GREEN, "Можно ✓", [
        "мягкий звук взрослого", "слушать и подхватывать",
        "короткая потешка", "игрушка и ладушки", "пауза и смена",
    ])
    card(c, 218 * mm, 45 * mm, 60 * mm, 95 * mm, RED, "Нельзя ✕", [
        "крик, давить горлом", "соло «как на сцене»",
        "длинный куплет", "долбить без паузы", "сложная хореография",
    ])
    footer(c, 6)
    c.showPage()

    # 7
    bg(c)
    title(c, "Задачи обучения пению", "Семь простых задач до 3 лет")
    draw_img(c, 7, 12 * mm, 28 * mm, 150 * mm, 110 * mm)
    text_block(c, 170 * mm, H - 40 * mm, [
        "1. Интерес к голосу взрослого",
        "2. Слушание короткой песни",
        "3. Звукоподражание и подпевание",
        "4. Голос + образ + жест",
        "5. Небольшой посильный репертуар",
        "6. Беречь голос: коротко + пауза",
        "7. Готовить почву после 3 лет",
        "",
        "интерес → слушание → звук/слог",
    ], size=11, color=TEAL_D, leading=7 * mm, bold=True)
    footer(c, 7)
    c.showPage()

    # 8
    bg(c)
    title(c, "Приёмы и этапы разучивания", "Как вести пение в 1–3 года")
    draw_img(c, 8, 12 * mm, 28 * mm, 150 * mm, 110 * mm)
    table_simple(c, 170 * mm, H - 30 * mm, [
        ["Этап", "Суть"],
        ["1. Интерес", "игрушка / жест"],
        ["2. Показ", "дети слушают"],
        ["3. Узнавание", "кто / что"],
        ["4. Подхват", "звук · слог · конец"],
        ["5. Игра", "закрепление"],
        ["6. Стоп", "отдых голоса"],
    ], [35 * mm, 70 * mm], row_h=12 * mm)
    footer(c, 8)
    c.showPage()

    # 9
    bg(c)
    title(c, "Упражнения для певческих навыков", "15–30 секунд — одна задача")
    draw_img(c, 9, 12 * mm, 28 * mm, 150 * mm, 110 * mm)
    table_simple(c, 170 * mm, H - 30 * mm, [
        ["Навык", "Упражнение"],
        ["Слушание", "игрушка «спит»"],
        ["Дыхание", "подуть на платочек"],
        ["Мягкий звук", "тихое «а-а» / «мм»"],
        ["Подражание", "«мяу», «ку-ку»"],
        ["Подхват", "последний слог"],
        ["Жест + голос", "ладушки"],
    ], [40 * mm, 65 * mm], row_h=12 * mm)
    footer(c, 9)
    c.showPage()

    # 10
    bg(c)
    title(c, "Подбор песенного репертуара", "Беру / не беру для 1–3 лет")
    draw_img(c, 10, 12 * mm, 28 * mm, 145 * mm, 105 * mm)
    card(c, 165 * mm, 45 * mm, 55 * mm, 95 * mm, LEAF, "Беру ✓", [
        "короткая с повтором", "близкий образ", "мягкая мелодия",
        "понятный текст", "петь на коврике",
    ])
    card(c, 228 * mm, 45 * mm, 52 * mm, 95 * mm, RED, "Не беру ✕", [
        "длинный шлягер", "взрослый текст", "широкие скачки",
        "крикливый пик", "сцена и строй",
    ])
    footer(c, 10)
    c.showPage()

    # 11
    bg(c)
    title(c, "Практика и чек-лист студента", "Мини-фрагмент 80–100 секунд")
    draw_img(c, 11, 12 * mm, 28 * mm, 150 * mm, 110 * mm)
    table_simple(c, 170 * mm, H - 30 * mm, [
        ["Шаг", "Действие"],
        ["1", "интерес / упражнение"],
        ["2", "показ + подхват"],
        ["3", "можно + нельзя"],
        ["4", "мягкий стоп"],
    ], [20 * mm, 85 * mm], row_h=12 * mm)
    card(c, 170 * mm, 28 * mm, 105 * mm, 40 * mm, TEAL, "Рубрика Да/Нет", [
        "образ · мягкость · краткость", "пауза · без крика · для 1–3 лет",
    ])
    footer(c, 11)
    c.showPage()

    # 12
    bg(c, TEAL_D)
    rgb(c, GOLD)
    c.setFont("DejaVu", 11)
    c.drawString(14 * mm, H - 16 * mm, "Итог + творческие задания")
    rgb(c, WHITE)
    c.setFont("DejaVuBold", 22)
    c.drawString(14 * mm, H - 32 * mm, "Формула пения до 3 лет")
    rgb(c, SAND)
    c.setFont("DejaVu", 12)
    for i, line in enumerate(["Ласковый голос педагога.", "Слушание.", "Короткий подхват.", "Пауза."]):
        c.drawString(14 * mm, H - 48 * mm - i * 8 * mm, line)
    draw_img(c, 12, W - 145 * mm, H - 120 * mm, 130 * mm, 90 * mm)
    hw = [
        ("1. Таблица", "значение · возраст · задачи"),
        ("2. Разбор", "этапы + дозировка"),
        ("3. Эссе + режим", "слушание важнее куплета"),
    ]
    for i, (t, b) in enumerate(hw):
        x = 14 * mm + i * 90 * mm
        round_rect(c, x, 22 * mm, 85 * mm, 35 * mm, WHITE, r=6)
        rgb(c, TEAL_D)
        c.setFont("DejaVuBold", 11)
        c.drawString(x + 3 * mm, 48 * mm, t)
        rgb(c, INK)
        c.setFont("DejaVu", 9)
        c.drawString(x + 3 * mm, 38 * mm, b)
    rgb(c, GOLD)
    c.setFont("DejaVu", 10)
    c.drawCentredString(W / 2, 12 * mm, "Берегите голос малыша — пение начнётся с вашего мягкого «рядом».")
    c.showPage()

    c.save()
    ART.parent.mkdir(parents=True, exist_ok=True)
    ART.write_bytes(OUT.read_bytes())
    print(f"OK pdf={OUT}")


if __name__ == "__main__":
    build()
