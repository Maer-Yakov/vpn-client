#!/usr/bin/env python3
"""Landscape slide-deck PDF twin for lesson 8 presentation."""

from pathlib import Path

from reportlab.lib.pagesizes import landscape
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

W, H = landscape((297 * mm, 210 * mm))
ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "zanyatie-08-assets"
OUT = ROOT / "zanyatie-08-prezentaciya.pdf"
ART = Path("/opt/cursor/artifacts/zanyatie-08-prezentaciya.pdf")

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
    (1, "z08-01-title.jpg"), (2, "z08-02-doors.jpg"), (3, "z08-03-ritual.jpg"),
    (4, "z08-04-mindmap.jpg"), (5, "z08-05-spheres.jpg"), (6, "z08-06-range.jpg"),
    (7, "z08-07-traffic.jpg"), (8, "z08-08-stairs.jpg"), (9, "z08-09-show.jpg"),
    (10, "z08-10-stages.jpg"), (11, "z08-11-stations.jpg"), (12, "z08-12-soft.jpg"),
    (13, "z08-13-rooster.jpg"), (14, "z08-14-exercises.jpg"), (15, "z08-15-repertoire.jpg"),
    (16, "z08-16-training.jpg"), (17, "z08-17-checklist.jpg"), (18, "z08-18-finale.jpg"),
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


def footer(c, n, total=18):
    rgb(c, MUTED)
    c.setFont("DejaVu", 9)
    c.drawString(14 * mm, 8 * mm, f"Занятие 8 · Пение 3–4 лет · Мягкий показ · Короткая фраза · Пауза   {n}/{total}")


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


def text_box(c, x, y, text, size=12, bold=False, color=INK):
    rgb(c, color)
    c.setFont("DejaVuBold" if bold else "DejaVu", size)
    c.drawString(x, y, text)


def circle(c, x, y, r, color):
    rgb(c, color)
    c.circle(x, y, r, fill=1, stroke=0)


def draw_img(c, n, x, y, w, h):
    c.drawImage(str(IMG[n]), x, y, width=w, height=h, preserveAspectRatio=True, mask="auto")


def draw_table(c, x, y, col_w, row_h, rows):
    for r, row in enumerate(rows):
        yy = y - r * row_h
        for ci, cell in enumerate(row):
            xx = x + sum(col_w[:ci])
            fill = TEAL if r == 0 else (SOFT if r % 2 else WHITE)
            rgb(c, fill)
            c.rect(xx, yy - row_h, col_w[ci], row_h, fill=1, stroke=0)
            rgb(c, WHITE if r == 0 else INK)
            c.setFont("DejaVuBold" if r == 0 else "DejaVu", 9 if r else 10)
            c.drawString(xx + 2 * mm, yy - row_h + 3.2 * mm, cell[:48])


def card(c, x, y, w, h, color, title_t, lines):
    round_rect(c, x, y, w, h, color)
    text_box(c, x + 4 * mm, y + h - 9 * mm, title_t, size=12, bold=True, color=WHITE)
    yy = y + h - 18 * mm
    for line in lines:
        text_box(c, x + 4 * mm, yy, line, size=9, color=WHITE)
        yy -= 5.5 * mm


