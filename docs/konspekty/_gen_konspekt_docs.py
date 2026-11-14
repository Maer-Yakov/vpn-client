#!/usr/bin/env python3
"""Generate PDF and DOCX from a lesson conspectus markdown file."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
FONT_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"


def register_fonts() -> None:
    pdfmetrics.registerFont(TTFont("DejaVuSerif", FONT_REG))
    pdfmetrics.registerFont(TTFont("DejaVuSerif-Bold", FONT_BOLD))
    pdfmetrics.registerFont(TTFont("DejaVuSans", FONT_SANS))
    pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", FONT_SANS_BOLD))
    pdfmetrics.registerFont(TTFont("DejaVuMono", FONT_MONO))


def md_inline_to_rl(text: str) -> str:
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"`(.+?)`", r"<font face='DejaVuMono' size='9'>\1</font>", text)
    return text


def set_run_font(run, name: str = "Times New Roman", size: int = 12, bold: bool = False):
    run.font.name = name
    run._element.rPr.rFonts.set(qn("w:eastAsia"), name)
    run.font.size = Pt(size)
    run.bold = bold


def parse_blocks(md: str):
    lines = md.splitlines()
    blocks = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.strip() == "---":
            blocks.append(("hr",))
            i += 1
            continue
        if line.startswith("```"):
            lang = line[3:].strip()
            i += 1
            code = []
            while i < len(lines) and not lines[i].startswith("```"):
                code.append(lines[i])
                i += 1
            i += 1
            blocks.append(("code", "\n".join(code), lang))
            continue
        if line.startswith("|") and i + 1 < len(lines) and re.match(r"^\|?\s*-+", lines[i + 1]):
            table = []
            while i < len(lines) and lines[i].startswith("|"):
                row = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not re.match(r"^:?-+:?$", row[0].replace(" ", "")) and not all(
                    re.match(r"^:?-+:?$", c.replace(" ", "")) for c in row
                ):
                    table.append(row)
                i += 1
            blocks.append(("table", table))
            continue
        if line.startswith("#"):
            level = len(line) - len(line.lstrip("#"))
            blocks.append(("heading", level, line[level:].strip()))
            i += 1
            continue
        if line.strip() == "":
            i += 1
            continue
        para = [line]
        i += 1
        while i < len(lines):
            nxt = lines[i]
            if (
                nxt.strip() == ""
                or nxt.startswith("#")
                or nxt.startswith("|")
                or nxt.startswith("```")
                or nxt.strip() == "---"
            ):
                break
            para.append(nxt)
            i += 1
        blocks.append(("para", "\n".join(para)))
    return blocks


def build_pdf(md_path: Path, pdf_path: Path) -> None:
    register_fonts()
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="TitleRU",
            fontName="DejaVuSerif-Bold",
            fontSize=16,
            leading=20,
            alignment=TA_CENTER,
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="H1RU",
            fontName="DejaVuSerif-Bold",
            fontSize=14,
            leading=18,
            spaceBefore=14,
            spaceAfter=8,
            textColor=colors.HexColor("#1a1a1a"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="H2RU",
            fontName="DejaVuSerif-Bold",
            fontSize=12.5,
            leading=16,
            spaceBefore=10,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="H3RU",
            fontName="DejaVuSerif-Bold",
            fontSize=11.5,
            leading=15,
            spaceBefore=8,
            spaceAfter=4,
        )
    )
    styles.add(
        ParagraphStyle(
            name="BodyRU",
            fontName="DejaVuSerif",
            fontSize=11,
            leading=15,
            alignment=TA_JUSTIFY,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="MetaRU",
            fontName="DejaVuSerif",
            fontSize=10.5,
            leading=14,
            alignment=TA_LEFT,
            spaceAfter=3,
        )
    )
    styles.add(
        ParagraphStyle(
            name="CodeRU",
            fontName="DejaVuMono",
            fontSize=9,
            leading=12,
            leftIndent=8,
            spaceBefore=4,
            spaceAfter=8,
            backColor=colors.HexColor("#f5f5f5"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="CellRU",
            fontName="DejaVuSerif",
            fontSize=9,
            leading=12,
        )
    )
    styles.add(
        ParagraphStyle(
            name="CellHeaderRU",
            fontName="DejaVuSerif-Bold",
            fontSize=9,
            leading=12,
        )
    )

    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=1.8 * cm,
        bottomMargin=1.8 * cm,
        title=md_path.stem,
    )
    story = []
    blocks = parse_blocks(md_path.read_text(encoding="utf-8"))

    for block in blocks:
        kind = block[0]
        if kind == "hr":
            story.append(Spacer(1, 6))
            continue
        if kind == "heading":
            level, text = block[1], block[2]
            style = {1: "H1RU", 2: "H2RU"}.get(level, "H3RU")
            if level == 1 and ("КОНСПЕКТ" in text.upper() or text.startswith("КОНСПЕКТ")):
                story.append(Paragraph(md_inline_to_rl(text), styles["TitleRU"]))
            else:
                story.append(Paragraph(md_inline_to_rl(text), styles[style]))
            continue
        if kind == "code":
            story.append(Preformatted(block[1], styles["CodeRU"]))
            continue
        if kind == "table":
            rows = block[1]
            data = []
            for r_i, row in enumerate(rows):
                styled = []
                for cell in row:
                    st = styles["CellHeaderRU"] if r_i == 0 else styles["CellRU"]
                    styled.append(Paragraph(md_inline_to_rl(cell), st))
                data.append(styled)
            col_n = max(len(r) for r in data) if data else 1
            usable = A4[0] - 4 * cm
            col_w = [usable / col_n] * col_n
            t = Table(data, colWidths=col_w, repeatRows=1)
            t.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8eef5")),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#444444")),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 4),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                        ("TOPPADDING", (0, 0), (-1, -1), 3),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#fafafa")]),
                    ]
                )
            )
            story.append(t)
            story.append(Spacer(1, 8))
            continue
        if kind == "para":
            text = block[1]
            # meta-ish short lines stay left
            style = styles["MetaRU"] if text.startswith("**") and len(text) < 180 else styles["BodyRU"]
            for part in text.split("\n"):
                if part.strip():
                    story.append(Paragraph(md_inline_to_rl(part), style))
            continue

    doc.build(story)


def add_docx_paragraph(doc: Document, text: str, *, bold_all: bool = False, size: int = 12, space_after: int = 6, align=None):
    p = doc.add_paragraph()
    if align is not None:
        p.alignment = align
    pf = p.paragraph_format
    pf.space_after = Pt(space_after)
    pf.line_spacing_rule = WD_LINE_SPACING.SINGLE
    # split bold segments
    parts = re.split(r"(\*\*.+?\*\*)", text)
    if bold_all and len(parts) == 1:
        run = p.add_run(text)
        set_run_font(run, size=size, bold=True)
        return p
    for part in parts:
        if not part:
            continue
        if part.startswith("**") and part.endswith("**"):
            run = p.add_run(part[2:-2])
            set_run_font(run, size=size, bold=True)
        else:
            run = p.add_run(part)
            set_run_font(run, size=size, bold=False)
    return p


def build_docx(md_path: Path, docx_path: Path) -> None:
    doc = Document()
    for section in doc.sections:
        section.top_margin = Cm(2)
        section.bottom_margin = Cm(2)
        section.left_margin = Cm(2.5)
        section.right_margin = Cm(2)

    style = doc.styles["Normal"]
    style.font.name = "Times New Roman"
    style.font.size = Pt(12)
    style._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")

    blocks = parse_blocks(md_path.read_text(encoding="utf-8"))
    for block in blocks:
        kind = block[0]
        if kind == "hr":
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(4)
            continue
        if kind == "heading":
            level, text = block[1], block[2]
            sizes = {1: 16, 2: 14, 3: 13}
            align = WD_ALIGN_PARAGRAPH.CENTER if level == 1 else WD_ALIGN_PARAGRAPH.LEFT
            add_docx_paragraph(doc, text, bold_all=True, size=sizes.get(level, 12), space_after=8, align=align)
            continue
        if kind == "code":
            p = doc.add_paragraph()
            run = p.add_run(block[1])
            set_run_font(run, name="Courier New", size=9)
            p.paragraph_format.left_indent = Cm(0.5)
            p.paragraph_format.space_after = Pt(8)
            continue
        if kind == "table":
            rows = block[1]
            if not rows:
                continue
            cols = max(len(r) for r in rows)
            table = doc.add_table(rows=len(rows), cols=cols)
            table.style = "Table Grid"
            for r_i, row in enumerate(rows):
                for c_i in range(cols):
                    cell = table.rows[r_i].cells[c_i]
                    val = row[c_i] if c_i < len(row) else ""
                    cell.text = ""
                    p = cell.paragraphs[0]
                    # strip md bold for table cells simply
                    clean = re.sub(r"\*\*(.+?)\*\*", r"\1", val)
                    run = p.add_run(clean)
                    set_run_font(run, size=10, bold=(r_i == 0))
            doc.add_paragraph()
            continue
        if kind == "para":
            for part in block[1].split("\n"):
                if part.strip():
                    add_docx_paragraph(doc, part, size=12, space_after=4)
            continue

    doc.save(str(docx_path))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("md")
    ap.add_argument("--pdf")
    ap.add_argument("--docx")
    args = ap.parse_args()
    md_path = Path(args.md)
    pdf_path = Path(args.pdf) if args.pdf else md_path.with_suffix(".pdf")
    docx_path = Path(args.docx) if args.docx else md_path.with_suffix(".docx")
    build_pdf(md_path, pdf_path)
    build_docx(md_path, docx_path)
    # also copy to artifacts
    art = Path("/opt/cursor/artifacts")
    if art.exists():
        import shutil

        shutil.copy2(pdf_path, art / pdf_path.name)
        shutil.copy2(docx_path, art / docx_path.name)
        shutil.copy2(md_path, art / md_path.name)
    print(f"OK pdf={pdf_path} docx={docx_path}")


if __name__ == "__main__":
    main()
