#!/usr/bin/env python3
"""Tests for achievement system stat-based achievements and game completion."""

import unittest

from core.achievements import AchievementManager, Achievement, load_achievement_manager
from engine.event_bus import EventBus


class TestStatAchievements(unittest.TestCase):
    """Tests for stat-based achievement tracking."""

    def setUp(self):
        """Set up a fresh achievement manager for each test."""
        self.manager = load_achievement_manager()

    def test_total_kills_100_unlocks_at_threshold(self):
        """Test that total_kills_100 achievement unlocks at exactly 100 kills."""
        stats = {"total_kills": 100}
        unlocked = self.manager.check_stat_achievements(stats)
        self.assertIn("total_kills_100", unlocked)

        # Verify achievement is marked as unlocked
        ach = self.manager.get_achievement("total_kills_100")
        self.assertIsNotNone(ach)
        self.assertTrue(ach.unlocked)
        self.assertEqual(ach.current_count, 100)

    def test_total_kills_100_does_not_unlock_below_threshold(self):
        """Test that total_kills_100 achievement doesn't unlock below 100."""
        stats = {"total_kills": 99}
        unlocked = self.manager.check_stat_achievements(stats)
        self.assertNotIn("total_kills_100", unlocked)

        ach = self.manager.get_achievement("total_kills_100")
        self.assertIsNotNone(ach)
        self.assertFalse(ach.unlocked)

    def test_total_kills_500_unlocks_at_threshold(self):
        """Test that total_kills_500 achievement unlocks at 500 kills."""
        stats = {"total_kills": 500}
        unlocked = self.manager.check_stat_achievements(stats)
        self.assertIn("total_kills_500", unlocked)

        ach = self.manager.get_achievement("total_kills_500")
        self.assertTrue(ach.unlocked)

    def test_gold_earned_5000_unlocks(self):
        """Test that gold_earned_5000 achievement unlocks at 5000 gold."""
        stats = {"total_gold_earned": 5000}
        unlocked = self.manager.check_stat_achievements(stats)
        self.assertIn("gold_earned_5000", unlocked)

    def test_gold_earned_10000_unlocks(self):
        """Test that gold_earned_10000 achievement unlocks at 10000 gold."""
        stats = {"total_gold_earned": 10000}
        unlocked = self.manager.check_stat_achievements(stats)
        self.assertIn("gold_earned_10000", unlocked)

    def test_side_quest_master_unlocks_at_10(self):
        """Test that side_quest_master achievement unlocks at 10 side quests."""
        stats = {"side_quests_completed": 10}
        unlocked = self.manager.check_stat_achievements(stats)
        self.assertIn("side_quest_master", unlocked)

    def test_all_side_quests_unlocks_at_17(self):
        """Test that all_side_quests achievement unlocks at 17 side quests."""
        stats = {"side_quests_completed": 17}
        unlocked = self.manager.check_stat_achievements(stats)
        self.assertIn("all_side_quests", unlocked)

    def test_quests_completed_20_unlocks(self):
        """Test that quests_completed_20 achievement unlocks at 20 quests."""
        stats = {"quests_completed": 20}
        unlocked = self.manager.check_stat_achievements(stats)
        self.assertIn("quests_completed_20", unlocked)

    def test_quests_completed_30_unlocks(self):
        """Test that quests_completed_30 achievement unlocks at 30 quests."""
        stats = {"quests_completed": 30}
        unlocked = self.manager.check_stat_achievements(stats)
        self.assertIn("quests_completed_30", unlocked)

    def test_all_endings_unlocks_at_3(self):
        """Test that all_endings achievement unlocks at 3 endings seen."""
        stats = {"endings_seen": 3}
        unlocked = self.manager.check_stat_achievements(stats)
        self.assertIn("all_endings", unlocked)

    def test_all_endings_does_not_unlock_below_3(self):
        """Test that all_endings achievement doesn't unlock below 3."""
        stats = {"endings_seen": 2}
        unlocked = self.manager.check_stat_achievements(stats)
        self.assertNotIn("all_endings", unlocked)

    def test_multiple_stat_achievements_unlock_together(self):
        """Test that multiple stat achievements can unlock in one call."""
        stats = {
            "total_kills": 100,
            "total_gold_earned": 5000,
            "side_quests_completed": 10,
        }
        unlocked = self.manager.check_stat_achievements(stats)
        self.assertIn("total_kills_100", unlocked)
        self.assertIn("gold_earned_5000", unlocked)
        self.assertIn("side_quest_master", unlocked)

    def test_already_unlocked_achievement_not_returned_again(self):
        """Test that already unlocked achievements aren't returned again."""
        stats = {"total_kills": 100}

        # First call should unlock
        unlocked1 = self.manager.check_stat_achievements(stats)
        self.assertIn("total_kills_100", unlocked1)

        # Second call should not return it again
        unlocked2 = self.manager.check_stat_achievements(stats)
        self.assertNotIn("total_kills_100", unlocked2)

    def test_progress_tracking_for_partial_completion(self):
        """Test that progress is tracked even when not complete."""
        stats = {"total_kills": 50}
        self.manager.check_stat_achievements(stats)

        ach = self.manager.get_achievement("total_kills_100")
        self.assertIsNotNone(ach)
        self.assertFalse(ach.unlocked)
        self.assertEqual(ach.current_count, 50)


