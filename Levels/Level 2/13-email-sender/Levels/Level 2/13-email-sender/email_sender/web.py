"""
Lightweight web UI for mail merge campaigns.

This module provides a Flask-based web interface for managing campaigns.
"""

import os
import logging
from pathlib import Path
from typing import Optional
from flask import (
    Flask,
    render_template_string,
    request,
    jsonify,
    redirect,
    url_for,
    send_file,
)
import csv
import io

from .storage import CampaignStorage
from .utils import load_recipients_from_csv, format_email_template, load_template_file
from .sheets_sync import SheetsSync
from .gmail_api import GmailAPISender
from .core import EmailSender

logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

# Initialize storage
storage = CampaignStorage()


def get_dashboard_stats() -> dict:
    """
    Aggregate statistics from all campaigns for the dashboard.

    Returns:
        Dictionary with dashboard metrics including totals and success rate.
    """
    campaigns = storage.list_campaigns()

    total_campaigns = len(campaigns)
    total_recipients = sum(c.get("recipient_count", 0) or 0 for c in campaigns)
    total_sent = sum(c.get("sent_count", 0) or 0 for c in campaigns)
    total_failed = sum(c.get("failed_count", 0) or 0 for c in campaigns)
    total_queued = total_recipients - total_sent - total_failed

    # Calculate success rate based on total recipients (avoid division by zero)
    # This gives a true picture of delivery progress, not just sent/(sent+failed)
    if total_recipients > 0:
        success_rate = round((total_sent / total_recipients) * 100, 1)
    else:
        success_rate = 0.0

    return {
        "total_campaigns": total_campaigns,
        "total_recipients": total_recipients,
        "total_sent": total_sent,
        "total_failed": total_failed,
        "total_queued": total_queued,
        "success_rate": success_rate,
        "recent_campaigns": campaigns[:5],  # Already ordered by created_at DESC
    }


