#!/usr/bin/env python3
"""Landscape slide-deck PDF twin for lesson 6 — with planned illustrations."""

from pathlib import Path

from reportlab.lib.pagesizes import landscape
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

W, H = landscape((297 * mm, 210 * mm))
ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "zanyatie-06-assets"
OUT = ROOT / "zanyatie-06-prezentaciya.pdf"
ART = Path("/opt/cursor/artifacts/zanyatie-06-prezentaciya.pdf")

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

IMG = {i: ASSETS / f"z06-{i:02d}-{name}.jpg" for i, name in [
    (1, "title"), (2, "doors"), (3, "ritual"), (4, "mindmap"),
    (5, "voice-waves"), (6, "intonations"), (7, "genres"), (8, "knees"),
    (9, "contact"), (10, "traffic"), (11, "stations"), (12, "arms"),
    (13, "ladushki"), (14, "pendulum"), (15, "rattle"), (16, "training"),
    (17, "checklist"), (18, "finale"),
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
    c.drawString(14 * mm, 8 * mm, f"Занятие 6 · Ритм 0–1,5 лет · Голос · Касание · Пауза   {n}/{total}")


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
    path = IMG[n]
    c.drawImage(str(path), x, y, width=w, height=h, preserveAspectRatio=True, mask="auto")


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
    text_box(c, 14 * mm, H - 30 * mm, "ЗАНЯТИЕ 6 · МОДУЛЬ II", size=11, bold=True, color=GOLD)
    text_box(c, 14 * mm, H - 50 * mm, "Ритмическое развитие детей", size=22, bold=True, color=WHITE)
    text_box(c, 14 * mm, H - 62 * mm, "от рождения до 1,5 лет", size=22, bold=True, color=WHITE)
    text_box(c, 14 * mm, H - 80 * mm, "Не танец по правилам — телесный диалог", size=12, color=SAND)
    text_box(c, 14 * mm, H - 95 * mm, "услышал → почувствовал рядом", size=11, color=WHITE)
    text_box(c, 14 * mm, H - 105 * mm, "со взрослым → оживился / успокоился", size=11, color=WHITE)
    draw_img(c, 1, 145 * mm, 35 * mm, 135 * mm, 145 * mm)
    text_box(c, 14 * mm, 18 * mm, "Бабаджан · Ветлугина · Картушина", size=10, color=SAND)
    c.showPage()

    # 2
    bg(c)
    title(c, "Чем этот возраст особенный", "Самый ранний этаж ритмики")
    draw_img(c, 2, 12 * mm, 35 * mm, 145 * mm, 120 * mm)
    draw_table(c, 165 * mm, H - 35 * mm, [55 * mm, 60 * mm], 14 * mm, [
        ["0–1,5 лет", "Позже (3–5+)"],
        ["совместное движение", "самостоятельность"],
        ["голос важнее колонки", "запись шире"],
        ["нет строя", "игровые правила"],
        ["контакт = главное", "контакт + задача"],
    ])
    text_box(c, 165 * mm, 40 * mm, "Младенец не готовит номер —", size=11, bold=True, color=TEAL_D)
    text_box(c, 165 * mm, 32 * mm, "учится быть в ритме рядом.", size=11, bold=True, color=TEAL_D)
    footer(c, 2)
    c.showPage()

    # 3
    bg(c)
    title(c, "Чему учимся сегодня", "Цель занятия для студента")
    steps = [
        "1. Понять слух и движение младенца",
        "2. Увидеть реакции на интонации",
        "3. Использовать колыбельные, потешки, пестушки",
        "4. Двигаться вместе со взрослым",
        "5. Держать телесный и эмоциональный контакт",
        "6. Провести мягкие игры и контрасты",
    ]
    for i, t in enumerate(steps):
        text_box(c, 14 * mm, H - 40 * mm - i * 14 * mm, t, size=12, color=INK)
    draw_img(c, 3, 160 * mm, 30 * mm, 120 * mm, 140 * mm)
    footer(c, 3)
    c.showPage()

    # 4
    bg(c)
    title(c, "Карта темы", "От слуха — к короткой забаве")
    draw_img(c, 4, 12 * mm, 28 * mm, 175 * mm, 135 * mm)
    draw_table(c, 195 * mm, H - 40 * mm, [30 * mm, 55 * mm], 12 * mm, [
        ["Слайды", "Блок"], ["5–11", "теория"], ["12–16", "практика"], ["17–18", "чек-лист"],
    ])
    for i, t in enumerate(["1. Слух", "2. Интонации", "3. Жанры", "4. Вместе", "5. Контакт", "6. Практика"]):
        text_box(c, 195 * mm, 95 * mm - i * 10 * mm, t, size=11, color=TEAL_D)
    footer(c, 4)
    c.showPage()

    # 5
    bg(c)
    title(c, "Слуховое и двигательное восприятие", "Звук входит вместе с теплом рук")
    draw_img(c, 5, 12 * mm, 40 * mm, 145 * mm, 115 * mm)
    draw_table(c, 165 * mm, H - 35 * mm, [50 * mm, 65 * mm], 14 * mm, [
        ["Период", "Слух / движение"],
        ["Первые месяцы", "голос → реакции"],
        ["~полгода", "погремушка → оживление"],
        ["1–1,5 года", "сигналы → подражание"],
    ])
    round_rect(c, 165 * mm, 35 * mm, 115 * mm, 40 * mm, SAND)
    text_box(c, 170 * mm, 60 * mm, "голос → тело → повтор", size=11, bold=True, color=TEAL_D)
    text_box(c, 170 * mm, 48 * mm, "Сенсорный опыт, не комбинация.", size=10, color=INK)
    footer(c, 5)
    c.showPage()

    # 6
    bg(c)
    title(c, "Реакции на музыкальные интонации", "Интонация — эмоциональное лицо звука")
    draw_img(c, 6, 12 * mm, 40 * mm, 145 * mm, 115 * mm)
    draw_table(c, 165 * mm, H - 35 * mm, [60 * mm, 55 * mm], 13 * mm, [
        ["Интонация", "Реакция"],
        ["Мягкая певучая", "спокойствие"],
        ["Светлая игривая", "оживление"],
        ["Тихо / чуть громче", "внимание"],
        ["Резкая громкая ✕", "плач"],
    ])
    text_box(c, 165 * mm, 40 * mm, "лицо и голос → предмет → запись", size=10, bold=True, color=TEAL_D)
    footer(c, 6)
    c.showPage()

    # 7
    bg(c)
    title(c, "Колыбельные, потешки, пестушки", "Главный «учебник» ритма для младенца")
    draw_img(c, 7, 12 * mm, 45 * mm, 150 * mm, 110 * mm)
    draw_table(c, 170 * mm, H - 35 * mm, [50 * mm, 60 * mm], 13 * mm, [
        ["Жанр", "Как"],
        ["Колыбельная", "качать, тихо"],
        ["Потешка", "жест, ладушки"],
        ["Пестушка", "касание"],
    ])
    card(c, 170 * mm, 35 * mm, 52 * mm, 45 * mm, LEAF, "Беру", ["добрый образ", "2–6 строк", "можно стоп"])
    card(c, 228 * mm, 35 * mm, 52 * mm, 45 * mm, RED, "Не беру", ["страшилки", "длинный текст", "дожать"])
    footer(c, 7)
    c.showPage()

    # 8
    bg(c)
    title(c, "Движение вместе со взрослым", "Взрослое тело — безопасный метроном")
    draw_img(c, 8, 12 * mm, 35 * mm, 155 * mm, 120 * mm)
    draw_table(c, 175 * mm, H - 35 * mm, [55 * mm, 50 * mm], 12 * mm, [
        ["Форма", "Когда"],
        ["На руках / коленях", "база"],
        ["Лёжа — мягко", "младшие"],
        ["Сидя с опорой", "хлопаем"],
        ["У опоры", "при готовности"],
    ])
    for i, t in enumerate(["• приглашать, не тащить", "• ритм задаёт взрослый", "• коротко (20–40 сек)", "• плач = стоп", "• ✕ не топать в строю"]):
        text_box(c, 175 * mm, 70 * mm - i * 9 * mm, t, size=10, color=TEAL_D)
    footer(c, 8)
    c.showPage()

    # 9
    bg(c)
    title(c, "Телесная чувствительность и контакт", "Без взгляда и тепла ритм не приживается")
    draw_img(c, 9, 12 * mm, 35 * mm, 145 * mm, 120 * mm)
    draw_table(c, 165 * mm, H - 35 * mm, [55 * mm, 60 * mm], 14 * mm, [
        ["Есть контакт", "Нет контакта"],
        ["оживление / покой", "вздрагивание, плач"],
        ["повтор приятен", "стимул = давление"],
        ["чуть усложнить", "упростить / стоп"],
    ])
    round_rect(c, 165 * mm, 35 * mm, 115 * mm, 40 * mm, SAND)
    text_box(c, 172 * mm, 58 * mm, "взгляд + голос + касание + пауза", size=10, bold=True, color=TEAL_D)
    text_box(c, 172 * mm, 46 * mm, "= эмоциональная безопасность", size=10, bold=True, color=TEAL_D)
    footer(c, 9)
    c.showPage()

    # 10
    bg(c)
    title(c, "Можно и нельзя в 0–1,5 лет", "Границы мягкости · светофор")
    draw_img(c, 10, 12 * mm, 30 * mm, 120 * mm, 130 * mm)
    card(c, 145 * mm, 55 * mm, 65 * mm, 100 * mm, GREEN, "Можно ✓", [
        "петь, качать, гладить",
        "короткие потешки",
        "мягкий контраст",
        "погремушка «спит»",
        "стоп по состоянию",
    ])
    card(c, 218 * mm, 55 * mm, 62 * mm, 100 * mm, RED, "Нельзя ✕", [
        "трясти, подбрасывать",
        "долбить до отказа",
        "крик / хлопок у уха",
        "долгий хаос-шум",
        "танец по правилам",
    ])
    text_box(c, 145 * mm, 35 * mm, "Право на паузу — профессиональный навык.", size=11, bold=True, color=TEAL_D)
    footer(c, 10)
    c.showPage()

    # 11
    bg(c)
    title(c, "Обзор практики", "Пять мягких блоков")
    draw_img(c, 11, 12 * mm, 28 * mm, 175 * mm, 135 * mm)
    for i, t in enumerate(["1. Игры на руках", "2. Ладушки / пальчики", "3. Покачивания", "4. Погремушки", "5. Сигналы и контрасты", "", "Одна задача", "и обязательный стоп."]):
        text_box(c, 195 * mm, H - 40 * mm - i * 11 * mm, t, size=11, bold=(i >= 6), color=TEAL_D if i >= 6 else INK)
    footer(c, 11)
    c.showPage()

    # 12
    bg(c)
    title(c, "Практика 1. Игры на руках", "Покачать — не значит растрясти")
    draw_img(c, 12, 12 * mm, 35 * mm, 150 * mm, 120 * mm)
    draw_table(c, 170 * mm, H - 35 * mm, [22 * mm, 90 * mm], 13 * mm, [
        ["Шаг", "Действие"],
        ["1", "устойчиво взять, голова"],
        ["2", "тихий напев + качание"],
        ["3", "лёгкий топ-топ"],
        ["4", "стоп: прижать, пауза"],
    ])
    text_box(c, 170 * mm, 45 * mm, "не трясти · не подбрасывать", size=11, bold=True, color=CORAL)
    text_box(c, 170 * mm, 35 * mm, "читать «плач» · стоп", size=11, bold=True, color=CORAL)
    footer(c, 12)
    c.showPage()

    # 13
    bg(c)
    title(c, "Практика 2. Ладушки и пальчиковые игры", "Голос теплее хлопка")
    draw_img(c, 13, 12 * mm, 35 * mm, 145 * mm, 120 * mm)
    draw_table(c, 165 * mm, H - 35 * mm, [55 * mm, 60 * mm], 13 * mm, [
        ["Хорошо", "Плохо"],
        ["голос слышнее хлопка", "хлопки глушат слово"],
        ["темп удобен малышу", "гонка «успеть всё»"],
        ["2–3 повтора", "долбить до отказа"],
        ["пауза — взгляд", "лицо в телефон"],
    ])
    text_box(c, 165 * mm, 40 * mm, "потешка → жест → повтор → пауза", size=10, bold=True, color=TEAL_D)
    footer(c, 13)
    c.showPage()

    # 14
    bg(c)
    title(c, "Практика 3. Покачивания под музыку", "Медленный пульс и мягкий контраст")
    draw_img(c, 14, 12 * mm, 35 * mm, 150 * mm, 120 * mm)
    draw_table(c, 170 * mm, H - 35 * mm, [40 * mm, 70 * mm], 13 * mm, [
        ["Вариант", "Содержание"],
        ["На руках", "колыбельная"],
        ["На коленях", "«кач-кач»"],
        ["Лёжа", "мягкое ведение"],
        ["Контраст", "20с → 10с → покой"],
    ])
    text_box(c, 170 * mm, 45 * mm, "«Бодрее» ≠ «громко».", size=11, bold=True, color=TEAL_D)
    footer(c, 14)
    c.showPage()

    # 15
    bg(c)
    title(c, "Практика 4. Погремушка и звуковые контрасты", "Учить тишине так же, как звуку")
    draw_img(c, 15, 12 * mm, 40 * mm, 145 * mm, 115 * mm)
    draw_table(c, 165 * mm, H - 35 * mm, [20 * mm, 95 * mm], 11 * mm, [
        ["Шаг", "Действие"],
        ["1", "показать лицом и голосом"],
        ["2", "тихо потрясти в ритме"],
        ["3", "«погремушка спит»"],
        ["4", "короткий звук → сон"],
        ["5", "вместе слегка потрясти"],
    ])
    card(c, 165 * mm, 30 * mm, 50 * mm, 35 * mm, LEAF, "Можно", ["3–5 смен", "стоп"])
    card(c, 222 * mm, 30 * mm, 55 * mm, 35 * mm, RED, "Нельзя", ["крик у уха", "дискотека"])
    footer(c, 15)
    c.showPage()

    # 16
    bg(c)
    title(c, "Мини-тренинг студента", "60–70 секунд мягкого ритуала")
    draw_img(c, 16, 12 * mm, 35 * mm, 150 * mm, 120 * mm)
    draw_table(c, 170 * mm, H - 35 * mm, [22 * mm, 90 * mm], 12 * mm, [
        ["Шаг", "Действие"],
        ["1", "выбрать форму"],
        ["2", "одна потешка / напев"],
        ["3", "начало → повтор → стоп"],
        ["4", "можно + нельзя"],
    ])
    card(c, 170 * mm, 30 * mm, 110 * mm, 45 * mm, TEAL, "Рубрика Да/Нет", [
        "контакт · мягкость · краткость",
        "пауза · без резкости",
        "понятно, зачем младенцу",
    ])
    footer(c, 16)
    c.showPage()

    # 17
    bg(c)
    title(c, "Чек-лист работы с 0–1,5 лет", "Перед возрастом 1,5–3")
    draw_img(c, 17, 12 * mm, 35 * mm, 135 * mm, 120 * mm)
    checks = [
        "1. Сенсомоторика и контакт, не номер",
        "2. Читаю реакцию на интонацию",
        "3. Различаю жанры",
        "4. Вместе, не тащу",
        "5. Взгляд, голос, касание",
        "6. Ладушки / качание мягко",
        "7. Погремушка со «сном»",
        "8. Стоп при переутомлении",
    ]
    for i, t in enumerate(checks):
        round_rect(c, 155 * mm, H - 40 * mm - i * 15 * mm, 125 * mm, 12 * mm, SOFT if i % 2 == 0 else SAND, r=4)
        text_box(c, 160 * mm, H - 36 * mm - i * 15 * mm, t, size=9, color=INK)
    text_box(c, 60 * mm, 20 * mm, "ГОЛОС  ↔  КАСАНИЕ  ↔  ПАУЗА", size=14, bold=True, color=TEAL_D)
    footer(c, 17)
    c.showPage()

    # 18
    bg(c, TEAL_D)
    circle(c, 15 * mm, H - 15 * mm, 25 * mm, TEAL)
    circle(c, W - 18 * mm, 20 * mm, 28 * mm, CORAL)
    text_box(c, 14 * mm, H - 28 * mm, "Итог + домашнее задание", size=11, bold=True, color=GOLD)
    text_box(c, 14 * mm, H - 48 * mm, "Ритм начинается", size=20, bold=True, color=WHITE)
    text_box(c, 14 * mm, H - 60 * mm, "с тёплого взрослого", size=20, bold=True, color=WHITE)
    text_box(c, 14 * mm, H - 80 * mm, "Мягкий голос. Короткая форма.", size=11, color=SAND)
    text_box(c, 14 * mm, H - 90 * mm, "Право на паузу.", size=11, color=SAND)
    draw_img(c, 18, 145 * mm, 85 * mm, 135 * mm, 95 * mm)
    hw = [
        ("1. Таблица", ["слух · ответ · роль", "примеры · можно/нельзя"]),
        ("2. Ритуал 2–3 мин", ["качание + потешка", "+ погремушка (8–12 мес.)"]),
        ("3. Мини-эссе", ["почему контакт важнее", "идеального жеста"]),
    ]
    for i, (t, lines) in enumerate(hw):
        round_rect(c, 14 * mm + i * 90 * mm, 25 * mm, 82 * mm, 45 * mm, WHITE)
        text_box(c, 18 * mm + i * 90 * mm, 58 * mm, t, size=10, bold=True, color=TEAL_D)
        for j, line in enumerate(lines):
            text_box(c, 18 * mm + i * 90 * mm, 48 * mm - j * 8 * mm, line, size=8, color=INK)
    text_box(c, 20 * mm, 12 * mm, "Сохраните мягкость — ритм начнётся с правильного этажа.", size=9, color=GOLD)
    c.showPage()

    c.save()
    ART.parent.mkdir(parents=True, exist_ok=True)
    ART.write_bytes(OUT.read_bytes())
    print(f"OK pdf={OUT}")


if __name__ == "__main__":
    build()
