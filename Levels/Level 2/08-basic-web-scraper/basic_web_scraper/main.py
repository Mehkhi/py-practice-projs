"""Command-line interface for the web scraper."""

import argparse
import logging
import sys
from typing import Dict, Any
from urllib.parse import urlparse

from .core import WebScraper


def setup_logging(verbose: bool = False) -> None:
    """Set up logging configuration.

    Args:
        verbose: Enable verbose logging
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,  # Reset any existing logging configuration
    )


def validate_url(url: str) -> str:
    """Validate and normalize URL.

    Args:
        url: URL to validate

    Returns:
        Validated URL

    Raises:
        argparse.ArgumentTypeError: If URL is invalid
    """
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        raise argparse.ArgumentTypeError(f"Invalid URL: {url}")

    # Add scheme if missing
    if not parsed.scheme:
        url = f"http://{url}"

    return url


def parse_config_args(args: argparse.Namespace) -> Dict[str, Any]:
    """Parse configuration arguments into a config dictionary.

    Args:
        args: Parsed command line arguments

    Returns:
        Configuration dictionary
    """
    config = {}

    if args.title_selector:
        config["title_selector"] = args.title_selector

    if args.price_patterns:
        config["price_patterns"] = args.price_patterns.split(",")

    if args.next_selectors:
        config["next_selectors"] = args.next_selectors.split(",")

    return config


def main() -> int:
    """Main entry point for the CLI.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = argparse.ArgumentParser(
        description="Basic Web Scraper - Extract data from websites",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape a single page
  python -m basic_web_scraper https://example.com

  # Scrape multiple pages with pagination
  python -m basic_web_scraper https://example.com --max-pages 5

  # Save results to JSON
  python -m basic_web_scraper https://example.com --output results.json

  # Save results to CSV
  python -m basic_web_scraper https://example.com --output results.csv

  # Custom title selector
  python -m basic_web_scraper https://example.com --title-selector "h1.title"

  # Custom delay and timeout
  python -m basic_web_scraper https://example.com --delay 2 --timeout 15
        """,
    )

    # Required arguments
    parser.add_argument("url", help="URL to scrape", type=validate_url)

    # Optional arguments
    parser.add_argument(
        "--max-pages",
        type=int,
        default=1,
        help="Maximum number of pages to scrape (default: 1)",
    )

    parser.add_argument(
        "--output", "-o", help="Output file (JSON or CSV format based on extension)"
    )

    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Delay between requests in seconds (default: 1.0)",
    )

    parser.add_argument(
        "--timeout",
        type=int,
        default=10,
        help="Request timeout in seconds (default: 10)",
    )

    parser.add_argument(
        "--title-selector",
        help='CSS selector for title elements (default: "h1, h2, h3")',
    )

    parser.add_argument(
        "--price-patterns", help="Comma-separated CSS selectors for price elements"
    )

    parser.add_argument(
        "--next-selectors", help="Comma-separated CSS selectors for next page links"
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    parser.add_argument(
        "--version", action="version", version="Basic Web Scraper 1.0.0"
    )

    args = parser.parse_args()

    # Set up logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    try:
        # Create scraper instance
        scraper = WebScraper(delay=args.delay, timeout=args.timeout)

        # Parse configuration
        config = parse_config_args(args)

        # Scrape the website
        logger.info(f"Starting scrape of {args.url}")

        if args.max_pages > 1:
            results = scraper.scrape_multiple_pages(
                start_url=args.url, max_pages=args.max_pages, config=config
            )
        else:
            results = [scraper.scrape_page(args.url, config)]

        # Display results summary
        successful_pages = [r for r in results if not r.get("error")]
        failed_pages = [r for r in results if r.get("error")]

        logger.info("Scraping completed:")
        logger.info(f"  - Total pages: {len(results)}")
        logger.info(f"  - Successful: {len(successful_pages)}")
        logger.info(f"  - Failed: {len(failed_pages)}")

        # Save results if output file specified
        if args.output:
            if args.output.endswith(".json"):
                success = scraper.save_to_json(results, args.output)
            elif args.output.endswith(".csv"):
                success = scraper.save_to_csv(results, args.output)
            else:
                logger.error("Output file must be .json or .csv")
                return 1

            if not success:
                logger.error("Failed to save results")
                return 1

        # Print summary to console
        print(f"\nScraping Results for {args.url}")
        print("=" * 50)

        for i, page in enumerate(results, 1):
            print(f"\nPage {i}: {page.get('url', 'Unknown URL')}")

            if page.get("error"):
                print(f"  Error: {page['error']}")
                continue

            titles = page.get("titles", [])
            if titles:
                print(f"  Titles ({len(titles)}):")
                for title in titles[:5]:  # Show first 5 titles
                    print(f"    - {title}")
                if len(titles) > 5:
                    print(f"    ... and {len(titles) - 5} more")

            links = page.get("links", [])
            print(f"  Links found: {len(links)}")

            prices = page.get("prices", [])
            if prices:
                print(f"  Prices ({len(prices)}):")
                for price in prices[:5]:  # Show first 5 prices
                    print(f"    - {price}")
                if len(prices) > 5:
                    print(f"    ... and {len(prices) - 5} more")

            next_page = page.get("next_page")
            if next_page:
                print(f"  Next page: {next_page}")

        return 0

    except KeyboardInterrupt:
        logger.info("Scraping interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
