#!/usr/bin/env python3
"""Landscape slide-deck PDF twin for lesson 6 presentation."""

from pathlib import Path

from reportlab.lib.pagesizes import landscape
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

W, H = landscape((297 * mm, 210 * mm))
OUT = Path(__file__).resolve().parent / "zanyatie-06-prezentaciya.pdf"
ART = Path("/opt/cursor/artifacts/zanyatie-06-prezentaciya.pdf")

TEAL = (0.16, 0.48, 0.55)
TEAL_D = (0.10, 0.35, 0.42)
CORAL = (0.83, 0.48, 0.42)
GOLD = (0.79, 0.64, 0.31)
LEAF = (0.35, 0.56, 0.48)
SKY = (0.36, 0.61, 0.72)
ROSE = (0.72, 0.42, 0.49)
CREAM = (0.97, 0.98, 0.99)
INK = (0.12, 0.18, 0.23)
MUTED = (0.35, 0.43, 0.47)
WHITE = (1, 1, 1)
SAND = (0.91, 0.94, 0.96)
SOFT = (0.89, 0.94, 0.95)
RED = (0.77, 0.36, 0.36)
GREEN = (0.29, 0.60, 0.48)


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
    c.setFont("DejaVuBold", 20)
    c.drawString(14 * mm, H - 16 * mm, text)
    if sub:
        rgb(c, MUTED)
        c.setFont("DejaVu", 11)
        c.drawString(14 * mm, H - 24 * mm, sub)


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


def draw_table(c, x, y, col_w, row_h, rows, header=True):
    for r, row in enumerate(rows):
        yy = y - r * row_h
        for ci, cell in enumerate(row):
            xx = x + sum(col_w[:ci])
            fill = TEAL if r == 0 and header else (SOFT if r % 2 else WHITE)
            rgb(c, fill)
            c.rect(xx, yy - row_h, col_w[ci], row_h, fill=1, stroke=0)
            rgb(c, WHITE if r == 0 and header else INK)
            c.setFont("DejaVuBold" if r == 0 else "DejaVu", 9 if r else 10)
            c.drawString(xx + 2 * mm, yy - row_h + 3.5 * mm, cell[:58])


def card(c, x, y, w, h, color, title_t, lines):
    round_rect(c, x, y, w, h, color)
    text_box(c, x + 5 * mm, y + h - 10 * mm, title_t, size=13, bold=True, color=WHITE)
    yy = y + h - 20 * mm
    for line in lines:
        text_box(c, x + 5 * mm, yy, line, size=10, color=WHITE)
        yy -= 6 * mm


