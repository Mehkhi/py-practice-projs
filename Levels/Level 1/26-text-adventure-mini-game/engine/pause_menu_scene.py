"""Pause menu scene for overworld pause functionality."""

import pygame
from typing import Dict, Optional, TYPE_CHECKING

from .base_menu_scene import BaseMenuScene
from .assets import AssetManager
from .ui import Menu, MessageBox, NineSlicePanel, ConfirmationDialog, draw_contextual_help
from .theme import Colors, Fonts, Layout
from core.world import World
from core.entities import Player
from core.save_load import SaveManager
from core.items import Item
from core.quests import QuestManager
from core.crafting import CraftingSystem

if TYPE_CHECKING:
    from .scene import SceneManager


class PauseMenuScene(BaseMenuScene):
    """Pause menu overlay for the overworld."""

    # Layout constants for proper centering
    MENU_WIDTH = 180
    MENU_PADDING = 20
    TITLE_Y = 80

    def __init__(
        self,
        manager: Optional["SceneManager"],
        world: World,
        player: Player,
        save_manager: SaveManager,
        assets: Optional[AssetManager] = None,
        scale: int = 2,
        save_slot: int = 1,
        items_db: Optional[Dict[str, Item]] = None,
        quest_manager: Optional[QuestManager] = None,
    ):
        super().__init__(manager, assets, scale)
        self.world = world
        self.player = player
        self.save_manager = save_manager
        self.save_slot = max(1, int(save_slot))
        self.items_db = items_db or {}
        self.quest_manager = quest_manager
        self.overlay: Optional[pygame.Surface] = None

        # UI components - center menu horizontally with proper spacing
        # Use compact mode for tighter menu item spacing
        self.menu = Menu(

            ["Resume", "Journal", "World Map", "Bestiary", "Boss Dossier", "Achievements", "Statistics", "Completion", "Party", "Skills", "Equipment", "Inventory", "Crafting", "Save Game", "Quit"],
            position=(Layout.center_x(self.MENU_WIDTH) + 20, 130),
            compact=True
        )

        # Crafting system
        self.crafting_system: Optional[CraftingSystem] = None
        self.message_box: Optional[MessageBox] = None

        # State
        self.showing_save_message = False
        self.save_message_timer = 0.0
        self.save_message_duration = 2.0  # Show message for 2 seconds

        # Confirmation dialog for quit
        self.quit_dialog = ConfirmationDialog(
            message="Are you sure you want to quit? Unsaved progress will be lost.",
            title="Quit Game",
            on_confirm=self._confirm_quit,
            on_cancel=self._cancel_quit,
        )

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle input events."""
        # Handle quit confirmation dialog first
        if self.quit_dialog.visible:
            self.quit_dialog.handle_event(event)
            return

        if self.showing_save_message:
            # Wait for message to disappear or allow Enter to dismiss
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.showing_save_message = False
                self.message_box = None
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.menu.move_selection(-1)
            elif event.key == pygame.K_DOWN:
                self.menu.move_selection(1)
            elif event.key == pygame.K_RETURN:
                self._handle_menu_selection()
            elif event.key == pygame.K_ESCAPE:
                # ESC also resumes (closes pause menu)
                self.manager.pop()

    def _handle_menu_selection(self) -> None:
        """Handle menu option selection."""
        selection = self.menu.get_selected()
        if not selection:
            return

        if selection == "Resume":
            self.manager.pop()
        elif selection == "Journal":
            self._open_journal()
        elif selection == "World Map":
            self._open_world_map()
        elif selection == "Bestiary":
            self._open_bestiary()
        elif selection == "Boss Dossier":
            self._open_boss_dossier()
        elif selection == "Achievements":
            self._open_achievements()
        elif selection == "Statistics":
            self._open_statistics()
        elif selection == "Completion":
            self._open_completion()
        elif selection == "Party":
            self._open_party_menu()
        elif selection == "Skills":
            self._open_skill_tree()
        elif selection == "Equipment":
            self._open_equipment()
        elif selection == "Inventory":
            self._open_inventory()
        elif selection == "Crafting":
            self._open_crafting()
        elif selection == "Save Game":
            self._save_game()
        elif selection == "Quit":
            self._quit_game()

    def _open_bestiary(self) -> None:
        """Open the enemy bestiary/compendium."""
        from .bestiary_scene import BestiaryScene

        if not hasattr(self.player, 'bestiary') or not self.player.bestiary:
            # Show message if no bestiary
            self.message_box = MessageBox(position=(200, 300), width=240, height=60)
            self.message_box.set_text("No bestiary available.")
            self.showing_save_message = True
            self.save_message_timer = 0.0
            return

        bestiary_scene = BestiaryScene(
            self.manager,
            self.player.bestiary,
            assets=self.assets,
            scale=self.scale,
        )
        self.manager.push(bestiary_scene)

    def _open_world_map(self) -> None:
        """Open the world map overview."""
        from .world_map_scene import WorldMapScene

        world_map_scene = WorldMapScene(
            self.manager,
            self.world,
            assets=self.assets,
            scale=self.scale,
        )
        self.manager.push(world_map_scene)

    def _open_boss_dossier(self) -> None:
        """Open the boss dossier."""
        from .boss_dossier_scene import BossDossierScene

        # Get SecretBossManager and HintManager from scene manager or world
        secret_boss_manager = self.get_manager_attr(
            "secret_boss_manager", "_open_boss_dossier"
        )
        hint_manager = self.get_manager_attr("hint_manager", "_open_boss_dossier")

        if not secret_boss_manager or not hint_manager:
            # Show message if managers not available
            self.message_box = MessageBox(position=(200, 300), width=240, height=60)
            self.message_box.set_text("Boss dossier not available.")
            self.showing_save_message = True
            self.save_message_timer = 0.0
            return

        dossier_scene = BossDossierScene(
            self.manager,
            secret_boss_manager,
            hint_manager,
            assets=self.assets,
            scale=self.scale,
        )
        self.manager.push(dossier_scene)

    def _open_achievements(self) -> None:
        """Open the achievements list."""
        from .achievement_scene import AchievementScene

        achievement_manager = self.get_manager_attr(
            "achievement_manager", "_open_achievements"
        )
        if not achievement_manager:
            # Show message if no achievement manager
            self.message_box = MessageBox(position=(200, 300), width=240, height=60)
            self.message_box.set_text("No achievements available.")
            self.showing_save_message = True
            self.save_message_timer = 0.0
            return

        achievement_scene = AchievementScene(
            self.manager,
            achievement_manager,
            assets=self.assets,
            scale=self.scale,
        )
        self.manager.push(achievement_scene)

    def _open_statistics(self) -> None:
        """Open the statistics screen."""
        from .statistics_scene import StatisticsScene

        statistics_scene = StatisticsScene(
            self.manager,
            assets=self.assets,
            scale=self.scale,
        )
        self.manager.push(statistics_scene)

    def _open_completion(self) -> None:
        """Open the completion tracking screen."""
        from .completion_scene import CompletionScene

        completion_scene = CompletionScene(
            self.manager,
            assets=self.assets,
            scale=self.scale,
        )
        self.manager.push(completion_scene)

    def _open_journal(self) -> None:
        """Open the quest journal."""
        from .quest_journal_scene import QuestJournalScene

        if not self.quest_manager:
            # Show message if no quest manager
            self.message_box = MessageBox(position=(200, 300), width=240, height=60)
            self.message_box.set_text("No quests available.")
            self.showing_save_message = True
            self.save_message_timer = 0.0
            return

        journal_scene = QuestJournalScene(
            self.manager,
            self.quest_manager,
            assets=self.assets,
            scale=self.scale,
        )
        self.manager.push(journal_scene)

    def _open_party_menu(self) -> None:
        """Open the party management screen."""
        from .party_menu_scene import PartyMenuScene

        party_scene = PartyMenuScene(
            self.manager,
            self.world,
            self.player,
            items_db=self.items_db,
            assets=self.assets,
            scale=self.scale,
        )
        self.manager.push(party_scene)

    def _open_skill_tree(self) -> None:
        """Open the skill tree screen."""
        from .skill_tree_scene import SkillTreeScene

        skill_tree_scene = SkillTreeScene(
            self.manager,
            self.player,
            assets=self.assets,
            scale=self.scale,
        )
        self.manager.push(skill_tree_scene)

    def _open_equipment(self) -> None:
        """Open the equipment management screen."""
        from .equipment_scene import EquipmentScene

        equipment_scene = EquipmentScene(
            self.manager,
            self.world,
            self.player,
            self.items_db,
            assets=self.assets,
            scale=self.scale,
        )
        self.manager.push(equipment_scene)

    def _open_inventory(self) -> None:
        """Open the inventory management screen."""
        from .inventory_scene import InventoryScene

        inventory_scene = InventoryScene(
            self.manager,
            self.world,
            self.player,
            self.items_db,
            assets=self.assets,
            scale=self.scale,
        )
        self.manager.push(inventory_scene)

    def _open_crafting(self) -> None:
        """Open the crafting screen."""
        from .crafting_scene import CraftingScene

        # Lazy-load crafting system
        if not self.crafting_system:
            self.crafting_system = CraftingSystem()

        crafting_scene = CraftingScene(
            self.manager,
            self.world,
            self.player,
            self.items_db,
            crafting_system=self.crafting_system,
            assets=self.assets,
            scale=self.scale,
        )
        self.manager.push(crafting_scene)

    def _save_game(self) -> None:
        """Open the save slot selection scene."""
        # Guard: Check if save_manager is available
        if self.save_manager is None:
            # Show friendly message using existing MessageBox flow
            self.message_box = MessageBox(position=(200, 300), width=240, height=60)
            self.message_box.set_text("No save manager available.")
            self.showing_save_message = True
            self.save_message_timer = 0.0
            return

        from .save_slot_scene import SaveSlotScene

        def on_save_complete(slot: int) -> None:
            """Callback when save is complete."""
            self.save_slot = slot  # Update current save slot

        save_scene = SaveSlotScene(
            self.manager,
            self.save_manager,
            mode="save",
            world=self.world,
            player=self.player,
            quest_manager=self.quest_manager,
            on_complete=on_save_complete,
            assets=self.assets,
            scale=self.scale,
        )
        self.manager.push(save_scene)

    def _quit_game(self) -> None:
        """Show quit confirmation dialog."""
        self.quit_dialog.show()

    def _confirm_quit(self) -> None:
        """Handle confirmed quit."""
        if self.manager:
            self.manager.quit_requested = True
        self.manager.pop()

    def _cancel_quit(self) -> None:
        """Handle cancelled quit."""
        pass  # Dialog already hidden, just return to menu

    def update(self, dt: float) -> None:
        """Update scene state."""
        # Drive menu animations with dt
        self.menu.update(dt)

        if self.showing_save_message:
            self.save_message_timer += dt
            if self.save_message_timer >= self.save_message_duration:
                self.showing_save_message = False
                self.message_box = None
            elif self.message_box:
                self.message_box.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the pause menu."""
        width, height = surface.get_size()

        # Draw semi-transparent overlay
        if not self.overlay or self.overlay.get_size() != (width, height):
            self.overlay = pygame.Surface((width, height), pygame.SRCALPHA)
            self.overlay.fill(Colors.BG_OVERLAY)
        surface.blit(self.overlay, (0, 0))

        # Calculate menu panel dimensions - account for compact mode
        num_items = len(self.menu.options)
        item_height = Layout.MENU_ITEM_HEIGHT_COMPACT  # Using compact mode
        menu_height = num_items * item_height + self.MENU_PADDING * 2

        # Center the menu panel horizontally
        menu_x = Layout.center_x(self.MENU_WIDTH, width)
        menu_y = 115

        # Draw menu background panel with rounded corners
        menu_bg_rect = pygame.Rect(menu_x, menu_y, self.MENU_WIDTH, menu_height)
        if self.panel:
            self.panel.draw(surface, menu_bg_rect)
        else:
            pygame.draw.rect(surface, Colors.BG_PANEL, menu_bg_rect, border_radius=Layout.CORNER_RADIUS)
            pygame.draw.rect(surface, Colors.BORDER, menu_bg_rect, Layout.BORDER_WIDTH, border_radius=Layout.CORNER_RADIUS)

        # Draw menu
        font = self.assets.get_font(Fonts.DEFAULT, Fonts.SIZE_BODY)
        self.menu.draw(
            surface,
            font,
            theme={
                "active": Colors.TEXT_HIGHLIGHT,
                "inactive": Colors.TEXT_SECONDARY,
                "disabled": Colors.TEXT_DISABLED
            }
        )

        # Draw title with shadow
        title_font = self.assets.get_font(Fonts.LARGE, Fonts.SIZE_TITLE) or font
        title_shadow = title_font.render("PAUSED", True, Colors.BLACK)
        title_text = title_font.render("PAUSED", True, Colors.TEXT_PRIMARY)
        title_rect = title_text.get_rect(center=(width // 2, self.TITLE_Y))
        surface.blit(title_shadow, title_rect.move(2, 2))
        surface.blit(title_text, title_rect)

        # Draw help text at bottom
        self._draw_help_text(surface, self.assets.get_font(Fonts.SMALL, Fonts.SIZE_SMALL))

        # Draw save message if showing
        if self.message_box:
            self.message_box.draw(surface, self.assets.get_font(Fonts.SMALL, Fonts.SIZE_SMALL), panel=self.panel)

        # Draw quit confirmation dialog
        self.quit_dialog.draw(surface, self.assets.get_font(Fonts.DEFAULT, Fonts.SIZE_BODY))

    def _draw_help_text(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        """Draw help text at bottom of screen."""
        help_text = "Up/Down: Navigate | Enter: Select | ESC: Resume"
        draw_contextual_help(surface, help_text, font, margin_bottom=Layout.SCREEN_MARGIN)
