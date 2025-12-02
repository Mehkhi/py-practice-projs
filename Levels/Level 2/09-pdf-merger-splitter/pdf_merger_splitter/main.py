"""Main CLI interface for PDF Merger & Splitter."""

import argparse
import logging
import sys
from pathlib import Path
from typing import List, Optional

from .core import PDFProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser.

    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        prog='pdf-merger-splitter',
        description='A CLI tool for merging, splitting, and manipulating PDF files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Merge PDFs
  %(prog)s merge -o output.pdf file1.pdf file2.pdf file3.pdf

  # Split PDF into individual pages
  %(prog)s split input.pdf -o output_dir/

  # Extract specific pages
  %(prog)s extract input.pdf -o extracted.pdf -p "1-3,5,7-9"

  # Add watermark
  %(prog)s watermark input.pdf -o watermarked.pdf -t "CONFIDENTIAL"

  # Rotate pages
  %(prog)s rotate input.pdf -o rotated.pdf -r 90 -p "1-3"

  # Encrypt PDF
  %(prog)s encrypt input.pdf -o encrypted.pdf --password "secret123"

  # Add page numbers
  %(prog)s pagenumbers input.pdf -o numbered.pdf --position bottom
        """
    )

    # Global arguments
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Merge command
    merge_parser = subparsers.add_parser('merge', help='Merge multiple PDF files')
    merge_parser.add_argument(
        'input_files',
        nargs='+',
        help='Input PDF files to merge'
    )
    merge_parser.add_argument(
        '-o', '--output',
        required=True,
        help='Output PDF file path'
    )
    merge_parser.add_argument(
        '--no-preserve-metadata',
        action='store_true',
        help='Do not preserve metadata from first PDF'
    )

    # Split command
    split_parser = subparsers.add_parser('split', help='Split PDF into multiple files')
    split_parser.add_argument('input_file', help='Input PDF file to split')
    split_parser.add_argument(
        '-o', '--output',
        required=True,
        help='Output directory for split files'
    )
    split_parser.add_argument(
        '-r', '--ranges',
        nargs='*',
        help='Page ranges for splitting (e.g., "1-3" "4-6"). If not specified, splits each page.'
    )

    # Extract command
    extract_parser = subparsers.add_parser('extract', help='Extract specific pages from PDF')
    extract_parser.add_argument('input_file', help='Input PDF file')
    extract_parser.add_argument(
        '-o', '--output',
        required=True,
        help='Output PDF file path'
    )
    extract_parser.add_argument(
        '-p', '--pages',
        required=True,
        help='Page range to extract (e.g., "1-3,5,7-9")'
    )

    # Watermark command
    watermark_parser = subparsers.add_parser('watermark', help='Add watermark to PDF')
    watermark_parser.add_argument('input_file', help='Input PDF file')
    watermark_parser.add_argument(
        '-o', '--output',
        required=True,
        help='Output PDF file path'
    )
    watermark_parser.add_argument(
        '-t', '--text',
        required=True,
        help='Watermark text'
    )
    watermark_parser.add_argument(
        '--opacity',
        type=float,
        default=0.3,
        help='Watermark opacity (0.0 to 1.0, default: 0.3)'
    )

    # Rotate command
    rotate_parser = subparsers.add_parser('rotate', help='Rotate pages in PDF')
    rotate_parser.add_argument('input_file', help='Input PDF file')
    rotate_parser.add_argument(
        '-o', '--output',
        required=True,
        help='Output PDF file path'
    )
    rotate_parser.add_argument(
        '-r', '--rotation',
        type=int,
        choices=[90, 180, 270],
        required=True,
        help='Rotation angle in degrees'
    )
    rotate_parser.add_argument(
        '-p', '--pages',
        help='Page range to rotate (e.g., "1-3,5"). If not specified, rotates all pages.'
    )

    # Encrypt command
    encrypt_parser = subparsers.add_parser('encrypt', help='Encrypt PDF with password')
    encrypt_parser.add_argument('input_file', help='Input PDF file')
    encrypt_parser.add_argument(
        '-o', '--output',
        required=True,
        help='Output PDF file path'
    )
    encrypt_parser.add_argument(
        '--password',
        required=True,
        help='Password to encrypt the PDF'
    )

    # Page numbers command
    pagenumbers_parser = subparsers.add_parser('pagenumbers', help='Add page numbers to PDF')
    pagenumbers_parser.add_argument('input_file', help='Input PDF file')
    pagenumbers_parser.add_argument(
        '-o', '--output',
        required=True,
        help='Output PDF file path'
    )
    pagenumbers_parser.add_argument(
        '--position',
        choices=['top', 'bottom'],
        default='bottom',
        help='Position of page numbers (default: bottom)'
    )
    pagenumbers_parser.add_argument(
        '--format',
        default='Page {num} of {total}',
        help='Format string for page numbers (default: "Page {num} of {total}")'
    )

    return parser


def handle_merge(args: argparse.Namespace, processor: PDFProcessor) -> None:
    """Handle merge command.

    Args:
        args: Parsed command line arguments
        processor: PDFProcessor instance
    """
    input_files: List[Path] = [Path(file_path) for file_path in args.input_files]
    output_path: Path = Path(args.output)
    try:
        processor.merge_pdfs(
            input_files=input_files,
            output_file=output_path,
            preserve_metadata=not args.no_preserve_metadata
        )
        print(f"Successfully merged {len(input_files)} files to {output_path}")
    except Exception as e:
        print(f"Error merging files: {e}", file=sys.stderr)
        sys.exit(1)


def handle_split(args: argparse.Namespace, processor: PDFProcessor) -> None:
    """Handle split command.

    Args:
        args: Parsed command line arguments
        processor: PDFProcessor instance
    """
    input_file: Path = Path(args.input_file)
    output_dir: Path = Path(args.output)
    page_ranges: Optional[List[str]] = args.ranges
    try:
        created_files = processor.split_pdf(
            input_file=input_file,
            output_dir=output_dir,
            page_ranges=page_ranges
        )
        print(f"Successfully split PDF into {len(created_files)} files:")
        for file_path in created_files:
            print(f"  - {file_path}")
    except Exception as e:
        print(f"Error splitting PDF: {e}", file=sys.stderr)
        sys.exit(1)


def handle_extract(args: argparse.Namespace, processor: PDFProcessor) -> None:
    """Handle extract command.

    Args:
        args: Parsed command line arguments
        processor: PDFProcessor instance
    """
    input_file: Path = Path(args.input_file)
    output_file: Path = Path(args.output)
    page_range: str = args.pages
    try:
        processor.extract_pages(
            input_file=input_file,
            output_file=output_file,
            page_range=page_range
        )
        print(f"Successfully extracted pages {page_range} to {output_file}")
    except Exception as e:
        print(f"Error extracting pages: {e}", file=sys.stderr)
        sys.exit(1)


def handle_watermark(args: argparse.Namespace, processor: PDFProcessor) -> None:
    """Handle watermark command.

    Args:
        args: Parsed command line arguments
        processor: PDFProcessor instance
    """
    input_file: Path = Path(args.input_file)
    output_file: Path = Path(args.output)
    watermark_text: str = args.text
    opacity: float = args.opacity
    try:
        processor.add_watermark(
            input_file=input_file,
            output_file=output_file,
            watermark_text=watermark_text,
            opacity=opacity
        )
        print(f"Successfully added watermark to {output_file}")
    except Exception as e:
        print(f"Error adding watermark: {e}", file=sys.stderr)
        sys.exit(1)


def handle_rotate(args: argparse.Namespace, processor: PDFProcessor) -> None:
    """Handle rotate command.

    Args:
        args: Parsed command line arguments
        processor: PDFProcessor instance
    """
    input_file: Path = Path(args.input_file)
    output_file: Path = Path(args.output)
    rotation: int = args.rotation
    page_range: Optional[str] = args.pages
    try:
        processor.rotate_pages(
            input_file=input_file,
            output_file=output_file,
            rotation=rotation,
            page_range=page_range
        )
        print(f"Successfully rotated pages by {rotation} degrees to {output_file}")
    except Exception as e:
        print(f"Error rotating pages: {e}", file=sys.stderr)
        sys.exit(1)


def handle_encrypt(args: argparse.Namespace, processor: PDFProcessor) -> None:
    """Handle encrypt command.

    Args:
        args: Parsed command line arguments
        processor: PDFProcessor instance
    """
    input_file: Path = Path(args.input_file)
    output_file: Path = Path(args.output)
    password: str = args.password
    try:
        processor.encrypt_pdf(
            input_file=input_file,
            output_file=output_file,
            password=password
        )
        print(f"Successfully encrypted PDF to {output_file}")
    except Exception as e:
        print(f"Error encrypting PDF: {e}", file=sys.stderr)
        sys.exit(1)


def handle_pagenumbers(args: argparse.Namespace, processor: PDFProcessor) -> None:
    """Handle pagenumbers command.

    Args:
        args: Parsed command line arguments
        processor: PDFProcessor instance
    """
    input_file: Path = Path(args.input_file)
    output_file: Path = Path(args.output)
    position: str = args.position
    format_str: str = args.format
    try:
        processor.add_page_numbers(
            input_file=input_file,
            output_file=output_file,
            position=position,
            format_str=format_str
        )
        print(f"Successfully added page numbers to {output_file}")
    except Exception as e:
        print(f"Error adding page numbers: {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    """Main entry point for the CLI application."""
    parser = create_parser()
    args = parser.parse_args()

    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Initialize processor
    processor = PDFProcessor()

    # Handle commands
    if args.command == 'merge':
        handle_merge(args, processor)
    elif args.command == 'split':
        handle_split(args, processor)
    elif args.command == 'extract':
        handle_extract(args, processor)
    elif args.command == 'watermark':
        handle_watermark(args, processor)
    elif args.command == 'rotate':
        handle_rotate(args, processor)
    elif args.command == 'encrypt':
        handle_encrypt(args, processor)
    elif args.command == 'pagenumbers':
        handle_pagenumbers(args, processor)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
