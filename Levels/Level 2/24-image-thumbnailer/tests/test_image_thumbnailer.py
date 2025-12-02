"""Tests for image thumbnailer."""

import tempfile
from pathlib import Path
from unittest.mock import patch

from PIL import Image

from image_thumbnailer import core, utils


class TestUtils:
    """Test utility functions."""

    def test_validate_image_path_valid(self):
        """Test validating a valid image path."""
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            img = Image.new("RGB", (100, 100), color="red")
            img.save(f.name)
            path = Path(f.name)

        try:
            assert utils.validate_image_path(path) is True
        finally:
            path.unlink()

    def test_validate_image_path_invalid_extension(self):
        """Test validating path with invalid extension."""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"not an image")
            path = Path(f.name)

        try:
            assert utils.validate_image_path(path) is False
        finally:
            path.unlink()

    def test_validate_image_path_nonexistent(self):
        """Test validating nonexistent path."""
        path = Path("/nonexistent/image.jpg")
        assert utils.validate_image_path(path) is False

    def test_find_image_files(self):
        """Test finding image files in directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test images
            img1 = Image.new("RGB", (50, 50), color="blue")
            img1.save(temp_path / "test1.jpg")
            img1.save(temp_path / "test2.png")

            # Create non-image file
            (temp_path / "text.txt").write_text("not an image")

            images = utils.find_image_files(temp_path)
            assert len(images) == 2
            assert all(img.suffix.lower() in {".jpg", ".png"} for img in images)

    def test_parse_size_valid(self):
        """Test parsing valid size string."""
        assert utils.parse_size("200x300") == (200, 300)
        assert utils.parse_size("100x100") == (100, 100)

    def test_parse_size_invalid(self):
        """Test parsing invalid size string."""
        assert utils.parse_size("invalid") is None
        assert utils.parse_size("200") is None
        assert utils.parse_size("200x300x400") is None


class TestCore:
    """Test core functionality."""

    def test_resize_image_maintain_aspect(self):
        """Test resizing with aspect ratio preservation."""
        img = Image.new("RGB", (400, 200), color="green")
        resized = core.resize_image(img, (200, 200), maintain_aspect=True)

        # Should maintain aspect ratio, so height should be 100
        assert resized.size == (200, 100)

    def test_resize_image_no_aspect(self):
        """Test resizing without aspect ratio preservation."""
        img = Image.new("RGB", (400, 200), color="green")
        resized = core.resize_image(img, (200, 200), maintain_aspect=False)

        assert resized.size == (200, 200)

    def test_add_watermark(self):
        """Test adding watermark to image."""
        img = Image.new("RGB", (200, 200), color="white")
        watermarked = core.add_watermark(img, "TEST")

        # Image should still be RGB and same size
        assert watermarked.mode == "RGB"
        assert watermarked.size == (200, 200)

    def test_add_border(self):
        """Test adding border to image."""
        img = Image.new("RGB", (100, 100), color="red")
        bordered = core.add_border(img, border_width=10, color="black")

        assert bordered.size == (120, 120)
        # Check border color at edges
        assert bordered.getpixel((0, 0)) == (0, 0, 0)  # black border
        assert bordered.getpixel((15, 15)) == (255, 0, 0)  # red image

    def test_preserve_exif_orientation(self):
        """Test EXIF orientation preservation."""
        img = Image.new("RGB", (100, 100), color="blue")
        # Test with no EXIF data
        oriented = core.preserve_exif_orientation(img)
        assert oriented.size == (100, 100)

    def test_create_thumbnail_success(self):
        """Test successful thumbnail creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test image
            img = Image.new("RGB", (400, 400), color="yellow")
            input_path = temp_path / "input.jpg"
            img.save(input_path)

            output_path = temp_path / "output.jpg"

            success = core.create_thumbnail(
                input_path=input_path, output_path=output_path, size=(200, 200)
            )

            assert success is True
            assert output_path.exists()
            with Image.open(output_path) as thumb:
                assert thumb.size == (200, 200)

    def test_create_thumbnail_invalid_input(self):
        """Test thumbnail creation with invalid input."""
        output_path = Path("/tmp/output.jpg")

        success = core.create_thumbnail(
            input_path=Path("/nonexistent.jpg"),
            output_path=output_path,
            size=(200, 200),
        )

        assert success is False

    def test_create_thumbnail_unsupported_format(self):
        """Test thumbnail creation with unsupported format."""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"not an image")
            input_path = Path(f.name)
            output_path = Path("/tmp/output.jpg")

        try:
            success = core.create_thumbnail(
                input_path=input_path, output_path=output_path, size=(200, 200)
            )
            assert success is False
        finally:
            input_path.unlink()

    def test_create_thumbnail_unsupported_output_format(self):
        """Unsupported output extensions should fail instead of reporting success."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            img = Image.new("RGB", (200, 200), color="purple")
            input_path = temp_path / "input.jpg"
            img.save(input_path)

            output_path = temp_path / "thumb.bmp"
            success = core.create_thumbnail(
                input_path=input_path, output_path=output_path, size=(100, 100)
            )

            assert success is False
            assert not output_path.exists()

    def test_batch_create_thumbnails(self):
        """Test batch thumbnail creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            input_dir = temp_path / "input"
            output_dir = temp_path / "output"
            input_dir.mkdir()

            # Create test images
            img1 = Image.new("RGB", (300, 300), color="red")
            img1.save(input_dir / "img1.jpg")
            img2 = Image.new("RGB", (300, 300), color="blue")
            img2.save(input_dir / "img2.png")

            count = core.batch_create_thumbnails(
                input_dir=input_dir, output_dir=output_dir, size=(150, 150)
            )

            assert count == 2
            assert (output_dir / "thumb_img1.jpg").exists()
            assert (output_dir / "thumb_img2.png").exists()

    def test_batch_create_thumbnails_invalid_dir(self):
        """Test batch creation with invalid directory."""
        count = core.batch_create_thumbnails(
            input_dir=Path("/nonexistent"),
            output_dir=Path("/tmp/output"),
            size=(100, 100),
        )

        assert count == 0


class TestCLI:
    """Test CLI functionality."""

    @patch("image_thumbnailer.main.core.create_thumbnail")
    def test_main_single_file(self, mock_create):
        """Test CLI with single file."""
        mock_create.return_value = True

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            img_path = temp_path / "test.jpg"
            Image.new("RGB", (100, 100), color="white").save(img_path)

            # Mock sys.argv
            with patch(
                "sys.argv",
                [
                    "image_thumbnailer",
                    str(img_path),
                    "-s",
                    "200x200",
                    "-o",
                    str(temp_path / "thumb.jpg"),
                ],
            ):
                from image_thumbnailer.main import main

                result = main()
                assert result == 0
                mock_create.assert_called_once()

    def test_main_invalid_size(self):
        """Test CLI with invalid size."""
        with patch("sys.argv", ["image_thumbnailer", "test.jpg", "-s", "invalid"]):
            from image_thumbnailer.main import main

            result = main()
            assert result == 1
