#!/usr/bin/env python3
"""Landscape slide-deck PDF twin for singing with musical instruments."""

from pathlib import Path

from reportlab.lib.pagesizes import landscape
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

W, H = landscape((297 * mm, 210 * mm))
ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "zanyatie-22-assets"
OUT = ROOT / "zanyatie-22-prezentaciya.pdf"
ART = Path("/opt/cursor/artifacts/zanyatie-22-prezentaciya.pdf")

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
    (1, "z22-01-title.jpg"), (2, "z22-02-doors.jpg"), (3, "z22-03-goal.jpg"),
    (4, "z22-04-instruments.jpg"), (5, "z22-05-types.jpg"), (6, "z22-06-org.jpg"),
    (7, "z22-07-traffic.jpg"), (8, "z22-08-warmup.jpg"), (9, "z22-09-select.jpg"),
    (10, "z22-10-repertoire.jpg"), (11, "z22-11-training.jpg"), (12, "z22-12-finale.jpg"),
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
    c.drawString(14 * mm, 8 * mm, f"Пение с инструментами · Голос · Ритм · Сигнал · Стоп   {n}/{total}")


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
    c.setFont("DejaVuBold", 24)
    c.drawString(14 * mm, H - 38 * mm, "Пение с музыкальными")
    c.drawString(14 * mm, H - 52 * mm, "инструментами")
    rgb(c, SAND)
    c.setFont("DejaVu", 11)
    c.drawString(14 * mm, H - 70 * mm, "Не шум ради шума — мягкий голос, простой ритм, сигнал")
    rgb(c, WHITE)
    c.drawString(14 * mm, H - 85 * mm, "голос → 1 вид → сигнал → мало инструментов → стоп")
    draw_img(c, 1, W - 145 * mm, 25 * mm, 130 * mm, 100 * mm)
    rgb(c, SAND)
    c.setFont("DejaVu", 9)
    c.drawString(14 * mm, 14 * mm, "Ветлугина · Метлов · Радынова · «Ладушки» · элементарное музицирование")
    c.showPage()

    bg(c)
    title(c, "Возможности и трудности", "Инструмент помогает — или мешает?")
    draw_img(c, 2, 12 * mm, 28 * mm, 145 * mm, 105 * mm)
    table_simple(c, 165 * mm, H - 30 * mm, [
        ["Возможности", "Трудности"],
        ["ритмическая опора", "громче голоса"],
        ["интерес к песне", "забывают петь"],
        ["ансамбль / слух", "хаос без сигнала"],
        ["роль «я помогаю»", "крик «перекричать»"],
    ], [55 * mm, 55 * mm])
    text_block(c, 165 * mm, 45 * mm, ["Не слышно песни?", "Тише и меньше."], size=12, color=TEAL_D, bold=True)
    footer(c, 2)
    c.showPage()

    bg(c)
    title(c, "Чему учимся сегодня", "Цель и продукт")
    steps = ["Возможности / риски", "Инструменты и виды", "Организация", "Разминка", "Подбор к песне", "Микропреподавание"]
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
    title(c, "Инструменты", "Что берём для пения дошкольников")
    draw_img(c, 4, 12 * mm, 30 * mm, 145 * mm, 100 * mm)
    table_simple(c, 165 * mm, H - 30 * mm, [
        ["Группа", "Для чего"],
        ["Ударные", "ритм, припев"],
        ["Звенящие", "конец фразы"],
        ["Мелодические", "1–2 звука"],
    ], [45 * mm, 65 * mm], row_h=14 * mm)
    text_block(c, 165 * mm, 55 * mm, ["Младшие — меньше.", "Старшие — до 2 партий."], size=12, color=TEAL_D, bold=True)
    footer(c, 4)
    c.showPage()

    bg(c)
    title(c, "Виды сопровождения", "Шесть рабочих вариантов")
    draw_img(c, 5, 12 * mm, 30 * mm, 145 * mm, 100 * mm)
    table_simple(c, 165 * mm, H - 30 * mm, [
        ["Вид", "Суть"],
        ["Пульс", "ровные удары"],
        ["Сильная доля", "удар на «раз»"],
        ["Припевное", "только припев"],
        ["Ответ фразы", "короткий отыгрыш"],
        ["Остинато", "повторный рисунок"],
        ["Звукообраз", "«кап», «динь»"],
    ], [45 * mm, 65 * mm], row_h=12 * mm)
    footer(c, 5)
    c.showPage()

    bg(c)
    title(c, "Принципы организации", "Как не превратить песню в хаос")
    draw_img(c, 6, 12 * mm, 28 * mm, 150 * mm, 110 * mm)
    table_simple(c, 170 * mm, H - 30 * mm, [
        ["Принцип", "Практика"],
        ["Голос главный", "слышна песня"],
        ["Один навык", "песня или партия"],
        ["Показ", "голос + инструмент"],
        ["Сигнал", "играй / стой"],
        ["Места", "кто где"],
        ["Дозировка", "пауза"],
    ], [45 * mm, 60 * mm], row_h=12 * mm)
    footer(c, 6)
    c.showPage()

    bg(c)
    title(c, "Можно и нельзя", "Светофор ансамбля")
    draw_img(c, 7, 12 * mm, 28 * mm, 120 * mm, 110 * mm)
    card(c, 145 * mm, 45 * mm, 65 * mm, 95 * mm, GREEN, "Можно ✓", [
        "мягкий удар", "1–2 инструмента",
        "припев / конец фразы", "сигнал и стоп", "сначала песня",
    ])
    card(c, 218 * mm, 45 * mm, 60 * mm, 95 * mm, RED, "Нельзя ✕", [
        "бить изо всех сил", "оркестр «всем всё»",
        "перекрывать куплет", "без правила", "крик поверх бубна",
    ])
    footer(c, 7)
    c.showPage()

    bg(c)
    title(c, "Разминка к ансамблю", "20–40 секунд — одна задача")
    draw_img(c, 8, 12 * mm, 28 * mm, 150 * mm, 110 * mm)
    table_simple(c, 170 * mm, H - 30 * mm, [
        ["Упражнение", "Задача"],
        ["Эхо-ритм", "повтор тихо"],
        ["Сильная доля", "удар на «раз»"],
        ["Играй / стой", "сигнал"],
        ["Тише", "динамика"],
        ["Голос + удар", "не потерять пение"],
    ], [50 * mm, 55 * mm], row_h=12 * mm)
    footer(c, 8)
    c.showPage()

    bg(c)
    title(c, "Подбор сопровождения", "Алгоритм из семи шагов")
    draw_img(c, 9, 12 * mm, 28 * mm, 150 * mm, 110 * mm)
    text_block(c, 170 * mm, H - 40 * mm, [
        "1. Какой возраст?",
        "2. Песня знакома?",
        "3. Где опора?",
        "4. Какой 1 вид?",
        "5. Какой инструмент?",
        "6. Какой сигнал?",
        "7. Где стоп?",
        "",
        "колыбельная → колокольчик",
        "бодрая → доля в припеве",
    ], size=11, color=TEAL_D, leading=7 * mm)
    footer(c, 9)
    c.showPage()

    bg(c)
    title(c, "Примерный репертуар", "Логика «песня → сопровождение»")
    draw_img(c, 10, 12 * mm, 28 * mm, 145 * mm, 105 * mm)
    table_simple(c, 165 * mm, H - 30 * mm, [
        ["Возраст", "Идея"],
        ["3–5", "припев погремушками"],
        ["3–5", "«динь» в конце"],
        ["4–5", "сильная доля"],
        ["5–7", "припев + ответ"],
        ["5–7", "остинато 1–2 звука"],
    ], [30 * mm, 80 * mm], row_h=12 * mm)
    footer(c, 10)
    c.showPage()

    bg(c)
    title(c, "Микропреподавание", "Фрагмент 90–120 секунд")
    draw_img(c, 11, 12 * mm, 28 * mm, 150 * mm, 110 * mm)
    table_simple(c, 170 * mm, H - 30 * mm, [
        ["Шаг", "Действие"],
        ["1", "возраст и цель"],
        ["2", "сигнал 15–20 сек"],
        ["3", "показ песни"],
        ["4", "песня + сопровождение"],
        ["5", "мягкий стоп"],
    ], [20 * mm, 85 * mm], row_h=11 * mm)
    card(c, 170 * mm, 22 * mm, 105 * mm, 35 * mm, TEAL, "Рубрика Да/Нет", [
        "голос слышен · не перекрывает", "сигнал · посильно · стоп",
    ])
    footer(c, 11)
    c.showPage()

    bg(c, TEAL_D)
    rgb(c, GOLD)
    c.setFont("DejaVu", 11)
    c.drawString(14 * mm, H - 16 * mm, "Итог + творческие задания")
    rgb(c, WHITE)
    c.setFont("DejaVuBold", 20)
    c.drawString(14 * mm, H - 32 * mm, "Формула пения")
    c.drawString(14 * mm, H - 42 * mm, "с инструментами")
    rgb(c, SAND)
    c.setFont("DejaVu", 12)
    for i, line in enumerate(["Знакомая песня.", "1 простой вид.", "Сигнал.", "Мало инструментов. Стоп."]):
        c.drawString(14 * mm, H - 58 * mm - i * 8 * mm, line)
    draw_img(c, 12, W - 145 * mm, H - 120 * mm, 130 * mm, 90 * mm)
    hw = [
        ("1. Таблица", "виды · принципы · сигналы"),
        ("2. Разбор + эссе", "алгоритм + почему не громче"),
        ("3. Сценарий", "разминка + песня + стоп"),
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
    c.drawCentredString(W / 2, 12 * mm, "Первым всегда остаётся мягкий голос.")
    c.showPage()

    c.save()
    ART.parent.mkdir(parents=True, exist_ok=True)
    ART.write_bytes(OUT.read_bytes())
    print(f"OK pdf={OUT}")


if __name__ == "__main__":
    build()
