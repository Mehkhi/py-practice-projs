"""
Comprehensive tests for the email sender package.

This module contains unit tests for all major functionality including
email sending, validation, CSV processing, and error handling.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from email.mime.multipart import MIMEMultipart

from email_sender.core import EmailSender, EmailError
from email_sender.utils import (
    validate_email,
    load_recipients_from_csv,
    create_sample_csv,
    format_email_template,
    get_file_size_mb,
    is_valid_attachment
)


class TestEmailValidation:
    """Test email validation functionality."""

    def test_valid_emails(self):
        """Test validation of valid email addresses."""
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "user+tag@example.org",
            "123@numbers.com",
            "test.email+tag@subdomain.example.com"
        ]

        for email in valid_emails:
            assert validate_email(email), f"Should be valid: {email}"

    def test_invalid_emails(self):
        """Test validation of invalid email addresses."""
        invalid_emails = [
            "",
            "invalid",
            "@example.com",
            "test@",
            "test..test@example.com",
            "test@.com",
            "test@example.",
            None,
            123
        ]

        for email in invalid_emails:
            assert not validate_email(email), f"Should be invalid: {email}"

    def test_email_validation_edge_cases(self):
        """Test edge cases in email validation."""
        # Empty string
        assert not validate_email("")

        # Whitespace
        assert not validate_email("  ")

        # Multiple @ symbols
        assert not validate_email("test@@example.com")

        # No domain
        assert not validate_email("test@")


class TestCSVProcessing:
    """Test CSV file processing functionality."""

    def test_create_sample_csv(self):
        """Test creation of sample CSV file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_path = f.name

        try:
            create_sample_csv(temp_path)

            # Verify file was created
            assert Path(temp_path).exists()

            # Verify content
            recipients = load_recipients_from_csv(temp_path)
            assert len(recipients) == 3
            assert recipients[0]['email'] == 'john.doe@example.com'
            assert recipients[0]['name'] == 'John Doe'

        finally:
            os.unlink(temp_path)

    def test_load_recipients_from_csv(self):
        """Test loading recipients from CSV file."""
        csv_content = """email,name,company
john@example.com,John Doe,Acme Corp
jane@example.com,Jane Smith,Tech Inc
invalid-email,Invalid User,Bad Corp
bob@example.com,Bob Wilson,Startup LLC"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            recipients = load_recipients_from_csv(temp_path)

            # Should load 3 valid recipients (invalid email should be skipped)
            assert len(recipients) == 3
            assert recipients[0]['email'] == 'john@example.com'
            assert recipients[1]['email'] == 'jane@example.com'
            assert recipients[2]['email'] == 'bob@example.com'

        finally:
            os.unlink(temp_path)

    def test_load_recipients_missing_file(self):
        """Test loading recipients from non-existent file."""
        with pytest.raises(FileNotFoundError):
            load_recipients_from_csv("nonexistent.csv")

    def test_load_recipients_invalid_csv(self):
        """Test loading recipients from invalid CSV."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("invalid,csv,content\nwith,no,proper,format")
            temp_path = f.name

        try:
            # Should return empty list for invalid CSV format
            recipients = load_recipients_from_csv(temp_path)
            assert recipients == []
        finally:
            os.unlink(temp_path)


