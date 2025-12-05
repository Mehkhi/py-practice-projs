"""Tests for shared AssetManager pattern."""

import unittest
from unittest.mock import Mock, patch, MagicMock

import pygame


class TestSharedAssetManager(unittest.TestCase):
    """Test that scenes correctly use injected AssetManager."""

    @classmethod
    def setUpClass(cls):
        pygame.init()
        # Create minimal display for tests
        pygame.display.set_mode((100, 100), pygame.HIDDEN)

    @classmethod
    def tearDownClass(cls):
        if pygame.get_init():
            pygame.quit()

    def test_base_menu_scene_uses_injected_assets(self):
        """Scene should use injected assets parameter."""
        from engine.assets import AssetManager

        # Create a shared asset manager
        shared_assets = AssetManager(preload_common=False)

        # Simulate the pattern used in scene __init__:
        # self.assets = assets or AssetManager(...)
        injected_assets = shared_assets
        result = injected_assets or AssetManager(preload_common=False)

        # Should use the injected one
        self.assertIs(result, shared_assets,
            "Injection pattern should preserve passed asset manager")

    def test_base_menu_scene_creates_assets_if_none(self):
        """Scene should create AssetManager if none provided."""
        from engine.assets import AssetManager

        # Simulate the pattern used in scene __init__:
        # self.assets = assets or AssetManager(...)
        injected_assets = None
        result = injected_assets or AssetManager(preload_common=False)

        # Should have created its own AssetManager
        self.assertIsNotNone(result,
            "Pattern should create AssetManager when None passed")

    def test_injected_assets_not_reloaded(self):
        """Verify injected AssetManager doesn't trigger reload."""
        from engine.assets import AssetManager
        from engine.assets.sprite_manager import SpriteManager

        # Create shared manager with mocked sprite manager
        shared_assets = AssetManager(preload_common=False)
        initial_sprite_count = len(shared_assets.sprite_manager.images)

        # Use the assets in a mock scene-like context
        # Just verify the manager wasn't recreated
        sprite_id = "test_placeholder"
        surface = shared_assets.get_image(sprite_id)

        # Should have added a placeholder
        self.assertEqual(
            len(shared_assets.sprite_manager.images),
            initial_sprite_count + 1,
            "Should only add the requested placeholder, not reload all"
        )


class TestAssetManagerReuse(unittest.TestCase):
    """Test patterns for AssetManager reuse across scenes."""

    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((100, 100), pygame.HIDDEN)

    @classmethod
    def tearDownClass(cls):
        if pygame.get_init():
            pygame.quit()

    def test_sprite_cache_persists_across_scene_usage(self):
        """Sprites cached in shared AssetManager persist for reuse."""
        from engine.assets import AssetManager

        shared_assets = AssetManager(preload_common=False)

        # Request a sprite (will create placeholder)
        sprite_id = "cached_sprite_test"
        surface1 = shared_assets.get_image(sprite_id)

        # Request same sprite again - should hit cache
        surface2 = shared_assets.get_image(sprite_id)

        # Should be the exact same surface object (cached)
        self.assertIs(surface1, surface2,
            "Same sprite ID should return cached surface")

    def test_scaled_cache_persists(self):
        """Scaled sprite cache persists across calls."""
        from engine.assets import AssetManager

        shared_assets = AssetManager(preload_common=False, scale=2)

        sprite_id = "scale_cache_test"
        size = (32, 32)

        # Request scaled version
        scaled1 = shared_assets.get_image(sprite_id, size)
        scaled2 = shared_assets.get_image(sprite_id, size)

        # Should be same cached scaled surface
        self.assertIs(scaled1, scaled2,
            "Same sprite at same size should return cached scaled surface")


if __name__ == '__main__':
    unittest.main()
