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
DEFAULT_RESIZABLE: bool = True
DEFAULT_START_FULLSCREEN: bool = False
DEFAULT_MIN_WINDOW_WIDTH: int = 640
DEFAULT_MIN_WINDOW_HEIGHT: int = 480

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

# --- AI Behavior Multipliers ---
# Multipliers for AI behavior types when selecting actions
AI_AGGRESSIVE_ATTACK_MULTIPLIER = 2.0  # Boost attack action weights
AI_AGGRESSIVE_SKILL_MULTIPLIER = 1.5  # Boost physical/fire skill weights
AI_DEFENSIVE_GUARD_MULTIPLIER = 2.0  # Boost guard/self-targeting weights
AI_DEFENSIVE_HOLY_MULTIPLIER = 1.5  # Boost holy skill weights
AI_SUPPORT_ITEM_MULTIPLIER = 2.0  # Boost item/ally-targeting weights
AI_SUPPORT_ALLY_SKILL_MULTIPLIER = 1.5  # Boost ally skill weights
AI_FALLBACK_GUARD_HP_THRESHOLD = 0.35  # Use guard fallback when HP <= 35%
AI_RULE_CACHE_MAX_SIZE = 50  # Maximum size of AI rule match cache

# --- Status Effect Values ---
# Damage/heal per stack per turn for status effects
STATUS_POISON_DAMAGE_PER_STACK = 5
STATUS_BLEED_DAMAGE_PER_STACK = 3
STATUS_TERROR_SP_DRAIN_PER_STACK = 2
STATUS_BURN_DAMAGE_PER_STACK = 4
STATUS_SLEEP_HEAL_PER_STACK = 2
STATUS_FROZEN_DAMAGE_PER_STACK = 2  # Cold damage (less than burn since frozen prevents action)
STATUS_STUN_SP_DRAIN_PER_STACK = 1  # Mental strain (less than terror since stun prevents action)
STATUS_CONFUSION_SELF_DAMAGE_PER_STACK = 2  # Panic-induced self-harm
STATUS_CONFUSION_DAMAGE_CHANCE = 0.3  # 30% chance to self-damage per tick


# --- Element Multipliers ---
# Damage multipliers for elemental affinities
ELEMENT_WEAK_MULTIPLIER = 1.5  # 50% more damage when hitting weakness
ELEMENT_RESIST_MULTIPLIER = 0.5  # 50% less damage when hitting resistance
ELEMENT_IMMUNE_MULTIPLIER = 0.0  # No damage when immune
ELEMENT_ABSORB_MULTIPLIER = -0.5  # Heals for 50% of damage when absorbing

# --- Stat Reduction Multipliers ---
# Multipliers for stat reductions from status effects and injuries
STAT_REDUCTION_ARM_MISSING = 0.7  # 30% reduction when arm is missing
STAT_REDUCTION_LEG_MISSING = 0.6  # 40% reduction when leg is missing
STAT_REDUCTION_BURN_ATTACK_MIN = 0.2  # Minimum attack multiplier from burn
STAT_REDUCTION_BURN_ATTACK_PER_STACK = 0.2  # Attack reduction per burn stack
STAT_REDUCTION_FROZEN_SPEED = 0.1  # 90% speed reduction when frozen

# --- Combat System Multipliers ---
# Combo attack bonuses
COMBO_CHAIN_ATTACK_BONUS_PER_ATTACKER = 0.2  # +20% per additional attacker
COMBO_ALL_OUT_ATTACK_MULTIPLIER = 1.5  # +50% damage when all players attack same target
COMBO_ELEMENTAL_FUSION_BONUS = 0.15  # +15% damage for elemental variety
CRITICAL_HIT_MULTIPLIER = 1.5  # Critical hit damage multiplier
FLEE_LUCK_BONUS_MAX = 0.10  # Maximum 10% luck bonus for fleeing
FLEE_LUCK_DIVISOR = 200.0  # Divisor for luck-to-flee-bonus conversion
FLEE_TURN_BONUS_PER_TURN = 0.05  # 5% per turn, up to max
FLEE_TURN_BONUS_MAX = 0.25  # Maximum 25% turn bonus for fleeing

# --- Enemy Scaling Multipliers ---
# Level scaling multipliers for enemy rewards
ENEMY_EXP_LEVEL_MULTIPLIER = 0.20  # +20% EXP per level above 1
ENEMY_GOLD_LEVEL_MULTIPLIER = 0.15  # +15% gold per level above 1
