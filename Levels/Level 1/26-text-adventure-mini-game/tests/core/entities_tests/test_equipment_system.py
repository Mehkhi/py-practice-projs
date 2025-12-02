"""Equipment and skill integration tests for entities."""

import unittest
from unittest.mock import patch

from core.entities import Player, Enemy, NPC
from core.items import Item, Inventory
from core.stats import Stats
from core.equipment_flow import equip_item_from_inventory


class EquipmentSystemTests(unittest.TestCase):
    def setUp(self):
        self.items_db = {
            "sword": Item(
                id="sword",
                name="Sword",
                description="",
                item_type="equipment",
                effect_id="",
                equip_slot="weapon",
                stat_modifiers={"attack": 5},
                granted_skills=["slash"],
            ),
            "mage_staff": Item(
                id="mage_staff",
                name="Mage Staff",
                description="",
                item_type="equipment",
                effect_id="",
                equip_slot="weapon",
                stat_modifiers={"magic": 3},
                granted_skills=["fire_bolt"],
            ),
            "bad_charm": Item(
                id="bad_charm",
                name="Bad Charm",
                description="",
                item_type="equipment",
                effect_id="",
                equip_slot="accessory",
                stat_modifiers={"max_hp": 10},
                granted_skills=[],
            ),
        }

    def _base_stats(self):
        return Stats(100, 100, 50, 50, 10, 5, 4, 6, 3)

    def test_equipment_applies_stats_and_skills_across_entities(self):
        sword = self.items_db["sword"]
        for entity_cls, kwargs in (
            (Player, {"inventory": Inventory(), "base_skills": ["tackle"]}),
            (Enemy, {"base_skills": ["howl"]}),
            (NPC, {"base_skills": ["heal"]}),
        ):
            entity = entity_cls(
                entity_id=f"{entity_cls.__name__.lower()}_1",
                name=entity_cls.__name__,
                x=0,
                y=0,
                sprite_id="sprite",
                stats=self._base_stats(),
                **kwargs,
            )
            entity.equip(sword)
            entity.recompute_equipment(self.items_db)

            self.assertEqual(entity.stats.get_effective_attack(), 15)
            self.assertIn("slash", entity.skills)
            self.assertIn(kwargs["base_skills"][0], entity.base_skills)
            self.assertIn(kwargs["base_skills"][0], entity.skills)

    def test_unsupported_modifier_warns_and_is_ignored(self):
        player = Player(
            entity_id="player",
            name="Hero",
            x=0,
            y=0,
            sprite_id="hero",
            stats=self._base_stats(),
            inventory=Inventory(),
        )
        player.equip(self.items_db["bad_charm"], slot="accessory")
        with patch("core.entities.log_warning") as mock_warning:
            player.recompute_equipment(self.items_db)
        self.assertNotIn("max_hp", player.stats.equipment_modifiers)
        mock_warning.assert_called()

    def test_missing_item_clears_slot(self):
        npc = NPC(
            entity_id="npc_1",
            name="Guide",
            x=0,
            y=0,
            sprite_id="npc",
            stats=self._base_stats(),
        )
        npc.equipment["weapon"] = "missing_item"
        npc.recompute_equipment(self.items_db)
        self.assertIsNone(npc.equipment["weapon"])

    def test_equip_helper_enforces_inventory_and_swaps(self):
        player = Player(
            entity_id="player",
            name="Hero",
            x=0,
            y=0,
            sprite_id="hero",
            stats=self._base_stats(),
            inventory=Inventory(),
        )
        player.inventory.add("sword", 1)
        player.inventory.add("mage_staff", 1)

        equipped = equip_item_from_inventory(player, "sword", self.items_db, slot="weapon")
        self.assertTrue(equipped)
        self.assertEqual(player.inventory.get_quantity("sword"), 0)
        self.assertEqual(player.equipment["weapon"], "sword")

        swapped = equip_item_from_inventory(player, "mage_staff", self.items_db, slot="weapon")
        self.assertTrue(swapped)
        self.assertEqual(player.equipment["weapon"], "mage_staff")
        self.assertEqual(player.inventory.get_quantity("mage_staff"), 0)
        self.assertEqual(player.inventory.get_quantity("sword"), 1)
        self.assertEqual(player.stats.get_effective_magic(), 7)


if __name__ == "__main__":
    unittest.main()
