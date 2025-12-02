"""Battle UI layout mixin for sizing and positioning logic."""

from typing import Tuple, Optional

from ..theme import Layout


class BattleUILayoutMixin:
    """Mixin providing standardized sizing and positioning for battle UI."""

    def _init_battle_sizing(self) -> None:
        """Initialize sprite sizing based on current scale."""
        # Base sprite size before scaling; BattleScene sets self.scale first
        self.sprite_size = 32
        self.draw_size = self.sprite_size * self.scale

    @staticmethod
    def _get_main_menu_position(screen_height: Optional[int] = None, message_box_y: Optional[int] = None) -> Tuple[int, int]:
        """Position for the main battle menu.

        Positions menu flush with right edge and bottom corner, adjacent to message box.

        Args:
            screen_height: Height of the screen surface (defaults to Layout.SCREEN_HEIGHT if None)
            message_box_y: Y position of the message box (if None, uses default calculation)

        Returns:
            Tuple of (x, y) position for the main menu
        """
        if screen_height is None:
            screen_height = Layout.SCREEN_HEIGHT

        # Calculate message box position if not provided
        if message_box_y is None:
            _, message_box_y = BattleUILayoutMixin._get_message_box_position(screen_height)

        # Menu panel width (will be calculated in hud.py, but estimate for text position)
        menu_panel_width = 120

        # Position menu text inside the panel (panel extends to right edge)
        # Text starts with padding from the panel's left edge
        menu_x = Layout.SCREEN_WIDTH - menu_panel_width + 25  # 25px padding from panel left

        # Calculate menu height: 8 options * compact line height + padding
        num_options = 8
        line_height = 28  # MENU_ITEM_HEIGHT_COMPACT
        panel_padding_v = 8  # Vertical padding in panel
        menu_height = num_options * line_height + panel_padding_v * 2

        # Position menu so panel bottom is flush with screen bottom
        # Menu text starts with padding offset from panel top
        menu_y = screen_height - menu_height + panel_padding_v

        return (menu_x, menu_y)

    @staticmethod
    def _get_submenu_position(screen_height: Optional[int] = None) -> Tuple[int, int]:
        """Position for battle submenus (move, skill, item selection).

        Positions submenu closer to the player sprite area, not in the sidebar.

        Returns:
            Tuple of (x, y) position for submenus
        """
        if screen_height is None:
            screen_height = Layout.SCREEN_HEIGHT

        # Position close to player sprite (player is around x=80)
        submenu_x = 200  # To the right of player sprite
        submenu_y = 250  # Above the message box area

        return (submenu_x, submenu_y)

    @staticmethod
    def _get_message_box_position(screen_height: Optional[int] = None, hotbar_height: int = 50, message_box_height: int = 90) -> Tuple[int, int]:
        """Position for the battle message box.

        Positions the message box above the hotbar, flush with left edge.
        Formula: y = screen_height - hotbar_height - message_box_height - gap

        Args:
            screen_height: Height of the screen surface (defaults to Layout.SCREEN_HEIGHT if None)
            hotbar_height: Height of the hotbar (default 50)
            message_box_height: Height of the message box (default 90 for collapsed)

        Returns:
            Tuple of (x, y) position for the message box
        """
        if screen_height is None:
            screen_height = Layout.SCREEN_HEIGHT

        gap = 10  # Small gap between message box and hotbar
        y = screen_height - hotbar_height - message_box_height - gap

        # Ensure message box doesn't go above ally sprites.
        # Allies are now at y=220, with status icons below extending to ~y=290-300
        # So message box should be at y >= 310 to avoid overlap
        min_y = 310  # Minimum y to avoid ally sprite overlap
        y = max(y, min_y)
        return (0, y)  # Flush with left edge

    def _get_ally_base_position(self) -> Tuple[int, int]:
        """Base position for drawing allies."""
        return (80, 220)

    def _get_ally_spacing(self) -> int:
        """Horizontal spacing between ally sprites."""
        return self.draw_size + 40

    def _get_enemy_base_position(self) -> Tuple[int, int]:
        """Base position for drawing enemies."""
        return (120, 60)

    def _get_enemy_spacing(self) -> int:
        """Horizontal spacing between enemy sprites."""
        return self.draw_size + 40
