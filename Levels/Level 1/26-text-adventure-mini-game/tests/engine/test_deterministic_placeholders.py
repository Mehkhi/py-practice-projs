"""Tests for deterministic placeholder color generation."""

import hashlib
import unittest

import pygame

from engine.assets.cache_utils import make_placeholder


class TestDeterministicPlaceholders(unittest.TestCase):
    """Test that placeholder colors are deterministic across runs."""

    @classmethod
    def setUpClass(cls):
        pygame.init()

    @classmethod
    def tearDownClass(cls):
        if pygame.get_init():
            pygame.quit()

    def test_same_sprite_id_yields_same_color(self):
        """Same sprite ID should produce identical placeholder colors."""
        sprite_id = "test_sprite_deterministic"

        # Generate placeholders twice
        surface1 = make_placeholder(sprite_id, (32, 32))
        surface2 = make_placeholder(sprite_id, (32, 32))

        # Sample colors from the same pixel positions
        # Using center of head circle which should be primary color
        head_pos = (16, 8)  # Approximate head center

        color1 = surface1.get_at(head_pos)
        color2 = surface2.get_at(head_pos)

        self.assertEqual(color1, color2,
            f"Colors should match for same sprite ID. Got {color1} vs {color2}")

    def test_different_sprite_ids_yield_different_colors(self):
        """Different sprite IDs should produce different placeholder colors."""
        surface1 = make_placeholder("sprite_alpha", (32, 32))
        surface2 = make_placeholder("sprite_beta", (32, 32))

        # Sample from the body area which should have primary color
        body_pos = (16, 20)

        color1 = surface1.get_at(body_pos)
        color2 = surface2.get_at(body_pos)

        # Colors should be different (unless we're extremely unlucky with hash collision)
        self.assertNotEqual(color1[:3], color2[:3],
            "Different sprite IDs should produce different colors")

    def test_blake2b_hash_is_deterministic(self):
        """Verify blake2b produces consistent results for the same input."""
        sprite_id = "consistent_hash_test"

        # Generate hash twice
        digest1 = hashlib.blake2b(sprite_id.encode('utf-8'), digest_size=4).digest()
        digest2 = hashlib.blake2b(sprite_id.encode('utf-8'), digest_size=4).digest()

        self.assertEqual(digest1, digest2,
            "blake2b should produce identical digests for same input")

    def test_placeholder_has_srcalpha(self):
        """Placeholder surfaces should have alpha channel."""
        surface = make_placeholder("alpha_test", (16, 16))

        # Check that the surface has per-pixel alpha
        self.assertTrue(surface.get_flags() & pygame.SRCALPHA,
            "Placeholder should have SRCALPHA flag")

    def test_placeholder_color_range(self):
        """Placeholder primary colors should be within visible range (50-205)."""
        sprite_id = "color_range_test"
        surface = make_placeholder(sprite_id, (32, 32))

        # Get a pixel from the body area
        body_pos = (16, 20)
        color = surface.get_at(body_pos)

        # RGB values should be in the clamped range
        for channel, value in [('R', color.r), ('G', color.g), ('B', color.b)]:
            self.assertGreaterEqual(value, 50,
                f"{channel} channel {value} should be >= 50")
            self.assertLessEqual(value, 205,
                f"{channel} channel {value} should be <= 205")


if __name__ == '__main__':
    unittest.main()
