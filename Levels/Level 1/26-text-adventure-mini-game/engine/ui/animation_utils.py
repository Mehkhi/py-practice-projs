"""Small animation helper functions for UI widgets.

These helpers keep simple animations (like cursor bounces and blinking
indicators) consistent across components.
"""

import math
from typing import Final


def advance_timer(timer: float, dt: float, speed: float = 1.0) -> float:
    """Advance an animation timer by ``dt`` scaled by ``speed``.

    This is a convenience wrapper for patterns like ``timer += dt * speed``.
    """
    return timer + dt * speed


def sine_wave(timer: float, frequency: float = 1.0) -> float:
    """Return a centered sine wave for the given ``timer``.

    The result is in the range [-1.0, 1.0]. ``frequency`` controls how many
    cycles occur per unit of ``timer``.
    """
    return math.sin(timer * frequency)


def sine_wave_01(timer: float, frequency: float = 1.0) -> float:
    """Return a sine wave remapped to the range [0.0, 1.0]."""
    return 0.5 + 0.5 * sine_wave(timer, frequency)
