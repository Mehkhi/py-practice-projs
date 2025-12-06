"""
Lightweight web UI for mail merge campaigns.

This module provides a Flask-based web interface for managing campaigns.
Templates are stored in the templates/ directory.

NOTE: This module now delegates to the web/ package which contains
the Flask blueprints for better code organization.
"""

# Re-export everything from the web package for backwards compatibility
from .web import app, create_app, run_web_server

__all__ = ["app", "create_app", "run_web_server"]