# CSS to be injected into all templates
NORD_CSS = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        :root {
            --n0: #2e3440; --n1: #3b4252; --n2: #434c5e; --n3: #4c566a;
            --n4: #d8dee9; --n5: #e5e9f0; --n6: #eceff4;
            --n7: #8fbcbb; --n8: #88c0d0; --n9: #81a1c1; --n10: #5e81ac;
            --n11: #bf616a; --n12: #d08770; --n13: #ebcb8b; --n14: #a3be8c; --n15: #b48ead;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: var(--n0);
            color: var(--n6);
            line-height: 1.6;
            padding: 2rem;
            min-height: 100vh;
        }
        .container { max-width: 1200px; margin: 0 auto; }

        /* Typography */
        h1, h2, h3, h4 { color: var(--n6); font-weight: 700; letter-spacing: -0.025em; }
        h1 { font-size: 1.8rem; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.75rem; }
        h2 { font-size: 1.4rem; margin-bottom: 1rem; }
        h3 { font-size: 1.1rem; }
        p { color: var(--n4); font-size: 0.95rem; }
        .text-muted { color: var(--n3); }
        a { color: var(--n8); text-decoration: none; transition: 0.2s; }
        a:hover { color: var(--n7); }

        /* Cards */
        .card {
            background: var(--n1);
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            border: 1px solid var(--n0);
            margin-bottom: 1.5rem;
            overflow: hidden;
        }
        .card-header {
            padding: 1.25rem 1.5rem;
            border-bottom: 1px solid var(--n0);
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: rgba(0,0,0,0.1);
        }
        .card-body { padding: 1.5rem; }

        /* Buttons */
        .btn {
            display: inline-flex; align-items: center; gap: 0.5rem;
            padding: 0.6rem 1.2rem;
            border-radius: 6px;
            font-weight: 500;
            font-size: 0.9rem;
            border: 1px solid transparent;
            cursor: pointer;
            transition: all 0.2s;
            text-decoration: none;
            line-height: 1;
        }
        .btn-primary { background: var(--n10); color: var(--n6); }
        .btn-primary:hover { background: var(--n9); transform: translateY(-1px); box-shadow: 0 2px 4px rgba(0,0,0,0.2); }

        .btn-success { background: var(--n14); color: var(--n1); }
        .btn-success:hover { background: var(--n7); transform: translateY(-1px); box-shadow: 0 2px 4px rgba(0,0,0,0.2); }

        .btn-outline { background: transparent; border-color: var(--n3); color: var(--n4); }
        .btn-outline:hover { border-color: var(--n9); color: var(--n9); background: var(--n2); }

        .btn-danger { background: var(--n11); color: var(--n6); }
        .btn-danger:hover { background: #d08770; }

        .btn-sm { padding: 0.4rem 0.8rem; font-size: 0.85rem; }

        /* Inputs */
        .form-group { margin-bottom: 1.5rem; }
        label { display: block; margin-bottom: 0.5rem; color: var(--n4); font-weight: 500; font-size: 0.9rem; }
        .label-hint { color: var(--n3); font-size: 0.8rem; font-weight: normal; margin-left: 0.5rem; }

        input[type="text"], input[type="number"], input[type="file"], textarea, select {
            width: 100%;
            padding: 0.75rem;
            background: var(--n0);
            border: 1px solid var(--n2);
            border-radius: 6px;
            color: var(--n6);
            font-size: 0.95rem;
            transition: 0.2s;
            font-family: inherit;
        }
        input:focus, select:focus, textarea:focus {
            outline: none;
            border-color: var(--n8);
            box-shadow: 0 0 0 3px rgba(136, 192, 208, 0.1);
        }
        .hint { color: var(--n3); font-size: 0.85rem; margin-top: 0.5rem; }

        /* Tables */
        table { width: 100%; border-collapse: collapse; }
        th { text-align: left; padding: 1rem; color: var(--n4); font-size: 0.75rem; text-transform: uppercase; border-bottom: 2px solid var(--n0); letter-spacing: 0.05em; }
        td { padding: 1rem; border-bottom: 1px solid var(--n0); color: var(--n5); font-size: 0.95rem; }
        tr:last-child td { border-bottom: none; }
        tr:hover td { background: rgba(255,255,255,0.02); }

        /* Stats & Badges */
        .header-nav { display: flex; gap: 1rem; align-items: center; }
        .badge { padding: 0.35rem 0.85rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; display: inline-flex; align-items: center; gap: 0.4rem; }
        .badge-sent { background: rgba(163, 190, 140, 0.15); color: var(--n14); border: 1px solid rgba(163, 190, 140, 0.2); }
        .badge-failed { background: rgba(191, 97, 106, 0.15); color: var(--n11); border: 1px solid rgba(191, 97, 106, 0.2); }
        .badge-queued { background: rgba(235, 203, 139, 0.15); color: var(--n13); border: 1px solid rgba(235, 203, 139, 0.2); }

        /* Dashboard Grid */
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1.5rem; margin-bottom: 2.5rem; }
        .stat-card { background: var(--n1); padding: 1.75rem; border-radius: 8px; border: 1px solid var(--n2); position: relative; overflow: hidden; transition: transform 0.2s; }
        .stat-card:hover { transform: translateY(-2px); border-color: var(--n3); }
        .stat-value { font-size: 2.25rem; font-weight: 700; color: var(--n6); line-height: 1.2; margin: 0.5rem 0; }
        .stat-label { color: var(--n4); font-size: 0.85rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }

        /* Accents */
        .accent-border-top { border-top: 4px solid var(--n8); }
        .border-sent { border-top-color: var(--n14); }
        .border-failed { border-top-color: var(--n11); }
        .border-queued { border-top-color: var(--n13); }

        /* Campaign List Item */
        .campaign-list { display: flex; flex-direction: column; gap: 1rem; }
        .campaign-item {
            background: var(--n1); border: 1px solid var(--n2); border-radius: 8px; padding: 1.5rem;
            display: flex; justify-content: space-between; align-items: center; transition: 0.2s;
        }
        .campaign-item:hover { border-color: var(--n9); box-shadow: 0 4px 12px rgba(0,0,0,0.1); }

        /* Empty State */
        .empty-state { text-align: center; padding: 4rem 2rem; color: var(--n3); }

        /* Responsive */
        @media (max-width: 768px) {
            .campaign-item { flex-direction: column; align-items: flex-start; gap: 1rem; }
            .header { flex-direction: column; align-items: flex-start; gap: 1rem; }
            .header-nav { width: 100%; justify-content: flex-start; flex-wrap: wrap; }
            .stat-card { padding: 1.25rem; }
        }
    </style>
