"""
Utility functions for the Markdown to HTML Converter.
"""

import os
import tempfile
from pathlib import Path
from typing import List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


def find_markdown_files(directory: str, recursive: bool = True) -> List[str]:
    """
    Find all markdown files in a directory.

    Args:
        directory: Directory to search in
        recursive: Whether to search recursively

        Returns:
            List of markdown file paths
    """
    directory_path = Path(directory)
    if not directory_path.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")

    if not directory_path.is_dir():
        raise ValueError(f"Path is not a directory: {directory}")

    pattern = "**/*.md" if recursive else "*.md"
    markdown_files = list(directory_path.glob(pattern))

    # Also include .markdown files
    pattern_markdown = "**/*.markdown" if recursive else "*.markdown"
    markdown_files.extend(directory_path.glob(pattern_markdown))

    return [str(f) for f in sorted(markdown_files)]


def create_temp_file(content: str, suffix: str = '.md') -> str:
    """
    Create a temporary file with the given content.

    Args:
        content: Content to write to the file
        suffix: File suffix

        Returns:
            Path to the temporary file
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False) as f:
        f.write(content)
        return f.name


def cleanup_temp_file(file_path: str) -> None:
    """
    Clean up a temporary file.

    Args:
        file_path: Path to the temporary file
    """
    try:
        os.unlink(file_path)
        logger.debug(f"Cleaned up temporary file: {file_path}")
    except OSError as e:
        logger.warning(f"Could not clean up temporary file {file_path}: {e}")


def get_file_size(file_path: str) -> int:
    """
    Get the size of a file in bytes.

    Args:
        file_path: Path to the file

        Returns:
            File size in bytes
    """
    return Path(file_path).stat().st_size


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.

    Args:
        size_bytes: Size in bytes

        Returns:
            Formatted size string
    """
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1

    return f"{size_bytes:.1f} {size_names[i]}"


def validate_html(html_content: str) -> Tuple[bool, List[str]]:
    """
    Basic HTML validation.

    Args:
        html_content: HTML content to validate

        Returns:
            Tuple of (is_valid, list_of_issues)
    """
    issues = []

    # Check for basic HTML structure
    if '<html' not in html_content.lower():
        issues.append("Missing <html> tag")

    if '<head' not in html_content.lower():
        issues.append("Missing <head> tag")

    if '<body' not in html_content.lower():
        issues.append("Missing <body> tag")

    # Check for unclosed tags (basic check)
    open_tags = []
    tag_pattern = r'<(/?)([a-zA-Z][a-zA-Z0-9]*)[^>]*>'
    import re

    for match in re.finditer(tag_pattern, html_content):
        is_closing = bool(match.group(1))
        tag_name = match.group(2).lower()

        if is_closing:
            if not open_tags or open_tags[-1] != tag_name:
                issues.append(f"Unmatched closing tag: </{tag_name}>")
            else:
                open_tags.pop()
        else:
            # Self-closing tags
            if not match.group(0).endswith('/>'):
                open_tags.append(tag_name)

    if open_tags:
        issues.append(f"Unclosed tags: {', '.join(open_tags)}")

    return len(issues) == 0, issues


def extract_metadata(content: str) -> dict:
    """
    Extract metadata from markdown content (YAML front matter).

    Args:
        content: Markdown content

        Returns:
            Dictionary with extracted metadata
    """
    metadata = {}

    if not content.startswith('---'):
        return metadata

    lines = content.split('\n')
    if len(lines) < 2:
        return metadata

    # Find end of front matter
    end_index = -1
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == '---':
            end_index = i
            break

    if end_index == -1:
        return metadata

    # Parse front matter
    for line in lines[1:end_index]:
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip().strip('"\'')
            metadata[key] = value

    return metadata


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename for safe filesystem usage.

    Args:
        filename: Original filename

        Returns:
            Sanitized filename
    """
    import re

    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)

    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')

    # Ensure it's not empty
    if not filename:
        filename = 'untitled'

    # Limit length
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255-len(ext)] + ext

    return filename


def get_theme_preview(theme: str) -> str:
    """
    Get a preview of what a theme looks like.

    Args:
        theme: Theme name

        Returns:
            HTML preview of the theme
    """
    sample_code = '''
def hello_world():
    """A simple hello world function."""
    print("Hello, World!")
    return True

# This is a comment
numbers = [1, 2, 3, 4, 5]
for num in numbers:
    if num % 2 == 0:
        print(f"{num} is even")
    else:
        print(f"{num} is odd")
'''

    try:
        from pygments import highlight
        from pygments.lexers import PythonLexer
        from pygments.formatters import HtmlFormatter

        lexer = PythonLexer()
        formatter = HtmlFormatter(style=theme, cssclass="highlight")

        highlighted = highlight(sample_code, lexer, formatter)
        css = formatter.get_style_defs('.highlight')

        return f"""
        <html>
        <head><style>{css}</style></head>
        <body>
        <h3>Theme Preview: {theme}</h3>
        {highlighted}
        </body>
        </html>
        """
    except Exception as e:
        return f"<p>Could not generate preview for theme '{theme}': {e}</p>"
