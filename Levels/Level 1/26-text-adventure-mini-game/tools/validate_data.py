"""Validate game data files with strict schema enabled.

This script is meant for CI or local preflight checks. It enables strict
schema mode, loads all core data files, and fails fast if any loader
raises an error.

Usage:
    STRICT_SCHEMA=1 .venv/bin/python3 tools/validate_data.py

(STRICT_SCHEMA is enabled by default inside this script, but exporting it
explicitly is fine.)
"""

import os
import sys
import traceback
from typing import Callable, List, Tuple

# Ensure project root is on sys.path so ``core`` imports resolve when run
# from the repository root or via CI.
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Enable strict schema before importing loader modules so they respect the
# policy. If STRICT_SCHEMA was already set, leave it alone.
os.environ.setdefault("STRICT_SCHEMA", "1")

from core.constants import (
    ACHIEVEMENTS_JSON,
    ARENA_JSON,
    BRAIN_TEASERS_JSON,
    CHALLENGE_DUNGEONS_JSON,
    DATA_DIR,
    FISHING_JSON,
    NPC_SCHEDULES_JSON,
    POST_GAME_UNLOCKS_JSON,
    PUZZLES_JSON,
    SECRET_BOSSES_JSON,
    SECRET_BOSS_HINTS_JSON,
    TUTORIAL_TIPS_JSON,
)
from core.data_loader import (
    build_bestiary_metadata,
    load_achievements_from_json,
    load_arena_data,
    load_brain_teasers,
    load_challenge_dungeons,
    load_fishing_data,
    load_npc_schedules,
    load_post_game_unlocks,
    load_puzzles_from_json,
    load_secret_bosses,
    load_secret_boss_hints,
    load_tutorial_data,
)
from core.dialogue import load_dialogue_from_json
from core.encounters import load_encounters_from_json
from core.items import load_items_from_json
from core.quest_manager import load_quest_manager
from core.entities import load_party_members_from_json


def _data_path(filename: str) -> str:
    return os.path.join(DATA_DIR, filename)


def main() -> int:
    checks: List[Tuple[str, Callable[[], None]]] = [
        ("achievements", lambda: load_achievements_from_json(ACHIEVEMENTS_JSON)),
        ("arena", lambda: load_arena_data(ARENA_JSON)),
        ("brain_teasers", lambda: load_brain_teasers(BRAIN_TEASERS_JSON)),
        ("challenge_dungeons", lambda: load_challenge_dungeons(CHALLENGE_DUNGEONS_JSON)),
        ("fishing", lambda: load_fishing_data(FISHING_JSON)),
        ("npc_schedules", lambda: load_npc_schedules(NPC_SCHEDULES_JSON)),
        ("post_game_unlocks", lambda: load_post_game_unlocks(POST_GAME_UNLOCKS_JSON)),
        ("puzzles", lambda: load_puzzles_from_json(PUZZLES_JSON)),
        ("secret_bosses", lambda: load_secret_bosses(SECRET_BOSSES_JSON)),
        ("secret_boss_hints", lambda: load_secret_boss_hints(SECRET_BOSS_HINTS_JSON)),
        ("tutorial_data", lambda: load_tutorial_data(TUTORIAL_TIPS_JSON)),
        ("items", lambda: load_items_from_json(_data_path("items.json"))),
        ("encounters", lambda: load_encounters_from_json(_data_path("encounters.json"))),
        ("dialogue", lambda: load_dialogue_from_json(_data_path("dialogue.json"))),
        ("quests", lambda: load_quest_manager(_data_path("quests.json"))),
    ]

    errors: List[Tuple[str, str]] = []

    # Run checks and capture exceptions
    results = {}
    for name, func in checks:
        try:
            results[name] = func()
        except Exception:
            errors.append((name, traceback.format_exc()))

    # Run dependent checks that need prior data
    if "items" in results:
        try:
            load_party_members_from_json(_data_path("party_members.json"), items_db=results["items"])
        except Exception:
            errors.append(("party_members", traceback.format_exc()))

    if "encounters" in results:
        try:
            build_bestiary_metadata(results["encounters"] or {})
        except Exception:
            errors.append(("bestiary_metadata", traceback.format_exc()))

    if errors:
        sys.stderr.write("Data validation failed:\n")
        for name, tb in errors:
            sys.stderr.write(f"\n[name: {name}]\n{tb}\n")
        return 1

    sys.stdout.write("Data validation passed for: " + ", ".join(sorted(results.keys())) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
