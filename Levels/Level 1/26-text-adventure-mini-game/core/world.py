"""World and map system for tile-based overworld."""

import copy
import os
from dataclasses import dataclass, field, replace
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
import json
from .entities import load_npcs_from_json
from .logging_utils import log_warning


@dataclass
class Tile:
    """Represents a single tile on the map."""
    tile_id: str
    walkable: bool
    sprite_id: str


@dataclass
class Warp:
    """Represents a map transition point."""
    x: int
    y: int
    target_map_id: str
    target_x: int
    target_y: int
    requires_flag: Optional[str] = None
    requires_item: Optional[str] = None
    blocked_by_flag: Optional[str] = None
    fail_dialogue_id: Optional[str] = None
    challenge_dungeon_id: Optional[str] = None


@dataclass
class Trigger:
    """Represents an event trigger at a map position."""
    id: str
    x: int
    y: int
    trigger_type: str  # "dialogue", "battle", "cutscene", "script", "fishing", "warp", "item", "flag"
    data: Dict
    once: bool = True
    fired: bool = False


@dataclass
class EntityRef:
    """Reference to an entity placed on a map."""
    entity_id: str
    x: int
    y: int
    requires_flag: Optional[str] = None  # Only show if this flag is set
    hide_if_flag: Optional[str] = None   # Hide if this flag is set (e.g., after recruitment)


@dataclass
class OverworldEnemySpawn:
    """Spawn point for an overworld enemy on a map."""
    spawn_id: str
    x: int
    y: int
    encounter_id: str
    sprite_id: str = "enemy"
    facing: str = "down"
    detection_range: int = 3
    move_interval: float = 1.5
    turn_interval: float = 2.0
    patrol_radius: int = 3
    once: bool = True  # If True, enemy disappears after defeat


@dataclass
class Prop:
    """Decorative object placed on a map for visual diversity."""
    prop_id: str
    x: int
    y: int
    sprite_id: str
    solid: bool = True  # Whether the prop blocks movement


class Map:
    """Represents a single map/area in the game world."""

    def __init__(
        self,
        map_id: str,
        width: int,
        height: int,
        tiles: List[List[Tile]],
        warps: List[Warp] = None,
        triggers: List[Trigger] = None,
        entities: List[EntityRef] = None,
        enemy_spawns: List[OverworldEnemySpawn] = None,
        props: List[Prop] = None,
    ):
        self.map_id = map_id
        actual_height = len(tiles)
        actual_width = len(tiles[0]) if tiles else 0
        if width is not None and width != actual_width:
            log_warning(
                f"map {map_id} declared width {width} but tiles are {actual_width}; "
                "using tile grid dimensions"
            )
        if height is not None and height != actual_height:
            log_warning(
                f"map {map_id} declared height {height} but tiles are {actual_height}; "
                "using tile grid dimensions"
            )
        self.width = actual_width
        self.height = actual_height
        self.tiles = tiles
        self.warps = warps or []
        self.triggers = triggers or []
        self.entities = entities or []
        self.enemy_spawns = enemy_spawns or []
        self.props = props or []

    def get_prop_at(self, x: int, y: int) -> Optional[Prop]:
        """Get the prop at a position, if any."""
        for prop in self.props:
            if prop.x == x and prop.y == y:
                return prop
        return None

    def is_blocked_by_prop(self, x: int, y: int) -> bool:
        """Check if a position is blocked by a solid prop."""
        prop = self.get_prop_at(x, y)
        return prop is not None and prop.solid

    def is_walkable(self, x: int, y: int) -> bool:
        """Check if a position is walkable, guarding malformed tile data and props."""
        if x < 0 or y < 0:
            return False
        if y >= len(self.tiles):
            return False
        row = self.tiles[y]
        if x >= len(row):
            return False
        # Check if blocked by a solid prop
        if self.is_blocked_by_prop(x, y):
            return False
        return row[x].walkable

    def get_trigger_at(self, x: int, y: int) -> Optional[Trigger]:
        """Get the trigger at a position, if any."""
        for trigger in self.triggers:
            if trigger.x == x and trigger.y == y and not (trigger.once and trigger.fired):
                return trigger
        return None

    def get_warp_at(self, x: int, y: int) -> Optional[Warp]:
        """Get the warp at a position, if any."""
        for warp in self.warps:
            if warp.x == x and warp.y == y:
                return warp
        return None

    def fire_trigger(self, trigger_id: str) -> bool:
        """Mark a trigger as fired."""
        for trigger in self.triggers:
            if trigger.id == trigger_id:
                trigger.fired = True
                return True
        return False

    def validate(self) -> None:
        """Validate internal map consistency and warn if out of sync."""
        if len(self.tiles) != self.height:
            log_warning(f"map {self.map_id} tile rows {len(self.tiles)} != height {self.height}")
        for idx, row in enumerate(self.tiles):
            if len(row) != self.width:
                log_warning(f"map {self.map_id} row {idx} length {len(row)} != width {self.width}")


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
            callback: Function that takes (flag_name: str, flag_value: bool) and returns None.
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
            from .logging_utils import log_warning
            log_warning(
                f"move_entity_to_map: Target map '{to_map}' not found for entity '{entity_id}'"
            )
            return False

        # Find walkable position (handles blocked positions)
        try:
            final_x, final_y = self.find_nearest_walkable(to_map, x, y)
        except ValueError:
            from .logging_utils import log_warning
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


