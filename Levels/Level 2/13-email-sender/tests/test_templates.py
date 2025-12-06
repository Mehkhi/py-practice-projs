"""
Tests for template rendering functionality.
"""

import pytest
import tempfile
import os
from pathlib import Path

from email_sender.utils import format_email_template, load_template_file


class TestTemplateFormatting:
    """Test template formatting functionality."""

    def test_format_simple_template(self):
        """Test formatting a simple template."""
        template = "Hello {name}, welcome to {company}!"
        data = {"name": "John", "company": "Acme Corp"}

        result = format_email_template(template, data)
        assert result == "Hello John, welcome to Acme Corp!"

    def test_format_template_missing_variable(self):
        """Test template with missing variable."""
        template = "Hello {name}, welcome to {company}!"
        data = {"name": "John"}  # Missing company

        result = format_email_template(template, data)
        # Should return original template when variable is missing
        assert result == template

    def test_format_template_empty_data(self):
        """Test template with empty data."""
        template = "Hello {name}!"
        data = {}

        result = format_email_template(template, data)
        assert result == template

    def test_format_template_multiple_variables(self):
        """Test template with multiple variables."""
        template = "Dear {name}, your order #{order_id} from {company} is ready."
        data = {
            "name": "Jane",
            "order_id": "12345",
            "company": "Shop Inc"
        }

        result = format_email_template(template, data)
        assert result == "Dear Jane, your order #12345 from Shop Inc is ready."

    def test_load_template_file(self):
        """Test loading template from file."""
        template_content = "<html><body>Hello {name}!</body></html>"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            f.write(template_content)
            temp_path = f.name

        try:
            loaded = load_template_file(temp_path)
            assert loaded == template_content
        finally:
            os.unlink(temp_path)

    def test_load_template_file_not_found(self):
        """Test loading non-existent template file."""
        with pytest.raises(FileNotFoundError):
            load_template_file("nonexistent.html")
