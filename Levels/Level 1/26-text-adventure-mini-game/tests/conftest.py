"""Shared test fixtures and path configuration.

This module ensures the project root is in sys.path for all tests,
eliminating the need for path manipulation in individual test files.

Also provides pygame initialization for headless test environments.
Works with both unittest and pytest.
"""

import os
import sys

# Ensure project root is in path for imports
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def _init_pygame_for_tests():
    """Initialize pygame and font module for tests.

    Sets up headless mode if DISPLAY is not available and ensures
    pygame.font is initialized (required for AssetManager).
    """
    try:
        import pygame

        # Set up headless mode for environments without DISPLAY (e.g., CI)
        if "DISPLAY" not in os.environ and "SDL_VIDEODRIVER" not in os.environ:
            os.environ["SDL_VIDEODRIVER"] = "dummy"

        # Initialize pygame if not already initialized
        if not pygame.get_init():
            pygame.init()

        # Explicitly initialize font module (required for AssetManager)
        if not pygame.font.get_init():
            pygame.font.init()
    except ImportError:
        # pygame not available - tests that need it will handle this
        pass
    except Exception as e:
        # Log but don't fail - some tests may handle this themselves
        print(f"Warning: pygame initialization failed: {e}")


# Initialize pygame when module is imported (works for both unittest and pytest)
_init_pygame_for_tests()


def pytest_configure(config):
    """Configure pytest hooks for pygame initialization."""
    _init_pygame_for_tests()


def pytest_unconfigure(config):
    """Clean up pygame after all tests complete."""
    try:
        import pygame
        if pygame.get_init():
            pygame.quit()
    except (ImportError, Exception):
        pass  # Ignore errors during cleanup
