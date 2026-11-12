#!/usr/bin/env python3
"""14-slide student presentation for lesson 1 — PowerPoint compatible."""

from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path

from PIL import Image as PILImage
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt, Emu

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
OUT = ROOT / "Prezentaciya_zanyatie_1_dlya_studentov.pptx"

# Palette
TEAL = RGBColor(0x0F, 0x76, 0x6E)
SKY = RGBColor(0x0E, 0x74, 0x90)
INK = RGBColor(0x1E, 0x29, 0x3B)
MUTED = RGBColor(0x64, 0x74, 0x8B)
BG = RGBColor(0xF8, 0xFA, 0xFC)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
SOFT = RGBColor(0xCC, 0xFB, 0xF1)
SOFT2 = RGBColor(0xE0, 0xF2, 0xFE)
LINE = RGBColor(0xCB, 0xD5, 0xE1)

REQUIRED = [
    "p14-hero.jpg",
    "p14-characters.jpg",
    "p14-roles.jpg",
    "p14-four-skills.jpg",
    "p14-scheme-definition.png",
    "p14-scheme-not-only.png",
    "p14-scheme-chain.png",
    "p14-scheme-spheres.png",
    "p14-scheme-concepts.png",
    "p14-scheme-roles.png",
    "p14-scheme-reactions.png",
    "p14-scheme-balance.png",
    "p14-scheme-characters.png",
]


def asset(name: str) -> Path:
    path = ASSETS / name
    if not path.is_file():
        raise FileNotFoundError(path)
    return path


def run(paragraph, text, size=22, bold=False, color=INK, align=None):
    paragraph.clear()
    if align is not None:
        paragraph.alignment = align
    r = paragraph.add_run()
    r.text = text
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.color.rgb = color
    r.font.name = "Calibri"
    return r


def add_run(paragraph, text, size=22, bold=False, color=INK):
    r = paragraph.add_run()
    r.text = text
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.color.rgb = color
    r.font.name = "Calibri"
    return r


def blank(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])


def bg(slide, color=BG):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    spTree = slide.shapes._spTree
    sp = shape._element
    spTree.remove(sp)
    spTree.insert(2, sp)


def accent_bar(slide):
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(0.18), Inches(7.5))
    bar.fill.solid()
    bar.fill.fore_color.rgb = TEAL
    bar.line.fill.background()


def title(slide, text, top=0.35):
    box = slide.shapes.add_textbox(Inches(0.55), Inches(top), Inches(12.3), Inches(0.8))
    tf = box.text_frame
    tf.word_wrap = True
    run(tf.paragraphs[0], text, size=32, bold=True, color=INK)
    return box


def picture_fit(slide, name, left, top, width, height):
    path = asset(name)
    with PILImage.open(path) as im:
        iw, ih = im.size
    box_w, box_h = int(width), int(height)
    scale = min(box_w / iw, box_h / ih)
    new_w, new_h = int(iw * scale), int(ih * scale)
    left_adj = int(left) + (box_w - new_w) // 2
    top_adj = int(top) + (box_h - new_h) // 2
    slide.shapes.add_picture(str(path), left_adj, top_adj, width=new_w, height=new_h)


def card(slide, left, top, width, height, fill=WHITE, line=TEAL):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    shape.line.color.rgb = line
    shape.line.width = Pt(1.5)
    return shape


def bullets(slide, left, top, width, height, items, size=22):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(12)
        add_run(p, "•  " + item, size=size, color=INK)
    return box


