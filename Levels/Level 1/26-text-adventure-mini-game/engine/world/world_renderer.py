"""World rendering helpers and projection utilities."""

from typing import List, Optional, Tuple, TYPE_CHECKING

import pygame

from core.entities import NPC
from core.logging_utils import log_warning
from core.world import Map

from .overworld_renderer import OverworldRenderer

if TYPE_CHECKING:
    from core.entities import Entity, NPC
    from engine.world_scene import WorldScene


class WorldRenderer:
    """Coordinates rendering and map lookups for the world scene."""

    def __init__(self, scene: "WorldScene"):
        self.scene = scene
        self._overworld_renderer = OverworldRenderer(scene)

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

    def get_current_entities(self) -> Tuple[Optional[Map], List["Entity"]]:
        """Return the current map and any instantiated entities on it."""
        try:
            current_map = self.scene.world.get_current_map()
        except Exception as exc:
            log_warning(f"Failed to load current map '{self.scene.world.current_map_id}': {exc}")
            return None, []

        all_entities = getattr(self.scene.world, "map_entities", {}).get(current_map.map_id, [])

        visible_entities = []
        for entity in all_entities:
            requires_flag = getattr(entity, "visibility_requires_flag", None)
            hide_if_flag = getattr(entity, "visibility_hide_if_flag", None)

            if requires_flag and not self.scene.world.get_flag(requires_flag):
                continue
            if hide_if_flag and self.scene.world.get_flag(hide_if_flag):
                continue

            visible_entities.append(entity)

        return current_map, visible_entities

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
