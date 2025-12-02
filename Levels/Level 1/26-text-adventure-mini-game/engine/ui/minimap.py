"""Minimap HUD component."""

from typing import Dict, List, Optional, Tuple

import pygame

from ..theme import Colors, Fonts


class Minimap:
    """HUD minimap overlay showing the current map, player position, and points of interest."""

    # Tile type to color mapping
    TILE_COLORS: Dict[str, Tuple[int, int, int]] = {
        "grass": (60, 120, 60),
        "path": (140, 120, 80),
        "dirt": (120, 90, 60),
        "water": (60, 100, 180),
        "stone": (100, 100, 110),
        "wall": (70, 70, 80),
        "void": (20, 20, 30),
        "cave": (50, 45, 55),
        "cave_floor": (70, 65, 75),
        "flower": (100, 140, 100),
        "tree": (40, 80, 40),
    }

    def __init__(
        self,
        size: int = 120,
        tile_size: int = 4,
        position: Optional[Tuple[int, int]] = None,
        alpha: int = 220,
        border_color: Optional[Tuple[int, int, int]] = None,
        border_width: int = 2,
        player_color: Optional[Tuple[int, int, int]] = None,
        warp_color: Optional[Tuple[int, int, int]] = None,
        trigger_color: Optional[Tuple[int, int, int]] = None,
        npc_color: Optional[Tuple[int, int, int]] = None,
        battle_color: Optional[Tuple[int, int, int]] = None,
    ):
        self.size = size
        self.tile_size = tile_size
        self.position = position
        self.alpha = alpha
        self.border_color = border_color or Colors.BORDER
        self.border_width = border_width
        # Store explicit overrides; use None to indicate lazy evaluation
        self._player_color_override = player_color
        self._warp_color_override = warp_color
        self._trigger_color_override = trigger_color
        self._npc_color_override = npc_color
        self._battle_color_override = battle_color

        # Cache the minimap surface
        self._cached_map_id: Optional[str] = None
        self._cached_surface: Optional[pygame.Surface] = None

    # Lazy color properties that re-evaluate accessibility colors on each access
    @property
    def player_color(self) -> Tuple[int, int, int]:
        """Get player marker color, respecting current accessibility settings."""
        return self._player_color_override or Colors.get_accessibility_color("player_marker")

    @property
    def warp_color(self) -> Tuple[int, int, int]:
        """Get warp marker color, respecting current accessibility settings."""
        return self._warp_color_override or Colors.get_accessibility_color("warp_marker")

    @property
    def trigger_color(self) -> Tuple[int, int, int]:
        """Get trigger marker color, respecting current accessibility settings."""
        return self._trigger_color_override or Colors.get_accessibility_color("enemy_marker")

    @property
    def npc_color(self) -> Tuple[int, int, int]:
        """Get NPC marker color, respecting current accessibility settings."""
        return self._npc_color_override or Colors.get_accessibility_color("npc_marker")

    @property
    def battle_color(self) -> Tuple[int, int, int]:
        """Get battle marker color, respecting current accessibility settings."""
        return self._battle_color_override or Colors.get_accessibility_color("enemy_marker")

    def _get_tile_color(self, sprite_id: str) -> Tuple[int, int, int]:
        """Get color for a tile based on its sprite_id."""
        # Check exact match first
        if sprite_id in self.TILE_COLORS:
            return self.TILE_COLORS[sprite_id]
        # Check partial matches
        for key, color in self.TILE_COLORS.items():
            if key in sprite_id.lower():
                return color
        # Default color for unknown tiles
        return (80, 80, 80)

    def _build_map_surface(self, current_map) -> pygame.Surface:
        """Build the base minimap surface from map tiles."""
        map_width = current_map.width
        map_height = current_map.height

        # Calculate surface size based on map dimensions
        surface_width = map_width * self.tile_size
        surface_height = map_height * self.tile_size

        surface = pygame.Surface((surface_width, surface_height), pygame.SRCALPHA)
        surface.fill((30, 30, 40, self.alpha))

        # Draw tiles
        for y, row in enumerate(current_map.tiles):
            for x, tile in enumerate(row):
                color = self._get_tile_color(tile.sprite_id)
                # Darken non-walkable tiles
                if not tile.walkable:
                    color = (color[0] // 2, color[1] // 2, color[2] // 2)
                rect = pygame.Rect(
                    x * self.tile_size,
                    y * self.tile_size,
                    self.tile_size,
                    self.tile_size
                )
                pygame.draw.rect(surface, color, rect)

        # Draw warps as small indicators
        for warp in current_map.warps:
            wx = warp.x * self.tile_size + self.tile_size // 2
            wy = warp.y * self.tile_size + self.tile_size // 2
            pygame.draw.circle(surface, self.warp_color, (wx, wy), max(2, self.tile_size // 2))

        return surface

    def draw(
        self,
        surface: pygame.Surface,
        current_map,
        player_x: int,
        player_y: int,
        entities: Optional[List] = None,
        triggers: Optional[List] = None,
    ) -> None:
        """Draw the minimap on the given surface."""
        screen_width, screen_height = surface.get_size()

        # Default position: top-right corner with padding
        if self.position is None:
            pos_x = screen_width - self.size - 10
            pos_y = 10
        else:
            pos_x, pos_y = self.position

        # Rebuild cache if map changed
        if self._cached_map_id != current_map.map_id or self._cached_surface is None:
            self._cached_surface = self._build_map_surface(current_map)
            self._cached_map_id = current_map.map_id

        # Calculate the visible portion of the map to show
        map_surface = self._cached_surface
        map_px_width = map_surface.get_width()
        map_px_height = map_surface.get_height()

        # Center the view on the player
        player_px_x = player_x * self.tile_size + self.tile_size // 2
        player_px_y = player_y * self.tile_size + self.tile_size // 2

        # Calculate the source rectangle (what part of the map to show)
        half_size = self.size // 2
        src_x = max(0, min(player_px_x - half_size, map_px_width - self.size))
        src_y = max(0, min(player_px_y - half_size, map_px_height - self.size))

        # Clamp source rect to map bounds
        src_width = min(self.size, map_px_width)
        src_height = min(self.size, map_px_height)

        # Create the display surface
        display_surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        display_surface.fill((30, 30, 40, self.alpha))

        # Blit the visible portion of the map
        src_rect = pygame.Rect(src_x, src_y, src_width, src_height)
        display_surface.blit(map_surface, (0, 0), src_rect)

        # Calculate player position on the minimap display
        player_display_x = player_px_x - src_x
        player_display_y = player_px_y - src_y

        # Draw NPCs/entities
        if entities:
            for entity in entities:
                ex = entity.x * self.tile_size + self.tile_size // 2 - src_x
                ey = entity.y * self.tile_size + self.tile_size // 2 - src_y
                if 0 <= ex < self.size and 0 <= ey < self.size:
                    pygame.draw.circle(display_surface, self.npc_color, (int(ex), int(ey)), max(2, self.tile_size // 2))

        # Draw active triggers (battles, dialogues)
        if triggers:
            for trigger in triggers:
                if trigger.fired and trigger.once:
                    continue
                tx = trigger.x * self.tile_size + self.tile_size // 2 - src_x
                ty = trigger.y * self.tile_size + self.tile_size // 2 - src_y
                if 0 <= tx < self.size and 0 <= ty < self.size:
                    # Use different color for battle triggers
                    color = self.battle_color if trigger.trigger_type == "battle" else self.trigger_color
                    pygame.draw.rect(
                        display_surface,
                        color,
                        pygame.Rect(int(tx) - 2, int(ty) - 2, 4, 4)
                    )

        # Draw player indicator (pulsing dot)
        pygame.draw.circle(
            display_surface,
            self.player_color,
            (int(player_display_x), int(player_display_y)),
            max(3, self.tile_size // 2 + 1)
        )
        # Inner dot for visibility
        pygame.draw.circle(
            display_surface,
            Colors.WHITE,
            (int(player_display_x), int(player_display_y)),
            max(1, self.tile_size // 4)
        )

        # Draw border
        border_rect = pygame.Rect(0, 0, self.size, self.size)
        pygame.draw.rect(display_surface, self.border_color, border_rect, self.border_width)

        # Blit to main surface
        surface.blit(display_surface, (pos_x, pos_y))

        # Draw legend below the minimap
        self._draw_legend(surface, pos_x, pos_y + self.size + 5)

    def _draw_legend(self, surface: pygame.Surface, x: int, y: int) -> None:
        """Draw a compact legend below the minimap."""
        # Legend items: (color, label)
        legend_items = [
            (self.player_color, "You"),
            (self.npc_color, "NPC"),
            (self.warp_color, "Exit"),
            (self.battle_color, "Battle"),
        ]

        # Calculate layout
        item_width = self.size // 2
        item_height = 12
        font = pygame.font.Font(None, 14)

        # Draw semi-transparent background for legend
        legend_height = (len(legend_items) // 2 + len(legend_items) % 2) * item_height + 4
        legend_bg = pygame.Surface((self.size, legend_height), pygame.SRCALPHA)
        legend_bg.fill(Colors.BG_OVERLAY)
        pygame.draw.rect(legend_bg, self.border_color, (0, 0, self.size, legend_height), 1)
        surface.blit(legend_bg, (x, y))

        # Draw legend items in 2 columns
        for i, (color, label) in enumerate(legend_items):
            col = i % 2
            row = i // 2
            item_x = x + 4 + col * item_width
            item_y = y + 2 + row * item_height

            # Draw color indicator
            pygame.draw.circle(surface, color, (item_x + 4, item_y + 5), 3)

            # Draw label
            label_surface = font.render(label, True, Colors.TEXT_SECONDARY)
            surface.blit(label_surface, (item_x + 12, item_y))
