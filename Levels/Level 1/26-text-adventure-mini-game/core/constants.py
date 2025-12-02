"""Core game constants.

This module centralizes game constants used across multiple modules
for equipment, formations, and other core gameplay systems.
"""

from typing import Dict, Tuple

# Equipment system constants
SUPPORTED_EQUIP_SLOTS: Tuple[str, ...] = ("weapon", "armor", "accessory")

# Formation positions and their combat effects
FORMATION_POSITIONS: Dict[str, Dict[str, float]] = {
    "front": {"defense_mod": -0.1, "attack_mod": 0.1, "aggro_mod": 1.5},   # More damage dealt/taken, draws aggro
    "middle": {"defense_mod": 0.0, "attack_mod": 0.0, "aggro_mod": 1.0},   # Balanced position
    "back": {"defense_mod": 0.1, "attack_mod": -0.1, "aggro_mod": 0.5},    # Less damage dealt/taken, avoids aggro
}

DEFAULT_FORMATION_POSITION: str = "middle"

# Screen dimension constants
DEFAULT_WINDOW_WIDTH: int = 640
DEFAULT_WINDOW_HEIGHT: int = 480
