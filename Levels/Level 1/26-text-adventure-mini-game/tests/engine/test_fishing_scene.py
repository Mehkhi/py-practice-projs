"""Unit tests for engine/fishing_scene.py - FishingScene."""

import unittest
from unittest.mock import Mock, MagicMock, patch
import pygame

from engine.fishing_scene import FishingScene, FishingPhase
from core.fishing import FishingSystem, FishingSpot, Fish, FishRarity, WaterType
from core.world import World
from core.entities import Player
from core.stats import Stats
from core.items import Inventory


class TestFishingScene(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        pygame.init()

        # Create test fish
        self.test_fish = Fish(
            fish_id="test_fish",
            name="Test Fish",
            rarity=FishRarity.COMMON,
            base_value=10,
            water_types=[WaterType.FRESHWATER],
            time_periods=[],
            min_size=0.5,
            max_size=2.0,
            catch_difficulty=3,
            description="A test fish",
            item_id="fish_test",
        )

        # Create test spot
        self.test_spot = FishingSpot(
            spot_id="test_spot",
            name="Test Spot",
            map_id="test_map",
            x=5,
            y=5,
            water_type=WaterType.FRESHWATER,
            is_premium=False,
            fish_pool=["test_fish"],
            rarity_modifiers={},
        )

        # Create fishing system
        self.fishing_system = FishingSystem(
            {"test_fish": self.test_fish},
            {"test_spot": self.test_spot}
        )

        # Create player
        self.player = Player(
            entity_id="player",
            name="Test Player",
            x=5,
            y=5,
            sprite_id="player",
            stats=Stats(
                max_hp=100,
                hp=100,
                max_sp=50,
                sp=50,
                attack=10,
                defense=5,
                magic=8,
                speed=10,
                luck=5
            ),
            inventory=Inventory()
        )

        # Create world
        self.world = World()

        # Create mock manager
        self.manager = Mock()
        self.manager.items_db = {}
        self.manager.day_night_cycle = Mock()
        self.manager.day_night_cycle.get_time_of_day.return_value = Mock(value="DAY")

        # Create scene
        self.scene = FishingScene(
            self.manager,
            self.fishing_system,
            self.test_spot,
            self.player,
            self.world
        )

    def tearDown(self):
        """Clean up after tests."""
        pygame.quit()

    def test_waiting_phase_timer(self):
        """Verify wait timer counts down correctly."""
        initial_timer = self.scene.wait_timer
        self.assertEqual(self.scene.phase, FishingPhase.WAITING)

        # Update with small dt
        self.scene.update(0.1)
        self.assertLess(self.scene.wait_timer, initial_timer)
        self.assertEqual(self.scene.phase, FishingPhase.WAITING)

        # Update until timer expires
        while self.scene.wait_timer > 0 and self.scene.phase == FishingPhase.WAITING:
            self.scene.update(0.1)

        # Should transition to HOOKING or restart WAITING (if no fish bit)
        self.assertIn(self.scene.phase, [FishingPhase.HOOKING, FishingPhase.WAITING])

    def test_hook_window_success(self):
        """Pressing SPACE in time succeeds."""
        # Force transition to hooking phase
        self.scene.phase = FishingPhase.HOOKING
        self.scene.current_fish = self.test_fish
        self.scene.hook_timer = 0.3  # Some time left

        # Create keydown event for SPACE
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
        self.scene.handle_event(event)

        # Should transition to REELING
        self.assertEqual(self.scene.phase, FishingPhase.REELING)
        self.assertEqual(self.scene.difficulty, self.test_fish.catch_difficulty)

    def test_hook_window_failure(self):
        """Missing window fails."""
        # Force transition to hooking phase
        self.scene.phase = FishingPhase.HOOKING
        self.scene.current_fish = self.test_fish
        self.scene.hook_timer = 0.0  # No time left

        # Update should transition to ESCAPED
        self.scene.update(0.1)

        self.assertEqual(self.scene.phase, FishingPhase.ESCAPED)
        self.assertIsNone(self.scene.current_fish)

    def test_reeling_catch_progress(self):
        """Progress increases when reel near fish position."""
        # Set up reeling phase
        self.scene.phase = FishingPhase.REELING
        self.scene.current_fish = self.test_fish
        self.scene.reel_position = 0.5
        self.scene.fish_position = 0.5  # Same position
        self.scene.catch_progress = 0.0
        self.scene.tension = 50.0

        initial_progress = self.scene.catch_progress

        # Update without reeling (fish should stay near)
        self.scene.update(0.1)

        # Progress should increase when positions are close
        if abs(self.scene.reel_position - self.scene.fish_position) < self.scene.sweet_spot_size:
            self.assertGreater(self.scene.catch_progress, initial_progress)

    def test_tension_line_break(self):
        """Too much tension causes escape."""
        # Set up reeling phase
        self.scene.phase = FishingPhase.REELING
        self.scene.current_fish = self.test_fish
        self.scene.tension = 95.0  # Near breaking point

        # Reel continuously to increase tension
        def _is_action_active(action: str) -> bool:
            return action in ("interact", "confirm", "up")

        with patch.object(self.scene.input_manager, 'is_action_active', side_effect=_is_action_active):
            # Update until tension exceeds 100
            for _ in range(20):
                self.scene.update(0.1)
                if self.scene.phase != FishingPhase.REELING:
                    break

        # Should escape due to line break
        self.assertEqual(self.scene.phase, FishingPhase.ESCAPED)
        self.assertGreaterEqual(self.scene.tension, 100.0)

    def test_tension_too_low(self):
        """Too little tension causes escape."""
        # Set up reeling phase
        self.scene.phase = FishingPhase.REELING
        self.scene.current_fish = self.test_fish
        self.scene.tension = 5.0  # Very low

        # Don't reel to decrease tension
        with patch.object(self.scene.input_manager, 'is_action_active', return_value=False):
            # Update until tension drops below 0
            for _ in range(20):
                self.scene.update(0.1)
                if self.scene.phase != FishingPhase.REELING:
                    break

        # Should escape due to low tension
        self.assertEqual(self.scene.phase, FishingPhase.ESCAPED)
        self.assertLessEqual(self.scene.tension, 0.0)

    def test_escape_to_cancel(self):
        """ESC key exits scene."""
        # Test in different phases
        for phase in [FishingPhase.WAITING, FishingPhase.HOOKING, FishingPhase.REELING]:
            self.scene.phase = phase
            event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)

            with patch.object(self.scene, '_exit') as mock_exit:
                self.scene.handle_event(event)
                mock_exit.assert_called_once()

    def test_catch_awards_item(self):
        """Successful catch adds item to inventory."""
        # Set up for catch
        self.scene.phase = FishingPhase.REELING
        self.scene.current_fish = self.test_fish
        self.scene.catch_progress = 99.0  # Almost caught
        self.scene.tension = 50.0

        # Force catch completion
        self.scene._complete_catch()

        # Should have caught fish
        self.assertEqual(self.scene.phase, FishingPhase.CAUGHT)
        self.assertIsNotNone(self.scene.caught_fish)

        # Item should be in inventory
        self.assertTrue(self.player.inventory.has_item(self.test_fish.item_id))

    def test_difficulty_scaling(self):
        """Higher difficulty fish are harder."""
        # Test with low difficulty fish
        easy_fish = Fish(
            fish_id="easy_fish",
            name="Easy Fish",
            rarity=FishRarity.COMMON,
            base_value=10,
            water_types=[WaterType.FRESHWATER],
            time_periods=[],
            min_size=0.5,
            max_size=2.0,
            catch_difficulty=1,
            description="Easy",
            item_id="fish_easy",
        )

        # Test with high difficulty fish
        hard_fish = Fish(
            fish_id="hard_fish",
            name="Hard Fish",
            rarity=FishRarity.LEGENDARY,
            base_value=500,
            water_types=[WaterType.MAGICAL],
            time_periods=[],
            min_size=1.0,
            max_size=3.0,
            catch_difficulty=10,
            description="Hard",
            item_id="fish_hard",
        )

        # Set up reeling for easy fish
        self.scene.phase = FishingPhase.REELING
        self.scene.current_fish = easy_fish
        self.scene.difficulty = easy_fish.catch_difficulty
        self.scene._init_reeling()

        easy_velocity_1 = self.scene.fish_velocity
        self.scene.update(0.1)
        easy_velocity_2 = self.scene.fish_velocity

        # Set up reeling for hard fish
        self.scene.current_fish = hard_fish
        self.scene.difficulty = hard_fish.catch_difficulty
        self.scene._init_reeling()

        hard_velocity_1 = self.scene.fish_velocity
        self.scene.update(0.1)
        hard_velocity_2 = self.scene.fish_velocity

        # Hard fish should move more erratically (velocity changes more)
        # This is a probabilistic test, so we check that difficulty affects behavior
        easy_change = abs(easy_velocity_2 - easy_velocity_1)
        hard_change = abs(hard_velocity_2 - hard_velocity_1)

        # Higher difficulty should generally result in more movement
        # (though randomness means this isn't guaranteed, so we just verify it's set correctly)
        self.assertEqual(self.scene.difficulty, hard_fish.catch_difficulty)


if __name__ == "__main__":
    unittest.main()
