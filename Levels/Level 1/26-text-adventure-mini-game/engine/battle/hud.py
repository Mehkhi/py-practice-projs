"""Battle HUD rendering logic.

This module contains HUD rendering components for battle scenes,
including HP/SP bars, status icons, menus, hotbar, and message box.
"""

from typing import Dict, List, Optional, Tuple, TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from core.combat import BattleState

from ..theme import Colors, Layout


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

    def _draw_party_hud(self, surface: pygame.Surface, font) -> None:
        """
        Draw HP/SP bars for player and all party members.

        NOTE: User requested to remove the large HUD panel entirely and rely on
        the small indicators near the sprites. This method is now a no-op
        to fulfill that request while keeping the structure if needed later.
        """
        pass

    def _draw_enemy_hud(self, surface: pygame.Surface, font) -> None:
        """Draw enemy names and HP bars synced with sprite positions."""
        from ..ui import draw_hp_bar, draw_status_icons
        from ..theme import Colors

        # Use layout mixin methods to ensure sync with sprite rendering
        enemy_x, enemy_y = self._get_enemy_base_position()
        spacing = self._get_enemy_spacing()

        for enemy in self.battle_system.enemies:
            if enemy.is_alive() and enemy.stats:
                # Draw name above HP bar with proper transparency
                if font:
                    name_text = enemy.entity.name

                    # Render text with antialiasing - pygame should handle transparency
                    # Draw shadow first (offset by 1 pixel)
                    shadow_surf = font.render(name_text, True, (0, 0, 0))
                    name_surf = font.render(name_text, True, (255, 255, 255))

                    # Center above sprite
                    name_x = enemy_x + (self.sprite_size - name_surf.get_width()) // 2
                    name_y = enemy_y - 35

                    # Blit shadow then text
                    surface.blit(shadow_surf, (name_x + 1, name_y + 1))
                    surface.blit(name_surf, (name_x, name_y))

                    # Draw HP numbers below name
                    hp_text = f"{enemy.stats.hp}/{enemy.stats.max_hp}"
                    hp_shadow = font.render(hp_text, True, (0, 0, 0))
                    hp_surf = font.render(hp_text, True, (255, 255, 255))
                    hp_x = enemy_x + (self.sprite_size - hp_surf.get_width()) // 2
                    hp_y = enemy_y - 22
                    surface.blit(hp_shadow, (hp_x + 1, hp_y + 1))
                    surface.blit(hp_surf, (hp_x, hp_y))

                # Draw HP bar above enemy (smaller, no text)
                draw_hp_bar(
                    surface,
                    enemy_x,
                    enemy_y - 8,
                    self.sprite_size,
                    4,
                    enemy.stats.hp,
                    enemy.stats.max_hp,
                    "",
                    font=font,
                    show_text=False
                )

                # Draw phase indicator if enemy has a phase
                if enemy.current_phase:
                    phase_y = enemy_y - 50
                    phase_text = enemy.current_phase.upper()
                    phase_surf = font.render(phase_text, True, (255, 200, 100))
                    surface.blit(phase_surf, (enemy_x, phase_y))

                # Draw status icons below sprite
                icons = self._collect_status_icons(enemy.stats.status_effects)
                if icons:
                    draw_status_icons(
                        surface,
                        icons,
                        (enemy_x, enemy_y + self.sprite_size + 5)
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
                message_box_y=message_box_y
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
            # Fallback: draw a semi-transparent dark rectangle with border and rounded corners
            panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
            bg_color = (20, 20, 30, 220)  # Dark blue-gray with high opacity
            pygame.draw.rect(panel_surface, bg_color, (0, 0, panel_width, panel_height), border_radius=Layout.CORNER_RADIUS)
            border_color = (*Colors.ACCENT[:3], 220)
            pygame.draw.rect(panel_surface, border_color, (0, 0, panel_width, panel_height), Layout.BORDER_WIDTH, border_radius=Layout.CORNER_RADIUS)
            surface.blit(panel_surface, (panel_x, panel_y))

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
            # Draw semi-transparent hotbar background with rounded corners
            hotbar_surface = pygame.Surface((hotbar_bg_rect.width, hotbar_bg_rect.height), pygame.SRCALPHA)
            bg_color = (40, 40, 50, 200)
            pygame.draw.rect(hotbar_surface, bg_color, (0, 0, hotbar_bg_rect.width, hotbar_bg_rect.height), border_radius=Layout.CORNER_RADIUS_SMALL)
            border_color = (100, 100, 120, 200)
            pygame.draw.rect(hotbar_surface, border_color, (0, 0, hotbar_bg_rect.width, hotbar_bg_rect.height), Layout.BORDER_WIDTH, border_radius=Layout.CORNER_RADIUS_SMALL)
            surface.blit(hotbar_surface, hotbar_bg_rect.topleft)

        # Draw each hotbar slot with padding from left edge
        slot_padding_left = 10  # Small padding from left edge
        for slot in range(1, 10):
            slot_x = slot_padding_left + (slot - 1) * (slot_width + slot_spacing)
            slot_rect = pygame.Rect(slot_x, hotbar_y, slot_width, slot_height)

            # Slot background
            pygame.draw.rect(surface, (50, 50, 60), slot_rect)
            pygame.draw.rect(surface, (100, 100, 120), slot_rect, 1)

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
                        # Item out of stock - gray out
                        pygame.draw.rect(surface, (30, 30, 30, 180), slot_rect)
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
