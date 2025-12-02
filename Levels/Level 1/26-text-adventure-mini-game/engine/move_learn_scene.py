"""Scene for learning new moves on level-up."""

import pygame
from typing import Optional, List, Callable, Union, TYPE_CHECKING

from .base_menu_scene import BaseMenuScene
from .assets import AssetManager
from .ui import Menu, MessageBox, NineSlicePanel
from core.moves import Move, get_moves_database
from core.entities import MAX_LEARNED_MOVES

if TYPE_CHECKING:
    from .scene import SceneManager
    from core.entities import Player, PartyMember


class MoveLearnScene(BaseMenuScene):
    """
    Scene for learning a new move when leveling up.

    If the character already has 4 moves, they must choose one to forget
    or cancel learning the new move.
    """

    def __init__(
        self,
        manager: Optional["SceneManager"],
        entity: Union["Player", "PartyMember"],
        new_move: Move,
        on_complete: Optional[Callable[[], None]] = None,
        assets: Optional[AssetManager] = None,
        scale: int = 2,
    ):
        super().__init__(manager, assets, scale)
        self.entity = entity
        self.new_move = new_move
        self.on_complete = on_complete
        self.moves_db = get_moves_database()

        # State
        self.state = "prompt"  # "prompt", "choose_forget", "confirm_forget", "done"
        self.selected_forget_index = 0

        # UI
        self.message_box = MessageBox(position=(10, 350), width=620, height=120)

        # Check if we need to forget a move
        learned_moves = getattr(entity, "learned_moves", [])
        if len(learned_moves) < MAX_LEARNED_MOVES:
            # Can learn directly
            self.state = "prompt"
            self._set_prompt_message()
        else:
            # Must choose a move to forget
            self.state = "choose_forget"
            self._set_choose_forget_message()

        # Build forget menu
        self.forget_menu = self._build_forget_menu()

    def _set_prompt_message(self) -> None:
        """Set message for learning prompt."""
        self.message_box.set_text(
            f"{self.entity.name} wants to learn {self.new_move.name}!\n"
            f"Power: {self.new_move.power} | Element: {self.new_move.element}\n"
            f"Press Enter to learn, Escape to skip."
        )

    def _set_choose_forget_message(self) -> None:
        """Set message for choosing which move to forget."""
        self.message_box.set_text(
            f"{self.entity.name} wants to learn {self.new_move.name}!\n"
            f"But {self.entity.name} already knows {MAX_LEARNED_MOVES} moves.\n"
            f"Choose a move to forget, or press Escape to cancel."
        )

    def _build_forget_menu(self) -> Menu:
        """Build menu of current moves to potentially forget."""
        learned_moves = getattr(self.entity, "learned_moves", [])
        menu_items = []

        for move_id in learned_moves:
            move = self.moves_db.get_move(move_id)
            if move:
                menu_items.append(f"{move.name} (Pwr:{move.power})")
            else:
                menu_items.append(move_id)

        # Add option to not learn the new move
        menu_items.append("Don't learn new move")

        return Menu(menu_items, position=(200, 150))

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle input events."""
        if event.type != pygame.KEYDOWN:
            return

        if self.state == "prompt":
            if event.key == pygame.K_RETURN:
                # Learn the move
                self._learn_move()
            elif event.key == pygame.K_ESCAPE:
                # Skip learning
                self._finish()

        elif self.state == "choose_forget":
            if event.key == pygame.K_UP:
                self.forget_menu.move_selection(-1)
            elif event.key == pygame.K_DOWN:
                self.forget_menu.move_selection(1)
            elif event.key == pygame.K_RETURN:
                self._handle_forget_selection()
            elif event.key == pygame.K_ESCAPE:
                # Cancel learning
                self._finish()

        elif self.state == "confirm_forget":
            if event.key == pygame.K_RETURN:
                self._confirm_forget()
            elif event.key == pygame.K_ESCAPE:
                # Go back to selection
                self.state = "choose_forget"
                self._set_choose_forget_message()

        elif self.state == "done":
            if event.key == pygame.K_RETURN:
                self._finish()

    def _handle_forget_selection(self) -> None:
        """Handle selection from forget menu."""
        learned_moves = getattr(self.entity, "learned_moves", [])
        selected_idx = self.forget_menu.selected_index

        if selected_idx >= len(learned_moves):
            # Selected "Don't learn new move"
            self.message_box.set_text(
                f"{self.entity.name} did not learn {self.new_move.name}.\n"
                f"Press Enter to continue."
            )
            self.state = "done"
        else:
            # Selected a move to forget
            old_move_id = learned_moves[selected_idx]
            old_move = self.moves_db.get_move(old_move_id)
            old_move_name = old_move.name if old_move else old_move_id

            self.selected_forget_index = selected_idx
            self.message_box.set_text(
                f"Forget {old_move_name} and learn {self.new_move.name}?\n"
                f"Press Enter to confirm, Escape to go back."
            )
            self.state = "confirm_forget"

    def _confirm_forget(self) -> None:
        """Confirm forgetting the selected move and learn the new one."""
        learned_moves = getattr(self.entity, "learned_moves", [])
        old_move_id = learned_moves[self.selected_forget_index]
        old_move = self.moves_db.get_move(old_move_id)
        old_move_name = old_move.name if old_move else old_move_id

        # Replace the move
        if hasattr(self.entity, "replace_move"):
            self.entity.replace_move(old_move_id, self.new_move.id)
        else:
            # Fallback: manually replace
            learned_moves[self.selected_forget_index] = self.new_move.id

        self.message_box.set_text(
            f"1, 2, and... Poof!\n"
            f"{self.entity.name} forgot {old_move_name}...\n"
            f"And learned {self.new_move.name}!\n"
            f"Press Enter to continue."
        )
        self.state = "done"

    def _learn_move(self) -> None:
        """Learn the new move directly (when there's room)."""
        if hasattr(self.entity, "learn_move"):
            self.entity.learn_move(self.new_move.id)
        else:
            # Fallback: manually add
            learned_moves = getattr(self.entity, "learned_moves", [])
            if self.new_move.id not in learned_moves:
                learned_moves.append(self.new_move.id)

        self.message_box.set_text(
            f"{self.entity.name} learned {self.new_move.name}!\n"
            f"Press Enter to continue."
        )
        self.state = "done"

    def _finish(self) -> None:
        """Finish the scene and return."""
        if self.on_complete:
            self.on_complete()
        self.manager.pop()

    def update(self, dt: float) -> None:
        """Update scene state."""
        pass  # No continuous updates needed

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the move learning scene."""
        # Semi-transparent overlay
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        font = self.assets.get_font()
        small_font = self.assets.get_font("small")

        # Draw title
        title = f"Learning New Move"
        if font:
            title_surface = font.render(title, True, (255, 255, 100))
            title_x = (surface.get_width() - title_surface.get_width()) // 2
            surface.blit(title_surface, (title_x, 30))

        # Draw new move info
        if small_font:
            info_y = 70
            move_info = [
                f"New Move: {self.new_move.name}",
                f"Power: {self.new_move.power} | Accuracy: {self.new_move.accuracy}%",
                f"Element: {self.new_move.element}",
                f"Description: {self.new_move.description}"
            ]
            for line in move_info:
                info_surface = small_font.render(line, True, (200, 200, 255))
                surface.blit(info_surface, (50, info_y))
                info_y += 22

        # Draw forget menu if in choose state
        if self.state in ("choose_forget", "confirm_forget"):
            self.forget_menu.draw(
                surface,
                font,
                theme={"active": (255, 255, 255), "inactive": (150, 150, 150)}
            )

        # Draw message box
        self.message_box.draw(surface, small_font, panel=self.panel)