def build(output: Path) -> None:
    missing = [n for n in REQUIRED if not (ASSETS / n).is_file()]
    if missing:
        raise FileNotFoundError("Missing assets:\n  - " + "\n  - ".join(missing))

    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # 1 Title
    s = blank(prs)
    bg(s, BG)
    picture_fit(s, "p14-hero.jpg", Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    panel = card(s, Inches(0.7), Inches(4.35), Inches(11.9), Inches(2.55), WHITE, TEAL)
    tf = panel.text_frame
    tf.word_wrap = True
    run(tf.paragraphs[0], "Занятие 1", 18, True, SKY, PP_ALIGN.CENTER)
    p = tf.add_paragraph()
    p.alignment = PP_ALIGN.CENTER
    p.space_before = Pt(8)
    add_run(p, "Введение в музыкально-ритмическое развитие ребёнка", 28, True, INK)
    p = tf.add_paragraph()
    p.alignment = PP_ALIGN.CENTER
    p.space_before = Pt(10)
    add_run(p, "Значение ритма и движения в развитии дошкольника", 18, False, MUTED)
    p = tf.add_paragraph()
    p.alignment = PP_ALIGN.CENTER
    p.space_before = Pt(8)
    add_run(p, "Для будущих воспитателей  ·  90 минут", 16, False, TEAL)

    # 2 Question
    s = blank(prs)
    bg(s)
    accent_bar(s)
    title(s, "Вопрос всего занятия")
    q = card(s, Inches(1.2), Inches(2.2), Inches(10.9), Inches(3.4), SOFT, TEAL)
    tf = q.text_frame
    tf.word_wrap = True
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    add_run(
        tf.paragraphs[0],
        "Что я могу делать с детьми каждый день,\nчтобы ритм и движение развивали,\nа не только готовили к утреннику?",
        28,
        True,
        INK,
    )
    # Fix newlines - pptx needs separate paragraphs
    q.text_frame.clear()
    for i, line in enumerate(
        [
            "Что я могу делать с детьми каждый день,",
            "чтобы ритм и движение развивали,",
            "а не только готовили к утреннику?",
        ]
    ):
        p = q.text_frame.paragraphs[0] if i == 0 else q.text_frame.add_paragraph()
        p.alignment = PP_ALIGN.CENTER
        p.space_before = Pt(10 if i else 28)
        add_run(p, line, 28, True, INK)

    # 3 Definition
    s = blank(prs)
    bg(s)
    accent_bar(s)
    title(s, "Что такое музыкально-ритмическое развитие")
    picture_fit(s, "p14-scheme-definition.png", Inches(0.4), Inches(1.2), Inches(12.5), Inches(5.9))

    # 4 Not only dance
    s = blank(prs)
    bg(s)
    accent_bar(s)
    title(s, "Это не только танец")
    picture_fit(s, "p14-scheme-not-only.png", Inches(0.4), Inches(1.15), Inches(12.5), Inches(5.95))

    # 5 Chain
    s = blank(prs)
    bg(s)
    accent_bar(s)
    title(s, "Как связано: музыка, эмоция, движение, мышление")
    picture_fit(s, "p14-scheme-chain.png", Inches(0.4), Inches(1.2), Inches(12.5), Inches(5.9))

    # 6 Why important
    s = blank(prs)
    bg(s)
    accent_bar(s)
    title(s, "Почему это важно дошкольнику")
    picture_fit(s, "p14-hero.jpg", Inches(0.5), Inches(1.35), Inches(6.6), Inches(5.5))
    bullets(
        s,
        Inches(7.5),
        Inches(1.8),
        Inches(5.2),
        Inches(5.0),
        [
            "Ведущая деятельность — игра",
            "Мышление — образное и действенное",
            "Эмоции активно развиваются",
            "Формируются предпосылки учебной деятельности",
            "Тело помогает понять музыку",
        ],
        size=22,
    )

    # 7 Four spheres
    s = blank(prs)
    bg(s)
    accent_bar(s)
    title(s, "Ритм развивает четыре сферы")
    picture_fit(s, "p14-scheme-spheres.png", Inches(0.35), Inches(1.15), Inches(12.6), Inches(5.95))

    # 8 Practice examples
    s = blank(prs)
    bg(s)
    accent_bar(s)
    title(s, "Как это выглядит на практике")
    picture_fit(s, "p14-four-skills.jpg", Inches(0.5), Inches(1.25), Inches(12.3), Inches(5.8))

    # 9 Concepts
    s = blank(prs)
    bg(s)
    accent_bar(s)
    title(s, "Четыре понятия — не путать")
    picture_fit(s, "p14-scheme-concepts.png", Inches(0.35), Inches(1.1), Inches(12.6), Inches(6.0))

    # 10 Mistake + balance
    s = blank(prs)
    bg(s)
    accent_bar(s)
    title(s, "Типичная ошибка")
    warn = card(s, Inches(1.4), Inches(1.4), Inches(10.5), Inches(1.5), RGBColor(0xFE, 0xF2, 0xF2), RGBColor(0xDC, 0x26, 0x26))
    tf = warn.text_frame
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    p.space_before = Pt(18)
    add_run(p, "Сводить всё занятие к танцу «на показ»", 26, True, RGBColor(0xB9, 0x1C, 0x1C))
    picture_fit(s, "p14-scheme-balance.png", Inches(0.5), Inches(3.1), Inches(12.3), Inches(4.1))

    # 11 Roles
    s = blank(prs)
    bg(s)
    accent_bar(s)
    title(s, "Музруководитель и воспитатель — одно дело")
    picture_fit(s, "p14-scheme-roles.png", Inches(0.3), Inches(1.15), Inches(7.4), Inches(5.9))
    picture_fit(s, "p14-roles.jpg", Inches(7.8), Inches(1.6), Inches(5.0), Inches(5.2))

    # 12 Character practice
    s = blank(prs)
    bg(s)
    accent_bar(s)
    title(s, "Практика: характер музыки → движение")
    picture_fit(s, "p14-scheme-characters.png", Inches(0.3), Inches(1.15), Inches(8.0), Inches(5.9))
    picture_fit(s, "p14-characters.jpg", Inches(8.4), Inches(1.7), Inches(4.5), Inches(5.1))

    # 13 Reactions
    s = blank(prs)
    bg(s)
    accent_bar(s)
    title(s, "Практика: реакция на музыку")
    picture_fit(s, "p14-scheme-reactions.png", Inches(0.35), Inches(1.15), Inches(12.6), Inches(5.95))

    # 14 Conclusion
    s = blank(prs)
    bg(s)
    accent_bar(s)
    title(s, "Главный вывод")
    main = card(s, Inches(0.7), Inches(1.35), Inches(12.0), Inches(2.2), SOFT, TEAL)
    tf = main.text_frame
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    p.space_before = Pt(28)
    add_run(p, "Ритм и движение — ежедневный ресурс развития ребёнка", 26, True, INK)
    p = tf.add_paragraph()
    p.alignment = PP_ALIGN.CENTER
    p.space_before = Pt(10)
    add_run(p, "Роль воспитателя: замечать, закреплять, продолжать", 20, False, TEAL)

    hw = card(s, Inches(0.7), Inches(3.9), Inches(12.0), Inches(3.0), WHITE, SKY)
    tf = hw.text_frame
    run(tf.paragraphs[0], "Домашнее задание", 22, True, SKY)
    for item in [
        "Карточка упражнения (возраст, цель, музыка, ход, критерии)",
        "3 контрастных фрагмента: марш / колыбельная / плясовая",
        "Определение у Ветлугиной + сравнение с конспектом занятия",
    ]:
        p = tf.add_paragraph()
        p.space_before = Pt(10)
        add_run(p, "•  " + item, 18, False, INK)

    prs.save(str(output))
    print(f"PPTX written: {output}")


def normalize_with_libreoffice(pptx_path: Path) -> None:
    outdir = pptx_path.parent / "_lo_export"
    outdir.mkdir(exist_ok=True)
    subprocess.run(
        [
            "soffice",
            "--headless",
            "--convert-to",
            "pptx",
            "--outdir",
            str(outdir),
            str(pptx_path),
        ],
        check=True,
        capture_output=True,
    )
    converted = outdir / pptx_path.name
    os.replace(converted, pptx_path)
    for leftover in outdir.iterdir():
        leftover.unlink()
    outdir.rmdir()
    print(f"Normalized via LibreOffice: {pptx_path}")


if __name__ == "__main__":
    with tempfile.TemporaryDirectory(prefix="pptx14-") as tmp:
        tmp_path = Path(tmp) / OUT.name
        build(tmp_path)
        normalize_with_libreoffice(tmp_path)
        os.replace(tmp_path, OUT)
    print(f"Published: {OUT}")
