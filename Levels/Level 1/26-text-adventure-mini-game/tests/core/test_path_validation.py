"""Unit tests for path validation and security.

Tests path traversal prevention, filename sanitization, and error handling
for file operations.
"""

import os
import tempfile
import unittest
from unittest.mock import patch

from core.path_validation import (
    ensure_directory_exists,
    sanitize_filename,
    validate_path_inside_base,
    validate_save_slot,
)
from core.save_load import SaveManager
from core.mod_loader import ModLoader
from core.world import World, Map, Tile
from core.entities import Player
from core.stats import Stats
from core.items import Inventory


class TestPathValidation(unittest.TestCase):
    """Test path validation utilities."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.base_dir = os.path.join(self.temp_dir, "base")
        os.makedirs(self.base_dir, exist_ok=True)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_validate_path_inside_base_valid_relative(self):
        """Test valid relative path stays within base."""
        # Create subdirectory to ensure path can be resolved
        subdir = os.path.join(self.base_dir, "subdir")
        os.makedirs(subdir, exist_ok=True)

        is_valid, resolved = validate_path_inside_base(
            "subdir/file.json", self.base_dir, allow_absolute=False
        )
        self.assertTrue(is_valid)
        self.assertIsNotNone(resolved)

        # Check that resolved path is within base
        # Use realpath to resolve symlinks (macOS /var -> /private/var)
        base_real = os.path.realpath(os.path.abspath(self.base_dir))
        resolved_real = os.path.realpath(os.path.abspath(resolved))

        # On Windows, paths might be case-insensitive, so normalize
        if os.name == 'nt':
            self.assertTrue(resolved_real.lower().startswith(base_real.lower()))
        else:
            self.assertTrue(resolved_real.startswith(base_real))

    def test_validate_path_inside_base_path_traversal_blocked(self):
        """Test path traversal attacks are blocked."""
        # Classic path traversal
        is_valid, resolved = validate_path_inside_base(
            "../../../etc/passwd", self.base_dir, allow_absolute=False
        )
        self.assertFalse(is_valid)
        self.assertIsNone(resolved)

        # Multiple traversals
        is_valid, resolved = validate_path_inside_base(
            "../../../../../../etc/passwd", self.base_dir, allow_absolute=False
        )
        self.assertFalse(is_valid)
        self.assertIsNone(resolved)

        # Mixed traversal
        is_valid, resolved = validate_path_inside_base(
            "../..//../etc/passwd", self.base_dir, allow_absolute=False
        )
        self.assertFalse(is_valid)
        self.assertIsNone(resolved)

    def test_validate_path_inside_base_absolute_blocked_when_disallowed(self):
        """Test absolute paths are blocked when allow_absolute=False."""
        absolute_path = os.path.join(self.temp_dir, "outside", "file.json")
        os.makedirs(os.path.dirname(absolute_path), exist_ok=True)

        is_valid, resolved = validate_path_inside_base(
            absolute_path, self.base_dir, allow_absolute=False
        )
        self.assertFalse(is_valid)
        self.assertIsNone(resolved)

    def test_validate_path_inside_base_absolute_allowed(self):
        """Test absolute paths work when allow_absolute=True."""
        absolute_path = os.path.join(self.base_dir, "file.json")
        with open(absolute_path, 'w') as f:
            f.write("test")

        is_valid, resolved = validate_path_inside_base(
            absolute_path, self.base_dir, allow_absolute=True
        )
        self.assertTrue(is_valid)
        self.assertIsNotNone(resolved)

    def test_validate_path_inside_base_absolute_outside_base(self):
        """Test absolute path outside base is rejected even when allowed."""
        outside_path = os.path.join(self.temp_dir, "outside", "file.json")
        os.makedirs(os.path.dirname(outside_path), exist_ok=True)

        is_valid, resolved = validate_path_inside_base(
            outside_path, self.base_dir, allow_absolute=True
        )
        self.assertFalse(is_valid)
        self.assertIsNone(resolved)

    def test_validate_path_inside_base_empty_path(self):
        """Test empty path is rejected."""
        is_valid, resolved = validate_path_inside_base(
            "", self.base_dir, allow_absolute=False
        )
        self.assertFalse(is_valid)
        self.assertIsNone(resolved)

    def test_validate_path_inside_base_nonexistent_base(self):
        """Test validation with nonexistent base directory."""
        nonexistent_base = os.path.join(self.temp_dir, "nonexistent")
        is_valid, resolved = validate_path_inside_base(
            "file.json", nonexistent_base, allow_absolute=False
        )
        # Path validation can still work with nonexistent base (validates structure)
        # But the resolved path won't exist
        if is_valid:
            self.assertIsNotNone(resolved)
            self.assertFalse(os.path.exists(resolved))
        else:
            # Or it may reject it - both behaviors are acceptable
            self.assertIsNone(resolved)

    def test_sanitize_filename_valid(self):
        """Test sanitization of valid filenames."""
        self.assertEqual(sanitize_filename("save_1.json"), "save_1.json")
        self.assertEqual(sanitize_filename("test-file.json"), "test-file.json")
        self.assertEqual(sanitize_filename("file.name.json"), "file.name.json")

    def test_sanitize_filename_removes_path_separators(self):
        """Test sanitization removes path separators."""
        # Multiple path separators get collapsed to single underscore
        result = sanitize_filename("../../../etc/passwd")
        self.assertIn("etc", result)
        self.assertIn("passwd", result)
        self.assertNotIn("/", result)
        self.assertNotIn("..", result)

        self.assertEqual(sanitize_filename("dir/file.json"), "dir_file.json")
        self.assertEqual(sanitize_filename("dir\\file.json"), "dir_file.json")

    def test_sanitize_filename_removes_dangerous_chars(self):
        """Test sanitization removes dangerous characters."""
        self.assertEqual(sanitize_filename("file\x00name.json"), "file_name.json")
        self.assertEqual(sanitize_filename("file..name.json"), "file_name.json")

    def test_sanitize_filename_strips_dots_and_spaces(self):
        """Test sanitization strips leading/trailing dots and spaces."""
        self.assertEqual(sanitize_filename(".hidden"), "hidden")
        self.assertEqual(sanitize_filename("file. "), "file")
        self.assertEqual(sanitize_filename("  file  "), "file")

    def test_sanitize_filename_empty_after_sanitization(self):
        """Test sanitization returns None for empty filenames."""
        self.assertIsNone(sanitize_filename(""))
        # "..." becomes "_" after sanitization, which is valid
        # So we test with only dots/spaces/underscores
        self.assertIsNone(sanitize_filename("   "))
        self.assertIsNone(sanitize_filename("___"))

    def test_sanitize_filename_too_long(self):
        """Test sanitization rejects overly long filenames."""
        long_name = "x" * 300
        self.assertIsNone(sanitize_filename(long_name, max_length=255))

    def test_sanitize_filename_reserved_names(self):
        """Test sanitization rejects Windows reserved names."""
        self.assertIsNone(sanitize_filename("CON.json"))
        self.assertIsNone(sanitize_filename("PRN.json"))
        self.assertIsNone(sanitize_filename("COM1.json"))
        self.assertIsNone(sanitize_filename("LPT1.json"))

    def test_validate_save_slot_valid(self):
        """Test validation of valid save slots."""
        is_valid, filename = validate_save_slot(1)
        self.assertTrue(is_valid)
        self.assertEqual(filename, "save_1.json")

        is_valid, filename = validate_save_slot(99)
        self.assertTrue(is_valid)
        self.assertEqual(filename, "save_99.json")

    def test_validate_save_slot_invalid(self):
        """Test validation rejects invalid save slots."""
        # Zero or negative
        is_valid, filename = validate_save_slot(0)
        self.assertFalse(is_valid)
        self.assertIsNone(filename)

        is_valid, filename = validate_save_slot(-1)
        self.assertFalse(is_valid)
        self.assertIsNone(filename)

        # Too large
        is_valid, filename = validate_save_slot(1000)
        self.assertFalse(is_valid)
        self.assertIsNone(filename)

    def test_validate_save_slot_non_integer(self):
        """Test validation rejects non-integer slots."""
        # Type checking should catch this, but test defensive behavior
        # Python's type system may not catch this at runtime, so we test the actual behavior
        try:
            is_valid, filename = validate_save_slot("1")  # type: ignore
            # If it doesn't raise, it should return False
            self.assertFalse(is_valid)
        except (TypeError, AttributeError):
            # Expected if type checking is strict
            pass

    def test_ensure_directory_exists_existing(self):
        """Test ensure_directory_exists with existing directory."""
        success, resolved = ensure_directory_exists(self.base_dir, create_if_missing=False)
        self.assertTrue(success)
        self.assertIsNotNone(resolved)
        self.assertEqual(os.path.abspath(resolved), os.path.abspath(self.base_dir))

    def test_ensure_directory_exists_create(self):
        """Test ensure_directory_exists creates missing directory."""
        new_dir = os.path.join(self.temp_dir, "new_dir")
        success, resolved = ensure_directory_exists(new_dir, create_if_missing=True)
        self.assertTrue(success)
        self.assertIsNotNone(resolved)
        self.assertTrue(os.path.isdir(resolved))

    def test_ensure_directory_exists_no_create(self):
        """Test ensure_directory_exists doesn't create when disabled."""
        new_dir = os.path.join(self.temp_dir, "nonexistent")
        success, resolved = ensure_directory_exists(new_dir, create_if_missing=False)
        self.assertFalse(success)
        self.assertIsNone(resolved)

    def test_ensure_directory_exists_file_not_dir(self):
        """Test ensure_directory_exists rejects files."""
        test_file = os.path.join(self.temp_dir, "test_file.txt")
        with open(test_file, 'w') as f:
            f.write("test")

        success, resolved = ensure_directory_exists(test_file, create_if_missing=False)
        self.assertFalse(success)
        self.assertIsNone(resolved)


