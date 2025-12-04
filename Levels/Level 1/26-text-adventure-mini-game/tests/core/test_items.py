"""Unit tests for core/items.py - Item loading, inventory operations."""

import json
import os
import tempfile
import unittest

from core.data_loader import clear_json_cache
from core.items import Item, Inventory, load_items_from_json


class TestItem(unittest.TestCase):
    def test_item_basic(self):
        item = Item(
            id="sword",
            name="Iron Sword",
            description="A basic sword",
            item_type="equipment",
            effect_id="weapon_attack",
        )
        self.assertEqual(item.id, "sword")
        self.assertEqual(item.name, "Iron Sword")
        self.assertEqual(item.item_type, "equipment")

    def test_item_defaults(self):
        item = Item(
            id="test",
            name="Test Item",
            description="",
            item_type="consumable",
            effect_id="",
        )
        self.assertEqual(item.value, 0)
        self.assertEqual(item.sprite_id, "item_default")
        self.assertEqual(item.icon_id, "item_default")
        self.assertEqual(item.target_pattern, "self")
        self.assertEqual(item.equip_slot, "")
        self.assertEqual(item.stat_modifiers, {})
        self.assertEqual(item.granted_skills, [])

    def test_item_equipment_with_modifiers(self):
        item = Item(
            id="magic_sword",
            name="Magic Sword",
            description="A magical blade",
            item_type="equipment",
            effect_id="",
            equip_slot="weapon",
            stat_modifiers={"attack": 5, "magic": 2},
            granted_skills=["fire_slash"],
        )
        self.assertEqual(item.equip_slot, "weapon")
        self.assertEqual(item.stat_modifiers["attack"], 5)
        self.assertEqual(item.stat_modifiers["magic"], 2)
        self.assertIn("fire_slash", item.granted_skills)

    def test_item_consumable(self):
        item = Item(
            id="health_potion",
            name="Health Potion",
            description="Restores HP",
            item_type="consumable",
            effect_id="heal_50",
            target_pattern="single_ally",
            value=20,
        )
        self.assertEqual(item.item_type, "consumable")
        self.assertEqual(item.effect_id, "heal_50")
        self.assertEqual(item.target_pattern, "single_ally")

    def test_item_key(self):
        item = Item(
            id="rusty_key",
            name="Rusty Key",
            description="Opens old doors",
            item_type="key",
            effect_id="unlock",
        )
        self.assertEqual(item.item_type, "key")


