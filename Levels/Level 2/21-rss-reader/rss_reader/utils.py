"""Utility functions for RSS reader."""

import logging
from typing import List
from datetime import datetime
from .core import Article


def format_article_display(article: Article, show_feed: bool = False) -> str:
    """Format an article for terminal display."""
    status = "✓" if article.is_read else "○"

    lines = [
        f"{status} {article.title}",
        f"  Link: {article.link}",
    ]

    if article.published:
        lines.append(f"  Date: {article.published.strftime('%Y-%m-%d %H:%M')}")

    if article.author:
        lines.append(f"  Author: {article.author}")

    if article.summary:
        # Truncate summary for display
        summary = (
            article.summary[:200] + "..."
            if len(article.summary) > 200
            else article.summary
        )
        lines.append(f"  Summary: {summary}")

    if show_feed and article.feed_id:
        lines.append(f"  Feed ID: {article.feed_id}")

    return "\n".join(lines)


def export_to_html(articles: List[Article], filename: str) -> bool:
    """Export articles to HTML file."""
    try:
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>RSS Articles Export</title>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .article {{ border-bottom: 1px solid #ccc; padding: 20px 0; }}
        .article h2 {{ color: #333; margin-bottom: 5px; }}
        .article .meta {{ color: #666; font-size: 0.9em; margin-bottom: 10px; }}
        .article .summary {{ line-height: 1.5; }}
        .read {{ opacity: 0.7; }}
        .unread {{ font-weight: bold; }}
    </style>
</head>
<body>
    <h1>RSS Articles Export</h1>
    <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
"""

        for article in articles:
            status_class = "read" if article.is_read else "unread"
            status_text = "Read" if article.is_read else "Unread"

            html_content += f"""
    <div class="article {status_class}">
        <h2>{article.title}</h2>
        <div class="meta">
            <strong>Status:</strong> {status_text} |
            <strong>Link:</strong> <a href="{article.link}">{article.link}</a>
"""

            if article.published:
                html_content += f" | <strong>Date:</strong> {article.published.strftime('%Y-%m-%d %H:%M')}"

            if article.author:
                html_content += f" | <strong>Author:</strong> {article.author}"

            html_content += (
                """
        </div>
        <div class="summary">
"""
                + (article.summary or "No summary available")
                + """
        </div>
    </div>
"""
            )

        html_content += """
</body>
</html>"""

        with open(filename, "w", encoding="utf-8") as f:
            f.write(html_content)

        logging.info(f"Exported {len(articles)} articles to {filename}")
        return True

    except Exception as e:
        logging.error(f"Failed to export to HTML: {e}")
        return False


def export_to_markdown(articles: List[Article], filename: str) -> bool:
    """Export articles to Markdown file."""
    try:
        markdown_content = f"""# RSS Articles Export

Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

"""

        for article in articles:
            status = "✓" if article.is_read else "○"

            markdown_content += f"""## {status} {article.title}

**Link:** {article.link}

"""

            if article.published:
                markdown_content += (
                    f"**Date:** {article.published.strftime('%Y-%m-%d %H:%M')}\n\n"
                )

            if article.author:
                markdown_content += f"**Author:** {article.author}\n\n"

            markdown_content += (
                f"**Summary:** {article.summary or 'No summary available'}\n\n---\n\n"
            )

        with open(filename, "w", encoding="utf-8") as f:
            f.write(markdown_content)

        logging.info(f"Exported {len(articles)} articles to {filename}")
        return True

    except Exception as e:
        logging.error(f"Failed to export to Markdown: {e}")
        return False


def setup_logging(level: str = "INFO") -> None:
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(), logging.FileHandler("rss_reader.log")],
    )
