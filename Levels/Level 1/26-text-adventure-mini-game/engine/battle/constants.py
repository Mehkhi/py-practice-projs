"""Battle scene constants.

This module contains constants used by the battle scene system,
including biome backdrop mappings, gradient colors, and animation timings.
"""

from typing import Dict, Tuple


# Mapping from biome names to backdrop sprite IDs
BIOME_TO_BACKDROP: Dict[str, str] = {
    "forest": "bg_forest",
    "cave": "bg_cave",
    "mountain": "bg_mountain",
    "ruins": "bg_ruins",
    "snow": "bg_snow",
    "tundra": "bg_snow",
    "swamp": "bg_swamp",
    "treasure": "bg_treasure_chamber",
    "dungeon": "bg_cave",
    "desert": "bg_ruins",  # Fallback for desert areas
}

# Biome-specific gradient colors for fallback backgrounds (top_color, bottom_color)
BIOME_GRADIENTS: Dict[str, Tuple[Tuple[int, int, int], Tuple[int, int, int]]] = {
    "forest": ((10, 30, 15), (20, 50, 25)),       # Dark green
    "cave": ((5, 5, 10), (15, 15, 25)),           # Dark gray-blue
    "mountain": ((20, 25, 40), (40, 50, 70)),     # Gray-blue
    "snow": ((30, 35, 45), (60, 65, 80)),         # Light gray-blue
    "tundra": ((30, 35, 45), (60, 65, 80)),       # Light gray-blue
    "swamp": ((10, 20, 10), (25, 35, 20)),        # Murky green
    "ruins": ((20, 15, 25), (35, 30, 45)),        # Purple-gray
    "treasure": ((25, 20, 10), (50, 40, 20)),     # Golden brown
    "dungeon": ((8, 8, 12), (18, 18, 28)),        # Very dark
    "desert": ((40, 35, 20), (60, 50, 30)),       # Sandy brown
}

# Flash effect constants
FLASH_INITIAL_INTENSITY: float = 1.0  # Starting intensity for flash effects (0.0 to 1.0)
FLASH_DECAY_RATE: float = 3.0  # Rate at which flash effects fade (intensity per second)

# AI notification constants
AI_NOTIFICATION_DURATION: float = 3.0  # Duration in seconds for AI pattern notifications
