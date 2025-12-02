"""Command-line interface for CSV Cleaner."""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

from .core import CSVCleaner


def setup_logging(verbose: bool = False) -> None:
    """Setup logging configuration.

    Args:
        verbose: Enable verbose logging
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def validate_file_path(file_path: str) -> str:
    """Validate that file path exists and is readable.

    Args:
        file_path: Path to validate

    Returns:
        Validated file path

    Raises:
        FileNotFoundError: If file doesn't exist
        PermissionError: If file is not readable
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if not path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")

    if not path.stat().st_size > 0:
        raise ValueError(f"File is empty: {file_path}")

    return str(path.absolute())


def create_output_path(input_path: str, output_path: Optional[str] = None) -> str:
    """Create output path from input path if not provided.

    Args:
        input_path: Input file path
        output_path: Optional output path

    Returns:
        Output file path
    """
    if output_path:
        return output_path

    input_path = Path(input_path)
    return str(input_path.parent / f"{input_path.stem}_cleaned{input_path.suffix}")


def main() -> int:
    """Main entry point for CSV Cleaner CLI.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = argparse.ArgumentParser(
        description="CSV Data Cleaner - Clean and validate CSV files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic cleaning
  python -m csv_cleaner input.csv

  # Specify output file
  python -m csv_cleaner input.csv -o cleaned_output.csv

  # Use configuration file
  python -m csv_cleaner input.csv -c config.yaml

  # Verbose output
  python -m csv_cleaner input.csv -v

  # Show help
  python -m csv_cleaner -h
        """
    )

    parser.add_argument(
        'input_file',
        help='Input CSV file to clean'
    )

    parser.add_argument(
        '-o', '--output',
        help='Output CSV file path (default: input_cleaned.csv)'
    )

    parser.add_argument(
        '-c', '--config',
        help='YAML configuration file path'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    parser.add_argument(
        '--version',
        action='version',
        version='CSV Cleaner 1.0.0'
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    try:
        # Validate input file
        input_path = validate_file_path(args.input_file)
        logger.info(f"Input file validated: {input_path}")

        # Create output path
        output_path = create_output_path(input_path, args.output)
        logger.info(f"Output will be saved to: {output_path}")

        # Initialize cleaner
        cleaner = CSVCleaner(config_path=args.config)

        # Clean CSV
        logger.info("Starting CSV cleaning process...")
        cleaned_df = cleaner.clean_csv(input_path)

        # Export results
        cleaner.export_cleaned_csv(cleaned_df, output_path)

        # Print summary
        stats = cleaner.cleaning_stats
        print(f"\n✅ CSV cleaning completed successfully!")
        print(f"📊 Summary:")
        print(f"   • Original rows: {stats['original_rows']}")
        print(f"   • Cleaned rows: {stats['cleaned_rows']}")
        print(f"   • Dropped rows: {stats['dropped_rows']}")
        print(f"   • Columns normalized: {stats['columns_normalized']}")
        print(f"   • Missing values filled: {stats['missing_values_filled']}")
        print(f"   • Type conversions: {stats['type_conversions']}")
        print(f"   • Outliers detected: {stats['outliers_detected']}")
        print(f"📁 Output saved to: {output_path}")

        if cleaner.error_log:
            print(f"⚠️  {len(cleaner.error_log)} warnings/errors logged")

        return 0

    except FileNotFoundError as e:
        logger.error(f"File error: {e}")
        print(f"❌ Error: {e}")
        return 1

    except PermissionError as e:
        logger.error(f"Permission error: {e}")
        print(f"❌ Error: {e}")
        return 1

    except ValueError as e:
        logger.error(f"Value error: {e}")
        print(f"❌ Error: {e}")
        return 1

    except Exception as e:
        import traceback
        logger.error(f"Unexpected error: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        print(f"❌ Unexpected error: {e}")
        if args.verbose:
            print(f"Traceback: {traceback.format_exc()}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
