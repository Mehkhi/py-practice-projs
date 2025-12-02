"""Battle HUD rendering logic.

This module contains HUD rendering components for battle scenes,
including HP/SP bars, status icons, menus, hotbar, and message box.
"""

from typing import Dict, List, Optional, Tuple, TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from core.combat import BattleState


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
        """Draw HP/SP bars for player and all party members with improved spacing."""
        from ..ui import draw_hp_bar, draw_sp_bar, draw_status_icons
        from ..theme import Colors, Layout

        hud_x = Layout.HUD_MARGIN
        hud_y = Layout.HUD_MARGIN
        bar_width = 180
        bar_height = Layout.BAR_HEIGHT
        sp_bar_width = 70
        row_height = Layout.HUD_ROW_HEIGHT
        bar_gap = Layout.BAR_GAP

        # Draw player stats
        if self.player.stats:
            # Player name label with subtle background
            if font:
                name_text = font.render(self.player.name, True, Colors.TEXT_PRIMARY)
                name_shadow = font.render(self.player.name, True, Colors.BG_DARK)
                surface.blit(name_shadow, (hud_x + 1, hud_y + 1))
                surface.blit(name_text, (hud_x, hud_y))

            # HP bar positioned below name
            bar_y = hud_y + Layout.HUD_NAME_HEIGHT + Layout.ELEMENT_GAP_SMALL
            draw_hp_bar(
                surface, hud_x, bar_y, bar_width, bar_height,
                self.player.stats.hp, self.player.stats.max_hp, "",
                font=font, show_text=False,
            )

            # SP bar with proper gap
            draw_sp_bar(
                surface, hud_x + bar_width + bar_gap, bar_y, sp_bar_width, bar_height,
                self.player.stats.sp, self.player.stats.max_sp, "",
                font=font, show_text=False,
            )

            # HP/SP text overlay on bars
            if font:
                hp_text = font.render(f"{self.player.stats.hp}/{self.player.stats.max_hp}", True, Colors.WHITE)
                sp_text = font.render(f"{self.player.stats.sp}", True, Colors.WHITE)
                # Center text on bars
                hp_text_x = hud_x + (bar_width - hp_text.get_width()) // 2
                sp_text_x = hud_x + bar_width + bar_gap + (sp_bar_width - sp_text.get_width()) // 2
                surface.blit(hp_text, (hp_text_x, bar_y + (bar_height - hp_text.get_height()) // 2))
                surface.blit(sp_text, (sp_text_x, bar_y + (bar_height - sp_text.get_height()) // 2))

            # Status icons
            icons = self._collect_status_icons(self.player.stats.status_effects)
            if icons:
                icon_x = hud_x + bar_width + bar_gap + sp_bar_width + bar_gap
                draw_status_icons(surface, icons, (icon_x, bar_y))

            hud_y += row_height

        # Draw party member stats
        for member in getattr(self.player, "party", []):
            if not member or not member.stats:
                continue

            # Dim color for dead members
            is_alive = member.is_alive()
            name_color = Colors.TEXT_PRIMARY if is_alive else Colors.TEXT_DISABLED

            if font:
                name_text = font.render(member.name, True, name_color)
                name_shadow = font.render(member.name, True, Colors.BG_DARK)
                surface.blit(name_shadow, (hud_x + 1, hud_y + 1))
                surface.blit(name_text, (hud_x, hud_y))

            bar_y = hud_y + Layout.HUD_NAME_HEIGHT + Layout.ELEMENT_GAP_SMALL
            draw_hp_bar(
                surface, hud_x, bar_y, bar_width, bar_height,
                member.stats.hp, member.stats.max_hp, "",
                font=font, show_text=False,
            )
            draw_sp_bar(
                surface, hud_x + bar_width + bar_gap, bar_y, sp_bar_width, bar_height,
                member.stats.sp, member.stats.max_sp, "",
                font=font, show_text=False,
            )

            # HP/SP text overlay
            if font:
                hp_text = font.render(f"{member.stats.hp}/{member.stats.max_hp}", True, Colors.WHITE)
                sp_text = font.render(f"{member.stats.sp}", True, Colors.WHITE)
                hp_text_x = hud_x + (bar_width - hp_text.get_width()) // 2
                sp_text_x = hud_x + bar_width + bar_gap + (sp_bar_width - sp_text.get_width()) // 2
                surface.blit(hp_text, (hp_text_x, bar_y + (bar_height - hp_text.get_height()) // 2))
                surface.blit(sp_text, (sp_text_x, bar_y + (bar_height - sp_text.get_height()) // 2))

            icons = self._collect_status_icons(member.stats.status_effects)
            if icons:
                icon_x = hud_x + bar_width + bar_gap + sp_bar_width + bar_gap
                draw_status_icons(surface, icons, (icon_x, bar_y))

            hud_y += row_height

    def _draw_enemy_hud(self, surface: pygame.Surface, font) -> None:
        """Draw enemy names and HP bars."""
        from ..ui import draw_hp_bar, draw_status_icons

        enemy_x = 120
        enemy_y = 120

        for enemy in self.battle_system.enemies:
            if enemy.is_alive() and enemy.stats:
                # Draw HP bar above enemy
                draw_hp_bar(
                    surface,
                    enemy_x,
                    enemy_y - 20,
                    self.sprite_size,
                    8,
                    enemy.stats.hp,
                    enemy.stats.max_hp,
                    "",  # No label to save space
                    font=font,
                )

                # Draw phase indicator if enemy has a phase
                if enemy.current_phase:
                    phase_y = enemy_y - 35
                    phase_text = enemy.current_phase.upper()
                    phase_surf = font.render(phase_text, True, (255, 200, 100))
                    # Draw background for phase indicator
                    phase_bg_rect = pygame.Rect(
                        enemy_x - 2,
                        phase_y - 2,
                        phase_surf.get_width() + 4,
                        phase_surf.get_height() + 4
                    )
                    phase_bg = pygame.Surface((phase_bg_rect.width, phase_bg_rect.height), pygame.SRCALPHA)
                    phase_bg.fill((40, 20, 10, 200))
                    surface.blit(phase_bg, phase_bg_rect.topleft)
                    # Draw phase text with outline
                    outline_surf = font.render(phase_text, True, (0, 0, 0))
                    for ox, oy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        surface.blit(outline_surf, (enemy_x + ox, phase_y + oy))
                    surface.blit(phase_surf, (enemy_x, phase_y))

                # Draw status icons below
                icons = self._collect_status_icons(enemy.stats.status_effects)
                if icons:
                    draw_status_icons(
                        surface,
                        icons,
                        (enemy_x, enemy_y + self.sprite_size + 5)
                    )

            enemy_x += self.draw_size + 40

    def _draw_menus(self, surface: pygame.Surface, font, message_box_y: Optional[int] = None) -> None:
        """Draw the active battle menu.

        Args:
            surface: Surface to draw on
            font: Font to use for rendering
            message_box_y: Pre-calculated message box Y position (if None, uses current position)
        """
        from core.combat import BattleState
        from ..theme import Colors, Layout

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
        line_height = Layout.MENU_ITEM_HEIGHT

        # Calculate max text width for panel sizing
        max_width = 0
        if font:
            for option in active_menu.options:
                text_width = font.size(option)[0]
                max_width = max(max_width, text_width)
        else:
            max_width = 150  # Default width

        # Panel dimensions with padding
        panel_padding = 16
        panel_width = max_width + panel_padding * 2 + 30  # Extra space for cursor
        panel_height = num_options * line_height + panel_padding * 2

        # Panel position (offset from menu position to account for cursor space)
        panel_x = menu_x - 25
        panel_y = menu_y - panel_padding // 2

        # Draw semi-transparent dark panel behind menu
        if self.panel:
            # Use 9-slice panel if available
            self.panel.draw(surface, pygame.Rect(panel_x, panel_y, panel_width, panel_height))
        else:
            # Fallback: draw a semi-transparent dark rectangle with border
            panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
            panel_surface.fill((20, 20, 30, 220))  # Dark blue-gray with high opacity
            surface.blit(panel_surface, (panel_x, panel_y))

            # Draw border
            border_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
            pygame.draw.rect(surface, Colors.ACCENT, border_rect, 2)

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
        """Draw the hotbar at the bottom of the screen."""
        if not self.player.inventory:
            return

        width, height = surface.get_size()
        hotbar_y = height - 50
        hotbar_x = 20
        slot_width = 50
        slot_height = 40
        slot_spacing = 5

        # Draw hotbar background
        hotbar_bg_rect = pygame.Rect(
            hotbar_x - 5,
            hotbar_y - 5,
            9 * (slot_width + slot_spacing) - slot_spacing + 10,
            slot_height + 10
        )
        if self.panel:
            self.panel.draw(surface, hotbar_bg_rect)
        else:
            pygame.draw.rect(surface, (40, 40, 50, 200), hotbar_bg_rect)
            pygame.draw.rect(surface, (100, 100, 120), hotbar_bg_rect, 2)

        # Draw each hotbar slot
        for slot in range(1, 10):
            slot_x = hotbar_x + (slot - 1) * (slot_width + slot_spacing)
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

        # Draw background panel
        bg_rect = pygame.Rect(x - 8, y - 4, text_width + 16, text_height + 8)
        bg_surf = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        bg_surf.fill((20, 20, 30, 200))
        surface.blit(bg_surf, bg_rect.topleft)

        # Draw border
        pygame.draw.rect(surface, indicator_color, bg_rect, 2)

        # Draw text
        surface.blit(text_surf, (x, y))
