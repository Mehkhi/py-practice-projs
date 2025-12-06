"""
Campaigns Blueprint - Routes for campaign management.
"""

import io
import csv
from flask import Blueprint, render_template, request, redirect, url_for, send_file

from ..storage import CampaignStorage
from ..utils import load_recipients_from_csv, format_email_template, load_template_file

campaigns_bp = Blueprint("campaigns", __name__)

# Get storage instance (will be set by app factory)
storage = None


def init_storage(storage_instance):
    """Initialize storage for this blueprint."""
    global storage
    storage = storage_instance


def get_dashboard_stats() -> dict:
    """Aggregate statistics from all campaigns for the dashboard."""
    campaigns = storage.list_campaigns()

    total_campaigns = len(campaigns)
    total_recipients = 0
    total_sent = 0
    total_failed = 0
    total_queued = 0

    for campaign in campaigns:
        stats = storage.get_campaign_stats(campaign["id"])
        campaign["recipient_count"] = stats["total"]
        campaign["sent_count"] = stats["sent"]
        campaign["failed_count"] = stats["failed"]

        total_recipients += stats["total"]
        total_sent += stats["sent"]
        total_failed += stats["failed"]
        total_queued += stats["queued"]

    if total_recipients > 0:
        success_rate = round((total_sent / total_recipients) * 100, 1)
    else:
        success_rate = 0.0

    total_opens = 0
    total_clicks = 0
    for c in campaigns:
        campaign_stats = storage.get_campaign_stats(c["id"])
        total_opens += campaign_stats.get("opened_count", 0)
        total_clicks += campaign_stats.get("click_count", 0)

    if total_sent > 0:
        average_open_rate = round((total_opens / total_sent) * 100, 1)
    else:
        average_open_rate = 0.0

    return {
        "total_campaigns": total_campaigns,
        "total_recipients": total_recipients,
        "total_sent": total_sent,
        "total_failed": total_failed,
        "total_queued": total_queued,
        "success_rate": success_rate,
        "total_opens": total_opens,
        "total_clicks": total_clicks,
        "average_open_rate": average_open_rate,
        "recent_campaigns": campaigns[:5],
    }


@campaigns_bp.route("/")
def index():
    """Display dashboard with stats and recent campaigns."""
    stats = get_dashboard_stats()
    return render_template("dashboard.html", stats=stats)


@campaigns_bp.route("/campaigns")
def campaigns_list():
    """List all campaigns."""
    campaigns = storage.list_campaigns()
    return render_template("campaigns/list.html", campaigns=campaigns)


@campaigns_bp.route("/campaign/new")
def new_campaign():
    """Show new campaign form."""
    signatures = storage.list_signatures()
    return render_template("campaigns/new.html", signatures=signatures)


@campaigns_bp.route("/campaign/create", methods=["POST"])
def create_campaign():
    """Create a new campaign."""
    name = request.form.get("name")
    subject = request.form.get("subject")
    body = request.form.get("body")
    html_template_path = request.form.get("html_template")
    source_type = request.form.get("source_type", "csv")
    signature_id = request.form.get("signature_id")

    if signature_id:
        try:
            signature_id = int(signature_id)
        except ValueError:
            signature_id = None
    else:
        signature_id = None

    html_template = None
    if html_template_path:
        try:
            html_template = load_template_file(html_template_path)
        except Exception as e:
            return f"Error loading HTML template: {e}", 400

    campaign_id = storage.create_campaign(
        name=name,
        subject=subject,
        body_template=body,
        html_template=html_template,
        template_file_path=html_template_path,
        source_type=source_type,
        signature_id=signature_id,
    )

    return redirect(url_for("campaigns.campaign_detail", campaign_id=campaign_id))


@campaigns_bp.route("/campaign/<int:campaign_id>")
def campaign_detail(campaign_id):
    """Show campaign details."""
    campaign = storage.get_campaign(campaign_id)
    if not campaign:
        return "Campaign not found", 404

    recipients = storage.get_recipients(campaign_id)
    stats = storage.get_campaign_stats(campaign_id)

    for recipient in recipients:
        clicks = storage.get_recipient_clicks(recipient["id"])
        recipient["click_count"] = len(clicks)

    return render_template(
        "campaigns/detail.html", campaign=campaign, recipients=recipients, stats=stats
    )


@campaigns_bp.route("/campaign/<int:campaign_id>/send", methods=["GET", "POST"])
def send_campaign(campaign_id):
    """Show send form or initiate sending."""
    campaign = storage.get_campaign(campaign_id)
    if not campaign:
        return "Campaign not found", 404

    if request.method == "POST":
        transport = request.form.get("transport", "smtp")
        return render_template(
            "campaigns/sending.html", campaign=campaign, transport=transport
        )

    return render_template("campaigns/send.html", campaign=campaign)


