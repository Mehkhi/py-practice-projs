"""Shared text utility helpers for UI components.

Provides consistent word-wrapping behavior so panels, tooltips, and overlays
calculate line breaks the same way.
"""

from typing import List

import pygame


def wrap_text(text: str, font: pygame.font.Font, max_width: int) -> List[str]:
    """Wrap ``text`` to fit within ``max_width`` pixels.

    The algorithm is whitespace-aware and tries to keep whole words on the
    same line. If a single word is wider than ``max_width``, it will be placed
    on its own line rather than split.
    """
    if not text:
        return []

    words = text.split()
    lines: List[str] = []
    current_line: List[str] = []

    for word in words:
        test_line = " ".join(current_line + [word])
        if font.size(test_line)[0] <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]

    if current_line:
        lines.append(" ".join(current_line))

    return lines
