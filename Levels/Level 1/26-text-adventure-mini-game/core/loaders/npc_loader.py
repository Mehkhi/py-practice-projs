"""NPC schedule data loader."""

from typing import Dict, List

from core.loaders.base import load_json_file
from core.logging_utils import log_warning
from core.npc_schedules import NPCSchedule, ScheduleEntry, ScheduleManager
from core.time_system import TimeOfDay


def load_npc_schedules(
    filepath: str = "data/npc_schedules.json",
) -> ScheduleManager:
    """Load NPC schedules from JSON file.

    Args:
        filepath: Path to the NPC schedules JSON file

    Returns:
        ScheduleManager instance with loaded schedules, or empty manager if file missing
    """
    data = load_json_file(
        filepath,
        default={"schedules": {}},
        context="Loading NPC schedules",
        warn_on_missing=True,
    )

    schedules: Dict[str, NPCSchedule] = {}
    schedules_data = data.get("schedules", {})

    for npc_id, schedule_data in schedules_data.items():
        # Validate required fields
        if "default_map_id" not in schedule_data:
            log_warning(
                f"Schedule for NPC '{npc_id}' missing 'default_map_id', skipping"
            )
            continue
        if "default_x" not in schedule_data:
            log_warning(f"Schedule for NPC '{npc_id}' missing 'default_x', skipping")
            continue
        if "default_y" not in schedule_data:
            log_warning(f"Schedule for NPC '{npc_id}' missing 'default_y', skipping")
            continue

        # Parse schedule entries
        entries: List[ScheduleEntry] = []
        for entry_data in schedule_data.get("entries", []):
            # Convert time period strings to TimeOfDay enum values
            time_periods: List[TimeOfDay] = []
            for period_str in entry_data.get("time_periods", []):
                try:
                    period = TimeOfDay[period_str.upper()]
                    time_periods.append(period)
                except KeyError:
                    log_warning(
                        f"Schedule for NPC '{npc_id}': invalid time period '{period_str}', skipping"
                    )

            if not time_periods:
                log_warning(
                    f"Schedule entry for NPC '{npc_id}' has no valid time periods, skipping"
                )
                continue

            # Validate entry fields
            if "map_id" not in entry_data:
                log_warning(
                    f"Schedule entry for NPC '{npc_id}' missing 'map_id', skipping"
                )
                continue
            if "x" not in entry_data:
                log_warning(
                    f"Schedule entry for NPC '{npc_id}' missing 'x', skipping"
                )
                continue
            if "y" not in entry_data:
                log_warning(
                    f"Schedule entry for NPC '{npc_id}' missing 'y', skipping"
                )
                continue

            entry = ScheduleEntry(
                time_periods=time_periods,
                map_id=entry_data["map_id"],
                x=entry_data["x"],
                y=entry_data["y"],
                activity=entry_data.get("activity"),
                shop_available=entry_data.get("shop_available", True),
                alternative_dialogue_id=entry_data.get("alternative_dialogue_id"),
            )
            entries.append(entry)

        schedule = NPCSchedule(
            npc_id=npc_id,
            default_map_id=schedule_data["default_map_id"],
            default_x=schedule_data["default_x"],
            default_y=schedule_data["default_y"],
            entries=entries,
        )
        schedules[npc_id] = schedule

    return ScheduleManager(schedules)
