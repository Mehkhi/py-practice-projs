"""Domain-specific data loader package.

This module re-exports common loader functions for convenience.
"""

from core.loaders.base import (
    clear_json_cache,
    get_cached_lookup,
    load_json_file,
    warm_json_cache,
)
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
    load_secret_bosses,
    load_secret_boss_hints,
)
from core.loaders.tutorial_loader import load_tutorial_data, load_tutorial_tips

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
    "warm_json_cache",
]
