"""Main CLI entry point for the Testing Workshop text analysis tool."""

import argparse
import logging
import sys

from . import core, utils

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def setup_argparse() -> argparse.ArgumentParser:
    """Set up command line argument parser.

    Returns:
        Configured ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        description="Text Analysis CLI Tool - Analyze text files or input",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m testing_workshop "Hello world! This is a test."
  python -m testing_workshop --file sample.txt
  python -m testing_workshop --file sample.txt --words-only
        """,
    )

    parser.add_argument(
        "text", nargs="?", help="Text to analyze (if not provided, reads from file)"
    )

    parser.add_argument("--file", "-f", type=str, help="Path to text file to analyze")

    parser.add_argument(
        "--words-only", "-w", action="store_true", help="Show only word count"
    )

    parser.add_argument(
        "--chars-only", "-c", action="store_true", help="Show only character count"
    )

    parser.add_argument(
        "--frequent-words",
        "-t",
        type=int,
        default=5,
        help="Number of most frequent words to show (default: 5)",
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    return parser


def get_text_content(args: argparse.Namespace) -> str:
    """Get text content from arguments or file.

    Args:
        args: Parsed command line arguments.

    Returns:
        Text content to analyze.

    Raises:
        ValueError: If neither text nor file is provided, or file issues.
    """
    if args.file:
        if not utils.validate_file_path(args.file):
            raise ValueError(f"File not found or not readable: {args.file}")
        logger.info(f"Reading text from file: {args.file}")
        return core.read_file_content(args.file)
    elif args.text:
        return args.text
    else:
        raise ValueError("Either provide text as argument or use --file option")


def display_results(results: dict, args: argparse.Namespace) -> None:
    """Display analysis results based on command line options.

    Args:
        results: Analysis results dictionary.
        args: Parsed command line arguments.
    """
    if args.words_only:
        print(results["word_count"])
    elif args.chars_only:
        print(results["character_count_with_spaces"])
    else:
        # Update results with custom frequent words count
        if args.frequent_words != 5:
            text = get_text_content(args)  # Re-get text for frequent words
            results["most_frequent_words"] = core.get_most_frequent_words(
                text, args.frequent_words
            )

        formatted = utils.format_analysis_results(results)
        print(formatted)


def main() -> int:
    """Main entry point for the CLI tool.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    parser = setup_argparse()
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        text = get_text_content(args)
        logger.info(f"Analyzing text of length: {len(text)}")

        results = core.analyze_text(text)
        display_results(results, args)

        logger.info("Analysis completed successfully")
        return 0

    except ValueError as e:
        logger.error(f"Input error: {e}")
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
