"""Tests for accessibility features integration."""

import os
import unittest
from unittest.mock import patch, MagicMock

from engine.accessibility import (
    AccessibilityManager,
    get_accessibility_manager,
    TEXT_SIZE_PRESETS,
    COLORBLIND_PALETTES,
)
from engine.theme import Colors


class TestAccessibilityManager(unittest.TestCase):
    """Test AccessibilityManager functionality."""

    def setUp(self):
        """Reset singleton instance before each test."""
        AccessibilityManager._instance = None
        AccessibilityManager._initialized = False

    def tearDown(self):
        """Clean up after each test."""
        # Remove settings file if it exists
        settings_path = os.path.join("data", "accessibility.json")
        if os.path.exists(settings_path):
            os.remove(settings_path)
        # Reset both class-level attributes to ensure clean state
        AccessibilityManager._instance = None
        AccessibilityManager._initialized = False

    def test_singleton_pattern(self):
        """Test that AccessibilityManager is a singleton."""
        manager1 = AccessibilityManager()
        manager2 = AccessibilityManager()
        self.assertIs(manager1, manager2)

    def test_get_accessibility_manager(self):
        """Test get_accessibility_manager helper function."""
        manager = get_accessibility_manager()
        self.assertIsInstance(manager, AccessibilityManager)

    def test_default_settings(self):
        """Test default accessibility settings."""
        manager = AccessibilityManager()
        self.assertEqual(manager.text_size, "normal")
        self.assertEqual(manager.colorblind_mode, "none")

    def test_text_size_scaling(self):
        """Test text size scaling."""
        manager = AccessibilityManager()

        # Test normal size (1.0 multiplier)
        manager.text_size = "normal"
        self.assertEqual(manager.scale_font_size(20), 20)

        # Test small size (0.85 multiplier)
        manager.text_size = "small"
        self.assertEqual(manager.scale_font_size(20), int(20 * 0.85))

        # Test large size (1.25 multiplier)
        manager.text_size = "large"
        self.assertEqual(manager.scale_font_size(20), int(20 * 1.25))

        # Test extra_large size (1.5 multiplier)
        manager.text_size = "extra_large"
        self.assertEqual(manager.scale_font_size(20), int(20 * 1.5))

        # Test minimum font size (8)
        manager.text_size = "small"
        self.assertGreaterEqual(manager.scale_font_size(5), 8)

    def test_colorblind_color_retrieval(self):
        """Test colorblind color palette retrieval."""
        manager = AccessibilityManager()

        # Test default mode
        manager.colorblind_mode = "none"
        hp_high = manager.get_color("hp_high")
        self.assertEqual(hp_high, COLORBLIND_PALETTES["none"]["hp_high"])

        # Test protanopia mode
        manager.colorblind_mode = "protanopia"
        hp_high_protanopia = manager.get_color("hp_high")
        self.assertEqual(hp_high_protanopia, COLORBLIND_PALETTES["protanopia"]["hp_high"])
        self.assertNotEqual(hp_high, hp_high_protanopia)

        # Test invalid color key (should return white)
        invalid_color = manager.get_color("invalid_key")
        self.assertEqual(invalid_color, (255, 255, 255))

    def test_set_text_size(self):
        """Test setting text size."""
        manager = AccessibilityManager()

        # Valid size
        result = manager.set_text_size("large")
        self.assertTrue(result)
        self.assertEqual(manager.text_size, "large")

        # Invalid size
        result = manager.set_text_size("invalid")
        self.assertFalse(result)
        self.assertEqual(manager.text_size, "large")  # Should remain unchanged

    def test_set_colorblind_mode(self):
        """Test setting colorblind mode."""
        manager = AccessibilityManager()

        # Valid mode
        result = manager.set_colorblind_mode("deuteranopia")
        self.assertTrue(result)
        self.assertEqual(manager.colorblind_mode, "deuteranopia")

        # Invalid mode
        result = manager.set_colorblind_mode("invalid")
        self.assertFalse(result)
        self.assertEqual(manager.colorblind_mode, "deuteranopia")  # Should remain unchanged

    def test_cycle_text_size(self):
        """Test cycling through text sizes."""
        manager = AccessibilityManager()
        manager.text_size = "normal"

        # Cycle forward
        new_size = manager.cycle_text_size(forward=True)
        self.assertEqual(new_size, "large")
        self.assertEqual(manager.text_size, "large")

        # Cycle backward
        new_size = manager.cycle_text_size(forward=False)
        self.assertEqual(new_size, "normal")
        self.assertEqual(manager.text_size, "normal")

    def test_cycle_colorblind_mode(self):
        """Test cycling through colorblind modes."""
        manager = AccessibilityManager()
        manager.colorblind_mode = "none"

        # Cycle forward
        new_mode = manager.cycle_colorblind_mode(forward=True)
        self.assertEqual(new_mode, "protanopia")
        self.assertEqual(manager.colorblind_mode, "protanopia")

        # Cycle backward
        new_mode = manager.cycle_colorblind_mode(forward=False)
        self.assertEqual(new_mode, "none")
        self.assertEqual(manager.colorblind_mode, "none")

    def test_save_and_load_settings(self):
        """Test saving and loading settings."""
        manager = AccessibilityManager()
        manager.text_size = "large"
        manager.colorblind_mode = "protanopia"

        # Save settings
        result = manager.save_settings()
        self.assertTrue(result)
        self.assertTrue(os.path.exists(manager.settings_path))

        # Create new manager instance (should load saved settings)
        AccessibilityManager._instance = None
        AccessibilityManager._initialized = False
        new_manager = AccessibilityManager()
        self.assertEqual(new_manager.text_size, "large")
        self.assertEqual(new_manager.colorblind_mode, "protanopia")

    def test_to_dict_and_from_dict(self):
        """Test exporting and importing settings."""
        manager = AccessibilityManager()
        manager.text_size = "extra_large"
        manager.colorblind_mode = "tritanopia"

        # Export
        data = manager.to_dict()
        self.assertEqual(data["text_size"], "extra_large")
        self.assertEqual(data["colorblind_mode"], "tritanopia")

        # Import
        new_manager = AccessibilityManager()
        new_manager.from_dict(data)
        self.assertEqual(new_manager.text_size, "extra_large")
        self.assertEqual(new_manager.colorblind_mode, "tritanopia")

    def test_configurable_settings_path(self):
        """Test that settings_path can be configured."""
        import tempfile

        # Create a temporary file path
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name

        try:
            # Create manager with custom settings path
            manager = AccessibilityManager(settings_path=temp_path)
            self.assertEqual(manager.settings_path, temp_path)

            # Modify and save settings
            manager.text_size = "large"
            manager.colorblind_mode = "protanopia"
            result = manager.save_settings()
            self.assertTrue(result)
            self.assertTrue(os.path.exists(temp_path))

            # Reset and create new manager with same path
            AccessibilityManager._instance = None
            AccessibilityManager._initialized = False
            new_manager = AccessibilityManager(settings_path=temp_path)
            self.assertEqual(new_manager.text_size, "large")
            self.assertEqual(new_manager.colorblind_mode, "protanopia")
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)


