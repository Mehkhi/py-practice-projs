"""Command-line interface for RSS Reader."""

import argparse
import sys
from .core import RSSReader
from .utils import (
    format_article_display,
    export_to_html,
    export_to_markdown,
    setup_logging,
)


def cmd_add_feed(reader: RSSReader, args) -> None:
    """Add a new RSS feed."""
    if reader.add_feed(args.name, args.url):
        print(f"✓ Added feed: {args.name}")
    else:
        print(f"✗ Failed to add feed: {args.name}")
        sys.exit(1)


def cmd_list_feeds(reader: RSSReader, args) -> None:
    """List all feeds."""
    feeds = reader.list_feeds()
    if not feeds:
        print("No feeds found. Add a feed with 'add-feed'.")
        return

    print("Feeds:")
    for feed in feeds:
        print(f"  {feed.feed_id}: {feed.name} ({feed.url})")


def cmd_remove_feed(reader: RSSReader, args) -> None:
    """Remove a feed."""
    if reader.remove_feed(args.feed_id):
        print(f"✓ Removed feed with ID: {args.feed_id}")
    else:
        print(f"✗ Failed to remove feed with ID: {args.feed_id}")
        sys.exit(1)


def cmd_fetch(reader: RSSReader, args) -> None:
    """Fetch articles from a feed."""
    articles = reader.fetch_articles(args.feed_id)
    if articles:
        print(f"✓ Fetched {len(articles)} articles")
    else:
        print("✗ No articles fetched or feed not found")
        sys.exit(1)


def cmd_list_articles(reader: RSSReader, args) -> None:
    """List articles."""
    articles = reader.get_articles(feed_id=args.feed_id, unread_only=args.unread)

    if not articles:
        print("No articles found.")
        return

    print(f"Articles ({len(articles)}):")
    print("-" * 50)

    for i, article in enumerate(articles, 1):
        print(f"\n[{i}]")
        print(format_article_display(article, show_feed=True))
        if i < len(articles):
            print()


def cmd_mark_read(reader: RSSReader, args) -> None:
    """Mark article(s) as read."""
    if args.article_id:
        if reader.mark_article_read(args.article_id):
            print(f"✓ Marked article {args.article_id} as read")
        else:
            print(f"✗ Failed to mark article {args.article_id} as read")
            sys.exit(1)
    elif args.feed_id:
        if reader.mark_feed_read(args.feed_id):
            print(f"✓ Marked all articles in feed {args.feed_id} as read")
        else:
            print(f"✗ Failed to mark feed {args.feed_id} as read")
            sys.exit(1)


def cmd_search(reader: RSSReader, args) -> None:
    """Search articles."""
    articles = reader.search_articles(args.query)

    if not articles:
        print(f"No articles found for: {args.query}")
        return

    print(f"Search results for '{args.query}' ({len(articles)}):")
    print("-" * 50)

    for i, article in enumerate(articles, 1):
        print(f"\n[{i}]")
        print(format_article_display(article))
        if i < len(articles):
            print()


def cmd_export(reader: RSSReader, args) -> None:
    """Export articles."""
    articles = reader.get_articles(feed_id=args.feed_id, unread_only=args.unread_only)

    if not articles:
        print("No articles to export")
        return

    success = False
    if args.format.lower() == "html":
        success = export_to_html(articles, args.filename)
    elif args.format.lower() == "markdown":
        success = export_to_markdown(articles, args.filename)
    else:
        print(f"✗ Unsupported format: {args.format}")
        sys.exit(1)

    if success:
        print(f"✓ Exported {len(articles)} articles to {args.filename}")
    else:
        print(f"✗ Failed to export to {args.filename}")
        sys.exit(1)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="RSS Reader - A command-line tool for reading RSS feeds"
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Set logging level",
    )
    parser.add_argument("--db", default="rss_reader.db", help="Database file path")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Add feed command
    add_parser = subparsers.add_parser("add-feed", help="Add a new RSS feed")
    add_parser.add_argument("name", help="Name for the feed")
    add_parser.add_argument("url", help="URL of the RSS feed")
    add_parser.set_defaults(func=cmd_add_feed)

    # List feeds command
    list_feeds_parser = subparsers.add_parser("list-feeds", help="List all feeds")
    list_feeds_parser.set_defaults(func=cmd_list_feeds)

    # Remove feed command
    remove_parser = subparsers.add_parser("remove-feed", help="Remove a feed")
    remove_parser.add_argument("feed_id", type=int, help="ID of the feed to remove")
    remove_parser.set_defaults(func=cmd_remove_feed)

    # Fetch articles command
    fetch_parser = subparsers.add_parser("fetch", help="Fetch articles from a feed")
    fetch_parser.add_argument("feed_id", type=int, help="ID of the feed to fetch from")
    fetch_parser.set_defaults(func=cmd_fetch)

    # List articles command
    list_parser = subparsers.add_parser("list", help="List articles")
    list_parser.add_argument("--feed-id", type=int, help="Filter by feed ID")
    list_parser.add_argument(
        "--unread", action="store_true", help="Show only unread articles"
    )
    list_parser.set_defaults(func=cmd_list_articles)

    # Mark as read command
    mark_parser = subparsers.add_parser("mark-read", help="Mark articles as read")
    mark_group = mark_parser.add_mutually_exclusive_group(required=True)
    mark_group.add_argument(
        "--article-id", type=int, help="ID of article to mark as read"
    )
    mark_group.add_argument(
        "--feed-id", type=int, help="ID of feed to mark all articles as read"
    )
    mark_parser.set_defaults(func=cmd_mark_read)

    # Search command
    search_parser = subparsers.add_parser("search", help="Search articles")
    search_parser.add_argument("query", help="Search query")
    search_parser.set_defaults(func=cmd_search)

    # Export command
    export_parser = subparsers.add_parser("export", help="Export articles")
    export_parser.add_argument("filename", help="Output filename")
    export_parser.add_argument(
        "--format", choices=["html", "markdown"], default="html", help="Export format"
    )
    export_parser.add_argument("--feed-id", type=int, help="Filter by feed ID")
    export_parser.add_argument(
        "--unread-only", action="store_true", help="Export only unread articles"
    )
    export_parser.set_defaults(func=cmd_export)

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.log_level)

    # Initialize RSS reader
    reader = RSSReader(args.db)

    # Execute command
    if args.command:
        args.func(reader, args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
