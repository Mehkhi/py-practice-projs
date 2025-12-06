"""
Tests for new storage features: signatures, attachments, recipient management, tracking.
"""

import pytest
import tempfile
import os
from pathlib import Path

from email_sender.storage import CampaignStorage


class TestSignatures:
    """Test email signature CRUD operations."""

    def setup_method(self):
        """Setup test fixtures."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()
        self.storage = CampaignStorage(db_path=self.temp_db.name)

    def teardown_method(self):
        """Cleanup test fixtures."""
        if Path(self.temp_db.name).exists():
            os.unlink(self.temp_db.name)

    def test_create_signature(self):
        """Test creating a signature."""
        sig_id = self.storage.create_signature(
            name="Professional",
            content="--\nJohn Doe\nSenior Developer",
            html_content="<p>--</p><p><strong>John Doe</strong></p>",
            is_default=True,
        )

        assert sig_id == 1
        sig = self.storage.get_signature(sig_id)
        assert sig["name"] == "Professional"
        assert sig["content"] == "--\nJohn Doe\nSenior Developer"
        assert sig["html_content"] == "<p>--</p><p><strong>John Doe</strong></p>"
        assert sig["is_default"] == 1

    def test_list_signatures(self):
        """Test listing signatures."""
        self.storage.create_signature(name="Sig1", content="Content 1")
        self.storage.create_signature(name="Sig2", content="Content 2", is_default=True)

        sigs = self.storage.list_signatures()
        assert len(sigs) == 2
        # Default should be first
        assert sigs[0]["name"] == "Sig2"
        assert sigs[0]["is_default"] == 1

    def test_get_default_signature(self):
        """Test getting default signature."""
        self.storage.create_signature(name="Sig1", content="Content 1")
        self.storage.create_signature(name="Sig2", content="Content 2", is_default=True)

        default = self.storage.get_default_signature()
        assert default is not None
        assert default["name"] == "Sig2"

    def test_update_signature(self):
        """Test updating a signature."""
        sig_id = self.storage.create_signature(name="Old Name", content="Old Content")

        result = self.storage.update_signature(
            sig_id, name="New Name", content="New Content"
        )
        assert result is True

        sig = self.storage.get_signature(sig_id)
        assert sig["name"] == "New Name"
        assert sig["content"] == "New Content"

    def test_delete_signature(self):
        """Test deleting a signature."""
        sig_id = self.storage.create_signature(name="ToDelete", content="Content")

        result = self.storage.delete_signature(sig_id)
        assert result is True

        sig = self.storage.get_signature(sig_id)
        assert sig is None

    def test_setting_new_default_unsets_old(self):
        """Test that setting a new default unsets the old one."""
        sig1_id = self.storage.create_signature(
            name="Sig1", content="C1", is_default=True
        )
        sig2_id = self.storage.create_signature(
            name="Sig2", content="C2", is_default=True
        )

        sig1 = self.storage.get_signature(sig1_id)
        sig2 = self.storage.get_signature(sig2_id)

        assert sig1["is_default"] == 0
        assert sig2["is_default"] == 1


class TestAttachments:
    """Test campaign attachment CRUD operations."""

    def setup_method(self):
        """Setup test fixtures."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()
        self.storage = CampaignStorage(db_path=self.temp_db.name)

        # Create a campaign for attachments
        self.campaign_id = self.storage.create_campaign(
            name="Test Campaign", subject="Test", source_type="csv"
        )

    def teardown_method(self):
        """Cleanup test fixtures."""
        if Path(self.temp_db.name).exists():
            os.unlink(self.temp_db.name)

    def test_add_attachment(self):
        """Test adding an attachment."""
        att_id = self.storage.add_attachment(
            campaign_id=self.campaign_id,
            filename="abc123.png",
            original_filename="logo.png",
            file_path="/tmp/uploads/abc123.png",
            mime_type="image/png",
            file_size=1024,
            is_inline=True,
            content_id="img001",
        )

        assert att_id == 1
        att = self.storage.get_attachment(att_id)
        assert att["filename"] == "abc123.png"
        assert att["original_filename"] == "logo.png"
        assert att["mime_type"] == "image/png"
        assert att["file_size"] == 1024
        assert att["is_inline"] == 1
        assert att["content_id"] == "img001"

    def test_get_campaign_attachments(self):
        """Test getting all attachments for a campaign."""
        self.storage.add_attachment(
            campaign_id=self.campaign_id,
            filename="file1.png",
            original_filename="image1.png",
            file_path="/tmp/file1.png",
        )
        self.storage.add_attachment(
            campaign_id=self.campaign_id,
            filename="file2.pdf",
            original_filename="doc.pdf",
            file_path="/tmp/file2.pdf",
        )

        attachments = self.storage.get_campaign_attachments(self.campaign_id)
        assert len(attachments) == 2

    def test_delete_attachment(self):
        """Test deleting an attachment."""
        att_id = self.storage.add_attachment(
            campaign_id=self.campaign_id,
            filename="todelete.png",
            original_filename="delete.png",
            file_path="/tmp/todelete.png",
        )

        file_path = self.storage.delete_attachment(att_id)
        assert file_path == "/tmp/todelete.png"

        att = self.storage.get_attachment(att_id)
        assert att is None

    def test_campaign_deletion_removes_attachments(self):
        """Test that deleting a campaign removes its attachments."""
        self.storage.add_attachment(
            campaign_id=self.campaign_id,
            filename="att1.png",
            original_filename="att1.png",
            file_path="/tmp/att1.png",
        )

        attachments_before = self.storage.get_campaign_attachments(self.campaign_id)
        assert len(attachments_before) == 1

        self.storage.delete_campaign(self.campaign_id)

        attachments_after = self.storage.get_campaign_attachments(self.campaign_id)
        assert len(attachments_after) == 0


