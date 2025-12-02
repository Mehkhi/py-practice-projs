
import pygame
from typing import Tuple, List, Optional
from ..config import CELL_SIZE, MARGIN, COLUMNS, ROWS, PANEL_WIDTH
from .theme import get_theme

def _to_px(x: int, y: int) -> Tuple[int, int]:
    return (MARGIN + x * CELL_SIZE, MARGIN + y * CELL_SIZE)

def _draw_block(screen: pygame.Surface, x: int, y: int, color: Tuple[int, int, int], theme, inset_px: int = 0) -> None:
    """Draw a single block with theme styling (rounded corners, outlines, gradients, shadows)."""
    base_rect = pygame.Rect(*_to_px(x, y), CELL_SIZE - 1, CELL_SIZE - 1)
    # Apply inset for animations
    if inset_px > 0:
        base_rect.inflate_ip(-inset_px * 2, -inset_px * 2)
        base_rect.x += inset_px
        base_rect.y += inset_px

    # Draw shadow first if enabled
    if theme.block_shadow:
        shadow_rect = base_rect.copy()
        shadow_rect.x += 2
        shadow_rect.y += 2
        shadow_color = tuple(max(0, c - 40) for c in color)
        pygame.draw.rect(screen, shadow_color, shadow_rect, border_radius=theme.block_border_radius)

    # Draw gradient if enabled
    if theme.block_gradient:
        # Create a surface for the gradient with alpha channel
        grad_surface = pygame.Surface((base_rect.width, base_rect.height), pygame.SRCALPHA)
        # Simple vertical gradient: lighter at top, darker at bottom
        lighter = tuple(min(255, c + 30) for c in color)
        darker = tuple(max(0, c - 30) for c in color)
        for i in range(base_rect.height):
            ratio = i / max(1, base_rect.height - 1)
            r = int(lighter[0] * (1 - ratio) + darker[0] * ratio)
            g = int(lighter[1] * (1 - ratio) + darker[1] * ratio)
            b = int(lighter[2] * (1 - ratio) + darker[2] * ratio)
            pygame.draw.line(grad_surface, (r, g, b), (0, i), (base_rect.width, i))

        # Create mask surface with rounded rectangle to respect border_radius
        if theme.block_border_radius > 0:
            mask_surface = pygame.Surface((base_rect.width, base_rect.height), pygame.SRCALPHA)
            mask_surface.fill((0, 0, 0, 0))  # Transparent black
            # Draw white filled rounded rectangle on mask
            pygame.draw.rect(mask_surface, (255, 255, 255, 255),
                           (0, 0, base_rect.width, base_rect.height),
                           border_radius=theme.block_border_radius)
            # Apply mask to gradient using alpha multiplication
            grad_surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        screen.blit(grad_surface, base_rect)
    else:
        # Draw solid color
        pygame.draw.rect(screen, color, base_rect, border_radius=theme.block_border_radius)

    # Draw outline if enabled
    if theme.block_outline_width > 0 and theme.block_outline_color:
        pygame.draw.rect(screen, theme.block_outline_color, base_rect,
                        width=theme.block_outline_width, border_radius=theme.block_border_radius)

def _draw_ghost_dotted(screen: pygame.Surface, x: int, y: int, color: Tuple[int, int, int]) -> None:
    """Draw a dotted outline for ghost piece."""
    rect = pygame.Rect(*_to_px(x, y), CELL_SIZE - 1, CELL_SIZE - 1)
    # Draw dotted border by drawing small rectangles at corners and edges
    dot_size = 3
    # Top edge
    for i in range(0, rect.width, dot_size * 2):
        pygame.draw.rect(screen, color, (rect.x + i, rect.y, dot_size, 2))
    # Bottom edge
    for i in range(0, rect.width, dot_size * 2):
        pygame.draw.rect(screen, color, (rect.x + i, rect.y + rect.height - 2, dot_size, 2))
    # Left edge
    for i in range(0, rect.height, dot_size * 2):
        pygame.draw.rect(screen, color, (rect.x, rect.y + i, 2, dot_size))
    # Right edge
    for i in range(0, rect.height, dot_size * 2):
        pygame.draw.rect(screen, color, (rect.x + rect.width - 2, rect.y + i, 2, dot_size))

