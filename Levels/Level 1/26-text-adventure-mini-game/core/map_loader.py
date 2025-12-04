"""Map loading and world construction from JSON data.

This module handles parsing map JSON files, padding malformed tile data,
validating warps, and constructing the World with all maps and NPCs.
"""

import copy
import json
import os
from dataclasses import replace
from typing import Dict, List, TYPE_CHECKING

from .entities import load_npcs_from_json
from .logging_utils import log_warning
from .map_models import (
    EntityRef,
    Map,
    OverworldEnemySpawn,
    Prop,
    Tile,
    Trigger,
    Warp,
)

if TYPE_CHECKING:
    from .world import World


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


def _validate_warps(world: "World") -> None:
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


def load_world_from_data(data_dir: str = "data") -> "World":
    """Load all maps from the data directory."""
    # Import here to avoid circular dependency
    from .world import World
    from .entities import NPC, OverworldEnemy

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
