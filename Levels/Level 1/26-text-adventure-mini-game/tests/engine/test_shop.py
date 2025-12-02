"""Unit tests for shop system including centralized shop definitions."""

import json
import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from core.entities import NPC, load_npcs_from_json
from core.items import load_items_from_json
from core.stats import Stats
from core.world import World
from engine.shop_scene import (
    ShopScene,
    load_shops_from_json,
    create_shop_scene,
    validate_shop_items,
    SHOP_TYPES,
    SELL_PRICE_MULTIPLIER,
)


class TestLoadShopsFromJson(unittest.TestCase):
    """Tests for load_shops_from_json function."""

    def test_load_shops_returns_dict(self):
        """Test that load_shops_from_json returns a dictionary."""
        shops = load_shops_from_json()
        self.assertIsInstance(shops, dict)

    def test_load_shops_contains_expected_shops(self):
        """Test that all expected shops are loaded."""
        shops = load_shops_from_json()
        expected_shops = [
            "village_general",
            "village_blacksmith",
            "city_weapon_shop",
            "city_armor_shop",
            "city_potion_shop",
            "mage_tower_shop",
            "traveling_merchant",
            "ironhold_general_shop",
            "nighthaven_black_market_shop",
        ]
        for shop_id in expected_shops:
            self.assertIn(shop_id, shops, f"Missing shop: {shop_id}")

    def test_shop_has_required_fields(self):
        """Test that each shop has required fields."""
        shops = load_shops_from_json()
        for shop_id, shop_data in shops.items():
            self.assertIn("name", shop_data, f"Shop {shop_id} missing 'name'")
            self.assertIn("shop_type", shop_data, f"Shop {shop_id} missing 'shop_type'")
            self.assertIn("stock", shop_data, f"Shop {shop_id} missing 'stock'")
            self.assertIsInstance(shop_data["stock"], dict)

    def test_shop_types_are_valid(self):
        """Test that all shop types are recognized."""
        shops = load_shops_from_json()
        for shop_id, shop_data in shops.items():
            shop_type = shop_data.get("shop_type")
            self.assertIn(
                shop_type,
                SHOP_TYPES,
                f"Shop {shop_id} has unknown shop_type: {shop_type}",
            )

    def test_load_missing_file_returns_empty(self):
        """Test that missing file returns empty dict."""
        shops = load_shops_from_json("/nonexistent/path/shops.json")
        self.assertEqual(shops, {})

    def test_load_malformed_json_returns_empty(self):
        """Test that malformed JSON returns empty dict."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("{ invalid json }")
            temp_path = f.name

        try:
            shops = load_shops_from_json(temp_path)
            self.assertEqual(shops, {})
        finally:
            os.unlink(temp_path)


class TestNpcShopIdReferences(unittest.TestCase):
    """Tests for NPC shop_id references matching shops.json."""

    def test_all_npc_shop_ids_exist_in_shops_db(self):
        """Test that all NPC shop_id references exist in shops.json."""
        npcs = load_npcs_from_json()
        shops = load_shops_from_json()

        for npc_id, npc in npcs.items():
            if npc.shop_id:
                self.assertIn(
                    npc.shop_id,
                    shops,
                    f"NPC '{npc_id}' references unknown shop_id: '{npc.shop_id}'",
                )

    def test_merchant_npcs_have_shop_id(self):
        """Test that NPCs with role='merchant' have shop_id set."""
        npcs = load_npcs_from_json()

        merchant_npcs = [npc for npc in npcs.values() if npc.role == "merchant"]
        self.assertGreater(len(merchant_npcs), 0, "No merchant NPCs found")

        for npc in merchant_npcs:
            self.assertIsNotNone(
                npc.shop_id,
                f"Merchant NPC '{npc.entity_id}' missing shop_id",
            )

    def test_merchant_npcs_no_inline_shop_inventory(self):
        """Test that merchant NPCs using shop_id don't have shop_inventory."""
        npcs = load_npcs_from_json()

        for npc_id, npc in npcs.items():
            if npc.shop_id:
                # shop_inventory should be empty when shop_id is used
                self.assertEqual(
                    npc.shop_inventory,
                    {},
                    f"NPC '{npc_id}' has both shop_id and shop_inventory (deprecated)",
                )


