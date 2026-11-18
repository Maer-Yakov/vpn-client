#!/usr/bin/env python3
"""Landscape slide-deck PDF twin for folklore in preschool vocal development."""

from pathlib import Path

from reportlab.lib.pagesizes import landscape
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

W, H = landscape((297 * mm, 210 * mm))
ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "zanyatie-26-assets"
OUT = ROOT / "zanyatie-26-prezentaciya.pdf"
ART = Path("/opt/cursor/artifacts/zanyatie-26-prezentaciya.pdf")

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
    (1, "z26-01-title.jpg"), (2, "z26-02-doors.jpg"), (3, "z26-03-goal.jpg"),
    (4, "z26-04-genres.jpg"), (5, "z26-05-meaning.jpg"), (6, "z26-06-warmup.jpg"),
    (7, "z26-07-exercises.jpg"), (8, "z26-08-ages.jpg"), (9, "z26-09-criteria.jpg"),
    (10, "z26-10-card.jpg"), (11, "z26-11-groups.jpg"), (12, "z26-12-finale.jpg"),
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
    c.drawString(14 * mm, 8 * mm, f"Фольклор в вокальном развитии · Жанр · Голос · Ритм · Игра   {n}/{total}")


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
    c.setFont("DejaVuBold", 20)
    c.drawString(14 * mm, H - 38 * mm, "Фольклор в вокальном")
    c.drawString(14 * mm, H - 52 * mm, "развитии дошкольников")
    rgb(c, SAND)
    c.setFont("DejaVu", 11)
    c.drawString(14 * mm, H - 70 * mm, "Живая речь, ритм и мягкий голос — не «музей»")
    rgb(c, WHITE)
    c.drawString(14 * mm, H - 85 * mm, "жанр → мягкий голос → ритм / жест → игра")
    draw_img(c, 1, W - 145 * mm, 25 * mm, 130 * mm, 100 * mm)
    rgb(c, SAND)
    c.setFont("DejaVu", 9)
    c.drawString(14 * mm, 14 * mm, "Ветлугина · Радынова · Метлов · Науменко · «Ладушки» · Мельников")
    c.showPage()

    bg(c)
    title(c, "Живой фольклор или «просто текст»?", "Чем отличается фольклорная работа")
    draw_img(c, 2, 12 * mm, 28 * mm, 145 * mm, 105 * mm)
    table_simple(c, 165 * mm, H - 30 * mm, [
        ["Это", "Не это"],
        ["короткий живой образец", "длинная «народная» ария"],
        ["мягкий игровой показ", "крик «по-народному»"],
        ["посильный жест", "сложная постановка"],
        ["повтор и игра", "заучивание большого текста"],
    ], [55 * mm, 55 * mm])
    text_block(c, 165 * mm, 45 * mm, ["Громкость — не признак", "народности."], size=12, color=TEAL_D, bold=True)
    footer(c, 2)
    c.showPage()

    bg(c)
    title(c, "Чему учимся сегодня", "Цель и продукт")
    steps = ["Жанры и значение", "Разминка", "Певческие и ритмические упражнения", "Репертуар 0–7 лет", "Работа в группах", "Итог"]
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
    title(c, "Жанры фольклора", "Что берёт воспитатель")
    draw_img(c, 4, 12 * mm, 30 * mm, 145 * mm, 100 * mm)
    table_simple(c, 165 * mm, H - 30 * mm, [
        ["Жанр", "Задача"],
        ["Пестушка", "контакт, мягкая речь"],
        ["Потешка", "ритм речи, игра"],
        ["Колыбельная", "мягкий звук"],
        ["Закличка", "интонация зова"],
        ["Игровая песня", "пение + правило"],
        ["Хороводная", "совместность"],
    ], [50 * mm, 60 * mm], row_h=12 * mm)
    footer(c, 4)
    c.showPage()

    bg(c)
    title(c, "Значение для детей", "Зачем фольклор голосу и развитию")
    draw_img(c, 5, 12 * mm, 30 * mm, 145 * mm, 100 * mm)
    table_simple(c, 165 * mm, H - 30 * mm, [
        ["Сфера", "Что даёт"],
        ["Вокальная", "естественная интонация"],
        ["Ритмическая", "слово + движение"],
        ["Речевая", "артикуляция, словарь"],
        ["Эмоциональная", "безопасность, радость"],
        ["Культурная", "традиция, образы"],
        ["Социальная", "контакт в круге"],
    ], [45 * mm, 65 * mm], row_h=12 * mm)
    footer(c, 5)
    c.showPage()

    bg(c)
    title(c, "Практическая разминка", "1–2 минуты фольклорного входа")
    draw_img(c, 6, 12 * mm, 28 * mm, 150 * mm, 110 * mm)
    table_simple(c, 170 * mm, H - 30 * mm, [
        ["Упражнение", "Задача"],
        ["Плечи / кисти", "снять зажим"],
        ["Зевота-улыбка", "свобода лица"],
        ["Шёпот → голос", "без форса"],
        ["Эхо-потешка", "интонация"],
        ["Жест-подпись", "1 жест"],
        ["Стоп", "мгновенно тихо"],
    ], [50 * mm, 55 * mm], row_h=12 * mm)
    footer(c, 6)
    c.showPage()

    bg(c)
    title(c, "Певческие и ритмические упражнения", "Голос и ритм на фольклоре")
    draw_img(c, 7, 12 * mm, 28 * mm, 150 * mm, 110 * mm)
    table_simple(c, 170 * mm, H - 30 * mm, [
        ["Певческое", "Ритмическое"],
        ["мягкие гласные", "хлопки на слова"],
        ["из речи в пение", "шаг на месте"],
        ["эхо в характере", "передай ритм"],
        ["тихий зов", "ложки дозированно"],
        ["повтор с опорой", "стоп на паузе"],
    ], [55 * mm, 50 * mm], row_h=12 * mm)
    footer(c, 7)
    c.showPage()

    bg(c)
    title(c, "Репертуар от рождения до 7 лет", "Что брать по возрасту")
    draw_img(c, 8, 12 * mm, 28 * mm, 145 * mm, 105 * mm)
    table_simple(c, 165 * mm, H - 30 * mm, [
        ["Возраст", "Приоритет"],
        ["0–1", "пестушки, колыбельные"],
        ["1–1,5", "простые потешки"],
        ["1,5–3", "потешки, игровые"],
        ["3–5", "заклички, игровые"],
        ["5–7", "игровые, хороводные"],
    ], [35 * mm, 75 * mm], row_h=14 * mm)
    footer(c, 8)
    c.showPage()

    bg(c)
    title(c, "Критерии отбора", "Беру / не беру")
    draw_img(c, 9, 12 * mm, 28 * mm, 120 * mm, 110 * mm)
    card(c, 145 * mm, 45 * mm, 65 * mm, 95 * mm, GREEN, "Беру ✓", [
        "короткий текст", "ясный ритм",
        "мягкий характер", "1 жест", "по возрасту",
    ])
    card(c, 218 * mm, 45 * mm, 60 * mm, 95 * mm, RED, "Не беру ✕", [
        "длинный архаичный", "сложная мелодия",
        "пугающий образ", "сложная постановка", "народность «для галочки»",
    ])
    footer(c, 9)
    c.showPage()

    bg(c)
    title(c, "Карточка подбора", "Как заполнять репертуарную карточку")
    draw_img(c, 10, 12 * mm, 28 * mm, 150 * mm, 110 * mm)
    text_block(c, 170 * mm, H - 40 * mm, [
        "Возраст",
        "Жанр",
        "Цель",
        "Длина",
        "Жест / опора",
        "Риск + стоп",
        "",
        "возраст → жанр → вход",
        "→ показ → проба → стоп",
    ], size=11, color=TEAL_D, leading=7 * mm)
    footer(c, 10)
    c.showPage()

    bg(c)
    title(c, "Работа в группах", "Фрагмент 60–90 секунд")
    draw_img(c, 11, 12 * mm, 28 * mm, 150 * mm, 110 * mm)
    table_simple(c, 170 * mm, H - 30 * mm, [
        ["Шаг", "Действие"],
        ["1", "возраст и цель"],
        ["2", "вход (1 фраза)"],
        ["3", "мягкий показ"],
        ["4", "проба"],
        ["5", "стоп"],
    ], [20 * mm, 85 * mm], row_h=11 * mm)
    card(c, 170 * mm, 22 * mm, 105 * mm, 35 * mm, TEAL, "Рубрика Да/Нет", [
        "жанр верен · образец короткий", "голос мягкий · жест · стоп",
    ])
    footer(c, 11)
    c.showPage()

    bg(c, TEAL_D)
    rgb(c, GOLD)
    c.setFont("DejaVu", 11)
    c.drawString(14 * mm, H - 16 * mm, "Итог + творческие задания")
    rgb(c, WHITE)
    c.setFont("DejaVuBold", 20)
    c.drawString(14 * mm, H - 32 * mm, "Формула фольклора")
    c.drawString(14 * mm, H - 42 * mm, "в ДОУ")
    rgb(c, SAND)
    c.setFont("DejaVu", 12)
    for i, line in enumerate(["Короткий жанр.", "Мягкий голос.", "Ясный ритм / жест.", "Игра по возрасту."]):
        c.drawString(14 * mm, H - 58 * mm - i * 8 * mm, line)
    draw_img(c, 12, W - 145 * mm, H - 120 * mm, 130 * mm, 90 * mm)
    hw = [
        ("1. Таблица + картотека", "жанры · 6 образцов"),
        ("2. Эссе + сценарий", "мягкость вместо крика"),
        ("3. Сравнение", "упрощать / усложнять"),
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
    c.drawCentredString(W / 2, 12 * mm, "Не сцена ради сцены — а тёплый голос, короткое слово и живая игра.")
    c.showPage()

    c.save()
    ART.parent.mkdir(parents=True, exist_ok=True)
    ART.write_bytes(OUT.read_bytes())
    print(f"OK pdf={OUT}")


if __name__ == "__main__":
    build()
