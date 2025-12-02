"""Core web scraping functionality.

This module provides the main scraping logic including HTML fetching,
parsing, element extraction, pagination handling, and data export.
"""

import json
import csv
import logging
import time
from typing import List, Dict, Any, Optional, Union
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


class WebScraper:
    """A web scraper for extracting data from websites.

    Supports HTML fetching, element extraction, pagination, and data export
    to JSON or CSV formats.
    """

    def __init__(self, delay: float = 1.0, timeout: int = 10):
        """Initialize the web scraper.

        Args:
            delay: Delay between requests in seconds (politeness delay)
            timeout: Request timeout in seconds
        """
        self.delay = delay
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )
        self.logger = logging.getLogger(__name__)

    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch and parse a web page.

        Args:
            url: URL to fetch

        Returns:
            BeautifulSoup object or None if fetch failed
        """
        try:
            self.logger.info(f"Fetching page: {url}")
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "lxml")
            time.sleep(self.delay)  # Politeness delay
            return soup

        except requests.RequestException as e:
            self.logger.error(f"Failed to fetch {url}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error parsing {url}: {e}")
            return None

    def extract_titles(
        self, soup: BeautifulSoup, selector: str = "h1, h2, h3"
    ) -> List[str]:
        """Extract titles from the page.

        Args:
            soup: BeautifulSoup object
            selector: CSS selector for title elements

        Returns:
            List of title texts
        """
        try:
            if not soup:
                return []

            titles = []
            elements = soup.select(selector)

            for element in elements:
                if element:
                    text = element.get_text(strip=True)
                    if text:
                        titles.append(text)

            return titles
        except Exception as e:
            self.logger.error(f"Error extracting titles: {e}")
            return []

    def extract_links(
        self, soup: BeautifulSoup, base_url: str = ""
    ) -> List[Dict[str, str]]:
        """Extract links from the page.

        Args:
            soup: BeautifulSoup object
            base_url: Base URL for resolving relative links

        Returns:
            List of dictionaries with link info
        """
        try:
            links = []
            for link in soup.find_all("a", href=True):
                href = link["href"]
                text = link.get_text(strip=True)

                # Resolve relative URLs
                if base_url:
                    absolute_url = urljoin(base_url, href)
                else:
                    absolute_url = href

                links.append({"url": absolute_url, "text": text, "original_href": href})
            return links
        except Exception as e:
            self.logger.error(f"Error extracting links: {e}")
            return []

    def extract_prices(
        self, soup: BeautifulSoup, price_patterns: List[str] = None
    ) -> List[str]:
        """Extract prices from the page.

        Args:
            soup: BeautifulSoup object
            price_patterns: List of CSS selectors for price elements

        Returns:
            List of price strings
        """
        if price_patterns is None:
            price_patterns = [
                '[class*="price"]',
                '[class*="cost"]',
                "[data-price]",
                ".price",
                ".cost",
            ]

        try:
            prices = []
            seen = set()
            for pattern in price_patterns:
                elements = soup.select(pattern)
                for element in elements:
                    text = element.get_text(strip=True)
                    # Simple price detection (can be enhanced)
                    if (
                        any(char in text for char in ["$", "€", "£", "¥"])
                        or text.replace(".", "").replace(",", "").isdigit()
                    ):
                        if text not in seen:
                            prices.append(text)
                            seen.add(text)
            return prices
        except Exception as e:
            self.logger.error(f"Error extracting prices: {e}")
            return []

    def find_next_page(
        self, soup: BeautifulSoup, next_selectors: List[str] = None
    ) -> Optional[str]:
        """Find the next page URL for pagination.

        Args:
            soup: BeautifulSoup object
            next_selectors: List of CSS selectors for next page links

        Returns:
            Next page URL or None if not found
        """
        if next_selectors is None:
            next_selectors = [
                'a[href*="next"]',
                'a[href*="page"]',
                ".next",
                ".pagination .next",
                '[rel="next"]',
            ]

        try:
            for selector in next_selectors:
                next_link = soup.select_one(selector)
                if next_link and next_link.get("href"):
                    return next_link["href"]
            return None
        except Exception as e:
            self.logger.error(f"Error finding next page: {e}")
            return None

    def scrape_page(self, url: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Scrape a single page.

        Args:
            url: URL to scrape
            config: Configuration dictionary

        Returns:
            Dictionary with scraped data
        """
        if config is None:
            config = {}

        soup = self.fetch_page(url)
        if not soup:
            return {"url": url, "error": "Failed to fetch page"}

        result = {
            "url": url,
            "titles": self.extract_titles(
                soup, config.get("title_selector", "h1, h2, h3")
            ),
            "links": self.extract_links(soup, url),
            "prices": self.extract_prices(soup, config.get("price_patterns")),
            "next_page": self.find_next_page(soup, config.get("next_selectors")),
        }

        return result

    def scrape_multiple_pages(
        self, start_url: str, max_pages: int = 5, config: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """Scrape multiple pages following pagination.

        Args:
            start_url: Starting URL
            max_pages: Maximum number of pages to scrape
            config: Configuration dictionary

        Returns:
            List of scraped data for each page
        """
        results = []
        current_url = start_url
        pages_scraped = 0

        while current_url and pages_scraped < max_pages:
            self.logger.info(f"Scraping page {pages_scraped + 1}: {current_url}")

            page_data = self.scrape_page(current_url, config)
            results.append(page_data)

            if page_data.get("error"):
                break

            # Get next page URL
            next_url = page_data.get("next_page")
            if next_url:
                current_url = urljoin(current_url, next_url)
            else:
                break

            pages_scraped += 1

        return results

    def save_to_json(self, data: Union[List, Dict], filename: str) -> bool:
        """Save data to JSON file.

        Args:
            data: Data to save
            filename: Output filename

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Data saved to {filename}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving to JSON: {e}")
            return False

    def save_to_csv(self, data: List[Dict[str, Any]], filename: str) -> bool:
        """Save scraped data to CSV file.

        Args:
            data: List of scraped data
            filename: Output filename

        Returns:
            True if successful, False otherwise
        """
        try:
            if not data:
                return False

            # Flatten the data for CSV
            flattened_data = []
            for page in data:
                base_row = {"url": page.get("url", ""), "error": page.get("error", "")}

                # Add titles as comma-separated string
                titles = page.get("titles", [])
                base_row["titles"] = "; ".join(titles) if titles else ""

                # Add prices as comma-separated string
                prices = page.get("prices", [])
                base_row["prices"] = "; ".join(prices) if prices else ""

                # Add link count
                links = page.get("links", [])
                base_row["link_count"] = len(links)

                # Add next page info
                base_row["next_page"] = page.get("next_page", "")

                flattened_data.append(base_row)

            with open(filename, "w", newline="", encoding="utf-8") as f:
                if flattened_data:
                    writer = csv.DictWriter(f, fieldnames=flattened_data[0].keys())
                    writer.writeheader()
                    writer.writerows(flattened_data)

            self.logger.info(f"Data saved to {filename}")
            return True

        except Exception as e:
            self.logger.error(f"Error saving to CSV: {e}")
            return False
