"""Asset management for loading sprites, sounds, and fonts.

This module provides a thin façade that composes FontManager, SpriteManager,
and SoundManager to provide a unified interface while maintaining modularity.
"""

from typing import Callable, Dict, List, Optional, Tuple

import pygame

from .font_manager import FontManager
from .sprite_manager import SpriteManager
from .sound_manager import SoundManager


class AssetManager:
    """Manages loading and caching of game assets.

    This is a thin façade that composes specialized managers for different
    asset types while maintaining backward compatibility with the original
    monolithic AssetManager interface.
    """

    def __init__(
        self,
        assets_dir: str = "assets",
        scale: int = 2,
        tileset_name: Optional[str] = None,
        preload_common: bool = True,
        tile_size: int = 32,
        sprite_size: int = 32,
    ):
        """Initialize the asset manager with component managers.

        Args:
            assets_dir: Base directory for assets
            scale: Scaling factor for sprites and UI
            tileset_name: Optional specific tileset to use
            preload_common: Whether to preload common sprites
            tile_size: Default tile size for preloading
            sprite_size: Default sprite size for preloading
        """
        self.assets_dir = assets_dir
        self.scale = max(1, int(scale))
        self.tileset_name = tileset_name

        # Initialize component managers
        self.font_manager = FontManager(assets_dir=assets_dir)
        self.sprite_manager = SpriteManager(
            assets_dir=assets_dir,
            scale=scale,
            tileset_name=tileset_name
        )
        self.sound_manager = SoundManager(assets_dir=assets_dir)

        # Preload common sprites if enabled
        if preload_common:
            self.preload_common_sprites(tile_size=tile_size, sprite_size=sprite_size)

    # --- Image/Sprite methods ---

    def has_image(self, sprite_id: str) -> bool:
        """Check if an image exists (is loaded) without generating a placeholder."""
        return self.sprite_manager.has_image(sprite_id)

    def get_image(self, sprite_id: str, size: Optional[Tuple[int, int]] = None) -> pygame.Surface:
        """
        Get an image by sprite ID. Creates a pixel-art placeholder if missing.
        Optionally scales to a specific size (before applying scale factor).
        """
        return self.sprite_manager.get_image(sprite_id, size)

    def get_tile_surface(self, sprite_id: str, tile_size: int) -> pygame.Surface:
        """Fetch a tile surface scaled to tile_size * scale."""
        return self.sprite_manager.get_tile_surface(sprite_id, tile_size)

    def preload_common_sprites(
        self,
        tile_size: int = 32,
        sprite_size: int = 32,
        common_sprites: Optional[List[str]] = None,
        common_sizes: Optional[List[Tuple[int, int]]] = None,
        strict: bool = False,
    ) -> None:
        """
        Preload common sprites and pre-generate frequently used scaled versions.

        This prevents stuttering during gameplay by ensuring common sprites are
        loaded and scaled versions are cached before they're needed.

        Args:
            tile_size: Default tile size for preloading tile surfaces.
            sprite_size: Default sprite size for preloading entity sprites.
            common_sprites: Optional list of specific sprite IDs to preload.
            common_sizes: Optional list of (width, height) tuples to pre-generate.
            strict: If True, raises RuntimeError on preload failure.
        """
        self.sprite_manager.preload_common_sprites(
            tile_size=tile_size,
            sprite_size=sprite_size,
            common_sprites=common_sprites,
            common_sizes=common_sizes,
            strict=strict
        )

    def warm_cache_for_resolution(self, tile_size: int, sprite_size: int) -> None:
        """
        Pre-generate scaled versions for current tileset resolution to avoid per-frame scaling on first use.

        Args:
            tile_size: Tile size for the current tileset resolution.
            sprite_size: Sprite size for the current tileset resolution.
        """
        self.sprite_manager.warm_cache_for_resolution(tile_size, sprite_size)

    def complete_background_loading(self, progress_callback: Optional[Callable[[int, int], None]] = None) -> None:
        """
        Complete background loading of sprites (heavy I/O phase).

        Args:
            progress_callback: Optional callback function(loaded_count, total_count)
        """
        self.sprite_manager.complete_background_loading(progress_callback)

    # --- Font methods ---

    def get_font(self, font_name: str = "default", size: Optional[int] = None, apply_accessibility: bool = True) -> Optional[pygame.font.Font]:
        """
        Get a font by name with optional override size.
        Always returns a valid font, falling back to pygame default if needed.

        Args:
            font_name: Name of the font to retrieve
            size: Optional size override
            apply_accessibility: If True, applies accessibility text scaling
        """
        return self.font_manager.get_font(font_name, size, apply_accessibility)

    # --- Sound methods ---

    def play_sound(self, sound_id: str) -> None:
        """Play a sound by ID."""
        self.sound_manager.play_sound(sound_id)

    # --- Backward compatibility properties ---

    @property
    def images(self) -> Dict[str, pygame.Surface]:
        """Access to loaded images (for backward compatibility)."""
        return self.sprite_manager.images

    @property
    def sounds(self) -> Dict[str, pygame.mixer.Sound]:
        """Access to loaded sounds (for backward compatibility)."""
        return self.sound_manager.sounds

    @property
    def fonts(self) -> Dict[str, pygame.font.Font]:
        """Access to loaded fonts (for backward compatibility)."""
        return self.font_manager.fonts
