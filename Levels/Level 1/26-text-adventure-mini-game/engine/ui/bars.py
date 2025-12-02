"""HP/SP bars and status icon drawing functions."""

from typing import Optional, Sequence, Tuple

import pygame

from ..theme import Colors, Fonts, Layout


def draw_hp_bar(surface: pygame.Surface, x: int, y: int, width: int, height: int,
                 current: int, maximum: int, label: str = "", font: Optional[pygame.font.Font] = None,
                 show_text: bool = True) -> None:
    """Draw a simple, clean HP bar without borders."""
    height = height or Layout.BAR_HEIGHT

    bg_rect = pygame.Rect(x, y, width, height)

    # Dark background for the empty part of the bar
    pygame.draw.rect(surface, (40, 40, 40), bg_rect, border_radius=Layout.BAR_BORDER_RADIUS)

    if maximum > 0:
        hp_ratio = max(0.0, min(1.0, current / maximum))
        hp_width = int(width * hp_ratio)

        if hp_width > 0:
            hp_rect = pygame.Rect(x, y, hp_width, height)

            # Use accessibility-aware color
            color = Colors.get_hp_color(hp_ratio)

            # Draw main fill
            pygame.draw.rect(surface, color, hp_rect, border_radius=Layout.BAR_BORDER_RADIUS)

    # Draw label
    if label and show_text:
        label_font = font or pygame.font.Font(None, Fonts.SIZE_SMALL)
        label_text = f"{label}: {current}/{maximum}"

        # Shadow
        text_shadow = label_font.render(label_text, True, Colors.BLACK, None)
        surface.blit(text_shadow, (x + 1, y - 14))

        # Main text
        text = label_font.render(label_text, True, Colors.TEXT_PRIMARY, None)
        surface.blit(text, (x, y - 15))


def draw_sp_bar(surface: pygame.Surface, x: int, y: int, width: int, height: int,
                current: int, maximum: int, label: str = "", font: Optional[pygame.font.Font] = None,
                show_text: bool = True) -> None:
    """Draw a simple, clean SP bar without borders."""
    height = height or Layout.BAR_HEIGHT

    bg_rect = pygame.Rect(x, y, width, height)

    # Background
    pygame.draw.rect(surface, (40, 40, 40), bg_rect, border_radius=Layout.BAR_BORDER_RADIUS)

    if maximum > 0:
        sp_ratio = max(0.0, min(1.0, current / maximum))
        sp_width = int(width * sp_ratio)

        if sp_width > 0:
            sp_rect = pygame.Rect(x, y, sp_width, height)

            # Use accessibility-aware color
            sp_color = Colors.get_sp_color()
            pygame.draw.rect(surface, sp_color, sp_rect, border_radius=Layout.BAR_BORDER_RADIUS)

    # Draw label
    if label and show_text:
        label_font = font or pygame.font.Font(None, Fonts.SIZE_SMALL)
        label_text = f"{label}: {current}/{maximum}"

        # Shadow
        text_shadow = label_font.render(label_text, True, Colors.BLACK, None)
        surface.blit(text_shadow, (x + 1, y - 14))

        # Main text
        text = label_font.render(label_text, True, Colors.TEXT_PRIMARY, None)
        surface.blit(text, (x, y - 15))


def draw_status_icons(
    surface: pygame.Surface,
    icons: Sequence[pygame.Surface],
    position: Tuple[int, int],
    spacing: int = Layout.ICON_GAP
) -> None:
    """Draw a row of status icons with consistent spacing."""
    x, y = position
    for icon in icons:
        surface.blit(icon, (x, y))
        x += icon.get_width() + spacing


def draw_help_text(
    surface: pygame.Surface,
    text: str,
    font: pygame.font.Font,
    margin_bottom: int = Layout.SCREEN_MARGIN,
    color: Tuple[int, int, int] = Colors.TEXT_SECONDARY,
) -> None:
    """Draw centered help text at the bottom of the screen."""
    width, height = surface.get_size()
    help_surface = font.render(text, True, color)
    help_rect = help_surface.get_rect(center=(width // 2, height - margin_bottom))
    surface.blit(help_surface, help_rect)


def draw_contextual_help(
    surface: pygame.Surface,
    text: str,
    font: pygame.font.Font,
    margin_bottom: int = Layout.SCREEN_MARGIN,
    text_color: Tuple[int, int, int] = Colors.TEXT_SECONDARY,
    bg_alpha: int = Layout.OVERLAY_ALPHA,
    padding_h: int = Layout.PADDING_MD,
    padding_v: int = Layout.PADDING_SM,
) -> None:
    """
    Draw contextual help text at the bottom of the screen with a semi-transparent background.

    This provides a consistent style for help/hint text across all menu scenes.

    Args:
        surface: The pygame surface to draw on.
        text: The help text to display.
        font: The font to use for rendering.
        margin_bottom: Distance from the bottom of the screen.
        text_color: Color of the help text.
        bg_alpha: Alpha value for the background (0-255).
        padding_h: Horizontal padding around the text.
        padding_v: Vertical padding around the text.
    """
    width, height = surface.get_size()

    # Render the text
    help_surface = font.render(text, True, text_color)
    text_width, text_height = help_surface.get_size()

    # Calculate background dimensions
    bg_width = text_width + padding_h * 2
    bg_height = text_height + padding_v * 2
    bg_x = (width - bg_width) // 2
    bg_y = height - margin_bottom - bg_height // 2

    # Draw semi-transparent background
    bg_surface = pygame.Surface((bg_width, bg_height), pygame.SRCALPHA)
    bg_surface.fill((*Colors.BG_DARK[:3], bg_alpha))
    pygame.draw.rect(
        bg_surface,
        Colors.BORDER,
        (0, 0, bg_width, bg_height),
        width=Layout.BORDER_WIDTH_THIN,
        border_radius=Layout.CORNER_RADIUS_SMALL,
    )
    surface.blit(bg_surface, (bg_x, bg_y))

    # Draw the text centered on the background
    text_x = bg_x + padding_h
    text_y = bg_y + padding_v
    surface.blit(help_surface, (text_x, text_y))


def draw_section_header(
    surface: pygame.Surface,
    text: str,
    x: int,
    y: int,
    font: pygame.font.Font,
    color: Tuple[int, int, int] = Colors.TEXT_PRIMARY,
    underline: bool = True,
    underline_width: int = 0,
) -> int:
    """Draw a section header with optional underline. Returns the y position after the header."""
    # Draw header text with shadow
    shadow = font.render(text, True, Colors.BG_DARK)
    surface.blit(shadow, (x + 1, y + 1))
    header = font.render(text, True, color)
    surface.blit(header, (x, y))

    new_y = y + font.get_linesize() + Layout.ELEMENT_GAP_SMALL

    if underline:
        line_width = underline_width or font.size(text)[0]
        line_y = y + font.get_linesize() + 2
        pygame.draw.line(surface, Colors.BORDER, (x, line_y), (x + line_width, line_y), 1)
        new_y += 4

    return new_y
