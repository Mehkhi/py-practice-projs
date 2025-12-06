"""
Signatures Blueprint - Routes for email signature management.
"""

from flask import Blueprint, render_template, request, redirect, url_for

from ..storage import CampaignStorage

signatures_bp = Blueprint("signatures", __name__)

# Get storage instance (will be set by app factory)
storage = None


def init_storage(storage_instance):
    """Initialize storage for this blueprint."""
    global storage
    storage = storage_instance


@signatures_bp.route("/signatures")
def list_signatures():
    """List all email signatures."""
    signatures = storage.list_signatures()
    return render_template("signatures/list.html", signatures=signatures)


@signatures_bp.route("/signature/new", methods=["GET", "POST"])
def new_signature():
    """Create a new email signature."""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        content = request.form.get("content", "").strip()
        html_content = request.form.get("html_content", "").strip() or None
        is_default = request.form.get("is_default") == "on"

        if not name or not content:
            return "Name and content are required", 400

        storage.create_signature(
            name=name, content=content, html_content=html_content, is_default=is_default
        )
        return redirect(url_for("signatures.list_signatures"))

    return render_template("signatures/form.html", signature=None)


@signatures_bp.route("/signature/<int:signature_id>/edit", methods=["GET", "POST"])
def edit_signature(signature_id):
    """Edit an existing email signature."""
    signature = storage.get_signature(signature_id)
    if not signature:
        return "Signature not found", 404

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        content = request.form.get("content", "").strip()
        html_content = request.form.get("html_content", "").strip() or None
        is_default = request.form.get("is_default") == "on"

        if not name or not content:
            return "Name and content are required", 400

        storage.update_signature(
            signature_id=signature_id,
            name=name,
            content=content,
            html_content=html_content,
            is_default=is_default,
        )
        return redirect(url_for("signatures.list_signatures"))

    return render_template("signatures/form.html", signature=signature)


@signatures_bp.route("/signature/<int:signature_id>/delete", methods=["POST"])
def delete_signature(signature_id):
    """Delete an email signature."""
    storage.delete_signature(signature_id)
    return redirect(url_for("signatures.list_signatures"))


@signatures_bp.route("/signature/<int:signature_id>/set-default", methods=["POST"])
def set_default_signature(signature_id):
    """Set a signature as the default."""
    storage.update_signature(signature_id, is_default=True)
    return redirect(url_for("signatures.list_signatures"))
