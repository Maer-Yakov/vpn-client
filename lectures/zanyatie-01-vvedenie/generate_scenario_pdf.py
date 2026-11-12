#!/usr/bin/env python3
"""Сценарий занятия 1 только для педагога: без картинок."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)

from font_paths import resolve_fonts

ROOT = Path(__file__).resolve().parent
OUT_PDF = ROOT / "Scenariy_zanyatiya_1_Muzykalno_ritmicheskoe_razvitie.pdf"

FONTS = resolve_fonts()
pdfmetrics.registerFont(TTFont("DejaVu", str(FONTS["regular"])))
pdfmetrics.registerFont(TTFont("DejaVuBold", str(FONTS["bold"])))
pdfmetrics.registerFont(TTFont("DejaVuItalic", str(FONTS["italic"])))
pdfmetrics.registerFont(TTFont("DejaVuBoldItalic", str(FONTS["bold_italic"])))
pdfmetrics.registerFontFamily(
    "DejaVu",
    normal="DejaVu",
    bold="DejaVuBold",
    italic="DejaVuItalic",
    boldItalic="DejaVuBoldItalic",
)

TEAL = colors.Color(28 / 255, 110 / 255, 120 / 255)
CORAL = colors.Color(196 / 255, 98 / 255, 78 / 255)
SAND = colors.Color(245 / 255, 240 / 255, 232 / 255)
INK = colors.Color(35 / 255, 42 / 255, 48 / 255)
LIGHT = colors.Color(214 / 255, 236 / 255, 238 / 255)


def build_styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="CoverTitle",
            fontName="DejaVuBold",
            fontSize=18,
            leading=24,
            alignment=TA_CENTER,
            textColor=TEAL,
            spaceAfter=10,
        )
    )
    styles.add(
        ParagraphStyle(
            name="CoverSub",
            fontName="DejaVu",
            fontSize=11,
            leading=15,
            alignment=TA_CENTER,
            textColor=INK,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="H1",
            fontName="DejaVuBold",
            fontSize=14,
            leading=19,
            textColor=TEAL,
            spaceBefore=14,
            spaceAfter=7,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Body",
            fontName="DejaVu",
            fontSize=10.5,
            leading=15,
            alignment=TA_JUSTIFY,
            textColor=INK,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="LessonBullet",
            fontName="DejaVu",
            fontSize=10.5,
            leading=15,
            textColor=INK,
            leftIndent=12,
            spaceAfter=3,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Time",
            fontName="DejaVuBold",
            fontSize=11,
            leading=15,
            textColor=CORAL,
            spaceBefore=10,
            spaceAfter=4,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Note",
            fontName="DejaVu",
            fontSize=10,
            leading=14,
            textColor=INK,
            backColor=LIGHT,
            borderPadding=6,
            spaceBefore=6,
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Speech",
            fontName="DejaVu",
            fontSize=10.5,
            leading=15,
            textColor=INK,
            leftIndent=8,
            rightIndent=8,
            spaceBefore=4,
            spaceAfter=8,
            backColor=SAND,
            borderPadding=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="TableCell",
            fontName="DejaVu",
            fontSize=9,
            leading=12,
            textColor=INK,
        )
    )
    styles.add(
        ParagraphStyle(
            name="TableHead",
            fontName="DejaVuBold",
            fontSize=9,
            leading=12,
            textColor=colors.white,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Footer",
            fontName="DejaVu",
            fontSize=8,
            textColor=colors.gray,
            alignment=TA_CENTER,
        )
    )
    return styles


def p(text, style):
    return Paragraph(text, style)


def bullets(items, styles):
    return [p(f"• {item}", styles["LessonBullet"]) for item in items]


def make_table(data, col_widths, styles):
    formatted = []
    for r, row in enumerate(data):
        style = styles["TableHead"] if r == 0 else styles["TableCell"]
        formatted.append([Paragraph(str(cell), style) for cell in row])
    table = Table(formatted, colWidths=col_widths, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), TEAL),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.Color(0.75, 0.8, 0.82)),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    return table


def add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont("DejaVu", 8)
    canvas.setFillColor(colors.gray)
    canvas.drawCentredString(
        A4[0] / 2,
        12 * mm,
        f"Сценарий для педагога · Занятие 1 · стр. {doc.page}",
    )
    canvas.restoreState()


def build_pdf(output_path: Path) -> None:
    styles = build_styles()
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=18 * mm,
        title="Сценарий для педагога. Занятие 1",
        author="Педагогический колледж",
    )
    story = []

    story.append(p("СЦЕНАРИЙ ДЛЯ ПЕДАГОГА", styles["CoverSub"]))
    story.append(p("Занятие 1. Введение в музыкально-ритмическое развитие ребёнка", styles["CoverTitle"]))
    story.append(p("Тема: значение ритма и движения в развитии дошкольника", styles["CoverSub"]))
    story.append(Spacer(1, 3 * mm))
    story.append(
        p(
            "Документ <b>только для преподавателя</b>. Здесь — что говорить студентам, "
            "какие вопросы задавать и как вести практику. Без иллюстраций.",
            styles["Note"],
        )
    )

    meta = [
        ["Кому", "студенты педагогического колледжа — будущие воспитатели"],
        ["Форма", "комбинированное занятие: теория + практика"],
        ["Время", "90 минут"],
        ["Опора", "презентация по желанию + аудиофрагменты"],
    ]
    meta_table = Table(
        [[Paragraph(f"<b>{a}</b>", styles["TableCell"]), Paragraph(b, styles["TableCell"])] for a, b in meta],
        colWidths=[3.2 * cm, 12.8 * cm],
    )
    meta_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), LIGHT),
                ("BOX", (0, 0), (-1, -1), 1, TEAL),
                ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.Color(0.8, 0.85, 0.86)),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(meta_table)

    story.append(p("Цель занятия", styles["H1"]))
    story.append(
        p(
            "Помочь студентам понять, зачем дошкольнику ритм и движение, "
            "и дать простой набор приёмов, которые они смогут провести с детьми.",
            styles["Body"],
        )
    )
    story.extend(
        bullets(
            [
                "донести понятие музыкально-ритмического развития живым языком;",
                "показать связь музыки, эмоции, движения и мышления;",
                "развести ритмику, музыкально-двигательную деятельность, танец и хореографию;",
                "проговорить роль воспитателя рядом с музыкальным руководителем;",
                "провести три практических упражнения и сразу разобрать: «как это с детьми».",
            ],
            styles,
        )
    )

    story.append(p("Хронометраж", styles["H1"]))
    story.append(
        make_table(
            [
                ["Этап", "Минуты", "Ваша главная задача"],
                ["I. Вход в тему", "0–10", "Зацепить внимание: ритм — не «развлечение»"],
                ["II. Теория через разговор", "10–45", "Объяснить тему и проверить понимание"],
                ["III. Двигательная пауза", "45–55", "Переключить студентов в режим «делаем сами»"],
                ["IV. Практика", "55–85", "Отработать 3 приёма и связать с работой воспитателя"],
                ["V. Итог", "85–90", "Закрепить вывод и дать домашнее задание"],
            ],
            [4.5 * cm, 2.2 * cm, 9.5 * cm],
            styles,
        )
    )
    story.append(PageBreak())

    story.append(p("I. Вход в тему (0–10 мин)", styles["H1"]))
    story.append(p("0:00–0:03. Обращение к студентам", styles["Time"]))
    story.append(
        p(
            "Скажите студентам:<br/><br/>"
            "«Добрый день! Сегодня мы говорим о том, без чего музыкальное воспитание в детском саду "
            "часто становится формальным, — о музыкально-ритмическом развитии ребёнка.<br/><br/>"
            "Я прошу вас слушать не как слушатели лекции, а как будущие воспитатели. "
            "Ваш вопрос на всё занятие такой: <b>что именно я могу делать с детьми каждый день, "
            "чтобы ритм и движение работали на развитие, а не только на утренник?</b>»",
            styles["Speech"],
        )
    )

    story.append(p("0:03–0:06. Договорённость о работе", styles["Time"]))
    story.append(
        p(
            "Скажите коротко:<br/><br/>"
            "«У нас 90 минут. Сначала разберём смысл темы, потом сами попробуем упражнения. "
            "Правила простые: слушаем фрагмент до конца; двигаемся безопасно; говорим по сигналу. "
            "Если что-то непонятно — останавливайте меня сразу: лучше сейчас, чем на практике с детьми».",
            styles["Speech"],
        )
    )

    story.append(p("0:06–0:10. Разминка «Музыкальный сигнал»", styles["Time"]))
    story.append(
        p(
            "Проведите сами, затем спросите группу.<br/><br/>"
            "1) Хлопните простой ритм — студенты повторяют.<br/>"
            "2) Включите 20–30 секунд марша: идём на месте.<br/>"
            "3) На паузе — полная остановка.<br/><br/>"
            "Спросите:<br/>"
            "«Что помогло вам вовремя остановиться?»<br/><br/>"
            "Подведите:<br/>"
            "«Вы только что использовали слух, внимание и телесный контроль. "
            "Вот это и есть рабочее ядро ритмики — не красивый танец, а управляемый отклик на музыку».",
            styles["Speech"],
        )
    )

    story.append(p("II. Теория через разговор (10–45 мин)", styles["H1"]))
    story.append(p("2.1. Что такое музыкально-ритмическое развитие (10–17 мин)", styles["Time"]))
    story.append(
        p(
            "Скажите студентам:<br/><br/>"
            "«Запишите опорную формулировку. "
            "<b>Музыкально-ритмическое развитие</b> — это процесс, в котором ребёнок учится "
            "слышать музыку и отвечать на неё движением: характером, темпом, динамикой, ритмом.<br/><br/>"
            "Обратите внимание: это не синоним “выучить танец к празднику”. "
            "Танец может быть частью пути, но цель шире — связать слух, чувство и действие».",
            styles["Speech"],
        )
    )
    story.append(
        p(
            "Задание группе (около 2 минут): в парах сформулировать определение своими словами. "
            "Попросите 2–3 пары зачитать. Исправьте только смыслово.",
            styles["Body"],
        )
    )
    story.append(
        p(
            "Добавьте возрастной ориентир:<br/><br/>"
            "«В 3–4 года ребёнку достаточно яркого характера и простой реакции. "
            "В 4–5 лет уже работаем с контрастами: быстро/медленно, громко/тихо. "
            "В 5–7 лет ждём большей точности ритма и выразительности. "
            "Не ждите от младших того, что по силам подготовительной группе».",
            styles["Speech"],
        )
    )

    story.append(p("2.2. Музыка — эмоция — движение — осмысление (17–24 мин)", styles["Time"]))
    story.append(
        p(
            "Скажите:<br/><br/>"
            "«Запомните цепочку: <b>музыка → эмоция → движение → осмысление</b>. "
            "Музыка задаёт образ. Эмоция делает его личным. Движение позволяет прожить музыку телом. "
            "Интеллект подключается, когда ребёнок сравнивает, запоминает последовательность и держит правило.<br/><br/>"
            "Почему нельзя ограничиться словами “просто послушайте”? "
            "Потому что дошкольник мыслит через действие и образ. Тело для него — способ понять музыку».",
            styles["Speech"],
        )
    )
    story.append(
        p(
            "Вопрос аудитории:<br/>"
            "«Если ребёнок правильно повторил движения, но лицом и телом “не в музыке” — это уже успех или ещё нет?»<br/><br/>"
            "Ожидаемый акцент: техника без переживания характера — слабый результат для дошкольного возраста.",
            styles["Note"],
        )
    )

    story.append(p("2.3. Что развивает ритм (24–32 мин)", styles["Time"]))
    story.append(
        p(
            "Скажите прямо:<br/><br/>"
            "«Ритм — это не отдельная “тема про хлопки”. Это каркас, на который вы можете нанизывать развитие сразу в четырёх сферах».",
            styles["Speech"],
        )
    )
    story.append(
        make_table(
            [
                ["Сфера", "Что говорите студентам", "Какой пример даёте"],
                ["Координация", "тело учится быть согласованным", "шаг на сильную долю; смена направления"],
                ["Внимание", "ребёнок учится ждать сигнал и переключаться", "«замри на паузе»; движение только на forte"],
                ["Память", "удерживаем последовательность и форму", "повтор хлопков; части A–B–A"],
                ["Речь", "ритм помогает слогу, дыханию, фразе", "хлопки по слогам имени; шаги под считалку"],
            ],
            [3.0 * cm, 6.5 * cm, 6.7 * cm],
            styles,
        )
    )
    story.append(
        p(
            "Закрепите фразой:<br/>"
            "«Если вас спросят на практике, зачем ритмика в группе, отвечайте не “чтобы красиво двигались”, "
            "а “чтобы развивались координация, внимание, память и речь”.»",
            styles["Speech"],
        )
    )

    story.append(p("2.4. Не путаем четыре понятия (32–40 мин)", styles["Time"]))
    story.append(
        p(
            "Скажите студентам:<br/><br/>"
            "«Сейчас разведём то, что на практике часто смешивают. Это важно, иначе всё занятие "
            "сводится к постановке танца».",
            styles["Speech"],
        )
    )
    story.append(
        make_table(
            [
                ["Понятие", "Как объяснить студентам", "Зачем это в ДОУ"],
                ["Ритмика", "метод: через движение осваиваем музыку", "слух, ритм, реакция, координация"],
                ["Музыкально-двигательная деятельность", "широкий вид детской деятельности", "игра, слушание, движение, импровизация"],
                ["Танец", "художественная форма движения", "выразительность, общение, эстетика"],
                ["Хореография", "постановка и техника композиции", "в ДОУ — только элементы, не профподготовка"],
            ],
            [4.2 * cm, 6.2 * cm, 5.8 * cm],
            styles,
        )
    )
    story.append(
        p(
            "Приём на проверку: устно дайте 4 примера — ход под музыку; хоровод; постановка к утреннику; "
            "игра «Море волнуется». Студенты относят каждый пример к одному понятию.<br/><br/>"
            "Подчеркните:<br/>"
            "«Если вы весь год только разучиваете танцы “на показ”, вы теряете слух, импровизацию и настоящую работу с ритмом».",
            styles["Speech"],
        )
    )

    story.append(p("2.5. Роль воспитателя рядом с музруководителем (40–45 мин)", styles["Time"]))
    story.append(
        p(
            "Обратитесь к студентам лично:<br/><br/>"
            "«Вы — не статисты на утреннике. Музыкальный руководитель проектирует занятие, "
            "подбирает музыку, ведёт ритмические формы. А вы, воспитатели, делаете главное в повседневности: "
            "закрепляете, наблюдаете, поддерживаете интерес, связываете ритм с речью, игрой и режимом дня.<br/><br/>"
            "Без вас музыкальное занятие остаётся эпизодом. С вами оно становится развитием».",
            styles["Speech"],
        )
    )
    story.append(PageBreak())

    story.append(p("III. Двигательная пауза (45–55 мин)", styles["H1"]))
    story.append(
        p(
            "Скажите перед паузой:<br/><br/>"
            "«Сейчас выходите из позиции “слушаем теорию” в позицию “пробуем телом”. "
            "Это нужно, чтобы потом проводить упражнения с детьми не по бумажке, а из собственного опыта».",
            styles["Speech"],
        )
    )
    story.extend(
        bullets(
            [
                "45–48: марш на месте → стоп на паузе;",
                "48–51: плавное покачивание под спокойную музыку;",
                "51–54: лёгкие пружинящие движения под плясовую;",
                "54–55: вопрос группе: «Что изменилось в теле, когда сменился характер музыки?»",
            ],
            styles,
        )
    )

    story.append(p("IV. Практика (55–85 мин)", styles["H1"]))
    story.append(
        p(
            "Общий формат:<br/><br/>"
            "«Я показываю модель. Вы выполняете. Потом сразу разбираем: "
            "как провести это с детьми 4–5 и 6–7 лет, что упростить, за чем следить».",
            styles["Speech"],
        )
    )

    story.append(p("Практика 1. Характер музыки → качество движения (55–65)", styles["Time"]))
    story.append(
        p(
            "Скажите:<br/><br/>"
            "«Ваша задача — не придумать красивый танец, а точно перевести характер музыки в качество движения».",
            styles["Speech"],
        )
    )
    story.append(
        make_table(
            [
                ["Характер", "Какое движение ищете", "Что подсказать детям"],
                ["Марш", "чёткий шаг, собранность", "доля, осанка, энергичность"],
                ["Плясовая", "лёгкость, прыжковость", "радость, свобода плеч"],
                ["Колыбельная", "плавность, мягкость", "тихо, медленно, бережно"],
                ["Вальс", "кружение, мягкий акцент на «раз»", "трёхдольность, плавность"],
            ],
            [3.3 * cm, 6.0 * cm, 6.9 * cm],
            styles,
        )
    )
    story.append(
        p(
            "Ход: слушаем 20–30 секунд без движения → называем характер одним-двумя словами → "
            "находим движение → спрашиваете: «Что в музыке вас на это натолкнуло?»",
            styles["Body"],
        )
    )

    story.append(p("Практика 2. Настроение только через движение (65–75)", styles["Time"]))
    story.append(
        p(
            "Скажите группе:<br/><br/>"
            "«Сначала без слов. Только тело. Потом назовём настроение.<br/><br/>"
            "Зачем это будущему воспитателю? Потому что движение — диагностика. "
            "Если ребёнок пластикой “не попал” в характер музыки, он, скорее всего, ещё не услышал её по-настоящему».",
            styles["Speech"],
        )
    )

    story.append(p("Практика 3. Музыкальная реакция (75–85)", styles["Time"]))
    story.append(
        p(
            "Проведите по очереди и после каждого спросите: «Что это тренирует у ребёнка?»",
            styles["Body"],
        )
    )
    story.append(
        make_table(
            [
                ["Упражнение", "Правило для студентов", "Смысл для детей"],
                ["Старт / стоп", "двигаемся, только пока звучит музыка", "внимание и торможение"],
                ["Сильная доля", "хлопок или притоп только на «раз»", "метр и координация"],
                ["Динамический код", "piano — на носках; forte — энергичный шаг", "динамика и контроль"],
                ["Темповый код", "ускоряемся и замедляемся строго по музыке", "чувство темпа"],
                ["Смена образа", "«капельки» / «ветер» по фразе", "переключение и форма"],
            ],
            [3.8 * cm, 7.0 * cm, 5.4 * cm],
            styles,
        )
    )
    story.append(
        p(
            "Критерии в конце практики: своевременность реакции, соответствие характеру, "
            "внимание к сигналу, безопасность, умение упростить задание под возраст.",
            styles["Note"],
        )
    )
    story.append(PageBreak())

    story.append(p("V. Итог (85–90 мин)", styles["H1"]))
    story.append(
        p(
            "Задайте короткие вопросы:<br/><br/>"
            "1) Чем музыкально-ритмическое развитие отличается от разучивания танца?<br/>"
            "2) Что сильнее всего тренирует упражнение «замри на паузе»?<br/>"
            "3) Где проходит ваша зона ответственности как воспитателей?<br/>"
            "4) Какое упражнение вы возьмёте для детей 4–5 лет и почему?",
            styles["Body"],
        )
    )
    story.append(
        p(
            "Закройте занятие прямой фразой:<br/><br/>"
            "«Ритм и движение — не украшение праздника. Это ежедневный ресурс развития ребёнка. "
            "Ваша работа как воспитателей — замечать, закреплять и продолжать то, "
            "что начинается на музыкальном занятии».",
            styles["Speech"],
        )
    )

    story.append(p("Домашнее задание (как объявить)", styles["H1"]))
    story.append(
        p(
            "«К следующему занятию подготовьте три вещи.<br/>"
            "Первое — карточку упражнения: возраст, цель, музыка, ход, критерии.<br/>"
            "Второе — три контрастных фрагмента: марш, колыбельная, плясовая — и краткое описание, "
            "какой двигательный отклик вы ждёте.<br/>"
            "Третье — выпишите у Ветлугиной определение музыкально-ритмических движений и сравните "
            "с тем, что мы сформулировали сегодня».",
            styles["Speech"],
        )
    )

    story.append(p("На что смотреть при оценке", styles["H1"]))
    story.append(
        make_table(
            [
                ["Критерий", "Достаточно", "Сильный ответ"],
                ["Понятия", "называет определения", "сравнивает на примерах"],
                ["Смысл темы", "пересказывает цепочку", "объясняет, зачем это детям"],
                ["Практика", "выполняет упражнения", "может провести фрагмент как ведущий"],
                ["Позиция воспитателя", "общими словами", "предлагает, что закрепить в группе"],
            ],
            [3.5 * cm, 6.0 * cm, 6.7 * cm],
            styles,
        )
    )

    story.append(p("Литература", styles["H1"]))
    story.extend(
        bullets(
            [
                "Ветлугина Н. А. Теория и методика музыкального воспитания в детском саду.",
                "Теплов Б. М. Психология музыкальных способностей.",
                "Буренина А. И. Ритмическая мозаика.",
            ],
            styles,
        )
    )

    story.append(Spacer(1, 6 * mm))
    story.append(p("Сценарий для педагога. Специальность «Дошкольное образование».", styles["Footer"]))

    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    print(f"PDF written: {output_path}")


if __name__ == "__main__":
    with tempfile.TemporaryDirectory(prefix="scenario-") as tmp:
        tmp_pdf = Path(tmp) / OUT_PDF.name
        build_pdf(tmp_pdf)
        os.replace(tmp_pdf, OUT_PDF)
    print(f"Published: {OUT_PDF}")
