#!/usr/bin/env python3
"""
Unit tests for Password Generator

Tests the core functionality of password generation, entropy calculation,
and security features.
"""

import unittest
from unittest.mock import patch
import string
import math
from password_generator import PasswordGenerator


class TestPasswordGenerator(unittest.TestCase):
    """Test cases for the PasswordGenerator class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.generator = PasswordGenerator()

    def test_initial_state(self):
        """Test generator initial state."""
        self.assertEqual(len(self.generator.character_classes), 4)
        self.assertTrue(self.generator.character_classes["uppercase"]["enabled"])
        self.assertTrue(self.generator.character_classes["lowercase"]["enabled"])
        self.assertTrue(self.generator.character_classes["digits"]["enabled"])
        self.assertFalse(self.generator.character_classes["symbols"]["enabled"])
        self.assertGreater(len(self.generator.word_list), 50)

    def test_validate_length_valid(self):
        """Test valid password length validation."""
        # Test minimum valid length
        is_valid, length, error = self.generator.validate_length("4")
        self.assertTrue(is_valid)
        self.assertEqual(length, 4)
        self.assertEqual(error, "")

        # Test typical length
        is_valid, length, error = self.generator.validate_length("12")
        self.assertTrue(is_valid)
        self.assertEqual(length, 12)

        # Test maximum valid length
        is_valid, length, error = self.generator.validate_length("128")
        self.assertTrue(is_valid)
        self.assertEqual(length, 128)

    def test_validate_length_invalid(self):
        """Test invalid password length validation."""
        # Empty input
        is_valid, length, error = self.generator.validate_length("")
        self.assertFalse(is_valid)
        self.assertIsNone(length)
        self.assertIn("cannot be empty", error)

        # Non-integer input
        is_valid, length, error = self.generator.validate_length("abc")
        self.assertFalse(is_valid)
        self.assertIsNone(length)
        self.assertIn("valid integer", error)

        # Too short
        is_valid, length, error = self.generator.validate_length("3")
        self.assertFalse(is_valid)
        self.assertIsNone(length)
        self.assertIn("at least 4", error)

        # Too long
        is_valid, length, error = self.generator.validate_length("129")
        self.assertFalse(is_valid)
        self.assertIsNone(length)
        self.assertIn("cannot exceed 128", error)

        # Negative number
        is_valid, length, error = self.generator.validate_length("-5")
        self.assertFalse(is_valid)
        self.assertIsNone(length)
        self.assertTrue("valid integer" in error or "at least 4" in error)

    def test_get_enabled_character_classes(self):
        """Test getting enabled character classes."""
        # Default state
        enabled = self.generator.get_enabled_character_classes()
        self.assertIn("uppercase", enabled)
        self.assertIn("lowercase", enabled)
        self.assertIn("digits", enabled)
        self.assertNotIn("symbols", enabled)

        # Disable some classes
        self.generator.character_classes["uppercase"]["enabled"] = False
        self.generator.character_classes["digits"]["enabled"] = False

        enabled = self.generator.get_enabled_character_classes()
        self.assertNotIn("uppercase", enabled)
        self.assertIn("lowercase", enabled)
        self.assertNotIn("digits", enabled)
        self.assertNotIn("symbols", enabled)

    def test_validate_character_classes(self):
        """Test character class validation."""
        # Default state - should be valid
        is_valid, error = self.generator.validate_character_classes()
        self.assertTrue(is_valid)
        self.assertEqual(error, "")

        # Disable all classes
        for class_name in self.generator.character_classes:
            self.generator.character_classes[class_name]["enabled"] = False

        is_valid, error = self.generator.validate_character_classes()
        self.assertFalse(is_valid)
        self.assertIn("At least one character class", error)

    def test_calculate_entropy(self):
        """Test entropy calculation."""
        # Empty password
        entropy = self.generator.calculate_entropy("")
        self.assertEqual(entropy, 0.0)

        # Simple lowercase password
        entropy = self.generator.calculate_entropy("password")
        expected = len("password") * math.log2(26)
        self.assertAlmostEqual(entropy, expected, places=2)

        # Mixed characters
        entropy = self.generator.calculate_entropy("Pass123!")
        # Should include lowercase, uppercase, digits, and symbols
        char_set_size = (
            26
            + 26
            + 10
            + len(self.generator.character_classes["symbols"]["characters"])
        )
        expected = len("Pass123!") * math.log2(char_set_size)
        self.assertAlmostEqual(entropy, expected, places=2)

    def test_assess_password_strength(self):
        """Test password strength assessment."""
        # Very weak password
        assessment = self.generator.assess_password_strength("abc")
        self.assertEqual(assessment["strength"], "Very Weak")
        self.assertEqual(assessment["length"], 3)
        self.assertTrue(assessment["has_lowercase"])
        self.assertFalse(assessment["has_uppercase"])
        self.assertFalse(assessment["has_digits"])
        self.assertFalse(assessment["has_symbols"])

        # Strong password
        assessment = self.generator.assess_password_strength("Str0ng!P@ss")
        self.assertIn(assessment["strength"], ["Moderate", "Strong", "Very Strong"])
        self.assertEqual(assessment["length"], 11)
        self.assertTrue(assessment["has_uppercase"])
        self.assertTrue(assessment["has_lowercase"])
        self.assertTrue(assessment["has_digits"])
        self.assertTrue(assessment["has_symbols"])

        # Check color codes are present
        self.assertIn("color_code", assessment)
        self.assertIn("entropy", assessment)

    def test_generate_password_basic(self):
        """Test basic password generation."""
        password = self.generator.generate_password(12)

        # Check length
        self.assertEqual(len(password), 12)

        # Check that it contains only allowed characters
        enabled_classes = self.generator.get_enabled_character_classes()
        allowed_chars = ""
        for chars in enabled_classes.values():
            allowed_chars += chars

        for char in password:
            self.assertIn(char, allowed_chars)

    def test_generate_password_ensure_classes(self):
        """Test password generation with class enforcement."""
        # Enable all classes
        for class_name in self.generator.character_classes:
            self.generator.character_classes[class_name]["enabled"] = True

        password = self.generator.generate_password(20, ensure_all_classes=True)

        # Check that it contains at least one character from each class
        self.assertTrue(any(c in string.ascii_uppercase for c in password))
        self.assertTrue(any(c in string.ascii_lowercase for c in password))
        self.assertTrue(any(c in string.digits for c in password))
        self.assertTrue(
            any(
                c in self.generator.character_classes["symbols"]["characters"]
                for c in password
            )
        )

    def test_generate_password_no_classes_enabled(self):
        """Test password generation with no classes enabled."""
        # Disable all classes
        for class_name in self.generator.character_classes:
            self.generator.character_classes[class_name]["enabled"] = False

        with self.assertRaises(ValueError):
            self.generator.generate_password(12)

    def test_generate_password_short_length_with_enforcement(self):
        """Test password generation when length is less than number of classes."""
        # Enable all classes
        for class_name in self.generator.character_classes:
            self.generator.character_classes[class_name]["enabled"] = True

        # Generate password shorter than number of classes
        password = self.generator.generate_password(2, ensure_all_classes=True)

        # Should still generate password (without enforcement due to length constraint)
        self.assertEqual(len(password), 2)

    def test_generate_passphrase_basic(self):
        """Test basic passphrase generation."""
        passphrase = self.generator.generate_passphrase()

        # Check that it contains words from the word list
        words = passphrase.split("-")
        self.assertGreaterEqual(len(words), 2)
        self.assertLessEqual(len(words), 4)  # Default is 4 words

        # Check that words are capitalized by default
        for word in words[:-1]:  # Last word might have number
            self.assertTrue(word[0].isupper() if word else True)

    def test_generate_passphrase_custom_options(self):
        """Test passphrase generation with custom options."""
        passphrase = self.generator.generate_passphrase(
            word_count=3, separator="_", capitalize=False, include_number=False
        )

        # Check separator
        self.assertIn("_", passphrase)

        # Check no number at end
        self.assertFalse(passphrase[-1].isdigit())

        # Check words are not capitalized
        words = passphrase.split("_")
        for word in words:
            if word:  # Skip empty strings
                self.assertTrue(word[0].islower())

    def test_generate_passphrase_edge_cases(self):
        """Test passphrase generation edge cases."""
        # Too few words
        passphrase = self.generator.generate_passphrase(word_count=1)
        words = passphrase.split("-")
        self.assertGreaterEqual(len(words), 2)

        # Too many words
        passphrase = self.generator.generate_passphrase(word_count=15)
        words = passphrase.split("-")
        self.assertLessEqual(len(words), 10)

    @patch("subprocess.run")
    def test_copy_to_clipboard_success(self, mock_run):
        """Test successful clipboard copy."""
        mock_run.return_value = None

        result = self.generator.copy_to_clipboard("test text")

        self.assertTrue(result)
        mock_run.assert_called()

    @patch("subprocess.run")
    def test_copy_to_clipboard_failure(self, mock_run):
        """Test clipboard copy failure."""
        mock_run.side_effect = Exception("Clipboard error")

        result = self.generator.copy_to_clipboard("test text")

        self.assertFalse(result)


class TestPasswordGeneratorIntegration(unittest.TestCase):
    """Integration tests for complete workflows."""

    def setUp(self):
        """Set up test fixtures."""
        self.generator = PasswordGenerator()

    def test_complete_password_workflow(self):
        """Test complete password generation workflow."""
        # Configure character classes
        self.generator.character_classes["symbols"]["enabled"] = True

        # Generate password
        password = self.generator.generate_password(16, ensure_all_classes=True)

        # Verify password properties
        self.assertEqual(len(password), 16)

        # Analyze password
        assessment = self.generator.assess_password_strength(password)

        # Should have all character types
        self.assertTrue(assessment["has_uppercase"])
        self.assertTrue(assessment["has_lowercase"])
        self.assertTrue(assessment["has_digits"])
        self.assertTrue(assessment["has_symbols"])

        # Should have reasonable entropy
        self.assertGreater(assessment["entropy"], 50)

    def test_complete_passphrase_workflow(self):
        """Test complete passphrase generation workflow."""
        # Generate passphrase
        passphrase = self.generator.generate_passphrase(
            word_count=5, separator=" ", capitalize=True, include_number=True
        )

        # Analyze passphrase
        assessment = self.generator.assess_password_strength(passphrase)

        # Should be reasonably long
        self.assertGreater(assessment["length"], 20)

        # Should have decent entropy
        self.assertGreater(assessment["entropy"], 40)

    def test_character_class_configuration_workflow(self):
        """Test character class configuration workflow."""
        # Disable all classes except symbols
        for class_name in self.generator.character_classes:
            self.generator.character_classes[class_name]["enabled"] = False
        self.generator.character_classes["symbols"]["enabled"] = True

        # Generate password
        password = self.generator.generate_password(10)

        # Should only contain symbols
        for char in password:
            self.assertIn(
                char, self.generator.character_classes["symbols"]["characters"]
            )

        # Assessment should reflect this
        assessment = self.generator.assess_password_strength(password)
        self.assertTrue(assessment["has_symbols"])
        self.assertFalse(assessment["has_uppercase"])
        self.assertFalse(assessment["has_lowercase"])
        self.assertFalse(assessment["has_digits"])

    def test_password_strength_comparison(self):
        """Test password strength assessment across different passwords."""
        passwords = {
            "weak": "abc",
            "moderate": "password123",
            "strong": "Str0ng!P@ssw0rd",
            "very_strong": "V3ry$tr0ng!P@ssw0rd#2023",
        }

        strengths = {}
        for name, password in passwords.items():
            assessment = self.generator.assess_password_strength(password)
            strengths[name] = assessment["entropy"]

        # Verify strength progression
        self.assertLess(strengths["weak"], strengths["moderate"])
        self.assertLess(strengths["moderate"], strengths["strong"])
        self.assertLess(strengths["strong"], strengths["very_strong"])


if __name__ == "__main__":
    unittest.main()
