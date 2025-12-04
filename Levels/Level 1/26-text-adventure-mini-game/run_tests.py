#!/usr/bin/env python3
"""Run all project tests using the venv with pygame installed."""
import os
import sys
import unittest

# Get the script directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Add project root to Python path so imports work
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

# Change to script directory
os.chdir(SCRIPT_DIR)

# Run tests using unittest discover with proper top-level directory
if __name__ == "__main__":
    loader = unittest.TestLoader()
    # Use top_level_dir to ensure imports work correctly
    suite = loader.discover(
        start_dir=os.path.join(SCRIPT_DIR, "tests"),
        top_level_dir=SCRIPT_DIR,
        pattern="test_*.py"
    )
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
