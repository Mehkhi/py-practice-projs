"""Shared caching utilities for asset managers."""

import hashlib
import os
from typing import Set, Tuple

import pygame

# Check for numpy availability for faster pixel operations
try:
    import numpy  # type: ignore[reportMissingImports]  # Optional dependency
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    numpy = None  # type: ignore[assignment]  # Satisfy type checker when numpy is unavailable

# Environment variable to disable sprite transparency cleanup for performance
# Set ENABLE_SPRITE_TRANSPARENCY_CLEANUP=1 to enable (useful for fixing sprite artifacts)
ENABLE_TRANSPARENCY_CLEANUP = os.environ.get("ENABLE_SPRITE_TRANSPARENCY_CLEANUP", "").lower() in {"1", "true", "yes", "on"}


def surface_has_transparency(surface: pygame.Surface) -> bool:
    """Return True if any pixel has alpha < 255.

    Uses numpy surfarray for faster pixel access if available, otherwise
    falls back to per-pixel get_at() checks.
    """
    if HAS_NUMPY:
        try:
            # Use surfarray for much faster alpha channel access
            alpha_array = pygame.surfarray.pixels_alpha(surface)
            # Check if any alpha value is less than 255
            has_transparency = numpy.any(alpha_array < 255)
            # Release the array reference
            del alpha_array
            return bool(has_transparency)
        except (pygame.error, AttributeError):
            # Fall back to per-pixel method if surfarray fails
            pass

    # Fallback: per-pixel check (slow but works without numpy)
    w, h = surface.get_size()
    for y in range(h):
        for x in range(w):
            if surface.get_at((x, y)).a < 255:
                return True
    return False


def clean_sprite_transparency(image: pygame.Surface, entry: str = "") -> pygame.Surface:
    """Remove solid backgrounds and stray color data from sprite surfaces."""
    w, h = image.get_size()

    # If sprite already has transparency, clear stray color on fully transparent pixels
    if surface_has_transparency(image):
        try:
            image.lock()
            for y in range(h):
                for x in range(w):
                    c = image.get_at((x, y))
                    if c.a == 0 and (c.r or c.g or c.b):
                        image.set_at((x, y), (0, 0, 0, 0))
            image.unlock()
        except Exception as e:
            from core.logging_utils import log_warning
            log_warning(f"Alpha cleanup failed for {entry}: {e}")
        return image

    # Otherwise, attempt to treat a uniform corner color as a background to strip
    # BUT only if it's a known placeholder color (magenta, pure black, pure white)
    corners = [
        image.get_at((0, 0)),
        image.get_at((w - 1, 0)),
        image.get_at((0, h - 1)),
        image.get_at((w - 1, h - 1)),
    ]
    corner_colors = {(c.r, c.g, c.b) for c in corners}
    if len(corner_colors) != 1:
        return image

    bg_rgb = corner_colors.pop()

    # Only strip known placeholder/keying colors to avoid corrupting natural tile colors
    # Common placeholder colors: magenta (255, 0, 255), pink variants, pure black, pure white
    is_placeholder_color = (
        (bg_rgb[0] > 200 and bg_rgb[1] < 50 and bg_rgb[2] > 200) or  # Magenta/pink
        (bg_rgb == (0, 0, 0)) or  # Pure black
        (bg_rgb == (255, 255, 255))  # Pure white
    )

    if not is_placeholder_color:
        return image

    bg_matches = 0
    non_bg = 0
    try:
        image.lock()
        for y in range(h):
            for x in range(w):
                c = image.get_at((x, y))
                if (c.r, c.g, c.b) == bg_rgb:
                    bg_matches += 1
                else:
                    non_bg += 1
        image.unlock()
    except Exception as e:
        from core.logging_utils import log_warning
        log_warning(f"Background scan failed for {entry}: {e}")
        return image

    # If there's nothing but the background color, make the whole surface transparent
    total_pixels = w * h
    if non_bg == 0:
        image.fill((*bg_rgb, 0))
        return image

    coverage = bg_matches / total_pixels
    # Only strip if the background color clearly dominates
    if coverage >= 0.5:
        try:
            image.lock()
            for y in range(h):
                for x in range(w):
                    c = image.get_at((x, y))
                    if (c.r, c.g, c.b) == bg_rgb:
                        image.set_at((x, y), (bg_rgb[0], bg_rgb[1], bg_rgb[2], 0))
            image.unlock()
            from core.logging_utils import log_debug
            log_debug(f"Applied background transparency fix to {entry or 'sprite'}")
        except Exception as e:
            from core.logging_utils import log_warning
            log_warning(f"Transparency strip failed for {entry}: {e}")

    return image


def make_placeholder(sprite_id: str, size: Tuple[int, int] = (16, 16)) -> pygame.Surface:
    """Generate a pixel-art styled placeholder with a hash-based palette and transparency.

    Uses blake2b for deterministic hashing, ensuring consistent colors across
    Python runs regardless of PYTHONHASHSEED randomization.
    """
    width, height = size
    surface = pygame.Surface((width, height), pygame.SRCALPHA)

    # Use blake2b for deterministic hashing across Python runs
    digest = hashlib.blake2b(sprite_id.encode('utf-8'), digest_size=4).digest()
    color_hash = int.from_bytes(digest[:3], 'big')
    # Clamp to 50-205 range for visibility (avoid near-black/near-white)
    primary = (
        50 + ((color_hash >> 16) & 0xFF) % 156,
        50 + ((color_hash >> 8) & 0xFF) % 156,
        50 + (color_hash & 0xFF) % 156
    )
    # Darker accent color for contrast
    accent = (
        max(0, primary[2] - 50),
        max(0, primary[0] - 50),
        max(0, primary[1] - 50)
    )

    # Create a character-shaped placeholder with transparency around edges
    # Draw a simple circular/oval shape to represent a character
    center_x, center_y = width // 2, height // 2

    # Draw body (oval)
    body_rect = pygame.Rect(width // 4, height // 3, width // 2, height * 2 // 3 - 2)
    pygame.draw.ellipse(surface, accent, body_rect)
    pygame.draw.ellipse(surface, primary, body_rect.inflate(-4, -4))

    # Draw head (circle)
    head_radius = min(width, height) // 4
    pygame.draw.circle(surface, accent, (center_x, height // 4), head_radius)
    pygame.draw.circle(surface, primary, (center_x, height // 4), head_radius - 2)

    # Draw outline for visibility
    pygame.draw.ellipse(surface, (255, 255, 255), body_rect, 1)
    pygame.draw.circle(surface, (255, 255, 255), (center_x, height // 4), head_radius, 1)

    return surface
