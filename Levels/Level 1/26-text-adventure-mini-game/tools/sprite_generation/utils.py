"""
Drawing Utilities and Helper Functions for Sprite Generation

Provides core drawing functions, scaling utilities, and advanced
shape drawing capabilities for creating detailed pixel art sprites.
"""

import pygame
import random
import math
from typing import Tuple, Optional, List, Dict

from .palette import PALETTE


def create_surface(size: Tuple[int, int] = (64, 64)) -> pygame.Surface:
    """
    Create a transparent surface at the specified size.

    Args:
        size: Tuple of (width, height), default (64, 64)

    Returns:
        Transparent pygame Surface
    """
    return pygame.Surface(size, pygame.SRCALPHA)


def scale_to_game_size(surface: pygame.Surface,
                       target_size: Tuple[int, int] = (32, 32)) -> pygame.Surface:
    """
    Scale surface to game size using smooth scaling for detail preservation.

    Uses pygame.transform.smoothscale for anti-aliased scaling which
    averages pixels together, preserving sub-pixel detail.

    Args:
        surface: Source surface (typically 64x64)
        target_size: Target size tuple, default (32, 32)

    Returns:
        Scaled pygame Surface
    """
    return pygame.transform.smoothscale(surface, target_size)


def draw_pixel(surface: pygame.Surface, color: tuple, pos: Tuple[int, int]) -> None:
    """
    Draw a single pixel with bounds checking.

    Args:
        surface: Target surface
        color: RGB or RGBA color tuple
        pos: (x, y) position
    """
    x, y = pos
    if 0 <= x < surface.get_width() and 0 <= y < surface.get_height():
        surface.set_at((x, y), color)


def draw_thick_pixel(surface: pygame.Surface, color: tuple,
                     pos: Tuple[int, int], thickness: int = 2) -> None:
    """
    Draw a 2x2 or 3x3 pixel block for thicker lines at 64x64.

    Args:
        surface: Target surface
        color: RGB or RGBA color tuple
        pos: Center (x, y) position
        thickness: 2 for 2x2, 3 for 3x3
    """
    x, y = pos
    if thickness == 2:
        for dx in range(2):
            for dy in range(2):
                draw_pixel(surface, color, (x + dx, y + dy))
    else:
        offset = thickness // 2
        for dx in range(-offset, offset + 1):
            for dy in range(-offset, offset + 1):
                draw_pixel(surface, color, (x + dx, y + dy))


