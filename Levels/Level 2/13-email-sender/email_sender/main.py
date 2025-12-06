"""
Command-line interface for the email sender.

This module provides the main CLI entry point with argument parsing
and command execution.
"""

import argparse
import logging
import sys
import time
from pathlib import Path
from typing import List, Optional

from .core import EmailSender, EmailError
from .utils import (
    validate_email,
    load_recipients_from_csv,
    create_sample_csv,
    format_email_template,
    load_template_file,
)
from .storage import CampaignStorage
from .gmail_api import GmailAPISender
from .sheets_sync import SheetsSync


def setup_logging(verbose: bool = False) -> None:
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def create_sample_files() -> None:
    """Create sample files for demonstration."""
    sample_csv = "sample_recipients.csv"
    sample_template = "sample_template.html"

    # Create sample CSV
    create_sample_csv(sample_csv)
    print(f"Created sample recipients file: {sample_csv}")

    # Create sample HTML template
    html_template = """<!DOCTYPE html>
<html>
<head>
    <title>Sample Email</title>
    <style>
        body { font-family: Arial, sans-serif; }
        .header { background-color: #f0f0f0; padding: 20px; }
        .content { padding: 20px; }
        .footer { background-color: #e0e0e0; padding: 10px; font-size: 12px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Hello {name}!</h1>
    </div>
    <div class="content">
        <p>This is a sample HTML email template.</p>
        <p>Your company: {company}</p>
        <p>Best regards,<br>Email Sender Team</p>
    </div>
    <div class="footer">
        <p>This is an automated message. Please do not reply.</p>
    </div>
</body>
</html>"""

    with open(sample_template, "w", encoding="utf-8") as f:
        f.write(html_template)

    print(f"Created sample HTML template: {sample_template}")


