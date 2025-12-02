"""Tests for backup_zip_script package."""

import logging
import sys
import zipfile
from pathlib import Path

import pytest

from backup_zip_script.core import (
    _get_files_to_backup,
    _matches_exclude_patterns,
    _rotate_backups,
    _verify_zip_integrity,
    create_backup_zip,
)
from backup_zip_script import main as cli_main
from backup_zip_script.utils import format_size


class TestCreateBackupZip:
    """Test the main create_backup_zip function."""

    def test_successful_backup(self, temp_dir, backup_dir):
        """Test successful backup creation."""
        # Create test files
        test_file = temp_dir / "test.txt"
        test_file.write_text("test content")

        # Create backup
        backup_path = create_backup_zip(temp_dir, backup_dir)

        # Verify backup was created
        assert backup_path.exists()
        assert backup_path.name.startswith("backup_")
        assert backup_path.name.endswith(".zip")

        # Verify ZIP contents
        with zipfile.ZipFile(backup_path, "r") as zipf:
            assert "test.txt" in zipf.namelist()

    def test_backup_with_subdirectory(self, temp_dir, backup_dir):
        """Test backup includes subdirectories."""
        # Create test structure
        subdir = temp_dir / "subdir"
        subdir.mkdir()
        test_file = subdir / "nested.txt"
        test_file.write_text("nested content")

        # Create backup
        backup_path = create_backup_zip(temp_dir, backup_dir)

        # Verify ZIP contents
        with zipfile.ZipFile(backup_path, "r") as zipf:
            assert "subdir/nested.txt" in zipf.namelist()

    def test_nonexistent_source_directory(self, backup_dir):
        """Test error when source directory doesn't exist."""
        nonexistent = Path("/nonexistent/path")

        with pytest.raises(ValueError, match="does not exist"):
            create_backup_zip(nonexistent, backup_dir)

    def test_source_is_file_not_directory(self, temp_dir, backup_dir):
        """Test error when source is a file instead of directory."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("content")

        with pytest.raises(ValueError, match="is not a directory"):
            create_backup_zip(test_file, backup_dir)


class TestExcludePatterns:
    """Test exclude pattern functionality."""

    def test_exclude_pycache_directory(self, temp_dir):
        """Test excluding __pycache__ directories."""
        # Create test structure
        pycache_dir = temp_dir / "__pycache__"
        pycache_dir.mkdir()
        pycache_file = pycache_dir / "module.pyc"
        pycache_file.write_text("compiled")

        regular_file = temp_dir / "regular.py"
        regular_file.write_text("python code")

        files = _get_files_to_backup(temp_dir, [])

        assert regular_file in files
        assert pycache_file not in files

    def test_exclude_git_directory(self, temp_dir):
        """Test excluding .git directories."""
        # Create test structure
        git_dir = temp_dir / ".git"
        git_dir.mkdir()
        git_file = git_dir / "config"
        git_file.write_text("git config")

        regular_file = temp_dir / "script.py"
        regular_file.write_text("python code")

        files = _get_files_to_backup(temp_dir, [])

        assert regular_file in files
        assert git_file not in files

    def test_custom_exclude_patterns(self, temp_dir):
        """Test custom exclude patterns."""
        # Create test files
        log_file = temp_dir / "debug.log"
        log_file.write_text("log content")

        tmp_file = temp_dir / "temp.tmp"
        tmp_file.write_text("temp content")

        py_file = temp_dir / "script.py"
        py_file.write_text("python code")

        files = _get_files_to_backup(temp_dir, ["*.log", "*.tmp"])

        assert py_file in files
        assert log_file not in files
        assert tmp_file not in files

    def test_exclude_directory_name_exact_match(self, temp_dir):
        """Exclude patterns should match directory names, not substrings."""
        catalog_dir = temp_dir / "catalog"
        catalog_dir.mkdir()
        file_in_catalog = catalog_dir / "data.txt"
        file_in_catalog.write_text("data")

        files = _get_files_to_backup(temp_dir, ["logs"])

        assert file_in_catalog in files

    def test_exclude_nested_directory(self, temp_dir):
        """Exclude should remove files living under excluded directories."""
        node_modules = temp_dir / "node_modules"
        node_modules.mkdir()
        nested = node_modules / "module.js"
        nested.write_text("console.log('hi');")

        keep_file = temp_dir / "app.js"
        keep_file.write_text("console.log('app');")

        files = _get_files_to_backup(temp_dir, ["node_modules"])

        assert keep_file in files
        assert nested not in files

    def test_exclude_pattern_matching(self):
        """Test the exclude pattern matching logic."""
        test_path = Path("/test/__pycache__/file.pyc")

        assert _matches_exclude_patterns(test_path, {"__pycache__"})
        assert _matches_exclude_patterns(test_path, {"*.pyc"})
        assert not _matches_exclude_patterns(test_path, {"*.py"})


class TestZipVerification:
    """Test ZIP integrity verification."""

    def test_valid_zip_verification(self, temp_dir, backup_dir):
        """Test verification of valid ZIP file."""
        # Create test file and backup
        test_file = temp_dir / "test.txt"
        test_file.write_text("test content")

        backup_path = create_backup_zip(temp_dir, backup_dir)

        # Verify integrity
        assert _verify_zip_integrity(backup_path)

    def test_corrupted_zip_detection(self, backup_dir):
        """Test detection of corrupted ZIP file."""
        # Create a corrupted ZIP file
        corrupted_zip = backup_dir / "corrupted.zip"
        corrupted_zip.write_bytes(b"not a zip file")

        assert not _verify_zip_integrity(corrupted_zip)


class TestRotationPolicy:
    """Test backup rotation functionality."""

    def test_rotation_removes_old_backups(self, backup_dir):
        """Test that old backups are removed when exceeding max_backups."""
        # Create multiple backup files with different timestamps
        for i in range(5):
            backup_file = backup_dir / f"backup_20230101_000{i}.zip"
            backup_file.write_text("dummy")
            # Set modification time to simulate age
            import time
            import os

            os.utime(
                backup_file,
                (time.time() - (4 - i) * 3600, time.time() - (4 - i) * 3600),
            )

        # Apply rotation with max 3 backups
        _rotate_backups(backup_dir, 3)

        # Should have only 3 files left
        backup_files = list(backup_dir.glob("backup_*.zip"))
        assert len(backup_files) == 3

    def test_rotation_keeps_recent_backups(self, backup_dir):
        """Test that most recent backups are kept."""
        # Create backup files
        for i in range(5):
            backup_file = backup_dir / f"backup_20230101_000{i}.zip"
            backup_file.write_text("dummy")
            import time
            import os

            # Set modification time (newer files have higher timestamps)
            os.utime(backup_file, (time.time() + i * 3600, time.time() + i * 3600))

        _rotate_backups(backup_dir, 2)

        backup_files = sorted(
            backup_dir.glob("backup_*.zip"),
            key=lambda x: x.stat().st_mtime,
            reverse=True,
        )
        assert len(backup_files) == 2
        # The two most recent should remain
        assert backup_files[0].name == "backup_20230101_0004.zip"
        assert backup_files[1].name == "backup_20230101_0003.zip"


class TestLogging:
    """Test logging functionality."""

    def test_backup_creation_logging(self, temp_dir, backup_dir, caplog):
        """Test that backup creation is logged."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("content")

        with caplog.at_level(logging.INFO):
            create_backup_zip(temp_dir, backup_dir)

        assert "Creating backup:" in caplog.text
        assert "Backup created successfully:" in caplog.text

    def test_error_logging(self, temp_dir, backup_dir, caplog):
        """Test that backup errors are logged."""
        # Create a scenario that will cause a backup error
        # Make backup_dir read-only to cause an error
        import stat

        backup_dir.chmod(stat.S_IRUSR | stat.S_IXUSR)  # Read and execute only

        test_file = temp_dir / "test.txt"
        test_file.write_text("content")

        with caplog.at_level(logging.ERROR):
            with pytest.raises(OSError):
                create_backup_zip(temp_dir, backup_dir)

        # Restore permissions
        backup_dir.chmod(stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)

        assert "Backup creation failed" in caplog.text


