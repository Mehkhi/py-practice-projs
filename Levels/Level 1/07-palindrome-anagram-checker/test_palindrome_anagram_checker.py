#!/usr/bin/env python3

import unittest
from palindrome_anagram_checker import normalize_string, is_palindrome, are_anagrams


class TestPalindromeAnagramChecker(unittest.TestCase):

    def test_normalize_string(self):
        """Test string normalization."""
        # Basic cases
        self.assertEqual(normalize_string("Hello"), "hello")
        self.assertEqual(normalize_string("HELLO"), "hello")

        # With spaces and punctuation
        self.assertEqual(normalize_string("A man, a plan, a canal: Panama"), "amanaplanacanalpanama")
        self.assertEqual(normalize_string("Hello, World!"), "helloworld")

        # With numbers
        self.assertEqual(normalize_string("123 ABC"), "123abc")

        # Edge cases
        self.assertEqual(normalize_string(""), "")
        self.assertEqual(normalize_string("   "), "")
        self.assertEqual(normalize_string("!@#$%^&*()"), "")
        self.assertEqual(normalize_string(None), "")

    def test_is_palindrome(self):
        """Test palindrome detection."""
        # Simple palindromes
        self.assertTrue(is_palindrome("racecar"))
        self.assertTrue(is_palindrome("level"))
        self.assertTrue(is_palindrome("madam"))

        # Palindromes with spaces and punctuation
        self.assertTrue(is_palindrome("A man, a plan, a canal: Panama"))
        self.assertTrue(is_palindrome("Was it a car or a cat I saw?"))
        self.assertTrue(is_palindrome("No lemon, no melon"))

        # Non-palindromes
        self.assertFalse(is_palindrome("hello"))
        self.assertFalse(is_palindrome("world"))
        self.assertFalse(is_palindrome("python"))

        # Edge cases
        self.assertTrue(is_palindrome(""))  # Empty string is a palindrome
        self.assertTrue(is_palindrome("a"))  # Single character
        self.assertTrue(is_palindrome("   "))  # Only spaces

    def test_are_anagrams(self):
        """Test anagram detection."""
        # Simple anagrams
        self.assertTrue(are_anagrams("listen", "silent"))
        self.assertTrue(are_anagrams("race", "care"))
        self.assertTrue(are_anagrams("dusty", "study"))

        # Anagrams with different cases and spaces
        self.assertTrue(are_anagrams("Dormitory", "Dirty room"))
        self.assertTrue(are_anagrams("The eyes", "They see"))
        self.assertTrue(are_anagrams("Astronomer", "Moon starer"))

        # Non-anagrams
        self.assertFalse(are_anagrams("hello", "world"))
        self.assertFalse(are_anagrams("python", "java"))
        self.assertFalse(are_anagrams("test", "tests"))  # Different lengths

        # Edge cases
        self.assertTrue(are_anagrams("", ""))  # Empty strings
        self.assertTrue(are_anagrams("a", "a"))  # Same single character
        self.assertFalse(are_anagrams("a", "b"))  # Different single character
        self.assertFalse(are_anagrams("ab", "a"))  # Different lengths

    def test_unicode_support(self):
        """Test basic Unicode support."""
        # Unicode palindromes
        self.assertTrue(is_palindrome("été"))
        self.assertTrue(is_palindrome("åßßå"))

        # Unicode anagrams (using actual anagrams after normalization)
        self.assertTrue(are_anagrams("résumé", "mérsu"))  # Both normalize to rsum


if __name__ == "__main__":
    unittest.main()
