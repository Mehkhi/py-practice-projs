"""
Command-line interface for the Markdown to HTML Converter.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

from .core import MarkdownConverter
from .server import start_preview_server


def setup_logging(verbose: bool = False) -> None:
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description="Convert Markdown files to HTML with syntax highlighting",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s input.md                    # Convert input.md to input.html
  %(prog)s input.md -o output.html     # Convert to specific output file
  %(prog)s input.md --theme github     # Use GitHub theme
  %(prog)s input.md --no-css           # Generate HTML without embedded CSS
  %(prog)s --validate input.md         # Validate markdown file
  %(prog)s --languages                 # List supported languages
  %(prog)s input.md --preview          # Start live preview server
        """
    )

    parser.add_argument(
        'input_file',
        nargs='?',
        help='Input markdown file to convert'
    )

    parser.add_argument(
        '-o', '--output',
        dest='output_file',
        help='Output HTML file (default: same name as input with .html extension)'
    )

    parser.add_argument(
        '-t', '--theme',
        default='default',
        help='Syntax highlighting theme (default: default)'
    )

    parser.add_argument(
        '--no-css',
        action='store_true',
        help='Generate HTML without embedded CSS'
    )

    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate markdown file and show statistics'
    )

    parser.add_argument(
        '--languages',
        action='store_true',
        help='List supported programming languages for syntax highlighting'
    )

    parser.add_argument(
        '--themes',
        action='store_true',
        help='List available syntax highlighting themes'
    )

    parser.add_argument(
        '--preview',
        action='store_true',
        help='Start live preview server for the markdown file'
    )

    parser.add_argument(
        '--port',
        type=int,
        default=8000,
        help='Port for preview server (default: 8000)'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )

    return parser


def validate_file(converter: MarkdownConverter, input_file: str) -> None:
    """Validate a markdown file and display statistics."""
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()

        result = converter.validate_markdown(content)

        print(f"Validation results for: {input_file}")
        print("=" * 50)

        if result['valid']:
            print("✅ File is valid markdown")
        else:
            print("❌ File has issues")

        stats = result['stats']
        print(f"\nStatistics:")
        print(f"  Lines: {stats['lines']}")
        print(f"  Characters: {stats['characters']}")
        print(f"  Words: {stats['words']}")
        print(f"  Headers: {stats['headers']}")
        print(f"  Code blocks: {stats['code_blocks']}")
        print(f"  Links: {stats['links']}")
        print(f"  Images: {stats['images']}")
        print(f"  Tables: {stats['tables']}")

        if result['warnings']:
            print(f"\nWarnings:")
            for warning in result['warnings']:
                print(f"  ⚠️  {warning}")

    except FileNotFoundError:
        print(f"❌ Error: File not found: {input_file}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error validating file: {e}")
        sys.exit(1)


def list_languages(converter: MarkdownConverter) -> None:
    """List supported programming languages."""
    languages = converter.get_supported_languages()
    print("Supported programming languages for syntax highlighting:")
    print("=" * 60)

    # Group languages by category
    categories = {
        'Web': ['html', 'css', 'javascript', 'json', 'xml'],
        'Python': ['python'],
        'Java Family': ['java', 'kotlin', 'scala'],
        'C Family': ['c', 'cpp', 'csharp'],
        'Scripting': ['bash', 'shell', 'powershell', 'ruby', 'php'],
        'Modern': ['go', 'rust', 'swift'],
        'Data': ['r', 'sql', 'yaml'],
        'Other': ['dockerfile', 'markdown', 'text']
    }

    for category, langs in categories.items():
        available_langs = [lang for lang in langs if lang in languages]
        if available_langs:
            print(f"\n{category}:")
            for lang in available_langs:
                print(f"  • {lang}")

    print(f"\nTotal: {len(languages)} languages supported")


def list_themes(converter: MarkdownConverter) -> None:
    """List available syntax highlighting themes."""
    themes = converter.get_available_themes()
    print("Available syntax highlighting themes:")
    print("=" * 40)

    # Group themes by category
    categories = {
        'Light Themes': ['default', 'vs', 'xcode', 'friendly', 'tango', 'pastie'],
        'Dark Themes': ['monokai', 'vim', 'perldoc', 'native', 'rrt', 'colorful'],
        'High Contrast': ['emacs', 'borland', 'manni', 'fruity', 'paraiso-light'],
        'Other': [theme for theme in themes if theme not in
                 ['default', 'vs', 'xcode', 'friendly', 'tango', 'pastie',
                  'monokai', 'vim', 'perldoc', 'native', 'rrt', 'colorful',
                  'emacs', 'borland', 'manni', 'fruity', 'paraiso-light']]
    }

    for category, theme_list in categories.items():
        available_themes = [theme for theme in theme_list if theme in themes]
        if available_themes:
            print(f"\n{category}:")
            for theme in available_themes:
                print(f"  • {theme}")

    print(f"\nTotal: {len(themes)} themes available")
    print("\nUse --theme <name> to apply a theme")


def main() -> None:
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args()

    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    # Handle special commands
    if args.languages:
        converter = MarkdownConverter()
        list_languages(converter)
        return

    if args.themes:
        converter = MarkdownConverter()
        list_themes(converter)
        return

    # Validate input file
    if not args.input_file:
        parser.error("Input file is required")

    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"❌ Error: Input file not found: {args.input_file}")
        sys.exit(1)

    # Create converter
    try:
        converter = MarkdownConverter(
            theme=args.theme,
            include_css=not args.no_css
        )
    except Exception as e:
        print(f"❌ Error initializing converter: {e}")
        sys.exit(1)

    # Handle validation
    if args.validate:
        validate_file(converter, args.input_file)
        return

    # Handle preview server
    if args.preview:
        try:
            start_preview_server(
                args.input_file,
                port=args.port,
                converter=converter,
                open_browser=True
            )
        except Exception as e:
            print(f"❌ Error starting preview server: {e}")
            sys.exit(1)
        return

    # Convert file
    try:
        logger.info(f"Starting conversion: {args.input_file}")
        output_file = converter.convert_file(
            args.input_file,
            args.output_file
        )
        print(f"✅ Successfully converted: {args.input_file} → {output_file}")

    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error during conversion: {e}")
        print(f"❌ Error: An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