def load_map_from_json(json_path: str) -> Map:
    """Load a map from a JSON file, padding tile data when malformed."""
    with open(json_path, 'r') as f:
        data = json.load(f)

    map_id = data.get("map_id")
    if not map_id:
        raise ValueError(f"Map file {json_path} is missing required field 'map_id'")

    declared_width = data.get("width")
    declared_height = data.get("height")
    raw_tiles = data.get("tiles", [])
    placeholder_tile = Tile("void", False, "void")

    def _placeholder_tile() -> Tile:
        return Tile(placeholder_tile.tile_id, placeholder_tile.walkable, placeholder_tile.sprite_id)

    def _has_required(obj: Dict, fields: List[str], label: str) -> bool:
        missing = [field for field in fields if field not in obj]
        if missing:
            log_warning(f"map {map_id}: {label} missing required fields {', '.join(missing)}, skipping entry")
            return False
        return True

    # Load tiles with tolerance for malformed entries
    tiles: List[List[Tile]] = []
    max_width_seen = 0
    for y, row in enumerate(raw_tiles):
        if not isinstance(row, list):
            log_warning(f"map {map_id}: row {y} is not a list, replacing with placeholder tiles")
            # Determine width for placeholder row: use declared_width if available, otherwise max width seen so far, or 1 as fallback
            placeholder_width = declared_width if declared_width else (max_width_seen if max_width_seen > 0 else 1)
            placeholder_row = [_placeholder_tile() for _ in range(placeholder_width)]
            tiles.append(placeholder_row)
            continue
        tile_row: List[Tile] = []
        for x, tile_data in enumerate(row):
            if not isinstance(tile_data, dict):
                log_warning(f"map {map_id}: tile at ({x}, {y}) is not an object, using placeholder")
                tile_row.append(_placeholder_tile())
                continue
            if "tile_id" not in tile_data:
                log_warning(f"map {map_id}: tile at ({x}, {y}) missing tile_id, using placeholder")
                tile_row.append(_placeholder_tile())
                continue
            tile_row.append(
                Tile(
                    tile_id=tile_data["tile_id"],
                    walkable=tile_data.get("walkable", True),
                    sprite_id=tile_data.get("sprite_id", tile_data["tile_id"]),
                )
            )
        if not tile_row:
            # Preserve row position even when every entry is invalid by filling placeholders
            placeholder_width = declared_width or max(len(row), max_width_seen, 1)
            tile_row = [_placeholder_tile() for _ in range(placeholder_width)]
        tiles.append(tile_row)
        max_width_seen = max(max_width_seen, len(tile_row))

    actual_height = len(tiles)
    actual_width = max((len(r) for r in tiles), default=0)

    target_width = declared_width or actual_width
    target_height = declared_height or actual_height
    target_width = max(target_width, actual_width)
    target_height = max(target_height, actual_height)

    if (declared_width and declared_width != actual_width) or (declared_height and declared_height != actual_height):
        log_warning(
            f"map {map_id} tile grid was {actual_width}x{actual_height} "
            f"but declared {declared_width}x{declared_height}; normalizing to {target_width}x{target_height}"
        )

    padded_tiles: List[List[Tile]] = []
    for row in tiles:
        row_copy = list(row)
        if len(row_copy) < target_width:
            row_copy.extend([_placeholder_tile() for _ in range(target_width - len(row_copy))])
        elif len(row_copy) > target_width:
            row_copy = row_copy[:target_width]
        padded_tiles.append(row_copy)
    while len(padded_tiles) < target_height:
        padded_tiles.append([_placeholder_tile() for _ in range(target_width)])
    if len(padded_tiles) > target_height:
        padded_tiles = padded_tiles[:target_height]

    # Load warps
    warps = []
    for warp_data in data.get('warps', []):
        if not isinstance(warp_data, dict):
            log_warning(f"map {map_id}: warp entry is not an object, skipping")
            continue
        if not _has_required(warp_data, ["x", "y", "target_map_id", "target_x", "target_y"], "warp"):
            continue
        warps.append(Warp(
            x=warp_data.get('x', 0),
            y=warp_data.get('y', 0),
            target_map_id=warp_data.get('target_map_id', ''),
            target_x=warp_data.get('target_x', 0),
            target_y=warp_data.get('target_y', 0),
            requires_flag=warp_data.get("requires_flag"),
            requires_item=warp_data.get("requires_item"),
            blocked_by_flag=warp_data.get("blocked_by_flag"),
            fail_dialogue_id=warp_data.get("fail_dialogue_id"),
            challenge_dungeon_id=warp_data.get("challenge_dungeon_id"),
        ))

    # Load triggers
    triggers = []
    for trigger_data in data.get('triggers', []):
        if not isinstance(trigger_data, dict):
            log_warning(f"map {map_id}: trigger entry is not an object, skipping")
            continue
        if not _has_required(trigger_data, ["id", "x", "y", "trigger_type"], "trigger"):
            continue
        triggers.append(Trigger(
            id=trigger_data.get('id', ''),
            x=trigger_data.get('x', 0),
            y=trigger_data.get('y', 0),
            trigger_type=trigger_data.get('trigger_type', ''),
            data=trigger_data.get('data', {}),
            once=trigger_data.get('once', True)
        ))

    # Load entity refs
    entities = []
    for entity_data in data.get('entities', []):
        if not isinstance(entity_data, dict):
            log_warning(f"map {map_id}: entity entry is not an object, skipping")
            continue
        if not _has_required(entity_data, ["entity_id", "x", "y"], "entity"):
            continue
        entities.append(EntityRef(
            entity_id=entity_data.get('entity_id', ''),
            x=entity_data.get('x', 0),
            y=entity_data.get('y', 0),
            requires_flag=entity_data.get('requires_flag'),
            hide_if_flag=entity_data.get('hide_if_flag')
        ))

    # Load overworld enemy spawns
    enemy_spawns = []
    for spawn_data in data.get('enemy_spawns', []):
        if not isinstance(spawn_data, dict):
            log_warning(f"map {map_id}: enemy_spawn entry is not an object, skipping")
            continue
        if not _has_required(spawn_data, ["spawn_id", "x", "y", "encounter_id"], "enemy_spawns"):
            continue
        enemy_spawns.append(OverworldEnemySpawn(
            spawn_id=spawn_data.get('spawn_id', ''),
            x=spawn_data.get('x', 0),
            y=spawn_data.get('y', 0),
            encounter_id=spawn_data.get('encounter_id', ''),
            sprite_id=spawn_data.get('sprite_id', 'enemy'),
            facing=spawn_data.get('facing', 'down'),
            detection_range=spawn_data.get('detection_range', 3),
            move_interval=spawn_data.get('move_interval', 1.5),
            turn_interval=spawn_data.get('turn_interval', 2.0),
            patrol_radius=spawn_data.get('patrol_radius', 3),
            once=spawn_data.get('once', True),
        ))

    # Load decorative props
    props = []
    for prop_data in data.get('props', []):
        if not isinstance(prop_data, dict):
            log_warning(f"map {map_id}: prop entry is not an object, skipping")
            continue
        if not _has_required(prop_data, ["prop_id", "x", "y"], "prop"):
            continue
        props.append(Prop(
            prop_id=prop_data.get('prop_id', ''),
            x=prop_data.get('x', 0),
            y=prop_data.get('y', 0),
            sprite_id=prop_data.get('sprite_id', prop_data.get('prop_id', 'prop')),
            solid=prop_data.get('solid', True),
        ))

    return Map(
        map_id=map_id,
        width=target_width,
        height=target_height,
        tiles=padded_tiles,
        warps=warps,
        triggers=triggers,
        entities=entities,
        enemy_spawns=enemy_spawns,
        props=props,
    )