class TestEmailSender:
    """Test EmailSender class functionality."""

    def setup_method(self):
        """Setup test fixtures."""
        self.sender = EmailSender(
            smtp_server="smtp.example.com",
            smtp_port=587,
            username="test@example.com",
            password="testpassword",
            use_tls=True
        )

    @patch('smtplib.SMTP')
    def test_connect_success(self, mock_smtp_class):
        """Test successful SMTP connection."""
        mock_smtp = Mock()
        mock_smtp_class.return_value = mock_smtp

        self.sender.connect()

        mock_smtp_class.assert_called_once_with("smtp.example.com", 587)
        mock_smtp.starttls.assert_called_once()
        mock_smtp.login.assert_called_once_with("test@example.com", "testpassword")
        assert self.sender._connection == mock_smtp

    @patch('smtplib.SMTP')
    def test_connect_authentication_error(self, mock_smtp_class):
        """Test SMTP authentication error."""
        import smtplib
        mock_smtp = Mock()
        mock_smtp.login.side_effect = smtplib.SMTPAuthenticationError(535, "Authentication failed")
        mock_smtp_class.return_value = mock_smtp

        with pytest.raises(EmailError, match="Authentication failed"):
            self.sender.connect()

    @patch('smtplib.SMTP')
    def test_connect_connection_error(self, mock_smtp_class):
        """Test SMTP connection error."""
        import smtplib
        mock_smtp_class.side_effect = smtplib.SMTPConnectError(421, "Connection failed")

        with pytest.raises(EmailError, match="Connection failed"):
            self.sender.connect()

    def test_disconnect(self):
        """Test SMTP disconnection."""
        mock_connection = Mock()
        self.sender._connection = mock_connection

        self.sender.disconnect()

        mock_connection.quit.assert_called_once()
        assert self.sender._connection is None

    def test_context_manager(self):
        """Test context manager functionality."""
        with patch.object(self.sender, 'connect') as mock_connect, \
             patch.object(self.sender, 'disconnect') as mock_disconnect:

            with self.sender:
                mock_connect.assert_called_once()

            mock_disconnect.assert_called_once()

    @patch('smtplib.SMTP')
    def test_send_email_success(self, mock_smtp_class):
        """Test successful email sending."""
        mock_smtp = Mock()
        mock_smtp_class.return_value = mock_smtp
        mock_smtp.send_message.return_value = {}
        self.sender._connection = mock_smtp

        result = self.sender.send_email(
            to_emails=["test@example.com"],
            subject="Test Subject",
            body="Test Body"
        )

        assert result['success'] is True
        assert result['recipients'] == ["test@example.com"]
        mock_smtp.send_message.assert_called_once()

    @patch('smtplib.SMTP')
    def test_send_email_invalid_recipients(self, mock_smtp_class):
        """Test email sending with invalid recipients."""
        mock_smtp = Mock()
        mock_smtp_class.return_value = mock_smtp
        self.sender._connection = mock_smtp

        with pytest.raises(EmailError, match="Invalid email addresses"):
            self.sender.send_email(
                to_emails=["invalid-email"],
                subject="Test Subject",
                body="Test Body"
            )

    @patch('smtplib.SMTP')
    def test_send_email_not_connected(self, mock_smtp_class):
        """Test email sending without connection."""
        with pytest.raises(EmailError, match="Not connected"):
            self.sender.send_email(
                to_emails=["test@example.com"],
                subject="Test Subject",
                body="Test Body"
            )

    @patch('smtplib.SMTP')
    def test_send_email_with_attachment(self, mock_smtp_class):
        """Test email sending with attachment."""
        mock_smtp = Mock()
        mock_smtp_class.return_value = mock_smtp
        mock_smtp.send_message.return_value = {}
        self.sender._connection = mock_smtp

        # Create a temporary file for attachment
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"test content")
            temp_path = f.name

        try:
            result = self.sender.send_email(
                to_emails=["test@example.com"],
                subject="Test Subject",
                body="Test Body",
                attachments=[temp_path]
            )

            assert result['success'] is True
            assert result['attachments_count'] == 1

        finally:
            os.unlink(temp_path)

    @patch('smtplib.SMTP')
    def test_send_email_attachment_not_found(self, mock_smtp_class):
        """Test email sending with non-existent attachment."""
        mock_smtp = Mock()
        mock_smtp_class.return_value = mock_smtp
        self.sender._connection = mock_smtp

        with pytest.raises(EmailError, match="Attachment file not found"):
            self.sender.send_email(
                to_emails=["test@example.com"],
                subject="Test Subject",
                body="Test Body",
                attachments=["nonexistent.txt"]
            )

    @patch('smtplib.SMTP')
    def test_send_email_partial_refused(self, mock_smtp_class):
        """send_email should error when SMTP reports refused recipients."""
        mock_smtp = Mock()
        mock_smtp_class.return_value = mock_smtp
        mock_smtp.send_message.return_value = {
            "bad@example.com": (550, b"User unknown")
        }
        self.sender._connection = mock_smtp

        with pytest.raises(EmailError, match="Recipients refused"):
            self.sender.send_email(
                to_emails=["good@example.com", "bad@example.com"],
                subject="Test Subject",
                body="Test Body"
            )

    @patch('smtplib.SMTP')
    def test_send_batch_success(self, mock_smtp_class):
        """Test successful batch email sending."""
        mock_smtp = Mock()
        mock_smtp_class.return_value = mock_smtp
        mock_smtp.send_message.return_value = {}
        self.sender._connection = mock_smtp

        # Create temporary CSV file
        csv_content = """email,name
test1@example.com,Test User 1
test2@example.com,Test User 2"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            result = self.sender.send_batch(
                recipients_file=temp_path,
                subject="Test Subject",
                body="Test Body",
                batch_size=1
            )

            assert result['total_recipients'] == 2
            assert result['successful_emails'] == 2
            assert result['failed_emails'] == 0
            assert result['batches_sent'] == 2

        finally:
            os.unlink(temp_path)


class TestUtilityFunctions:
    """Test utility functions."""

    def test_format_email_template(self):
        """Test email template formatting."""
        template = "Hello {name}, welcome to {company}!"
        data = {"name": "John", "company": "Acme Corp"}

        result = format_email_template(template, data)
        assert result == "Hello John, welcome to Acme Corp!"

    def test_format_email_template_missing_variable(self):
        """Test template formatting with missing variable."""
        template = "Hello {name}, welcome to {company}!"
        data = {"name": "John"}  # Missing company

        result = format_email_template(template, data)
        assert result == template  # Should return original template

    def test_get_file_size_mb(self):
        """Test file size calculation."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"x" * 1024)  # 1KB
            temp_path = f.name

        try:
            size_mb = get_file_size_mb(temp_path)
            assert size_mb == 1024 / (1024 * 1024)  # 1KB in MB

        finally:
            os.unlink(temp_path)

    def test_get_file_size_mb_nonexistent(self):
        """Test file size calculation for non-existent file."""
        size_mb = get_file_size_mb("nonexistent.txt")
        assert size_mb == 0.0

    def test_is_valid_attachment(self):
        """Test attachment validation."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"test content")
            temp_path = f.name

        try:
            assert is_valid_attachment(temp_path)
            assert not is_valid_attachment("nonexistent.txt")
            # Create a larger file for size test
            with tempfile.NamedTemporaryFile(delete=False) as f2:
                f2.write(b"x" * (1024 * 1024))  # 1MB
                large_file = f2.name
            try:
                assert not is_valid_attachment(large_file, max_size_mb=0.5)  # Too large
            finally:
                os.unlink(large_file)

        finally:
            os.unlink(temp_path)


class TestErrorHandling:
    """Test error handling scenarios."""

    def test_email_error_creation(self):
        """Test EmailError exception creation."""
        error = EmailError("Test error message")
        assert str(error) == "Test error message"
        assert isinstance(error, Exception)

    @patch('smtplib.SMTP')
    def test_smtp_recipients_refused(self, mock_smtp_class):
        """Test handling of SMTP recipients refused error."""
        import smtplib
        mock_smtp = Mock()
        mock_smtp_class.return_value = mock_smtp
        mock_smtp.send_message.side_effect = smtplib.SMTPRecipientsRefused("Recipients refused")

        sender = EmailSender("smtp.example.com", 587, "test@example.com", "password")
        sender._connection = mock_smtp

        with pytest.raises(EmailError, match="Recipients refused"):
            sender.send_email(
                to_emails=["test@example.com"],
                subject="Test",
                body="Test"
            )

    @patch('smtplib.SMTP')
    def test_smtp_data_error(self, mock_smtp_class):
        """Test handling of SMTP data error."""
        import smtplib
        mock_smtp = Mock()
        mock_smtp_class.return_value = mock_smtp
        mock_smtp.send_message.side_effect = smtplib.SMTPDataError(550, "Data error")

        sender = EmailSender("smtp.example.com", 587, "test@example.com", "password")
        sender._connection = mock_smtp

        with pytest.raises(EmailError, match="Data error"):
            sender.send_email(
                to_emails=["test@example.com"],
                subject="Test",
                body="Test"
            )


if __name__ == '__main__':
    pytest.main([__file__])
