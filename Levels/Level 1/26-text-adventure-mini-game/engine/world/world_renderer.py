"""World rendering helpers and projection utilities."""

from typing import List, Optional, Tuple, TYPE_CHECKING

import pygame

from core.entities import NPC
from core.logging_utils import log_warning
from core.world import Map, Prop

from .overworld_renderer import OverworldRenderer

if TYPE_CHECKING:
    from core.entities import Entity, NPC, OverworldEnemy
    from engine.world_scene import WorldScene


class WorldRenderer:
    """Coordinates rendering and map lookups for the world scene."""

    def __init__(self, scene: "WorldScene"):
        self.scene = scene
        self._overworld_renderer = OverworldRenderer(scene)
        # Reusable lists to avoid per-frame allocations
        self._visible_entities_cache: List["Entity"] = []
        self._visible_props_cache: List[Prop] = []
        self._visible_enemies_cache: List["OverworldEnemy"] = []
        # Track last camera position for cache invalidation
        self._last_camera_offset: Tuple[int, int] = (-1, -1)
        self._camera_move_threshold: int = 32  # Recompute culling if camera moved more than this

    def preload_map_sprites(self) -> None:
        """Preload sprites for the current map to prevent stuttering during gameplay."""
        current_map = self.scene.world.get_current_map()
        if not current_map:
            return

        map_sprites: List[str] = []

        for row in current_map.tiles:
            for tile in row:
                sprite_id = getattr(tile, "sprite_id", None) or getattr(tile, "tile_type", None)
                if sprite_id and sprite_id not in map_sprites:
                    map_sprites.append(sprite_id)

        for prop in current_map.props:
            if hasattr(prop, "sprite_id") and prop.sprite_id and prop.sprite_id not in map_sprites:
                map_sprites.append(prop.sprite_id)

        _, entities = self.get_current_entities()
        for entity in entities:
            if hasattr(entity, "sprite_id") and entity.sprite_id and entity.sprite_id not in map_sprites:
                map_sprites.append(entity.sprite_id)

        if hasattr(self.scene.player, "sprite_id") and self.scene.player.sprite_id:
            if self.scene.player.sprite_id not in map_sprites:
                map_sprites.append(self.scene.player.sprite_id)

        active_enemies = self.scene.world.get_active_overworld_enemies(current_map.map_id)
        for enemy in active_enemies:
            if hasattr(enemy, "sprite_id") and enemy.sprite_id and enemy.sprite_id not in map_sprites:
                map_sprites.append(enemy.sprite_id)

        for sprite_id in map_sprites:
            try:
                self.scene.assets.get_tile_surface(sprite_id, self.scene.tile_size)
            except Exception as exc:
                log_warning(f"Failed to preload map sprite {sprite_id}: {exc}")

    def _cull_to_viewport(
        self,
        items: List,
        get_position,
        screen_width: int,
        screen_height: int,
        margin: int = 1
    ) -> List:
        """Cull items to viewport bounds using screen-space coordinates.

        Args:
            items: List of items to cull (entities, props, etc.)
            get_position: Function(item) -> (x, y) that returns map coordinates
            screen_width: Screen width in pixels
            screen_height: Screen height in pixels
            margin: Extra margin in tiles to include items slightly off-screen

        Returns:
            List of items visible in viewport
        """
        visible = []
        # Calculate viewport bounds in map coordinates
        cam_x, cam_y = self.scene.camera_offset
        start_tile_x = max(0, cam_x // self.scene.draw_tile - margin)
        start_tile_y = max(0, cam_y // self.scene.draw_tile - margin)
        end_tile_x = (cam_x + screen_width) // self.scene.draw_tile + margin + 1
        end_tile_y = (cam_y + screen_height) // self.scene.draw_tile + margin + 1

        for item in items:
            x, y = get_position(item)
            # Check if item is within viewport bounds
            if start_tile_x <= x < end_tile_x and start_tile_y <= y < end_tile_y:
                visible.append(item)

        return visible

    def get_current_entities(self, cull_to_viewport: bool = True) -> Tuple[Optional[Map], List["Entity"]]:
        """Return the current map and any instantiated entities on it.

        Args:
            cull_to_viewport: If True, only return entities visible in viewport
        """
        try:
            current_map = self.scene.world.get_current_map()
        except Exception as exc:
            log_warning(f"Failed to load current map '{self.scene.world.current_map_id}': {exc}")
            return None, []

        all_entities = getattr(self.scene.world, "map_entities", {}).get(current_map.map_id, [])

        # Reuse cached list instead of creating new one
        self._visible_entities_cache.clear()

        for entity in all_entities:
            requires_flag = getattr(entity, "visibility_requires_flag", None)
            hide_if_flag = getattr(entity, "visibility_hide_if_flag", None)

            if requires_flag and not self.scene.world.get_flag(requires_flag):
                continue
            if hide_if_flag and self.scene.world.get_flag(hide_if_flag):
                continue

            self._visible_entities_cache.append(entity)

        # Apply viewport culling if requested
        if cull_to_viewport and self.scene.manager:
            try:
                screen = pygame.display.get_surface()
                if screen:
                    screen_width, screen_height = screen.get_size()
                    self._visible_entities_cache = self._cull_to_viewport(
                        self._visible_entities_cache,
                        lambda e: (e.x, e.y),
                        screen_width,
                        screen_height
                    )
            except Exception:
                # Fallback if screen not available
                pass

        return current_map, self._visible_entities_cache

    def get_visible_props(self, current_map: Optional[Map], screen_width: int, screen_height: int) -> List[Prop]:
        """Get props visible in the current viewport.

        Args:
            current_map: Current map instance
            screen_width: Screen width in pixels
            screen_height: Screen height in pixels

        Returns:
            List of props visible in viewport
        """
        if not current_map:
            return []

        # Reuse cached list
        self._visible_props_cache.clear()

        # Cull props to viewport
        self._visible_props_cache = self._cull_to_viewport(
            current_map.props,
            lambda p: (p.x, p.y),
            screen_width,
            screen_height
        )

        return self._visible_props_cache

    def get_visible_enemies(self, current_map: Optional[Map], screen_width: int, screen_height: int) -> List["OverworldEnemy"]:
        """Get overworld enemies visible in the current viewport.

        Args:
            current_map: Current map instance
            screen_width: Screen width in pixels
            screen_height: Screen height in pixels

        Returns:
            List of enemies visible in viewport
        """
        if not current_map:
            return []

        active_enemies = self.scene.world.get_active_overworld_enemies(current_map.map_id)

        # Reuse cached list
        self._visible_enemies_cache.clear()

        # Cull enemies to viewport
        self._visible_enemies_cache = self._cull_to_viewport(
            active_enemies,
            lambda e: (e.x, e.y),
            screen_width,
            screen_height
        )

        return self._visible_enemies_cache

    def find_npc_by_id(self, npc_id: str) -> Optional["NPC"]:
        """Find an NPC by id on the current map."""
        _, entities = self.get_current_entities()
        for entity in entities:
            if isinstance(entity, NPC) and entity.entity_id == npc_id:
                return entity
        return None

    def find_nearby_npc(self) -> Optional["NPC"]:
        """Find an NPC adjacent to the player (Manhattan distance <= 1)."""
        _, entities = self.get_current_entities()
        px, py = self.scene.player.x, self.scene.player.y
        for entity in entities:
            if isinstance(entity, NPC):
                if abs(entity.x - px) + abs(entity.y - py) <= 1:
                    return entity
        return None

    def project(self, x: int, y: int) -> Tuple[int, int]:
        """Convert map coordinates to screen-space using projection."""
        screen_x = x * self.scene.draw_tile - self.scene.camera_offset[0]
        screen_y = y * self.scene.draw_tile - self.scene.camera_offset[1]

        if self.scene.projection == "oblique":
            screen_y -= (x % 2) * (self.scene.draw_tile // 4)
        return screen_x, screen_y

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the overworld via the renderer."""
        self._overworld_renderer.draw(surface)
