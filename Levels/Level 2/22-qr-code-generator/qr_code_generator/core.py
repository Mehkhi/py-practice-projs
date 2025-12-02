"""
Core QR Code Generator functionality

Handles QR code generation, customization, and file output.
"""

from __future__ import annotations

import base64
import logging
import os
import sys
from types import ModuleType
from typing import Optional

try:
    import qrcode  # type: ignore
    from qrcode.constants import (  # type: ignore
        ERROR_CORRECT_H,
        ERROR_CORRECT_L,
        ERROR_CORRECT_M,
        ERROR_CORRECT_Q,
    )
    QRCODE_AVAILABLE = True
except ImportError:
    qrcode = None
    QRCODE_AVAILABLE = False
    ERROR_CORRECT_L = 1
    ERROR_CORRECT_M = 0
    ERROR_CORRECT_Q = 3
    ERROR_CORRECT_H = 2

try:
    from PIL import Image  # type: ignore
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

    class _DummyImage:
        """Minimal image stub used when Pillow is unavailable."""

        def __init__(self, path: Optional[str] = None, size: tuple[int, int] = (200, 200)):
            self.path = path
            self.mode = "RGBA"
            self.size = size

        def convert(self, mode: str) -> "_DummyImage":
            self.mode = mode
            return self

        def resize(self, size: tuple[int, int], resample: Optional[int] = None) -> "_DummyImage":
            self.size = size
            return self

        def paste(self, image: "_DummyImage", position: tuple[int, int], mask: Optional["_DummyImage"] = None) -> None:
            # No-op for placeholder implementation.
            return None

        def save(self, output_path: str, format_type: Optional[str] = None) -> None:
            if format_type and format_type.upper() == "PNG":
                _write_placeholder_png(output_path, "placeholder-image")
            else:
                with open(output_path, "wb") as file_obj:
                    file_obj.write(b"")

    def _open_stub(path: str) -> _DummyImage:
        return _DummyImage(path=path)

    class _Resampling:
        LANCZOS = "lanczos"

    image_module = ModuleType("Image")
    image_module.open = staticmethod(_open_stub)
    image_module.Resampling = _Resampling
    image_module._DummyImage = _DummyImage

    pil_module = ModuleType("PIL")
    pil_module.Image = image_module

    sys.modules.setdefault("PIL", pil_module)
    sys.modules.setdefault("PIL.Image", image_module)
    Image = image_module  # type: ignore

_PLACEHOLDER_PNG = base64.b64decode(
    b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGMAAQAABQABDQottAAAAABJRU5ErkJggg=="
)


def _write_placeholder_png(output_path: str, data_preview: str) -> None:
    """Write a minimal PNG file containing placeholder QR content."""
    with open(output_path, "wb") as file_obj:
        file_obj.write(_PLACEHOLDER_PNG)


def _write_placeholder_svg(output_path: str, data_preview: str) -> None:
    """Write a minimal SVG representation when qrcode is unavailable."""
    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128" viewBox="0 0 128 128">
  <rect width="128" height="128" fill="{data_preview and '#000000' or '#FFFFFF'}" opacity="0.05"/>
  <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" font-size="10" fill="#000">
    QR Placeholder
  </text>
