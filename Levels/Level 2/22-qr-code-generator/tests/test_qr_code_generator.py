"""
Comprehensive unit tests for QR Code Generator

Tests core functionality, edge cases, and error handling.
"""

import unittest
import tempfile
import os
import csv
from unittest.mock import patch, MagicMock
from pathlib import Path

from qr_code_generator.core import QRCodeGenerator
from qr_code_generator.utils import (
    validate_url, validate_email, validate_phone, create_vcard,
    parse_csv_batch, sanitize_filename, get_error_correction_level
)


class TestUtils(unittest.TestCase):
    """Test utility functions."""

    def test_validate_url(self):
        """Test URL validation."""
        # Valid URLs
        self.assertTrue(validate_url("https://www.example.com"))
        self.assertTrue(validate_url("http://example.com"))
        self.assertTrue(validate_url("https://example.com/path"))
        self.assertTrue(validate_url("ftp://example.com"))

        # Invalid URLs
        self.assertFalse(validate_url("not-a-url"))
        self.assertFalse(validate_url("www.example.com"))
        self.assertFalse(validate_url("example.com"))
        self.assertFalse(validate_url(""))

    def test_validate_email(self):
        """Test email validation."""
        # Valid emails
        self.assertTrue(validate_email("test@example.com"))
        self.assertTrue(validate_email("user.name@domain.co.uk"))
        self.assertTrue(validate_email("user+tag@example.org"))

        # Invalid emails
        self.assertFalse(validate_email("not-an-email"))
        self.assertFalse(validate_email("@example.com"))
        self.assertFalse(validate_email("user@"))
        self.assertFalse(validate_email("user.example.com"))

    def test_validate_phone(self):
        """Test phone validation."""
        # Valid phones
        self.assertTrue(validate_phone("1234567890"))
        self.assertTrue(validate_phone("+1234567890"))
        self.assertTrue(validate_phone("(123) 456-7890"))
        self.assertTrue(validate_phone("123-456-7890"))

        # Invalid phones
        self.assertFalse(validate_phone("123"))
        self.assertFalse(validate_phone("abc123"))
        self.assertFalse(validate_phone(""))

    def test_create_vcard(self):
        """Test vCard creation."""
        # Basic vCard
        vcard = create_vcard("John Doe")
        self.assertIn("BEGIN:VCARD", vcard)
        self.assertIn("FN:John Doe", vcard)
        self.assertIn("END:VCARD", vcard)

        # Full vCard
        vcard = create_vcard(
            name="Jane Smith",
            phone="+1234567890",
            email="jane@example.com",
            org="Acme Corp",
            url="https://example.com"
        )
        self.assertIn("FN:Jane Smith", vcard)
        self.assertIn("TEL:+1234567890", vcard)
        self.assertIn("EMAIL:jane@example.com", vcard)
        self.assertIn("ORG:Acme Corp", vcard)
        self.assertIn("URL:https://example.com", vcard)

        # Empty name should raise error
        with self.assertRaises(ValueError):
            create_vcard("")

    def test_sanitize_filename(self):
        """Test filename sanitization."""
        # Valid characters
        self.assertEqual(sanitize_filename("valid_name.txt"), "valid_name.txt")

        # Invalid characters
        self.assertEqual(sanitize_filename("invalid<>name"), "invalid__name")
        self.assertEqual(sanitize_filename("path/to/file"), "path_to_file")

        # Edge cases
        self.assertEqual(sanitize_filename(""), "qr_code")
        self.assertEqual(sanitize_filename("..."), "qr_code")
        self.assertEqual(sanitize_filename("   "), "qr_code")

    def test_get_error_correction_level(self):
        """Test error correction level conversion."""
        self.assertEqual(get_error_correction_level('L'), 1)
        self.assertEqual(get_error_correction_level('M'), 0)
        self.assertEqual(get_error_correction_level('Q'), 3)
        self.assertEqual(get_error_correction_level('H'), 2)

        # Case insensitive
        self.assertEqual(get_error_correction_level('l'), 1)
        self.assertEqual(get_error_correction_level('m'), 0)

        # Invalid level
        with self.assertRaises(ValueError):
            get_error_correction_level('X')

    def test_parse_csv_batch(self):
        """Test CSV batch parsing."""
        # Create temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            writer = csv.writer(f)
            writer.writerow(['data', 'filename', 'type', 'size', 'format'])
            writer.writerow(['https://example.com', 'example', 'url', '15', 'png'])
            writer.writerow(['Hello World', 'hello', 'text', '10', 'svg'])
            csv_path = f.name

        try:
            batch_data = parse_csv_batch(csv_path)

            self.assertEqual(len(batch_data), 2)

            # Check first entry
            self.assertEqual(batch_data[0]['data'], 'https://example.com')
            self.assertEqual(batch_data[0]['filename'], 'example')
            self.assertEqual(batch_data[0]['type'], 'url')
            self.assertEqual(batch_data[0]['size'], 15)
            self.assertEqual(batch_data[0]['format'], 'png')

            # Check second entry
            self.assertEqual(batch_data[1]['data'], 'Hello World')
            self.assertEqual(batch_data[1]['filename'], 'hello')
            self.assertEqual(batch_data[1]['type'], 'text')
            self.assertEqual(batch_data[1]['size'], 10)
            self.assertEqual(batch_data[1]['format'], 'svg')

        finally:
            os.unlink(csv_path)

        # Test missing data column
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            writer = csv.writer(f)
            writer.writerow(['filename', 'type'])
            writer.writerow(['test', 'text'])
            csv_path = f.name

        try:
            with self.assertRaises(ValueError):
                parse_csv_batch(csv_path)
        finally:
            os.unlink(csv_path)

        # Test non-existent file
        with self.assertRaises(FileNotFoundError):
            parse_csv_batch('non_existent.csv')


