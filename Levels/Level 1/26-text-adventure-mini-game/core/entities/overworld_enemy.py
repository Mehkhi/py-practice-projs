"""Overworld-visible enemy that can roam and trigger battles."""

import random
from dataclasses import dataclass, field
from typing import Tuple, TYPE_CHECKING

from .base import Entity

if TYPE_CHECKING:
    from ..world import Map


@dataclass
class OverworldEnemy(Entity):
    """
    Enemy entity visible in the overworld that can roam and trigger battles.

    Battles are triggered when the enemy is facing the player and the player
    is within detection range.
    """

    encounter_id: str = "default"  # Which encounter to start when battle triggers
    facing: str = "down"  # "up", "down", "left", "right"
    detection_range: int = 3  # How many tiles ahead the enemy can "see"
    move_interval: float = 1.5  # Seconds between movement attempts
    turn_interval: float = 2.0  # Seconds between random direction changes
    patrol_radius: int = 3  # How far from spawn point enemy can roam
    spawn_x: int = 0  # Original spawn position
    spawn_y: int = 0
    defeated: bool = False  # Whether this enemy has been defeated (for once-only encounters)
    once: bool = True  # If True, enemy disappears after defeat

    # Timers (not serialized, reset on load)
    _move_timer: float = field(default=0.0, repr=False)
    _turn_timer: float = field(default=0.0, repr=False)

    def __post_init__(self) -> None:
        """Initialize overworld enemy defaults."""
        if self.faction == "neutral":
            self.faction = "enemy"
        self.solid = True  # Enemies block movement
        self.spawn_x = self.x
        self.spawn_y = self.y

    def get_facing_offset(self) -> Tuple[int, int]:
        """Get the (dx, dy) offset for the current facing direction."""
        offsets = {
            "up": (0, -1),
            "down": (0, 1),
            "left": (-1, 0),
            "right": (1, 0),
        }
        return offsets.get(self.facing, (0, 1))

    def can_see_position(self, target_x: int, target_y: int) -> bool:
        """
        Check if this enemy can see the target position based on facing direction.

        Returns True if the target is in a straight line in front of the enemy
        within detection_range tiles.
        """
        dx, dy = self.get_facing_offset()

        for dist in range(1, self.detection_range + 1):
            check_x = self.x + dx * dist
            check_y = self.y + dy * dist
            if check_x == target_x and check_y == target_y:
                return True
        return False

    def update(self, dt: float, current_map: "Map", blocked_positions: set) -> bool:
        """
        Update enemy movement and facing.

        Args:
            dt: Delta time in seconds
            current_map: The current map for walkability checks
            blocked_positions: Set of (x, y) positions that are blocked (player, other entities)

        Returns:
            True if the enemy moved this frame
        """
        self._move_timer += dt
        self._turn_timer += dt
        moved = False

        # Random direction change
        if self._turn_timer >= self.turn_interval:
            self._turn_timer = 0.0
            directions = ["up", "down", "left", "right"]
            self.facing = random.choice(directions)

        # Movement attempt
        if self._move_timer >= self.move_interval:
            self._move_timer = 0.0

            # 50% chance to move, 50% chance to just stand
            if random.random() < 0.5:
                dx, dy = self.get_facing_offset()
                new_x = self.x + dx
                new_y = self.y + dy

                # Check if within patrol radius
                dist_from_spawn = abs(new_x - self.spawn_x) + abs(new_y - self.spawn_y)

                if dist_from_spawn <= self.patrol_radius:
                    # Check walkability and blocked positions
                    if current_map.is_walkable(new_x, new_y) and (
                        new_x,
                        new_y,
                    ) not in blocked_positions:
                        self.x = new_x
                        self.y = new_y
                        moved = True
                else:
                    # Turn around if at edge of patrol area
                    opposite = {
                        "up": "down",
                        "down": "up",
                        "left": "right",
                        "right": "left",
                    }
                    self.facing = opposite.get(self.facing, "down")

        return moved
