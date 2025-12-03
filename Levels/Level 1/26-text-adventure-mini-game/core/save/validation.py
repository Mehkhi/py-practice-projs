"""Validation and recovery logic for save data.

This module contains functions for validating save file structure and
recovering from partial corruption.
"""

import copy
import os
from dataclasses import MISSING, dataclass, fields
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

from ..logging_utils import log_warning
from ..stats import Stats, create_default_player_stats
from .serializer import DEFAULT_STARTING_MAP, SAVE_FILE_VERSION, serialize_entity_stats

# Track validation warnings to avoid repeating the same message many times
_EMITTED_VALIDATION_WARNINGS: Set[str] = set()


def _is_validation_quiet() -> bool:
    """Check if validation warnings should be suppressed.

    Checks environment variable dynamically to support test patching.
    """
    return os.environ.get("SAVE_VALIDATION_QUIET", "").lower() in ("1", "true", "yes", "on")


def _log_validation_warning(message: str) -> None:
    """Optionally emit validation warnings (silence via SAVE_VALIDATION_QUIET=1)."""
    if _is_validation_quiet():
        return
    if message in _EMITTED_VALIDATION_WARNINGS:
        return
    _EMITTED_VALIDATION_WARNINGS.add(message)
    log_warning(message)


@dataclass(frozen=True)
class FieldSpec:
    """Schema entry describing expected type and default handling."""
    default: Any
    type_check: Union[type, Tuple[type, ...]]
    required: bool = True
    default_factory: Optional[Callable[[], Any]] = None

    def build_default(self) -> Any:
        """Return a fresh default value for this field."""
        if self.default_factory is not None:
            return self.default_factory()
        return copy.deepcopy(self.default)


def _describe_type(type_check: Union[type, Tuple[type, ...]]) -> str:
    """Human-readable description for type validation errors."""
    if isinstance(type_check, tuple):
        if type_check == (int, float):
            return "a number"
        joined = ", ".join(t.__name__ for t in type_check)
        return f"one of ({joined})"
    return f"a {type_check.__name__}"


def _infer_type_check(default: Any) -> Union[type, Tuple[type, ...]]:
    """Map default value to a suitable isinstance check."""
    if isinstance(default, (int, float)):
        return (int, float)
    return type(default)


def _get_required_stat_fields(serialized_keys: Set[str]) -> Set[str]:
    """Required Stats fields have no dataclass defaults and are serialized."""
    required: Set[str] = set()
    for field_info in fields(Stats):
        has_default = field_info.default is not MISSING or field_info.default_factory is not MISSING
        if not has_default and field_info.name in serialized_keys:
            required.add(field_info.name)
    return required


def _build_stat_schema(default_stats: Dict[str, Any], required_fields: Set[str]) -> Dict[str, FieldSpec]:
    """Create schema entries for all serialized stats fields."""
    schema: Dict[str, FieldSpec] = {}
    for key, value in default_stats.items():
        schema[key] = FieldSpec(
            default=value,
            type_check=_infer_type_check(value),
            required=key in required_fields
        )
    return schema


DEFAULT_STATS_DATA = serialize_entity_stats(create_default_player_stats()) or {}
REQUIRED_STAT_FIELDS = _get_required_stat_fields(set(DEFAULT_STATS_DATA.keys()))
STATS_SCHEMA = _build_stat_schema(DEFAULT_STATS_DATA, REQUIRED_STAT_FIELDS)

DEFAULT_RUNTIME_STATE: Dict[str, Dict[str, Dict[str, bool]]] = {
    "trigger_states": {},
    "enemy_states": {}
}

META_SCHEMA: Dict[str, FieldSpec] = {
    "version": FieldSpec(SAVE_FILE_VERSION, int, required=False),
    "timestamp": FieldSpec("", str, default_factory=lambda: datetime.now().isoformat()),
    "play_time_seconds": FieldSpec(0.0, (int, float))
}

