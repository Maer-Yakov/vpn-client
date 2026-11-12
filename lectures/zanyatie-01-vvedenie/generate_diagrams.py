#!/usr/bin/env python3
"""Generate educational diagrams for lesson 1."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from font_paths import resolve_fonts

OUT = Path(__file__).resolve().parent / "assets"
OUT.mkdir(parents=True, exist_ok=True)
FONTS = resolve_fonts()

TEAL = (28, 110, 120)
TEAL_LIGHT = (214, 236, 238)
CORAL = (196, 98, 78)
CORAL_LIGHT = (252, 232, 224)
SAND = (245, 240, 232)
INK = (35, 42, 48)
MUTED = (90, 100, 108)
WHITE = (255, 255, 255)
GOLD = (196, 155, 78)


def font(size: int, bold: bool = False):
    path = FONTS["bold"] if bold else FONTS["regular"]
    return ImageFont.truetype(str(path), size)


def rounded_rect(draw, xy, radius, fill, outline=None, width=2):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def center_text(draw, box, text, fnt, fill=INK):
    x0, y0, x1, y1 = box
    bbox = draw.textbbox((0, 0), text, font=fnt)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((x0 + x1 - tw) / 2, (y0 + y1 - th) / 2), text, font=fnt, fill=fill)


def multiline_center(draw, cx, cy, lines, fnt, fill=INK, gap=8):
    heights = []
    widths = []
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=fnt)
        widths.append(bbox[2] - bbox[0])
        heights.append(bbox[3] - bbox[1])
    total_h = sum(heights) + gap * (len(lines) - 1)
    y = cy - total_h / 2
    for i, line in enumerate(lines):
        draw.text((cx - widths[i] / 2, y), line, font=fnt, fill=fill)
        y += heights[i] + gap


def arrow(draw, x0, y0, x1, y1, fill=TEAL, width=4):
    draw.line((x0, y0, x1, y1), fill=fill, width=width)
    # arrow head
    import math

    angle = math.atan2(y1 - y0, x1 - x0)
    size = 14
    left = (x1 - size * math.cos(angle - 0.45), y1 - size * math.sin(angle - 0.45))
    right = (x1 - size * math.cos(angle + 0.45), y1 - size * math.sin(angle + 0.45))
    draw.polygon([ (x1, y1), left, right ], fill=fill)


def make_connection_scheme():
    img = Image.new("RGB", (1600, 700), SAND)
    draw = ImageDraw.Draw(img)
    title = font(36, True)
    body = font(28, True)
    small = font(22)

    draw.text((60, 40), "Связь музыки, эмоций, движения и интеллекта", font=title, fill=INK)

    boxes = [
        (80, 220, 360, 420, "Музыка", TEAL_LIGHT, TEAL),
        (430, 220, 710, 420, "Эмоция", CORAL_LIGHT, CORAL),
        (780, 220, 1060, 420, "Движение", TEAL_LIGHT, TEAL),
        (1130, 220, 1510, 420, "Осмысление", CORAL_LIGHT, CORAL),
    ]
    captions = [
        "темп, ритм,\nхарактер",
        "настроение,\nпереживание",
        "жест, шаг,\nпластика",
        "внимание,\nпамять, речь",
    ]
    for (x0, y0, x1, y1, label, fill, outline), cap in zip(boxes, captions):
        rounded_rect(draw, (x0, y0, x1, y1), 28, fill, outline, 4)
        center_text(draw, (x0, y0 + 20, x1, y0 + 90), label, body, outline)
        multiline_center(draw, (x0 + x1) / 2, (y0 + y1) / 2 + 40, cap.split("\n"), small, MUTED)

    for i in range(3):
        x0 = boxes[i][2] + 8
        x1 = boxes[i + 1][0] - 8
        arrow(draw, x0, 320, x1, 320, TEAL, 5)

    rounded_rect(draw, (80, 500, 1510, 640), 20, WHITE, TEAL, 3)
    note = "Для дошкольника путь познания музыки идёт через переживание и телесный отклик"
    center_text(draw, (80, 500, 1510, 640), note, font(26), INK)
    img.save(OUT / "scheme-connection.png")


def make_rhythm_roles():
    img = Image.new("RGB", (1600, 900), SAND)
    draw = ImageDraw.Draw(img)
    title = font(36, True)
    body = font(26, True)
    small = font(22)

    draw.text((60, 40), "Ритм развивает четыре важные сферы", font=title, fill=INK)

    items = [
        ("Координация", "согласованность\nрук, ног, корпуса,\nравновесие", TEAL_LIGHT, TEAL),
        ("Внимание", "устойчивость,\nпереключение,\nреакция на сигнал", CORAL_LIGHT, CORAL),
        ("Память", "последовательность\nдвижений и\nритм-формул", TEAL_LIGHT, TEAL),
        ("Речь", "слоговой ритм,\nдыхание,\nартикуляция", CORAL_LIGHT, CORAL),
    ]
    w = 340
    gap = 40
    start = 70
    for i, (label, text, fill, outline) in enumerate(items):
        x0 = start + i * (w + gap)
        y0 = 160
        x1 = x0 + w
        y1 = 520
        rounded_rect(draw, (x0, y0, x1, y1), 28, fill, outline, 4)
        # circle badge
        cx, cy = (x0 + x1) / 2, y0 + 90
        draw.ellipse((cx - 42, cy - 42, cx + 42, cy + 42), fill=outline)
        center_text(draw, (cx - 42, cy - 42, cx + 42, cy + 42), str(i + 1), font(32, True), WHITE)
        center_text(draw, (x0, y0 + 160, x1, y0 + 220), label, body, outline)
        multiline_center(draw, (x0 + x1) / 2, y0 + 310, text.split("\n"), small, MUTED)

    rounded_rect(draw, (70, 580, 1530, 820), 24, WHITE, TEAL, 3)
    draw.text((110, 620), "Практический вывод", font=body, fill=TEAL)
    lines = [
        "Ритм — универсальный каркас занятия: через него педагог одновременно",
        "тренирует тело, слух, внимание и речевые предпосылки ребёнка.",
    ]
    draw.text((110, 680), lines[0], font=small, fill=INK)
    draw.text((110, 720), lines[1], font=small, fill=INK)
    img.save(OUT / "scheme-rhythm-roles.png")


def make_concepts_compare():
    img = Image.new("RGB", (1600, 1000), SAND)
    draw = ImageDraw.Draw(img)
    title = font(34, True)
    head = font(24, True)
    small = font(20)

    draw.text((60, 36), "Чем отличаются ключевые понятия", font=title, fill=INK)

    rows = [
        ("Ритмика", "Метод / система упражнений", "Освоить музыку через движение", "Ходьба с сменой темпа"),
        ("Музыкально-\nдвигательная\nдеятельность", "Вид детской деятельности", "Целостное муз. развитие", "Игра под музыку"),
        ("Танец", "Художественная форма", "Выразительность, общение", "Хоровод, пляска"),
        ("Хореография", "Искусство постановки", "Композиция и техника*", "Постановка к утреннику"),
    ]
    headers = ["Понятие", "Суть", "Цель в ДОУ", "Пример"]
    col_x = [60, 360, 780, 1180, 1540]
    y = 120
    # header
    rounded_rect(draw, (50, y, 1550, y + 70), 16, TEAL, TEAL, 2)
    for i, h in enumerate(headers):
        draw.text((col_x[i] + 16, y + 20), h, font=head, fill=WHITE)
    y += 90
    for idx, row in enumerate(rows):
        fill = WHITE if idx % 2 == 0 else TEAL_LIGHT
        h = 170
        rounded_rect(draw, (50, y, 1550, y + h), 16, fill, (200, 210, 214), 2)
        for i, cell in enumerate(row):
            lines = cell.split("\n")
            yy = y + 35
            for line in lines:
                draw.text((col_x[i] + 16, yy), line, font=small, fill=INK)
                yy += 28
        y += h + 16

    draw.text((60, 940), "* В детском саду — только элементы хореографии, не профессиональная подготовка", font=font(18), fill=MUTED)
    img.save(OUT / "scheme-concepts.png")


def make_timeline():
    img = Image.new("RGB", (1600, 900), SAND)
    draw = ImageDraw.Draw(img)
    title = font(34, True)
    body = font(22, True)
    small = font(18)

    draw.text((60, 36), "Хронометраж занятия — 90 минут", font=title, fill=INK)

    blocks = [
        (0, 10, "Организационный\nмомент", "10 мин", CORAL),
        (10, 45, "Теоретический\nблок", "35 мин", TEAL),
        (45, 55, "Физ-/музык.\nпауза", "10 мин", GOLD),
        (55, 85, "Практический\nблок", "30 мин", TEAL),
        (85, 90, "Рефлексия и\nитог", "5 мин", CORAL),
    ]
    # timeline bar
    bar_y = 220
    draw.rounded_rectangle((80, bar_y, 1520, bar_y + 50), radius=20, fill=TEAL_LIGHT)
    for start, end, label, dur, color in blocks:
        x0 = 80 + start / 90 * 1440
        x1 = 80 + end / 90 * 1440
        draw.rounded_rectangle((x0 + 4, bar_y + 6, x1 - 4, bar_y + 44), radius=14, fill=color)

    # cards
    positions = [80, 360, 640, 920, 1200]
    for i, ((start, end, label, dur, color), x) in enumerate(zip(blocks, positions)):
        rounded_rect(draw, (x, 340, x + 260, 820), 22, WHITE, color, 4)
        draw.ellipse((x + 95, 370, x + 165, 440), fill=color)
        center_text(draw, (x + 95, 370, x + 165, 440), str(i + 1), font(28, True), WHITE)
        multiline_center(draw, x + 130, 520, label.split("\n"), body, INK)
        center_text(draw, (x, 600, x + 260, 660), dur, font(28, True), color)
        detail = [
            f"{start}–{end} мин",
            "",
        ]
        if i == 0:
            detail.append("приветствие,\nцели, разминка")
        elif i == 1:
            detail.append("5 теоретических\nблоков плана")
        elif i == 2:
            detail.append("движение под\nмузыку")
        elif i == 3:
            detail.append("3 практических\nупражнения")
        else:
            detail.append("выводы и\nдомашнее задание")
        multiline_center(draw, x + 130, 730, "\n".join(detail).split("\n"), small, MUTED)

    img.save(OUT / "scheme-timeline.png")


def make_roles_scheme():
    img = Image.new("RGB", (1600, 850), SAND)
    draw = ImageDraw.Draw(img)
    title = font(34, True)
    body = font(26, True)
    small = font(20)

    draw.text((60, 36), "Задачи специалистов: сотрудничество", font=title, fill=INK)

    # left card
    rounded_rect(draw, (70, 140, 740, 760), 28, TEAL_LIGHT, TEAL, 4)
    center_text(draw, (70, 170, 740, 230), "Музыкальный руководитель", body, TEAL)
    left = [
        "• подбор музыки и репертуара",
        "• формирование восприятия",
        "• развитие чувства ритма",
        "• организация игр и танцев",
        "• контроль качества и безопасности",
        "• консультирование воспитателей",
    ]
    y = 280
    for line in left:
        draw.text((120, y), line, font=small, fill=INK)
        y += 55

    # right card
    rounded_rect(draw, (860, 140, 1530, 760), 28, CORAL_LIGHT, CORAL, 4)
    center_text(draw, (860, 170, 1530, 230), "Воспитатель группы", body, CORAL)
    right = [
        "• поддержка интереса в группе",
        "• закрепление игр и движений",
        "• наблюдение за детьми",
        "• организация пространства",
        "• связь с речью и физкультурой",
        "• эмоциональный комфорт",
    ]
    y = 280
    for line in right:
        draw.text((920, y), line, font=small, fill=INK)
        y += 55

    # center connector
    draw.ellipse((740, 400, 860, 520), fill=WHITE, outline=GOLD, width=4)
    multiline_center(draw, 800, 460, ["общее", "дело"], font(20, True), GOLD)

    img.save(OUT / "scheme-roles.png")


if __name__ == "__main__":
    make_connection_scheme()
    make_rhythm_roles()
    make_concepts_compare()
    make_timeline()
    make_roles_scheme()
    print("Diagrams saved to", OUT)
