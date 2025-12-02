"""Comprehensive tests for the Testing Workshop text analysis tool."""

import pytest
from unittest.mock import mock_open, patch

from testing_workshop import core, utils, main


class TestCoreFunctions:
    """Test core text analysis functions."""

    @pytest.fixture
    def sample_text(self):
        """Fixture providing sample text for testing."""
        return "Hello world! This is a test. Hello again."

    @pytest.fixture
    def empty_text(self):
        """Fixture providing empty text."""
        return ""

    def test_count_words_basic(self, sample_text):
        """Test basic word counting functionality."""
        assert core.count_words(sample_text) == 8

    def test_count_words_empty(self, empty_text):
        """Test word counting with empty text."""
        assert core.count_words(empty_text) == 0

    @pytest.mark.parametrize(
        "text,expected",
        [
            ("Hello world", 11),
            ("Hello   world", 13),  # Multiple spaces
            ("Hello\nworld", 11),  # Newline
            ("Hello\tworld", 11),  # Tab
        ],
    )
    def test_count_characters_with_spaces(self, text, expected):
        """Test character counting with spaces included."""
        assert core.count_characters(text, include_spaces=True) == expected

    @pytest.mark.parametrize(
        "text,expected",
        [
            ("Hello world", 10),
            ("Hello   world", 10),  # Multiple spaces removed
            ("Hello\nworld", 10),  # Newline removed
            ("Hello\tworld", 10),  # Tab removed
        ],
    )
    def test_count_characters_no_spaces(self, text, expected):
        """Test character counting with spaces excluded."""
        assert core.count_characters(text, include_spaces=False) == expected

    def test_get_most_frequent_words(self, sample_text):
        """Test getting most frequent words."""
        result = core.get_most_frequent_words(sample_text, 3)
        expected = [("hello", 2), ("world", 1), ("this", 1)]
        assert result == expected

    def test_get_most_frequent_words_empty(self, empty_text):
        """Test most frequent words with empty text."""
        assert core.get_most_frequent_words(empty_text) == []

    def test_estimate_reading_time(self, sample_text):
        """Test reading time estimation."""
        result = core.estimate_reading_time(sample_text)
        # 8 words at 200 wpm = 0.04 minutes
        assert abs(result - 0.04) < 0.001

    def test_estimate_reading_time_empty(self, empty_text):
        """Test reading time with empty text."""
        assert core.estimate_reading_time(empty_text) == 0.0

    def test_analyze_text_comprehensive(self, sample_text):
        """Test comprehensive text analysis."""
        result = core.analyze_text(sample_text)

        assert result["word_count"] == 8
        assert result["character_count_with_spaces"] == 41
        assert result["character_count_no_spaces"] == 34
        assert len(result["most_frequent_words"]) == 5
        assert result["estimated_reading_time"] > 0
        assert result["line_count"] == 1


class TestFileOperations:
    """Test file reading functionality."""

    @patch("builtins.open", new_callable=mock_open, read_data="File content here.")
    def test_read_file_content_success(self, mock_file):
        """Test successful file reading."""
        result = core.read_file_content("test.txt")
        assert result == "File content here."
        mock_file.assert_called_once_with("test.txt", "r", encoding="utf-8")

    @patch("builtins.open")
    def test_read_file_content_not_found(self, mock_open_func):
        """Test file not found error."""
        mock_open_func.side_effect = FileNotFoundError("File not found")
        with pytest.raises(FileNotFoundError, match="File not found: nonexistent.txt"):
            core.read_file_content("nonexistent.txt")

    @patch("builtins.open")
    def test_read_file_content_io_error(self, mock_open_func):
        """Test IO error during file reading."""
        mock_open_func.side_effect = IOError("Permission denied")
        with pytest.raises(IOError, match="Error reading file test.txt"):
            core.read_file_content("test.txt")


