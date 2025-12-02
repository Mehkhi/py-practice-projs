"""
Core email sending functionality.

This module provides the main EmailSender class that handles SMTP connections,
email composition, and sending operations.
"""

import smtplib
import ssl
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional, Dict, Any
from pathlib import Path
import time

from .utils import validate_email, load_recipients_from_csv

logger = logging.getLogger(__name__)


class EmailSender:
    """
    A professional email sender with support for attachments, HTML templates,
    and batch processing.
    """

    def __init__(
        self,
        smtp_server: str,
        smtp_port: int,
        username: str,
        password: str,
        use_tls: bool = True
    ):
        """
        Initialize the EmailSender.

        Args:
            smtp_server: SMTP server hostname
            smtp_port: SMTP server port
            username: SMTP username/email
            password: SMTP password/app password
            use_tls: Whether to use TLS encryption
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.use_tls = use_tls
        self._connection: Optional[smtplib.SMTP] = None

    def connect(self) -> None:
        """Establish SMTP connection."""
        try:
            logger.info(f"Connecting to SMTP server {self.smtp_server}:{self.smtp_port}")
            self._connection = smtplib.SMTP(self.smtp_server, self.smtp_port)

            if self.use_tls:
                context = ssl.create_default_context()
                self._connection.starttls(context=context)
                logger.info("TLS encryption enabled")

            self._connection.login(self.username, self.password)
            logger.info("Successfully connected and authenticated")

        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP authentication failed: {e}")
            raise EmailError(f"Authentication failed: {e}")
        except smtplib.SMTPConnectError as e:
            logger.error(f"SMTP connection failed: {e}")
            raise EmailError(f"Connection failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during connection: {e}")
            raise EmailError(f"Connection error: {e}")

    def disconnect(self) -> None:
        """Close SMTP connection."""
        if self._connection:
            try:
                self._connection.quit()
                logger.info("SMTP connection closed")
            except Exception as e:
                logger.warning(f"Error closing connection: {e}")
            finally:
                self._connection = None

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()

    def send_email(
        self,
        to_emails: List[str],
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        attachments: Optional[List[str]] = None,
        from_email: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send an email to multiple recipients.

        Args:
            to_emails: List of recipient email addresses
            subject: Email subject
            body: Plain text body
            html_body: HTML body (optional)
            attachments: List of file paths to attach
            from_email: Sender email (defaults to username)

        Returns:
            Dictionary with sending results
        """
        if not self._connection:
            raise EmailError("Not connected to SMTP server. Call connect() first.")

        # Validate email addresses
        invalid_emails = [email for email in to_emails if not validate_email(email)]
        if invalid_emails:
            raise EmailError(f"Invalid email addresses: {invalid_emails}")

        from_email = from_email or self.username

        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = from_email
        msg['To'] = ', '.join(to_emails)
        msg['Subject'] = subject

        # Add text body
        text_part = MIMEText(body, 'plain', 'utf-8')
        msg.attach(text_part)

        # Add HTML body if provided
        if html_body:
            html_part = MIMEText(html_body, 'html', 'utf-8')
            msg.attach(html_part)

        # Add attachments
        if attachments:
            for attachment_path in attachments:
                self._add_attachment(msg, attachment_path)

        # Send email
        try:
            logger.info(f"Sending email to {len(to_emails)} recipients")
            send_result = self._connection.send_message(msg)
            refused = send_result if isinstance(send_result, dict) else {}
            if refused:
                logger.error(f"SMTP reported refused recipients: {refused}")
                raise EmailError(f"Recipients refused: {refused}")
            logger.info("Email sent successfully")

            return {
                'success': True,
                'recipients': to_emails,
                'attachments_count': len(attachments) if attachments else 0
            }

        except smtplib.SMTPRecipientsRefused as e:
            logger.error(f"Recipients refused: {e}")
            raise EmailError(f"Recipients refused: {e}")
        except smtplib.SMTPDataError as e:
            logger.error(f"SMTP data error: {e}")
            raise EmailError(f"Data error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error sending email: {e}")
            raise EmailError(f"Send error: {e}")

    def _add_attachment(self, msg: MIMEMultipart, file_path: str) -> None:
        """Add an attachment to the email message."""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"Attachment file not found: {file_path}")

            with open(file_path, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())

            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {file_path.name}'
            )
            msg.attach(part)
            logger.info(f"Added attachment: {file_path.name}")

        except Exception as e:
            logger.error(f"Error adding attachment {file_path}: {e}")
            raise EmailError(f"Attachment error: {e}")

    def send_batch(
        self,
        recipients_file: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        attachments: Optional[List[str]] = None,
        batch_size: int = 10,
        delay_seconds: float = 1.0
    ) -> Dict[str, Any]:
        """
        Send emails in batches with rate limiting.

        Args:
            recipients_file: CSV file with recipient data
            subject: Email subject
            body: Plain text body
            html_body: HTML body (optional)
            attachments: List of file paths to attach
            batch_size: Number of emails per batch
            delay_seconds: Delay between batches

        Returns:
            Dictionary with batch sending results
        """
        try:
            recipients_data = load_recipients_from_csv(recipients_file)
            total_recipients = len(recipients_data)

            logger.info(f"Starting batch send to {total_recipients} recipients")

            results = {
                'total_recipients': total_recipients,
                'batches_sent': 0,
                'successful_emails': 0,
                'failed_emails': 0,
                'errors': []
            }

            for i in range(0, total_recipients, batch_size):
                batch = recipients_data[i:i + batch_size]
                batch_emails = [row.get('email', '') for row in batch if row.get('email')]

                if not batch_emails:
                    continue

                try:
                    result = self.send_email(
                        to_emails=batch_emails,
                        subject=subject,
                        body=body,
                        html_body=html_body,
                        attachments=attachments
                    )

                    results['batches_sent'] += 1
                    results['successful_emails'] += len(batch_emails)
                    logger.info(f"Batch {results['batches_sent']} sent successfully")

                except Exception as e:
                    results['failed_emails'] += len(batch_emails)
                    results['errors'].append(f"Batch {results['batches_sent'] + 1}: {str(e)}")
                    logger.error(f"Batch {results['batches_sent'] + 1} failed: {e}")

                # Rate limiting delay
                if i + batch_size < total_recipients:
                    time.sleep(delay_seconds)

            logger.info(f"Batch sending completed. Success: {results['successful_emails']}, Failed: {results['failed_emails']}")
            return results

        except Exception as e:
            logger.error(f"Batch sending failed: {e}")
            raise EmailError(f"Batch sending error: {e}")


class EmailError(Exception):
    """Custom exception for email sending errors."""
    pass
