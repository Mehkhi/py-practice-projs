"""Configuration for achievement trigger mappings."""

from typing import Any, Dict, Optional

SIMPLE_TRIGGER_CONFIG: Dict[str, Dict[str, Any]] = {
    "on_enemy_killed": {"trigger_type": "kill"},
    "on_boss_killed": {"trigger_type": "boss_kill"},
    "on_battle_won": {"trigger_type": "battle_win"},
    "on_battle_fled": {"trigger_type": "flee"},
    "on_battle_spared": {"trigger_type": "spare"},
    "on_item_collected": {"trigger_type": "collect", "uses_amount": True},
    "on_item_crafted": {"trigger_type": "craft"},
    "on_quest_completed": {"trigger_type": "quest"},
    "on_map_entered": {"trigger_type": "explore"},
    "on_npc_talked": {"trigger_type": "talk"},
    "on_party_member_recruited": {"trigger_type": "recruit"},
    "on_skill_learned": {"trigger_type": "skill"},
    "on_equipment_equipped": {"trigger_type": "equip"},
    "on_death": {"trigger_type": "death"},
    "on_game_completed": {"trigger_type": "ending"},
    "on_flag_set": {"trigger_type": "flag"},
}

EVENT_PAYLOAD_MAP: Dict[str, Dict[str, Optional[str]]] = {
    "enemy_killed": {"method": "on_enemy_killed", "target_key": "enemy_type", "amount_key": None},
    "boss_killed": {"method": "on_boss_killed", "target_key": "boss_id", "amount_key": None},
    "battle_won": {"method": "on_battle_won", "target_key": None, "amount_key": None},
    "battle_fled": {"method": "on_battle_fled", "target_key": None, "amount_key": None},
    "battle_spared": {"method": "on_battle_spared", "target_key": "enemy_type", "amount_key": None},
    "item_collected": {"method": "on_item_collected", "target_key": "item_id", "amount_key": "amount"},
    "item_crafted": {"method": "on_item_crafted", "target_key": "item_id", "amount_key": None},
    "quest_completed": {"method": "on_quest_completed", "target_key": "quest_id", "amount_key": None},
    "map_entered": {"method": "on_map_entered", "target_key": "map_id", "amount_key": None},
    "npc_talked": {"method": "on_npc_talked", "target_key": "npc_id", "amount_key": None},
    "party_member_recruited": {"method": "on_party_member_recruited", "target_key": "member_id", "amount_key": None},
    "skill_learned": {"method": "on_skill_learned", "target_key": "skill_id", "amount_key": None},
    "equipment_equipped": {"method": "on_equipment_equipped", "target_key": "item_id", "amount_key": None},
    "player_death": {"method": "on_death", "target_key": None, "amount_key": None},
    "game_completed": {"method": "on_game_completed", "target_key": "ending_id", "amount_key": None},
    "flag_set": {"method": "on_flag_set", "target_key": "flag_name", "amount_key": None},
}
