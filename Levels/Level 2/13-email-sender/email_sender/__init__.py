"""
Email Sender Package

A professional mail merge tool for sending emails with attachments, HTML templates,
campaign tracking, and batch processing capabilities.
"""

__version__ = "2.0.0"
__author__ = "Python Practice Projects"

from .core import EmailSender
from .utils import validate_email, load_recipients_from_csv, format_email_template, load_template_file
from .storage import CampaignStorage
from .gmail_api import GmailAPISender
from .sheets_sync import SheetsSync

__all__ = [
    "EmailSender",
    "validate_email",
    "load_recipients_from_csv",
    "format_email_template",
    "load_template_file",
    "CampaignStorage",
    "GmailAPISender",
    "SheetsSync",
]
