"""Integration tests for fishing system integration with world, achievements, and save/load."""

import json
import os
import unittest
from unittest.mock import Mock, MagicMock

from core.fishing import FishingSystem, Fish, FishRarity, WaterType, CaughtFish
from core.achievements import AchievementManager
from core.world import World
from core.save.serializer import serialize_state
from core.save.deserializer import deserialize_state
from core.loaders.fishing_loader import load_fishing_data
from core.data_loader import load_achievements_from_json


class TestFishingIntegration(unittest.TestCase):
    """Test fishing integration with other systems."""

    def setUp(self):
        """Set up test fixtures."""
        self.fish_db, self.spots = load_fishing_data()
        self.fishing_system = FishingSystem(self.fish_db, self.spots)
        self.achievement_manager = AchievementManager()
        self.achievement_manager.load_achievements("data/achievements.json")
        self.world = World()

    def test_fishing_spot_in_map(self):
        """Test that fishing triggers exist in map data."""
        # Load a map that should have fishing spots
        map_path = os.path.join("data", "maps", "forest_path.json")
        if os.path.exists(map_path):
            with open(map_path, "r") as f:
                map_data = json.load(f)

            triggers = map_data.get("triggers", [])
            fishing_triggers = [
                t for t in triggers
                if t.get("trigger_type") == "fishing"
            ]

            self.assertGreater(len(fishing_triggers), 0, "Map should have at least one fishing trigger")

            # Check that trigger has required fields
            for trigger in fishing_triggers:
                self.assertIn("id", trigger)
                self.assertIn("x", trigger)
                self.assertIn("y", trigger)
                self.assertIn("data", trigger)
                self.assertIn("spot_id", trigger["data"])

    def test_achievement_first_catch(self):
        """Test that first catch achievement unlocks correctly."""
        # Get first catch achievement
        first_catch = self.achievement_manager.achievements.get("first_catch")
        self.assertIsNotNone(first_catch, "first_catch achievement should exist")
        self.assertFalse(first_catch.unlocked, "Achievement should start unlocked")

        # Catch a fish
        caught_fish = CaughtFish(
            fish=self.fish_db["common_carp"],
            size=1.5
        )
        self.fishing_system.record_catch(caught_fish)

        # Track achievement
        unlocked = self.achievement_manager.on_fish_caught(
            fish_id="common_carp",
            rarity="common",
            size_category="medium",
            time_of_day="DAY",
            unique_species_count=1
        )

        # Check achievement unlocked
        self.assertIn("first_catch", unlocked, "first_catch achievement should unlock")
        first_catch = self.achievement_manager.achievements.get("first_catch")
        self.assertTrue(first_catch.unlocked, "Achievement should be unlocked")

    def test_achievement_legendary(self):
        """Test that legendary fish achievement triggers correctly."""
        # Get legendary catch achievement
        legendary_catch = self.achievement_manager.achievements.get("legendary_catch")
        self.assertIsNotNone(legendary_catch, "legendary_catch achievement should exist")
        self.assertFalse(legendary_catch.unlocked, "Achievement should start unlocked")

        # Catch a legendary fish
        if "abyssal_angler" in self.fish_db:
            caught_fish = CaughtFish(
                fish=self.fish_db["abyssal_angler"],
                size=2.0
            )
            self.fishing_system.record_catch(caught_fish)

            # Track achievement
            unlocked = self.achievement_manager.on_fish_caught(
                fish_id="abyssal_angler",
                rarity="legendary",
                size_category="large",
                time_of_day="MIDNIGHT",
                unique_species_count=1
            )

            # Check achievement unlocked
            self.assertIn("legendary_catch", unlocked, "legendary_catch achievement should unlock")
            legendary_catch = self.achievement_manager.achievements.get("legendary_catch")
            self.assertTrue(legendary_catch.unlocked, "Achievement should be unlocked")

    def test_fish_selling_bonus(self):
        """Test that fisherman shop pays bonus price for fish."""
        from engine.shop_scene import ShopScene, load_shops_from_json
        from core.items import Item, ItemType

        # Load shops
        shops_db = load_shops_from_json()
        fisherman_shop = shops_db.get("fisherman_shop")

        self.assertIsNotNone(fisherman_shop, "fisherman_shop should exist")
        self.assertEqual(fisherman_shop.get("fish_buyer_bonus", 1.0), 1.2, "Fisherman shop should have 1.2 bonus")

        # Create a mock fish item
        fish_item = Item(
            id="fish_common_carp",
            name="Common Carp",
            item_type=ItemType.CONSUMABLE.value,
            value=15,
            description="A fish",
            effect_id=""
        )
        fish_item.item_type = "fish"  # Override for test

        # Create shop scene with fisherman shop
        mock_manager = Mock()
        mock_world = Mock()
        mock_world.get_flag = Mock(return_value=1000)
        mock_world.set_flag = Mock()
        mock_player = Mock()
        mock_player.inventory = Mock()
        mock_player.inventory.has = Mock(return_value=True)
        mock_player.inventory.remove = Mock()

        items_db = {"fish_common_carp": fish_item}

        shop_scene = ShopScene(
            manager=mock_manager,
            world=mock_world,
            player=mock_player,
            items_db=items_db,
            stock=fisherman_shop["stock"],
            title=fisherman_shop["name"],
            shop_type=fisherman_shop["shop_type"],
            shop_id="fisherman_shop"
        )
        shop_scene.fish_buyer_bonus = fisherman_shop.get("fish_buyer_bonus", 1.0)

        # Calculate sell price
        sell_price = shop_scene._get_sell_price(fish_item)

        # Base price would be 15 * 0.5 = 7, with 1.2 bonus = 8
        expected_price = int(15 * 0.5 * 1.2)
        self.assertEqual(sell_price, expected_price, f"Fish should sell for {expected_price} with bonus")

    def test_fishing_save_load(self):
        """Test that fishing records persist through save/load."""
        # Record some catches
        caught1 = CaughtFish(fish=self.fish_db["common_carp"], size=1.5)
        caught2 = CaughtFish(fish=self.fish_db["golden_trout"], size=1.2)
        self.fishing_system.record_catch(caught1)
        self.fishing_system.record_catch(caught2)

        # Serialize
        save_data = serialize_state(
            world=self.world,
            player=Mock(),
            fishing_system=self.fishing_system
        )

        # Check fishing data is in save
        self.assertIn("fishing", save_data, "Save data should include fishing state")
        fishing_data = save_data["fishing"]
        self.assertIn("player_records", fishing_data, "Fishing data should include player_records")

        # Deserialize
        new_fishing_system = FishingSystem(self.fish_db, self.spots)
        deserialize_state(
            data=save_data,
            world=self.world,
            fishing_system=new_fishing_system
        )

        # Check records are preserved
        self.assertEqual(len(new_fishing_system.player_records), 2, "Should have 2 records after load")
        self.assertIn("common_carp", new_fishing_system.player_records)
        self.assertIn("golden_trout", new_fishing_system.player_records)
        self.assertEqual(new_fishing_system.player_records["common_carp"].size, 1.5)
        self.assertEqual(new_fishing_system.player_records["golden_trout"].size, 1.2)

    def test_fish_variety_coverage(self):
        """Test that all water types and time periods have fish."""
        water_types = {WaterType.FRESHWATER, WaterType.SALTWATER, WaterType.SWAMP, WaterType.MAGICAL}
        time_periods = ["DAY", "NIGHT", "DAWN", "DUSK", "MIDNIGHT"]

        # Check water type coverage
        fish_by_water = {wt: [] for wt in water_types}
        for fish in self.fish_db.values():
            for wt in fish.water_types:
                fish_by_water[wt].append(fish.fish_id)

        for water_type in water_types:
            self.assertGreater(
                len(fish_by_water[water_type]), 0,
                f"Should have at least one fish for {water_type.value}"
            )

        # Check time period coverage
        fish_by_time = {tp: [] for tp in time_periods}
        for fish in self.fish_db.values():
            if not fish.time_periods:  # Empty means any time
                for tp in time_periods:
                    fish_by_time[tp].append(fish.fish_id)
            else:
                for tp in fish.time_periods:
                    if tp in fish_by_time:
                        fish_by_time[tp].append(fish.fish_id)

        # At least some fish should be available at each time
        for time_period in time_periods:
            self.assertGreater(
                len(fish_by_time[time_period]), 0,
                f"Should have at least one fish available at {time_period}"
            )


if __name__ == "__main__":
    unittest.main()
