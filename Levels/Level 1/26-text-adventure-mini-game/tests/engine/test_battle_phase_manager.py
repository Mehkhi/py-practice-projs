"""Unit tests for BattlePhaseManager."""

import unittest
from unittest.mock import Mock

from core.combat import BattleState
from engine.battle.phases import BattlePhaseManager


class TestBattlePhaseManager(unittest.TestCase):
    """Test cases for BattlePhaseManager."""

    def test_update_raises_error_for_missing_phase(self) -> None:
        """Test that update() raises ValueError when BattleState has no registered phase."""
        # Create a minimal mock scene with battle_system
        mock_scene = Mock()
        mock_battle_system = Mock()
        mock_battle_system.state = BattleState.PLAYER_CHOOSE
        mock_scene.battle_system = mock_battle_system

        # Create phase manager
        phase_manager = BattlePhaseManager(scene=mock_scene)

        # Remove a phase to simulate missing handler scenario
        del phase_manager._phases[BattleState.PLAYER_CHOOSE]

        # Set state to the unmapped state
        mock_battle_system.state = BattleState.PLAYER_CHOOSE

        # Verify ValueError is raised with appropriate message
        with self.assertRaises(ValueError) as context:
            phase_manager.update(dt=0.016)

        error_message = str(context.exception)
        self.assertIn("BattlePhaseManager", error_message)
        self.assertIn("No phase handler registered", error_message)
        self.assertIn("PLAYER_CHOOSE", error_message)

    def test_update_raises_error_on_state_transition_with_missing_phase(self) -> None:
        """Test that update() raises ValueError when transitioning to unmapped state."""
        # Create a minimal mock scene with battle_system
        mock_scene = Mock()
        mock_battle_system = Mock()
        mock_battle_system.state = BattleState.VICTORY
        mock_scene.battle_system = mock_battle_system

        # Create phase manager
        phase_manager = BattlePhaseManager(scene=mock_scene)

        # Set initial state to a valid one
        phase_manager._current_state = BattleState.PLAYER_CHOOSE

        # Remove the target phase to simulate missing handler
        del phase_manager._phases[BattleState.VICTORY]

        # Set state to the unmapped state (triggers state transition)
        mock_battle_system.state = BattleState.VICTORY

        # Verify ValueError is raised during state transition
        with self.assertRaises(ValueError) as context:
            phase_manager.update(dt=0.016)

        error_message = str(context.exception)
        self.assertIn("BattlePhaseManager", error_message)
        self.assertIn("No phase handler registered", error_message)
        self.assertIn("VICTORY", error_message)

    def test_update_succeeds_with_valid_phase(self) -> None:
        """Test that update() works correctly when all phases are registered."""
        # Create a minimal mock scene with battle_system
        mock_scene = Mock()
        mock_battle_system = Mock()
        mock_battle_system.state = BattleState.PLAYER_CHOOSE
        mock_scene.battle_system = mock_battle_system

        # Create phase manager
        phase_manager = BattlePhaseManager(scene=mock_scene)

        # Verify update() doesn't raise an error
        try:
            phase_manager.update(dt=0.016)
        except ValueError:
            self.fail("update() raised ValueError unexpectedly for valid phase")


if __name__ == "__main__":
    unittest.main()
