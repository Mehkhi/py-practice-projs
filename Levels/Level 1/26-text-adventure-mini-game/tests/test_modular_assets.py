"""Test demonstrating the modular AssetManager benefits."""

import unittest
import pygame
from unittest.mock import Mock, patch

# Test the modular structure
from engine.assets.font_manager import FontManager
from engine.assets.sprite_manager import SpriteManager
from engine.assets.sound_manager import SoundManager
from engine.assets import AssetManager


class TestModularAssetManager(unittest.TestCase):
    """Test the benefits of the modular AssetManager design."""

    def setUp(self):
        pygame.init()

    def tearDown(self):
        if pygame.get_init():
            pygame.quit()

    def test_individual_managers_can_be_instantiated(self):
        """Test that individual managers can be created independently."""
        font_mgr = FontManager()
        sprite_mgr = SpriteManager()
        sound_mgr = SoundManager()

        # All managers should initialize without errors
        self.assertIsNotNone(font_mgr)
        self.assertIsNotNone(sprite_mgr)
        self.assertIsNotNone(sound_mgr)

    def test_facade_composes_managers(self):
        """Test that the AssetManager façade properly composes individual managers."""
        assets = AssetManager(preload_common=False)  # Skip preloading for faster test

        # Should have component managers
        self.assertIsNotNone(assets.font_manager)
        self.assertIsNotNone(assets.sprite_manager)
        self.assertIsNotNone(assets.sound_manager)

        # Component managers should be correct types
        self.assertIsInstance(assets.font_manager, FontManager)
        self.assertIsInstance(assets.sprite_manager, SpriteManager)
        self.assertIsInstance(assets.sound_manager, SoundManager)

    def test_facade_delegates_to_correct_manager(self):
        """Test that façade methods delegate to appropriate managers."""
        assets = AssetManager(preload_common=False)

        # Font methods should delegate to font_manager
        font = assets.get_font("default")
        self.assertIsNotNone(font)

        # Sprite methods should delegate to sprite_manager
        image = assets.get_image("test_sprite")
        self.assertIsNotNone(image)

        # Sound methods should delegate to sound_manager
        # Should not raise exception even for non-existent sound
        assets.play_sound("nonexistent_sound")

    def test_headless_testing_with_mocks(self):
        """Test that individual managers can be easily mocked for headless testing."""
        # Create mock managers
        mock_font_mgr = Mock()
        mock_sprite_mgr = Mock()
        mock_sound_mgr = Mock()

        # Configure mock return values
        mock_font_mgr.get_font.return_value = Mock()
        mock_sprite_mgr.get_image.return_value = Mock()
        mock_sound_mgr.play_sound.return_value = None

        # Create AssetManager with mocked components
        with patch('engine.assets.FontManager', return_value=mock_font_mgr), \
             patch('engine.assets.SpriteManager', return_value=mock_sprite_mgr), \
             patch('engine.assets.SoundManager', return_value=mock_sound_mgr):

            assets = AssetManager(preload_common=False)

            # Test that calls are delegated correctly
            assets.get_font("test_font")
            assets.get_image("test_sprite")
            assets.play_sound("test_sound")

            # Verify mocks were called
            mock_font_mgr.get_font.assert_called_once_with("test_font", None, True)
            mock_sprite_mgr.get_image.assert_called_once_with("test_sprite", None)
            mock_sound_mgr.play_sound.assert_called_once_with("test_sound")

    def test_individual_manager_isolation(self):
        """Test that managers can be tested in isolation."""
        # Test FontManager in isolation
        font_mgr = FontManager()
        font = font_mgr.get_font("default")
        self.assertIsNotNone(font)

        # Test SpriteManager in isolation
        sprite_mgr = SpriteManager(scale=1)  # Use scale=1 for simpler testing
        image = sprite_mgr.get_image("test_placeholder")
        self.assertIsNotNone(image)
        self.assertIsInstance(image, pygame.Surface)

        # Test SoundManager in isolation
        sound_mgr = SoundManager()
        # Should not raise exception
        sound_mgr.play_sound("nonexistent_sound")

    def test_backward_compatibility_properties(self):
        """Test that backward compatibility properties work."""
        assets = AssetManager(preload_common=False)

        # Should be able to access underlying dictionaries
        self.assertIsInstance(assets.images, dict)
        self.assertIsInstance(assets.fonts, dict)
        self.assertIsInstance(assets.sounds, dict)

        # Properties should delegate to component managers
        self.assertIs(assets.images, assets.sprite_manager.images)
        self.assertIs(assets.fonts, assets.font_manager.fonts)
        self.assertIs(assets.sounds, assets.sound_manager.sounds)


if __name__ == '__main__':
    unittest.main()
