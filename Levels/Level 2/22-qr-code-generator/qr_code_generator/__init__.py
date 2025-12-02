"""
QR Code Generator Package

A professional CLI tool for generating QR codes with various customization options.
Supports text, URLs, vCards, and batch processing from CSV files.
"""

__version__ = "1.0.0"
__author__ = "QR Code Generator"

from .core import QRCodeGenerator
from .utils import validate_url, create_vcard, parse_csv_batch

__all__ = ["QRCodeGenerator", "validate_url", "create_vcard", "parse_csv_batch"]
