#!/usr/bin/env python3
"""
Unit tests for the File Organizer program.

These tests verify the core functionality of the FileOrganizer class.
"""

import tempfile
import shutil
from pathlib import Path
import pytest
from file_organizer import FileOrganizer


class TestFileOrganizer:
    """Test cases for FileOrganizer class."""

    def setup_method(self):
        """Set up test environment before each test."""
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)

        # Create test files with different extensions
        self.test_files = {
            'image.jpg': 'Images',
            'document.pdf': 'Documents',
            'spreadsheet.xlsx': 'Spreadsheets',
            'video.mp4': 'Videos',
            'audio.mp3': 'Audio',
            'archive.zip': 'Archives',
            'code.py': 'Code',
            'unknown.xyz': 'Other'
        }

        # Create the test files
        for filename in self.test_files.keys():
            file_path = self.test_path / filename
            file_path.write_text(f"Test content for {filename}")

    def teardown_method(self):
        """Clean up test environment after each test."""
        # Remove the temporary directory
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_init(self):
        """Test FileOrganizer initialization."""
        organizer = FileOrganizer(self.test_dir)
        assert organizer.target_dir == Path(self.test_dir)
        assert organizer.dry_run is False
        assert organizer.file_categories == {}
        assert organizer.actions_taken == []

    def test_init_dry_run(self):
        """Test FileOrganizer initialization with dry run."""
        organizer = FileOrganizer(self.test_dir, dry_run=True)
        assert organizer.target_dir == Path(self.test_dir)
        assert organizer.dry_run is True

    def test_scan_directory(self):
        """Test directory scanning functionality."""
        organizer = FileOrganizer(self.test_dir)
        categories = organizer.scan_directory()

        # Check that all test files are categorized correctly
        assert 'Images' in categories
        assert 'Documents' in categories
        assert 'Spreadsheets' in categories
        assert 'Videos' in categories
        assert 'Audio' in categories
        assert 'Archives' in categories
        assert 'Code' in categories
        assert 'Other' in categories

        # Check specific file counts
        assert len(categories['Images']) == 1
        assert len(categories['Documents']) == 1
        assert len(categories['Code']) == 1
        assert len(categories['Other']) == 1

    def test_scan_nonexistent_directory(self):
        """Test scanning a non-existent directory."""
        organizer = FileOrganizer("/nonexistent/directory")
        with pytest.raises(FileNotFoundError):
            organizer.scan_directory()

    def test_extension_categories(self):
        """Test that extension categories are properly defined."""
        organizer = FileOrganizer(self.test_dir)

        # Test some common extensions
        assert organizer.extension_categories['jpg'] == 'Images'
        assert organizer.extension_categories['pdf'] == 'Documents'
        assert organizer.extension_categories['py'] == 'Code'
        assert organizer.extension_categories['mp4'] == 'Videos'
        assert organizer.extension_categories['mp3'] == 'Audio'
        assert organizer.extension_categories['zip'] == 'Archives'

    def test_create_category_folders_dry_run(self):
        """Test folder creation in dry run mode."""
        organizer = FileOrganizer(self.test_dir, dry_run=True)
        categories = {'Images', 'Documents', 'Code'}

        organizer.create_category_folders(categories)

        # Check that folders were not actually created
        for category in categories:
            folder_path = self.test_path / category
            assert not folder_path.exists()

        # Check that actions were recorded
        assert len(organizer.actions_taken) == 3
        assert all("Would create folder" in action for action in organizer.actions_taken)

    def test_create_category_folders_real(self):
        """Test actual folder creation."""
        organizer = FileOrganizer(self.test_dir, dry_run=False)
        categories = {'Images', 'Documents', 'Code'}

        organizer.create_category_folders(categories)

        # Check that folders were actually created
        for category in categories:
            folder_path = self.test_path / category
            assert folder_path.exists()
            assert folder_path.is_dir()

        # Check that actions were recorded
        assert len(organizer.actions_taken) == 3
        assert all("Created folder" in action for action in organizer.actions_taken)

    def test_move_files_dry_run(self):
        """Test file moving in dry run mode."""
        organizer = FileOrganizer(self.test_dir, dry_run=True)
        organizer.scan_directory()

        # Count files before moving
        files_before = list(self.test_path.glob('*'))
        file_count_before = len([f for f in files_before if f.is_file()])

        organizer.move_files()

        # Check that files were not actually moved
        files_after = list(self.test_path.glob('*'))
        file_count_after = len([f for f in files_after if f.is_file()])
        assert file_count_before == file_count_after

        # Check that actions were recorded
        assert len(organizer.actions_taken) > 0
        # Check that we have both folder creation and file move actions
        move_actions = [action for action in organizer.actions_taken if "Would move" in action]
        folder_actions = [action for action in organizer.actions_taken if "Would create folder" in action]
        assert len(move_actions) > 0
        assert len(folder_actions) > 0

    def test_move_files_real(self):
        """Test actual file moving."""
        organizer = FileOrganizer(self.test_dir, dry_run=False)
        organizer.scan_directory()

        organizer.move_files()

        # Check that files were moved to category folders
        for filename, expected_category in self.test_files.items():
            category_folder = self.test_path / expected_category
            assert category_folder.exists()

            file_path = category_folder / filename
            assert file_path.exists()

            # Check that original file no longer exists in root
            original_path = self.test_path / filename
            assert not original_path.exists()

    def test_generate_report(self):
        """Test report generation."""
        organizer = FileOrganizer(self.test_dir)
        organizer.scan_directory()
        organizer.move_files()

        # This test mainly checks that the method doesn't crash
        # and produces some output
        organizer.generate_report()

        # Check that actions were recorded
        assert len(organizer.actions_taken) > 0

    def test_organize_dry_run(self):
        """Test the complete organize process in dry run mode."""
        organizer = FileOrganizer(self.test_dir, dry_run=True)

        # Count files before organizing
        files_before = list(self.test_path.glob('*'))
        file_count_before = len([f for f in files_before if f.is_file()])

        organizer.organize()

        # Check that files were not actually moved
        files_after = list(self.test_path.glob('*'))
        file_count_after = len([f for f in files_after if f.is_file()])
        assert file_count_before == file_count_after

        # Check that actions were recorded
        assert len(organizer.actions_taken) > 0


def test_main_function():
    """Test that the main function can be imported without errors."""
    # This is a basic test to ensure the module can be imported
    import file_organizer
    assert hasattr(file_organizer, 'main')
    assert callable(file_organizer.main)


if __name__ == "__main__":
    # Run tests if script is executed directly
    pytest.main([__file__, "-v"])
