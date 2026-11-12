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
        # macOS system fallbacks with Cyrillic
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/Library/Fonts/Arial Unicode.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Helvetica.ttc",
        "/System/Library/Fonts/Helvetica.ttc",
    ],
    "bold": [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
        "/usr/local/share/fonts/DejaVuSans-Bold.ttf",
        "/Library/Fonts/DejaVuSans-Bold.ttf",
        str(Path.home() / ".fonts" / "DejaVuSans-Bold.ttf"),
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/Library/Fonts/Arial Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial.ttf",
    ],
    "italic": [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf",
        "/usr/share/fonts/TTF/DejaVuSans-Oblique.ttf",
        "/usr/local/share/fonts/DejaVuSans-Oblique.ttf",
        "/Library/Fonts/DejaVuSans-Oblique.ttf",
        str(Path.home() / ".fonts" / "DejaVuSans-Oblique.ttf"),
        "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf",
        "/usr/share/fonts/truetype/noto/NotoSans-Italic.ttf",
        "/System/Library/Fonts/Supplemental/Arial Italic.ttf",
        "/Library/Fonts/Arial Italic.ttf",
    ],
    "bold_italic": [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf",
        "/usr/share/fonts/TTF/DejaVuSans-BoldOblique.ttf",
        "/usr/local/share/fonts/DejaVuSans-BoldOblique.ttf",
        "/Library/Fonts/DejaVuSans-BoldOblique.ttf",
        str(Path.home() / ".fonts" / "DejaVuSans-BoldOblique.ttf"),
        "/usr/share/fonts/truetype/liberation/LiberationSans-BoldItalic.ttf",
        "/usr/share/fonts/truetype/noto/NotoSans-BoldItalic.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold Italic.ttf",
        "/Library/Fonts/Arial Bold Italic.ttf",
    ],
}


def _first_existing(paths: list[str]) -> Path | None:
    for raw in paths:
        path = Path(os.path.expandvars(raw)).expanduser()
        if path.is_file():
            return path
    return None


def resolve_fonts(required: tuple[str, ...] = ("regular", "bold")) -> dict[str, Path]:
    """Resolve font files. Only ``required`` variants must exist; others are optional."""
    found: dict[str, Path] = {}
    missing_required: list[str] = []
    for kind, paths in CANDIDATES.items():
        path = _first_existing(paths)
        if path is not None:
            found[kind] = path
        elif kind in required:
            missing_required.append(kind)

    if missing_required:
        searched = []
        for kind in missing_required:
            searched.extend(CANDIDATES[kind][:5])
        hint = "\n  - ".join(searched)
        raise FileNotFoundError(
            "Не найдены обязательные шрифты с кириллицей: "
            + ", ".join(missing_required)
            + ". Установите fonts-dejavu (Debian/Ubuntu: `sudo apt install fonts-dejavu`) "
            "или положите TTF DejaVu / Arial Unicode в один из путей:\n  - "
            + hint
        )
    return found
