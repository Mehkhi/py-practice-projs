"""Save slot selection scene for save/load operations."""

import pygame
from typing import Optional, Dict, Callable, Any, TYPE_CHECKING

from .base_menu_scene import BaseMenuScene
from .assets import AssetManager
from .ui import Menu, MessageBox, NineSlicePanel, ConfirmationDialog
from .theme import Colors, Fonts, Layout
from core.save_load import SaveManager, SaveContext
from core.world import World
from core.entities import Player
from core.quests import QuestManager
from core.tutorial_system import TipTrigger

if TYPE_CHECKING:
    from .scene import SceneManager


class SaveSlotScene(BaseMenuScene):
    """Scene for selecting a save slot to save or load."""

    # Color palette
    COLORS = {
        "bg": (20, 25, 40),
        "panel_bg": (35, 40, 60),
        "panel_border": (80, 90, 120),
        "title": (255, 248, 220),
        "slot_active": (255, 255, 255),
        "slot_inactive": (140, 150, 180),
        "slot_empty": (90, 100, 130),
        "highlight": (60, 70, 110),
        "accent": (255, 200, 100),
        "info_label": (160, 170, 200),
        "info_value": (255, 255, 255),
        "warning": (255, 100, 100),
    }

    def __init__(
        self,
        manager: Optional["SceneManager"],
        save_manager: SaveManager,
        mode: str = "save",  # "save" or "load"
        world: Optional[World] = None,
        player: Optional[Player] = None,
        quest_manager: Optional[QuestManager] = None,
        on_complete: Optional[Callable[[int], None]] = None,
        assets: Optional[AssetManager] = None,
        scale: int = 2,
    ):
        """
        Initialize the save slot scene.

        Args:
            manager: Scene manager
            save_manager: SaveManager instance
            mode: "save" to save game, "load" to load game
            world: World instance (required for save mode)
            player: Player instance (required for save mode)
            quest_manager: Optional quest manager
            on_complete: Callback when slot is selected (receives slot number)
            assets: Asset manager
            scale: Display scale
        """
        super().__init__(manager, assets, scale)
        self.save_manager = save_manager
        self.mode = mode
        self.world = world
        self.player = player
        self.quest_manager = quest_manager
        self.on_complete = on_complete

        # Slot selection (1-3)
        self.selected_slot = 0  # Index 0-2 for slots 1-3
        self.num_slots = 3

        # Load slot previews
        self.slot_previews = self._load_previews()

        # UI state
        self.message_box: Optional[MessageBox] = None
        self.showing_message = False
        self.message_timer = 0.0
        self.message_duration = 2.0

        # Confirmation dialog for overwriting saves
        self.confirm_dialog = ConfirmationDialog(
            message="Overwrite existing save?",
            title="Confirm Save",
            on_confirm=self._confirm_save,
            on_cancel=self._cancel_confirm,
            panel=self.panel,
        )

        # Delete confirmation dialog
        self.delete_dialog = ConfirmationDialog(
            message="Delete this save file?",
            title="Confirm Delete",
            on_confirm=self._confirm_delete,
            on_cancel=self._cancel_confirm,
            panel=self.panel,
        )

        # Animation
        self.cursor_anim_time = 0.0

    def _load_previews(self) -> Dict[int, Optional[Dict[str, Any]]]:
        """Load preview data for all slots."""
        previews = {}
        for slot in range(1, self.num_slots + 1):
            previews[slot] = self.save_manager.get_slot_preview(slot)
        return previews

    def _refresh_previews(self) -> None:
        """Refresh preview data after save/delete."""
        self.slot_previews = self._load_previews()

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle input events."""
        # Handle confirmation dialogs first
        if self.confirm_dialog.visible:
            self.confirm_dialog.handle_event(event)
            return

        if self.delete_dialog.visible:
            self.delete_dialog.handle_event(event)
            return

        if self.showing_message:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.showing_message = False
                self.message_box = None
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_slot = (self.selected_slot - 1) % self.num_slots
            elif event.key == pygame.K_DOWN:
                self.selected_slot = (self.selected_slot + 1) % self.num_slots
            elif event.key == pygame.K_RETURN:
                self._select_slot()
            elif event.key == pygame.K_DELETE or event.key == pygame.K_BACKSPACE:
                self._try_delete_slot()
            elif event.key == pygame.K_ESCAPE:
                self.manager.pop()

    def _select_slot(self) -> None:
        """Handle slot selection."""
        slot = self.selected_slot + 1  # Convert to 1-indexed
        preview = self.slot_previews.get(slot)

        if self.mode == "load":
            if preview is None:
                # Can't load empty slot
                self._show_message("No save data in this slot.")
                return
            # Load the game - callback handles scene transition, so don't pop
            if self.on_complete:
                self.on_complete(slot)
            # Note: Don't call pop() here - the on_complete callback replaces
            # this scene with WorldScene via scene_manager.replace()

        elif self.mode == "save":
            if preview is not None:
                # Confirm overwrite
                self.confirm_dialog.show()
            else:
                # Save directly
                self._do_save(slot)

    def _do_save(self, slot: int) -> None:
        """Perform the save operation."""
        if not self.world or not self.player:
            self._show_message("Cannot save: missing game data.")
            return

        try:
            # Build SaveContext from scene manager's registered managers
            context = SaveContext(world=self.world, player=self.player)

            # Register quest_manager if provided directly
            if self.quest_manager:
                context.register_if_saveable(self.quest_manager)

            # Register managers from scene manager (if available)
            if self.manager:
                for attr_name in [
                    'day_night_cycle', 'achievement_manager', 'weather_system',
                    'schedule_manager',
                    'fishing_system', 'puzzle_manager', 'brain_teaser_manager',
                    'gambling_manager', 'arena_manager', 'challenge_dungeon_manager',
                    'secret_boss_manager', 'hint_manager', 'post_game_manager',
                    'tutorial_manager',
                ]:
                    manager_obj = self.manager.get_manager(
                        attr_name, "save_slot_scene_do_save"
                    )
                    if manager_obj is not None:
                        context.register_if_saveable(manager_obj)

            self.save_manager.save_to_slot_with_context(slot, context)
            self._refresh_previews()
            self._show_message(f"Game saved to Slot {slot}!")
            tutorial_manager = self.get_manager_attr(
                "tutorial_manager", "save_slot_scene_do_save"
            )
            if (
                self.world
                and not self.world.get_flag("_tutorial_first_save_shown", False)
                and tutorial_manager
            ):
                self.world.set_flag("_tutorial_first_save_shown", True)
                tutorial_manager.trigger_tip(TipTrigger.FIRST_SAVE)
            if self.on_complete:
                self.on_complete(slot)
        except Exception as e:
            self._show_message(f"Save failed: {e}")

    def _confirm_save(self) -> None:
        """Handle confirmed overwrite."""
        slot = self.selected_slot + 1
        self._do_save(slot)

    def _cancel_confirm(self) -> None:
        """Handle cancelled confirmation."""
        pass  # Dialog already hidden

    def _try_delete_slot(self) -> None:
        """Try to delete the selected slot."""
        slot = self.selected_slot + 1
        preview = self.slot_previews.get(slot)

        if preview is None:
            self._show_message("Slot is already empty.")
            return

        self.delete_dialog.show()

    def _confirm_delete(self) -> None:
        """Handle confirmed delete."""
        slot = self.selected_slot + 1
        if self.save_manager.delete_slot(slot):
            self._refresh_previews()
            self._show_message(f"Slot {slot} deleted.")
        else:
            self._show_message("Failed to delete slot.")

    def _show_message(self, text: str) -> None:
        """Show a temporary message."""
        self.message_box = MessageBox(position=(200, 350), width=240, height=60)
        self.message_box.set_text(text)
        self.showing_message = True
        self.message_timer = 0.0

    def update(self, dt: float) -> None:
        """Update scene state."""
        self.cursor_anim_time += dt

        if self.showing_message:
            self.message_timer += dt
            if self.message_timer >= self.message_duration:
                self.showing_message = False
                self.message_box = None

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the save slot scene."""
        width, height = surface.get_size()
        center_x = width // 2

        # Draw background
        surface.fill(self.COLORS["bg"])

        # Draw title
        title_text = "Save Game" if self.mode == "save" else "Load Game"
        self._draw_title(surface, center_x, 40, title_text)

        # Draw slot panels
        slot_start_y = 90
        slot_height = 100
        slot_spacing = 15

        for i in range(self.num_slots):
            slot_num = i + 1
            y = slot_start_y + i * (slot_height + slot_spacing)
            is_selected = i == self.selected_slot
            preview = self.slot_previews.get(slot_num)
            self._draw_slot_panel(surface, center_x, y, slot_num, preview, is_selected, slot_height)

        # Draw instructions
        self._draw_instructions(surface, center_x, height - 40)

        # Draw message box if showing
        if self.message_box:
            self.message_box.draw(surface, self.assets.get_font("small"), panel=self.panel)

        # Draw confirmation dialogs
        self.confirm_dialog.draw(surface, self.assets.get_font("default"))
        self.delete_dialog.draw(surface, self.assets.get_font("default"))

    def _draw_title(self, surface: pygame.Surface, center_x: int, y: int, text: str) -> None:
        """Draw the scene title."""
        font = self.assets.get_font("large", 32) or pygame.font.Font(None, 32)
        title = font.render(text, True, self.COLORS["title"])
        title_rect = title.get_rect(center=(center_x, y))
        surface.blit(title, title_rect)

    def _draw_slot_panel(
        self,
        surface: pygame.Surface,
        center_x: int,
        y: int,
        slot_num: int,
        preview: Optional[Dict[str, Any]],
        is_selected: bool,
        height: int
    ) -> None:
        """Draw a single save slot panel."""
        panel_width = 400
        panel_x = center_x - panel_width // 2
        panel_rect = pygame.Rect(panel_x, y, panel_width, height)

        # Draw panel background
        bg_color = self.COLORS["highlight"] if is_selected else self.COLORS["panel_bg"]
        pygame.draw.rect(surface, bg_color, panel_rect, border_radius=8)
        pygame.draw.rect(surface, self.COLORS["panel_border"], panel_rect, width=2, border_radius=8)

        # Draw selection cursor
        if is_selected:
            import math
            cursor_offset = 3 * math.sin(self.cursor_anim_time * 5)
            cursor_x = panel_x + 15 + cursor_offset
            cursor_y = y + height // 2
            arrow_points = [
                (cursor_x, cursor_y - 8),
                (cursor_x + 10, cursor_y),
                (cursor_x, cursor_y + 8),
            ]
            pygame.draw.polygon(surface, self.COLORS["accent"], arrow_points)

        # Draw slot content
        content_x = panel_x + 40
        font = self.assets.get_font("default", 20) or pygame.font.Font(None, 20)
        small_font = self.assets.get_font("small", 16) or pygame.font.Font(None, 16)

        if preview:
            # Slot has data - show preview
            # Name and level
            name_text = f"{preview['name']} - Lv.{preview['level']}"
            if preview.get('player_class'):
                class_str = preview['player_class'].title()
                if preview.get('player_subclass'):
                    class_str += f" ({preview['player_subclass'].title()})"
                name_text += f" [{class_str}]"

            name_surface = font.render(name_text, True, self.COLORS["slot_active"])
            surface.blit(name_surface, (content_x, y + 15))

            # Location
            location_label = small_font.render("Location: ", True, self.COLORS["info_label"])
            location_value = small_font.render(preview['location'], True, self.COLORS["info_value"])
            surface.blit(location_label, (content_x, y + 40))
            surface.blit(location_value, (content_x + location_label.get_width(), y + 40))

            # Playtime
            time_label = small_font.render("Play Time: ", True, self.COLORS["info_label"])
            time_value = small_font.render(preview['play_time'], True, self.COLORS["info_value"])
            surface.blit(time_label, (content_x, y + 60))
            surface.blit(time_value, (content_x + time_label.get_width(), y + 60))

            # Timestamp (right side)
            timestamp_text = small_font.render(preview['timestamp'], True, self.COLORS["info_label"])
            timestamp_rect = timestamp_text.get_rect(right=panel_x + panel_width - 20, top=y + 15)
            surface.blit(timestamp_text, timestamp_rect)

            # Slot number indicator
            slot_indicator = small_font.render(f"Slot {slot_num}", True, self.COLORS["info_label"])
            slot_rect = slot_indicator.get_rect(right=panel_x + panel_width - 20, bottom=y + height - 10)
            surface.blit(slot_indicator, slot_rect)
        else:
            # Empty slot
            empty_text = font.render(f"Slot {slot_num} - Empty", True, self.COLORS["slot_empty"])
            empty_rect = empty_text.get_rect(center=(center_x, y + height // 2))
            surface.blit(empty_text, empty_rect)

    def _draw_instructions(self, surface: pygame.Surface, center_x: int, y: int) -> None:
        """Draw control instructions."""
        font = self.assets.get_font("small", 14) or pygame.font.Font(None, 14)

        if self.mode == "save":
            instructions = "↑↓ Select  •  Enter Save  •  Del Delete  •  Esc Back"
        else:
            instructions = "↑↓ Select  •  Enter Load  •  Del Delete  •  Esc Back"

        text = font.render(instructions, True, Colors.TEXT_SECONDARY)
        text_rect = text.get_rect(center=(center_x, y))
        surface.blit(text, text_rect)
