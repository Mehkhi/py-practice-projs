"""Comprehensive unit tests for the URL shortener."""

import os
import tempfile
import unittest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from local_url_shortener.core import URLShortener
from local_url_shortener.web import create_app
from local_url_shortener.utils import (
    validate_short_code,
    sanitize_url,
    generate_qr_code,
    parse_expiration_time,
    truncate_string,
    is_port_available,
)


class TestURLShortener(unittest.TestCase):
    """Test cases for URLShortener core functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()
        self.shortener = URLShortener(self.temp_db.name)

    def tearDown(self):
        """Clean up test fixtures."""
        os.unlink(self.temp_db.name)

    def test_database_initialization(self):
        """Test database initialization."""
        # Database should be created and tables should exist
        with self.shortener.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            self.assertIn("urls", tables)

    def test_create_short_url_basic(self):
        """Test basic URL shortening."""
        original_url = "https://example.com"
        short_code, full_url = self.shortener.create_short_url(original_url)

        self.assertIsNotNone(short_code)
        self.assertEqual(len(short_code), 6)
        self.assertTrue(full_url.endswith(short_code))
        self.assertIn("localhost:5000", full_url)

    def test_create_short_url_with_custom_code(self):
        """Test URL shortening with custom code."""
        original_url = "https://example.com"
        custom_code = "mylink"
        short_code, full_url = self.shortener.create_short_url(
            original_url, custom_code=custom_code
        )

        self.assertEqual(short_code, custom_code)
        self.assertTrue(full_url.endswith(custom_code))

    def test_create_short_url_duplicate_custom_code(self):
        """Test duplicate custom code handling."""
        original_url = "https://example.com"
        custom_code = "mylink"

        # Create first URL
        self.shortener.create_short_url(original_url, custom_code=custom_code)

        # Try to create second URL with same custom code
        with self.assertRaises(ValueError) as context:
            self.shortener.create_short_url(
                "https://another.com", custom_code=custom_code
            )

        self.assertIn("already exists", str(context.exception))

    def test_create_short_url_with_expiration(self):
        """Test URL shortening with expiration."""
        original_url = "https://example.com"
        expires_days = 7
        short_code, full_url = self.shortener.create_short_url(
            original_url, expires_days=expires_days
        )

        stats = self.shortener.get_url_stats(short_code)
        self.assertIsNotNone(stats["expires_at"])

        # Check that expiration date is approximately correct
        expires_at = datetime.fromisoformat(stats["expires_at"])
        expected_expiry = datetime.now() + timedelta(days=expires_days)
        self.assertAlmostEqual(
            expires_at.timestamp(),
            expected_expiry.timestamp(),
            delta=60,  # Allow 1 minute difference
        )

    def test_create_short_url_hash_idempotent(self):
        """Hash-based shortening should reuse existing code for same URL."""
        original_url = "https://example.com/hash"

        code1, _ = self.shortener.create_short_url(
            original_url, use_hash=True, expires_days=1
        )
        stats_first = self.shortener.get_url_stats(code1)
        self.assertIsNotNone(stats_first)
        first_expiry = datetime.fromisoformat(stats_first["expires_at"])

        code2, _ = self.shortener.create_short_url(
            original_url, use_hash=True, expires_days=5
        )
        self.assertEqual(code1, code2)

        stats_second = self.shortener.get_url_stats(code2)
        self.assertIsNotNone(stats_second)
        second_expiry = datetime.fromisoformat(stats_second["expires_at"])
        self.assertGreater(second_expiry, first_expiry)

        with self.shortener.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM urls WHERE short_code = ?", (code1,)
            )
            count = cursor.fetchone()[0]
            self.assertEqual(count, 1)

    def test_create_short_url_invalid_url(self):
        """Test URL shortening with invalid URL."""
        with self.assertRaises(ValueError):
            self.shortener.create_short_url("invalid-url")

        with self.assertRaises(ValueError):
            self.shortener.create_short_url("")

        with self.assertRaises(ValueError):
            self.shortener.create_short_url(None)

    def test_get_original_url(self):
        """Test retrieving original URL."""
        original_url = "https://example.com"
        short_code, _ = self.shortener.create_short_url(original_url)

        retrieved_url = self.shortener.get_original_url(short_code)
        self.assertEqual(retrieved_url, original_url)

    def test_get_original_url_nonexistent(self):
        """Test retrieving non-existent URL."""
        retrieved_url = self.shortener.get_original_url("nonexistent")
        self.assertIsNone(retrieved_url)

    def test_get_original_url_expired(self):
        """Test retrieving expired URL."""
        original_url = "https://example.com"
        short_code, _ = self.shortener.create_short_url(original_url, expires_days=1)

        # Manually set expiration to past
        past_date = (datetime.now() - timedelta(days=1)).isoformat()
        with self.shortener.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE urls SET expires_at = ? WHERE short_code = ?",
                (past_date, short_code),
            )
            conn.commit()

        retrieved_url = self.shortener.get_original_url(short_code)
        self.assertIsNone(retrieved_url)

    def test_click_count_increment(self):
        """Test click count increment."""
        original_url = "https://example.com"
        short_code, _ = self.shortener.create_short_url(original_url)

        # Initial click count should be 0
        stats = self.shortener.get_url_stats(short_code)
        self.assertEqual(stats["click_count"], 0)

        # Access URL once
        self.shortener.get_original_url(short_code)

        # Click count should be 1
        stats = self.shortener.get_url_stats(short_code)
        self.assertEqual(stats["click_count"], 1)

        # Access URL again
        self.shortener.get_original_url(short_code)

        # Click count should be 2
        stats = self.shortener.get_url_stats(short_code)
        self.assertEqual(stats["click_count"], 2)

    def test_get_url_stats(self):
        """Test getting URL statistics."""
        original_url = "https://example.com"
        custom_code = "testlink"
        short_code, _ = self.shortener.create_short_url(
            original_url, custom_code=custom_code, expires_days=5
        )

        stats = self.shortener.get_url_stats(short_code)

        self.assertEqual(stats["short_code"], short_code)
        self.assertEqual(stats["original_url"], original_url)
        self.assertTrue(stats["custom_code"])
        self.assertIsNotNone(stats["created_at"])
        self.assertIsNotNone(stats["expires_at"])
        self.assertFalse(stats["expired"])
        self.assertEqual(stats["click_count"], 0)

    def test_get_url_stats_nonexistent(self):
        """Test getting stats for non-existent URL."""
        stats = self.shortener.get_url_stats("nonexistent")
        self.assertIsNone(stats)

    def test_list_all_urls(self):
        """Test listing all URLs."""
        # Create multiple URLs
        urls = [
            ("https://example1.com", "link1"),
            ("https://example2.com", None),
            ("https://example3.com", "link3"),
        ]

        for url, custom in urls:
            self.shortener.create_short_url(url, custom_code=custom)

        all_urls = self.shortener.list_all_urls()
        self.assertEqual(len(all_urls), 3)

        # Check that all URLs are present
        original_urls = [url["original_url"] for url in all_urls]
        for url, _ in urls:
            self.assertIn(url, original_urls)

    def test_delete_url(self):
        """Test deleting a URL."""
        original_url = "https://example.com"
        short_code, _ = self.shortener.create_short_url(original_url)

        # URL should exist
        self.assertIsNotNone(self.shortener.get_url_stats(short_code))

        # Delete URL
        result = self.shortener.delete_url(short_code)
        self.assertTrue(result)

        # URL should no longer exist
        self.assertIsNone(self.shortener.get_url_stats(short_code))

    def test_delete_nonexistent_url(self):
        """Test deleting non-existent URL."""
        result = self.shortener.delete_url("nonexistent")
        self.assertFalse(result)

    def test_cleanup_expired(self):
        """Test cleaning up expired URLs."""
        # Create URLs with different expiration times
        self.shortener.create_short_url("https://permanent.com")
        self.shortener.create_short_url("https://expired.com", expires_days=1)

        # Manually set one URL to expired
        past_date = (datetime.now() - timedelta(days=1)).isoformat()
        with self.shortener.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE urls SET expires_at = ? WHERE original_url = ?",
                (past_date, "https://expired.com"),
            )
            conn.commit()

        # Cleanup expired URLs
        deleted_count = self.shortener.cleanup_expired()
        self.assertEqual(deleted_count, 1)

        # Check that only permanent URL remains
        all_urls = self.shortener.list_all_urls()
        self.assertEqual(len(all_urls), 1)
        self.assertEqual(all_urls[0]["original_url"], "https://permanent.com")

    def test_generate_short_code_uniqueness(self):
        """Test that generated short codes are unique."""
        codes = set()
        for i in range(100):
            code = self.shortener.generate_short_code()
            self.assertNotIn(code, codes)
            codes.add(code)
            self.assertEqual(len(code), 6)

    def test_generate_hash_code(self):
        """Test hash-based code generation."""
        url = "https://example.com"
        code1 = self.shortener.generate_hash_code(url)
        code2 = self.shortener.generate_hash_code(url)

        # Same URL should generate same hash
        self.assertEqual(code1, code2)
        self.assertEqual(len(code1), 6)

    def test_validate_url(self):
        """Test URL validation."""
        # Valid URLs
        self.assertTrue(self.shortener.validate_url("https://example.com"))
        self.assertTrue(self.shortener.validate_url("http://example.com"))
        self.assertTrue(self.shortener.validate_url("https://sub.example.com/path"))

        # Invalid URLs
        self.assertFalse(self.shortener.validate_url("example.com"))
        self.assertFalse(self.shortener.validate_url("ftp://example.com"))
        self.assertFalse(self.shortener.validate_url(""))
        self.assertFalse(self.shortener.validate_url(None))
        self.assertFalse(self.shortener.validate_url(123))

    def test_custom_code_validation(self):
        """Test custom code validation."""
        # Valid custom codes
        self.shortener.create_short_url("https://example.com", custom_code="abc")
        self.shortener.create_short_url("https://example2.com", custom_code="abc123")

        # Invalid custom codes
        with self.assertRaises(ValueError):
            self.shortener.create_short_url(
                "https://example.com", custom_code="ab"
            )  # Too short

        with self.assertRaises(ValueError):
            self.shortener.create_short_url(
                "https://example.com", custom_code=""
            )  # Empty


class TestUtils(unittest.TestCase):
    """Test cases for utility functions."""

    def test_validate_short_code(self):
        """Test short code validation."""
        # Valid codes
        self.assertTrue(validate_short_code("abc"))
        self.assertTrue(validate_short_code("abc123"))
        self.assertTrue(validate_short_code("a_b-c"))
        self.assertTrue(validate_short_code("A" * 50))

        # Invalid codes
        self.assertFalse(validate_short_code(""))
        self.assertFalse(validate_short_code("ab"))  # Too short
        self.assertFalse(validate_short_code("a" * 51))  # Too long
        self.assertFalse(validate_short_code("abc!@#"))  # Invalid characters
        self.assertFalse(validate_short_code(None))
        self.assertFalse(validate_short_code(123))

    def test_sanitize_url(self):
        """Test URL sanitization."""
        # Basic sanitization
        self.assertEqual(sanitize_url("example.com"), "https://example.com")
        self.assertEqual(sanitize_url("http://example.com"), "http://example.com")
        self.assertEqual(sanitize_url("https://example.com"), "https://example.com")

        # Whitespace handling
        self.assertEqual(sanitize_url("  example.com  "), "https://example.com")

        # Empty input
        self.assertEqual(sanitize_url(""), "")
        self.assertEqual(sanitize_url(None), "")

    def test_truncate_string(self):
        """Test string truncation."""
        # No truncation needed
        self.assertEqual(truncate_string("short", 10), "short")

        # Truncation needed
        self.assertEqual(
            truncate_string("this is a very long string", 10), "this is..."
        )
        self.assertEqual(truncate_string("1234567890", 5), "12...")

        # Custom suffix
        self.assertEqual(
            truncate_string("long string", 10, suffix="[more]"), "long[more]"
        )

    def test_parse_expiration_time(self):
        """Test expiration time parsing."""
        # Days format
        result = parse_expiration_time("7")
        self.assertIsNotNone(result)
        expiry_date = datetime.fromisoformat(result)
        expected = datetime.now() + timedelta(days=7)
        self.assertAlmostEqual(expiry_date.timestamp(), expected.timestamp(), delta=60)

        result = parse_expiration_time("7d")
        self.assertIsNotNone(result)

        # Date format
        result = parse_expiration_time("2024-12-25")
        self.assertIsNotNone(result)
        self.assertEqual(result, "2024-12-25T00:00:00")

        # DateTime format
        result = parse_expiration_time("2024-12-25 14:30:00")
        self.assertIsNotNone(result)
        self.assertEqual(result, "2024-12-25T14:30:00")

        # Invalid formats
        self.assertIsNone(parse_expiration_time(""))
        self.assertIsNone(parse_expiration_time("invalid"))
        self.assertIsNone(parse_expiration_time("7x"))

    @patch("local_url_shortener.utils.QR_AVAILABLE", True)
    @patch("local_url_shortener.utils.qrcode")
    def test_generate_qr_code(self, mock_qrcode):
        """Test QR code generation."""
        # Mock QR code generation
        mock_img = MagicMock()
        mock_qr_instance = MagicMock()
        mock_qr_instance.make_image.return_value = mock_img
        mock_qrcode.QRCode.return_value = mock_qr_instance

        url = "https://example.com"
        filename = generate_qr_code(url)

        # Verify QR code was created
        mock_qrcode.QRCode.assert_called_once()
        mock_qr_instance.add_data.assert_called_once_with(url)
        mock_qr_instance.make.assert_called_once_with(fit=True)
        mock_img.save.assert_called_once()

        self.assertTrue(filename.endswith(".png"))

    @patch("local_url_shortener.utils.QR_AVAILABLE", False)
    def test_generate_qr_code_unavailable(self):
        """Test QR code generation when library is unavailable."""
        with self.assertRaises(ImportError):
            generate_qr_code("https://example.com")

    def test_is_port_available(self):
        """Test port availability checking."""
        # Test with a commonly available port
        # Note: This test might fail if the port is actually in use
        available = is_port_available(65432)  # Use a high-numbered port
        self.assertIsInstance(available, bool)

        # Test with a commonly used port
        available = is_port_available(80)  # HTTP port
        self.assertIsInstance(available, bool)


class TestWebAPI(unittest.TestCase):
    """Test cases for the Flask API endpoints."""

    def setUp(self):
        """Create an app with a temporary database."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()
        self.shortener = URLShortener(self.temp_db.name)
        self.app = create_app(self.shortener)
        self.app.testing = True
        self.client = self.app.test_client()

    def tearDown(self):
        """Remove the temporary database."""
        os.unlink(self.temp_db.name)

    def test_api_shorten_accepts_string_expiration(self):
        """API should accept expires_days provided as a string."""
        response = self.client.post(
            "/api/shorten",
            json={"url": "https://example.com", "expires_days": "7"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsNotNone(data)
        self.assertIn("short_code", data)
        self.assertEqual(data["expires_days"], 7)

        stats = self.shortener.get_url_stats(data["short_code"])
        self.assertIsNotNone(stats)
        self.assertIsNotNone(stats["expires_at"])

    def test_api_shorten_rejects_invalid_expiration(self):
        """API should reject expires_days values that cannot be parsed."""
        response = self.client.post(
            "/api/shorten",
            json={"url": "https://example.com", "expires_days": "seven"},
        )
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIsNotNone(data)
        self.assertIn("error", data)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()
        self.shortener = URLShortener(self.temp_db.name)

    def tearDown(self):
        """Clean up test fixtures."""
        os.unlink(self.temp_db.name)

    def test_complete_workflow(self):
        """Test complete URL shortening workflow."""
        # 1. Create short URL
        original_url = "https://example.com"
        short_code, full_url = self.shortener.create_short_url(
            original_url, custom_code="mylink", expires_days=7
        )

        # 2. Verify creation
        self.assertEqual(short_code, "mylink")
        stats = self.shortener.get_url_stats(short_code)
        self.assertIsNotNone(stats)
        self.assertEqual(stats["original_url"], original_url)

        # 3. Test redirection
        retrieved_url = self.shortener.get_original_url(short_code)
        self.assertEqual(retrieved_url, original_url)

        # 4. Verify click count
        stats = self.shortener.get_url_stats(short_code)
        self.assertEqual(stats["click_count"], 1)

        # 5. List URLs
        all_urls = self.shortener.list_all_urls()
        self.assertEqual(len(all_urls), 1)
        self.assertEqual(all_urls[0]["short_code"], short_code)

        # 6. Delete URL
        result = self.shortener.delete_url(short_code)
        self.assertTrue(result)

        # 7. Verify deletion
        all_urls = self.shortener.list_all_urls()
        self.assertEqual(len(all_urls), 0)

    def test_multiple_urls_workflow(self):
        """Test workflow with multiple URLs."""
        urls = ["https://google.com", "https://github.com", "https://stackoverflow.com"]

        short_codes = []

        # Create multiple URLs
        for url in urls:
            short_code, _ = self.shortener.create_short_url(url)
            short_codes.append(short_code)

        # Verify all URLs exist
        all_urls = self.shortener.list_all_urls()
        self.assertEqual(len(all_urls), 3)

        # Access all URLs
        for short_code in short_codes:
            self.shortener.get_original_url(short_code)

        # Verify click counts
        for short_code in short_codes:
            stats = self.shortener.get_url_stats(short_code)
            self.assertEqual(stats["click_count"], 1)

        # Delete all URLs
        for short_code in short_codes:
            self.shortener.delete_url(short_code)

        # Verify all deleted
        all_urls = self.shortener.list_all_urls()
        self.assertEqual(len(all_urls), 0)


if __name__ == "__main__":
    unittest.main()
