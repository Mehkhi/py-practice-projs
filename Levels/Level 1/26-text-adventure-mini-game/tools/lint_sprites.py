#!/usr/bin/env python3
"""Lint check for duplicate sprite IDs in asset directories.

This script can be used in CI to fail builds when duplicate sprite IDs
are detected across different subdirectories.

Usage:
    python tools/lint_sprites.py [--strict]

Options:
    --strict    Exit with error code 1 if any duplicates found (default)
    --warn      Only print warnings, always exit 0

Exit codes:
    0 - No duplicates found (or --warn mode)
    1 - Duplicates found (in --strict mode)
"""

import sys
import os

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Initialize pygame minimally for headless sprite loading
import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.HIDDEN)

from engine.assets.sprite_manager import SpriteManager


def main() -> int:
    """Check for duplicate sprite IDs and report results.

    Returns:
        0 if no duplicates found, 1 if duplicates found (in strict mode).
    """
    strict_mode = "--warn" not in sys.argv

    print("Checking for duplicate sprite IDs...")

    # Create sprite manager which will detect duplicates during initialization
    try:
        mgr = SpriteManager()
    except Exception as e:
        print(f"ERROR: Failed to initialize SpriteManager: {e}")
        return 1

    # Get duplicate detections
    duplicates = mgr.get_duplicate_sprite_ids()

    if not duplicates:
        print("OK: No duplicate sprite IDs found.")
        print(f"Total sprites loaded: {len(mgr.images)}")
        return 0

    # Report duplicates
    print(f"{'ERROR' if strict_mode else 'WARNING'}: Found {len(duplicates)} duplicate sprite ID(s):")
    for sprite_id, path1, path2 in duplicates:
        print(f"  - '{sprite_id}':")
        print(f"      First:     {path1}")
        print(f"      Duplicate: {path2}")

    if strict_mode:
        print("\nFix: Rename or remove duplicate files, or use unique sprite IDs.")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
