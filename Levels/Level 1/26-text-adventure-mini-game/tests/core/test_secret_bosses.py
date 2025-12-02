"""Tests for secret boss system."""

import unittest
from unittest.mock import Mock, MagicMock

from core.secret_bosses import (
    SecretBossManager,
    SecretBoss,
    UnlockCondition,
    UnlockConditionType,
)
from core.time_system import TimeOfDay, DayNightCycle


class TestSecretBosses(unittest.TestCase):
    """Test suite for secret boss system."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a simple test boss
        self.test_boss = SecretBoss(
            boss_id="test_boss",
            name="Test Boss",
            title="The Test",
            description="A test boss",
            encounter_id="test_encounter",
            location_map_id="test_map",
            location_x=5,
            location_y=5,
            unlock_conditions=[
                UnlockCondition(
                    condition_type=UnlockConditionType.FLAG_SET,
                    data={"flag": "test_flag"},
                    description="Set test flag",
                    hidden=False,
                )
            ],
            spawn_trigger_type="interact",
            lore_entries=[],
            rewards={"gold": 100, "exp": 50},
            unique_drops=["test_item"],
            achievement_id="test_achievement",
            rematch_available=True,
            post_game_only=False,
        )

        self.manager = SecretBossManager({"test_boss": self.test_boss})

        # Create mock objects
        self.world = Mock()
        self.world.get_flag = Mock(return_value=False)

        self.player = Mock()
        self.player.stats = Mock()
        self.player.stats.level = 1
        self.player.inventory = Mock()
        self.player.inventory.has = Mock(return_value=False)

        self.achievement_manager = Mock()
        self.achievement_manager.get_achievement = Mock(return_value=None)

    def test_flag_condition_check(self):
        """Test flag condition checking."""
        # Test FLAG_SET
        condition = UnlockCondition(
            condition_type=UnlockConditionType.FLAG_SET,
            data={"flag": "test_flag"},
            description="Test",
        )
        self.world.get_flag.return_value = False
        result = self.manager.check_unlock_condition(
            condition, self.world, self.player, self.achievement_manager
        )
        self.assertFalse(result)

        self.world.get_flag.return_value = True
        result = self.manager.check_unlock_condition(
            condition, self.world, self.player, self.achievement_manager
        )
        self.assertTrue(result)

        # Test FLAGS_ALL
        condition = UnlockCondition(
            condition_type=UnlockConditionType.FLAGS_ALL,
            data={"flags": ["flag1", "flag2"]},
            description="Test",
        )
        self.world.get_flag.side_effect = lambda f, d: f == "flag1"
        result = self.manager.check_unlock_condition(
            condition, self.world, self.player, self.achievement_manager
        )
        self.assertFalse(result)

        self.world.get_flag.side_effect = lambda f, d: True
        result = self.manager.check_unlock_condition(
            condition, self.world, self.player, self.achievement_manager
        )
        self.assertTrue(result)

        # Test FLAGS_ANY
        condition = UnlockCondition(
            condition_type=UnlockConditionType.FLAGS_ANY,
            data={"flags": ["flag1", "flag2"]},
            description="Test",
        )
        self.world.get_flag.side_effect = lambda f, d: False
        result = self.manager.check_unlock_condition(
            condition, self.world, self.player, self.achievement_manager
        )
        self.assertFalse(result)

        self.world.get_flag.side_effect = lambda f, d: f == "flag1"
        result = self.manager.check_unlock_condition(
            condition, self.world, self.player, self.achievement_manager
        )
        self.assertTrue(result)

    def test_multi_condition_all_required(self):
        """Test that all conditions must pass for unlock."""
        boss = SecretBoss(
            boss_id="multi_boss",
            name="Multi Boss",
            title="The Multi",
            description="Test",
            encounter_id="test",
            location_map_id="test",
            location_x=0,
            location_y=0,
            unlock_conditions=[
                UnlockCondition(
                    condition_type=UnlockConditionType.FLAG_SET,
                    data={"flag": "flag1"},
                    description="Flag 1",
                ),
                UnlockCondition(
                    condition_type=UnlockConditionType.FLAG_SET,
                    data={"flag": "flag2"},
                    description="Flag 2",
                ),
            ],
            spawn_trigger_type="interact",
            lore_entries=[],
            rewards={},
            unique_drops=[],
        )
        manager = SecretBossManager({"multi_boss": boss})

        # Only one flag set
        self.world.get_flag.side_effect = lambda f, d: f == "flag1"
        result = manager.check_boss_available(
            "multi_boss", self.world, self.player, self.achievement_manager, False
        )
        self.assertFalse(result)

        # Both flags set
        self.world.get_flag.side_effect = lambda f, d: True
        result = manager.check_boss_available(
            "multi_boss", self.world, self.player, self.achievement_manager, False
        )
        self.assertTrue(result)

    def test_boss_discovery_tracking(self):
        """Test that discovered bosses are tracked correctly."""
        # First discovery should return True (newly discovered)
        self.assertTrue(self.manager.discover_boss("test_boss"))
        self.assertIn("test_boss", self.manager.discovered)

        # Second discovery should return False (already known)
        result = self.manager.discover_boss("test_boss")
        self.assertFalse(result)

    def test_boss_defeat_tracking(self):
        """Test that defeated bosses are tracked correctly."""
        rewards = self.manager.defeat_boss("test_boss")
        self.assertIn("test_boss", self.manager.defeated)
        self.assertIn("unique_drops", rewards)
        self.assertEqual(rewards["unique_drops"], ["test_item"])

        # Second defeat should not include unique drops
        rewards2 = self.manager.defeat_boss("test_boss")
        self.assertNotIn("unique_drops", rewards2)

    def test_unique_drops_first_only(self):
        """Test that unique drops only appear on first defeat."""
        rewards1 = self.manager.defeat_boss("test_boss")
        self.assertIn("unique_drops", rewards1)

        rewards2 = self.manager.defeat_boss("test_boss")
        self.assertNotIn("unique_drops", rewards2)

    def test_rematch_availability(self):
        """Test rematch availability."""
        # Boss with rematch_available=True should be defeatable multiple times
        self.manager.defeat_boss("test_boss")
        self.assertIn("test_boss", self.manager.defeated)

        # Boss should still be available for rematch
        self.world.get_flag.return_value = True
        result = self.manager.check_boss_available(
            "test_boss", self.world, self.player, self.achievement_manager, False
        )
        self.assertTrue(result)

    def test_post_game_requirement(self):
        """Test that post-game bosses are locked before final boss."""
        boss = SecretBoss(
            boss_id="post_game_boss",
            name="Post Game Boss",
            title="The Post Game",
            description="Test",
            encounter_id="test",
            location_map_id="test",
            location_x=0,
            location_y=0,
            unlock_conditions=[],
            spawn_trigger_type="interact",
            lore_entries=[],
            rewards={},
            unique_drops=[],
            post_game_only=True,
        )
        manager = SecretBossManager({"post_game_boss": boss})

        # Should be locked before final boss
        result = manager.check_boss_available(
            "post_game_boss", self.world, self.player, self.achievement_manager, False
        )
        self.assertFalse(result)

        # Should be available after final boss
        result = manager.check_boss_available(
            "post_game_boss", self.world, self.player, self.achievement_manager, True
        )
        self.assertTrue(result)

    def test_chain_unlock(self):
        """Test that defeating one boss can unlock another."""
        boss1 = SecretBoss(
            boss_id="boss1",
            name="Boss 1",
            title="First",
            description="Test",
            encounter_id="test",
            location_map_id="test",
            location_x=0,
            location_y=0,
            unlock_conditions=[
                UnlockCondition(
                    condition_type=UnlockConditionType.FLAG_SET,
                    data={"flag": "unlock_boss1"},
                    description="Unlock boss 1",
                )
            ],
            spawn_trigger_type="interact",
            lore_entries=[],
            rewards={},
            unique_drops=[],
        )

        boss2 = SecretBoss(
            boss_id="boss2",
            name="Boss 2",
            title="Second",
            description="Test",
            encounter_id="test",
            location_map_id="test",
            location_x=0,
            location_y=0,
            unlock_conditions=[
                UnlockCondition(
                    condition_type=UnlockConditionType.BOSSES_DEFEATED,
                    data={"boss_ids": ["boss1"]},
                    description="Defeat boss 1",
                )
            ],
            spawn_trigger_type="interact",
            lore_entries=[],
            rewards={},
            unique_drops=[],
        )

        manager = SecretBossManager({"boss1": boss1, "boss2": boss2})

        # Boss2 should not be available initially
        self.world.get_flag.return_value = True
        result = manager.check_boss_available(
            "boss2", self.world, self.player, self.achievement_manager, False
        )
        self.assertFalse(result)

        # Defeat boss1
        manager.defeat_boss("boss1")

        # Boss2 should now be available
        result = manager.check_boss_available(
            "boss2", self.world, self.player, self.achievement_manager, False
        )
        self.assertTrue(result)

    def test_hidden_hints(self):
        """Test that hidden conditions are not shown in hints."""
        boss = SecretBoss(
            boss_id="hidden_boss",
            name="Hidden Boss",
            title="The Hidden",
            description="Test",
            encounter_id="test",
            location_map_id="test",
            location_x=0,
            location_y=0,
            unlock_conditions=[
                UnlockCondition(
                    condition_type=UnlockConditionType.FLAG_SET,
                    data={"flag": "visible_flag"},
                    description="Visible condition",
                    hidden=False,
                ),
                UnlockCondition(
                    condition_type=UnlockConditionType.FLAG_SET,
                    data={"flag": "hidden_flag"},
                    description="Hidden condition",
                    hidden=True,
                ),
            ],
            spawn_trigger_type="interact",
            lore_entries=[],
            rewards={},
            unique_drops=[],
        )
        manager = SecretBossManager({"hidden_boss": boss})

        hints = manager.get_unlock_hints("hidden_boss")
        self.assertEqual(len(hints), 1)
        self.assertIn("Visible condition", hints)
        self.assertNotIn("Hidden condition", hints)

    def test_serialize_deserialize(self):
        """Test that state persists through save/load cycle."""
        # Set up some state
        self.manager.discover_boss("test_boss")
        self.manager.defeat_boss("test_boss")

        # Serialize
        data = self.manager.serialize()
        self.assertIn("discovered", data)
        self.assertIn("defeated", data)
        self.assertIn("test_boss", data["discovered"])
        self.assertIn("test_boss", data["defeated"])

        # Deserialize
        new_manager = SecretBossManager.deserialize(data, {"test_boss": self.test_boss})
        self.assertIn("test_boss", new_manager.discovered)
        self.assertIn("test_boss", new_manager.defeated)

    def test_time_of_day_condition(self):
        """Test TIME_OF_DAY condition checks current time period."""
        condition = UnlockCondition(
            condition_type=UnlockConditionType.TIME_OF_DAY,
            data={"time": "MIDNIGHT"},
            description="Must be midnight",
        )

        day_night_cycle = DayNightCycle()
        day_night_cycle.set_time(0, 0)  # Set to midnight

        result = self.manager.check_unlock_condition(
            condition, self.world, self.player, self.achievement_manager, day_night_cycle
        )
        self.assertTrue(result)

        day_night_cycle.set_time(12, 0)  # Set to noon
        result = self.manager.check_unlock_condition(
            condition, self.world, self.player, self.achievement_manager, day_night_cycle
        )
        self.assertFalse(result)

    def test_item_possessed_condition(self):
        """Test ITEM_POSSESSED condition checks inventory correctly."""
        condition = UnlockCondition(
            condition_type=UnlockConditionType.ITEM_POSSESSED,
            data={"item_id": "test_item"},
            description="Must have test item",
        )

        self.player.inventory.has.return_value = False
        result = self.manager.check_unlock_condition(
            condition, self.world, self.player, self.achievement_manager
        )
        self.assertFalse(result)

        self.player.inventory.has.return_value = True
        result = self.manager.check_unlock_condition(
            condition, self.world, self.player, self.achievement_manager
        )
        self.assertTrue(result)

    def test_level_minimum_condition(self):
        """Test LEVEL_MINIMUM condition checks player level."""
        condition = UnlockCondition(
            condition_type=UnlockConditionType.LEVEL_MINIMUM,
            data={"level": 10},
            description="Must be level 10",
        )

        self.player.stats.level = 5
        result = self.manager.check_unlock_condition(
            condition, self.world, self.player, self.achievement_manager
        )
        self.assertFalse(result)

        self.player.stats.level = 10
        result = self.manager.check_unlock_condition(
            condition, self.world, self.player, self.achievement_manager
        )
        self.assertTrue(result)

        self.player.stats.level = 15
        result = self.manager.check_unlock_condition(
            condition, self.world, self.player, self.achievement_manager
        )
        self.assertTrue(result)

    def test_achievement_condition(self):
        """Test ACHIEVEMENT condition checks achievement manager."""
        condition = UnlockCondition(
            condition_type=UnlockConditionType.ACHIEVEMENT,
            data={"achievement_id": "test_achievement"},
            description="Must have achievement",
        )

        # Achievement not unlocked
        achievement = Mock()
        achievement.unlocked = False
        self.achievement_manager.get_achievement.return_value = achievement
        result = self.manager.check_unlock_condition(
            condition, self.world, self.player, self.achievement_manager
        )
        self.assertFalse(result)

        # Achievement unlocked
        achievement.unlocked = True
        result = self.manager.check_unlock_condition(
            condition, self.world, self.player, self.achievement_manager
        )
        self.assertTrue(result)

    def test_special_condition(self):
        """Test SPECIAL condition checks flag pattern."""
        condition = UnlockCondition(
            condition_type=UnlockConditionType.SPECIAL,
            data={"flag": "secret_boss_test_boss_unlocked"},
            description="Special unlock",
        )

        self.world.get_flag.return_value = False
        result = self.manager.check_unlock_condition(
            condition, self.world, self.player, self.achievement_manager
        )
        self.assertFalse(result)

        self.world.get_flag.return_value = True
        result = self.manager.check_unlock_condition(
            condition, self.world, self.player, self.achievement_manager
        )
        self.assertTrue(result)

    def test_update_available_bosses(self):
        """Test that update_available_bosses correctly updates available set."""
        self.world.get_flag.return_value = False
        newly_unlocked = self.manager.update_available_bosses(
            self.world, self.player, self.achievement_manager, False
        )
        self.assertEqual(len(newly_unlocked), 0)
        self.assertNotIn("test_boss", self.manager.available)

        self.world.get_flag.return_value = True
        newly_unlocked = self.manager.update_available_bosses(
            self.world, self.player, self.achievement_manager, False
        )
        self.assertEqual(len(newly_unlocked), 1)
        self.assertIn("test_boss", newly_unlocked)
        self.assertIn("test_boss", self.manager.available)


if __name__ == "__main__":
    unittest.main()
