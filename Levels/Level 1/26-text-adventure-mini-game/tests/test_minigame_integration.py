"""Integration tests for mini-game systems and cross-system features."""

import json
import os
import tempfile
import unittest
from unittest.mock import Mock

from core.world import World, Map, Tile
from core.entities import Player
from core.items import Inventory
from core.stats import Stats
from core.save_load import SaveManager
from core.tutorial_system import TipTrigger, TutorialManager, TutorialTip, HelpEntry
from engine.scene import SceneManager
from engine.statistics_scene import StatisticsScene
from core.fishing import FishingSystem, Fish, FishingSpot, FishRarity, WaterType, CaughtFish
from core.gambling import GamblingManager
from core.arena import ArenaManager, ArenaFighter
from core.puzzles import PuzzleManager, DungeonPuzzle
from core.brain_teasers import BrainTeaserManager, BrainTeaser, BrainTeaserType


class TestMiniGameIntegration(unittest.TestCase):
    """Integration tests for mini-game systems."""

    def setUp(self):
        """Set up test fixtures."""
        self.world = World()
        tiles = [[Tile("grass", True, "grass") for _ in range(5)] for _ in range(5)]
        self.world.add_map(Map(map_id="test_map", width=5, height=5, tiles=tiles))

        self.stats = Stats(100, 100, 50, 50, 10, 5, 8, 7, 5)
        self.inventory = Inventory()
        self.player = Player(
            entity_id="player_1",
            name="TestHero",
            x=2, y=2,
            sprite_id="hero",
            stats=self.stats,
            inventory=self.inventory,
        )

        # Create mini-game managers
        self.fish_db = {
            "test_fish": Fish(
                fish_id="test_fish",
                name="Test Fish",
                rarity=FishRarity.COMMON,
                base_value=10,
                water_types=[WaterType.FRESHWATER],
                time_periods=[],
                min_size=1.0,
                max_size=5.0,
                catch_difficulty=1,
                description="A test fish",
                item_id="test_fish_item"
            )
        }
        self.spots = {
            "test_spot": FishingSpot(
                spot_id="test_spot",
                name="Test Spot",
                map_id="test_map",
                x=2, y=2,
                water_type=WaterType.FRESHWATER,
                fish_pool=["test_fish"]
            )
        }
        self.fishing_system = FishingSystem(self.fish_db, self.spots)

        self.gambling_manager = GamblingManager()

        self.fighters = {
            "fighter1": ArenaFighter(
                fighter_id="fighter1",
                name="Test Fighter",
                sprite_id="fighter",
                stats={"hp": 100, "attack": 10, "defense": 5, "speed": 8},
                skills=[],
                odds=2.0
            )
        }
        self.arena_manager = ArenaManager(self.fighters)

        self.puzzle_definitions = {}
        self.puzzle_manager = PuzzleManager(self.puzzle_definitions)

        self.brain_teaser_definitions = {}
        self.brain_teaser_manager = BrainTeaserManager(self.brain_teaser_definitions)

        self.save_manager = SaveManager(save_dir=tempfile.mkdtemp())

    def test_all_managers_in_scene_manager(self):
        """Test that all mini-game managers are accessible from scene manager."""
        from engine.title_scene import TitleScene

        initial_scene = TitleScene(manager=None, save_manager=self.save_manager)
        scene_manager = SceneManager(
            initial_scene,
            fishing_system=self.fishing_system,
            gambling_manager=self.gambling_manager,
            arena_manager=self.arena_manager,
            brain_teaser_manager=self.brain_teaser_manager,
        )

        # Verify all managers are accessible
        self.assertIsNotNone(scene_manager.fishing_system)
        self.assertIsNotNone(scene_manager.gambling_manager)
        self.assertIsNotNone(scene_manager.arena_manager)
        self.assertIsNotNone(scene_manager.brain_teaser_manager)

        self.assertEqual(scene_manager.fishing_system, self.fishing_system)
        self.assertEqual(scene_manager.gambling_manager, self.gambling_manager)
        self.assertEqual(scene_manager.arena_manager, self.arena_manager)

    def test_fishing_save_load(self):
        """Test that fishing state persists through save/load."""
        # Record a catch
        fish = self.fish_db["test_fish"]
        caught = CaughtFish(fish=fish, size=3.5)
        self.fishing_system.record_catch(caught)

        # Save
        save_data = self.save_manager.serialize_state(
            self.world,
            self.player,
            fishing_system=self.fishing_system
        )

        # Create new fishing system and load
        new_fishing_system = FishingSystem(self.fish_db, self.spots)
        self.save_manager.deserialize_state(
            save_data,
            self.world,
            fishing_system=new_fishing_system
        )

        # Verify catch was restored
        self.assertEqual(len(new_fishing_system.player_records), 1)
        self.assertIn("test_fish", new_fishing_system.player_records)
        self.assertEqual(new_fishing_system.player_records["test_fish"].size, 3.5)

    def test_gambling_save_load(self):
        """Test that gambling stats persist through save/load."""
        # Set some stats
        self.gambling_manager.stats.total_wagered = 100
        self.gambling_manager.stats.total_won = 150
        self.gambling_manager.stats.games_played = 5

        # Save
        save_data = self.save_manager.serialize_state(
            self.world,
            self.player,
            gambling_manager=self.gambling_manager
        )

        # Create new gambling manager and load
        new_gambling_manager = GamblingManager()
        self.save_manager.deserialize_state(
            save_data,
            self.world,
            gambling_manager=new_gambling_manager
        )

        # Verify stats were restored
        self.assertEqual(new_gambling_manager.stats.total_wagered, 100)
        self.assertEqual(new_gambling_manager.stats.total_won, 150)
        self.assertEqual(new_gambling_manager.stats.games_played, 5)

    def test_arena_save_load(self):
        """Test that arena state persists through save/load."""
        # Set some state
        self.arena_manager.fighters["fighter1"].wins = 5
        self.arena_manager.fighters["fighter1"].losses = 2

        # Save
        save_data = self.save_manager.serialize_state(
            self.world,
            self.player,
            arena_manager=self.arena_manager
        )

        # Create new arena manager and load
        new_arena_manager = ArenaManager(self.fighters)
        self.save_manager.deserialize_state(
            save_data,
            self.world,
            arena_manager=new_arena_manager
        )

        # Verify state was restored
        self.assertEqual(new_arena_manager.fighters["fighter1"].wins, 5)
        self.assertEqual(new_arena_manager.fighters["fighter1"].losses, 2)

    def test_puzzle_save_load(self):
        """Test that puzzle progress persists through save/load."""
        # Create a simple puzzle
        puzzle = DungeonPuzzle(
            puzzle_id="test_puzzle",
            map_id="test_map",
            elements={},
            solved=False
        )
        self.puzzle_manager.puzzles["test_puzzle"] = puzzle
        puzzle.solved = True

        # Save
        save_data = self.save_manager.serialize_state(
            self.world,
            self.player,
            puzzle_manager=self.puzzle_manager
        )

        # Create new puzzle manager and load
        new_puzzle_manager = PuzzleManager(self.puzzle_definitions)
        new_puzzle_manager.puzzles["test_puzzle"] = DungeonPuzzle(
            puzzle_id="test_puzzle",
            map_id="test_map",
            elements={},
            solved=False
        )
        self.save_manager.deserialize_state(
            save_data,
            self.world,
            puzzle_manager=new_puzzle_manager
        )

        # Verify puzzle state was restored
        self.assertTrue(new_puzzle_manager.puzzles["test_puzzle"].solved)

    def test_cross_system_achievement(self):
        """Test that multi-activity achievements can be tracked."""
        # This test verifies the achievement system can handle cross-system flags
        # The actual triggering would be done by the achievement system
        # when flags like "jack_of_all_trades" are set

        # Set flags that would trigger the achievement
        self.world.set_flag("fish_caught_today", True)
        self.world.set_flag("gamble_won_today", True)
        self.world.set_flag("puzzle_solved_today", True)

        # Check that flags are set (achievement system would check these)
        self.assertTrue(self.world.get_flag("fish_caught_today"))
        self.assertTrue(self.world.get_flag("gamble_won_today"))
        self.assertTrue(self.world.get_flag("puzzle_solved_today"))

    def test_statistics_scene_data(self):
        """Test that statistics scene displays all data correctly."""
        # Create scene with all managers
        scene = StatisticsScene(
            manager=None,
            fishing_system=self.fishing_system,
            gambling_manager=self.gambling_manager,
            arena_manager=self.arena_manager,
            puzzle_manager=self.puzzle_manager,
            brain_teaser_manager=self.brain_teaser_manager,
        )

        # Build statistics
        stats = scene._build_statistics()

        # Verify all categories are present
        self.assertIn("FISHING", stats)
        self.assertIn("GAMBLING", stats)
        self.assertIn("ARENA", stats)
        self.assertIn("PUZZLES", stats)
        self.assertIn("BRAIN TEASERS", stats)

        # Verify fishing stats have data
        fishing_stats = stats["FISHING"]
        self.assertGreater(len(fishing_stats), 0)

        # Verify gambling stats have data
        gambling_stats = stats["GAMBLING"]
        self.assertGreater(len(gambling_stats), 0)
        # Check for key stats
        stat_labels = [label for label, _ in gambling_stats]
        self.assertIn("Total Wagered", stat_labels)
        self.assertIn("Games Played", stat_labels)

    def test_tutorial_triggers(self):
        """Test that all mini-game tutorial triggers are defined."""
        # Create tutorial manager
        tutorial_manager = TutorialManager()

        # Verify all new triggers exist in TipTrigger enum
        self.assertIn(TipTrigger.FIRST_FISH_CAUGHT, TipTrigger)
        self.assertIn(TipTrigger.FIRST_LEGENDARY_FISH, TipTrigger)
        self.assertIn(TipTrigger.FIRST_GAMBLING, TipTrigger)
        self.assertIn(TipTrigger.FIRST_GAMBLING_WIN, TipTrigger)
        self.assertIn(TipTrigger.FIRST_GAMBLING_LOSS, TipTrigger)
        self.assertIn(TipTrigger.FIRST_ARENA_VISIT, TipTrigger)
        self.assertIn(TipTrigger.FIRST_ARENA_BET, TipTrigger)
        self.assertIn(TipTrigger.FIRST_DUNGEON_PUZZLE, TipTrigger)
        self.assertIn(TipTrigger.FIRST_PUZZLE_SOLVED, TipTrigger)
        self.assertIn(TipTrigger.FIRST_BRAIN_TEASER, TipTrigger)

        # Test that triggers can be used
        tip = TutorialTip(
            tip_id="test_tip",
            trigger=TipTrigger.FIRST_GAMBLING,
            title="Test",
            content="Test content"
        )
        tutorial_manager.register_tip(tip)

        # Trigger the tip
        result = tutorial_manager.trigger_tip(TipTrigger.FIRST_GAMBLING)
        self.assertIsNotNone(result)
        self.assertEqual(result.tip_id, "test_tip")

    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up temp directory
        if hasattr(self, 'save_manager') and hasattr(self.save_manager, 'save_dir'):
            import shutil
            if os.path.exists(self.save_manager.save_dir):
                shutil.rmtree(self.save_manager.save_dir)


if __name__ == "__main__":
    unittest.main()
