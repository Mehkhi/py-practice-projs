"""Achievement system for tracking player accomplishments."""

import json
import os
from datetime import datetime
from types import MethodType
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, TYPE_CHECKING

from .achievement_types import Achievement, AchievementCategory, AchievementRarity
from .achievements_config import EVENT_PAYLOAD_MAP, SIMPLE_TRIGGER_CONFIG
from .logging_utils import log_warning
from .save.serializers.achievement_serializer import (
    deserialize_achievements_state,
    serialize_achievements_state,
)

if TYPE_CHECKING:
    from engine.event_bus import EventBus


def _resolve_amount(args: Tuple[Any, ...], kwargs: Dict[str, Any], default: int = 1) -> int:
    """Pull an integer amount from positional or keyword args."""
    if "amount" in kwargs:
        try:
            return int(kwargs["amount"])
        except (TypeError, ValueError):
            return default
    if args:
        try:
            return int(args[0])
        except (TypeError, ValueError):
            return default
    return default


def _build_simple_handler(trigger_type: str, uses_amount: bool) -> Callable[..., List[str]]:
    """Create a small handler that delegates to _check_trigger."""
    def handler(self: "AchievementManager", target: str = "", *args: Any, **kwargs: Any) -> List[str]:
        amount = _resolve_amount(args, kwargs) if uses_amount else 1
        return self._check_trigger(trigger_type, target, amount)
    return handler


_SIMPLE_TRIGGER_HANDLERS: Dict[str, Callable[..., List[str]]] = {
    name: _build_simple_handler(cfg["trigger_type"], cfg.get("uses_amount", False))
    for name, cfg in SIMPLE_TRIGGER_CONFIG.items()
}