def draw_background(screen: pygame.Surface, line_clear_flash: bool = False) -> None:
    theme = get_theme()
    screen.fill(theme.bg)

    # Optional background pattern per theme
    from .theme import get_theme_name
    theme_name = get_theme_name()
    if theme_name == "Neon":
        # Draw subtle diagonal lines for Neon theme
        pattern_color = tuple(min(255, c + 10) for c in theme.bg)
        for i in range(-ROWS * CELL_SIZE, COLUMNS * CELL_SIZE + ROWS * CELL_SIZE, 20):
            start_x = MARGIN + i
            start_y = MARGIN
            end_x = MARGIN + i + ROWS * CELL_SIZE
            end_y = MARGIN + ROWS * CELL_SIZE
            if end_x > MARGIN and start_x < MARGIN + COLUMNS * CELL_SIZE:
                pygame.draw.line(screen, pattern_color,
                                (max(MARGIN, start_x), max(MARGIN, start_y)),
                                (min(MARGIN + COLUMNS * CELL_SIZE, end_x), min(MARGIN + ROWS * CELL_SIZE, end_y)), 1)

    # Flash grid color on line clear
    grid_color = theme.grid
    if line_clear_flash:
        # Brighten grid lines for flash effect
        grid_color = tuple(min(255, c + 100) for c in theme.grid)
    # grid
    for x in range(COLUMNS + 1):
        px, _ = _to_px(x, 0)
        pygame.draw.line(screen, grid_color, (px, MARGIN), (px, MARGIN + ROWS * CELL_SIZE))
    for y in range(ROWS + 1):
        _, py = _to_px(0, y)
        pygame.draw.line(screen, grid_color, (MARGIN, py), (MARGIN + COLUMNS * CELL_SIZE, py))

