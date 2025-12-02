#!/usr/bin/env python3
"""
Unit tests for String Templater for Emails

Tests core functionality including template loading, variable detection,
replacement, and conditional processing.
"""

import unittest
import tempfile
import os
from string_templater_for_emails import EmailTemplater


class TestEmailTemplater(unittest.TestCase):
    """Test cases for EmailTemplater class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.templater = EmailTemplater()

    def test_load_template_from_string(self):
        """Test loading template from string."""
        template = "Hello {{name}}, welcome to {{company}}!"
        result = self.templater.load_template(template)

        self.assertTrue(result)
        self.assertEqual(self.templater.template, template)

    def test_load_template_from_file(self):
        """Test loading template from file."""
        template_content = "Dear {{customer_name}},\nYour order {{order_id}} is ready for pickup."

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp_file:
            temp_file.write(template_content)
            temp_file_path = temp_file.name

        try:
            result = self.templater.load_template(temp_file_path)

            self.assertTrue(result)
            self.assertEqual(self.templater.template, template_content)
        finally:
            os.unlink(temp_file_path)

    def test_load_template_invalid_file(self):
        """Test loading template from non-existent file."""
        result = self.templater.load_template("nonexistent_file.txt")

        self.assertFalse(result)

    def test_detect_variables(self):
        """Test variable detection in template."""
        template = "Hello {{name}}, your {{item}} costs ${{price}}."
        self.templater.load_template(template)

        variables = self.templater.detect_variables()

        expected_variables = ['name', 'item', 'price']
        self.assertEqual(set(variables), set(expected_variables))

    def test_detect_variables_no_variables(self):
        """Test variable detection with no variables."""
        template = "This is a plain text email with no variables."
        self.templater.load_template(template)

        variables = self.templater.detect_variables()

        self.assertEqual(variables, [])

    def test_detect_variables_duplicates(self):
        """Test variable detection with duplicate variables."""
        template = "Hello {{name}}, {{name}} is a great name!"
        self.templater.load_template(template)

        variables = self.templater.detect_variables()

        self.assertEqual(variables, ['name'])

    def test_replace_variables(self):
        """Test variable replacement."""
        template = "Hello {{name}}, your order {{order_id}} is ready!"
        self.templater.load_template(template)

        data = {'name': 'John', 'order_id': '12345'}
        result = self.templater.replace_variables(data)

        expected = "Hello John, your order 12345 is ready!"
        self.assertEqual(result, expected)

    def test_replace_variables_missing_data(self):
        """Test variable replacement with missing data."""
        template = "Hello {{name}}, your order {{order_id}} is ready!"
        self.templater.load_template(template)

        data = {'name': 'John'}  # Missing order_id
        result = self.templater.replace_variables(data)

        expected = "Hello John, your order {{order_id}} is ready!"
        self.assertEqual(result, expected)

    def test_replace_variables_extra_data(self):
        """Test variable replacement with extra data."""
        template = "Hello {{name}}!"
        self.templater.load_template(template)

        data = {'name': 'John', 'extra_field': 'ignored'}
        result = self.templater.replace_variables(data)

        expected = "Hello John!"
        self.assertEqual(result, expected)

    def test_conditional_sections_if_true(self):
        """Test conditional sections with true condition."""
        template = "Hello {{name}}!{{if premium}} You are a premium member.{{endif}}"
        self.templater.load_template(template)

        data = {'name': 'John', 'premium': True}
        result = self.templater.replace_variables(data)

        expected = "Hello John! You are a premium member."
        self.assertEqual(result, expected)

    def test_conditional_sections_if_false(self):
        """Test conditional sections with false condition."""
        template = "Hello {{name}}!{{if premium}} You are a premium member.{{endif}}"
        self.templater.load_template(template)

        data = {'name': 'John', 'premium': False}
        result = self.templater.replace_variables(data)

        expected = "Hello John!"
        self.assertEqual(result, expected)

    def test_conditional_sections_with_else(self):
        """Test conditional sections with else clause."""
        template = "Hello {{name}}!{{if premium}} You are a premium member.{{else}} Consider upgrading to premium.{{endif}}"
        self.templater.load_template(template)

        data = {'name': 'John', 'premium': False}
        result = self.templater.replace_variables(data)

        expected = "Hello John! Consider upgrading to premium."
        self.assertEqual(result, expected)

    def test_load_data_from_json(self):
        """Test loading data from JSON file."""
        json_data = {'name': 'John', 'order_id': '12345'}

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
            import json
            json.dump(json_data, temp_file)
            temp_file_path = temp_file.name

        try:
            result = self.templater.load_data_from_json(temp_file_path)

            self.assertEqual(result, json_data)
        finally:
            os.unlink(temp_file_path)

    def test_load_data_from_json_invalid_file(self):
        """Test loading data from invalid JSON file."""
        result = self.templater.load_data_from_json("nonexistent.json")

        self.assertIsNone(result)

    def test_generate_batch_emails(self):
        """Test batch email generation."""
        template = "Hello {{name}}, your order {{order_id}} is ready!"
        self.templater.load_template(template)

        data_list = [
            {'name': 'John', 'order_id': '12345'},
            {'name': 'Jane', 'order_id': '67890'}
        ]

        emails = self.templater.generate_batch_emails(data_list)

        self.assertEqual(len(emails), 2)
        self.assertEqual(emails[0], "Hello John, your order 12345 is ready!")
        self.assertEqual(emails[1], "Hello Jane, your order 67890 is ready!")

    def test_complex_template(self):
        """Test complex template with multiple features."""
        template = """Dear {{customer_name}},

Thank you for your order {{order_id}}.

{{if premium}}
As a premium member, you get free shipping!
{{else}}
Shipping costs $5.99.
{{endif}}

Your items:
{{if item1}}{{item1}}{{endif}}
{{if item2}}{{item2}}{{endif}}

Total: ${{total}}

Best regards,
{{company_name}}"""

        self.templater.load_template(template)

        data = {
            'customer_name': 'John Doe',
            'order_id': 'ORD-12345',
            'premium': True,
            'item1': 'Widget A',
            'item2': 'Widget B',
            'total': '29.99',
            'company_name': 'Widget Store'
        }

        result = self.templater.replace_variables(data)

        self.assertIn('Dear John Doe,', result)
        self.assertIn('order ORD-12345', result)
        self.assertIn('free shipping', result)
        self.assertNotIn('Shipping costs $5.99', result)
        self.assertIn('Widget A', result)
        self.assertIn('Widget B', result)
        self.assertIn('$29.99', result)
        self.assertIn('Widget Store', result)


if __name__ == '__main__':
    unittest.main()
