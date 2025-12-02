#!/usr/bin/env python3

import unittest
import tempfile
import os
from word_count import WordCounter


class TestWordCounter(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures."""
        self.counter = WordCounter()
        self.test_text = "Hello world! This is a test. Hello again, world!"
        self.counter.set_text(self.test_text)

    def test_count_characters(self):
        """Test character counting."""
        # Test with sample text
        self.assertEqual(self.counter.count_characters(), len(self.test_text))

        # Test with empty text
        self.counter.set_text("")
        self.assertEqual(self.counter.count_characters(), 0)

        # Test with spaces
        self.counter.set_text("   ")
        self.assertEqual(self.counter.count_characters(), 3)

    def test_count_characters_no_spaces(self):
        """Test character counting excluding spaces."""
        self.counter.set_text("Hello world")
        self.assertEqual(self.counter.count_characters_no_spaces(), 10)  # "Helloworld"

        self.counter.set_text("   ")
        self.assertEqual(self.counter.count_characters_no_spaces(), 0)

    def test_count_words(self):
        """Test word counting."""
        # Test with sample text
        self.assertEqual(self.counter.count_words(), 9)  # Hello, world, This, is, a, test, Hello, again, world

        # Test with empty text
        self.counter.set_text("")
        self.assertEqual(self.counter.count_words(), 0)

        # Test with punctuation
        self.counter.set_text("Hello, world! How are you?")
        self.assertEqual(self.counter.count_words(), 5)

        # Test with multiple spaces
        self.counter.set_text("Hello    world")
        self.assertEqual(self.counter.count_words(), 2)

    def test_count_lines(self):
        """Test line counting."""
        # Test with single line
        self.counter.set_text("Hello world")
        self.assertEqual(self.counter.count_lines(), 1)

        # Test with multiple lines
        self.counter.set_text("Line 1\nLine 2\nLine 3")
        self.assertEqual(self.counter.count_lines(), 3)

        # Test with empty lines
        self.counter.set_text("Line 1\n\nLine 3")
        self.assertEqual(self.counter.count_lines(), 2)  # Empty line is filtered out

        # Test with empty text
        self.counter.set_text("")
        self.assertEqual(self.counter.count_lines(), 0)

    def test_count_paragraphs(self):
        """Test paragraph counting."""
        # Test with single paragraph
        self.counter.set_text("This is a single paragraph.")
        self.assertEqual(self.counter.count_paragraphs(), 1)

        # Test with multiple paragraphs
        self.counter.set_text("Paragraph 1.\n\nParagraph 2.\n\nParagraph 3.")
        self.assertEqual(self.counter.count_paragraphs(), 3)

        # Test with empty text
        self.counter.set_text("")
        self.assertEqual(self.counter.count_paragraphs(), 0)

    def test_get_word_frequency(self):
        """Test word frequency calculation."""
        freq = self.counter.get_word_frequency()

        # Check that common words are counted correctly
        self.assertEqual(freq['hello'], 2)
        self.assertEqual(freq['world'], 2)
        self.assertEqual(freq['this'], 1)
        self.assertEqual(freq['is'], 1)
        self.assertEqual(freq['a'], 1)
        self.assertEqual(freq['test'], 1)
        self.assertEqual(freq['again'], 1)

    def test_get_word_frequency_exclude_stop_words(self):
        """Test word frequency with stop words excluded."""
        freq = self.counter.get_word_frequency(exclude_stop_words=True)

        # Stop words should be excluded
        self.assertNotIn('this', freq)
        self.assertNotIn('is', freq)
        self.assertNotIn('a', freq)

        # Non-stop words should be included
        self.assertEqual(freq['hello'], 2)
        self.assertEqual(freq['world'], 2)
        self.assertEqual(freq['test'], 1)
        self.assertEqual(freq['again'], 1)

    def test_get_most_common_words(self):
        """Test getting most common words."""
        most_common = self.counter.get_most_common_words(3)

        # Should return top 3 words
        self.assertEqual(len(most_common), 3)

        # Check that they're in order
        self.assertEqual(most_common[0], ('hello', 2))
        self.assertEqual(most_common[1], ('world', 2))
        self.assertEqual(most_common[2], ('this', 1))

    def test_get_average_word_length(self):
        """Test average word length calculation."""
        # Test with sample text
        avg_length = self.counter.get_average_word_length()
        expected = (5 + 5 + 4 + 2 + 1 + 4 + 5 + 5 + 5) / 9  # Total letters / word count
        self.assertAlmostEqual(avg_length, expected, places=2)

        # Test with empty text
        self.counter.set_text("")
        self.assertEqual(self.counter.get_average_word_length(), 0.0)

    def test_get_reading_time(self):
        """Test reading time estimation."""
        # Test with sample text (9 words at 200 WPM)
        reading_time = self.counter.get_reading_time(200)
        self.assertEqual(reading_time, 9 / 200)

        # Test with custom WPM
        reading_time = self.counter.get_reading_time(100)
        self.assertEqual(reading_time, 9 / 100)

        # Test with empty text
        self.counter.set_text("")
        self.assertEqual(self.counter.get_reading_time(), 0.0)

    def test_get_statistics(self):
        """Test comprehensive statistics."""
        stats = self.counter.get_statistics()

        # Check that all required fields are present
        required_fields = [
            'filename', 'characters', 'characters_no_spaces', 'words',
            'lines', 'paragraphs', 'average_word_length', 'reading_time_minutes', 'unique_words'
        ]

        for field in required_fields:
            self.assertIn(field, stats)

        # Check some specific values
        self.assertEqual(stats['words'], 9)
        self.assertEqual(stats['lines'], 1)
        self.assertEqual(stats['paragraphs'], 1)
        self.assertGreater(stats['average_word_length'], 0)
        self.assertGreater(stats['reading_time_minutes'], 0)

    def test_read_file(self):
        """Test reading from file."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("Hello world!\nThis is a test file.")
            temp_filename = f.name

        try:
            # Test successful file read
            result = self.counter.read_file(temp_filename)
            self.assertTrue(result)
            self.assertEqual(self.counter.text, "Hello world!\nThis is a test file.")
            self.assertEqual(self.counter.filename, temp_filename)

            # Test file not found
            result = self.counter.read_file("nonexistent_file.txt")
            self.assertFalse(result)

        finally:
            # Clean up
            os.unlink(temp_filename)

    def test_analyze_text(self):
        """Test complete text analysis."""
        analysis = self.counter.analyze_text(top_words=5)

        # Check that analysis contains expected components
        self.assertIn('statistics', analysis)
        self.assertIn('most_common_words', analysis)
        self.assertIn('word_frequency', analysis)

        # Check most common words
        self.assertEqual(len(analysis['most_common_words']), 5)
        self.assertEqual(analysis['most_common_words'][0], ('hello', 2))

        # Check statistics
        stats = analysis['statistics']
        self.assertEqual(stats['words'], 9)
        self.assertGreater(stats['unique_words'], 0)


if __name__ == "__main__":
    unittest.main()