class TestValidateShopItems(unittest.TestCase):
    """Tests for validate_shop_items function."""

    def test_validate_shop_items_with_valid_items(self):
        """Test that valid shops return no warnings."""
        shops_db = load_shops_from_json()
        items_db = load_items_from_json()
        warnings = validate_shop_items(shops_db, items_db)
        self.assertEqual(warnings, [])

    def test_validate_shop_items_detects_invalid_items(self):
        """Test that invalid item IDs are detected."""
        shops_db = {
            "test_shop": {
                "name": "Test Shop",
                "shop_type": "general",
                "stock": {"nonexistent_item": 5, "another_fake_item": 3},
            }
        }
        items_db = {}
        warnings = validate_shop_items(shops_db, items_db)
        self.assertEqual(len(warnings), 2)
        self.assertIn("nonexistent_item", warnings[0])
        self.assertIn("another_fake_item", warnings[1])


class TestShopStockItemValidation(unittest.TestCase):
    """Tests for validating shop stock item IDs against items database."""

    def test_all_shop_items_exist_in_items_db(self):
        """Test that all item IDs in shop stock exist in items.json."""
        shops = load_shops_from_json()
        items_db = load_items_from_json()

        missing_items = []
        for shop_id, shop_data in shops.items():
            for item_id in shop_data.get("stock", {}).keys():
                if item_id not in items_db:
                    missing_items.append((shop_id, item_id))

        self.assertEqual(
            missing_items,
            [],
            f"Shops reference unknown items: {missing_items}",
        )


class TestCreateShopScene(unittest.TestCase):
    """Tests for create_shop_scene factory function."""

    def setUp(self):
        """Set up test fixtures."""
        self.world = World()
        self.player = MagicMock()
        self.player.inventory = MagicMock()
        self.items_db = load_items_from_json()
        self.shops_db = load_shops_from_json()

    def test_create_shop_scene_with_valid_shop_id(self):
        """Test creating a shop scene with valid shop_id."""
        scene = create_shop_scene(
            manager=None,
            world=self.world,
            player=self.player,
            items_db=self.items_db,
            shop_id="village_general",
            shops_db=self.shops_db,
        )
        self.assertIsNotNone(scene)
        self.assertIsInstance(scene, ShopScene)
        self.assertEqual(scene.shop_id, "village_general")
        self.assertEqual(scene.title, "Village General Store")

    def test_create_shop_scene_with_invalid_shop_id(self):
        """Test that invalid shop_id returns None."""
        scene = create_shop_scene(
            manager=None,
            world=self.world,
            player=self.player,
            items_db=self.items_db,
            shop_id="nonexistent_shop",
            shops_db=self.shops_db,
        )
        self.assertIsNone(scene)

    def test_create_shop_scene_loads_shops_if_not_provided(self):
        """Test that shops_db is loaded if not provided."""
        scene = create_shop_scene(
            manager=None,
            world=self.world,
            player=self.player,
            items_db=self.items_db,
            shop_id="village_general",
            shops_db=None,  # Should auto-load
        )
        self.assertIsNotNone(scene)

    def test_create_shop_scene_copies_stock(self):
        """Test that stock is copied, not referenced."""
        scene = create_shop_scene(
            manager=None,
            world=self.world,
            player=self.player,
            items_db=self.items_db,
            shop_id="village_general",
            shops_db=self.shops_db,
        )
        original_stock = self.shops_db["village_general"]["stock"]

        # Modify scene stock
        scene.stock["health_potion"] = 0

        # Original should be unchanged
        self.assertNotEqual(original_stock.get("health_potion", 0), 0)

    def test_create_shop_scene_with_quest_manager(self):
        """Test that quest_manager is passed through."""
        quest_manager = MagicMock()
        scene = create_shop_scene(
            manager=None,
            world=self.world,
            player=self.player,
            items_db=self.items_db,
            shop_id="village_general",
            shops_db=self.shops_db,
            quest_manager=quest_manager,
        )
        self.assertEqual(scene.quest_manager, quest_manager)


