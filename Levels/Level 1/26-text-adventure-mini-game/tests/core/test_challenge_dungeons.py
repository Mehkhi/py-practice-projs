"""Unit tests for core/challenge_dungeons.py - Challenge dungeon system."""

import unittest
import time
from unittest.mock import Mock

from core.challenge_dungeons import (
    ChallengeTier,
    ChallengeModifier,
    ChallengeDungeon,
    ChallengeDungeonProgress,
    ChallengeDungeonManager,
)


class TestChallengeTier(unittest.TestCase):
    def test_tier_values(self):
        """Test that tier enum values are correct."""
        self.assertEqual(ChallengeTier.APPRENTICE.value, "apprentice")
        self.assertEqual(ChallengeTier.ADEPT.value, "adept")
        self.assertEqual(ChallengeTier.EXPERT.value, "expert")
        self.assertEqual(ChallengeTier.MASTER.value, "master")
        self.assertEqual(ChallengeTier.LEGENDARY.value, "legendary")


class TestChallengeModifier(unittest.TestCase):
    def test_modifier_creation(self):
        """Test creating a challenge modifier."""
        modifier = ChallengeModifier(
            modifier_id="brutal",
            name="Brutal",
            description="Enemies deal 50% more damage",
            effect_type="stat_mod",
            effect_data={"enemy_damage_multiplier": 1.5}
        )
        self.assertEqual(modifier.modifier_id, "brutal")
        self.assertEqual(modifier.name, "Brutal")
        self.assertEqual(modifier.effect_type, "stat_mod")


class TestChallengeDungeon(unittest.TestCase):
    def test_dungeon_creation(self):
        """Test creating a challenge dungeon."""
        dungeon = ChallengeDungeon(
            dungeon_id="test_dungeon",
            name="Test Dungeon",
            description="A test dungeon",
            tier=ChallengeTier.APPRENTICE,
            required_level=15,
            map_ids=["map1", "map2"],
            entry_map_id="map1",
            entry_x=5,
            entry_y=5,
            modifiers=[],
            rewards={"gold": 100},
            first_clear_rewards={"gold": 50}
        )
        self.assertEqual(dungeon.dungeon_id, "test_dungeon")
        self.assertEqual(dungeon.tier, ChallengeTier.APPRENTICE)
        self.assertEqual(dungeon.required_level, 15)
        self.assertFalse(dungeon.no_save)
        self.assertFalse(dungeon.no_items)


