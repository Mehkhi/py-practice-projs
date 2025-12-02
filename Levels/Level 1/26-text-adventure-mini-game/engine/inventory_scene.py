"""Inventory management scene for viewing and managing items."""

import pygame
from typing import Dict, List, Optional, Tuple, TYPE_CHECKING

from .base_menu_scene import BaseMenuScene
from .assets import AssetManager
from .ui import Menu, MessageBox, NineSlicePanel, draw_contextual_help
from .theme import Colors, Fonts, Layout, SceneLayout
from core.world import World
from core.entities import Player
from core.items import Item, Inventory

if TYPE_CHECKING:
    from .scene import SceneManager


class InventoryScene(BaseMenuScene):
    """Scene for viewing and managing inventory with sorting, filtering, and hotbar assignment."""

    # Layout constants - using SceneLayout preset with custom additions
    LAYOUT = SceneLayout.SIDE_PANEL
    HOTBAR_Y = 350
    HOTBAR_SLOT_WIDTH = 56
    HOTBAR_SLOT_HEIGHT = 38

    # Sort and filter options
    SORT_OPTIONS = ["type", "name", "quantity"]
    SORT_NAMES = ["By Type", "By Name", "By Quantity"]
    FILTER_OPTIONS = [None, "consumable", "equipment", "key"]
    FILTER_NAMES = ["All Items", "Consumables", "Equipment", "Keys"]

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

        # UI state
        self.mode = "items"  # "items", "sort", "filter", "hotbar"
        self.current_sort = "type"
        self.current_filter: Optional[str] = None
        self.selected_index = 0
        self.scroll_offset = 0
        self.max_visible_items = 8
        self.hotbar_slot_selected: Optional[int] = None  # 1-9 when assigning to hotbar

        # Message display
        self.message_box = MessageBox(
            position=(self.LAYOUT["message_box_x"], self.LAYOUT["message_box_y"]),
            width=self.LAYOUT["message_box_width"],
            height=self.LAYOUT["message_box_height"],
        )
        self.message_box.set_text("Press S to sort, F to filter, H to assign hotbar, ESC to close.")

        # Build item list
        self._refresh_item_list()

    def _refresh_item_list(self) -> None:
        """Refresh the displayed item list based on current sort and filter."""
        if not self.player.inventory:
            self.displayed_items: List[Tuple[str, int]] = []
            return

        # Get filtered items first
        filtered_dict = (
            self.player.inventory.get_filtered_items(self.current_filter, self.items_db)
            if self.current_filter
            else self.player.inventory.get_all_items()
        )

        # Get sorted items
        sorted_items = self.player.inventory.get_sorted_items(self.current_sort, self.items_db)

        # Apply filter to sorted results
        if self.current_filter:
            self.displayed_items = [
                (item_id, qty) for item_id, qty in sorted_items
                if item_id in filtered_dict
            ]
        else:
            self.displayed_items = sorted_items

        # Adjust selection if out of bounds
        if self.selected_index >= len(self.displayed_items):
            self.selected_index = max(0, len(self.displayed_items) - 1)
        self._adjust_scroll()

    def _adjust_scroll(self) -> None:
        """Adjust scroll offset to keep selected item visible."""
        if self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        elif self.selected_index >= self.scroll_offset + self.max_visible_items:
            self.scroll_offset = self.selected_index - self.max_visible_items + 1

    def _get_selected_item(self) -> Optional[Tuple[str, int]]:
        """Get currently selected item (item_id, quantity)."""
        if 0 <= self.selected_index < len(self.displayed_items):
            return self.displayed_items[self.selected_index]
        return None

    def _get_hotbar_slot_for_item(self, item_id: str) -> Optional[int]:
        """Get the hotbar slot number (1-9) for an item, or None if not assigned."""
        if not self.player.inventory:
            return None
        return self.player.inventory.get_slot_for_item(item_id)

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle input events."""
        if event.type != pygame.KEYDOWN:
            return

        if self.mode == "hotbar":
            # Selecting hotbar slot (1-9)
            if event.key >= pygame.K_1 and event.key <= pygame.K_9:
                slot = event.key - pygame.K_0
                selected = self._get_selected_item()
                if selected:
                    item_id, _ = selected
                    item = self.items_db.get(item_id)
                    # Only consumables can be assigned to hotbar
                    if item and item.item_type == "consumable":
                        if self.player.inventory:
                            self.player.inventory.set_hotbar_item(slot, item_id)
                            self.message_box.set_text(f"Assigned {item.name} to hotbar slot {slot}!")
                        self.mode = "items"
                        self.hotbar_slot_selected = None
                    else:
                        self.message_box.set_text("Only consumable items can be assigned to hotbar.")
            elif event.key == pygame.K_ESCAPE:
                self.mode = "items"
                self.hotbar_slot_selected = None
                self.message_box.set_text("Press S to sort, F to filter, H to assign hotbar, ESC to close.")
            return

        if event.key == pygame.K_ESCAPE:
            self.manager.pop()
        elif event.key == pygame.K_UP:
            if self.displayed_items:
                self.selected_index = (self.selected_index - 1) % len(self.displayed_items)
                self._adjust_scroll()
        elif event.key == pygame.K_DOWN:
            if self.displayed_items:
                self.selected_index = (self.selected_index + 1) % len(self.displayed_items)
                self._adjust_scroll()
        elif event.key == pygame.K_s:
            # Cycle through sort options
            current_idx = self.SORT_OPTIONS.index(self.current_sort)
            self.current_sort = self.SORT_OPTIONS[(current_idx + 1) % len(self.SORT_OPTIONS)]
            self._refresh_item_list()
            sort_name = self.SORT_NAMES[self.SORT_OPTIONS.index(self.current_sort)]
            self.message_box.set_text(f"Sorting: {sort_name}")
        elif event.key == pygame.K_f:
            # Cycle through filter options
            current_idx = self.FILTER_OPTIONS.index(self.current_filter)
            self.current_filter = self.FILTER_OPTIONS[(current_idx + 1) % len(self.FILTER_OPTIONS)]
            self._refresh_item_list()
            filter_name = self.FILTER_NAMES[self.FILTER_OPTIONS.index(self.current_filter)]
            self.message_box.set_text(f"Filter: {filter_name}")
        elif event.key == pygame.K_h:
            # Enter hotbar assignment mode
            selected = self._get_selected_item()
            if selected:
                item_id, _ = selected
                item = self.items_db.get(item_id)
                if item and item.item_type == "consumable":
                    self.mode = "hotbar"
                    self.message_box.set_text("Press 1-9 to assign to hotbar slot, ESC to cancel.")
                else:
                    self.message_box.set_text("Only consumable items can be assigned to hotbar.")
            else:
                self.message_box.set_text("No item selected.")

    def update(self, dt: float) -> None:
        """Update scene state."""
        pass

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the inventory scene."""
        # Draw semi-transparent overlay
        self.draw_overlay(surface)

        font = self.assets.get_font("default")
        small_font = self.assets.get_font("small") or font
        title_font = self.assets.get_font("large", 24) or font

        # Draw title with shadow
        title_shadow = title_font.render("INVENTORY", True, Colors.BG_DARK)
        title_text = title_font.render("INVENTORY", True, Colors.TEXT_PRIMARY)
        title_rect = title_text.get_rect(center=(surface.get_width() // 2, self.LAYOUT["title_y"]))
        surface.blit(title_shadow, title_rect.move(2, 2))
        surface.blit(title_text, title_rect)

        # Draw item details panel on the right
        self._draw_details_panel(surface, font, small_font)

        # Draw menu background with rounded corners
        menu_bg_rect = pygame.Rect(SceneLayout.get_menu_bg_rect(self.LAYOUT))
        if self.panel:
            self.panel.draw(surface, menu_bg_rect)
        else:
            pygame.draw.rect(surface, (40, 40, 50), menu_bg_rect, border_radius=Layout.CORNER_RADIUS)
            pygame.draw.rect(surface, (100, 100, 120), menu_bg_rect, 2, border_radius=Layout.CORNER_RADIUS)

        # Draw item list
        self._draw_item_list(surface, font, small_font)

        # Draw hotbar
        self._draw_hotbar(surface, font, small_font)

        # Draw message box
        self.message_box.draw(surface, small_font, panel=self.panel)

        # Draw mode indicator
        mode_text = "HOTBAR" if self.mode == "hotbar" else "ITEMS"
        mode_surface = small_font.render(f"[{mode_text}]", True, Colors.TEXT_SECONDARY)
        mode_indicator_x = self.LAYOUT["menu_bg_x"] + Layout.PADDING_SM
        mode_indicator_y = self.LAYOUT["menu_bg_y"] - Layout.LINE_HEIGHT_COMPACT
        surface.blit(mode_surface, (mode_indicator_x, mode_indicator_y))

        # Draw sort/filter indicators
        sort_name = self.SORT_NAMES[self.SORT_OPTIONS.index(self.current_sort)]
        filter_name = self.FILTER_NAMES[self.FILTER_OPTIONS.index(self.current_filter)]
        info_text = f"Sort: {sort_name} | Filter: {filter_name}"
        info_surface = small_font.render(info_text, True, Colors.TEXT_SECONDARY)
        surface.blit(info_surface, (
            self.LAYOUT["menu_bg_x"] + Layout.PADDING_SM,
            self.LAYOUT["menu_bg_y"] + self.LAYOUT["menu_bg_height"] + Layout.ELEMENT_GAP
        ))

        # Draw help text at bottom
        self._draw_help_text(surface, small_font)

    def _draw_item_list(self, surface: pygame.Surface, font: pygame.font.Font, small_font: pygame.font.Font) -> None:
        """Draw the list of items."""
        x = self.LAYOUT["menu_bg_x"] + Layout.PADDING_MD
        y_start = self.LAYOUT["menu_bg_y"] + Layout.PADDING_MD
        line_height = Layout.MENU_ITEM_HEIGHT_COMPACT

        visible_items = self.displayed_items[
            self.scroll_offset:self.scroll_offset + self.max_visible_items
        ]

        for i, (item_id, quantity) in enumerate(visible_items):
            item = self.items_db.get(item_id)
            if not item:
                continue

            item_y = y_start + i * line_height
            is_selected = (self.scroll_offset + i) == self.selected_index

            # Highlight selected item with rounded corners
            if is_selected:
                highlight_rect = pygame.Rect(
                    x - Layout.PADDING_SM,
                    item_y - Layout.PADDING_XS,
                    self.LAYOUT["menu_bg_width"] - Layout.PADDING_LG,
                    line_height
                )
                pygame.draw.rect(surface, Colors.BG_PANEL, highlight_rect, border_radius=Layout.CORNER_RADIUS_SMALL)
                pygame.draw.rect(surface, Colors.ACCENT, highlight_rect, 1, border_radius=Layout.CORNER_RADIUS_SMALL)

            # Item name and quantity
            hotbar_slot = self._get_hotbar_slot_for_item(item_id)
            hotbar_indicator = f"[{hotbar_slot}] " if hotbar_slot else ""
            item_name = item.name
            max_stack = f"/{item.max_stack_size}" if item.max_stack_size else ""
            item_text = f"{hotbar_indicator}{item_name} x{quantity}{max_stack}"

            color = Colors.TEXT_HIGHLIGHT if is_selected else Colors.TEXT_SECONDARY
            text_surface = small_font.render(item_text, True, color)
            # Vertically center text in the line
            text_y = item_y + (line_height - text_surface.get_height()) // 2 - Layout.PADDING_XS
            surface.blit(text_surface, (x, text_y))

    def _draw_details_panel(
        self,
        surface: pygame.Surface,
        font: pygame.font.Font,
        small_font: pygame.font.Font,
    ) -> None:
        """Draw item details panel."""
        panel_x = self.LAYOUT["details_x"]
        panel_y = self.LAYOUT["details_y"]
        panel_width = self.LAYOUT["details_width"]
        panel_height = self.LAYOUT["details_height"]

        # Panel background
        details_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        if self.panel:
            self.panel.draw(surface, details_rect)
        else:
            pygame.draw.rect(surface, (40, 40, 50), details_rect, border_radius=Layout.CORNER_RADIUS)
            pygame.draw.rect(surface, (100, 100, 120), details_rect, 2, border_radius=Layout.CORNER_RADIUS)

        selected = self._get_selected_item()
        if not selected:
            no_item_text = small_font.render("No item selected", True, Colors.TEXT_DISABLED)
            surface.blit(no_item_text, (panel_x + Layout.PADDING_LG, panel_y + Layout.PADDING_XL))
            return

        item_id, quantity = selected
        item = self.items_db.get(item_id)
        if not item:
            return

        y_offset = panel_y + Layout.PADDING_LG

        # Item name with shadow
        name_shadow = font.render(item.name, True, Colors.BG_DARK)
        name_text = font.render(item.name, True, Colors.TEXT_PRIMARY)
        surface.blit(name_shadow, (panel_x + Layout.PADDING_LG + 1, y_offset + 1))
        surface.blit(name_text, (panel_x + Layout.PADDING_LG, y_offset))
        y_offset += Layout.LINE_HEIGHT + Layout.ELEMENT_GAP

        # Item type
        type_text = small_font.render(f"Type: {item.item_type.title()}", True, Colors.TEXT_SECONDARY)
        surface.blit(type_text, (panel_x + Layout.PADDING_LG, y_offset))
        y_offset += Layout.LINE_HEIGHT_COMPACT

        # Quantity
        max_stack_text = f" / {item.max_stack_size}" if item.max_stack_size else ""
        qty_text = small_font.render(f"Quantity: {quantity}{max_stack_text}", True, Colors.TEXT_SECONDARY)
        surface.blit(qty_text, (panel_x + Layout.PADDING_LG, y_offset))
        y_offset += Layout.LINE_HEIGHT_COMPACT

        # Value
        if item.value > 0:
            value_text = small_font.render(f"Value: {item.value} gold", True, Colors.ACCENT)
            surface.blit(value_text, (panel_x + Layout.PADDING_LG, y_offset))
            y_offset += Layout.LINE_HEIGHT_COMPACT

        y_offset += Layout.ELEMENT_GAP

        # Description (wrapped)
        desc_lines = self._wrap_text(item.description, small_font, panel_width - Layout.PADDING_LG * 2)
        for line in desc_lines:
            desc_text = small_font.render(line, True, Colors.TEXT_SECONDARY)
            surface.blit(desc_text, (panel_x + Layout.PADDING_LG, y_offset))
            y_offset += Layout.LINE_HEIGHT_COMPACT
            if y_offset > panel_y + panel_height - Layout.PADDING_XL * 2:
                break

        # Stat modifiers
        if item.stat_modifiers:
            y_offset += Layout.ELEMENT_GAP
            mod_header = small_font.render("Stat Modifiers:", True, (150, 200, 255))
            surface.blit(mod_header, (panel_x + Layout.PADDING_LG, y_offset))
            y_offset += Layout.LINE_HEIGHT_COMPACT
            for stat, value in item.stat_modifiers.items():
                sign = "+" if value >= 0 else ""
                color = (100, 255, 100) if value > 0 else (255, 100, 100)
                mod_text = small_font.render(f"  {stat.title()}: {sign}{value}", True, color)
                surface.blit(mod_text, (panel_x + Layout.PADDING_LG, y_offset))
                y_offset += Layout.LINE_HEIGHT_COMPACT - 2

        # Hotbar assignment
        hotbar_slot = self._get_hotbar_slot_for_item(item_id)
        if hotbar_slot:
            y_offset += Layout.ELEMENT_GAP
            hotbar_text = small_font.render(f"Hotbar: Slot {hotbar_slot}", True, (100, 255, 255))
            surface.blit(hotbar_text, (panel_x + Layout.PADDING_LG, y_offset))

    def _draw_hotbar(self, surface: pygame.Surface, font: pygame.font.Font, small_font: pygame.font.Font) -> None:
        """Draw the hotbar at the bottom."""
        if not self.player.inventory:
            return

        hotbar_x = Layout.SCREEN_MARGIN + 20
        hotbar_y = self.HOTBAR_Y
        slot_spacing = Layout.ELEMENT_GAP_SMALL

        # Hotbar label
        label_text = small_font.render("Hotbar:", True, Colors.TEXT_SECONDARY)
        surface.blit(label_text, (hotbar_x, hotbar_y - Layout.LINE_HEIGHT_COMPACT))

        for slot in range(1, 10):
            slot_x = hotbar_x + (slot - 1) * (self.HOTBAR_SLOT_WIDTH + slot_spacing)
            slot_rect = pygame.Rect(slot_x, hotbar_y, self.HOTBAR_SLOT_WIDTH, self.HOTBAR_SLOT_HEIGHT)

            # Slot background with rounded corners
            if self.mode == "hotbar" and self.hotbar_slot_selected == slot:
                pygame.draw.rect(surface, Colors.BG_PANEL, slot_rect, border_radius=Layout.CORNER_RADIUS_SMALL)
                pygame.draw.rect(surface, Colors.ACCENT, slot_rect, 2, border_radius=Layout.CORNER_RADIUS_SMALL)
            else:
                pygame.draw.rect(surface, Colors.BG_DARK, slot_rect, border_radius=Layout.CORNER_RADIUS_SMALL)
            pygame.draw.rect(surface, Colors.BORDER, slot_rect, 1, border_radius=Layout.CORNER_RADIUS_SMALL)

            # Slot number
            num_text = small_font.render(str(slot), True, Colors.TEXT_SECONDARY)
            num_rect = num_text.get_rect(center=(slot_x + self.HOTBAR_SLOT_WIDTH // 2, hotbar_y + 10))
            surface.blit(num_text, num_rect)

            # Item in slot
            item_id = self.player.inventory.get_hotbar_item(slot)
            if item_id:
                item = self.items_db.get(item_id)
                if item:
                    qty = self.player.inventory.get_quantity(item_id)
                    item_name = item.name[:7]  # Truncate long names
                    item_text = small_font.render(item_name, True, Colors.TEXT_PRIMARY)
                    surface.blit(item_text, (slot_x + 2, hotbar_y + 18))
                    qty_text = small_font.render(f"x{qty}", True, Colors.TEXT_SECONDARY)
                    surface.blit(qty_text, (slot_x + 2, hotbar_y + 28))

    def _wrap_text(self, text: str, font: pygame.font.Font, max_width: int) -> List[str]:
        """Wrap text to fit within max_width."""
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            test_line = " ".join(current_line + [word])
            test_width = font.size(test_line)[0]
            if test_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]

        if current_line:
            lines.append(" ".join(current_line))

        return lines if lines else [text]

    def _draw_help_text(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        """Draw standardized help text at the bottom of the screen."""
        if self.mode == "hotbar":
            help_text = "1-9: Assign to Slot  |  ESC: Cancel"
        else:
            help_text = "Up/Down: Select  |  S: Sort  |  F: Filter  |  H: Hotbar  |  ESC: Close"

        draw_contextual_help(surface, help_text, font, margin_bottom=Layout.SCREEN_MARGIN)
