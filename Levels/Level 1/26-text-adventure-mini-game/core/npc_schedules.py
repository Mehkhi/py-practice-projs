"""NPC scheduling system for time-based location management."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING

from .time_system import TimeOfDay
from .logging_utils import log_warning

if TYPE_CHECKING:
    from .world import World, Map
    from .entities import NPC


@dataclass
class ScheduleEntry:
    """A single schedule entry defining where an NPC should be at a given time."""

    time_periods: List[TimeOfDay]  # When this entry is active
    map_id: str  # Which map the NPC should be on
    x: int  # X position on that map
    y: int  # Y position on that map
    activity: Optional[str] = None  # Optional activity description (e.g., "sleeping", "working")
    shop_available: bool = True  # Whether the shop is open during this schedule entry
    alternative_dialogue_id: Optional[str] = None  # Dialogue to show when shop is closed


@dataclass
class NPCSchedule:
    """Complete schedule for an NPC across all time periods."""

    npc_id: str  # Entity ID of the NPC
    default_map_id: str  # Fallback map if no schedule matches
    default_x: int  # Fallback X position
    default_y: int  # Fallback Y position
    entries: List[ScheduleEntry] = field(default_factory=list)  # Time-based location entries


class ScheduleManager:
    """Manages all NPC schedules and handles NPC repositioning."""

    save_key: str = "npc_schedules"

    def __init__(self, schedules: Optional[Dict[str, NPCSchedule]] = None) -> None:
        """Initialize the schedule manager.

        Args:
            schedules: Dictionary mapping NPC IDs to their schedules
        """
        self.schedules: Dict[str, NPCSchedule] = schedules or {}
        self._last_time_period: Optional[TimeOfDay] = None
        self._npc_positions: Dict[str, Tuple[str, int, int]] = {}
        self._pending_position_restore: bool = False
        self._force_schedule_refresh: bool = False

    def get_npc_location(
        self, npc_id: str, time_of_day: TimeOfDay
    ) -> Tuple[str, int, int]:
        """Get where an NPC should be at a given time.

        Args:
            npc_id: The entity ID of the NPC
            time_of_day: Current time period

        Returns:
            Tuple of (map_id, x, y) for the NPC's scheduled location
        """
        schedule = self.schedules.get(npc_id)
        if not schedule:
            # No schedule found, return None values to indicate no movement needed
            return ("", 0, 0)

        # Find first matching entry for current time period
        for entry in schedule.entries:
            if time_of_day in entry.time_periods:
                return (entry.map_id, entry.x, entry.y)

        # No matching entry, use default
        return (schedule.default_map_id, schedule.default_x, schedule.default_y)

    def get_npc_activity(self, npc_id: str, time_of_day: TimeOfDay) -> Optional[str]:
        """Get what activity an NPC is doing at the current time.

        Args:
            npc_id: The entity ID of the NPC
            time_of_day: Current time period

        Returns:
            Activity string if available, None otherwise
        """
        schedule = self.schedules.get(npc_id)
        if not schedule:
            return None

        # Find first matching entry for current time period
        for entry in schedule.entries:
            if time_of_day in entry.time_periods:
                return entry.activity

        return None

    def is_shop_available(self, npc_id: str, time_of_day: TimeOfDay) -> bool:
        """Check if an NPC's shop is currently open.

        Args:
            npc_id: The entity ID of the NPC
            time_of_day: Current time period

        Returns:
            True if shop is available, False otherwise. Defaults to True if no schedule found.
        """
        schedule = self.schedules.get(npc_id)
        if not schedule:
            # No schedule found, default to available for backward compatibility
            return True

        # Find first matching entry for current time period
        for entry in schedule.entries:
            if time_of_day in entry.time_periods:
                return entry.shop_available

        # No matching entry, default to available
        return True

    def get_alternative_dialogue(self, npc_id: str, time_of_day: TimeOfDay) -> Optional[str]:
        """Get alternative dialogue ID for when shop is closed.

        Args:
            npc_id: The entity ID of the NPC
            time_of_day: Current time period

        Returns:
            Alternative dialogue ID if shop is closed and one is set, None otherwise
        """
        schedule = self.schedules.get(npc_id)
        if not schedule:
            return None

        # Find first matching entry for current time period
        for entry in schedule.entries:
            if time_of_day in entry.time_periods:
                # Only return alternative dialogue if shop is closed
                if not entry.shop_available:
                    return entry.alternative_dialogue_id
                return None

        return None

    def get_npcs_on_map(self, map_id: str, time_of_day: TimeOfDay) -> List[str]:
        """Get list of NPC IDs currently scheduled to be on a map.

        Args:
            map_id: The map ID to check
            time_of_day: Current time period

        Returns:
            List of NPC IDs scheduled to be on the map at this time
        """
        npc_ids: List[str] = []
        for npc_id, schedule in self.schedules.items():
            # Find first matching entry for current time period
            for entry in schedule.entries:
                if time_of_day in entry.time_periods:
                    if entry.map_id == map_id:
                        npc_ids.append(npc_id)
                    break
            else:
                # No matching entry, check default location
                if schedule.default_map_id == map_id:
                    npc_ids.append(npc_id)

        return npc_ids

    def is_npc_available_for_quest(self, npc_id: str, time_of_day: TimeOfDay) -> bool:
        """Check if an NPC is available to give/progress quests.

        NPCs who are 'sleeping', 'away', or 'busy' typically can't give quests.

        Args:
            npc_id: The entity ID of the NPC
            time_of_day: Current time period

        Returns:
            True if NPC is available for quests, False otherwise
        """
        activity = self.get_npc_activity(npc_id, time_of_day)
        unavailable_activities = {"sleeping", "away", "busy"}
        return activity not in unavailable_activities if activity else True

    def _find_nearest_walkable(
        self, map_obj: "Map", x: int, y: int, max_radius: int = 5
    ) -> Optional[Tuple[int, int]]:
        """Find the nearest walkable tile to (x, y) using BFS-style expansion."""
        # If the requested position is already walkable, return immediately
        if map_obj.is_walkable(x, y):
            return (x, y)

        for radius in range(1, max_radius + 1):
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    if abs(dx) + abs(dy) != radius:
                        continue
                    check_x = x + dx
                    check_y = y + dy
                    if map_obj.is_walkable(check_x, check_y):
                        return (check_x, check_y)

        return None

    def update(self, world: "World", time_of_day: TimeOfDay) -> List[str]:
        """Update all NPC positions based on current time.

        Only processes when time period changes.

        Args:
            world: The world instance containing maps and entities
            time_of_day: Current time period

        Returns:
            List of NPC IDs that were moved
        """
        should_restore_positions = self._pending_position_restore
        force_schedule_refresh = self._force_schedule_refresh
        # Skip if time period hasn't changed
        if time_of_day == self._last_time_period and not (should_restore_positions or force_schedule_refresh):
            return []

        # Don't move NPCs if there's an active interaction
        if world.npc_interaction_active:
            return []

        moved_npcs: List[str] = []

        if should_restore_positions:
            moved_npcs.extend(self._apply_saved_positions(world))
            self._pending_position_restore = False
            self._force_schedule_refresh = False
            self._last_time_period = time_of_day
            return moved_npcs

        self._force_schedule_refresh = False
        self._last_time_period = time_of_day

        # Process each scheduled NPC
        for npc_id, schedule in self.schedules.items():
            # Find NPC in world using World method
            result = world.get_entity_by_id(npc_id)
            if not result:
                # NPC not found in world, log warning and skip
                log_warning(f"Schedule: NPC '{npc_id}' not found in world, skipping schedule update")
                continue

            current_map_id, npc = result

            # Get scheduled location
            target_map_id, target_x, target_y = self.get_npc_location(npc_id, time_of_day)

            if not target_map_id:
                # No schedule location (shouldn't happen, but handle gracefully)
                self._npc_positions[npc_id] = (current_map_id, npc.x, npc.y)
                continue

            # Check if NPC needs to move
            needs_move = False
            if current_map_id != target_map_id:
                needs_move = True
            elif npc.x != target_x or npc.y != target_y:
                needs_move = True

            final_map_id = current_map_id
            if needs_move:
                # Use World method to move entity
                if world.move_entity_to_map(npc_id, current_map_id, target_map_id, target_x, target_y):
                    moved_npcs.append(npc_id)
                    final_map_id = target_map_id

            self._npc_positions[npc_id] = (final_map_id, npc.x, npc.y)
        return moved_npcs

    def serialize(self) -> Dict[str, Any]:
        """Serialize state (Saveable protocol)."""
        return {
            "last_time_period": self._last_time_period.value if self._last_time_period else None,
            "npc_positions": {
                npc_id: {"map_id": map_id, "x": x, "y": y}
                for npc_id, (map_id, x, y) in self._npc_positions.items()
            },
        }

    def deserialize_into(self, data: Dict[str, Any]) -> None:
        """Restore state from saved data (Saveable protocol)."""
        if not isinstance(data, dict):
            log_warning(f"ScheduleManager.deserialize_into expected dict, got {type(data).__name__}")
            self._last_time_period = None
            self._npc_positions = {}
            self._pending_position_restore = False
            self._force_schedule_refresh = False
            return

        raw_period = data.get("last_time_period")
        if raw_period is None:
            self._last_time_period = None
        elif isinstance(raw_period, str):
            try:
                self._last_time_period = TimeOfDay(raw_period)
            except ValueError:
                try:
                    self._last_time_period = TimeOfDay[raw_period.upper()]
                except KeyError:
                    log_warning(f"ScheduleManager: invalid last_time_period '{raw_period}', resetting")
                    self._last_time_period = None
        else:
            self._last_time_period = None

        self._npc_positions = {}
        raw_positions = data.get("npc_positions", {})
        if isinstance(raw_positions, dict):
            for npc_id, position in raw_positions.items():
                if not isinstance(position, dict):
                    continue
                map_id = position.get("map_id")
                x = position.get("x")
                y = position.get("y")
                if isinstance(map_id, str) and isinstance(x, int) and isinstance(y, int):
                    self._npc_positions[npc_id] = (map_id, x, y)

        if self._npc_positions:
            self._pending_position_restore = True
            self._force_schedule_refresh = False
        else:
            # Force a schedule update to reposition NPCs for older saves without position data
            self._pending_position_restore = False
            self._force_schedule_refresh = self._last_time_period is not None

    def _apply_saved_positions(self, world: "World") -> List[str]:
        """Move NPCs to their last known saved positions."""
        moved_npcs: List[str] = []
        for npc_id, (map_id, x, y) in self._npc_positions.items():
            result = world.get_entity_by_id(npc_id)
            if not result:
                log_warning(f"Schedule: NPC '{npc_id}' not found during position restore")
                continue

            current_map_id, npc = result
            target_map_id = map_id or current_map_id
            if not target_map_id:
                continue

            if world.move_entity_to_map(npc_id, current_map_id, target_map_id, x, y):
                moved_npcs.append(npc_id)
                self._npc_positions[npc_id] = (target_map_id, npc.x, npc.y)
            else:
                self._npc_positions[npc_id] = (current_map_id, npc.x, npc.y)

        return moved_npcs
