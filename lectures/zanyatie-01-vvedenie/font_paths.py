#!/usr/bin/env python3
"""Resolve Cyrillic-capable fonts across common Linux/macOS locations."""

from __future__ import annotations

import os
from pathlib import Path

CANDIDATES = {
    "regular": [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/TTF/DejaVuSans.ttf",
        "/usr/local/share/fonts/DejaVuSans.ttf",
        "/Library/Fonts/DejaVuSans.ttf",
        str(Path.home() / ".fonts" / "DejaVuSans.ttf"),
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
    ],
    "bold": [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
        "/usr/local/share/fonts/DejaVuSans-Bold.ttf",
        "/Library/Fonts/DejaVuSans-Bold.ttf",
        str(Path.home() / ".fonts" / "DejaVuSans-Bold.ttf"),
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
    ],
    "italic": [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf",
        "/usr/share/fonts/TTF/DejaVuSans-Oblique.ttf",
        "/usr/local/share/fonts/DejaVuSans-Oblique.ttf",
        "/Library/Fonts/DejaVuSans-Oblique.ttf",
        str(Path.home() / ".fonts" / "DejaVuSans-Oblique.ttf"),
        "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf",
        "/usr/share/fonts/truetype/noto/NotoSans-Italic.ttf",
    ],
    "bold_italic": [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf",
        "/usr/share/fonts/TTF/DejaVuSans-BoldOblique.ttf",
        "/usr/local/share/fonts/DejaVuSans-BoldOblique.ttf",
        "/Library/Fonts/DejaVuSans-BoldOblique.ttf",
        str(Path.home() / ".fonts" / "DejaVuSans-BoldOblique.ttf"),
        "/usr/share/fonts/truetype/liberation/LiberationSans-BoldItalic.ttf",
        "/usr/share/fonts/truetype/noto/NotoSans-BoldItalic.ttf",
    ],
}


def _first_existing(paths: list[str]) -> Path:
    for raw in paths:
        path = Path(os.path.expandvars(raw)).expanduser()
        if path.is_file():
            return path
    searched = "\n  - ".join(paths)
    raise FileNotFoundError(
        "Не найден шрифт с поддержкой кириллицы. Установите пакет fonts-dejavu "
        "(Debian/Ubuntu: `sudo apt install fonts-dejavu`) или положите TTF DejaVu "
        f"в один из путей:\n  - {searched}"
    )


def resolve_fonts() -> dict[str, Path]:
    return {kind: _first_existing(paths) for kind, paths in CANDIDATES.items()}
