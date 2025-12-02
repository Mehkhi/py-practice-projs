"""Tests for the basic_web_scraper package."""

import json
import os
import tempfile
import unittest
from unittest.mock import Mock, patch

from bs4 import BeautifulSoup

from basic_web_scraper.core import WebScraper
from basic_web_scraper.utils import (
    is_valid_url,
    normalize_url,
    extract_price_from_text,
    clean_text,
    get_domain,
    is_same_domain,
    sanitize_filename,
    format_file_size,
)


class TestWebScraper(unittest.TestCase):
    """Test cases for the WebScraper class."""

    def setUp(self):
        """Set up test fixtures."""
        self.scraper = WebScraper(delay=0, timeout=5)

        # Sample HTML content for testing
        self.sample_html = """
        <html>
            <head><title>Test Page</title></head>
            <body>
                <h1>Main Title</h1>
                <h2>Subtitle</h2>
                <h3>Section Title</h3>
                <a href="https://example.com/page1">Link 1</a>
                <a href="/relative-link">Link 2</a>
                <a href="http://other.com">External Link</a>
                <div class="price">$19.99</div>
                <div class="cost">€25.50</div>
                <span data-price="£15.00">£15.00</span>
                <a href="/page/2" class="next">Next Page</a>
            </body>
        </html>
        """
        self.soup = BeautifulSoup(self.sample_html, "lxml")

    def test_init(self):
        """Test WebScraper initialization."""
        scraper = WebScraper(delay=2.0, timeout=15)
        self.assertEqual(scraper.delay, 2.0)
        self.assertEqual(scraper.timeout, 15)
        self.assertIsNotNone(scraper.session)

    @patch("basic_web_scraper.core.requests.Session.get")
    def test_fetch_page_success(self, mock_get):
        """Test successful page fetching."""
        mock_response = Mock()
        mock_response.content = self.sample_html.encode()
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.scraper.fetch_page("https://example.com")

        self.assertIsNotNone(result)
        self.assertIsInstance(result, BeautifulSoup)
        mock_get.assert_called_once_with("https://example.com", timeout=5)

    @patch("basic_web_scraper.core.requests.Session.get")
    def test_fetch_page_failure(self, mock_get):
        """Test page fetching failure."""
        mock_get.side_effect = Exception("Network error")

        result = self.scraper.fetch_page("https://example.com")

        self.assertIsNone(result)

    def test_extract_titles_default_selector(self):
        """Test title extraction with default selector."""
        titles = self.scraper.extract_titles(self.soup)

        self.assertEqual(len(titles), 3)
        self.assertIn("Main Title", titles)
        self.assertIn("Subtitle", titles)
        self.assertIn("Section Title", titles)

    def test_extract_titles_custom_selector(self):
        """Test title extraction with custom selector."""
        titles = self.scraper.extract_titles(self.soup, "h1")

        self.assertEqual(len(titles), 1)
        self.assertEqual(titles[0], "Main Title")

    def test_extract_links(self):
        """Test link extraction."""
        links = self.scraper.extract_links(self.soup, "https://example.com")

        self.assertEqual(len(links), 4)

        # Check absolute URL resolution
        link_urls = [link["url"] for link in links]
        self.assertIn("https://example.com/page1", link_urls)
        self.assertIn("https://example.com/relative-link", link_urls)
        self.assertIn("http://other.com", link_urls)
        self.assertIn("https://example.com/page/2", link_urls)

    def test_extract_links_no_base_url(self):
        """Test link extraction without base URL."""
        links = self.scraper.extract_links(self.soup)

        self.assertEqual(len(links), 4)
        self.assertEqual(links[0]["url"], "https://example.com/page1")
        self.assertEqual(links[1]["url"], "/relative-link")

    def test_extract_prices_default_patterns(self):
        """Test price extraction with default patterns."""
        prices = self.scraper.extract_prices(self.soup)

        self.assertGreater(len(prices), 0)
        # Should find at least one price
        price_found = any(
            "$" in price or "€" in price or "£" in price for price in prices
        )
        self.assertTrue(price_found)

    def test_extract_prices_custom_patterns(self):
        """Test price extraction with custom patterns."""
        prices = self.scraper.extract_prices(self.soup, [".price"])

        self.assertEqual(len(prices), 1)
        self.assertIn("$19.99", prices)

    def test_extract_prices_preserves_order(self):
        """Prices should be de-duplicated while preserving source order."""
        html = """
        <html>
            <body>
                <div class="price">$9.99</div>
                <div class="price">€8.50</div>
                <div class="price">$9.99</div>
                <div class="price">£7.25</div>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "lxml")

        prices = self.scraper.extract_prices(soup, [".price"])

        self.assertEqual(prices, ["$9.99", "€8.50", "£7.25"])

    def test_find_next_page_default_selectors(self):
        """Test finding next page with default selectors."""
        next_url = self.scraper.find_next_page(self.soup)

        # The first selector that matches will be returned
        self.assertIn(next_url, ["/page/2", "https://example.com/page1"])

    def test_find_next_page_custom_selectors(self):
        """Test finding next page with custom selectors."""
        next_url = self.scraper.find_next_page(self.soup, [".next"])

        self.assertEqual(next_url, "/page/2")

    def test_find_next_page_not_found(self):
        """Test when next page is not found."""
        html_no_next = """
        <html>
            <body>
                <h1>No pagination</h1>
            </body>
        </html>
        """
        soup = BeautifulSoup(html_no_next, "lxml")

        next_url = self.scraper.find_next_page(soup)

        self.assertIsNone(next_url)

    @patch.object(WebScraper, "fetch_page")
    def test_scrape_page_success(self, mock_fetch):
        """Test successful page scraping."""
        mock_fetch.return_value = self.soup

        result = self.scraper.scrape_page("https://example.com")

        self.assertEqual(result["url"], "https://example.com")
        self.assertIn("titles", result)
        self.assertIn("links", result)
        self.assertIn("prices", result)
        self.assertIn("next_page", result)
        self.assertNotIn("error", result)

    @patch.object(WebScraper, "fetch_page")
    def test_scrape_page_failure(self, mock_fetch):
        """Test page scraping failure."""
        mock_fetch.return_value = None

        result = self.scraper.scrape_page("https://example.com")

        self.assertEqual(result["url"], "https://example.com")
        self.assertIn("error", result)

    @patch.object(WebScraper, "scrape_page")
    def test_scrape_multiple_pages(self, mock_scrape):
        """Test scraping multiple pages."""
        # Mock responses for 3 pages
        mock_responses = [
            {
                "url": "https://example.com",
                "titles": ["Title 1"],
                "links": [],
                "prices": [],
                "next_page": "/page/2",
            },
            {
                "url": "https://example.com/page/2",
                "titles": ["Title 2"],
                "links": [],
                "prices": [],
                "next_page": "/page/3",
            },
            {
                "url": "https://example.com/page/3",
                "titles": ["Title 3"],
                "links": [],
                "prices": [],
                "next_page": None,
            },
        ]
        mock_scrape.side_effect = mock_responses

        results = self.scraper.scrape_multiple_pages("https://example.com", max_pages=5)

        self.assertEqual(len(results), 3)
        self.assertEqual(results[0]["titles"][0], "Title 1")
        self.assertEqual(results[1]["titles"][0], "Title 2")
        self.assertEqual(results[2]["titles"][0], "Title 3")

    def test_save_to_json_success(self):
        """Test successful JSON saving."""
        data = {"test": "data"}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            filename = f.name

        try:
            result = self.scraper.save_to_json(data, filename)
            self.assertTrue(result)

            # Verify file contents
            with open(filename, "r") as f:
                loaded_data = json.load(f)
            self.assertEqual(loaded_data, data)
        finally:
            os.unlink(filename)

    def test_save_to_json_failure(self):
        """Test JSON saving failure."""
        result = self.scraper.save_to_json({"test": "data"}, "/invalid/path/file.json")
        self.assertFalse(result)

    def test_save_to_csv_success(self):
        """Test successful CSV saving."""
        data = [
            {
                "url": "https://example.com",
                "titles": ["Title 1", "Title 2"],
                "links": [{"url": "https://example.com/link1", "text": "Link 1"}],
                "prices": ["$19.99", "$29.99"],
                "next_page": "/page/2",
            }
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            filename = f.name

        try:
            result = self.scraper.save_to_csv(data, filename)
            self.assertTrue(result)

            # Verify file exists and has content
            self.assertTrue(os.path.exists(filename))
            with open(filename, "r") as f:
                content = f.read()
            self.assertIn("url", content)
            self.assertIn("titles", content)
        finally:
            os.unlink(filename)

    def test_save_to_csv_empty_data(self):
        """Test CSV saving with empty data."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            filename = f.name

        try:
            result = self.scraper.save_to_csv([], filename)
            self.assertFalse(result)
        finally:
            os.unlink(filename)


