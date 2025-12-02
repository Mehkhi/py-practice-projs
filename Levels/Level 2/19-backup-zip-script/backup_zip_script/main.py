"""Main entry point for the backup ZIP script."""

import argparse
import logging
import sys
from pathlib import Path

from .core import create_backup_zip


def setup_logging(verbose: bool = False) -> None:
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def main() -> int:
    """Main entry point for the CLI application."""
    parser = argparse.ArgumentParser(
        description="Create compressed backups with rotation and exclusion patterns",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /path/to/source --backup-dir /path/to/backups
  %(prog)s . --exclude "*.log" "*.tmp" --max-backups 5 --verbose
        """,
    )

    parser.add_argument("source_dir", type=Path, help="Directory to backup")

    parser.add_argument(
        "--backup-dir",
        type=Path,
        default=Path("./backups"),
        help="Directory to store backup files (default: ./backups)",
    )

    parser.add_argument(
        "--exclude",
        action="extend",
        nargs="+",
        default=[],
        metavar="PATTERN",
        help="Patterns to exclude (supports glob syntax; repeat or pass multiple values)",
    )

    parser.add_argument(
        "--max-backups",
        type=int,
        default=10,
        help="Maximum number of backups to keep (default: 10)",
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.verbose)

    try:
        # Create absolute paths
        source_dir = args.source_dir.resolve()
        backup_dir = args.backup_dir.resolve()

        logger = logging.getLogger(__name__)
        logger.info(f"Starting backup of {source_dir} to {backup_dir}")

        # Create backup
        backup_path = create_backup_zip(
            source_dir=source_dir,
            backup_dir=backup_dir,
            exclude_patterns=args.exclude,
            max_backups=args.max_backups,
        )

        print(f"Backup created successfully: {backup_path}")
        return 0

    except KeyboardInterrupt:
        print("\nBackup cancelled by user", file=sys.stderr)
        return 1
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Backup failed: {e}")
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