class TestUtils:
    """Test utility helpers."""

    def test_format_size_small_values(self):
        """Format bytes into human readable units."""
        assert format_size(0) == "0.0 B"
        assert format_size(512) == "512.0 B"

    def test_format_size_larger_units(self):
        """Convert using higher units."""
        assert format_size(1024) == "1.0 KB"
        assert format_size(1536) == "1.5 KB"
        assert format_size(1024 * 1024) == "1.0 MB"
        assert format_size(1024 * 1024 * 1024) == "1.0 GB"


class TestCLI:
    """Test command line interface behavior."""

    def test_multiple_exclude_values_single_flag(self, tmp_path, monkeypatch):
        """CLI should accept multiple patterns after one --exclude flag."""
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        keep_file = source_dir / "keep.txt"
        keep_file.write_text("keep me")
        ignored_log = source_dir / "debug.log"
        ignored_log.write_text("log")
        ignored_tmp = source_dir / "cache.tmp"
        ignored_tmp.write_text("tmp")

        backup_dir = tmp_path / "backups"

        argv = [
            "backup-zip-script",
            str(source_dir),
            "--backup-dir",
            str(backup_dir),
            "--exclude",
            "*.log",
            "*.tmp",
        ]
        monkeypatch.setattr(sys, "argv", argv)

        exit_code = cli_main.main()
        assert exit_code == 0

        backups = list(backup_dir.glob("backup_*.zip"))
        assert len(backups) == 1

        with zipfile.ZipFile(backups[0], "r") as zipf:
            names = set(zipf.namelist())

        assert "keep.txt" in names
        assert "debug.log" not in names
        assert "cache.tmp" not in names


# Pytest fixtures
@pytest.fixture
def temp_dir(tmp_path):
    """Create a temporary directory for testing."""
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    return source_dir


@pytest.fixture
def backup_dir(tmp_path):
    """Create a temporary backup directory."""
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    return backup_dir
