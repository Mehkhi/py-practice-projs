"""Enemy stat scaling and reward calculations.

This module contains functions for scaling enemy stats based on level and difficulty,
as well as calculating EXP and gold rewards for defeating enemies.
"""

from typing import Dict
from core.constants import (
    ENEMY_EXP_LEVEL_MULTIPLIER,
    ENEMY_GOLD_LEVEL_MULTIPLIER,
)


# --- Enemy Level Scaling ---

# Difficulty multipliers for enemy stats
DIFFICULTY_STAT_MULTIPLIERS: Dict[str, float] = {
    "easy": 0.75,
    "normal": 1.0,
    "hard": 1.25,
    "elite": 1.5,
    "boss": 2.0,
}

# Difficulty multipliers for rewards (EXP, gold, drop rates)
DIFFICULTY_REWARD_MULTIPLIERS: Dict[str, float] = {
    "easy": 0.5,
    "normal": 1.0,
    "hard": 1.5,
    "elite": 2.0,
    "boss": 3.0,
}

# Per-level stat scaling for enemies (percentage increase per level above 1)
ENEMY_LEVEL_STAT_SCALING: Dict[str, float] = {
    "max_hp": 0.15,    # +15% per level
    "attack": 0.10,    # +10% per level
    "defense": 0.10,   # +10% per level
    "magic": 0.10,     # +10% per level
    "speed": 0.05,     # +5% per level
    "luck": 0.05,      # +5% per level
    "max_sp": 0.08,    # +8% per level
}

# Base EXP reward per enemy level
BASE_ENEMY_EXP_PER_LEVEL = 15

# Base gold reward per enemy level
BASE_ENEMY_GOLD_PER_LEVEL = 5


def scale_enemy_stat(base_value: int, enemy_level: int, stat_name: str, difficulty: str = "normal") -> int:
    """
    Scale an enemy's base stat based on their level and difficulty.

    Args:
        base_value: The base stat value defined in the encounter
        enemy_level: The enemy's level (1-10)
        stat_name: The stat being scaled (e.g., "max_hp", "attack")
        difficulty: The enemy's difficulty tier

    Returns:
        The scaled stat value as an integer
    """
    # Get scaling factor for this stat (default to 10% if not specified)
    level_scaling = ENEMY_LEVEL_STAT_SCALING.get(stat_name, 0.10)

    # Calculate level multiplier (level 1 = 1.0, level 2 = 1.0 + scaling, etc.)
    level_multiplier = 1.0 + (enemy_level - 1) * level_scaling

    # Get difficulty multiplier
    difficulty_multiplier = DIFFICULTY_STAT_MULTIPLIERS.get(difficulty, 1.0)

    # Apply both multipliers
    scaled_value = base_value * level_multiplier * difficulty_multiplier

    return max(1, int(scaled_value))


def calculate_enemy_exp_reward(enemy_level: int, difficulty: str = "normal", base_exp: int = 0) -> int:
    """
    Calculate EXP reward for defeating an enemy.

    Args:
        enemy_level: The enemy's level
        difficulty: The enemy's difficulty tier
        base_exp: Optional base EXP override (if 0, uses formula)

    Returns:
        EXP reward as an integer
    """
    if base_exp > 0:
        # Scale provided base EXP by level and difficulty
        level_multiplier = 1.0 + (enemy_level - 1) * ENEMY_EXP_LEVEL_MULTIPLIER
        difficulty_multiplier = DIFFICULTY_REWARD_MULTIPLIERS.get(difficulty, 1.0)
        return max(1, int(base_exp * level_multiplier * difficulty_multiplier))

    # Calculate from formula: base per level * level * difficulty
    base = BASE_ENEMY_EXP_PER_LEVEL * enemy_level
    difficulty_multiplier = DIFFICULTY_REWARD_MULTIPLIERS.get(difficulty, 1.0)
    return max(1, int(base * difficulty_multiplier))


def calculate_enemy_gold_reward(enemy_level: int, difficulty: str = "normal", base_gold: int = 0) -> int:
    """
    Calculate gold reward for defeating an enemy.

    Args:
        enemy_level: The enemy's level
        difficulty: The enemy's difficulty tier
        base_gold: Optional base gold override (if 0, uses formula)

    Returns:
        Gold reward as an integer
    """
    if base_gold > 0:
        # Scale provided base gold by level and difficulty
        level_multiplier = 1.0 + (enemy_level - 1) * ENEMY_GOLD_LEVEL_MULTIPLIER
        difficulty_multiplier = DIFFICULTY_REWARD_MULTIPLIERS.get(difficulty, 1.0)
        return max(1, int(base_gold * level_multiplier * difficulty_multiplier))

    # Calculate from formula: base per level * level * difficulty
    base = BASE_ENEMY_GOLD_PER_LEVEL * enemy_level
    difficulty_multiplier = DIFFICULTY_REWARD_MULTIPLIERS.get(difficulty, 1.0)
    return max(1, int(base * difficulty_multiplier))


def get_scaled_enemy_stats(
    base_stats: Dict[str, int],
    enemy_level: int,
    difficulty: str = "normal"
) -> Dict[str, int]:
    """
    Scale all enemy stats based on level and difficulty.

    Args:
        base_stats: Dictionary of base stat values
        enemy_level: The enemy's level
        difficulty: The enemy's difficulty tier

    Returns:
        Dictionary of scaled stat values
    """
    scaled = {}
    for stat_name, base_value in base_stats.items():
        scaled[stat_name] = scale_enemy_stat(base_value, enemy_level, stat_name, difficulty)

    # Ensure HP starts at max
    if "max_hp" in scaled and "hp" in scaled:
        scaled["hp"] = scaled["max_hp"]
    if "max_sp" in scaled and "sp" in scaled:
        scaled["sp"] = scaled["max_sp"]

    return scaled