def send_single_email(
    smtp_server: str,
    smtp_port: int,
    username: str,
    password: str,
    to_emails: List[str],
    subject: str,
    body: str,
    html_file: Optional[str] = None,
    attachments: Optional[List[str]] = None,
    use_tls: bool = True,
) -> None:
    """Send a single email."""
    try:
        with EmailSender(smtp_server, smtp_port, username, password, use_tls) as sender:
            html_body = None
            if html_file and Path(html_file).exists():
                with open(html_file, "r", encoding="utf-8") as f:
                    html_body = f.read()

            result = sender.send_email(
                to_emails=to_emails,
                subject=subject,
                body=body,
                html_body=html_body,
                attachments=attachments,
            )

            print(f"✅ Email sent successfully!")
            print(f"   Recipients: {len(result['recipients'])}")
            print(f"   Attachments: {result['attachments_count']}")

    except EmailError as e:
        print(f"❌ Email sending failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


def send_batch_emails(
    smtp_server: str,
    smtp_port: int,
    username: str,
    password: str,
    recipients_file: str,
    subject: str,
    body: str,
    html_file: Optional[str] = None,
    attachments: Optional[List[str]] = None,
    batch_size: int = 10,
    delay_seconds: float = 1.0,
    use_tls: bool = True,
) -> None:
    """Send batch emails."""
    try:
        with EmailSender(smtp_server, smtp_port, username, password, use_tls) as sender:
            html_body = None
            if html_file and Path(html_file).exists():
                with open(html_file, "r", encoding="utf-8") as f:
                    html_body = f.read()

            result = sender.send_batch(
                recipients_file=recipients_file,
                subject=subject,
                body=body,
                html_body=html_body,
                attachments=attachments,
                batch_size=batch_size,
                delay_seconds=delay_seconds,
            )

            print(f"✅ Batch sending completed!")
            print(f"   Total recipients: {result['total_recipients']}")
            print(f"   Successful emails: {result['successful_emails']}")
            print(f"   Failed emails: {result['failed_emails']}")
            print(f"   Batches sent: {result['batches_sent']}")

            if result["errors"]:
                print(f"   Errors: {len(result['errors'])}")
                for error in result["errors"][:5]:  # Show first 5 errors
                    print(f"     - {error}")
                if len(result["errors"]) > 5:
                    print(f"     ... and {len(result['errors']) - 5} more errors")

    except EmailError as e:
        print(f"❌ Batch sending failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Professional email sender with attachments and batch processing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Send single email
  python -m email_sender send --smtp smtp.gmail.com --port 587 --user your@email.com --pass yourpassword --to recipient@example.com --subject "Test" --body "Hello World"

  # Send with HTML template and attachment
  python -m email_sender send --smtp smtp.gmail.com --port 587 --user your@email.com --pass yourpassword --to recipient@example.com --subject "Test" --body "Hello" --html template.html --attach file.pdf

  # Send batch emails from CSV
  python -m email_sender batch --smtp smtp.gmail.com --port 587 --user your@email.com --pass yourpassword --recipients recipients.csv --subject "Newsletter" --body "Monthly update"

  # Create sample files
  python -m email_sender samples
        """,
    )

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose logging"
    )
    parser.add_argument("--version", action="version", version="Email Sender 1.0.0")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Send command
    send_parser = subparsers.add_parser("send", help="Send a single email")
    send_parser.add_argument("--smtp", required=True, help="SMTP server hostname")
    send_parser.add_argument("--port", type=int, required=True, help="SMTP server port")
    send_parser.add_argument("--user", required=True, help="SMTP username/email")
    send_parser.add_argument(
        "--pass", dest="password", required=True, help="SMTP password"
    )
    send_parser.add_argument(
        "--to", nargs="+", required=True, help="Recipient email addresses"
    )
    send_parser.add_argument("--subject", required=True, help="Email subject")
    send_parser.add_argument("--body", required=True, help="Email body text")
    send_parser.add_argument("--html", help="HTML template file")
    send_parser.add_argument("--attach", nargs="*", help="Attachment file paths")
    send_parser.add_argument(
        "--no-tls", action="store_true", help="Disable TLS encryption"
    )

    # Batch command
    batch_parser = subparsers.add_parser("batch", help="Send batch emails from CSV")
    batch_parser.add_argument("--smtp", required=True, help="SMTP server hostname")
    batch_parser.add_argument(
        "--port", type=int, required=True, help="SMTP server port"
    )
    batch_parser.add_argument("--user", required=True, help="SMTP username/email")
    batch_parser.add_argument(
        "--pass", dest="password", required=True, help="SMTP password"
    )
    batch_parser.add_argument(
        "--recipients", required=True, help="CSV file with recipients"
    )
    batch_parser.add_argument("--subject", required=True, help="Email subject")
    batch_parser.add_argument("--body", required=True, help="Email body text")
    batch_parser.add_argument("--html", help="HTML template file")
    batch_parser.add_argument("--attach", nargs="*", help="Attachment file paths")
    batch_parser.add_argument(
        "--batch-size", type=int, default=10, help="Emails per batch"
    )
    batch_parser.add_argument(
        "--delay", type=float, default=1.0, help="Delay between batches (seconds)"
    )
    batch_parser.add_argument(
        "--no-tls", action="store_true", help="Disable TLS encryption"
    )

    # Samples command
    subparsers.add_parser("samples", help="Create sample files")

    # Web UI command
    web_parser = subparsers.add_parser("web", help="Start web UI server")
    web_parser.add_argument(
        "--host", default="127.0.0.1", help="Host to bind to (default: 127.0.0.1)"
    )
    web_parser.add_argument(
        "--port", type=int, default=9002, help="Port to bind to (default: 9002)"
    )
    web_parser.add_argument(
        "--no-debug",
        action="store_true",
        help="Disable debug mode (auto-reload is enabled by default)",
    )

    # Campaign commands
    campaign_parser = subparsers.add_parser(
        "campaign", help="Mail merge campaign management"
    )
    campaign_subparsers = campaign_parser.add_subparsers(
        dest="campaign_command", help="Campaign commands"
    )

    # Campaign create
    create_parser = campaign_subparsers.add_parser(
        "create", help="Create a new campaign"
    )
    create_parser.add_argument("--name", required=True, help="Campaign name")
    create_parser.add_argument("--subject", required=True, help="Email subject")
    create_parser.add_argument("--body", help="Plain text body template")
    create_parser.add_argument("--html", help="HTML template file")
    create_parser.add_argument(
        "--source-type",
        choices=["csv", "sheet"],
        default="csv",
        help="Data source type",
    )

    # Campaign import-csv
    import_parser = campaign_subparsers.add_parser(
        "import-csv", help="Import recipients from CSV"
    )
    import_parser.add_argument(
        "--campaign-id", type=int, required=True, help="Campaign ID"
    )
    import_parser.add_argument("--csv", required=True, help="CSV file path")

    # Campaign sync-sheet
    sync_parser = campaign_subparsers.add_parser(
        "sync-sheet", help="Sync recipients from Google Sheet"
    )
    sync_parser.add_argument(
        "--campaign-id", type=int, required=True, help="Campaign ID"
    )
    sync_parser.add_argument("--sheet-id", required=True, help="Google Sheet ID or URL")
    sync_parser.add_argument(
        "--range", default="A1:Z1000", help="Sheet range (default: A1:Z1000)"
    )
    sync_parser.add_argument("--credentials", help="Path to OAuth2 credentials JSON")

    # Campaign send
    send_campaign_parser = campaign_subparsers.add_parser(
        "send", help="Send campaign emails"
    )
    send_campaign_parser.add_argument(
        "--campaign-id", type=int, required=True, help="Campaign ID"
    )
    send_campaign_parser.add_argument(
        "--transport",
        choices=["gmail", "smtp"],
        default="gmail",
        help="Email transport",
    )
    send_campaign_parser.add_argument(
        "--smtp", help="SMTP server (if using SMTP transport)"
    )
    send_campaign_parser.add_argument(
        "--port", type=int, help="SMTP port (if using SMTP transport)"
    )
    send_campaign_parser.add_argument(
        "--user", help="SMTP username (if using SMTP transport)"
    )
    send_campaign_parser.add_argument(
        "--pass", dest="password", help="SMTP password (if using SMTP transport)"
    )
    send_campaign_parser.add_argument(
        "--batch-size", type=int, default=10, help="Emails per batch"
    )
    send_campaign_parser.add_argument(
        "--delay", type=float, default=1.0, help="Delay between batches (seconds)"
    )
    send_campaign_parser.add_argument(
        "--dry-run", action="store_true", help="Preview without sending"
    )

    # Campaign list
    campaign_subparsers.add_parser("list", help="List all campaigns")

    # Campaign status
    status_parser = campaign_subparsers.add_parser(
        "status", help="Show campaign status"
    )
    status_parser.add_argument(
        "--campaign-id", type=int, required=True, help="Campaign ID"
    )

    # Campaign export
    export_parser = campaign_subparsers.add_parser(
        "export", help="Export campaign results to CSV"
    )
    export_parser.add_argument(
        "--campaign-id", type=int, required=True, help="Campaign ID"
    )
    export_parser.add_argument("--output", required=True, help="Output CSV file path")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    setup_logging(args.verbose)

    if args.command == "samples":
        create_sample_files()
        return

    # Web UI command
    if args.command == "web":
        from .web import run_web_server

        # Debug mode is enabled by default, disable only if --no-debug is set
        debug_mode = not getattr(args, "no_debug", False)
        run_web_server(host=args.host, port=args.port, debug=debug_mode)
        return

    # Campaign commands
    if args.command == "campaign":
        handle_campaign_command(args)
        return

    # Validate email addresses for send command
    if args.command == "send":
        invalid_emails = [email for email in args.to if not validate_email(email)]
        if invalid_emails:
            print(f"❌ Invalid email addresses: {invalid_emails}")
            sys.exit(1)

    # Execute commands
    if args.command == "send":
        send_single_email(
            smtp_server=args.smtp,
            smtp_port=args.port,
            username=args.user,
            password=args.password,
            to_emails=args.to,
            subject=args.subject,
            body=args.body,
            html_file=args.html,
            attachments=args.attach,
            use_tls=not args.no_tls,
        )

    elif args.command == "batch":
        send_batch_emails(
            smtp_server=args.smtp,
            smtp_port=args.port,
            username=args.user,
            password=args.password,
            recipients_file=args.recipients,
            subject=args.subject,
            body=args.body,
            html_file=args.html,
            attachments=args.attach,
            batch_size=args.batch_size,
            delay_seconds=args.delay,
            use_tls=not args.no_tls,
        )


def handle_campaign_command(args) -> None:
    """Handle campaign subcommands."""
    storage = CampaignStorage()

    if args.campaign_command == "create":
        html_template = None
        template_file_path = None
        if args.html:
            template_file_path = args.html
            html_template = load_template_file(args.html)

        campaign_id = storage.create_campaign(
            name=args.name,
            subject=args.subject,
            body_template=args.body,
            html_template=html_template,
            template_file_path=template_file_path,
            source_type=args.source_type,
        )
        print(f"✅ Created campaign {campaign_id}: {args.name}")

    elif args.campaign_command == "import-csv":
        recipients = load_recipients_from_csv(args.csv)
        added = storage.add_recipients(args.campaign_id, recipients)
        print(f"✅ Imported {added} recipients to campaign {args.campaign_id}")

    elif args.campaign_command == "sync-sheet":
        try:
            sync = SheetsSync(credentials_path=args.credentials)
            sheet_id = sync.extract_sheet_id(args.sheet_id)
            added = sync.sync_to_campaign(
                storage, args.campaign_id, sheet_id, args.range
            )
            print(
                f"✅ Synced {added} recipients from Google Sheet to campaign {args.campaign_id}"
            )
        except Exception as e:
            print(f"❌ Error syncing sheet: {e}")
            sys.exit(1)

    elif args.campaign_command == "send":
        send_campaign_emails(
            storage=storage,
            campaign_id=args.campaign_id,
            transport=args.transport,
            smtp_server=args.smtp,
            smtp_port=args.port,
            smtp_user=args.user,
            smtp_password=args.password,
            batch_size=args.batch_size,
            delay_seconds=args.delay,
            dry_run=args.dry_run,
        )

    elif args.campaign_command == "list":
        campaigns = storage.list_campaigns()
        if not campaigns:
            print("No campaigns found.")
            return

        print("\n📋 Campaigns:")
        print("-" * 80)
        for camp in campaigns:
            print(f"ID: {camp['id']} | {camp['name']}")
            print(f"  Subject: {camp['subject']}")
            print(
                f"  Recipients: {camp.get('recipient_count', 0)} | "
                f"Sent: {camp.get('sent_count', 0)} | "
                f"Failed: {camp.get('failed_count', 0)}"
            )
            print(f"  Created: {camp['created_at']}")
            print()

    elif args.campaign_command == "status":
        campaign = storage.get_campaign(args.campaign_id)
        if not campaign:
            print(f"❌ Campaign {args.campaign_id} not found")
            sys.exit(1)

        stats = storage.get_campaign_stats(args.campaign_id)
        print(f"\n📊 Campaign: {campaign['name']}")
        print(f"Subject: {campaign['subject']}")
        print(f"\nStatus:")
        print(f"  Total: {stats['total']}")
        print(f"  Queued: {stats['queued']}")
        print(f"  Sent: {stats['sent']}")
        print(f"  Failed: {stats['failed']}")

    elif args.campaign_command == "export":
        import csv

        results = storage.export_campaign_results(args.campaign_id)
        if not results:
            print(f"❌ No results found for campaign {args.campaign_id}")
            sys.exit(1)

        with open(args.output, "w", newline="", encoding="utf-8") as f:
            if results:
                fieldnames = list(results[0].keys())
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)

        print(f"✅ Exported {len(results)} results to {args.output}")

    else:
        print("❌ Unknown campaign command")
        sys.exit(1)


def send_campaign_emails(
    storage: CampaignStorage,
    campaign_id: int,
    transport: str = "gmail",
    smtp_server: Optional[str] = None,
    smtp_port: Optional[int] = None,
    smtp_user: Optional[str] = None,
    smtp_password: Optional[str] = None,
    batch_size: int = 10,
    delay_seconds: float = 1.0,
    dry_run: bool = False,
) -> None:
    """Send emails for a campaign."""
    campaign = storage.get_campaign(campaign_id)
    if not campaign:
        print(f"❌ Campaign {campaign_id} not found")
        sys.exit(1)

    recipients = storage.get_recipients(campaign_id, status="queued")
    if not recipients:
        print(f"ℹ️  No queued recipients for campaign {campaign_id}")
        return

    print(f"📧 Sending campaign '{campaign['name']}' to {len(recipients)} recipients")

    # Load templates
    body_template = campaign.get("body_template") or ""
    html_template = campaign.get("html_template") or ""

    # Initialize sender
    if transport == "gmail":
        try:
            sender = GmailAPISender()
        except Exception as e:
            print(f"❌ Gmail API error: {e}")
            sys.exit(1)
    else:
        if not all([smtp_server, smtp_port, smtp_user, smtp_password]):
            print("❌ SMTP transport requires --smtp, --port, --user, and --pass")
            sys.exit(1)
        sender = EmailSender(smtp_server, smtp_port, smtp_user, smtp_password)
        sender.connect()

    try:
        successful = 0
        failed = 0

        for i in range(0, len(recipients), batch_size):
            batch = recipients[i : i + batch_size]

            for recipient in batch:
                email = recipient["email"]
                personalization = recipient.get("personalization_data", {})

                # Render templates
                subject = format_email_template(campaign["subject"], personalization)
                body = (
                    format_email_template(body_template, personalization)
                    if body_template
                    else ""
                )
                html_body = (
                    format_email_template(html_template, personalization)
                    if html_template
                    else None
                )

                if dry_run:
                    print(f"  [DRY RUN] Would send to {email}: {subject[:50]}...")
                    storage.update_recipient_status(recipient["id"], "sent")
                    successful += 1
                    continue

                try:
                    if transport == "gmail":
                        result = sender.send_email(
                            to_emails=[email],
                            subject=subject,
                            body=body,
                            html_body=html_body,
                            campaign_id=campaign_id,
                            recipient_id=recipient["id"],
                            enable_tracking=True,
                        )
                    else:
                        result = sender.send_email(
                            to_emails=[email],
                            subject=subject,
                            body=body,
                            html_body=html_body,
                            campaign_id=campaign_id,
                            recipient_id=recipient["id"],
                            enable_tracking=True,
                        )

                    storage.update_recipient_status(recipient["id"], "sent")
                    successful += 1
                    print(f"  ✅ Sent to {email}")

                except Exception as e:
                    storage.update_recipient_status(recipient["id"], "failed", str(e))
                    failed += 1
                    print(f"  ❌ Failed to send to {email}: {e}")

            # Rate limiting delay
            if i + batch_size < len(recipients):
                time.sleep(delay_seconds)

        print(f"\n✅ Campaign sending completed!")
        print(f"   Successful: {successful}")
        print(f"   Failed: {failed}")

    finally:
        if transport == "smtp":
            sender.disconnect()


if __name__ == "__main__":
    main()
