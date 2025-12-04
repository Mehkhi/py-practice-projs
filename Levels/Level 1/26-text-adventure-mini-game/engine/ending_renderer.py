"""Ending scene rendering and visual effects.

This module handles all drawing and visual effects for ending scenes,
including backgrounds, particles, text rendering, and UI elements.
"""

import math
import random
from typing import Dict, List, Optional, Tuple

import pygame

from .assets import AssetManager


class EndingRenderer:
    """Handles all rendering for ending scenes.

    Manages:
    - Theme-based gradient backgrounds
    - Particle system rendering
    - Text rendering with effects
    - Menu UI rendering
    - Visual effects and animations
    """

    # Color palettes for each ending type
    ENDING_THEMES = {
        "good": {
            "bg_top": (20, 45, 80),
            "bg_bottom": (60, 100, 140),
            "accent": (255, 220, 100),
            "text": (255, 255, 240),
            "particle_colors": [(255, 230, 150), (200, 220, 255), (255, 200, 100)],
        },
        "bad": {
            "bg_top": (40, 10, 15),
            "bg_bottom": (80, 25, 35),
            "accent": (200, 50, 50),
            "text": (255, 200, 200),
            "particle_colors": [(200, 50, 50), (150, 30, 30), (100, 20, 20)],
        },
        "neutral": {
            "bg_top": (30, 35, 50),
            "bg_bottom": (60, 70, 90),
            "accent": (180, 180, 200),
            "text": (220, 220, 230),
            "particle_colors": [(180, 180, 200), (150, 160, 180), (200, 200, 220)],
        },
    }

    def __init__(
        self,
        ending_id: str,
        assets: Optional[AssetManager] = None,
        screen_width: int = 800,
        screen_height: int = 600,
    ):
        """Initialize the ending renderer.

        Args:
            ending_id: Type of ending (good, bad, neutral)
            assets: Asset manager for fonts
            screen_width: Screen width for rendering
            screen_height: Screen height for rendering
        """
        self.ending_id = ending_id
        self.assets = assets or AssetManager()
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Get theme colors
        self.theme = self.ENDING_THEMES.get(ending_id, self.ENDING_THEMES["neutral"])

        # Pre-render surfaces
        self._gradient_surface: Optional[pygame.Surface] = None

    def draw_gradient_background(self, surface: pygame.Surface) -> None:
        """Draw a smooth vertical gradient background based on ending theme.

        Args:
            surface: Surface to draw on
        """
        width, height = surface.get_size()

        if (self._gradient_surface is None or
            self._gradient_surface.get_size() != (width, height)):
            self._gradient_surface = pygame.Surface((width, height))
            top = self.theme["bg_top"]
            bottom = self.theme["bg_bottom"]
            for y in range(height):
                ratio = y / height
                ratio = ratio * ratio * (3 - 2 * ratio)  # Smoothstep
                r = int(top[0] + (bottom[0] - top[0]) * ratio)
                g = int(top[1] + (bottom[1] - top[1]) * ratio)
                b = int(top[2] + (bottom[2] - top[2]) * ratio)
                pygame.draw.line(self._gradient_surface, (r, g, b), (0, y), (width, y))

        surface.blit(self._gradient_surface, (0, 0))

    def draw_particles(
        self,
        surface: pygame.Surface,
        particles: List[dict],
        total_timer: float
    ) -> None:
        """Draw floating ambient particles.

        Args:
            surface: Surface to draw on
            particles: List of particle dictionaries
            total_timer: Total time for animation effects
        """
        width, height = surface.get_size()
        for p in particles:
            x, y = int(p["x"]), int(p["y"])
            if 0 <= x < width and 0 <= y < height:
                size = int(p["size"])
                twinkle = 0.5 + 0.5 * math.sin(total_timer * 2 + p["phase_offset"])
                alpha = int(p["alpha"] * twinkle)
                color = (*p["color"], max(20, min(255, alpha)))

                particle_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(particle_surf, color, (size, size), size)
                surface.blit(particle_surf, (x - size, y - size))

    def draw_title_section(
        self,
        surface: pygame.Surface,
        ending_data: Optional[Dict],
        total_timer: float
    ) -> int:
        """Draw the ending title with effects.

        Args:
            surface: Surface to draw on
            ending_data: Ending data dictionary
            total_timer: Total time for animation effects

        Returns:
            Y coordinate after drawing (for layout)
        """
        if ending_data:
            title = ending_data.get("title", "The End")
        else:
            title = "The End"

        center_x = surface.get_width() // 2
        y = 30

        # Get font
        font_large = self.assets.get_font("large", 36) or pygame.font.Font(None, 36)

        # Animated title with glow
        glow_intensity = 0.7 + 0.3 * math.sin(total_timer * 2)
        accent = self.theme["accent"]
        glow_color = (
            int(accent[0] * glow_intensity),
            int(accent[1] * glow_intensity),
            int(accent[2] * glow_intensity)
        )

        # Shadow
        shadow = font_large.render(title, True, (20, 20, 30))
        surface.blit(shadow, (center_x - shadow.get_width() // 2 + 2, y + 2))

        # Glow
        for offset in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            glow = font_large.render(title, True, glow_color)
            surface.blit(glow, (center_x - glow.get_width() // 2 + offset[0], y + offset[1]))

        # Main title
        main = font_large.render(title, True, self.theme["text"])
        surface.blit(main, (center_x - main.get_width() // 2, y))

        return y + 50

    def draw_blurb_section(
        self,
        surface: pygame.Surface,
        ending_data: Optional[Dict],
        start_y: int
    ) -> int:
        """Draw the ending blurb with word wrap.

        Args:
            surface: Surface to draw on
            ending_data: Ending data dictionary
            start_y: Starting Y coordinate

        Returns:
            Y coordinate after drawing (for layout)
        """
        if ending_data:
            blurb = ending_data.get("blurb", "")
        else:
            blurb = "Your journey has reached its conclusion."

        center_x = surface.get_width() // 2
        y = start_y

        # Get font
        font = self.assets.get_font("default", 22) or pygame.font.Font(None, 22)

        # Word wrap
        words = blurb.split()
        lines = []
        current_line = []
        max_width = 500

        for word in words:
            test_line = " ".join(current_line + [word])
            test_surface = font.render(test_line, True, (255, 255, 255))
            if test_surface.get_width() <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]
        if current_line:
            lines.append(" ".join(current_line))

        for line in lines:
            line_surf = font.render(line, True, self.theme["text"])
            surface.blit(line_surf, (center_x - line_surf.get_width() // 2, y))
            y += 24

        return y + 20

    def draw_stats_section(
        self,
        surface: pygame.Surface,
        stats: List[Tuple[str, str]],
        start_y: int
    ) -> int:
        """Draw game statistics.

        Args:
            surface: Surface to draw on
            stats: List of (label, value) tuples
            start_y: Starting Y coordinate

        Returns:
            Y coordinate after drawing (for layout)
        """
        center_x = surface.get_width() // 2
        y = start_y

        # Get fonts
        font = self.assets.get_font("default", 22) or pygame.font.Font(None, 22)
        small_font = self.assets.get_font("small", 16) or pygame.font.Font(None, 16)

        # Section title
        title = font.render("Journey Statistics", True, self.theme["accent"])
        surface.blit(title, (center_x - title.get_width() // 2, y))
        y += 30

        for label, value in stats:
            stat_text = f"{label}: {value}"
            stat_surf = small_font.render(stat_text, True, self.theme["text"])
            surface.blit(stat_surf, (center_x - stat_surf.get_width() // 2, y))
            y += 20

        return y + 15

    def draw_credits_section(
        self,
        surface: pygame.Surface,
        ending_data: Optional[Dict],
        start_y: int
    ) -> int:
        """Draw credits.

        Args:
            surface: Surface to draw on
            ending_data: Ending data dictionary
            start_y: Starting Y coordinate

        Returns:
            Y coordinate after drawing (for layout)
        """
        if ending_data:
            credits_text = ending_data.get("credits", "Thank you for playing!")
        else:
            credits_text = "Thank you for playing!"

        center_x = surface.get_width() // 2
        y = start_y

        # Get font
        small_font = self.assets.get_font("small", 16) or pygame.font.Font(None, 16)

        credits_surf = small_font.render(credits_text, True, (180, 180, 180))
        surface.blit(credits_surf, (center_x - credits_surf.get_width() // 2, y))

        return y + 30

    def draw_ng_plus_menu(
        self,
        surface: pygame.Surface,
        menu_options: List[str],
        selected_option: int,
        total_timer: float,
        cycle_info: str = ""
    ) -> None:
        """Draw the New Game+ menu.

        Args:
            surface: Surface to draw on
            menu_options: List of menu option strings
            selected_option: Currently selected option index
            total_timer: Total time for animation effects
            cycle_info: Optional NG+ cycle information
        """
        center_x = surface.get_width() // 2
        y = surface.get_height() - 100

        # Get fonts
        font = self.assets.get_font("default", 22) or pygame.font.Font(None, 22)
        small_font = self.assets.get_font("small", 16) or pygame.font.Font(None, 16)

        # Menu background
        menu_width, menu_height = 250, 100
        menu_rect = pygame.Rect(center_x - menu_width // 2, y, menu_width, menu_height)

        bg_surf = pygame.Surface((menu_width, menu_height), pygame.SRCALPHA)
        pygame.draw.rect(bg_surf, (20, 25, 40, 200), (0, 0, menu_width, menu_height), border_radius=8)
        pygame.draw.rect(bg_surf, (*self.theme["accent"], 150), (0, 0, menu_width, menu_height), width=2, border_radius=8)
        surface.blit(bg_surf, menu_rect.topleft)

        # Menu title
        title = small_font.render("What would you like to do?", True, self.theme["text"])
        surface.blit(title, (center_x - title.get_width() // 2, y + 10))

        # Menu options
        for i, option in enumerate(menu_options):
            option_y = y + 35 + i * 28
            is_selected = i == selected_option

            if is_selected:
                # Highlight
                highlight_rect = pygame.Rect(center_x - 100, option_y - 2, 200, 24)
                pygame.draw.rect(surface, (*self.theme["accent"][:3], 80), highlight_rect, border_radius=4)

                # Cursor
                cursor_x = center_x - 90 + 3 * math.sin(total_timer * 5)
                pygame.draw.polygon(surface, self.theme["accent"], [
                    (cursor_x, option_y + 4),
                    (cursor_x + 8, option_y + 10),
                    (cursor_x, option_y + 16),
                ])

            color = self.theme["accent"] if is_selected else self.theme["text"]
            option_surf = font.render(option, True, color)
            surface.blit(option_surf, (center_x - option_surf.get_width() // 2, option_y))

        # NG+ info
        if cycle_info:
            info = small_font.render(f"Current {cycle_info}", True, (150, 150, 150))
            surface.blit(info, (center_x - info.get_width() // 2, y + menu_height + 5))

    def draw_skip_hint(
        self,
        surface: pygame.Surface,
        total_timer: float
    ) -> None:
        """Draw skip hint during cutscene.

        Args:
            surface: Surface to draw on
            total_timer: Total time for animation effects
        """
        small_font = self.assets.get_font("small", 16) or pygame.font.Font(None, 16)
        center_x = surface.get_width() // 2
        height = surface.get_height()

        alpha = int(120 * (0.5 + 0.5 * math.sin(total_timer * 3)))
        hint_surf = small_font.render("Press SPACE to continue, ESC to skip", True, (150, 150, 150))
        hint_surf.set_alpha(alpha)
        surface.blit(hint_surf, (center_x - hint_surf.get_width() // 2, height - 30))

    def draw_fade_overlay(
        self,
        surface: pygame.Surface,
        fade_alpha: int
    ) -> None:
        """Draw fade overlay effect.

        Args:
            surface: Surface to draw on
            fade_alpha: Alpha value for fade (0-255)
        """
        if fade_alpha > 0:
            width, height = surface.get_size()
            fade_surf = pygame.Surface((width, height))
            fade_surf.fill((0, 0, 0))
            fade_surf.set_alpha(fade_alpha)
            surface.blit(fade_surf, (0, 0))
