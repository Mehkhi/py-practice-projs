"""
Attachments Blueprint - Routes for campaign attachment management.
"""

import os
import logging
from flask import Blueprint, render_template, request, redirect, url_for, send_file

from ..storage import CampaignStorage

logger = logging.getLogger(__name__)

attachments_bp = Blueprint("attachments", __name__)

# Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp", "svg", "pdf", "doc", "docx"}

# Get storage instance (will be set by app factory)
storage = None


def init_storage(storage_instance):
    """Initialize storage for this blueprint."""
    global storage
    storage = storage_instance


def allowed_file(filename):
    """Check if file extension is allowed."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_mime_type(filename):
    """Get MIME type from filename."""
    import mimetypes

    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type or "application/octet-stream"


@attachments_bp.route("/campaign/<int:campaign_id>/attachments")
def campaign_attachments(campaign_id):
    """Show attachments for a campaign."""
    campaign = storage.get_campaign(campaign_id)
    if not campaign:
        return "Campaign not found", 404

    attachments = storage.get_campaign_attachments(campaign_id)
    return render_template(
        "attachments/manage.html", campaign=campaign, attachments=attachments
    )


@attachments_bp.route("/campaign/<int:campaign_id>/upload", methods=["POST"])
def upload_attachment(campaign_id):
    """Upload an attachment to a campaign."""
    campaign = storage.get_campaign(campaign_id)
    if not campaign:
        return "Campaign not found", 404

    if "file" not in request.files:
        return "No file provided", 400

    file = request.files["file"]
    if file.filename == "":
        return "No file selected", 400

    if not allowed_file(file.filename):
        return f"File type not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}", 400

    # Create uploads directory if needed
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # Generate unique filename
    import uuid

    ext = file.filename.rsplit(".", 1)[1].lower()
    unique_filename = f"{uuid.uuid4().hex}.{ext}"
    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)

    # Save file
    file.save(file_path)
    file_size = os.path.getsize(file_path)

    # Check if inline image
    is_inline = request.form.get("is_inline") == "on"
    content_id = None
    if is_inline:
        content_id = f"img{uuid.uuid4().hex[:8]}"

    # Store in database
    storage.add_attachment(
        campaign_id=campaign_id,
        filename=unique_filename,
        original_filename=file.filename,
        file_path=file_path,
        mime_type=get_mime_type(file.filename),
        file_size=file_size,
        is_inline=is_inline,
        content_id=content_id,
    )

    return redirect(
        url_for("attachments.campaign_attachments", campaign_id=campaign_id)
    )


@attachments_bp.route("/attachment/<int:attachment_id>/delete", methods=["POST"])
def delete_attachment(attachment_id):
    """Delete an attachment."""
    attachment = storage.get_attachment(attachment_id)
    if not attachment:
        return "Attachment not found", 404

    campaign_id = attachment["campaign_id"]
    file_path = storage.delete_attachment(attachment_id)

    # Delete file from disk
    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            logger.warning(f"Failed to delete file {file_path}: {e}")

    return redirect(
        url_for("attachments.campaign_attachments", campaign_id=campaign_id)
    )


@attachments_bp.route("/attachment/<int:attachment_id>/view")
def view_attachment(attachment_id):
    """View/download an attachment."""
    attachment = storage.get_attachment(attachment_id)
    if not attachment:
        return "Attachment not found", 404

    file_path = attachment["file_path"]
    if not os.path.exists(file_path):
        return "File not found", 404

    return send_file(
        file_path,
        mimetype=attachment.get("mime_type"),
        as_attachment=False,
        download_name=attachment["original_filename"],
    )
