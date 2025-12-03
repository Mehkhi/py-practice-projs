"""Equipment management scene for equipping/unequipping items."""

from typing import Dict, List, Optional, Tuple, TYPE_CHECKING

import pygame

from .base_menu_scene import BaseMenuScene
from .assets import AssetManager
from .ui import Menu, MessageBox, NineSlicePanel, draw_contextual_help
from .theme import Colors, Fonts, Layout, SceneLayout
from core.constants import SUPPORTED_EQUIP_SLOTS
from core.world import World
from core.entities import Player, PartyMember, Entity
from core.items import Item
from core.tutorial_system import TipTrigger
from core.equipment_flow import (
    equip_item_from_inventory,
    unequip_item_to_inventory,
    get_equippable_items,
)
from core.logging_utils import log_warning

if TYPE_CHECKING:
    from .scene import SceneManager


class EquipmentScene(BaseMenuScene):
    """Scene for managing player and party member equipment."""

    # Display names for equipment slots
    SLOT_NAMES = {
        "weapon": "Weapon",
        "armor": "Armor",
        "accessory": "Accessory",
    }

    # Layout constants - using SceneLayout preset with custom additions
    LAYOUT = SceneLayout.SIDE_PANEL
    MODIFIER_TEXT_OFFSET_X = 160  # X offset for stat modifier display in stats panel

    def __init__(
        self,
        manager: Optional["SceneManager"],
        world: World,
        player: Player,
        items_db: Dict[str, Item],
        assets: Optional[AssetManager] = None,
        scale: int = 2,
    ):
        super().__init__(manager, assets, scale)
        self.world = world
        self.player = player
        self.items_db = items_db

        # UI state - now supports party member selection
        self.mode = "member"  # "member", "slots", or "items"
        self.selected_member: Optional[Entity] = None  # Player or PartyMember
        self.selected_slot: Optional[str] = None
        self.member_menu: Optional[Menu] = None
        self.slot_menu: Optional[Menu] = None
        self.item_menu: Optional[Menu] = None
        self.item_mapping: Dict[int, Optional[str]] = {}  # menu index -> item_id
        self.member_mapping: Dict[int, Optional[Entity]] = {}  # menu index -> entity

        # Message display
        self.message_box = MessageBox(
            position=(self.LAYOUT["message_box_x"], self.LAYOUT["message_box_y"]),
            width=self.LAYOUT["message_box_width"],
            height=self.LAYOUT["message_box_height"],
        )
        self.message_box.set_text("Select a party member to manage equipment.")

        # Build initial member menu
        self._refresh_member_menu()

    def _get_equipped_item(self, slot: str) -> Optional[Item]:
        """Get the item currently equipped in a slot for the selected member."""
        target = self.selected_member or self.player
        item_id = target.get_equipped_item_id(slot)
        if item_id:
            return self.items_db.get(item_id)
        return None

    def _refresh_member_menu(self) -> None:
        """Rebuild the party member selection menu."""
        options: List[str] = []
        self.member_mapping.clear()
        idx = 0

        # Add player first
        options.append(f"{self.player.name} (You)")
        self.member_mapping[idx] = self.player
        idx += 1

        # Add party members
        for member in self.player.party:
            role = getattr(member, "role", "fighter").title()
            options.append(f"{member.name} ({role})")
            self.member_mapping[idx] = member
            idx += 1

        options.append("Back")
        self.member_menu = Menu(options, position=SceneLayout.get_menu_position(self.LAYOUT))

    def _refresh_slot_menu(self) -> None:
        """Rebuild the slot selection menu with current equipment."""
        options: List[str] = []
        for slot in SUPPORTED_EQUIP_SLOTS:
            slot_name = self.SLOT_NAMES.get(slot, slot.title())
            equipped_item = self._get_equipped_item(slot)
            if equipped_item:
                options.append(f"{slot_name}: {equipped_item.name}")
            else:
                options.append(f"{slot_name}: (empty)")
        options.append("Back")
        self.slot_menu = Menu(options, position=SceneLayout.get_menu_position(self.LAYOUT))

    def _refresh_item_menu(self) -> None:
        """Rebuild the item selection menu for the selected slot."""
        if not self.selected_slot:
            return

        options: List[str] = []
        self.item_mapping.clear()
        idx = 0

        # Option to unequip if something is equipped
        equipped_item = self._get_equipped_item(self.selected_slot)
        if equipped_item:
            options.append(f"Unequip {equipped_item.name}")
            self.item_mapping[idx] = None  # None signals unequip action
            idx += 1

        # List equippable items from inventory (always use player's inventory)
        target = self.selected_member or self.player
        equippable = get_equippable_items(target, self.items_db, self.selected_slot, inventory=self.player.inventory)

        # Sort items by name for better organization
        sorted_items = sorted(equippable.items(), key=lambda x: x[1].name)

        for item_id, item in sorted_items:
            qty = self.player.inventory.get_quantity(item_id) if self.player.inventory else 0
            stat_preview = self._format_stat_modifiers(item)

            # Show hotbar assignment if present
            hotbar_slot = None
            if self.player.inventory:
                hotbar_slot = self._get_hotbar_slot_for_item(item_id)
            hotbar_indicator = f"[{hotbar_slot}] " if hotbar_slot else ""

            # Show max stack size if applicable
            max_stack_text = f"/{item.max_stack_size}" if item.max_stack_size else ""

            label = f"{hotbar_indicator}{item.name} x{qty}{max_stack_text}"
            if stat_preview:
                label += f" ({stat_preview})"
            options.append(label)
            self.item_mapping[idx] = item_id
            idx += 1

        options.append("Cancel")
        self.item_menu = Menu(options, position=SceneLayout.get_menu_position(self.LAYOUT))

    def _get_hotbar_slot_for_item(self, item_id: str) -> Optional[int]:
        """Get the hotbar slot number (1-9) for an item, or None if not assigned."""
        if not self.player.inventory:
            return None
        return self.player.inventory.get_slot_for_item(item_id)

    def _format_stat_modifiers(self, item: Item) -> str:
        """Format item stat modifiers for display."""
        if not item.stat_modifiers:
            return ""
        parts = []
        for stat, value in item.stat_modifiers.items():
            sign = "+" if value >= 0 else ""
            parts.append(f"{stat[:3].upper()}{sign}{value}")
        return ", ".join(parts)

    def _handle_member_selection(self) -> None:
        """Handle selection in member menu."""
        if not self.member_menu:
            return

        selected_idx = self.member_menu.selected_index

        # Last option is Back
        if selected_idx == len(self.member_menu.options) - 1:
            if self.manager:
                self.manager.pop()
            return

        member = self.member_mapping.get(selected_idx)
        if member:
            self.selected_member = member
            self.mode = "slots"
            self._refresh_slot_menu()
            self.message_box.set_text(f"Managing equipment for {member.name}.")
        else:
            self.message_box.set_text("Error: Could not select party member.")

    def _handle_slot_selection(self) -> None:
        """Handle selection in slot menu."""
        if not self.slot_menu:
            return

        selected_idx = self.slot_menu.selected_index
        slots = list(SUPPORTED_EQUIP_SLOTS)

        # Last option is Back - return to member selection
        if selected_idx == len(slots):
            self.mode = "member"
            self.selected_member = None
            self._refresh_member_menu()
            self.message_box.set_text("Select a party member to manage equipment.")
            return

        if selected_idx < len(slots):
            self.selected_slot = slots[selected_idx]
            self.mode = "items"
            self._refresh_item_menu()
            slot_name = self.SLOT_NAMES.get(self.selected_slot, self.selected_slot)
            self.message_box.set_text(f"Select equipment for {slot_name}.")

    def _handle_item_selection(self) -> None:
        """Handle selection in item menu."""
        if not self.item_menu or not self.selected_slot:
            return

        selected_idx = self.item_menu.selected_index

        # Last option is Cancel
        if selected_idx == len(self.item_menu.options) - 1:
            self.mode = "slots"
            self.selected_slot = None
            self._refresh_slot_menu()
            self.message_box.set_text("Select a slot to manage equipment.")
            return

        item_id = self.item_mapping.get(selected_idx)
        target = self.selected_member or self.player

        if item_id is None:
            # Unequip action
            if unequip_item_to_inventory(target, self.selected_slot, self.items_db, inventory=self.player.inventory):
                self.message_box.set_text("Item unequipped!")
                tutorial_manager = self.get_manager_attr(
                    "tutorial_manager", "_handle_item_selection"
                )
                if tutorial_manager:
                    tutorial_manager.trigger_tip(TipTrigger.FIRST_EQUIPMENT_CHANGE)
            else:
                self.message_box.set_text("Failed to unequip item.")
        else:
            # Equip action
            item = self.items_db.get(item_id)
            if not item:
                self.message_box.set_text("Item not found.")
            elif equip_item_from_inventory(target, item_id, self.items_db, self.selected_slot, inventory=self.player.inventory):
                self.message_box.set_text(f"Equipped {item.name}!")
                tutorial_manager = self.get_manager_attr(
                    "tutorial_manager", "_handle_item_selection"
                )
                if tutorial_manager:
                    tutorial_manager.trigger_tip(TipTrigger.FIRST_EQUIPMENT_CHANGE)
            else:
                self.message_box.set_text("Failed to equip item. Check inventory.")

        # Return to slot view after action
        self.mode = "slots"
        self.selected_slot = None
        self._refresh_slot_menu()

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle input events."""
        if event.type != pygame.KEYDOWN:
            return

        # Get current menu based on mode
        if self.mode == "member":
            current_menu = self.member_menu
        elif self.mode == "items":
            current_menu = self.item_menu
        else:
            current_menu = self.slot_menu

        if not current_menu:
            return

        if event.key == pygame.K_UP:
            current_menu.move_selection(-1)
        elif event.key == pygame.K_DOWN:
            current_menu.move_selection(1)
        elif event.key == pygame.K_RETURN:
            if self.mode == "member":
                self._handle_member_selection()
            elif self.mode == "slots":
                self._handle_slot_selection()
            else:
                self._handle_item_selection()
        elif event.key == pygame.K_ESCAPE:
            if self.mode == "items":
                # Go back to slot selection
                self.mode = "slots"
                self.selected_slot = None
                self._refresh_slot_menu()
                self.message_box.set_text("Select a slot to manage equipment.")
            elif self.mode == "slots":
                # Go back to member selection
                self.mode = "member"
                self.selected_member = None
                self._refresh_member_menu()
                self.message_box.set_text("Select a party member to manage equipment.")
            else:
                # Exit equipment scene
                if self.manager:
                    self.manager.pop()

    def update(self, dt: float) -> None:
        """Update scene state and drive menu/message animations."""
        if self.member_menu:
            self.member_menu.update(dt)
        if self.slot_menu:
            self.slot_menu.update(dt)
        if self.item_menu:
            self.item_menu.update(dt)
        if self.message_box:
            self.message_box.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the equipment scene."""
        # Draw semi-transparent overlay
        self.draw_overlay(surface)

        font = self.assets.get_font("default")
        small_font = self.assets.get_font("small") or font
        title_font = self.assets.get_font("large", 24) or font

        # Draw title with shadow
        title_shadow = title_font.render("EQUIPMENT", True, Colors.BG_DARK)
        title_text = title_font.render("EQUIPMENT", True, Colors.TEXT_PRIMARY)
        title_rect = title_text.get_rect(center=(surface.get_width() // 2, self.LAYOUT["title_y"]))
        surface.blit(title_shadow, title_rect.move(2, 2))
        surface.blit(title_text, title_rect)

        # Draw player stats panel on the right
        self._draw_stats_panel(surface, font, small_font)

        # Draw inventory count
        self._draw_inventory_count(surface, small_font)

        # Draw menu background with rounded corners
        menu_bg_rect = pygame.Rect(SceneLayout.get_menu_bg_rect(self.LAYOUT))
        if self.panel:
            self.panel.draw(surface, menu_bg_rect)
        else:
            pygame.draw.rect(surface, (40, 40, 50), menu_bg_rect, border_radius=Layout.CORNER_RADIUS)
            pygame.draw.rect(surface, (100, 100, 120), menu_bg_rect, 2, border_radius=Layout.CORNER_RADIUS)

        # Draw current menu based on mode
        if self.mode == "member":
            current_menu = self.member_menu
        elif self.mode == "items":
            current_menu = self.item_menu
        else:
            current_menu = self.slot_menu

        if current_menu:
            current_menu.draw(
                surface,
                font,
                theme={
                    "active": Colors.TEXT_HIGHLIGHT,
                    "inactive": Colors.TEXT_SECONDARY,
                    "disabled": Colors.TEXT_DISABLED
                }
            )

        # Draw message box
        self.message_box.draw(surface, small_font, panel=self.panel)

        # Draw mode indicator (positioned relative to menu background)
        mode_labels = {"member": "Party", "slots": "Slots", "items": "Items"}
        mode_text = mode_labels.get(self.mode, "Slots")
        mode_surface = small_font.render(f"[{mode_text}]", True, Colors.TEXT_SECONDARY)
        mode_indicator_x = self.LAYOUT["menu_bg_x"] + Layout.PADDING_SM
        mode_indicator_y = self.LAYOUT["menu_bg_y"] - Layout.LINE_HEIGHT_COMPACT
        surface.blit(mode_surface, (mode_indicator_x, mode_indicator_y))

        # Draw help text at bottom
        self._draw_help_text(surface, small_font)

    def _draw_stats_panel(
        self,
        surface: pygame.Surface,
        font: pygame.font.Font,
        small_font: pygame.font.Font,
    ) -> None:
        """Draw selected member stats and equipment bonuses."""
        panel_x = self.LAYOUT["details_x"]
        panel_y = self.LAYOUT["details_y"]
        panel_width = self.LAYOUT["details_width"]
        panel_height = self.LAYOUT["details_height"]

        # Panel background with rounded corners
        stats_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        if self.panel:
            self.panel.draw(surface, stats_rect)
        else:
            pygame.draw.rect(surface, (40, 40, 50), stats_rect, border_radius=Layout.CORNER_RADIUS)
            pygame.draw.rect(surface, (100, 100, 120), stats_rect, 2, border_radius=Layout.CORNER_RADIUS)

        # Get target entity (selected member or player)
        target = self.selected_member or self.player

        # Header with member name and shadow
        header_text = f"{target.name}'s Stats" if self.selected_member else "Stats"
        header_shadow = font.render(header_text, True, Colors.BG_DARK)
        header = font.render(header_text, True, Colors.TEXT_PRIMARY)
        surface.blit(header_shadow, (panel_x + Layout.PADDING_LG + 1, panel_y + Layout.PADDING_MD + 1))
        surface.blit(header, (panel_x + Layout.PADDING_LG, panel_y + Layout.PADDING_MD))

        if not target.stats:
            return

        stats = target.stats
        modifiers = getattr(stats, "equipment_modifiers", {}) or {}

        y_offset = panel_y + Layout.PADDING_XL + Layout.LINE_HEIGHT
        stat_names = [
            ("HP", stats.hp, stats.max_hp, None),
            ("SP", stats.sp, stats.max_sp, None),
            ("Attack", stats.effective_attack, None, modifiers.get("attack", 0)),
            ("Defense", stats.effective_defense, None, modifiers.get("defense", 0)),
            ("Magic", stats.effective_magic, None, modifiers.get("magic", 0)),
            ("Speed", stats.effective_speed, None, modifiers.get("speed", 0)),
            ("Luck", stats.effective_luck, None, modifiers.get("luck", 0)),
        ]

        for name, value, max_val, modifier in stat_names:
            if max_val is not None:
                text = f"{name}: {value}/{max_val}"
            else:
                text = f"{name}: {value}"

            stat_surface = small_font.render(text, True, Colors.TEXT_SECONDARY)
            surface.blit(stat_surface, (panel_x + Layout.PADDING_LG + Layout.PADDING_XS, y_offset))

            # Show modifier bonus/penalty
            if modifier and modifier != 0:
                sign = "+" if modifier > 0 else ""
                color = Colors.TEXT_SUCCESS if modifier > 0 else Colors.TEXT_ERROR
                mod_text = small_font.render(f"({sign}{modifier})", True, color)
                surface.blit(mod_text, (panel_x + self.MODIFIER_TEXT_OFFSET_X, y_offset))

            y_offset += Layout.LINE_HEIGHT_COMPACT

        # Draw currently equipped items
        y_offset += Layout.ELEMENT_GAP_LARGE
        equip_header = small_font.render("Equipped:", True, Colors.TEXT_SECONDARY)
        surface.blit(equip_header, (panel_x + Layout.PADDING_LG + Layout.PADDING_XS, y_offset))
        y_offset += Layout.LINE_HEIGHT_COMPACT

        for slot in SUPPORTED_EQUIP_SLOTS:
            slot_name = self.SLOT_NAMES.get(slot, slot)[:3]
            item = self._get_equipped_item(slot)
            item_name = item.name if item else "---"
            line = f"{slot_name}: {item_name}"
            line_surface = small_font.render(line, True, Colors.TEXT_SECONDARY)
            surface.blit(line_surface, (panel_x + Layout.PADDING_LG + Layout.PADDING_SM, y_offset))
            y_offset += Layout.LINE_HEIGHT_COMPACT

    def _draw_inventory_count(self, surface: pygame.Surface, small_font: pygame.font.Font) -> None:
        """Draw inventory item count indicator."""
        if not self.player.inventory:
            return

        total_count = self.player.inventory.get_total_item_count()
        unique_count = len(self.player.inventory.get_all_items())

        count_text = small_font.render(f"Items: {unique_count} unique, {total_count} total", True, Colors.TEXT_SECONDARY)
        surface.blit(count_text, (Layout.SCREEN_MARGIN, surface.get_height() - Layout.SCREEN_MARGIN - Layout.PADDING_SM))

    def _draw_help_text(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        """Draw standardized help text at the bottom of the screen."""
        mode_labels = {
            "member": "Up/Down: Select Member  |  Enter: Confirm  |  ESC: Close",
            "slots": "Up/Down: Select Slot  |  Enter: Confirm  |  ESC: Back",
            "items": "Up/Down: Select Item  |  Enter: Equip/Unequip  |  ESC: Back"
        }
        help_text = mode_labels.get(self.mode, "Up/Down: Navigate  |  Enter: Confirm  |  ESC: Back")

        draw_contextual_help(surface, help_text, font, margin_bottom=Layout.SCREEN_MARGIN)
