"""
Tracking Blueprint - Routes for email open and click tracking.
"""

import base64
import logging
from urllib.parse import unquote
from flask import Blueprint, Response, redirect, request

from ..storage import CampaignStorage

logger = logging.getLogger(__name__)

tracking_bp = Blueprint("tracking", __name__)

# 1x1 transparent PNG (base64 encoded)
TRANSPARENT_PIXEL = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
)

# Get storage instance (will be set by app factory)
storage = None


def init_storage(storage_instance):
    """Initialize storage for this blueprint."""
    global storage
    storage = storage_instance


@tracking_bp.route("/track/open/<int:campaign_id>/<int:recipient_id>")
def track_email_open(campaign_id: int, recipient_id: int):
    """Track email open events via tracking pixel."""
    try:
        recipient = storage.get_recipient_by_id(recipient_id)
        if recipient and recipient.get("campaign_id") == campaign_id:
            storage.record_email_open(recipient_id)
            logger.info(
                f"Tracked email open: campaign={campaign_id}, recipient={recipient_id}"
            )
        else:
            logger.warning(
                f"Invalid tracking request: campaign={campaign_id}, recipient={recipient_id}"
            )
    except Exception as e:
        logger.error(f"Error tracking email open: {e}")

    response = Response(TRANSPARENT_PIXEL, mimetype="image/png")
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@tracking_bp.route("/track/click/<int:campaign_id>/<int:recipient_id>")
def track_email_click(campaign_id: int, recipient_id: int):
    """Track link clicks and redirect to original URL."""
    original_url = request.args.get("url", "")

    if not original_url:
        return "Missing URL parameter", 400

    try:
        original_url = unquote(original_url)
    except Exception as e:
        logger.error(f"Error decoding URL: {e}")
        return "Invalid URL", 400

    if not original_url.startswith(("http://", "https://")):
        logger.warning(f"Rejected redirect to non-http URL: {original_url}")
        return "Invalid redirect URL", 400

    try:
        recipient = storage.get_recipient_by_id(recipient_id)
        if recipient and recipient.get("campaign_id") == campaign_id:
            storage.record_email_click(recipient_id, campaign_id, original_url)
            logger.info(
                f"Tracked click: campaign={campaign_id}, recipient={recipient_id}"
            )
    except Exception as e:
        logger.error(f"Error tracking click: {e}")

    return redirect(original_url)
