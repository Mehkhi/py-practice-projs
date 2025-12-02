"""Brain teaser puzzle scene for solving standalone puzzles."""

import random
from typing import Any, Callable, List, Optional, TYPE_CHECKING

import pygame

from .base_menu_scene import BaseMenuScene
from .theme import Colors, Fonts, Layout
from core.brain_teasers import (
    BrainTeaser,
    BrainTeaserManager,
    BrainTeaserType,
    LockCombination,
    Riddle,
    SimonSays,
)
from core.tutorial_system import TipTrigger

if TYPE_CHECKING:
    from .scene import SceneManager
    from core.entities import Player
    from core.world import World


class BrainTeaserScene(BaseMenuScene):
    """
    Scene for solving brain teaser puzzles.

    Adapts UI based on teaser type.
    """

    def __init__(
        self,
        manager: Optional["SceneManager"],
        teaser: BrainTeaser,
        brain_teaser_manager: BrainTeaserManager,
        player: Optional["Player"] = None,
        world: Optional["World"] = None,
        on_complete: Optional[Callable] = None,
        assets: Optional[Any] = None,
        scale: int = 2,
    ):
        """Initialize brain teaser scene.

        Args:
            manager: Scene manager for navigation
            teaser: The brain teaser puzzle to solve
            brain_teaser_manager: Manager for brain teasers
            player: Optional player reference for rewards
            world: Optional world reference for flags
            on_complete: Optional callback when puzzle is completed
            assets: Optional asset manager
            scale: Asset scale factor
        """
        super().__init__(manager, assets, scale)
        self.teaser = teaser
        self.btm = brain_teaser_manager
        self.player = player
        self.world = world
        self.on_complete = on_complete

        self.solved = False
        self.failed = False
        self.feedback_message = ""
        self.feedback_timer = 0.0
        self.show_hint = False

        # Type-specific state
        self._init_puzzle_state()
        self._encounter_tip_triggered = False
        self._trigger_first_brain_teaser_tip()

    def _init_puzzle_state(self) -> None:
        """Initialize state based on puzzle type."""
        if self.teaser.teaser_type == BrainTeaserType.RIDDLE:
            self.text_input_active = True
            self.input_text = ""

        elif self.teaser.teaser_type == BrainTeaserType.LOCK_COMBINATION:
            data: LockCombination = self.teaser.data
            self.dial_values = [0] * data.num_dials
            self.selected_dial = 0

        elif self.teaser.teaser_type == BrainTeaserType.SIMON_SAYS:
            simon: SimonSays = self.teaser.data
            self.sequence = self._generate_sequence(simon)
            simon.generated_sequence = list(self.sequence)
            self.player_sequence = []
            self.showing_sequence = True
            self.show_index = 0
            self.show_timer = 0.0
            self.sequence_delay = 0.5  # Time between sequence elements

    def _generate_sequence(self, simon: SimonSays) -> List[str]:
        """Generate random sequence for Simon Says."""
        return random.choices(simon.colors, k=simon.sequence_length)

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle pygame events."""
        if self.solved or self.failed:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_ESCAPE, pygame.K_SPACE):
                    self._exit()
            return

        # Type-specific input handling
        if self.teaser.teaser_type == BrainTeaserType.RIDDLE:
            self._handle_text_input(event)

        elif self.teaser.teaser_type == BrainTeaserType.LOCK_COMBINATION:
            self._handle_combination_input(event)

        elif self.teaser.teaser_type == BrainTeaserType.SIMON_SAYS:
            self._handle_simon_input(event)

    def _handle_text_input(self, event: pygame.event.Event) -> None:
        """Handle text input for riddles and word puzzles."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self._submit_answer(self.input_text)
            elif event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            elif event.key == pygame.K_h:
                self.show_hint = not self.show_hint
            elif event.key == pygame.K_ESCAPE:
                self._exit()
            elif event.unicode.isalnum() or event.unicode == " ":
                self.input_text += event.unicode

    def _handle_combination_input(self, event: pygame.event.Event) -> None:
        """Handle dial input for combination locks."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.selected_dial = max(0, self.selected_dial - 1)
            elif event.key == pygame.K_RIGHT:
                data: LockCombination = self.teaser.data
                self.selected_dial = min(len(self.dial_values) - 1, self.selected_dial + 1)
            elif event.key == pygame.K_UP:
                max_val = self.teaser.data.max_value
                self.dial_values[self.selected_dial] = (
                    self.dial_values[self.selected_dial] + 1
                ) % (max_val + 1)
            elif event.key == pygame.K_DOWN:
                max_val = self.teaser.data.max_value
                self.dial_values[self.selected_dial] = (
                    self.dial_values[self.selected_dial] - 1
                ) % (max_val + 1)
            elif event.key == pygame.K_RETURN:
                self._submit_answer(self.dial_values.copy())
            elif event.key == pygame.K_ESCAPE:
                self._exit()

    def _handle_simon_input(self, event: pygame.event.Event) -> None:
        """Handle input for Simon Says."""
        if self.showing_sequence:
            # Wait for sequence to finish
            return

        if event.type == pygame.KEYDOWN:
            simon: SimonSays = self.teaser.data
            if event.key == pygame.K_1:
                self.player_sequence.append(simon.colors[0])
                self._check_simon_progress()
            elif event.key == pygame.K_2:
                self.player_sequence.append(simon.colors[1])
                self._check_simon_progress()
            elif event.key == pygame.K_3:
                if len(simon.colors) > 2:
                    self.player_sequence.append(simon.colors[2])
                    self._check_simon_progress()
            elif event.key == pygame.K_4:
                if len(simon.colors) > 3:
                    self.player_sequence.append(simon.colors[3])
                    self._check_simon_progress()
            elif event.key == pygame.K_ESCAPE:
                self._exit()

    def _check_simon_progress(self) -> None:
        """Check if Simon Says sequence is correct so far."""
        if len(self.player_sequence) > len(self.sequence):
            # Too many inputs
            self._submit_answer(self.player_sequence)
            return

        # Check if current sequence matches
        for i, color in enumerate(self.player_sequence):
            if i >= len(self.sequence) or color != self.sequence[i]:
                # Wrong sequence
                self._submit_answer(self.player_sequence)
                return

        # Check if complete
        if len(self.player_sequence) == len(self.sequence):
            self._submit_answer(self.player_sequence)

    def _submit_answer(self, answer: Any) -> None:
        """Submit answer and check result."""
        correct, feedback = self.btm.check_answer(self.teaser.teaser_id, answer)

        if correct:
            self.solved = True
            self.btm.mark_solved(self.teaser.teaser_id)
            self.feedback_message = feedback
            self._award_rewards()
        else:
            remaining = self.btm.get_remaining_attempts(self.teaser.teaser_id)
            if remaining == 0:
                self.failed = True
                self.feedback_message = "No attempts remaining. The puzzle remains unsolved."
            else:
                self.feedback_message = feedback
                if remaining > 0:
                    self.feedback_message += f" ({remaining} attempts remaining)"

        self.feedback_timer = 2.0  # Show feedback for 2 seconds

    def _award_rewards(self) -> None:
        """Award rewards from puzzle completion."""
        if not self.teaser.rewards:
            return

        # Award gold
        if "gold" in self.teaser.rewards and self.world:
            current_gold = self.world.get_flag("gold") or 0
            self.world.set_flag("gold", current_gold + self.teaser.rewards["gold"])

        # Award items
        if "items" in self.teaser.rewards and self.player and self.player.inventory:
            for item_id, quantity in self.teaser.rewards["items"].items():
                self.player.inventory.add(item_id, quantity)

        # Set flags
        if "flags" in self.teaser.rewards and self.world:
            for flag in self.teaser.rewards["flags"]:
                self.world.set_flag(flag, True)

        if self.on_complete:
            self.on_complete()

    def _trigger_first_brain_teaser_tip(self) -> None:
        """Trigger tutorial tip when encountering first brain teaser."""
        if self._encounter_tip_triggered:
            return

        already_shown = self.world.get_flag("_tutorial_first_brain_teaser", False) if self.world else False
        if already_shown:
            self._encounter_tip_triggered = True
            return

        tutorial_manager = self.get_manager_attr(
            "tutorial_manager", "_trigger_first_brain_teaser_tip"
        )
        if tutorial_manager:
            if self.world:
                self.world.set_flag("_tutorial_first_brain_teaser", True)
            tutorial_manager.trigger_tip(TipTrigger.FIRST_BRAIN_TEASER)
            self._encounter_tip_triggered = True

    def _exit(self) -> None:
        """Exit the puzzle scene."""
        if self.manager:
            self.manager.pop()

    def update(self, dt: float) -> None:
        """Update scene state."""
        # Update feedback timer
        if self.feedback_timer > 0:
            self.feedback_timer -= dt

        # Update Simon Says sequence display
        if self.teaser.teaser_type == BrainTeaserType.SIMON_SAYS and self.showing_sequence:
            self.show_timer += dt
            if self.show_timer >= self.sequence_delay:
                self.show_timer = 0.0
                self.show_index += 1
                if self.show_index >= len(self.sequence):
                    self.showing_sequence = False
                    self.show_index = 0

    def draw(self, surface: pygame.Surface) -> None:
        """Draw puzzle UI based on type."""
        # Draw overlay
        self.draw_overlay(surface)

        # Draw puzzle-specific UI
        if self.teaser.teaser_type == BrainTeaserType.RIDDLE:
            self._draw_riddle(surface)
        elif self.teaser.teaser_type == BrainTeaserType.LOCK_COMBINATION:
            self._draw_lock_combination(surface)
        elif self.teaser.teaser_type == BrainTeaserType.SIMON_SAYS:
            self._draw_simon_says(surface)

        # Draw feedback message
        if self.feedback_message and self.feedback_timer > 0:
            self._draw_feedback(surface)

        # Draw help text
        self._draw_help_text(surface)

    def _draw_riddle(self, surface: pygame.Surface) -> None:
        """Draw riddle puzzle UI."""
        width, height = surface.get_size()
        font = self.assets.get_font(Fonts.DEFAULT, Fonts.SIZE_BODY)
        title_font = self.assets.get_font(Fonts.DEFAULT, Fonts.SIZE_SUBHEADING)

        if not font or not title_font:
            return

        # Draw title
        title_text = self.teaser.name
        title_surface = title_font.render(title_text, True, Colors.ACCENT)
        title_x = Layout.center_x(title_surface.get_width())
        surface.blit(title_surface, (title_x, 50))

        # Draw panel
        panel_width = 500
        panel_height = 300
        panel_x = Layout.center_x(panel_width)
        panel_y = 120

        if self.panel:
            self.panel.draw(
                surface,
                (panel_x, panel_y, panel_width, panel_height),
                color=Colors.BG_PANEL,
            )

        # Draw question (word-wrapped)
        riddle: Riddle = self.teaser.data
        question_lines = self._word_wrap(riddle.question, panel_width - 40, font)
        y_offset = panel_y + 20
        for line in question_lines:
            text_surface = font.render(line, True, Colors.TEXT_PRIMARY)
            surface.blit(text_surface, (panel_x + 20, y_offset))
            y_offset += font.get_height() + 4

        # Draw input field
        input_y = panel_y + 150
        input_rect = pygame.Rect(panel_x + 20, input_y, panel_width - 40, 30)
        pygame.draw.rect(surface, Colors.BG_DARK, input_rect)
        pygame.draw.rect(surface, Colors.BORDER, input_rect, 2)

        # Draw input text
        input_surface = font.render(self.input_text, True, Colors.TEXT_PRIMARY)
        surface.blit(input_surface, (panel_x + 25, input_y + 5))

        # Draw hint if shown
        if self.show_hint and riddle.hint:
            hint_y = input_y + 40
            hint_text = f"Hint: {riddle.hint}"
            hint_surface = font.render(hint_text, True, Colors.TEXT_SECONDARY)
            surface.blit(hint_surface, (panel_x + 20, hint_y))

        # Draw attempts remaining
        remaining = self.btm.get_remaining_attempts(self.teaser.teaser_id)
        if remaining >= 0:
            attempts_text = f"Attempts: {remaining}"
        else:
            attempts_text = "Attempts: Unlimited"
        attempts_surface = font.render(attempts_text, True, Colors.TEXT_SECONDARY)
        surface.blit(attempts_surface, (panel_x + 20, panel_y + panel_height - 30))

    def _draw_lock_combination(self, surface: pygame.Surface) -> None:
        """Draw combination lock UI."""
        width, height = surface.get_size()
        font = self.assets.get_font(Fonts.DEFAULT, Fonts.SIZE_BODY)
        title_font = self.assets.get_font(Fonts.DEFAULT, Fonts.SIZE_SUBHEADING)

        if not font or not title_font:
            return

        # Draw title
        title_text = self.teaser.name
        title_surface = title_font.render(title_text, True, Colors.ACCENT)
        title_x = Layout.center_x(title_surface.get_width())
        surface.blit(title_surface, (title_x, 50))

        # Draw panel
        panel_width = 500
        panel_height = 350
        panel_x = Layout.center_x(panel_width)
        panel_y = 120

        if self.panel:
            self.panel.draw(
                surface,
                (panel_x, panel_y, panel_width, panel_height),
                color=Colors.BG_PANEL,
            )

        # Draw dials
        lock: LockCombination = self.teaser.data
        dial_spacing = 80
        start_x = panel_x + (panel_width - (lock.num_dials * dial_spacing)) // 2
        dial_y = panel_y + 100

        for i in range(lock.num_dials):
            dial_x = start_x + i * dial_spacing

            # Draw dial background
            dial_rect = pygame.Rect(dial_x - 20, dial_y - 30, 40, 60)
            pygame.draw.rect(surface, Colors.BG_DARK, dial_rect)
            pygame.draw.rect(
                surface,
                Colors.ACCENT if i == self.selected_dial else Colors.BORDER,
                dial_rect,
                2,
            )

            # Draw number
            number_text = str(self.dial_values[i])
            number_surface = font.render(number_text, True, Colors.TEXT_PRIMARY)
            number_x = dial_x - number_surface.get_width() // 2
            surface.blit(number_surface, (number_x, dial_y - 10))

            # Draw arrows
            if i == self.selected_dial:
                # Up arrow
                arrow_points = [
                    (dial_x, dial_y - 25),
                    (dial_x - 5, dial_y - 20),
                    (dial_x + 5, dial_y - 20),
                ]
                pygame.draw.polygon(surface, Colors.ACCENT, arrow_points)

                # Down arrow
                arrow_points = [
                    (dial_x, dial_y + 25),
                    (dial_x - 5, dial_y + 20),
                    (dial_x + 5, dial_y + 20),
                ]
                pygame.draw.polygon(surface, Colors.ACCENT, arrow_points)

        # Draw clues
        if lock.clues:
            clues_y = dial_y + 80
            for i, clue in enumerate(lock.clues):
                clue_text = f"{i + 1}. {clue}"
                clue_surface = font.render(clue_text, True, Colors.TEXT_SECONDARY)
                surface.blit(clue_surface, (panel_x + 20, clues_y + i * 25))

    def _draw_simon_says(self, surface: pygame.Surface) -> None:
        """Draw Simon Says UI."""
        width, height = surface.get_size()
        font = self.assets.get_font(Fonts.DEFAULT, Fonts.SIZE_BODY)
        title_font = self.assets.get_font(Fonts.DEFAULT, Fonts.SIZE_SUBHEADING)

        if not font or not title_font:
            return

        # Draw title
        title_text = self.teaser.name
        title_surface = title_font.render(title_text, True, Colors.ACCENT)
        title_x = Layout.center_x(title_surface.get_width())
        surface.blit(title_surface, (title_x, 50))

        # Draw panel
        panel_width = 400
        panel_height = 300
        panel_x = Layout.center_x(panel_width)
        panel_y = 120

        if self.panel:
            self.panel.draw(
                surface,
                (panel_x, panel_y, panel_width, panel_height),
                color=Colors.BG_PANEL,
            )

        # Draw colored buttons
        simon: SimonSays = self.teaser.data
        button_size = 60
        button_spacing = 20
        start_x = panel_x + (panel_width - (len(simon.colors) * (button_size + button_spacing))) // 2
        button_y = panel_y + 100

        color_map = {
            "red": Colors.FIRE,
            "blue": Colors.WATER,
            "green": Colors.WIND,
            "yellow": Colors.LIGHTNING,
        }

        for i, color_name in enumerate(simon.colors):
            button_x = start_x + i * (button_size + button_spacing)
            button_rect = pygame.Rect(button_x, button_y, button_size, button_size)

            # Get color
            button_color = color_map.get(color_name, Colors.TEXT_SECONDARY)

            # Highlight if showing sequence
            if self.showing_sequence and self.show_index < len(self.sequence):
                if self.sequence[self.show_index] == color_name:
                    # Flash this button
                    flash_alpha = int(255 * (1.0 - (self.show_timer / self.sequence_delay)))
                    flash_surface = pygame.Surface((button_size, button_size), pygame.SRCALPHA)
                    flash_surface.fill((*button_color, flash_alpha))
                    surface.blit(flash_surface, (button_x, button_y))

            pygame.draw.rect(surface, button_color, button_rect)
            pygame.draw.rect(surface, Colors.BORDER, button_rect, 2)

            # Draw number label
            label_text = str(i + 1)
            label_surface = font.render(label_text, True, Colors.WHITE)
            label_x = button_x + (button_size - label_surface.get_width()) // 2
            label_y = button_y + (button_size - label_surface.get_height()) // 2
            surface.blit(label_surface, (label_x, label_y))

        # Draw status
        status_y = button_y + button_size + 20
        if self.showing_sequence:
            status_text = "Watch the sequence..."
        else:
            status_text = f"Repeat the sequence ({len(self.player_sequence)}/{len(self.sequence)})"
        status_surface = font.render(status_text, True, Colors.TEXT_PRIMARY)
        status_x = Layout.center_x(status_surface.get_width())
        surface.blit(status_surface, (status_x, status_y))

    def _draw_feedback(self, surface: pygame.Surface) -> None:
        """Draw feedback message."""
        font = self.assets.get_font(Fonts.DEFAULT, Fonts.SIZE_BODY)
        if not font:
            return

        color = Colors.TEXT_SUCCESS if self.solved else Colors.TEXT_ERROR
        feedback_surface = font.render(self.feedback_message, True, color)
        feedback_x = Layout.center_x(feedback_surface.get_width())
        feedback_y = Layout.SCREEN_HEIGHT - 100
        surface.blit(feedback_surface, (feedback_x, feedback_y))

    def _draw_help_text(self, surface: pygame.Surface) -> None:
        """Draw help text at bottom."""
        font = self.assets.get_font(Fonts.SMALL, Fonts.SIZE_SMALL)
        if not font:
            return

        if self.solved or self.failed:
            help_text = "Enter/Space/ESC: Close"
        elif self.teaser.teaser_type == BrainTeaserType.RIDDLE:
            help_text = "Type answer and press Enter  •  H: Show hint  •  ESC: Exit"
        elif self.teaser.teaser_type == BrainTeaserType.LOCK_COMBINATION:
            help_text = "←/→: Select dial  •  ↑/↓: Change value  •  Enter: Submit  •  ESC: Exit"
        elif self.teaser.teaser_type == BrainTeaserType.SIMON_SAYS:
            help_text = "1-4: Press buttons in sequence  •  ESC: Exit"
        else:
            help_text = "ESC: Exit"

        help_surface = font.render(help_text, True, Colors.TEXT_SECONDARY)
        help_rect = help_surface.get_rect(center=(Layout.SCREEN_WIDTH // 2, Layout.SCREEN_HEIGHT - Layout.SCREEN_MARGIN))
        bg_rect = help_rect.inflate(Layout.PADDING_MD * 2, Layout.PADDING_SM)
        pygame.draw.rect(surface, Colors.BG_DARK, bg_rect, border_radius=Layout.CORNER_RADIUS_SMALL)
        surface.blit(help_surface, help_rect)

    def _word_wrap(self, text: str, max_width: int, font: pygame.font.Font) -> List[str]:
        """Word-wrap text to fit within max_width."""
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            test_surface = font.render(test_line, True, Colors.TEXT_PRIMARY)
            if test_surface.get_width() <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return lines
