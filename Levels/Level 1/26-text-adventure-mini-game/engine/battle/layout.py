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

        Positions menu to avoid overlapping with message box and other UI elements.

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

        # Position menu on right side, above message box
        # Ensure menu doesn't overlap with message box (leave gap)
        menu_y = message_box_y - 200  # Position well above message box
        menu_y = max(100, menu_y)  # Don't go too high (keep at least 100px from top)

        # Right side of screen with margin
        menu_x = Layout.SCREEN_WIDTH - 110  # Approximate menu width + margin

        return (menu_x, menu_y)

    @staticmethod
    def _get_message_box_position(screen_height: Optional[int] = None, hotbar_height: int = 50, message_box_height: int = 90) -> Tuple[int, int]:
        """Position for the battle message box.

        Positions the message box above the hotbar with proper spacing.
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

        gap = 20  # Minimum gap between message box and hotbar
        y = screen_height - hotbar_height - message_box_height - gap

        # Ensure message box doesn't go above ally sprites.
        # Allies are now at y=220, with status icons below extending to ~y=290-300
        # So message box should be at y >= 310 to avoid overlap
        min_y = 310  # Minimum y to avoid ally sprite overlap
        y = max(y, min_y)
        return (Layout.SCREEN_MARGIN, y)

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
