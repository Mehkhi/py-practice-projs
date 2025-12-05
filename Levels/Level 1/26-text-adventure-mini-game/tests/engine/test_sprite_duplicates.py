"""Tests for duplicate sprite ID detection."""

import os
import shutil
import tempfile
import unittest

import pygame

from engine.assets.sprite_manager import SpriteManager


class TestDuplicateSpriteDetection(unittest.TestCase):
    """Test duplicate sprite ID detection in SpriteManager."""

    @classmethod
    def setUpClass(cls):
        pygame.init()

    @classmethod
    def tearDownClass(cls):
        if pygame.get_init():
            pygame.quit()

    def setUp(self):
        """Create temporary asset directory structure for testing."""
        self.test_dir = tempfile.mkdtemp()
        self.sprites_dir = os.path.join(self.test_dir, "sprites")
        os.makedirs(self.sprites_dir)

    def tearDown(self):
        """Clean up temporary directories."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def _create_test_sprite(self, path: str) -> None:
        """Create a simple 1x1 test sprite image at the given path."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        surface = pygame.Surface((1, 1))
        surface.fill((255, 0, 0))
        pygame.image.save(surface, path)

    def test_no_duplicates_with_unique_ids(self):
        """SpriteManager should not flag unique sprite IDs as duplicates."""
        # Create unique sprites
        self._create_test_sprite(os.path.join(self.sprites_dir, "sprite_a.png"))
        self._create_test_sprite(os.path.join(self.sprites_dir, "sprite_b.png"))

        mgr = SpriteManager(assets_dir=self.test_dir)
        duplicates = mgr.get_duplicate_sprite_ids()

        self.assertEqual(duplicates, [],
            "No duplicates should be detected for unique sprite IDs")

    def test_detects_duplicate_in_subdirectories(self):
        """SpriteManager should detect duplicate IDs in different subdirectories."""
        # Create same-named sprite in two subdirectories
        subdir1 = os.path.join(self.sprites_dir, "category1")
        subdir2 = os.path.join(self.sprites_dir, "category2")

        self._create_test_sprite(os.path.join(subdir1, "duplicate.png"))
        self._create_test_sprite(os.path.join(subdir2, "duplicate.png"))

        mgr = SpriteManager(assets_dir=self.test_dir)
        duplicates = mgr.get_duplicate_sprite_ids()

        self.assertEqual(len(duplicates), 1,
            "Should detect exactly one duplicate")

        sprite_id, path1, path2 = duplicates[0]
        self.assertEqual(sprite_id, "duplicate",
            "Duplicate sprite ID should be 'duplicate'")
        self.assertIn("category1", path1 + path2,
            "One path should contain 'category1'")
        self.assertIn("category2", path1 + path2,
            "One path should contain 'category2'")

    def test_first_found_wins(self):
        """When duplicates exist, the first-found sprite should be loaded."""
        # Create duplicate sprites with different content
        subdir1 = os.path.join(self.sprites_dir, "01_first")  # ASCII sort order
        subdir2 = os.path.join(self.sprites_dir, "02_second")

        # Create first with red color
        path1 = os.path.join(subdir1, "test_sprite.png")
        os.makedirs(os.path.dirname(path1), exist_ok=True)
        surface1 = pygame.Surface((2, 2))
        surface1.fill((255, 0, 0))  # Red
        pygame.image.save(surface1, path1)

        # Create second with blue color
        path2 = os.path.join(subdir2, "test_sprite.png")
        os.makedirs(os.path.dirname(path2), exist_ok=True)
        surface2 = pygame.Surface((2, 2))
        surface2.fill((0, 0, 255))  # Blue
        pygame.image.save(surface2, path2)

        mgr = SpriteManager(assets_dir=self.test_dir)

        # The loaded sprite should exist
        self.assertTrue(mgr.has_image("test_sprite"),
            "Sprite should be loaded despite duplicate")

        # Should have detected the duplicate
        duplicates = mgr.get_duplicate_sprite_ids()
        self.assertEqual(len(duplicates), 1,
            "Should detect exactly one duplicate")

    def test_get_duplicate_sprite_ids_returns_copy(self):
        """get_duplicate_sprite_ids should return a new list, not internal state."""
        self._create_test_sprite(os.path.join(self.sprites_dir, "unique.png"))

        mgr = SpriteManager(assets_dir=self.test_dir)
        duplicates1 = mgr.get_duplicate_sprite_ids()
        duplicates2 = mgr.get_duplicate_sprite_ids()

        # Should be equal but not same object
        self.assertEqual(duplicates1, duplicates2)
        self.assertIsNot(duplicates1, duplicates2,
            "Should return a new list each time")

    def test_empty_directory_no_duplicates(self):
        """Empty asset directory should produce no duplicate warnings."""
        mgr = SpriteManager(assets_dir=self.test_dir)
        duplicates = mgr.get_duplicate_sprite_ids()

        self.assertEqual(duplicates, [],
            "Empty directory should have no duplicates")


if __name__ == '__main__':
    unittest.main()
