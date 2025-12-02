"""Unit tests for core/post_game.py - Post-game integration system."""

import unittest
from unittest.mock import Mock

from core.post_game import (
    PostGameUnlock,
    PostGameState,
    PostGameManager,
)


class TestPostGameUnlock(unittest.TestCase):
    def test_unlock_creation(self):
        """Test creating a post-game unlock."""
        unlock = PostGameUnlock(
            unlock_id="test_unlock",
            name="Test Unlock",
            description="A test unlock",
            unlock_type="feature",
            requires_ending=None
        )
        self.assertEqual(unlock.unlock_id, "test_unlock")
        self.assertEqual(unlock.name, "Test Unlock")
        self.assertEqual(unlock.unlock_type, "feature")
        self.assertIsNone(unlock.requires_ending)

    def test_unlock_with_ending_requirement(self):
        """Test unlock with specific ending requirement."""
        unlock = PostGameUnlock(
            unlock_id="good_ending_bonus",
            name="Hero's Reward",
            description="Bonus for good ending",
            unlock_type="cosmetic",
            requires_ending="good"
        )
        self.assertEqual(unlock.requires_ending, "good")


class TestPostGameState(unittest.TestCase):
    def test_state_creation(self):
        """Test creating post-game state."""
        state = PostGameState()
        self.assertFalse(state.final_boss_defeated)
        self.assertIsNone(state.ending_achieved)
        self.assertEqual(state.post_game_time, 0.0)
        self.assertEqual(state.secret_bosses_defeated, 0)
        self.assertEqual(state.challenge_dungeons_cleared, 0)
        self.assertFalse(state.true_ending_unlocked)

    def test_state_with_values(self):
        """Test state with values set."""
        state = PostGameState(
            final_boss_defeated=True,
            ending_achieved="good",
            post_game_time=100.5,
            secret_bosses_defeated=3,
            challenge_dungeons_cleared=5
        )
        self.assertTrue(state.final_boss_defeated)
        self.assertEqual(state.ending_achieved, "good")
        self.assertEqual(state.post_game_time, 100.5)
        self.assertEqual(state.secret_bosses_defeated, 3)
        self.assertEqual(state.challenge_dungeons_cleared, 5)


