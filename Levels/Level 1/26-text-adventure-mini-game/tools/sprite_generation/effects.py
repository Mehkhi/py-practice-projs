"""
Effects System for Sprite Generation

Provides auras, particle systems, and special visual effects
for bosses and special enemies.
"""

import pygame
import random
import math
from typing import List, Tuple, Optional

from .utils import create_surface, lerp_color, lighten_color, darken_color
from .palette import PALETTE


# =============================================================================
# AURA EFFECTS
# =============================================================================

def create_aura(color: tuple, intensity: str = 'medium',
                style: str = 'pulse', size: Tuple[int, int] = (64, 64),
                frames: int = 4) -> List[pygame.Surface]:
    """
    Create aura effect overlay for bosses/special enemies.

    Args:
        color: Base aura color (RGB or RGBA)
        intensity: 'low', 'medium', 'high'
        style: 'pulse', 'flame', 'void', 'holy', 'electric'
        size: Surface size
        frames: Number of animation frames

    Returns:
        List of aura overlay surfaces
    """
    intensity_values = {
        'low': {'alpha': 40, 'radius': 4, 'layers': 2},
        'medium': {'alpha': 60, 'radius': 6, 'layers': 3},
        'high': {'alpha': 80, 'radius': 8, 'layers': 4},
    }

    config = intensity_values.get(intensity, intensity_values['medium'])
    aura_frames = []

    for frame_idx in range(frames):
        surface = create_surface(size)
        cx, cy = size[0] // 2, size[1] // 2

        # Animation phase
        phase = (frame_idx / frames) * 2 * math.pi

        if style == 'pulse':
            _draw_pulse_aura(surface, cx, cy, color, config, phase)
        elif style == 'flame':
            _draw_flame_aura(surface, cx, cy, color, config, phase)
        elif style == 'void':
            _draw_void_aura(surface, cx, cy, color, config, phase)
        elif style == 'holy':
            _draw_holy_aura(surface, cx, cy, color, config, phase)
        elif style == 'electric':
            _draw_electric_aura(surface, cx, cy, color, config, phase)

        aura_frames.append(surface)

    return aura_frames


def _draw_pulse_aura(surface: pygame.Surface, cx: int, cy: int,
                     color: tuple, config: dict, phase: float) -> None:
    """Draw a pulsing glow aura."""
    base_radius = config['radius']
    alpha = config['alpha']
    layers = config['layers']

    # Pulse effect
    pulse = 1.0 + 0.2 * math.sin(phase)

    for i in range(layers, 0, -1):
        layer_radius = int(base_radius * i * 2 * pulse)
        layer_alpha = int(alpha / i)

        aura_color = (*color[:3], layer_alpha)
        pygame.draw.circle(surface, aura_color, (cx, cy), layer_radius)


