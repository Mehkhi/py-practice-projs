"""
Currency Converter Package

A professional CLI tool for currency conversion with live exchange rates,
batch processing, and comprehensive error handling.
"""

__version__ = "1.0.0"
__author__ = "Currency Converter Team"

from .core import CurrencyConverter
from .main import main

__all__ = ["CurrencyConverter", "main"]
