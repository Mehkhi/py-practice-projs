"""
Email tracking utilities.

This module provides functions to inject tracking pixels and wrap links
for open and click tracking.
"""

import re
import logging
from urllib.parse import urlencode, quote
from typing import Optional

logger = logging.getLogger(__name__)


def inject_tracking_pixel(
    html_body: str,
    campaign_id: int,
    recipient_id: int,
    base_url: str = "http://127.0.0.1:9002",
) -> str:
    """
    Inject a 1x1 transparent tracking pixel into HTML email body.

    Args:
        html_body: The HTML content of the email
        campaign_id: The campaign ID for tracking
        recipient_id: The recipient ID for tracking
        base_url: Base URL for the tracking server

    Returns:
        Modified HTML with tracking pixel injected
    """
    if not html_body:
        return html_body

    tracking_url = f"{base_url}/track/open/{campaign_id}/{recipient_id}"
    tracking_pixel = (
        f'<img src="{tracking_url}" width="1" height="1" '
        f'style="display:none;" alt="" />'
    )

    # Try to inject before </body> tag
    body_close_pattern = re.compile(r"</body>", re.IGNORECASE)
    if body_close_pattern.search(html_body):
        html_body = body_close_pattern.sub(f"{tracking_pixel}</body>", html_body)
    else:
        # If no </body> tag, append at the end
        html_body += tracking_pixel

    logger.debug(
        f"Injected tracking pixel for campaign {campaign_id}, recipient {recipient_id}"
    )
    return html_body


def wrap_links_with_tracking(
    html_body: str,
    campaign_id: int,
    recipient_id: int,
    base_url: str = "http://127.0.0.1:9002",
) -> str:
    """
    Replace all links in HTML with tracking URLs.

    Args:
        html_body: The HTML content of the email
        campaign_id: The campaign ID for tracking
        recipient_id: The recipient ID for tracking
        base_url: Base URL for the tracking server

    Returns:
        Modified HTML with links wrapped for tracking
    """
    if not html_body:
        return html_body

    # Pattern to match <a href="..."> tags
    # Captures the href value and preserves other attributes
    link_pattern = re.compile(
        r'<a\s+([^>]*?)href=["\']([^"\']+)["\']([^>]*)>', re.IGNORECASE | re.DOTALL
    )

    def replace_link(match):
        before_href = match.group(1)
        original_url = match.group(2)
        after_href = match.group(3)

        # Skip mailto:, tel:, and anchor links
        if original_url.startswith(("mailto:", "tel:", "#", "javascript:")):
            return match.group(0)

        # Skip tracking URLs (avoid double-wrapping)
        if "/track/click/" in original_url:
            return match.group(0)

        # Create tracking URL
        encoded_url = quote(original_url, safe="")
        tracking_url = (
            f"{base_url}/track/click/{campaign_id}/{recipient_id}?url={encoded_url}"
        )

        return f'<a {before_href}href="{tracking_url}"{after_href}>'

    tracked_html = link_pattern.sub(replace_link, html_body)
    logger.debug(
        f"Wrapped links with tracking for campaign {campaign_id}, recipient {recipient_id}"
    )
    return tracked_html


def add_tracking_to_email(
    html_body: str,
    campaign_id: int,
    recipient_id: int,
    base_url: str = "http://127.0.0.1:9002",
) -> str:
    """
    Add both tracking pixel and link tracking to an HTML email.

    Args:
        html_body: The HTML content of the email
        campaign_id: The campaign ID for tracking
        recipient_id: The recipient ID for tracking
        base_url: Base URL for the tracking server

    Returns:
        Fully tracked HTML email content
    """
    if not html_body:
        return html_body

    # First wrap links, then inject pixel
    tracked_html = wrap_links_with_tracking(
        html_body, campaign_id, recipient_id, base_url
    )
    tracked_html = inject_tracking_pixel(
        tracked_html, campaign_id, recipient_id, base_url
    )

    logger.info(
        f"Added tracking to email for campaign {campaign_id}, recipient {recipient_id}"
    )
    return tracked_html
