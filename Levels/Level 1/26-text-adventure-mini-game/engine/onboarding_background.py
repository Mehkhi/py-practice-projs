"""Reusable onboarding background renderer.

This module provides background rendering utilities for onboarding scenes,
including gradient backgrounds, animated starfields, particles, and vignette effects.
These can be used independently and tested separately from scene logic.
"""

import math
from typing import Dict, List

import pygame

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    np = None  # type: ignore[assignment]
    HAS_NUMPY = False

from .theme import Colors
from .onboarding_theme import generate_stars, generate_particles, update_particles


class OnboardingBackgroundRenderer:
    """Manages and renders the onboarding background with stars, particles, and effects."""

    def __init__(self, width: int, height: int, star_seed: int = 42, particle_seed: int = 123):
        """Initialize the background renderer.

        Args:
            width: Screen width
            height: Screen height
            star_seed: Random seed for star field generation
            particle_seed: Random seed for particle generation
        """
        self.width = width
        self.height = height
        self.stars = generate_stars(50, width, height, seed=star_seed)
        self.particles = generate_particles(15, width, height, seed=particle_seed)
        self._cache: Dict[str, pygame.Surface] = {}
        self.anim_timer = 0.0

    def update(self, dt: float) -> None:
        """Update animation state and particle positions.

        Args:
            dt: Delta time in seconds
        """
        self.anim_timer += dt
        update_particles(self.particles, dt, self.width, self.height)

    def cleanup(self) -> None:
        """Explicitly clean up cached surfaces to free memory.

        Call this when the renderer is no longer needed, especially during
        window resizing or scene transitions.
        """
        # Drop cached surfaces so references are released promptly.
        self._cache.clear()
        self._cache = {}

    def _build_gradient_surface(self, width: int, height: int) -> pygame.Surface:
        """Create the onboarding gradient surface with an optional NumPy fast path."""
        grad = pygame.Surface((width, height))
        top, bottom = Colors.BG_ONBOARDING_TOP, Colors.BG_ONBOARDING_BOTTOM

        if HAS_NUMPY:
            y_indices = np.arange(height, dtype=np.float32) / height
            ratios = y_indices * y_indices * (3 - 2 * y_indices)  # Smoothstep

            r = (top[0] + (bottom[0] - top[0]) * ratios).astype(np.uint8)
            g = (top[1] + (bottom[1] - top[1]) * ratios).astype(np.uint8)
            b = (top[2] + (bottom[2] - top[2]) * ratios).astype(np.uint8)

            gradient_array = np.zeros((height, width, 3), dtype=np.uint8)
            gradient_array[:, :, 0] = r[:, np.newaxis]
            gradient_array[:, :, 1] = g[:, np.newaxis]
            gradient_array[:, :, 2] = b[:, np.newaxis]

            pygame.surfarray.blit_array(grad, gradient_array.swapaxes(0, 1))
        else:
            grad.lock()
            try:
                for y in range(height):
                    ratio = y / height
                    ratio = ratio * ratio * (3 - 2 * ratio)
                    r = int(top[0] + (bottom[0] - top[0]) * ratio)
                    g = int(top[1] + (bottom[1] - top[1]) * ratio)
                    b = int(top[2] + (bottom[2] - top[2]) * ratio)
                    pygame.draw.line(grad, (r, g, b), (0, y), (width - 1, y))
            finally:
                grad.unlock()

        return grad

    def _build_vignette_surface(self, width: int, height: int) -> pygame.Surface:
        """Create the vignette surface with an optional NumPy fast path."""
        vig = pygame.Surface((width, height), pygame.SRCALPHA)
        cx, cy = width // 2, height // 2
        max_dist = math.sqrt(cx ** 2 + cy ** 2)

        if HAS_NUMPY:
            x_coords = np.arange(width, dtype=np.float32)
            y_coords = np.arange(height, dtype=np.float32)
            xx, yy = np.meshgrid(x_coords, y_coords)

            distances = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
            alphas = np.minimum(80, (distances / max_dist) ** 2 * 120).astype(np.uint8)
            pygame.surfarray.pixels_alpha(vig)[:] = alphas.T
        else:
            vig.lock()
            try:
                for y in range(height):
                    dy = y - cy
                    for x in range(width):
                        dx = x - cx
                        distance = math.sqrt(dx * dx + dy * dy)
                        alpha = min(80, (distance / max_dist) ** 2 * 120)
                        vig.set_at((x, y), (0, 0, 0, int(alpha)))
            finally:
                vig.unlock()

        return vig

    def draw(self, surface: pygame.Surface, fade_in: float = 1.0) -> None:
        """Draw the complete onboarding background.

        Args:
            surface: Target surface to draw on
            fade_in: Fade-in alpha multiplier (0.0 to 1.0)
        """
        width, height = surface.get_size()

        # Update cache if dimensions changed
        if width != self.width or height != self.height:
            # Clear old cached surfaces - they're the wrong size now
            self._cache.clear()
            self.width = width
            self.height = height

        # Gradient background (cached) - using optimized NumPy-based rendering
        if self._cache.get("gradient") is None or self._cache["gradient"].get_size() != (width, height):
            self._cache["gradient"] = self._build_gradient_surface(width, height)
        surface.blit(self._cache["gradient"], (0, 0))

        # Stars
        for star in self.stars:
            twinkle = math.sin(self.anim_timer * star["twinkle_speed"] + star["twinkle_offset"])
            brightness = max(40, min(255, int(star["base_brightness"] + 60 * twinkle)))
            if star["layer"] == 0:
                color = (brightness, brightness, int(brightness * 1.1))
            elif star["layer"] == 1:
                color = (brightness, int(brightness * 0.95), brightness)
            else:
                color = (int(brightness * 1.1), int(brightness * 1.05), brightness)
            x, y = int(star["x"]), int(star["y"])
            size = star["size"]
            if size > 1.5:
                pygame.draw.circle(surface, (color[0]//4, color[1]//4, color[2]//4), (x, y), int(size + 2))
            pygame.draw.circle(surface, color, (x, y), max(1, int(size)))

        # Particles
        # Draw directly to surface - most efficient approach since particles have
        # varying colors/alphas per frame. Direct drawing avoids surface creation overhead.
        for p in self.particles:
            x, y = int(p["x"]), int(p["y"])
            if 0 <= x < width and 0 <= y < height:
                size = int(p["size"])
                alpha = int(p["alpha"] * (0.5 + 0.5 * math.sin(self.anim_timer * 2 + x * 0.1)))
                color = (*p["color"], max(20, min(255, alpha)))
                # Draw directly - pygame handles alpha blending efficiently
                pygame.draw.circle(surface, color, (x, y), size)

        # Vignette (cached) - using optimized NumPy-based rendering
        if self._cache.get("vignette") is None or self._cache["vignette"].get_size() != (width, height):
            self._cache["vignette"] = self._build_vignette_surface(width, height)
        surface.blit(self._cache["vignette"], (0, 0))


def draw_title_text(surface: pygame.Surface, text: str, font: pygame.font.Font,
                    center_x: int, y: int) -> None:
    """Draw title text with glow and shadow effects.

    Args:
        surface: Target surface to draw on
        text: Text to render
        font: Font to use for rendering
        center_x: X coordinate for center alignment
        y: Y coordinate for top alignment
    """
    shadow = font.render(text, True, Colors.TITLE_SHADOW)
    surface.blit(shadow, shadow.get_rect(center=(center_x + 2, y + 2)))
    glow = font.render(text, True, Colors.TITLE_GLOW)
    for off in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        surface.blit(glow, glow.get_rect(center=(center_x + off[0], y + off[1])))
    main = font.render(text, True, Colors.TITLE_MAIN)
    surface.blit(main, main.get_rect(center=(center_x, y)))


# Legacy function for backward compatibility
def draw_onboarding_background(surface: pygame.Surface, cache: dict, anim_timer: float,
                                stars: List[dict], particles: List[dict]) -> None:
    """Legacy function wrapper for backward compatibility.

    This function is deprecated. Use OnboardingBackgroundRenderer instead.

    Args:
        surface: Target surface to draw on
        cache: Background cache dictionary
        anim_timer: Animation timer value
        stars: List of star dictionaries
        particles: List of particle dictionaries
    """
    # Create a temporary renderer for compatibility
    width, height = surface.get_size()
    renderer = OnboardingBackgroundRenderer(width, height)
    renderer.stars = stars
    renderer.particles = particles
    renderer.anim_timer = anim_timer
    renderer._cache = cache
    renderer.draw(surface)
