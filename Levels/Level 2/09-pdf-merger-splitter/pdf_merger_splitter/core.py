"""Core PDF manipulation operations."""

import logging
from pathlib import Path
from typing import List, Optional, Tuple, Union

from PyPDF2 import PdfMerger, PdfReader, PdfWriter
from PyPDF2.generic import (
    ArrayObject,
    DictionaryObject,
    FloatObject,
    NameObject,
    NumberObject,
    RectangleObject,
    TextStringObject,
)

from .utils import ensure_output_dir, get_page_number_text, parse_page_range, parse_page_order, validate_pdf_path

logger = logging.getLogger(__name__)


def _clamp(value: float, lower: float, upper: float) -> float:
    """Clamp value to the inclusive range [lower, upper]."""
    return max(lower, min(value, upper))


def _create_free_text_annotation(
    rect: Tuple[float, float, float, float],
    text: str,
    font_size: float,
    color: Tuple[float, float, float],
    opacity: float,
    justification: int = 1,
) -> DictionaryObject:
    """Create a FreeText annotation dictionary configured for display/print."""
    llx, lly, urx, ury = rect
    color = tuple(_clamp(component, 0.0, 1.0) for component in color)
    annotation = DictionaryObject()
    annotation[NameObject("/Type")] = NameObject("/Annot")
    annotation[NameObject("/Subtype")] = NameObject("/FreeText")
    annotation[NameObject("/Rect")] = RectangleObject([llx, lly, urx, ury])
    annotation[NameObject("/Contents")] = TextStringObject(text)
    annotation[NameObject("/DA")] = TextStringObject(
        f"/Helv {font_size:.2f} Tf {color[0]:.3f} {color[1]:.3f} {color[2]:.3f} rg"
    )
    annotation[NameObject("/C")] = ArrayObject([FloatObject(component) for component in color])
    annotation[NameObject("/Q")] = NumberObject(justification)
    annotation[NameObject("/Border")] = ArrayObject(
        [NumberObject(0), NumberObject(0), NumberObject(0)]
    )
    annotation[NameObject("/F")] = NumberObject(4)  # Print the annotation when exporting
    opacity = _clamp(opacity, 0.0, 1.0)
    annotation[NameObject("/CA")] = FloatObject(opacity)
    annotation[NameObject("/ca")] = FloatObject(opacity)
    annotation[NameObject("/DS")] = TextStringObject("font: Helvetica;")
    return annotation


