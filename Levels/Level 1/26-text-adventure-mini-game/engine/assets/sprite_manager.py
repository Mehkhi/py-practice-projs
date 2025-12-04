"""Sprite management for loading, caching, and scaling images."""

import json
import os
from typing import Callable, Dict, List, Optional, Tuple

import pygame

from core.logging_utils import log_warning, log_debug
from .cache_utils import clean_sprite_transparency, make_placeholder, ENABLE_TRANSPARENCY_CLEANUP


class SpriteManager:
    """Manages loading, caching, and scaling of sprite images."""

    def __init__(self, assets_dir: str = "assets", scale: int = 2, tileset_name: Optional[str] = None):
        self.assets_dir = assets_dir
        self.scale = max(1, int(scale))
        self.tileset_name = tileset_name

        self.images: Dict[str, pygame.Surface] = {}
        self.scaled_cache: Dict[Tuple[str, int, int], pygame.Surface] = {}
        self._alpha_surfaces: set[str] = set()  # Track which sprites have alpha channel
        self._pending_sprites: List[Tuple[str, str]] = []  # (sprite_path, sprite_id) for background loading

        self._load_sprites()

    def _collect_sprite_paths_from_dir(self, directory: str, recursive: bool = False) -> None:
        """Collect sprite file paths from a directory (lightweight phase).

        This method only collects file paths without loading images, allowing
        the actual loading to be deferred to a background phase.

        Args:
            directory: Path to the directory to scan.
            recursive: If True, also scan subdirectories.
        """
        if not os.path.exists(directory):
            return
        for entry in os.listdir(directory):
            full_path = os.path.join(directory, entry)

            # Recursively scan subdirectories
            if recursive and os.path.isdir(full_path):
                self._collect_sprite_paths_from_dir(full_path, recursive=True)
                continue

            if entry.lower().endswith((".png", ".jpg", ".bmp")):
                sprite_id = os.path.splitext(entry)[0]
                # Always add to pending if not already pending (real sprites should replace placeholders)
                # Check if already pending to avoid duplicates
                if not any(pending_id == sprite_id for _, pending_id in self._pending_sprites):
                    self._pending_sprites.append((full_path, sprite_id))

    def _load_sprite_background(self, sprite_path: str, sprite_id: str) -> None:
        """Load a single sprite with heavy I/O operations (background phase).

        This method performs the actual image loading, alpha conversion, and
        optional transparency cleaning. Should be called during background loading.

        Args:
            sprite_path: Full path to the sprite file.
            sprite_id: Sprite ID to use for caching.
        """
        try:
            # Load image
            image = pygame.image.load(sprite_path)

            # Ensure we are working with an SRCALPHA surface regardless of display state
            try:
                image = image.convert_alpha()
                self._alpha_surfaces.add(sprite_id)  # Track that this sprite has alpha
            except pygame.error:
                # convert_alpha requires a display; fall back to manual conversion
                temp_surface = pygame.Surface(image.get_size(), pygame.SRCALPHA)
                temp_surface.blit(image, (0, 0))
                image = temp_surface
                self._alpha_surfaces.add(sprite_id)  # Manual conversion also has alpha

            # Normalize transparency to avoid opaque boxes around sprites
            # Only if enabled via environment variable (disabled by default for performance)
            if ENABLE_TRANSPARENCY_CLEANUP:
                image = clean_sprite_transparency(image, os.path.basename(sprite_path))

            self.images[sprite_id] = image
            # Clear any scaled placeholder caches now that the real sprite is available
            self._invalidate_scaled_cache(sprite_id)
        except Exception as e:
            log_warning(f"Failed to load sprite {sprite_id} from {sprite_path}: {e}")

    def _load_sprites_from_dir(self, directory: str, recursive: bool = False) -> None:
        """Load loose sprite files from a directory (legacy synchronous method).

        This method is kept for backward compatibility but now delegates to
        the background loading system. For new code, use _collect_sprite_paths_from_dir
        and complete_background_loading().

        Args:
            directory: Path to the directory to load sprites from.
            recursive: If True, also load sprites from subdirectories.
        """
        # Collect paths first (lightweight)
        self._collect_sprite_paths_from_dir(directory, recursive)
        # Then load immediately (for backward compatibility)
        self._load_pending_sprites()

    def _load_pending_sprites(self) -> None:
        """Load all pending sprites (internal helper for background loading)."""
        while self._pending_sprites:
            sprite_path, sprite_id = self._pending_sprites.pop(0)
            self._load_sprite_background(sprite_path, sprite_id)

    def _load_sprites(self) -> None:
        """Load sprite files from the sprites directory.

        This method collects sprite paths and loads them synchronously to ensure
        all sprites are available immediately after SpriteManager initialization.
        For deferred/background loading (e.g., during a loading screen), use
        complete_background_loading() after initialization with preload_common=False.
        """
        sprites_dir = os.path.join(self.assets_dir, "sprites")
        # Collect sprite paths recursively to include subdirectories like portraits/
        self._collect_sprite_paths_from_dir(sprites_dir, recursive=True)

        if self.tileset_name:
            tileset_dir = os.path.join(self.assets_dir, "tilesets", self.tileset_name)
            self._collect_sprite_paths_from_dir(tileset_dir)

        # Load all collected sprites synchronously (eager loading)
        # This ensures sprites are available immediately, not just placeholders
        self._load_pending_sprites()

    def has_image(self, sprite_id: str) -> bool:
        """Check if an image exists (is loaded) without generating a placeholder."""
        return sprite_id in self.images

    def _invalidate_scaled_cache(self, sprite_id: str) -> None:
        """Remove scaled cache entries for a sprite to avoid stale placeholders."""
        if not self.scaled_cache:
            return

        stale_keys = [key for key in self.scaled_cache if key[0] == sprite_id]
        for key in stale_keys:
            del self.scaled_cache[key]

    def get_image(self, sprite_id: str, size: Optional[Tuple[int, int]] = None) -> pygame.Surface:
        """
        Get an image by sprite ID. Creates a pixel-art placeholder if missing.
        Optionally scales to a specific size (before applying scale factor).
        """
        base_surface = self.images.get(sprite_id)
        if base_surface is None:
            # Generate placeholder at requested size for better fidelity
            placeholder_size = size if size else (16, 16)
            log_debug(f"Generating placeholder for missing sprite: {sprite_id}")
            base_surface = make_placeholder(sprite_id, placeholder_size)
            self.images[sprite_id] = base_surface
            self._alpha_surfaces.add(sprite_id)  # Placeholders are created with SRCALPHA

        if not size:
            return base_surface

        cache_key = (sprite_id, size[0] * self.scale, size[1] * self.scale)
        if cache_key in self.scaled_cache:
            return self.scaled_cache[cache_key]

        scaled = pygame.transform.scale(
            base_surface,
            (cache_key[1], cache_key[2])
        )

        # Preserve alpha channel on scaled surfaces to avoid black boxes reappearing
        # Only call convert_alpha if base surface doesn't already have alpha
        # pygame.transform.scale preserves alpha, but convert_alpha ensures proper format
        if sprite_id in self._alpha_surfaces:
            # Base has alpha, scaled surface should preserve it
            # Only need convert_alpha if display isn't initialized (for headless environments)
            try:
                scaled = scaled.convert_alpha()
            except pygame.error:
                # Fallback for headless environments
                temp_surface = pygame.Surface(scaled.get_size(), pygame.SRCALPHA)
                temp_surface.blit(scaled, (0, 0))
                scaled = temp_surface
        else:
            # Base doesn't have alpha, need convert_alpha on scaled
            try:
                scaled = scaled.convert_alpha()
            except pygame.error:
                temp_surface = pygame.Surface(scaled.get_size(), pygame.SRCALPHA)
                temp_surface.blit(scaled, (0, 0))
                scaled = temp_surface
        self.scaled_cache[cache_key] = scaled
        return scaled

    def get_tile_surface(self, sprite_id: str, tile_size: int) -> pygame.Surface:
        """Fetch a tile surface scaled to tile_size * scale."""
        return self.get_image(sprite_id, (tile_size, tile_size))

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
                          If None, uses default common sprite list from
                          _get_default_common_sprites() or data/preload_sprites.json.
            common_sizes: Optional list of (width, height) tuples to pre-generate
                         for each sprite. If None, defaults to [(tile_size, tile_size), (sprite_size, sprite_size)].
            strict: If True, raises RuntimeError on preload failure instead of
                   logging a warning. Useful for development/testing to catch
                   missing sprites early.

        Raises:
            RuntimeError: If strict=True and a sprite fails to preload.
        """
        if common_sprites is None:
            common_sprites = self._get_default_common_sprites()

        # Default sizes if not provided
        if common_sizes is None:
            common_sizes = [(tile_size, tile_size), (sprite_size, sprite_size)]

        # Deduplicate while preserving order
        seen: set = set()
        unique_sprites: List[str] = []
        for sprite_id in common_sprites:
            if sprite_id not in seen:
                seen.add(sprite_id)
                unique_sprites.append(sprite_id)

        # Preload base images and scaled versions
        for sprite_id in unique_sprites:
            try:
                # Preload base image (will create placeholder if missing)
                self.get_image(sprite_id)

                # Pre-generate scaled versions for all common sizes
                for size in common_sizes:
                    self.get_image(sprite_id, size)
            except Exception as e:
                if strict:
                    raise RuntimeError(f"Critical sprite preload failed: {sprite_id}") from e
                log_warning(f"Failed to preload sprite {sprite_id}: {e}")

    def _get_default_common_sprites(self) -> List[str]:
        """
        Get the default list of common sprites to preload.

        Attempts to load from data/preload_sprites.json first for easy
        configuration. Falls back to built-in defaults if the config file
        is missing or invalid.

        Returns:
            List of sprite IDs that are frequently used in the game.
        """
        # Try to load from external config first for easier maintenance
        preload_config_path = os.path.join("data", "preload_sprites.json")
        if os.path.exists(preload_config_path):
            try:
                with open(preload_config_path, "r") as f:
                    config = json.load(f)
                    external_sprites = config.get("common_sprites", [])
                    if external_sprites:
                        log_debug(f"Loaded {len(external_sprites)} sprites from preload config")
                        return external_sprites
            except Exception as e:
                log_warning(f"Failed to load preload config from {preload_config_path}: {e}")

        # Fall back to built-in defaults
        sprites: List[str] = []

        # Common tiles (from sprite manifest)
        sprites.extend([
            "grass", "dirt", "stone", "water", "wall", "path",
            "grass_0", "grass_1", "grass_2", "grass_3",
            "dirt_1", "dirt_2", "dirt_3", "dirt_path", "dirt_leaves",
            "stone_1", "stone_2", "stone_3", "stone_floor", "stone_wall", "stone_cracked",
            "water_1", "water_2", "water_3",
            "wall_1", "wall_2", "wall_3",
            "lava", "lava_1", "lava_2", "lava_3", "lava_rock",
            "ice", "snow", "sand", "swamp", "moss", "ruins",
            "wood_floor", "wood_floor_1", "wood_floor_2", "wood_floor_3",
            "void", "void_1", "void_2", "void_3",
            "gold_floor", "puddle", "roots",
        ])

        # UI elements
        sprites.append("ui_panel")
        sprites.append("ui_cursor")

        # Status icons (load from status_icons.json)
        status_icons = self._load_status_icon_sprites()
        sprites.extend(status_icons)

        # Background sprites (battle backdrops)
        sprites.extend([
            "bg_cave", "bg_forest", "bg_mountain", "bg_ruins",
            "bg_snow", "bg_swamp", "bg_treasure_chamber",
        ])

        # Common enemies (frequently encountered)
        sprites.extend([
            "goblin", "slime", "bat", "skeleton", "spider",
            "ghost", "orc", "troll", "wolf", "imp",
            "boss_champion", "boss_shadow", "boss_unknown", "boss_void", "boss_wyrm", "boss_primordial",
            "mirror_player",
        ])

        # Player class sprites (common classes)
        sprites.extend([
            "class_warrior", "class_mage", "class_rogue", "class_cleric",
            "class_knight", "class_ranger", "class_paladin", "class_monk",
        ])

        # Party member sprites
        sprites.extend([
            "party_brock", "party_luna", "party_sage",
        ])

        # NPC sprites
        sprites.extend([
            "npc_default", "npc_guard", "npc_merchant", "npc_villager",
        ])

        # Common props
        sprites.extend([
            "prop_barrel", "prop_crate", "prop_rock", "prop_bush",
            "prop_tree", "prop_campfire", "prop_torch",
        ])

        return sprites

    def warm_cache_for_resolution(self, tile_size: int, sprite_size: int) -> None:
        """
        Pre-generate scaled versions for current tileset resolution to avoid per-frame scaling on first use.

        This method warms the scaling cache by pre-generating scaled versions of common sprites
        at the specified tile and sprite sizes. This prevents stuttering when sprites are first
        used at a particular resolution.

        Args:
            tile_size: Tile size for the current tileset resolution.
            sprite_size: Sprite size for the current tileset resolution.
        """
        common_sprites = self._get_default_common_sprites()
        common_sizes = [(tile_size, tile_size), (sprite_size, sprite_size)]

        for sprite_id in common_sprites:
            if sprite_id in self.images:
                # Pre-generate scaled versions for current resolution
                for size in common_sizes:
                    try:
                        self.get_image(sprite_id, size)
                    except Exception as e:
                        log_debug(f"Failed to warm cache for {sprite_id} at {size}: {e}")

    def _load_status_icon_sprites(self, data_dir: str = "data") -> List[str]:
        """
        Load status icon sprite IDs from status_icons.json.

        Args:
            data_dir: Directory containing data files (default: "data").

        Returns:
            List of status icon sprite IDs.
        """
        status_icons: List[str] = []
        path = os.path.join(data_dir, "status_icons.json")
        if not os.path.exists(path):
            return status_icons

        try:
            with open(path, "r") as f:
                icon_map = json.load(f)
                # Extract unique sprite IDs from the mapping
                for sprite_id in icon_map.values():
                    if sprite_id not in status_icons:
                        status_icons.append(sprite_id)
        except Exception as e:
            log_warning(f"Failed to load status icon sprites from {path}: {e}")

        return status_icons

    def complete_background_loading(self, progress_callback: Optional[Callable[[int, int], None]] = None) -> None:
        """
        Complete background loading of sprites (heavy I/O phase).

        This method loads all sprites that were collected during the lightweight
        phase. It performs the actual image loading, alpha conversion, and
        optional transparency cleaning.

        Should be called during a loading screen or scene transition to avoid
        blocking the main game loop.

        Args:
            progress_callback: Optional callback function(loaded_count, total_count)
                            called after each sprite is loaded to report progress.
        """
        total = len(self._pending_sprites)
        loaded = 0

        while self._pending_sprites:
            sprite_path, sprite_id = self._pending_sprites.pop(0)
            self._load_sprite_background(sprite_path, sprite_id)
            loaded += 1

            if progress_callback:
                try:
                    progress_callback(loaded, total)
                except Exception as e:
                    log_warning(f"Progress callback failed: {e}")

        log_debug(f"Background loading complete: {loaded} sprites loaded")
