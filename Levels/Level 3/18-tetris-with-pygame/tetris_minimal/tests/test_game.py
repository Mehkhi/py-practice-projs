"""
Unit tests for Tetris game movement state machine (DAS/ARR and lock-delay logic).

These tests verify:
- DAS (Delayed Auto Shift): Initial delay before key repeat starts
- ARR (Auto Repeat Rate): Interval between repeated movements
- Lock delay: Time before locking a landed piece
- Horizontal key jitter prevention when both keys are held
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import pygame
import sys
from pathlib import Path

# Add parent directory to path so we can import tetris
sys.path.insert(0, str(Path(__file__).parent.parent))

from tetris.game import Game, KEY_REPEAT_DELAY, KEY_REPEAT_INTERVAL, LOCK_DELAY_MS, GRAVITY_EVENT, LOCK_DELAY_EVENT
from tetris.config import COLUMNS, ROWS


class TestDASARR(unittest.TestCase):
    """Tests for Delayed Auto Shift (DAS) and Auto Repeat Rate (ARR) logic."""

    def setUp(self):
        """Initialize pygame and create a game instance for each test."""
        pygame.init()
        # Dummy video driver is set in conftest.py, but we still need to initialize display
        try:
            pygame.display.set_mode((1, 1))
        except pygame.error:
            # If display init fails, that's okay for headless tests
            pass
        self.game = Game()
        # Start with piece at a safe position
        self.game.pos = (COLUMNS // 2, 5)

    def tearDown(self):
        """Clean up pygame after each test."""
        pygame.quit()

    @patch('pygame.key.get_pressed')
    @patch('pygame.time.get_ticks')
    def test_initial_key_press_moves_immediately(self, mock_ticks, mock_get_pressed):
        """Test that pressing a key moves immediately (no delay on first press)."""
        # Key is held down after initial press
        mock_get_pressed.return_value = {
            pygame.K_LEFT: True, pygame.K_RIGHT: False, pygame.K_DOWN: False,
            pygame.K_a: False, pygame.K_d: False, pygame.K_s: False
        }
        mock_ticks.return_value = 1000

        initial_x = self.game.pos[0]

        # Simulate LEFT key press
        event = Mock()
        event.type = pygame.KEYDOWN
        event.key = pygame.K_LEFT
        self.game.update(event)

        # Piece should move immediately
        self.assertEqual(self.game.pos[0], initial_x - 1)
        self.assertIsNotNone(self.game.key_press_times[pygame.K_LEFT])

    @patch('pygame.key.get_pressed')
    @patch('pygame.time.get_ticks')
    def test_key_repeat_delay(self, mock_ticks, mock_get_pressed):
        """Test that key repeat only starts after KEY_REPEAT_DELAY milliseconds."""
        mock_get_pressed.return_value = {
            pygame.K_LEFT: True, pygame.K_RIGHT: False, pygame.K_DOWN: False,
            pygame.K_a: False, pygame.K_d: False, pygame.K_s: False
        }

        initial_x = self.game.pos[0]
        start_time = 1000

        # Press LEFT key
        mock_ticks.return_value = start_time
        event = Mock()
        event.type = pygame.KEYDOWN
        event.key = pygame.K_LEFT
        self.game.update(event)

        # Move should happen immediately
        self.assertEqual(self.game.pos[0], initial_x - 1)
        first_x = self.game.pos[0]

        # Advance time but not enough to trigger repeat
        mock_ticks.return_value = start_time + KEY_REPEAT_DELAY - 10
        self.game.update(None)  # Process held keys

        # Should not have moved again yet
        self.assertEqual(self.game.pos[0], first_x)

        # Advance past the delay threshold
        mock_ticks.return_value = start_time + KEY_REPEAT_DELAY
        self.game.update(None)

        # Should have moved once more
        self.assertEqual(self.game.pos[0], first_x - 1)

    @patch('pygame.key.get_pressed')
    @patch('pygame.time.get_ticks')
    def test_key_repeat_interval(self, mock_ticks, mock_get_pressed):
        """Test that repeated movements happen at KEY_REPEAT_INTERVAL intervals."""
        mock_get_pressed.return_value = {
            pygame.K_LEFT: True, pygame.K_RIGHT: False, pygame.K_DOWN: False,
            pygame.K_a: False, pygame.K_d: False, pygame.K_s: False
        }

        initial_x = self.game.pos[0]
        start_time = 1000

        # Press LEFT key
        mock_ticks.return_value = start_time
        event = Mock()
        event.type = pygame.KEYDOWN
        event.key = pygame.K_LEFT
        self.game.update(event)

        # Wait past initial delay
        mock_ticks.return_value = start_time + KEY_REPEAT_DELAY
        self.game.update(None)
        first_repeat_x = self.game.pos[0]

        # Advance time but not enough for next repeat
        mock_ticks.return_value = start_time + KEY_REPEAT_DELAY + KEY_REPEAT_INTERVAL - 5
        self.game.update(None)
        self.assertEqual(self.game.pos[0], first_repeat_x)

        # Advance past interval threshold
        mock_ticks.return_value = start_time + KEY_REPEAT_DELAY + KEY_REPEAT_INTERVAL
        self.game.update(None)
        self.assertEqual(self.game.pos[0], first_repeat_x - 1)

    @patch('pygame.key.get_pressed')
    @patch('pygame.time.get_ticks')
    def test_horizontal_key_jitter_prevention(self, mock_ticks, mock_get_pressed):
        """Test that holding both LEFT and RIGHT doesn't cause jitter."""
        # Both keys held
        mock_get_pressed.return_value = {
            pygame.K_LEFT: True, pygame.K_RIGHT: True, pygame.K_DOWN: False,
            pygame.K_a: False, pygame.K_d: False, pygame.K_s: False
        }

        initial_x = self.game.pos[0]
        start_time = 1000

        # Press LEFT first
        mock_ticks.return_value = start_time
        event = Mock()
        event.type = pygame.KEYDOWN
        event.key = pygame.K_LEFT
        self.game.update(event)
        self.assertEqual(self.game.pos[0], initial_x - 1)
        self.assertEqual(self.game.last_horizontal_key, pygame.K_LEFT)

        # Then press RIGHT (while LEFT still held)
        event.key = pygame.K_RIGHT
        self.game.update(event)
        # Should have moved right (most recent key)
        self.assertEqual(self.game.pos[0], initial_x)  # Back to start
        self.assertEqual(self.game.last_horizontal_key, pygame.K_RIGHT)

        # Process held keys - should only process RIGHT (most recent)
        mock_ticks.return_value = start_time + KEY_REPEAT_DELAY
        self.game.update(None)
        # Should have moved right again
        self.assertEqual(self.game.pos[0], initial_x + 1)

    @patch('pygame.key.get_pressed')
    @patch('pygame.time.get_ticks')
    def test_key_release_clears_timers(self, mock_ticks, mock_get_pressed):
        """Test that releasing a key clears its timers."""
        mock_get_pressed.return_value = {
            pygame.K_LEFT: True, pygame.K_RIGHT: False, pygame.K_DOWN: False,
            pygame.K_a: False, pygame.K_d: False, pygame.K_s: False
        }

        start_time = 1000
        mock_ticks.return_value = start_time

        # Press LEFT
        event = Mock()
        event.type = pygame.KEYDOWN
        event.key = pygame.K_LEFT
        self.game.update(event)
        self.assertIsNotNone(self.game.key_press_times[pygame.K_LEFT])

        # Release LEFT
        mock_get_pressed.return_value = {
            pygame.K_LEFT: False, pygame.K_RIGHT: False, pygame.K_DOWN: False,
            pygame.K_a: False, pygame.K_d: False, pygame.K_s: False
        }
        event.type = pygame.KEYUP
        event.key = pygame.K_LEFT
        self.game.update(event)

        # Timers should be cleared
        self.assertIsNone(self.game.key_press_times[pygame.K_LEFT])
        self.assertIsNone(self.game.key_last_move_times[pygame.K_LEFT])

    @patch('pygame.key.get_pressed')
    @patch('pygame.time.get_ticks')
    def test_tick_drives_repeat(self, mock_ticks, mock_get_pressed):
        """Test that tick() drives key repeat behavior correctly."""
        mock_get_pressed.return_value = {
            pygame.K_LEFT: True, pygame.K_RIGHT: False, pygame.K_DOWN: False,
            pygame.K_a: False, pygame.K_d: False, pygame.K_s: False
        }

        initial_x = self.game.pos[0]
        start_time = 1000

        # Press LEFT key using handle_event
        mock_ticks.return_value = start_time
        event = Mock()
        event.type = pygame.KEYDOWN
        event.key = pygame.K_LEFT
        self.game.handle_event(event)

        # Move should happen immediately
        self.assertEqual(self.game.pos[0], initial_x - 1)
        first_x = self.game.pos[0]

        # Advance time but not enough to trigger repeat
        mock_ticks.return_value = start_time + KEY_REPEAT_DELAY - 10
        self.game.tick()  # Use tick() instead of update(None)

        # Should not have moved again yet
        self.assertEqual(self.game.pos[0], first_x)

        # Advance past the delay threshold
        mock_ticks.return_value = start_time + KEY_REPEAT_DELAY
        self.game.tick()

        # Should have moved once more
        self.assertEqual(self.game.pos[0], first_x - 1)
        second_x = self.game.pos[0]

        # Advance past first repeat interval
        mock_ticks.return_value = start_time + KEY_REPEAT_DELAY + KEY_REPEAT_INTERVAL
        self.game.tick()

        # Should have moved again
        self.assertEqual(self.game.pos[0], second_x - 1)

    @patch('pygame.key.get_pressed')
    @patch('pygame.time.get_ticks')
    def test_handle_event_throttle(self, mock_ticks, mock_get_pressed):
        """Test that handle_event throttles held-key polling to prevent extra repeats."""
        from tetris.config import FPS

        mock_get_pressed.return_value = {
            pygame.K_LEFT: True, pygame.K_RIGHT: False, pygame.K_DOWN: False,
            pygame.K_a: False, pygame.K_d: False, pygame.K_s: False
        }

        initial_x = self.game.pos[0]
        start_time = 1000
        frame_time_ms = 1000 // FPS

        # Press LEFT key
        mock_ticks.return_value = start_time
        event = Mock()
        event.type = pygame.KEYDOWN
        event.key = pygame.K_LEFT
        self.game.handle_event(event)

        # Move should happen immediately
        self.assertEqual(self.game.pos[0], initial_x - 1)
        first_x = self.game.pos[0]

        # Advance time past repeat delay
        mock_ticks.return_value = start_time + KEY_REPEAT_DELAY

        # Simulate many events arriving in quick succession (same frame time)
        # Only the first handle_event should poll held keys due to throttling
        for i in range(10):
            event = Mock()
            event.type = pygame.KEYUP  # Some other event
            event.key = pygame.K_SPACE
            self.game.handle_event(event)

        # Should have moved only once (from the throttled poll)
        self.assertEqual(self.game.pos[0], first_x - 1)

        # Advance time by repeat interval to trigger another move
        mock_ticks.return_value = start_time + KEY_REPEAT_DELAY + KEY_REPEAT_INTERVAL

        # Now another handle_event should poll again
        event = Mock()
        event.type = pygame.KEYUP
        event.key = pygame.K_SPACE
        self.game.handle_event(event)

        # Should have moved again (another repeat)
        self.assertEqual(self.game.pos[0], first_x - 2)

    @patch('pygame.key.get_pressed')
    @patch('pygame.time.get_ticks')
    def test_pause_preserves_horizontal_preference(self, mock_ticks, mock_get_pressed):
        """Test that pausing while both horizontal keys are held preserves preference."""
        # Both keys held
        mock_get_pressed.return_value = {
            pygame.K_LEFT: True, pygame.K_RIGHT: True, pygame.K_DOWN: False,
            pygame.K_a: False, pygame.K_d: False, pygame.K_s: False
        }

        initial_x = self.game.pos[0]
        start_time = 1000
        mock_ticks.return_value = start_time

        # Press LEFT first
        event = Mock()
        event.type = pygame.KEYDOWN
        event.key = pygame.K_LEFT
        self.game.update(event)
        self.assertEqual(self.game.pos[0], initial_x - 1)
        self.assertEqual(self.game.last_horizontal_key, pygame.K_LEFT)

        # Press RIGHT (while LEFT still held)
        event.key = pygame.K_RIGHT
        self.game.update(event)
        self.assertEqual(self.game.pos[0], initial_x)  # Back to start
        self.assertEqual(self.game.last_horizontal_key, pygame.K_RIGHT)

        # Pause while both keys are still held
        event.key = pygame.K_p
        self.game.update(event)
        self.assertTrue(self.game.paused)
        # last_horizontal_key should be preserved
        self.assertEqual(self.game.last_horizontal_key, pygame.K_RIGHT)

        # Advance time past repeat delay
        mock_ticks.return_value = start_time + KEY_REPEAT_DELAY

        # Unpause
        event.key = pygame.K_p
        self.game.update(event)
        self.assertFalse(self.game.paused)

        # Process held keys - should move RIGHT (preserved preference)
        self.game.update(None)
        self.assertEqual(self.game.pos[0], initial_x + 1)

    @patch('pygame.key.get_pressed')
    @patch('pygame.time.get_ticks')
    def test_both_pressed_fallback_when_no_preference(self, mock_ticks, mock_get_pressed):
        """Test that both-pressed fallback works when last_horizontal_key is None."""
        # Both keys held
        mock_get_pressed.return_value = {
            pygame.K_LEFT: True, pygame.K_RIGHT: True, pygame.K_DOWN: False,
            pygame.K_a: False, pygame.K_d: False, pygame.K_s: False
        }

        initial_x = self.game.pos[0]
        start_time = 1000
        mock_ticks.return_value = start_time

        # Simulate both keys being pressed (to initialize key press times)
        event = Mock()
        event.type = pygame.KEYDOWN
        event.key = pygame.K_LEFT
        self.game.handle_event(event)
        self.assertEqual(self.game.pos[0], initial_x - 1)

        event.key = pygame.K_RIGHT
        self.game.handle_event(event)
        self.assertEqual(self.game.pos[0], initial_x)  # Back to initial position

        # Clear last_horizontal_key to simulate edge case where preference is lost
        self.game.last_horizontal_key = None

        # Advance past repeat delay
        mock_ticks.return_value = start_time + KEY_REPEAT_DELAY

        # Process held keys - should fallback to LEFT
        self.game.update(None)
        # Should have moved LEFT (fallback)
        self.assertEqual(self.game.pos[0], initial_x - 1)

    @patch('pygame.key.get_pressed')
    @patch('pygame.time.get_ticks')
    def test_update_with_event_polls_held_keys(self, mock_ticks, mock_get_pressed):
        """Test that update(event) triggers held-key polling for legacy compatibility."""
        mock_get_pressed.return_value = {
            pygame.K_LEFT: True, pygame.K_RIGHT: False, pygame.K_DOWN: False,
            pygame.K_a: False, pygame.K_d: False, pygame.K_s: False
        }

        initial_x = self.game.pos[0]
        start_time = 1000

        # Press LEFT key using update(event)
        mock_ticks.return_value = start_time
        event = Mock()
        event.type = pygame.KEYDOWN
        event.key = pygame.K_LEFT
        self.game.update(event)

        # Move should happen immediately
        self.assertEqual(self.game.pos[0], initial_x - 1)
        first_x = self.game.pos[0]

        # Advance time past repeat delay
        mock_ticks.return_value = start_time + KEY_REPEAT_DELAY

        # Call update with a different event (simulating legacy per-event loop)
        event.type = pygame.KEYUP
        event.key = pygame.K_SPACE
        self.game.update(event)

        # Should have moved again due to polling triggered by update(event)
        self.assertEqual(self.game.pos[0], first_x - 1)


