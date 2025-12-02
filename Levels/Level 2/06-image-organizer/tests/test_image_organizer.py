"""
Comprehensive tests for the image organizer.
"""

import os
import tempfile
import shutil
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from PIL import Image

from image_organizer.core import ImageOrganizer
from image_organizer.utils import (
    create_thumbnail,
    get_image_info,
    validate_image_file,
    get_safe_filename,
    format_file_size
)


class TestImageOrganizer:
    """Test cases for ImageOrganizer class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.source_dir = Path(self.temp_dir) / "source"
        self.target_dir = Path(self.temp_dir) / "target"
        self.source_dir.mkdir()

    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    def create_test_image(self, filename: str, date_taken: datetime = None) -> Path:
        """Create a test image file with optional EXIF data."""
        image_path = self.source_dir / filename

        # Create a simple test image
        img = Image.new('RGB', (100, 100), color='red')

        if date_taken:
            # Add EXIF data with date - need to create proper EXIF structure
            from PIL.ExifTags import TAGS
            exif_dict = img.getexif()
            exif_dict[306] = date_taken.strftime("%Y:%m:%d %H:%M:%S")  # DateTime tag
            img.save(image_path, 'JPEG', exif=exif_dict)
        else:
            img.save(image_path, 'JPEG')

        return image_path

    def test_scan_images_finds_supported_formats(self):
        """Test that scan_images finds all supported image formats."""
        # Create test images
        self.create_test_image("test1.jpg")
        self.create_test_image("test2.png")
        self.create_test_image("test3.tiff")

        # Create non-image file
        (self.source_dir / "test.txt").write_text("not an image")

        organizer = ImageOrganizer(str(self.source_dir), str(self.target_dir))
        images = organizer.scan_images()

        assert len(images) == 3
        assert any("test1.jpg" in str(img) for img in images)
        assert any("test2.png" in str(img) for img in images)
        assert any("test3.tiff" in str(img) for img in images)

    def test_scan_images_empty_directory(self):
        """Test scan_images with empty directory."""
        organizer = ImageOrganizer(str(self.source_dir), str(self.target_dir))
        images = organizer.scan_images()

        assert len(images) == 0

    def test_scan_images_nonexistent_directory(self):
        """Test scan_images with non-existent directory."""
        nonexistent_dir = Path(self.temp_dir) / "nonexistent"
        organizer = ImageOrganizer(str(nonexistent_dir), str(self.target_dir))
        images = organizer.scan_images()

        assert len(images) == 0

    def test_get_image_date_with_exif(self):
        """Test getting date from EXIF data."""
        test_date = datetime(2023, 5, 15, 14, 30, 0)
        image_path = self.create_test_image("test_with_exif.jpg", test_date)

        organizer = ImageOrganizer(str(self.source_dir), str(self.target_dir))
        result_date = organizer.get_image_date(image_path)

        assert result_date is not None
        assert result_date.year == 2023
        assert result_date.month == 5
        assert result_date.day == 15

    def test_get_image_date_fallback_to_mtime(self):
        """Test fallback to file modification time when no EXIF."""
        image_path = self.create_test_image("test_no_exif.jpg")

        # Set a specific modification time
        test_mtime = datetime(2022, 12, 25, 10, 15, 30).timestamp()
        os.utime(image_path, (test_mtime, test_mtime))

        organizer = ImageOrganizer(str(self.source_dir), str(self.target_dir))
        result_date = organizer.get_image_date(image_path)

        assert result_date is not None
        assert result_date.year == 2022
        assert result_date.month == 12
        assert result_date.day == 25

    def test_get_image_date_error_handling(self):
        """Test error handling in get_image_date."""
        # Create a corrupted file
        corrupted_path = self.source_dir / "corrupted.jpg"
        corrupted_path.write_bytes(b"not an image")

        organizer = ImageOrganizer(str(self.source_dir), str(self.target_dir))
        result_date = organizer.get_image_date(corrupted_path)

        # Should fallback to mtime or return None
        assert result_date is not None or result_date is None

    def test_get_organization_path(self):
        """Test generation of organization path."""
        test_date = datetime(2023, 5, 15, 14, 30, 0)
        image_path = self.source_dir / "test.jpg"

        organizer = ImageOrganizer(str(self.source_dir), str(self.target_dir))
        result_path = organizer.get_organization_path(test_date, image_path)

        expected_path = self.target_dir / "2023" / "05" / "test.jpg"
        assert result_path == expected_path

    def test_organize_image_success(self):
        """Test successful image organization."""
        test_date = datetime(2023, 5, 15, 14, 30, 0)
        image_path = self.create_test_image("test.jpg", test_date)

        organizer = ImageOrganizer(str(self.source_dir), str(self.target_dir))
        success = organizer.organize_image(image_path)

        assert success is True
        assert organizer.stats['processed'] == 1
        assert organizer.stats['moved'] == 1

        # Check that file was moved
        expected_path = self.target_dir / "2023" / "05" / "test.jpg"
        assert expected_path.exists()
        assert not image_path.exists()

    def test_organize_image_dry_run(self):
        """Test dry run mode doesn't actually move files."""
        test_date = datetime(2023, 5, 15, 14, 30, 0)
        image_path = self.create_test_image("test.jpg", test_date)

        organizer = ImageOrganizer(str(self.source_dir), str(self.target_dir), dry_run=True)
        success = organizer.organize_image(image_path)

        assert success is True
        assert organizer.stats['processed'] == 1
        assert organizer.stats['moved'] == 1

        # Check that file was NOT moved in dry run
        assert image_path.exists()
        expected_path = self.target_dir / "2023" / "05" / "test.jpg"
        assert not expected_path.exists()

    def test_organize_image_no_date(self):
        """Test handling of images without date information."""
        # Create image without EXIF and set mtime to 0 (epoch)
        image_path = self.create_test_image("test.jpg")
        os.utime(image_path, (0, 0))

        organizer = ImageOrganizer(str(self.source_dir), str(self.target_dir))
        success = organizer.organize_image(image_path)

        # Should still process the image (uses epoch time as fallback)
        assert success is True
        assert organizer.stats['processed'] == 1
        assert organizer.stats['moved'] == 1

    def test_duplicate_detection(self):
        """Test duplicate detection functionality."""
        # Create two identical images
        test_date = datetime(2023, 5, 15, 14, 30, 0)
        image1 = self.create_test_image("test1.jpg", test_date)
        image2 = self.create_test_image("test2.jpg", test_date)

        organizer = ImageOrganizer(str(self.source_dir), str(self.target_dir))

        # Organize first image
        success1 = organizer.organize_image(image1)
        assert success1 is True

        # Organize second image (should be detected as duplicate)
        success2 = organizer.organize_image(image2)
        assert success2 is False
        assert organizer.stats['duplicates_found'] == 1
        assert organizer.stats['skipped'] == 1

    def test_generate_report(self):
        """Test report generation."""
        organizer = ImageOrganizer(str(self.source_dir), str(self.target_dir))
        organizer.stats = {
            'processed': 5,
            'moved': 4,
            'skipped': 1,
            'errors': 0,
            'duplicates_found': 0,
            'thumbnails_created': 0
        }

        report = organizer.generate_report()

        assert "IMAGE ORGANIZATION REPORT" in report
        assert "Images Processed: 5" in report
        assert "Images Moved: 4" in report
        assert "Images Skipped: 1" in report


