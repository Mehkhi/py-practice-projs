"""NPC schedule data loader."""

from typing import Dict, List

from core.constants import NPC_SCHEDULES_JSON
from core.loaders.base import detach_json_data, ensure_dict, ensure_list, load_json_file, validate_required_keys
from core.logging_utils import log_schema_warning
from core.npc_schedules import NPCSchedule, ScheduleEntry, ScheduleManager
from core.time_system import TimeOfDay


def load_npc_schedules(
    filepath: str = NPC_SCHEDULES_JSON,
) -> ScheduleManager:
    """Load NPC schedules from JSON file.

    Args:
        filepath: Path to the NPC schedules JSON file

    Returns:
        ScheduleManager instance with loaded schedules, or empty manager if file missing
    """
    context = "npc schedule loader"
    data = load_json_file(
        filepath,
        default={"schedules": {}},
        context="Loading NPC schedules",
        warn_on_missing=True,
        copy_data=False,
    )

    data = ensure_dict(data, context=context, section="root")
    schedules: Dict[str, NPCSchedule] = {}
    schedules_data = ensure_dict(
        data.get("schedules", {}),
        context=context,
        section="schedules",
    )

    for npc_id, schedule_data in schedules_data.items():
        schedule_entry = detach_json_data(
            ensure_dict(
                schedule_data,
                context=context,
                section="schedule",
                identifier=npc_id,
            )
        )
        if not validate_required_keys(
            schedule_entry,
            ("default_map_id", "default_x", "default_y"),
            context=context,
            section="schedule",
            identifier=npc_id,
        ):
            continue

        # Parse schedule entries
        entries: List[ScheduleEntry] = []
        for entry_data in ensure_list(
            schedule_entry.get("entries", []),
            context=context,
            section="schedule.entries",
            identifier=npc_id,
        ):
            entry_entry = detach_json_data(
                ensure_dict(
                    entry_data,
                    context=context,
                    section="schedule.entry",
                    identifier=npc_id,
                )
            )
            # Convert time period strings to TimeOfDay enum values
            time_periods: List[TimeOfDay] = []
            for period_str in ensure_list(
                entry_entry.get("time_periods", []),
                context=context,
                section="schedule.entry.time_periods",
                identifier=npc_id,
            ):
                try:
                    period = TimeOfDay[period_str.upper()]
                    time_periods.append(period)
                except KeyError:
                    log_schema_warning(
                        context,
                        f"invalid time period '{period_str}', skipping value",
                        section="schedule.entry.time_periods",
                        identifier=npc_id,
                    )

            if not time_periods:
                log_schema_warning(
                    context,
                    "has no valid time periods, skipping entry",
                    section="schedule.entry",
                    identifier=npc_id,
                )
                continue

            if not validate_required_keys(
                entry_entry,
                ("map_id", "x", "y"),
                context=context,
                section="schedule.entry",
                identifier=npc_id,
            ):
                continue

            entry = ScheduleEntry(
                time_periods=time_periods,
                map_id=entry_entry["map_id"],
                x=entry_entry["x"],
                y=entry_entry["y"],
                activity=entry_entry.get("activity"),
                shop_available=entry_entry.get("shop_available", True),
                alternative_dialogue_id=entry_entry.get("alternative_dialogue_id"),
            )
            entries.append(entry)

        schedule = NPCSchedule(
            npc_id=npc_id,
            default_map_id=schedule_entry["default_map_id"],
            default_x=schedule_entry["default_x"],
            default_y=schedule_entry["default_y"],
            entries=entries,
        )
        schedules[npc_id] = schedule

    return ScheduleManager(schedules)