"""


# HTML Templates
DASHBOARD_TEMPLATE = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Mail Merge - Dashboard</title>
    {NORD_CSS}
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>Mail Merge</h1>
            <div class="header-nav">
                <a href="/campaigns" class="btn btn-outline btn-sm">View All Campaigns</a>
                <a href="/campaign/new" class="btn btn-primary btn-sm">Create New</a>
            </div>
        </div>

        <!-- Stats Grid -->
        <div class="stats-grid">
            <div class="stat-card accent-border-top">
                <div class="stat-label">Total Campaigns</div>
                <div class="stat-value">{{{{ stats.total_campaigns }}}}</div>
            </div>
            <div class="stat-card accent-border-top border-sent">
                <div class="stat-label">Emails Sent</div>
                <div class="stat-value">{{{{ stats.total_sent }}}}</div>
            </div>
            <div class="stat-card accent-border-top border-failed">
                <div class="stat-label">Emails Failed</div>
                <div class="stat-value">{{{{ stats.total_failed }}}}</div>
            </div>
            <div class="stat-card accent-border-top border-queued">
                <div class="stat-label">Success Rate</div>
                <div class="stat-value">{{{{ stats.success_rate }}}}%</div>
            </div>
        </div>

        <!-- Recent Campaigns -->
        <div class="card">
            <div class="card-header">
                <h2>Recent Campaigns</h2>
                <a href="/campaigns" class="btn btn-outline btn-sm">View All →</a>
            </div>
            <div class="card-body">
                {{% if stats.recent_campaigns %}}
                <div class="campaign-list">
                    {{% for campaign in stats.recent_campaigns %}}
                    <div class="campaign-item">
                        <div class="campaign-info">
                            <h3 style="margin-bottom: 0.25rem">{{{{ campaign.name }}}}</h3>
                            <p style="font-size: 0.9rem; color: var(--n4)">{{{{ campaign.subject }}}}</p>
                            <div style="display: flex; gap: 1rem; margin-top: 0.75rem; font-size: 0.85rem; color: var(--n3)">
                                <span>Recipients: {{{{ campaign.recipient_count or 0 }}}}</span>
                                <span style="color: var(--n14)">Sent: {{{{ campaign.sent_count or 0 }}}}</span>
                                <span style="color: var(--n11)">Failed: {{{{ campaign.failed_count or 0 }}}}</span>
                            </div>
                        </div>
                        <div class="campaign-actions">
                            <a href="/campaign/{{{{ campaign.id }}}}" class="btn btn-outline btn-sm">Manage</a>
                            <a href="/campaign/{{{{ campaign.id }}}}/send" class="btn btn-success btn-sm">Send</a>
                        </div>
                    </div>
                    {{% endfor %}}
                </div>
                {{% else %}}
                <div class="empty-state">
                    <h3>No Campaigns Yet</h3>
                    <p>Create your first campaign to get started!</p>
                    <a href="/campaign/new" class="btn btn-primary" style="margin-top: 1rem;">Create Campaign</a>
                </div>
                {{% endif %}}
            </div>
        </div>
    </div>
</body>
</html>
"""

CAMPAIGNS_LIST_TEMPLATE = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Mail Merge - All Campaigns</title>
    {NORD_CSS}
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>All Campaigns</h1>
            <div class="header-nav">
                <a href="/" class="btn btn-outline btn-sm">← Dashboard</a>
                <a href="/campaign/new" class="btn btn-primary btn-sm">New Campaign</a>
                <a href="/campaign/import" class="btn btn-outline btn-sm">Import CSV</a>
            </div>
        </div>

        <div class="card">
            <div class="card-body">
                {{% if campaigns %}}
                <div class="campaign-list">
                    {{% for campaign in campaigns %}}
                    <div class="campaign-item">
                        <div class="campaign-info" style="flex: 1">
                            <div style="display: flex; align-items: baseline; gap: 0.5rem; margin-bottom: 0.25rem;">
                                <h3>{{{{ campaign.name }}}}</h3>
                                <span style="font-size: 0.8rem; color: var(--n3)">#{{{{ campaign.id }}}}</span>
                            </div>
                            <p style="margin-bottom: 0.75rem">{{{{ campaign.subject }}}}</p>

                            <div style="display: flex; gap: 0.5rem;">
                                <span class="badge badge-queued">Total: {{{{ campaign.recipient_count or 0 }}}}</span>
                                <span class="badge badge-sent">Sent: {{{{ campaign.sent_count or 0 }}}}</span>
                                <span class="badge badge-failed">Failed: {{{{ campaign.failed_count or 0 }}}}</span>
                            </div>
                        </div>

                        <div class="campaign-actions" style="display: flex; gap: 0.5rem;">
                            <a href="/campaign/{{{{ campaign.id }}}}" class="btn btn-outline btn-sm">Details</a>
                            <a href="/campaign/{{{{ campaign.id }}}}/send" class="btn btn-success btn-sm">Send</a>
                            <a href="/campaign/{{{{ campaign.id }}}}/export" class="btn btn-outline btn-sm">Export</a>
                        </div>
                    </div>
                    {{% endfor %}}
                </div>
                {{% else %}}
                <div class="empty-state">
                    <h3>No Campaigns Yet</h3>
                    <p>Create your first campaign to get started!</p>
                    <a href="/campaign/new" class="btn btn-primary" style="margin-top: 15px;">Create Campaign</a>
                </div>
                {{% endif %}}
            </div>
        </div>
    </div>
