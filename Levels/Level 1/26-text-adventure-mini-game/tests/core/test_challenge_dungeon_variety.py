"""Unit tests for challenge dungeon variety and new features."""

import unittest
import time
from unittest.mock import Mock, MagicMock

from core.challenge_dungeons import (
    ChallengeTier,
    ChallengeModifier,
    ChallengeDungeon,
    ChallengeDungeonManager,
)
from core.loaders.challenge_loader import load_challenge_dungeons


class TestChallengeDungeonVariety(unittest.TestCase):
    """Test variety of challenge dungeons and new features."""

    def setUp(self):
        """Set up test fixtures."""
        self.dungeons, self.modifiers = load_challenge_dungeons()

    def test_all_tiers_have_dungeons(self):
        """Verify each tier has at least one dungeon."""
        dungeons_by_tier = {}
        for dungeon in self.dungeons.values():
            tier = dungeon.tier
            if tier not in dungeons_by_tier:
                dungeons_by_tier[tier] = []
            dungeons_by_tier[tier].append(dungeon.dungeon_id)

        # Check all tiers have at least one dungeon
        for tier in ChallengeTier:
            self.assertIn(
                tier,
                dungeons_by_tier,
                f"Tier {tier.value} has no dungeons"
            )
            self.assertGreater(
                len(dungeons_by_tier[tier]),
                0,
                f"Tier {tier.value} has no dungeons"
            )

    def test_modifier_combinations(self):
        """Test multiple modifiers apply correctly."""
        # Find a dungeon with multiple modifiers
        multi_mod_dungeon = None
        for dungeon in self.dungeons.values():
            if len(dungeon.modifiers) >= 2:
                multi_mod_dungeon = dungeon
                break

        self.assertIsNotNone(
            multi_mod_dungeon,
            "No dungeon found with multiple modifiers"
        )

        # Test modifier application
        manager = ChallengeDungeonManager(self.dungeons, self.modifiers)
        manager.active_dungeon_id = multi_mod_dungeon.dungeon_id

        battle_context = {}
        result = manager.apply_modifiers_to_battle(battle_context)

        # Should have multiple modifier effects
        modifier_count = len(multi_mod_dungeon.modifiers)
        self.assertGreater(modifier_count, 1)

        # Check that modifiers were applied
        has_stat_mod = any(
            "enemy_hp_multiplier" in result or
            "enemy_damage_multiplier" in result or
            "enemy_speed_multiplier" in result or
            "enemy_lifesteal" in result
        )
        has_restriction = "healing_disabled" in result
        has_hazard = "hazards" in result or "stat_scramble" in result

        # At least one type of modifier should be present
        self.assertTrue(
            has_stat_mod or has_restriction or has_hazard,
            "No modifiers were applied to battle context"
        )

    def test_time_limit_enforcement(self):
        """Verify time-limited dungeons fail on timeout."""
        # Find a time-limited dungeon
        time_limit_dungeon = None
        for dungeon in self.dungeons.values():
            if dungeon.time_limit:
                time_limit_dungeon = dungeon
                break

        if not time_limit_dungeon:
            self.skipTest("No time-limited dungeon found")

        manager = ChallengeDungeonManager(self.dungeons, self.modifiers)
        manager.enter_dungeon(time_limit_dungeon.dungeon_id)

        # Check that floor timer is set
        self.assertIsNotNone(manager.floor_time_limit)
        self.assertEqual(manager.floor_time_limit, time_limit_dungeon.time_limit)

        # Test timer check
        manager.start_floor()
        time.sleep(0.01)  # Small delay

        # Should not be expired yet
        elapsed = time.time() - manager.current_floor_start_time
        self.assertFalse(manager.check_floor_timer(elapsed))

        # Simulate timeout
        manager.current_floor_start_time = time.time() - (time_limit_dungeon.time_limit + 1)
        elapsed = time.time() - manager.current_floor_start_time
        self.assertTrue(manager.check_floor_timer(elapsed))

    def test_life_drain_mechanic(self):
        """Verify life drain heals enemies correctly."""
        # Find dungeon with life_drain modifier
        life_drain_dungeon = None
        for dungeon in self.dungeons.values():
            if "life_drain" in dungeon.modifiers:
                life_drain_dungeon = dungeon
                break

        if not life_drain_dungeon:
            self.skipTest("No dungeon with life_drain modifier found")

        manager = ChallengeDungeonManager(self.dungeons, self.modifiers)
        manager.active_dungeon_id = life_drain_dungeon.dungeon_id

        battle_context = {}
        result = manager.apply_modifiers_to_battle(battle_context)

        # Should have enemy_lifesteal in battle context
        self.assertIn("enemy_lifesteal", result)
        self.assertEqual(result["enemy_lifesteal"], 0.25)

    def test_reality_warp_scramble(self):
        """Verify stat scramble applies randomly."""
        # Find dungeon with reality_warp modifier
        reality_warp_dungeon = None
        for dungeon in self.dungeons.values():
            if "reality_warp" in dungeon.modifiers:
                reality_warp_dungeon = dungeon
                break

        if not reality_warp_dungeon:
            self.skipTest("No dungeon with reality_warp modifier found")

        manager = ChallengeDungeonManager(self.dungeons, self.modifiers)
        manager.active_dungeon_id = reality_warp_dungeon.dungeon_id

        battle_context = {}
        result = manager.apply_modifiers_to_battle(battle_context)

        # Should have stat_scramble flag
        self.assertIn("stat_scramble", result)
        self.assertTrue(result["stat_scramble"])

    def test_dungeon_select_scene(self):
        """Test selection UI shows correct info."""
        from engine.challenge_select_scene import ChallengeSelectScene
        from core.entities import Player
        from core.world import World
        from core.stats import Stats

        # Create mock scene manager
        mock_manager = Mock()
        mock_manager.challenge_dungeon_manager = ChallengeDungeonManager(
            self.dungeons, self.modifiers
        )

        # Create minimal player and world
        player = Mock(spec=Player)
        player.stats = Mock(spec=Stats)
        player.stats.level = 30

        world = Mock(spec=World)
        world.get_flag = Mock(return_value=False)

        # Create scene
        scene = ChallengeSelectScene(
            manager=mock_manager,
            challenge_manager=mock_manager.challenge_dungeon_manager,
            player=player,
            world=world
        )

        # Check that dungeons are grouped by tier
        self.assertGreater(len(scene.dungeon_list), 0)
        self.assertGreater(len(scene.dungeons_by_tier), 0)

        # Check that all dungeons are in the list
        self.assertEqual(len(scene.dungeon_list), len(self.dungeons))

    def test_new_dungeons_exist(self):
        """Verify all new dungeons are defined."""
        expected_dungeons = [
            "frozen_abyss",
            "crimson_spire",
            "clockwork_labyrinth",
            "void_sanctum",
        ]

        for dungeon_id in expected_dungeons:
            self.assertIn(
                dungeon_id,
                self.dungeons,
                f"Dungeon {dungeon_id} not found"
            )

    def test_new_modifiers_exist(self):
        """Verify new modifiers are defined."""
        expected_modifiers = ["life_drain", "reality_warp"]

        for modifier_id in expected_modifiers:
            self.assertIn(
                modifier_id,
                self.modifiers,
                f"Modifier {modifier_id} not found"
            )

    def test_frozen_abyss_has_ice_theme(self):
        """Verify Frozen Abyss has correct modifiers."""
        if "frozen_abyss" not in self.dungeons:
            self.skipTest("Frozen Abyss dungeon not found")

        dungeon = self.dungeons["frozen_abyss"]
        self.assertEqual(dungeon.tier, ChallengeTier.ADEPT)
        self.assertIn("swift_enemies", dungeon.modifiers)
        self.assertIn("fortified", dungeon.modifiers)

    def test_crimson_spire_has_life_drain(self):
        """Verify Crimson Spire has life drain."""
        if "crimson_spire" not in self.dungeons:
            self.skipTest("Crimson Spire dungeon not found")

        dungeon = self.dungeons["crimson_spire"]
        self.assertEqual(dungeon.tier, ChallengeTier.EXPERT)
        self.assertIn("life_drain", dungeon.modifiers)

    def test_clockwork_labyrinth_has_time_limit(self):
        """Verify Clockwork Labyrinth has time limit."""
        if "clockwork_labyrinth" not in self.dungeons:
            self.skipTest("Clockwork Labyrinth dungeon not found")

        dungeon = self.dungeons["clockwork_labyrinth"]
        self.assertEqual(dungeon.tier, ChallengeTier.EXPERT)
        self.assertIsNotNone(dungeon.time_limit)
        self.assertEqual(dungeon.time_limit, 180)

    def test_void_sanctum_has_reality_warp(self):
        """Verify Void Sanctum has reality warp."""
        if "void_sanctum" not in self.dungeons:
            self.skipTest("Void Sanctum dungeon not found")

        dungeon = self.dungeons["void_sanctum"]
        self.assertEqual(dungeon.tier, ChallengeTier.MASTER)
        self.assertIn("reality_warp", dungeon.modifiers)
        self.assertIn("no_healing", dungeon.modifiers)

    def test_trials_of_eternity_expanded(self):
        """Verify Trials of Eternity has all 6 maps."""
        if "trials_of_eternity" not in self.dungeons:
            self.skipTest("Trials of Eternity dungeon not found")

        dungeon = self.dungeons["trials_of_eternity"]
        self.assertEqual(len(dungeon.map_ids), 6)
        self.assertIn("trial_floor_1", dungeon.map_ids)
        self.assertIn("trial_final", dungeon.map_ids)


if __name__ == "__main__":
    unittest.main()
