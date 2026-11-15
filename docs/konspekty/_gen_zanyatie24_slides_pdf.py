#!/usr/bin/env python3
"""Landscape slide-deck PDF twin for health-preserving vocal work."""

from pathlib import Path

from reportlab.lib.pagesizes import landscape
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

W, H = landscape((297 * mm, 210 * mm))
ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "zanyatie-24-assets"
OUT = ROOT / "zanyatie-24-prezentaciya.pdf"
ART = Path("/opt/cursor/artifacts/zanyatie-24-prezentaciya.pdf")

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
    (1, "z24-01-title.jpg"), (2, "z24-02-doors.jpg"), (3, "z24-03-goal.jpg"),
    (4, "z24-04-voice.jpg"), (5, "z24-05-principles.jpg"), (6, "z24-06-hygiene.jpg"),
    (7, "z24-07-body.jpg"), (8, "z24-08-artic.jpg"), (9, "z24-09-bank.jpg"),
    (10, "z24-10-complex.jpg"), (11, "z24-11-rubric.jpg"), (12, "z24-12-finale.jpg"),
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
    c.drawString(14 * mm, 8 * mm, f"Здоровьесбережение в вокале · Мягкость · Краткость · Пауза   {n}/{total}")


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
    c.drawString(14 * mm, H - 38 * mm, "Здоровьесбережение")
    c.drawString(14 * mm, H - 52 * mm, "в вокальной работе")
    rgb(c, SAND)
    c.setFont("DejaVu", 11)
    c.drawString(14 * mm, H - 70 * mm, "Естественное, комфортное пение — без крика и спешки")
    rgb(c, WHITE)
    c.drawString(14 * mm, H - 85 * mm, "мягкий показ → короткая проба → наблюдение → пауза")
    draw_img(c, 1, W - 145 * mm, 25 * mm, 130 * mm, 100 * mm)
    rgb(c, SAND)
    c.setFont("DejaVu", 9)
    c.drawString(14 * mm, 14 * mm, "Ветлугина · Радынова · Метлов · охрана детского голоса · «Ладушки»")
    c.showPage()

    bg(c)
    title(c, "Голос — не «чем громче, тем лучше»", "Зачем нужно здоровьесбережение")
    draw_img(c, 2, 12 * mm, 28 * mm, 145 * mm, 105 * mm)
    table_simple(c, 165 * mm, H - 30 * mm, [
        ["Риск", "Что происходит"],
        ["Крик «для выразительности»", "напряжение"],
        ["Длинные повторы", "утомление"],
        ["Неудобный диапазон", "зажим / отказ"],
        ["Стыд за тихий голос", "страх"],
    ], [65 * mm, 45 * mm])
    text_block(c, 165 * mm, 45 * mm, ["Здоровье важнее", "громкости."], size=12, color=TEAL_D, bold=True)
    footer(c, 2)
    c.showPage()

    bg(c)
    title(c, "Чему учимся сегодня", "Цель и продукт")
    steps = ["Особенности детского голоса", "Принципы и гигиена", "Осанка · дыхание · расслабление", "Артикуляция · дикция · слух", "Банк упражнений", "Мини-комплекс"]
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
    title(c, "Особенности детского голоса", "Не уменьшенный взрослый голос")
    draw_img(c, 4, 12 * mm, 30 * mm, 145 * mm, 100 * mm)
    table_simple(c, 165 * mm, H - 30 * mm, [
        ["Особенность", "Смысл"],
        ["Аппарат формируется", "без «взрослого» звука"],
        ["Малый диапазон", "посильный репертуар"],
        ["Быстрая утомляемость", "короткие фрагменты"],
        ["Легко кричит", "мягкость"],
        ["Копирует эталон", "показ решающий"],
    ], [50 * mm, 60 * mm], row_h=12 * mm)
    footer(c, 4)
    c.showPage()

    bg(c)
    title(c, "Принципы здоровьесбережения", "Восемь рабочих принципов")
    draw_img(c, 5, 12 * mm, 30 * mm, 145 * mm, 100 * mm)
    table_simple(c, 165 * mm, H - 30 * mm, [
        ["Принцип", "Практика"],
        ["Мягкость", "без жёсткой атаки"],
        ["Краткость", "короткие упражнения"],
        ["Посильность", "по возрасту"],
        ["Пауза", "тишина — методика"],
        ["Наблюдение", "видеть усталость"],
        ["Эталон", "спокойный показ"],
    ], [45 * mm, 65 * mm], row_h=12 * mm)
    footer(c, 5)
    c.showPage()

    bg(c)
    title(c, "Голосовая гигиена", "Можно и нельзя")
    draw_img(c, 6, 12 * mm, 28 * mm, 120 * mm, 110 * mm)
    card(c, 145 * mm, 45 * mm, 65 * mm, 95 * mm, GREEN, "Можно ✓", [
        "после лёгкой разминки", "коротко, с паузами",
        "мягкая динамика", "удобная осанка", "остановить при усталости",
    ])
    card(c, 218 * mm, 45 * mm, 60 * mm, 95 * mm, RED, "Нельзя ✕", [
        "при осиплости", "долгие репетиции",
        "«кто громче»", "зажим шеи", "через силу",
    ])
    footer(c, 6)
    c.showPage()

    bg(c)
    title(c, "Осанка, дыхание, расслабление", "Тело помогает голосу")
    draw_img(c, 7, 12 * mm, 28 * mm, 150 * mm, 110 * mm)
    table_simple(c, 170 * mm, H - 30 * mm, [
        ["Блок", "Упражнения"],
        ["Осанка", "нить вверх, плечи вниз"],
        ["Дыхание", "цветок, свеча"],
        ["Расслабление", "кисти, зевота-улыбка"],
        ["Стоп-сигнал", "тише / пауза"],
    ], [40 * mm, 65 * mm], row_h=14 * mm)
    footer(c, 7)
    c.showPage()

    bg(c)
    title(c, "Артикуляция, дикция, слух", "Ясность без напряжения")
    draw_img(c, 8, 12 * mm, 28 * mm, 150 * mm, 110 * mm)
    table_simple(c, 170 * mm, H - 30 * mm, [
        ["Направление", "Примеры"],
        ["Артикуляция", "мягкие гласные"],
        ["Дикция", "слоги, тихая скороговорка"],
        ["Слух", "эхо, выше–ниже"],
        ["Правило", "не громче «для исправления»"],
    ], [45 * mm, 60 * mm], row_h=14 * mm)
    footer(c, 8)
    c.showPage()

    bg(c)
    title(c, "Банк упражнений гигиены", "Бережные упражнения")
    draw_img(c, 9, 12 * mm, 28 * mm, 150 * mm, 110 * mm)
    table_simple(c, 170 * mm, H - 30 * mm, [
        ["Упражнение", "Зачем"],
        ["Тихий «ммм»", "мягкий контакт"],
        ["Узкая «сирена»", "гибкость без форса"],
        ["«Пылинка»", "спокойный выдох"],
        ["«Ля-ля» 2–3 звука", "разогрев"],
        ["Речь → пение", "без скачка громкости"],
        ["Пауза", "отдых"],
    ], [55 * mm, 50 * mm], row_h=12 * mm)
    footer(c, 9)
    c.showPage()

    bg(c)
    title(c, "Мини-комплекс 2–2,5 минуты", "Старт пения без вреда")
    draw_img(c, 10, 12 * mm, 28 * mm, 150 * mm, 110 * mm)
    text_block(c, 170 * mm, H - 40 * mm, [
        "1. Плечи вниз + «нить»",
        "2. «Цветок» — «свеча»",
        "3. Мягкие слоги",
        "4. Эхо 2–3 звука",
        "5. Пауза → короткая песня",
        "",
        "тело → дыхание → слоги",
        "→ эхо → пауза → песня",
    ], size=11, color=TEAL_D, leading=7 * mm)
    footer(c, 10)
    c.showPage()

    bg(c)
    title(c, "Рубрика наблюдения", "Как понять, что всё безопасно")
    draw_img(c, 11, 12 * mm, 28 * mm, 150 * mm, 110 * mm)
    table_simple(c, 170 * mm, H - 30 * mm, [
        ["Вопрос", "Да/Нет"],
        ["Есть разминка?", ""],
        ["Упражнения короткие?", ""],
        ["Эталон мягкий?", ""],
        ["Есть паузы?", ""],
        ["Нет «кто громче»?", ""],
        ["Готовы остановить?", ""],
    ], [70 * mm, 35 * mm], row_h=12 * mm)
    footer(c, 11)
    c.showPage()

    bg(c, TEAL_D)
    rgb(c, GOLD)
    c.setFont("DejaVu", 11)
    c.drawString(14 * mm, H - 16 * mm, "Итог + творческие задания")
    rgb(c, WHITE)
    c.setFont("DejaVuBold", 20)
    c.drawString(14 * mm, H - 32 * mm, "Формула")
    c.drawString(14 * mm, H - 42 * mm, "безопасного пения")
    rgb(c, SAND)
    c.setFont("DejaVu", 12)
    for i, line in enumerate(["Мягкий показ.", "Короткая проба.", "Наблюдение.", "Пауза. Повтор если легко."]):
        c.drawString(14 * mm, H - 58 * mm - i * 8 * mm, line)
    draw_img(c, 12, W - 145 * mm, H - 120 * mm, 130 * mm, 90 * mm)
    hw = [
        ("1. Таблица + разбор", "принципы · признаки стоп"),
        ("2. Эссе + сценарий", "не исправлять громкостью"),
        ("3. Картотека", "6 упражнений с «стоп»"),
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
    c.drawCentredString(W / 2, 12 * mm, "Голос растёт в радости и свободе, а не в крике и спешке.")
    c.showPage()

    c.save()
    ART.parent.mkdir(parents=True, exist_ok=True)
    ART.write_bytes(OUT.read_bytes())
    print(f"OK pdf={OUT}")


if __name__ == "__main__":
    build()