</body>
</html>
"""

CAMPAIGN_DETAIL_TEMPLATE = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Campaign: {{{{ campaign.name }}}}</title>
    {NORD_CSS}
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <div style="font-size: 0.85rem; color: var(--n8); margin-bottom: 0.25rem; text-transform: uppercase; font-weight: 600;">Campaign #{{{{ campaign.id }}}}</div>
                <h1>{{{{ campaign.name }}}}</h1>
                <p class="text-muted">Subject: <span style="color: var(--n6)">{{{{ campaign.subject }}}}</span></p>
            </div>
            <div class="header-nav">
                <a href="/" class="btn btn-outline btn-sm">Dashboard</a>
                <a href="/campaigns" class="btn btn-outline btn-sm">All Campaigns</a>
            </div>
        </div>

        <div class="stats-grid">
            <div class="stat-card border-sent">
                <div class="stat-label">Sent</div>
                <div class="stat-value" style="color: var(--n14)">{{{{ stats.sent }}}}</div>
            </div>
            <div class="stat-card border-failed">
                <div class="stat-label">Failed</div>
                <div class="stat-value" style="color: var(--n11)">{{{{ stats.failed }}}}</div>
            </div>
            <div class="stat-card border-queued">
                <div class="stat-label">Queued</div>
                <div class="stat-value" style="color: var(--n13)">{{{{ stats.queued }}}}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Total</div>
                <div class="stat-value">{{{{ stats.total }}}}</div>
            </div>
        </div>

        <div style="margin-bottom: 2rem; display: flex; gap: 1rem;">
            <a href="/campaign/{{{{ campaign.id }}}}/send" class="btn btn-success">Launch Campaign</a>
            <a href="/campaign/{{{{ campaign.id }}}}/export" class="btn btn-primary">Export Results</a>
        </div>

        <div class="card">
            <div class="card-header">
                <h2>Recipients</h2>
                <span class="badge badge-queued">{{{{ recipients|length }}}} total</span>
            </div>
            <div class="card-body" style="padding: 0;">
                {{% if recipients %}}
                <div style="overflow-x: auto;">
                    <table>
                        <thead>
                            <tr>
                                <th>Email</th>
                                <th>Status</th>
                                <th>Info</th>
                                <th>Sent At</th>
                            </tr>
                        </thead>
                        <tbody>
                            {{% for recipient in recipients %}}
                            <tr>
                                <td style="font-weight: 500;">{{{{ recipient.email }}}}</td>
                                <td>
                                    {{% if recipient.status == 'sent' %}}
                                        <span class="badge badge-sent">Sent</span>
                                    {{% elif recipient.status == 'failed' %}}
                                        <span class="badge badge-failed">Failed</span>
                                    {{% else %}}
                                        <span class="badge badge-queued">Queued</span>
                                    {{% endif %}}
                                </td>
                                <td>
                                    {{% if recipient.error_message %}}
                                        <span style="color: var(--n11); font-size: 0.85rem;">{{{{ recipient.error_message }}}}</span>
                                    {{% else %}}
                                        <span style="color: var(--n3); font-size: 0.85rem;">-</span>
                                    {{% endif %}}
                                </td>
                                <td style="font-size: 0.85rem; color: var(--n4);">{{{{ recipient.sent_at or '-' }}}}</td>
                            </tr>
                            {{% endfor %}}
                        </tbody>
                    </table>
                </div>
                {{% else %}}
                <div class="empty-state">
                    <p>No recipients yet.</p>
                    <a href="/campaign/import" class="btn btn-outline btn-sm" style="margin-top: 1rem">Import from CSV</a>
                </div>
                {{% endif %}}
            </div>
        </div>
    </div>
</body>
</html>
"""

