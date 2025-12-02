"""
Tests for the Markdown to HTML Converter.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, mock_open

from markdown_html_converter.core import MarkdownConverter
from markdown_html_converter.utils import (
    find_markdown_files,
    create_temp_file,
    cleanup_temp_file,
    get_file_size,
    format_file_size,
    validate_html,
    extract_metadata,
    sanitize_filename
)


class TestMarkdownConverter:
    """Test cases for MarkdownConverter class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.converter = MarkdownConverter()

    def test_initialization(self):
        """Test converter initialization."""
        converter = MarkdownConverter(theme="default", include_css=False)
        assert converter.theme == "default"
        assert converter.include_css is False

    def test_convert_text_basic(self):
        """Test basic markdown to HTML conversion."""
        markdown_text = "# Hello World\n\nThis is a **bold** text."
        html = self.converter.convert_text(markdown_text)

        assert "<h1" in html and "Hello World" in html
        assert "<strong>bold</strong>" in html
        assert "<!DOCTYPE html>" in html
        assert "<html" in html

    def test_convert_text_with_code_blocks(self):
        """Test conversion with code blocks."""
        markdown_text = """
```python
def hello():
    print("Hello, World!")
```
"""
        html = self.converter.convert_text(markdown_text)

        assert "hello" in html
        assert "print" in html
        assert "highlight" in html  # CSS class for syntax highlighting

    def test_convert_text_with_tables(self):
        """Test conversion with tables."""
        markdown_text = """
| Name | Age | City |
|------|-----|------|
| John | 25  | NYC  |
| Jane | 30  | LA   |
"""
        html = self.converter.convert_text(markdown_text)

        assert "<table>" in html
        assert "<th>Name</th>" in html
        assert "<td>John</td>" in html

    def test_convert_text_with_lists(self):
        """Test conversion with lists."""
        markdown_text = """
- Item 1
- Item 2
  - Nested item
- Item 3

1. First
2. Second
3. Third
"""
        html = self.converter.convert_text(markdown_text)

        assert "<ul>" in html
        assert "<li>Item 1</li>" in html
        assert "<ol>" in html
        assert "<li>First</li>" in html

    def test_convert_text_with_links_and_images(self):
        """Test conversion with links and images."""
        markdown_text = """
[Google](https://google.com)
![Alt text](image.jpg)
"""
        html = self.converter.convert_text(markdown_text)

        assert 'href="https://google.com"' in html
        assert 'src="image.jpg"' in html
        assert 'alt="Alt text"' in html

    def test_convert_text_without_css(self):
        """Test conversion without CSS."""
        converter = MarkdownConverter(include_css=False)
        markdown_text = "# Test"
        html = converter.convert_text(markdown_text)

        assert "<style>" not in html

    def test_convert_file_success(self):
        """Test successful file conversion."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# Test File\n\nThis is a test.")
            temp_file = f.name

        try:
            output_file = self.converter.convert_file(temp_file)
            assert os.path.exists(output_file)

            with open(output_file, 'r') as f:
                content = f.read()
                assert "<h1" in content and "Test File" in content
        finally:
            os.unlink(temp_file)
            if os.path.exists(output_file):
                os.unlink(output_file)

    def test_convert_file_with_output_path(self):
        """Test file conversion with specific output path."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# Test")
            temp_file = f.name

        with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as f:
            output_path = f.name

        try:
            result = self.converter.convert_file(temp_file, output_path)
            assert result == output_path
            assert os.path.exists(output_path)
        finally:
            os.unlink(temp_file)
            if os.path.exists(output_path):
                os.unlink(output_path)

    def test_convert_file_not_found(self):
        """Test file conversion with non-existent file."""
        with pytest.raises(FileNotFoundError):
            self.converter.convert_file("nonexistent.md")

    def test_convert_file_invalid_extension(self):
        """Test file conversion with invalid file extension."""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            temp_file = f.name

        try:
            with pytest.raises(ValueError, match="must be a markdown file"):
                self.converter.convert_file(temp_file)
        finally:
            os.unlink(temp_file)

    def test_validate_markdown(self):
        """Test markdown validation."""
        content = """# Title

This is a paragraph with **bold** text.

```python
def test():
    pass
```

- List item 1
- List item 2
"""
        result = self.converter.validate_markdown(content)

        assert result['valid'] is True
        assert result['stats']['lines'] > 0
        assert result['stats']['headers'] == 1
        assert result['stats']['code_blocks'] == 1

    def test_get_supported_languages(self):
        """Test getting supported languages."""
        languages = self.converter.get_supported_languages()
        assert isinstance(languages, list)
        assert 'python' in languages
        assert 'javascript' in languages
        assert 'html' in languages