def _draw_flame_aura(surface: pygame.Surface, cx: int, cy: int,
                     color: tuple, config: dict, phase: float) -> None:
    """Draw a flame-like aura with flickering edges."""
    base_radius = config['radius']
    alpha = config['alpha']

    # Draw base glow
    pygame.draw.circle(surface, (*color[:3], alpha // 2), (cx, cy), base_radius * 2)

    # Draw flame wisps
    num_flames = 8
    for i in range(num_flames):
        angle = (i / num_flames) * 2 * math.pi + phase
        flicker = random.uniform(0.7, 1.3)

        length = base_radius * 2 * flicker
        end_x = int(cx + math.cos(angle) * length)
        end_y = int(cy + math.sin(angle) * length)

        flame_color = lighten_color(color, 40)
        pygame.draw.line(surface, (*flame_color[:3], alpha),
                        (cx, cy), (end_x, end_y), 2)


def _draw_void_aura(surface: pygame.Surface, cx: int, cy: int,
                    color: tuple, config: dict, phase: float) -> None:
    """Draw a dark inward-pulling void aura."""
    base_radius = config['radius']
    alpha = config['alpha']
    layers = config['layers']

    # Outer dark ring
    for i in range(layers):
        ring_radius = base_radius * 3 - i * 2
        ring_alpha = int(alpha * (i + 1) / layers)
        ring_color = darken_color(color, 20 * i)

        pygame.draw.circle(surface, (*ring_color[:3], ring_alpha),
                          (cx, cy), ring_radius, 2)

    # Void tendrils pulling inward
    num_tendrils = 6
    for i in range(num_tendrils):
        angle = (i / num_tendrils) * 2 * math.pi + phase * 0.5

        start_radius = base_radius * 3
        end_radius = base_radius

        start_x = int(cx + math.cos(angle) * start_radius)
        start_y = int(cy + math.sin(angle) * start_radius)
        end_x = int(cx + math.cos(angle + 0.2) * end_radius)
        end_y = int(cy + math.sin(angle + 0.2) * end_radius)

        pygame.draw.line(surface, (*color[:3], alpha // 2),
                        (start_x, start_y), (end_x, end_y), 1)


def _draw_holy_aura(surface: pygame.Surface, cx: int, cy: int,
                    color: tuple, config: dict, phase: float) -> None:
    """Draw a bright outward-radiating holy aura."""
    base_radius = config['radius']
    alpha = config['alpha']

    # Bright central glow
    glow_color = lighten_color(color, 60)
    pygame.draw.circle(surface, (*glow_color[:3], alpha),
                      (cx, cy), base_radius * 2)

    # Radiating light beams
    num_beams = 8
    for i in range(num_beams):
        angle = (i / num_beams) * 2 * math.pi
        beam_length = base_radius * 3 + int(math.sin(phase + i) * base_radius)

        end_x = int(cx + math.cos(angle) * beam_length)
        end_y = int(cy + math.sin(angle) * beam_length)

        beam_color = (*color[:3], alpha // 2)
        pygame.draw.line(surface, beam_color, (cx, cy), (end_x, end_y), 1)


def _draw_electric_aura(surface: pygame.Surface, cx: int, cy: int,
                        color: tuple, config: dict, phase: float) -> None:
    """Draw a crackling electric aura."""
    base_radius = config['radius']
    alpha = config['alpha']

    # Base glow
    pygame.draw.circle(surface, (*color[:3], alpha // 3),
                      (cx, cy), base_radius * 2)

    # Electric arcs
    num_arcs = 5
    for i in range(num_arcs):
        angle = (i / num_arcs) * 2 * math.pi + phase

        # Create jagged lightning path
        points = [(cx, cy)]
        current_x, current_y = cx, cy
        length = base_radius * 3
        segments = 4

        for j in range(segments):
            progress = (j + 1) / segments
            target_x = cx + math.cos(angle) * length * progress
            target_y = cy + math.sin(angle) * length * progress

            # Add jitter
            jitter = random.randint(-3, 3)
            current_x = int(target_x + jitter)
            current_y = int(target_y + jitter)
            points.append((current_x, current_y))

        if len(points) >= 2:
            pygame.draw.lines(surface, (*color[:3], alpha), False, points, 1)


# =============================================================================
# PARTICLE SYSTEMS
# =============================================================================

def create_particle_effect(particle_type: str, color: tuple,
                           density: str = 'medium',
                           size: Tuple[int, int] = (64, 64),
                           frames: int = 4) -> List[pygame.Surface]:
    """
    Create particle effect overlay frames.

    Args:
        particle_type: 'ember', 'snow', 'shadow', 'sparkle', 'void', 'nature', 'magic'
        color: Base particle color
        density: 'low', 'medium', 'high'
        size: Surface size
        frames: Number of animation frames

    Returns:
        List of particle overlay surfaces
    """
    density_counts = {'low': 5, 'medium': 10, 'high': 20}
    num_particles = density_counts.get(density, 10)

    particle_frames = []

    # Generate particle positions that animate across frames
    particles = _generate_particle_paths(particle_type, num_particles, size, frames)

    for frame_idx in range(frames):
        surface = create_surface(size)

        for particle in particles:
            pos = particle['positions'][frame_idx]
            p_color = particle.get('color', color)
            p_size = particle.get('size', 2)
            p_alpha = particle.get('alpha', 200)

            if 0 <= pos[0] < size[0] and 0 <= pos[1] < size[1]:
                _draw_particle(surface, pos, p_color, p_size, p_alpha, particle_type)

        particle_frames.append(surface)

    return particle_frames


def _generate_particle_paths(particle_type: str, count: int,
                             size: Tuple[int, int], frames: int) -> List[dict]:
    """Generate particle movement paths based on type."""
    particles = []
    w, h = size

    for _ in range(count):
        particle = {'positions': [], 'size': random.randint(1, 3)}

        if particle_type == 'ember':
            # Rising ember particles
            start_x = random.randint(w // 4, 3 * w // 4)
            start_y = h - 10
            for f in range(frames):
                x = start_x + random.randint(-2, 2)
                y = start_y - (f * 8) + random.randint(-2, 2)
                particle['positions'].append((x, y))
            particle['color'] = random.choice([
                PALETTE.get('fire_orange', (255, 160, 50)),
                PALETTE.get('fire_yellow', (255, 230, 100)),
                PALETTE.get('fire_red', (220, 80, 30))
            ])

        elif particle_type == 'snow':
            # Falling snow particles
            start_x = random.randint(0, w)
            start_y = random.randint(-10, 0)
            for f in range(frames):
                x = start_x + int(math.sin(f * 0.5 + random.random()) * 3)
                y = start_y + (f * 6)
                particle['positions'].append((x, y))
            particle['color'] = PALETTE.get('ice_white', (240, 250, 255))

        elif particle_type == 'shadow':
            # Drifting shadow wisps
            start_x = random.randint(w // 4, 3 * w // 4)
            start_y = random.randint(h // 4, 3 * h // 4)
            angle = random.uniform(0, 2 * math.pi)
            for f in range(frames):
                x = start_x + int(math.cos(angle + f * 0.3) * 5)
                y = start_y + int(math.sin(angle + f * 0.3) * 5)
                particle['positions'].append((x, y))
            particle['color'] = PALETTE.get('void_purple', (60, 30, 80))
            particle['alpha'] = 120

        elif particle_type == 'sparkle':
            # Random twinkling sparkles
            x = random.randint(0, w)
            y = random.randint(0, h)
            for f in range(frames):
                particle['positions'].append((x, y))
            particle['size'] = 1 if random.random() > 0.5 else 2
            particle['alpha'] = random.choice([100, 150, 200, 255])
            particle['color'] = PALETTE.get('holy_white', (255, 255, 240))

        elif particle_type == 'void':
            # Swirling vortex particles
            cx, cy = w // 2, h // 2
            angle = random.uniform(0, 2 * math.pi)
            radius = random.randint(5, 20)
            for f in range(frames):
                current_angle = angle + f * 0.5
                current_radius = radius - f * 2
                x = cx + int(math.cos(current_angle) * current_radius)
                y = cy + int(math.sin(current_angle) * current_radius)
                particle['positions'].append((x, y))
            particle['color'] = PALETTE.get('void_glow', (150, 80, 200))

        elif particle_type == 'nature':
            # Floating leaves/petals
            start_x = random.randint(0, w)
            start_y = random.randint(0, h // 2)
            for f in range(frames):
                x = start_x + int(math.sin(f * 0.3 + random.random()) * 4)
                y = start_y + (f * 4)
                particle['positions'].append((x, y))
            particle['color'] = random.choice([
                PALETTE.get('leaf_light', (140, 200, 100)),
                PALETTE.get('flower_yellow', (250, 220, 80)),
                PALETTE.get('flower_purple', (160, 80, 180))
            ])

        elif particle_type == 'magic':
            # Orbiting rune particles
            cx, cy = w // 2, h // 2
            angle = random.uniform(0, 2 * math.pi)
            radius = random.randint(10, 25)
            for f in range(frames):
                current_angle = angle + f * 0.4
                x = cx + int(math.cos(current_angle) * radius)
                y = cy + int(math.sin(current_angle) * radius)
                particle['positions'].append((x, y))
            particle['color'] = random.choice([
                PALETTE.get('ice_light', (200, 230, 250)),
                PALETTE.get('fire_yellow', (255, 230, 100)),
                PALETTE.get('void_glow', (150, 80, 200))
            ])

        else:
            # Default: random floating
            x = random.randint(0, w)
            y = random.randint(0, h)
            for f in range(frames):
                particle['positions'].append((x + random.randint(-2, 2),
                                              y + random.randint(-2, 2)))

        particles.append(particle)

    return particles


def _draw_particle(surface: pygame.Surface, pos: Tuple[int, int],
                   color: tuple, size: int, alpha: int,
                   particle_type: str) -> None:
    """Draw a single particle."""
    x, y = int(pos[0]), int(pos[1])

    if len(color) == 3:
        draw_color = (*color, alpha)
    else:
        draw_color = (*color[:3], min(color[3], alpha))

    if particle_type in ['ember', 'sparkle', 'magic']:
        # Bright glowing particles
        pygame.draw.circle(surface, draw_color, (x, y), size)
        if size > 1:
            glow = (*color[:3], alpha // 3)
            pygame.draw.circle(surface, glow, (x, y), size + 1)

    elif particle_type in ['shadow', 'void']:
        # Soft dark particles
        pygame.draw.circle(surface, draw_color, (x, y), size + 1)

    elif particle_type == 'nature':
        # Leaf-like shape
        pygame.draw.ellipse(surface, draw_color, (x - 2, y - 1, 4, 2))

    else:
        pygame.draw.circle(surface, draw_color, (x, y), size)


# =============================================================================
# SPECIAL BOSS EFFECTS
# =============================================================================

def create_phase_transition_effect(boss_name: str, phase_num: int,
                                   size: Tuple[int, int] = (64, 64),
                                   frames: int = 8) -> List[pygame.Surface]:
    """
    Create dramatic effect for boss phase changes.

    Args:
        boss_name: Name of the boss
        phase_num: Phase number being transitioned to
        size: Surface size
        frames: Number of animation frames

    Returns:
        List of effect overlay surfaces
    """
    effect_frames = []

    for f in range(frames):
        surface = create_surface(size)
        progress = f / frames
        cx, cy = size[0] // 2, size[1] // 2

        if phase_num == 1:
            # Initial awakening - golden pulse
            color = PALETTE.get('gold_base', (255, 215, 0))
            radius = int(progress * 40)
            alpha = int((1 - progress) * 200)
            pygame.draw.circle(surface, (*color[:3], alpha), (cx, cy), radius, 3)

        elif phase_num == 2:
            # Power surge - red/orange
            color = PALETTE.get('fire_orange', (255, 160, 50))
            for i in range(3):
                radius = int(progress * 30 + i * 10)
                alpha = int((1 - progress) * 150)
                pygame.draw.circle(surface, (*color[:3], alpha), (cx, cy), radius, 2)

        elif phase_num == 3:
            # Desperate power - dark energy
            color = PALETTE.get('void_purple', (60, 30, 80))
            # Expanding void
            radius = int(progress * 50)
            pygame.draw.circle(surface, (*color[:3], 180), (cx, cy), radius)
            # Lightning cracks
            for _ in range(5):
                angle = random.uniform(0, 2 * math.pi)
                length = random.randint(10, 30)
                end_x = cx + int(math.cos(angle) * length)
                end_y = cy + int(math.sin(angle) * length)
                pygame.draw.line(surface, (200, 100, 255, 200),
                               (cx, cy), (end_x, end_y), 1)

        effect_frames.append(surface)

    return effect_frames


def create_ultimate_attack_effect(attack_name: str,
                                  size: Tuple[int, int] = (64, 64),
                                  frames: int = 8) -> List[pygame.Surface]:
    """
    Create screen-filling attack effect overlay.

    Args:
        attack_name: Name of the ultimate attack
        size: Surface size
        frames: Number of animation frames

    Returns:
        List of effect overlay surfaces
    """
    effect_frames = []

    attack_styles = {
        'fire_blast': ('fire', PALETTE.get('fire_orange', (255, 160, 50))),
        'ice_storm': ('ice', PALETTE.get('ice_base', (150, 200, 230))),
        'shadow_wave': ('shadow', PALETTE.get('void_purple', (60, 30, 80))),
        'holy_judgment': ('holy', PALETTE.get('holy_gold', (255, 230, 150))),
        'chaos_burst': ('chaos', (random.randint(100, 255),
                                  random.randint(100, 255),
                                  random.randint(100, 255))),
    }

    style, color = attack_styles.get(attack_name, ('fire', (255, 160, 50)))

    for f in range(frames):
        surface = create_surface(size)
        progress = f / frames
        cx, cy = size[0] // 2, size[1] // 2

        if style == 'fire':
            # Expanding fire wave
            radius = int(progress * 60)
            alpha = int((1 - progress * 0.5) * 200)
            pygame.draw.circle(surface, (*color[:3], alpha), (cx, cy), radius)

            # Fire particles
            for _ in range(10):
                px = cx + random.randint(-radius, radius)
                py = cy + random.randint(-radius, radius)
                pygame.draw.circle(surface, PALETTE.get('fire_yellow', (255, 230, 100)),
                                 (px, py), random.randint(1, 3))

        elif style == 'ice':
            # Freezing blast
            num_shards = 12
            for i in range(num_shards):
                angle = (i / num_shards) * 2 * math.pi
                length = int(progress * 50)
                end_x = cx + int(math.cos(angle) * length)
                end_y = cy + int(math.sin(angle) * length)
                pygame.draw.line(surface, (*color[:3], 200),
                               (cx, cy), (end_x, end_y), 2)

        elif style == 'shadow':
            # Dark wave
            for ring in range(int(progress * 5)):
                radius = ring * 10 + int(progress * 20)
                alpha = int((1 - progress) * 150)
                pygame.draw.circle(surface, (*color[:3], alpha),
                                 (cx, cy), radius, 2)

        elif style == 'holy':
            # Divine light beams
            num_beams = 16
            for i in range(num_beams):
                angle = (i / num_beams) * 2 * math.pi
                length = int(progress * 100)
                width = int((1 - progress) * 4) + 1
                end_x = cx + int(math.cos(angle) * length)
                end_y = cy + int(math.sin(angle) * length)
                pygame.draw.line(surface, (*color[:3], 200),
                               (cx, cy), (end_x, end_y), width)

        elif style == 'chaos':
            # Random chaotic energy
            for _ in range(20):
                px = random.randint(0, size[0])
                py = random.randint(0, size[1])
                chaos_color = (random.randint(100, 255),
                              random.randint(100, 255),
                              random.randint(100, 255),
                              random.randint(100, 200))
                pygame.draw.circle(surface, chaos_color, (px, py),
                                 random.randint(1, 4))

        effect_frames.append(surface)

    return effect_frames


def create_damage_flash(color: tuple = (255, 255, 255),
                        size: Tuple[int, int] = (64, 64)) -> pygame.Surface:
    """Create a simple damage flash overlay."""
    surface = create_surface(size)
    surface.fill((*color[:3], 100))
    return surface


def create_healing_effect(size: Tuple[int, int] = (64, 64),
                          frames: int = 4) -> List[pygame.Surface]:
    """Create healing sparkle effect."""
    color = PALETTE.get('leaf_light', (140, 200, 100))
    return create_particle_effect('sparkle', color, 'medium', size, frames)


def create_buff_effect(buff_type: str, size: Tuple[int, int] = (64, 64),
                       frames: int = 4) -> List[pygame.Surface]:
    """Create buff indicator effect."""
    buff_colors = {
        'attack': PALETTE.get('fire_red', (220, 80, 30)),
        'defense': PALETTE.get('steel_base', (180, 185, 195)),
        'speed': PALETTE.get('lightning_yellow', (255, 255, 150)),
        'magic': PALETTE.get('void_glow', (150, 80, 200)),
    }

    color = buff_colors.get(buff_type, (255, 255, 255))
    return create_aura(color, 'low', 'pulse', size, frames)


def create_debuff_effect(debuff_type: str, size: Tuple[int, int] = (64, 64),
                         frames: int = 4) -> List[pygame.Surface]:
    """Create debuff indicator effect."""
    debuff_colors = {
        'poison': PALETTE.get('slime_green', (120, 200, 100)),
        'burn': PALETTE.get('fire_orange', (255, 160, 50)),
        'freeze': PALETTE.get('ice_base', (150, 200, 230)),
        'curse': PALETTE.get('void_purple', (60, 30, 80)),
    }

    color = debuff_colors.get(debuff_type, (128, 0, 128))

    effect_frames = []
    for f in range(frames):
        surface = create_surface(size)

        # Dripping effect for debuffs
        for i in range(5):
            x = size[0] // 6 * (i + 1)
            y = random.randint(0, size[1] // 2) + f * 4
            if y < size[1]:
                pygame.draw.ellipse(surface, (*color[:3], 150),
                                  (x - 2, y, 4, 6))

        effect_frames.append(surface)

    return effect_frames
