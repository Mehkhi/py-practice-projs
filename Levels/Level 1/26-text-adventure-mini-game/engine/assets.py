"""Asset management for loading sprites, sounds, and fonts."""

import json
import os
from typing import Dict, List, Optional, Tuple

import pygame

from core.logging_utils import log_warning, log_error, log_debug


class AssetManager:
    """Manages loading and caching of game assets."""

    def __init__(
        self,
        assets_dir: str = "assets",
        scale: int = 2,
        tileset_name: Optional[str] = None,
        preload_common: bool = True,
        tile_size: int = 32,
        sprite_size: int = 32,
    ):
        self.assets_dir = assets_dir
        self.scale = max(1, int(scale))
        self.tileset_name = tileset_name

        self.images: Dict[str, pygame.Surface] = {}
        self.scaled_cache: Dict[Tuple[str, int, int], pygame.Surface] = {}
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.fonts: Dict[str, pygame.font.Font] = {}
        self.font_variants: Dict[Tuple[str, int], pygame.font.Font] = {}

        self._load_fonts()
        self._load_sprites()
        self._load_sounds()

        # Preload common sprites if enabled
        if preload_common:
            self.preload_common_sprites(tile_size=tile_size, sprite_size=sprite_size)

    # --- Loading helpers ---

    def _load_fonts(self) -> None:
        """Load default and bundled fonts."""
        # Try to load default pygame fonts
        try:
            self.fonts["default"] = pygame.font.Font(None, 24)
            self.fonts["small"] = pygame.font.Font(None, 16)
            self.fonts["large"] = pygame.font.Font(None, 32)
        except (pygame.error, OSError, Exception) as e:
            log_warning(f"Failed to load default pygame fonts: {e}. Will use fallback.")
            # Ensure we have at least one fallback font
            try:
                self.fonts["default"] = pygame.font.Font(None, 24)
            except Exception:
                log_error("Critical: Unable to create any default font. Game may have rendering issues.")

        # Load bundled fonts from assets/fonts directory
        fonts_dir = os.path.join(self.assets_dir, "fonts")
        if os.path.exists(fonts_dir):
            for filename in os.listdir(fonts_dir):
                if not filename.lower().endswith((".ttf", ".otf")):
                    continue
                font_id = os.path.splitext(filename)[0]
                try:
                    path = os.path.join(fonts_dir, filename)
                    # Use default sizes; callers can request resized copies
                    self.fonts[font_id] = pygame.font.Font(path, 24)
                    log_debug(f"Loaded bundled font: {font_id} from {filename}")
                except (pygame.error, OSError, FileNotFoundError) as e:
                    log_warning(f"Failed to load bundled font {filename}: {e}")
                except Exception as e:
                    log_warning(f"Unexpected error loading font {filename}: {e}")

    def _load_sprites_from_dir(self, directory: str, recursive: bool = False) -> None:
        """Load loose sprite files from a directory.

        Args:
            directory: Path to the directory to load sprites from.
            recursive: If True, also load sprites from subdirectories.
        """
        if not os.path.exists(directory):
            return
        for entry in os.listdir(directory):
            full_path = os.path.join(directory, entry)

            # Recursively load from subdirectories
            if recursive and os.path.isdir(full_path):
                self._load_sprites_from_dir(full_path, recursive=True)
                continue

            if entry.lower().endswith((".png", ".jpg", ".bmp")):
                sprite_id = os.path.splitext(entry)[0]
                try:
                    # Load image with alpha channel support
                    image = pygame.image.load(full_path)
                    # Only use convert_alpha if display is initialized
                    if pygame.display.get_surface() is not None:
                        image = image.convert_alpha()
                    self.images[sprite_id] = image
                except Exception as e:
                    log_warning(f"Failed to load sprite {entry} from {full_path}: {e}")

    def _load_sprites(self) -> None:
        """Load top-level sprites and optional tileset folder."""
        sprites_dir = os.path.join(self.assets_dir, "sprites")
        # Load sprites recursively to include subdirectories like portraits/
        self._load_sprites_from_dir(sprites_dir, recursive=True)

        if self.tileset_name:
            tileset_dir = os.path.join(self.assets_dir, "tilesets", self.tileset_name)
            self._load_sprites_from_dir(tileset_dir)

    def _load_sounds(self) -> None:
        """Load sound effects/music."""
        audio_dir = os.path.join(self.assets_dir, "audio")
        if not os.path.exists(audio_dir):
            return
        for filename in os.listdir(audio_dir):
            if filename.lower().endswith((".wav", ".ogg", ".mp3")):
                sound_id = os.path.splitext(filename)[0]
                try:
                    sound = pygame.mixer.Sound(os.path.join(audio_dir, filename))
                    self.sounds[sound_id] = sound
                except Exception as e:
                    log_warning(f"Failed to load sound {filename} from {audio_dir}: {e}")

    # --- Retrieval helpers ---

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
            base_surface = self._make_placeholder(sprite_id, placeholder_size)
            self.images[sprite_id] = base_surface

        if not size:
            return base_surface

        cache_key = (sprite_id, size[0] * self.scale, size[1] * self.scale)
        if cache_key in self.scaled_cache:
            return self.scaled_cache[cache_key]

        scaled = pygame.transform.scale(
            base_surface,
            (cache_key[1], cache_key[2])
        )
        self.scaled_cache[cache_key] = scaled
        return scaled

    def get_tile_surface(self, sprite_id: str, tile_size: int) -> pygame.Surface:
        """Fetch a tile surface scaled to tile_size * scale."""
        return self.get_image(sprite_id, (tile_size, tile_size))

    def get_font(self, font_name: str = "default", size: Optional[int] = None, apply_accessibility: bool = True) -> Optional[pygame.font.Font]:
        """
        Get a font by name with optional override size.
        Always returns a valid font, falling back to pygame default if needed.

        Args:
            font_name: Name of the font to retrieve
            size: Optional size override
            apply_accessibility: If True, applies accessibility text scaling
        """
        # Apply accessibility scaling if enabled and size is specified
        if apply_accessibility and size:
            try:
                from .accessibility import get_accessibility_manager
                size = get_accessibility_manager().scale_font_size(size)
            except ImportError:
                pass  # Accessibility module not available

        base_font = self.fonts.get(font_name) or self.fonts.get("default")

        # If no base font found, try to create a fallback
        if not base_font:
            log_warning(f"Font '{font_name}' not found, using pygame default fallback")
            try:
                base_font = pygame.font.Font(None, size or 24)
                # Cache it as default for future use
                if "default" not in self.fonts:
                    self.fonts["default"] = base_font
            except Exception as e:
                log_error(f"Failed to create fallback font: {e}")
                return None

        # If size override requested, create or reuse a cached variant
        if base_font and size:
            cache_key = (font_name, size)
            if cache_key in self.font_variants:
                return self.font_variants[cache_key]
            try:
                # Try to use the font's file path if available
                font_path = getattr(base_font, "name", None)
                if font_path:
                    variant = pygame.font.Font(font_path, size)
                else:
                    # Fallback to creating from None (pygame default)
                    variant = pygame.font.Font(None, size)
                self.font_variants[cache_key] = variant
                return variant
            except (pygame.error, OSError) as e:
                log_warning(f"Failed to create font size {size} from {font_name}: {e}. Using base font.")
                try:
                    # Last resort: try pygame default at requested size
                    fallback = pygame.font.Font(None, size)
                    log_debug(f"Using pygame default fallback at size {size}")
                    self.font_variants[cache_key] = fallback
                    return fallback
                except Exception:
                    # Return base font as final fallback
                    return base_font
            except Exception as e:
                log_warning(f"Unexpected error creating font size {size}: {e}. Using base font.")
                return base_font

        return base_font

    def play_sound(self, sound_id: str) -> None:
        """Play a sound by ID."""
        if sound_id in self.sounds:
            try:
                self.sounds[sound_id].play()
            except Exception as e:
                log_warning(f"Failed to play sound {sound_id}: {e}")

    # --- Preloading helpers ---

    def preload_common_sprites(
        self,
        tile_size: int = 32,
        sprite_size: int = 32,
        common_sprites: Optional[List[str]] = None,
        strict: bool = False,
    ) -> None:
        """
        Preload common sprites and pre-generate frequently used scaled versions.

        This prevents stuttering during gameplay by ensuring common sprites are
        loaded and scaled versions are cached before they're needed.

        Called automatically during AssetManager initialization if preload_common=True.
        Can also be called manually after AssetManager creation to preload
        additional sprites or different sizes.

        Performance note: This method performs synchronous I/O and should be
        called during scene transitions (e.g., loading screens) rather than
        during active gameplay.

        Args:
            tile_size: Default tile size for preloading tile surfaces.
            sprite_size: Default sprite size for preloading entity sprites.
            common_sprites: Optional list of specific sprite IDs to preload.
                          If None, uses default common sprite list from
                          _get_default_common_sprites() or data/preload_sprites.json.
            strict: If True, raises RuntimeError on preload failure instead of
                   logging a warning. Useful for development/testing to catch
                   missing sprites early.

        Raises:
            RuntimeError: If strict=True and a sprite fails to preload.

        Example:
            # Preload additional sprites for a specific scene
            assets.preload_common_sprites(
                common_sprites=["boss_sprite", "special_effect_1"]
            )

            # Strict mode for development testing
            assets.preload_common_sprites(strict=True)
        """
        if common_sprites is None:
            common_sprites = self._get_default_common_sprites()

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

                # Pre-generate common scaled versions
                # Tile size for world scenes
                self.get_tile_surface(sprite_id, tile_size)

                # Sprite size for battle scenes
                self.get_image(sprite_id, (sprite_size, sprite_size))
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
            "enemy_slime", "enemy_bat", "enemy_skeleton", "enemy_spider", "enemy_ghost",
            "ghost", "orc", "troll", "wolf", "imp",
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

    # --- Placeholder helpers ---

    def _make_placeholder(self, sprite_id: str, size: Tuple[int, int] = (16, 16)) -> pygame.Surface:
        """Generate a pixel-art styled placeholder with a hash-based palette and transparency."""
        width, height = size
        surface = pygame.Surface((width, height), pygame.SRCALPHA)

        color_hash = hash(sprite_id) % 0xFFFFFF
        # Clamp to 50-205 range for visibility (avoid near-black/near-white)
        primary = (
            50 + ((color_hash >> 16) & 0xFF) % 156,
            50 + ((color_hash >> 8) & 0xFF) % 156,
            50 + (color_hash & 0xFF) % 156
        )
        # Darker accent color for contrast
        accent = (
            max(0, primary[2] - 50),
            max(0, primary[0] - 50),
            max(0, primary[1] - 50)
        )

        # Create a character-shaped placeholder with transparency around edges
        # Draw a simple circular/oval shape to represent a character
        center_x, center_y = width // 2, height // 2

        # Draw body (oval)
        body_rect = pygame.Rect(width // 4, height // 3, width // 2, height * 2 // 3 - 2)
        pygame.draw.ellipse(surface, accent, body_rect)
        pygame.draw.ellipse(surface, primary, body_rect.inflate(-4, -4))

        # Draw head (circle)
        head_radius = min(width, height) // 4
        pygame.draw.circle(surface, accent, (center_x, height // 4), head_radius)
        pygame.draw.circle(surface, primary, (center_x, height // 4), head_radius - 2)

        # Draw outline for visibility
        pygame.draw.ellipse(surface, (255, 255, 255), body_rect, 1)
        pygame.draw.circle(surface, (255, 255, 255), (center_x, height // 4), head_radius, 1)

        return surface