def draw_antialiased_line(surface: pygame.Surface, color: tuple,
                          start: Tuple[int, int], end: Tuple[int, int],
                          width: int = 2) -> None:
    """
    Draw a smooth line with anti-aliasing.

    Args:
        surface: Target surface
        color: RGB or RGBA color tuple
        start: Start (x, y) position
        end: End (x, y) position
        width: Line width
    """
    pygame.draw.aaline(surface, color, start, end)
    if width > 1:
        # Draw additional lines for width
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        length = math.sqrt(dx * dx + dy * dy)
        if length > 0:
            nx = -dy / length
            ny = dx / length
            for i in range(1, width):
                offset = (i - width // 2) * 0.5
                s = (start[0] + nx * offset, start[1] + ny * offset)
                e = (end[0] + nx * offset, end[1] + ny * offset)
                pygame.draw.aaline(surface, color, s, e)


def draw_gradient_rect(surface: pygame.Surface, rect: Tuple[int, int, int, int],
                       top_color: tuple, bottom_color: tuple,
                       direction: str = 'vertical') -> None:
    """
    Draw a rectangle with gradient fill.

    Args:
        surface: Target surface
        rect: (x, y, width, height) tuple
        top_color: Starting color (top for vertical, left for horizontal)
        bottom_color: Ending color
        direction: 'vertical' or 'horizontal'
    """
    x, y, w, h = rect

    if direction == 'vertical':
        for i in range(h):
            t = i / max(1, h - 1)
            color = lerp_color(top_color, bottom_color, t)
            pygame.draw.line(surface, color, (x, y + i), (x + w - 1, y + i))
    else:
        for i in range(w):
            t = i / max(1, w - 1)
            color = lerp_color(top_color, bottom_color, t)
            pygame.draw.line(surface, color, (x + i, y), (x + i, y + h - 1))


def draw_gradient_circle(surface: pygame.Surface, center: Tuple[int, int],
                         radius: int, inner_color: tuple,
                         outer_color: tuple) -> None:
    """
    Draw a circle with radial gradient for 3D spherical effect.

    Args:
        surface: Target surface
        center: (x, y) center position
        radius: Circle radius
        inner_color: Color at center
        outer_color: Color at edge
    """
    for r in range(radius, 0, -1):
        t = 1 - (r / radius)
        color = lerp_color(outer_color, inner_color, t)
        pygame.draw.circle(surface, color, center, r)


def draw_ellipse_gradient(surface: pygame.Surface, rect: Tuple[int, int, int, int],
                          inner_color: tuple, outer_color: tuple) -> None:
    """
    Draw an ellipse with radial gradient.

    Args:
        surface: Target surface
        rect: Bounding rectangle (x, y, width, height)
        inner_color: Color at center
        outer_color: Color at edge
    """
    x, y, w, h = rect
    steps = max(w, h) // 2
    for i in range(steps, 0, -1):
        t = 1 - (i / steps)
        color = lerp_color(outer_color, inner_color, t)
        scale = i / steps
        ew = int(w * scale)
        eh = int(h * scale)
        ex = x + (w - ew) // 2
        ey = y + (h - eh) // 2
        if ew > 0 and eh > 0:
            pygame.draw.ellipse(surface, color, (ex, ey, ew, eh))


def apply_dither(surface: pygame.Surface, color: tuple,
                 pattern: str = 'checkerboard', density: float = 0.3) -> None:
    """
    Apply a dither pattern for texture.

    Args:
        surface: Target surface
        color: Color to dither with
        pattern: 'checkerboard', 'noise', or 'diagonal'
        density: Dither density (0.0 to 1.0)
    """
    w, h = surface.get_size()

    for y in range(h):
        for x in range(w):
            pixel = surface.get_at((x, y))
            if pixel.a > 0:  # Only dither non-transparent pixels
                apply_dither_pixel = False

                if pattern == 'checkerboard':
                    apply_dither_pixel = (x + y) % 2 == 0
                elif pattern == 'noise':
                    apply_dither_pixel = random.random() < density
                elif pattern == 'diagonal':
                    apply_dither_pixel = (x + y) % 3 == 0

                if apply_dither_pixel and random.random() < density:
                    surface.set_at((x, y), color)


def add_noise_texture(surface: pygame.Surface, intensity: int = 15,
                      preserve_alpha: bool = True) -> None:
    """
    Add subtle noise for organic texture.

    Args:
        surface: Target surface
        intensity: Noise intensity (0-255)
        preserve_alpha: If True, only modify visible pixels
    """
    w, h = surface.get_size()

    for y in range(h):
        for x in range(w):
            pixel = surface.get_at((x, y))
            if not preserve_alpha or pixel.a > 0:
                noise = random.randint(-intensity, intensity)
                r = max(0, min(255, pixel.r + noise))
                g = max(0, min(255, pixel.g + noise))
                b = max(0, min(255, pixel.b + noise))
                surface.set_at((x, y), (r, g, b, pixel.a))


def add_outline(surface: pygame.Surface, color: tuple,
                thickness: int = 1) -> pygame.Surface:
    """
    Add pixel-perfect outline around non-transparent pixels.

    Args:
        surface: Source surface
        color: Outline color
        thickness: Outline thickness in pixels

    Returns:
        New surface with outline
    """
    w, h = surface.get_size()
    result = create_surface((w + thickness * 2, h + thickness * 2))

    # Find all edge pixels and draw outline
    for y in range(h):
        for x in range(w):
            if surface.get_at((x, y)).a > 0:
                # Check all neighbors
                for dy in range(-thickness, thickness + 1):
                    for dx in range(-thickness, thickness + 1):
                        if dx == 0 and dy == 0:
                            continue
                        nx, ny = x + dx, y + dy
                        if nx < 0 or nx >= w or ny < 0 or ny >= h:
                            # Out of bounds = edge
                            draw_pixel(result, color,
                                       (x + thickness + dx, y + thickness + dy))
                        elif surface.get_at((nx, ny)).a == 0:
                            # Transparent neighbor = edge
                            draw_pixel(result, color,
                                       (x + thickness + dx, y + thickness + dy))

    # Blit original on top
    result.blit(surface, (thickness, thickness))
    return result


def add_shadow(surface: pygame.Surface, offset: Tuple[int, int] = (2, 2),
               color: tuple = (0, 0, 0, 80)) -> pygame.Surface:
    """
    Add drop shadow beneath sprite.

    Args:
        surface: Source surface
        offset: Shadow offset (x, y)
        color: Shadow color with alpha

    Returns:
        New surface with shadow
    """
    w, h = surface.get_size()
    ox, oy = offset
    result = create_surface((w + abs(ox), h + abs(oy)))

    # Create shadow mask
    shadow = create_surface((w, h))
    for y in range(h):
        for x in range(w):
            if surface.get_at((x, y)).a > 0:
                shadow.set_at((x, y), color)

    # Position shadow
    shadow_x = ox if ox > 0 else 0
    shadow_y = oy if oy > 0 else 0
    result.blit(shadow, (shadow_x, shadow_y))

    # Position sprite
    sprite_x = 0 if ox > 0 else abs(ox)
    sprite_y = 0 if oy > 0 else abs(oy)
    result.blit(surface, (sprite_x, sprite_y))

    return result


def add_highlight(surface: pygame.Surface, direction: str = 'top-left',
                  intensity: int = 40) -> None:
    """
    Add directional highlight for 3D effect.

    Args:
        surface: Target surface (modified in place)
        direction: 'top-left', 'top-right', 'bottom-left', 'bottom-right'
        intensity: Highlight intensity
    """
    w, h = surface.get_size()

    for y in range(h):
        for x in range(w):
            pixel = surface.get_at((x, y))
            if pixel.a > 0:
                # Calculate distance from highlight source
                if direction == 'top-left':
                    dist = math.sqrt(x * x + y * y) / math.sqrt(w * w + h * h)
                elif direction == 'top-right':
                    dist = math.sqrt((w - x) ** 2 + y * y) / math.sqrt(w * w + h * h)
                elif direction == 'bottom-left':
                    dist = math.sqrt(x * x + (h - y) ** 2) / math.sqrt(w * w + h * h)
                else:  # bottom-right
                    dist = math.sqrt((w - x) ** 2 + (h - y) ** 2) / math.sqrt(w * w + h * h)

                # Apply highlight (inverse of distance)
                highlight = int((1 - dist) * intensity)
                r = min(255, pixel.r + highlight)
                g = min(255, pixel.g + highlight)
                b = min(255, pixel.b + highlight)
                surface.set_at((x, y), (r, g, b, pixel.a))


def lerp_color(color1: tuple, color2: tuple, t: float) -> tuple:
    """
    Linear interpolation between two colors.

    Args:
        color1: Starting color (RGB or RGBA)
        color2: Ending color (RGB or RGBA)
        t: Interpolation factor (0.0 to 1.0)

    Returns:
        Interpolated color tuple
    """
    t = max(0.0, min(1.0, t))

    r = int(color1[0] + (color2[0] - color1[0]) * t)
    g = int(color1[1] + (color2[1] - color1[1]) * t)
    b = int(color1[2] + (color2[2] - color1[2]) * t)

    if len(color1) > 3 and len(color2) > 3:
        a = int(color1[3] + (color2[3] - color1[3]) * t)
        return (r, g, b, a)

    return (r, g, b)


def darken_color(color: tuple, amount: int = 40) -> tuple:
    """
    Return a darker version of the color.

    Args:
        color: RGB or RGBA color tuple
        amount: Amount to darken (0-255)

    Returns:
        Darkened color tuple
    """
    r = max(0, color[0] - amount)
    g = max(0, color[1] - amount)
    b = max(0, color[2] - amount)

    if len(color) > 3:
        return (r, g, b, color[3])
    return (r, g, b)


def lighten_color(color: tuple, amount: int = 40) -> tuple:
    """
    Return a lighter version of the color.

    Args:
        color: RGB or RGBA color tuple
        amount: Amount to lighten (0-255)

    Returns:
        Lightened color tuple
    """
    r = min(255, color[0] + amount)
    g = min(255, color[1] + amount)
    b = min(255, color[2] + amount)

    if len(color) > 3:
        return (r, g, b, color[3])
    return (r, g, b)


def saturate_color(color: tuple, amount: float = 1.5) -> tuple:
    """
    Increase or decrease color saturation.

    Args:
        color: RGB or RGBA color tuple
        amount: Saturation multiplier (1.0 = no change)

    Returns:
        Saturated color tuple
    """
    grey = (color[0] + color[1] + color[2]) // 3
    r = int(grey + (color[0] - grey) * amount)
    g = int(grey + (color[1] - grey) * amount)
    b = int(grey + (color[2] - grey) * amount)

    r = max(0, min(255, r))
    g = max(0, min(255, g))
    b = max(0, min(255, b))

    if len(color) > 3:
        return (r, g, b, color[3])
    return (r, g, b)


# =============================================================================
# ADVANCED DRAWING FUNCTIONS
# =============================================================================

def draw_humanoid_base(surface: pygame.Surface, skin_color: tuple,
                       proportions: str = 'normal') -> Dict[str, Tuple[int, int]]:
    """
    Draw basic humanoid shape (head, torso, arms, legs).

    Args:
        surface: Target surface (64x64)
        skin_color: Skin color tuple
        proportions: 'normal', 'stocky', 'tall', 'child', 'muscular'

    Returns:
        Dict of body part positions for attaching details
    """
    w, h = surface.get_size()
    cx = w // 2  # Center x

    # Define proportions
    if proportions == 'stocky':
        head_size = 14
        body_width = 20
        body_height = 18
        leg_height = 16
        arm_width = 6
    elif proportions == 'tall':
        head_size = 12
        body_width = 14
        body_height = 22
        leg_height = 20
        arm_width = 4
    elif proportions == 'child':
        head_size = 16
        body_width = 14
        body_height = 12
        leg_height = 12
        arm_width = 4
    elif proportions == 'muscular':
        head_size = 12
        body_width = 22
        body_height = 20
        leg_height = 18
        arm_width = 8
    else:  # normal
        head_size = 12
        body_width = 16
        body_height = 18
        leg_height = 18
        arm_width = 5

    skin_shadow = darken_color(skin_color, 30)
    skin_highlight = lighten_color(skin_color, 20)

    positions = {}

    # Calculate positions
    head_y = 4
    body_y = head_y + head_size
    leg_y = body_y + body_height

    # Draw head
    head_rect = (cx - head_size // 2, head_y, head_size, head_size)
    pygame.draw.ellipse(surface, skin_color, head_rect)
    positions['head'] = (cx, head_y + head_size // 2)
    positions['face'] = (cx, head_y + head_size // 2 + 2)

    # Draw body/torso
    body_rect = (cx - body_width // 2, body_y, body_width, body_height)
    pygame.draw.rect(surface, skin_shadow, body_rect)
    positions['torso'] = (cx, body_y + body_height // 2)
    positions['chest'] = (cx, body_y + 4)

    # Draw arms
    left_arm_x = cx - body_width // 2 - arm_width
    right_arm_x = cx + body_width // 2
    arm_height = body_height - 4

    pygame.draw.rect(surface, skin_color, (left_arm_x, body_y + 2, arm_width, arm_height))
    pygame.draw.rect(surface, skin_color, (right_arm_x, body_y + 2, arm_width, arm_height))

    positions['left_hand'] = (left_arm_x + arm_width // 2, body_y + arm_height)
    positions['right_hand'] = (right_arm_x + arm_width // 2, body_y + arm_height)
    positions['left_shoulder'] = (left_arm_x + arm_width, body_y + 2)
    positions['right_shoulder'] = (right_arm_x, body_y + 2)

    # Draw legs
    leg_width = body_width // 2 - 2
    leg_gap = 4
    left_leg_x = cx - leg_width - leg_gap // 2
    right_leg_x = cx + leg_gap // 2

    pygame.draw.rect(surface, skin_shadow, (left_leg_x, leg_y, leg_width, leg_height))
    pygame.draw.rect(surface, skin_shadow, (right_leg_x, leg_y, leg_width, leg_height))

    positions['left_foot'] = (left_leg_x + leg_width // 2, leg_y + leg_height)
    positions['right_foot'] = (right_leg_x + leg_width // 2, leg_y + leg_height)

    return positions


def draw_eyes(surface: pygame.Surface, position: Tuple[int, int],
              style: str = 'normal', color: tuple = None,
              glow: bool = False) -> None:
    """
    Draw eyes with various styles.

    Args:
        surface: Target surface
        position: Center position (x, y)
        style: 'normal', 'angry', 'glowing', 'hollow', 'beast', 'single'
        color: Eye color (default white with black pupil)
        glow: Add glow effect
    """
    x, y = position

    if color is None:
        color = PALETTE['eye_white']

    pupil_color = PALETTE.get('black', (0, 0, 0))

    if style == 'normal':
        # Two oval eyes
        pygame.draw.ellipse(surface, color, (x - 6, y - 2, 4, 4))
        pygame.draw.ellipse(surface, color, (x + 2, y - 2, 4, 4))
        draw_pixel(surface, pupil_color, (x - 4, y))
        draw_pixel(surface, pupil_color, (x + 4, y))

    elif style == 'angry':
        # Angled angry eyes
        pygame.draw.ellipse(surface, color, (x - 6, y - 2, 4, 3))
        pygame.draw.ellipse(surface, color, (x + 2, y - 2, 4, 3))
        draw_pixel(surface, pupil_color, (x - 4, y - 1))
        draw_pixel(surface, pupil_color, (x + 4, y - 1))
        # Angry brow
        pygame.draw.line(surface, darken_color(color, 60), (x - 7, y - 4), (x - 3, y - 3))
        pygame.draw.line(surface, darken_color(color, 60), (x + 3, y - 3), (x + 7, y - 4))

    elif style == 'glowing':
        # Glowing eyes with glow effect
        glow_color = lighten_color(color, 50)
        if glow:
            pygame.draw.circle(surface, (*color[:3], 60), (x - 4, y), 5)
            pygame.draw.circle(surface, (*color[:3], 60), (x + 4, y), 5)
        pygame.draw.ellipse(surface, glow_color, (x - 6, y - 2, 4, 4))
        pygame.draw.ellipse(surface, glow_color, (x + 2, y - 2, 4, 4))

    elif style == 'hollow':
        # Dark hollow eye sockets
        pygame.draw.ellipse(surface, (20, 20, 30), (x - 6, y - 3, 5, 5))
        pygame.draw.ellipse(surface, (20, 20, 30), (x + 1, y - 3, 5, 5))
        if glow:
            draw_pixel(surface, color, (x - 4, y))
            draw_pixel(surface, color, (x + 4, y))

    elif style == 'beast':
        # Beast-like horizontal slit eyes
        pygame.draw.ellipse(surface, color, (x - 7, y - 1, 6, 3))
        pygame.draw.ellipse(surface, color, (x + 1, y - 1, 6, 3))
        pygame.draw.line(surface, pupil_color, (x - 5, y - 1), (x - 5, y + 1))
        pygame.draw.line(surface, pupil_color, (x + 4, y - 1), (x + 4, y + 1))

    elif style == 'single':
        # Single large eye (cyclops)
        pygame.draw.ellipse(surface, color, (x - 5, y - 4, 10, 8))
        pygame.draw.circle(surface, pupil_color, (x, y), 2)
        if glow:
            pygame.draw.circle(surface, (*color[:3], 80), (x, y), 7)


def draw_hair(surface: pygame.Surface, head_position: Tuple[int, int],
              style: str = 'short', color: tuple = None) -> None:
    """
    Draw hair with various styles.

    Args:
        surface: Target surface
        head_position: Head center position (x, y)
        style: 'short', 'long', 'bald', 'mohawk', 'ponytail', 'wild', 'flowing'
        color: Hair color
    """
    x, y = head_position

    if color is None:
        color = PALETTE['hair_brown']

    dark = darken_color(color, 30)
    light = lighten_color(color, 20)

    if style == 'bald':
        return

    elif style == 'short':
        # Short cropped hair
        pygame.draw.ellipse(surface, color, (x - 7, y - 10, 14, 10))
        pygame.draw.ellipse(surface, dark, (x - 5, y - 8, 10, 6))

    elif style == 'long':
        # Long flowing hair
        pygame.draw.ellipse(surface, color, (x - 8, y - 10, 16, 12))
        pygame.draw.rect(surface, color, (x - 8, y, 4, 16))
        pygame.draw.rect(surface, dark, (x + 4, y, 4, 16))

    elif style == 'mohawk':
        # Punk mohawk
        for i in range(8):
            spike_h = 6 + random.randint(-2, 2)
            pygame.draw.rect(surface, color, (x - 2 + i * 1 - 3, y - 10 - spike_h, 2, spike_h))

    elif style == 'ponytail':
        # Hair with ponytail
        pygame.draw.ellipse(surface, color, (x - 7, y - 10, 14, 10))
        pygame.draw.rect(surface, color, (x - 2, y - 2, 4, 2))
        pygame.draw.ellipse(surface, dark, (x - 3, y, 6, 14))

    elif style == 'wild':
        # Wild unkempt hair
        pygame.draw.ellipse(surface, color, (x - 10, y - 12, 20, 14))
        for _ in range(6):
            sx = x + random.randint(-8, 8)
            sy = y - 10 + random.randint(-4, 2)
            pygame.draw.circle(surface, light, (sx, sy), random.randint(2, 4))

    elif style == 'flowing':
        # Magical flowing hair
        pygame.draw.ellipse(surface, color, (x - 8, y - 10, 16, 12))
        # Flowing strands
        for i in range(3):
            strand_x = x - 8 + i * 4
            points = [
                (strand_x, y),
                (strand_x - 2 - i, y + 8),
                (strand_x - 1 - i, y + 16),
                (strand_x + 2 - i, y + 20)
            ]
            if len(points) >= 2:
                pygame.draw.lines(surface, light, False, points, 2)


def draw_clothing(surface: pygame.Surface, body_positions: Dict[str, Tuple[int, int]],
                  clothing_type: str, color: tuple) -> None:
    """
    Draw clothing over body.

    Args:
        surface: Target surface
        body_positions: Dict of body part positions from draw_humanoid_base
        clothing_type: 'tunic', 'robe', 'armor', 'dress', 'leather', 'cloak'
        color: Primary clothing color
    """
    torso = body_positions.get('torso', (32, 32))
    chest = body_positions.get('chest', (32, 24))

    dark = darken_color(color, 40)
    light = lighten_color(color, 30)

    if clothing_type == 'tunic':
        # Simple tunic
        pygame.draw.rect(surface, color, (torso[0] - 8, chest[1] - 2, 16, 16))
        pygame.draw.rect(surface, dark, (torso[0] - 8, chest[1] + 10, 16, 4))

    elif clothing_type == 'robe':
        # Long flowing robe
        pygame.draw.rect(surface, color, (torso[0] - 10, chest[1] - 4, 20, 28))
        pygame.draw.rect(surface, dark, (torso[0] - 10, chest[1] + 20, 20, 8))
        # Robe opening
        pygame.draw.line(surface, dark, (torso[0], chest[1]), (torso[0], chest[1] + 24), 2)

    elif clothing_type == 'armor':
        # Plate armor
        pygame.draw.rect(surface, color, (torso[0] - 10, chest[1] - 2, 20, 18))
        # Shoulder pads
        pygame.draw.ellipse(surface, light, (torso[0] - 14, chest[1] - 4, 8, 6))
        pygame.draw.ellipse(surface, light, (torso[0] + 6, chest[1] - 4, 8, 6))
        # Armor details
        pygame.draw.rect(surface, dark, (torso[0] - 4, chest[1] + 2, 8, 2))

    elif clothing_type == 'dress':
        # Flowing dress
        points = [
            (torso[0] - 8, chest[1]),
            (torso[0] + 8, chest[1]),
            (torso[0] + 14, chest[1] + 30),
            (torso[0] - 14, chest[1] + 30)
        ]
        pygame.draw.polygon(surface, color, points)
        pygame.draw.polygon(surface, dark, points, 2)

    elif clothing_type == 'leather':
        # Leather armor
        pygame.draw.rect(surface, color, (torso[0] - 9, chest[1] - 2, 18, 16))
        # Straps
        pygame.draw.line(surface, dark, (torso[0] - 6, chest[1]), (torso[0] - 6, chest[1] + 14), 2)
        pygame.draw.line(surface, dark, (torso[0] + 6, chest[1]), (torso[0] + 6, chest[1] + 14), 2)

    elif clothing_type == 'cloak':
        # Hooded cloak
        pygame.draw.ellipse(surface, color, (torso[0] - 8, chest[1] - 16, 16, 12))  # Hood
        pygame.draw.rect(surface, color, (torso[0] - 12, chest[1] - 6, 24, 30))  # Body
        pygame.draw.rect(surface, dark, (torso[0] - 12, chest[1] + 20, 24, 6))  # Bottom


def draw_weapon(surface: pygame.Surface, hand_position: Tuple[int, int],
                weapon_type: str, metal_color: tuple) -> None:
    """
    Draw a weapon in hand.

    Args:
        surface: Target surface
        hand_position: Hand position (x, y)
        weapon_type: 'sword', 'staff', 'dagger', 'axe', 'bow', 'shield', 'spear'
        metal_color: Metal color for weapon
    """
    x, y = hand_position
    dark = darken_color(metal_color, 40)
    light = lighten_color(metal_color, 30)
    handle_color = PALETTE.get('leather_dark', (80, 55, 35))

    if weapon_type == 'sword':
        # Sword blade
        pygame.draw.rect(surface, metal_color, (x - 1, y - 20, 3, 18))
        pygame.draw.polygon(surface, light, [(x - 1, y - 20), (x + 2, y - 20), (x, y - 24)])
        # Handle
        pygame.draw.rect(surface, handle_color, (x - 1, y - 2, 3, 6))
        # Crossguard
        pygame.draw.rect(surface, dark, (x - 4, y - 3, 9, 2))

    elif weapon_type == 'staff':
        # Wooden staff
        pygame.draw.rect(surface, handle_color, (x - 1, y - 28, 3, 32))
        # Crystal top
        pygame.draw.circle(surface, PALETTE.get('ice_light', (200, 230, 250)), (x, y - 30), 4)
        pygame.draw.circle(surface, (255, 255, 255), (x - 1, y - 31), 1)

    elif weapon_type == 'dagger':
        # Short dagger
        pygame.draw.rect(surface, metal_color, (x - 1, y - 10, 2, 8))
        pygame.draw.polygon(surface, light, [(x - 1, y - 10), (x + 1, y - 10), (x, y - 13)])
        pygame.draw.rect(surface, handle_color, (x - 1, y - 2, 2, 4))

    elif weapon_type == 'axe':
        # Battle axe
        pygame.draw.rect(surface, handle_color, (x - 1, y - 22, 3, 24))
        # Axe head
        pygame.draw.polygon(surface, metal_color, [
            (x - 8, y - 18), (x - 8, y - 8),
            (x, y - 6), (x, y - 20)
        ])
        pygame.draw.polygon(surface, dark, [
            (x - 8, y - 18), (x - 8, y - 8),
            (x, y - 6), (x, y - 20)
        ], 1)

    elif weapon_type == 'bow':
        # Wooden bow
        pygame.draw.arc(surface, handle_color, (x - 16, y - 24, 16, 48), 1.57, 4.71, 2)
        # String
        pygame.draw.line(surface, (200, 200, 180), (x - 8, y - 22), (x - 8, y + 22))

    elif weapon_type == 'shield':
        # Round shield
        pygame.draw.circle(surface, metal_color, (x, y - 8), 10)
        pygame.draw.circle(surface, dark, (x, y - 8), 10, 2)
        pygame.draw.circle(surface, light, (x, y - 8), 4)

    elif weapon_type == 'spear':
        # Long spear
        pygame.draw.rect(surface, handle_color, (x - 1, y - 30, 2, 34))
        # Spear head
        pygame.draw.polygon(surface, metal_color, [
            (x - 3, y - 30), (x + 3, y - 30),
            (x, y - 38)
        ])


def draw_accessory(surface: pygame.Surface, position: Tuple[int, int],
                   accessory_type: str, color: tuple) -> None:
    """
    Draw an accessory or headwear.

    Args:
        surface: Target surface
        position: Position (x, y)
        accessory_type: 'hat', 'helmet', 'crown', 'hood', 'horns', 'mask', 'glasses'
        color: Accessory color
    """
    x, y = position
    dark = darken_color(color, 30)
    light = lighten_color(color, 30)

    if accessory_type == 'hat':
        # Wide-brimmed hat
        pygame.draw.ellipse(surface, color, (x - 12, y - 4, 24, 6))
        pygame.draw.ellipse(surface, dark, (x - 6, y - 10, 12, 8))

    elif accessory_type == 'helmet':
        # Knight helmet
        pygame.draw.ellipse(surface, color, (x - 8, y - 10, 16, 14))
        pygame.draw.rect(surface, dark, (x - 6, y - 2, 12, 2))  # Visor slit
        pygame.draw.rect(surface, light, (x - 1, y - 14, 2, 8))  # Crest

    elif accessory_type == 'crown':
        # Royal crown
        pygame.draw.rect(surface, color, (x - 8, y - 6, 16, 6))
        # Crown points
        for i in range(5):
            px = x - 6 + i * 3
            pygame.draw.polygon(surface, color, [
                (px, y - 6), (px + 2, y - 6), (px + 1, y - 10)
            ])
        # Gems
        pygame.draw.circle(surface, PALETTE.get('eye_red', (200, 50, 50)), (x, y - 4), 2)

    elif accessory_type == 'hood':
        # Hooded cloak
        pygame.draw.ellipse(surface, color, (x - 10, y - 12, 20, 16))
        pygame.draw.ellipse(surface, dark, (x - 6, y - 6, 12, 10))

    elif accessory_type == 'horns':
        # Demon/beast horns
        pygame.draw.polygon(surface, color, [
            (x - 8, y - 4), (x - 12, y - 16), (x - 6, y - 6)
        ])
        pygame.draw.polygon(surface, color, [
            (x + 8, y - 4), (x + 12, y - 16), (x + 6, y - 6)
        ])
        pygame.draw.polygon(surface, dark, [
            (x - 8, y - 4), (x - 12, y - 16), (x - 6, y - 6)
        ], 1)
        pygame.draw.polygon(surface, dark, [
            (x + 8, y - 4), (x + 12, y - 16), (x + 6, y - 6)
        ], 1)

    elif accessory_type == 'mask':
        # Face mask
        pygame.draw.ellipse(surface, color, (x - 6, y - 4, 12, 10))
        draw_pixel(surface, (0, 0, 0), (x - 3, y))
        draw_pixel(surface, (0, 0, 0), (x + 3, y))

    elif accessory_type == 'glasses':
        # Round spectacles
        pygame.draw.circle(surface, color, (x - 4, y), 4, 1)
        pygame.draw.circle(surface, color, (x + 4, y), 4, 1)
        pygame.draw.line(surface, color, (x, y), (x, y))  # Bridge


# =============================================================================
# SHAPE DRAWING UTILITIES
# =============================================================================

def draw_filled_circle(surface: pygame.Surface, color: tuple,
                       center: Tuple[int, int], radius: int) -> None:
    """Draw a filled circle with anti-aliased edge."""
    pygame.draw.circle(surface, color, center, radius)


def draw_rounded_rect(surface: pygame.Surface, color: tuple,
                      rect: Tuple[int, int, int, int], radius: int) -> None:
    """
    Draw a rectangle with rounded corners.

    Args:
        surface: Target surface
        color: Fill color
        rect: (x, y, width, height)
        radius: Corner radius
    """
    x, y, w, h = rect
    radius = min(radius, w // 2, h // 2)

    # Main rectangle minus corners
    pygame.draw.rect(surface, color, (x + radius, y, w - 2 * radius, h))
    pygame.draw.rect(surface, color, (x, y + radius, w, h - 2 * radius))

    # Corner circles
    pygame.draw.circle(surface, color, (x + radius, y + radius), radius)
    pygame.draw.circle(surface, color, (x + w - radius, y + radius), radius)
    pygame.draw.circle(surface, color, (x + radius, y + h - radius), radius)
    pygame.draw.circle(surface, color, (x + w - radius, y + h - radius), radius)


def draw_polygon_thick(surface: pygame.Surface, color: tuple,
                       points: List[Tuple[int, int]], thickness: int = 2) -> None:
    """Draw a thick polygon outline."""
    pygame.draw.polygon(surface, color, points, thickness)


def fill_polygon(surface: pygame.Surface, color: tuple,
                 points: List[Tuple[int, int]]) -> None:
    """Draw a filled polygon."""
    pygame.draw.polygon(surface, color, points)
