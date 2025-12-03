"""Save file version migration logic.

This module handles migrating save files from older versions to the current version.
"""

import copy
import os
from datetime import datetime
from typing import Any, Dict, Set

from ..logging_utils import log_warning
from .serializer import DEFAULT_STARTING_MAP

# Track migration warnings to avoid spamming identical messages during recovery
_EMITTED_MIGRATION_WARNINGS: Set[str] = set()


def _is_migration_quiet() -> bool:
    """Check if migration warnings should be suppressed.

    Checks environment variable dynamically to support test patching.
    """
    return os.environ.get("SAVE_VALIDATION_QUIET", "").lower() in ("1", "true", "yes", "on")


def _log_migration_warning(message: str) -> None:
    """Optionally emit migration warnings (silence via SAVE_VALIDATION_QUIET=1)."""
    if _is_migration_quiet():
        return
    if message in _EMITTED_MIGRATION_WARNINGS:
        return
    _EMITTED_MIGRATION_WARNINGS.add(message)
    log_warning(message)


def get_save_version(data: Dict[str, Any]) -> int:
    """Extract save file version from loaded data, forgiving bad types."""
    meta = data.get("meta", {}) if isinstance(data, dict) else {}
    raw_version = meta.get("version", 0)
    try:
        return int(raw_version)
    except (TypeError, ValueError):
        _log_migration_warning(
            f"Save meta.version was invalid ({raw_version!r}); treating as version 0 for migration"
        )
        return 0


def migrate_save_data(data: Dict[str, Any], from_version: int, to_version: int) -> Dict[str, Any]:
    """Migrate save data from one version to another.

    Args:
        data: The save data to migrate
        from_version: Current version of the save data
        to_version: Target version to migrate to

    Returns:
        Migrated save data dictionary
    """
    if from_version >= to_version:
        return data

    # Deep copy to avoid mutating the original data
    migrated_data = copy.deepcopy(data)

    # Migration from version 0 to 1
    if from_version == 0 and to_version >= 1:
        migrated_data = _migrate_v0_to_v1(migrated_data)

    # Future migrations would be added here:
    # if from_version <= 1 and to_version >= 2:
    #     migrated_data = _migrate_v1_to_v2(migrated_data)

    return migrated_data


def _migrate_v0_to_v1(data: Dict[str, Any]) -> Dict[str, Any]:
    """Migrate save data from version 0 to version 1.

    Version 1 added:
    - meta.version field
    - meta.timestamp field (required)
    - meta.play_time_seconds field (required)
    - world.runtime_state for trigger and enemy states

    Args:
        data: Save data at version 0

    Returns:
        Save data migrated to version 1
    """
    # Ensure meta section exists
    if "meta" not in data:
        data["meta"] = {}

    # Add version field if missing
    if "version" not in data["meta"]:
        data["meta"]["version"] = 1
        _log_migration_warning("Migrated save file from version 0 to version 1: added version field")

    # Ensure required fields exist with defaults
    if "timestamp" not in data["meta"]:
        data["meta"]["timestamp"] = datetime.now().isoformat()
        _log_migration_warning("Migrated save file: added missing timestamp")

    if "play_time_seconds" not in data["meta"]:
        data["meta"]["play_time_seconds"] = 0.0
        _log_migration_warning("Migrated save file: added missing play_time_seconds")

    # Ensure world section has required fields
    if "world" not in data:
        data["world"] = {}

    if "current_map_id" not in data["world"]:
        data["world"]["current_map_id"] = DEFAULT_STARTING_MAP
        _log_migration_warning("Migrated save file: added missing current_map_id")

    if "flags" not in data["world"]:
        data["world"]["flags"] = {}
        _log_migration_warning("Migrated save file: added missing flags")

    if "runtime_state" not in data["world"]:
        data["world"]["runtime_state"] = {
            "trigger_states": {},
            "enemy_states": {}
        }
        _log_migration_warning("Migrated save file: added missing runtime_state")

    return data
