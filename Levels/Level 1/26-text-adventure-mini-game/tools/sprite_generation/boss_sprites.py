"""
Boss Sprite Generators

Contains sprite generators for all boss encounters with special effects:
- Ancient Guardian (Final Boss)
- Zyraxis, Ancient Wyrm
- Umbraxis, Shadow Sovereign
- ??? True Final Boss
- Sir Aldric, Forgotten Champion
- Nullix, Void Emperor
- Gorakk, Primordial Beast
- Shadow Player (Mirror Boss)
"""

import pygame
import random
import math
from typing import List, Dict, Optional

from .base_sprite import BaseSprite
from .utils import create_surface, draw_pixel, lerp_color, darken_color, lighten_color
from .palette import PALETTE
from .effects import create_aura, create_particle_effect


class BossSprite(BaseSprite):
    """
    Extended sprite class for bosses.
    Includes aura effects, particle systems, and phase transitions.
    """

    def __init__(self, name: str):
        super().__init__(name, 'boss')
        self.aura_frames: List[pygame.Surface] = []
        self.particle_frames: List[pygame.Surface] = []
        self.phase_variants: Dict[int, pygame.Surface] = {}

    def generate_aura(self, color: tuple, intensity: str = 'medium',
                      style: str = 'pulse') -> List[pygame.Surface]:
        """Generate pulsing aura effect overlay."""
        self.aura_frames = create_aura(color, intensity, style, self.base_size)
        return self.aura_frames

    def generate_particles(self, particle_type: str,
                          color: tuple) -> List[pygame.Surface]:
        """Generate particle effect overlay."""
        self.particle_frames = create_particle_effect(
            particle_type, color, 'medium', self.base_size
        )
        return self.particle_frames

    def get_composite_frame(self, base_frame: pygame.Surface,
                           aura_idx: int = 0,
                           particle_idx: int = 0) -> pygame.Surface:
        """Combine base sprite with effects."""
        result = create_surface(self.base_size)

        # Layer: aura (behind), base sprite, particles (in front)
        if self.aura_frames and aura_idx < len(self.aura_frames):
            result.blit(self.aura_frames[aura_idx], (0, 0))

        result.blit(base_frame, (0, 0))

        if self.particle_frames and particle_idx < len(self.particle_frames):
            result.blit(self.particle_frames[particle_idx], (0, 0))

        return result


class AncientGuardianSprite(BossSprite):
    """Massive stone/metal construct - Final Boss."""

    def __init__(self):
        super().__init__('boss')
        self.generate_aura(PALETTE['gold_base'], 'high', 'holy')
        self.generate_particles('magic', PALETTE['holy_gold'])

    def _generate_base_sprite(self) -> pygame.Surface:
        surface = create_surface(self.base_size)
        cx = 32

        stone = PALETTE['earth_base']
        metal = PALETTE['steel_base']
        gold = PALETTE['gold_base']
        rune = PALETTE['holy_gold']

        # Massive armored body
        pygame.draw.rect(surface, metal, (cx - 16, 18, 32, 34))
        pygame.draw.rect(surface, darken_color(metal, 30), (cx - 16, 18, 32, 34), 2)

        # Ornate armor details
        pygame.draw.rect(surface, gold, (cx - 14, 22, 28, 4))
        pygame.draw.rect(surface, gold, (cx - 14, 44, 28, 4))

        # Glowing runes on chest
        pygame.draw.polygon(surface, rune, [
            (cx, 28), (cx - 8, 38), (cx, 34), (cx + 8, 38)
        ])

        # Helmet with single glowing eye
        pygame.draw.ellipse(surface, metal, (cx - 12, 4, 24, 18))
        pygame.draw.rect(surface, darken_color(metal, 20), (cx - 10, 10, 20, 8))
        # Central gem/eye
        pygame.draw.circle(surface, rune, (cx, 14), 4)
        pygame.draw.circle(surface, (255, 255, 255), (cx, 14), 2)

        # Floating armor pieces (magical)
        pygame.draw.ellipse(surface, metal, (cx - 24, 20, 10, 14))
        pygame.draw.ellipse(surface, metal, (cx + 14, 20, 10, 14))
        # Connection lines (magic)
        pygame.draw.line(surface, (*rune[:3], 150), (cx - 16, 26), (cx - 20, 26), 2)
        pygame.draw.line(surface, (*rune[:3], 150), (cx + 16, 26), (cx + 20, 26), 2)

        # Huge sword
        pygame.draw.rect(surface, metal, (cx + 20, 8, 6, 44))
        pygame.draw.polygon(surface, lighten_color(metal, 30), [
            (cx + 19, 8), (cx + 27, 8), (cx + 23, -2)
        ])
        pygame.draw.rect(surface, gold, (cx + 18, 48, 10, 6))
        # Rune on blade
        pygame.draw.line(surface, rune, (cx + 23, 14), (cx + 23, 40), 2)

        # Shield
        pygame.draw.ellipse(surface, metal, (cx - 28, 24, 14, 20))
        pygame.draw.ellipse(surface, gold, (cx - 26, 28, 10, 12))
        pygame.draw.circle(surface, rune, (cx - 21, 34), 3)

        # Legs (armored)
        pygame.draw.rect(surface, metal, (cx - 12, 50, 10, 12))
        pygame.draw.rect(surface, metal, (cx + 2, 50, 10, 12))

        # Ancient cracks
        pygame.draw.line(surface, darken_color(stone, 30), (cx - 8, 24), (cx - 4, 36), 1)
        pygame.draw.line(surface, darken_color(stone, 30), (cx + 6, 28), (cx + 10, 42), 1)

        return surface


