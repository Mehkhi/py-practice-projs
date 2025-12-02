"""
Email Sender Package

A professional CLI tool for sending emails with attachments, HTML templates,
and batch processing capabilities.
"""

__version__ = "1.0.0"
__author__ = "Python Practice Projects"

from .core import EmailSender
from .utils import validate_email, load_recipients_from_csv

__all__ = ["EmailSender", "validate_email", "load_recipients_from_csv"]
