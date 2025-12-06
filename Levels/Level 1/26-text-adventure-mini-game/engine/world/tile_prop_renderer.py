"""Rendering for tiles, props, and puzzle elements."""

from typing import TYPE_CHECKING, Dict, Optional, Tuple

import pygame

if TYPE_CHECKING:
    from engine.world_scene import WorldScene
    from core.world import Map, Prop


class TilePropRenderer:
    """Handles rendering of tiles, props, and puzzle elements."""

    def __init__(self, scene: "WorldScene"):
        """Initialize renderer with reference to the world scene."""
        self.scene = scene
        self._tile_surface_cache: Dict[str, pygame.Surface] = {}
        self._tile_surface_cache_map_id: Optional[str] = None
        self._tile_surface_cache_tile_size: Optional[int] = None
        self._shadow_surface_cache: Dict[Tuple[int, int], pygame.Surface] = {}

    def _prepare_tile_surface_cache(self, current_map: "Map") -> Dict[str, pygame.Surface]:
        """Cache tile surfaces for the current map/tile size to avoid per-tile lookups."""
        if not current_map or not current_map.tiles:
            return self._tile_surface_cache

        tile_size = self.scene.tile_size
        if (self._tile_surface_cache_map_id != current_map.map_id or
                self._tile_surface_cache_tile_size != tile_size):
            self._tile_surface_cache.clear()
            override_grass = current_map.map_id == "forest_path"

            for row in current_map.tiles:
                for tile in row:
                    sprite_id = getattr(tile, "sprite_id", None) or getattr(tile, "tile_type", None)
                    # Fallback to grass if sprite_id is missing/empty
                    if not sprite_id:
                        sprite_id = "grass"
                    if override_grass and sprite_id == "grass_dark":
                        sprite_id = "grass"
                    if sprite_id not in self._tile_surface_cache:
                        self._tile_surface_cache[sprite_id] = self.scene.assets.get_tile_surface(sprite_id, tile_size)

            self._tile_surface_cache_map_id = current_map.map_id
            self._tile_surface_cache_tile_size = tile_size

        return self._tile_surface_cache

    def draw_tiles(self, surface: pygame.Surface, current_map: "Map") -> None:
        """Draw all tiles in the visible viewport."""
        screen_width, screen_height = surface.get_size()
        map_height = len(current_map.tiles)
        map_width = len(current_map.tiles[0]) if current_map.tiles else 0

        start_tile_x = max(0, self.scene.camera_offset[0] // self.scene.draw_tile)
        start_tile_y = max(0, self.scene.camera_offset[1] // self.scene.draw_tile)
        end_tile_x = min(map_width, (self.scene.camera_offset[0] + screen_width) // self.scene.draw_tile + 2)
        end_tile_y = min(map_height, (self.scene.camera_offset[1] + screen_height) // self.scene.draw_tile + 2)

        tile_surface_cache = self._prepare_tile_surface_cache(current_map)

        for y in range(start_tile_y, end_tile_y):
            row = current_map.tiles[y]
            row_end = min(end_tile_x, len(row))
            for x in range(start_tile_x, row_end):
                tile = row[x]

                # Get sprite_id with fallback handling
                sprite_id = getattr(tile, "sprite_id", None) or getattr(tile, "tile_type", None)

                # Fallback to grass if sprite_id is missing/empty
                if not sprite_id:
                    sprite_id = "grass"

                # Tile sprite overrides for small aesthetic tweaks
                if current_map.map_id == "forest_path" and sprite_id == "grass_dark":
                    sprite_id = "grass"

                tile_surface = tile_surface_cache.get(sprite_id)
                if tile_surface is None:
                    tile_surface = self.scene.assets.get_tile_surface(sprite_id, self.scene.tile_size)
                    tile_surface_cache[sprite_id] = tile_surface

                screen_x, screen_y = self.scene.renderer.project(x, y)
                surface.blit(tile_surface, (screen_x, screen_y))

    def draw_puzzle_elements(self, surface: pygame.Surface, current_map: "Map") -> None:
        """Draw puzzle elements on the map."""
        if not hasattr(self.scene, 'puzzle_manager') or not self.scene.puzzle_manager:
            return

        puzzle = self.scene.puzzle_manager.get_puzzle_for_map(current_map.map_id)
        if not puzzle:
            return

        from core.puzzles import PuzzleElementType

        for element in puzzle.elements.values():
            screen_x, screen_y = self.scene.renderer.project(element.x, element.y)

            # Get sprite based on element type and state
            sprite_id = element.sprite_id
            if element.element_type == PuzzleElementType.DOOR:
                # Use open/closed sprite based on state
                if element.state == "open" and "data" in element.__dict__:
                    sprite_id = element.data.get("open_sprite", sprite_id)
                elif element.state == "closed":
                    sprite_id = element.sprite_id
            elif element.element_type == PuzzleElementType.PRESSURE_PLATE:
                # Use pressed sprite if activated
                if element.state == "activated":
                    sprite_id = element.data.get("pressed_sprite", sprite_id)

            if sprite_id:
                sprite = self.scene.assets.get_image(
                    sprite_id, (self.scene.tile_size, self.scene.tile_size)
                )

                # Apply visual feedback based on visual_state
                visual_state = getattr(element, 'visual_state', 'normal')
                if visual_state == "flashing":
                    # Flash effect - alternate between normal and bright
                    flash_cycle = int(self.scene.anim_time * 5) % 2
                    if flash_cycle == 0:
                        # Bright flash
                        flash_surface = pygame.Surface(sprite.get_size(), pygame.SRCALPHA)
                        flash_surface.fill((255, 255, 255, 100))
                        sprite = sprite.copy()
                        sprite.blit(flash_surface, (0, 0), special_flags=pygame.BLEND_ADD)
                elif visual_state == "glowing":
                    # Glow effect - add yellow glow
                    glow_surface = pygame.Surface(sprite.get_size(), pygame.SRCALPHA)
                    glow_surface.fill((255, 255, 0, 80))
                    sprite = sprite.copy()
                    sprite.blit(glow_surface, (0, 0), special_flags=pygame.BLEND_ADD)
                elif visual_state == "animating":
                    # Animation effect - slight pulsing
                    pulse = int(self.scene.anim_time * 3) % 2
                    if pulse == 0:
                        pulse_surface = pygame.Surface(sprite.get_size(), pygame.SRCALPHA)
                        pulse_surface.fill((255, 255, 255, 50))
                        sprite = sprite.copy()
                        sprite.blit(pulse_surface, (0, 0), special_flags=pygame.BLEND_ADD)
                elif visual_state == "error":
                    # Error effect - red flash
                    error_surface = pygame.Surface(sprite.get_size(), pygame.SRCALPHA)
                    error_surface.fill((255, 0, 0, 150))
                    sprite = sprite.copy()
                    sprite.blit(error_surface, (0, 0), special_flags=pygame.BLEND_ADD)
                    # Reset error state after brief display
                    if hasattr(self.scene, 'anim_time') and int(self.scene.anim_time * 2) % 2 == 0:
                        element.visual_state = "normal"

                surface.blit(sprite, (screen_x, screen_y))

            # Draw subtle highlight for target positions (pressure plates)
            if element.element_type == PuzzleElementType.PRESSURE_PLATE:
                if element.state == "default":
                    # Draw subtle target indicator
                    highlight_rect = pygame.Rect(
                        screen_x, screen_y, self.scene.draw_tile, self.scene.draw_tile
                    )
                    highlight_surface = pygame.Surface(
                        (self.scene.draw_tile, self.scene.draw_tile), pygame.SRCALPHA
                    )
                    pygame.draw.rect(
                        highlight_surface, (255, 255, 0, 30), highlight_surface.get_rect()
                    )
                    surface.blit(highlight_surface, highlight_rect)

    def draw_prop(self, surface: pygame.Surface, prop: "Prop") -> None:
        """Draw a decorative prop on the map."""
        screen_x, screen_y = self.scene.renderer.project(prop.x, prop.y)

        # Get the prop sprite
        sprite = self.scene.assets.get_image(prop.sprite_id, (self.scene.tile_size, self.scene.tile_size))

        # Draw shadow under solid props for depth (reuse cached surface)
        if prop.solid:
            shadow_rect = pygame.Rect(
                screen_x + self.scene.draw_tile // 4,
                screen_y + self.scene.draw_tile - 3 * self.scene.scale,
                self.scene.draw_tile // 2,
                3 * self.scene.scale
            )
            shadow_key = (shadow_rect.width, shadow_rect.height)
            if shadow_key not in self._shadow_surface_cache:
                shadow_surf = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
                pygame.draw.ellipse(shadow_surf, (0, 0, 0, 40), shadow_surf.get_rect())
                self._shadow_surface_cache[shadow_key] = shadow_surf
            else:
                shadow_surf = self._shadow_surface_cache[shadow_key]
            surface.blit(shadow_surf, shadow_rect)

        # Draw the prop sprite
        surface.blit(sprite, (screen_x, screen_y))
