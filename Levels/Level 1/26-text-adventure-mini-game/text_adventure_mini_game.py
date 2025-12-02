#!/usr/bin/env python3
"""
JRPG Engine - Text Adventure Mini-Game

A JRPG engine with top-down overworld, turn-based combat,
and data-driven world system.
"""

import logging
import os
import sys

import pygame

from engine.game import RpgGame


def main() -> None:
    """Main entry point."""
    # Configure logging early to surface font warnings and other logs
    log_level_str = os.environ.get("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_str, logging.INFO)
    logging.basicConfig(level=log_level, format='%(levelname)s: %(message)s')

    try:
        game = RpgGame()
        game.run()
    except KeyboardInterrupt:
        # Graceful exit on Ctrl+C
        pass
    finally:
        pygame.quit()
        sys.exit(0)


if __name__ == "__main__":
    main()