class TestRecipientManagement:
    """Test recipient management operations."""

    def setup_method(self):
        """Setup test fixtures."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()
        self.storage = CampaignStorage(db_path=self.temp_db.name)

        # Create a campaign with recipients
        self.campaign_id = self.storage.create_campaign(
            name="Test Campaign", subject="Test", source_type="csv"
        )
        self.storage.add_recipients(
            self.campaign_id,
            [
                {"email": "user1@example.com", "name": "User 1"},
                {"email": "user2@example.com", "name": "User 2"},
            ],
        )

    def teardown_method(self):
        """Cleanup test fixtures."""
        if Path(self.temp_db.name).exists():
            os.unlink(self.temp_db.name)

    def test_get_recipient_by_id(self):
        """Test getting a recipient by ID."""
        recipients = self.storage.get_recipients(self.campaign_id)
        recipient_id = recipients[0]["id"]

        recipient = self.storage.get_recipient_by_id(recipient_id)
        assert recipient is not None
        assert recipient["email"] == "user1@example.com"

    def test_delete_recipient(self):
        """Test deleting a recipient."""
        recipients = self.storage.get_recipients(self.campaign_id)
        recipient_id = recipients[0]["id"]

        result = self.storage.delete_recipient(recipient_id)
        assert result is True

        recipient = self.storage.get_recipient_by_id(recipient_id)
        assert recipient is None

        # Verify only one recipient remains
        remaining = self.storage.get_recipients(self.campaign_id)
        assert len(remaining) == 1

    def test_retry_recipient(self):
        """Test retrying a failed recipient."""
        recipients = self.storage.get_recipients(self.campaign_id)
        recipient_id = recipients[0]["id"]

        # Mark as failed first
        self.storage.update_recipient_status(recipient_id, "failed", "Connection error")

        # Retry
        result = self.storage.retry_recipient(recipient_id)
        assert result is True

        recipient = self.storage.get_recipient_by_id(recipient_id)
        assert recipient["status"] == "queued"
        assert recipient["error_message"] is None

    def test_retry_all_failed(self):
        """Test retrying all failed recipients."""
        recipients = self.storage.get_recipients(self.campaign_id)

        # Mark both as failed
        for r in recipients:
            self.storage.update_recipient_status(r["id"], "failed", "Error")

        count = self.storage.retry_all_failed(self.campaign_id)
        assert count == 2

        # Verify all are queued now
        recipients = self.storage.get_recipients(self.campaign_id)
        for r in recipients:
            assert r["status"] == "queued"


class TestTracking:
    """Test email tracking operations."""

    def setup_method(self):
        """Setup test fixtures."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()
        self.storage = CampaignStorage(db_path=self.temp_db.name)

        # Create a campaign with a recipient
        self.campaign_id = self.storage.create_campaign(
            name="Test Campaign", subject="Test", source_type="csv"
        )
        self.storage.add_recipients(
            self.campaign_id,
            [
                {"email": "test@example.com", "name": "Test User"},
            ],
        )
        recipients = self.storage.get_recipients(self.campaign_id)
        self.recipient_id = recipients[0]["id"]

        # Mark as sent
        self.storage.update_recipient_status(self.recipient_id, "sent")

    def teardown_method(self):
        """Cleanup test fixtures."""
        if Path(self.temp_db.name).exists():
            os.unlink(self.temp_db.name)

    def test_record_email_open(self):
        """Test recording an email open."""
        self.storage.record_email_open(self.recipient_id)

        recipient = self.storage.get_recipient_by_id(self.recipient_id)
        assert recipient["opened_at"] is not None
        assert recipient["open_count"] == 1
        assert recipient["first_opened_at"] is not None

    def test_multiple_opens(self):
        """Test multiple opens are counted."""
        self.storage.record_email_open(self.recipient_id)
        self.storage.record_email_open(self.recipient_id)
        self.storage.record_email_open(self.recipient_id)

        recipient = self.storage.get_recipient_by_id(self.recipient_id)
        assert recipient["open_count"] == 3

    def test_record_click(self):
        """Test recording a click."""
        self.storage.record_email_click(
            self.recipient_id, self.campaign_id, "https://example.com"
        )

        clicks = self.storage.get_recipient_clicks(self.recipient_id)
        assert len(clicks) == 1
        assert clicks[0]["original_url"] == "https://example.com"

    def test_multiple_clicks(self):
        """Test multiple clicks are recorded."""
        self.storage.record_email_click(
            self.recipient_id, self.campaign_id, "https://example.com/page1"
        )
        self.storage.record_email_click(
            self.recipient_id, self.campaign_id, "https://example.com/page2"
        )

        clicks = self.storage.get_recipient_clicks(self.recipient_id)
        assert len(clicks) == 2

    def test_campaign_stats_include_tracking(self):
        """Test campaign stats include open/click data."""
        # Record some opens and clicks
        self.storage.record_email_open(self.recipient_id)
        self.storage.record_email_click(
            self.recipient_id, self.campaign_id, "https://example.com"
        )

        stats = self.storage.get_campaign_stats(self.campaign_id)
        assert stats["opened_count"] == 1
        assert stats["click_count"] == 1
        assert stats["open_rate"] > 0


