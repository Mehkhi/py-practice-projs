"""Factory for creating and configuring player instances."""

from typing import Any, Dict, Optional

from core.entities import Player
from core.items import Inventory
from core.moves import get_moves_database
from core.stats import Stats

from .class_selection_scene import load_classes_data


class PlayerFactory:
    """Creates player entities for new games and class selection."""

    def __init__(
        self,
        config: Dict[str, Any],
        items_db: Optional[Dict[str, Any]] = None,
        encounters_data: Optional[Dict[str, Dict[str, Any]]] = None,
        bestiary_metadata: Optional[Dict[str, Any]] = None,
    ):
        self.config = config
        self.items_db = items_db or {}
        self.encounters_data = encounters_data
        self.bestiary_metadata = bestiary_metadata

    def create_default_player(self) -> Player:
        """Create a starter player used before class selection."""
        start_x = self.config.get("player_start_x", 5)
        start_y = self.config.get("player_start_y", 5)
        stats = Stats(
            max_hp=100,
            hp=100,
            max_sp=50,
            sp=50,
            attack=10,
            defense=5,
            magic=8,
            speed=10,
            luck=5
        )

        player = Player(
            entity_id="player",
            name="Hero",
            x=start_x,
            y=start_y,
            sprite_id="player",
            stats=stats,
            inventory=Inventory()
        )
        player.inventory.add("health_potion", 2)
        player.base_skills = ["fire_bolt", "heal"]
        player.skills = list(player.base_skills)
        return player

    def create_with_class(self, player_name: str, primary_class: str, subclass: str) -> Player:
        """Create a player with class and subclass applied."""
        classes_data = load_classes_data()
        class_info = classes_data.get("classes", {}).get(primary_class, {})
        subclass_bonus = classes_data.get("subclass_bonuses", {}).get(subclass, {})

        base_stats = class_info.get("stats", {})
        final_stats = {
            "max_hp": base_stats.get("max_hp", 100),
            "hp": base_stats.get("hp", base_stats.get("max_hp", 100)),
            "max_sp": base_stats.get("max_sp", 50),
            "sp": base_stats.get("sp", base_stats.get("max_sp", 50)),
            "attack": base_stats.get("attack", 10),
            "defense": base_stats.get("defense", 5),
            "magic": base_stats.get("magic", 8),
            "speed": base_stats.get("speed", 10),
            "luck": base_stats.get("luck", 5),
        }

        subclass_stats = subclass_bonus.get("stats", {})
        for stat, bonus in subclass_stats.items():
            if stat in final_stats:
                final_stats[stat] += bonus

        final_stats["hp"] = final_stats["max_hp"]
        final_stats["sp"] = final_stats["max_sp"]

        stats = Stats(
            max_hp=final_stats["max_hp"],
            hp=final_stats["hp"],
            max_sp=final_stats["max_sp"],
            sp=final_stats["sp"],
            attack=final_stats["attack"],
            defense=final_stats["defense"],
            magic=final_stats["magic"],
            speed=final_stats["speed"],
            luck=final_stats["luck"]
        )

        start_x = self.config.get("player_start_x", 5)
        start_y = self.config.get("player_start_y", 5)

        base_skills = list(class_info.get("base_skills", []))
        subclass_skills = subclass_bonus.get("skills", [])
        combined_skills = list(dict.fromkeys(base_skills + subclass_skills))

        player_sprite_id = f"player_{primary_class}_{subclass}"
        moves_db = get_moves_database()
        starting_moves = moves_db.get_starting_moves(primary_class)

        player = Player(
            entity_id="player",
            name=player_name,
            x=start_x,
            y=start_y,
            sprite_id=player_sprite_id,
            stats=stats,
            inventory=Inventory(),
            base_skills=combined_skills,
            skills=list(combined_skills),
            player_class=primary_class,
            player_subclass=subclass,
            learned_moves=list(starting_moves)
        )

        player.inventory.add("health_potion", 2)

        if self.encounters_data and hasattr(player, "bestiary"):
            player.bestiary.seed_from_encounter_data(
                self.encounters_data,
                metadata=self.bestiary_metadata,
            )

        starting_weapon = class_info.get("starting_weapon")
        if starting_weapon and starting_weapon in self.items_db:
            weapon_item = self.items_db[starting_weapon]
            player.inventory.add(starting_weapon, 1)
            player.equip(weapon_item, "weapon")
            player.recompute_equipment(self.items_db)

        return player