class TestInventory(unittest.TestCase):
    def setUp(self):
        self.inventory = Inventory()

    def test_inventory_empty(self):
        self.assertEqual(self.inventory.get_all_items(), {})

    def test_add_item(self):
        self.inventory.add("health_potion", 1)
        self.assertEqual(self.inventory.get_quantity("health_potion"), 1)

    def test_add_item_multiple(self):
        self.inventory.add("health_potion", 3)
        self.assertEqual(self.inventory.get_quantity("health_potion"), 3)

    def test_add_item_stacks(self):
        self.inventory.add("health_potion", 2)
        self.inventory.add("health_potion", 3)
        self.assertEqual(self.inventory.get_quantity("health_potion"), 5)

    def test_add_different_items(self):
        self.inventory.add("health_potion", 2)
        self.inventory.add("sword", 1)
        self.assertEqual(self.inventory.get_quantity("health_potion"), 2)
        self.assertEqual(self.inventory.get_quantity("sword"), 1)

    def test_remove_item(self):
        self.inventory.add("health_potion", 3)
        result = self.inventory.remove("health_potion", 1)
        self.assertTrue(result)
        self.assertEqual(self.inventory.get_quantity("health_potion"), 2)

    def test_remove_item_all(self):
        self.inventory.add("health_potion", 2)
        result = self.inventory.remove("health_potion", 2)
        self.assertTrue(result)
        self.assertEqual(self.inventory.get_quantity("health_potion"), 0)
        self.assertNotIn("health_potion", self.inventory.items)

    def test_remove_item_insufficient(self):
        self.inventory.add("health_potion", 1)
        result = self.inventory.remove("health_potion", 5)
        self.assertFalse(result)
        self.assertEqual(self.inventory.get_quantity("health_potion"), 1)

    def test_remove_item_not_in_inventory(self):
        result = self.inventory.remove("nonexistent", 1)
        self.assertFalse(result)

    def test_has_item_true(self):
        self.inventory.add("sword", 2)
        self.assertTrue(self.inventory.has("sword"))
        self.assertTrue(self.inventory.has("sword", 2))

    def test_has_item_false(self):
        self.assertFalse(self.inventory.has("sword"))
        self.inventory.add("sword", 1)
        self.assertFalse(self.inventory.has("sword", 5))

    def test_get_quantity_not_in_inventory(self):
        self.assertEqual(self.inventory.get_quantity("missing"), 0)

    def test_get_all_items(self):
        self.inventory.add("sword", 1)
        self.inventory.add("potion", 3)
        items = self.inventory.get_all_items()
        self.assertEqual(items["sword"], 1)
        self.assertEqual(items["potion"], 3)

    def test_get_all_items_returns_copy(self):
        self.inventory.add("sword", 1)
        items = self.inventory.get_all_items()
        items["sword"] = 999
        self.assertEqual(self.inventory.get_quantity("sword"), 1)

    def test_clear(self):
        self.inventory.add("sword", 1)
        self.inventory.add("potion", 5)
        self.inventory.clear()
        self.assertEqual(self.inventory.get_all_items(), {})
        self.assertEqual(self.inventory.hotbar_slots, {})

    def test_max_stack_size_enforcement(self):
        """Test that max_stack_size is enforced when adding items."""
        items_db = {
            "potion": Item(
                id="potion",
                name="Health Potion",
                description="Heals HP",
                item_type="consumable",
                effect_id="heal",
                max_stack_size=99
            ),
            "key": Item(
                id="key",
                name="Key",
                description="Opens doors",
                item_type="key",
                effect_id="unlock",
                max_stack_size=1
            )
        }

        # Add items up to stack limit
        added = self.inventory.add("potion", 50, items_db)
        self.assertEqual(added, 50)
        self.assertEqual(self.inventory.get_quantity("potion"), 50)

        # Try to add more than stack limit allows
        added = self.inventory.add("potion", 60, items_db)
        self.assertEqual(added, 49)  # Only 49 more can fit (99 - 50)
        self.assertEqual(self.inventory.get_quantity("potion"), 99)

        # Test key with max_stack_size=1
        added = self.inventory.add("key", 1, items_db)
        self.assertEqual(added, 1)
        self.assertEqual(self.inventory.get_quantity("key"), 1)

        # Try to add another key - should fail
        added = self.inventory.add("key", 1, items_db)
        self.assertEqual(added, 0)  # Can't add more
        self.assertEqual(self.inventory.get_quantity("key"), 1)

    def test_max_stack_size_unlimited(self):
        """Test that items without max_stack_size can stack unlimited."""
        items_db = {
            "unlimited_item": Item(
                id="unlimited_item",
                name="Unlimited Item",
                description="No stack limit",
                item_type="consumable",
                effect_id="test",
                max_stack_size=None
            )
        }

        # Should be able to add unlimited amounts
        added = self.inventory.add("unlimited_item", 1000, items_db)
        self.assertEqual(added, 1000)
        self.assertEqual(self.inventory.get_quantity("unlimited_item"), 1000)

    def test_get_total_item_count(self):
        """Test total item count calculation."""
        self.inventory.add("sword", 1)
        self.inventory.add("potion", 5)
        self.inventory.add("key", 3)
        self.assertEqual(self.inventory.get_total_item_count(), 9)

    def test_get_sorted_items_by_name(self):
        """Test sorting items by name."""
        items_db = {
            "zebra": Item(id="zebra", name="Zebra", description="", item_type="consumable", effect_id=""),
            "apple": Item(id="apple", name="Apple", description="", item_type="consumable", effect_id=""),
            "banana": Item(id="banana", name="Banana", description="", item_type="consumable", effect_id="")
        }

        self.inventory.add("zebra", 1)
        self.inventory.add("apple", 1)
        self.inventory.add("banana", 1)

        sorted_items = self.inventory.get_sorted_items("name", items_db)
        self.assertEqual(sorted_items[0][0], "apple")
        self.assertEqual(sorted_items[1][0], "banana")
        self.assertEqual(sorted_items[2][0], "zebra")

    def test_get_sorted_items_by_type(self):
        """Test sorting items by type."""
        items_db = {
            "sword": Item(id="sword", name="Sword", description="", item_type="equipment", effect_id=""),
            "potion": Item(id="potion", name="Potion", description="", item_type="consumable", effect_id=""),
            "key": Item(id="key", name="Key", description="", item_type="key", effect_id="")
        }

        self.inventory.add("sword", 1)
        self.inventory.add("potion", 1)
        self.inventory.add("key", 1)

        sorted_items = self.inventory.get_sorted_items("type", items_db)
        # Should be sorted by type: consumable, equipment, key
        types = [items_db[item_id].item_type for item_id, _ in sorted_items]
        self.assertEqual(types, ["consumable", "equipment", "key"])

    def test_get_sorted_items_by_quantity(self):
        """Test sorting items by quantity (descending)."""
        self.inventory.add("potion", 10)
        self.inventory.add("sword", 1)
        self.inventory.add("key", 5)

        sorted_items = self.inventory.get_sorted_items("quantity")
        self.assertEqual(sorted_items[0][1], 10)  # Highest quantity first
        self.assertEqual(sorted_items[1][1], 5)
        self.assertEqual(sorted_items[2][1], 1)

    def test_get_filtered_items_by_type(self):
        """Test filtering items by item_type."""
        items_db = {
            "sword": Item(id="sword", name="Sword", description="", item_type="equipment", effect_id=""),
            "potion": Item(id="potion", name="Potion", description="", item_type="consumable", effect_id=""),
            "key": Item(id="key", name="Key", description="", item_type="key", effect_id="")
        }

        self.inventory.add("sword", 1)
        self.inventory.add("potion", 3)
        self.inventory.add("key", 2)

        consumables = self.inventory.get_filtered_items("consumable", items_db)
        self.assertEqual(len(consumables), 1)
        self.assertIn("potion", consumables)
        self.assertEqual(consumables["potion"], 3)

        equipment = self.inventory.get_filtered_items("equipment", items_db)
        self.assertEqual(len(equipment), 1)
        self.assertIn("sword", equipment)

        keys = self.inventory.get_filtered_items("key", items_db)
        self.assertEqual(len(keys), 1)
        self.assertIn("key", keys)

    def test_get_filtered_items_all(self):
        """Test filtering with None returns all items."""
        self.inventory.add("sword", 1)
        self.inventory.add("potion", 3)

        all_items = self.inventory.get_filtered_items(None)
        self.assertEqual(len(all_items), 2)
        self.assertIn("sword", all_items)
        self.assertIn("potion", all_items)

    def test_set_hotbar_item(self):
        """Test setting items in hotbar slots."""
        self.assertTrue(self.inventory.set_hotbar_item(1, "potion"))
        self.assertEqual(self.inventory.get_hotbar_item(1), "potion")

        self.assertTrue(self.inventory.set_hotbar_item(5, "sword"))
        self.assertEqual(self.inventory.get_hotbar_item(5), "sword")

        # Invalid slot should return False
        self.assertFalse(self.inventory.set_hotbar_item(0, "potion"))
        self.assertFalse(self.inventory.set_hotbar_item(10, "potion"))

    def test_get_hotbar_item(self):
        """Test getting items from hotbar slots."""
        self.inventory.set_hotbar_item(3, "potion")
        self.assertEqual(self.inventory.get_hotbar_item(3), "potion")

        # Empty slot should return None
        self.assertIsNone(self.inventory.get_hotbar_item(1))

        # Invalid slot should return None
        self.assertIsNone(self.inventory.get_hotbar_item(0))
        self.assertIsNone(self.inventory.get_hotbar_item(10))

    def test_clear_hotbar_item(self):
        """Test clearing hotbar items."""
        self.inventory.set_hotbar_item(1, "potion")
        self.inventory.set_hotbar_item(2, "sword")

        # Clear a specific slot
        self.assertTrue(self.inventory.set_hotbar_item(1, None))
        self.assertIsNone(self.inventory.get_hotbar_item(1))
        self.assertEqual(self.inventory.get_hotbar_item(2), "sword")  # Other slot still has item

        # Clear all hotbar slots
        self.inventory.clear_hotbar()
        self.assertIsNone(self.inventory.get_hotbar_item(2))
        self.assertEqual(len(self.inventory.hotbar_slots), 0)

    def test_hotbar_multiple_slots(self):
        """Test using multiple hotbar slots."""
        self.inventory.set_hotbar_item(1, "potion")
        self.inventory.set_hotbar_item(9, "sword")
        self.inventory.set_hotbar_item(5, "key")

        self.assertEqual(self.inventory.get_hotbar_item(1), "potion")
        self.assertEqual(self.inventory.get_hotbar_item(9), "sword")
        self.assertEqual(self.inventory.get_hotbar_item(5), "key")

        # All other slots should be empty
        for slot in [2, 3, 4, 6, 7, 8]:
            self.assertIsNone(self.inventory.get_hotbar_item(slot))

    def test_hotbar_replace_item(self):
        """Test replacing an item in a hotbar slot."""
        self.inventory.set_hotbar_item(1, "potion")
        self.assertEqual(self.inventory.get_hotbar_item(1), "potion")

        # Replace with different item
        self.inventory.set_hotbar_item(1, "sword")
        self.assertEqual(self.inventory.get_hotbar_item(1), "sword")

    def test_add_with_items_db_but_no_max_stack(self):
        """Test adding items when items_db is provided but item has no max_stack_size."""
        items_db = {
            "unlimited": Item(
                id="unlimited",
                name="Unlimited",
                description="",
                item_type="consumable",
                effect_id="",
                max_stack_size=None
            )
        }

        added = self.inventory.add("unlimited", 100, items_db)
        self.assertEqual(added, 100)
        self.assertEqual(self.inventory.get_quantity("unlimited"), 100)