class AchievementManager:
    """Manages all achievements and tracks progress."""

    save_key: str = "achievements"

    def __init__(self, event_bus: Optional["EventBus"] = None) -> None:
        self.achievements: Dict[str, Achievement] = {}
        self._definitions: Dict[str, Dict[str, Any]] = {}
        self._pending_unlocks: List[Achievement] = []
        self._callbacks: List[Callable[[Achievement], None]] = []
        self._event_bus: Optional["EventBus"] = event_bus
        self._daily_activities: Dict[str, Set[str]] = {}
        self._challenge_dungeon_times: Dict[str, float] = {}
        self._challenge_dungeon_pacifist: Dict[str, bool] = {}

        if self._event_bus is not None:
            self._register_event_handlers()

    def _register_event_handlers(self) -> None:
        """Subscribe achievement handlers to the event bus."""
        if self._event_bus is None:
            return

        for event_name in EVENT_PAYLOAD_MAP:
            self._event_bus.subscribe(
                event_name,
                lambda payload, event_name=event_name: self._dispatch_simple_event(event_name, payload),
            )

        self._event_bus.subscribe("level_up", self._on_level_up_event)
        self._event_bus.subscribe("gold_changed", self._on_gold_changed_event)
        self._event_bus.subscribe("fish_caught", self._on_fish_caught_event)

    def _dispatch_simple_event(self, event_name: str, payload: Optional[Dict[str, Any]]) -> None:
        """Route simple event bus payloads into generic trigger handlers."""
        metadata = EVENT_PAYLOAD_MAP[event_name]
        payload = payload or {}
        target_key = metadata.get("target_key")
        amount_key = metadata.get("amount_key")
        target = str(payload.get(target_key, "")) if target_key else ""
        amount_value = payload.get(amount_key, 1) if amount_key else 1
        if amount_key:
            try:
                amount_value = int(amount_value)
            except (TypeError, ValueError):
                amount_value = 1
        handler = getattr(self, metadata["method"])
        handler(target, amount_value)

    def _on_level_up_event(self, payload: Dict[str, Any]) -> None:
        new_level = int(payload.get("new_level", 1))
        self.on_level_up(new_level)

    def _on_gold_changed_event(self, payload: Dict[str, Any]) -> None:
        total_gold = int(payload.get("total_gold", 0))
        self.on_gold_changed(total_gold)

    def _on_fish_caught_event(self, payload: Dict[str, Any]) -> None:
        self.on_fish_caught(
            str(payload.get("fish_id", "")),
            str(payload.get("rarity", "")),
            str(payload.get("size_category", "")),
            str(payload.get("time_of_day", "")),
            int(payload.get("unique_species_count", 0)),
        )

    def load_achievements(self, json_path: str) -> None:
        """Load achievement definitions from JSON file."""
        if not os.path.exists(json_path):
            return

        with open(json_path, "r") as f:
            data = json.load(f)

        self._definitions = {}
        self.achievements = {}
        for ach_data in data.get("achievements", []):
            ach_id = ach_data["id"]
            self._definitions[ach_id] = ach_data
            self.achievements[ach_id] = Achievement.from_definition(ach_data)

    def get_achievement(self, achievement_id: str) -> Optional[Achievement]:
        """Get an achievement by ID."""
        return self.achievements.get(achievement_id)

    def get_achievements_by_category(self, category: AchievementCategory) -> List[Achievement]:
        """Get all achievements in a category."""
        return [a for a in self.achievements.values() if a.category == category]

    def get_unlocked_achievements(self) -> List[Achievement]:
        """Get all unlocked achievements."""
        return [a for a in self.achievements.values() if a.unlocked]

    def get_total_points(self) -> int:
        """Get total achievement points earned."""
        return sum(a.points for a in self.achievements.values() if a.unlocked)

    def get_max_points(self) -> int:
        """Get maximum possible achievement points."""
        return sum(a.points for a in self.achievements.values())

    def get_completion_by_category(self) -> Dict[str, Tuple[int, int]]:
        """Get (unlocked, total) achievements per category."""
        result: Dict[str, List[int]] = {}
        for ach in self.achievements.values():
            cat = ach.category.value
            if cat not in result:
                result[cat] = [0, 0]
            result[cat][1] += 1
            if ach.unlocked:
                result[cat][0] += 1
        return {k: tuple(v) for k, v in result.items()}

    def get_unlocked_count(self) -> int:
        """Get count of unlocked achievements."""
        return len(self.get_unlocked_achievements())

    def _check_prerequisites(self, achievement: Achievement) -> bool:
        """Check if all prerequisites are met for an achievement."""
        for req_id in achievement.required_achievements:
            req_ach = self.achievements.get(req_id)
            if not req_ach or not req_ach.unlocked:
                return False
        return True

    def _try_unlock(self, achievement: Achievement, amount: int = 1) -> bool:
        """Try to update and unlock an achievement. Returns True if newly unlocked."""
        if achievement.unlocked:
            return False
        if not self._check_prerequisites(achievement):
            return False
        if achievement.update_progress(amount):
            for callback in self._callbacks:
                try:
                    callback(achievement)
                except Exception as e:
                    log_warning(f"Achievement callback error: {e}")
            self._pending_unlocks.append(achievement)
            return True
        return False

    def _force_unlock(self, achievement: Achievement) -> bool:
        """Force unlock an achievement regardless of current progress."""
        if achievement.unlocked:
            return False
        if not self._check_prerequisites(achievement):
            return False

        achievement.unlocked = True
        achievement.current_count = achievement.target_count
        achievement.unlock_time = datetime.now().isoformat()

        for callback in self._callbacks:
            try:
                callback(achievement)
            except Exception as e:
                log_warning(f"Achievement callback error: {e}")
        self._pending_unlocks.append(achievement)
        return True

    def register_callback(self, callback: Callable[[Achievement], None]) -> None:
        """Register a callback to be called when an achievement is unlocked."""
        self._callbacks.append(callback)

    def unregister_callback(self, callback: Callable[[Achievement], None]) -> None:
        """Unregister a previously registered callback."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def pop_pending_unlock(self) -> Optional[Achievement]:
        """Pop the next pending unlock for UI display."""
        if self._pending_unlocks:
            return self._pending_unlocks.pop(0)
        return None

    def __getattr__(self, name: str) -> Any:
        """Dynamically expose simple trigger handlers to keep the public API intact."""
        handler = _SIMPLE_TRIGGER_HANDLERS.get(name)
        if handler:
            return MethodType(handler, self)
        raise AttributeError(f"{self.__class__.__name__} has no attribute '{name}'")

    def _check_trigger(self, trigger_type: str, target: str = "", amount: int = 1) -> List[str]:
        """Generic trigger handler used by most event callbacks."""
        unlocked: List[str] = []
        for ach in self.achievements.values():
            if ach.trigger_type != trigger_type:
                continue
            if ach.trigger_target and ach.trigger_target != target:
                continue
            if self._try_unlock(ach, amount):
                unlocked.append(ach.id)
        return unlocked

    def _check_threshold_trigger(self, trigger_type: str, current_value: int, default_target: int = 0) -> List[str]:
        """Check achievements that unlock when a numeric threshold is met."""
        unlocked: List[str] = []
        for ach in self.achievements.values():
            if ach.trigger_type != trigger_type:
                continue
            target_value = int(ach.trigger_target) if ach.trigger_target else default_target
            if current_value >= target_value and self._try_unlock(ach):
                unlocked.append(ach.id)
        return unlocked

    def on_level_up(self, new_level: int) -> List[str]:
        """Called when player levels up."""
        return self._check_threshold_trigger("level", new_level, default_target=1)

    def on_gold_changed(self, total_gold: int) -> List[str]:
        """Called when gold amount changes."""
        return self._check_threshold_trigger("gold", total_gold)

    def on_fish_caught(
        self,
        fish_id: str,
        rarity: str,
        size_category: str,
        time_of_day: str,
        unique_species_count: int,
    ) -> List[str]:
        """Called when a fish is caught."""
        unlocked = []
        unlocked.extend(self._check_trigger("fish_caught"))
        unlocked.extend(self._handle_fish_species(unique_species_count))
        unlocked.extend(self._check_trigger("fish_rarity", rarity))
        unlocked.extend(self._check_trigger("fish_size_category", size_category))
        unlocked.extend(self._check_trigger("fish_time", time_of_day))
        return unlocked

    def _handle_fish_species(self, unique_species_count: int) -> List[str]:
        unlocked: List[str] = []
        for ach in self.achievements.values():
            if ach.trigger_type != "fish_species":
                continue
            if unique_species_count >= ach.target_count:
                if self._try_unlock(ach):
                    unlocked.append(ach.id)
            elif not ach.unlocked:
                ach.current_count = unique_species_count
        return unlocked

    def check_stat_achievements(self, stats: Dict[str, Any]) -> List[str]:
        """Check achievements based on cumulative stats."""
        unlocked = []
        for ach in self.achievements.values():
            if ach.trigger_type != "stat":
                continue
            stat_name = ach.trigger_target
            if stat_name in stats and not ach.unlocked:
                current_value = stats[stat_name]
                ach.current_count = min(current_value, ach.target_count)
                if ach.current_count >= ach.target_count:
                    if self._force_unlock(ach):
                        unlocked.append(ach.id)
        return unlocked

    def on_daily_activity(self, activity_type: str, current_date: Optional[str] = None) -> List[str]:
        """Track daily activities for cross-system achievements."""
        if current_date is None:
            current_date = datetime.now().date().isoformat()

        if current_date not in self._daily_activities:
            self._daily_activities[current_date] = set()
        self._daily_activities[current_date].add(activity_type)

        unlocked = []
        activities_today = self._daily_activities[current_date]
        required_activities = {"fish_caught", "gambling_win", "puzzle_solved"}

        if required_activities.issubset(activities_today):
            ach = self.achievements.get("jack_of_all_trades")
            if ach and not ach.unlocked and self._try_unlock(ach):
                unlocked.append(ach.id)

        return unlocked

    def on_challenge_dungeon_complete(
        self,
        dungeon_id: str,
        completion_time: float,
        pacifist: bool = False,
    ) -> List[str]:
        """Track challenge dungeon completion for speed and pacifist achievements."""
        unlocked = []
        self._challenge_dungeon_times[dungeon_id] = completion_time

        if completion_time < 300:
            ach = self.achievements.get("speed_demon")
            if ach and not ach.unlocked and self._try_unlock(ach):
                unlocked.append(ach.id)

        if pacifist:
            self._challenge_dungeon_pacifist[dungeon_id] = True
            ach = self.achievements.get("pacifist_run")
            if ach and not ach.unlocked and self._try_unlock(ach):
                unlocked.append(ach.id)

        return unlocked

    def check_composite_achievements(
        self,
        fishing_proficiency: Optional[int] = None,
        gambling_proficiency: Optional[int] = None,
        puzzle_proficiency: Optional[int] = None,
    ) -> List[str]:
        """Check composite achievements that require multiple systems."""
        unlocked = []
        if (
            fishing_proficiency is not None
            and gambling_proficiency is not None
            and puzzle_proficiency is not None
        ):
            max_proficiency = 100
            if (
                fishing_proficiency >= max_proficiency
                and gambling_proficiency >= max_proficiency
                and puzzle_proficiency >= max_proficiency
            ):
                ach = self.achievements.get("master_of_all")
                if ach and not ach.unlocked and self._try_unlock(ach):
                    unlocked.append(ach.id)
        return unlocked

    def serialize_state(self) -> Dict[str, Any]:
        """Serialize all achievement states for saving."""
        return serialize_achievements_state(self)

    def serialize(self) -> Dict[str, Any]:
        """Serialize state (Saveable protocol)."""
        return self.serialize_state()

    def deserialize_state(self, data: Dict[str, Any]) -> None:
        """Restore achievement states from saved data."""
        deserialize_achievements_state(self, data)

    def deserialize_into(self, data: Dict[str, Any]) -> None:
        """Restore state from saved data (Saveable protocol)."""
        self.deserialize_state(data)


def load_achievement_manager(
    json_path: str = "data/achievements.json",
    event_bus: Optional["EventBus"] = None,
) -> AchievementManager:
    """Load and return an AchievementManager with achievements from JSON."""
    manager = AchievementManager(event_bus=event_bus)
    manager.load_achievements(json_path)
    return manager
