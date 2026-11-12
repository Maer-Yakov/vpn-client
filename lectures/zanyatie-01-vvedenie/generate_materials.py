#!/usr/bin/env python3
"""Generate PDF lesson script and PPTX presentation for lesson 1."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

from PIL import Image as PILImage
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image as RLImage,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from font_paths import resolve_fonts

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
OUT_PDF = ROOT / "Scenariy_zanyatiya_1_Muzykalno_ritmicheskoe_razvitie.pdf"
OUT_PPTX = ROOT / "Prezentaciya_zanyatie_1_Muzykalno_ritmicheskoe_razvitie.pptx"

REQUIRED_ASSETS = [
    "slide-cover.jpg",
    "slide-children-rhythm.jpg",
    "slide-four-skills.jpg",
    "slide-music-characters.jpg",
    "slide-teachers-roles.jpg",
    "scheme-connection.png",
    "scheme-rhythm-roles.png",
    "scheme-concepts.png",
    "scheme-timeline.png",
    "scheme-roles.png",
]

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


def require_assets() -> None:
    missing = [name for name in REQUIRED_ASSETS if not (ASSETS / name).is_file()]
    if missing:
        listed = "\n  - ".join(missing)
        raise FileNotFoundError(
            "Не хватает файлов в assets/. Сначала выполните "
            f"`python3 generate_diagrams.py` и убедитесь, что иллюстрации на месте:\n  - {listed}"
        )


def asset(name: str) -> Path:
    path = ASSETS / name
    if not path.is_file():
        raise FileNotFoundError(f"Отсутствует обязательный файл: {path}")
    return path


def build_styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="CoverTitle",
            fontName="DejaVuBold",
            fontSize=22,
            leading=28,
            alignment=TA_CENTER,
            textColor=TEAL,
            spaceAfter=12,
        )
    )
    styles.add(
        ParagraphStyle(
            name="CoverSub",
            fontName="DejaVu",
            fontSize=13,
            leading=18,
            alignment=TA_CENTER,
            textColor=INK,
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="H1",
            fontName="DejaVuBold",
            fontSize=16,
            leading=22,
            textColor=TEAL,
            spaceBefore=16,
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="H2",
            fontName="DejaVuBold",
            fontSize=13,
            leading=18,
            textColor=CORAL,
            spaceBefore=12,
            spaceAfter=6,
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
            textColor=TEAL,
            spaceBefore=8,
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
    styles.add(
        ParagraphStyle(
            name="Speech",
            fontName="DejaVu",
            fontSize=10.5,
            leading=15,
            textColor=INK,
            leftIndent=10,
            rightIndent=10,
            spaceBefore=4,
            spaceAfter=6,
            backColor=SAND,
            borderPadding=8,
        )
    )
    return styles


def p(text, style):
    return Paragraph(text, style)


def bullets(items, styles):
    flow = []
    for item in items:
        flow.append(p(f"• {item}", styles["LessonBullet"]))
    return flow


def timed_block(title, minutes, content_flow, styles):
    block = [p(f"{title} <font color='#C6624E'>({minutes})</font>", styles["Time"])]
    block.extend(content_flow)
    return KeepTogether(block)


def make_table(data, col_widths, styles):
    formatted = []
    for r, row in enumerate(data):
        formatted_row = []
        for cell in row:
            style = styles["TableHead"] if r == 0 else styles["TableCell"]
            formatted_row.append(Paragraph(str(cell), style))
        formatted.append(formatted_row)
    table = Table(formatted, colWidths=col_widths, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), TEAL),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("BACKGROUND", (0, 1), (-1, -1), colors.white),
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
        f"Занятие 1. Музыкально-ритмическое развитие · стр. {doc.page}",
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
        title="Сценарий занятия 1. Введение в музыкально-ритмическое развитие ребёнка",
        author="Педагогический колледж",
    )
    story = []

    # Cover
    story.append(Spacer(1, 12 * mm))
    story.append(p("ПЕДАГОГИЧЕСКИЙ КОЛЛЕДЖ", styles["CoverSub"]))
    story.append(p("Специальность: Дошкольное образование<br/>МДК / дисциплина: Теория и методика музыкального воспитания", styles["CoverSub"]))
    story.append(Spacer(1, 8 * mm))
    story.append(p("СЦЕНАРИЙ ЗАНЯТИЯ № 1", styles["CoverTitle"]))
    story.append(p("Введение в музыкально-ритмическое развитие ребёнка", styles["CoverTitle"]))
    story.append(p("Тема: значение ритма и движения в развитии дошкольника", styles["CoverSub"]))
    story.append(Spacer(1, 6 * mm))
    story.append(RLImage(str(asset("slide-cover.jpg")), width=14 * cm, height=7.8 * cm))
    story.append(Spacer(1, 8 * mm))
    meta = [
        ["Аудитория", "студенты — будущие воспитатели"],
        ["Форма", "комбинированное занятие (лекция + практика)"],
        ["Длительность", "90 минут"],
        ["Место", "музыкальный / методический кабинет"],
    ]
    meta_table = Table(
        [[Paragraph(f"<b>{a}</b>", styles["TableCell"]), Paragraph(b, styles["TableCell"])] for a, b in meta],
        colWidths=[4.5 * cm, 11.5 * cm],
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
    story.append(PageBreak())

    # Passport
    story.append(p("1. Паспорт занятия", styles["H1"]))
    story.append(p("<b>Цель занятия:</b> сформировать у студентов представление о сущности музыкально-ритмического развития дошкольника, его значении для координации, внимания, памяти и речи, а также отработать базовые приёмы организации двигательного отклика на музыку.", styles["Body"]))
    story.append(p("<b>Задачи:</b>", styles["Body"]))
    story.extend(
        bullets(
            [
                "<b>образовательная</b> — раскрыть понятие музыкально-ритмического развития и отличия ритмики, музыкально-двигательной деятельности, танца и хореографии;",
                "<b>развивающая</b> — развить умение анализировать связь музыки, движения, эмоций и интеллекта;",
                "<b>практическая</b> — освоить упражнения на характер музыки, настроение через движение и музыкальную реакцию;",
                "<b>воспитательная</b> — формировать ответственную позицию будущего воспитателя как партнёра музыкального руководителя.",
            ],
            styles,
        )
    )
    story.append(p("<b>Планируемые результаты:</b> студент объясняет понятие; различает четыре смежных понятия; называет задачи специалистов; проводит 3 типа упражнений; подбирает фрагменты музыки разного характера.", styles["Body"]))
    story.append(p("<b>Оборудование:</b> аудиосистема / ноутбук, подборка музыкальных фрагментов (марш, плясовая, колыбельная, вальс), бубен/деревянные палочки, карточки «характер музыки», флипчарт или доска, раздатка с опорной схемой, презентация.", styles["Body"]))
    story.append(p("<b>Методы:</b> объяснительно-иллюстративный, беседа, сравнение, практический показ, упражнение, рефлексия.", styles["Body"]))

    story.append(p("2. Хронометраж занятия (90 минут)", styles["H1"]))
    story.append(RLImage(str(asset("scheme-timeline.png")), width=16.5 * cm, height=9.3 * cm))
    story.append(Spacer(1, 3 * mm))

    timeline = [
        ["Этап", "Время", "Минуты", "Содержание"],
        ["I. Организационный момент", "0–10", "10", "Приветствие, цели, правила, разминка внимания"],
        ["II. Теоретический блок", "10–45", "35", "5 теоретических вопросов плана"],
        ["III. Музыкально-двигательная пауза", "45–55", "10", "Переход к практике через движение"],
        ["IV. Практический блок", "55–85", "30", "3 практических упражнения"],
        ["V. Рефлексия и итог", "85–90", "5", "Выводы, ДЗ, оценка занятия"],
    ]
    story.append(make_table(timeline, [5.2 * cm, 2.2 * cm, 1.8 * cm, 7 * cm], styles))
    story.append(PageBreak())

    # Detailed script
    story.append(p("3. Подробный сценарий занятия", styles["H1"]))

    # Stage I
    story.append(p("I. Организационный момент (0–10 мин)", styles["H2"]))
    story.append(p("<b>0:00–0:03. Приветствие и настрой</b>", styles["Time"]))
    story.append(
        p(
            "<i>Слова преподавателя:</i><br/>«Добрый день! Сегодня мы начинаем тему, без которой невозможно качественное музыкальное воспитание в детском саду, — музыкально-ритмическое развитие ребёнка. Наша задача — понять не только „что делать на занятии“, но и „зачем движение нужно дошкольнику“».",
            styles["Speech"],
        )
    )
    story.append(p("<b>0:03–0:06. Целеполагание</b>", styles["Time"]))
    story.extend(
        bullets(
            [
                "озвучить тему и цель;",
                "показать хронометраж на слайде;",
                "договориться о правилах практики: слушать фрагмент до конца, двигаться безопасно, обсуждать после сигнала преподавателя.",
            ],
            styles,
        )
    )
    story.append(p("<b>0:06–0:10. Входная разминка «Музыкальный сигнал»</b>", styles["Time"]))
    story.extend(
        bullets(
            [
                "преподаватель хлопает простой ритм — студенты повторяют;",
                "затем включает 20–30 секунд марша: идём на месте;",
                "пауза в музыке — полная остановка;",
                "вопрос: «Что помогало вам вовремя остановиться?» (слух, внимание, телесный контроль).",
            ],
            styles,
        )
    )
    story.append(
        p(
            "<b>Педагогический смысл:</b> сразу показать студентам, что ритмика — это не „развлечение“, а инструмент развития внимания и саморегуляции.",
            styles["Note"],
        )
    )

    # Stage II
    story.append(p("II. Теоретический блок (10–45 мин) — 35 минут", styles["H2"]))

    story.append(p("<b>2.1. Понятие музыкально-ритмического развития (10–17 мин) — 7 мин</b>", styles["Time"]))
    story.append(
        p(
            "<i>Опорное определение:</i> музыкально-ритмическое развитие — процесс формирования у ребёнка способности воспринимать музыку и выражать её характер, темп, динамику и ритм через движение.",
            styles["Body"],
        )
    )
    story.extend(
        bullets(
            [
                "это единство слуха, эмоции и двигательного ответа;",
                "не сводится к разучиванию танца к утреннику;",
                "в дошкольном возрасте движение — язык понимания музыки.",
            ],
            styles,
        )
    )
    story.append(p("<b>Работа со студентами (2 мин):</b> в парах сформулировать определение своими словами за 40 секунд, затем 2–3 формулировки зачитать.", styles["Body"]))
    story.append(
        p(
            "<i>Возрастные ориентиры:</i> 3–4 года — яркий характер и простые реакции; 4–5 лет — контрасты темпа/динамики; 5–7 лет — точность ритма, фразировка, выразительность.",
            styles["Note"],
        )
    )

    story.append(p("<b>2.2. Связь музыки, движения, эмоций и интеллекта (17–24 мин) — 7 мин</b>", styles["Time"]))
    story.append(RLImage(str(asset("scheme-connection.png")), width=16.5 * cm, height=7.2 * cm))
    story.append(
        p(
            "Цепочка: <b>музыка → эмоция → движение → осмысление → закрепление в опыте</b>.",
            styles["Body"],
        )
    )
    story.extend(
        bullets(
            [
                "музыка задаёт образ и напряжение/разрядку;",
                "эмоция делает восприятие личностным;",
                "движение „проживает“ музыку телесно;",
                "интеллект включается через сравнение, запоминание последовательности, удержание правила.",
            ],
            styles,
        )
    )
    story.append(
        p(
            "<i>Вопрос к аудитории:</i> «Почему для дошкольника недостаточно „просто послушать“ пьесу без движения?» Ожидаемый ответ: ведущее мышление наглядно-действенное и образное; тело помогает понять свойства музыки.",
            styles["Speech"],
        )
    )

    story.append(p("<b>2.3. Роль ритма в развитии координации, внимания, памяти и речи (24–32 мин) — 8 мин</b>", styles["Time"]))
    story.append(RLImage(str(asset("scheme-rhythm-roles.png")), width=16.5 * cm, height=9.3 * cm))
    rhythm_table = [
        ["Сфера", "Что развивается", "Пример упражнения"],
        ["Координация", "согласованность моторики, равновесие", "шаг на сильную долю; смена направления"],
        ["Внимание", "устойчивость, переключение, реакция", "«замри на паузе»; движение только на forte"],
        ["Память", "последовательность, ритм-формулы, форма", "повтор хлопков; структура A–B–A"],
        ["Речь", "слоговой ритм, дыхание, артикуляция", "хлопки по слогам имени; шаги под считалку"],
    ]
    story.append(make_table(rhythm_table, [3.2 * cm, 6.5 * cm, 6.5 * cm], styles))
    story.append(
        p(
            "<b>Мини-вывод для конспекта:</b> ритм — универсальный каркас, на который ребёнок „нанизывает“ движение, внимание, память и речь.",
            styles["Note"],
        )
    )

    story.append(p("<b>2.4. Отличие ритмики, музыкально-двигательной деятельности, танца и хореографии (32–40 мин) — 8 мин</b>", styles["Time"]))
    story.append(RLImage(str(asset("scheme-concepts.png")), width=16.5 * cm, height=10.3 * cm))
    concepts = [
        ["Понятие", "Суть", "Цель в ДОУ"],
        ["Ритмика", "метод / система упражнений", "освоить музыку через движение"],
        ["Музыкально-двигательная деятельность", "вид детской деятельности", "целостное музыкальное развитие"],
        ["Танец", "художественная форма движения", "выразительность, общение, эстетика"],
        ["Хореография", "искусство постановки танца", "элементы композиции (не профподготовка)"],
    ]
    story.append(make_table(concepts, [5.5 * cm, 5.5 * cm, 5.2 * cm], styles))
    story.append(
        p(
            "<b>Типичная ошибка практики:</b> свести всё занятие к разучиванию танца „на показ“. Тогда страдают слуховое развитие, импровизация и работа с ритмом.",
            styles["Note"],
        )
    )
    story.append(p("<b>Приём «4 карточки»:</b> студенты сортируют примеры (ход под музыку; хоровод; постановка к утреннику; игра «Море волнуется») по четырём понятиям.", styles["Body"]))

    story.append(p("<b>2.5. Задачи музыкального руководителя и педагога (40–45 мин) — 5 мин</b>", styles["Time"]))
    story.append(RLImage(str(asset("scheme-roles.png")), width=16.5 * cm, height=8.8 * cm))
    story.append(p("<b>Музыкальный руководитель:</b> подбор музыки; формирование восприятия; развитие ритма; организация игр/танцев; качество и безопасность; консультация воспитателей.", styles["Body"]))
    story.append(p("<b>Воспитатель:</b> интерес в группе; закрепление материала; наблюдение за детьми; пространство и дисциплина; связь с речью/физкультурой; эмоциональный комфорт.", styles["Body"]))
    story.append(
        p(
            "<i>Акцент для студентов колледжа:</i> воспитатель — не „помощник на утреннике“, а соавтор ежедневного закрепления музыкально-ритмического опыта.",
            styles["Speech"],
        )
    )
    story.append(PageBreak())

    # Stage III
    story.append(p("III. Музыкально-двигательная пауза (45–55 мин) — 10 минут", styles["H2"]))
    story.append(
        p(
            "Цель паузы — сменить умственную нагрузку и подготовить студентов к роли ведущего упражнений.",
            styles["Body"],
        )
    )
    story.extend(
        bullets(
            [
                "<b>45–48:</b> марш на месте → остановка на паузе;",
                "<b>48–51:</b> плавное покачивание под колыбельную / спокойную пьесу;",
                "<b>51–54:</b> лёгкие пружинящие движения под плясовую;",
                "<b>54–55:</b> обсуждение: какие качества движения менялись и почему.",
            ],
            styles,
        )
    )
    story.append(Spacer(1, 2 * mm))
    story.append(RLImage(str(asset("slide-music-characters.jpg")), width=16 * cm, height=9 * cm))

    # Stage IV
    story.append(p("IV. Практический блок (55–85 мин) — 30 минут", styles["H2"]))
    story.append(
        p(
            "Формат: преподаватель показывает модель → студенты выполняют → краткий разбор „как провести это с детьми“.",
            styles["Body"],
        )
    )

    story.append(p("<b>Практика 1. Движение под музыку с разным характером (55–65 мин) — 10 мин</b>", styles["Time"]))
    practice1 = [
        ["Характер", "Качество движения", "Что подчеркнуть детям"],
        ["Маршевый", "чёткий шаг, собранность", "доля, осанка, энергичность"],
        ["Плясовой", "лёгкость, прыжковость", "весёлость, свобода плеч"],
        ["Колыбельный", "плавность, мягкость", "тихо, медленно, бережность"],
        ["Вальсовый", "кружение, мягкий „раз“", "трёхдольность, плавность"],
    ]
    story.append(make_table(practice1, [3.5 * cm, 5.5 * cm, 7.2 * cm], styles))
    story.extend(
        bullets(
            [
                "прослушать фрагмент без движения (20–30 сек);",
                "назвать характер 1–2 словами;",
                "найти движение;",
                "обсудить музыкальные подсказки (темп, штрих, фактура).",
            ],
            styles,
        )
    )

    story.append(p("<b>Практика 2. Определение настроения через движение (65–75 мин) — 10 мин</b>", styles["Time"]))
    story.extend(
        bullets(
            [
                "правило: сначала только движение, без слов;",
                "преподаватель включает 3 контрастных фрагмента;",
                "после каждого сигнала — вербализация настроения;",
                "рефлексия: какое движение точнее передало чувство и почему.",
            ],
            styles,
        )
    )
    story.append(
        p(
            "<b>Для будущих воспитателей:</b> движение — диагностический инструмент. По пластике ребёнка видно, воспринял ли он характер музыки.",
            styles["Note"],
        )
    )

    story.append(p("<b>Практика 3. Упражнения на музыкальную реакцию (75–85 мин) — 10 мин</b>", styles["Time"]))
    reactions = [
        ["Упражнение", "Правило", "Что развивает"],
        ["Старт / стоп", "движение только пока звучит музыка", "внимание, торможение"],
        ["Сильная доля", "хлопок/притоп только на „раз“", "метр, координация"],
        ["Динамический код", "piano — на носках; forte — энергичный шаг", "динамика, контроль"],
        ["Темповый код", "ускорение/замедление по музыке", "темп, гибкость"],
        ["Смена образа", "„капельки“ / „ветер“ по фразе", "форма, переключение"],
    ]
    story.append(make_table(reactions, [4 * cm, 7 * cm, 5.2 * cm], styles))
    story.append(p("<b>Критерии успеха:</b> своевременность реакции; соответствие характеру; внимание к сигналу; безопасность; возможность адаптации для 4–5 и 6–7 лет.", styles["Body"]))
    story.append(Spacer(1, 2 * mm))
    story.append(RLImage(str(asset("slide-children-rhythm.jpg")), width=16 * cm, height=9 * cm))
    story.append(PageBreak())

    # Stage V
    story.append(p("V. Рефлексия и завершение (85–90 мин) — 5 минут", styles["H2"]))
    story.append(p("<b>Вопросы для рефлексии:</b>", styles["Body"]))
    story.extend(
        bullets(
            [
                "Чем музыкально-ритмическое развитие отличается от разучивания танца?",
                "Какую функцию сильнее тренирует упражнение „замри на паузе“?",
                "Где проходит граница задач музыкального руководителя и воспитателя?",
                "Какое упражнение вы возьмёте для детей 4–5 лет и почему?",
            ],
            styles,
        )
    )
    story.append(
        p(
            "<i>Итоговая фраза преподавателя:</i><br/>«Ритм и движение — это не украшение праздника. Это ежедневный ресурс развития ребёнка. Ваша роль как воспитателей — замечать, закреплять и продолжать то, что начинается на музыкальном занятии».",
            styles["Speech"],
        )
    )

    story.append(p("4. Домашнее задание", styles["H1"]))
    story.extend(
        bullets(
            [
                "Составить карточку упражнения (возраст, цель, музыка, ход, критерии оценки).",
                "Подобрать 3 контрастных фрагмента (марш / колыбельная / плясовая) и описать ожидаемый двигательный отклик.",
                "Выписать из Н. А. Ветлугиной определение музыкально-ритмических движений и сопоставить с конспектом занятия.",
            ],
            styles,
        )
    )

    story.append(p("5. Критерии оценивания работы студентов на занятии", styles["H1"]))
    assessment = [
        ["Критерий", "Базовый уровень", "Продвинутый уровень"],
        ["Понятийный аппарат", "воспроизводит определения", "сравнивает понятия на примерах"],
        ["Анализ", "называет 1–2 связи", "объясняет цепочку музыка→эмоция→движение→интеллект"],
        ["Практика", "выполняет упражнения", "может провести фрагмент как ведущий"],
        ["Рефлексия", "даёт общий отзыв", "предлагает адаптацию под возраст"],
    ]
    story.append(make_table(assessment, [3.5 * cm, 6.5 * cm, 6.5 * cm], styles))

    story.append(p("6. Литература", styles["H1"]))
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

    story.append(p("7. Приложение. Опорный конспект для студента (кратко)", styles["H1"]))
    story.extend(
        bullets(
            [
                "Музыкально-ритмическое развитие = восприятие музыки + двигательное выражение её содержания.",
                "Связка: музыка → эмоция → движение → осмысление.",
                "Ритм развивает координацию, внимание, память, речь.",
                "Ритмика ≠ танец ≠ хореография; музыкально-двигательная деятельность — шире.",
                "Музыкальный руководитель проектирует; воспитатель закрепляет и сопровождает.",
                "Практика: характер → движение; настроение через пластику; реакция на сигнал.",
            ],
            styles,
        )
    )

    story.append(Spacer(1, 8 * mm))
    story.append(
        p(
            "Материал предназначен для проведения занятия со студентами педагогических колледжей (специальность „Дошкольное образование“).",
            styles["Footer"],
        )
    )

    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    print(f"PDF written: {output_path}")


# -------------------- PPTX --------------------

PPT_TEAL = RGBColor(0x1C, 0x6E, 0x78)
PPT_CORAL = RGBColor(0xC4, 0x62, 0x4E)
PPT_INK = RGBColor(0x23, 0x2A, 0x30)
PPT_MUTED = RGBColor(0x5A, 0x64, 0x6C)
PPT_SAND = RGBColor(0xF5, 0xF0, 0xE8)
PPT_WHITE = RGBColor(0xFF, 0xFF, 0xFF)
PPT_LIGHT = RGBColor(0xD6, 0xEC, 0xEE)


def set_run(run, size=20, bold=False, color=PPT_INK, font_name="DejaVu Sans"):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = font_name


def add_bg(slide, r, g, b):
    fill = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    fill.fill.solid()
    fill.fill.fore_color.rgb = RGBColor(r, g, b)
    fill.line.fill.background()
    # send to back
    spTree = slide.shapes._spTree
    sp = fill._element
    spTree.remove(sp)
    spTree.insert(2, sp)


def add_title_bar(slide, text):
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(1.05))
    bar.fill.solid()
    bar.fill.fore_color.rgb = PPT_TEAL
    bar.line.fill.background()
    tf = bar.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    run = p.add_run()
    run.text = "  " + text
    set_run(run, 28, True, PPT_WHITE)


def add_bullets(text_frame, items, size=20):
    text_frame.clear()
    for i, item in enumerate(items):
        p = text_frame.paragraphs[0] if i == 0 else text_frame.add_paragraph()
        p.level = 0
        p.space_after = Pt(10)
        run = p.add_run()
        run.text = "• " + item
        set_run(run, size, False, PPT_INK)


def new_slide(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])


def add_image_fit(slide, path, left, top, width, height):
    """Place image inside a box while preserving aspect ratio."""
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"Отсутствует обязательный файл: {path}")
    with PILImage.open(path) as im:
        iw, ih = im.size
    box_w = int(width)
    box_h = int(height)
    scale = min(box_w / iw, box_h / ih)
    new_w = int(iw * scale)
    new_h = int(ih * scale)
    left_adj = int(left) + (box_w - new_w) // 2
    top_adj = int(top) + (box_h - new_h) // 2
    slide.shapes.add_picture(str(path), left_adj, top_adj, width=new_w, height=new_h)


def build_pptx(output_path: Path) -> None:
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # 1 Cover
    s = new_slide(prs)
    add_bg(s, 245, 240, 232)
    add_image_fit(s, asset("slide-cover.jpg"), Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    overlay = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), Inches(1.6), Inches(12.1), Inches(4.3))
    overlay.fill.solid()
    overlay.fill.fore_color.rgb = RGBColor(255, 255, 255)
    overlay.fill.fore_color.rgb = PPT_WHITE
    # semi via solid white is fine
    overlay.line.color.rgb = PPT_TEAL
    tf = overlay.text_frame
    tf.word_wrap = True
    lines = [
        ("Занятие 1", 22, False, PPT_CORAL),
        ("Введение в музыкально-ритмическое развитие ребёнка", 30, True, PPT_TEAL),
        ("Тема: значение ритма и движения в развитии дошкольника", 18, False, PPT_INK),
        ("Студенты педагогических колледжей · 90 минут", 16, False, PPT_MUTED),
    ]
    for i, (text, size, bold, color) in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.CENTER
        p.space_after = Pt(12)
        run = p.add_run()
        run.text = text
        set_run(run, size, bold, color)

    # 2 Goals
    s = new_slide(prs)
    add_bg(s, 245, 240, 232)
    add_title_bar(s, "Цель и задачи занятия")
    box = s.shapes.add_textbox(Inches(0.7), Inches(1.4), Inches(12), Inches(5.5))
    add_bullets(
        box.text_frame,
        [
            "Цель: понять сущность музыкально-ритмического развития дошкольника и отработать базовые приёмы.",
            "Образовательная: понятие, отличия ритмики / танца / хореографии, задачи специалистов.",
            "Развивающая: анализ связи музыки, движения, эмоций и интеллекта.",
            "Практическая: характер музыки, настроение через движение, музыкальная реакция.",
            "Результат: студент может объяснить, сравнить и провести фрагмент упражнения.",
        ],
        22,
    )

    # 3 Timeline
    s = new_slide(prs)
    add_bg(s, 245, 240, 232)
    add_title_bar(s, "Хронометраж: 90 минут")
    add_image_fit(s, asset("scheme-timeline.png"), Inches(0.4), Inches(1.25), Inches(12.5), Inches(5.9))

    # 4 Definition
    s = new_slide(prs)
    add_bg(s, 245, 240, 232)
    add_title_bar(s, "1. Понятие музыкально-ритмического развития")
    left = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.5), Inches(1.4), Inches(6.2), Inches(5.5))
    left.fill.solid()
    left.fill.fore_color.rgb = PPT_LIGHT
    left.line.color.rgb = PPT_TEAL
    tf = left.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    run = p.add_run()
    run.text = "Определение"
    set_run(run, 22, True, PPT_TEAL)
    p2 = tf.add_paragraph()
    p2.space_before = Pt(16)
    run2 = p2.add_run()
    run2.text = (
        "Процесс формирования у ребёнка способности воспринимать музыку и выражать её характер, "
        "темп, динамику и ритм через движение."
    )
    set_run(run2, 20, False, PPT_INK)
    right = s.shapes.add_textbox(Inches(7), Inches(1.5), Inches(5.7), Inches(5.3))
    add_bullets(
        right.text_frame,
        [
            "Слух + эмоция + движение",
            "Не только танец к утреннику",
            "3–4 года: яркий характер",
            "4–5 лет: контрасты",
            "5–7 лет: точность и выразительность",
        ],
        22,
    )

    # 5 Connection
    s = new_slide(prs)
    add_bg(s, 245, 240, 232)
    add_title_bar(s, "2. Связь музыки, движения, эмоций и интеллекта")
    add_image_fit(s, asset("scheme-connection.png"), Inches(0.35), Inches(1.3), Inches(12.6), Inches(5.5))

    # 6 Why important + image
    s = new_slide(prs)
    add_bg(s, 245, 240, 232)
    add_title_bar(s, "Почему это важно дошкольнику")
    add_image_fit(s, asset("slide-children-rhythm.jpg"), Inches(0.4), Inches(1.3), Inches(7.2), Inches(5.5))
    box = s.shapes.add_textbox(Inches(7.9), Inches(1.5), Inches(4.9), Inches(5.3))
    add_bullets(
        box.text_frame,
        [
            "Ведущая деятельность — игра",
            "Мышление образное и действенное",
            "Эмоции активно развиваются",
            "Формируются предпосылки учебной деятельности",
            "Тело помогает понять музыку",
        ],
        20,
    )

    # 7 Rhythm roles
    s = new_slide(prs)
    add_bg(s, 245, 240, 232)
    add_title_bar(s, "3. Роль ритма: координация, внимание, память, речь")
    add_image_fit(s, asset("scheme-rhythm-roles.png"), Inches(0.35), Inches(1.2), Inches(12.6), Inches(5.9))

    # 8 Four skills image
    s = new_slide(prs)
    add_bg(s, 245, 240, 232)
    add_title_bar(s, "Ритм на практике: четыре сферы развития")
    add_image_fit(s, asset("slide-four-skills.jpg"), Inches(0.8), Inches(1.3), Inches(11.7), Inches(5.6))

    # 9 Concepts
    s = new_slide(prs)
    add_bg(s, 245, 240, 232)
    add_title_bar(s, "4. Ритмика, деятельность, танец, хореография")
    add_image_fit(s, asset("scheme-concepts.png"), Inches(0.25), Inches(1.15), Inches(12.8), Inches(6.0))

    # 10 Error slide
    s = new_slide(prs)
    add_bg(s, 245, 240, 232)
    add_title_bar(s, "Важное предупреждение для практики")
    card = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), Inches(2.0), Inches(10.9), Inches(4.2))
    card.fill.solid()
    card.fill.fore_color.rgb = RGBColor(0xFC, 0xE8, 0xE0)
    card.line.color.rgb = PPT_CORAL
    tf = card.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = "Типичная ошибка"
    set_run(run, 28, True, PPT_CORAL)
    p2 = tf.add_paragraph()
    p2.alignment = PP_ALIGN.CENTER
    p2.space_before = Pt(20)
    run2 = p2.add_run()
    run2.text = "Сводить всё занятие к разучиванию танца „на показ“."
    set_run(run2, 24, False, PPT_INK)
    p3 = tf.add_paragraph()
    p3.alignment = PP_ALIGN.CENTER
    p3.space_before = Pt(18)
    run3 = p3.add_run()
    run3.text = "Баланс: восприятие и реакция → игра → элементы танца"
    set_run(run3, 22, True, PPT_TEAL)

    # 11 Roles
    s = new_slide(prs)
    add_bg(s, 245, 240, 232)
    add_title_bar(s, "5. Задачи музыкального руководителя и воспитателя")
    add_image_fit(s, asset("scheme-roles.png"), Inches(0.35), Inches(1.2), Inches(12.6), Inches(5.7))

    # 12 Teachers image
    s = new_slide(prs)
    add_bg(s, 245, 240, 232)
    add_title_bar(s, "Сотрудничество специалистов")
    add_image_fit(s, asset("slide-teachers-roles.jpg"), Inches(0.4), Inches(1.3), Inches(7.3), Inches(5.5))
    box = s.shapes.add_textbox(Inches(8), Inches(1.6), Inches(4.8), Inches(5.2))
    add_bullets(
        box.text_frame,
        [
            "Музруководитель проектирует и ведёт",
            "Воспитатель закрепляет в группе",
            "Вместе наблюдают за детьми",
            "Общие принципы: доступность, повтор, контраст, выразительность",
        ],
        20,
    )

    # 13 Practice intro
    s = new_slide(prs)
    add_bg(s, 245, 240, 232)
    add_title_bar(s, "Практика со студентами")
    add_image_fit(s, asset("slide-music-characters.jpg"), Inches(0.4), Inches(1.3), Inches(7.3), Inches(5.5))
    box = s.shapes.add_textbox(Inches(8), Inches(1.6), Inches(4.8), Inches(5.2))
    add_bullets(
        box.text_frame,
        [
            "1) Движение под музыку разного характера",
            "2) Настроение через движение",
            "3) Упражнения на музыкальную реакцию",
            "Формат: показ → выполнение → разбор „как с детьми“",
        ],
        20,
    )

    # 14 Practice 1
    s = new_slide(prs)
    add_bg(s, 245, 240, 232)
    add_title_bar(s, "Практика 1. Характер музыки → качество движения")
    rows = [
        ("Марш", "чёткий шаг, собранность"),
        ("Плясовая", "лёгкость, прыжковость"),
        ("Колыбельная", "плавность, мягкость"),
        ("Вальс", "кружение, мягкий акцент на „раз“"),
    ]
    for i, (title, desc) in enumerate(rows):
        x = 0.5 + (i % 2) * 6.3
        y = 1.5 + (i // 2) * 2.7
        shape = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(5.9), Inches(2.3))
        shape.fill.solid()
        shape.fill.fore_color.rgb = PPT_LIGHT if i % 2 == 0 else RGBColor(0xFC, 0xE8, 0xE0)
        shape.line.color.rgb = PPT_TEAL if i % 2 == 0 else PPT_CORAL
        tf = shape.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        run = p.add_run()
        run.text = title
        set_run(run, 24, True, PPT_TEAL if i % 2 == 0 else PPT_CORAL)
        p2 = tf.add_paragraph()
        p2.space_before = Pt(12)
        run2 = p2.add_run()
        run2.text = desc
        set_run(run2, 20, False, PPT_INK)

    # 15 Practice 2-3
    s = new_slide(prs)
    add_bg(s, 245, 240, 232)
    add_title_bar(s, "Практика 2–3. Настроение и музыкальная реакция")
    box = s.shapes.add_textbox(Inches(0.7), Inches(1.4), Inches(12), Inches(5.6))
    add_bullets(
        box.text_frame,
        [
            "Настроение: показать только движением, затем назвать чувство.",
            "Старт/стоп: движение лишь пока звучит музыка.",
            "Сильная доля: хлопок или притоп только на „раз“.",
            "Динамический код: piano — на носках; forte — энергичный шаг.",
            "Темповый код: ускорение и замедление строго по музыке.",
            "Смена образа: „капельки“ / „ветер“ по музыкальной фразе.",
        ],
        22,
    )

    # 16 Reflection
    s = new_slide(prs)
    add_bg(s, 245, 240, 232)
    add_title_bar(s, "Рефлексия и домашнее задание")
    left = s.shapes.add_textbox(Inches(0.6), Inches(1.4), Inches(6.2), Inches(5.5))
    tf = left.text_frame
    p = tf.paragraphs[0]
    run = p.add_run()
    run.text = "Обсудим"
    set_run(run, 24, True, PPT_CORAL)
    for item in [
        "Чем ритмическое развитие отличается от танца?",
        "Что тренирует упражнение «замри на паузе»?",
        "Где граница задач специалистов?",
        "Что возьмёте для детей 4–5 лет?",
    ]:
        p = tf.add_paragraph()
        p.space_before = Pt(12)
        run = p.add_run()
        run.text = "• " + item
        set_run(run, 18, False, PPT_INK)

    right = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.1), Inches(1.5), Inches(5.6), Inches(5.2))
    right.fill.solid()
    right.fill.fore_color.rgb = PPT_LIGHT
    right.line.color.rgb = PPT_TEAL
    tf = right.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    run = p.add_run()
    run.text = "Домашнее задание"
    set_run(run, 24, True, PPT_TEAL)
    for item in [
        "Карточка упражнения",
        "3 контрастных фрагмента",
        "Определение из Ветлугиной + сравнение с конспектом",
    ]:
        p = tf.add_paragraph()
        p.space_before = Pt(14)
        run = p.add_run()
        run.text = "• " + item
        set_run(run, 18, False, PPT_INK)

    # 17 Literature
    s = new_slide(prs)
    add_bg(s, 245, 240, 232)
    add_title_bar(s, "Литература")
    box = s.shapes.add_textbox(Inches(1.2), Inches(2.2), Inches(10.8), Inches(4))
    add_bullets(
        box.text_frame,
        [
            "Н. А. Ветлугина — «Теория и методика музыкального воспитания в детском саду»",
            "Б. М. Теплов — «Психология музыкальных способностей»",
            "А. И. Буренина — «Ритмическая мозаика»",
        ],
        24,
    )

    # 18 Final
    s = new_slide(prs)
    add_bg(s, 245, 240, 232)
    add_image_fit(s, asset("slide-cover.jpg"), Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    card = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.5), Inches(2.1), Inches(10.3), Inches(3.4))
    card.fill.solid()
    card.fill.fore_color.rgb = PPT_WHITE
    card.line.color.rgb = PPT_TEAL
    tf = card.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = "Ритм и движение — ежедневный ресурс развития ребёнка"
    set_run(run, 28, True, PPT_TEAL)
    p2 = tf.add_paragraph()
    p2.alignment = PP_ALIGN.CENTER
    p2.space_before = Pt(18)
    run2 = p2.add_run()
    run2.text = "Воспитатель замечает, закрепляет и продолжает музыкальный опыт"
    set_run(run2, 20, False, PPT_INK)

    prs.save(str(output_path))
    print(f"PPTX written: {output_path}")


def publish_pair() -> None:
    require_assets()
    with tempfile.TemporaryDirectory(prefix="lesson1-build-") as tmp:
        tmpdir = Path(tmp)
        pdf_tmp = tmpdir / OUT_PDF.name
        pptx_tmp = tmpdir / OUT_PPTX.name
        build_pdf(pdf_tmp)
        build_pptx(pptx_tmp)
        os.replace(pdf_tmp, OUT_PDF)
        os.replace(pptx_tmp, OUT_PPTX)
    print(f"Published:\n  - {OUT_PDF}\n  - {OUT_PPTX}")


if __name__ == "__main__":
    publish_pair()
