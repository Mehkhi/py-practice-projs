"""Backward-compatible re-exports for loader functions.

All loader implementations now live under ``core.loaders``.
"""

import os
from typing import Any, Dict, Mapping, Optional, Sequence, Tuple

import core.loaders.base as _base

from core.constants import (
    ACHIEVEMENTS_JSON,
    ARENA_JSON,
    BRAIN_TEASERS_JSON,
    CHALLENGE_DUNGEONS_JSON,
    FISHING_JSON,
    NPC_SCHEDULES_JSON,
    POST_GAME_UNLOCKS_JSON,
    PUZZLES_JSON,
    SECRET_BOSSES_JSON,
    SECRET_BOSS_HINTS_JSON,
    TUTORIAL_TIPS_JSON,
)
from core.logging_utils import log_debug, log_warning
from core.loaders.achievement_loader import load_achievements_from_json
from core.loaders.arena_loader import load_arena_data
from core.loaders.bestiary_loader import build_bestiary_metadata
from core.loaders.brain_teaser_loader import load_brain_teasers
from core.loaders.challenge_loader import load_challenge_dungeons
from core.loaders.fishing_loader import load_fishing_data
from core.loaders.npc_loader import load_npc_schedules
from core.loaders.post_game_loader import load_post_game_unlocks
from core.loaders.puzzle_loader import load_puzzles_from_json
from core.loaders.secret_boss_loader import (
    load_secret_boss_hints,
    load_secret_bosses,
)
from core.loaders.tutorial_loader import load_tutorial_data, load_tutorial_tips

# Paths we routinely touch at startup or per-scene. Used by warm_data_caches().
DEFAULT_WARMUP_PATHS: Sequence[str] = (
    ACHIEVEMENTS_JSON,
    ARENA_JSON,
    BRAIN_TEASERS_JSON,
    CHALLENGE_DUNGEONS_JSON,
    FISHING_JSON,
    NPC_SCHEDULES_JSON,
    POST_GAME_UNLOCKS_JSON,
    PUZZLES_JSON,
    SECRET_BOSSES_JSON,
    SECRET_BOSS_HINTS_JSON,
    TUTORIAL_TIPS_JSON,
    os.path.join("data", "skills.json"),
    os.path.join("data", "status_icons.json"),
    os.path.join("data", "items.json"),
    os.path.join("data", "encounters.json"),
    os.path.join("data", "dialogue.json"),
)

# Optional lookup indexes to precompute during warmup.
DEFAULT_LOOKUPS: Mapping[str, Sequence[Tuple[str, str]]] = {
    ACHIEVEMENTS_JSON: (("achievements", "id"),),
    BRAIN_TEASERS_JSON: (("teasers", "teaser_id"),),
    CHALLENGE_DUNGEONS_JSON: (
        ("dungeons", "dungeon_id"),
        ("modifiers", "modifier_id"),
    ),
    FISHING_JSON: (
        ("fish", "fish_id"),
        ("spots", "spot_id"),
    ),
    NPC_SCHEDULES_JSON: (("schedules", "npc_id"),),
    PUZZLES_JSON: (("puzzles", "puzzle_id"),),
    SECRET_BOSSES_JSON: (("bosses", "boss_id"),),
    SECRET_BOSS_HINTS_JSON: (("hints", "hint_id"),),
    TUTORIAL_TIPS_JSON: (
        ("tips", "tip_id"),
        ("help_entries", "entry_id"),
    ),
    os.path.join("data", "skills.json"): (("skills", "id"),),
    os.path.join("data", "items.json"): (("items", "id"),),
}


def _bind_logging() -> None:
    """Ensure the base module uses the same logger bindings as this facade."""
    _base.log_warning = log_warning
    _base.log_debug = log_debug


def load_json_file(
    path: str,
    default: Any = None,
    context: Optional[str] = None,
    warn_on_missing: bool = False,
    *,
    use_cache: bool = True,
    force_reload: bool = False,
    copy_data: bool = True,
) -> Any:
    """Compatibility wrapper that delegates to ``core.loaders.base`` with caching."""
    _bind_logging()
    return _base.load_json_file(
        path,
        default=default,
        context=context,
        warn_on_missing=warn_on_missing,
        use_cache=use_cache,
        force_reload=force_reload,
        copy_data=copy_data,
    )


def get_cached_lookup(
    path: str,
    section: str,
    key_field: str = "id",
    *,
    default: Any = None,
    copy_lookup: bool = True,
) -> Dict[str, Any]:
    """Facade for ``core.loaders.base.get_cached_lookup``."""
    _bind_logging()
    return _base.get_cached_lookup(
        path,
        section,
        key_field,
        default=default,
        copy_lookup=copy_lookup,
    )


def clear_json_cache(path: Optional[str] = None) -> None:
    """Clear cached JSON payloads and lookup maps."""
    _bind_logging()
    _base.clear_json_cache(path)


def warm_data_caches(
    paths: Sequence[str] = DEFAULT_WARMUP_PATHS,
    *,
    warn_on_missing: bool = False,
    lookups: Optional[Mapping[str, Sequence[Tuple[str, str]]]] = None,
) -> Dict[str, Any]:
    """
    Warm the shared JSON cache for commonly used files and optional lookups.

    Args:
        paths: Iterable of paths to preload (defaults to DEFAULT_WARMUP_PATHS)
        warn_on_missing: Whether to warn about missing files during warmup
        lookups: Optional mapping of path -> iterable of (section, key_field)
            pairs to precompute lookup dictionaries for. Defaults to
            DEFAULT_LOOKUPS when omitted.
    """
    _bind_logging()
    lookup_map = DEFAULT_LOOKUPS if lookups is None else lookups
    return _base.warm_json_cache(
        paths,
        warn_on_missing=warn_on_missing,
        lookups=lookup_map,
    )


__all__ = [
    "build_bestiary_metadata",
    "clear_json_cache",
    "get_cached_lookup",
    "load_achievements_from_json",
    "load_arena_data",
    "load_brain_teasers",
    "load_challenge_dungeons",
    "load_fishing_data",
    "load_json_file",
    "load_npc_schedules",
    "load_post_game_unlocks",
    "load_puzzles_from_json",
    "load_secret_bosses",
    "load_secret_boss_hints",
    "load_tutorial_data",
    "load_tutorial_tips",
    "warm_data_caches",
    "DEFAULT_LOOKUPS",
    "DEFAULT_WARMUP_PATHS",
]