class TestAccessibilityThemeIntegration(unittest.TestCase):
    """Test accessibility integration with theme system."""

    def setUp(self):
        """Reset singleton instance before each test."""
        AccessibilityManager._instance = None
        AccessibilityManager._initialized = False

    def tearDown(self):
        """Clean up after each test."""
        # Reset both class-level attributes to ensure clean state
        AccessibilityManager._instance = None
        AccessibilityManager._initialized = False

    def test_get_accessibility_color(self):
        """Test Colors.get_accessibility_color() method."""
        manager = AccessibilityManager()

        # Test with default mode
        manager.colorblind_mode = "none"
        hp_high = Colors.get_accessibility_color("hp_high")
        self.assertEqual(hp_high, COLORBLIND_PALETTES["none"]["hp_high"])

        # Test with colorblind mode
        manager.colorblind_mode = "protanopia"
        hp_high_protanopia = Colors.get_accessibility_color("hp_high")
        self.assertEqual(hp_high_protanopia, COLORBLIND_PALETTES["protanopia"]["hp_high"])

        # Test fallback for invalid key
        default_color = Colors.get_accessibility_color("invalid_key")
        self.assertEqual(default_color, Colors.WHITE)

    def test_get_hp_color(self):
        """Test Colors.get_hp_color() method."""
        manager = AccessibilityManager()

        # Test high HP (> 0.6)
        manager.colorblind_mode = "none"
        high_hp_color = Colors.get_hp_color(0.8)
        self.assertEqual(high_hp_color, COLORBLIND_PALETTES["none"]["hp_high"])

        # Test medium HP (0.3-0.6)
        medium_hp_color = Colors.get_hp_color(0.5)
        self.assertEqual(medium_hp_color, COLORBLIND_PALETTES["none"]["hp_medium"])

        # Test low HP (< 0.3)
        low_hp_color = Colors.get_hp_color(0.2)
        self.assertEqual(low_hp_color, COLORBLIND_PALETTES["none"]["hp_low"])

        # Test with colorblind mode
        manager.colorblind_mode = "deuteranopia"
        high_hp_color_cb = Colors.get_hp_color(0.8)
        self.assertEqual(high_hp_color_cb, COLORBLIND_PALETTES["deuteranopia"]["hp_high"])

    def test_get_sp_color(self):
        """Test Colors.get_sp_color() method."""
        manager = AccessibilityManager()

        # Test default mode
        manager.colorblind_mode = "none"
        sp_color = Colors.get_sp_color()
        self.assertEqual(sp_color, COLORBLIND_PALETTES["none"]["sp_bar"])

        # Test with colorblind mode
        manager.colorblind_mode = "tritanopia"
        sp_color_cb = Colors.get_sp_color()
        self.assertEqual(sp_color_cb, COLORBLIND_PALETTES["tritanopia"]["sp_bar"])

    def test_accessibility_color_fallback(self):
        """Test that accessibility colors fall back gracefully when manager unavailable."""
        # Temporarily break the import to test fallback
        with patch('engine.accessibility.get_accessibility_manager', side_effect=ImportError):
            # Should fall back to default colors
            hp_high = Colors.get_accessibility_color("hp_high")
            self.assertEqual(hp_high, Colors.HP_HIGH)

            hp_color = Colors.get_hp_color(0.8)
            self.assertEqual(hp_color, Colors.HP_HIGH)

            sp_color = Colors.get_sp_color()
            self.assertEqual(sp_color, Colors.SP_FILL)


