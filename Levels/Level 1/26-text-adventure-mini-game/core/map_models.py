"""Pure data models for map representation.

This module contains the core dataclasses and classes used to represent
map data structures: tiles, warps, triggers, entities, props, and the Map class.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional

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