class TestUtils:
    """Test cases for utility functions."""

    def test_find_markdown_files(self):
        """Test finding markdown files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            Path(temp_dir, "test1.md").write_text("# Test 1")
            Path(temp_dir, "test2.markdown").write_text("# Test 2")
            Path(temp_dir, "subdir").mkdir(parents=True)
            Path(temp_dir, "subdir", "test3.md").write_text("# Test 3")
            Path(temp_dir, "not_md.txt").write_text("Not markdown")

            # Test recursive search
            files = find_markdown_files(temp_dir, recursive=True)
            assert len(files) == 3
            assert any("test1.md" in f for f in files)
            assert any("test2.markdown" in f for f in files)
            assert any("test3.md" in f for f in files)

            # Test non-recursive search
            files = find_markdown_files(temp_dir, recursive=False)
            assert len(files) == 2

    def test_find_markdown_files_nonexistent_directory(self):
        """Test finding markdown files in non-existent directory."""
        with pytest.raises(FileNotFoundError):
            find_markdown_files("/nonexistent/directory")

    def test_find_markdown_files_not_directory(self):
        """Test finding markdown files when path is not a directory."""
        with tempfile.NamedTemporaryFile() as f:
            with pytest.raises(ValueError):
                find_markdown_files(f.name)

    def test_create_temp_file(self):
        """Test creating temporary file."""
        content = "Test content"
        temp_file = create_temp_file(content, ".md")

        try:
            assert os.path.exists(temp_file)
            with open(temp_file, 'r') as f:
                assert f.read() == content
        finally:
            cleanup_temp_file(temp_file)

    def test_cleanup_temp_file(self):
        """Test cleaning up temporary file."""
        temp_file = create_temp_file("test")
        assert os.path.exists(temp_file)

        cleanup_temp_file(temp_file)
        assert not os.path.exists(temp_file)

    def test_get_file_size(self):
        """Test getting file size."""
        with tempfile.NamedTemporaryFile(mode='w') as f:
            f.write("test content")
            f.flush()
            size = get_file_size(f.name)
            assert size > 0

    def test_format_file_size(self):
        """Test formatting file size."""
        assert format_file_size(0) == "0 B"
        assert format_file_size(1024) == "1.0 KB"
        assert format_file_size(1024 * 1024) == "1.0 MB"

    def test_validate_html_valid(self):
        """Test HTML validation with valid HTML."""
        html = "<html><head><title>Test</title></head><body><p>Hello</p></body></html>"
        is_valid, issues = validate_html(html)
        assert is_valid
        assert len(issues) == 0

    def test_validate_html_invalid(self):
        """Test HTML validation with invalid HTML."""
        html = "<html><head><title>Test</head><body><p>Hello</body>"
        is_valid, issues = validate_html(html)
        assert not is_valid
        assert len(issues) > 0

    def test_extract_metadata(self):
        """Test extracting metadata from markdown."""
        content = """---
title: Test Document
author: John Doe
date: 2023-01-01
---

# Content starts here
"""
        metadata = extract_metadata(content)
        assert metadata['title'] == 'Test Document'
        assert metadata['author'] == 'John Doe'
        assert metadata['date'] == '2023-01-01'

    def test_extract_metadata_no_frontmatter(self):
        """Test extracting metadata from markdown without frontmatter."""
        content = "# Just a heading\n\nNo metadata here."
        metadata = extract_metadata(content)
        assert metadata == {}

    def test_sanitize_filename(self):
        """Test filename sanitization."""
        assert sanitize_filename("test<file>.md") == "test_file_.md"
        assert sanitize_filename("file:with|bad*chars?.txt") == "file_with_bad_chars_.txt"
        assert sanitize_filename("") == "untitled"
        assert sanitize_filename(".") == "untitled"
        assert sanitize_filename("  ") == "untitled"


class TestIntegration:
    """Integration tests."""

    def test_full_conversion_workflow(self):
        """Test complete conversion workflow."""
        markdown_content = """# Sample Document

This is a **sample** markdown document with various elements.

## Code Example

```python
def hello_world():
    print("Hello, World!")
    return True
```

## List

- Item 1
- Item 2
- Item 3

## Table

| Name | Value |
|------|-------|
| A    | 1     |
| B    | 2     |

## Link

[Visit Google](https://google.com)
"""

        converter = MarkdownConverter()
        html = converter.convert_text(markdown_content)

        # Check basic structure
        assert "<!DOCTYPE html>" in html
        assert "<html" in html
        assert "<head>" in html
        assert "<body>" in html

        # Check content
        assert "<h1" in html and "Sample Document" in html
        assert "<strong>sample</strong>" in html
        assert "hello_world" in html
        assert "<table>" in html
        assert 'href="https://google.com"' in html

        # Check CSS is included
        assert "<style>" in html
        assert "highlight" in html  # Pygments CSS class


if __name__ == '__main__':
    pytest.main([__file__])
