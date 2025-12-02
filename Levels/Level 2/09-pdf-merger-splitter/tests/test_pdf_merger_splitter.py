"""Tests for PDF Merger & Splitter."""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

from PyPDF2 import PdfReader, PdfWriter

from pdf_merger_splitter.core import PDFProcessor
from pdf_merger_splitter.utils import parse_page_range, validate_pdf_path, get_page_number_text


class TestPDFProcessor(unittest.TestCase):
    """Test cases for PDFProcessor class."""

    def setUp(self):
        """Set up test fixtures."""
        self.processor = PDFProcessor()
        self.temp_dir = tempfile.mkdtemp()
        self.test_pdf_path = Path(self.temp_dir) / "test.pdf"
        self.test_pdf2_path = Path(self.temp_dir) / "test2.pdf"
        self.output_path = Path(self.temp_dir) / "output.pdf"

        # Create test PDF files
        self._create_test_pdf(self.test_pdf_path, 3)
        self._create_test_pdf(self.test_pdf2_path, 2)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def _create_test_pdf(self, file_path: Path, num_pages: int, metadata: dict | None = None) -> None:
        """Create a simple test PDF with specified number of pages.

        Args:
            file_path: Path where to create the PDF
            num_pages: Number of pages to create
        """
        writer = PdfWriter()
        for i in range(num_pages):
            writer.add_blank_page(width=612, height=792)  # Standard letter size

        if metadata:
            writer.add_metadata(metadata)

        with open(file_path, 'wb') as f:
            writer.write(f)

    def test_merge_pdfs_success(self):
        """Test successful PDF merging."""
        self.processor.merge_pdfs(
            input_files=[self.test_pdf_path, self.test_pdf2_path],
            output_file=self.output_path
        )

        self.assertTrue(self.output_path.exists())

        # Verify merged PDF has correct number of pages
        reader = PdfReader(str(self.output_path))
        self.assertEqual(len(reader.pages), 5)  # 3 + 2 pages

    def test_merge_pdfs_preserves_metadata(self):
        """Metadata from the first PDF should be retained in the merged output."""
        meta = {"/Author": "Unit Test", "/Title": "Sample"}
        self._create_test_pdf(self.test_pdf_path, 2, metadata=meta)

        self.processor.merge_pdfs(
            input_files=[self.test_pdf_path, self.test_pdf2_path],
            output_file=self.output_path,
            preserve_metadata=True,
        )

        reader = PdfReader(str(self.output_path))
        self.assertEqual(reader.metadata.get("/Author"), "Unit Test")
        self.assertEqual(reader.metadata.get("/Title"), "Sample")

    def test_merge_pdfs_no_files(self):
        """Test merging with no input files raises ValueError."""
        with self.assertRaises(ValueError):
            self.processor.merge_pdfs(
                input_files=[],
                output_file=self.output_path
            )

    def test_merge_pdfs_nonexistent_file(self):
        """Test merging with nonexistent file raises FileNotFoundError."""
        with self.assertRaises(FileNotFoundError):
            self.processor.merge_pdfs(
                input_files=[Path("nonexistent.pdf")],
                output_file=self.output_path
            )

    def test_split_pdf_individual_pages(self):
        """Test splitting PDF into individual pages."""
        output_dir = Path(self.temp_dir) / "split_output"

        created_files = self.processor.split_pdf(
            input_file=self.test_pdf_path,
            output_dir=output_dir
        )

        self.assertEqual(len(created_files), 3)
        self.assertTrue(all(f.exists() for f in created_files))

        # Verify each split file has 1 page
        for file_path in created_files:
            reader = PdfReader(str(file_path))
            self.assertEqual(len(reader.pages), 1)

    def test_split_pdf_by_ranges(self):
        """Test splitting PDF by page ranges."""
        output_dir = Path(self.temp_dir) / "split_ranges"

        created_files = self.processor.split_pdf(
            input_file=self.test_pdf_path,
            output_dir=output_dir,
            page_ranges=["1-2", "3"]
        )

        self.assertEqual(len(created_files), 2)

        # Verify first file has 2 pages, second has 1 page
        reader1 = PdfReader(str(created_files[0]))
        reader2 = PdfReader(str(created_files[1]))
        self.assertEqual(len(reader1.pages), 2)
        self.assertEqual(len(reader2.pages), 1)

    def test_extract_pages_success(self):
        """Test successful page extraction."""
        self.processor.extract_pages(
            input_file=self.test_pdf_path,
            output_file=self.output_path,
            page_range="1-2"
        )

        self.assertTrue(self.output_path.exists())

        # Verify extracted PDF has correct number of pages
        reader = PdfReader(str(self.output_path))
        self.assertEqual(len(reader.pages), 2)

    def test_extract_pages_invalid_range(self):
        """Test extracting with invalid page range raises ValueError."""
        with self.assertRaises(ValueError):
            self.processor.extract_pages(
                input_file=self.test_pdf_path,
                output_file=self.output_path,
                page_range="1-10"  # More pages than exist
            )

    def test_rotate_pages_success(self):
        """Test successful page rotation."""
        self.processor.rotate_pages(
            input_file=self.test_pdf_path,
            output_file=self.output_path,
            rotation=90
        )

        self.assertTrue(self.output_path.exists())

        # Verify output PDF has same number of pages
        reader = PdfReader(str(self.output_path))
        self.assertEqual(len(reader.pages), 3)

    def test_rotate_pages_invalid_angle(self):
        """Test rotating with invalid angle raises ValueError."""
        with self.assertRaises(ValueError):
            self.processor.rotate_pages(
                input_file=self.test_pdf_path,
                output_file=self.output_path,
                rotation=45  # Invalid angle
            )

    def test_encrypt_pdf_success(self):
        """Test successful PDF encryption."""
        password = "test123"
        self.processor.encrypt_pdf(
            input_file=self.test_pdf_path,
            output_file=self.output_path,
            password=password
        )

        self.assertTrue(self.output_path.exists())

        # Verify PDF is encrypted
        reader = PdfReader(str(self.output_path))
        self.assertTrue(reader.is_encrypted)

    def test_add_page_numbers_success(self):
        """Test successful page number addition."""
        self.processor.add_page_numbers(
            input_file=self.test_pdf_path,
            output_file=self.output_path
        )

        self.assertTrue(self.output_path.exists())

        # Verify output PDF has same number of pages
        reader = PdfReader(str(self.output_path))
        self.assertEqual(len(reader.pages), 3)

    def test_add_watermark_success(self):
        """Test successful watermark addition."""
        self.processor.add_watermark(
            input_file=self.test_pdf_path,
            output_file=self.output_path,
            watermark_text="CONFIDENTIAL"
        )

        self.assertTrue(self.output_path.exists())

        # Verify output PDF has same number of pages
        reader = PdfReader(str(self.output_path))
        self.assertEqual(len(reader.pages), 3)


