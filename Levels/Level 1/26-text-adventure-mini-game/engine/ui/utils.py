"""Shared UI utility functions."""

from typing import Optional, TYPE_CHECKING

import pygame

from ..theme import Colors, Layout

if TYPE_CHECKING:
    from ..theme import PanelStyle
    from .nine_slice import NineSlicePanel


def draw_rounded_panel(
    surface: pygame.Surface,
    rect: pygame.Rect,
    bg_color: tuple,
    border_color: tuple,
    border_width: int = Layout.BORDER_WIDTH_THIN,
    radius: int = Layout.CORNER_RADIUS_SMALL
) -> None:
    """Draw a rounded panel with background and border.

    Note: This function delegates to draw_themed_panel for consistency.
    Consider using draw_themed_panel directly with style presets.
    """
    from ..theme import PanelStyle
    # Extract alpha if 4-tuple, else default
    alpha = bg_color[3] if len(bg_color) == 4 else 220
    style = PanelStyle(
        bg=bg_color[:3],
        border=border_color[:3] if len(border_color) >= 3 else border_color,
        radius=radius,
        border_width=border_width,
        alpha=alpha,
    )
    draw_themed_panel(surface, rect, style, panel=None)


def draw_themed_panel(
    surface: pygame.Surface,
    rect: pygame.Rect,
    style: Optional["PanelStyle"] = None,
    panel: Optional["NineSlicePanel"] = None,
    border_overlay: Optional[bool] = None,
) -> None:
    """
    Draw a panel using NineSlice if provided, else rounded rect fallback.

    This is the preferred method for drawing UI panels. It uses the NineSlice
    textured panel when available, and falls back to a styled rounded rect
    when no panel asset is present.

    Args:
        surface: Target surface to draw on
        rect: Rectangle defining panel bounds
        style: PanelStyle preset (defaults to PANEL_DEFAULT)
        panel: Optional NineSlicePanel for textured rendering
        border_overlay: If True, draw style's border over NineSlice panel.
                        If None (default), auto-enable for non-PANEL_DEFAULT styles
                        with a valid panel (enables highlight/overlay effects).
    """
    from ..theme import PANEL_DEFAULT
    style = style or PANEL_DEFAULT

    if panel is not None and panel.source is not None:
        # Use textured NineSlice panel
        panel.draw(surface, rect)

        # Auto-apply border overlay for non-default styles (highlight, overlay, etc.)
        # unless explicitly disabled with border_overlay=False
        should_overlay = border_overlay if border_overlay is not None else (style is not PANEL_DEFAULT)
        if should_overlay:
            pygame.draw.rect(
                surface,
                style.border,
                rect,
                style.border_width,
                border_radius=style.radius,
            )
    else:
        # Fallback to rounded rect with style
        panel_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        bg_color = (*style.bg[:3], style.alpha)
        pygame.draw.rect(
            panel_surf,
            bg_color,
            panel_surf.get_rect(),
            border_radius=style.radius,
        )
        surface.blit(panel_surf, rect.topleft)
        pygame.draw.rect(
            surface,
            style.border,
            rect,
            style.border_width,
            border_radius=style.radius,
        )
