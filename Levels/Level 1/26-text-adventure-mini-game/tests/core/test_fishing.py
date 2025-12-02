"""Unit tests for core/fishing.py - FishingSystem, Fish, FishingSpot, CaughtFish."""

import unittest
from unittest.mock import patch, MagicMock

from core.fishing import (
    Fish,
    FishingSpot,
    CaughtFish,
    FishingSystem,
    FishRarity,
    WaterType,
)
from core.time_system import TimeOfDay


class TestFishingSystem(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        # Create test fish
        self.common_fish = Fish(
            fish_id="common_carp",
            name="Common Carp",
            rarity=FishRarity.COMMON,
            base_value=15,
            water_types=[WaterType.FRESHWATER],
            time_periods=[],
            min_size=0.5,
            max_size=2.0,
            catch_difficulty=2,
            description="A common fish",
            item_id="fish_common_carp",
        )

        self.rare_fish = Fish(
            fish_id="golden_trout",
            name="Golden Trout",
            rarity=FishRarity.RARE,
            base_value=150,
            water_types=[WaterType.FRESHWATER, WaterType.MAGICAL],
            time_periods=["DAWN", "DUSK"],
            min_size=0.8,
            max_size=1.5,
            catch_difficulty=7,
            description="A rare fish",
            item_id="fish_golden_trout",
        )

        self.legendary_fish = Fish(
            fish_id="abyssal_angler",
            name="Abyssal Angler",
            rarity=FishRarity.LEGENDARY,
            base_value=500,
            water_types=[WaterType.MAGICAL],
            time_periods=["MIDNIGHT"],
            min_size=1.0,
            max_size=3.0,
            catch_difficulty=10,
            description="A legendary fish",
            item_id="fish_abyssal_angler",
        )

        self.fish_db = {
            "common_carp": self.common_fish,
            "golden_trout": self.rare_fish,
            "abyssal_angler": self.legendary_fish,
        }

        # Create test spots
        self.regular_spot = FishingSpot(
            spot_id="starter_pond",
            name="Village Pond",
            map_id="starter_village",
            x=12,
            y=8,
            water_type=WaterType.FRESHWATER,
            is_premium=False,
            fish_pool=["common_carp"],
            rarity_modifiers={},
        )

        self.premium_spot = FishingSpot(
            spot_id="enchanted_spring",
            name="Enchanted Spring",
            map_id="fairy_grove",
            x=7,
            y=5,
            water_type=WaterType.MAGICAL,
            is_premium=True,
            fish_pool=["golden_trout", "abyssal_angler"],
            rarity_modifiers={"rare": 1.5, "legendary": 1.2},
        )

        self.spots = {
            "starter_pond": self.regular_spot,
            "enchanted_spring": self.premium_spot,
        }

        self.system = FishingSystem(self.fish_db, self.spots)

    def test_fish_rarity_affects_catch_chance(self):
        """Test that rare fish are harder to catch than common fish."""
        # Common fish should have higher base chance
        common_chance = self.system.calculate_catch_chance(
            self.common_fish, self.regular_spot
        )
        rare_chance = self.system.calculate_catch_chance(
            self.rare_fish, self.premium_spot
        )
        legendary_chance = self.system.calculate_catch_chance(
            self.legendary_fish, self.premium_spot
        )

        # Common should be easier than rare
        self.assertGreater(common_chance, rare_chance)
        # Rare should be easier than legendary
        self.assertGreater(rare_chance, legendary_chance)

    def test_time_restriction(self):
        """Test that time-restricted fish only available at correct times."""
        # Golden trout requires DAWN or DUSK
        available_dawn = self.system.get_available_fish(
            self.premium_spot, "DAWN"
        )
        available_noon = self.system.get_available_fish(
            self.premium_spot, "NOON"
        )
        available_midnight = self.system.get_available_fish(
            self.premium_spot, "MIDNIGHT"
        )

        # Should be available at DAWN
        self.assertIn(self.rare_fish, available_dawn)
        # Should NOT be available at NOON
        self.assertNotIn(self.rare_fish, available_noon)
        # Abyssal angler should be available at MIDNIGHT
        self.assertIn(self.legendary_fish, available_midnight)
        # But not at DAWN
        self.assertNotIn(self.legendary_fish, available_dawn)

    def test_water_type_restriction(self):
        """Test that fish only available in correct water types."""
        # Common carp is freshwater only
        freshwater_spot = FishingSpot(
            spot_id="test",
            name="Test",
            map_id="test",
            x=0,
            y=0,
            water_type=WaterType.FRESHWATER,
            fish_pool=["common_carp"],
        )
        saltwater_spot = FishingSpot(
            spot_id="test2",
            name="Test2",
            map_id="test",
            x=0,
            y=0,
            water_type=WaterType.SALTWATER,
            fish_pool=["common_carp"],
        )

        available_fresh = self.system.get_available_fish(freshwater_spot, "NOON")
        available_salt = self.system.get_available_fish(saltwater_spot, "NOON")

        # Should be available in freshwater
        self.assertIn(self.common_fish, available_fresh)
        # Should NOT be available in saltwater
        self.assertNotIn(self.common_fish, available_salt)

    def test_premium_spot_better_rates(self):
        """Test that premium spots have improved modifiers."""
        # Calculate chance for rare fish at premium spot
        premium_chance = self.system.calculate_catch_chance(
            self.rare_fish, self.premium_spot
        )

        # Create a regular spot with same fish but no modifiers
        regular_spot_no_mod = FishingSpot(
            spot_id="test",
            name="Test",
            map_id="test",
            x=0,
            y=0,
            water_type=WaterType.MAGICAL,
            is_premium=False,
            fish_pool=["golden_trout"],
            rarity_modifiers={},
        )
        regular_chance = self.system.calculate_catch_chance(
            self.rare_fish, regular_spot_no_mod
        )

        # Premium spot should have better chance due to rarity modifier
        self.assertGreater(premium_chance, regular_chance)

    def test_size_generation_in_range(self):
        """Test that generated sizes are within min/max range."""
        for _ in range(100):  # Test multiple times
            size = self.system.generate_fish_size(self.common_fish)
            self.assertGreaterEqual(size, self.common_fish.min_size)
            self.assertLessEqual(size, self.common_fish.max_size)

        # Test legendary fish range
        for _ in range(100):
            size = self.system.generate_fish_size(self.legendary_fish)
            self.assertGreaterEqual(size, self.legendary_fish.min_size)
            self.assertLessEqual(size, self.legendary_fish.max_size)

    def test_value_calculation(self):
        """Test that value scales correctly with size."""
        # Small fish (at min size)
        small_caught = CaughtFish(fish=self.common_fish, size=0.5)
        small_value = small_caught.value

        # Large fish (at max size)
        large_caught = CaughtFish(fish=self.common_fish, size=2.0)
        large_value = large_caught.value

        # Large fish should be worth more
        self.assertGreater(large_value, small_value)

        # Value should be based on size ratio (size / max_size)
        # At min (0.5): ratio = 0.5/2.0 = 0.25, multiplier = 0.5 + 0.25 = 0.75
        # At max (2.0): ratio = 2.0/2.0 = 1.0, multiplier = 0.5 + 1.0 = 1.5
        expected_small = int(self.common_fish.base_value * 0.75)
        expected_large = int(self.common_fish.base_value * 1.5)
        self.assertEqual(small_value, expected_small)
        self.assertEqual(large_value, expected_large)

    def test_record_tracking(self):
        """Test that personal records are correctly updated."""
        # First catch should be a record
        caught1 = CaughtFish(fish=self.common_fish, size=1.0)
        is_record1 = self.system.record_catch(caught1)
        self.assertTrue(is_record1)
        self.assertEqual(
            self.system.player_records["common_carp"].size, 1.0
        )

        # Smaller catch should not be a record
        caught2 = CaughtFish(fish=self.common_fish, size=0.8)
        is_record2 = self.system.record_catch(caught2)
        self.assertFalse(is_record2)
        self.assertEqual(
            self.system.player_records["common_carp"].size, 1.0
        )

        # Larger catch should be a new record
        caught3 = CaughtFish(fish=self.common_fish, size=1.5)
        is_record3 = self.system.record_catch(caught3)
        self.assertTrue(is_record3)
        self.assertEqual(
            self.system.player_records["common_carp"].size, 1.5
        )

    def test_bait_improves_odds(self):
        """Test that bait increases catch chance."""
        # Use rare fish with lower base chance to avoid capping
        chance_no_bait = self.system.calculate_catch_chance(
            self.rare_fish, self.premium_spot, has_bait=False
        )
        chance_with_bait = self.system.calculate_catch_chance(
            self.rare_fish, self.premium_spot, has_bait=True
        )

        # Bait should improve chance by 0.2 (may be capped at 1.0)
        expected = min(chance_no_bait + 0.2, 1.0)
        self.assertAlmostEqual(chance_with_bait, expected, places=5)
        self.assertGreaterEqual(chance_with_bait, chance_no_bait)

    def test_rod_quality_improves_odds(self):
        """Test that better rods increase catch chance."""
        # Use rare fish with lower base chance to avoid capping
        chance_rod1 = self.system.calculate_catch_chance(
            self.rare_fish, self.premium_spot, rod_quality=1
        )
        chance_rod5 = self.system.calculate_catch_chance(
            self.rare_fish, self.premium_spot, rod_quality=5
        )
        chance_rod10 = self.system.calculate_catch_chance(
            self.rare_fish, self.premium_spot, rod_quality=10
        )

        # Better rod should improve chance
        self.assertGreater(chance_rod5, chance_rod1)
        # Rod 10 may be capped, but should be at least as good as rod 5
        self.assertGreaterEqual(chance_rod10, chance_rod5)

        # Rod 5 should add 0.4 (0.1 * 4, since rod_quality=1 already adds 0.1)
        # Rod 10 should add 0.9 (0.1 * 9), but may be capped at 1.0
        self.assertAlmostEqual(
            chance_rod5, chance_rod1 + 0.4, places=5
        )
        expected_rod10 = min(chance_rod1 + 0.9, 1.0)
        self.assertAlmostEqual(chance_rod10, expected_rod10, places=5)

    def test_serialize_deserialize(self):
        """Test that fishing state survives save/load."""
        # Record some catches
        caught1 = CaughtFish(fish=self.common_fish, size=1.5)
        caught2 = CaughtFish(fish=self.rare_fish, size=1.2)
        self.system.record_catch(caught1)
        self.system.record_catch(caught2)

        # Serialize
        data = self.system.serialize()

        # Deserialize
        new_system = FishingSystem.deserialize(data, self.fish_db, self.spots)

        # Check that records are preserved
        self.assertEqual(len(new_system.player_records), 2)
        self.assertEqual(
            new_system.player_records["common_carp"].size, 1.5
        )
        self.assertEqual(
            new_system.player_records["golden_trout"].size, 1.2
        )
        self.assertEqual(
            new_system.player_records["common_carp"].fish.fish_id,
            "common_carp"
        )

    def test_get_spot_at(self):
        """Test finding spot by coordinates."""
        spot = self.system.get_spot_at("starter_village", 12, 8)
        self.assertIsNotNone(spot)
        self.assertEqual(spot.spot_id, "starter_pond")

        # Non-existent spot
        spot2 = self.system.get_spot_at("starter_village", 99, 99)
        self.assertIsNone(spot2)

    def test_get_available_fish_empty_pool(self):
        """Test handling of empty fish pool."""
        empty_spot = FishingSpot(
            spot_id="empty",
            name="Empty",
            map_id="test",
            x=0,
            y=0,
            water_type=WaterType.FRESHWATER,
            fish_pool=[],
        )
        available = self.system.get_available_fish(empty_spot, "NOON")
        self.assertEqual(len(available), 0)

    def test_caught_fish_size_category(self):
        """Test size category calculation."""
        # ratio = (size - min_size) / (max_size - min_size)
        # For common_fish: min=0.5, max=2.0, range=1.5

        # Tiny (ratio < 0.25): size < 0.5 + 0.25*1.5 = 0.875
        tiny = CaughtFish(fish=self.common_fish, size=0.8)  # ratio = 0.2
        self.assertEqual(tiny.size_category, "tiny")

        # Small (0.25 <= ratio < 0.5): 0.875 <= size < 1.25
        small = CaughtFish(fish=self.common_fish, size=1.0)  # ratio = 0.33
        self.assertEqual(small.size_category, "small")

        # Medium (0.5 <= ratio < 0.75): 1.25 <= size < 1.625
        medium = CaughtFish(fish=self.common_fish, size=1.4)  # ratio = 0.6
        self.assertEqual(medium.size_category, "medium")

        # Large (0.75 <= ratio < 0.95): 1.625 <= size < 1.925
        large = CaughtFish(fish=self.common_fish, size=1.8)  # ratio = 0.87
        self.assertEqual(large.size_category, "large")

        # Enormous (ratio >= 0.95): size >= 1.925
        enormous = CaughtFish(fish=self.common_fish, size=1.99)  # ratio = 0.99
        self.assertEqual(enormous.size_category, "enormous")

    def test_get_fishing_stats(self):
        """Test fishing statistics retrieval."""
        # No records initially
        stats = self.system.get_fishing_stats()
        self.assertEqual(stats["total_caught"], 0)
        self.assertEqual(len(stats["records"]), 0)

        # Add some records
        self.system.record_catch(CaughtFish(fish=self.common_fish, size=1.5))
        self.system.record_catch(CaughtFish(fish=self.rare_fish, size=1.2))

        stats = self.system.get_fishing_stats()
        self.assertEqual(stats["total_caught"], 2)
        self.assertEqual(stats["records"]["common_carp"], 1.5)
        self.assertEqual(stats["records"]["golden_trout"], 1.2)


if __name__ == "__main__":
    unittest.main()
