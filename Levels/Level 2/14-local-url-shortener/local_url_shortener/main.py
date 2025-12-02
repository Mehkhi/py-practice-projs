"""Command-line interface for the URL shortener."""

import argparse
import logging
import sys

from .core import URLShortener
from .utils import generate_qr_code, setup_logging

logger = logging.getLogger(__name__)


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description="Local URL Shortener - Create and manage short URLs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s shorten https://example.com
  %(prog)s shorten https://example.com --custom mylink
  %(prog)s shorten https://example.com --expires 30
  %(prog)s expand abc123
  %(prog)s stats abc123
  %(prog)s list
  %(prog)s delete abc123
  %(prog)s serve --port 8080
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Shorten command
    shorten_parser = subparsers.add_parser("shorten", help="Create a short URL")
    shorten_parser.add_argument("url", help="URL to shorten")
    shorten_parser.add_argument("--custom", help="Custom short code")
    shorten_parser.add_argument("--expires", type=int, help="Expiration in days")
    shorten_parser.add_argument(
        "--hash", action="store_true", help="Use hash-based code generation"
    )
    shorten_parser.add_argument("--qr", action="store_true", help="Generate QR code")

    # Expand command
    expand_parser = subparsers.add_parser("expand", help="Get original URL")
    expand_parser.add_argument("code", help="Short code to expand")

    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Show URL statistics")
    stats_parser.add_argument("code", help="Short code")

    # List command
    subparsers.add_parser("list", help="List all URLs")

    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a short URL")
    delete_parser.add_argument("code", help="Short code to delete")

    # Cleanup command
    subparsers.add_parser("cleanup", help="Remove expired URLs")

    # Serve command
    serve_parser = subparsers.add_parser("serve", help="Start web server")
    serve_parser.add_argument("--host", default="localhost", help="Host to bind to")
    serve_parser.add_argument("--port", type=int, default=5000, help="Port to bind to")
    serve_parser.add_argument("--debug", action="store_true", help="Enable debug mode")

    return parser


def handle_shorten(shortener: URLShortener, args) -> None:
    """Handle the shorten command."""
    try:
        short_code, full_url = shortener.create_short_url(
            args.url,
            custom_code=args.custom,
            expires_days=args.expires,
            use_hash=args.hash,
        )

        print(f"Short URL: {full_url}")
        print(f"Short code: {short_code}")

        if args.expires:
            print(f"Expires in: {args.expires} days")

        if args.qr:
            qr_path = generate_qr_code(full_url, short_code)
            print(f"QR code saved to: {qr_path}")

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_expand(shortener: URLShortener, args) -> None:
    """Handle the expand command."""
    original_url = shortener.get_original_url(args.code)

    if original_url:
        print(f"Original URL: {original_url}")
    else:
        print(f"Short code '{args.code}' not found or expired", file=sys.stderr)
        sys.exit(1)


def handle_stats(shortener: URLShortener, args) -> None:
    """Handle the stats command."""
    stats = shortener.get_url_stats(args.code)

    if stats:
        print(f"Short code: {stats['short_code']}")
        print(f"Original URL: {stats['original_url']}")
        print(f"Created: {stats['created_at']}")
        print(f"Click count: {stats['click_count']}")
        print(f"Custom code: {'Yes' if stats['custom_code'] else 'No'}")

        if stats["expires_at"]:
            print(f"Expires: {stats['expires_at']}")
            print(f"Status: {'Expired' if stats['expired'] else 'Active'}")
        else:
            print("Expires: Never")

    else:
        print(f"Short code '{args.code}' not found", file=sys.stderr)
        sys.exit(1)


def handle_list(shortener: URLShortener, args) -> None:
    """Handle the list command."""
    urls = shortener.list_all_urls()

    if not urls:
        print("No URLs found")
        return

    print(f"{'Code':<10} {'Clicks':<8} {'Custom':<8} {'Expires':<12} {'URL'}")
    print("-" * 80)

    for url_info in urls:
        code = url_info["short_code"]
        clicks = url_info["click_count"]
        custom = "Yes" if url_info["custom_code"] else "No"

        if url_info["expires_at"]:
            expires = "Expired" if url_info["expired"] else "Active"
        else:
            expires = "Never"

        # Truncate long URLs
        display_url = url_info["original_url"]
        if len(display_url) > 40:
            display_url = display_url[:37] + "..."

        print(f"{code:<10} {clicks:<8} {custom:<8} {expires:<12} {display_url}")


def handle_delete(shortener: URLShortener, args) -> None:
    """Handle the delete command."""
    if shortener.delete_url(args.code):
        print(f"Deleted short URL: {args.code}")
    else:
        print(f"Short code '{args.code}' not found", file=sys.stderr)
        sys.exit(1)


def handle_cleanup(shortener: URLShortener, args) -> None:
    """Handle the cleanup command."""
    deleted_count = shortener.cleanup_expired()
    print(f"Cleaned up {deleted_count} expired URLs")


def handle_serve(shortener: URLShortener, args) -> None:
    """Handle the serve command."""
    try:
        from .web import create_app

        app = create_app(shortener)

        print(f"Starting server on {args.host}:{args.port}")
        print("Press Ctrl+C to stop")

        app.run(host=args.host, port=args.port, debug=args.debug)

    except ImportError:
        print(
            "Error: Flask not installed. Install with: pip install flask",
            file=sys.stderr,
        )
        sys.exit(1)
    except Exception as e:
        logger.error(f"Server error: {e}")
        print(f"Server error: {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args()

    # Setup logging
    setup_logging()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Initialize URL shortener
    try:
        shortener = URLShortener()
    except Exception as e:
        logger.error(f"Failed to initialize URL shortener: {e}")
        print(f"Failed to initialize: {e}", file=sys.stderr)
        sys.exit(1)

    # Route to appropriate handler
    handlers = {
        "shorten": handle_shorten,
        "expand": handle_expand,
        "stats": handle_stats,
        "list": handle_list,
        "delete": handle_delete,
        "cleanup": handle_cleanup,
        "serve": handle_serve,
    }

    handler = handlers.get(args.command)
    if handler:
        handler(shortener, args)
    else:
        print(f"Unknown command: {args.command}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