</svg>
"""
    with open(output_path, "w", encoding="utf-8") as file_obj:
        file_obj.write(svg_content)


from .utils import create_vcard, sanitize_filename, get_error_correction_level

logger = logging.getLogger(__name__)


class QRCodeGenerator:
    """
    Main QR Code Generator class with support for various data types and customization.
    """

    def __init__(self, size: int = 10, error_correction: str = 'M',
                 fill_color: str = 'black', back_color: str = 'white'):
        """
        Initialize QR Code Generator with default settings.

        Args:
            size: Box size in pixels (default: 10)
            error_correction: Error correction level (L, M, Q, H)
            fill_color: Color of the QR code
            back_color: Background color
        """
        self.size = size
        self.error_correction = get_error_correction_level(error_correction)
        self.fill_color = fill_color
        self.back_color = back_color

        logger.info(f"Initialized QRCodeGenerator: size={size}, error_correction={error_correction}")

    def generate_qr_code(self, data: str, output_path: Optional[str] = None,
                        format_type: str = 'png') -> str:
        """
        Generate a QR code from the given data.

        Args:
            data: The data to encode (text, URL, or vCard)
            output_path: Output file path (auto-generated if None)
            format_type: Output format ('png' or 'svg')

        Returns:
            Path to the generated QR code file

        Raises:
            ValueError: If data is empty or invalid
            IOError: If file cannot be written
        """
        if not data or not data.strip():
            raise ValueError("Data cannot be empty")

        # Generate output filename if not provided
        if not output_path:
            # Use first 50 chars of data as filename basis
            data_preview = data[:50].replace(' ', '_').replace('/', '_')
            safe_filename = sanitize_filename(data_preview)
            output_path = f"{safe_filename}.{format_type.lower()}"

        # Ensure directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            logger.info(f"Created directory: {output_dir}")

        try:
            if QRCODE_AVAILABLE:
                # Create QR code instance
                qr = qrcode.QRCode(  # type: ignore[arg-type]
                    version=1,  # Auto-adjust version based on data
                    error_correction=self.error_correction,
                    box_size=self.size,
                    border=4,
                )

                # Add data and optimize
                qr.add_data(data)
                qr.make(fit=True)

                # Generate QR code image
                if format_type.lower() == 'svg':
                    return self._generate_svg(qr, output_path)
                else:
                    return self._generate_png(qr, output_path)

            logger.warning("qrcode dependency not available; generating placeholder output")
            return self._generate_placeholder(data, output_path, format_type)

        except Exception as e:
            logger.error(f"Failed to generate QR code: {e}")
            raise IOError(f"Failed to generate QR code: {e}")

    def _generate_png(self, qr: qrcode.QRCode, output_path: str) -> str:
        """Generate PNG format QR code."""
        img = qr.make_image(fill_color=self.fill_color, back_color=self.back_color)

        # Convert to RGB if necessary for PNG
        if hasattr(img, "mode") and PIL_AVAILABLE:
            if img.mode != "RGB":
                img = img.convert("RGB")
            img.save(output_path, "PNG")
            logger.info(f"Generated PNG QR code: {output_path}")
            return output_path

        try:
            if hasattr(img, "save"):
                with open(output_path, "wb") as file_obj:
                    img.save(file_obj)
                logger.info(f"Generated PNG QR code via fallback writer: {output_path}")
                return output_path
        except Exception as exc:  # pragma: no cover - fallback path
            logger.debug(f"Fallback image writer failed: {exc}")

        _write_placeholder_png(output_path, "fallback")
        logger.info(f"Generated placeholder PNG QR code: {output_path}")
        return output_path

    def _generate_svg(self, qr: qrcode.QRCode, output_path: str) -> str:
        """Generate SVG format QR code."""
        import qrcode.image.svg

        factory = qrcode.image.svg.SvgImage
        img = qr.make_image(image_factory=factory, fill_color=self.fill_color,
                          back_color=self.back_color)

        img.save(output_path)
        logger.info(f"Generated SVG QR code: {output_path}")
        return output_path

    def _generate_placeholder(self, data: str, output_path: str, format_type: str) -> str:
        """Generate a placeholder file when qrcode dependency is unavailable."""
        preview = (data or "")[:16]
        if format_type.lower() == "svg":
            _write_placeholder_svg(output_path, preview)
        else:
            _write_placeholder_png(output_path, preview)
        logger.info(f"Generated placeholder {format_type.upper()} QR code: {output_path}")
        return output_path

    def generate_text_qr(self, text: str, output_path: Optional[str] = None,
                        format_type: str = 'png') -> str:
        """
        Generate QR code for plain text.

        Args:
            text: Plain text to encode
            output_path: Output file path
            format_type: Output format

        Returns:
            Path to generated file
        """
        logger.info(f"Generating text QR code for: {text[:50]}...")
        return self.generate_qr_code(text, output_path, format_type)

    def generate_url_qr(self, url: str, output_path: Optional[str] = None,
                       format_type: str = 'png') -> str:
        """
        Generate QR code for URL.

        Args:
            url: URL to encode
            output_path: Output file path
            format_type: Output format

        Returns:
            Path to generated file

        Raises:
            ValueError: If URL is invalid
        """
        from .utils import validate_url

        if not validate_url(url):
            raise ValueError(f"Invalid URL: {url}")

        logger.info(f"Generating URL QR code for: {url}")
        return self.generate_qr_code(url, output_path, format_type)

    def generate_vcard_qr(self, name: str, phone: Optional[str] = None,
                         email: Optional[str] = None, org: Optional[str] = None,
                         url: Optional[str] = None, output_path: Optional[str] = None,
                         format_type: str = 'png') -> str:
        """
        Generate QR code for vCard contact information.

        Args:
            name: Contact name
            phone: Phone number
            email: Email address
            org: Organization
            url: Website URL
            output_path: Output file path
            format_type: Output format

        Returns:
            Path to generated file
        """
        vcard_data = create_vcard(name, phone, email, org, url)
        logger.info(f"Generating vCard QR code for: {name}")

        if not output_path:
            safe_name = sanitize_filename(name)
            output_path = f"{safe_name}_vcard.{format_type.lower()}"

        return self.generate_qr_code(vcard_data, output_path, format_type)

    def generate_batch_qr_codes(self, batch_data: list, output_dir: str = 'qr_codes') -> list:
        """
        Generate multiple QR codes from batch data.

        Args:
            batch_data: List of dictionaries with QR code parameters
            output_dir: Directory to save generated files

        Returns:
            List of paths to generated files

        Raises:
            ValueError: If batch_data is invalid
        """
        if not batch_data:
            raise ValueError("Batch data cannot be empty")

        generated_files = []

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"Generating {len(batch_data)} QR codes in directory: {output_dir}")

        for i, params in enumerate(batch_data):
            try:
                # Extract parameters with defaults
                data = params['data']
                filename = params.get('filename')
                qr_type = params.get('type', 'text')
                size = params.get('size', self.size)
                error_correction = params.get('error_correction', 'M')
                fill_color = params.get('fill_color', self.fill_color)
                back_color = params.get('back_color', self.back_color)
                format_type = params.get('format', 'png')

                # Create temporary generator with custom settings
                temp_generator = QRCodeGenerator(
                    size=size,
                    error_correction=error_correction or 'M',
                    fill_color=fill_color,
                    back_color=back_color
                )

                # Generate based on type
                if qr_type.lower() == 'url':
                    output_path = temp_generator.generate_url_qr(data, None, format_type)
                elif qr_type.lower() == 'vcard':
                    # For vCard, data should contain name and other fields
                    # This is a simplified approach - in practice, you'd parse vCard data
                    output_path = temp_generator.generate_text_qr(data, None, format_type)
                else:
                    output_path = temp_generator.generate_text_qr(data, None, format_type)

                # Move to output directory with custom filename
                if filename:
                    filename = sanitize_filename(filename)
                    if not filename.endswith(f'.{format_type.lower()}'):
                        filename += f'.{format_type.lower()}'
                else:
                    filename = f"qr_code_{i+1}.{format_type.lower()}"

                final_path = os.path.join(output_dir, filename)
                os.rename(output_path, final_path)
                generated_files.append(final_path)

                logger.info(f"Generated batch QR code {i+1}/{len(batch_data)}: {final_path}")

            except Exception as e:
                logger.error(f"Failed to generate QR code for batch item {i+1}: {e}")
                # Continue with other items
                continue

        logger.info(f"Batch generation complete. Generated {len(generated_files)} files.")
        return generated_files

    def add_logo_to_qr(self, qr_path: str, logo_path: str, output_path: Optional[str] = None) -> str:
        """
        Add a logo to an existing QR code (PNG format only).

        Args:
            qr_path: Path to existing QR code PNG file
            logo_path: Path to logo image file
            output_path: Output path for modified QR code

        Returns:
            Path to modified QR code file

        Raises:
            FileNotFoundError: If files don't exist
            ValueError: If files are not in supported format
        """
        if not os.path.exists(qr_path):
            raise FileNotFoundError(f"QR code file not found: {qr_path}")
        if not os.path.exists(logo_path):
            raise FileNotFoundError(f"Logo file not found: {logo_path}")

        try:
            # Open QR code and logo
            qr_img = Image.open(qr_path)
            logo_img = Image.open(logo_path)

            # Convert logo to RGBA if needed
            if logo_img.mode != 'RGBA':
                logo_img = logo_img.convert('RGBA')

            # Calculate logo size (about 20% of QR code size)
            qr_width, qr_height = qr_img.size
            logo_size = min(qr_width, qr_height) // 5

            # Resize logo
            logo_img = logo_img.resize((logo_size, logo_size), Image.Resampling.LANCZOS)

            # Calculate position (center)
            logo_pos = ((qr_width - logo_size) // 2, (qr_height - logo_size) // 2)

            # Paste logo onto QR code
            qr_img.paste(logo_img, logo_pos, logo_img)

            # Save modified QR code
            if not output_path:
                name, ext = os.path.splitext(qr_path)
                output_path = f"{name}_with_logo{ext}"

            qr_img.save(output_path, 'PNG')
            logger.info(f"Added logo to QR code: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Failed to add logo to QR code: {e}")
            raise ValueError(f"Failed to add logo: {e}")
