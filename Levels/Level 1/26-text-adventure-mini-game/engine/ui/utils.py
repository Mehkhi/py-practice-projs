"""Shared UI utility functions."""

import pygame

from ..theme import Colors, Layout


def draw_rounded_panel(
    surface: pygame.Surface,
    rect: pygame.Rect,
    bg_color: tuple,
    border_color: tuple,
    border_width: int = Layout.BORDER_WIDTH_THIN,
    radius: int = Layout.CORNER_RADIUS_SMALL
) -> None:
    """Draw a rounded panel with background and border."""
    # Draw background
    panel_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(panel_surf, bg_color, panel_surf.get_rect(), border_radius=radius)
    surface.blit(panel_surf, rect.topleft)
    # Draw border
    pygame.draw.rect(surface, border_color, rect, border_width, border_radius=radius)
