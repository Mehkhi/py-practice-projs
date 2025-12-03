"""Core game constants.

This module centralizes game constants used across multiple modules
for equipment, formations, and other core gameplay systems.
"""

import os
from typing import Dict, Tuple

# Equipment system constants
SUPPORTED_EQUIP_SLOTS: Tuple[str, ...] = ("weapon", "armor", "accessory")

# Formation positions and their combat effects
FORMATION_POSITIONS: Dict[str, Dict[str, float]] = {
    "front": {"defense_mod": -0.1, "attack_mod": 0.1, "aggro_mod": 1.5},   # More damage dealt/taken, draws aggro
    "middle": {"defense_mod": 0.0, "attack_mod": 0.0, "aggro_mod": 1.0},   # Balanced position
    "back": {"defense_mod": 0.1, "attack_mod": -0.1, "aggro_mod": 0.5},    # Less damage dealt/taken, avoids aggro
}

DEFAULT_FORMATION_POSITION: str = "middle"

# Screen dimension constants
DEFAULT_WINDOW_WIDTH: int = 640
DEFAULT_WINDOW_HEIGHT: int = 480

# Data file locations
DATA_DIR = "data"
ACHIEVEMENTS_JSON = os.path.join(DATA_DIR, "achievements.json")
ARENA_JSON = os.path.join(DATA_DIR, "arena.json")
BRAIN_TEASERS_JSON = os.path.join(DATA_DIR, "brain_teasers.json")
CHALLENGE_DUNGEONS_JSON = os.path.join(DATA_DIR, "challenge_dungeons.json")
FISHING_JSON = os.path.join(DATA_DIR, "fishing.json")
NPC_SCHEDULES_JSON = os.path.join(DATA_DIR, "npc_schedules.json")
POST_GAME_UNLOCKS_JSON = os.path.join(DATA_DIR, "post_game_unlocks.json")
PUZZLES_JSON = os.path.join(DATA_DIR, "puzzles.json")
SECRET_BOSSES_JSON = os.path.join(DATA_DIR, "secret_bosses.json")
SECRET_BOSS_HINTS_JSON = os.path.join(DATA_DIR, "secret_boss_hints.json")
TUTORIAL_TIPS_JSON = os.path.join(DATA_DIR, "tutorial_tips.json")
