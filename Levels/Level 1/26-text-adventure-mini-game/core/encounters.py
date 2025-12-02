"""Encounter factory for creating enemies and rewards from encounter data."""

import os
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING

from .constants import SUPPORTED_EQUIP_SLOTS
from .data_loader import load_json_file
from .entities import Enemy
from .stats import Stats, scale_enemy_stat, calculate_enemy_exp_reward, calculate_enemy_gold_reward
from .logging_utils import log_warning

if TYPE_CHECKING:
    from .items import Item


def load_encounters_from_json(
    path: str = os.path.join("data", "encounters.json"),
    data: Optional[Dict[str, Any]] = None
) -> Dict[str, Dict[str, Any]]:
    """
    Load encounter definitions from JSON file.

    Args:
        path: Path to the encounters JSON file

    Returns:
        Dictionary mapping encounter IDs to their encounter data
    """
    data_source = data if data is not None else load_json_file(path, default={}, context="Loading encounters")
    return data_source.get("encounters", {}) or {}


def create_encounter_from_data(
    encounter_id: str,
    encounters_data: Dict,
    items_db: Optional[Dict[str, "Item"]] = None,
) -> Tuple[List[Enemy], Dict, Optional[str], List[Dict]]:
    """
    Create enemies and rewards from encounter data.

    Args:
        encounter_id: The ID of the encounter to load
        encounters_data: Dictionary mapping encounter IDs to encounter data
        items_db: Optional items database for equipment recomputation

    Returns:
        Tuple of (enemies, rewards, backdrop_id, ai_metadata):
        - enemies: List of constructed Enemy instances with scaled stats
        - rewards: Dict with 'items', 'flags', 'exp', 'gold' (scaled)
        - backdrop_id: Optional backdrop identifier
        - ai_metadata: List of dicts with 'enemy_index', 'ai_profile', 'skills', 'items'
          for post-BattleSystem setup

    Note:
        The 'hp' and 'sp' fields in encounter JSON are ignored; enemies always
        spawn at full HP/SP (scaled_max_hp and scaled_max_sp respectively).
    """
    encounter_data = (encounters_data or {}).get(encounter_id)
    enemies: List[Enemy] = []
    rewards: Dict = {"items": {}, "flags": []}
    backdrop_id: Optional[str] = None
    ai_metadata: List[Dict] = []

    if encounter_data:
        rewards_data = encounter_data.get("rewards", {})
        rewards["items"] = rewards_data.get("items", {})
        rewards["flags"] = rewards_data.get("flags", [])
        backdrop_id = encounter_data.get("backdrop_id")

        # Calculate scaled rewards based on enemy levels
        total_exp = 0
        total_gold = 0
        base_exp = rewards_data.get("exp", 0)
        base_gold = rewards_data.get("gold", 0)

        for enemy_index, enemy_data in enumerate(encounter_data.get("enemies", [])):
            # Get enemy level and difficulty for stat scaling
            enemy_level = enemy_data.get("level", 1)
            enemy_difficulty = enemy_data.get("difficulty", "normal")

            # Calculate per-enemy EXP and gold contribution
            num_enemies = max(1, len(encounter_data.get("enemies", [])))
            total_exp += calculate_enemy_exp_reward(
                enemy_level, enemy_difficulty, base_exp // num_enemies
            )
            total_gold += calculate_enemy_gold_reward(
                enemy_level, enemy_difficulty, base_gold // num_enemies
            )

            # Get base stats and apply level/difficulty scaling
            base_max_hp = enemy_data.get("max_hp", 50)
            base_max_sp = enemy_data.get("max_sp", 20)
            base_attack = enemy_data.get("attack", 8)
            base_defense = enemy_data.get("defense", 3)
            base_magic = enemy_data.get("magic", 5)
            base_speed = enemy_data.get("speed", 7)
            base_luck = enemy_data.get("luck", 3)

            scaled_max_hp = scale_enemy_stat(base_max_hp, enemy_level, "max_hp", enemy_difficulty)
            scaled_max_sp = scale_enemy_stat(base_max_sp, enemy_level, "max_sp", enemy_difficulty)
            scaled_attack = scale_enemy_stat(base_attack, enemy_level, "attack", enemy_difficulty)
            scaled_defense = scale_enemy_stat(base_defense, enemy_level, "defense", enemy_difficulty)
            scaled_magic = scale_enemy_stat(base_magic, enemy_level, "magic", enemy_difficulty)
            scaled_speed = scale_enemy_stat(base_speed, enemy_level, "speed", enemy_difficulty)
            scaled_luck = scale_enemy_stat(base_luck, enemy_level, "luck", enemy_difficulty)

            enemy_stats = Stats(
                max_hp=scaled_max_hp,
                hp=scaled_max_hp,  # Start at full HP
                max_sp=scaled_max_sp,
                sp=scaled_max_sp,  # Start at full SP
                attack=scaled_attack,
                defense=scaled_defense,
                magic=scaled_magic,
                speed=scaled_speed,
                luck=scaled_luck,
                weaknesses=enemy_data.get("weaknesses", []),
                resistances=enemy_data.get("resistances", []),
                immunities=enemy_data.get("immunities", []),
                absorbs=enemy_data.get("absorbs", []),
            )

            # Set up equipment
            equipment_data = enemy_data.get("equipment") or {}
            equipment = {slot: None for slot in SUPPORTED_EQUIP_SLOTS}
            for slot, item_id in equipment_data.items():
                if slot in SUPPORTED_EQUIP_SLOTS:
                    equipment[slot] = item_id

            base_skills = enemy_data.get("base_skills", [])
            skills = enemy_data.get("skills", [])

            # Create enemy with spare mechanics if present in data
            enemy_kwargs = {
                "entity_id": enemy_data.get("id", "enemy"),
                "name": enemy_data.get("name", "Enemy"),
                "x": 0,
                "y": 0,
                "sprite_id": enemy_data.get("sprite_id", "enemy"),
                "stats": enemy_stats,
                "enemy_type": enemy_data.get("type", "generic"),
                "base_skills": list(base_skills),
                "skills": list(skills),
                "equipment": equipment,
                "level": enemy_level,
                "difficulty": enemy_difficulty,
            }

            # Add spare mechanics if present (for world battles)
            for spare_key in ("spareable", "spare_threshold", "spare_hp_threshold", "spare_messages"):
                if spare_key in enemy_data:
                    enemy_kwargs[spare_key] = enemy_data[spare_key]

            enemy = Enemy(**enemy_kwargs)

            # Recompute equipment if items_db provided
            if equipment_data and items_db is not None:
                enemy.recompute_equipment(items_db)

            enemies.append(enemy)

            # Collect AI metadata for post-BattleSystem setup
            ai_metadata.append({
                "enemy_index": enemy_index,
                "ai_profile": enemy_data.get("ai_profile"),
                "skills": enemy_data.get("skills"),
                "items": enemy_data.get("items", {}),
                "enemy_id": enemy_data.get("id", "enemy"),
            })

        # Add scaled rewards to the rewards dict
        rewards["exp"] = total_exp
        rewards["gold"] = total_gold

    # Fallback enemy if encounter loading failed
    if not enemies:
        # Use different fallback stats based on encounter_id
        if encounter_id == "tutorial_battle":
            enemy_stats = Stats(50, 50, 20, 20, 3, 1, 2, 4, 1)
            enemy = Enemy("tutorial_slime", "Practice Slime", 0, 0, "slime", stats=enemy_stats)
        else:
            enemy_stats = Stats(50, 50, 20, 20, 8, 3, 5, 7, 3)
            enemy = Enemy("enemy_1", "Slime", 0, 0, "enemy", stats=enemy_stats)
        enemies.append(enemy)

    return enemies, rewards, backdrop_id, ai_metadata