def build():
    fonts()
    c = canvas.Canvas(str(OUT), pagesize=(W, H))

    # 1
    bg(c, TEAL_D)
    circle(c, 18 * mm, H - 18 * mm, 30 * mm, TEAL)
    circle(c, W - 18 * mm, 18 * mm, 34 * mm, CORAL)
    text_box(c, 14 * mm, H - 30 * mm, "ЗАНЯТИЕ 8 · МОДУЛЬ II", size=11, bold=True, color=GOLD)
    text_box(c, 14 * mm, H - 50 * mm, "Пение с детьми", size=22, bold=True, color=WHITE)
    text_box(c, 14 * mm, H - 62 * mm, "младшего дошкольного возраста", size=18, bold=True, color=WHITE)
    text_box(c, 14 * mm, H - 80 * mm, "Не хор «любой ценой» — желание подхватить", size=11, color=SAND)
    text_box(c, 14 * mm, H - 95 * mm, "услышал → подхватил → повторил фразу", size=11, color=WHITE)
    draw_img(c, 1, 145 * mm, 35 * mm, 135 * mm, 145 * mm)
    text_box(c, 14 * mm, 18 * mm, "Ветлугина · Дзержинская · Метлов · «Ладушки»", size=10, color=SAND)
    c.showPage()

    # 2
    bg(c)
    title(c, "Чем пение в 3–4 года особенное", "Подхватывать песню — не сдавать номер")
    draw_img(c, 2, 12 * mm, 35 * mm, 145 * mm, 120 * mm)
    draw_table(c, 165 * mm, H - 35 * mm, [55 * mm, 60 * mm], 14 * mm, [
        ["3–4 года", "Позже (5–7)"],
        ["узкий диапазон", "диапазон шире"],
        ["показ обязателен", "больше самостоятельности"],
        ["игра важнее «нот»", "точнее интонация"],
        ["риск крика высок", "лучше мягкий звук"],
    ])
    text_box(c, 165 * mm, 35 * mm, "Важнее желание петь, чем идеальная нота.", size=10, bold=True, color=TEAL_D)
    footer(c, 2)
    c.showPage()

    # 3
    bg(c)
    title(c, "Чему учимся сегодня", "Цель занятия для студента")
    steps = ["1. Значение пения", "2. Особенности голоса 3–4 лет", "3. Задачи обучения",
             "4. Приёмы и этапы", "5. Упражнения", "6. Репертуар"]
    for i, t in enumerate(steps):
        text_box(c, 14 * mm, H - 40 * mm - i * 14 * mm, t, size=12, color=INK)
    draw_img(c, 3, 160 * mm, 30 * mm, 120 * mm, 140 * mm)
    footer(c, 3)
    c.showPage()

    # 4
    bg(c)
    title(c, "Карта темы", "От значения пения — к репертуару")
    draw_img(c, 4, 12 * mm, 28 * mm, 175 * mm, 135 * mm)
    draw_table(c, 195 * mm, H - 40 * mm, [30 * mm, 55 * mm], 12 * mm, [
        ["Слайды", "Блок"], ["5–11", "теория"], ["12–16", "практика"], ["17–18", "чек-лист"],
    ])
    footer(c, 4)
    c.showPage()

    # 5–18 in compact pattern
    slides = [
        (5, "Значение пения в развитии ребёнка", "Мост между слухом, речью и игрой",
         [["Сфера", "Что"], ["Слух", "высота, темп"], ["Речь", "словарь, дикция"],
          ["Дыхание", "выдох"], ["Эмоции", "через голос"], ["Общение", "петь вместе"]]),
        (6, "Возрастные особенности 3–4 лет", "Детский голос и поведение в пении",
         [["Особенность", "Для педагога"], ["Диапазон узкий", "без скачков"],
          ["Фраза короткая", "1–2 строки"], ["Интонация неточна", "показ"],
          ["Форсирование", "мягкий звук, паузы"]]),
    ]
    for n, tit, sub, rows in slides:
        bg(c)
        title(c, tit, sub)
        draw_img(c, n, 12 * mm, 40 * mm, 145 * mm, 115 * mm)
        draw_table(c, 165 * mm, H - 35 * mm, [55 * mm, 60 * mm], 13 * mm, rows)
        footer(c, n)
        c.showPage()

    # 7
    bg(c)
    title(c, "Можно и нельзя для голоса", "Границы бережности")
    draw_img(c, 7, 12 * mm, 30 * mm, 120 * mm, 130 * mm)
    card(c, 145 * mm, 55 * mm, 65 * mm, 100 * mm, GREEN, "Можно ✓", [
        "мягкий звук", "петь вместе", "короткая песня", "жест / игрушка", "удобная поза",
    ])
    card(c, 218 * mm, 55 * mm, 62 * mm, 100 * mm, RED, "Нельзя ✕", [
        "крик", "соло «на сцене»", "длинный номер", "без паузы", "сложная хореография",
    ])
    footer(c, 7)
    c.showPage()

    # 8
    bg(c)
    title(c, "Задачи обучения пению", "Что проверяем в младшей группе")
    draw_img(c, 8, 12 * mm, 35 * mm, 150 * mm, 120 * mm)
    for i, t in enumerate(["1. Желание петь", "2. Мягкий звук", "3. Слушать фразу",
                           "4. Интонация через показ", "5. Слово + жест", "6. Репертуар", "7. Паузы"]):
        text_box(c, 175 * mm, H - 40 * mm - i * 14 * mm, t, size=11, color=TEAL_D)
    footer(c, 8)
    c.showPage()

    # 9
    bg(c)
    title(c, "Методические приёмы", "Как вести пение в 3–4 года")
    draw_img(c, 9, 12 * mm, 35 * mm, 145 * mm, 120 * mm)
    draw_table(c, 165 * mm, H - 35 * mm, [55 * mm, 60 * mm], 12 * mm, [
        ["Приём", "Как"], ["Показ", "лицом к детям"], ["Вместе", "педагог ведёт"],
        ["Образ", "игрушка"], ["Жест", "опора"], ["Повтор", "2–4 + пауза"],
    ])
    footer(c, 9)
    c.showPage()

    # 10
    bg(c)
    title(c, "Этапы разучивания песни", "От интереса — к игровому закреплению")
    draw_img(c, 10, 12 * mm, 35 * mm, 155 * mm, 120 * mm)
    draw_table(c, 175 * mm, H - 35 * mm, [40 * mm, 65 * mm], 11 * mm, [
        ["Этап", "Суть"], ["Интерес", "игрушка"], ["Показ", "педагог"],
        ["Смысл", "вопросы"], ["Фразы", "повтор"], ["Вместе", "соединение"],
        ["Игра", "жест"], ["Стоп", "пауза"],
    ])
    footer(c, 10)
    c.showPage()

    # 11
    bg(c)
    title(c, "Обзор практики", "Упражнения и репертуар")
    draw_img(c, 11, 12 * mm, 28 * mm, 175 * mm, 135 * mm)
    text_box(c, 195 * mm, H - 50 * mm, "1. Разминка голоса", size=12, bold=True, color=TEAL_D)
    text_box(c, 195 * mm, H - 65 * mm, "2. Полка песен", size=12, bold=True, color=TEAL_D)
    text_box(c, 195 * mm, H - 90 * mm, "беру / не беру", size=11, color=INK)
    footer(c, 11)
    c.showPage()

    # 12
    bg(c)
    title(c, "Практика 1. Мягкий звук vs форсирование", "Собственный голос педагога")
    draw_img(c, 12, 12 * mm, 35 * mm, 150 * mm, 120 * mm)
    draw_table(c, 170 * mm, H - 35 * mm, [40 * mm, 40 * mm, 40 * mm], 13 * mm, [
        ["Признак", "Мягко", "Форс"], ["Лицо", "свободно", "напряжено"],
        ["Звук", "льётся", "давит"], ["Дыхание", "спокойно", "судорожно"],
    ])
    footer(c, 12)
    c.showPage()

    # 13
    bg(c)
    title(c, "Практика 2. Этапы на конкретной песне", "Модель разучивания")
    draw_img(c, 13, 12 * mm, 35 * mm, 150 * mm, 120 * mm)
    draw_table(c, 170 * mm, H - 35 * mm, [40 * mm, 70 * mm], 11 * mm, [
        ["Этап", "Действие"], ["Интерес", "игрушка"], ["Показ", "целиком"],
        ["Фразы", "повтор"], ["Вместе", "соединение"], ["Игра", "жест"], ["Стоп", "пауза"],
    ])
    footer(c, 13)
    c.showPage()

    # 14
    bg(c)
    title(c, "Практика 3. Банк упражнений", "20–40 секунд — одна задача")
    draw_img(c, 14, 12 * mm, 35 * mm, 150 * mm, 120 * mm)
    draw_table(c, 170 * mm, H - 35 * mm, [45 * mm, 65 * mm], 12 * mm, [
        ["Навык", "Упражнение"], ["Дыхание", "платочек"], ["Атака", "мм / ау"],
        ["Высота", "повтор"], ["Дикция", "потешка"], ["Динамика", "тихо/громче"],
    ])
    footer(c, 14)
    c.showPage()

    # 15
    bg(c)
    title(c, "Практика 4. Подбор репертуара", "Песня — педагогическое решение")
    draw_img(c, 15, 12 * mm, 35 * mm, 145 * mm, 120 * mm)
    card(c, 165 * mm, 90 * mm, 55 * mm, 70 * mm, GREEN, "Беру ✓", ["короткая", "образ", "мягкая"])
    card(c, 228 * mm, 90 * mm, 52 * mm, 70 * mm, RED, "Не беру ✕", ["шлягер", "скачки", "крик"])
    footer(c, 15)
    c.showPage()

    # 16
    bg(c)
    title(c, "Мини-тренинг студента", "90–100 секунд мини-пения")
    draw_img(c, 16, 12 * mm, 35 * mm, 150 * mm, 120 * mm)
    card(c, 170 * mm, 40 * mm, 110 * mm, 100 * mm, TEAL, "Рубрика", [
        "образ", "мягкость", "краткость", "повтор", "пауза", "без крика",
    ])
    footer(c, 16)
    c.showPage()

    # 17
    bg(c)
    title(c, "Чек-лист пения в младшей группе", "Перед репертуаром средней группы")
    draw_img(c, 17, 12 * mm, 35 * mm, 135 * mm, 120 * mm)
    checks = [
        "1. Значение пения", "2. Риск крика", "3. Задачи", "4. Показ",
        "5. Этапы", "6. Упражнения", "7. Репертуар", "8. Паузы",
    ]
    for i, t in enumerate(checks):
        round_rect(c, 155 * mm, H - 40 * mm - i * 15 * mm, 125 * mm, 12 * mm, SOFT if i % 2 == 0 else SAND, r=4)
        text_box(c, 160 * mm, H - 36 * mm - i * 15 * mm, t, size=9, color=INK)
    text_box(c, 50 * mm, 20 * mm, "МЯГКИЙ ПОКАЗ  ↔  КОРОТКАЯ ФРАЗА  ↔  ПАУЗА", size=12, bold=True, color=TEAL_D)
    footer(c, 17)
    c.showPage()

    # 18
    bg(c, TEAL_D)
    circle(c, 15 * mm, H - 15 * mm, 25 * mm, TEAL)
    circle(c, W - 18 * mm, 20 * mm, 28 * mm, CORAL)
    text_box(c, 14 * mm, H - 28 * mm, "Итог + домашнее задание", size=11, bold=True, color=GOLD)
    text_box(c, 14 * mm, H - 48 * mm, "Пение начинается", size=20, bold=True, color=WHITE)
    text_box(c, 14 * mm, H - 60 * mm, "с желания подхватить", size=20, bold=True, color=WHITE)
    text_box(c, 14 * mm, H - 80 * mm, "Мягкий голос. Короткая песня.", size=11, color=SAND)
    text_box(c, 14 * mm, H - 90 * mm, "Этапы без спешки.", size=11, color=SAND)
    draw_img(c, 18, 145 * mm, 85 * mm, 135 * mm, 95 * mm)
    hw = [
        ("1. Таблица", ["значение · голос", "задачи · этапы"]),
        ("2. Разбор песни", ["этапы + дозировка"]),
        ("3. Мини-эссе", ["мягкий показ важнее"]),
    ]
    for i, (t, lines) in enumerate(hw):
        round_rect(c, 14 * mm + i * 90 * mm, 25 * mm, 82 * mm, 45 * mm, WHITE)
        text_box(c, 18 * mm + i * 90 * mm, 58 * mm, t, size=10, bold=True, color=TEAL_D)
        for j, line in enumerate(lines):
            text_box(c, 18 * mm + i * 90 * mm, 48 * mm - j * 8 * mm, line, size=8, color=INK)
    text_box(c, 20 * mm, 12 * mm, "Берегите детский голос — пение начнётся с правильного этажа.", size=9, color=GOLD)
    c.showPage()

    c.save()
    ART.parent.mkdir(parents=True, exist_ok=True)
    ART.write_bytes(OUT.read_bytes())
    print(f"OK pdf={OUT}")


if __name__ == "__main__":
    build()