class ZyraxisSprite(BossSprite):
    """Ancient Wyrm - Dragon boss."""

    def __init__(self):
        super().__init__('boss_wyrm')
        self.generate_aura(PALETTE['fire_orange'], 'high', 'flame')
        self.generate_particles('ember', PALETTE['fire_red'])

    def _generate_base_sprite(self) -> pygame.Surface:
        surface = create_surface(self.base_size)
        cx = 32

        scale = PALETTE['scale_red']
        scale_dark = darken_color(scale, 50)
        gold = PALETTE['gold_shadow']

        # Dragon head and neck (body off-screen)
        # Neck
        pygame.draw.ellipse(surface, scale, (cx - 10, 30, 20, 32))
        pygame.draw.ellipse(surface, scale_dark, (cx - 6, 36, 12, 24))

        # Head
        pygame.draw.ellipse(surface, scale, (cx - 14, 8, 28, 26))

        # Snout
        pygame.draw.ellipse(surface, scale, (cx - 8, 4, 16, 14))

        # Multiple horns crown
        for i in range(5):
            hx = cx - 10 + i * 5
            pygame.draw.polygon(surface, scale_dark, [
                (hx, 10), (hx - 2, -4 - i % 2 * 4), (hx + 2, 10)
            ])

        # Golden trim on horns
        pygame.draw.line(surface, gold, (cx - 10, 10), (cx - 12, -4), 1)
        pygame.draw.line(surface, gold, (cx + 10, 10), (cx + 12, -4), 1)

        # Glowing orange eyes
        pygame.draw.ellipse(surface, PALETTE['fire_orange'], (cx - 8, 14, 6, 5))
        pygame.draw.ellipse(surface, PALETTE['fire_orange'], (cx + 2, 14, 6, 5))
        pygame.draw.ellipse(surface, (255, 255, 200), (cx - 6, 15, 3, 3))
        pygame.draw.ellipse(surface, (255, 255, 200), (cx + 4, 15, 3, 3))

        # Nostrils with smoke
        draw_pixel(surface, (40, 40, 40), (cx - 4, 8))
        draw_pixel(surface, (40, 40, 40), (cx + 4, 8))
        # Smoke wisps
        pygame.draw.ellipse(surface, (100, 100, 100, 100), (cx - 6, 2, 4, 6))
        pygame.draw.ellipse(surface, (100, 100, 100, 100), (cx + 2, 2, 4, 6))

        # Fire in throat/mouth
        pygame.draw.ellipse(surface, PALETTE['fire_yellow'], (cx - 6, 22, 12, 8))
        pygame.draw.ellipse(surface, PALETTE['fire_white'], (cx - 3, 24, 6, 4))

        # Scarred ancient scales
        pygame.draw.line(surface, darken_color(scale, 40), (cx - 10, 20), (cx - 4, 28), 2)
        pygame.draw.line(surface, darken_color(scale, 40), (cx + 6, 18), (cx + 10, 26), 2)

        # Scale pattern
        for row in range(3):
            for col in range(4):
                sx = cx - 8 + col * 5
                sy = 36 + row * 8
                pygame.draw.ellipse(surface, scale_dark, (sx, sy, 4, 6))

        return surface