WORLD_RUNTIME_SCHEMA: Dict[str, FieldSpec] = {
    "trigger_states": FieldSpec({}, dict, required=False),
    "enemy_states": FieldSpec({}, dict, required=False)
}

WORLD_SCHEMA: Dict[str, FieldSpec] = {
    "current_map_id": FieldSpec(DEFAULT_STARTING_MAP, str),
    "flags": FieldSpec({}, dict),
    "visited_maps": FieldSpec([], list, required=False),
    "runtime_state": FieldSpec(DEFAULT_RUNTIME_STATE, dict, required=False)
}

PLAYER_SCHEMA: Dict[str, FieldSpec] = {
    "entity_id": FieldSpec("player_1", str),
    "name": FieldSpec("Hero", str),
    "x": FieldSpec(0, (int, float)),
    "y": FieldSpec(0, (int, float)),
    "inventory": FieldSpec({}, dict),
    "hotbar_slots": FieldSpec({}, dict, required=False),
    "equipment": FieldSpec({}, dict, required=False),
    "skills": FieldSpec([], list, required=False),
    "learned_moves": FieldSpec([], list, required=False),
    "stats": FieldSpec(DEFAULT_STATS_DATA, dict),
    "memory_value": FieldSpec(0, (int, float), required=False),
    "memory_stat_type": FieldSpec(None, (str, type(None)), required=False),
    "party": FieldSpec([], list, required=False),
    "party_formation": FieldSpec({}, dict, required=False),
    "formation_position": FieldSpec("front", str, required=False),
    "skill_tree_progress": FieldSpec(None, (dict, type(None)), required=False),
    "player_class": FieldSpec(None, (str, type(None)), required=False),
    "player_subclass": FieldSpec(None, (str, type(None)), required=False),
    "crafting_progress": FieldSpec(None, (dict, type(None)), required=False),
    "bestiary": FieldSpec(None, (dict, type(None)), required=False)
}

OPTIONAL_SECTIONS: List[str] = [
    "quests", "fishing", "gambling", "arena", "puzzles", "brain_teasers",
    "challenge_dungeons", "secret_bosses", "post_game", "tutorial",
    "achievements", "day_night", "weather", "npc_schedules"
]


def _validate_fields(
    section: Dict[str, Any],
    schema: Dict[str, FieldSpec],
    section_name: str,
    errors: List[str]
) -> None:
    """Validate a dictionary against a schema."""
    for key, spec in schema.items():
        if key not in section:
            if spec.required:
                errors.append(f"Missing '{section_name}.{key}'")
            continue
        if not isinstance(section.get(key), spec.type_check):
            expected = _describe_type(spec.type_check)
            errors.append(f"'{section_name}.{key}' must be {expected}")


def _apply_schema(section: Dict[str, Any], schema: Dict[str, FieldSpec], path: str) -> None:
    """Ensure a section contains all schema fields with correct types."""
    for key, spec in schema.items():
        ensure_field(section, key, spec.build_default(), spec.type_check, path)


def _ensure_section_dict(target: Dict[str, Any], key: str) -> Dict[str, Any]:
    """Ensure a top-level section exists and is a dictionary."""
    if key not in target:
        target[key] = {}
        _log_validation_warning(f"Recovering save: added missing '{key}' section")
    section = target.get(key)
    if not isinstance(section, dict):
        section = {}
        target[key] = section
    return section