NEW_CAMPAIGN_TEMPLATE = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>New Campaign</title>
    {NORD_CSS}
</head>
<body>
    <div class="container" style="max-width: 800px;">
        <div class="header">
            <h1>Create New Campaign</h1>
            <a href="/" class="btn btn-outline btn-sm">Cancel</a>
        </div>

        <div class="card">
            <div class="card-body">
                <form method="POST" action="/campaign/create">
                    <div class="form-group">
                        <label>Campaign Name</label>
                        <input type="text" name="name" placeholder="e.g., Summer Newsletter 2024" required autofocus>
                        <p class="hint">Internal name for your reference</p>
                    </div>

                    <div class="form-group">
                        <label>Email Subject</label>
                        <input type="text" name="subject" placeholder="e.g., Your Weekly Update" required>
                        <p class="hint">What recipients will see in their inbox</p>
                    </div>

                    <div class="form-group">
                        <label>Body Template <span class="label-hint">(Plain text fallback)</span></label>
                        <textarea name="body" placeholder="Hello {{name}},&#10;&#10;Thank you for subscribing..." rows="6"></textarea>
                        <p class="hint">Use {{variable}} for personalization placeholders</p>
                    </div>

                    <div class="form-group">
                        <label>HTML Template Path <span class="label-hint">(Optional)</span></label>
                        <input type="text" name="html_template" placeholder="/path/to/template.html">
                        <p class="hint">Absolute path to an HTML file for rich email content</p>
                    </div>

                    <div class="form-group">
                        <label>Source Type</label>
                        <select name="source_type">
                            <option value="csv">CSV File</option>
                            <option value="sheet">Google Sheet</option>
                        </select>
                    </div>

                    <div style="margin-top: 2rem; display: flex; gap: 1rem; border-top: 1px solid var(--n2); padding-top: 1.5rem;">
                        <button type="submit" class="btn btn-primary">Create Campaign</button>
                        <a href="/" class="btn btn-outline">Cancel</a>
                    </div>
                </form>
            </div>
        </div>
    </div>
</body>
</html>
"""


@app.route("/")
def index():
    """Display dashboard with stats and recent campaigns."""
    stats = get_dashboard_stats()
    return render_template_string(DASHBOARD_TEMPLATE, stats=stats)


@app.route("/campaigns")
def campaigns_list():
    """List all campaigns."""
    campaigns = storage.list_campaigns()
    return render_template_string(CAMPAIGNS_LIST_TEMPLATE, campaigns=campaigns)


@app.route("/campaign/new")
def new_campaign():
    """Show new campaign form."""
    return render_template_string(NEW_CAMPAIGN_TEMPLATE)


@app.route("/campaign/create", methods=["POST"])
def create_campaign():
    """Create a new campaign."""
    name = request.form.get("name")
    subject = request.form.get("subject")
    body = request.form.get("body")
    html_template_path = request.form.get("html_template")
    source_type = request.form.get("source_type", "csv")

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
    )

    return redirect(url_for("campaign_detail", campaign_id=campaign_id))


@app.route("/campaign/<int:campaign_id>")
def campaign_detail(campaign_id):
    """Show campaign details."""
    campaign = storage.get_campaign(campaign_id)
    if not campaign:
        return "Campaign not found", 404

    recipients = storage.get_recipients(campaign_id)
    stats = storage.get_campaign_stats(campaign_id)

    return render_template_string(
        CAMPAIGN_DETAIL_TEMPLATE, campaign=campaign, recipients=recipients, stats=stats
    )


@app.route("/campaign/import", methods=["GET", "POST"])
def import_csv():
    """Import CSV to a campaign."""
    if request.method == "GET":
        campaigns = storage.list_campaigns()
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Import CSV</title>
    {NORD_CSS}
</head>
<body>
    <div class="container" style="max-width: 600px;">
        <div class="header">
            <h1>Import Recipients</h1>
            <a href="/" class="btn btn-outline btn-sm">Dashboard</a>
        </div>
        <div class="card">
            <div class="card-body">
                <form method="POST" enctype="multipart/form-data">
                    <div class="form-group">
                        <label>Target Campaign ID</label>
                        <input type="number" name="campaign_id" placeholder="e.g., 1" required>
                        <p class="hint">The ID of the campaign to add recipients to</p>
                    </div>
                    <div class="form-group">
                        <label>CSV File</label>
                        <div style="background: var(--n0); border: 2px dashed var(--n2); padding: 2rem; text-align: center; border-radius: 8px;">
                            <input type="file" name="csv_file" accept=".csv" required style="background: transparent; border: none;">
                        </div>
                        <p class="hint">File must contain an "email" column</p>
                    </div>
                    <div style="margin-top: 2rem; display: flex; gap: 1rem;">
                        <button type="submit" class="btn btn-success">Import Data</button>
                        <a href="/campaigns" class="btn btn-outline">Cancel</a>
                    </div>
                </form>
            </div>
        </div>
    </div>
</body>
</html>
        """

    try:
        campaign_id = int(request.form.get("campaign_id"))
    except (ValueError, TypeError):
        return "Invalid campaign ID", 400

    # Check campaign exists
    campaign = storage.get_campaign(campaign_id)
    if not campaign:
        return "Campaign not found. Please check the ID.", 404

    csv_file = request.files.get("csv_file")

    if not csv_file:
        return "No file uploaded", 400

    # Save uploaded file temporarily
    temp_path = Path(f"temp_{csv_file.filename}")
    csv_file.save(str(temp_path))

    try:
        recipients = load_recipients_from_csv(str(temp_path))
        added = storage.add_recipients(campaign_id, recipients)
        return redirect(url_for("campaign_detail", campaign_id=campaign_id))
    finally:
        if temp_path.exists():
            temp_path.unlink()