def draw_locked(screen: pygame.Surface, grid: List[List[Optional[str]]], lock_alpha: int = 0) -> None:
    theme = get_theme()
    for y, row in enumerate(grid):
        for x, cell in enumerate(row):
            if cell:
                color = theme.piece_colors[cell]
                # Apply lock animation darkening if active
                if lock_alpha > 0:
                    # Darken color by blending with black
                    color = tuple(max(0, c - lock_alpha // 3) for c in color)
                _draw_block(screen, x, y, color, theme)

def draw_piece(screen: pygame.Surface, kind: str, cells: List[Tuple[int,int]], pos: Tuple[int,int], ghost_distance: int = 0, inset_px: int = 0) -> None:
    theme = get_theme()
    px, py = pos
    # ghost
    if ghost_distance > 0:
        for (cx, cy) in cells:
            gx = px + cx
            gy = py + cy + ghost_distance
            if gy >= 0:
                if theme.ghost_dotted:
                    # Draw dotted outline for ghost
                    _draw_ghost_dotted(screen, gx, gy, theme.ghost)
                else:
                    rect = pygame.Rect(*_to_px(gx, gy), CELL_SIZE - 1, CELL_SIZE - 1)
                    pygame.draw.rect(screen, theme.ghost, rect, width=1)
    # actual piece
    for (cx, cy) in cells:
        x = px + cx
        y = py + cy
        if y >= 0:
            _draw_block(screen, x, y, theme.piece_colors[kind], theme, inset_px=inset_px)

def draw_panel(screen: pygame.Surface, font: pygame.font.Font, score: int, level: int, lines: int, next_kind: str) -> None:
    from .theme import get_theme_name
    theme = get_theme()
    # panel origin at right of board
    panel_x = MARGIN + COLUMNS * CELL_SIZE + 20
    panel_y = MARGIN

    # Draw panel background if theme has one
    if theme.panel_bg:
        panel_bg_rect = pygame.Rect(panel_x - 10, panel_y - 10, PANEL_WIDTH * CELL_SIZE + 20, ROWS * CELL_SIZE + 20)
        pygame.draw.rect(screen, theme.panel_bg, panel_bg_rect)
        # Add subtle border
        pygame.draw.rect(screen, theme.grid, panel_bg_rect, width=1)

    title = font.render("TETRIS", True, theme.text)
    screen.blit(title, (panel_x, panel_y))

    y = panel_y + 40
    for label, value in [("Score", score), ("Level", level), ("Lines", lines)]:
        text = font.render(f"{label}: {value}", True, theme.text)
        screen.blit(text, (panel_x, y))
        y += 30

    # Add theme name display
    y += 10
    theme_name_text = font.render(f"Theme: {get_theme_name()}", True, theme.text)
    screen.blit(theme_name_text, (panel_x, y))
    y += 30

    y += 10
    screen.blit(font.render("Next:", True, theme.text), (panel_x, y))
    y += 10

    # Improved 4x4 preview box with better styling
    preview_rect = pygame.Rect(panel_x, y, CELL_SIZE * 4, CELL_SIZE * 4)
    # Draw preview box background
    preview_bg = theme.panel_bg if theme.panel_bg else theme.bg
    pygame.draw.rect(screen, preview_bg, preview_rect)
    # Draw preview box border
    pygame.draw.rect(screen, theme.grid, preview_rect, width=2)

    # draw a centered preview using a rough set of preview positions
    from ..core.piece import SHAPES
    cells = SHAPES[next_kind][0]
    # center to 4x4 box
    # offset (1,1) looks decent for most shapes
    for (cx, cy) in cells:
        rx = preview_rect.x + (cx) * CELL_SIZE + 5
        ry = preview_rect.y + (cy) * CELL_SIZE + 5
        preview_block_rect = pygame.Rect(rx, ry, CELL_SIZE - 10, CELL_SIZE - 10)
        # Draw preview block with theme styling
        color = theme.piece_colors[next_kind]
        # Draw shadow if enabled
        if theme.block_shadow:
            shadow_rect = preview_block_rect.copy()
            shadow_rect.x += 1
            shadow_rect.y += 1
            shadow_color = tuple(max(0, c - 40) for c in color)
            pygame.draw.rect(screen, shadow_color, shadow_rect, border_radius=theme.block_border_radius)
        # Draw gradient or solid
        if theme.block_gradient:
            # Create a surface for the gradient with alpha channel
            grad_surface = pygame.Surface((preview_block_rect.width, preview_block_rect.height), pygame.SRCALPHA)
            lighter = tuple(min(255, c + 30) for c in color)
            darker = tuple(max(0, c - 30) for c in color)
            for i in range(preview_block_rect.height):
                ratio = i / max(1, preview_block_rect.height - 1)
                r = int(lighter[0] * (1 - ratio) + darker[0] * ratio)
                g = int(lighter[1] * (1 - ratio) + darker[1] * ratio)
                b = int(lighter[2] * (1 - ratio) + darker[2] * ratio)
                pygame.draw.line(grad_surface, (r, g, b), (0, i), (preview_block_rect.width, i))

            # Create mask surface with rounded rectangle to respect border_radius
            if theme.block_border_radius > 0:
                mask_surface = pygame.Surface((preview_block_rect.width, preview_block_rect.height), pygame.SRCALPHA)
                mask_surface.fill((0, 0, 0, 0))  # Transparent black
                # Draw white filled rounded rectangle on mask
                pygame.draw.rect(mask_surface, (255, 255, 255, 255),
                               (0, 0, preview_block_rect.width, preview_block_rect.height),
                               border_radius=theme.block_border_radius)
                # Apply mask to gradient using alpha multiplication
                grad_surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

            screen.blit(grad_surface, preview_block_rect)
        else:
            pygame.draw.rect(screen, color, preview_block_rect, border_radius=theme.block_border_radius)
        # Draw outline if enabled
        if theme.block_outline_width > 0 and theme.block_outline_color:
            pygame.draw.rect(screen, theme.block_outline_color, preview_block_rect,
                            width=theme.block_outline_width, border_radius=theme.block_border_radius)
