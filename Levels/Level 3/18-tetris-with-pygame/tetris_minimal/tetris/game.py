
from __future__ import annotations
import pygame
from typing import Tuple, Optional

from .config import (
    COLUMNS, ROWS, WINDOW_WIDTH, WINDOW_HEIGHT, FPS
)
from .core.board import Board
from .core.bag import Bag
from .core.piece import Piece
from .core.rules import ScoreState, gravity_ms
from .ui.render import draw_background, draw_locked, draw_piece, draw_panel
from .ui.theme import cycle_theme, set_theme, get_theme_name

GRAVITY_EVENT = pygame.USEREVENT + 1
LOCK_DELAY_EVENT = pygame.USEREVENT + 2

# Timing constants for key repeat (in milliseconds)
KEY_REPEAT_DELAY = 150  # Initial delay before repeating starts
KEY_REPEAT_INTERVAL = 50  # Time between repeats once started
LOCK_DELAY_MS = 500  # Time before locking a landed piece (allows lateral movement)

class Game:
    def __init__(self, seed: int | None = None, bag: Bag | None = None):
        """
        Initialize a new Tetris game.

        Args:
            seed: Optional random seed for deterministic piece order.
            bag: Optional Bag instance to inject (for testing). If provided, seed is ignored.
        """
        # Store initial parameters for restart functionality
        self._initial_seed = seed
        # Store bag factory info to recreate fresh bag on restart
        if bag is not None:
            self._initial_bag_seed = getattr(bag, '_seed', None)
        else:
            self._initial_bag_seed = None

        self.board = Board(COLUMNS, ROWS)
        if bag is not None:
            self.bag = bag
        elif seed is not None:
            self.bag = Bag(seed=seed)
        else:
            self.bag = Bag()
        self.score = ScoreState()
        self.current = Piece(self.bag.take())
        self.next_kind = self.bag.peek()
        # Spawn roughly centered, allow negative y so piece enters board
        self.pos: Tuple[int,int] = (COLUMNS // 2 - 2, -2)
        self.paused = False
        self.game_over = False
        # Track when movement keys were first pressed and last moved (for repeat timing)
        self.key_press_times: dict[int, Optional[int]] = {
            pygame.K_LEFT: None,
            pygame.K_RIGHT: None,
            pygame.K_DOWN: None,
        }
        self.key_last_move_times: dict[int, Optional[int]] = {
            pygame.K_LEFT: None,
            pygame.K_RIGHT: None,
            pygame.K_DOWN: None,
        }
        # Track the most recently pressed horizontal direction key (to prevent jitter when both are held)
        self.last_horizontal_key: Optional[int] = None
        # Lock delay tracking: when piece first lands (can't move down)
        self.lock_delay_start: Optional[int] = None
        # Throttle held-key polling to avoid multiple repeats within one frame
        self._last_held_poll_ms: Optional[int] = None
        # Theme toast display timer (show theme name for 1.5 seconds after change)
        self.theme_toast_end_time: Optional[int] = None
        # Animation timers
        self.spawn_start_ms: Optional[int] = None
        self.lock_start_ms: Optional[int] = None
        self.line_clear_start_ms: Optional[int] = None
        # Initialize spawn timer after first piece is created
        if pygame.get_init():
            self.spawn_start_ms = pygame.time.get_ticks()
        self._set_gravity_timer()

    def _set_gravity_timer(self):
        pygame.time.set_timer(GRAVITY_EVENT, gravity_ms(self.score.level))

    def _can_move(self, dx: int, dy: int) -> bool:
        nx, ny = self.pos[0] + dx, self.pos[1] + dy
        return not self.board.collides(self.current.blocks(), (nx, ny))

    def _try_rotate(self, delta: int) -> None:
        rotated = self.current.rotated(delta)
        # Simple wall-kick: try nudges
        for dx in [0, -1, 1, -2, 2]:
            new_pos = (self.pos[0] + dx, self.pos[1])
            if not self.board.collides(rotated.blocks(), new_pos):
                self.current = rotated
                self.pos = new_pos
                # Reset lock delay if piece moved (rotation with wall-kick)
                self._reset_lock_delay()
                # Re-check grounding and re-arm lock delay if still on floor
                self._check_and_start_lock_delay()
                return
        # else: keep as is

    def _new_piece(self):
        self.current = Piece(self.bag.take())
        self.next_kind = self.bag.peek()
        self.pos = (COLUMNS // 2 - 2, -2)
        self.spawn_start_ms = pygame.time.get_ticks()  # Track spawn time for animation
        if self.board.collides(self.current.blocks(), self.pos):
            self.game_over = True

    def _reset_lock_delay(self):
        """Reset the lock delay timer (called when piece moves laterally or rotates)."""
        self.lock_delay_start = None
        pygame.time.set_timer(LOCK_DELAY_EVENT, 0)  # Cancel any pending lock delay event

    def _check_and_start_lock_delay(self):
        """Check if piece can't move down and start lock delay if needed."""
        if not self._can_move(0, 1):
            # Piece can't move down - start lock delay if not already started
            if self.lock_delay_start is None:
                self.lock_delay_start = pygame.time.get_ticks()
                pygame.time.set_timer(LOCK_DELAY_EVENT, LOCK_DELAY_MS)
        else:
            # Piece can still move down - reset lock delay
            self._reset_lock_delay()

    def _lock_current(self):
        cleared = self.board.lock_piece(self.current.kind, self.current.blocks(), self.pos)
        self.lock_start_ms = pygame.time.get_ticks()  # Track lock time for animation
        if cleared:
            self.score.on_clear(cleared)
            self.line_clear_start_ms = pygame.time.get_ticks()  # Track line clear time for animation
            # update gravity if level changed
            self._set_gravity_timer()
        self._reset_lock_delay()  # Clear lock delay when locking
        self._new_piece()

    def _hard_drop(self):
        d = self.board.drop_distance(self.current.blocks(), self.pos)
        self.pos = (self.pos[0], self.pos[1] + d)
        self.score.on_hard_drop(d)
        self._lock_current()

    def _handle_movement_key(self, key: int, dx: int, dy: int, is_down: bool = False):
        """Handle movement for left/right/down keys with repeat logic."""
        if self.game_over or self.paused:
            return

        moved = False
        if key == pygame.K_DOWN:
            # Soft-drop: accelerate descent but don't lock immediately
            if self._can_move(0, 1):
                self.pos = (self.pos[0], self.pos[1] + 1)
                self.score.on_soft_drop()
                moved = True
                # Check if piece can still move after soft-drop
                self._check_and_start_lock_delay()
            else:
                # Can't move down - start lock delay instead of locking immediately
                self._check_and_start_lock_delay()
        elif key == pygame.K_LEFT and self._can_move(-1, 0):
            self.pos = (self.pos[0] - 1, self.pos[1])
            moved = True
            # Reset lock delay on lateral movement
            self._reset_lock_delay()
            # Re-check grounding and re-arm lock delay if still on floor
            self._check_and_start_lock_delay()
        elif key == pygame.K_RIGHT and self._can_move(1, 0):
            self.pos = (self.pos[0] + 1, self.pos[1])
            moved = True
            # Reset lock delay on lateral movement
            self._reset_lock_delay()
            # Re-check grounding and re-arm lock delay if still on floor
            self._check_and_start_lock_delay()

        # Record when movement actually happened
        if moved:
            self.key_last_move_times[key] = pygame.time.get_ticks()

    def _is_key_pressed(self, keys, key_code):
        """
        Safely check if a key is pressed, handling both real ScancodeWrapper
        and test dict mocks.

        Args:
            keys: Result from pygame.key.get_pressed()
            key_code: The pygame key constant to check

        Returns:
            bool: True if key is pressed, False otherwise
        """
        try:
            return keys[key_code]
        except (KeyError, IndexError):
            return False

    def poll_held_keys(self):
        """
        Public method to poll held keys and apply repeat movement.

        This method checks for held movement keys and applies DAS/ARR repeat logic.
        Should be called once per frame (typically from tick()).
        """
        self._process_held_keys()

    def _process_held_keys(self):
        """Check for held movement keys and apply repeat movement."""
        if self.game_over or self.paused:
            # Don't process movement while paused/game over, but preserve timestamps
            # so held keys continue immediately when resuming
            return

        keys = pygame.key.get_pressed()
        current_time = pygame.time.get_ticks()

        # Handle horizontal keys first - prioritize most recent direction
        left_pressed = self._is_key_pressed(keys, pygame.K_LEFT) or self._is_key_pressed(keys, pygame.K_a)
        right_pressed = self._is_key_pressed(keys, pygame.K_RIGHT) or self._is_key_pressed(keys, pygame.K_d)

        # Determine which horizontal key to process (if any)
        horizontal_key_to_process = None
        if left_pressed and right_pressed:
            # Both keys held - only process the most recently pressed one
            if self.last_horizontal_key in [pygame.K_LEFT, pygame.K_RIGHT]:
                horizontal_key_to_process = self.last_horizontal_key
            else:
                # Fallback: prefer Left when both are held and no preference is set
                horizontal_key_to_process = pygame.K_LEFT
        elif left_pressed:
            horizontal_key_to_process = pygame.K_LEFT
        elif right_pressed:
            horizontal_key_to_process = pygame.K_RIGHT

        # Process horizontal movement (if applicable)
        if horizontal_key_to_process is not None:
            key = horizontal_key_to_process
            if self.key_press_times[key] is None:
                # Just started pressing - record time but don't move yet
                # (movement already handled by KEYDOWN event)
                self.key_press_times[key] = current_time
            else:
                # Key has been held - check if it's time to repeat
                time_held = current_time - self.key_press_times[key]

                # After initial delay, check if enough time has passed since last move
                if time_held >= KEY_REPEAT_DELAY:
                    last_move_time = self.key_last_move_times[key]
                    if last_move_time is None or (current_time - last_move_time) >= KEY_REPEAT_INTERVAL:
                        dx = -1 if key == pygame.K_LEFT else 1
                        self._handle_movement_key(key, dx, 0)
        else:
            # Neither horizontal key is pressed, or both are pressed but no last_horizontal_key set
            # Clear timers for horizontal keys
            if not left_pressed:
                self.key_press_times[pygame.K_LEFT] = None
                self.key_last_move_times[pygame.K_LEFT] = None
            if not right_pressed:
                self.key_press_times[pygame.K_RIGHT] = None
                self.key_last_move_times[pygame.K_RIGHT] = None

        # Process DOWN key (independent of horizontal keys)
        if self._is_key_pressed(keys, pygame.K_DOWN) or self._is_key_pressed(keys, pygame.K_s):
            key = pygame.K_DOWN
            if self.key_press_times[key] is None:
                # Just started pressing - record time but don't move yet
                # (movement already handled by KEYDOWN event)
                self.key_press_times[key] = current_time
            else:
                # Key has been held - check if it's time to repeat
                time_held = current_time - self.key_press_times[key]

                # After initial delay, check if enough time has passed since last move
                if time_held >= KEY_REPEAT_DELAY:
                    last_move_time = self.key_last_move_times[key]
                    if last_move_time is None or (current_time - last_move_time) >= KEY_REPEAT_INTERVAL:
                        self._handle_movement_key(key, 0, 1, is_down=True)
        else:
            # DOWN key is not pressed - clear the timers
            self.key_press_times[pygame.K_DOWN] = None
            self.key_last_move_times[pygame.K_DOWN] = None

    def tick(self):
        """
        Per-frame update method. Polls held keys for repeat movement.

        Should be called once per frame in the main game loop.
        This ensures DAS/ARR behavior works correctly regardless of event frequency.
        """
        self.poll_held_keys()

    def handle_event(self, event: pygame.event.Event):
        """
        Handle a single pygame event.

        Processes keyboard input, gravity events, and lock delay events.
        Also performs throttled held-key polling to ensure repeat behavior
        works even when frontends only forward events.
        """
        # Handle pause toggle first to freeze the board immediately
        # This prevents held-key polling from causing an extra move when pausing
        if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
            # Toggle pause state
            self.paused = not self.paused
            if self.paused:
                # Pausing: stop gravity timer and lock delay timer
                pygame.time.set_timer(GRAVITY_EVENT, 0)
                pygame.time.set_timer(LOCK_DELAY_EVENT, 0)
                # Drain any pending timer events from the queue
                pygame.event.clear([GRAVITY_EVENT, LOCK_DELAY_EVENT])
                # Clear lock_delay_start to prevent stale state on resume
                self.lock_delay_start = None
            else:
                # Unpausing: clear any pending timer events and re-arm timers
                pygame.event.clear([GRAVITY_EVENT, LOCK_DELAY_EVENT])
                # Re-arm gravity timer based on current level
                self._set_gravity_timer()
                # Restart lock delay timer if piece is still touching down
                self._check_and_start_lock_delay()
            # Return early after pause toggle to prevent further processing
            return

        # Throttled held-key poll: only poll if enough time has passed since last poll
        # This prevents multiple repeats within one frame when many events arrive
        # Skip polling if paused to avoid unnecessary work
        if not self.paused:
            current_time = pygame.time.get_ticks()
            frame_time_ms = 1000 // FPS
            if self._last_held_poll_ms is None or (current_time - self._last_held_poll_ms) >= frame_time_ms:
                self.poll_held_keys()
                self._last_held_poll_ms = current_time

        if event.type == pygame.KEYDOWN:
            if self.game_over:
                if event.key == pygame.K_r:
                    # Clear any pending timer events before restart
                    pygame.time.set_timer(GRAVITY_EVENT, 0)
                    pygame.time.set_timer(LOCK_DELAY_EVENT, 0)
                    pygame.event.clear([GRAVITY_EVENT, LOCK_DELAY_EVENT])
                    # Recreate fresh bag for deterministic restart
                    restart_bag = Bag(seed=self._initial_bag_seed) if self._initial_bag_seed is not None else None
                    self.__init__(self._initial_seed, restart_bag)
                return
            if self.paused:
                return
            # Handle immediate movement on key press
            if event.key == pygame.K_LEFT:
                self.key_press_times[pygame.K_LEFT] = pygame.time.get_ticks()
                self.last_horizontal_key = pygame.K_LEFT  # Track most recent horizontal key
                self._handle_movement_key(pygame.K_LEFT, -1, 0)
            elif event.key == pygame.K_RIGHT:
                self.key_press_times[pygame.K_RIGHT] = pygame.time.get_ticks()
                self.last_horizontal_key = pygame.K_RIGHT  # Track most recent horizontal key
                self._handle_movement_key(pygame.K_RIGHT, 1, 0)
            elif event.key == pygame.K_DOWN:
                self.key_press_times[pygame.K_DOWN] = pygame.time.get_ticks()
                self._handle_movement_key(pygame.K_DOWN, 0, 1, is_down=True)
            elif event.key == pygame.K_UP or event.key == pygame.K_x or event.key == pygame.K_w:
                self._try_rotate(+1)
            elif event.key == pygame.K_z:
                self._try_rotate(-1)
            # WASD movement support
            elif event.key == pygame.K_a:
                self.key_press_times[pygame.K_LEFT] = pygame.time.get_ticks()
                self.last_horizontal_key = pygame.K_LEFT  # Track most recent horizontal key
                self._handle_movement_key(pygame.K_LEFT, -1, 0)
            elif event.key == pygame.K_d:
                self.key_press_times[pygame.K_RIGHT] = pygame.time.get_ticks()
                self.last_horizontal_key = pygame.K_RIGHT  # Track most recent horizontal key
                self._handle_movement_key(pygame.K_RIGHT, 1, 0)
            elif event.key == pygame.K_s:
                self.key_press_times[pygame.K_DOWN] = pygame.time.get_ticks()
                self._handle_movement_key(pygame.K_DOWN, 0, 1, is_down=True)
            elif event.key == pygame.K_SPACE:
                self._hard_drop()
            elif event.key == pygame.K_r:
                # Clear any pending timer events before restart
                pygame.time.set_timer(GRAVITY_EVENT, 0)
                pygame.time.set_timer(LOCK_DELAY_EVENT, 0)
                pygame.event.clear([GRAVITY_EVENT, LOCK_DELAY_EVENT])
                # Recreate fresh bag for deterministic restart
                restart_bag = Bag(seed=self._initial_bag_seed) if self._initial_bag_seed is not None else None
                self.__init__(self._initial_seed, restart_bag)
            elif event.key == pygame.K_t:
                # Theme cycling: T for forward, Shift+T for backward
                try:
                    keys = pygame.key.get_pressed()
                    direction = -1 if (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) else 1
                except:
                    direction = 1
                cycle_theme(direction)
                self.theme_toast_end_time = pygame.time.get_ticks() + 1500  # Show for 1.5 seconds
            elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
                # Direct theme selection: 1-4 for themes in order
                theme_index = event.key - pygame.K_1
                theme_names = ["NES", "Modern", "Neon", "Minimal"]
                if theme_index < len(theme_names):
                    if set_theme(theme_names[theme_index]):
                        self.theme_toast_end_time = pygame.time.get_ticks() + 1500
        elif event.type == pygame.KEYUP:
            # Clear the timers when key is released
            if event.key in self.key_press_times:
                self.key_press_times[event.key] = None
                self.key_last_move_times[event.key] = None

            # Handle horizontal key release - switch to other key if still held
            keys = pygame.key.get_pressed()
            if event.key in [pygame.K_LEFT, pygame.K_a]:
                # LEFT/A released - if RIGHT/D is still held, make it the active key
                if self._is_key_pressed(keys, pygame.K_RIGHT) or self._is_key_pressed(keys, pygame.K_d):
                    self.last_horizontal_key = pygame.K_RIGHT
                else:
                    self.last_horizontal_key = None
            elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                # RIGHT/D released - if LEFT/A is still held, make it the active key
                if self._is_key_pressed(keys, pygame.K_LEFT) or self._is_key_pressed(keys, pygame.K_a):
                    self.last_horizontal_key = pygame.K_LEFT
                else:
                    self.last_horizontal_key = None
        elif event.type == GRAVITY_EVENT:
            # Only process gravity events when not paused and not game over
            if self.paused or self.game_over:
                return
            if self._can_move(0, 1):
                self.pos = (self.pos[0], self.pos[1] + 1)
                # Reset lock delay since piece moved down
                self._reset_lock_delay()
            else:
                # Can't move down - start lock delay instead of locking immediately
                self._check_and_start_lock_delay()
        elif event.type == LOCK_DELAY_EVENT:
            # Only process lock delay events when not paused and not game over
            if self.paused or self.game_over:
                return
            # Verify this event is still valid - check if we have an active lock delay
            if self.lock_delay_start is None:
                return
            # Verify timing - only process if enough time has actually passed
            current_time = pygame.time.get_ticks()
            if current_time - self.lock_delay_start < LOCK_DELAY_MS:
                return  # Event fired too early, ignore
            # Lock delay expired - check if piece still can't move down
            if not self._can_move(0, 1):
                # Still can't move - lock the piece
                self._lock_current()
            else:
                # Piece can move again (shouldn't happen, but reset just in case)
                self._reset_lock_delay()

    def update(self, event: pygame.event.Event | None):
        """
        Backwards-compatible wrapper for handle_event and tick.

        - If event is None, calls tick() (per-frame update)
        - If event is provided, calls handle_event(event) and then tick() to ensure
          continuous key polling for DAS/ARR behavior

        Note: This method is maintained for backwards compatibility.
        New code should use handle_event() and tick() directly.
        """
        if event is None:
            return self.tick()
        self.handle_event(event)
        # Always poll held keys to ensure DAS/ARR works even when called per-event
        self.tick()
        return None

    def draw(self, screen: pygame.Surface, font: pygame.font.Font):
        current_time = pygame.time.get_ticks()

        # Calculate spawn animation inset (0-6px over 150ms)
        spawn_inset = 0
        if self.spawn_start_ms:
            elapsed = current_time - self.spawn_start_ms
            if elapsed < 150:
                # Animate from 6px to 1px inset
                progress = elapsed / 150.0
                spawn_inset = int(6 * (1 - progress) + 1 * progress)

        # Calculate lock animation (darken blocks for 120ms)
        lock_alpha = 0
        if self.lock_start_ms:
            elapsed = current_time - self.lock_start_ms
            if elapsed < 120:
                # Fade from 0.3 to 0 over 120ms
                progress = elapsed / 120.0
                lock_alpha = int(255 * 0.3 * (1 - progress))

        # Calculate line clear flash (flash grid for 120ms)
        line_clear_flash = False
        if self.line_clear_start_ms:
            elapsed = current_time - self.line_clear_start_ms
            if elapsed < 120:
                line_clear_flash = True

        draw_background(screen, line_clear_flash=line_clear_flash)
        # ghost
        ghost_d = self.board.drop_distance(self.current.blocks(), self.pos)
        draw_locked(screen, self.board.grid, lock_alpha=lock_alpha)
        draw_piece(screen, self.current.kind, self.current.blocks(), self.pos, ghost_distance=ghost_d, inset_px=spawn_inset)
        draw_panel(screen, font, self.score.score, self.score.level, self.score.lines, self.next_kind)
        if self.paused:
            _draw_center_text(screen, font, "PAUSED (P to resume)")
        if self.game_over:
            _draw_center_text(screen, font, "GAME OVER (R to restart)")
        # Show theme toast if active
        if self.theme_toast_end_time and pygame.time.get_ticks() < self.theme_toast_end_time:
            theme_name = get_theme_name()
            _draw_theme_toast(screen, font, f"Theme: {theme_name}")
        elif self.theme_toast_end_time:
            # Clear toast timer when expired
            self.theme_toast_end_time = None

def _draw_center_text(screen: pygame.Surface, font: pygame.font.Font, message: str) -> None:
    text = font.render(message, True, (240, 240, 240))
    rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
    screen.blit(text, rect)

def _draw_theme_toast(screen: pygame.Surface, font: pygame.font.Font, message: str) -> None:
    """Draw theme name toast at top center of screen."""
    from .ui.theme import get_theme
    theme = get_theme()
    text = font.render(message, True, theme.text)
    rect = text.get_rect(center=(WINDOW_WIDTH // 2, 30))
    # Draw semi-transparent background
    bg_rect = pygame.Rect(rect.x - 10, rect.y - 5, rect.width + 20, rect.height + 10)
    bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
    bg_surface.set_alpha(200)
    bg_surface.fill(theme.bg)
    screen.blit(bg_surface, bg_rect)
    screen.blit(text, rect)

def main():
    pygame.init()
    pygame.display.set_caption("Tetris Minimal")
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 20) or pygame.font.Font(None, 20)

    game = Game()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            else:
                game.handle_event(event)
        # Process held keys each frame for repeat movement
        game.tick()
        game.draw(screen, font)
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()
