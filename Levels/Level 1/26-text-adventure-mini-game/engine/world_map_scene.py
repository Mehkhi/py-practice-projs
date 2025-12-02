"""Scene for viewing an overview of visited and unvisited maps."""

import math
from typing import Dict, List, Optional, Tuple, TYPE_CHECKING

import pygame

from .base_menu_scene import BaseMenuScene
from .theme import Colors, Fonts, Layout
from core.world import World, get_map_graph

if TYPE_CHECKING:
    from .scene import SceneManager


class WorldMapScene(BaseMenuScene):
    """Visualize the world map graph and visited progress."""

    def __init__(
        self,
        manager: Optional["SceneManager"],
        world: World,
        assets: Optional["AssetManager"] = None,
        scale: int = 2,
    ):
        super().__init__(manager, assets, scale)
        self.world = world
        self.graph = get_map_graph(world)
        self.map_ids = sorted(self.graph.keys() or list(world.maps.keys()))
        self.selected_index = 0
        if self.world.current_map_id in self.map_ids:
            self.selected_index = self.map_ids.index(self.world.current_map_id)
        self.node_positions: Dict[str, Tuple[int, int]] = {}

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_ESCAPE:
            self.manager.pop()
        elif event.key in (pygame.K_RIGHT, pygame.K_DOWN):
            self._move_selection(1)
        elif event.key in (pygame.K_LEFT, pygame.K_UP):
            self._move_selection(-1)

    def _move_selection(self, delta: int) -> None:
        if not self.map_ids:
            return
        self.selected_index = (self.selected_index + delta) % len(self.map_ids)

    def draw(self, surface: pygame.Surface) -> None:
        self.draw_overlay(surface)
        width, height = surface.get_size()
        panel_rect = pygame.Rect(
            Layout.SCREEN_MARGIN,
            Layout.SCREEN_MARGIN,
            width - Layout.SCREEN_MARGIN * 2,
            height - Layout.SCREEN_MARGIN * 2,
        )
        self._draw_panel(surface, panel_rect)

        if not self.map_ids:
            empty_font = self.assets.get_font(Fonts.DEFAULT, Fonts.SIZE_BODY)
            message = empty_font.render("No maps available.", True, Colors.TEXT_SECONDARY)
            surface.blit(message, message.get_rect(center=panel_rect.center))
            return

        self.node_positions = self._compute_node_positions(panel_rect)
        title_font = self.assets.get_font(Fonts.DEFAULT, Fonts.SIZE_HEADING)
        small_font = self.assets.get_font(Fonts.SMALL, Fonts.SIZE_SMALL)

        title = title_font.render("World Map", True, Colors.TEXT_PRIMARY)
        surface.blit(title, (panel_rect.left + Layout.PADDING_LG, panel_rect.top + Layout.PADDING_LG))

        self._draw_connections(surface)
        self._draw_nodes(surface)
        self._draw_info_panel(surface, panel_rect, small_font)
        self._draw_help_text(surface, small_font)

    def _draw_panel(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        if self.panel:
            self.panel.draw(surface, rect)
        else:
            pygame.draw.rect(surface, Colors.BG_PANEL, rect, border_radius=Layout.CORNER_RADIUS)
            pygame.draw.rect(surface, Colors.BORDER, rect, Layout.BORDER_WIDTH, border_radius=Layout.CORNER_RADIUS)

    def _compute_node_positions(self, panel_rect: pygame.Rect) -> Dict[str, Tuple[int, int]]:
        """Compute circular positions for each map."""
        positions: Dict[str, Tuple[int, int]] = {}
        center_x = panel_rect.centerx
        center_y = panel_rect.centery + 20
        radius = min(panel_rect.width, panel_rect.height) // 3
        total = max(1, len(self.map_ids))

        for idx, map_id in enumerate(self.map_ids):
            angle = (2 * math.pi * idx) / total
            x = center_x + int(radius * math.cos(angle))
            y = center_y + int(radius * math.sin(angle))
            positions[map_id] = (x, y)
        return positions

    def _draw_connections(self, surface: pygame.Surface) -> None:
        visited = getattr(self.world, "visited_maps", set())
        for source, connections in self.graph.items():
            start = self.node_positions.get(source)
            if not start:
                continue
            for target, _ in connections:
                end = self.node_positions.get(target)
                if not end:
                    continue
                both_visited = source in visited and target in visited
                color = Colors.BORDER_HIGHLIGHT if both_visited else Colors.BORDER
                pygame.draw.line(surface, color, start, end, 2)

    def _draw_nodes(self, surface: pygame.Surface) -> None:
        visited = getattr(self.world, "visited_maps", set())
        current = self.world.current_map_id
        selected_map = self.map_ids[self.selected_index] if self.map_ids else None

        for map_id, position in self.node_positions.items():
            if map_id == current:
                color = Colors.ACCENT
            elif map_id in visited:
                color = Colors.TEXT_SUCCESS
            else:
                color = Colors.TEXT_DISABLED
            pygame.draw.circle(surface, color, position, 10)
            pygame.draw.circle(surface, Colors.BORDER, position, 10, 1)

            if map_id == selected_map:
                pygame.draw.circle(surface, Colors.BORDER_HIGHLIGHT, position, 14, 2)

    def _draw_info_panel(
        self,
        surface: pygame.Surface,
        panel_rect: pygame.Rect,
        font: pygame.font.Font,
    ) -> None:
        """Render details for the selected map."""
        info_rect = pygame.Rect(
            panel_rect.left + Layout.PADDING_LG,
            panel_rect.bottom - 140,
            panel_rect.width - Layout.PADDING_LG * 2,
            110,
        )
        pygame.draw.rect(surface, Colors.BG_DARK, info_rect, border_radius=Layout.CORNER_RADIUS_SMALL)
        pygame.draw.rect(surface, Colors.BORDER, info_rect, Layout.BORDER_WIDTH_THIN, border_radius=Layout.CORNER_RADIUS_SMALL)

        if not self.map_ids:
            return

        selected_map = self.map_ids[self.selected_index]
        label = self._format_map_label(selected_map)
        visited = getattr(self.world, "visited_maps", set())
        status = "Visited" if selected_map in visited else "Unvisited"

        title_font = self.assets.get_font(Fonts.DEFAULT, Fonts.SIZE_SUBHEADING)
        title = title_font.render(label, True, Colors.TEXT_PRIMARY)
        surface.blit(title, (info_rect.left + Layout.PADDING_MD, info_rect.top + Layout.PADDING_MD))

        status_text = font.render(f"Status: {status}", True, Colors.TEXT_SECONDARY)
        surface.blit(status_text, (info_rect.left + Layout.PADDING_MD, info_rect.top + 50))

        connections = [self._format_map_label(target) for target, _ in self.graph.get(selected_map, [])]
        if connections:
            conn_text = font.render("Connections: " + ", ".join(connections[:3]), True, Colors.TEXT_SECONDARY)
        else:
            conn_text = font.render("Connections: None", True, Colors.TEXT_DISABLED)
        surface.blit(conn_text, (info_rect.left + Layout.PADDING_MD, info_rect.top + 75))

        legend_y = info_rect.top + Layout.PADDING_MD
        legend_x = info_rect.right - 160
        self._draw_legend(surface, legend_x, legend_y, font)

    def _draw_legend(self, surface: pygame.Surface, x: int, y: int, font: pygame.font.Font) -> None:
        """Draw legend explaining node colors."""
        entries = [
            (Colors.ACCENT, "Current"),
            (Colors.TEXT_SUCCESS, "Visited"),
            (Colors.TEXT_DISABLED, "Unvisited"),
        ]
        for color, label in entries:
            pygame.draw.circle(surface, color, (x, y + 6), 6)
            text = font.render(label, True, Colors.TEXT_SECONDARY)
            surface.blit(text, (x + 12, y))
            y += Layout.LINE_HEIGHT_COMPACT

    def _draw_help_text(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        """Render control hint text."""
        help_text = "←/→ or ↑/↓: Navigate  •  ESC: Close"
        text_surface = font.render(help_text, True, Colors.TEXT_SECONDARY)
        help_rect = text_surface.get_rect(
            center=(surface.get_width() // 2, surface.get_height() - Layout.SCREEN_MARGIN)
        )
        surface.blit(text_surface, help_rect)

    def _format_map_label(self, map_id: str) -> str:
        """Pretty formatting for map ids."""
        return map_id.replace("_", " ").title()