def get_map_graph(world: World) -> Dict[str, List[Tuple[str, bool]]]:
    """
    Build a directed graph of map connections from warps.

    Returns:
        Dictionary mapping source map_id to list of (target_map_id, is_conditional) tuples.
        is_conditional is True if the warp has requires_flag, requires_item, or blocked_by_flag.
    """
    graph: Dict[str, List[Tuple[str, bool]]] = {}

    for map_id, map_obj in world.maps.items():
        connections: List[Tuple[str, bool]] = []
        for warp in map_obj.warps:
            # Skip warps to non-existent maps
            if warp.target_map_id not in world.maps:
                continue

            # Check if warp is conditional
            is_conditional = bool(
                warp.requires_flag or warp.requires_item or warp.blocked_by_flag
            )

            connections.append((warp.target_map_id, is_conditional))

        graph[map_id] = connections

    return graph


def analyze_map_connectivity(
    world: World, start_map_id: str = "forest_path"
) -> Tuple[List[str], List[str], List[str], Dict[str, List[Tuple[str, bool]]]]:
    """
    Analyze map connectivity to identify dead ends, disconnected maps, and orphaned maps.

    Args:
        world: The World instance to analyze
        start_map_id: The starting map for reachability analysis (default: "forest_path")

    Returns:
        Tuple of (dead_ends, disconnected, orphaned, graph):
        - dead_ends: Maps with no outgoing warps (or only conditional warps)
        - disconnected: Maps unreachable from start_map_id
        - orphaned: Maps that exist but aren't referenced by any warp's target_map_id
                    (excludes start_map_id since it's the entry point)
        - graph: The map connectivity graph
    """
    graph = get_map_graph(world)

    # Find all maps referenced as warp targets
    referenced_maps: set = set()
    for connections in graph.values():
        for target_map_id, _ in connections:
            referenced_maps.add(target_map_id)

    # Find orphaned maps (exist but never referenced)
    # Exclude start_map_id since it's the entry point and expected to not be referenced
    all_maps = set(world.maps.keys())
    orphaned = sorted(all_maps - referenced_maps - {start_map_id})

    # Find dead ends (maps with no outgoing warps, or only conditional warps)
    dead_ends: List[str] = []
    for map_id, connections in graph.items():
        if not connections:
            # No outgoing warps at all
            dead_ends.append(map_id)
        else:
            # Check if all warps are conditional
            all_conditional = all(is_conditional for _, is_conditional in connections)
            if all_conditional:
                dead_ends.append(map_id)

    # Find disconnected maps (unreachable from start_map_id)
    disconnected: List[str] = []
    if start_map_id in world.maps:
        # BFS to find all reachable maps
        visited: set = set()
        queue: List[str] = [start_map_id]
        visited.add(start_map_id)

        while queue:
            current = queue.pop(0)
            if current in graph:
                for target_map_id, is_conditional in graph[current]:
                    # Only follow non-conditional warps for reachability
                    # (conditional warps may never be accessible)
                    if not is_conditional and target_map_id not in visited:
                        visited.add(target_map_id)
                        queue.append(target_map_id)

        # All maps not visited are disconnected
        disconnected = sorted(all_maps - visited)
    else:
        # Start map doesn't exist, all maps are disconnected
        disconnected = sorted(all_maps)

    return (sorted(dead_ends), disconnected, orphaned, graph)