class TestEndingAchievements(unittest.TestCase):
    """Tests for ending-related achievements."""

    def setUp(self):
        """Set up a fresh achievement manager for each test."""
        self.manager = load_achievement_manager()

    def test_good_ending_achievement_unlocks(self):
        """Test that good_ending achievement unlocks via on_game_completed."""
        unlocked = self.manager.on_game_completed("good")
        self.assertIn("good_ending", unlocked)

        ach = self.manager.get_achievement("good_ending")
        self.assertTrue(ach.unlocked)

    def test_bad_ending_achievement_unlocks(self):
        """Test that bad_ending achievement unlocks via on_game_completed."""
        unlocked = self.manager.on_game_completed("bad")
        self.assertIn("bad_ending", unlocked)

    def test_neutral_ending_achievement_unlocks(self):
        """Test that neutral_ending achievement unlocks via on_game_completed."""
        unlocked = self.manager.on_game_completed("neutral")
        self.assertIn("neutral_ending", unlocked)

    def test_true_ending_requires_all_side_quests(self):
        """Test that true_ending requires all_side_quests prerequisite."""
        # Try to unlock true_ending without all_side_quests
        unlocked = self.manager.on_game_completed("good")
        self.assertNotIn("true_ending", unlocked)

        # Now unlock all_side_quests first
        self.manager.check_stat_achievements({"side_quests_completed": 17})

        # Reset good_ending to test true_ending
        # (In practice, this would be a new manager or reset)
        manager2 = load_achievement_manager()
        manager2.check_stat_achievements({"side_quests_completed": 17})
        unlocked2 = manager2.on_game_completed("good")

        # Both good_ending and true_ending should unlock
        self.assertIn("good_ending", unlocked2)
        self.assertIn("true_ending", unlocked2)


class TestNGPlusAchievements(unittest.TestCase):
    """Tests for New Game+ cycle achievements."""

    def setUp(self):
        """Set up a fresh achievement manager for each test."""
        self.manager = load_achievement_manager()

    def test_ng_plus_1_unlocks_via_flag(self):
        """Test that ng_plus_1 achievement unlocks via flag."""
        unlocked = self.manager.on_flag_set("ng_plus_cycle_1_complete")
        self.assertIn("ng_plus_1", unlocked)

    def test_ng_plus_2_unlocks_via_flag(self):
        """Test that ng_plus_2 achievement unlocks via flag."""
        unlocked = self.manager.on_flag_set("ng_plus_cycle_2_complete")
        self.assertIn("ng_plus_2", unlocked)

    def test_ng_plus_3_unlocks_via_flag(self):
        """Test that ng_plus_3 achievement unlocks via flag."""
        unlocked = self.manager.on_flag_set("ng_plus_cycle_3_complete")
        self.assertIn("ng_plus_3", unlocked)

    def test_ng_plus_achievements_are_hidden(self):
        """Test that NG+ achievements are hidden until unlocked."""
        ng1 = self.manager.get_achievement("ng_plus_1")
        ng2 = self.manager.get_achievement("ng_plus_2")
        ng3 = self.manager.get_achievement("ng_plus_3")

        self.assertTrue(ng1.hidden)
        self.assertTrue(ng2.hidden)
        self.assertTrue(ng3.hidden)


class TestQuestMilestoneAchievements(unittest.TestCase):
    """Tests for quest milestone achievements."""

    def setUp(self):
        """Set up a fresh achievement manager for each test."""
        self.manager = load_achievement_manager()

    def test_cave_exploration_quest_achievement(self):
        """Test that cave_explorer_quest achievement unlocks on quest completion."""
        unlocked = self.manager.on_quest_completed("cave_exploration")
        self.assertIn("cave_explorer_quest", unlocked)

    def test_garden_secrets_quest_achievement(self):
        """Test that garden_secrets_quest achievement unlocks on quest completion."""
        unlocked = self.manager.on_quest_completed("garden_secrets")
        self.assertIn("garden_secrets_quest", unlocked)

    def test_ruins_expedition_quest_achievement(self):
        """Test that ruins_expedition_quest achievement unlocks on quest completion."""
        unlocked = self.manager.on_quest_completed("ruins_expedition")
        self.assertIn("ruins_expedition_quest", unlocked)

    def test_treasure_hunt_quest_achievement(self):
        """Test that treasure_hunt_quest achievement unlocks on quest completion."""
        unlocked = self.manager.on_quest_completed("treasure_hunt")
        self.assertIn("treasure_hunt_quest", unlocked)


