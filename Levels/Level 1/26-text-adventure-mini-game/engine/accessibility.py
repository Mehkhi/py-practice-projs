"""Accessibility settings manager for text size, colorblind modes, and UI preferences."""

import json
import os
from typing import Dict, Optional, Tuple, Any

from core.logging_utils import log_warning

# Text size presets (multiplier applied to base font sizes)
TEXT_SIZE_PRESETS = {
    "small": 0.85,
    "normal": 1.0,
    "large": 1.25,
    "extra_large": 1.5,
}

TEXT_SIZE_NAMES = {
    "small": "Small",
    "normal": "Normal",
    "large": "Large",
    "extra_large": "Extra Large",
}

# Colorblind mode color palettes
# Each mode provides alternative colors for key UI elements
COLORBLIND_PALETTES = {
    "none": {
        # Default colors (no modification)
        "hp_high": (0, 255, 0),
        "hp_medium": (255, 200, 0),
        "hp_low": (255, 80, 80),
        "sp_bar": (100, 150, 255),
        "positive": (100, 255, 100),
        "negative": (255, 100, 100),
        "accent": (255, 200, 100),
        "highlight": (60, 70, 110),
        "player_marker": (255, 255, 100),
        "enemy_marker": (255, 100, 100),
        "npc_marker": (200, 100, 255),
        "warp_marker": (100, 200, 255),
    },
    "protanopia": {
        # Red-blind: Replace reds with blues/yellows
        "hp_high": (0, 200, 255),
        "hp_medium": (255, 255, 0),
        "hp_low": (255, 200, 0),
        "sp_bar": (100, 150, 255),
        "positive": (0, 200, 255),
        "negative": (255, 200, 0),
        "accent": (255, 255, 100),
        "highlight": (60, 100, 140),
        "player_marker": (255, 255, 100),
        "enemy_marker": (255, 200, 0),
        "npc_marker": (100, 200, 255),
        "warp_marker": (0, 255, 200),
    },
    "deuteranopia": {
        # Green-blind: Replace greens with blues/yellows
        "hp_high": (0, 200, 255),
        "hp_medium": (255, 255, 0),
        "hp_low": (255, 150, 100),
        "sp_bar": (150, 150, 255),
        "positive": (0, 200, 255),
        "negative": (255, 150, 100),
        "accent": (255, 255, 100),
        "highlight": (80, 80, 140),
        "player_marker": (255, 255, 100),
        "enemy_marker": (255, 150, 100),
        "npc_marker": (150, 150, 255),
        "warp_marker": (0, 255, 200),
    },
    "tritanopia": {
        # Blue-blind: Replace blues with reds/greens
        "hp_high": (0, 255, 100),
        "hp_medium": (255, 200, 0),
        "hp_low": (255, 100, 100),
        "sp_bar": (255, 150, 200),
        "positive": (0, 255, 100),
        "negative": (255, 100, 100),
        "accent": (255, 200, 100),
        "highlight": (100, 80, 80),
        "player_marker": (255, 255, 100),
        "enemy_marker": (255, 100, 100),
        "npc_marker": (255, 150, 200),
        "warp_marker": (0, 255, 150),
    },
    "high_contrast": {
        # High contrast mode for low vision
        "hp_high": (0, 255, 0),
        "hp_medium": (255, 255, 0),
        "hp_low": (255, 0, 0),
        "sp_bar": (0, 150, 255),
        "positive": (0, 255, 0),
        "negative": (255, 0, 0),
        "accent": (255, 255, 0),
        "highlight": (100, 100, 150),
        "player_marker": (255, 255, 0),
        "enemy_marker": (255, 0, 0),
        "npc_marker": (255, 0, 255),
        "warp_marker": (0, 255, 255),
    },
}

COLORBLIND_MODE_NAMES = {
    "none": "Default",
    "protanopia": "Protanopia (Red-Blind)",
    "deuteranopia": "Deuteranopia (Green-Blind)",
    "tritanopia": "Tritanopia (Blue-Blind)",
    "high_contrast": "High Contrast",
}