class TestPostGameManager(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.unlocks = {
            "all_challenge_dungeons": PostGameUnlock(
                unlock_id="all_challenge_dungeons",
                name="Challenge Dungeons Unlocked",
                description="All challenge dungeons accessible",
                unlock_type="dungeon",
                requires_ending=None
            ),
            "legendary_tier": PostGameUnlock(
                unlock_id="legendary_tier",
                name="Legendary Tier",
                description="Legendary content unlocked",
                unlock_type="dungeon",
                requires_ending=None
            ),
            "good_ending_bonus": PostGameUnlock(
                unlock_id="good_ending_bonus",
                name="Hero's Reward",
                description="Bonus for good ending",
                unlock_type="cosmetic",
                requires_ending="good"
            ),
        }
        self.manager = PostGameManager(self.unlocks)

    def test_manager_initialization(self):
        """Test manager initialization."""
        self.assertEqual(len(self.manager.unlocks), 3)
        self.assertFalse(self.manager.state.final_boss_defeated)
        self.assertEqual(len(self.manager.active_unlocks), 0)

    def test_final_boss_triggers_unlocks(self):
        """Test that defeating final boss triggers unlocks."""
        newly_unlocked = self.manager.on_final_boss_defeated("good")

        self.assertTrue(self.manager.state.final_boss_defeated)
        self.assertEqual(self.manager.state.ending_achieved, "good")
        # Should unlock all unlocks that don't require ending or require "good"
        self.assertEqual(len(newly_unlocked), 3)  # All three unlocks
        self.assertEqual(len(self.manager.active_unlocks), 3)

    def test_ending_specific_unlocks(self):
        """Test that ending-specific unlocks only unlock for correct ending."""
        # Bad ending should not unlock good_ending_bonus
        newly_unlocked = self.manager.on_final_boss_defeated("bad")

        self.assertTrue(self.manager.state.final_boss_defeated)
        self.assertEqual(self.manager.state.ending_achieved, "bad")
        # Should only unlock unlocks without ending requirement
        self.assertEqual(len(newly_unlocked), 2)  # all_challenge_dungeons and legendary_tier
        self.assertIn("all_challenge_dungeons", self.manager.active_unlocks)
        self.assertIn("legendary_tier", self.manager.active_unlocks)
        self.assertNotIn("good_ending_bonus", self.manager.active_unlocks)

    def test_level_locks_removed(self):
        """Test that level locks are removed post-game."""
        # Before final boss
        self.assertFalse(self.manager.check_level_lock(50, 10))

        # After final boss
        self.manager.on_final_boss_defeated("good")
        self.assertTrue(self.manager.check_level_lock(50, 10))  # Should bypass level requirement
        self.assertTrue(self.manager.check_level_lock(100, 1))  # Even very high requirements

    def test_level_locks_before_post_game(self):
        """Test that level locks still work before post-game."""
        # Should check actual level
        self.assertFalse(self.manager.check_level_lock(50, 10))
        self.assertTrue(self.manager.check_level_lock(50, 50))
        self.assertTrue(self.manager.check_level_lock(50, 60))

    def test_is_unlocked(self):
        """Test checking if unlock is active."""
        self.assertFalse(self.manager.is_unlocked("all_challenge_dungeons"))

        self.manager.on_final_boss_defeated("good")
        self.assertTrue(self.manager.is_unlocked("all_challenge_dungeons"))
        self.assertTrue(self.manager.is_unlocked("legendary_tier"))
        self.assertTrue(self.manager.is_unlocked("good_ending_bonus"))

    def test_serialize(self):
        """Test serialization."""
        self.manager.on_final_boss_defeated("good")
        self.manager.state.post_game_time = 100.5
        self.manager.state.secret_bosses_defeated = 2
        self.manager.state.challenge_dungeons_cleared = 3

        data = self.manager.serialize()

        self.assertTrue(data["final_boss_defeated"])
        self.assertEqual(data["ending_achieved"], "good")
        self.assertEqual(data["post_game_time"], 100.5)
        self.assertEqual(data["secret_bosses_defeated"], 2)
        self.assertEqual(data["challenge_dungeons_cleared"], 3)
        self.assertIn("all_challenge_dungeons", data["active_unlocks"])

    def test_deserialize(self):
        """Test deserialization."""
        data = {
            "final_boss_defeated": True,
            "ending_achieved": "good",
            "post_game_time": 100.5,
            "secret_bosses_defeated": 2,
            "challenge_dungeons_cleared": 3,
            "active_unlocks": ["all_challenge_dungeons", "legendary_tier"]
        }

        manager = PostGameManager.deserialize(data, self.unlocks)

        self.assertTrue(manager.state.final_boss_defeated)
        self.assertEqual(manager.state.ending_achieved, "good")
        self.assertEqual(manager.state.post_game_time, 100.5)
        self.assertEqual(manager.state.secret_bosses_defeated, 2)
        self.assertEqual(manager.state.challenge_dungeons_cleared, 3)
        self.assertIn("all_challenge_dungeons", manager.active_unlocks)
        self.assertIn("legendary_tier", manager.active_unlocks)

    def test_post_game_state_persistence(self):
        """Test that state persists across serialize/deserialize."""
        self.manager.on_final_boss_defeated("good")
        self.manager.state.post_game_time = 200.0
        self.manager.state.secret_bosses_defeated = 5

        data = self.manager.serialize()
        restored = PostGameManager.deserialize(data, self.unlocks)

        self.assertEqual(restored.state.final_boss_defeated, self.manager.state.final_boss_defeated)
        self.assertEqual(restored.state.ending_achieved, self.manager.state.ending_achieved)
        self.assertEqual(restored.state.post_game_time, self.manager.state.post_game_time)
        self.assertEqual(restored.state.secret_bosses_defeated, self.manager.state.secret_bosses_defeated)
        self.assertEqual(restored.active_unlocks, self.manager.active_unlocks)

    def test_get_post_game_message(self):
        """Test getting post-game welcome message."""
        message = self.manager.get_post_game_message()
        self.assertIn("Congratulations", message)
        self.assertIn("level restrictions", message)
        self.assertIn("Challenge Dungeons", message)

    def test_no_duplicate_unlocks(self):
        """Test that calling on_final_boss_defeated twice doesn't duplicate unlocks."""
        newly_unlocked1 = self.manager.on_final_boss_defeated("good")
        newly_unlocked2 = self.manager.on_final_boss_defeated("good")

        self.assertEqual(len(newly_unlocked1), 3)
        self.assertEqual(len(newly_unlocked2), 0)  # No new unlocks second time
        self.assertEqual(len(self.manager.active_unlocks), 3)


if __name__ == "__main__":
    unittest.main()