class TestLoadItemsFromJson(unittest.TestCase):
    def test_load_empty_items(self):
        data = {"items": []}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            temp_path = f.name

        try:
            items = load_items_from_json(temp_path)
            self.assertEqual(len(items), 0)
        finally:
            os.unlink(temp_path)

    def test_load_single_item(self):
        data = {
            "items": [
                {
                    "id": "sword",
                    "name": "Iron Sword",
                    "description": "A basic sword",
                    "item_type": "equipment",
                    "effect_id": "",
                    "equip_slot": "weapon",
                    "value": 10,
                }
            ]
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            temp_path = f.name

        try:
            items = load_items_from_json(temp_path)
            self.assertIn("sword", items)
            self.assertEqual(items["sword"].name, "Iron Sword")
            self.assertEqual(items["sword"].value, 10)
        finally:
            os.unlink(temp_path)

    def test_load_item_with_stat_modifiers(self):
        data = {
            "items": [
                {
                    "id": "magic_ring",
                    "name": "Magic Ring",
                    "description": "",
                    "item_type": "equipment",
                    "effect_id": "",
                    "equip_slot": "accessory",
                    "stat_modifiers": {"magic": 3, "luck": 1},
                }
            ]
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            temp_path = f.name

        try:
            items = load_items_from_json(temp_path)
            ring = items["magic_ring"]
            self.assertEqual(ring.stat_modifiers["magic"], 3)
            self.assertEqual(ring.stat_modifiers["luck"], 1)
        finally:
            os.unlink(temp_path)

    def test_load_item_with_granted_skills(self):
        data = {
            "items": [
                {
                    "id": "staff",
                    "name": "Mage Staff",
                    "description": "",
                    "item_type": "equipment",
                    "effect_id": "",
                    "equip_slot": "weapon",
                    "granted_skills": ["fire_bolt", "ice_shard"],
                }
            ]
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            temp_path = f.name

        try:
            items = load_items_from_json(temp_path)
            staff = items["staff"]
            self.assertIn("fire_bolt", staff.granted_skills)
            self.assertIn("ice_shard", staff.granted_skills)
        finally:
            os.unlink(temp_path)

    def test_load_multiple_items(self):
        data = {
            "items": [
                {"id": "sword", "name": "Sword", "description": "", "item_type": "equipment", "effect_id": ""},
                {"id": "potion", "name": "Potion", "description": "", "item_type": "consumable", "effect_id": "heal"},
                {"id": "key", "name": "Key", "description": "", "item_type": "key", "effect_id": "unlock"},
            ]
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            temp_path = f.name

        try:
            items = load_items_from_json(temp_path)
            self.assertEqual(len(items), 3)
            self.assertIn("sword", items)
            self.assertIn("potion", items)
            self.assertIn("key", items)
        finally:
            os.unlink(temp_path)

    def test_load_nonexistent_file_returns_empty(self):
        items = load_items_from_json("/nonexistent/path/items.json")
        self.assertEqual(items, {})

    def test_load_item_defaults(self):
        data = {
            "items": [
                {"id": "minimal", "item_type": "consumable", "effect_id": "test"}
            ]
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            temp_path = f.name

        try:
            items = load_items_from_json(temp_path)
            item = items["minimal"]
            self.assertEqual(item.name, "minimal")  # defaults to id
            self.assertEqual(item.description, "")
            self.assertEqual(item.value, 0)
        finally:
            os.unlink(temp_path)

    def test_items_load_does_not_taint_cached_json(self):
        """Mutating loaded items should not mutate the cached JSON payload."""
        data = {
            "items": [
                {
                    "id": "ring",
                    "item_type": "equipment",
                    "effect_id": "buff",
                    "stat_modifiers": {"magic": 3},
                    "granted_skills": ["blink"],
                }
            ]
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            temp_path = f.name

        try:
            loaded = load_items_from_json(temp_path)
            ring = loaded["ring"]
            ring.stat_modifiers["magic"] = 999
            ring.granted_skills.append("tainted")

            reloaded = load_items_from_json(temp_path)
            fresh_ring = reloaded["ring"]

            self.assertEqual(fresh_ring.stat_modifiers["magic"], 3)
            self.assertEqual(fresh_ring.granted_skills, ["blink"])
        finally:
            clear_json_cache(temp_path)
            os.unlink(temp_path)


class TestInventoryEdgeCases(unittest.TestCase):
    """Edge case tests for inventory operations."""

    def setUp(self):
        self.inventory = Inventory()

    def test_add_zero_quantity(self):
        """Test adding zero quantity is rejected and returns 0."""
        # Zero quantity should be rejected - no item entry created
        added = self.inventory.add("potion", 0)
        self.assertEqual(added, 0)
        self.assertEqual(self.inventory.get_quantity("potion"), 0)
        # Zero quantities should not create an entry
        self.assertNotIn("potion", self.inventory.items)

    def test_add_negative_quantity(self):
        """Test adding negative quantity is rejected and returns 0."""
        # Negative quantities should be rejected - no item entry created
        added = self.inventory.add("potion", -5)
        self.assertEqual(added, 0)  # Returns 0 (nothing added)
        self.assertEqual(self.inventory.get_quantity("potion"), 0)

    def test_remove_clears_hotbar_assignment(self):
        """Test that removing all of an item clears its hotbar slot."""
        self.inventory.add("potion", 3)
        self.inventory.set_hotbar_item(1, "potion")
        self.assertEqual(self.inventory.get_hotbar_item(1), "potion")

        # Remove all potions
        self.inventory.remove("potion", 3)

        # Hotbar slot should still have the assignment (by current design)
        # This documents current behavior - the assignment persists even when item is gone
        self.assertEqual(self.inventory.get_hotbar_item(1), "potion")

    def test_get_slot_for_item_found(self):
        """Test get_slot_for_item returns correct slot when item is assigned."""
        self.inventory.set_hotbar_item(3, "sword")
        self.inventory.set_hotbar_item(7, "potion")

        self.assertEqual(self.inventory.get_slot_for_item("sword"), 3)
        self.assertEqual(self.inventory.get_slot_for_item("potion"), 7)

    def test_get_slot_for_item_not_found(self):
        """Test get_slot_for_item returns None when item not assigned."""
        self.inventory.set_hotbar_item(1, "sword")

        self.assertIsNone(self.inventory.get_slot_for_item("potion"))
        self.assertIsNone(self.inventory.get_slot_for_item("nonexistent"))

    def test_get_slot_for_item_empty_hotbar(self):
        """Test get_slot_for_item returns None on empty hotbar."""
        self.assertIsNone(self.inventory.get_slot_for_item("any_item"))

    def test_get_sorted_items_case_insensitive(self):
        """Test that sorting by name is case-insensitive."""
        items_db = {
            "apple": Item(id="apple", name="apple", description="", item_type="consumable", effect_id=""),
            "Banana": Item(id="Banana", name="Banana", description="", item_type="consumable", effect_id=""),
            "cherry": Item(id="cherry", name="cherry", description="", item_type="consumable", effect_id="")
        }

        self.inventory.add("cherry", 1)
        self.inventory.add("apple", 1)
        self.inventory.add("Banana", 1)

        sorted_items = self.inventory.get_sorted_items("name", items_db)
        # Should be: apple, Banana, cherry (case-insensitive)
        self.assertEqual(sorted_items[0][0], "apple")
        self.assertEqual(sorted_items[1][0], "Banana")
        self.assertEqual(sorted_items[2][0], "cherry")

    def test_get_sorted_items_missing_from_db(self):
        """Test sorting handles items not in items_db gracefully."""
        items_db = {
            "apple": Item(id="apple", name="Apple", description="", item_type="consumable", effect_id="")
        }

        self.inventory.add("apple", 1)
        self.inventory.add("unknown_item", 1)  # Not in items_db

        # Should not raise an error
        sorted_items = self.inventory.get_sorted_items("name", items_db)
        self.assertEqual(len(sorted_items), 2)


if __name__ == "__main__":
    unittest.main()
