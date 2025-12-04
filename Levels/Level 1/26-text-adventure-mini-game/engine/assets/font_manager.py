"""Font management for loading and caching fonts."""

import os
from typing import Dict, Optional, Tuple

import pygame

from core.logging_utils import log_warning, log_error, log_debug


class FontManager:
    """Manages loading and caching of fonts."""

    def __init__(self, assets_dir: str = "assets"):
        self.assets_dir = assets_dir
        self.fonts: Dict[str, pygame.font.Font] = {}
        self.font_variants: Dict[Tuple[str, int], pygame.font.Font] = {}
        self.font_base_sizes: Dict[str, int] = {}
        self._load_fonts()

    def _load_fonts(self) -> None:
        """Load default and bundled fonts.

        Handles headless test environments by checking pygame.font initialization
        and attempting to initialize it if needed. Fonts are created lazily in
        get_font() if initialization fails here.
        """
        # Ensure pygame.font is initialized before creating fonts
        if not pygame.font.get_init():
            try:
                pygame.font.init()
            except Exception as e:
                log_warning(f"Failed to initialize pygame.font: {e}. Fonts will be created lazily on first use.")
                return  # Exit early, fonts will be created in get_font() when needed

        # Try to load system monospace fonts first
        try:
            # Preferred font stack
            font_choices = ["Consolas", "Menlo", "Courier New", "Courier", "monospace"]
            font_path = None

            # Iterate to find the first available system font path
            for name in font_choices:
                font_path = pygame.font.match_font(name)
                if font_path:
                    log_debug(f"Found system font match: {name} -> {font_path}")
                    break

            if font_path:
                sys_font = pygame.font.Font(font_path, 24)
                sys_font_small = pygame.font.Font(font_path, 16)
                sys_font_large = pygame.font.Font(font_path, 32)
            else:
                # Fallback to SysFont with the comma-separated string
                # (SysFont handles comma-separated strings better than match_font)
                font_names_str = ",".join(font_choices)
                sys_font = pygame.font.SysFont(font_names_str, 24)
                sys_font_small = pygame.font.SysFont(font_names_str, 16)
                sys_font_large = pygame.font.SysFont(font_names_str, 32)
                log_debug(f"Loaded system font via SysFont fallback: {font_names_str}")

            self.fonts["default"] = sys_font
            self.fonts["small"] = sys_font_small
            self.fonts["large"] = sys_font_large
            self.font_base_sizes["default"] = 24
            self.font_base_sizes["small"] = 16
            self.font_base_sizes["large"] = 32
        except (pygame.error, OSError, Exception) as e:
            log_warning(f"Failed to load system fonts: {e}. Will use fallback.")
            # Fallback to default pygame fonts
            try:
                self.fonts["default"] = pygame.font.Font(None, 24)
                self.fonts["small"] = pygame.font.Font(None, 16)
                self.fonts["large"] = pygame.font.Font(None, 32)
                self.font_base_sizes["default"] = 24
                self.font_base_sizes["small"] = 16
                self.font_base_sizes["large"] = 32
            except Exception:
                log_warning("Unable to create default font during initialization. Will attempt lazy creation on first use.")

        # Load bundled fonts from assets/fonts directory
        fonts_dir = os.path.join(self.assets_dir, "fonts")
        if os.path.exists(fonts_dir):
            for filename in os.listdir(fonts_dir):
                if not filename.lower().endswith((".ttf", ".otf")):
                    continue
                font_id = os.path.splitext(filename)[0]
                try:
                    path = os.path.join(fonts_dir, filename)
                    # Use default sizes; callers can request resized copies
                    self.fonts[font_id] = pygame.font.Font(path, 24)
                    self.font_base_sizes[font_id] = 24
                    log_debug(f"Loaded bundled font: {font_id} from {filename}")
                except (pygame.error, OSError, FileNotFoundError) as e:
                    log_warning(f"Failed to load bundled font {filename}: {e}")
                except Exception as e:
                    log_warning(f"Unexpected error loading font {filename}: {e}")

    def get_font(self, font_name: str = "default", size: Optional[int] = None, apply_accessibility: bool = True) -> Optional[pygame.font.Font]:
        """
        Get a font by name with optional override size.
        Always returns a valid font, falling back to pygame default if needed.

        Args:
            font_name: Name of the font to retrieve
            size: Optional size override
            apply_accessibility: If True, applies accessibility text scaling
        """
        access_mgr = None
        if apply_accessibility:
            try:
                from ..accessibility import get_accessibility_manager
                access_mgr = get_accessibility_manager()
            except ImportError:
                access_mgr = None

        # Apply accessibility scaling if enabled and size is specified
        if access_mgr and size:
            size = access_mgr.scale_font_size(size)

        base_font = self.fonts.get(font_name) or self.fonts.get("default")

        # If no base font found, try to create a fallback (lazy initialization)
        if not base_font:
            if not pygame.font.get_init():
                try:
                    pygame.font.init()
                except Exception as e:
                    log_error(f"Failed to initialize pygame.font for fallback: {e}")
                    return None

            log_warning(f"Font '{font_name}' not found, using pygame default fallback")
            try:
                base_font = pygame.font.Font(None, size or 24)
                if "default" not in self.fonts:
                    self.fonts["default"] = base_font
                    self.font_base_sizes.setdefault("default", size or 24)
                self.font_base_sizes.setdefault(font_name, size or 24)
            except Exception as e:
                log_error(f"Failed to create fallback font: {e}")
                return None

        # If size override requested, create or reuse a cached variant
        if base_font and size:
            return self._create_font_variant(font_name, base_font, size)

        # If no size is provided, still respect accessibility scaling using the base size
        if access_mgr and not size:
            base_size = self.font_base_sizes.get(font_name) or self.font_base_sizes.get("default")
            if base_size:
                scaled_size = access_mgr.scale_font_size(base_size)
                if scaled_size != base_size:
                    return self._create_font_variant(font_name, base_font, scaled_size)

        return base_font

    def _create_font_variant(self, font_name: str, base_font: pygame.font.Font, size: int) -> Optional[pygame.font.Font]:
        """Create or return a cached font variant at a given size."""
        cache_key = (font_name, size)
        if cache_key in self.font_variants:
            return self.font_variants[cache_key]
        try:
            if not pygame.font.get_init():
                pygame.font.init()

            font_path = getattr(base_font, "name", None)
            if font_path:
                variant = pygame.font.Font(font_path, size)
            else:
                variant = pygame.font.Font(None, size)
            self.font_variants[cache_key] = variant
            return variant
        except (pygame.error, OSError) as e:
            log_warning(f"Failed to create font size {size} from {font_name}: {e}. Using base font.")
            try:
                if not pygame.font.get_init():
                    pygame.font.init()
                fallback = pygame.font.Font(None, size)
                log_debug(f"Using pygame default fallback at size {size}")
                self.font_variants[cache_key] = fallback
                return fallback
            except Exception:
                return base_font
        except Exception as e:
            log_warning(f"Unexpected error creating font size {size}: {e}. Using base font.")
            return base_font
