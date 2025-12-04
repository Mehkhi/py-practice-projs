"""Overworld bootstrap service for scene initialization.

This service handles the complex initialization logic for the overworld scene,
including asset loading, configuration, and component setup.
"""

from typing import Any, Dict, Optional, Tuple

from ..assets import AssetManager
from ..ui import Minimap, HelpOverlay, TipPopup, HintButton
from ..theme import Layout
from ..config_loader import load_config


class OverworldBootstrap:
    """Bootstrap service for overworld scene initialization."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize bootstrap with configuration.

        Args:
            config: Configuration dictionary. If None, loads from default config.
        """
        self.config = config or load_config()

    def create_asset_manager(
        self,
        tile_size: int,
        scale: int,
        tileset_name: Optional[str] = None
    ) -> AssetManager:
        """Create and configure the AssetManager.

        Args:
            tile_size: Base tile size in pixels
            scale: Display scale factor
            tileset_name: Name of tileset to use

        Returns:
            Configured AssetManager instance
        """
        # If tileset_name not provided, read from config with "default" fallback
        if tileset_name is None:
            tileset_name = self.config.get("tileset", "default")

        assets = AssetManager(
            scale=scale,
            tileset_name=tileset_name,
            tile_size=tile_size,
            sprite_size=tile_size,  # World scenes use tile_size for entities
        )

        # Warm cache for current tileset resolution to avoid per-frame scaling on first use
        assets.warm_cache_for_resolution(tile_size, tile_size)

        return assets

    def load_skills_database(self) -> Dict[str, Any]:
        """Load the skills database from JSON.

        Returns:
            Dictionary mapping skill IDs to skill objects
        """
        from core.combat import load_skills_from_json
        return load_skills_from_json()

    def load_shops_database(self) -> Dict[str, Any]:
        """Load the shops database from JSON.

        Returns:
            Dictionary containing shop definitions
        """
        from ..shop_scene import load_shops_from_json
        return load_shops_from_json()

    def setup_tutorial_ui(
        self,
        assets: AssetManager,
        tutorial_manager: Optional[Any] = None
    ) -> Tuple[Optional[HelpOverlay], Optional[TipPopup], Optional[HintButton]]:
        """Set up tutorial UI components.

        Args:
            assets: AssetManager for loading fonts and images
            tutorial_manager: Tutorial manager instance

        Returns:
            Tuple of (help_overlay, tip_popup, hint_button)
        """
        if not tutorial_manager:
            return None, None, None

        help_overlay = HelpOverlay(tutorial_manager, theme=None)
        tip_popup = TipPopup(theme=None)
        hint_button = HintButton(tutorial_manager, theme=None, assets=assets)
        hint_button.set_context("world")

        # Reposition hint button to bottom-right to avoid overlap with HUD
        # Use Layout constants for consistent spacing, but with extra margin
        # to ensure tooltips don't clip off screen
        btn_w, btn_h = hint_button.size
        margin_right = Layout.SCREEN_MARGIN * 2
        margin_bottom = Layout.SCREEN_MARGIN
        hint_button.position = (
            Layout.SCREEN_WIDTH - btn_w - margin_right,
            Layout.SCREEN_HEIGHT - btn_h - margin_bottom
        )

        return help_overlay, tip_popup, hint_button

    def setup_minimap(self) -> Optional[Minimap]:
        """Set up minimap if enabled in configuration.

        Returns:
            Minimap instance if enabled, None otherwise
        """
        if not self.config.get("minimap_enabled", True):
            return None

        return Minimap(
            size=self.config.get("minimap_size", 120),
            tile_size=self.config.get("minimap_tile_size", 4),
        )

    def initialize_party_overlay_state(self) -> Dict[str, Any]:
        """Initialize party overlay state.

        Returns:
            Dictionary containing initial party overlay state
        """
        return {
            'visible': False,
            'selection': 0,
            'message': None,
            'message_timer': 0.0
        }

    def get_auto_save_settings(self) -> Dict[str, Any]:
        """Get auto-save configuration.

        Returns:
            Dictionary with auto-save settings
        """
        return {
            'enabled': self.config.get("auto_save_enabled", True),
            'on_map_change': self.config.get("auto_save_on_map_change", True),
        }

    def create_transition_manager(self) -> Any:
        """Create screen transition manager.

        Returns:
            TransitionManager instance
        """
        from ..ui import TransitionManager
        return TransitionManager(default_duration=0.4)

    def load_puzzle_manager(self) -> Any:
        """Load and initialize puzzle manager.

        Returns:
            PuzzleManager instance
        """
        from core.data_loader import load_puzzles_from_json
        from core.puzzles import PuzzleManager

        puzzles_data = load_puzzles_from_json()
        return PuzzleManager(puzzles_data)