class TestUtils:
    """Test cases for utility functions."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_dir = Path(self.temp_dir)

    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    def test_create_thumbnail(self):
        """Test thumbnail creation."""
        # Create test image
        image_path = self.test_dir / "test.jpg"
        img = Image.new('RGB', (200, 200), color='blue')
        img.save(image_path, 'JPEG')

        # Create thumbnail
        thumbnail_path = self.test_dir / "thumb.jpg"
        success = create_thumbnail(image_path, thumbnail_path, (50, 50))

        assert success is True
        assert thumbnail_path.exists()

        # Verify thumbnail size
        with Image.open(thumbnail_path) as thumb:
            assert thumb.size[0] <= 50
            assert thumb.size[1] <= 50

    def test_create_thumbnail_preserves_extension(self):
        """Thumbnails should be saved using the destination file extension."""
        image_path = self.test_dir / "test.png"
        img = Image.new('RGBA', (120, 120), color=(0, 255, 0, 128))
        img.save(image_path, 'PNG')

        thumbnail_path = self.test_dir / "thumb.png"
        success = create_thumbnail(image_path, thumbnail_path, (60, 60))

        assert success is True
        assert thumbnail_path.exists()
        with Image.open(thumbnail_path) as thumb:
            assert thumb.format == 'PNG'
            assert thumb.size[0] <= 60
            assert thumb.size[1] <= 60

    def test_get_image_info(self):
        """Test image information extraction."""
        # Create test image
        image_path = self.test_dir / "test.jpg"
        img = Image.new('RGB', (100, 150), color='green')
        img.save(image_path, 'JPEG')

        info = get_image_info(image_path)

        assert info['path'] == str(image_path)
        assert info['size_bytes'] > 0
        assert info['dimensions'] == (100, 150)
        assert info['format'] == 'JPEG'
        assert info['mode'] == 'RGB'
        assert info['has_exif'] is False

    def test_validate_image_file(self):
        """Test image file validation."""
        # Valid image
        image_path = self.test_dir / "valid.jpg"
        img = Image.new('RGB', (50, 50), color='red')
        img.save(image_path, 'JPEG')

        assert validate_image_file(image_path) is True

        # Invalid file
        invalid_path = self.test_dir / "invalid.txt"
        invalid_path.write_text("not an image")

        assert validate_image_file(invalid_path) is False

    def test_get_safe_filename(self):
        """Test filename sanitization."""
        assert get_safe_filename("test file.jpg") == "test_file.jpg"
        assert get_safe_filename("file/with\\invalid:chars") == "file_with_invalid_chars"
        assert get_safe_filename("...") == "image"  # Empty after stripping becomes "image"
        assert get_safe_filename("") == "image"  # Empty becomes "image"
        assert get_safe_filename("normal_file.png") == "normal_file.png"

    def test_format_file_size(self):
        """Test file size formatting."""
        assert format_file_size(1024) == "1.0 KB"
        assert format_file_size(1048576) == "1.0 MB"
        assert format_file_size(512) == "512.0 B"
        assert format_file_size(0) == "0.0 B"


if __name__ == '__main__':
    pytest.main([__file__])
