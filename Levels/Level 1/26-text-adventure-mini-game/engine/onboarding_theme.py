"""Shared onboarding theme utilities.

This module centralizes star-field and particle generation used by onboarding
scenes (title, name entry, class selection) so they can be reused without
duplicating logic.

For onboarding colors, use the Colors class from engine.theme which provides:
- BG_ONBOARDING_TOP, BG_ONBOARDING_BOTTOM: Gradient background colors
- TITLE_MAIN, TITLE_GLOW, TITLE_SHADOW: Title text effects
- SUBTITLE, TEXT_HINT: Secondary text colors
- PANEL_BG_ONBOARDING, PANEL_BORDER_ONBOARDING: Panel styling
- LIST_BG, LIST_SELECTED: List styling
- STAT_HIGH, STAT_LOW, STAT_NORMAL: Stat display colors
- SKILL_TEXT: Blue text for skill labels and values
- PLACEHOLDER_BG: Background for placeholder elements
- DIVIDER: Decorative divider color
"""

import math
import random
from typing import List, Dict, Tuple

# Default particle colors for onboarding scenes
DEFAULT_PARTICLE_COLORS: List[Tuple[int, int, int]] = [
    (255, 220, 150),  # Warm gold
    (200, 180, 255),  # Soft purple
    (180, 220, 255),  # Light blue
]


def generate_stars(count: int, width: int, height: int, seed: int = 42) -> List[Dict]:
    """Generate a layered star field for onboarding scenes.

    Args:
        count: Number of stars to generate
        width: Screen width
        height: Screen height
        seed: Random seed for reproducible star positions

    Returns:
        List of star dictionaries with position, size, layer, and twinkle properties
    """
    stars: List[Dict] = []
    random.seed(seed)
    for _ in range(count):
        layer = random.choice([0, 0, 0, 1, 1, 2])
        stars.append(
            {
                "x": random.randint(0, width),
                "y": random.randint(0, height),
                "size": 1 + layer * 0.5,
                "layer": layer,
                "twinkle_offset": random.uniform(0, math.pi * 2),
                "twinkle_speed": random.uniform(1.5, 4.0),
                "base_brightness": 80 + layer * 40,
            }
        )
    return stars


def generate_particles(
    count: int,
    width: int,
    height: int,
    seed: int = 123,
    colors: List[Tuple[int, int, int]] = None,
) -> List[Dict]:
    """Generate floating ambient particles for onboarding scenes.

    Args:
        count: Number of particles to generate
        width: Screen width
        height: Screen height
        seed: Random seed for reproducible particle positions
        colors: Optional list of RGB tuples for particle colors

    Returns:
        List of particle dictionaries with position, velocity, size, alpha, and color
    """
    if colors is None:
        colors = DEFAULT_PARTICLE_COLORS

    particles: List[Dict] = []
    random.seed(seed)
    for _ in range(count):
        particles.append({
            "x": random.uniform(0, width),
            "y": random.uniform(0, height),
            "vx": random.uniform(-8, 8),
            "vy": random.uniform(-15, -5),
            "size": random.uniform(1, 3),
            "alpha": random.randint(40, 120),
            "color": random.choice(colors),
        })
    return particles


def update_particles(particles: List[Dict], dt: float, width: int, height: int) -> None:
    """Update particle positions with wrapping.

    Args:
        particles: List of particle dictionaries to update
        dt: Delta time in seconds
        width: Screen width for wrapping
        height: Screen height for wrapping
    """
    for p in particles:
        p["x"] += p["vx"] * dt
        p["y"] += p["vy"] * dt
        # Wrap vertically
        if p["y"] < -10:
            p["y"] = height + 10
            p["x"] = random.uniform(0, width)
        # Wrap horizontally
        if p["x"] < -10:
            p["x"] = width + 10
        elif p["x"] > width + 10:
            p["x"] = -10