class PDFProcessor:
    """Main class for PDF processing operations."""

    def __init__(self):
        """Initialize the PDF processor."""
        self.logger = logging.getLogger(__name__)

    def merge_pdfs(
        self,
        input_files: List[Union[str, Path]],
        output_file: Union[str, Path],
        preserve_metadata: bool = True
    ) -> None:
        """Merge multiple PDF files into one.

        Args:
            input_files: List of input PDF file paths
            output_file: Output PDF file path
            preserve_metadata: Whether to preserve metadata from first PDF

        Raises:
            FileNotFoundError: If any input file doesn't exist
            ValueError: If no valid input files provided
        """
        if not input_files:
            raise ValueError("No input files provided for merging")

        # Validate all input files
        validated_files = []
        for file_path in input_files:
            validated_files.append(validate_pdf_path(file_path))

        # Ensure output directory exists
        output_path = ensure_output_dir(output_file)

        self.logger.info(f"Merging {len(validated_files)} PDF files into {output_path}")

        merger = PdfMerger()

        try:
            # Add each PDF to the merger
            for i, file_path in enumerate(validated_files):
                self.logger.debug(f"Adding file {i+1}: {file_path}")
                merger.append(str(file_path))

            if preserve_metadata and validated_files:
                try:
                    first_reader = PdfReader(str(validated_files[0]))
                    if first_reader.metadata:
                        merger.add_metadata(dict(first_reader.metadata))
                        self.logger.debug(
                            "Preserved metadata from %s", validated_files[0]
                        )
                except Exception as exc:
                    self.logger.warning(
                        "Could not preserve metadata from %s: %s",
                        validated_files[0],
                        exc,
                    )

            # Write the merged PDF
            with open(output_path, 'wb') as output_file_handle:
                merger.write(output_file_handle)

            self.logger.info(f"Successfully merged PDFs to {output_path}")

        except Exception as e:
            self.logger.error(f"Error merging PDFs: {e}")
            raise
        finally:
            merger.close()

    def split_pdf(
        self,
        input_file: Union[str, Path],
        output_dir: Union[str, Path],
        page_ranges: Optional[List[str]] = None
    ) -> List[Path]:
        """Split a PDF into multiple files based on page ranges.

        Args:
            input_file: Input PDF file path
            output_dir: Output directory for split files
            page_ranges: List of page ranges (e.g., ["1-3", "4-6"])
                        If None, splits each page into separate file

        Returns:
            List of created file paths

        Raises:
            FileNotFoundError: If input file doesn't exist
        """
        input_path = validate_pdf_path(input_file)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        self.logger.info(f"Splitting PDF {input_path} into {output_path}")

        reader = PdfReader(str(input_path))
        total_pages = len(reader.pages)

        created_files = []

        if page_ranges is None:
            # Split each page into separate file
            for page_num in range(total_pages):
                writer = PdfWriter()
                writer.add_page(reader.pages[page_num])

                output_file = output_path / f"{input_path.stem}_page_{page_num + 1}.pdf"
                with open(output_file, 'wb') as f:
                    writer.write(f)

                created_files.append(output_file)
                self.logger.debug(f"Created: {output_file}")
        else:
            # Split by specified ranges
            for i, range_str in enumerate(page_ranges):
                pages = parse_page_range(range_str, total_pages)

                writer = PdfWriter()
                for page_num in pages:
                    writer.add_page(reader.pages[page_num - 1])  # Convert to 0-based

                output_file = output_path / f"{input_path.stem}_part_{i + 1}.pdf"
                with open(output_file, 'wb') as f:
                    writer.write(f)

                created_files.append(output_file)
                self.logger.debug(f"Created: {output_file}")

        self.logger.info(f"Successfully split PDF into {len(created_files)} files")
        return created_files

    def extract_pages(
        self,
        input_file: Union[str, Path],
        output_file: Union[str, Path],
        page_range: str
    ) -> None:
        """Extract specific pages from a PDF to a new file.

        Args:
            input_file: Input PDF file path
            output_file: Output PDF file path
            page_range: Page range string (e.g., "1-3,5,7-9")

        Raises:
            FileNotFoundError: If input file doesn't exist
            ValueError: If page range is invalid
        """
        input_path = validate_pdf_path(input_file)
        output_path = ensure_output_dir(output_file)

        self.logger.info(f"Extracting pages {page_range} from {input_path} to {output_path}")

        reader = PdfReader(str(input_path))
        total_pages = len(reader.pages)

        pages = parse_page_range(page_range, total_pages)

        writer = PdfWriter()
        for page_num in pages:
            writer.add_page(reader.pages[page_num - 1])  # Convert to 0-based

        with open(output_path, 'wb') as f:
            writer.write(f)

        self.logger.info(f"Successfully extracted {len(pages)} pages to {output_path}")

    def add_watermark(
        self,
        input_file: Union[str, Path],
        output_file: Union[str, Path],
        watermark_text: str,
        opacity: float = 0.3
    ) -> None:
        """Add text watermark to all pages of a PDF.

        Note: This is a simplified implementation that adds a watermark
        by creating a simple overlay. For production use, consider using
        more advanced PDF libraries.

        Args:
            input_file: Input PDF file path
            output_file: Output PDF file path
            watermark_text: Text to use as watermark
            opacity: Watermark opacity (0.0 to 1.0)

        Raises:
            FileNotFoundError: If input file doesn't exist
        """
        input_path = validate_pdf_path(input_file)
        output_path = ensure_output_dir(output_file)

        self.logger.info(f"Adding watermark to {input_path}")

        reader = PdfReader(str(input_path))
        writer = PdfWriter()

        effective_opacity = _clamp(opacity, 0.0, 1.0)
        for page_index, page in enumerate(reader.pages):
            page_width = float(page.mediabox.width)
            page_height = float(page.mediabox.height)
            base_dimension = min(page_width, page_height)
            font_size = max(24.0, base_dimension * 0.08)
            margin = base_dimension * 0.1
            rect_width = max(page_width - 2 * margin, page_width * 0.6)
            rect_height = font_size * 1.6
            llx = (page_width - rect_width) / 2
            lly = (page_height - rect_height) / 2
            rect = (
                llx,
                lly,
                llx + rect_width,
                lly + rect_height,
            )
            annotation = _create_free_text_annotation(
                rect=rect,
                text=watermark_text,
                font_size=font_size,
                color=(0.6, 0.6, 0.6),
                opacity=effective_opacity,
                justification=1,
            )
            writer.add_page(page)
            writer.add_annotation(page_index, annotation)
            self.logger.debug("Applied watermark to page %s", page_index + 1)

        with open(output_path, 'wb') as f:
            writer.write(f)

        self.logger.info(f"Successfully applied watermark to {output_path}")

    def rotate_pages(
        self,
        input_file: Union[str, Path],
        output_file: Union[str, Path],
        rotation: int,
        page_range: Optional[str] = None
    ) -> None:
        """Rotate pages in a PDF.

        Args:
            input_file: Input PDF file path
            output_file: Output PDF file path
            rotation: Rotation angle (90, 180, or 270 degrees)
            page_range: Page range to rotate (if None, rotates all pages)

        Raises:
            FileNotFoundError: If input file doesn't exist
            ValueError: If rotation angle is invalid
        """
        if rotation not in [90, 180, 270]:
            raise ValueError("Rotation must be 90, 180, or 270 degrees")

        input_path = validate_pdf_path(input_file)
        output_path = ensure_output_dir(output_file)

        self.logger.info(f"Rotating pages in {input_path} by {rotation} degrees")

        reader = PdfReader(str(input_path))
        writer = PdfWriter()

        total_pages = len(reader.pages)

        if page_range is None:
            pages_to_rotate = range(total_pages)
        else:
            pages_to_rotate = [p - 1 for p in parse_page_range(page_range, total_pages)]

        for i, page in enumerate(reader.pages):
            if i in pages_to_rotate:
                page.rotate(rotation)
            writer.add_page(page)

        with open(output_path, 'wb') as f:
            writer.write(f)

        self.logger.info(f"Successfully rotated pages in {output_path}")

    def reorder_pages(
        self,
        input_file: Union[str, Path],
        output_file: Union[str, Path],
        new_order: str,
    ) -> None:
        """Reorder pages according to an order string.

        The order string can contain comma or space separated tokens like
        "3,1,2-4" and allows duplicates to copy pages multiple times.
        """
        input_path = validate_pdf_path(input_file)
        output_path = ensure_output_dir(output_file)

        reader = PdfReader(str(input_path))
        total_pages = len(reader.pages)
        if total_pages == 0:
            with open(output_path, 'wb') as f:
                PdfWriter().write(f)
            return

        sequence = parse_page_order(new_order, total_pages)
        if not sequence:
            raise ValueError("New page order cannot be empty")

        writer = PdfWriter()
        for one_based in sequence:
            writer.add_page(reader.pages[one_based - 1])

        # Preserve metadata if present
        if reader.metadata:
            writer.add_metadata(reader.metadata)

        with open(output_path, 'wb') as f:
            writer.write(f)
        self.logger.info("Reordered %s pages into %s", len(sequence), output_path)

    def encrypt_pdf(
        self,
        input_file: Union[str, Path],
        output_file: Union[str, Path],
        password: str
    ) -> None:
        """Encrypt a PDF with a password.

        Args:
            input_file: Input PDF file path
            output_file: Output PDF file path
            password: Password to encrypt the PDF

        Raises:
            FileNotFoundError: If input file doesn't exist
        """
        input_path = validate_pdf_path(input_file)
        output_path = ensure_output_dir(output_file)

        self.logger.info(f"Encrypting {input_path}")

        reader = PdfReader(str(input_path))
        writer = PdfWriter()

        # Copy all pages
        for page in reader.pages:
            writer.add_page(page)

        # Copy metadata if present
        if reader.metadata:
            writer.add_metadata(reader.metadata)

        # Encrypt with password
        writer.encrypt(password)

        with open(output_path, 'wb') as f:
            writer.write(f)

        self.logger.info(f"Successfully encrypted PDF to {output_path}")

    def add_page_numbers(
        self,
        input_file: Union[str, Path],
        output_file: Union[str, Path],
        position: str = "bottom",
        format_str: str = "Page {num} of {total}"
    ) -> None:
        """Add page numbers to a PDF using FreeText annotations.

        This implementation writes visible page labels without rasterising
        the pages. For complex layouts, you may still prefer dedicated PDF
        composition libraries.

        Args:
            input_file: Input PDF file path
            output_file: Output PDF file path
            position: Position of page numbers ("top" or "bottom")
            format_str: Format string for page numbers

        Raises:
            FileNotFoundError: If input file doesn't exist
        """
        input_path = validate_pdf_path(input_file)
        output_path = ensure_output_dir(output_file)

        self.logger.info(f"Adding page numbers to {input_path}")

        reader = PdfReader(str(input_path))
        writer = PdfWriter()
        total_pages = len(reader.pages)

        position_normalized = position.lower()
        if position_normalized not in {"top", "bottom"}:
            raise ValueError("Position must be either 'top' or 'bottom'")

        if total_pages == 0:
            with open(output_path, 'wb') as f:
                writer.write(f)
            self.logger.info(f"No pages found in {input_path}; created empty file at {output_path}")
            return

        base_dimension = min(
            float(reader.pages[0].mediabox.width),
            float(reader.pages[0].mediabox.height),
        )
        font_size = max(12.0, base_dimension * 0.04)

        for page_index, page in enumerate(reader.pages):
            writer.add_page(page)
            page_width = float(page.mediabox.width)
            page_height = float(page.mediabox.height)
            margin = max(18.0, min(page_width, page_height) * 0.05)
            rect_width = max(page_width - 2 * margin, page_width * 0.5)
            rect_height = font_size * 1.6
            llx = (page_width - rect_width) / 2
            if position_normalized == "top":
                lly = max(page_height - margin - rect_height, margin)
            else:
                lly = margin
            rect = (
                llx,
                lly,
                llx + rect_width,
                lly + rect_height,
            )
            try:
                label = get_page_number_text(page_index + 1, total_pages, format_str)
            except (KeyError, IndexError) as exc:
                raise ValueError(
                    "Invalid format string for page numbers. Use placeholders {num} and {total}."
                ) from exc
            annotation = _create_free_text_annotation(
                rect=rect,
                text=label,
                font_size=font_size,
                color=(0.0, 0.0, 0.0),
                opacity=1.0,
                justification=1,
            )
            writer.add_annotation(page_index, annotation)
            self.logger.debug(
                "Added page number '%s' to page %s at %s",
                label,
                page_index + 1,
                position_normalized,
            )

        with open(output_path, 'wb') as f:
            writer.write(f)

        self.logger.info(f"Successfully added page numbers to {output_path} ({position_normalized})")

    def write_metadata(
        self,
        input_file: Union[str, Path],
        output_file: Union[str, Path],
        title: str | None = None,
        author: str | None = None,
        subject: str | None = None,
        keywords: str | None = None,
    ) -> None:
        """Write PDF document info metadata to a new file.

        Blank (None) fields are ignored (existing values preserved if present).
        """
        input_path = validate_pdf_path(input_file)
        output_path = ensure_output_dir(output_file)

        reader = PdfReader(str(input_path))
        writer = PdfWriter()

        for page in reader.pages:
            writer.add_page(page)

        # Start with existing metadata
        meta = {}
        if reader.metadata:
            meta.update(reader.metadata)

        # Update with provided fields using standard keys
        if title is not None:
            meta["/Title"] = title
        if author is not None:
            meta["/Author"] = author
        if subject is not None:
            meta["/Subject"] = subject
        if keywords is not None:
            meta["/Keywords"] = keywords

        if meta:
            writer.add_metadata(meta)

        with open(output_path, 'wb') as f:
            writer.write(f)
        self.logger.info("Wrote metadata to %s", output_path)
