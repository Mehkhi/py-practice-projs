"""Backward-compatible re-exports for loader functions.

All loader implementations now live under ``core.loaders``.
"""

from typing import Any, Optional

import core.loaders.base as _base

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


def load_json_file(
    path: str,
    default: Any = None,
    context: Optional[str] = None,
    warn_on_missing: bool = False,
) -> Any:
    """Compatibility wrapper that delegates to ``core.loaders.base``."""
    _base.log_warning = log_warning
    _base.log_debug = log_debug
    return _base.load_json_file(
        path,
        default=default,
        context=context,
        warn_on_missing=warn_on_missing,
    )


__all__ = [
    "build_bestiary_metadata",
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
]
