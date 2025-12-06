"""Battle HUD rendering logic.

This module contains HUD rendering components for battle scenes,
including HP/SP bars, status icons, menus, hotbar, and message box.
"""

from typing import Dict, List, Optional, Tuple, TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from core.combat import BattleState

from ..theme import Colors, Layout
from ..ui import draw_hp_bar, draw_sp_bar, draw_status_icons
from ..ui.utils import draw_rounded_panel

# Semi-transparent panel background color used across HUD elements
_PANEL_BG = (20, 25, 40, 180)


class BattleHudMixin:
    """Mixin providing HUD rendering logic for BattleScene.

    This mixin handles:
    - Party member HP/SP bars and status icons
    - Enemy HP bars and phase indicators
    - Menu panel rendering
    - Hotbar rendering
    - Message box rendering
    - Status icon collection

    Attributes expected from host class:
        battle_system: BattleSystem instance
        player: Player entity
        assets: AssetManager for sprites/fonts
        main_menu, skill_menu, etc.: Menu instances
        message_box: MessageBox for battle messages
        menu_mode: Current menu state string
        panel: NineSlice panel for UI backgrounds
        items_db: Item database
        status_icon_map: Mapping of status IDs to sprite IDs
        sprite_size, draw_size: Sprite dimensions
    """

    # Panel layout constants (shared across all HUD methods)
    _PANEL_PADDING = 8
    _PANEL_ELEMENT_GAP = 6
    _PANEL_BAR_HEIGHT = 4

    def _get_party_panel_size(self, participant, font) -> Tuple[int, int]:
        """Calculate the dimensions of the unified party member panel."""
        if not participant.stats or not font:
            return 0, 0

        # Use class constants for panel layout
        panel_padding = self._PANEL_PADDING
        element_gap = self._PANEL_ELEMENT_GAP
        bar_height = self._PANEL_BAR_HEIGHT

        content_width = 0
        content_height = 0

        # 1. Name
        name_text = participant.entity.name
        w, h = font.size(name_text)
        content_width = max(content_width, w)
        content_height += h

        # 2. HP Numbers
        hp_text = f"{participant.stats.hp}/{participant.stats.max_hp}"
        w, h = font.size(hp_text)
        content_width = max(content_width, w)
        content_height += element_gap
        content_height += h

        # 3. HP Bar
        content_height += element_gap
        content_height += bar_height

        # 4. SP (if applicable)
        has_sp = participant.stats.max_sp > 0
        if has_sp:
            sp_text = f"{participant.stats.sp}/{participant.stats.max_sp}"
            w, h = font.size(sp_text)
            content_width = max(content_width, w)
            content_height += element_gap
            content_height += h
            content_height += element_gap
            content_height += bar_height

        # 5. Status Icons
        icons = self._collect_status_icons(participant.stats.status_effects)
        if icons:
            icon_spacing = getattr(Layout, "ICON_GAP", 4)
            icon_size = icons[0].get_width()
            icons_width = len(icons) * icon_size
            if len(icons) > 1:
                icons_width += icon_spacing * (len(icons) - 1)
            content_width = max(content_width, icons_width)
            content_height += element_gap
            content_height += icon_size

        # Calculate final panel dimensions
        panel_width = max(content_width + panel_padding * 2, self.draw_size + 20)
        panel_height = content_height + panel_padding * 2

        return panel_width, panel_height

    def _draw_party_hud(self, surface: pygame.Surface, font) -> None:
        """Draw party member information in a unified panel above each ally sprite.

        Uses the same visual pattern as enemy HUD for consistency.
        """
        # Get ally positions synced with sprite rendering
        ally_base_x, ally_y = self._get_ally_base_position()
        spacing = self._get_ally_spacing()
        offset_x, offset_y = getattr(self, "screen_shake_offset", (0, 0))

        # Iterate alive allies only - matches sprite rendering order
        alive_allies = self._alive_allies()
        for idx, participant in enumerate(alive_allies):
            if not participant.stats:
                continue

            # Calculate position based on index (synced with sprite rendering)
            ally_x = ally_base_x + idx * spacing
            render_x = ally_x + offset_x
            render_y = ally_y + offset_y

            if not font:
                continue

            # Get panel size using the helper
            panel_width, panel_height = self._get_party_panel_size(participant, font)

            # Use class constants for panel layout
            panel_padding = self._PANEL_PADDING
            element_gap = self._PANEL_ELEMENT_GAP
            bar_height = self._PANEL_BAR_HEIGHT

            # Position panel centered above ally sprite
            panel_x = render_x + (self.draw_size - panel_width) // 2
            panel_y = render_y - panel_height - 8  # 8px gap above sprite

            # Draw unified panel background
            panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
            if self.panel:
                self.panel.draw(surface, panel_rect)
            else:
                draw_rounded_panel(
                    surface,
                    panel_rect,
                    _PANEL_BG,
                    Colors.BORDER,
                    border_width=Layout.BORDER_WIDTH_THIN,
                    radius=Layout.CORNER_RADIUS_SMALL
                )

            # Draw elements vertically stacked
            current_y = panel_y + panel_padding

            # 1. Name
            name_text = participant.entity.name
            name_shadow = font.render(name_text, True, (0, 0, 0))
            name_surf = font.render(name_text, True, (255, 255, 255))

            element_x = panel_x + (panel_width - name_surf.get_width()) // 2
            surface.blit(name_shadow, (element_x + 1, current_y + 1))
            surface.blit(name_surf, (element_x, current_y))
            current_y += name_surf.get_height() + element_gap

            # 2. HP Numbers
            hp_text = f"{participant.stats.hp}/{participant.stats.max_hp}"
            hp_shadow = font.render(hp_text, True, (0, 0, 0))
            hp_surf = font.render(hp_text, True, (255, 255, 255))

            element_x = panel_x + (panel_width - hp_surf.get_width()) // 2
            surface.blit(hp_shadow, (element_x + 1, current_y + 1))
            surface.blit(hp_surf, (element_x, current_y))
            current_y += hp_surf.get_height() + element_gap

            # 3. HP Bar
            bar_x = panel_x + panel_padding
            bar_width = panel_width - panel_padding * 2
            draw_hp_bar(
                surface,
                bar_x,
                current_y,
                bar_width,
                bar_height,
                participant.stats.hp,
                participant.stats.max_hp,
                "",
                font=font,
                show_text=False
            )
            current_y += bar_height + element_gap

            # 4. SP (if applicable)
            has_sp = participant.stats.max_sp > 0
            if has_sp:
                sp_text = f"{participant.stats.sp}/{participant.stats.max_sp}"
                sp_shadow = font.render(sp_text, True, (0, 0, 0))
                sp_surf = font.render(sp_text, True, (100, 150, 255))

                element_x = panel_x + (panel_width - sp_surf.get_width()) // 2
                surface.blit(sp_shadow, (element_x + 1, current_y + 1))
                surface.blit(sp_surf, (element_x, current_y))
                current_y += sp_surf.get_height() + element_gap

                draw_sp_bar(
                    surface,
                    bar_x,
                    current_y,
                    bar_width,
                    bar_height,
                    participant.stats.sp,
                    participant.stats.max_sp,
                    "",
                    font=font,
                    show_text=False
                )
                current_y += bar_height + element_gap

            # 5. Status Icons
            icons = self._collect_status_icons(participant.stats.status_effects)
            if icons:
                icon_spacing = getattr(Layout, "ICON_GAP", 4)
                icon_size = icons[0].get_width()
                icons_width = len(icons) * icon_size
                if len(icons) > 1:
                    icons_width += icon_spacing * (len(icons) - 1)

                icons_x = panel_x + (panel_width - icons_width) // 2
                draw_status_icons(
                    surface,
                    icons,
                    (icons_x, current_y)
                )

    def _get_enemy_panel_size(self, enemy, font) -> Tuple[int, int]:
        """Calculate the dimensions of the unified enemy panel."""
        if not enemy.is_alive() or not enemy.stats or not font:
            return 0, 0

        # Use class constants for panel layout
        panel_padding = self._PANEL_PADDING
        element_gap = self._PANEL_ELEMENT_GAP
        bar_height = self._PANEL_BAR_HEIGHT

        content_width = 0
        content_height = 0

        # 1. Phase indicator
        if enemy.current_phase:
            phase_text = enemy.current_phase.upper()
            w, h = font.size(phase_text)
            content_width = max(content_width, w)
            content_height += h

        # 2. Name
        name_text = enemy.entity.name
        w, h = font.size(name_text)
        content_width = max(content_width, w)
        if content_height > 0:
            content_height += element_gap
        content_height += h

        # 3. HP Numbers
        hp_text = f"{enemy.stats.hp}/{enemy.stats.max_hp}"
        w, h = font.size(hp_text)
        content_width = max(content_width, w)
        content_height += element_gap
        content_height += h

        # 4. HP Bar
        content_height += element_gap
        content_height += bar_height

        # 5. Status Icons
        icons = self._collect_status_icons(enemy.stats.status_effects)
        if icons:
            icon_spacing = getattr(Layout, "ICON_GAP", 4)
            icon_size = icons[0].get_width()
            icons_width = len(icons) * icon_size
            if len(icons) > 1:
                icons_width += icon_spacing * (len(icons) - 1)
            content_width = max(content_width, icons_width)
            content_height += element_gap
            content_height += icon_size

        # Calculate final panel dimensions
        panel_width = max(content_width + panel_padding * 2, self.sprite_size + 20)
        panel_height = content_height + panel_padding * 2

        return panel_width, panel_height

    def _draw_enemy_hud(self, surface: pygame.Surface, font) -> None:
        """Draw enemy information in a single unified panel above each enemy sprite."""
        # Use layout mixin methods to ensure sync with sprite rendering
        enemy_x, enemy_y = self._get_enemy_base_position()
        spacing = self._get_enemy_spacing()
        offset_x, offset_y = getattr(self, "screen_shake_offset", (0, 0))

        for enemy in self.battle_system.enemies:
            if enemy.is_alive() and enemy.stats:
                render_x = enemy_x + offset_x
                render_y = enemy_y + offset_y

                if not font:
                    enemy_x += spacing
                    continue

                # Get panel size using the helper
                panel_width, panel_height = self._get_enemy_panel_size(enemy, font)

                # Use class constants for panel layout
                panel_padding = self._PANEL_PADDING
                element_gap = self._PANEL_ELEMENT_GAP
                bar_height = self._PANEL_BAR_HEIGHT

                # Position panel centered above enemy sprite
                panel_x = render_x + (self.sprite_size - panel_width) // 2
                panel_y = render_y - panel_height - 8  # 8px gap above sprite

                # Draw unified panel background
                panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
                if self.panel:
                    self.panel.draw(surface, panel_rect)
                else:
                    draw_rounded_panel(
                        surface,
                        panel_rect,
                        _PANEL_BG,
                        Colors.BORDER,
                        border_width=Layout.BORDER_WIDTH_THIN,
                        radius=Layout.CORNER_RADIUS_SMALL
                    )

                # Draw elements
                current_y = panel_y + panel_padding

                # 1. Phase
                if enemy.current_phase:
                    phase_text = enemy.current_phase.upper()
                    phase_shadow = font.render(phase_text, True, (0, 0, 0))
                    phase_surf = font.render(phase_text, True, (255, 200, 100))

                    element_x = panel_x + (panel_width - phase_surf.get_width()) // 2
                    surface.blit(phase_shadow, (element_x + 1, current_y + 1))
                    surface.blit(phase_surf, (element_x, current_y))
                    current_y += phase_surf.get_height()

                # 2. Name
                name_text = enemy.entity.name
                name_shadow = font.render(name_text, True, (0, 0, 0))
                name_surf = font.render(name_text, True, (255, 255, 255))

                if enemy.current_phase:
                     current_y += element_gap

                element_x = panel_x + (panel_width - name_surf.get_width()) // 2
                surface.blit(name_shadow, (element_x + 1, current_y + 1))
                surface.blit(name_surf, (element_x, current_y))
                current_y += name_surf.get_height() + element_gap

                # 3. HP Numbers
                hp_text = f"{enemy.stats.hp}/{enemy.stats.max_hp}"
                hp_shadow = font.render(hp_text, True, (0, 0, 0))
                hp_surf = font.render(hp_text, True, (255, 255, 255))

                element_x = panel_x + (panel_width - hp_surf.get_width()) // 2
                surface.blit(hp_shadow, (element_x + 1, current_y + 1))
                surface.blit(hp_surf, (element_x, current_y))
                current_y += hp_surf.get_height() + element_gap

                # 4. HP Bar
                bar_x = panel_x + panel_padding
                bar_width = panel_width - panel_padding * 2
                draw_hp_bar(
                    surface,
                    bar_x,
                    current_y,
                    bar_width,
                    bar_height,
                    enemy.stats.hp,
                    enemy.stats.max_hp,
                    "",
                    font=font,
                    show_text=False
                )
                current_y += bar_height + element_gap

                # 5. Status Icons
                icons = self._collect_status_icons(enemy.stats.status_effects)
                if icons:
                    # Calculate total width of icons to center them
                    icon_spacing = getattr(Layout, "ICON_GAP", 4)
                    icon_size = icons[0].get_width()
                    icons_width = len(icons) * icon_size
                    if len(icons) > 1:
                        icons_width += icon_spacing * (len(icons) - 1)

                    icons_x = panel_x + (panel_width - icons_width) // 2
                    draw_status_icons(
                        surface,
                        icons,
                        (icons_x, current_y)
                    )

            enemy_x += spacing

    def _draw_menus(self, surface: pygame.Surface, font, message_box_y: Optional[int] = None) -> None:
        """Draw the active battle menu.

        Args:
            surface: Surface to draw on
            font: Font to use for rendering
            message_box_y: Pre-calculated message box Y position (if None, uses current position)
        """
        from core.combat import BattleState

        if self.battle_system.state != BattleState.PLAYER_CHOOSE:
            return

        # Determine which menu to draw and calculate panel dimensions
        active_menu = None
        if self.menu_mode == "main":
            active_menu = self.main_menu
        elif self.menu_mode == "skill" and self.skill_menu:
            active_menu = self.skill_menu
        elif self.menu_mode == "item" and self.item_menu:
            active_menu = self.item_menu
        elif self.menu_mode == "move" and self.move_menu:
            active_menu = self.move_menu
        elif self.menu_mode == "memory" and self.memory_menu:
            active_menu = self.memory_menu
        elif self.menu_mode == "memory_stat" and self.memory_stat_menu:
            active_menu = self.memory_stat_menu

        if not active_menu:
            return

        # Use pre-calculated message box position if provided, otherwise get current position
        width, height = surface.get_size()
        if message_box_y is None:
            # Fallback: get current message box position
            if hasattr(self, 'combat_log') and self.combat_log:
                message_box_y = self.combat_log.position[1]
            else:
                message_box_y = self.message_box.position[1]

        # Recalculate menu position if it's the main menu
        if self.menu_mode == "main" and active_menu == self.main_menu:
            new_menu_pos = self._get_main_menu_position(
                screen_height=height,
                message_box_y=message_box_y,
                screen_width=width,
            )
            active_menu.position = new_menu_pos

        # Calculate menu panel dimensions based on menu content
        menu_x, menu_y = active_menu.position
        num_options = len(active_menu.options)
        line_height = Layout.MENU_ITEM_HEIGHT_COMPACT  # Use compact height for tighter fit

        # Panel dimensions - sized to fit content tightly
        panel_padding_v = 8  # Vertical padding (top/bottom)
        panel_padding_h = 12  # Horizontal padding (left/right)
        panel_height = num_options * line_height + panel_padding_v * 2

        # Differentiate between main menu (sidebar) and submenus (near player)
        is_main_menu = (self.menu_mode == "main")

        if is_main_menu:
            # Main menu: fixed width, flush with right edge
            panel_width = 120
            panel_x = width - panel_width  # Flush with right edge
            panel_y = menu_y - panel_padding_v
        else:
            # Submenus: dynamic width based on content, positioned near player
            max_text_width = 0
            if font:
                for option in active_menu.options:
                    text_width = font.size(option)[0]
                    max_text_width = max(max_text_width, text_width)
            else:
                max_text_width = 150
            panel_width = max_text_width + panel_padding_h * 2 + 30  # Extra for cursor
            panel_x = menu_x - panel_padding_h - 15  # Offset for cursor space
            panel_y = menu_y - panel_padding_v

        # Draw semi-transparent dark panel behind menu
        if self.panel:
            # Use 9-slice panel if available
            self.panel.draw(surface, pygame.Rect(panel_x, panel_y, panel_width, panel_height))
        else:
            # Fallback: draw panel matching weather/time styling
            panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
            draw_rounded_panel(
                surface,
                panel_rect,
                _PANEL_BG,
                Colors.BORDER,
                border_width=Layout.BORDER_WIDTH_THIN,
                radius=Layout.CORNER_RADIUS_SMALL
            )

        # Draw the menu on top of the panel
        active_menu.draw(surface, font)

    def _draw_message_box(self, surface: pygame.Surface, font, precalculated_position: Optional[Tuple[int, int]] = None) -> None:
        """Draw the battle message box or combat log.

        Args:
            surface: Surface to draw on
            font: Font to use for rendering
            precalculated_position: Pre-calculated position tuple (x, y) to use (if None, calculates dynamically)
        """
        # Use pre-calculated position if provided, otherwise calculate dynamically
        if precalculated_position is None:
            width, height = surface.get_size()
            if hasattr(self, 'combat_log') and self.combat_log:
                message_box_height = self.combat_log.expanded_height if self.combat_log.expanded else self.combat_log.collapsed_height
            else:
                message_box_height = self.message_box.height
            precalculated_position = self._get_message_box_position(
                screen_height=height,
                message_box_height=message_box_height
            )

        # Use combat log if available, otherwise fall back to message box
        if hasattr(self, 'combat_log') and self.combat_log:
            self.combat_log.position = precalculated_position
            self.combat_log.draw(surface, font, panel=self.panel)
        else:
            self.message_box.position = precalculated_position
            self.message_box.draw(surface, font, panel=self.panel)

    def _draw_hotbar(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        """Draw the hotbar at the bottom of the screen, flush with left edge."""
        if not self.player.inventory:
            return

        width, height = surface.get_size()
        hotbar_y = height - 50
        hotbar_x = 0  # Flush with left edge
        slot_width = 50
        slot_height = 40
        slot_spacing = 5

        # Calculate hotbar width to match message box (flush with menu panel)
        menu_panel_width = 120
        hotbar_total_width = width - menu_panel_width

        # Draw hotbar background - extends to match message box width
        hotbar_bg_rect = pygame.Rect(
            hotbar_x,
            hotbar_y - 5,
            hotbar_total_width,
            slot_height + 10
        )
        if self.panel:
            self.panel.draw(surface, hotbar_bg_rect)
        else:
            # Draw semi-transparent hotbar background with rounded corners matching weather/time styling
            draw_rounded_panel(
                surface,
                hotbar_bg_rect,
                _PANEL_BG,
                Colors.BORDER,
                border_width=Layout.BORDER_WIDTH_THIN,
                radius=Layout.CORNER_RADIUS_SMALL
            )

        # Draw each hotbar slot with padding from left edge
        slot_padding_left = 10  # Small padding from left edge
        for slot in range(1, 10):
            slot_x = slot_padding_left + (slot - 1) * (slot_width + slot_spacing)
            slot_rect = pygame.Rect(slot_x, hotbar_y, slot_width, slot_height)

            # Slot background with semi-transparent rounded corners matching weather/time styling
            draw_rounded_panel(
                surface,
                slot_rect,
                _PANEL_BG,
                Colors.BORDER,
                border_width=Layout.BORDER_WIDTH_THIN,
                radius=Layout.CORNER_RADIUS_SMALL
            )

            # Slot number (small, top-left)
            num_text = font.render(str(slot), True, (200, 200, 200))
            surface.blit(num_text, (slot_x + 2, hotbar_y + 2))

            # Item in slot
            item_id = self.player.inventory.get_hotbar_item(slot)
            if item_id:
                item = self.items_db.get(item_id)
                if item:
                    qty = self.player.inventory.get_quantity(item_id)
                    if qty > 0:
                        # Item name (truncated)
                        item_name = item.name[:6]  # Truncate to fit
                        name_text = font.render(item_name, True, (255, 255, 255))
                        name_rect = name_text.get_rect(center=(slot_x + slot_width // 2, hotbar_y + 15))
                        surface.blit(name_text, name_rect)

                        # Quantity
                        qty_text = font.render(f"x{qty}", True, (200, 200, 200))
                        qty_rect = qty_text.get_rect(center=(slot_x + slot_width // 2, hotbar_y + 28))
                        surface.blit(qty_text, qty_rect)
                    else:
                        # Item out of stock - gray out with semi-transparent overlay
                        out_overlay = pygame.Surface((slot_width, slot_height), pygame.SRCALPHA)
                        out_bg_color = (30, 30, 30, 180)
                        pygame.draw.rect(out_overlay, out_bg_color, (0, 0, slot_width, slot_height), border_radius=Layout.CORNER_RADIUS_SMALL)
                        surface.blit(out_overlay, slot_rect.topleft)
                        out_text = font.render("OUT", True, (150, 150, 150))
                        out_rect = out_text.get_rect(center=(slot_x + slot_width // 2, hotbar_y + slot_height // 2))
                        surface.blit(out_text, out_rect)

    def _collect_status_icons(self, status_effects: Dict[str, object]) -> List[pygame.Surface]:
        """Translate status IDs to icon surfaces."""
        icons: List[pygame.Surface] = []
        for status_id in status_effects.keys():
            sprite_id = self.status_icon_map.get(status_id)
            if sprite_id:
                icons.append(self.assets.get_image(sprite_id, (16, 16)))
        return icons

    def _draw_auto_battle_indicator(self, surface: pygame.Surface, font) -> None:
        """Draw auto-battle mode and speed indicator in top-right corner."""
        if not getattr(self, 'auto_battle', False):
            return

        width, height = surface.get_size()

        # Build indicator text
        speed = getattr(self, 'battle_speed', 1)
        if speed == 1:
            speed_text = "AUTO"
            indicator_color = (100, 200, 100)  # Green
        elif speed == 2:
            speed_text = "AUTO ▶▶ 2x"
            indicator_color = (200, 200, 100)  # Yellow
        else:  # speed == 4
            speed_text = "AUTO ▶▶▶▶ 4x"
            indicator_color = (255, 150, 100)  # Orange

        # Render text
        text_surf = font.render(speed_text, True, indicator_color)
        text_width = text_surf.get_width()
        text_height = text_surf.get_height()

        # Position in top-right corner with padding
        padding = 10
        x = width - text_width - padding - 10
        y = padding

        # Draw background panel with rounded corners
        bg_rect = pygame.Rect(x - 8, y - 4, text_width + 16, text_height + 8)
        bg_surf = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        bg_color = (20, 20, 30, 200)
        pygame.draw.rect(bg_surf, bg_color, (0, 0, bg_rect.width, bg_rect.height), border_radius=Layout.CORNER_RADIUS_SMALL)
        border_color = (*indicator_color[:3], 200) if len(indicator_color) == 3 else indicator_color
        pygame.draw.rect(bg_surf, border_color, (0, 0, bg_rect.width, bg_rect.height), Layout.BORDER_WIDTH, border_radius=Layout.CORNER_RADIUS_SMALL)
        surface.blit(bg_surf, bg_rect.topleft)

        # Draw text
        surface.blit(text_surf, (x, y))
