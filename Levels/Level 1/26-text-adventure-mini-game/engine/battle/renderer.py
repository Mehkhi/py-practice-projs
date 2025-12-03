"""Battle scene rendering logic.

This module contains rendering logic for battle scenes, including
HUD elements, sprites, menus, and visual effects.
"""

import math
import random
from typing import Dict, List, Optional, Tuple, TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from core.combat import BattleState


# Weather tint colors (RGBA)
WEATHER_TINTS = {
    "rain": (100, 100, 150, 40),
    "storm": (80, 80, 100, 60),
    "fog": (200, 200, 200, 50),
    "snow": (220, 220, 240, 30),
    "clear": (0, 0, 0, 0),
}

# Biome gradient colors
BIOME_GRADIENTS = {
    "forest": ((20, 40, 20), (40, 60, 40)),
    "cave": ((15, 15, 20), (30, 30, 40)),
    "desert": ((60, 50, 30), (80, 70, 50)),
    "mountain": ((40, 45, 50), (60, 65, 70)),
    "swamp": ((25, 35, 25), (40, 50, 40)),
    "ocean": ((20, 30, 50), (40, 50, 70)),
    "ruins": ((30, 25, 35), (50, 45, 55)),
    "castle": ((25, 25, 30), (45, 45, 50)),
}