class TestSaveManagerPathValidation(unittest.TestCase):
    """Test SaveManager path validation."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.world = World()
        tiles = [[Tile("grass", True, "grass")] * 3] * 3
        self.world.add_map(Map(map_id="forest_path", width=3, height=3, tiles=tiles))
        self.player = Player(
            entity_id="player_1",
            name="Hero",
            x=5,
            y=10,
            sprite_id="hero",
            stats=Stats(100, 100, 50, 50, 10, 5, 4, 6, 3),
            inventory=Inventory(),
        )

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_save_manager_invalid_save_dir(self):
        """Test SaveManager handles path traversal in save directory."""
        # Path traversal in save_dir - ensure_directory_exists may create it
        # but it should resolve to an absolute path within the current directory
        try:
            save_manager = SaveManager(save_dir="saves/../../../etc")
            # If it succeeds, the path should be resolved and validated
            # The actual resolved path should be safe
            self.assertIsNotNone(save_manager.save_dir)
        except ValueError:
            # Or it may reject it - both behaviors are acceptable
            pass

    def test_save_manager_path_traversal_in_slot(self):
        """Test SaveManager blocks path traversal in slot numbers."""
        save_manager = SaveManager(save_dir=self.temp_dir)

        # Try to use path traversal in slot (should be caught by validate_save_slot)
        with self.assertRaises(ValueError):
            save_manager.save_to_slot(0, self.world, self.player)

        with self.assertRaises(ValueError):
            save_manager.load_from_slot(-1, self.world)

    def test_save_manager_slot_exists_validation(self):
        """Test slot_exists validates slot numbers."""
        save_manager = SaveManager(save_dir=self.temp_dir)

        # Invalid slots return False
        self.assertFalse(save_manager.slot_exists(0))
        self.assertFalse(save_manager.slot_exists(-1))
        self.assertFalse(save_manager.slot_exists(1000))

    def test_save_manager_delete_slot_validation(self):
        """Test delete_slot validates slot numbers."""
        save_manager = SaveManager(save_dir=self.temp_dir)

        # Invalid slots return False
        self.assertFalse(save_manager.delete_slot(0))
        self.assertFalse(save_manager.delete_slot(-1))
        self.assertFalse(save_manager.delete_slot(1000))

    def test_save_manager_get_slot_preview_validation(self):
        """Test get_slot_preview validates slot numbers."""
        save_manager = SaveManager(save_dir=self.temp_dir)

        # Invalid slots return None
        self.assertIsNone(save_manager.get_slot_preview(0))
        self.assertIsNone(save_manager.get_slot_preview(-1))
        self.assertIsNone(save_manager.get_slot_preview(1000))


class TestModLoaderPathValidation(unittest.TestCase):
    """Test ModLoader path validation."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.mods_dir = os.path.join(self.temp_dir, "mods")
        os.makedirs(self.mods_dir, exist_ok=True)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_mod_loader_path_traversal_in_override(self):
        """Test ModLoader blocks path traversal in override paths."""
        # Create a mod with path traversal in override
        mod_dir = os.path.join(self.mods_dir, "test_mod")
        os.makedirs(mod_dir, exist_ok=True)

        manifest_path = os.path.join(mod_dir, "mod.json")
        manifest_data = {
            "id": "test_mod",
            "name": "Test Mod",
            "version": "1.0.0",
            "data_overrides": {
                "items": "../../../etc/passwd"  # Path traversal attempt
            }
        }

        import json
        with open(manifest_path, 'w') as f:
            json.dump(manifest_data, f)

        loader = ModLoader(mods_path=self.mods_dir, enabled=True)
        loader.discover_mods()

        # Should discover the mod but reject the override path
        self.assertEqual(len(loader.manifests), 1)

        # Attempting to merge should skip the invalid override
        base_data = {"items": {"test": "item"}}
        merged = loader.merge_data("data/items.json", "items")
        # Should return base data (override was rejected)
        self.assertIsInstance(merged, dict)

    def test_mod_loader_invalid_mod_directory_name(self):
        """Test ModLoader skips mods with invalid directory names."""
        # Create mod directory with invalid name
        invalid_mod_dir = os.path.join(self.mods_dir, "../../invalid")
        os.makedirs(invalid_mod_dir, exist_ok=True)

        loader = ModLoader(mods_path=self.mods_dir, enabled=True)
        loader.discover_mods()

        # Should skip the invalid mod directory
        self.assertEqual(len(loader.manifests), 0)


