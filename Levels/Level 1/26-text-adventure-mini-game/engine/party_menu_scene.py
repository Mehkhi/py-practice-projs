"""Party menu scene for managing party members."""

import pygame
from typing import Dict, List, Optional, TYPE_CHECKING

from .base_menu_scene import BaseMenuScene
from .assets import AssetManager
from .ui import Menu, MessageBox, NineSlicePanel, ConfirmationDialog, draw_hp_bar, draw_sp_bar, draw_contextual_help
from .theme import Colors, Fonts, Layout
from core.world import World
from core.entities import Player, PartyMember
from core.items import Item

if TYPE_CHECKING:
    from .scene import SceneManager


class PartyMenuScene(BaseMenuScene):
    """Party management menu scene."""

    def __init__(
        self,
        manager: Optional["SceneManager"],
        world: World,
        player: Player,
        items_db: Optional[Dict[str, Item]] = None,
        assets: Optional[AssetManager] = None,
        scale: int = 2,
    ):
        super().__init__(manager, assets, scale)
        self.world = world
        self.player = player
        self.items_db = items_db or {}

        # State
        self.selected_member_index: int = 0  # 0 = player, 1+ = party members
        self.mode = "view"  # "view", "action", "formation"

        # Action menu for selected member
        self.action_menu: Optional[Menu] = None

        # Formation selection menu
        self.formation_menu: Optional[Menu] = None

        # Message display
        self.message_box: Optional[MessageBox] = None
        self.showing_message = False
        self.message_timer = 0.0
        self.message_duration = 2.0

        # Confirmation dialog for member removal
        self.remove_confirm_dialog = ConfirmationDialog(
            message="Remove this party member? They will leave your party.",
            title="Remove Party Member",
            on_confirm=self._confirm_remove_member,
            on_cancel=self._cancel_remove_member,
            panel=self.panel,
        )
        self.pending_remove_index: Optional[int] = None

    def _get_all_members(self) -> List:
        """Get player + all party members as a list."""
        return [self.player] + list(self.player.party)

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle input events."""
        # Handle confirmation dialog first
        if self.remove_confirm_dialog.visible:
            self.remove_confirm_dialog.handle_event(event)
            return

        if self.showing_message:
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                self.showing_message = False
                self.message_box = None
            return

        if event.type == pygame.KEYDOWN:
            if self.mode == "view":
                if event.key == pygame.K_UP:
                    self._move_selection(-1)
                elif event.key == pygame.K_DOWN:
                    self._move_selection(1)
                elif event.key == pygame.K_RETURN:
                    self._open_action_menu()
                elif event.key == pygame.K_ESCAPE:
                    self.manager.pop()
            elif self.mode == "action":
                if self.action_menu:
                    if event.key == pygame.K_UP:
                        self.action_menu.move_selection(-1)
                    elif event.key == pygame.K_DOWN:
                        self.action_menu.move_selection(1)
                    elif event.key == pygame.K_RETURN:
                        self._handle_action_selection()
                    elif event.key == pygame.K_ESCAPE:
                        self.mode = "view"
                        self.action_menu = None
            elif self.mode == "formation":
                if self.formation_menu:
                    if event.key == pygame.K_UP:
                        self.formation_menu.move_selection(-1)
                    elif event.key == pygame.K_DOWN:
                        self.formation_menu.move_selection(1)
                    elif event.key == pygame.K_RETURN:
                        self._handle_formation_selection()
                    elif event.key == pygame.K_ESCAPE:
                        self.mode = "action"
                        self.formation_menu = None

    def _move_selection(self, delta: int) -> None:
        """Move member selection."""
        members = self._get_all_members()
        if not members:
            return
        self.selected_member_index = (self.selected_member_index + delta) % len(members)

    def _open_action_menu(self) -> None:
        """Open action menu for selected member."""
        members = self._get_all_members()
        if not members:
            return

        selected = members[self.selected_member_index]

        # Build action options based on who is selected
        options = ["View Stats"]

        # Can only change formation and remove party members (not the player)
        if self.selected_member_index > 0:
            options.append("Change Formation")
            options.append("Remove from Party")

        options.append("Cancel")

        self.action_menu = Menu(options, position=(350, 200))
        self.mode = "action"

    def _handle_action_selection(self) -> None:
        """Handle action menu selection."""
        if not self.action_menu:
            return

        selection = self.action_menu.get_selected()
        if not selection:
            return

        if selection == "View Stats":
            self._show_stats()
        elif selection == "Change Formation":
            self._open_formation_menu()
        elif selection == "Remove from Party":
            self._remove_member()
        elif selection == "Cancel":
            self.mode = "view"
            self.action_menu = None

    def _show_stats(self) -> None:
        """Show detailed stats for selected member."""
        members = self._get_all_members()
        if self.selected_member_index >= len(members):
            return

        member = members[self.selected_member_index]
        if not member.stats:
            self._show_message("No stats available.")
            return

        stats = member.stats
        role = getattr(member, "role", "Hero") if self.selected_member_index > 0 else "Hero"

        stats_text = (
            f"{member.name} ({role})\n"
            f"HP: {stats.hp}/{stats.max_hp}  SP: {stats.sp}/{stats.max_sp}\n"
            f"ATK: {stats.attack}  DEF: {stats.defense}  MAG: {stats.magic}\n"
            f"SPD: {stats.speed}  LCK: {stats.luck}  LV: {stats.level}"
        )

        self._show_message(stats_text)
        self.mode = "view"
        self.action_menu = None

    def _open_formation_menu(self) -> None:
        """Open formation position selection menu."""
        members = self._get_all_members()
        if self.selected_member_index == 0 or self.selected_member_index >= len(members):
            return

        member = members[self.selected_member_index]
        current_position = self.player.get_member_formation(member.entity_id)

        # Create formation options
        positions = ["Front", "Middle", "Back"]
        # Highlight current position
        options = [f"{pos} {'(Current)' if pos.lower() == current_position else ''}" for pos in positions]
        options.append("Cancel")

        self.formation_menu = Menu(options, position=(360, 200))
        self.mode = "formation"

    def _handle_formation_selection(self) -> None:
        """Handle formation position selection."""
        if not self.formation_menu:
            return

        selection = self.formation_menu.get_selected()
        if not selection:
            return

        if selection == "Cancel":
            self.mode = "action"
            self.formation_menu = None
            return

        # Extract position from selection (remove "(Current)" if present)
        position = selection.split()[0].lower()

        members = self._get_all_members()
        if self.selected_member_index >= len(members):
            return

        member = members[self.selected_member_index]
        success = self.player.set_member_formation(member.entity_id, position)

        if success:
            self._show_message(f"{member.name} moved to {position.capitalize()} position.")
        else:
            self._show_message("Failed to change formation position.")

        self.mode = "action"
        self.formation_menu = None

    def _remove_member(self) -> None:
        """Show confirmation dialog for removing party member."""
        if self.selected_member_index == 0:
            self._show_message("Cannot remove the main character!")
            return

        members = self._get_all_members()
        if self.selected_member_index >= len(members):
            return

        # Store the index for confirmation
        self.pending_remove_index = self.selected_member_index
        self.remove_confirm_dialog.show()

    def _confirm_remove_member(self) -> None:
        """Handle confirmed party member removal."""
        if self.pending_remove_index is None:
            return

        members = self._get_all_members()
        if self.pending_remove_index >= len(members):
            self.pending_remove_index = None
            return

        member = members[self.pending_remove_index]
        removed = self.player.remove_party_member(member.entity_id)

        if removed:
            self._show_message(f"{removed.name} left the party.")
            # Adjust selection if needed
            if self.selected_member_index >= len(self._get_all_members()):
                self.selected_member_index = max(0, len(self._get_all_members()) - 1)
        else:
            self._show_message("Failed to remove party member.")

        self.pending_remove_index = None
        self.mode = "view"
        self.action_menu = None

    def _cancel_remove_member(self) -> None:
        """Handle cancelled party member removal."""
        self.pending_remove_index = None
        # Dialog already hidden, just return to action menu

    def _show_message(self, text: str) -> None:
        """Show a message to the player."""
        self.message_box = MessageBox(position=(100, 350), width=440, height=100)
        self.message_box.set_text(text)
        self.showing_message = True
        self.message_timer = 0.0

    def update(self, dt: float) -> None:
        """Update scene state."""
        if self.showing_message:
            self.message_timer += dt
            if self.message_timer >= self.message_duration:
                self.showing_message = False
                self.message_box = None

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the party menu."""
        # Draw semi-transparent overlay
        size = surface.get_size()
        if not self.overlay or self.overlay.get_size() != size:
            self.overlay = pygame.Surface(size)
            self.overlay.set_alpha(200)
            self.overlay.fill((20, 20, 30))
        surface.blit(self.overlay, (0, 0))

        font = self.assets.get_font("default")
        font_small = self.assets.get_font("small") or font

        # Draw title
        title_font = self.assets.get_font("large", 24) or font
        title_text = title_font.render("PARTY", True, Colors.TEXT_PRIMARY)
        title_rect = title_text.get_rect(center=(surface.get_width() // 2, 40))
        surface.blit(title_text, title_rect)

        # Draw party members list
        members = self._get_all_members()
        start_y = 80
        card_height = 70
        card_width = 300
        card_x = 40

        for i, member in enumerate(members):
            card_y = start_y + i * (card_height + 10)

            # Draw card background
            card_rect = pygame.Rect(card_x, card_y, card_width, card_height)

            # Highlight selected
            if i == self.selected_member_index:
                if self.panel:
                    self.panel.draw(surface, card_rect)
                else:
                    pygame.draw.rect(surface, Colors.BG_PANEL, card_rect)
                pygame.draw.rect(surface, Colors.ACCENT, card_rect, 2)
            else:
                if self.panel:
                    self.panel.draw(surface, card_rect)
                else:
                    pygame.draw.rect(surface, Colors.BG_DARK, card_rect)
                pygame.draw.rect(surface, Colors.BORDER, card_rect, 1)

            # Draw member info
            name_color = Colors.TEXT_PRIMARY if member.stats and not member.stats.is_dead() else Colors.TEXT_DISABLED
            role_text = ""
            if i == 0:
                role_text = " (Leader)"
            elif hasattr(member, "role"):
                role_text = f" ({member.role.capitalize()})"

            # Get formation position for display (only for party members, not player)
            formation_text = ""
            if i > 0:
                formation_pos = self.player.get_member_formation(member.entity_id)
                formation_text = f" [{formation_pos.upper()}]"

            name_surface = font.render(f"{member.name}{role_text}{formation_text}", True, name_color)
            surface.blit(name_surface, (card_x + 10, card_y + 8))

            # Draw HP/SP bars
            if member.stats:
                bar_x = card_x + 10
                bar_y = card_y + 32
                bar_width = 180
                bar_height = 14

                draw_hp_bar(
                    surface, bar_x, bar_y, bar_width, bar_height,
                    member.stats.hp, member.stats.max_hp, "",
                    font=font_small
                )
                draw_sp_bar(
                    surface, bar_x, bar_y + bar_height + 4, bar_width, bar_height,
                    member.stats.sp, member.stats.max_sp, "",
                    font=font_small
                )

                # Draw level
                level_text = font_small.render(f"Lv.{member.stats.level}", True, Colors.TEXT_SECONDARY)
                surface.blit(level_text, (card_x + bar_width + 20, bar_y + 5))

        # Draw party size indicator
        party_size_text = font_small.render(
            f"Party: {len(self.player.party)}/{self.player.max_party_size}",
            True, Colors.TEXT_SECONDARY
        )
        surface.blit(party_size_text, (card_x, start_y + len(members) * (card_height + 10) + 10))

        # Draw action menu if open
        if self.mode == "action" and self.action_menu:
            # Draw action menu background
            menu_bg_rect = pygame.Rect(340, 180, 160, 120)
            if self.panel:
                self.panel.draw(surface, menu_bg_rect)
            else:
                pygame.draw.rect(surface, Colors.BG_PANEL, menu_bg_rect)
                pygame.draw.rect(surface, Colors.BORDER, menu_bg_rect, 2)

            self.action_menu.draw(
                surface, font,
                theme={
                    "active": Colors.TEXT_HIGHLIGHT,
                    "inactive": Colors.TEXT_SECONDARY,
                    "disabled": Colors.TEXT_DISABLED
                }
            )

        # Draw formation menu if open
        if self.mode == "formation" and self.formation_menu:
            # Draw formation menu background
            menu_bg_rect = pygame.Rect(350, 180, 140, 120)
            if self.panel:
                self.panel.draw(surface, menu_bg_rect)
            else:
                pygame.draw.rect(surface, Colors.BG_PANEL, menu_bg_rect)
                pygame.draw.rect(surface, Colors.BORDER, menu_bg_rect, 2)

            self.formation_menu.draw(
                surface, font,
                theme={
                    "active": Colors.TEXT_HIGHLIGHT,
                    "inactive": Colors.TEXT_SECONDARY,
                    "disabled": Colors.TEXT_DISABLED
                }
            )

        # Draw help text at bottom
        self._draw_help_text(surface, font_small)

        # Draw message box if showing
        if self.message_box:
            self.message_box.draw(surface, font_small, panel=self.panel)

        # Draw confirmation dialog
        self.remove_confirm_dialog.draw(surface, font)

    def _draw_help_text(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        """Draw standardized help text at the bottom of the screen."""
        mode_labels = {
            "view": "Up/Down: Select Member  |  Enter: Actions  |  ESC: Close",
            "action": "Up/Down: Select Action  |  Enter: Confirm  |  ESC: Back",
            "formation": "Up/Down: Select Position  |  Enter: Confirm  |  ESC: Cancel"
        }
        help_text = mode_labels.get(self.mode, "Up/Down: Navigate  |  Enter: Confirm  |  ESC: Back")

        draw_contextual_help(surface, help_text, font, margin_bottom=Layout.SCREEN_MARGIN)