class BattleRendererMixin:
    """Mixin providing rendering logic for BattleScene.

    This mixin handles:
    - Background rendering with biome/weather effects
    - Enemy and ally sprite drawing
    - HUD elements (HP/SP bars, status icons)
    - Menu rendering
    - Flash effects and damage numbers
    - AI debug overlay

    Attributes expected from host class:
        battle_system: BattleSystem instance
        assets: AssetManager for sprites
        sprite_size, draw_size: Sprite dimensions
        player: Player entity
        world: World for weather/biome data
        message_box, main_menu, etc.: UI components
        panel: NineSlice panel for UI backgrounds
    """

    def _draw_damage_numbers(self, surface: pygame.Surface) -> None:
        """Draw floating damage numbers."""
        font = self.assets.get_font("small")
        for popup in self.damage_numbers:
            alpha = min(255, int(popup["timer"] * 255))
            text = popup["text"]
            color = popup["color"]

            text_surf = font.render(text, True, color)
            if alpha < 255:
                text_surf.set_alpha(alpha)

            offset_x, offset_y = getattr(self, "screen_shake_offset", (0, 0))
            x = int(popup["x"] + offset_x)
            y = int(popup["y"] + offset_y)
            outline_color = (0, 0, 0)
            for ox, oy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                outline_surf = font.render(text, True, outline_color)
                if alpha < 255:
                    outline_surf.set_alpha(alpha)
                surface.blit(outline_surf, (x + ox, y + oy))
            surface.blit(text_surf, (x, y))

    def _draw_combo_flash(self, surface: pygame.Surface) -> None:
        """Draw combo attack flash effect."""
        if self.combo_flash <= 0:
            return

        alpha = int(self.combo_flash * 100)
        flash_surf = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        flash_surf.fill((255, 200, 100, alpha))
        surface.blit(flash_surf, (0, 0))

        if self.combo_flash > 0.35:
            font = self.assets.get_font()
            text = "COMBO!"
            text_surf = font.render(text, True, (255, 255, 0))
            text_rect = text_surf.get_rect(center=(surface.get_width() // 2, 100))

            outline_surf = font.render(text, True, (0, 0, 0))
            for ox, oy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
                surface.blit(outline_surf, text_rect.move(ox, oy))
            surface.blit(text_surf, text_rect)

    def _draw_coordinated_tactic_flash(self, surface: pygame.Surface) -> None:
        """Draw coordinated tactic flash effect."""
        if self.coordinated_tactic_flash <= 0:
            return

        alpha = int(self.coordinated_tactic_flash * 80)
        flash_surf = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        flash_surf.fill((100, 150, 255, alpha))
        surface.blit(flash_surf, (0, 0))

        if self.coordinated_tactic_flash > 0.35:
            font = self.assets.get_font()
            text = "COORDINATED ATTACK!"
            text_surf = font.render(text, True, (150, 200, 255))
            text_rect = text_surf.get_rect(center=(surface.get_width() // 2, 100))

            outline_surf = font.render(text, True, (0, 0, 0))
            for ox, oy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
                surface.blit(outline_surf, text_rect.move(ox, oy))
            surface.blit(text_surf, text_rect)

    def _draw_phase_transition_flash(self, surface: pygame.Surface) -> None:
        """Draw phase transition flash effect."""
        if self.phase_transition_flash <= 0:
            return

        alpha = int(self.phase_transition_flash * 80)
        flash_surf = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        flash_surf.fill((255, 150, 100, alpha))
        surface.blit(flash_surf, (0, 0))

        if self.phase_transition_flash > 0.35:
            font = self.assets.get_font()
            text = "PHASE SHIFT!"
            text_surf = font.render(text, True, (255, 200, 100))
            text_rect = text_surf.get_rect(center=(surface.get_width() // 2, 100))

            outline_surf = font.render(text, True, (0, 0, 0))
            for ox, oy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
                surface.blit(outline_surf, text_rect.move(ox, oy))
            surface.blit(text_surf, text_rect)

    def _draw_ai_debug_overlay(self, surface: pygame.Surface, font) -> None:
        """Draw AI debug overlay showing adaptation level and learned patterns."""
        from engine.theme import Colors

        if not self.show_ai_debug or not self.battle_system.learning_ai:
            return

        learning_ai = self.battle_system.learning_ai
        overlay_x = 10
        overlay_y = 10
        overlay_width = 300
        overlay_height = 150

        panel_surf = pygame.Surface((overlay_width, overlay_height), pygame.SRCALPHA)
        panel_surf.fill((20, 20, 30, 220))
        surface.blit(panel_surf, (overlay_x, overlay_y))

        border_rect = pygame.Rect(overlay_x, overlay_y, overlay_width, overlay_height)
        pygame.draw.rect(surface, Colors.ACCENT, border_rect, 2)

        title_text = "AI Adaptation Debug"
        title_surf = font.render(title_text, True, Colors.ACCENT)
        surface.blit(title_surf, (overlay_x + 10, overlay_y + 5))

        level_text = f"Adaptation Level: {learning_ai.adaptation_level}"
        level_surf = font.render(level_text, True, Colors.TEXT_PRIMARY)
        surface.blit(level_surf, (overlay_x + 10, overlay_y + 25))

        summary = learning_ai.get_adaptation_summary()
        if summary:
            words = summary.split()
            lines = []
            current_line = ""
            for word in words:
                test_line = current_line + (" " if current_line else "") + word
                if font.size(test_line)[0] < overlay_width - 20:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)

            y_offset = 45
            for line in lines[:4]:
                line_surf = font.render(line, True, Colors.TEXT_SECONDARY)
                surface.blit(line_surf, (overlay_x + 10, overlay_y + y_offset))
                y_offset += 18

        hint_text = "Press 'L' to toggle"
        hint_surf = font.render(hint_text, True, Colors.TEXT_SECONDARY)
        surface.blit(hint_surf, (overlay_x + 10, overlay_y + overlay_height - 20))

    def _draw_ai_notification(self, surface: pygame.Surface, font) -> None:
        """Draw temporary notification when AI learns a new pattern."""
        from .animations import AI_NOTIFICATION_DURATION

        if not self.ai_pattern_notification or self.ai_notification_timer <= 0:
            return

        alpha = min(255, int(self.ai_notification_timer * 255 / AI_NOTIFICATION_DURATION))

        notification_text = f"[AI] {self.ai_pattern_notification}"
        text_surf = font.render(notification_text, True, (150, 200, 255))
        text_rect = text_surf.get_rect(center=(surface.get_width() // 2, 30))

        panel_width = text_rect.width + 20
        panel_height = text_rect.height + 10
        panel_x = text_rect.centerx - panel_width // 2
        panel_y = text_rect.centery - panel_height // 2

        panel_surf = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_surf.fill((20, 30, 50, alpha))
        surface.blit(panel_surf, (panel_x, panel_y))

        outline_surf = font.render(notification_text, True, (0, 0, 0))
        for ox, oy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            surface.blit(outline_surf, text_rect.move(ox, oy))

        if alpha < 255:
            text_surf.set_alpha(alpha)
        surface.blit(text_surf, text_rect)

    def _draw_target_cursor(self, surface: pygame.Surface, x: int = 0, y: int = 0) -> None:
        """Draw a target cursor at the given position."""
        from engine.theme import Colors

        color = Colors.ACCENT
        offset = int(math.sin(pygame.time.get_ticks() / 150) * 5)

        points = [
            (x, y - 20 + offset),
            (x - 10, y - 35 + offset),
            (x + 10, y - 35 + offset)
        ]
        pygame.draw.polygon(surface, color, points)
        pygame.draw.polygon(surface, Colors.BLACK, points, 2)
