"""World and map system for tile-based overworld.

This module provides the World class for managing game state and maps,
along with re-exports of map-related types for backward compatibility.
"""

from typing import Any, Callable, Dict, List, Optional, Set, Tuple

# Re-export models for backward compatibility
from .map_models import (
    Tile,
    Warp,
    Trigger,
    EntityRef,
    OverworldEnemySpawn,
    Prop,
    Map,
)

# Re-export loader functions for backward compatibility
from .map_loader import (
    load_map_from_json,
    load_world_from_data,
    _validate_warps,
)

# Re-export analysis functions for backward compatibility
from .map_analysis import (
    get_map_graph,
    analyze_map_connectivity,
)

from .logging_utils import log_warning


class World:
    """Container for all maps and global game state."""

    def __init__(self):
        self.maps: Dict[str, Map] = {}
        self.current_map_id: str = "forest_path"
        self.flags: Dict[str, Any] = {}
        self.map_entities: Dict[str, List["Entity"]] = {}
        self.map_overworld_enemies: Dict[str, List["OverworldEnemy"]] = {}
        self.npc_interaction_active: bool = False
        self.visited_maps: Set[str] = set()
        self.mark_map_visited(self.current_map_id)
        self._flag_change_callback: Optional[Callable[[str, Any], None]] = None

    def get_current_map(self) -> Map:
        """Get the currently active map."""
        return self.maps[self.current_map_id]

    def set_current_map(self, map_id: str) -> None:
        """Change the current map."""
        if map_id in self.maps:
            self.current_map_id = map_id
            self.mark_map_visited(map_id)
        else:
            raise ValueError(f"Map {map_id} not found")

    def set_flag(self, flag_name: str, value: Any = True) -> None:
        """Set a world flag.

        Args:
            flag_name: Name of the flag to set
            value: Value to set (default True)

        If a flag change callback is registered, it will be called after
        setting the flag. This allows systems like quest manager to react
        to flag changes without polling.
        """
        self.flags[flag_name] = value
        if self._flag_change_callback:
            self._flag_change_callback(flag_name, value)

    def set_flag_change_callback(self, callback: Optional[Callable[[str, Any], None]]) -> None:
        """Register a callback to be called when flags change.

        Args:
            callback: Function that takes (flag_name: str, flag_value: Any) and returns None.
                      Flag values can be bool, int, float, str, or dict depending on the flag.
                      Pass None to unregister.
        """
        self._flag_change_callback = callback

    def get_flag(self, flag_name: str, default: Any = False) -> Any:
        """Get a world flag value."""
        return self.flags.get(flag_name, default)

    def add_map(self, map_obj: Map) -> None:
        """Add a map to the world."""
        self.maps[map_obj.map_id] = map_obj

    def set_map_entities(self, map_id: str, entities: List["Entity"]) -> None:
        """Assign instantiated entities to a map for runtime use."""
        self.map_entities[map_id] = entities

    def get_map_entities(self, map_id: str) -> List["Entity"]:
        """Get instantiated entities for a map."""
        return self.map_entities.get(map_id, [])

    def set_map_overworld_enemies(self, map_id: str, enemies: List["OverworldEnemy"]) -> None:
        """Assign instantiated overworld enemies to a map."""
        self.map_overworld_enemies[map_id] = enemies

    def get_map_overworld_enemies(self, map_id: str) -> List["OverworldEnemy"]:
        """Get instantiated overworld enemies for a map."""
        return self.map_overworld_enemies.get(map_id, [])

    def get_active_overworld_enemies(self, map_id: str) -> List["OverworldEnemy"]:
        """Get only non-defeated overworld enemies for a map."""
        return [e for e in self.get_map_overworld_enemies(map_id) if not e.defeated]

    def mark_enemy_defeated(self, map_id: str, spawn_id: str) -> None:
        """Mark an overworld enemy as defeated by its spawn_id."""
        for enemy in self.get_map_overworld_enemies(map_id):
            if enemy.entity_id == spawn_id:
                enemy.defeated = True
                break

    def mark_map_visited(self, map_id: Optional[str]) -> None:
        """Record that a map has been visited."""
        if map_id:
            self.visited_maps.add(map_id)

    def get_entity_by_id(self, entity_id: str) -> Optional[Tuple[str, "Entity"]]:
        """Find an entity across all maps.

        Args:
            entity_id: The entity ID to search for

        Returns:
            Tuple of (map_id, entity) if found, None otherwise
        """
        for map_id, entities in self.map_entities.items():
            for entity in entities:
                if hasattr(entity, "entity_id") and entity.entity_id == entity_id:
                    return (map_id, entity)
        return None

    def find_nearest_walkable(self, map_id: str, x: int, y: int) -> Tuple[int, int]:
        """Find the nearest walkable tile to the given position.

        Uses BFS (Manhattan distance) to search outward from target position.

        Args:
            map_id: The map ID to search on
            x: Target X coordinate
            y: Target Y coordinate

        Returns:
            Tuple of (x, y) for the nearest walkable position

        Raises:
            ValueError: If no walkable tile is found within max radius
        """
        if map_id not in self.maps:
            raise ValueError(f"Map '{map_id}' not found")
        map_obj = self.maps[map_id]

        # Check target position first
        if map_obj.is_walkable(x, y):
            return (x, y)

        # Search in expanding radius (BFS with Manhattan distance)
        max_radius = 5
        for radius in range(1, max_radius + 1):
            # Check all positions at this Manhattan distance
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    if abs(dx) + abs(dy) != radius:
                        continue
                    check_x = x + dx
                    check_y = y + dy
                    if map_obj.is_walkable(check_x, check_y):
                        return (check_x, check_y)

        raise ValueError(
            f"No walkable tile found near ({x}, {y}) on map '{map_id}' within radius {max_radius}"
        )

    def move_entity_to_map(
        self, entity_id: str, from_map: str, to_map: str, x: int, y: int
    ) -> bool:
        """Move an entity from one map to another.

        Args:
            entity_id: The entity ID to move
            from_map: The source map ID
            to_map: The target map ID
            x: Target X coordinate
            y: Target Y coordinate

        Returns:
            True if successful, False if entity not found
        """
        # Find entity in source map
        if from_map not in self.map_entities:
            return False

        entity = None
        for e in self.map_entities[from_map]:
            if hasattr(e, "entity_id") and e.entity_id == entity_id:
                entity = e
                break

        if not entity:
            return False

        # Check if target map exists
        if to_map not in self.maps:
            log_warning(
                f"move_entity_to_map: Target map '{to_map}' not found for entity '{entity_id}'"
            )
            return False

        # Find walkable position (handles blocked positions)
        try:
            final_x, final_y = self.find_nearest_walkable(to_map, x, y)
        except ValueError:
            log_warning(
                f"move_entity_to_map: No walkable position found near ({x}, {y}) "
                f"on map '{to_map}' for entity '{entity_id}'"
            )
            return False

        # If already on target map, just update position
        if from_map == to_map:
            entity.set_position(final_x, final_y)
            return True

        # Move between maps: remove from old map, add to new map
        self.map_entities[from_map].remove(entity)

        # Add to new map
        if to_map not in self.map_entities:
            self.map_entities[to_map] = []
        self.map_entities[to_map].append(entity)

        # Update position
        entity.set_position(final_x, final_y)
        return True
