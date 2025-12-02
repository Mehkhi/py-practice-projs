"""
SQLite Contact Manager

A professional CLI tool for managing contacts with SQLite database.
Supports CRUD operations, search, import/export, and advanced features.
"""

__version__ = "1.0.0"
__author__ = "Python Practice Project"

from .simple_core import SimpleContactManager as ContactManager
from .main import main

__all__ = ["ContactManager", "main"]
