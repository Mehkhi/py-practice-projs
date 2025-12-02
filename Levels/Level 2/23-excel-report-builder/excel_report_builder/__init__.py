"""
Excel Report Builder

A professional CLI tool for generating formatted Excel reports from CSV data.
Supports formatting, charts, formulas, and multiple sheets.
"""

__version__ = "1.0.0"
__author__ = "Excel Report Builder Team"

from .core import ExcelReportBuilder
from .utils import DataProcessor, ChartGenerator
from .templates import TemplateManager, ReportTemplate

__all__ = ["ExcelReportBuilder", "DataProcessor", "ChartGenerator", "TemplateManager", "ReportTemplate"]