class TestShopScene(unittest.TestCase):
    """Tests for ShopScene class."""

    def setUp(self):
        """Set up test fixtures."""
        self.world = World()
        self.world.set_flag("gold", 100)
        self.player = MagicMock()
        self.player.inventory = MagicMock()
        self.player.inventory.has.return_value = True
        self.player.inventory.get_all_items.return_value = {"health_potion": 5}
        self.items_db = load_items_from_json()
        self.stock = {"health_potion": 10, "sp_potion": 5}

    def test_shop_scene_initialization(self):
        """Test basic ShopScene initialization."""
        scene = ShopScene(
            manager=None,
            world=self.world,
            player=self.player,
            items_db=self.items_db,
            stock=self.stock,
            title="Test Shop",
        )
        self.assertEqual(scene.title, "Test Shop")
        self.assertEqual(scene.stock, self.stock)
        self.assertEqual(scene.mode, ShopScene.MODE_MAIN)

    def test_gold_retrieval(self):
        """Test gold retrieval from world flags."""
        scene = ShopScene(
            manager=None,
            world=self.world,
            player=self.player,
            items_db=self.items_db,
            stock=self.stock,
        )
        self.assertEqual(scene._gold(), 100)

    def test_set_gold(self):
        """Test setting gold in world flags."""
        scene = ShopScene(
            manager=None,
            world=self.world,
            player=self.player,
            items_db=self.items_db,
            stock=self.stock,
        )
        scene._set_gold(50)
        self.assertEqual(self.world.get_flag("gold"), 50)

    def test_set_gold_prevents_negative(self):
        """Test that gold cannot go negative."""
        scene = ShopScene(
            manager=None,
            world=self.world,
            player=self.player,
            items_db=self.items_db,
            stock=self.stock,
        )
        scene._set_gold(-100)
        self.assertEqual(self.world.get_flag("gold"), 0)

    def test_sell_price_calculation(self):
        """Test sell price is calculated correctly."""
        scene = ShopScene(
            manager=None,
            world=self.world,
            player=self.player,
            items_db=self.items_db,
            stock=self.stock,
        )
        item = self.items_db.get("health_potion")
        if item:
            expected_price = max(1, int(item.value * SELL_PRICE_MULTIPLIER))
            self.assertEqual(scene._get_sell_price(item), expected_price)


class TestShopPersistence(unittest.TestCase):
    """Tests for shop stock persistence."""

    def setUp(self):
        """Set up test fixtures."""
        self.world = World()
        self.world.set_flag("gold", 1000)
        self.player = MagicMock()
        self.player.inventory = MagicMock()
        self.items_db = load_items_from_json()
        self.stock = {"health_potion": 10}

    def test_stock_persisted_to_world_flags(self):
        """Test that stock changes are persisted to world flags."""
        scene = ShopScene(
            manager=None,
            world=self.world,
            player=self.player,
            items_db=self.items_db,
            stock=dict(self.stock),
            shop_id="test_shop",
        )
        scene.stock["health_potion"] = 5
        scene._save_persisted_stock()

        persisted = self.world.get_flag("shop_test_shop_stock")
        self.assertIsNotNone(persisted)
        self.assertEqual(persisted.get("health_potion"), 5)

    def test_stock_loaded_from_world_flags(self):
        """Test that persisted stock is loaded on scene creation."""
        # Pre-persist stock
        self.world.set_flag("shop_test_shop_stock", {"health_potion": 3})

        scene = ShopScene(
            manager=None,
            world=self.world,
            player=self.player,
            items_db=self.items_db,
            stock=dict(self.stock),
            shop_id="test_shop",
        )
        self.assertEqual(scene.stock.get("health_potion"), 3)


class TestShopRestock(unittest.TestCase):
    """Tests for shop restocking functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.world = World()
        self.world.set_flag("gold", 1000)
        self.world.set_flag("game_day", 10)
        self.player = MagicMock()
        self.player.inventory = MagicMock()
        self.items_db = load_items_from_json()
        self.stock = {"health_potion": 10}

    def test_restock_after_interval(self):
        """Test that shop restocks after interval passes."""
        # Set last restock to 5 days ago
        self.world.set_flag("shop_test_shop_last_restock", 5)
        self.world.set_flag("shop_test_shop_stock", {"health_potion": 2})

        scene = ShopScene(
            manager=None,
            world=self.world,
            player=self.player,
            items_db=self.items_db,
            stock=dict(self.stock),
            shop_id="test_shop",
            restock_interval=3,  # Restock every 3 days
            base_stock=dict(self.stock),
        )
        # Should have restocked since 10 - 5 = 5 days >= 3 day interval
        self.assertEqual(scene.stock.get("health_potion"), 10)

    def test_no_restock_before_interval(self):
        """Test that shop doesn't restock before interval."""
        self.world.set_flag("game_day", 7)
        self.world.set_flag("shop_test_shop_last_restock", 5)
        self.world.set_flag("shop_test_shop_stock", {"health_potion": 2})

        scene = ShopScene(
            manager=None,
            world=self.world,
            player=self.player,
            items_db=self.items_db,
            stock=dict(self.stock),
            shop_id="test_shop",
            restock_interval=3,
            base_stock=dict(self.stock),
        )
        # Should NOT have restocked since 7 - 5 = 2 days < 3 day interval
        self.assertEqual(scene.stock.get("health_potion"), 2)


if __name__ == "__main__":
    unittest.main()