class TestQRCodeGenerator(unittest.TestCase):
    """Test QRCodeGenerator class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.generator = QRCodeGenerator()

    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up temporary files
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_initialization(self):
        """Test QRCodeGenerator initialization."""
        # Default initialization
        gen = QRCodeGenerator()
        self.assertEqual(gen.size, 10)
        self.assertEqual(gen.error_correction, 0)  # M level
        self.assertEqual(gen.fill_color, 'black')
        self.assertEqual(gen.back_color, 'white')

        # Custom initialization
        gen = QRCodeGenerator(size=15, error_correction='H',
                            fill_color='blue', back_color='yellow')
        self.assertEqual(gen.size, 15)
        self.assertEqual(gen.error_correction, 2)  # H level
        self.assertEqual(gen.fill_color, 'blue')
        self.assertEqual(gen.back_color, 'yellow')

    def test_generate_text_qr(self):
        """Test text QR code generation."""
        output_path = os.path.join(self.temp_dir, 'test_text.png')

        result_path = self.generator.generate_text_qr("Hello World", output_path)

        self.assertEqual(result_path, output_path)
        self.assertTrue(os.path.exists(output_path))

        # Check file size (should be > 0)
        self.assertGreater(os.path.getsize(output_path), 0)

    def test_generate_url_qr(self):
        """Test URL QR code generation."""
        output_path = os.path.join(self.temp_dir, 'test_url.png')

        result_path = self.generator.generate_url_qr("https://example.com", output_path)

        self.assertEqual(result_path, output_path)
        self.assertTrue(os.path.exists(output_path))

        # Test invalid URL
        with self.assertRaises(ValueError):
            self.generator.generate_url_qr("invalid-url")

    def test_generate_vcard_qr(self):
        """Test vCard QR code generation."""
        output_path = os.path.join(self.temp_dir, 'test_vcard.png')

        result_path = self.generator.generate_vcard_qr(
            name="John Doe",
            phone="+1234567890",
            email="john@example.com",
            output_path=output_path
        )

        self.assertEqual(result_path, output_path)
        self.assertTrue(os.path.exists(output_path))

    @patch('qr_code_generator.core.qrcode.QRCode')
    def test_generate_uses_configured_error_correction(self, mock_qrcode_cls):
        """Ensure requested error correction level is forwarded to qrcode."""
        generator = QRCodeGenerator(error_correction='H')

        mock_qr = MagicMock()
        mock_qrcode_cls.return_value = mock_qr

        mock_image = MagicMock()
        mock_image.mode = "RGB"

        def fake_save(path, fmt=None):
            with open(path, 'wb') as file_obj:
                file_obj.write(b'data')

        mock_image.save.side_effect = fake_save
        mock_qr.make_image.return_value = mock_image

        output_path = os.path.join(self.temp_dir, 'ec.png')
        generator.generate_text_qr("data", output_path)

        _, kwargs = mock_qrcode_cls.call_args
        self.assertEqual(
            kwargs['error_correction'],
            get_error_correction_level('H'),
        )
        self.assertTrue(os.path.exists(output_path))

    def test_generate_svg_qr(self):
        """Test SVG QR code generation."""
        output_path = os.path.join(self.temp_dir, 'test.svg')

        result_path = self.generator.generate_text_qr("Hello World", output_path, 'svg')

        self.assertEqual(result_path, output_path)
        self.assertTrue(os.path.exists(output_path))

        # Check if it's actually SVG content
        with open(output_path, 'r') as f:
            content = f.read()
            self.assertIn('<svg', content)
            self.assertIn('</svg>', content)

    def test_auto_filename_generation(self):
        """Test automatic filename generation."""
        result_path = self.generator.generate_text_qr("Test Message")

        self.assertTrue(result_path.endswith('.png'))
        self.assertTrue(os.path.exists(result_path))

        # Clean up
        os.unlink(result_path)

    def test_empty_data_error(self):
        """Test error handling for empty data."""
        with self.assertRaises(ValueError):
            self.generator.generate_qr_code("")

        with self.assertRaises(ValueError):
            self.generator.generate_qr_code("   ")

    def test_batch_generation(self):
        """Test batch QR code generation."""
        batch_data = [
            {'data': 'First QR', 'type': 'text'},
            {'data': 'https://example.com', 'type': 'url'},
            {'data': 'Second QR', 'type': 'text', 'filename': 'custom_name'}
        ]

        output_dir = os.path.join(self.temp_dir, 'batch_output')
        generated_files = self.generator.generate_batch_qr_codes(batch_data, output_dir)

        self.assertEqual(len(generated_files), 3)
        self.assertTrue(os.path.exists(output_dir))

        # Check all files exist
        for file_path in generated_files:
            self.assertTrue(os.path.exists(file_path))
            self.assertGreater(os.path.getsize(file_path), 0)

    def test_batch_generation_empty_data(self):
        """Test batch generation with empty data."""
        with self.assertRaises(ValueError):
            self.generator.generate_batch_qr_codes([])

    @patch('PIL.Image.open')
    @patch('os.path.exists')
    def test_add_logo_to_qr(self, mock_exists, mock_image_open):
        """Test adding logo to QR code."""
        # Mock file existence
        mock_exists.return_value = True

        # Mock images
        mock_qr = MagicMock()
        mock_logo = MagicMock()
        mock_logo.convert.return_value = mock_logo
        mock_logo.resize.return_value = mock_logo
        mock_qr.size = (200, 200)
        mock_image_open.side_effect = [mock_qr, mock_logo]

        output_path = os.path.join(self.temp_dir, 'qr_with_logo.png')

        result_path = self.generator.add_logo_to_qr('qr.png', 'logo.png', output_path)

        self.assertEqual(result_path, output_path)
        mock_qr.paste.assert_called_once()
        mock_qr.save.assert_called_once()

    def test_add_logo_file_not_found(self):
        """Test adding logo with missing files."""
        with self.assertRaises(FileNotFoundError):
            self.generator.add_logo_to_qr('nonexistent.png', 'logo.png')

        with patch('os.path.exists') as mock_exists:
            mock_exists.side_effect = lambda x: x == 'qr.png'
            with self.assertRaises(FileNotFoundError):
                self.generator.add_logo_to_qr('qr.png', 'nonexistent.png')


class TestCLI(unittest.TestCase):
    """Test CLI functionality."""

    @patch('qr_code_generator.main.QRCodeGenerator')
    def test_main_function_text(self, mock_qr_class):
        """Test main function with text input."""
        mock_qr = MagicMock()
        mock_qr_class.return_value = mock_qr
        mock_qr.generate_text_qr.return_value = 'test.png'

        with patch('sys.argv', ['qr_code_generator', 'Hello World']):
            with patch('qr_code_generator.main.create_parser') as mock_parser:
                mock_args = MagicMock()
                mock_args.text = 'Hello World'
                mock_args.url = None
                mock_args.vcard = False
                mock_args.batch = None
                mock_args.output = None
                mock_args.format = 'png'
                mock_args.size = 10
                mock_args.error_correction = 'M'
                mock_args.fill_color = 'black'
                mock_args.back_color = 'white'
                mock_args.add_logo = None
                mock_args.verbose = False
                mock_args.output_dir = 'qr_codes'
                mock_args.name = None
                mock_args.phone = None
                mock_args.email = None
                mock_args.org = None

                mock_parser_instance = MagicMock()
                mock_parser_instance.parse_args.return_value = mock_args
                mock_parser.return_value = mock_parser_instance

                from qr_code_generator.main import main
                result = main()

                self.assertEqual(result, 0)
                mock_qr.generate_text_qr.assert_called_once_with('Hello World', None, 'png')


if __name__ == '__main__':
    unittest.main()
