"""Party overlay mixin for managing party formation UI.

This mixin provides reusable party overlay functionality that can be used
by any scene that needs to display party formation management UI.
"""

import pygame
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from ..theme import Colors, Layout, PANEL_OVERLAY, PANEL_ITEM_SELECTED, PANEL_SUBPANEL
from .utils import draw_themed_panel

if TYPE_CHECKING:
    from core.entities import Entity, Player

FORMATION_SEQUENCE = ["front", "middle", "back"]


class PartyOverlayMixin:
    """Mixin providing party overlay functionality for scenes."""

    def __init__(self):
        """Initialize party overlay state."""
        self.party_overlay_visible = False
        self.party_overlay_selection = 0
        self.party_overlay_message: Optional[str] = None
        self.party_overlay_message_timer = 0.0

    def _party_overlay_members(self) -> List["Entity"]:
        """Get all party members including the player."""
        if not hasattr(self, 'player'):
            return []
        members: List["Entity"] = [self.player]
        members.extend([ally for ally in getattr(self.player, "party", []) if ally])
        return members

    def _toggle_party_overlay(self, force_state: Optional[bool] = None) -> None:
        """Toggle party overlay visibility."""
        desired_state = (not self.party_overlay_visible) if force_state is None else bool(force_state)
        if desired_state == self.party_overlay_visible:
            return
        self.party_overlay_visible = desired_state
        if desired_state:
            members = self._party_overlay_members()
            if members:
                self.party_overlay_selection = min(self.party_overlay_selection, len(members) - 1)
            else:
                self.party_overlay_selection = 0
            self._party_overlay_show_message("Use Arrows to adjust formations.")
        else:
            self.party_overlay_message = None

    def handle_party_overlay_event(self, event: pygame.event.Event) -> bool:
        """Handle events specific to the party overlay.

        Returns:
            True if the event was handled, False otherwise.
        """
        if event.type != pygame.KEYDOWN:
            return True
        if event.key in (pygame.K_ESCAPE, pygame.K_f):
            self._toggle_party_overlay(False)
            return True
        if event.key == pygame.K_UP:
            self._move_party_overlay_selection(-1)
            return True
        if event.key == pygame.K_DOWN:
            self._move_party_overlay_selection(1)
            return True
        if event.key == pygame.K_LEFT:
            self._adjust_party_overlay_position(-1)
            return True
        if event.key == pygame.K_RIGHT:
            self._adjust_party_overlay_position(1)
            return True
        return True

    def _move_party_overlay_selection(self, delta: int) -> None:
        """Move the party overlay selection."""
        members = self._party_overlay_members()
        if not members:
            self.party_overlay_selection = 0
            return
        self.party_overlay_selection = (self.party_overlay_selection + delta) % len(members)

    def _adjust_party_overlay_position(self, direction: int) -> None:
        """Adjust the formation position of the selected party member."""
        members = self._party_overlay_members()
        if not members or not hasattr(self, 'player'):
            return
        index = self.party_overlay_selection % len(members)
        member = members[index]
        current_position = (
            getattr(self.player, "formation_position", FORMATION_SEQUENCE[0])
            if index == 0
            else self.player.get_member_formation(member.entity_id)
        )
        if current_position not in FORMATION_SEQUENCE:
            current_position = FORMATION_SEQUENCE[0]
        new_index = (FORMATION_SEQUENCE.index(current_position) + direction) % len(FORMATION_SEQUENCE)
        new_position = FORMATION_SEQUENCE[new_index]
        if index == 0:
            self.player.formation_position = new_position
            self._party_overlay_show_message(f"Leader moves to {new_position.capitalize()}.")
        else:
            if self.player.set_member_formation(member.entity_id, new_position):
                self._party_overlay_show_message(
                    f"{member.name} moves to {new_position.capitalize()}."
                )
            else:
                self._party_overlay_show_message(f"Can't move {member.name} there.")

    def update_party_overlay(self, dt: float) -> None:
        """Update party overlay state (timers, etc.)."""
        if self.party_overlay_message and self.party_overlay_message_timer > 0:
            self.party_overlay_message_timer = max(0.0, self.party_overlay_message_timer - dt)
            if self.party_overlay_message_timer <= 0:
                self.party_overlay_message = None

    def draw_party_overlay(self, surface: pygame.Surface) -> None:
        """Draw the party overlay UI."""
        if not self.party_overlay_visible or not hasattr(self, 'assets'):
            return

        width, height = surface.get_size()
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        margin = Layout.SCREEN_MARGIN
        panel_rect = pygame.Rect(
            margin,
            margin,
            width - margin * 2,
            height - margin * 2,
        )
        draw_themed_panel(surface, panel_rect, PANEL_OVERLAY)

        title_font = self.assets.get_font("large", 28) or self.assets.get_font("default")
        font = self.assets.get_font("default")
        small_font = self.assets.get_font("small") or font

        if title_font:
            title_text = title_font.render("Party Formation", True, Colors.TEXT_PRIMARY)
            surface.blit(title_text, (panel_rect.centerx - title_text.get_width() // 2, panel_rect.top + 20))

        members = self._party_overlay_members()
        row_height = 60
        row_y = panel_rect.top + 80
        row_x = panel_rect.left + 40
        row_width = panel_rect.width - 80

        for idx, member in enumerate(members):
            card_rect = pygame.Rect(row_x, row_y + idx * (row_height + 10), row_width, row_height)
            if idx == self.party_overlay_selection:
                draw_themed_panel(surface, card_rect, PANEL_ITEM_SELECTED)
            else:
                draw_themed_panel(surface, card_rect, PANEL_SUBPANEL)

            if font:
                role_label = "Leader" if idx == 0 else getattr(member, "role", "Ally").title()
                formation = (
                    getattr(self.player, "formation_position", "front")
                    if idx == 0
                    else self.player.get_member_formation(member.entity_id)
                )
                name_text = font.render(
                    f"{member.name} - {role_label}",
                    True,
                    Colors.TEXT_PRIMARY,
                )
                surface.blit(name_text, (card_rect.x + 16, card_rect.y + 8))

                formation_text = small_font.render(
                    f"Position: {formation.capitalize()}",
                    True,
                    Colors.TEXT_SECONDARY,
                )
                surface.blit(formation_text, (card_rect.x + 16, card_rect.y + 30))

        instructions = "F/Esc: Close  |  Up/Down: Select  |  Left/Right: Cycle"
        if small_font:
            help_text = small_font.render(instructions, True, Colors.TEXT_SECONDARY)
            surface.blit(
                help_text,
                (
                    panel_rect.centerx - help_text.get_width() // 2,
                    panel_rect.bottom - 40,
                ),
            )

        if self.party_overlay_message and small_font:
            msg_text = small_font.render(self.party_overlay_message, True, Colors.TEXT_PRIMARY)
            surface.blit(
                msg_text,
                (
                    panel_rect.centerx - msg_text.get_width() // 2,
                    panel_rect.bottom - 70,
                ),
            )

    def _party_overlay_show_message(self, text: str) -> None:
        """Show a temporary message in the party overlay."""
        self.party_overlay_message = text
        self.party_overlay_message_timer = 2.0
