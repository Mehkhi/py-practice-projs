"""CSV Data Cleaner - A professional CLI tool for cleaning and validating CSV data."""

__version__ = "1.0.0"
__author__ = "CSV Cleaner Team"

from .core import CSVCleaner
from .main import main

__all__ = ["CSVCleaner", "main"]
