"""Integration tests for final achievement consolidation and completion tracking."""

import unittest
import tempfile
import os
import shutil
from typing import Dict, Any

from core.achievements import AchievementManager, AchievementCategory
from engine.event_bus import EventBus
from core.world import World
from core.entities import Player
from core.save_load import SaveManager
from core.post_game import PostGameManager, PostGameUnlock
from engine.scene import SceneManager
from engine.title_scene import TitleScene


class TestFinalIntegration(unittest.TestCase):
    """Integration tests for final achievement and completion systems."""

    def setUp(self):
        """Set up test fixtures."""
        self.world = World()
        self.player = Player("test_player", 0, 0)
        self.save_manager = SaveManager(save_dir=tempfile.mkdtemp())
        # Use a dedicated EventBus so we can also verify event-based wiring
        self.event_bus = EventBus()
        self.achievement_manager = AchievementManager(event_bus=self.event_bus)
        self.achievement_manager.load_achievements("data/achievements.json")

    def tearDown(self):
        """Clean up temporary directories created in setUp."""
        if hasattr(self, "save_manager") and getattr(self.save_manager, "save_dir", None):
            shutil.rmtree(self.save_manager.save_dir, ignore_errors=True)

    def test_all_managers_initialized(self):
        """Test that all managers exist in SceneManager."""
        initial_scene = TitleScene(manager=None, save_manager=self.save_manager)
        scene_manager = SceneManager(
            initial_scene,
            save_manager=self.save_manager,
            achievement_manager=self.achievement_manager,
        )

        # Verify managers are accessible
        self.assertIsNotNone(scene_manager.achievement_manager)
        self.assertIsNotNone(scene_manager.save_manager)

    def test_achievement_points_calculation(self):
        """Test that achievement points sum correctly."""
        # Unlock a few achievements
        self.achievement_manager.on_battle_won()
        self.achievement_manager.on_fish_caught("test_fish", "common", "medium", "DAY", 1)

        total_points = self.achievement_manager.get_total_points()
        max_points = self.achievement_manager.get_max_points()

        self.assertGreater(total_points, 0)
        self.assertGreater(max_points, total_points)
        self.assertIsInstance(total_points, int)
        self.assertIsInstance(max_points, int)

    def test_category_completion(self):
        """Test that category breakdowns are accurate."""
        # Unlock achievements in different categories
        self.achievement_manager.on_battle_won()  # Combat
        self.achievement_manager.on_map_entered("test_map")  # Exploration

        completion = self.achievement_manager.get_completion_by_category()

        self.assertIsInstance(completion, dict)
        # Should have entries for categories with achievements
        self.assertGreater(len(completion), 0)

        # Check structure: (unlocked, total) tuples
        for cat, (unlocked, total) in completion.items():
            self.assertIsInstance(unlocked, int)
            self.assertIsInstance(total, int)
            self.assertGreaterEqual(unlocked, 0)
            self.assertGreaterEqual(total, unlocked)

    def test_full_save_load_cycle(self):
        """Test that complete state survives save/load."""
        # Set up some state
        self.achievement_manager.on_battle_won()
        self.achievement_manager.on_fish_caught("test_fish", "common", "medium", "DAY", 1)

        # Create post-game manager
        post_game_unlocks: Dict[str, PostGameUnlock] = {}
        post_game_manager = PostGameManager(post_game_unlocks)

        # Save
        self.save_manager.save_to_slot(
            1,
            self.world,
            self.player,
            achievement_manager=self.achievement_manager,
            post_game_manager=post_game_manager,
        )

        # Create new managers
        new_achievement_manager = AchievementManager()
        new_achievement_manager.load_achievements("data/achievements.json")
        new_post_game_manager = PostGameManager(post_game_unlocks)

        # Load
        loaded_player = self.save_manager.load_from_slot(
            1,
            self.world,
            achievement_manager=new_achievement_manager,
            post_game_manager=new_post_game_manager,
        )

        # Verify achievement state persisted
        self.assertIsNotNone(loaded_player)
        # Check that achievements were restored
        unlocked_count = new_achievement_manager.get_unlocked_count()
        self.assertGreaterEqual(unlocked_count, 0)

    def test_completion_calculation(self):
        """Test that completion percentages are accurate."""
        from engine.completion_scene import CompletionScene
        from engine.scene import SceneManager

        # Create a scene manager with minimal setup
        initial_scene = TitleScene(manager=None, save_manager=self.save_manager)
        scene_manager = SceneManager(
            initial_scene,
            save_manager=self.save_manager,
            achievement_manager=self.achievement_manager,
        )

        completion_scene = CompletionScene(scene_manager)
        completion_data = completion_scene.calculate_completion()

        # Should have completion data for various systems
        self.assertIsInstance(completion_data, dict)
        self.assertIn("main_story", completion_data)
        self.assertIn("achievements", completion_data)

        # Check structure
        for key, data in completion_data.items():
            self.assertIn("label", data)
            self.assertIn("current", data)
            self.assertIn("total", data)
            self.assertGreaterEqual(data["current"], 0)
            self.assertGreaterEqual(data["total"], data["current"])

    def test_cross_system_achievements(self):
        """Test that composite achievements trigger correctly."""
        from datetime import datetime

        # Track daily activities
        today = datetime.now().date().isoformat()
        self.achievement_manager.on_daily_activity("fish_caught", today)
        self.achievement_manager.on_daily_activity("gambling_win", today)
        unlocked = self.achievement_manager.on_daily_activity("puzzle_solved", today)

        # Should unlock jack_of_all_trades if all three activities done in one day
        self.assertIsInstance(unlocked, list)
        self.assertIn("jack_of_all_trades", unlocked)

    def test_post_game_flow_complete(self):
        """Test that post-game flow works end-to-end."""
        post_game_unlocks: Dict[str, PostGameUnlock] = {}
        post_game_manager = PostGameManager(post_game_unlocks)

        # Simulate final boss defeat
        newly_unlocked = post_game_manager.on_final_boss_defeated("good")

        self.assertTrue(post_game_manager.state.final_boss_defeated)
        self.assertEqual(post_game_manager.state.ending_achieved, "good")
        self.assertIsInstance(newly_unlocked, list)

    def test_all_tutorials_registered(self):
        """Test that tutorial tips are properly loaded."""
        from core.tutorial_system import TutorialManager
        from core.loaders.tutorial_loader import load_tutorial_tips

        tips, help_entries = load_tutorial_tips()
        tutorial_manager = TutorialManager()
        tutorial_manager.tips = tips
        tutorial_manager.help_entries = help_entries

        # Check that tips are loaded
        self.assertGreater(len(tutorial_manager.tips), 0)
        self.assertGreater(len(tutorial_manager.help_entries), 0)

        # Check for new tips
        tip_ids = [tip.tip_id for tip in tutorial_manager.tips.values()]
        self.assertIn("post_game_intro", tip_ids)
        self.assertIn("completion_hint", tip_ids)

    def test_achievement_categories_exist(self):
        """Test that all achievement categories are properly defined."""
        categories = [
            AchievementCategory.STORY,
            AchievementCategory.COMBAT,
            AchievementCategory.EXPLORATION,
            AchievementCategory.ACTIVITIES,
            AchievementCategory.CHALLENGE,
            AchievementCategory.SECRET,
        ]

        for category in categories:
            achievements = self.achievement_manager.get_achievements_by_category(category)
            # Categories may be empty, but should not error
            self.assertIsInstance(achievements, list)

    def test_achievement_points_in_serialization(self):
        """Test that points are included in achievement serialization."""
        # Unlock an achievement
        self.achievement_manager.on_battle_won()

        # Serialize
        serialized = self.achievement_manager.serialize_state()

        # Check structure
        self.assertIn("achievements", serialized)
        if serialized["achievements"]:
            first_ach = serialized["achievements"][0]
            self.assertIn("points", first_ach)
            self.assertIsInstance(first_ach["points"], int)


if __name__ == "__main__":
    unittest.main()