class UmbraxisSprite(BossSprite):
    """Shadow Sovereign - Living shadow boss."""

    def __init__(self):
        super().__init__('boss_shadow')
        self.generate_aura(PALETTE['void_purple'], 'high', 'void')
        self.generate_particles('shadow', PALETTE['void_glow'])

    def _generate_base_sprite(self) -> pygame.Surface:
        surface = create_surface(self.base_size)
        cx, cy = 32, 32

        shadow = PALETTE['void_black']
        glow = PALETTE['void_glow']

        # Flowing shadow form
        for layer in range(3):
            alpha = 200 - layer * 50
            size = 24 - layer * 4
            pygame.draw.ellipse(surface, (*shadow[:3], alpha),
                              (cx - size, cy - size//2, size * 2, size + 10))

        # Crown of dark crystals
        for i in range(5):
            angle = math.pi + (i - 2) * 0.4
            length = 16 + (i % 2) * 6
            end_x = cx + int(math.cos(angle) * length)
            end_y = cy - 20 + int(math.sin(angle) * length)
            pygame.draw.polygon(surface, darken_color(glow, 40), [
                (cx + (i - 2) * 4, cy - 16),
                (end_x - 2, end_y),
                (end_x + 2, end_y)
            ])

        # Glowing purple eyes
        pygame.draw.ellipse(surface, glow, (cx - 8, cy - 10, 6, 5))
        pygame.draw.ellipse(surface, glow, (cx + 2, cy - 10, 6, 5))
        # Inner glow
        pygame.draw.ellipse(surface, (255, 200, 255), (cx - 6, cy - 9, 3, 3))
        pygame.draw.ellipse(surface, (255, 200, 255), (cx + 4, cy - 9, 3, 3))

        # Shadow tendrils
        for i in range(6):
            angle = (i / 6) * 2 * math.pi
            start_x = cx + int(math.cos(angle) * 16)
            start_y = cy + int(math.sin(angle) * 12)
            end_x = cx + int(math.cos(angle) * 28)
            end_y = cy + int(math.sin(angle) * 20)

            # Wavy tendril
            mid_x = (start_x + end_x) // 2 + random.randint(-4, 4)
            mid_y = (start_y + end_y) // 2 + random.randint(-4, 4)

            pygame.draw.line(surface, (*shadow[:3], 180), (start_x, start_y), (mid_x, mid_y), 3)
            pygame.draw.line(surface, (*shadow[:3], 120), (mid_x, mid_y), (end_x, end_y), 2)

        # Reality distortion around edges
        for _ in range(8):
            dx = cx + random.randint(-24, 24)
            dy = cy + random.randint(-18, 18)
            pygame.draw.circle(surface, (*glow[:3], 60), (dx, dy), random.randint(2, 4))

        # Afterimage hints (glimpses of former form)
        pygame.draw.ellipse(surface, (*shadow[:3], 100), (cx - 6, cy + 8, 12, 16))

        return surface


class TrueFinalBossSprite(BossSprite):
    """??? Cosmic entity - True Final Boss."""

    def __init__(self):
        super().__init__('boss_unknown')
        self.generate_aura((200, 100, 255), 'high', 'electric')
        self.generate_particles('void', (150, 200, 255))

    def _generate_base_sprite(self) -> pygame.Surface:
        surface = create_surface(self.base_size)
        cx, cy = 32, 32

        # Constantly shifting cosmic form
        # Void background
        pygame.draw.circle(surface, PALETTE['void_black'], (cx, cy), 24)

        # Galaxy patterns
        for ring in range(3):
            radius = 8 + ring * 6
            color = lerp_color((100, 50, 150), (50, 100, 200), ring / 3)
            pygame.draw.circle(surface, (*color[:3], 150 - ring * 30), (cx, cy), radius, 2)

        # Stars within
        for _ in range(12):
            sx = cx + random.randint(-20, 20)
            sy = cy + random.randint(-20, 20)
            pygame.draw.circle(surface, (255, 255, 255), (sx, sy), 1)

        # Multiple eyes appearing
        eye_positions = [
            (cx - 8, cy - 8), (cx + 6, cy - 6),
            (cx, cy + 4), (cx - 6, cy + 8)
        ]
        for i, (ex, ey) in enumerate(eye_positions):
            if random.random() > 0.3:  # Some eyes blink
                eye_color = random.choice([
                    PALETTE['eye_glow_red'],
                    PALETTE['eye_glow_blue'],
                    PALETTE['eye_glow_green'],
                    PALETTE['void_glow']
                ])
                pygame.draw.ellipse(surface, eye_color, (ex - 3, ey - 2, 6, 4))
                pygame.draw.ellipse(surface, (0, 0, 0), (ex - 1, ey - 1, 2, 2))

        # Tentacles of starlight
        for i in range(8):
            angle = (i / 8) * 2 * math.pi
            length = 20 + random.randint(-4, 8)

            points = [(cx, cy)]
            for j in range(4):
                progress = (j + 1) / 4
                x = cx + int(math.cos(angle + j * 0.2) * length * progress)
                y = cy + int(math.sin(angle + j * 0.2) * length * progress)
                points.append((x, y))

            color = lerp_color((255, 200, 255), (100, 150, 255), random.random())
            if len(points) >= 2:
                pygame.draw.lines(surface, (*color[:3], 200), False, points, 2)

        # Dimensional tears
        for _ in range(3):
            tx = cx + random.randint(-16, 16)
            ty = cy + random.randint(-16, 16)
            pygame.draw.line(surface, (255, 255, 255),
                           (tx - 3, ty), (tx + 3, ty), 1)

        return surface


class SirAldricSprite(BossSprite):
    """Forgotten Champion - Noble ghost knight."""

    def __init__(self):
        super().__init__('boss_champion')
        self.generate_aura(PALETTE['ghost_blue'], 'medium', 'pulse')
        self.generate_particles('sparkle', PALETTE['ghost_glow'])

    def _generate_base_sprite(self) -> pygame.Surface:
        surface = create_surface(self.base_size)
        cx = 32

        ghost = PALETTE['ghost_blue']
        armor = PALETTE['steel_base']
        armor_dark = PALETTE['steel_shadow']

        # Ghostly glow base
        pygame.draw.ellipse(surface, (*ghost[:3], 80), (cx - 18, 10, 36, 48))

        # Ornate ancient armor
        pygame.draw.rect(surface, (*armor[:3], 220), (cx - 12, 22, 24, 26))
        pygame.draw.rect(surface, armor_dark, (cx - 12, 22, 24, 26), 2)

        # Faded heraldry on tabard
        pygame.draw.rect(surface, (*PALETTE['cloth_red'][:3], 150),
                        (cx - 8, 26, 16, 20))
        # Faded symbol
        pygame.draw.circle(surface, (*PALETTE['gold_shadow'][:3], 100), (cx, 34), 5)

        # Helmet with plume
        pygame.draw.ellipse(surface, (*armor[:3], 220), (cx - 10, 6, 20, 18))
        pygame.draw.rect(surface, (20, 20, 30), (cx - 6, 14, 12, 3))  # Visor
        # Ghostly eyes
        pygame.draw.rect(surface, PALETTE['ghost_glow'], (cx - 5, 15, 4, 2))
        pygame.draw.rect(surface, PALETTE['ghost_glow'], (cx + 1, 15, 4, 2))
        # Tattered plume
        pygame.draw.polygon(surface, (*PALETTE['cloth_red_dark'][:3], 180), [
            (cx - 2, 6), (cx + 2, 6), (cx + 4, -6), (cx - 4, -4)
        ])

        # Massive lance
        pygame.draw.rect(surface, armor_dark, (cx + 14, 10, 4, 40))
        pygame.draw.polygon(surface, armor, [
            (cx + 12, 10), (cx + 20, 10), (cx + 16, 0)
        ])

        # Tower shield
        pygame.draw.ellipse(surface, (*armor[:3], 200), (cx - 26, 20, 16, 28))
        pygame.draw.ellipse(surface, armor_dark, (cx - 26, 20, 16, 28), 2)
        # Shield emblem (faded)
        pygame.draw.circle(surface, (*PALETTE['gold_shadow'][:3], 120), (cx - 18, 34), 4)

        # Ghostly lower body (fading)
        for y in range(12):
            alpha = max(0, 180 - y * 12)
            pygame.draw.rect(surface, (*ghost[:3], alpha),
                           (cx - 10 + y//3, 48 + y, 20 - y//2, 2))

        # Falling petals (honor particles)
        for _ in range(4):
            px = cx + random.randint(-20, 20)
            py = random.randint(0, 50)
            pygame.draw.ellipse(surface, (*PALETTE['flower_red'][:3], 100),
                              (px, py, 3, 2))

        return surface


class NullixSprite(BossSprite):
    """Void Emperor - Being of pure void."""

    def __init__(self):
        super().__init__('boss_void')
        self.generate_aura(PALETTE['void_black'], 'high', 'void')
        self.generate_particles('void', PALETTE['void_purple'])

    def _generate_base_sprite(self) -> pygame.Surface:
        surface = create_surface(self.base_size)
        cx, cy = 32, 32

        void = PALETTE['void_black']
        glow = PALETTE['void_glow']

        # Robed figure of pure void
        pygame.draw.polygon(surface, void, [
            (cx - 14, 16), (cx + 14, 16),
            (cx + 20, 58), (cx - 20, 58)
        ])

        # Ancient emperor robes details
        pygame.draw.polygon(surface, darken_color(glow, 60), [
            (cx - 14, 16), (cx + 14, 16),
            (cx + 20, 58), (cx - 20, 58)
        ], 2)

        # Crown of void crystals
        for i in range(5):
            cx_offset = (i - 2) * 6
            pygame.draw.polygon(surface, glow, [
                (cx + cx_offset - 2, 14),
                (cx + cx_offset + 2, 14),
                (cx + cx_offset, 4 - abs(i - 2) * 2)
            ])

        # No face - empty void
        pygame.draw.ellipse(surface, (5, 3, 10), (cx - 8, 18, 16, 14))

        # Void energy leaks from sleeves
        pygame.draw.ellipse(surface, (*glow[:3], 150), (cx - 22, 32, 10, 14))
        pygame.draw.ellipse(surface, (*glow[:3], 150), (cx + 12, 32, 10, 14))

        # Floating void orbs orbit
        for i in range(4):
            angle = (i / 4) * 2 * math.pi
            ox = cx + int(math.cos(angle) * 22)
            oy = cy + int(math.sin(angle) * 16)
            pygame.draw.circle(surface, void, (ox, oy), 4)
            pygame.draw.circle(surface, glow, (ox, oy), 4, 1)

        # Reality tears around body
        for _ in range(4):
            tx = cx + random.randint(-18, 18)
            ty = random.randint(20, 50)
            length = random.randint(4, 10)
            angle = random.uniform(-0.5, 0.5)
            end_x = tx + int(math.cos(angle) * length)
            end_y = ty + int(math.sin(angle) * length)
            pygame.draw.line(surface, glow, (tx, ty), (end_x, end_y), 1)

        # Dark purple lightning
        for _ in range(2):
            start = (cx + random.randint(-10, 10), 20)
            end = (cx + random.randint(-16, 16), 50)
            pygame.draw.line(surface, glow, start, end, 1)

        return surface


class GorakkSprite(BossSprite):
    """Primordial Beast - Elemental beast."""

    def __init__(self):
        super().__init__('boss_primordial')
        self.generate_aura(PALETTE['leaf_base'], 'high', 'pulse')
        self.generate_particles('nature', PALETTE['leaf_light'])

    def _generate_base_sprite(self) -> pygame.Surface:
        surface = create_surface(self.base_size)
        cx = 32

        # Body shifts between elements
        earth = PALETTE['earth_base']
        fire = PALETTE['fire_orange']
        ice = PALETTE['ice_base']
        nature = PALETTE['leaf_base']

        # Massive quadruped body
        pygame.draw.ellipse(surface, earth, (cx - 18, 28, 36, 26))

        # Elemental segments
        pygame.draw.ellipse(surface, fire, (cx - 14, 32, 14, 18))
        pygame.draw.ellipse(surface, ice, (cx, 32, 14, 18))

        # Head with multiple elemental features
        pygame.draw.ellipse(surface, earth, (cx - 10, 12, 20, 18))

        # Four different elemental eyes
        pygame.draw.circle(surface, PALETTE['fire_yellow'], (cx - 6, 18), 3)  # Fire
        pygame.draw.circle(surface, PALETTE['ice_light'], (cx + 4, 18), 3)    # Ice
        pygame.draw.circle(surface, PALETTE['leaf_light'], (cx - 6, 24), 2)   # Nature
        pygame.draw.circle(surface, PALETTE['earth_light'], (cx + 4, 24), 2)  # Earth

        # Leaves growing
        for i in range(3):
            lx = cx - 8 + i * 6
            pygame.draw.ellipse(surface, nature, (lx, 8, 4, 8))

        # Stone/fire spikes
        pygame.draw.polygon(surface, earth, [
            (cx - 16, 30), (cx - 20, 20), (cx - 12, 28)
        ])
        pygame.draw.polygon(surface, fire, [
            (cx + 16, 30), (cx + 20, 20), (cx + 12, 28)
        ])

        # Legs (elemental variety)
        pygame.draw.rect(surface, earth, (cx - 16, 50, 8, 10))
        pygame.draw.rect(surface, fire, (cx - 6, 50, 8, 10))
        pygame.draw.rect(surface, ice, (cx + 4, 50, 8, 10))
        pygame.draw.rect(surface, nature, (cx + 14, 50, 8, 10))

        # Tribal markings
        pygame.draw.line(surface, PALETTE['gold_shadow'], (cx - 8, 34), (cx + 8, 34), 2)
        pygame.draw.line(surface, PALETTE['gold_shadow'], (cx, 36), (cx, 44), 2)

        # Water drips (from ice)
        for _ in range(2):
            wx = cx + random.randint(4, 14)
            wy = random.randint(36, 48)
            pygame.draw.ellipse(surface, PALETTE['ice_light'], (wx, wy, 2, 4))

        return surface


class ShadowPlayerSprite(BossSprite):
    """Shadow Player - Mirror boss that mimics player."""

    def __init__(self):
        super().__init__('mirror_player')
        self.generate_aura(PALETTE['void_black'], 'medium', 'void')
        self.generate_particles('shadow', PALETTE['void_purple'])

    def _generate_base_sprite(self) -> pygame.Surface:
        surface = create_surface(self.base_size)
        cx = 32

        shadow = (20, 15, 25)
        shadow_light = (40, 30, 50)
        glow = PALETTE['eye_glow_red']

        # Dark silhouette of player character
        # Body
        pygame.draw.ellipse(surface, shadow, (cx - 10, 24, 20, 24))

        # Head
        pygame.draw.ellipse(surface, shadow, (cx - 8, 10, 16, 16))

        # Red glowing eyes
        pygame.draw.ellipse(surface, glow, (cx - 5, 16, 4, 3))
        pygame.draw.ellipse(surface, glow, (cx + 1, 16, 4, 3))

        # Shadow tendrils at edges
        for i in range(6):
            angle = (i / 6) * 2 * math.pi
            start_x = cx + int(math.cos(angle) * 12)
            start_y = 32 + int(math.sin(angle) * 10)
            end_x = cx + int(math.cos(angle) * 20)
            end_y = 32 + int(math.sin(angle) * 16)
            pygame.draw.line(surface, (*shadow_light[:3], 150),
                           (start_x, start_y), (end_x, end_y), 2)

        # Inverted/corrupted equipment silhouettes
        # Sword
        pygame.draw.rect(surface, shadow_light, (cx + 12, 20, 4, 24))
        pygame.draw.polygon(surface, shadow_light, [
            (cx + 11, 20), (cx + 17, 20), (cx + 14, 14)
        ])

        # Arms
        pygame.draw.ellipse(surface, shadow, (cx - 18, 26, 8, 16))
        pygame.draw.ellipse(surface, shadow, (cx + 10, 26, 8, 16))

        # Legs
        pygame.draw.ellipse(surface, shadow, (cx - 8, 44, 7, 14))
        pygame.draw.ellipse(surface, shadow, (cx + 1, 44, 7, 14))

        # Clone trail effect
        for i in range(3):
            alpha = 60 - i * 15
            offset = (i + 1) * 3
            pygame.draw.ellipse(surface, (*shadow[:3], alpha),
                              (cx - 10 - offset, 24, 20, 24))

        return surface


# Factory function
def get_boss_sprite(name: str) -> Optional[BossSprite]:
    """Get a boss sprite generator by name."""
    sprites = {
        'boss': AncientGuardianSprite,
        'boss_wyrm': ZyraxisSprite,
        'boss_shadow': UmbraxisSprite,
        'boss_unknown': TrueFinalBossSprite,
        'boss_champion': SirAldricSprite,
        'boss_void': NullixSprite,
        'boss_primordial': GorakkSprite,
        'mirror_player': ShadowPlayerSprite,
    }

    sprite_class = sprites.get(name.lower())
    if sprite_class:
        return sprite_class()
    return None


BOSS_SPRITES = [
    'boss', 'boss_wyrm', 'boss_shadow', 'boss_unknown',
    'boss_champion', 'boss_void', 'boss_primordial', 'mirror_player'
]
