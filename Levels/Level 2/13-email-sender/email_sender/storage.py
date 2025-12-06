"""
Storage module for mail merge campaigns.

This module provides SQLite-based storage for campaigns, recipients,
and send status tracking.
"""

import sqlite3
import logging
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class CampaignStorage:
    """SQLite storage for mail merge campaigns."""

    def __init__(self, db_path: str = "mail_merge.db"):
        """
        Initialize the storage.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self._init_db()

    def _init_db(self) -> None:
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Campaigns table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS campaigns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    body_template TEXT,
                    html_template TEXT,
                    template_file_path TEXT,
                    source_type TEXT NOT NULL,
                    source_path TEXT,
                    sheet_id TEXT,
                    sheet_range TEXT,
                    signature_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_synced_at TIMESTAMP,
                    status TEXT DEFAULT 'draft',
                    FOREIGN KEY (signature_id) REFERENCES email_signatures(id)
                )
            """)

            # Recipients table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS recipients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    campaign_id INTEGER NOT NULL,
                    email TEXT NOT NULL,
                    personalization_data TEXT,
                    status TEXT DEFAULT 'queued',
                    error_message TEXT,
                    sent_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    opened_at TIMESTAMP,
                    open_count INTEGER DEFAULT 0,
                    first_opened_at TIMESTAMP,
                    FOREIGN KEY (campaign_id) REFERENCES campaigns(id),
                    UNIQUE(campaign_id, email)
                )
            """)

            # Email clicks table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS email_clicks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    recipient_id INTEGER NOT NULL,
                    campaign_id INTEGER NOT NULL,
                    original_url TEXT NOT NULL,
                    clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (recipient_id) REFERENCES recipients(id),
                    FOREIGN KEY (campaign_id) REFERENCES campaigns(id)
                )
            """)

            # Email signatures table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS email_signatures (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    content TEXT NOT NULL,
                    html_content TEXT,
                    is_default INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Campaign attachments table (for images and files)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS campaign_attachments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    campaign_id INTEGER NOT NULL,
                    filename TEXT NOT NULL,
                    original_filename TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    mime_type TEXT,
                    file_size INTEGER,
                    is_inline INTEGER DEFAULT 0,
                    content_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (campaign_id) REFERENCES campaigns(id)
                )
            """)

            # Migrate existing databases: add missing columns if they don't exist
            # Check if recipients table exists and has the tracking columns
            cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='recipients'
            """)
            if cursor.fetchone():
                # Table exists, check for missing columns
                cursor.execute("PRAGMA table_info(recipients)")
                columns = [row[1] for row in cursor.fetchall()]

                if "opened_at" not in columns:
                    logger.info(
                        "Migrating database: adding opened_at, open_count, first_opened_at columns"
                    )
                    cursor.execute(
                        "ALTER TABLE recipients ADD COLUMN opened_at TIMESTAMP"
                    )
                    cursor.execute(
                        "ALTER TABLE recipients ADD COLUMN open_count INTEGER DEFAULT 0"
                    )
                    cursor.execute(
                        "ALTER TABLE recipients ADD COLUMN first_opened_at TIMESTAMP"
                    )

            # Create indexes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_recipients_campaign
                ON recipients(campaign_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_recipients_status
                ON recipients(status)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_recipients_email
                ON recipients(email)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_recipients_opened
                ON recipients(opened_at)
            """)

            # Email clicks indexes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_clicks_recipient
                ON email_clicks(recipient_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_clicks_campaign
                ON email_clicks(campaign_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_clicks_clicked_at
                ON email_clicks(clicked_at)
            """)

            conn.commit()
            logger.info(f"Database initialized at {self.db_path}")

    def create_campaign(
        self,
        name: str,
        subject: str,
        body_template: Optional[str] = None,
        html_template: Optional[str] = None,
        template_file_path: Optional[str] = None,
        source_type: str = "csv",
        source_path: Optional[str] = None,
        sheet_id: Optional[str] = None,
        sheet_range: Optional[str] = None,
        signature_id: Optional[int] = None,
    ) -> int:
        """
        Create a new campaign.

        Returns:
            Campaign ID
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO campaigns (
                    name, subject, body_template, html_template,
                    template_file_path, source_type, source_path,
                    sheet_id, sheet_range, signature_id, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    name,
                    subject,
                    body_template,
                    html_template,
                    template_file_path,
                    source_type,
                    source_path,
                    sheet_id,
                    sheet_range,
                    signature_id,
                    datetime.now().isoformat(),
                ),
            )
            campaign_id = cursor.lastrowid
            conn.commit()
            logger.info(f"Created campaign {campaign_id}: {name}")
            return campaign_id

    def get_campaign(self, campaign_id: int) -> Optional[Dict[str, Any]]:
        """Get campaign by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM campaigns WHERE id = ?", (campaign_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None

    def list_campaigns(self) -> List[Dict[str, Any]]:
        """List all campaigns."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.*,
                       COUNT(r.id) as recipient_count,
                       SUM(CASE WHEN r.status = 'sent' THEN 1 ELSE 0 END) as sent_count,
                       SUM(CASE WHEN r.status = 'failed' THEN 1 ELSE 0 END) as failed_count
                FROM campaigns c
                LEFT JOIN recipients r ON c.id = r.campaign_id
                GROUP BY c.id
                ORDER BY c.created_at DESC
            """)
            return [dict(row) for row in cursor.fetchall()]

    def add_recipients(self, campaign_id: int, recipients: List[Dict[str, Any]]) -> int:
        """
        Add recipients to a campaign.

        Args:
            campaign_id: Campaign ID
            recipients: List of recipient dicts with 'email' and other fields

        Returns:
            Number of recipients added
        """
        added = 0
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for recipient in recipients:
                email = recipient.get("email", "").strip()
                if not email:
                    continue

                # Store personalization data as JSON
                personalization = {k: v for k, v in recipient.items() if k != "email"}
                personalization_json = json.dumps(personalization)

                try:
                    cursor.execute(
                        """
                        INSERT OR REPLACE INTO recipients
                        (campaign_id, email, personalization_data, status, created_at)
                        VALUES (?, ?, ?, 'queued', ?)
                    """,
                        (
                            campaign_id,
                            email,
                            personalization_json,
                            datetime.now().isoformat(),
                        ),
                    )
                    added += 1
                except sqlite3.Error as e:
                    logger.warning(f"Error adding recipient {email}: {e}")

            conn.commit()
            logger.info(f"Added {added} recipients to campaign {campaign_id}")
            return added

    def get_recipients(
        self, campaign_id: int, status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get recipients for a campaign.

        Args:
            campaign_id: Campaign ID
            status: Filter by status (queued, sent, failed)

        Returns:
            List of recipient dicts
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            if status:
                cursor.execute(
                    """
                    SELECT * FROM recipients
                    WHERE campaign_id = ? AND status = ?
                    ORDER BY created_at
                """,
                    (campaign_id, status),
                )
            else:
                cursor.execute(
                    """
                    SELECT * FROM recipients
                    WHERE campaign_id = ?
                    ORDER BY created_at
                """,
                    (campaign_id,),
                )

            results = []
            for row in cursor.fetchall():
                recipient = dict(row)
                # Parse personalization data
                if recipient.get("personalization_data"):
                    try:
                        recipient["personalization_data"] = json.loads(
                            recipient["personalization_data"]
                        )
                    except json.JSONDecodeError:
                        recipient["personalization_data"] = {}
                else:
                    recipient["personalization_data"] = {}
                results.append(recipient)

            return results

    def update_recipient_status(
        self, recipient_id: int, status: str, error_message: Optional[str] = None
    ) -> None:
        """Update recipient send status."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            sent_at = datetime.now().isoformat() if status == "sent" else None
            cursor.execute(
                """
                UPDATE recipients
                SET status = ?, error_message = ?, sent_at = ?
                WHERE id = ?
            """,
                (status, error_message, sent_at, recipient_id),
            )
            conn.commit()

    def update_campaign_sync_time(self, campaign_id: int) -> None:
        """Update last sync time for a campaign."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE campaigns
                SET last_synced_at = ?, updated_at = ?
                WHERE id = ?
            """,
                (datetime.now().isoformat(), datetime.now().isoformat(), campaign_id),
            )
            conn.commit()

    def get_campaign_stats(self, campaign_id: int) -> Dict[str, Any]:
        """Get statistics for a campaign including open/click metrics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Basic stats
            cursor.execute(
                """
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'queued' THEN 1 ELSE 0 END) as queued,
                    SUM(CASE WHEN status = 'sent' THEN 1 ELSE 0 END) as sent,
                    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
                    SUM(CASE WHEN opened_at IS NOT NULL THEN 1 ELSE 0 END) as opened_count
                FROM recipients
                WHERE campaign_id = ?
            """,
                (campaign_id,),
            )
            row = cursor.fetchone()

            total = row[0] or 0
            sent = row[2] or 0
            opened_count = row[4] or 0

            # Get click count
            cursor.execute(
                """
                SELECT COUNT(*) FROM email_clicks
                WHERE campaign_id = ?
            """,
                (campaign_id,),
            )
            click_count = cursor.fetchone()[0] or 0

            # Calculate rates
            open_rate = round((opened_count / sent * 100), 1) if sent > 0 else 0.0
            click_rate = round((click_count / sent * 100), 1) if sent > 0 else 0.0

            return {
                "total": total,
                "queued": row[1] or 0,
                "sent": sent,
                "failed": row[3] or 0,
                "opened_count": opened_count,
                "click_count": click_count,
                "open_rate": open_rate,
                "click_rate": click_rate,
            }

    def export_campaign_results(self, campaign_id: int) -> List[Dict[str, Any]]:
        """Export campaign results for CSV export."""
        recipients = self.get_recipients(campaign_id)
        results = []
        for r in recipients:
            # Get click count for this recipient
            clicks = self.get_recipient_clicks(r["id"])
            click_count = len(clicks)

            results.append(
                {
                    "email": r["email"],
                    "status": r["status"],
                    "error_message": r.get("error_message", ""),
                    "sent_at": r.get("sent_at", ""),
                    "opened": "Yes" if r.get("opened_at") else "No",
                    "open_count": r.get("open_count", 0),
                    "first_opened_at": r.get("first_opened_at", ""),
                    "click_count": click_count,
                    **r.get("personalization_data", {}),
                }
            )
        return results

    def record_email_open(self, recipient_id: int) -> None:
        """Record an email open event."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            now = datetime.now().isoformat()

            # Update open count and timestamps
            cursor.execute(
                """
                UPDATE recipients
                SET open_count = open_count + 1,
                    opened_at = ?,
                    first_opened_at = COALESCE(first_opened_at, ?)
                WHERE id = ?
            """,
                (now, now, recipient_id),
            )
            conn.commit()
            logger.info(f"Recorded email open for recipient {recipient_id}")

    def record_email_click(
        self, recipient_id: int, campaign_id: int, original_url: str
    ) -> None:
        """Record a link click event."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO email_clicks (recipient_id, campaign_id, original_url)
                VALUES (?, ?, ?)
            """,
                (recipient_id, campaign_id, original_url),
            )
            conn.commit()
            logger.info(f"Recorded click for recipient {recipient_id}: {original_url}")

    def get_recipient_clicks(self, recipient_id: int) -> List[Dict[str, Any]]:
        """Get all clicks for a recipient."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM email_clicks
                WHERE recipient_id = ?
                ORDER BY clicked_at DESC
            """,
                (recipient_id,),
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_recipient_by_id(self, recipient_id: int) -> Optional[Dict[str, Any]]:
        """Get a recipient by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM recipients WHERE id = ?", (recipient_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None

    # =========================================================================
    # Campaign Management
    # =========================================================================

    def delete_campaign(self, campaign_id: int) -> bool:
        """
        Delete a campaign and all its recipients, clicks, and attachments.

        Returns:
            True if campaign was deleted, False if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Check if campaign exists
            cursor.execute("SELECT id FROM campaigns WHERE id = ?", (campaign_id,))
            if not cursor.fetchone():
                return False

            # Delete clicks first (foreign key constraint)
            cursor.execute(
                "DELETE FROM email_clicks WHERE campaign_id = ?", (campaign_id,)
            )

            # Delete recipients
            cursor.execute(
                "DELETE FROM recipients WHERE campaign_id = ?", (campaign_id,)
            )

            # Delete attachments
            cursor.execute(
                "DELETE FROM campaign_attachments WHERE campaign_id = ?", (campaign_id,)
            )

            # Delete campaign
            cursor.execute("DELETE FROM campaigns WHERE id = ?", (campaign_id,))

            conn.commit()
            logger.info(f"Deleted campaign {campaign_id} and all related data")
            return True

    # =========================================================================
    # Recipient Management
    # =========================================================================

    def delete_recipient(self, recipient_id: int) -> bool:
        """
        Delete a single recipient and their clicks.

        Returns:
            True if recipient was deleted, False if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Check if recipient exists
            cursor.execute("SELECT id FROM recipients WHERE id = ?", (recipient_id,))
            if not cursor.fetchone():
                return False

            # Delete clicks first
            cursor.execute(
                "DELETE FROM email_clicks WHERE recipient_id = ?", (recipient_id,)
            )

            # Delete recipient
            cursor.execute("DELETE FROM recipients WHERE id = ?", (recipient_id,))

            conn.commit()
            logger.info(f"Deleted recipient {recipient_id}")
            return True

    def update_recipient(
        self,
        recipient_id: int,
        email: Optional[str] = None,
        personalization_data: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Update a recipient's email or personalization data.

        Returns:
            True if recipient was updated, False if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Check if recipient exists
            cursor.execute("SELECT id FROM recipients WHERE id = ?", (recipient_id,))
            if not cursor.fetchone():
                return False

            updates = []
            params = []

            if email is not None:
                updates.append("email = ?")
                params.append(email)

            if personalization_data is not None:
                updates.append("personalization_data = ?")
                params.append(json.dumps(personalization_data))

            if not updates:
                return True  # Nothing to update

            params.append(recipient_id)
            cursor.execute(
                f"UPDATE recipients SET {', '.join(updates)} WHERE id = ?", params
            )
            conn.commit()
            logger.info(f"Updated recipient {recipient_id}")
            return True

    def retry_recipient(self, recipient_id: int) -> bool:
        """
        Reset a failed recipient to queued status for retry.

        Returns:
            True if recipient was reset, False if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE recipients
                SET status = 'queued', error_message = NULL, sent_at = NULL
                WHERE id = ? AND status = 'failed'
                """,
                (recipient_id,),
            )
            conn.commit()
            if cursor.rowcount > 0:
                logger.info(f"Reset recipient {recipient_id} to queued status")
                return True
            return False

    def retry_all_failed(self, campaign_id: int) -> int:
        """
        Reset all failed recipients in a campaign to queued status.

        Returns:
            Number of recipients reset
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE recipients
                SET status = 'queued', error_message = NULL, sent_at = NULL
                WHERE campaign_id = ? AND status = 'failed'
                """,
                (campaign_id,),
            )
            conn.commit()
            count = cursor.rowcount
            logger.info(f"Reset {count} failed recipients in campaign {campaign_id}")
            return count

    # =========================================================================
    # Email Signature Profiles
    # =========================================================================

    def create_signature(
        self,
        name: str,
        content: str,
        html_content: Optional[str] = None,
        is_default: bool = False,
    ) -> int:
        """
        Create a new email signature profile.

        Args:
            name: Unique name for the signature
            content: Plain text signature
            html_content: HTML version of signature (optional)
            is_default: Whether this is the default signature

        Returns:
            Signature ID
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # If this is default, unset any existing default
            if is_default:
                cursor.execute("UPDATE email_signatures SET is_default = 0")

            cursor.execute(
                """
                INSERT INTO email_signatures (name, content, html_content, is_default, updated_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    name,
                    content,
                    html_content,
                    1 if is_default else 0,
                    datetime.now().isoformat(),
                ),
            )
            signature_id = cursor.lastrowid
            conn.commit()
            logger.info(f"Created signature {signature_id}: {name}")
            return signature_id

    def get_signature(self, signature_id: int) -> Optional[Dict[str, Any]]:
        """Get a signature by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM email_signatures WHERE id = ?", (signature_id,)
            )
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None

    def get_signature_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a signature by name."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM email_signatures WHERE name = ?", (name,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None

    def list_signatures(self) -> List[Dict[str, Any]]:
        """List all signature profiles."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM email_signatures ORDER BY is_default DESC, name ASC"
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_default_signature(self) -> Optional[Dict[str, Any]]:
        """Get the default signature profile."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM email_signatures WHERE is_default = 1")
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None

    def update_signature(
        self,
        signature_id: int,
        name: Optional[str] = None,
        content: Optional[str] = None,
        html_content: Optional[str] = None,
        is_default: Optional[bool] = None,
    ) -> bool:
        """
        Update a signature profile.

        Returns:
            True if signature was updated, False if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Check if signature exists
            cursor.execute(
                "SELECT id FROM email_signatures WHERE id = ?", (signature_id,)
            )
            if not cursor.fetchone():
                return False

            # If setting as default, unset any existing default
            if is_default:
                cursor.execute("UPDATE email_signatures SET is_default = 0")

            updates = ["updated_at = ?"]
            params = [datetime.now().isoformat()]

            if name is not None:
                updates.append("name = ?")
                params.append(name)

            if content is not None:
                updates.append("content = ?")
                params.append(content)

            if html_content is not None:
                updates.append("html_content = ?")
                params.append(html_content)

            if is_default is not None:
                updates.append("is_default = ?")
                params.append(1 if is_default else 0)

            params.append(signature_id)
            cursor.execute(
                f"UPDATE email_signatures SET {', '.join(updates)} WHERE id = ?", params
            )
            conn.commit()
            logger.info(f"Updated signature {signature_id}")
            return True

    def delete_signature(self, signature_id: int) -> bool:
        """
        Delete a signature profile.

        Returns:
            True if signature was deleted, False if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM email_signatures WHERE id = ?", (signature_id,))
            conn.commit()
            if cursor.rowcount > 0:
                logger.info(f"Deleted signature {signature_id}")
                return True
            return False

    # =========================================================================
    # Campaign Attachments (Images & Files)
    # =========================================================================

    def add_attachment(
        self,
        campaign_id: int,
        filename: str,
        original_filename: str,
        file_path: str,
        mime_type: Optional[str] = None,
        file_size: Optional[int] = None,
        is_inline: bool = False,
        content_id: Optional[str] = None,
    ) -> int:
        """
        Add an attachment to a campaign.

        Args:
            campaign_id: Campaign to attach to
            filename: Stored filename (UUID-based)
            original_filename: Original uploaded filename
            file_path: Path where file is stored
            mime_type: MIME type of the file
            file_size: Size in bytes
            is_inline: Whether this is an inline image (for HTML emails)
            content_id: Content-ID for inline images (e.g., "image001")

        Returns:
            Attachment ID
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO campaign_attachments (
                    campaign_id, filename, original_filename, file_path,
                    mime_type, file_size, is_inline, content_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    campaign_id,
                    filename,
                    original_filename,
                    file_path,
                    mime_type,
                    file_size,
                    1 if is_inline else 0,
                    content_id,
                ),
            )
            attachment_id = cursor.lastrowid
            conn.commit()
            logger.info(f"Added attachment {attachment_id} to campaign {campaign_id}")
            return attachment_id

    def get_attachment(self, attachment_id: int) -> Optional[Dict[str, Any]]:
        """Get an attachment by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM campaign_attachments WHERE id = ?", (attachment_id,)
            )
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None

    def get_campaign_attachments(self, campaign_id: int) -> List[Dict[str, Any]]:
        """Get all attachments for a campaign."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM campaign_attachments
                WHERE campaign_id = ?
                ORDER BY created_at ASC
                """,
                (campaign_id,),
            )
            return [dict(row) for row in cursor.fetchall()]

    def delete_attachment(self, attachment_id: int) -> Optional[str]:
        """
        Delete an attachment record.

        Returns:
            File path of deleted attachment (for file cleanup), or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Get file path before deleting
            cursor.execute(
                "SELECT file_path FROM campaign_attachments WHERE id = ?",
                (attachment_id,),
            )
            row = cursor.fetchone()
            if not row:
                return None

            file_path = row["file_path"]

            cursor.execute(
                "DELETE FROM campaign_attachments WHERE id = ?", (attachment_id,)
            )
            conn.commit()
            logger.info(f"Deleted attachment {attachment_id}")
            return file_path

    def delete_campaign_attachments(self, campaign_id: int) -> List[str]:
        """
        Delete all attachments for a campaign.

        Returns:
            List of file paths for cleanup
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Get all file paths before deleting
            cursor.execute(
                "SELECT file_path FROM campaign_attachments WHERE campaign_id = ?",
                (campaign_id,),
            )
            file_paths = [row["file_path"] for row in cursor.fetchall()]

            cursor.execute(
                "DELETE FROM campaign_attachments WHERE campaign_id = ?",
                (campaign_id,),
            )
            conn.commit()
            logger.info(
                f"Deleted {len(file_paths)} attachments from campaign {campaign_id}"
            )
            return file_paths