def build():
    fonts()
    c = canvas.Canvas(str(OUT), pagesize=(W, H))
    total = 18

    # 1 title
    bg(c, TEAL_D)
    circle(c, 20 * mm, H - 20 * mm, 35 * mm, TEAL)
    circle(c, W - 15 * mm, 20 * mm, 40 * mm, CORAL)
    circle(c, W - 30 * mm, H - 15 * mm, 22 * mm, GOLD)
    text_box(c, 40 * mm, H - 45 * mm, "ЗАНЯТИЕ 6 · МОДУЛЬ II", size=12, bold=True, color=GOLD)
    text_box(c, 40 * mm, H - 70 * mm, "Ритмическое развитие детей", size=28, bold=True, color=WHITE)
    text_box(c, 40 * mm, H - 85 * mm, "от рождения до 1,5 лет", size=28, bold=True, color=WHITE)
    text_box(c, 40 * mm, H - 105 * mm, "Не танец по правилам — телесный диалог", size=14, color=SAND)
    text_box(c, 30 * mm, H - 125 * mm, "услышал → почувствовал рядом со взрослым → оживился / успокоился", size=12, color=WHITE)
    for i, (lab, col) in enumerate([("ухо", SKY), ("сердце", CORAL), ("руки", LEAF), ("погремушка", GOLD)]):
        round_rect(c, 35 * mm + i * 55 * mm, 35 * mm, 48 * mm, 14 * mm, col, r=6)
        text_box(c, 42 * mm + i * 55 * mm, 39 * mm, lab, size=11, bold=True, color=WHITE)
    text_box(c, 50 * mm, 16 * mm, "Бабаджан · Ветлугина · Картушина «Забавы для малышей»", size=10, color=SAND)
    c.showPage()

    # 2
    bg(c)
    title(c, "Чем этот возраст особенный", "Самый ранний этаж ритмики")
    draw_table(
        c, 14 * mm, H - 40 * mm, [85 * mm, 90 * mm], 14 * mm,
        [
            ["0–1,5 лет", "Позже (3–5+)"],
            ["совместное движение", "больше самостоятельности"],
            ["голос важнее колонки", "запись используется шире"],
            ["нет строя и «стопа по правилу»", "появляются игровые правила"],
            ["контакт = главное условие", "контакт важен, но уже есть задача"],
        ],
    )
    card(c, 200 * mm, H - 95 * mm, 80 * mm, 45 * mm, TEAL, "Дверь открыта", ["тёплый диалог", "голос + касание", "короткий повтор"])
    card(c, 200 * mm, H - 155 * mm, 80 * mm, 45 * mm, RED, "Дверь закрыта", ["номер / строй", "танец по правилам", "давление до отказа"])
    text_box(c, 14 * mm, 22 * mm, "Младенец не готовит номер — он учится быть в ритме рядом со взрослым.", size=12, bold=True, color=TEAL_D)
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
        yy = H - 45 * mm - i * 16 * mm
        circle(c, 22 * mm, yy + 3 * mm, 5 * mm, TEAL if i % 2 == 0 else LEAF)
        text_box(c, 32 * mm, yy, t, size=13, color=INK)
    card(c, 200 * mm, H - 95 * mm, 80 * mm, 42 * mm, TEAL, "Знает", ["особенности 0–1,5 лет", "границы можно / нельзя"])
    card(c, 200 * mm, H - 155 * mm, 80 * mm, 48 * mm, CORAL, "Умеет", ["покачивание / ладушки", "погремушка со «сном»", "стоп при переутомлении"])
    footer(c, 3)
    c.showPage()

    # 4
    bg(c)
    title(c, "Карта темы", "От слуха — к короткой забаве")
    topics = [
        (TEAL, "1. Слух и движение"),
        (SKY, "2. Интонации"),
        (LEAF, "3. Колыбельная / потешка"),
        (GOLD, "4. Вместе со взрослым"),
        (CORAL, "5. Контакт"),
        (ROSE, "6. Практика игр"),
    ]
    for i, (col, t) in enumerate(topics):
        col_i, row_i = i % 3, i // 3
        card(c, 14 * mm + col_i * 90 * mm, H - 90 * mm - row_i * 50 * mm, 82 * mm, 40 * mm, col, t, ["ключевой блок занятия"])
    draw_table(
        c, 14 * mm, 55 * mm, [50 * mm, 200 * mm], 10 * mm,
        [["Слайды", "Блок"], ["5–11", "теория"], ["12–16", "практика"], ["17–18", "чек-лист и итог"]],
    )
    footer(c, 4)
    c.showPage()

    # 5
    bg(c)
    title(c, "Слуховое и двигательное восприятие", "Звук входит вместе с теплом рук")
    draw_table(
        c, 14 * mm, H - 40 * mm, [55 * mm, 100 * mm, 110 * mm], 16 * mm,
        [
            ["Период", "Слух", "Движение"],
            ["Первые месяцы", "голос, ориентировка на звук", "общие реакции тела"],
            ["Ближе к полугоду", "интерес к погремушке, интонации", "тянется, трясёт, оживляется"],
            ["К 1–1,5 годам", "короткие игровые сигналы", "подражает простым жестам рядом"],
        ],
    )
    round_rect(c, 14 * mm, 45 * mm, 265 * mm, 35 * mm, SAND)
    text_box(c, 30 * mm, 65 * mm, "голос / звук → реакция тела → повтор в контакте → привычный отклик", size=13, bold=True, color=TEAL_D)
    text_box(c, 30 * mm, 52 * mm, "Даём сенсорный опыт, а не комбинацию.", size=11, color=MUTED)
    footer(c, 5)
    c.showPage()

    # 6
    bg(c)
    title(c, "Реакции на музыкальные интонации", "Интонация — эмоциональное лицо звука")
    draw_table(
        c, 12 * mm, H - 38 * mm, [55 * mm, 95 * mm, 115 * mm], 14 * mm,
        [
            ["Интонация", "Желаемая реакция", "Чего избегать"],
            ["Мягкая певучая", "спокойствие, контакт", "громкая запись без тепла голоса"],
            ["Светлая игривая", "оживление", "длинная серия до перевозбуждения"],
            ["Тихо / чуть громче", "внимание", "резкие скачки и крик"],
            ["Резкая громкая", "вздрагивание, плач", "использовать «для веселья»"],
        ],
    )
    for i, (lab, col) in enumerate([("спокойно ✓", LEAF), ("игриво ✓", GOLD), ("резко ✕", RED)]):
        round_rect(c, 30 * mm + i * 80 * mm, 40 * mm, 70 * mm, 14 * mm, col, r=6)
        text_box(c, 42 * mm + i * 80 * mm, 44 * mm, lab, size=11, bold=True, color=WHITE)
    text_box(c, 40 * mm, 25 * mm, "сначала лицо и голос → потом предмет → потом запись", size=12, bold=True, color=TEAL_D)
    footer(c, 6)
    c.showPage()

    # 7
    bg(c)
    title(c, "Колыбельные, потешки, пестушки", "Главный «учебник» ритма для младенца")
    draw_table(
        c, 12 * mm, H - 38 * mm, [50 * mm, 100 * mm, 115 * mm], 15 * mm,
        [
            ["Жанр", "Ритмическая роль", "Как использовать"],
            ["Колыбельная", "медленный пульс, успокоение", "покачивание, тихий голос"],
            ["Потешка", "слоговой ритм, повтор", "жест рук, ладушки"],
            ["Пестушка", "ритм заботы + касание", "поглаживание, пальчики"],
        ],
    )
    card(c, 14 * mm, 30 * mm, 125 * mm, 55 * mm, LEAF, "Беру", ["добрый короткий образ", "2–6 строк на заход", "можно остановиться"])
    card(c, 150 * mm, 30 * mm, 125 * mm, 55 * mm, RED, "Не беру", ["страшилки, резкая динамика", "длинный монолог", "«дожать до конца любой ценой»"])
    footer(c, 7)
    c.showPage()

    # 8
    bg(c)
    title(c, "Движение вместе со взрослым", "Взрослое тело — безопасный метроном")
    draw_table(
        c, 12 * mm, H - 40 * mm, [90 * mm, 80 * mm], 14 * mm,
        [
            ["Форма", "Когда уместно"],
            ["На руках / на коленях", "база возраста"],
            ["Лёжа — мягкое ведение рук/ног", "младшие месяцы"],
            ["Сидя с опорой", "вместе хлопаем, качаемся"],
            ["У опоры / с поддержкой", "только при готовности"],
        ],
    )
    card(c, 195 * mm, H - 130 * mm, 85 * mm, 85 * mm, TEAL, "Принципы", [
        "приглашать, не тащить",
        "ритм задаёт взрослый",
        "коротко (20–40 сек)",
        "плач / отворот = стоп",
        "✗ не топать в строю",
    ])
    footer(c, 8)
    c.showPage()

    # 9
    bg(c)
    title(c, "Телесная чувствительность и контакт", "Без взгляда и тепла ритм не приживается")
    draw_table(
        c, 12 * mm, H - 40 * mm, [130 * mm, 135 * mm], 16 * mm,
        [
            ["Есть контакт", "Нет контакта"],
            ["осмысленное оживление / успокоение", "вздрагивание, отворот, плач"],
            ["повтор приятен", "стимул как давление"],
            ["можно чуть усложнить", "нужно упростить / остановиться"],
        ],
    )
    round_rect(c, 14 * mm, 40 * mm, 265 * mm, 45 * mm, SAND)
    text_box(c, 25 * mm, 68 * mm, "взгляд + голос + касание + пауза = эмоциональная безопасность", size=14, bold=True, color=TEAL_D)
    text_box(c, 25 * mm, 52 * mm, "Ритм 0–1,5 лет = мягкий слух + совместное тело + голос + повтор + безопасность.", size=11, color=INK)
    footer(c, 9)
    c.showPage()

    # 10
    bg(c)
    title(c, "Можно и нельзя в 0–1,5 лет", "Границы мягкости")
    card(c, 14 * mm, 40 * mm, 130 * mm, 115 * mm, GREEN, "Можно ✓", [
        "петь, качать, гладить в ритме",
        "короткие потешки и ладушки",
        "мягкий контраст тихо / чуть громче",
        "погремушка с ритуалом «спит»",
        "остановиться по состоянию ребёнка",
    ])
    card(c, 155 * mm, 40 * mm, 125 * mm, 115 * mm, RED, "Нельзя ✕", [
        "трясти, подбрасывать",
        "долбить до отказа",
        "крик, хлопок у уха",
        "долгий хаотичный шум",
        "«танец по правилам», строй",
    ])
    text_box(c, 40 * mm, 22 * mm, "Право на паузу — профессиональный навык, не слабость.", size=12, bold=True, color=TEAL_D)
    footer(c, 10)
    c.showPage()

    # 11
    bg(c)
    title(c, "Обзор практики", "Пять мягких блоков")
    blocks = [
        (TEAL, "Игры на руках", "ритм через тело"),
        (SKY, "Ладушки", "слог + жест"),
        (LEAF, "Покачивания", "медленный пульс"),
        (GOLD, "Погремушки", "звук ↔ тишина"),
        (CORAL, "Контрасты", "без перегруза"),
    ]
    for i, (col, t, b) in enumerate(blocks):
        card(c, 10 * mm + i * 56 * mm, 50 * mm, 52 * mm, 100 * mm, col, t, [b, "", "одна задача", "обязательный стоп"])
    text_box(c, 20 * mm, 30 * mm, "В каждой пробе — одна задача и обязательный стоп.", size=11, color=MUTED)
    footer(c, 11)
    c.showPage()

    # 12
    bg(c)
    title(c, "Практика 1. Игры на руках", "Покачать — не значит растрясти")
    draw_table(
        c, 12 * mm, H - 40 * mm, [20 * mm, 155 * mm], 14 * mm,
        [
            ["Шаг", "Действие"],
            ["1", "устойчиво взять, поддержать голову"],
            ["2", "тихий напев + мягкое качание"],
            ["3", "чуть оживлённый напев + лёгкий топ-топ"],
            ["4", "стоп: прижать, снизить голос, пауза"],
        ],
    )
    card(c, 200 * mm, H - 130 * mm, 80 * mm, 85 * mm, CORAL, "Безопасность", [
        "не трясти",
        "не подбрасывать",
        "читать «плач»",
        "стоп сразу",
    ])
    footer(c, 12)
    c.showPage()

    # 13
    bg(c)
    title(c, "Практика 2. Ладушки и пальчиковые игры", "Голос теплее хлопка")
    draw_table(
        c, 12 * mm, H - 40 * mm, [130 * mm, 135 * mm], 14 * mm,
        [
            ["Хорошо", "Плохо"],
            ["голос слышнее хлопка", "хлопки глушат слово"],
            ["темп удобен малышу", "гонка «успеть всё»"],
            ["2–3 повтора", "долбить до отказа"],
            ["пауза посмотреть в глаза", "лицо в сторону / в телефон"],
        ],
    )
    round_rect(c, 14 * mm, 35 * mm, 265 * mm, 40 * mm, SAND)
    text_box(c, 25 * mm, 58 * mm, "потешка → жест на ударных слогах → повтор → взгляд-пауза", size=13, bold=True, color=TEAL_D)
    text_box(c, 25 * mm, 45 * mm, "Не требовать идеального попадания ладошек.", size=11, color=MUTED)
    footer(c, 13)
    c.showPage()

    # 14
    bg(c)
    title(c, "Практика 3. Покачивания под музыку", "Медленный пульс и мягкий контраст")
    draw_table(
        c, 12 * mm, H - 40 * mm, [55 * mm, 210 * mm], 14 * mm,
        [
            ["Вариант", "Содержание"],
            ["На руках", "колыбельная"],
            ["На коленях", "«кач-кач»"],
            ["Лёжа (модель)", "лёгкое ведение без резкости"],
            ["Контраст", "20 сек спокойно → 10 сек чуть бодрее → спокойно"],
        ],
    )
    text_box(c, 30 * mm, 45 * mm, "спокойный пульс → короткий контраст → возврат к спокойствию", size=13, bold=True, color=TEAL_D)
    text_box(c, 30 * mm, 30 * mm, "«Бодрее» ≠ «громко».", size=11, color=MUTED)
    footer(c, 14)
    c.showPage()

    # 15
    bg(c)
    title(c, "Практика 4. Погремушка и звуковые контрасты", "Учить тишине так же, как звуку")
    draw_table(
        c, 12 * mm, H - 40 * mm, [20 * mm, 145 * mm], 12 * mm,
        [
            ["Шаг", "Действие"],
            ["1", "показать лицом и голосом"],
            ["2", "тихо потрясти в ритме слогов"],
            ["3", "«погремушка спит»"],
            ["4", "снова короткий звук → сон"],
            ["5", "вместе слегка потрясти"],
        ],
    )
    card(c, 190 * mm, H - 100 * mm, 90 * mm, 50 * mm, LEAF, "Можно", ["мягкий контраст 2 качеств", "3–5 коротких смен", "стоп при переутомлении"])
    card(c, 190 * mm, H - 165 * mm, 90 * mm, 50 * mm, RED, "Нельзя", ["крик / хлопок у уха", "длинная «дискотека»", "«ещё разок» через силу"])
    footer(c, 15)
    c.showPage()

    # 16
    bg(c)
    title(c, "Мини-тренинг студента", "60–70 секунд мягкого ритуала")
    draw_table(
        c, 12 * mm, H - 40 * mm, [20 * mm, 145 * mm], 14 * mm,
        [
            ["Шаг", "Действие"],
            ["1", "выбрать форму (руки / ладушки / качание / погремушка)"],
            ["2", "одна потешка или напев"],
            ["3", "начало → повтор → мягкий стоп"],
            ["4", "одно «можно» и одно «нельзя»"],
        ],
    )
    card(c, 190 * mm, H - 145 * mm, 90 * mm, 100 * mm, TEAL, "Рубрика Да/Нет", [
        "Контакт лица и голоса",
        "Движения мягкие",
        "Длительность короткая",
        "Есть пауза / стоп",
        "Нет резкости",
        "Понятно зачем младенцу",
    ])
    footer(c, 16)
    c.showPage()

    # 17
    bg(c)
    title(c, "Чек-лист работы с 0–1,5 лет", "Перед тем как идти к возрасту 1,5–3")
    checks = [
        "1. Понимаю: сенсомоторика и контакт, не номер?",
        "2. Умею читать реакцию на интонацию?",
        "3. Различаю колыбельную, потешку, пестушку?",
        "4. Двигаюсь вместе, не тащу?",
        "5. Держу взгляд, голос, касание?",
        "6. Могу провести ладушки / покачивание мягко?",
        "7. Учу погремушку со «сном» и тишиной?",
        "8. Останавливаюсь при переутомлении?",
    ]
    for i, t in enumerate(checks):
        col, row = i // 4, i % 4
        round_rect(c, 12 * mm + col * 140 * mm, H - 55 * mm - row * 25 * mm, 132 * mm, 20 * mm, SOFT if i % 2 == 0 else SAND)
        text_box(c, 18 * mm + col * 140 * mm, H - 48 * mm - row * 25 * mm, t, size=10, color=INK)
    text_box(c, 70 * mm, 28 * mm, "ГОЛОС   ↔   КАСАНИЕ   ↔   ПАУЗА", size=18, bold=True, color=TEAL_D)
    footer(c, 17)
    c.showPage()

    # 18
    bg(c, TEAL_D)
    circle(c, 15 * mm, H - 15 * mm, 28 * mm, TEAL)
    circle(c, W - 20 * mm, 25 * mm, 32 * mm, CORAL)
    text_box(c, 40 * mm, H - 30 * mm, "Итог + домашнее задание", size=12, bold=True, color=GOLD)
    text_box(c, 30 * mm, H - 50 * mm, "Ритм начинается с тёплого взрослого", size=22, bold=True, color=WHITE)
    text_box(c, 30 * mm, H - 70 * mm, "Мягкий голос.  Короткая форма.  Право на паузу.", size=13, color=SAND)
    hw = [
        ("1. Таблица на 1 стр.", ["слух · двигательный ответ", "роль взрослого · 2 примера", "можно / нельзя"]),
        ("2. Ритуал 2–3 мин", ["покачивание + потешка", "+ погремушка с тишиной", "(для 8–12 мес.)"]),
        ("3. Мини-эссе", ["почему контакт важнее", "идеального жеста"]),
    ]
    for i, (t, lines) in enumerate(hw):
        round_rect(c, 18 * mm + i * 90 * mm, 45 * mm, 82 * mm, 55 * mm, WHITE)
        text_box(c, 24 * mm + i * 90 * mm, 88 * mm, t, size=11, bold=True, color=TEAL_D)
        for j, line in enumerate(lines):
            text_box(c, 24 * mm + i * 90 * mm, 76 * mm - j * 8 * mm, line, size=9, color=INK)
    text_box(c, 25 * mm, 25 * mm, "Сохраните мягкость — и ритмическое развитие начнётся с правильного этажа.", size=11, color=GOLD)
    text_box(c, 80 * mm, 12 * mm, "Бабаджан · Ветлугина · Картушина", size=10, color=SAND)
    c.showPage()

    c.save()
    ART.parent.mkdir(parents=True, exist_ok=True)
    ART.write_bytes(OUT.read_bytes())
    print(f"OK pdf={OUT}")


if __name__ == "__main__":
    build()
