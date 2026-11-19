#!/usr/bin/env python3
"""Landscape slide-deck PDF twin for artistic song image and artistry."""

from pathlib import Path

from reportlab.lib.pagesizes import landscape
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

W, H = landscape((297 * mm, 210 * mm))
ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "zanyatie-25-assets"
OUT = ROOT / "zanyatie-25-prezentaciya.pdf"
ART = Path("/opt/cursor/artifacts/zanyatie-25-prezentaciya.pdf")

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
    (1, "z25-01-title.jpg"), (2, "z25-02-doors.jpg"), (3, "z25-03-goal.jpg"),
    (4, "z25-04-components.jpg"), (5, "z25-05-ages.jpg"), (6, "z25-06-means.jpg"),
    (7, "z25-07-warmup.jpg"), (8, "z25-08-analysis.jpg"), (9, "z25-09-games.jpg"),
    (10, "z25-10-limits.jpg"), (11, "z25-11-micro.jpg"), (12, "z25-12-finale.jpg"),
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
    c.drawString(14 * mm, 8 * mm, f"Художественный образ песни · Голос · Мимика · Жест   {n}/{total}")


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
    c.drawString(14 * mm, H - 18 * mm, "ДОШКОЛЬНЫЙ ВОЗРАСТ")
    rgb(c, WHITE)
    c.setFont("DejaVuBold", 22)
    c.drawString(14 * mm, H - 38 * mm, "Художественный образ")
    c.drawString(14 * mm, H - 52 * mm, "песни и артистизм")
    rgb(c, SAND)
    c.setFont("DejaVu", 11)
    c.drawString(14 * mm, H - 70 * mm, "Естественная выразительность — голос, лицо, один жест")
    rgb(c, WHITE)
    c.drawString(14 * mm, H - 85 * mm, "настроение → мягкий голос → лицо → 1 жест → игра")
    draw_img(c, 1, W - 145 * mm, 25 * mm, 130 * mm, 100 * mm)
    rgb(c, SAND)
    c.setFont("DejaVu", 9)
    c.drawString(14 * mm, 14 * mm, "Ветлугина · Радынова · Метлов · «Ладушки» · театрализация в ДОУ")
    c.showPage()

    bg(c)
    title(c, "Образ или «просто текст»?", "Чем отличается выразительное пение")
    draw_img(c, 2, 12 * mm, 28 * mm, 145 * mm, 105 * mm)
    table_simple(c, 165 * mm, H - 30 * mm, [
        ["Это", "Не это"],
        ["мягкая выразительность", "крик «для эмоций»"],
        ["1–2 ясных средства", "гора жестов"],
        ["игра и образ", "взрослый театр"],
        ["проживание настроения", "штампы без смысла"],
    ], [55 * mm, 55 * mm])
    text_block(c, 165 * mm, 45 * mm, ["Артистизм — не громкость", "и не гримаса."], size=12, color=TEAL_D, bold=True)
    footer(c, 2)
    c.showPage()

    bg(c)
    title(c, "Чему учимся сегодня", "Цель и продукт")
    steps = ["Образ и артистизм", "Компоненты образа", "Эмоция · мимика · жест · голос", "Анализ песни", "Игры на артистизм", "Микропреподавание"]
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
    title(c, "Компоненты художественного образа", "Из чего складывается образ песни")
    draw_img(c, 4, 12 * mm, 30 * mm, 145 * mm, 100 * mm)
    table_simple(c, 165 * mm, H - 30 * mm, [
        ["Компонент", "Вопрос"],
        ["Герой", "кто говорит?"],
        ["Настроение", "какое чувство?"],
        ["Музыка", "как звучит?"],
        ["Голос", "как поём?"],
        ["Мимика / жест", "что видно?"],
        ["Игровой приём", "чем помочь?"],
    ], [50 * mm, 60 * mm], row_h=12 * mm)
    footer(c, 4)
    c.showPage()

    bg(c)
    title(c, "Артистизм по возрасту", "Какой уровень посилен")
    draw_img(c, 5, 12 * mm, 30 * mm, 145 * mm, 100 * mm)
    table_simple(c, 165 * mm, H - 30 * mm, [
        ["Возраст", "Акцент"],
        ["1,5–3", "настроение + показ"],
        ["3–5", "герой + 1 жест"],
        ["5–7", "мини-роли 20–40 сек"],
    ], [35 * mm, 75 * mm], row_h=16 * mm)
    text_block(c, 165 * mm, 55 * mm, ["Чем младше — тем яснее", "одно настроение."], size=12, color=TEAL_D, bold=True)
    footer(c, 5)
    c.showPage()

    bg(c)
    title(c, "Эмоция · мимика · жест · голос", "Связка средств выразительности")
    draw_img(c, 6, 12 * mm, 30 * mm, 145 * mm, 100 * mm)
    table_simple(c, 165 * mm, H - 30 * mm, [
        ["Средство", "Риск"],
        ["Эмоция", "наигранность"],
        ["Мимика", "гримасы"],
        ["Жест", "хаос движений"],
        ["Голос", "крик «для эмоций»"],
    ], [45 * mm, 65 * mm], row_h=14 * mm)
    footer(c, 6)
    c.showPage()

    bg(c)
    title(c, "Практическая разминка", "1–2 минуты до выразительности")
    draw_img(c, 7, 12 * mm, 28 * mm, 150 * mm, 110 * mm)
    table_simple(c, 170 * mm, H - 30 * mm, [
        ["Упражнение", "Задача"],
        ["Плечи / кисти", "снять зажим"],
        ["Зевота-улыбка", "свобода лица"],
        ["Мягкие гласные", "артикуляция"],
        ["Эхо настроения", "характер"],
        ["Жест-подпись", "1 жест"],
        ["Стоп", "мгновенно мягко"],
    ], [50 * mm, 55 * mm], row_h=12 * mm)
    footer(c, 7)
    c.showPage()

    bg(c)
    title(c, "Анализ образа песни", "Карточка анализа")
    draw_img(c, 8, 12 * mm, 28 * mm, 150 * mm, 110 * mm)
    text_block(c, 170 * mm, H - 40 * mm, [
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
    ], size=11, color=TEAL_D, leading=7 * mm)
    footer(c, 8)
    c.showPage()

    bg(c)
    title(c, "Игры на артистизм", "Банк коротких приёмов")
    draw_img(c, 9, 12 * mm, 28 * mm, 150 * mm, 110 * mm)
    table_simple(c, 170 * mm, H - 30 * mm, [
        ["Игра", "Задача"],
        ["Угадай настроение", "слух к характеру"],
        ["Жест-герой", "1 жест"],
        ["Эхо в характере", "мягкая выразительность"],
        ["Кто поёт?", "угадать героя"],
        ["Тихий спектакль", "не громкостью"],
        ["Передай образ", "очередь 20–30 сек"],
    ], [55 * mm, 50 * mm], row_h=12 * mm)
    footer(c, 9)
    c.showPage()

    bg(c)
    title(c, "Можно и нельзя", "Границы артистизма в ДОУ")
    draw_img(c, 10, 12 * mm, 28 * mm, 120 * mm, 110 * mm)
    card(c, 145 * mm, 45 * mm, 65 * mm, 95 * mm, GREEN, "Можно ✓", [
        "1 ясное настроение", "1 жест-подпись",
        "мягкий эталон", "короткий прогон", "похвала за ясность",
    ])
    card(c, 218 * mm, 45 * mm, 60 * mm, 95 * mm, RED, "Нельзя ✕", [
        "крик «для эмоций»", "гора жестов",
        "начинать с костюмов", "длинный спектакль", "стыд за «неартистов»",
    ])
    footer(c, 10)
    c.showPage()

    bg(c)
    title(c, "Микропреподавание", "Фрагмент 90–120 секунд")
    draw_img(c, 11, 12 * mm, 28 * mm, 150 * mm, 110 * mm)
    table_simple(c, 170 * mm, H - 30 * mm, [
        ["Шаг", "Действие"],
        ["1", "вход в образ"],
        ["2", "мягкий показ"],
        ["3", "фраза + 1 средство"],
        ["4", "короткий прогон"],
        ["5", "мягкий стоп"],
    ], [20 * mm, 85 * mm], row_h=11 * mm)
    card(c, 170 * mm, 22 * mm, 105 * mm, 35 * mm, TEAL, "Рубрика Да/Нет", [
        "настроение понятно · голос мягкий", "1 жест · коротко · есть стоп",
    ])
    footer(c, 11)
    c.showPage()

    bg(c, TEAL_D)
    rgb(c, GOLD)
    c.setFont("DejaVu", 11)
    c.drawString(14 * mm, H - 16 * mm, "Итог + творческие задания")
    rgb(c, WHITE)
    c.setFont("DejaVuBold", 20)
    c.drawString(14 * mm, H - 32 * mm, "Формула работы")
    c.drawString(14 * mm, H - 42 * mm, "над образом")
    rgb(c, SAND)
    c.setFont("DejaVu", 12)
    for i, line in enumerate(["Понятное настроение.", "Мягкий голос.", "Лицо.", "1 жест. Короткая игра."]):
        c.drawString(14 * mm, H - 58 * mm - i * 8 * mm, line)
    draw_img(c, 12, W - 145 * mm, H - 120 * mm, 130 * mm, 90 * mm)
    hw = [
        ("1. Таблица + разбор", "компоненты · анализ песни"),
        ("2. Эссе + сценарий", "не воспитывать криком"),
        ("3. Картотека", "6 позиций с предостережением"),
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
    c.drawCentredString(W / 2, 12 * mm, "Не сцена ради сцены — а понятная, добрая выразительность.")
    c.showPage()

    c.save()
    ART.parent.mkdir(parents=True, exist_ok=True)
    ART.write_bytes(OUT.read_bytes())
    print(f"OK pdf={OUT}")


if __name__ == "__main__":
    build()