@campaigns_bp.route("/campaign/<int:campaign_id>/export")
def export_campaign(campaign_id):
    """Export campaign results as CSV."""
    results = storage.export_campaign_results(campaign_id)
    if not results:
        return "No results to export", 404

    output = io.StringIO()
    fieldnames = list(results[0].keys())
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(results)

    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode("utf-8")),
        mimetype="text/csv",
        as_attachment=True,
        download_name=f"campaign_{campaign_id}_results.csv",
    )


@campaigns_bp.route("/campaign/import", methods=["GET", "POST"])
def import_csv():
    """Import recipients from CSV."""
    if request.method == "POST":
        campaign_id = request.form.get("campaign_id")
        csv_file = request.files.get("csv_file")

        if not campaign_id or not csv_file:
            return "Missing campaign ID or CSV file", 400

        try:
            campaign_id = int(campaign_id)
            content = csv_file.read().decode("utf-8")
            recipients = load_recipients_from_csv(io.StringIO(content))
            storage.add_recipients(campaign_id, recipients)
            return redirect(
                url_for("campaigns.campaign_detail", campaign_id=campaign_id)
            )
        except Exception as e:
            return f"Error importing CSV: {e}", 400

    return render_template("campaigns/import.html")


@campaigns_bp.route("/campaign/<int:campaign_id>/delete", methods=["POST"])
def delete_campaign(campaign_id):
    """Delete a campaign and all its data."""
    if storage.delete_campaign(campaign_id):
        return redirect(url_for("campaigns.campaigns_list"))
    return "Campaign not found", 404


@campaigns_bp.route("/campaign/<int:campaign_id>/preview")
def preview_email(campaign_id):
    """Preview email with personalization for a specific recipient."""
    campaign = storage.get_campaign(campaign_id)
    if not campaign:
        return "Campaign not found", 404

    recipients = storage.get_recipients(campaign_id)
    if not recipients:
        return "No recipients in this campaign", 404

    recipient_id = request.args.get("recipient_id", type=int)
    selected_recipient = None
    for r in recipients:
        if r["id"] == recipient_id:
            selected_recipient = r
            break
    if not selected_recipient:
        selected_recipient = recipients[0]

    personalization = selected_recipient.get("personalization_data", {})
    if isinstance(personalization, str):
        import json

        try:
            personalization = json.loads(personalization)
        except:
            personalization = {}

    rendered_subject = format_email_template(
        campaign.get("subject", ""), personalization
    )
    rendered_text = format_email_template(
        campaign.get("body_template", ""), personalization
    )
    rendered_html = campaign.get("html_template", "") or rendered_text
    if rendered_html:
        rendered_html = format_email_template(rendered_html, personalization)

    signature_id = campaign.get("signature_id")
    if signature_id:
        signature = storage.get_signature(signature_id)
        if signature:
            rendered_text += "\n\n" + signature.get("content", "")
            if signature.get("html_content"):
                rendered_html += "<br><br>" + signature.get("html_content")

    return render_template(
        "campaigns/preview.html",
        campaign=campaign,
        recipients=recipients,
        selected_recipient=selected_recipient,
        rendered_subject=rendered_subject,
        rendered_text=rendered_text,
        rendered_html=rendered_html,
        from_email=None,
    )


# Recipient management routes
@campaigns_bp.route("/recipient/<int:recipient_id>/delete", methods=["POST"])
def delete_recipient(recipient_id):
    """Delete a single recipient."""
    recipient = storage.get_recipient_by_id(recipient_id)
    if not recipient:
        return "Recipient not found", 404

    campaign_id = recipient["campaign_id"]
    storage.delete_recipient(recipient_id)
    return redirect(url_for("campaigns.campaign_detail", campaign_id=campaign_id))


@campaigns_bp.route("/recipient/<int:recipient_id>/retry", methods=["POST"])
def retry_recipient(recipient_id):
    """Retry a failed recipient."""
    recipient = storage.get_recipient_by_id(recipient_id)
    if not recipient:
        return "Recipient not found", 404

    campaign_id = recipient["campaign_id"]
    storage.retry_recipient(recipient_id)
    return redirect(url_for("campaigns.campaign_detail", campaign_id=campaign_id))


@campaigns_bp.route("/campaign/<int:campaign_id>/retry-all", methods=["POST"])
def retry_all_failed(campaign_id):
    """Retry all failed recipients in a campaign."""
    storage.retry_all_failed(campaign_id)
    return redirect(url_for("campaigns.campaign_detail", campaign_id=campaign_id))