class TestLockDelay(unittest.TestCase):
    """Tests for lock delay logic (allows lateral movement after piece lands)."""

    def setUp(self):
        """Initialize pygame and create a game instance for each test."""
        pygame.init()
        # Dummy video driver is set in conftest.py, but we still need to initialize display
        try:
            pygame.display.set_mode((1, 1))
        except pygame.error:
            # If display init fails, that's okay for headless tests
            pass
        self.game = Game()
        # Position piece near bottom
        self.game.pos = (COLUMNS // 2, ROWS - 3)

    def tearDown(self):
        """Clean up pygame after each test."""
        pygame.quit()

    def _fill_bottom_rows(self, num_rows: int):
        """Helper to fill bottom rows of board to create landing condition."""
        for y in range(ROWS - num_rows, ROWS):
            for x in range(COLUMNS):
                self.game.board.grid[y][x] = 'I'

    @patch('pygame.time.get_ticks')
    @patch('pygame.time.set_timer')
    def test_lock_delay_starts_when_piece_cant_move_down(self, mock_set_timer, mock_ticks):
        """Test that lock delay starts when piece can't move down."""
        mock_ticks.return_value = 1000

        # Fill bottom row so piece can't move down
        self._fill_bottom_rows(1)
        # Move piece to just above filled area
        self.game.pos = (COLUMNS // 2, ROWS - 2)

        # Trigger gravity event (piece can't move down)
        event = Mock()
        event.type = GRAVITY_EVENT
        self.game.update(event)

        # Lock delay should have started
        self.assertIsNotNone(self.game.lock_delay_start)
        mock_set_timer.assert_called()

    @patch('pygame.key.get_pressed')
    @patch('pygame.time.get_ticks')
    @patch('pygame.time.set_timer')
    def test_rotation_resets_lock_delay(self, mock_set_timer, mock_ticks, mock_get_pressed):
        """Test that rotating resets the lock delay."""
        # Mock get_pressed to return no keys pressed (avoid interference from throttling logic)
        mock_get_pressed.return_value = {
            pygame.K_LEFT: False, pygame.K_RIGHT: False, pygame.K_DOWN: False,
            pygame.K_a: False, pygame.K_d: False, pygame.K_s: False
        }
        mock_ticks.return_value = 1000

        # Create a narrow platform in the center for piece to land on
        # This gives room for rotation without collision
        for x in range(COLUMNS // 2 - 1, COLUMNS // 2 + 3):
            self.game.board.grid[ROWS - 1][x] = 'I'

        # Position piece higher up, centered on platform
        self.game.pos = (COLUMNS // 2, ROWS - 5)

        # Move piece down until it's grounded on the platform
        while self.game._can_move(0, 1):
            self.game.pos = (self.game.pos[0], self.game.pos[1] + 1)

        # Start lock delay
        event = Mock()
        event.type = GRAVITY_EVENT
        self.game.update(event)
        self.assertIsNotNone(self.game.lock_delay_start)

        # Record the initial lock_delay_start time
        initial_lock_delay_start = self.game.lock_delay_start

        # Reset mock to track rotation calls
        mock_set_timer.reset_mock()
        mock_ticks.return_value = 1500

        # Rotate - should reset lock delay (even if it re-arms)
        event.type = pygame.KEYDOWN
        event.key = pygame.K_UP
        self.game.update(event)

        # Lock delay should have been reset at some point during rotation
        # Check that set_timer was called (to cancel the timer)
        self.assertGreaterEqual(mock_set_timer.call_count, 1)
        # Verify timer was canceled at least once
        mock_set_timer.assert_any_call(LOCK_DELAY_EVENT, 0)

    @patch('pygame.key.get_pressed')
    @patch('pygame.time.get_ticks')
    def test_lock_delay_expires_and_locks_piece(self, mock_ticks, mock_get_pressed):
        """Test that piece locks after lock delay expires."""
        # Mock get_pressed to return no keys pressed
        mock_get_pressed.return_value = {
            pygame.K_LEFT: False, pygame.K_RIGHT: False, pygame.K_DOWN: False,
            pygame.K_a: False, pygame.K_d: False, pygame.K_s: False
        }
        start_time = 1000
        mock_ticks.return_value = start_time

        # Fill bottom 3 rows to provide landing surface
        self._fill_bottom_rows(3)
        # Position piece at ROWS-4 so piece blocks (with max y offset of 2) stay in bounds
        self.game.pos = (COLUMNS // 2, ROWS - 4)

        # Start lock delay
        self.game._check_and_start_lock_delay()
        self.assertIsNotNone(self.game.lock_delay_start)

        initial_piece_kind = self.game.current.kind

        # Simulate lock delay event after delay expires
        mock_ticks.return_value = start_time + LOCK_DELAY_MS
        event = Mock()
        event.type = LOCK_DELAY_EVENT
        self.game.update(event)

        # Piece should be locked (new piece spawned)
        self.assertNotEqual(self.game.current.kind, initial_piece_kind)
        self.assertIsNone(self.game.lock_delay_start)

    @patch('pygame.key.get_pressed')
    @patch('pygame.time.get_ticks')
    def test_lock_delay_cancelled_when_piece_can_move_again(self, mock_ticks, mock_get_pressed):
        """Test that lock delay is cancelled if piece can move down again."""
        # Mock get_pressed to return no keys pressed
        mock_get_pressed.return_value = {
            pygame.K_LEFT: False, pygame.K_RIGHT: False, pygame.K_DOWN: False,
            pygame.K_a: False, pygame.K_d: False, pygame.K_s: False
        }
        start_time = 1000
        mock_ticks.return_value = start_time

        # Fill bottom row
        self._fill_bottom_rows(1)
        # Position piece higher up
        self.game.pos = (COLUMNS // 2, ROWS - 5)

        # Move piece down until it's grounded
        while self.game._can_move(0, 1):
            self.game.pos = (self.game.pos[0], self.game.pos[1] + 1)

        # Start lock delay
        self.game._check_and_start_lock_delay()
        self.assertIsNotNone(self.game.lock_delay_start)

        # Clear bottom row so piece can move down again
        for x in range(COLUMNS):
            self.game.board.grid[ROWS - 1][x] = None

        # Trigger gravity - piece should move down and reset lock delay
        event = Mock()
        event.type = GRAVITY_EVENT
        self.game.update(event)

        # Lock delay should be reset
        self.assertIsNone(self.game.lock_delay_start)

    @patch('pygame.time.get_ticks')
    @patch('pygame.time.set_timer')
    def test_pause_cancels_lock_delay_timer(self, mock_set_timer, mock_ticks):
        """Test that pausing cancels the lock delay timer and clears lock_delay_start."""
        mock_ticks.return_value = 1000

        # Fill bottom row
        self._fill_bottom_rows(1)
        self.game.pos = (COLUMNS // 2, ROWS - 2)

        # Start lock delay
        event = Mock()
        event.type = GRAVITY_EVENT
        self.game.update(event)
        self.assertIsNotNone(self.game.lock_delay_start)

        # Pause - should cancel timer and clear lock_delay_start
        event.type = pygame.KEYDOWN
        event.key = pygame.K_p
        self.game.update(event)

        # Timer should be cancelled (set_timer called with 0)
        mock_set_timer.assert_called_with(LOCK_DELAY_EVENT, 0)
        # lock_delay_start should be cleared
        self.assertIsNone(self.game.lock_delay_start)

    @patch('pygame.time.get_ticks')
    @patch('pygame.time.set_timer')
    def test_resume_rearms_lock_delay_when_grounded(self, mock_set_timer, mock_ticks):
        """Test that resuming re-arms lock delay if piece is still grounded."""
        mock_ticks.return_value = 1000

        # Fill bottom row
        self._fill_bottom_rows(1)
        self.game.pos = (COLUMNS // 2, ROWS - 2)

        # Start lock delay
        event = Mock()
        event.type = GRAVITY_EVENT
        self.game.update(event)
        self.assertIsNotNone(self.game.lock_delay_start)

        # Pause - clears lock_delay_start
        event.type = pygame.KEYDOWN
        event.key = pygame.K_p
        self.game.update(event)
        self.assertIsNone(self.game.lock_delay_start)

        # Reset mock to track resume calls
        mock_set_timer.reset_mock()
        mock_ticks.return_value = 2000

        # Resume - should re-arm lock delay since piece is still grounded
        event.key = pygame.K_p
        self.game.update(event)

        # Should have started lock delay again
        self.assertIsNotNone(self.game.lock_delay_start)
        # Should have set timer for lock delay
        mock_set_timer.assert_called_with(LOCK_DELAY_EVENT, LOCK_DELAY_MS)

    @patch('pygame.key.get_pressed')
    @patch('pygame.time.get_ticks')
    @patch('pygame.time.set_timer')
    def test_lateral_move_rearms_lock_delay_when_grounded(self, mock_set_timer, mock_ticks, mock_get_pressed):
        """Test that lateral movement re-arms lock delay if piece is still grounded."""
        # Mock get_pressed to return no keys pressed
        mock_get_pressed.return_value = {
            pygame.K_LEFT: False, pygame.K_RIGHT: False, pygame.K_DOWN: False,
            pygame.K_a: False, pygame.K_d: False, pygame.K_s: False
        }
        mock_ticks.return_value = 1000

        # Simple setup: fill only bottom row, position piece higher up
        # This gives piece room to fall and hit the bottom
        self._fill_bottom_rows(1)
        # Position piece so it will land on bottom row when gravity pulls it down
        # Use a higher position to ensure piece is clearly above the bottom
        self.game.pos = (COLUMNS // 2, ROWS - 5)

        # Move piece down until it's grounded
        while self.game._can_move(0, 1):
            self.game.pos = (self.game.pos[0], self.game.pos[1] + 1)

        # Now piece should be grounded - start lock delay
        event = Mock()
        event.type = GRAVITY_EVENT
        self.game.update(event)
        self.assertIsNotNone(self.game.lock_delay_start)

        # Reset mock to track lateral move calls
        mock_set_timer.reset_mock()
        mock_ticks.return_value = 1500

        # Move left while grounded - should reset and re-arm lock delay
        event.type = pygame.KEYDOWN
        event.key = pygame.K_LEFT
        self.game.update(event)

        # Should have reset lock delay (canceled timer)
        # Then re-armed it (set timer again)
        # Check that set_timer was called at least twice: once to cancel, once to re-arm
        self.assertGreaterEqual(mock_set_timer.call_count, 2)
        # Last call should be to re-arm with LOCK_DELAY_MS
        mock_set_timer.assert_any_call(LOCK_DELAY_EVENT, LOCK_DELAY_MS)
        # lock_delay_start should be set again
        self.assertIsNotNone(self.game.lock_delay_start)

    @patch('pygame.key.get_pressed')
    @patch('pygame.time.get_ticks')
    @patch('pygame.time.set_timer')
    def test_rotation_rearms_lock_delay_when_grounded(self, mock_set_timer, mock_ticks, mock_get_pressed):
        """Test that rotation re-arms lock delay if piece is still grounded."""
        mock_ticks.return_value = 1000
        mock_get_pressed.return_value = {
            pygame.K_LEFT: False,
            pygame.K_RIGHT: False,
            pygame.K_DOWN: False,
            pygame.K_a: False,
            pygame.K_d: False,
            pygame.K_s: False
        }

        # Create a narrow platform in the center for piece to land on
        # This gives room for rotation without collision
        for x in range(COLUMNS // 2 - 1, COLUMNS // 2 + 3):
            self.game.board.grid[ROWS - 1][x] = 'I'

        # Position piece higher up, centered on platform
        self.game.pos = (COLUMNS // 2, ROWS - 5)

        # Move piece down until it's grounded on the platform
        while self.game._can_move(0, 1):
            self.game.pos = (self.game.pos[0], self.game.pos[1] + 1)

        # Now piece should be grounded - start lock delay
        event = Mock()
        event.type = GRAVITY_EVENT
        self.game.update(event)
        self.assertIsNotNone(self.game.lock_delay_start)

        # Reset mock to track rotation calls
        mock_set_timer.reset_mock()
        mock_ticks.return_value = 1500

        # Rotate while grounded - should reset and re-arm lock delay
        event.type = pygame.KEYDOWN
        event.key = pygame.K_UP
        self.game.update(event)

        # Should have reset lock delay (canceled timer)
        # Then re-armed it (set timer again)
        # Check that set_timer was called at least twice: once to cancel, once to re-arm
        self.assertGreaterEqual(mock_set_timer.call_count, 2)
        # Last call should be to re-arm with LOCK_DELAY_MS
        mock_set_timer.assert_any_call(LOCK_DELAY_EVENT, LOCK_DELAY_MS)
        # lock_delay_start should be set again
        self.assertIsNotNone(self.game.lock_delay_start)


class TestBoardClearLines(unittest.TestCase):
    """Tests for Board._clear_lines functionality."""

    def setUp(self):
        """Initialize pygame and create a board instance for each test."""
        pygame.init()
        try:
            pygame.display.set_mode((1, 1))
        except pygame.error:
            pass
        from tetris.core.board import Board
        from tetris.config import COLUMNS, ROWS
        self.board = Board(COLUMNS, ROWS)

    def tearDown(self):
        """Clean up pygame after each test."""
        pygame.quit()

    def test_no_lines_cleared(self):
        """Test that _clear_lines returns 0 when no lines are full."""
        # Fill some cells but not full rows
        self.board.grid[ROWS - 1][0] = 'I'
        self.board.grid[ROWS - 1][1] = 'I'
        cleared = self.board._clear_lines()
        self.assertEqual(cleared, 0)
        # Grid should be unchanged
        self.assertIsNotNone(self.board.grid[ROWS - 1][0])

    def test_single_line_cleared(self):
        """Test that a single full line is cleared."""
        # Fill bottom row completely
        for x in range(COLUMNS):
            self.board.grid[ROWS - 1][x] = 'I'
        cleared = self.board._clear_lines()
        self.assertEqual(cleared, 1)
        # Bottom row should now be empty
        self.assertTrue(all(cell is None for cell in self.board.grid[ROWS - 1]))

    def test_multiple_lines_cleared(self):
        """Test that multiple full lines are cleared."""
        # Fill bottom two rows completely
        for y in range(ROWS - 2, ROWS):
            for x in range(COLUMNS):
                self.board.grid[y][x] = 'I'
        # Add a block above to verify it falls down
        self.board.grid[ROWS - 3][0] = 'T'
        cleared = self.board._clear_lines()
        self.assertEqual(cleared, 2)
        # The block from ROWS-3 should have fallen down to ROWS-1
        self.assertEqual(self.board.grid[ROWS - 1][0], 'T')
        # Rest of bottom row should be empty
        self.assertTrue(all(cell is None for cell in self.board.grid[ROWS - 1][1:]))
        # Second-to-bottom row should be completely empty
        self.assertTrue(all(cell is None for cell in self.board.grid[ROWS - 2]))

    def test_all_lines_cleared(self):
        """Test clearing all lines (edge case)."""
        # Fill entire board
        for y in range(ROWS):
            for x in range(COLUMNS):
                self.board.grid[y][x] = 'I'
        cleared = self.board._clear_lines()
        self.assertEqual(cleared, ROWS)
        # All rows should be empty
        for y in range(ROWS):
            self.assertTrue(all(cell is None for cell in self.board.grid[y]))


class TestScoring(unittest.TestCase):
    """Tests for ScoreState scoring logic."""

    def setUp(self):
        """Initialize pygame and create a score state for each test."""
        pygame.init()
        try:
            pygame.display.set_mode((1, 1))
        except pygame.error:
            pass
        from tetris.core.rules import ScoreState
        self.score = ScoreState()

    def tearDown(self):
        """Clean up pygame after each test."""
        pygame.quit()

    def test_single_line_score(self):
        """Test scoring for clearing 1 line."""
        initial_score = self.score.score
        self.score.on_clear(1)
        # Level 1: 1 line = 100 points
        self.assertEqual(self.score.score, initial_score + 100)
        self.assertEqual(self.score.lines, 1)

    def test_double_line_score(self):
        """Test scoring for clearing 2 lines."""
        initial_score = self.score.score
        self.score.on_clear(2)
        # Level 1: 2 lines = 300 points
        self.assertEqual(self.score.score, initial_score + 300)
        self.assertEqual(self.score.lines, 2)

    def test_triple_line_score(self):
        """Test scoring for clearing 3 lines."""
        initial_score = self.score.score
        self.score.on_clear(3)
        # Level 1: 3 lines = 500 points
        self.assertEqual(self.score.score, initial_score + 500)
        self.assertEqual(self.score.lines, 3)

    def test_tetris_score(self):
        """Test scoring for clearing 4 lines (Tetris)."""
        initial_score = self.score.score
        self.score.on_clear(4)
        # Level 1: 4 lines = 800 points
        self.assertEqual(self.score.score, initial_score + 800)
        self.assertEqual(self.score.lines, 4)

    def test_scoring_scales_with_level(self):
        """Test that scoring multiplies by level."""
        # Advance to level 2
        self.score.lines = 10
        self.score.level = 2
        initial_score = self.score.score
        self.score.on_clear(1)
        # Level 2: 1 line = 100 * 2 = 200 points
        self.assertEqual(self.score.score, initial_score + 200)

    def test_level_up(self):
        """Test that level increases after clearing enough lines."""
        self.assertEqual(self.score.level, 1)
        # Clear 10 lines (should level up to 2)
        self.score.on_clear(10)
        self.assertEqual(self.score.level, 2)
        self.assertEqual(self.score.lines, 10)
        # Clear 10 more lines (should level up to 3)
        self.score.on_clear(10)
        self.assertEqual(self.score.level, 3)
        self.assertEqual(self.score.lines, 20)

    def test_soft_drop_score(self):
        """Test scoring for soft drop."""
        initial_score = self.score.score
        self.score.on_soft_drop()
        # Soft drop gives 1 point per step
        self.assertEqual(self.score.score, initial_score + 1)

    def test_hard_drop_score(self):
        """Test scoring for hard drop."""
        initial_score = self.score.score
        distance = 5
        self.score.on_hard_drop(distance)
        # Hard drop gives 2 points per cell dropped
        self.assertEqual(self.score.score, initial_score + 2 * distance)


class TestGravity(unittest.TestCase):
    """Tests for gravity timing by level."""

    def setUp(self):
        """Initialize pygame for each test."""
        pygame.init()
        try:
            pygame.display.set_mode((1, 1))
        except pygame.error:
            pass

    def tearDown(self):
        """Clean up pygame after each test."""
        pygame.quit()

    def test_gravity_ms_level_1(self):
        """Test gravity timing for level 1."""
        from tetris.core.rules import gravity_ms
        # Level 1: max(80, 800 - (1-1)*60) = max(80, 800) = 800ms
        self.assertEqual(gravity_ms(1), 800)

    def test_gravity_ms_level_2(self):
        """Test gravity timing for level 2."""
        from tetris.core.rules import gravity_ms
        # Level 2: max(80, 800 - (2-1)*60) = max(80, 740) = 740ms
        self.assertEqual(gravity_ms(2), 740)

    def test_gravity_ms_level_10(self):
        """Test gravity timing for level 10."""
        from tetris.core.rules import gravity_ms
        # Level 10: max(80, 800 - (10-1)*60) = max(80, 260) = 260ms
        self.assertEqual(gravity_ms(10), 260)

    def test_gravity_ms_minimum(self):
        """Test that gravity has a minimum of 80ms."""
        from tetris.core.rules import gravity_ms
        # Very high level should still return minimum
        # Level 13: max(80, 800 - (13-1)*60) = max(80, 80) = 80ms
        self.assertEqual(gravity_ms(13), 80)
        # Level 20: max(80, 800 - (20-1)*60) = max(80, -340) = 80ms
        self.assertEqual(gravity_ms(20), 80)


class TestGhostPiece(unittest.TestCase):
    """Tests for ghost piece (preview of drop position) and lock interactions."""

    def setUp(self):
        """Initialize pygame and create a game instance for each test."""
        pygame.init()
        try:
            pygame.display.set_mode((1, 1))
        except pygame.error:
            pass
        self.game = Game(seed=42)  # Use seed for deterministic testing
        self.game.pos = (COLUMNS // 2, 5)

    def tearDown(self):
        """Clean up pygame after each test."""
        pygame.quit()

    def test_ghost_distance_calculation(self):
        """Test that drop_distance calculates correct distance."""
        # Place piece above empty board
        self.game.pos = (COLUMNS // 2, 0)
        distance = self.game.board.drop_distance(self.game.current.blocks(), self.game.pos)
        # Should be able to drop to bottom (allowing for piece height)
        self.assertGreater(distance, ROWS - 5)  # Piece starts at y=0, board height is ROWS

    def test_ghost_distance_with_obstacle(self):
        """Test that drop_distance stops at obstacles."""
        # Fill a row near bottom
        obstacle_y = ROWS - 5
        for x in range(COLUMNS):
            self.game.board.grid[obstacle_y][x] = 'I'
        # Place piece above obstacle
        self.game.pos = (COLUMNS // 2, 0)
        distance = self.game.board.drop_distance(self.game.current.blocks(), self.game.pos)
        # Should stop just above obstacle
        self.assertLess(distance, obstacle_y)

    def test_lock_piece_updates_board(self):
        """Test that locking a piece updates the board grid."""
        initial_kind = self.game.current.kind
        blocks = self.game.current.blocks()
        pos = (COLUMNS // 2, ROWS - 3)
        cleared = self.game.board.lock_piece(initial_kind, blocks, pos)
        # Check that blocks were placed on board
        for (cx, cy) in blocks:
            x, y = pos[0] + cx, pos[1] + cy
            if y >= 0:
                self.assertEqual(self.game.board.grid[y][x], initial_kind)

    def test_lock_triggers_line_clear(self):
        """Test that locking a piece that completes a line triggers clearing."""
        # Fill bottom row except one column, leaving column 0 empty
        for x in range(1, COLUMNS):
            self.game.board.grid[ROWS - 1][x] = 'I'
        # Use an O piece (2x2) positioned to fill the gap at columns 0-1
        from tetris.core.piece import Piece
        self.game.current = Piece('O')
        self.game.pos = (-1, ROWS - 3)  # Position so blocks occupy columns 0-1, rows 18-19
        initial_score = self.game.score.score
        self.game._lock_current()
        # Score should have increased (line cleared)
        self.assertGreater(self.game.score.score, initial_score)


class TestPauseRegression(unittest.TestCase):
    """Regression tests for pause/resume timing issues."""

    def setUp(self):
        """Initialize pygame and create a game instance for each test."""
        pygame.init()
        try:
            pygame.display.set_mode((1, 1))
        except pygame.error:
            pass
        self.game = Game(seed=42)
        self.game.pos = (COLUMNS // 2, 5)

    def tearDown(self):
        """Clean up pygame after each test."""
        pygame.quit()

    @patch('pygame.time.get_ticks')
    @patch('pygame.time.set_timer')
    def test_pause_longer_than_gravity_interval(self, mock_set_timer, mock_ticks):
        """Test that pausing longer than a gravity interval doesn't cause immediate drop."""
        from tetris.core.rules import gravity_ms

        start_time = 1000
        mock_ticks.return_value = start_time

        # Get current gravity interval
        gravity_interval = gravity_ms(self.game.score.level)

        # Position piece so it can move down
        self.game.pos = (COLUMNS // 2, 5)
        initial_y = self.game.pos[1]

        # Pause the game
        event = Mock()
        event.type = pygame.KEYDOWN
        event.key = pygame.K_p
        self.game.handle_event(event)
        self.assertTrue(self.game.paused)

        # Verify gravity timer was stopped
        mock_set_timer.assert_any_call(GRAVITY_EVENT, 0)  # GRAVITY_EVENT stopped

        # Advance time by more than one gravity interval while paused
        mock_ticks.return_value = start_time + gravity_interval + 100

        # Simulate a gravity event arriving (should be ignored while paused)
        event.type = GRAVITY_EVENT
        self.game.handle_event(event)

        # Piece should not have moved (still paused)
        self.assertEqual(self.game.pos[1], initial_y)

        # Resume the game
        event.type = pygame.KEYDOWN
        event.key = pygame.K_p
        self.game.handle_event(event)
        self.assertFalse(self.game.paused)

        # Verify gravity timer was re-armed
        mock_set_timer.assert_any_call(GRAVITY_EVENT, gravity_interval)

        # Piece should still be at same position (no immediate drop)
        self.assertEqual(self.game.pos[1], initial_y)

        # Now advance time and trigger gravity event after resume
        mock_ticks.return_value = start_time + gravity_interval + 200
        event.type = GRAVITY_EVENT
        self.game.handle_event(event)

        # Now piece should have moved down
        self.assertEqual(self.game.pos[1], initial_y + 1)

    @patch('pygame.time.get_ticks')
    @patch('pygame.time.set_timer')
    def test_deterministic_piece_order_with_seed(self, mock_set_timer, mock_ticks):
        """Test that using a seed produces deterministic piece order."""
        # Create two games with same seed
        game1 = Game(seed=12345)
        game2 = Game(seed=12345)

        # Take several pieces from each
        pieces1 = []
        pieces2 = []
        for _ in range(14):  # Two full bags
            pieces1.append(game1.bag.take())
            pieces2.append(game2.bag.take())

        # Pieces should be in same order
        self.assertEqual(pieces1, pieces2)

        # Different seed should produce different order
        game3 = Game(seed=99999)
        pieces3 = []
        for _ in range(14):
            pieces3.append(game3.bag.take())

        # Should be different from seed 12345
        self.assertNotEqual(pieces1, pieces3)


class TestRestartRegression(unittest.TestCase):
    """Regression tests for restart functionality."""

    def setUp(self):
        """Initialize pygame and create a game instance for each test."""
        pygame.init()
        try:
            pygame.display.set_mode((1, 1))
        except pygame.error:
            pass
        self.game = Game(seed=42)

    def tearDown(self):
        """Clean up pygame after each test."""
        pygame.quit()

    @patch('pygame.time.set_timer')
    @patch('pygame.event.clear')
    def test_restart_clears_timer_events(self, mock_event_clear, mock_set_timer):
        """Test that restart clears pending timer events to prevent gravity spikes."""
        # Simulate game over state
        self.game.game_over = True

        # Create restart event
        restart_event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_r})

        # Handle restart
        self.game.handle_event(restart_event)

        # Verify timers were cancelled and events cleared
        mock_set_timer.assert_any_call(GRAVITY_EVENT, 0)
        mock_set_timer.assert_any_call(LOCK_DELAY_EVENT, 0)
        mock_event_clear.assert_called_with([GRAVITY_EVENT, LOCK_DELAY_EVENT])

        # Verify game was reset (not game over anymore)
        self.assertFalse(self.game.game_over)

    def test_bag_seed_persistence_after_restart(self):
        """Test that injected bag seeds persist through restart."""
        from tetris.core.bag import Bag

        # Create game with injected seeded bag
        test_bag = Bag(seed=999)
        game = Game(seed=42, bag=test_bag)

        # Take some pieces to advance the bag state
        original_pieces = []
        for _ in range(5):
            original_pieces.append(game.bag.take())

        # Trigger restart
        game.game_over = True
        restart_event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_r})
        game.handle_event(restart_event)

        # Take pieces from restarted game
        restarted_pieces = []
        for _ in range(5):
            restarted_pieces.append(game.bag.take())

        # Should match original sequence (deterministic restart)
        self.assertEqual(original_pieces, restarted_pieces)


class TestWASDControls(unittest.TestCase):
    """Tests for WASD control support."""

    def setUp(self):
        """Initialize pygame and create a game instance for each test."""
        pygame.init()
        try:
            pygame.display.set_mode((1, 1))
        except pygame.error:
            pass
        self.game = Game(seed=42)
        self.game.pos = (COLUMNS // 2, 5)

    def tearDown(self):
        """Clean up pygame after each test."""
        pygame.quit()

    def test_wasd_movement(self):
        """Test that WASD keys trigger the same movement as arrow keys."""
        initial_pos = self.game.pos

        # Test A key (left)
        a_event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_a})
        self.game.handle_event(a_event)
        self.assertEqual(self.game.pos[0], initial_pos[0] - 1)

        # Reset position
        self.game.pos = initial_pos

        # Test D key (right)
        d_event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_d})
        self.game.handle_event(d_event)
        self.assertEqual(self.game.pos[0], initial_pos[0] + 1)

        # Reset position
        self.game.pos = initial_pos

        # Test S key (down)
        s_event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_s})
        self.game.handle_event(s_event)
        self.assertEqual(self.game.pos[1], initial_pos[1] + 1)

    def test_w_key_rotation(self):
        """Test that W key triggers rotation like UP key."""
        initial_rotation = self.game.current.rot

        # Test W key (rotate clockwise)
        w_event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_w})
        self.game.handle_event(w_event)
        self.assertEqual(self.game.current.rot, (initial_rotation + 1) % 4)

    @patch('pygame.time.get_ticks')
    @patch('pygame.key.get_pressed')
    def test_wasd_held_key_repeat(self, mock_keys_pressed, mock_ticks):
        """Test that WASD keys repeat like arrow keys when held."""
        start_time = 1000

        # Test A key held (left movement)
        initial_x = self.game.pos[0]

        # Press A key
        mock_ticks.return_value = start_time
        a_event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_a})
        self.game.handle_event(a_event)
        self.assertEqual(self.game.pos[0], initial_x - 1)  # Initial movement

        # Simulate A key held and trigger repeat
        mock_keys_pressed.return_value = {
            pygame.K_LEFT: False, pygame.K_RIGHT: False, pygame.K_DOWN: False,
            pygame.K_a: True, pygame.K_d: False, pygame.K_s: False
        }
        mock_ticks.return_value = start_time + KEY_REPEAT_DELAY
        self.game._process_held_keys()
        self.assertEqual(self.game.pos[0], initial_x - 2)  # Repeat movement

        # Test D key held (right movement)
        self.game.pos = (initial_x, self.game.pos[1])  # Reset position

        # Press D key
        mock_ticks.return_value = start_time
        d_event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_d})
        self.game.handle_event(d_event)
        self.assertEqual(self.game.pos[0], initial_x + 1)  # Initial movement

        # Simulate D key held and trigger repeat
        mock_keys_pressed.return_value = {
            pygame.K_LEFT: False, pygame.K_RIGHT: False, pygame.K_DOWN: False,
            pygame.K_a: False, pygame.K_d: True, pygame.K_s: False
        }
        mock_ticks.return_value = start_time + KEY_REPEAT_DELAY
        self.game._process_held_keys()
        self.assertEqual(self.game.pos[0], initial_x + 2)  # Repeat movement

        # Test S key held (down movement)
        initial_y = self.game.pos[1]
        self.game.pos = (initial_x, initial_y)  # Reset position

        # Press S key
        mock_ticks.return_value = start_time
        s_event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_s})
        self.game.handle_event(s_event)
        self.assertEqual(self.game.pos[1], initial_y + 1)  # Initial movement

        # Simulate S key held and trigger repeat
        mock_keys_pressed.return_value = {
            pygame.K_LEFT: False, pygame.K_RIGHT: False, pygame.K_DOWN: False,
            pygame.K_a: False, pygame.K_d: False, pygame.K_s: True
        }
        mock_ticks.return_value = start_time + KEY_REPEAT_DELAY
        self.game._process_held_keys()
        self.assertEqual(self.game.pos[1], initial_y + 2)  # Repeat movement