class TestAchievementFormatting(unittest.TestCase):
    """Tests for helper formatting methods on Achievement."""

    def setUp(self):
        """Set up a fresh achievement manager for each formatting test."""
        self.manager = load_achievement_manager()

    def _make_achievement(self) -> Achievement:
        return Achievement(
            id="format_test",
            name="Formatting Check",
            description="Complete something special.",
            target_count=5,
        )

    def test_unlock_display_formats_iso_timestamp(self):
        achievement = self._make_achievement()
        achievement.unlocked = True
        achievement.unlock_time = "2025-01-02T13:45:00"

        display = achievement.get_unlock_display()
        self.assertIn("Jan 02, 2025", display)
        self.assertIn("01:45 PM", display)

    def test_unlock_display_returns_locked_when_not_complete(self):
        achievement = self._make_achievement()
        self.assertEqual(achievement.get_unlock_display(), "Locked")

    def test_reward_lines_include_all_rewards(self):
        achievement = self._make_achievement()
        achievement.reward_gold = 250
        achievement.reward_exp = 40
        achievement.reward_items = {"health_potion": 2}
        achievement.reward_title = "Hero"

        rewards = achievement.get_reward_lines()
        self.assertIn("250 Gold", rewards)
        self.assertIn("40 EXP", rewards)
        self.assertIn("Health Potion x2", rewards)
        self.assertIn("Title: Hero", rewards)

    def test_reward_lines_defaults_to_no_rewards(self):
        achievement = self._make_achievement()
        self.assertEqual(achievement.get_reward_lines(), ["No rewards"])

    def test_progress_text_varies_with_state(self):
        achievement = self._make_achievement()
        achievement.current_count = 3
        self.assertEqual(achievement.get_progress_text(), "3/5")
        achievement.unlocked = True
        self.assertEqual(achievement.get_progress_text(), "Completed")

    def test_final_confrontation_quest_achievement(self):
        """Test that final_confrontation_quest achievement unlocks on quest completion."""
        unlocked = self.manager.on_quest_completed("final_confrontation")
        self.assertIn("final_confrontation_quest", unlocked)


class TestForceUnlock(unittest.TestCase):
    """Tests for the _force_unlock method."""

    def setUp(self):
        """Set up a fresh achievement manager for each test."""
        self.manager = load_achievement_manager()

    def test_force_unlock_sets_unlocked_state(self):
        """Test that _force_unlock properly sets achievement state."""
        ach = self.manager.get_achievement("total_kills_100")
        self.assertFalse(ach.unlocked)

        result = self.manager._force_unlock(ach)

        self.assertTrue(result)
        self.assertTrue(ach.unlocked)
        self.assertEqual(ach.current_count, ach.target_count)
        self.assertIsNotNone(ach.unlock_time)

    def test_force_unlock_returns_false_if_already_unlocked(self):
        """Test that _force_unlock returns False for already unlocked achievements."""
        ach = self.manager.get_achievement("total_kills_100")

        # First unlock
        self.manager._force_unlock(ach)

        # Second attempt should return False
        result = self.manager._force_unlock(ach)
        self.assertFalse(result)

    def test_force_unlock_respects_prerequisites(self):
        """Test that _force_unlock checks prerequisites."""
        # true_ending requires all_side_quests
        ach = self.manager.get_achievement("true_ending")

        # Should fail because prerequisite not met
        result = self.manager._force_unlock(ach)
        self.assertFalse(result)
        self.assertFalse(ach.unlocked)


class TestAchievementDataIntegrity(unittest.TestCase):
    """Tests to verify achievement data configuration is correct."""

    def setUp(self):
        """Set up a fresh achievement manager for each test."""
        self.manager = load_achievement_manager()


class TestTriggerFiltering(unittest.TestCase):
    """Tests for generic trigger filtering edge cases."""

    def setUp(self) -> None:
        self.manager = load_achievement_manager()

    def test_targeted_trigger_requires_event_target(self) -> None:
        """Targeted achievements should not unlock when events omit target."""
        targeted = self.manager.get_achievement("cave_explorer_quest")
        self.assertIsNotNone(targeted)

        unlocked = self.manager._check_trigger("quest")
        self.assertNotIn("cave_explorer_quest", unlocked)
        self.assertFalse(targeted.unlocked)


