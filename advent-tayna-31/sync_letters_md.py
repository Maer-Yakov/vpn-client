#!/usr/bin/env python3
"""Regenerate LETTERS.md from canonical letters_data.json."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "letters_data.json"
OUT = ROOT / "LETTERS.md"

STYLE_RU = {
    "khokhloma": "хохлома",
    "gzhel": "гжель",
    "palekh": "палех",
}


def main() -> None:
    letters = json.loads(DATA.read_text(encoding="utf-8"))
    lines = [
        "# Тексты писем 1–31 (карточки)",
        "",
        "Канонический источник копирайта: `letters_data.json`.",
        "Этот файл генерируется командой `python3 sync_letters_md.py`.",
        "",
        "Стиль рамки: нечётные — хохлома, чётные — гжель; 31 — палех.",
        "",
    ]
    for letter in letters:
        style = STYLE_RU[letter["style"]]
        lines.append(f"## {letter['n']} декабря — {letter['title']} ({style})")
        lines.append(letter["greeting"])
        lines.append(letter["body"])
        lines.append(f"★ Задание: {letter['task']}")
        lines.append(f"Подсказка для родителей: {letter['tip']}")
        lines.append("")
    OUT.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
