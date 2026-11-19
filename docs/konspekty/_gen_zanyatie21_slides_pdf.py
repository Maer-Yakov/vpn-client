#!/usr/bin/env python3
"""Landscape slide-deck PDF twin for musical games and songs with movement."""

from pathlib import Path

from reportlab.lib.pagesizes import landscape
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

W, H = landscape((297 * mm, 210 * mm))
ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "zanyatie-21-assets"
OUT = ROOT / "zanyatie-21-prezentaciya.pdf"
ART = Path("/opt/cursor/artifacts/zanyatie-21-prezentaciya.pdf")

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
    (1, "z21-01-title.jpg"), (2, "z21-02-doors.jpg"), (3, "z21-03-goal.jpg"),
    (4, "z21-04-spheres.jpg"), (5, "z21-05-forms.jpg"), (6, "z21-06-traffic.jpg"),
    (7, "z21-07-select.jpg"), (8, "z21-08-stages.jpg"), (9, "z21-09-exercises.jpg"),
    (10, "z21-10-repertoire.jpg"), (11, "z21-11-training.jpg"), (12, "z21-12-finale.jpg"),
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
    c.drawString(14 * mm, 8 * mm, f"Игры и песни с движением · Слух · Жест · Роль · Стоп   {n}/{total}")


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

    bg(c, TEAL_D)
    rgb(c, GOLD)
    c.setFont("DejaVu", 11)
    c.drawString(14 * mm, H - 18 * mm, "ПЕНИЕ · ДВИЖЕНИЕ · ИГРА")
    rgb(c, WHITE)
    c.setFont("DejaVuBold", 24)
    c.drawString(14 * mm, H - 38 * mm, "Музыкальные игры")
    c.drawString(14 * mm, H - 52 * mm, "и песни с движением")
    rgb(c, SAND)
    c.setFont("DejaVu", 11)
    c.drawString(14 * mm, H - 70 * mm, "Не хаос под трек — слух, образ, жест и мягкий голос")
    rgb(c, WHITE)
    c.drawString(14 * mm, H - 85 * mm, "услышать → показать → повторить движением → стоп")
    draw_img(c, 1, W - 145 * mm, 25 * mm, 130 * mm, 100 * mm)
    rgb(c, SAND)
    c.setFont("DejaVu", 9)
    c.drawString(14 * mm, 14 * mm, "Ветлугина · Радынова · Буренина · «Ладушки» · «Музыка и движение»")
    c.showPage()

    bg(c)
    title(c, "Зачем эта тема", "Мост между «просто поём» и «просто двигаемся»")
    draw_img(c, 2, 12 * mm, 28 * mm, 145 * mm, 105 * mm)
    table_simple(c, 165 * mm, H - 30 * mm, [
        ["Без игры", "С игрой / песней"],
        ["пение «сидя»", "образ и действие"],
        ["движение без слуха", "ответ на музыку"],
        ["длинные объяснения", "короткий показ"],
        ["крик и беготня", "правило + пауза"],
    ], [55 * mm, 55 * mm])
    text_block(c, 165 * mm, 45 * mm, ["Убрать музыку —", "смысл меняется?"], size=12, color=TEAL_D, bold=True)
    footer(c, 2)
    c.showPage()

    bg(c)
    title(c, "Чему учимся сегодня", "Цель и продукт")
    steps = ["Значение", "Три формы", "Подбор материала", "Этапы подготовки", "Упражнения", "Практика"]
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

    bg(c)
    title(c, "Значение", "Что развивают игра и песня с движением")
    draw_img(c, 4, 12 * mm, 30 * mm, 145 * mm, 100 * mm)
    table_simple(c, 165 * mm, H - 30 * mm, [
        ["Сфера", "Что развивается"],
        ["Слух", "начало, темп, характер"],
        ["Голос", "подпевание, мягкость"],
        ["Ритм", "шаг, хлопок, жест"],
        ["Координация", "слово + движение"],
        ["Внимание", "правило, сигнал, роль"],
        ["Общение", "круг, пара, вместе"],
    ], [40 * mm, 70 * mm], row_h=12 * mm)
    footer(c, 4)
    c.showPage()

    bg(c)
    title(c, "Три формы", "Игра · игра-песня · песня с движением")
    draw_img(c, 5, 12 * mm, 30 * mm, 145 * mm, 100 * mm)
    table_simple(c, 165 * mm, H - 30 * mm, [
        ["Форма", "Опора"],
        ["Музыкальная игра", "правило + сигнал"],
        ["Игра-песня", "текст = сценарий"],
        ["Песня с движением", "фраза + жест"],
    ], [55 * mm, 55 * mm], row_h=14 * mm)
    text_block(c, 165 * mm, 55 * mm, ["игра → слышать", "игра-песня → образ", "песня+жест → фраза"], size=11, color=TEAL_D, bold=True, leading=7 * mm)
    footer(c, 5)
    c.showPage()

    bg(c)
    title(c, "Можно и нельзя", "Светофор безопасной игры")
    draw_img(c, 6, 12 * mm, 28 * mm, 120 * mm, 110 * mm)
    card(c, 145 * mm, 45 * mm, 65 * mm, 95 * mm, GREEN, "Можно ✓", [
        "мягкий голос + жест", "короткое правило",
        "повтор и пауза", "посильное движение", "смена роли дозированно",
    ])
    card(c, 218 * mm, 45 * mm, 60 * mm, 95 * mm, RED, "Нельзя ✕", [
        "крик поверх музыки", "длинная лекция",
        "бег без стопа", "сложная «эстрада»", "толчки в кругу",
    ])
    footer(c, 6)
    c.showPage()

    bg(c)
    title(c, "Подбор материала", "Беру / не беру")
    draw_img(c, 7, 12 * mm, 28 * mm, 145 * mm, 105 * mm)
    card(c, 165 * mm, 45 * mm, 55 * mm, 95 * mm, LEAF, "Беру ✓", [
        "ясный образ", "короткий повтор", "2–4 движения",
        "есть задача", "безопасный стоп",
    ])
    card(c, 228 * mm, 45 * mm, 52 * mm, 95 * mm, RED, "Не беру ✕", [
        "длинный текст", "взрослая эстрада", "сложная хореография",
        "просто трек", "без паузы",
    ])
    footer(c, 7)
    c.showPage()

    bg(c)
    title(c, "Этапы подготовки и проведения", "Как готовить и как вести")
    draw_img(c, 8, 12 * mm, 28 * mm, 150 * mm, 110 * mm)
    table_simple(c, 170 * mm, H - 30 * mm, [
        ["Этап", "Суть"],
        ["Интерес", "образ / вопрос"],
        ["Показ", "голос + жест"],
        ["Правило", "1–2 правила"],
        ["Проба", "фраза + движение"],
        ["Вместе", "соединение"],
        ["Характер", "тихо / бодро"],
        ["Вариация", "смена роли"],
        ["Стоп", "отдых"],
    ], [40 * mm, 65 * mm], row_h=10 * mm)
    footer(c, 8)
    c.showPage()

    bg(c)
    title(c, "Упражнения-настройки", "20–40 секунд — одна задача")
    draw_img(c, 9, 12 * mm, 28 * mm, 150 * mm, 110 * mm)
    table_simple(c, 170 * mm, H - 30 * mm, [
        ["Упражнение", "Задача"],
        ["Эхо-жест", "фраза + жест"],
        ["Стоп-игра", "реакция на паузу"],
        ["Тихо — бодро", "характер"],
        ["Кто ведущий", "внимание к показу"],
        ["Голос не кричит", "мягкий эталон"],
    ], [50 * mm, 55 * mm], row_h=12 * mm)
    footer(c, 9)
    c.showPage()

    bg(c)
    title(c, "Банк материала", "Игры-песни и песни с движением")
    draw_img(c, 10, 12 * mm, 28 * mm, 145 * mm, 105 * mm)
    text_block(c, 165 * mm, H - 40 * mm, [
        "Игры-песни:",
        "«Каравай», «Заинька»",
        "«Где ты, зайка?»",
        "«Мы на луг ходили»",
        "",
        "Песни с движением:",
        "дождик, солнышко,",
        "птички, животные",
        "",
        "Музыкальные игры:",
        "тихо/громко · характер",
    ], size=11, color=TEAL_D, leading=6.5 * mm)
    footer(c, 10)
    c.showPage()

    bg(c)
    title(c, "Практика и чек-лист", "Мини-фрагмент 90–120 секунд")
    draw_img(c, 11, 12 * mm, 28 * mm, 150 * mm, 110 * mm)
    table_simple(c, 170 * mm, H - 30 * mm, [
        ["Шаг", "Действие"],
        ["1", "назвать форму"],
        ["2", "упражнение / образ"],
        ["3", "показ + движение"],
        ["4", "повтор + можно/нельзя"],
        ["5", "мягкий стоп"],
    ], [20 * mm, 85 * mm], row_h=11 * mm)
    card(c, 170 * mm, 22 * mm, 105 * mm, 35 * mm, TEAL, "Рубрика Да/Нет", [
        "форма · мягкость · жест к фразе", "пауза · безопасность · возраст",
    ])
    footer(c, 11)
    c.showPage()

    bg(c, TEAL_D)
    rgb(c, GOLD)
    c.setFont("DejaVu", 11)
    c.drawString(14 * mm, H - 16 * mm, "Итог + творческие задания")
    rgb(c, WHITE)
    c.setFont("DejaVuBold", 20)
    c.drawString(14 * mm, H - 32 * mm, "Формула игры и песни")
    c.drawString(14 * mm, H - 42 * mm, "с движением")
    rgb(c, SAND)
    c.setFont("DejaVu", 12)
    for i, line in enumerate(["Услышать.", "Показать мягко.", "Повторить движением.", "Не кричать. Стоп."]):
        c.drawString(14 * mm, H - 58 * mm - i * 8 * mm, line)
    draw_img(c, 12, W - 145 * mm, H - 120 * mm, 130 * mm, 90 * mm)
    hw = [
        ("1. Таблица", "значение · 3 формы · этапы"),
        ("2. Разбор + эссе", "2 материала + почему не хаос"),
        ("3. Сценарий", "настройка + показ + стоп"),
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
    c.drawCentredString(W / 2, 12 * mm, "Игра начинается с вашего спокойного показа — голосом и телом.")
    c.showPage()

    c.save()
    ART.parent.mkdir(parents=True, exist_ok=True)
    ART.write_bytes(OUT.read_bytes())
    print(f"OK pdf={OUT}")


if __name__ == "__main__":
    build()
