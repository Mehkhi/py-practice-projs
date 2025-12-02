"""
Command-line interface for the email sender.

This module provides the main CLI entry point with argument parsing
and command execution.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import List, Optional

from .core import EmailSender, EmailError
from .utils import validate_email, load_recipients_from_csv, create_sample_csv


def setup_logging(verbose: bool = False) -> None:
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
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

    with open(sample_template, 'w', encoding='utf-8') as f:
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
    use_tls: bool = True
) -> None:
    """Send a single email."""
    try:
        with EmailSender(smtp_server, smtp_port, username, password, use_tls) as sender:
            html_body = None
            if html_file and Path(html_file).exists():
                with open(html_file, 'r', encoding='utf-8') as f:
                    html_body = f.read()

            result = sender.send_email(
                to_emails=to_emails,
                subject=subject,
                body=body,
                html_body=html_body,
                attachments=attachments
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
    use_tls: bool = True
) -> None:
    """Send batch emails."""
    try:
        with EmailSender(smtp_server, smtp_port, username, password, use_tls) as sender:
            html_body = None
            if html_file and Path(html_file).exists():
                with open(html_file, 'r', encoding='utf-8') as f:
                    html_body = f.read()

            result = sender.send_batch(
                recipients_file=recipients_file,
                subject=subject,
                body=body,
                html_body=html_body,
                attachments=attachments,
                batch_size=batch_size,
                delay_seconds=delay_seconds
            )

            print(f"✅ Batch sending completed!")
            print(f"   Total recipients: {result['total_recipients']}")
            print(f"   Successful emails: {result['successful_emails']}")
            print(f"   Failed emails: {result['failed_emails']}")
            print(f"   Batches sent: {result['batches_sent']}")

            if result['errors']:
                print(f"   Errors: {len(result['errors'])}")
                for error in result['errors'][:5]:  # Show first 5 errors
                    print(f"     - {error}")
                if len(result['errors']) > 5:
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
        """
    )

    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose logging')
    parser.add_argument('--version', action='version', version='Email Sender 1.0.0')

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Send command
    send_parser = subparsers.add_parser('send', help='Send a single email')
    send_parser.add_argument('--smtp', required=True, help='SMTP server hostname')
    send_parser.add_argument('--port', type=int, required=True, help='SMTP server port')
    send_parser.add_argument('--user', required=True, help='SMTP username/email')
    send_parser.add_argument('--pass', dest='password', required=True, help='SMTP password')
    send_parser.add_argument('--to', nargs='+', required=True, help='Recipient email addresses')
    send_parser.add_argument('--subject', required=True, help='Email subject')
    send_parser.add_argument('--body', required=True, help='Email body text')
    send_parser.add_argument('--html', help='HTML template file')
    send_parser.add_argument('--attach', nargs='*', help='Attachment file paths')
    send_parser.add_argument('--no-tls', action='store_true', help='Disable TLS encryption')

    # Batch command
    batch_parser = subparsers.add_parser('batch', help='Send batch emails from CSV')
    batch_parser.add_argument('--smtp', required=True, help='SMTP server hostname')
    batch_parser.add_argument('--port', type=int, required=True, help='SMTP server port')
    batch_parser.add_argument('--user', required=True, help='SMTP username/email')
    batch_parser.add_argument('--pass', dest='password', required=True, help='SMTP password')
    batch_parser.add_argument('--recipients', required=True, help='CSV file with recipients')
    batch_parser.add_argument('--subject', required=True, help='Email subject')
    batch_parser.add_argument('--body', required=True, help='Email body text')
    batch_parser.add_argument('--html', help='HTML template file')
    batch_parser.add_argument('--attach', nargs='*', help='Attachment file paths')
    batch_parser.add_argument('--batch-size', type=int, default=10, help='Emails per batch')
    batch_parser.add_argument('--delay', type=float, default=1.0, help='Delay between batches (seconds)')
    batch_parser.add_argument('--no-tls', action='store_true', help='Disable TLS encryption')

    # Samples command
    subparsers.add_parser('samples', help='Create sample files')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    setup_logging(args.verbose)

    if args.command == 'samples':
        create_sample_files()
        return

    # Validate email addresses for send command
    if args.command == 'send':
        invalid_emails = [email for email in args.to if not validate_email(email)]
        if invalid_emails:
            print(f"❌ Invalid email addresses: {invalid_emails}")
            sys.exit(1)

    # Execute commands
    if args.command == 'send':
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
            use_tls=not args.no_tls
        )

    elif args.command == 'batch':
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
            use_tls=not args.no_tls
        )


if __name__ == '__main__':
    main()
