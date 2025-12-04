"""Dungeon puzzle system for interactive puzzles."""

# Re-export everything for backward compatibility
from .models import *
from .manager import PuzzleManager
from .conditions import check_puzzle_solved
from .mechanics import *

# Also re-export from mechanics modules for direct access
from .mechanics.blocks_ice import calculate_push_destination