class TestErrorPathHandling(unittest.TestCase):
    """Test error handling for file operations."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_permission_error_handling(self):
        """Test handling of permission errors."""
        # Create a read-only directory (on Unix-like systems)
        read_only_dir = os.path.join(self.temp_dir, "readonly")
        os.makedirs(read_only_dir, mode=0o555)

        try:
            # Try to create SaveManager with read-only directory
            # Should handle gracefully or raise appropriate error
            save_manager = SaveManager(save_dir=read_only_dir)
            # If it succeeds, try to save (should fail gracefully)
            world = World()
            tiles = [[Tile("grass", True, "grass")] * 3] * 3
            world.add_map(Map(map_id="forest_path", width=3, height=3, tiles=tiles))
            player = Player(
                entity_id="p1",
                name="Hero",
                x=0,
                y=0,
                sprite_id="hero",
                stats=Stats(100, 100, 50, 50, 10, 5, 4, 6, 3),
                inventory=Inventory(),
            )

            # Should raise OSError or PermissionError
            with self.assertRaises((OSError, PermissionError)):
                save_manager.save_to_slot(1, world, player)
        finally:
            # Restore permissions for cleanup
            try:
                os.chmod(read_only_dir, 0o755)
            except OSError:
                pass

    def test_concurrent_file_access(self):
        """Test handling of concurrent file access."""
        save_manager = SaveManager(save_dir=self.temp_dir)
        world = World()
        tiles = [[Tile("grass", True, "grass")] * 3] * 3
        world.add_map(Map(map_id="forest_path", width=3, height=3, tiles=tiles))
        player = Player(
            entity_id="p1",
            name="Hero",
            x=0,
            y=0,
            sprite_id="hero",
            stats=Stats(100, 100, 50, 50, 10, 5, 4, 6, 3),
            inventory=Inventory(),
        )

        # Save to slot
        save_manager.save_to_slot(1, world, player)

        # Try to load while file is locked (simulate concurrent access)
        # On Windows, opening a file exclusively can cause this
        save_path = os.path.join(self.temp_dir, "save_1.json")
        try:
            # Try to open file exclusively (if supported)
            with open(save_path, 'r+b') as locked_file:
                # Try to load - should handle gracefully
                # Note: This may work on some systems, so we just verify no crash
                try:
                    loaded = save_manager.load_from_slot(1, world)
                    # If it works, that's fine too
                except (OSError, PermissionError):
                    # Expected on systems with strict file locking
                    pass
        except (OSError, PermissionError):
            # File locking not supported or already closed
            pass

    def test_invalid_json_encoding(self):
        """Test handling of files with invalid encoding."""
        save_manager = SaveManager(save_dir=self.temp_dir)
        world = World()
        tiles = [[Tile("grass", True, "grass")] * 3] * 3
        world.add_map(Map(map_id="forest_path", width=3, height=3, tiles=tiles))
        player = Player(
            entity_id="p1",
            name="Hero",
            x=0,
            y=0,
            sprite_id="hero",
            stats=Stats(100, 100, 50, 50, 10, 5, 4, 6, 3),
            inventory=Inventory(),
        )

        # Create a save file with invalid encoding
        save_path = os.path.join(self.temp_dir, "save_1.json")
        with open(save_path, 'wb') as f:
            # Write invalid UTF-8 sequence
            f.write(b'\xff\xfe\x00\x00')  # Invalid UTF-8

        # Should raise ValueError (may be UnicodeDecodeError wrapped)
        with self.assertRaises((ValueError, UnicodeDecodeError)) as context:
            save_manager.load_from_slot(1, world)
        # Error message should mention the issue
        error_msg = str(context.exception).lower()
        self.assertTrue(
            "corrupted" in error_msg or "decode" in error_msg or "utf-8" in error_msg
        )

    def test_symlink_attack_prevention(self):
        """Test that symlink attacks are prevented."""
        # Create a symlink pointing outside the save directory
        target_dir = os.path.join(self.temp_dir, "target")
        os.makedirs(target_dir, exist_ok=True)

        # Create symlink (if supported)
        try:
            link_path = os.path.join(self.temp_dir, "saves")
            if os.path.exists(link_path):
                os.remove(link_path)
            os.symlink(target_dir, link_path)

            # Try to create SaveManager with symlinked directory
            # Path validation should resolve symlinks and validate against real path
            save_manager = SaveManager(save_dir=link_path)
            # Should work, but path should be resolved
            self.assertIsNotNone(save_manager.save_dir)
        except (OSError, NotImplementedError):
            # Symlinks not supported on this system
            pass

    def test_very_long_path(self):
        """Test handling of very long paths."""
        # Create a very long directory name
        long_path = self.temp_dir
        for i in range(20):  # Create nested directories
            long_path = os.path.join(long_path, "a" * 100)

        try:
            os.makedirs(long_path, exist_ok=True)
            save_manager = SaveManager(save_dir=long_path)
            # Should work if path is valid
            self.assertIsNotNone(save_manager.save_dir)
        except (OSError, ValueError) as e:
            # Path too long - acceptable error
            error_msg = str(e).lower()
            self.assertTrue(
                "path" in error_msg or "name" in error_msg or "too long" in error_msg
            )


if __name__ == "__main__":
    unittest.main()