def _validate_warps(world: World) -> None:
    """Validate all warps in the world for target map existence and coordinate validity."""
    for map_id, map_obj in world.maps.items():
        for warp in map_obj.warps:
            # Check if target map exists
            if warp.target_map_id not in world.maps:
                log_warning(
                    f"warp in map '{map_id}' at ({warp.x}, {warp.y}) "
                    f"targets non-existent map '{warp.target_map_id}'"
                )
                continue

            target_map = world.maps[warp.target_map_id]

            # Check if target coordinates are within bounds
            if warp.target_x < 0 or warp.target_y < 0:
                log_warning(
                    f"warp in map '{map_id}' at ({warp.x}, {warp.y}) "
                    f"targets invalid coordinates ({warp.target_x}, {warp.target_y}) in map '{warp.target_map_id}' "
                    "(negative coordinates)"
                )
            elif warp.target_x >= target_map.width or warp.target_y >= target_map.height:
                log_warning(
                    f"warp in map '{map_id}' at ({warp.x}, {warp.y}) "
                    f"targets out-of-bounds coordinates ({warp.target_x}, {warp.target_y}) in map '{warp.target_map_id}' "
                    f"(map size: {target_map.width}x{target_map.height})"
                )
            else:
                # Check if target coordinates are walkable (optional but useful)
                if not target_map.is_walkable(warp.target_x, warp.target_y):
                    log_warning(
                        f"warp in map '{map_id}' at ({warp.x}, {warp.y}) "
                        f"targets non-walkable tile ({warp.target_x}, {warp.target_y}) in map '{warp.target_map_id}'"
                    )

            # Check if source coordinates are walkable (optional but useful)
            if not map_obj.is_walkable(warp.x, warp.y):
                log_warning(
                    f"warp in map '{map_id}' at ({warp.x}, {warp.y}) "
                    "is placed on a non-walkable tile"
                )


