"""
Command-line interface for the image organizer.
"""

import logging
import sys
from pathlib import Path
from typing import Optional

import click

from .core import ImageOrganizer


def setup_logging(verbose: bool = False) -> None:
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


@click.command()
@click.argument('source_dir', type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.argument('target_dir', type=click.Path(path_type=Path))
@click.option('--dry-run', is_flag=True, help='Show what would be done without actually moving files')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.option('--thumbnails', is_flag=True, help='Create thumbnails for organized images')
@click.option('--thumbnail-size', default='150x150', help='Thumbnail size (e.g., 150x150)')
@click.option('--naming', help='Custom naming template (e.g., "{date}_{original_name}")')
@click.version_option(version='1.0.0')
def main(source_dir: Path, target_dir: Path, dry_run: bool, verbose: bool,
         thumbnails: bool, thumbnail_size: str, naming: str) -> None:
    """
    Organize images by date using EXIF data.

    SOURCE_DIR: Directory containing images to organize
    TARGET_DIR: Directory where organized images will be placed
    """
    setup_logging(verbose)
    logger = logging.getLogger(__name__)

    try:
        # Parse thumbnail size
        try:
            width, height = map(int, thumbnail_size.split('x'))
            thumbnail_size_tuple = (width, height)
        except ValueError:
            click.echo(f"Invalid thumbnail size format: {thumbnail_size}. Use format like '150x150'", err=True)
            sys.exit(1)

        # Create image organizer
        organizer = ImageOrganizer(
            source_dir=str(source_dir),
            target_dir=str(target_dir),
            dry_run=dry_run,
            create_thumbnails=thumbnails,
            thumbnail_size=thumbnail_size_tuple,
            custom_naming=naming
        )

        # Organize images
        stats = organizer.organize_images()

        # Generate and display report
        report = organizer.generate_report()
        click.echo(report)

        # Exit with appropriate code
        if stats['errors'] > 0:
            sys.exit(1)
        elif stats['processed'] == 0:
            click.echo("No images found to organize.")
            sys.exit(0)
        else:
            click.echo("Image organization completed successfully!")
            sys.exit(0)

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
