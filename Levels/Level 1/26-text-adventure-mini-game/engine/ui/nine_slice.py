"""Nine-slice panel renderer component."""

from typing import Optional

import pygame

from ..theme import Colors, Layout


class NineSlicePanel:
    """
    9-slice panel renderer for pixel-art UI framing.
    Can use a source image or fallback to procedural drawing.
    """

    def __init__(self, source: Optional[pygame.Surface] = None):
        self.source = source
        if source:
            w, h = source.get_size()
            self.cell_w = w // 3
            self.cell_h = h // 3
        else:
            self.cell_w = 8
            self.cell_h = 8

    def draw(self, surface: pygame.Surface, dest_rect: pygame.Rect) -> None:
        if not self.source:
            # Fallback procedural drawing with semi-transparent style
            panel_surface = pygame.Surface((dest_rect.width, dest_rect.height), pygame.SRCALPHA)
            bg_color = (*Colors.BG_PANEL[:3], 220)
            pygame.draw.rect(panel_surface, bg_color, (0, 0, dest_rect.width, dest_rect.height), border_radius=Layout.CORNER_RADIUS)

            # Inner bevel (darker)
            inner_rect = pygame.Rect(2, 2, dest_rect.width - 4, dest_rect.height - 4)
            inner_color = (*Colors.BG_DARK[:3], 200)
            pygame.draw.rect(panel_surface, inner_color, inner_rect, 1, border_radius=Layout.CORNER_RADIUS)

            # Outer border
            border_color = (*Colors.BORDER[:3], 220)
            pygame.draw.rect(panel_surface, border_color, (0, 0, dest_rect.width, dest_rect.height), Layout.BORDER_WIDTH, border_radius=Layout.CORNER_RADIUS)
            surface.blit(panel_surface, dest_rect.topleft)
            return

        sw, sh = self.cell_w, self.cell_h
        sx = [0, sw, sw * 2]
        sy = [0, sh, sh * 2]

        dx = [dest_rect.left, dest_rect.left + sw, dest_rect.right - sw]
        dy = [dest_rect.top, dest_rect.top + sh, dest_rect.bottom - sh]

        for j in range(3):
            for i in range(3):
                src = pygame.Rect(sx[i], sy[j], sw, sh)
                if i == 1:
                    dw = max(0, dest_rect.width - 2 * sw)
                else:
                    dw = sw
                if j == 1:
                    dh = max(0, dest_rect.height - 2 * sh)
                else:
                    dh = sh

                dst = pygame.Rect(dx[i], dy[j], dw, dh)
                if dw <= 0 or dh <= 0:
                    continue

                tile = pygame.transform.scale(self.source.subsurface(src), (int(dw), int(dh)))
                surface.blit(tile, dst)