class TestEventBusIntegration(unittest.TestCase):
    """Tests for EventBus integration with AchievementManager."""

    def setUp(self) -> None:
        self.event_bus = EventBus()
        # Wire manager to the bus so subscriptions are active
        self.manager = load_achievement_manager(event_bus=self.event_bus)

    def test_enemy_killed_event_unlocks_kill_achievements(self) -> None:
        """Publishing enemy_killed should delegate to on_enemy_killed via _check_trigger."""
        # Ensure there is at least one kill-type achievement defined
        kill_achievements = [
            a for a in self.manager.achievements.values() if a.trigger_type == "kill"
        ]
        if not kill_achievements:
            self.skipTest("No kill achievements defined in data")

        # Use as many kills as the first achievement requires so we deterministically unlock it.
        target_achievement = kill_achievements[0]
        target_enemy_type = target_achievement.trigger_target or "test_enemy"

        # Publish kill events equal to the target_count to guarantee unlock.
        for _ in range(max(1, target_achievement.target_count)):
            self.event_bus.publish(
                "enemy_killed",
                enemy_type=target_enemy_type,
                enemy_id="enemy_001",
            )

        unlocked_ids = {a.id for a in self.manager.get_unlocked_achievements()}
        self.assertTrue(
            any(a.id in unlocked_ids for a in kill_achievements),
            "At least one kill achievement should unlock from enemy_killed event",
        )

    def test_map_entered_event_unlocks_exploration_achievements(self) -> None:
        """Publishing map_entered should delegate to on_map_entered."""
        explore_achievements = [
            a for a in self.manager.achievements.values()
            if a.trigger_type == "explore"
        ]
        if not explore_achievements:
            self.skipTest("No explore achievements defined in data")

        target_map = explore_achievements[0].trigger_target or "forest_path"
        self.event_bus.publish("map_entered", map_id=target_map)

        unlocked_ids = {a.id for a in self.manager.get_unlocked_achievements()}
        self.assertTrue(
            any(a.id in unlocked_ids for a in explore_achievements),
            "At least one exploration achievement should unlock from map_entered event",
        )

    def test_battle_won_event_unlocks_battle_achievements(self) -> None:
        """Publishing battle_won should unlock at least one battle achievement."""
        battle_achievements = [
            a for a in self.manager.achievements.values()
            if a.trigger_type == "battle_win"
        ]
        if not battle_achievements:
            self.skipTest("No battle achievements defined in data")

        target = battle_achievements[0]
        for _ in range(max(1, target.target_count)):
            self.event_bus.publish("battle_won")

        unlocked_ids = {a.id for a in self.manager.get_unlocked_achievements()}
        self.assertTrue(
            any(a.id in unlocked_ids for a in battle_achievements),
            "At least one battle_win achievement should unlock from battle_won event",
        )

    def test_all_side_quests_target_count_is_17(self):
        """Verify all_side_quests has correct target count matching quest data."""
        ach = self.manager.get_achievement("all_side_quests")
        self.assertIsNotNone(ach)
        self.assertEqual(ach.target_count, 17,
            "all_side_quests target_count should be 17 to match actual side quest count")

    def test_stat_achievements_have_stat_trigger_type(self):
        """Verify stat-based achievements have correct trigger type."""
        stat_achievement_ids = [
            "total_kills_100", "total_kills_500",
            "gold_earned_5000", "gold_earned_10000",
            "side_quest_master", "all_side_quests",
            "quests_completed_20", "quests_completed_30",
            "all_endings"
        ]

        for ach_id in stat_achievement_ids:
            ach = self.manager.get_achievement(ach_id)
            self.assertIsNotNone(ach, f"Achievement {ach_id} not found")
            self.assertEqual(ach.trigger_type, "stat",
                f"Achievement {ach_id} should have trigger_type 'stat'")

    def test_ending_achievements_have_ending_trigger_type(self):
        """Verify ending achievements have correct trigger type."""
        ending_achievement_ids = [
            "good_ending", "bad_ending", "neutral_ending", "true_ending"
        ]

        for ach_id in ending_achievement_ids:
            ach = self.manager.get_achievement(ach_id)
            self.assertIsNotNone(ach, f"Achievement {ach_id} not found")
            self.assertEqual(ach.trigger_type, "ending",
                f"Achievement {ach_id} should have trigger_type 'ending'")

    def test_ng_plus_achievements_have_flag_trigger_type(self):
        """Verify NG+ achievements have correct trigger type."""
        ng_achievement_ids = ["ng_plus_1", "ng_plus_2", "ng_plus_3"]

        for ach_id in ng_achievement_ids:
            ach = self.manager.get_achievement(ach_id)
            self.assertIsNotNone(ach, f"Achievement {ach_id} not found")
            self.assertEqual(ach.trigger_type, "flag",
                f"Achievement {ach_id} should have trigger_type 'flag'")


if __name__ == "__main__":
    unittest.main()
