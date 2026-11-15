#!/usr/bin/env python3
"""Landscape slide-deck PDF twin for singing ages 5–7 presentation."""

from pathlib import Path

from reportlab.lib.pagesizes import landscape
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

W, H = landscape((297 * mm, 210 * mm))
ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "zanyatie-20-assets"
OUT = ROOT / "zanyatie-20-prezentaciya.pdf"
ART = Path("/opt/cursor/artifacts/zanyatie-20-prezentaciya.pdf")

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
    (1, "z20-01-title.jpg"), (2, "z20-02-doors.jpg"), (3, "z20-03-goal.jpg"),
    (4, "z20-04-spheres.jpg"), (5, "z20-05-ages.jpg"), (6, "z20-06-traffic.jpg"),
    (7, "z20-07-tasks.jpg"), (8, "z20-08-stages.jpg"), (9, "z20-09-exercises.jpg"),
    (10, "z20-10-repertoire.jpg"), (11, "z20-11-training.jpg"), (12, "z20-12-finale.jpg"),
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
    c.drawString(14 * mm, 8 * mm, f"Пение 5–7 лет · Мягкий эталон · Фраза · Унисон · Пауза   {n}/{total}")


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
    c.drawString(14 * mm, H - 18 * mm, "СТАРШИЙ ДОШКОЛЬНЫЙ ВОЗРАСТ")
    rgb(c, WHITE)
    c.setFont("DejaVuBold", 26)
    c.drawString(14 * mm, H - 38 * mm, "Пение с детьми")
    c.drawString(14 * mm, H - 52 * mm, "от 5–7 лет")
    rgb(c, SAND)
    c.setFont("DejaVu", 11)
    c.drawString(14 * mm, H - 70 * mm, "Не сила голоса — мягкий эталон, фраза, унисон и пауза")
    rgb(c, WHITE)
    c.drawString(14 * mm, H - 85 * mm, "мягкий показ → фраза → выразительность → унисон → пауза")
    draw_img(c, 1, W - 145 * mm, 25 * mm, 130 * mm, 100 * mm)
    rgb(c, SAND)
    c.setFont("DejaVu", 9)
    c.drawString(14 * mm, 14 * mm, "Ветлугина · Метлов · Радынова · «Ладушки» · Орлова / Бекина")
    c.showPage()

    # 2
    bg(c)
    title(c, "Чем пение в 5–7 лет особенное", "От подхвата — к выразительности и унисону")
    draw_img(c, 2, 12 * mm, 28 * mm, 145 * mm, 105 * mm)
    table_simple(c, 165 * mm, H - 30 * mm, [
        ["3–5 лет", "5–7 лет"],
        ["больше подхват", "больше самостоятельный повтор"],
        ["короткая фраза", "куплет–припев возможен"],
        ["характер намечается", "характер и динамика"],
        ["сильная опора на взрослого", "дети держат увереннее"],
    ], [55 * mm, 55 * mm])
    text_block(c, 165 * mm, 45 * mm, ["Увереннее — не значит", "громче любой ценой."], size=12, color=TEAL_D, bold=True)
    footer(c, 2)
    c.showPage()

    # 3
    bg(c)
    title(c, "Чему учимся сегодня", "Цель и продукт")
    steps = ["Значение пения", "Особенности 5–7 лет", "Задачи обучения", "Приёмы и этапы", "Упражнения", "Репертуар"]
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
    title(c, "Значение пения", "Развитие и готовность к школе")
    draw_img(c, 4, 12 * mm, 30 * mm, 145 * mm, 100 * mm)
    table_simple(c, 165 * mm, H - 30 * mm, [
        ["Сфера", "Что развивается"],
        ["Слух", "интонация, унисон"],
        ["Голос", "фраза, выразительность"],
        ["Речь", "дикция, дыхание"],
        ["Эмоции", "характер, настроение"],
        ["Общение", "петь вместе"],
        ["К школе", "самоконтроль, слух"],
    ], [35 * mm, 75 * mm], row_h=12 * mm)
    footer(c, 4)
    c.showPage()

    # 5
    bg(c)
    title(c, "Возрастные особенности 5–7 лет", "Что реально доступно голосу")
    draw_img(c, 5, 12 * mm, 30 * mm, 145 * mm, 100 * mm)
    table_simple(c, 165 * mm, H - 30 * mm, [
        ["Особенность", "Для педагога"],
        ["Диапазон шире", "без крайних пиков"],
        ["Фраза длиннее", "работа над фразой"],
        ["Интонация точнее", "мягкий повтор"],
        ["Внимание устойчивее", "куплет–припев"],
        ["Любят выразительность", "характер, динамика"],
        ["Риск форсирования", "особенно на праздниках"],
    ], [50 * mm, 60 * mm], row_h=12 * mm)
    footer(c, 5)
    c.showPage()

    # 6
    bg(c)
    title(c, "Можно и нельзя для голоса", "Светофор бережного пения")
    draw_img(c, 6, 12 * mm, 28 * mm, 120 * mm, 110 * mm)
    card(c, 145 * mm, 45 * mm, 65 * mm, 95 * mm, GREEN, "Можно ✓", [
        "мягкий естественный звук", "фразы, характер, унисон",
        "удобная поза, паузы", "посильная песня", "мягкое уточнение",
    ])
    card(c, 218 * mm, 45 * mm, 60 * mm, 95 * mm, RED, "Нельзя ✕", [
        "крик, давить горлом", "соло «как у взрослых»",
        "долгое пение без отдыха", "шлягер с высоким пиком", "стыдить за интонацию",
    ])
    footer(c, 6)
    c.showPage()

    # 7
    bg(c)
    title(c, "Задачи обучения пению", "Восемь проверяемых задач")
    draw_img(c, 7, 12 * mm, 28 * mm, 150 * mm, 110 * mm)
    text_block(c, 170 * mm, H - 40 * mm, [
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
    ], size=11, color=TEAL_D, leading=7 * mm)
    footer(c, 7)
    c.showPage()

    # 8
    bg(c)
    title(c, "Приёмы и этапы разучивания", "Как вести песню в 5–7 лет")
    draw_img(c, 8, 12 * mm, 28 * mm, 150 * mm, 110 * mm)
    table_simple(c, 170 * mm, H - 30 * mm, [
        ["Этап", "Суть"],
        ["Интерес", "образ / установка"],
        ["Показ", "педагог поёт"],
        ["Смысл", "характер, вопросы"],
        ["Фразы", "короткий повтор"],
        ["Вместе", "соединение"],
        ["Выразительность", "динамика / образ"],
        ["Унисон", "слушать друг друга"],
        ["Стоп", "отдых голоса"],
    ], [45 * mm, 60 * mm], row_h=10 * mm)
    footer(c, 8)
    c.showPage()

    # 9
    bg(c)
    title(c, "Упражнения для певческих навыков", "20–40 секунд — одна задача")
    draw_img(c, 9, 12 * mm, 28 * mm, 150 * mm, 110 * mm)
    table_simple(c, 170 * mm, H - 30 * mm, [
        ["Навык", "Упражнение"],
        ["Дыхание", "платочек; фраза на выдохе"],
        ["Мягкая атака", "«мм», «ау», «ля»"],
        ["Интонация", "попевка / ступеньки"],
        ["Унисон", "споём одинаково"],
        ["Дикция", "потешка шёпотом→голос"],
        ["Характер", "ласково / бодро"],
    ], [40 * mm, 65 * mm], row_h=12 * mm)
    footer(c, 9)
    c.showPage()

    # 10
    bg(c)
    title(c, "Подбор песенного репертуара", "Беру / не беру для 5–7 лет")
    draw_img(c, 10, 12 * mm, 28 * mm, 145 * mm, 105 * mm)
    card(c, 165 * mm, 45 * mm, 55 * mm, 95 * mm, LEAF, "Беру ✓", [
        "песня старшей группы", "ясный образ", "мягкая мелодия",
        "куплет–припев", "есть цель",
    ])
    card(c, 228 * mm, 45 * mm, 52 * mm, 95 * mm, RED, "Не беру ✕", [
        "взрослый шлягер", "чуждый текст", "высокий пик",
        "широкие скачки", "просто из интернета",
    ])
    footer(c, 10)
    c.showPage()

    # 11
    bg(c)
    title(c, "Практика и чек-лист", "Мини-фрагмент 90–120 секунд")
    draw_img(c, 11, 12 * mm, 28 * mm, 150 * mm, 110 * mm)
    table_simple(c, 170 * mm, H - 30 * mm, [
        ["Шаг", "Действие"],
        ["1", "упражнение 20–30 сек"],
        ["2", "показ 1–2 фраз + повтор"],
        ["3", "характер или унисон"],
        ["4", "можно + нельзя"],
        ["5", "мягкий стоп"],
    ], [20 * mm, 85 * mm], row_h=11 * mm)
    card(c, 170 * mm, 22 * mm, 105 * mm, 35 * mm, TEAL, "Рубрика Да/Нет", [
        "мягкость · фразы · характер/унисон", "пауза · без крика · для 5–7 лет",
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
    c.drawString(14 * mm, H - 32 * mm, "Формула пения 5–7 лет")
    rgb(c, SAND)
    c.setFont("DejaVu", 12)
    for i, line in enumerate(["Мягкий эталон.", "Посильная песня.", "Фраза и выразительность.", "Унисон без крика."]):
        c.drawString(14 * mm, H - 48 * mm - i * 8 * mm, line)
    draw_img(c, 12, W - 145 * mm, H - 120 * mm, 130 * mm, 90 * mm)
    hw = [
        ("1. Таблица", "значение · 5–7 · задачи · этапы"),
        ("2. Разбор + эссе", "этапы + почему не крик"),
        ("3. Сценарий", "упражнение + фраза + стоп"),
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
    c.drawCentredString(W / 2, 12 * mm, "Берегите голос — пение 5–7 лет начнётся с правильного эталона.")
    c.showPage()

    c.save()
    ART.parent.mkdir(parents=True, exist_ok=True)
    ART.write_bytes(OUT.read_bytes())
    print(f"OK pdf={OUT}")


if __name__ == "__main__":
    build()