@app.route("/campaign/<int:campaign_id>/send", methods=["GET", "POST"])
def send_campaign(campaign_id):
    """Send campaign emails."""
    campaign = storage.get_campaign(campaign_id)
    if not campaign:
        return "Campaign not found", 404

    if request.method == "GET":
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Send Campaign</title>
    {NORD_CSS}
</head>
<body>
    <div class="container" style="max-width: 600px;">
        <div class="header">
            <div>
                <h1>Send Campaign</h1>
                <p style="color: var(--n8)">{campaign["name"]}</p>
            </div>
            <a href="/campaign/{campaign["id"]}" class="btn btn-outline btn-sm">Back</a>
        </div>
        <div class="card">
            <div class="card-body">
                <div style="background: rgba(235, 203, 139, 0.1); border-left: 4px solid var(--n13); padding: 1rem; margin-bottom: 2rem; border-radius: 4px;">
                    <strong style="color: var(--n13)">Warning:</strong> This will immediately queue emails for sending.
                </div>

                <form method="POST">
                    <div class="form-group">
                        <label>Email Transport</label>
                        <select name="transport">
                            <option value="gmail">Gmail API (Recommended)</option>
                            <option value="smtp">SMTP</option>
                        </select>
                    </div>

                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                        <div class="form-group">
                            <label>Batch Size</label>
                            <input type="number" name="batch_size" value="10" min="1" max="100">
                        </div>
                        <div class="form-group">
                            <label>Delay (seconds)</label>
                            <input type="number" name="delay" value="1.0" step="0.1" min="0">
                        </div>
                    </div>

                    <div style="margin-top: 1rem; display: flex; gap: 1rem; justify-content: center;">
                        <button type="submit" class="btn btn-success" style="width: 100%; padding: 1rem;">
                            Start Sending
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</body>
</html>
        """

    transport = request.form.get("transport", "gmail")
    batch_size = int(request.form.get("batch_size", 10))
    delay = float(request.form.get("delay", 1.0))

    # TODO: Trigger async sending task here
    # For now we just show the started page

    return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Sending Initiated</title>
    {NORD_CSS}
</head>
<body style="display: flex; align-items: center; justify-content: center;">
    <div class="card" style="text-align: center; max-width: 500px; padding: 2rem;">
        <h1 style="justify-content: center;">Sending Started!</h1>
        <p>The campaign has been queued for sending.</p>
        <p style="margin-bottom: 2rem; font-size: 0.9rem;">Note: In this demo version, you need to run the CLI 'send' command to actually process the queue.</p>

        <div style="display: flex; gap: 1rem; justify-content: center;">
            <a href="/campaign/{campaign_id}" class="btn btn-primary">Track Progress</a>
            <a href="/" class="btn btn-outline">Dashboard</a>
        </div>
    </div>
</body>
</html>
    """


@app.route("/campaign/<int:campaign_id>/export")
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


def run_web_server(host: str = "127.0.0.1", port: int = 5000, debug: bool = False):
    """Run the web server."""
    print(f"Starting web server at http://{host}:{port}")
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    run_web_server(debug=True)