def validate_save_data(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate save file structure and required fields.

    Args:
        data: The loaded save data dictionary

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors: List[str] = []

    if not isinstance(data, dict):
        return (False, ["Save data must be a dictionary"])

    for section_name, schema in (("meta", META_SCHEMA), ("world", WORLD_SCHEMA), ("player", PLAYER_SCHEMA)):
        if section_name not in data:
            errors.append(f"Missing '{section_name}' section")
            continue
        section = data.get(section_name)
        if not isinstance(section, dict):
            errors.append(f"'{section_name}' must be a dictionary")
            continue
        _validate_fields(section, schema, section_name, errors)
        if section_name == "world" and isinstance(section.get("runtime_state"), dict):
            _validate_fields(section["runtime_state"], WORLD_RUNTIME_SCHEMA, "world.runtime_state", errors)

    player = data.get("player")
    if isinstance(player, dict) and isinstance(player.get("stats"), dict):
        _validate_fields(player["stats"], STATS_SCHEMA, "player.stats", errors)

    for section in OPTIONAL_SECTIONS:
        if section in data and not isinstance(data[section], dict):
            errors.append(f"'{section}' must be a dictionary")

    if "quests" in data and isinstance(data["quests"], dict):
        if "active_quests" in data["quests"] and not isinstance(data["quests"]["active_quests"], dict):
            errors.append("'quests.active_quests' must be a dictionary")
        if "completed_quests" in data["quests"] and not isinstance(data["quests"]["completed_quests"], dict):
            errors.append("'quests.completed_quests' must be a dictionary")

    if "fishing" in data and isinstance(data["fishing"], dict):
        if "player_records" in data["fishing"] and not isinstance(data["fishing"]["player_records"], dict):
            errors.append("'fishing.player_records' must be a dictionary")

    if "achievements" in data and isinstance(data["achievements"], dict):
        if "achievements" in data["achievements"] and not isinstance(data["achievements"]["achievements"], list):
            errors.append("'achievements.achievements' must be a list")

    if "post_game" in data and isinstance(data["post_game"], dict):
        if "final_boss_defeated" in data["post_game"] and not isinstance(data["post_game"]["final_boss_defeated"], bool):
            errors.append("'post_game.final_boss_defeated' must be a boolean")

    return (len(errors) == 0, errors)


def ensure_field(
    data: Dict[str, Any],
    key: str,
    default: Any,
    type_check: Union[type, Tuple[type, ...]],
    log_path: str = ""
) -> bool:
    """Ensure a field exists in data with the correct type, setting default if not.

    Args:
        data: Dictionary to check/modify
        key: Key to ensure exists
        default: Default value if missing or wrong type
        type_check: Type or tuple of types to check against
        log_path: Path prefix for log message (e.g. 'player.stats')

    Returns:
        True if the field was fixed, False if it was already valid
    """
    if key not in data or not isinstance(data.get(key), type_check):
        data[key] = default
        if log_path:
            _log_validation_warning(f"Recovering save: fixed '{log_path}.{key}'")
        return True
    return False


def recover_partial_save(data: Dict[str, Any]) -> Dict[str, Any]:
    """Attempt to recover from partial save corruption by providing defaults.

    Args:
        data: Partially corrupted save data

    Returns:
        Recovered save data with defaults filled in
    """
    # Deep copy to avoid mutating the original data
    recovered = copy.deepcopy(data) if isinstance(data, dict) else {}

    meta = _ensure_section_dict(recovered, "meta")
    _apply_schema(meta, META_SCHEMA, "meta")

    world = _ensure_section_dict(recovered, "world")
    _apply_schema(world, WORLD_SCHEMA, "world")
    runtime_state = world.get("runtime_state")
    if isinstance(runtime_state, dict):
        _apply_schema(runtime_state, WORLD_RUNTIME_SCHEMA, "world.runtime_state")
    else:
        ensure_field(world, "runtime_state", WORLD_SCHEMA["runtime_state"].build_default(), dict, "world")

    player = _ensure_section_dict(recovered, "player")
    _apply_schema(player, PLAYER_SCHEMA, "player")

    stats_data = player.get("stats")
    if not isinstance(stats_data, dict):
        player["stats"] = PLAYER_SCHEMA["stats"].build_default()
        _log_validation_warning("Recovering save: fixed 'player.stats' with defaults")
        stats_data = player["stats"]

    _apply_schema(stats_data, STATS_SCHEMA, "player.stats")

    return recovered
