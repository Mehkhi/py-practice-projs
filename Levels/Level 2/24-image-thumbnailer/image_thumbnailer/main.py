"""Command-line interface for image thumbnailer."""

import argparse
import sys
from pathlib import Path

from . import core
from .utils import parse_size, setup_logging, validate_directory, validate_image_path


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser.

    Returns:
        Configured ArgumentParser
    """
    parser = argparse.ArgumentParser(
        description="Create thumbnails from images",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create thumbnail from single image
  python -m image_thumbnailer image.jpg -s 200x200 -o thumb.jpg

  # Batch process directory
  python -m image_thumbnailer input_dir/ -d output_dir/ -s 300x300

  # Add watermark and border
  python -m image_thumbnailer image.png -o thumb.png -w "Copyright" -b 5
        """,
    )

    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "input_path", nargs="?", type=Path, help="Path to input image file"
    )
    input_group.add_argument(
        "-i", "--input-dir", type=Path, help="Directory containing images to process"
    )

    # Output options
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output file path (for single image) or output directory (for batch)",
    )
    parser.add_argument(
        "-d", "--output-dir", type=Path, help="Output directory for batch processing"
    )

    # Size options
    parser.add_argument(
        "-s",
        "--size",
        type=str,
        default="200x200",
        help="Thumbnail size in WIDTHxHEIGHT format (default: 200x200)",
    )

    # Processing options
    parser.add_argument(
        "--no-aspect",
        action="store_true",
        help="Do not maintain aspect ratio (force exact size)",
    )

    parser.add_argument("-w", "--watermark", type=str, help="Add watermark text")

    parser.add_argument(
        "--watermark-position",
        choices=["bottom-right", "bottom-left", "top-right", "top-left"],
        default="bottom-right",
        help="Watermark position (default: bottom-right)",
    )

    parser.add_argument(
        "-b",
        "--border",
        type=int,
        default=0,
        help="Add border with specified width in pixels",
    )

    parser.add_argument(
        "--border-color",
        type=str,
        default="black",
        help="Border color (default: black)",
    )

    parser.add_argument(
        "-q",
        "--quality",
        type=int,
        default=85,
        choices=range(1, 101),
        metavar="[1-100]",
        help="JPEG/WebP quality (default: 85)",
    )

    # Logging options
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose logging"
    )

    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Set logging level (default: INFO)",
    )

    return parser


def main() -> int:
    """Main entry point for the CLI application.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = create_parser()
    args = parser.parse_args()

    # Setup logging
    log_level = "DEBUG" if args.verbose else args.log_level
    setup_logging(log_level)

    # Parse size
    size = parse_size(args.size)
    if not size:
        return 1

    # Determine mode and validate inputs
    if args.input_path:
        # Single file mode
        if not validate_image_path(args.input_path):
            return 1

        if not args.output:
            # Generate default output name
            output_path = args.input_path.parent / f"thumb_{args.input_path.name}"
        else:
            output_path = args.output

        # Create thumbnail
        success = core.create_thumbnail(
            input_path=args.input_path,
            output_path=output_path,
            size=size,
            maintain_aspect=not args.no_aspect,
            watermark_text=args.watermark,
            border_width=args.border,
            quality=args.quality,
        )

        if success:
            print(f"Thumbnail created: {output_path}")
            return 0
        else:
            print("Failed to create thumbnail", file=sys.stderr)
            return 1

    elif args.input_dir:
        # Batch mode
        if not validate_directory(args.input_dir):
            return 1

        if args.output_dir:
            output_dir = args.output_dir
        elif args.output:
            output_dir = args.output
        else:
            output_dir = args.input_dir / "thumbnails"

        if not validate_directory(output_dir, create_if_missing=True):
            return 1

        # Process batch
        count = core.batch_create_thumbnails(
            input_dir=args.input_dir,
            output_dir=output_dir,
            size=size,
            maintain_aspect=not args.no_aspect,
            watermark_text=args.watermark,
            border_width=args.border,
            quality=args.quality,
        )

        print(f"Created {count} thumbnails in {output_dir}")
        return 0

    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
