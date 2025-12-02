"""Achievement serialization helpers."""

from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from core.achievements import AchievementManager


def serialize_achievements_state(manager: "AchievementManager") -> Dict[str, Any]:
    """Serialize all achievement-related state."""
    return {
        "achievements": [ach.to_dict() for ach in manager.achievements.values()],
        "daily_activities": {k: list(v) for k, v in manager._daily_activities.items()},
        "challenge_dungeon_times": manager._challenge_dungeon_times,
        "challenge_dungeon_pacifist": manager._challenge_dungeon_pacifist,
    }


def deserialize_achievements_state(manager: "AchievementManager", data: Dict[str, Any]) -> None:
    """Restore achievement-related state onto an existing manager."""
    ach_states = {a["id"]: a for a in data.get("achievements", [])}

    for ach_id, ach in manager.achievements.items():
        if ach_id in ach_states:
            state = ach_states[ach_id]
            ach.current_count = state.get("current_count", 0)
            ach.unlocked = state.get("unlocked", False)
            ach.unlock_time = state.get("unlock_time")

    daily_data = data.get("daily_activities", {})
    manager._daily_activities = {k: set(v) for k, v in daily_data.items()}

    manager._challenge_dungeon_times = data.get("challenge_dungeon_times", {})
    manager._challenge_dungeon_pacifist = data.get("challenge_dungeon_pacifist", {})
