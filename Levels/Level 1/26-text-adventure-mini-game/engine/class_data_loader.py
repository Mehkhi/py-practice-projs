"""Class data and sprite loading utilities.

This module provides functions for loading class definitions from JSON
and managing sprite generation/loading for classes and subclasses.
These utilities can be reused across scenes and tested independently.
"""

import json
import os
import sys
from typing import Any, Dict, Optional

import pygame

from core.logging_utils import log_warning, log_error


# Import sprite generation for dynamic class sprite creation
_sprite_generator_path = os.path.join(os.path.dirname(__file__), '..', 'tools')
sys.path.insert(0, _sprite_generator_path)
try:
    from generate_sprites import generate_class_sprite, SUBCLASS_COLORS
    HAS_SPRITE_GENERATOR = True
except ImportError:
    HAS_SPRITE_GENERATOR = False
    SUBCLASS_COLORS = {}


def load_classes_data(path: Optional[str] = None) -> Dict[str, Any]:
    """Load class definitions from JSON.

    Args:
        path: Optional path to classes.json file. Defaults to data/classes.json.

    Returns:
        Dictionary containing "classes" and "subclass_bonuses" keys.
        Returns empty structure if file not found or load fails.
    """
    if path is None:
        path = os.path.join("data", "classes.json")

    if not os.path.exists(path):
        log_warning(f"Classes data file not found: {path}")
        return {"classes": {}, "subclass_bonuses": {}}

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except OSError as e:
        log_warning(f"Failed to read classes data file {path}: {e}")
        return {"classes": {}, "subclass_bonuses": {}}
    except json.JSONDecodeError as e:
        log_error(f"Invalid JSON in classes data file {path}: {e}")
        return {"classes": {}, "subclass_bonuses": {}}


class ClassSpriteLoader:
    """Manages loading and caching of class sprites."""

    def __init__(self, assets: Optional[Any] = None):
        """Initialize the sprite loader.

        Args:
            assets: Optional AssetManager instance for loading pre-generated sprites
        """
        self.assets = assets
        self._sprite_cache: Dict[str, pygame.Surface] = {}

    def get_class_sprite(self, class_id: str, size: int = 96) -> Optional[pygame.Surface]:
        """Get or generate a sprite for a class.

        Args:
            class_id: Class identifier
            size: Desired sprite size (width and height)

        Returns:
            Scaled pygame Surface, or None if generation fails
        """
        cache_key = f"{class_id}_{size}"
        if cache_key in self._sprite_cache:
            return self._sprite_cache[cache_key]

        # Try to load pre-generated sprite first
        sprite_name = f"class_{class_id}"
        if self.assets:
            try:
                sprite = self.assets.get_image(sprite_name)
                if sprite:
                    scaled = pygame.transform.scale(sprite, (size, size))
                    self._sprite_cache[cache_key] = scaled
                    return scaled
            except (AttributeError, pygame.error) as e:
                log_warning(f"Failed to load pre-generated sprite {sprite_name}: {e}")
            except Exception as e:
                log_error(f"Unexpected error loading sprite {sprite_name}: {e}")

        # Fall back to dynamic generation
        if HAS_SPRITE_GENERATOR:
            try:
                sprite = generate_class_sprite(class_id)
                if sprite:
                    scaled = pygame.transform.scale(sprite, (size, size))
                    self._sprite_cache[cache_key] = scaled
                    return scaled
            except (TypeError, ValueError, AttributeError) as e:
                log_warning(f"Failed to generate sprite for class {class_id}: {e}")
            except Exception as e:
                log_error(f"Unexpected error generating sprite for class {class_id}: {e}")

        return None

    def get_combo_sprite(self, primary_class: str, subclass_id: str, size: int = 96) -> Optional[pygame.Surface]:
        """Get or generate a sprite for a primary class with subclass coloring.

        Args:
            primary_class: Primary class identifier
            subclass_id: Subclass identifier
            size: Desired sprite size (width and height)

        Returns:
            Scaled pygame Surface, or None if generation fails
        """
        cache_key = f"{primary_class}_{subclass_id}_{size}"
        if cache_key in self._sprite_cache:
            return self._sprite_cache[cache_key]

        # Try to load pre-generated sprite
        sprite_name = f"player_{primary_class}_{subclass_id}"
        if self.assets:
            try:
                sprite = self.assets.get_image(sprite_name)
                if sprite:
                    scaled = pygame.transform.scale(sprite, (size, size))
                    self._sprite_cache[cache_key] = scaled
                    return scaled
            except (AttributeError, pygame.error) as e:
                log_warning(f"Failed to load pre-generated combo sprite {sprite_name}: {e}")
            except Exception as e:
                log_error(f"Unexpected error loading combo sprite {sprite_name}: {e}")

        # Fall back to dynamic generation
        if HAS_SPRITE_GENERATOR:
            try:
                sprite = generate_class_sprite(primary_class, subclass_id)
                if sprite:
                    scaled = pygame.transform.scale(sprite, (size, size))
                    self._sprite_cache[cache_key] = scaled
                    return scaled
            except (TypeError, ValueError, AttributeError) as e:
                log_warning(f"Failed to generate combo sprite for {primary_class}_{subclass_id}: {e}")
            except Exception as e:
                log_error(f"Unexpected error generating combo sprite for {primary_class}_{subclass_id}: {e}")

        return None

    def clear_cache(self) -> None:
        """Clear the sprite cache."""
        self._sprite_cache.clear()
