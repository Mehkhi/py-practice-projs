"""
Main entry point for the To-Do GUI application.

This module provides the main function to start the application.
"""

import sys
import logging
from pathlib import Path

from .gui import TodoGUI


def main():
    """Main entry point for the application."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('todo_app.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

    logger = logging.getLogger(__name__)
    logger.info("Starting To-Do GUI application")

    try:
        # Create and run the GUI application
        app = TodoGUI()
        app.run()
    except Exception as e:
        logger.error(f"Application error: {e}")
        print(f"Error starting application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
