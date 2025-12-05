"""Rendering for entities (player, enemies, NPCs)."""

import math
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

import pygame

from ..theme import Colors

if TYPE_CHECKING:
    from engine.world_scene import WorldScene
    from core.entities import OverworldEnemy


def draw_direction_indicator(
    surface: pygame.Surface,
    screen_x: int,
    screen_y: int,
    tile_size: int,
    facing: str,
    indicator_size: int,
    fill_color: Tuple[int, int, int],
    border_color: Tuple[int, int, int],
    indicator_gap: int = 2,
) -> None:
    """Draw a triangle indicator showing facing direction.

    Args:
        surface: Pygame surface to draw on
        screen_x: Screen x position of the entity
        screen_y: Screen y position of the entity
        tile_size: Size of the entity tile in pixels
        facing: Direction the entity is facing ("up", "down", "left", "right")
        indicator_size: Size of the indicator triangle
        fill_color: RGB tuple for the indicator fill
        border_color: RGB tuple for the indicator border
        indicator_gap: Gap between entity edge and indicator (default 2)
    """
    center_x = screen_x + tile_size // 2
    center_y = screen_y + tile_size // 2

    # Calculate indicator position based on facing direction
    facing_offsets = {
        "up": (0, -tile_size // 2 - indicator_size - indicator_gap),
        "down": (0, tile_size // 2 + indicator_gap),
        "left": (-tile_size // 2 - indicator_size - indicator_gap, 0),
        "right": (tile_size // 2 + indicator_gap, 0),
    }
    offset_x, offset_y = facing_offsets.get(facing, (0, tile_size // 2))
    indicator_x = center_x + offset_x
    indicator_y = center_y + offset_y

    # Calculate triangle points based on facing direction
    if facing == "up":
        points = [
            (indicator_x, indicator_y),
            (indicator_x - indicator_size // 2, indicator_y + indicator_size),
            (indicator_x + indicator_size // 2, indicator_y + indicator_size),
        ]
    elif facing == "down":
        points = [
            (indicator_x, indicator_y + indicator_size),
            (indicator_x - indicator_size // 2, indicator_y),
            (indicator_x + indicator_size // 2, indicator_y),
        ]
    elif facing == "left":
        points = [
            (indicator_x, indicator_y),
            (indicator_x + indicator_size, indicator_y - indicator_size // 2),
            (indicator_x + indicator_size, indicator_y + indicator_size // 2),
        ]
    else:  # right
        points = [
            (indicator_x + indicator_size, indicator_y),
            (indicator_x, indicator_y - indicator_size // 2),
            (indicator_x, indicator_y + indicator_size // 2),
        ]

    # Draw the triangle with fill and border
    pygame.draw.polygon(surface, fill_color, points)
    pygame.draw.polygon(surface, border_color, points, 1)


class EntityRenderer:
    """Handles rendering of entities including player, enemies, and NPCs."""

    def __init__(self, scene: "WorldScene"):
        """Initialize renderer with reference to the world scene."""
        self.scene = scene
        self._shadow_surface_cache: Dict[Tuple[int, int], pygame.Surface] = {}
        self._detection_surface_cache: Optional[pygame.Surface] = None
        self._enemy_detection_cache: Dict[int, Dict[str, Any]] = {}
        self._fallback_surface_cache: Dict[Tuple[int, int, int], pygame.Surface] = {}

    def _get_sprite_safe(
        self, sprite_id: str, size: Tuple[int, int], fallback_color: Tuple[int, int, int] = (128, 128, 128)
    ) -> pygame.Surface:
        """Safely get a sprite, returning a colored fallback if loading fails.

        Args:
            sprite_id: The sprite identifier to load.
            size: Tuple of (width, height) for the sprite.
            fallback_color: RGB color for the fallback surface if loading fails.

        Returns:
            The loaded sprite surface, or a colored rectangle fallback.
        """
        try:
            if self.scene.assets is None:
                raise ValueError("Assets manager is not available")
            sprite = self.scene.assets.get_image(sprite_id, size)
            if sprite is not None:
                return sprite
        except (AttributeError, pygame.error, OSError, ValueError) as e:
            # Log the error but don't crash - this is a rendering issue, not fatal
            import logging
            logging.debug(f"Failed to load sprite '{sprite_id}': {e}")

        # Return cached or create new fallback surface
        cache_key = (size[0], size[1], hash(fallback_color))
        if cache_key not in self._fallback_surface_cache:
            fallback = pygame.Surface(size, pygame.SRCALPHA)
            fallback.fill((*fallback_color, 200))
            # Draw a simple "X" pattern to indicate missing sprite
            pygame.draw.line(fallback, (255, 255, 255), (0, 0), size, 2)
            pygame.draw.line(fallback, (255, 255, 255), (size[0], 0), (0, size[1]), 2)
            self._fallback_surface_cache[cache_key] = fallback
        return self._fallback_surface_cache[cache_key]

    def _get_detection_tiles(self, enemy: "OverworldEnemy") -> List[Tuple[int, int]]:
        """Precompute detection tile positions in world space for reuse."""
        tile_size = self.scene.draw_tile
        cache_key = (
            enemy.x,
            enemy.y,
            enemy.facing,
            enemy.detection_range,
            tile_size,
            self.scene.projection,
        )
        cached = self._enemy_detection_cache.get(id(enemy))
        if cached and cached.get("key") == cache_key:
            return cached["positions"]

        dx, dy = enemy.get_facing_offset()
        positions: List[Tuple[int, int]] = []
        for dist in range(1, enemy.detection_range + 1):
            tile_x = enemy.x + dx * dist
            tile_y = enemy.y + dy * dist
            world_x = tile_x * tile_size
            world_y = tile_y * tile_size
            if self.scene.projection == "oblique":
                world_y -= (tile_x % 2) * (tile_size // 4)
            positions.append((world_x, world_y))

        self._enemy_detection_cache[id(enemy)] = {
            "key": cache_key,
            "positions": positions,
        }
        return positions

    def draw_entities(self, surface: pygame.Surface, entities: List) -> None:
        """Draw all entities (NPCs, etc.) on the map."""
        sprite_size = (self.scene.tile_size, self.scene.tile_size)
        for entity in entities:
            sprite = self._get_sprite_safe(entity.sprite_id, sprite_size, fallback_color=(100, 100, 150))
            screen_x, screen_y = self.scene.renderer.project(entity.x, entity.y)
            surface.blit(sprite, (screen_x, screen_y))

    def draw_player(self, surface: pygame.Surface) -> None:
        """Draw the player with improved walking animation."""
        player_screen_x, player_screen_y = self.scene.renderer.project(self.scene.player.x, self.scene.player.y)

        # Get base player sprite (with safe fallback)
        sprite_size = (self.scene.tile_size, self.scene.tile_size)
        player_surface = self._get_sprite_safe(self.scene.player.sprite_id, sprite_size, fallback_color=(80, 120, 200))

        # Calculate animation offsets
        if self.scene.is_walking:
            # Walking animation: bob up and down more pronounced, with horizontal sway
            walk_bob = int(self.scene.bob_height * 1.5 * abs(math.sin(self.scene.walk_frame * math.pi / 2)))
            # Slight horizontal sway for more natural movement
            walk_sway = int(self.scene.scale * math.sin(self.scene.walk_frame * math.pi / 2))

            # Apply walking offsets
            draw_x = player_screen_x + walk_sway
            draw_y = player_screen_y - walk_bob

            # Draw walking "dust" effect (small particles behind player)
            self._draw_walk_dust(surface, player_screen_x, player_screen_y)
        else:
            # Idle animation: gentle breathing bob
            idle_bob = int(self.scene.bob_height * 0.5 * abs(math.sin(self.scene.anim_time * 2)))
            draw_x = player_screen_x
            draw_y = player_screen_y - idle_bob

        # Apply directional flip for left/right facing
        if self.scene.player_facing == "left":
            player_surface = pygame.transform.flip(player_surface, True, False)

        # Draw shadow under player (reuse cached surface)
        shadow_rect = pygame.Rect(
            player_screen_x + self.scene.draw_tile // 4,
            player_screen_y + self.scene.draw_tile - 4 * self.scene.scale,
            self.scene.draw_tile // 2,
            4 * self.scene.scale
        )
        shadow_key = (shadow_rect.width, shadow_rect.height)
        if shadow_key not in self._shadow_surface_cache:
            shadow_surf = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow_surf, (0, 0, 0, 60), shadow_surf.get_rect())
            self._shadow_surface_cache[shadow_key] = shadow_surf
        else:
            shadow_surf = self._shadow_surface_cache[shadow_key]
        surface.blit(shadow_surf, shadow_rect)

        # Draw the player sprite
        surface.blit(player_surface, (draw_x, draw_y))

        # Draw direction indicator (small arrow showing facing direction)
        self._draw_facing_indicator(surface, player_screen_x, player_screen_y)

        # Draw highlight on current tile
        highlight_rect = pygame.Rect(player_screen_x, player_screen_y, self.scene.draw_tile, self.scene.draw_tile)
        pygame.draw.rect(surface, Colors.WHITE, highlight_rect, 1)

    def _draw_walk_dust(self, surface: pygame.Surface, screen_x: int, screen_y: int) -> None:
        """Draw dust particles when walking."""
        if self.scene.walk_frame in (1, 3):  # Only show dust on certain frames
            dust_size = 3 * self.scene.scale
            dust_alpha = 100 - int(self.scene.walk_anim_time * 300)
            if dust_alpha > 0:
                # Position dust behind the player based on facing direction
                offsets = {
                    "up": (self.scene.draw_tile // 2, self.scene.draw_tile + dust_size),
                    "down": (self.scene.draw_tile // 2, -dust_size),
                    "left": (self.scene.draw_tile + dust_size, self.scene.draw_tile // 2),
                    "right": (-dust_size, self.scene.draw_tile // 2),
                }
                offset_x, offset_y = offsets.get(self.scene.player_facing, (0, self.scene.draw_tile))
                dust_x = screen_x + offset_x - dust_size // 2
                dust_y = screen_y + offset_y - dust_size // 2

                dust_surface = pygame.Surface((dust_size * 2, dust_size * 2), pygame.SRCALPHA)
                pygame.draw.circle(dust_surface, (180, 160, 140, dust_alpha), (dust_size, dust_size), dust_size)
                surface.blit(dust_surface, (dust_x, dust_y))

    def _draw_facing_indicator(self, surface: pygame.Surface, screen_x: int, screen_y: int) -> None:
        """Draw a small indicator showing which direction the player is facing."""
        # Player indicator: subtle blue, smaller size
        draw_direction_indicator(
            surface=surface,
            screen_x=screen_x,
            screen_y=screen_y,
            tile_size=self.scene.draw_tile,
            facing=self.scene.player_facing,
            indicator_size=4 * self.scene.scale,
            fill_color=(100, 150, 255),
            border_color=(60, 100, 200),
            indicator_gap=2,
        )

    def draw_overworld_enemy(self, surface: pygame.Surface, enemy: "OverworldEnemy") -> None:
        """Draw an overworld enemy with a direction indicator."""
        screen_x, screen_y = self.scene.renderer.project(enemy.x, enemy.y)

        # Draw the enemy sprite (with safe fallback)
        sprite_size = (self.scene.tile_size, self.scene.tile_size)
        sprite = self._get_sprite_safe(enemy.sprite_id, sprite_size, fallback_color=(200, 80, 80))
        surface.blit(sprite, (screen_x, screen_y))

        # Draw a direction indicator (red triangle showing danger direction)
        draw_direction_indicator(
            surface=surface,
            screen_x=screen_x,
            screen_y=screen_y,
            tile_size=self.scene.draw_tile,
            facing=enemy.facing,
            indicator_size=6 * self.scene.scale,
            fill_color=(255, 80, 80),
            border_color=(180, 40, 40),
            indicator_gap=0,
        )

        # Draw detection range visualization (optional - shows line of sight)
        # Reuse cached detection surface
        detection_size = (self.scene.draw_tile, self.scene.draw_tile)
        if self._detection_surface_cache is None or self._detection_surface_cache.get_size() != detection_size:
            self._detection_surface_cache = pygame.Surface(detection_size, pygame.SRCALPHA)
            self._detection_surface_cache.fill((255, 0, 0, 30))  # Semi-transparent red

        detection_tiles = self._get_detection_tiles(enemy)
        cam_x, cam_y = self.scene.camera_offset
        for tile_world_x, tile_world_y in detection_tiles:
            detection_rect = pygame.Rect(
                tile_world_x - cam_x,
                tile_world_y - cam_y,
                self.scene.draw_tile,
                self.scene.draw_tile
            )
            surface.blit(self._detection_surface_cache, detection_rect)