class TestUtils(unittest.TestCase):
    """Test cases for utility functions."""

    def test_parse_page_range_single(self):
        """Test parsing single page number."""
        result = parse_page_range("3", 10)
        self.assertEqual(result, [3])

    def test_parse_page_range_range(self):
        """Test parsing page range."""
        result = parse_page_range("2-5", 10)
        self.assertEqual(result, [2, 3, 4, 5])

    def test_parse_page_range_mixed(self):
        """Test parsing mixed page ranges."""
        result = parse_page_range("1-3,5,7-9", 10)
        self.assertEqual(result, [1, 2, 3, 5, 7, 8, 9])

    def test_parse_page_range_empty(self):
        """Test parsing empty page range returns all pages."""
        result = parse_page_range("", 5)
        self.assertEqual(result, [1, 2, 3, 4, 5])

    def test_parse_page_range_invalid(self):
        """Test parsing invalid page range raises ValueError."""
        with self.assertRaises(ValueError):
            parse_page_range("1-10", 5)  # Range exceeds total pages

        with self.assertRaises(ValueError):
            parse_page_range("0", 5)  # Page number too low

        with self.assertRaises(ValueError):
            parse_page_range("invalid", 5)  # Invalid format

    def test_validate_pdf_path_success(self):
        """Test validating existing PDF file."""
        # Create a temporary PDF file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            temp_path = f.name

        try:
            result = validate_pdf_path(temp_path)
            self.assertEqual(result, Path(temp_path))
        finally:
            os.unlink(temp_path)

    def test_validate_pdf_path_nonexistent(self):
        """Test validating nonexistent file raises FileNotFoundError."""
        with self.assertRaises(FileNotFoundError):
            validate_pdf_path("nonexistent.pdf")

    def test_validate_pdf_path_not_pdf(self):
        """Test validating non-PDF file raises ValueError."""
        # Create a temporary text file
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            temp_path = f.name

        try:
            with self.assertRaises(ValueError):
                validate_pdf_path(temp_path)
        finally:
            os.unlink(temp_path)

    def test_get_page_number_text_default(self):
        """Test default page number text format."""
        result = get_page_number_text(3, 10)
        self.assertEqual(result, "Page 3 of 10")

    def test_get_page_number_text_custom(self):
        """Test custom page number text format."""
        result = get_page_number_text(3, 10, "{num}/{total}")
        self.assertEqual(result, "3/10")


class TestCLIIntegration(unittest.TestCase):
    """Integration tests for CLI functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_pdf_path = Path(self.temp_dir) / "test.pdf"
        self.output_path = Path(self.temp_dir) / "output.pdf"

        # Create test PDF
        writer = PdfWriter()
        writer.add_blank_page(width=612, height=792)
        with open(self.test_pdf_path, 'wb') as f:
            writer.write(f)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)

    @patch('sys.argv', ['pdf-merger-splitter', 'merge', '-o', 'output.pdf', 'input.pdf'])
    def test_cli_merge_command_parsing(self):
        """Test that CLI merge command is parsed correctly."""
        from pdf_merger_splitter.main import create_parser
        parser = create_parser()
        args = parser.parse_args(['merge', '-o', 'output.pdf', 'input.pdf'])

        self.assertEqual(args.command, 'merge')
        self.assertEqual(args.output, 'output.pdf')
        self.assertEqual(args.input_files, ['input.pdf'])

    @patch('sys.argv', ['pdf-merger-splitter', 'extract', 'input.pdf', '-o', 'output.pdf', '-p', '1-3'])
    def test_cli_extract_command_parsing(self):
        """Test that CLI extract command is parsed correctly."""
        from pdf_merger_splitter.main import create_parser
        parser = create_parser()
        args = parser.parse_args(['extract', 'input.pdf', '-o', 'output.pdf', '-p', '1-3'])

        self.assertEqual(args.command, 'extract')
        self.assertEqual(args.input_file, 'input.pdf')
        self.assertEqual(args.output, 'output.pdf')
        self.assertEqual(args.pages, '1-3')


if __name__ == '__main__':
    unittest.main()