class TestTrackingModule:
    """Test the tracking utilities module."""

    def test_inject_tracking_pixel(self):
        """Test tracking pixel injection."""
        from email_sender.tracking import inject_tracking_pixel

        html = "<html><body><p>Hello</p></body></html>"
        result = inject_tracking_pixel(html, campaign_id=1, recipient_id=42)

        assert "/track/open/1/42" in result
        assert 'width="1"' in result
        assert 'height="1"' in result

    def test_wrap_links_with_tracking(self):
        """Test link wrapping."""
        from email_sender.tracking import wrap_links_with_tracking

        html = '<a href="https://example.com">Click here</a>'
        result = wrap_links_with_tracking(html, campaign_id=1, recipient_id=42)

        assert "/track/click/1/42" in result
        assert "url=" in result

    def test_mailto_links_not_wrapped(self):
        """Test that mailto links are not wrapped."""
        from email_sender.tracking import wrap_links_with_tracking

        html = '<a href="mailto:test@example.com">Email us</a>'
        result = wrap_links_with_tracking(html, campaign_id=1, recipient_id=42)

        assert "/track/click/" not in result
        assert "mailto:test@example.com" in result

    def test_add_tracking_to_email(self):
        """Test combined tracking function."""
        from email_sender.tracking import add_tracking_to_email

        html = '<html><body><a href="https://example.com">Link</a></body></html>'
        result = add_tracking_to_email(html, campaign_id=1, recipient_id=42)

        # Should have both pixel and link tracking
        assert "/track/open/1/42" in result
        assert "/track/click/1/42" in result