class TestKeyPressedIntegration(unittest.TestCase):
    """Integration tests for _is_key_pressed with real pygame.key.ScancodeWrapper."""

    def setUp(self):
        """Initialize pygame and create a game instance for each test."""
        pygame.init()
        try:
            pygame.display.set_mode((1, 1))
        except pygame.error:
            pass
        self.game = Game()

    def tearDown(self):
        """Clean up pygame after each test."""
        pygame.quit()

    def test_is_key_pressed_with_real_pygame_keys(self):
        """
        Integration test: Verify _is_key_pressed works with real pygame.key.ScancodeWrapper.

        This test uses the actual pygame.key.get_pressed() return value (ScancodeWrapper),
        not a mock dictionary, to ensure the method handles both indexing styles correctly.
        """
        # Get real pygame keys object (ScancodeWrapper)
        keys = pygame.key.get_pressed()

        # Test that we can query various keys without errors
        # (They should all be False since no keys are actually pressed in headless mode)
        self.assertFalse(self.game._is_key_pressed(keys, pygame.K_LEFT))
        self.assertFalse(self.game._is_key_pressed(keys, pygame.K_RIGHT))
        self.assertFalse(self.game._is_key_pressed(keys, pygame.K_DOWN))
        self.assertFalse(self.game._is_key_pressed(keys, pygame.K_UP))

        # Test WASD keys
        self.assertFalse(self.game._is_key_pressed(keys, pygame.K_a))
        self.assertFalse(self.game._is_key_pressed(keys, pygame.K_d))
        self.assertFalse(self.game._is_key_pressed(keys, pygame.K_w))
        self.assertFalse(self.game._is_key_pressed(keys, pygame.K_s))

        # Test special keys
        self.assertFalse(self.game._is_key_pressed(keys, pygame.K_SPACE))
        self.assertFalse(self.game._is_key_pressed(keys, pygame.K_z))
        self.assertFalse(self.game._is_key_pressed(keys, pygame.K_x))

        # Verify the keys object is actually a ScancodeWrapper, not a dict
        self.assertNotIsInstance(keys, dict)
        self.assertEqual(type(keys).__name__, 'ScancodeWrapper')

    def test_is_key_pressed_with_mock_dict(self):
        """
        Integration test: Verify _is_key_pressed works with mock dict (test compatibility).

        This ensures the method still works with the dict-based mocks used in unit tests.
        """
        # Create a mock keys dict (simulating what we use in unit tests)
        mock_keys = {
            pygame.K_LEFT: True,
            pygame.K_RIGHT: False,
            pygame.K_a: True,
            pygame.K_d: False,
        }

        # Test that it works with dict-style keys
        self.assertTrue(self.game._is_key_pressed(mock_keys, pygame.K_LEFT))
        self.assertFalse(self.game._is_key_pressed(mock_keys, pygame.K_RIGHT))
        self.assertTrue(self.game._is_key_pressed(mock_keys, pygame.K_a))
        self.assertFalse(self.game._is_key_pressed(mock_keys, pygame.K_d))

        # Test key not in dict (should return False, not raise KeyError)
        self.assertFalse(self.game._is_key_pressed(mock_keys, pygame.K_SPACE))

    def test_process_held_keys_with_real_pygame_keys(self):
        """
        Integration test: Verify _process_held_keys works with real pygame keys.

        This ensures the entire key processing pipeline works with ScancodeWrapper.
        """
        # Call _process_held_keys with real pygame keys
        # Should not raise any exceptions even though no keys are pressed
        try:
            self.game._process_held_keys()
            # If we get here, the method handled real pygame keys correctly
            success = True
        except (KeyError, IndexError, TypeError) as e:
            success = False
            self.fail(f"_process_held_keys failed with real pygame keys: {e}")

        self.assertTrue(success)


if __name__ == '__main__':
    unittest.main()