class AccessibilityManager:
    """
    Manages accessibility settings including text size, colorblind modes,
    and other UI preferences.

    Usage:
        access_mgr = AccessibilityManager()

        # Get scaled font size
        font_size = access_mgr.scale_font_size(24)

        # Get colorblind-adjusted color
        hp_color = access_mgr.get_color("hp_high")
    """

    _instance: Optional["AccessibilityManager"] = None
    _initialized: bool = False

    def __new__(cls, settings_path: Optional[str] = None) -> "AccessibilityManager":
        """Singleton pattern - only one accessibility manager should exist."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, settings_path: Optional[str] = None):
        if self._initialized:
            return
        self._initialized = True

        # Current settings
        self.text_size: str = "normal"
        self.colorblind_mode: str = "none"

        # Path for saving/loading settings (configurable for testing)
        self.settings_path = settings_path or os.path.join("data", "accessibility.json")

        # Load saved settings if they exist
        self.load_settings()

    def get_text_scale(self) -> float:
        """Get the current text size multiplier."""
        return TEXT_SIZE_PRESETS.get(self.text_size, 1.0)

    def scale_font_size(self, base_size: int) -> int:
        """Scale a font size according to current text size setting."""
        scale = self.get_text_scale()
        return max(8, int(base_size * scale))

    def get_color(self, color_key: str) -> Tuple[int, int, int]:
        """Get a color adjusted for the current colorblind mode."""
        palette = COLORBLIND_PALETTES.get(self.colorblind_mode, COLORBLIND_PALETTES["none"])
        return palette.get(color_key, (255, 255, 255))

    def get_palette(self) -> Dict[str, Tuple[int, int, int]]:
        """Get the full color palette for the current colorblind mode."""
        return COLORBLIND_PALETTES.get(self.colorblind_mode, COLORBLIND_PALETTES["none"])

    def set_text_size(self, size: str) -> bool:
        """Set the text size preset."""
        if size in TEXT_SIZE_PRESETS:
            self.text_size = size
            return True
        return False

    def set_colorblind_mode(self, mode: str) -> bool:
        """Set the colorblind mode."""
        if mode in COLORBLIND_PALETTES:
            self.colorblind_mode = mode
            return True
        return False

    def cycle_text_size(self, forward: bool = True) -> str:
        """Cycle through text size presets."""
        sizes = list(TEXT_SIZE_PRESETS.keys())
        current_idx = sizes.index(self.text_size) if self.text_size in sizes else 1
        if forward:
            new_idx = (current_idx + 1) % len(sizes)
        else:
            new_idx = (current_idx - 1) % len(sizes)
        self.text_size = sizes[new_idx]
        return self.text_size

    def cycle_colorblind_mode(self, forward: bool = True) -> str:
        """Cycle through colorblind modes."""
        modes = list(COLORBLIND_PALETTES.keys())
        current_idx = modes.index(self.colorblind_mode) if self.colorblind_mode in modes else 0
        if forward:
            new_idx = (current_idx + 1) % len(modes)
        else:
            new_idx = (current_idx - 1) % len(modes)
        self.colorblind_mode = modes[new_idx]
        return self.colorblind_mode

    def get_text_size_name(self) -> str:
        """Get human-readable name for current text size."""
        return TEXT_SIZE_NAMES.get(self.text_size, "Normal")

    def get_colorblind_mode_name(self) -> str:
        """Get human-readable name for current colorblind mode."""
        return COLORBLIND_MODE_NAMES.get(self.colorblind_mode, "Default")

    def get_all_text_sizes(self) -> list:
        """Get list of all text size options."""
        return list(TEXT_SIZE_PRESETS.keys())

    def get_all_colorblind_modes(self) -> list:
        """Get list of all colorblind mode options."""
        return list(COLORBLIND_PALETTES.keys())

    def save_settings(self) -> bool:
        """Save current settings to file."""
        try:
            os.makedirs(os.path.dirname(self.settings_path), exist_ok=True)
            settings = {
                "text_size": self.text_size,
                "colorblind_mode": self.colorblind_mode,
            }
            with open(self.settings_path, 'w') as f:
                json.dump(settings, f, indent=2)
            return True
        except Exception as e:
            log_warning(f"Failed to save accessibility settings to {self.settings_path}: {e}")
            return False

    def load_settings(self) -> bool:
        """Load settings from file."""
        if not os.path.exists(self.settings_path):
            return False
        try:
            with open(self.settings_path, 'r') as f:
                settings = json.load(f)
            if "text_size" in settings and settings["text_size"] in TEXT_SIZE_PRESETS:
                self.text_size = settings["text_size"]
            if "colorblind_mode" in settings and settings["colorblind_mode"] in COLORBLIND_PALETTES:
                self.colorblind_mode = settings["colorblind_mode"]
            return True
        except Exception as e:
            log_warning(f"Failed to load accessibility settings from {self.settings_path}: {e}")
            return False

    def to_dict(self) -> Dict[str, Any]:
        """Export settings as a dictionary."""
        return {
            "text_size": self.text_size,
            "colorblind_mode": self.colorblind_mode,
        }

    def from_dict(self, data: Dict[str, Any]) -> None:
        """Import settings from a dictionary."""
        if "text_size" in data:
            self.set_text_size(data["text_size"])
        if "colorblind_mode" in data:
            self.set_colorblind_mode(data["colorblind_mode"])


def get_accessibility_manager() -> AccessibilityManager:
    """Get the singleton AccessibilityManager instance."""
    return AccessibilityManager()
