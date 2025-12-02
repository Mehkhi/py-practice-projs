"""Shared test fixtures and path configuration.

This module ensures the project root is in sys.path for all tests,
eliminating the need for path manipulation in individual test files.
"""

import os
import sys

# Ensure project root is in path for imports
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