class TestUtils(unittest.TestCase):
    """Test cases for utility functions."""

    def test_is_valid_url(self):
        """Test URL validation."""
        self.assertTrue(is_valid_url("https://example.com"))
        self.assertTrue(is_valid_url("http://example.com/path"))
        self.assertFalse(is_valid_url("example.com"))
        self.assertFalse(is_valid_url("not-a-url"))
        self.assertFalse(is_valid_url(""))

    def test_normalize_url(self):
        """Test URL normalization."""
        # Add scheme
        self.assertEqual(normalize_url("example.com"), "http://example.com")

        # Resolve relative URLs
        self.assertEqual(
            normalize_url("/path", "https://example.com"), "https://example.com/path"
        )

        # Already absolute URL
        self.assertEqual(
            normalize_url("https://example.com/path"), "https://example.com/path"
        )

    def test_extract_price_from_text(self):
        """Test price extraction from text."""
        self.assertEqual(extract_price_from_text("$19.99"), "$19.99")
        self.assertEqual(extract_price_from_text("€25.50"), "€25.50")
        self.assertEqual(extract_price_from_text("Price: £15.00"), "£15.00")
        self.assertEqual(extract_price_from_text("No price here"), None)
        self.assertEqual(extract_price_from_text(""), None)

    def test_clean_text(self):
        """Test text cleaning."""
        self.assertEqual(clean_text("  Hello   World  "), "Hello World")
        self.assertEqual(clean_text("Multiple\n\nLines"), "Multiple Lines")
        self.assertEqual(clean_text(""), "")
        self.assertEqual(clean_text("   "), "")

    def test_get_domain(self):
        """Test domain extraction."""
        self.assertEqual(get_domain("https://example.com"), "example.com")
        self.assertEqual(get_domain("http://sub.example.com/path"), "sub.example.com")
        self.assertEqual(get_domain("invalid-url"), "")

    def test_is_same_domain(self):
        """Test same domain checking."""
        self.assertTrue(
            is_same_domain("https://example.com/page1", "https://example.com/page2")
        )
        self.assertFalse(is_same_domain("https://example.com", "https://other.com"))
        self.assertFalse(is_same_domain("invalid-url1", "invalid-url2"))

    def test_sanitize_filename(self):
        """Test filename sanitization."""
        self.assertEqual(sanitize_filename("file.txt"), "file.txt")
        self.assertEqual(sanitize_filename("file<name>.txt"), "file_name_.txt")
        self.assertEqual(sanitize_filename("file/name.txt"), "file_name.txt")
        self.assertEqual(sanitize_filename(""), "output")
        self.assertEqual(sanitize_filename("   "), "output")
        self.assertEqual(sanitize_filename("..hidden.."), "hidden")

    def test_format_file_size(self):
        """Test file size formatting."""
        self.assertEqual(format_file_size(0), "0 B")
        self.assertEqual(format_file_size(1024), "1.0 KB")
        self.assertEqual(format_file_size(1048576), "1.0 MB")
        self.assertEqual(format_file_size(1073741824), "1.0 GB")
        self.assertEqual(format_file_size(512), "512.0 B")


if __name__ == "__main__":
    unittest.main()
