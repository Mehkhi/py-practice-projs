"""
Tests for campaign storage functionality.
"""

import pytest
import tempfile
import os
from pathlib import Path

from email_sender.storage import CampaignStorage


class TestCampaignStorage:
    """Test CampaignStorage class."""

    def setup_method(self):
        """Setup test fixtures."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.storage = CampaignStorage(db_path=self.temp_db.name)

    def teardown_method(self):
        """Cleanup test fixtures."""
        if Path(self.temp_db.name).exists():
            os.unlink(self.temp_db.name)

    def test_create_campaign(self):
        """Test creating a campaign."""
        campaign_id = self.storage.create_campaign(
            name="Test Campaign",
            subject="Test Subject",
            body_template="Hello {name}",
            source_type="csv"
        )

        assert campaign_id == 1
        campaign = self.storage.get_campaign(campaign_id)
        assert campaign['name'] == "Test Campaign"
        assert campaign['subject'] == "Test Subject"
        assert campaign['body_template'] == "Hello {name}"

    def test_list_campaigns(self):
        """Test listing campaigns."""
        # Create multiple campaigns
        self.storage.create_campaign(
            name="Campaign 1",
            subject="Subject 1",
            source_type="csv"
        )
        self.storage.create_campaign(
            name="Campaign 2",
            subject="Subject 2",
            source_type="sheet"
        )

        campaigns = self.storage.list_campaigns()
        assert len(campaigns) == 2
        assert campaigns[0]['name'] == "Campaign 2"  # Most recent first
        assert campaigns[1]['name'] == "Campaign 1"

    def test_add_recipients(self):
        """Test adding recipients to a campaign."""
        campaign_id = self.storage.create_campaign(
            name="Test Campaign",
            subject="Test Subject",
            source_type="csv"
        )

        recipients = [
            {'email': 'test1@example.com', 'name': 'Test User 1'},
            {'email': 'test2@example.com', 'name': 'Test User 2', 'company': 'Test Corp'}
        ]

        added = self.storage.add_recipients(campaign_id, recipients)
        assert added == 2

        stored_recipients = self.storage.get_recipients(campaign_id)
        assert len(stored_recipients) == 2
        assert stored_recipients[0]['email'] == 'test1@example.com'
        assert stored_recipients[0]['personalization_data']['name'] == 'Test User 1'

    def test_get_recipients_by_status(self):
        """Test getting recipients filtered by status."""
        campaign_id = self.storage.create_campaign(
            name="Test Campaign",
            subject="Test Subject",
            source_type="csv"
        )

        recipients = [
            {'email': 'test1@example.com'},
            {'email': 'test2@example.com'}
        ]
        self.storage.add_recipients(campaign_id, recipients)

        # Update one recipient status
        all_recipients = self.storage.get_recipients(campaign_id)
        self.storage.update_recipient_status(all_recipients[0]['id'], 'sent')

        queued = self.storage.get_recipients(campaign_id, status='queued')
        sent = self.storage.get_recipients(campaign_id, status='sent')

        assert len(queued) == 1
        assert len(sent) == 1

    def test_update_recipient_status(self):
        """Test updating recipient status."""
        campaign_id = self.storage.create_campaign(
            name="Test Campaign",
            subject="Test Subject",
            source_type="csv"
        )

        recipients = [{'email': 'test@example.com'}]
        self.storage.add_recipients(campaign_id, recipients)

        recipient = self.storage.get_recipients(campaign_id)[0]
        assert recipient['status'] == 'queued'

        self.storage.update_recipient_status(recipient['id'], 'sent', 'Success')
        updated = self.storage.get_recipients(campaign_id)[0]
        assert updated['status'] == 'sent'
        assert updated['error_message'] == 'Success'
        assert updated['sent_at'] is not None

    def test_get_campaign_stats(self):
        """Test getting campaign statistics."""
        campaign_id = self.storage.create_campaign(
            name="Test Campaign",
            subject="Test Subject",
            source_type="csv"
        )

        recipients = [
            {'email': 'test1@example.com'},
            {'email': 'test2@example.com'},
            {'email': 'test3@example.com'}
        ]
        self.storage.add_recipients(campaign_id, recipients)

        all_recipients = self.storage.get_recipients(campaign_id)
        self.storage.update_recipient_status(all_recipients[0]['id'], 'sent')
        self.storage.update_recipient_status(all_recipients[1]['id'], 'failed', 'Error message')

        stats = self.storage.get_campaign_stats(campaign_id)
        assert stats['total'] == 3
        assert stats['queued'] == 1
        assert stats['sent'] == 1
        assert stats['failed'] == 1

    def test_export_campaign_results(self):
        """Test exporting campaign results."""
        campaign_id = self.storage.create_campaign(
            name="Test Campaign",
            subject="Test Subject",
            source_type="csv"
        )

        recipients = [
            {'email': 'test1@example.com', 'name': 'User 1'},
            {'email': 'test2@example.com', 'name': 'User 2'}
        ]
        self.storage.add_recipients(campaign_id, recipients)

        all_recipients = self.storage.get_recipients(campaign_id)
        self.storage.update_recipient_status(all_recipients[0]['id'], 'sent')

        results = self.storage.export_campaign_results(campaign_id)
        assert len(results) == 2
        assert results[0]['email'] == 'test1@example.com'
        assert results[0]['status'] == 'sent'
        assert results[0]['name'] == 'User 1'