class TestLazyColorEvaluation(unittest.TestCase):
    """Test that UI components use lazy color evaluation for accessibility."""

    def setUp(self):
        """Reset singleton instance before each test."""
        AccessibilityManager._instance = None
        AccessibilityManager._initialized = False

    def tearDown(self):
        """Clean up after each test."""
        AccessibilityManager._instance = None
        AccessibilityManager._initialized = False

    def test_minimap_lazy_colors(self):
        """Test that Minimap colors update when accessibility mode changes."""
        from engine.ui import Minimap

        # Create manager and set to default mode
        manager = AccessibilityManager()
        manager.colorblind_mode = "none"

        # Create minimap without explicit color overrides
        minimap = Minimap()

        # Get initial colors
        initial_player_color = minimap.player_color
        initial_battle_color = minimap.battle_color
        self.assertEqual(initial_player_color, COLORBLIND_PALETTES["none"]["player_marker"])
        self.assertEqual(initial_battle_color, COLORBLIND_PALETTES["none"]["enemy_marker"])

        # Change accessibility mode
        manager.colorblind_mode = "protanopia"

        # Colors should now reflect new mode (lazy evaluation)
        new_player_color = minimap.player_color
        new_battle_color = minimap.battle_color
        self.assertEqual(new_player_color, COLORBLIND_PALETTES["protanopia"]["player_marker"])
        self.assertEqual(new_battle_color, COLORBLIND_PALETTES["protanopia"]["enemy_marker"])

    def test_minimap_explicit_color_overrides(self):
        """Test that explicit color overrides are preserved."""
        from engine.ui import Minimap

        manager = AccessibilityManager()
        manager.colorblind_mode = "none"

        # Create minimap with explicit color override
        custom_color = (255, 0, 255)
        minimap = Minimap(player_color=custom_color)

        # Explicit override should be used
        self.assertEqual(minimap.player_color, custom_color)

        # Change mode - explicit override should still be used
        manager.colorblind_mode = "protanopia"
        self.assertEqual(minimap.player_color, custom_color)

    def test_tooltip_lazy_colors(self):
        """Test that Tooltip colors update when accessibility mode changes."""
        from engine.ui import Tooltip

        manager = AccessibilityManager()
        manager.colorblind_mode = "none"

        # Create tooltip without explicit color overrides
        tooltip = Tooltip()

        # Get initial colors
        initial_positive = tooltip.stat_positive_color
        initial_negative = tooltip.stat_negative_color
        self.assertEqual(initial_positive, COLORBLIND_PALETTES["none"]["positive"])
        self.assertEqual(initial_negative, COLORBLIND_PALETTES["none"]["negative"])

        # Change accessibility mode
        manager.colorblind_mode = "deuteranopia"

        # Colors should now reflect new mode
        new_positive = tooltip.stat_positive_color
        new_negative = tooltip.stat_negative_color
        self.assertEqual(new_positive, COLORBLIND_PALETTES["deuteranopia"]["positive"])
        self.assertEqual(new_negative, COLORBLIND_PALETTES["deuteranopia"]["negative"])

    def test_tooltip_explicit_color_overrides(self):
        """Test that explicit color overrides are preserved for Tooltip."""
        from engine.ui import Tooltip

        manager = AccessibilityManager()
        manager.colorblind_mode = "none"

        # Create tooltip with explicit color override
        custom_positive = (0, 255, 128)
        tooltip = Tooltip(stat_positive_color=custom_positive)

        # Explicit override should be used
        self.assertEqual(tooltip.stat_positive_color, custom_positive)

        # Change mode - explicit override should still be used
        manager.colorblind_mode = "protanopia"
        self.assertEqual(tooltip.stat_positive_color, custom_positive)


if __name__ == "__main__":
    unittest.main()