class TestChallengeDungeonManager(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.modifier = ChallengeModifier(
            modifier_id="brutal",
            name="Brutal",
            description="Enemies deal 50% more damage",
            effect_type="stat_mod",
            effect_data={"enemy_damage_multiplier": 1.5}
        )
        self.modifiers = {"brutal": self.modifier}

        self.dungeon = ChallengeDungeon(
            dungeon_id="test_dungeon",
            name="Test Dungeon",
            description="A test dungeon",
            tier=ChallengeTier.APPRENTICE,
            required_level=15,
            map_ids=["map1"],
            entry_map_id="map1",
            entry_x=5,
            entry_y=5,
            modifiers=["brutal"],
            rewards={"gold": 100, "exp": 200},
            first_clear_rewards={"gold": 50}
        )
        self.dungeons = {"test_dungeon": self.dungeon}

        self.manager = ChallengeDungeonManager(self.dungeons, self.modifiers)

    def test_can_enter_level_requirement_blocks_entry(self):
        """Test that under-leveled players are blocked."""
        can_enter, reason = self.manager.can_enter("test_dungeon", 10, False)
        self.assertFalse(can_enter)
        self.assertIn("level 15", reason)

    def test_can_enter_level_requirement_allows_entry(self):
        """Test that players meeting level requirement can enter."""
        can_enter, reason = self.manager.can_enter("test_dungeon", 15, False)
        self.assertTrue(can_enter)
        self.assertEqual(reason, "")

    def test_final_boss_unlocks_all(self):
        """Test that all dungeons are accessible post-game."""
        # Create a legendary dungeon
        legendary_dungeon = ChallengeDungeon(
            dungeon_id="legendary",
            name="Legendary",
            description="Legendary dungeon",
            tier=ChallengeTier.LEGENDARY,
            required_level=50,
            map_ids=["map1"],
            entry_map_id="map1",
            entry_x=5,
            entry_y=5,
            modifiers=[],
            rewards={},
            first_clear_rewards={}
        )
        self.manager.dungeons["legendary"] = legendary_dungeon

        # Even at level 1, should be able to enter if final boss defeated
        can_enter, reason = self.manager.can_enter("legendary", 1, True)
        self.assertTrue(can_enter)

    def test_legendary_tier_post_game_only(self):
        """Test that legendary tier requires final boss."""
        legendary_dungeon = ChallengeDungeon(
            dungeon_id="legendary",
            name="Legendary",
            description="Legendary dungeon",
            tier=ChallengeTier.LEGENDARY,
            required_level=50,
            map_ids=["map1"],
            entry_map_id="map1",
            entry_x=5,
            entry_y=5,
            modifiers=[],
            rewards={},
            first_clear_rewards={}
        )
        self.manager.dungeons["legendary"] = legendary_dungeon

        # Even at level 50, should be blocked without final boss
        can_enter, reason = self.manager.can_enter("legendary", 50, False)
        self.assertFalse(can_enter)
        self.assertIn("main story", reason)

    def test_modifier_application(self):
        """Test that modifiers correctly modify battle context."""
        battle_context = {}
        self.manager.active_dungeon_id = "test_dungeon"
        result = self.manager.apply_modifiers_to_battle(battle_context)

        self.assertIn("enemy_damage_multiplier", result)
        self.assertEqual(result["enemy_damage_multiplier"], 1.5)

    def test_first_clear_bonus(self):
        """Test that first clear gives bonus rewards."""
        self.manager.enter_dungeon("test_dungeon")
        time.sleep(0.1)  # Small delay to ensure time difference
        rewards = self.manager.exit_dungeon(completed=True)

        # Should have regular rewards + first clear bonus
        self.assertEqual(rewards["gold"], 150)  # 100 + 50
        self.assertEqual(rewards["exp"], 200)

        # Progress should be marked as cleared
        progress = self.manager.progress["test_dungeon"]
        self.assertTrue(progress.cleared)

    def test_best_time_tracking(self):
        """Test that best time updates correctly."""
        self.manager.enter_dungeon("test_dungeon")
        time.sleep(0.1)
        self.manager.exit_dungeon(completed=True)

        progress = self.manager.progress["test_dungeon"]
        self.assertIsNotNone(progress.best_time)
        self.assertGreater(progress.best_time, 0)

        # Second completion with longer time should not update best time
        self.manager.enter_dungeon("test_dungeon")
        time.sleep(0.2)
        self.manager.exit_dungeon(completed=True)

        # Best time should be the first (shorter) time
        self.assertLessEqual(progress.best_time, 0.2)

    def test_death_counting(self):
        """Test that deaths increment on player death."""
        self.manager.enter_dungeon("test_dungeon")
        self.manager.exit_dungeon(completed=False, player_died=True)

        progress = self.manager.progress["test_dungeon"]
        self.assertEqual(progress.deaths, 1)
        self.assertEqual(progress.attempts, 1)

        # Second death
        self.manager.enter_dungeon("test_dungeon")
        self.manager.exit_dungeon(completed=False, player_died=True)
        self.assertEqual(progress.deaths, 2)
        self.assertEqual(progress.attempts, 2)

    def test_no_save_restriction(self):
        """Test that no_save restriction is tracked."""
        no_save_dungeon = ChallengeDungeon(
            dungeon_id="no_save",
            name="No Save",
            description="No save dungeon",
            tier=ChallengeTier.LEGENDARY,
            required_level=50,
            map_ids=["map1"],
            entry_map_id="map1",
            entry_x=5,
            entry_y=5,
            modifiers=[],
            rewards={},
            first_clear_rewards={},
            no_save=True
        )
        self.manager.dungeons["no_save"] = no_save_dungeon

        self.assertTrue(no_save_dungeon.no_save)

    def test_progress_persistence(self):
        """Test that progress survives serialize/deserialize."""
        # Enter and complete dungeon
        self.manager.enter_dungeon("test_dungeon")
        time.sleep(0.1)
        self.manager.exit_dungeon(completed=True)

        # Serialize
        data = self.manager.serialize()

        # Create new manager and deserialize
        new_manager = ChallengeDungeonManager.deserialize(
            data, self.dungeons, self.modifiers
        )

        # Check progress was restored
        progress = new_manager.progress.get("test_dungeon")
        self.assertIsNotNone(progress)
        self.assertTrue(progress.cleared)
        self.assertIsNotNone(progress.best_time)
        self.assertEqual(progress.attempts, 1)

    def test_get_active_modifiers(self):
        """Test getting active modifiers for current dungeon."""
        self.manager.active_dungeon_id = "test_dungeon"
        modifiers = self.manager.get_active_modifiers()

        self.assertEqual(len(modifiers), 1)
        self.assertEqual(modifiers[0].modifier_id, "brutal")

    def test_get_active_modifiers_no_active_dungeon(self):
        """Test getting modifiers when no dungeon is active."""
        self.manager.active_dungeon_id = None
        modifiers = self.manager.get_active_modifiers()

        self.assertEqual(len(modifiers), 0)

    def test_enter_dungeon_tracks_attempts(self):
        """Test that entering a dungeon increments attempts."""
        initial_attempts = self.manager.progress.get("test_dungeon")
        self.assertIsNone(initial_attempts)

        self.manager.enter_dungeon("test_dungeon")
        progress = self.manager.progress["test_dungeon"]
        self.assertEqual(progress.attempts, 1)

        self.manager.exit_dungeon(completed=False)
        self.manager.enter_dungeon("test_dungeon")
        self.assertEqual(progress.attempts, 2)

    def test_exit_dungeon_clears_active(self):
        """Test that exiting dungeon clears active_dungeon_id."""
        self.manager.enter_dungeon("test_dungeon")
        self.assertEqual(self.manager.active_dungeon_id, "test_dungeon")

        self.manager.exit_dungeon(completed=False)
        self.assertIsNone(self.manager.active_dungeon_id)

    def test_apply_modifiers_restriction(self):
        """Test applying restriction modifiers."""
        no_healing_mod = ChallengeModifier(
            modifier_id="no_healing",
            name="No Healing",
            description="Healing disabled",
            effect_type="restriction",
            effect_data={"no_healing": True}
        )
        self.manager.modifiers["no_healing"] = no_healing_mod

        dungeon = ChallengeDungeon(
            dungeon_id="restriction_test",
            name="Restriction Test",
            description="Test restrictions",
            tier=ChallengeTier.APPRENTICE,
            required_level=15,
            map_ids=["map1"],
            entry_map_id="map1",
            entry_x=5,
            entry_y=5,
            modifiers=["no_healing"],
            rewards={},
            first_clear_rewards={}
        )
        self.manager.dungeons["restriction_test"] = dungeon

        self.manager.active_dungeon_id = "restriction_test"
        battle_context = {}
        result = self.manager.apply_modifiers_to_battle(battle_context)

        self.assertTrue(result.get("healing_disabled", False))

    def test_apply_modifiers_hazard(self):
        """Test applying hazard modifiers."""
        poison_mod = ChallengeModifier(
            modifier_id="poison_mist",
            name="Poison Mist",
            description="Poison damage each turn",
            effect_type="hazard",
            effect_data={
                "hazards": [{"type": "poison", "damage": 5, "target": "all"}]
            }
        )
        self.manager.modifiers["poison_mist"] = poison_mod

        dungeon = ChallengeDungeon(
            dungeon_id="hazard_test",
            name="Hazard Test",
            description="Test hazards",
            tier=ChallengeTier.APPRENTICE,
            required_level=15,
            map_ids=["map1"],
            entry_map_id="map1",
            entry_x=5,
            entry_y=5,
            modifiers=["poison_mist"],
            rewards={},
            first_clear_rewards={}
        )
        self.manager.dungeons["hazard_test"] = dungeon

        self.manager.active_dungeon_id = "hazard_test"
        battle_context = {}
        result = self.manager.apply_modifiers_to_battle(battle_context)

        self.assertIn("hazards", result)
        self.assertEqual(len(result["hazards"]), 1)
        self.assertEqual(result["hazards"][0]["type"], "poison")


if __name__ == "__main__":
    unittest.main()
