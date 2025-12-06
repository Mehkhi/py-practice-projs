"""
Gmail API transport module.

This module provides Gmail API-based email sending functionality.
"""

import base64
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional, Dict, Any
from pathlib import Path
import os

from .auth_service import (
    is_google_api_available,
    require_google_api,
    GoogleAuthService,
    GMAIL_SEND_SCOPES,
)

# Re-export for backwards compatibility
GMAIL_AVAILABLE = is_google_api_available()

logger = logging.getLogger(__name__)


class GmailAPISender:
    """Gmail API-based email sender."""

    def __init__(
        self, credentials_path: Optional[str] = None, token_path: Optional[str] = None
    ):
        """
        Initialize Gmail API sender.

        Args:
            credentials_path: Path to OAuth2 credentials JSON file
            token_path: Path to store/load OAuth2 token
        """
        require_google_api()

        self._auth_service = GoogleAuthService(
            credentials_path=credentials_path,
            token_path=token_path,
        )
        self.service = self._auth_service.get_service(
            service_name="gmail",
            version="v1",
            scopes=GMAIL_SEND_SCOPES,
        )

    def _create_message(
        self,
        to_emails: List[str],
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        attachments: Optional[List[str]] = None,
        from_email: Optional[str] = None,
        campaign_id: Optional[int] = None,
        recipient_id: Optional[int] = None,
        enable_tracking: bool = True,
    ) -> Dict[str, str]:
        """
        Create a MIME message.

        Returns:
            Dictionary with 'raw' base64-encoded message
        """
        msg = MIMEMultipart("alternative")
        msg["To"] = ", ".join(to_emails)
        msg["Subject"] = subject

        if from_email:
            msg["From"] = from_email

        # Add text body
        text_part = MIMEText(body, "plain", "utf-8")
        msg.attach(text_part)

        # Add HTML body if provided
        if html_body:
            # Inject tracking if enabled and IDs provided
            if enable_tracking and campaign_id is not None and recipient_id is not None:
                from .tracking import add_tracking_to_email

                html_body = add_tracking_to_email(html_body, campaign_id, recipient_id)
            html_part = MIMEText(html_body, "html", "utf-8")
            msg.attach(html_part)

        # Add attachments
        if attachments:
            for attachment_path in attachments:
                self._add_attachment(msg, attachment_path)

        # Encode message
        raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")
        return {"raw": raw_message}

    def _add_attachment(self, msg: MIMEMultipart, file_path: str) -> None:
        """Add an attachment to the email message."""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"Attachment file not found: {file_path}")

            with open(file_path, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())

            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition", f"attachment; filename= {file_path.name}"
            )
            msg.attach(part)
            logger.info(f"Added attachment: {file_path.name}")

        except Exception as e:
            logger.error(f"Error adding attachment {file_path}: {e}")
            raise

    def send_email(
        self,
        to_emails: List[str],
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        attachments: Optional[List[str]] = None,
        from_email: Optional[str] = None,
        campaign_id: Optional[int] = None,
        recipient_id: Optional[int] = None,
        enable_tracking: bool = True,
    ) -> Dict[str, Any]:
        """
        Send an email via Gmail API.

        Args:
            to_emails: List of recipient email addresses
            subject: Email subject
            body: Plain text body
            html_body: HTML body (optional)
            attachments: List of file paths to attach
            from_email: Sender email (uses authenticated user if not provided)
            campaign_id: Campaign ID for tracking (optional)
            recipient_id: Recipient ID for tracking (optional)
            enable_tracking: Whether to inject tracking into HTML (default True)

        Returns:
            Dictionary with sending results
        """
        try:
            message = self._create_message(
                to_emails=to_emails,
                subject=subject,
                body=body,
                html_body=html_body,
                attachments=attachments,
                from_email=from_email,
                campaign_id=campaign_id,
                recipient_id=recipient_id,
                enable_tracking=enable_tracking,
            )

            sent_message = (
                self.service.users()
                .messages()
                .send(userId="me", body=message)
                .execute()
            )

            logger.info(
                f"Email sent successfully. Message ID: {sent_message.get('id')}"
            )
            return {
                "success": True,
                "message_id": sent_message.get("id"),
                "recipients": to_emails,
                "attachments_count": len(attachments) if attachments else 0,
            }

        except HttpError as e:
            error_details = e.error_details[0] if e.error_details else {}
            error_msg = error_details.get("message", str(e))
            logger.error(f"Gmail API error: {error_msg}")
            raise Exception(f"Gmail API error: {error_msg}")
        except Exception as e:
            logger.error(f"Unexpected error sending email: {e}")
            raise
