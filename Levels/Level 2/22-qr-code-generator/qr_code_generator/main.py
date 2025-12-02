"""
Command-line interface for QR Code Generator

Provides a comprehensive CLI for generating QR codes with various options.
"""

import argparse
import logging
import sys
import os
from typing import Optional

from .core import QRCodeGenerator
from .utils import parse_csv_batch

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('qr_generator.log')
    ]
)

logger = logging.getLogger(__name__)


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description='Generate QR codes with various customization options',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate simple text QR code
  python -m qr_code_generator "Hello World"

  # Generate URL QR code with custom colors
  python -m qr_code_generator --url "https://example.com" --fill-color blue --back-color white

  # Generate vCard QR code
  python -m qr_code_generator --vcard --name "John Doe" --phone "+1234567890" --email "john@example.com"

  # Generate from CSV batch
  python -m qr_code_generator --batch data.csv --output-dir ./qr_codes

  # Generate SVG format
  python -m qr_code_generator "Sample Text" --format svg --output sample.svg
        """
    )

    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        'text',
        nargs='?',
        help='Text content to encode in QR code'
    )
    input_group.add_argument(
        '--url',
        help='URL to encode in QR code'
    )
    input_group.add_argument(
        '--vcard',
        action='store_true',
        help='Generate vCard QR code (requires --name and optional contact fields)'
    )
    input_group.add_argument(
        '--batch',
        help='CSV file path for batch generation'
    )

    # vCard options
    parser.add_argument(
        '--name',
        help='Contact name (required for vCard)'
    )
    parser.add_argument(
        '--phone',
        help='Phone number for vCard'
    )
    parser.add_argument(
        '--email',
        help='Email address for vCard'
    )
    parser.add_argument(
        '--org',
        help='Organization for vCard'
    )

    # Output options
    parser.add_argument(
        '--output', '-o',
        help='Output file path (auto-generated if not specified)'
    )
    parser.add_argument(
        '--format', '-f',
        choices=['png', 'svg'],
        default='png',
        help='Output format (default: png)'
    )
    parser.add_argument(
        '--output-dir',
        default='qr_codes',
        help='Output directory for batch generation (default: qr_codes)'
    )

    # QR code customization
    parser.add_argument(
        '--size', '-s',
        type=int,
        default=10,
        help='Box size in pixels (default: 10)'
    )
    parser.add_argument(
        '--error-correction', '-e',
        choices=['L', 'M', 'Q', 'H'],
        default='M',
        help='Error correction level: L(7%%), M(15%%), Q(25%%), H(30%%) (default: M)'
    )
    parser.add_argument(
        '--fill-color',
        default='black',
        help='QR code fill color (default: black)'
    )
    parser.add_argument(
        '--back-color',
        default='white',
        help='QR code background color (default: white)'
    )

    # Logo option
    parser.add_argument(
        '--add-logo',
        help='Path to logo image to add to QR code (PNG format only)'
    )

    # Other options
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    parser.add_argument(
        '--version',
        action='version',
        version='QR Code Generator 1.0.0'
    )

    return parser


def validate_args(args: argparse.Namespace) -> None:
    """Validate command line arguments."""
    if args.vcard and not args.name:
        raise ValueError("--name is required when using --vcard")

    if args.size <= 0:
        raise ValueError("--size must be a positive integer")

    if args.add_logo and args.format.lower() != 'png':
        raise ValueError("--add-logo is only supported with PNG format")

    if args.batch and not os.path.exists(args.batch):
        raise FileNotFoundError(f"Batch file not found: {args.batch}")


def main() -> int:
    """Main entry point for the CLI application."""
    try:
        parser = create_parser()
        args = parser.parse_args()

        # Configure logging level
        if args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)

        # Validate arguments
        validate_args(args)

        # Create QR code generator
        qr_generator = QRCodeGenerator(
            size=args.size,
            error_correction=args.error_correction,
            fill_color=args.fill_color,
            back_color=args.back_color
        )

        output_path = None

        # Handle different input types
        if args.batch:
            # Batch generation
            logger.info(f"Starting batch generation from: {args.batch}")
            batch_data = parse_csv_batch(args.batch)
            generated_files = qr_generator.generate_batch_qr_codes(
                batch_data,
                args.output_dir
            )

            print(f"\n✅ Successfully generated {len(generated_files)} QR codes:")
            for file_path in generated_files:
                print(f"   📁 {file_path}")

        elif args.vcard:
            # vCard generation
            logger.info(f"Generating vCard QR code for: {args.name}")
            output_path = qr_generator.generate_vcard_qr(
                name=args.name,
                phone=args.phone,
                email=args.email,
                org=args.org,
                url=args.url,
                output_path=args.output,
                format_type=args.format
            )
            print(f"✅ vCard QR code generated: {output_path}")

        elif args.url:
            # URL generation
            logger.info(f"Generating URL QR code for: {args.url}")
            output_path = qr_generator.generate_url_qr(
                args.url,
                args.output,
                args.format
            )
            print(f"✅ URL QR code generated: {output_path}")

        else:
            # Text generation
            logger.info(f"Generating text QR code for: {args.text[:50]}...")
            output_path = qr_generator.generate_text_qr(
                args.text,
                args.output,
                args.format
            )
            print(f"✅ Text QR code generated: {output_path}")

        # Add logo if requested
        if args.add_logo and output_path:
            logger.info(f"Adding logo to QR code: {args.add_logo}")
            logo_output = qr_generator.add_logo_to_qr(
                output_path,
                args.add_logo
            )
            print(f"✅ Logo added: {logo_output}")

        return 0

    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
        return 1
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"❌ Error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
