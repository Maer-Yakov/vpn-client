#!/usr/bin/env python3
"""Regenerate LETTERS.md from canonical letters_data.json."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "letters_data.json"
OUT = ROOT / "LETTERS.md"


def main() -> None:
    letters = json.loads(DATA.read_text(encoding="utf-8"))
    lines = [
        "# Тексты писем 1–31",
        "",
        "Канон: `letters_data.json` (из PDF «31 красочных писем» + чеклист 29.10.2026).",
        "Подпись: Дедушка Мороз и Искорка. Без заданий на самостоятельное письмо/чтение.",
        "",
        "Стили рамок (цикл прикладного искусства): хохлома, гжель, дымковская,",
        "городецкая, жостово, палех, мезенская, филимоновская.",
        "",
    ]
    for letter in letters:
        lines.append(
            f"## {letter['n']} декабря — {letter['title']} ({letter['style_ru']})"
        )
        lines.append(letter["greeting"])
        lines.append(letter["from"])
        lines.append(letter["story"])
        lines.append(f"★ Задание: {letter['task']}")
        if letter.get("teaser"):
            lines.append(letter["teaser"])
        lines.append(f"Родителям: {letter['tip']}")
        lines.append(letter["signature"])
        lines.append("")
    OUT.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