class TestUtils:
    """Test utility functions."""

    def test_format_analysis_results(self):
        """Test formatting of analysis results."""
        results = {
            "word_count": 10,
            "character_count_with_spaces": 50,
            "character_count_no_spaces": 40,
            "line_count": 2,
            "estimated_reading_time": 0.05,
            "most_frequent_words": [("hello", 2), ("world", 1)],
        }
        formatted = utils.format_analysis_results(results)
        assert "Word count: 10" in formatted
        assert "Characters (with spaces): 50" in formatted
        assert "Most frequent words:" in formatted
        assert "hello: 2" in formatted
        assert "Estimated reading time: 0.1 minutes" in formatted

    @pytest.mark.parametrize(
        "file_exists,readable,expected",
        [
            (True, True, True),
            (True, False, False),
            (False, True, False),
            (False, False, False),
        ],
    )
    def test_validate_file_path(self, file_exists, readable, expected, tmp_path):
        """Test file path validation with different scenarios."""
        if file_exists:
            test_file = tmp_path / "test.txt"
            test_file.write_text("test")
            if not readable:
                test_file.chmod(0o000)  # Remove all permissions

        file_path = str(tmp_path / "test.txt") if file_exists else "nonexistent.txt"
        assert utils.validate_file_path(file_path) == expected

    @pytest.mark.parametrize(
        "text,max_length,expected",
        [
            ("Short text", 20, "Short text"),
            (
                "This is a very long text that should be truncated",
                20,
                "This is a very lo...",
            ),
            ("", 10, ""),
        ],
    )
    def test_truncate_text(self, text, max_length, expected):
        """Test text truncation functionality."""
        assert utils.truncate_text(text, max_length) == expected

    @pytest.mark.parametrize(
        "value,default,expected",
        [
            ("42", 0, 42),
            ("not_a_number", 10, 10),
            ("", 5, 5),
            (None, 7, 7),
        ],
    )
    def test_safe_int_conversion(self, value, default, expected):
        """Test safe integer conversion."""
        assert utils.safe_int_conversion(value, default) == expected


class TestCLI:
    """Test CLI functionality."""

    @patch("testing_workshop.main.core.analyze_text")
    @patch("builtins.print")
    def test_main_with_text_argument(self, mock_print, mock_analyze):
        """Test CLI with direct text input."""
        mock_analyze.return_value = {
            "word_count": 3,
            "character_count_with_spaces": 15,
            "character_count_no_spaces": 13,
            "most_frequent_words": [],
            "estimated_reading_time": 0.015,
            "line_count": 1,
        }

        with patch("sys.argv", ["main.py", "hello world test"]):
            result = main.main()
            assert result == 0
            mock_analyze.assert_called_once_with("hello world test")

    @patch("testing_workshop.main.utils.validate_file_path")
    @patch("testing_workshop.main.core.read_file_content")
    @patch("testing_workshop.main.core.analyze_text")
    @patch("builtins.print")
    def test_main_with_file_argument(
        self, mock_print, mock_analyze, mock_read_file, mock_validate
    ):
        """Test CLI with file input."""
        mock_validate.return_value = True
        mock_read_file.return_value = "file content"
        mock_analyze.return_value = {
            "word_count": 2,
            "character_count_with_spaces": 12,
            "character_count_no_spaces": 10,
            "most_frequent_words": [],
            "estimated_reading_time": 0.01,
            "line_count": 1,
        }

        with patch("sys.argv", ["main.py", "--file", "test.txt"]):
            result = main.main()
            assert result == 0
            mock_read_file.assert_called_once_with("test.txt")
            mock_analyze.assert_called_once_with("file content")

    @patch("builtins.print")
    def test_main_no_arguments_error(self, mock_print):
        """Test CLI error when no text or file provided."""
        with patch("sys.argv", ["main.py"]):
            result = main.main()
            assert result == 1

    @patch("testing_workshop.main.core.read_file_content")
    @patch("builtins.print")
    def test_main_file_not_found_error(self, mock_print, mock_read_file):
        """Test CLI error when file not found."""
        mock_read_file.side_effect = FileNotFoundError("File not found: missing.txt")

        with patch("sys.argv", ["main.py", "--file", "missing.txt"]):
            result = main.main()
            assert result == 1
