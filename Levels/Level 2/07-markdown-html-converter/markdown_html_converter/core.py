"""
Core markdown to HTML conversion functionality.
"""

import logging
import re
from typing import Optional, Dict, Any
from pathlib import Path

import markdown
from pygments import highlight
from pygments.lexers import get_lexer_by_name, TextLexer
from pygments.formatters import HtmlFormatter
from pygments.util import ClassNotFound

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MarkdownConverter:
    """Main class for converting Markdown to HTML with syntax highlighting."""

    def __init__(self, theme: str = "default", include_css: bool = True):
        """
        Initialize the MarkdownConverter.

        Args:
            theme: CSS theme name for syntax highlighting
            include_css: Whether to include CSS in the output HTML
        """
        self.theme = theme
        self.include_css = include_css

        # Validate theme and fallback to default if invalid
        try:
            self.formatter = HtmlFormatter(style=theme, cssclass="highlight")
        except ClassNotFound:
            logger.warning(f"Theme '{theme}' not found, falling back to 'default'")
            self.theme = "default"
            self.formatter = HtmlFormatter(style="default", cssclass="highlight")

        # Configure markdown with extensions
        self.md = markdown.Markdown(
            extensions=[
                'codehilite',
                'fenced_code',
                'tables',
                'toc',
                'nl2br',
                'sane_lists'
            ],
            extension_configs={
                'codehilite': {
                    'css_class': 'highlight',
                    'use_pygments': True,
                    'noclasses': False,
                }
            }
        )

    def convert_file(self, input_path: str, output_path: Optional[str] = None) -> str:
        """
        Convert a markdown file to HTML.

        Args:
            input_path: Path to input markdown file
            output_path: Path for output HTML file (optional)

        Returns:
            Path to the generated HTML file

        Raises:
            FileNotFoundError: If input file doesn't exist
            ValueError: If input file is not a markdown file
        """
        input_file = Path(input_path)

        if not input_file.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        if not input_file.suffix.lower() in ['.md', '.markdown']:
            raise ValueError(f"Input file must be a markdown file (.md or .markdown): {input_path}")

        logger.info(f"Converting markdown file: {input_path}")

        # Read markdown content
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                markdown_content = f.read()
        except UnicodeDecodeError:
            logger.error(f"Could not decode file {input_path}. Trying with latin-1 encoding.")
            with open(input_file, 'r', encoding='latin-1') as f:
                markdown_content = f.read()

        # Convert to HTML
        html_content = self.convert_text(markdown_content)

        # Determine output path
        if output_path is None:
            output_file = input_file.with_suffix('.html')
        else:
            output_file = Path(output_path)

        # Write HTML file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        logger.info(f"HTML file generated: {output_file}")
        return str(output_file)

    def convert_text(self, markdown_text: str) -> str:
        """
        Convert markdown text to HTML.

        Args:
            markdown_text: Markdown content as string

        Returns:
            Complete HTML document as string
        """
        # Convert markdown to HTML
        html_body = self.md.convert(markdown_text)

        # Reset markdown instance for next conversion
        self.md.reset()

        # Generate CSS if needed
        css = ""
        if self.include_css:
            css = self._generate_css()

        # Create complete HTML document
        html_document = self._create_html_document(html_body, css)

        return html_document

    def _generate_css(self) -> str:
        """Generate CSS for syntax highlighting and basic styling."""
        # Get Pygments CSS
        pygments_css = self.formatter.get_style_defs('.highlight')

        # Additional custom CSS
        custom_css = """
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #fff;
        }

        h1, h2, h3, h4, h5, h6 {
            color: #2c3e50;
            margin-top: 2em;
            margin-bottom: 1em;
        }

        h1 { border-bottom: 2px solid #3498db; padding-bottom: 10px; }
        h2 { border-bottom: 1px solid #bdc3c7; padding-bottom: 5px; }

        code {
            background-color: #f8f9fa;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-size: 0.9em;
        }

        pre {
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 6px;
            padding: 16px;
            overflow-x: auto;
            margin: 1em 0;
        }

        pre code {
            background-color: transparent;
            padding: 0;
        }

        blockquote {
            border-left: 4px solid #3498db;
            margin: 1em 0;
            padding-left: 1em;
            color: #666;
            font-style: italic;
        }

        table {
            border-collapse: collapse;
            width: 100%;
            margin: 1em 0;
        }

        th, td {
            border: 1px solid #ddd;
            padding: 8px 12px;
            text-align: left;
        }

        th {
            background-color: #f2f2f2;
            font-weight: bold;
        }

        ul, ol {
            margin: 1em 0;
            padding-left: 2em;
        }

        li {
            margin: 0.5em 0;
        }

        a {
            color: #3498db;
            text-decoration: none;
        }

        a:hover {
            text-decoration: underline;
        }

        hr {
            border: none;
            border-top: 1px solid #ddd;
            margin: 2em 0;
        }
        """

        return f"<style>\n{pygments_css}\n{custom_css}\n</style>"

    def _create_html_document(self, body: str, css: str) -> str:
        """Create a complete HTML document with the given body and CSS."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Markdown to HTML Converter</title>
    {css}
</head>
<body>
{body}
</body>
</html>"""

    def get_supported_languages(self) -> list:
        """Get list of supported programming languages for syntax highlighting."""
        # This is a subset of commonly used languages
        return [
            'python', 'javascript', 'java', 'c', 'cpp', 'csharp', 'php',
            'ruby', 'go', 'rust', 'swift', 'kotlin', 'scala', 'r',
            'sql', 'html', 'css', 'xml', 'yaml', 'json', 'bash', 'shell',
            'powershell', 'dockerfile', 'markdown', 'text'
        ]

    def get_available_themes(self) -> list:
        """Get list of available Pygments themes."""
        from pygments.styles import get_all_styles
        return list(get_all_styles())

    def validate_markdown(self, content: str) -> Dict[str, Any]:
        """
        Validate markdown content and return statistics.

        Args:
            content: Markdown content to validate

        Returns:
            Dictionary with validation results and statistics
        """
        stats = {
            'lines': len(content.splitlines()),
            'characters': len(content),
            'words': len(content.split()),
            'headers': len(re.findall(r'^#+\s+', content, re.MULTILINE)),
            'code_blocks': len(re.findall(r'```', content)) // 2,
            'links': len(re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)),
            'images': len(re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', content)),
            'tables': len(re.findall(r'\|.*\|', content)),
        }

        return {
            'valid': True,
            'stats': stats,
            'warnings': []
        }
