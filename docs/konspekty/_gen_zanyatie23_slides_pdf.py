#!/usr/bin/env python3
"""Landscape slide-deck PDF twin for musical song-fairy tales."""

from pathlib import Path

from reportlab.lib.pagesizes import landscape
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

W, H = landscape((297 * mm, 210 * mm))
ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "zanyatie-23-assets"
OUT = ROOT / "zanyatie-23-prezentaciya.pdf"
ART = Path("/opt/cursor/artifacts/zanyatie-23-prezentaciya.pdf")

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
    (1, "z23-01-title.jpg"), (2, "z23-02-forms.jpg"), (3, "z23-03-goal.jpg"),
    (4, "z23-04-types.jpg"), (5, "z23-05-bridge.jpg"), (6, "z23-06-steps.jpg"),
    (7, "z23-07-exercises.jpg"), (8, "z23-08-analysis.jpg"), (9, "z23-09-props.jpg"),
    (10, "z23-10-puppet.jpg"), (11, "z23-11-lab.jpg"), (12, "z23-12-finale.jpg"),
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
    c.drawString(14 * mm, 8 * mm, f"Музыкальные песни-сказки · Пение · Образ · Кукла · Пауза   {n}/{total}")


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
    c.drawString(14 * mm, H - 38 * mm, "Музыкальные")
    c.drawString(14 * mm, H - 52 * mm, "песни-сказки")
    rgb(c, SAND)
    c.setFont("DejaVu", 11)
    c.drawString(14 * mm, H - 70 * mm, "Короткая, посильная, добрая песенная сказка")
    rgb(c, WHITE)
    c.drawString(14 * mm, H - 85 * mm, "мягкое пение → образ → 1 кукла/жест → сюжет → пауза")
    draw_img(c, 1, W - 145 * mm, 25 * mm, 130 * mm, 100 * mm)
    rgb(c, SAND)
    c.setFont("DejaVu", 9)
    c.drawString(14 * mm, 14 * mm, "Ветлугина · Радынова · Метлов · «Ладушки» · театрализация в ДОУ")
    c.showPage()

    bg(c)
    title(c, "Песня, игра или песня-сказка?", "Чем отличается")
    draw_img(c, 2, 12 * mm, 28 * mm, 145 * mm, 105 * mm)
    table_simple(c, 165 * mm, H - 30 * mm, [
        ["Форма", "Отличие"],
        ["Обычная песня", "без сюжета/ролей"],
        ["Игра-песня", "правило, не всегда сказка"],
        ["Театр", "длиннее, больше реквизита"],
        ["Песня-сказка", "короткая + образ"],
    ], [50 * mm, 60 * mm])
    text_block(c, 165 * mm, 45 * mm, ["Голос главный.", "Кукла — опора."], size=12, color=TEAL_D, bold=True)
    footer(c, 2)
    c.showPage()

    bg(c)
    title(c, "Чему учимся сегодня", "Цель и продукт")
    steps = ["Понятие и виды", "Влияние на развитие", "Разучивание", "Анализ образов", "Реквизит и куклы", "Мини-показ"]
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
    title(c, "Виды песен-сказок", "Шесть рабочих видов")
    draw_img(c, 4, 12 * mm, 30 * mm, 145 * mm, 100 * mm)
    table_simple(c, 165 * mm, H - 30 * mm, [
        ["Вид", "Суть"],
        ["Один герой", "становимся героем"],
        ["Диалог", "реплики по очереди"],
        ["Цепочка", "герои добавляются"],
        ["Событие", "короткий сюжет"],
        ["Хоровод", "круг + сюжет"],
        ["Кукольная", "образ — кукла"],
    ], [45 * mm, 65 * mm], row_h=12 * mm)
    footer(c, 4)
    c.showPage()

    bg(c)
    title(c, "Влияние на развитие", "Музыка · речь · общение")
    draw_img(c, 5, 12 * mm, 30 * mm, 145 * mm, 100 * mm)
    table_simple(c, 165 * mm, H - 30 * mm, [
        ["Сфера", "Что развивается"],
        ["Музыкальное", "характер, фраза"],
        ["Речевое", "словарь, диалог"],
        ["Социальное", "роли, эмпатия"],
        ["Эмоции", "образ без страха"],
        ["Внимание", "порядок событий"],
    ], [45 * mm, 65 * mm], row_h=12 * mm)
    footer(c, 5)
    c.showPage()

    bg(c)
    title(c, "Этапы разучивания", "Как разучивать песню-сказку")
    draw_img(c, 6, 12 * mm, 28 * mm, 150 * mm, 110 * mm)
    table_simple(c, 170 * mm, H - 30 * mm, [
        ["Этап", "Действие"],
        ["Интерес", "кукла / вопрос"],
        ["Слушание", "сюжет целиком"],
        ["Образы", "характер героя"],
        ["Фразы", "1–2 строки"],
        ["Роль", "мягкий голос"],
        ["Действие", "жест / кукла"],
        ["Стоп", "пауза"],
    ], [40 * mm, 65 * mm], row_h=11 * mm)
    footer(c, 6)
    c.showPage()

    bg(c)
    title(c, "Творческие упражнения", "Банк коротких заданий")
    draw_img(c, 7, 12 * mm, 28 * mm, 150 * mm, 110 * mm)
    table_simple(c, 170 * mm, H - 30 * mm, [
        ["Упражнение", "Задача"],
        ["Голос героя", "без крика"],
        ["Жест-подпись", "1 жест"],
        ["Эхо-сказки", "в характере"],
        ["Кто говорит?", "угадать"],
        ["Тихое волшебство", "тише, не громче"],
        ["Очередь ролей", "смена 20–30 сек"],
    ], [55 * mm, 50 * mm], row_h=12 * mm)
    footer(c, 7)
    c.showPage()

    bg(c)
    title(c, "Анализ музыкальных образов", "Карточка образа")
    draw_img(c, 8, 12 * mm, 28 * mm, 150 * mm, 110 * mm)
    text_block(c, 170 * mm, H - 40 * mm, [
        "Кто герой?",
        "Характер музыки",
        "Темп и динамика",
        "Жест / движение",
        "Речевая краска",
        "Роль куклы",
        "Риск",
        "",
        "зайка — медведь",
        "контраст жестом, не криком",
    ], size=11, color=TEAL_D, leading=7 * mm)
    footer(c, 8)
    c.showPage()

    bg(c)
    title(c, "Реквизит: можно и нельзя", "Чемоданчик сказки")
    draw_img(c, 9, 12 * mm, 28 * mm, 120 * mm, 110 * mm)
    card(c, 145 * mm, 45 * mm, 65 * mm, 95 * mm, GREEN, "Беру ✓", [
        "1–3 предмета", "видимая кукла",
        "безопасно надеть", "связано с героем", "убрать за 5 сек",
    ])
    card(c, 218 * mm, 45 * mm, 60 * mm, 95 * mm, RED, "Не беру ✕", [
        "гора костюмов", "мелкий «для себя»",
        "мешает петь", "случайный яркий", "сложный монтаж",
    ])
    footer(c, 9)
    c.showPage()

    bg(c)
    title(c, "Игрушки на руку", "Кукла помогает увидеть героя")
    draw_img(c, 10, 12 * mm, 28 * mm, 150 * mm, 110 * mm)
    table_simple(c, 170 * mm, H - 30 * mm, [
        ["Задача", "Как"],
        ["Внимание", "появление до пения"],
        ["Герой", "поёт с педагогом"],
        ["Диалог", "вопрос — ответ"],
        ["Смена роли", "передать"],
        ["Стоп", "поклон / уход"],
    ], [40 * mm, 65 * mm], row_h=12 * mm)
    footer(c, 10)
    c.showPage()

    bg(c)
    title(c, "Мини-лаборатория", "Показ 60–90 секунд")
    draw_img(c, 11, 12 * mm, 28 * mm, 150 * mm, 110 * mm)
    table_simple(c, 170 * mm, H - 30 * mm, [
        ["Шаг", "Действие"],
        ["1", "появление куклы"],
        ["2", "1–2 фразы"],
        ["3", "жест / действие"],
        ["4", "короткий прогон"],
        ["5", "мягкий стоп"],
    ], [20 * mm, 85 * mm], row_h=11 * mm)
    card(c, 170 * mm, 22 * mm, 105 * mm, 35 * mm, TEAL, "Рубрика Да/Нет", [
        "кукла помогает · песня слышна", "нет хаоса · убрать быстро · мягко",
    ])
    footer(c, 11)
    c.showPage()

    bg(c, TEAL_D)
    rgb(c, GOLD)
    c.setFont("DejaVu", 11)
    c.drawString(14 * mm, H - 16 * mm, "Итог + творческие задания")
    rgb(c, WHITE)
    c.setFont("DejaVuBold", 20)
    c.drawString(14 * mm, H - 32 * mm, "Формула")
    c.drawString(14 * mm, H - 42 * mm, "песни-сказки")
    rgb(c, SAND)
    c.setFont("DejaVu", 12)
    for i, line in enumerate(["Мягкое пение.", "Ясный образ.", "1 кукла / жест.", "Короткий сюжет. Пауза."]):
        c.drawString(14 * mm, H - 58 * mm - i * 8 * mm, line)
    draw_img(c, 12, W - 145 * mm, H - 120 * mm, 130 * mm, 90 * mm)
    hw = [
        ("1. Таблица + разбор", "виды · этапы · реквизит"),
        ("2. Эссе + сценарий", "не начинать со спектакля"),
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
    c.drawCentredString(W / 2, 12 * mm, "Сказка начинается с мягкого пения — не с декораций.")
    c.showPage()

    c.save()
    ART.parent.mkdir(parents=True, exist_ok=True)
    ART.write_bytes(OUT.read_bytes())
    print(f"OK pdf={OUT}")


if __name__ == "__main__":
    build()