def load_world_from_data(data_dir: str = "data") -> World:
    """Load all maps from the data directory."""
    world = World()
    maps_dir = os.path.join(data_dir, "maps")
    npc_definitions = load_npcs_from_json(os.path.join(data_dir, "entities.json"))

    def _warn_out_of_bounds_refs(map_obj: Map) -> None:
        for warp in map_obj.warps:
            if warp.x < 0 or warp.y < 0 or warp.x >= map_obj.width or warp.y >= map_obj.height:
                log_warning(f"warp in map {map_obj.map_id} at ({warp.x}, {warp.y}) is out of bounds")
        for trigger in map_obj.triggers:
            if trigger.x < 0 or trigger.y < 0 or trigger.x >= map_obj.width or trigger.y >= map_obj.height:
                log_warning(f"trigger {trigger.id} in map {map_obj.map_id} at ({trigger.x}, {trigger.y}) is out of bounds")
        for entity in map_obj.entities:
            if entity.x < 0 or entity.y < 0 or entity.x >= map_obj.width or entity.y >= map_obj.height:
                log_warning(f"entity '{entity.entity_id}' in map {map_obj.map_id} at ({entity.x}, {entity.y}) is out of bounds")

    if not os.path.exists(maps_dir):
        raise ValueError(f"Maps directory not found at {maps_dir}")

    loaded_any = False
    for filename in os.listdir(maps_dir):
        if filename.endswith('.json'):
            map_path = os.path.join(maps_dir, filename)
            try:
                map_obj = load_map_from_json(map_path)
                map_obj.validate()
                _warn_out_of_bounds_refs(map_obj)
                world.add_map(map_obj)
                loaded_any = True
            except Exception as e:
                log_warning(f"Failed to load map {filename}: {e}")

    if not loaded_any:
        raise ValueError(f"No maps loaded from {maps_dir}")

    # Instantiate NPCs on maps based on references
    if npc_definitions:
        from core.entities import NPC  # Local import to avoid circular
        for map_id, map_obj in world.maps.items():
            instances: List[NPC] = []
            for ref in map_obj.entities:
                npc_proto = npc_definitions.get(ref.entity_id)
                if not npc_proto:
                    log_warning(f"NPC '{ref.entity_id}' not found for map '{map_id}'")
                    continue
                npc_instance = replace(npc_proto)
                npc_instance.set_position(ref.x, ref.y)
                # Deep copy stats if present so each NPC tracks its own state
                if npc_instance.stats:
                    npc_instance.stats = copy.deepcopy(npc_instance.stats)
                # Store visibility flags for conditional display
                npc_instance.visibility_requires_flag = ref.requires_flag
                npc_instance.visibility_hide_if_flag = ref.hide_if_flag
                instances.append(npc_instance)
            world.set_map_entities(map_id, instances)

    # Instantiate overworld enemies from spawn points
    from core.entities import OverworldEnemy
    for map_id, map_obj in world.maps.items():
        enemy_instances: List[OverworldEnemy] = []
        for spawn in map_obj.enemy_spawns:
            enemy = OverworldEnemy(
                entity_id=spawn.spawn_id,
                name=spawn.spawn_id,  # Can be overridden by encounter data
                x=spawn.x,
                y=spawn.y,
                sprite_id=spawn.sprite_id,
                encounter_id=spawn.encounter_id,
                facing=spawn.facing,
                detection_range=spawn.detection_range,
                move_interval=spawn.move_interval,
                turn_interval=spawn.turn_interval,
                patrol_radius=spawn.patrol_radius,
                once=spawn.once,
            )
            enemy_instances.append(enemy)
        world.set_map_overworld_enemies(map_id, enemy_instances)

    # Validate all warps after all maps are loaded
    _validate_warps(world)

    return world
