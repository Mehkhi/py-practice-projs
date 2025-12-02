
from dataclasses import dataclass
from typing import Dict, Tuple, Optional

@dataclass
class Theme:
    """Theme configuration for Tetris visuals."""
    name: str
    bg: Tuple[int, int, int]
    grid: Tuple[int, int, int]
    text: Tuple[int, int, int]
    ghost: Tuple[int, int, int]
    piece_colors: Dict[str, Tuple[int, int, int]]
    block_border_radius: int
    block_outline_color: Optional[Tuple[int, int, int]]
    block_outline_width: int
    block_gradient: bool
    block_shadow: bool
    panel_bg: Optional[Tuple[int, int, int]] = None
    ghost_dotted: bool = False  # Use dotted outline for ghost instead of solid

# Theme definitions
THEMES: Dict[str, Theme] = {
    "NES": Theme(
        name="NES",
        bg=(0, 0, 0),
        grid=(40, 40, 40),
        text=(255, 255, 255),
        ghost=(100, 100, 100),
        piece_colors={
            "I": (0, 255, 255),      # cyan - bright
            "O": (255, 255, 0),      # yellow - bright
            "T": (160, 0, 255),      # purple - bright
            "S": (0, 255, 0),        # green - bright
            "Z": (255, 0, 0),        # red - bright
            "J": (0, 0, 255),        # blue - bright
            "L": (255, 160, 0),      # orange - bright
        },
        block_border_radius=0,       # Classic square blocks
        block_outline_color=None,
        block_outline_width=0,
        block_gradient=False,
        block_shadow=False,
        panel_bg=None,
        ghost_dotted=False,
    ),
    "Modern": Theme(
        name="Modern",
        bg=(30, 30, 35),
        grid=(60, 60, 65),
        text=(240, 240, 245),
        ghost=(100, 100, 110),
        piece_colors={
            "I": (64, 224, 208),     # turquoise - soft
            "O": (255, 215, 0),      # gold - soft
            "T": (186, 85, 211),     # medium orchid - soft
            "S": (50, 205, 50),      # lime green - soft
            "Z": (255, 99, 71),      # tomato - soft
            "J": (70, 130, 180),     # steel blue - soft
            "L": (255, 165, 0),      # orange - soft
        },
        block_border_radius=4,       # Rounded corners
        block_outline_color=(50, 50, 55),
        block_outline_width=1,
        block_gradient=True,
        block_shadow=True,
        panel_bg=(25, 25, 30),
        ghost_dotted=False,
    ),
    "Neon": Theme(
        name="Neon",
        bg=(10, 5, 20),
        grid=(40, 20, 50),
        text=(255, 200, 255),
        ghost=(80, 40, 100),
        piece_colors={
            "I": (0, 255, 255),      # cyan - glowing
            "O": (255, 255, 0),      # yellow - glowing
            "T": (255, 0, 255),      # magenta - glowing
            "S": (0, 255, 128),      # green-cyan - glowing
            "Z": (255, 64, 64),      # red - glowing
            "J": (64, 128, 255),     # blue - glowing
            "L": (255, 128, 0),      # orange - glowing
        },
        block_border_radius=2,
        block_outline_color=(255, 255, 255),
        block_outline_width=1,
        block_gradient=True,
        block_shadow=True,
        panel_bg=(15, 10, 25),
        ghost_dotted=True,
    ),
    "Minimal": Theme(
        name="Minimal",
        bg=(255, 255, 255),
        grid=(220, 220, 220),
        text=(20, 20, 20),
        ghost=(180, 180, 180),
        piece_colors={
            "I": (0, 150, 200),      # cyan - muted
            "O": (200, 150, 0),      # yellow - muted
            "T": (150, 0, 200),      # purple - muted
            "S": (0, 150, 0),        # green - muted
            "Z": (200, 0, 0),        # red - muted
            "J": (0, 0, 200),        # blue - muted
            "L": (200, 100, 0),      # orange - muted
        },
        block_border_radius=1,
        block_outline_color=(0, 0, 0),
        block_outline_width=2,
        block_gradient=False,
        block_shadow=False,
        panel_bg=None,
        ghost_dotted=True,
    ),
}

# Theme manager
_current_theme_name: str = "Modern"

def get_theme() -> Theme:
    """Get the currently active theme."""
    return THEMES[_current_theme_name]

def set_theme(name: str) -> bool:
    """Set the active theme by name. Returns True if successful, False if theme not found."""
    global _current_theme_name
    if name in THEMES:
        _current_theme_name = name
        return True
    return False

def cycle_theme(direction: int = 1) -> Theme:
    """Cycle to the next/previous theme. Returns the new active theme."""
    global _current_theme_name
    theme_names = list(THEMES.keys())
    current_index = theme_names.index(_current_theme_name)
    new_index = (current_index + direction) % len(theme_names)
    _current_theme_name = theme_names[new_index]
    return THEMES[_current_theme_name]

def list_themes() -> list[str]:
    """Return a list of all available theme names."""
    return list(THEMES.keys())

def get_theme_name() -> str:
    """Get the name of the currently active theme."""
    return _current_theme_name
