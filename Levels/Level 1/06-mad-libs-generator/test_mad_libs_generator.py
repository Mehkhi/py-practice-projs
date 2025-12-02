#!/usr/bin/env python3

import unittest
import os
import tempfile
from mad_libs_generator import load_template, find_placeholders, fill_template


class TestMadLibsGenerator(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures."""
        self.test_template = "The {adjective} {noun} {verb} {adverb}."
        self.test_words = {
            "adjective": "quick",
            "noun": "fox",
            "verb": "jumps",
            "adverb": "quickly"
        }

    def test_find_placeholders(self):
        """Test placeholder detection."""
        placeholders = find_placeholders(self.test_template)
        expected = ["adjective", "noun", "verb", "adverb"]
        self.assertEqual(placeholders, expected)

    def test_find_placeholders_empty(self):
        """Test placeholder detection with no placeholders."""
        template = "This is just a regular sentence."
        placeholders = find_placeholders(template)
        self.assertEqual(placeholders, [])

    def test_fill_template(self):
        """Test template filling."""
        result = fill_template(self.test_template, self.test_words)
        expected = "The quick fox jumps quickly."
        self.assertEqual(result, expected)

    def test_fill_template_partial(self):
        """Test template filling with partial word replacement."""
        partial_words = {"adjective": "happy", "noun": "dog"}
        result = fill_template(self.test_template, partial_words)
        expected = "The happy dog {verb} {adverb}."
        self.assertEqual(result, expected)

    def test_load_template_file(self):
        """Test loading template from file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("Test {placeholder} content.")
            temp_filename = f.name

        try:
            content = load_template(temp_filename)
            self.assertEqual(content, "Test {placeholder} content.")
        finally:
            os.unlink(temp_filename)

    def test_load_template_nonexistent(self):
        """Test loading non-existent template file."""
        content = load_template("nonexistent_file.txt")
        self.assertIsNone(content)


if __name__ == "__main__":
    unittest.main()
