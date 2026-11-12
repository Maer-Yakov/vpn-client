#!/usr/bin/env python3
"""Сценарий занятия 7 в формате практического конспекта (как образец «4 занятие»)."""

from __future__ import annotations

import os
import tempfile
import time
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    ListFlowable,
    ListItem,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)

from font_paths import resolve_fonts

ROOT = Path(__file__).resolve().parent
OUT_PDF = ROOT / "Scenariy_zanyatiya_7_Muzykalno_ritmicheskoe_razvitie_1_5_3.pdf"

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

INK = colors.Color(30 / 255, 30 / 255, 30 / 255)
MUTED = colors.Color(70 / 255, 70 / 255, 70 / 255)


def build_styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="DocTitle",
            fontName="DejaVuBold",
            fontSize=16,
            leading=21,
            alignment=TA_CENTER,
            textColor=INK,
            spaceAfter=10,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Meta",
            fontName="DejaVu",
            fontSize=11,
            leading=15,
            alignment=TA_LEFT,
            textColor=INK,
            spaceAfter=4,
        )
    )
    styles.add(
        ParagraphStyle(
            name="MetaBold",
            fontName="DejaVuBold",
            fontSize=11,
            leading=15,
            textColor=INK,
            spaceBefore=8,
            spaceAfter=3,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Section",
            fontName="DejaVuBold",
            fontSize=12.5,
            leading=17,
            textColor=INK,
            spaceBefore=12,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SubSection",
            fontName="DejaVuBold",
            fontSize=11,
            leading=15,
            textColor=INK,
            spaceBefore=8,
            spaceAfter=3,
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
            spaceAfter=4,
        )
    )
    styles.add(
        ParagraphStyle(
            name="BulletText",
            fontName="DejaVu",
            fontSize=10.5,
            leading=14.5,
            textColor=INK,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Footer",
            fontName="DejaVu",
            fontSize=8,
            textColor=MUTED,
            alignment=TA_CENTER,
        )
    )
    return styles


def p(text, style):
    return Paragraph(text, style)


def bullets(items, styles, bullet="•", left=12):
    flowables = []
    for item in items:
        flowables.append(
            ListItem(
                Paragraph(item, styles["BulletText"]),
                leftIndent=left,
                bulletColor=INK,
                value=bullet,
            )
        )
    return ListFlowable(
        flowables,
        bulletType="bullet",
        start=bullet,
        leftIndent=left,
        bulletFontName="DejaVu",
        bulletFontSize=10.5,
        spaceBefore=1,
        spaceAfter=4,
    )


def add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont("DejaVu", 8)
    canvas.setFillColor(MUTED)
    canvas.drawCentredString(A4[0] / 2, 12 * mm, f"стр. {doc.page}")
    canvas.restoreState()


def build_pdf(output_path: Path) -> None:
    styles = build_styles()
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title="Сценарий занятия 7. Музыкально-ритмическое развитие детей от 1,5 до 3 лет",
        author="Педагогический колледж",
    )
    story = []

    story.append(
        p(
            "Сценарий занятия: Музыкально-ритмическое развитие детей от 1,5 до 3 лет",
            styles["DocTitle"],
        )
    )
    story.append(p("<b>Продолжительность:</b> 90 минут", styles["Meta"]))
    story.append(
        p(
            "<b>Аудитория:</b> студенты педагогических специальностей (будущие воспитатели); "
            "содержание ориентировано на работу с детьми раннего возраста.",
            styles["Meta"],
        )
    )
    story.append(
        p(
            "<b>Цель:</b> сформировать у студентов умение организовывать музыкально-ритмическую "
            "деятельность детей 1,5–3 лет: развивать самостоятельные движения через подражание, "
            "простые двигательные последовательности, реакцию на начало и окончание музыки, "
            "ритмичную ходьбу и бег, игры с предметами.",
            styles["Body"],
        )
    )

    story.append(p("Материалы:", styles["MetaBold"]))
    story.append(
        bullets(
            [
                "музыкальный центр или ноутбук с колонками;",
                "аудиозаписи разного характера: спокойная, маршевая умеренная, лёгкая плясовая, "
                "фрагменты с чётким началом и окончанием;",
                "платочки / лёгкие шарфики (по числу участников);",
                "погремушки (по числу участников или на подгруппу);",
                "ленточки;",
                "мягкие модули или коврики;",
                "корзина для сбора предметов после игр.",
            ],
            styles,
        )
    )

    story.append(p("Ход занятия:", styles["MetaBold"]))

    # ----- I -----
    story.append(p("I. Вводная часть (15 минут)", styles["Section"]))

    story.append(p("1. Приветствие и настрой (4 минуты)", styles["SubSection"]))
    story.append(
        bullets(
            [
                "Участники собираются в кругу.",
                "Краткое приветствие и обозначение темы: «Сегодня мы учимся работать с малышами "
                "1,5–3 лет: они ещё не танцуют “по правилам”, но уже могут шагать, хлопать, "
                "останавливаться и играть с платочком под музыку».",
                "Опорный вопрос занятия: что ребёнок этого возраста уже может делать сам, "
                "а чего от него ещё рано требовать?",
            ],
            styles,
        )
    )

    story.append(p("2. Погружение в возраст через движение (6 минут)", styles["SubSection"]))
    story.append(
        bullets(
            [
                "Игра «Музыка есть — движения есть»: пока звучит музыка — мягкие покачивания "
                "или лёгкие хлопки; музыка закончилась — полная остановка.",
                "Повтор 2–3 раза на коротких фрагментах.",
                "Короткий разбор: для малыша старт и стоп — уже большое умение; именно с этого "
                "начинается реакция на начало и окончание музыки.",
            ],
            styles,
        )
    )

    story.append(p("3. Разминка «Повтори за мной» (5 минут)", styles["SubSection"]))
    story.append(
        bullets(
            [
                "Педагог показывает простые движения крупно и чуть замедленнее обычного: "
                "руки вверх — вниз, хлопок, притоп, поворот корпуса.",
                "Студенты повторяют сразу за показом — модель подражания взрослому.",
                "Правило показа: одно движение — один смысл; не больше 1–2 элементов подряд.",
            ],
            styles,
        )
    )

    # ----- II -----
    story.append(p("II. Основная часть (50 минут)", styles["Section"]))

    story.append(
        p(
            "1. Самостоятельные движения и подражание (10 минут)",
            styles["SubSection"],
        )
    )
    story.append(
        bullets(
            [
                "Краткая теоретическая опора: путь малыша — «вместе с взрослым → по показу → сам».",
                "Практикум в парах: один — педагог, второй — «ребёнок 2 лет».",
                "Задание «педагога»: показать шаг под музыку так, чтобы «ребёнок» мог повторить; "
                "затем отойти и дать попробовать самому на знакомый фрагмент.",
                "Смена ролей.",
                "Вывод: самостоятельность — это инициатива ребёнка на музыкальный сигнал, "
                "а не работа без взрослого и не идеальная техника.",
            ],
            styles,
        )
    )

    story.append(
        p(
            "2. Простые двигательные последовательности (8 минут)",
            styles["SubSection"],
        )
    )
    story.append(
        bullets(
            [
                "Цепочка из двух действий: музыка — идём; пауза — стоим.",
                "Цепочка из трёх действий: хлопки → притопы → стоп.",
                "Усложнение только после уверенного повтора предыдущего шага.",
                "Типичная ошибка: сразу давать “танец целиком”. Для 1,5–3 лет достаточно "
                "2–3 понятных действий.",
            ],
            styles,
        )
    )

    story.append(
        p(
            "3. Ритмичная ходьба, бег и реакция на музыку (10 минут)",
            styles["SubSection"],
        )
    )
    story.append(
        bullets(
            [
                "Ходьба по кругу за педагогом под умеренную маршевую музыку.",
                "На окончание музыки — остановка.",
                "Лёгкий короткий бег под быстрый фрагмент; мгновенный стоп на паузе.",
                "Чередование: медленная часть — шаг; быстрая — лёгкий бег.",
                "Акцент безопасности: бег короткий, без столкновений; не доводить до усталости.",
            ],
            styles,
        )
    )

    story.append(
        p(
            "4. Образные игры: мишки, зайчики, птички (12 минут)",
            styles["SubSection"],
        )
    )
    story.append(
        bullets(
            [
                "«Идём как мишки» (4 минуты): медленная тяжёлая ходьба, руки «лапы». "
                "Для 1,5–2 лет достаточно тяжёлых шагов за педагогом; ближе к 3 годам можно "
                "добавить покачивание «мишка устал».",
                "«Прыгаем как зайчики» (4 минуты): пружинка ногами или небольшие прыжки на месте. "
                "Не требовать высоты и длинных серий прыжков.",
                "«Птички летают» (4 минуты): лёгкий шаг или короткий бег, руки-крылья; "
                "на окончание музыки птички «садятся».",
                "После каждой игры — один вопрос: какое качество движения соответствует музыке?",
            ],
            styles,
        )
    )

    story.append(
        p(
            "5. Хлопки, притопы и игры с предметами (10 минут)",
            styles["SubSection"],
        )
    )
    story.append(
        bullets(
            [
                "Хлопки под музыку → хлопки по показу педагога → мягкий притоп → хлопок и притоп по очереди.",
                "Игра с платочками: машем под музыку; на паузе прячем платочек за спину.",
                "Игра с погремушками: трясём только пока звучит музыка; на окончании — тишина.",
                "Игра с ленточками: «рисуем» волны и круги в воздухе; на окончании лента опускается вниз.",
                "Правило: сначала движение без предмета или с показом, затем тот же приём с предметом.",
                "Техника безопасности: не наматывать ленту на шею; не бить погремушкой соседа; "
                "после игры — ритуал «предмет отдыхает в корзине».",
            ],
            styles,
        )
    )

    # ----- III -----
    story.append(p("III. Заключительная часть (25 минут)", styles["Section"]))

    story.append(
        p(
            "1. Простые движения в паре с педагогом и мини-пробы студентов (15 минут)",
            styles["SubSection"],
        )
    )
    story.append(
        bullets(
            [
                "Модель пары «педагог — ребёнок»: ходьба за руки под музыку, мягкое покачивание, "
                "общий стоп на паузе. Для 1,5–2 лет такая пара важнее, чем пара детей между собой.",
                "Студенты делятся на группы по 3–4 человека.",
                "Каждая группа готовит и показывает короткий фрагмент занятия для возраста 1,5–3 лет "
                "(2–3 минуты): одна образная игра или одна предметная игра + реакция на окончание музыки.",
                "Можно использовать платочки, погремушки, ленточки.",
                "Педагог помогает с упрощением показа и безопасностью пространства.",
                "Презентация мини-игр по группам.",
            ],
            styles,
        )
    )

    story.append(p("2. Итоги занятия и рефлексия (5 минут)", styles["SubSection"]))
    story.append(
        bullets(
            [
                "Что важнее в работе с малышами: точность танца или ясный показ и радость отклика?",
                "Какую цепочку из двух действий вы возьмёте на первую встречу с группой 2 лет?",
                "Какой предмет лучше помогает тренировать реакцию на окончание музыки?",
                "Игра «Закончи фразу»: «С детьми 1,5–3 лет я буду...», «Самым полезным сегодня было...»",
            ],
            styles,
        )
    )

    story.append(p("3. Прощание и домашнее задание (5 минут)", styles["SubSection"]))
    story.append(
        bullets(
            [
                "Спокойная музыка, ритуал прощания.",
                "Домашнее задание: карточка одной игры для возраста 1,5–3 лет "
                "(цель, музыка, ход, вариации для 1,5–2 и 2–3 лет, критерии наблюдения, техника безопасности); "
                "две игры с одним предметом — на «старт/стоп» и на образ; "
                "выписки 5–7 рекомендаций из литературы по списку ниже.",
                "Благодарность за участие.",
            ],
            styles,
        )
    )

    story.append(p("Литература:", styles["MetaBold"]))
    story.append(
        bullets(
            [
                "Дзержинская И. Л. Музыкальное воспитание младших дошкольников.",
                "Каплунова И., Новоскольцева И. Ладушки.",
                "Бабаджан Т. С. Музыкальное воспитание детей раннего возраста.",
            ],
            styles,
        )
    )

    story.append(Spacer(1, 8 * mm))
    story.append(
        p(
            "Специальность «Дошкольное образование». Занятие 7.",
            styles["Footer"],
        )
    )

    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    print(f"PDF written: {output_path}")


def publish_pdf() -> None:
    """Пишем во временный файл на той же ФС, что и OUT_PDF, затем атомарно публикуем."""
    OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    build_started = time.time_ns()
    with tempfile.TemporaryDirectory(prefix="scenario7-", dir=str(OUT_PDF.parent)) as tmp:
        tmp_pdf = Path(tmp) / OUT_PDF.name
        build_pdf(tmp_pdf)
        if OUT_PDF.exists() and OUT_PDF.stat().st_mtime_ns > build_started:
            raise RuntimeError(
                "Пропуск публикации: целевой PDF уже обновлён более новой сборкой."
            )
        os.replace(tmp_pdf, OUT_PDF)
    print(f"Published: {OUT_PDF}")


if __name__ == "__main__":
    publish_pdf()
