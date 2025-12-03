"""
Enemy Sprite Generators

Contains detailed sprite generators for all enemy types including:
- Basic enemies (slime, goblin, orc, wolf, spider, skeleton, ghost, bat, troll, imp)
- Mid-tier enemies (werewolf, mimic, golem, mushroom, harpy, lizardman, cyclops, witch, vampire, necromancer, bandit, dark_knight)
- Elemental enemies (fire, ice, earth elementals)
- Undead/Demons (demon, wraith, snake)
"""

import pygame
import random
import math
from typing import List, Tuple, Dict, Optional

from .base_sprite import BaseSprite
from .utils import (
    create_surface, draw_pixel, draw_thick_pixel, draw_gradient_circle,
    draw_gradient_rect, draw_ellipse_gradient, lerp_color, darken_color,
    lighten_color, add_outline, add_noise_texture, draw_eyes
)
from .palette import PALETTE


class SlimeSprite(BaseSprite):
    """Translucent gelatinous slime with visible core."""

    def __init__(self, variant: str = 'green'):
        super().__init__(f'slime_{variant}' if variant != 'green' else 'slime', 'enemy')
        self.variant = variant
        self.colors = self._get_variant_colors()

    def _get_variant_colors(self) -> Dict[str, tuple]:
        variants = {
            'green': {
                'body': PALETTE['slime_green'],
                'core': (80, 180, 80),
                'highlight': (180, 255, 180),
            },
            'blue': {
                'body': PALETTE['ice_base'],
                'core': (100, 150, 200),
                'highlight': (220, 240, 255),
            },
            'red': {
                'body': (200, 80, 80),
                'core': (150, 50, 50),
                'highlight': (255, 150, 150),
            },
            'purple': {
                'body': PALETTE['void_glow'],
                'core': (100, 50, 150),
                'highlight': (200, 150, 255),
            },
        }
        return variants.get(self.variant, variants['green'])

    def _generate_base_sprite(self) -> pygame.Surface:
        surface = create_surface(self.base_size)
        cx, cy = 32, 38

        body = self.colors['body']
        core = self.colors['core']
        highlight = self.colors['highlight']

        # Main body - ellipse with gradient
        draw_ellipse_gradient(surface, (cx - 20, cy - 16, 40, 32),
                             lighten_color(body, 20), darken_color(body, 30))

        # Core/nucleus
        pygame.draw.ellipse(surface, core, (cx - 6, cy - 4, 12, 10))
        pygame.draw.ellipse(surface, lighten_color(core, 40), (cx - 3, cy - 2, 6, 5))

        # Highlight spot
        pygame.draw.ellipse(surface, highlight, (cx - 14, cy - 12, 8, 6))

        # Bubbles inside
        for _ in range(4):
            bx = cx + random.randint(-12, 12)
            by = cy + random.randint(-8, 8)
            br = random.randint(2, 4)
            pygame.draw.circle(surface, (*highlight[:3], 100), (bx, by), br)

        # Eyes
        pygame.draw.ellipse(surface, (255, 255, 255), (cx - 8, cy - 8, 6, 5))
        pygame.draw.ellipse(surface, (255, 255, 255), (cx + 2, cy - 8, 6, 5))
        draw_pixel(surface, (0, 0, 0), (cx - 5, cy - 6))
        draw_pixel(surface, (0, 0, 0), (cx + 5, cy - 6))

        # Drip effects at bottom
        for i in range(3):
            dx = cx - 10 + i * 10
            pygame.draw.ellipse(surface, darken_color(body, 20),
                              (dx - 3, cy + 10, 6, 8))

        return surface

    def _generate_idle_frames(self) -> List[pygame.Surface]:
        frames = []
        for i in range(4):
            surface = create_surface(self.base_size)
            cx, cy = 32, 38

            # Squish/bounce animation
            squish = [1.0, 0.9, 1.0, 1.1][i]
            width = int(40 * squish)
            height = int(32 / squish)
            offset_y = int((32 - height) / 2)

            body = self.colors['body']
            core = self.colors['core']
            highlight = self.colors['highlight']

            # Main body
            draw_ellipse_gradient(surface,
                                 (cx - width//2, cy - height//2 + offset_y, width, height),
                                 lighten_color(body, 20), darken_color(body, 30))

            # Core with pulse
            core_size = 10 + [0, 1, 0, -1][i]
            pygame.draw.ellipse(surface, core,
                              (cx - core_size//2, cy - core_size//3, core_size, int(core_size*0.8)))

            # Highlight
            pygame.draw.ellipse(surface, highlight, (cx - 14, cy - 12 + offset_y, 8, 6))

            # Eyes
            ey = cy - 8 + offset_y
            pygame.draw.ellipse(surface, (255, 255, 255), (cx - 8, ey, 6, 5))
            pygame.draw.ellipse(surface, (255, 255, 255), (cx + 2, ey, 6, 5))
            draw_pixel(surface, (0, 0, 0), (cx - 5, ey + 2))
            draw_pixel(surface, (0, 0, 0), (cx + 5, ey + 2))

            frames.append(surface)
        return frames


class GoblinSprite(BaseSprite):
    """Small hunched humanoid with large pointed ears."""

    def __init__(self, variant: str = 'normal'):
        name = 'goblin' if variant == 'normal' else f'goblin_{variant}'
        super().__init__(name, 'enemy')
        self.variant = variant

    def _generate_base_sprite(self) -> pygame.Surface:
        surface = create_surface(self.base_size)
        cx = 32

        skin = PALETTE['skin_orc']
        skin_dark = darken_color(skin, 30)
        cloth = PALETTE['leather_base']
        cloth_dark = PALETTE['leather_dark']

        # Body - hunched
        pygame.draw.ellipse(surface, cloth, (cx - 10, 30, 20, 18))
        pygame.draw.rect(surface, cloth_dark, (cx - 8, 40, 16, 10))

        # Head - large
        pygame.draw.ellipse(surface, skin, (cx - 10, 12, 20, 18))

        # Large pointed ears
        pygame.draw.polygon(surface, skin, [
            (cx - 10, 18), (cx - 20, 8), (cx - 8, 22)
        ])
        pygame.draw.polygon(surface, skin, [
            (cx + 10, 18), (cx + 20, 8), (cx + 8, 22)
        ])
        pygame.draw.polygon(surface, skin_dark, [
            (cx - 10, 18), (cx - 20, 8), (cx - 8, 22)
        ], 1)
        pygame.draw.polygon(surface, skin_dark, [
            (cx + 10, 18), (cx + 20, 8), (cx + 8, 22)
        ], 1)

        # Eyes - large yellow
        pygame.draw.ellipse(surface, PALETTE['eye_yellow'], (cx - 8, 18, 6, 5))
        pygame.draw.ellipse(surface, PALETTE['eye_yellow'], (cx + 2, 18, 6, 5))
        draw_pixel(surface, (0, 0, 0), (cx - 5, 20))
        draw_pixel(surface, (0, 0, 0), (cx + 5, 20))

        # Sharp teeth grin
        pygame.draw.rect(surface, (40, 40, 40), (cx - 5, 26, 10, 3))
        for i in range(4):
            draw_pixel(surface, (240, 240, 230), (cx - 4 + i * 2, 26))

        # Wild hair
        for i in range(5):
            hx = cx - 8 + i * 4
            pygame.draw.line(surface, PALETTE['hair_black'], (hx, 12), (hx + random.randint(-2, 2), 6), 1)

        # Arms
        pygame.draw.ellipse(surface, skin, (cx - 18, 32, 8, 14))
        pygame.draw.ellipse(surface, skin, (cx + 10, 32, 8, 14))

        # Legs
        pygame.draw.ellipse(surface, skin_dark, (cx - 8, 48, 7, 12))
        pygame.draw.ellipse(surface, skin_dark, (cx + 1, 48, 7, 12))

        # Weapon - crude dagger
        pygame.draw.rect(surface, PALETTE['steel_shadow'], (cx + 16, 36, 3, 12))
        pygame.draw.polygon(surface, PALETTE['steel_base'], [
            (cx + 15, 36), (cx + 20, 36), (cx + 17, 30)
        ])

        return surface


class OrcSprite(BaseSprite):
    """Large muscular humanoid with tusks."""

    def __init__(self):
        super().__init__('orc', 'enemy')

    def _generate_base_sprite(self) -> pygame.Surface:
        surface = create_surface(self.base_size)
        cx = 32

        skin = PALETTE['skin_orc']
        skin_dark = PALETTE['skin_orc_dark']
        armor = PALETTE['leather_dark']

        # Large muscular body
        pygame.draw.ellipse(surface, armor, (cx - 14, 24, 28, 24))

        # Shoulder pads
        pygame.draw.ellipse(surface, PALETTE['iron_base'], (cx - 20, 22, 12, 10))
        pygame.draw.ellipse(surface, PALETTE['iron_base'], (cx + 8, 22, 12, 10))

        # Head
        pygame.draw.ellipse(surface, skin, (cx - 10, 8, 20, 18))

        # Heavy brow
        pygame.draw.rect(surface, skin_dark, (cx - 9, 12, 18, 4))

        # Small angry eyes
        pygame.draw.ellipse(surface, PALETTE['eye_red'], (cx - 6, 14, 4, 3))
        pygame.draw.ellipse(surface, PALETTE['eye_red'], (cx + 2, 14, 4, 3))

        # Lower tusks
        pygame.draw.polygon(surface, PALETTE['bone_white'], [
            (cx - 8, 22), (cx - 6, 22), (cx - 7, 14)
        ])
        pygame.draw.polygon(surface, PALETTE['bone_white'], [
            (cx + 6, 22), (cx + 8, 22), (cx + 7, 14)
        ])

        # War paint
        pygame.draw.line(surface, PALETTE['blood_red'], (cx - 8, 18), (cx - 2, 20), 2)
        pygame.draw.line(surface, PALETTE['blood_red'], (cx + 2, 20), (cx + 8, 18), 2)

        # Arms
        pygame.draw.ellipse(surface, skin, (cx - 24, 26, 12, 20))
        pygame.draw.ellipse(surface, skin, (cx + 12, 26, 12, 20))

        # Legs
        pygame.draw.rect(surface, skin_dark, (cx - 10, 46, 8, 14))
        pygame.draw.rect(surface, skin_dark, (cx + 2, 46, 8, 14))

        # Large axe
        pygame.draw.rect(surface, PALETTE['leather_base'], (cx + 20, 20, 4, 30))
        pygame.draw.polygon(surface, PALETTE['steel_base'], [
            (cx + 14, 24), (cx + 14, 38), (cx + 22, 38), (cx + 22, 24), (cx + 24, 31)
        ])

        return surface


class WolfSprite(BaseSprite):
    """Quadruped canine with thick fur."""

    def __init__(self):
        super().__init__('wolf', 'enemy')

    def _generate_base_sprite(self) -> pygame.Surface:
        surface = create_surface(self.base_size)

        fur = PALETTE['fur_grey']
        fur_light = lighten_color(fur, 30)
        fur_dark = darken_color(fur, 30)

        # Body
        pygame.draw.ellipse(surface, fur, (16, 30, 32, 20))
        pygame.draw.ellipse(surface, fur_light, (18, 34, 28, 12))

        # Head
        pygame.draw.ellipse(surface, fur, (8, 24, 20, 16))

        # Snout
        pygame.draw.ellipse(surface, fur_light, (4, 30, 14, 10))
        draw_pixel(surface, (0, 0, 0), (6, 34))  # Nose

        # Ears
        pygame.draw.polygon(surface, fur, [(14, 24), (10, 14), (18, 22)])
        pygame.draw.polygon(surface, fur, [(22, 24), (26, 14), (18, 22)])
        pygame.draw.polygon(surface, fur_dark, [(14, 24), (10, 14), (18, 22)], 1)

        # Eyes - piercing yellow
        pygame.draw.ellipse(surface, PALETTE['eye_yellow'], (12, 28, 4, 3))
        pygame.draw.ellipse(surface, PALETTE['eye_yellow'], (18, 28, 4, 3))
        draw_pixel(surface, (0, 0, 0), (14, 29))
        draw_pixel(surface, (0, 0, 0), (20, 29))

        # Fangs
        draw_pixel(surface, (255, 255, 255), (8, 38))
        draw_pixel(surface, (255, 255, 255), (14, 38))

        # Legs
        pygame.draw.rect(surface, fur_dark, (18, 46, 6, 12))
        pygame.draw.rect(surface, fur_dark, (24, 46, 6, 12))
        pygame.draw.rect(surface, fur_dark, (36, 46, 6, 12))
        pygame.draw.rect(surface, fur_dark, (42, 46, 6, 12))

        # Tail
        pygame.draw.ellipse(surface, fur, (44, 28, 14, 10))

        return surface


class SpiderSprite(BaseSprite):
    """Eight-legged arachnid with pattern markings."""

    def __init__(self):
        super().__init__('spider', 'enemy')

    def _generate_base_sprite(self) -> pygame.Surface:
        surface = create_surface(self.base_size)
        cx, cy = 32, 36

        body_color = PALETTE['chitin_black']
        body_mark = PALETTE['blood_red']

        # Abdomen
        pygame.draw.ellipse(surface, body_color, (cx - 12, cy - 4, 24, 20))
        # Pattern on abdomen
        pygame.draw.ellipse(surface, body_mark, (cx - 6, cy, 12, 10))
        pygame.draw.circle(surface, body_mark, (cx, cy - 2), 3)

        # Cephalothorax
        pygame.draw.ellipse(surface, body_color, (cx - 8, cy - 14, 16, 14))

        # Eyes (8 - 2 large, 6 small)
        pygame.draw.circle(surface, PALETTE['eye_glow_red'], (cx - 4, cy - 10), 3)
        pygame.draw.circle(surface, PALETTE['eye_glow_red'], (cx + 4, cy - 10), 3)
        for i in range(3):
            pygame.draw.circle(surface, PALETTE['eye_red'], (cx - 6 + i * 2, cy - 14), 1)
            pygame.draw.circle(surface, PALETTE['eye_red'], (cx + 2 + i * 2, cy - 14), 1)

        # Fangs
        pygame.draw.line(surface, body_color, (cx - 3, cy - 4), (cx - 5, cy + 2), 2)
        pygame.draw.line(surface, body_color, (cx + 3, cy - 4), (cx + 5, cy + 2), 2)

        # Legs (4 on each side, segmented)
        leg_positions = [(-12, -8), (-14, -2), (-14, 4), (-12, 10)]
        for i, (lx, ly) in enumerate(leg_positions):
            # Left legs
            pygame.draw.line(surface, body_color, (cx + lx, cy + ly), (cx + lx - 12, cy + ly - 6), 2)
            pygame.draw.line(surface, body_color, (cx + lx - 12, cy + ly - 6), (cx + lx - 16, cy + ly + 8), 2)
            # Right legs
            pygame.draw.line(surface, body_color, (cx - lx, cy + ly), (cx - lx + 12, cy + ly - 6), 2)
            pygame.draw.line(surface, body_color, (cx - lx + 12, cy + ly - 6), (cx - lx + 16, cy + ly + 8), 2)

        return surface


class SkeletonSprite(BaseSprite):
    """Undead skeleton with glowing eyes."""

    def __init__(self):
        super().__init__('skeleton', 'enemy')

    def _generate_base_sprite(self) -> pygame.Surface:
        surface = create_surface(self.base_size)
        cx = 32

        bone = PALETTE['bone_white']
        bone_dark = PALETTE['bone_shadow']

        # Skull
        pygame.draw.ellipse(surface, bone, (cx - 8, 10, 16, 16))
        # Eye sockets
        pygame.draw.ellipse(surface, (20, 20, 30), (cx - 6, 14, 5, 6))
        pygame.draw.ellipse(surface, (20, 20, 30), (cx + 1, 14, 5, 6))
        # Glowing eyes
        draw_pixel(surface, PALETTE['eye_glow_red'], (cx - 4, 16))
        draw_pixel(surface, PALETTE['eye_glow_red'], (cx + 4, 16))
        # Jaw
        pygame.draw.rect(surface, bone_dark, (cx - 5, 22, 10, 4))
        # Teeth
        for i in range(5):
            draw_pixel(surface, bone, (cx - 4 + i * 2, 22))

        # Spine/ribcage
        pygame.draw.rect(surface, bone, (cx - 2, 26, 4, 16))
        for i in range(4):
            ry = 28 + i * 4
            pygame.draw.line(surface, bone_dark, (cx - 10, ry), (cx - 2, ry + 2), 2)
            pygame.draw.line(surface, bone_dark, (cx + 2, ry + 2), (cx + 10, ry), 2)

        # Arms
        pygame.draw.line(surface, bone, (cx - 10, 28), (cx - 16, 40), 2)
        pygame.draw.line(surface, bone, (cx - 16, 40), (cx - 14, 48), 2)
        pygame.draw.line(surface, bone, (cx + 10, 28), (cx + 16, 40), 2)
        pygame.draw.line(surface, bone, (cx + 16, 40), (cx + 14, 48), 2)

        # Legs
        pygame.draw.line(surface, bone, (cx - 2, 42), (cx - 6, 58), 3)
        pygame.draw.line(surface, bone, (cx + 2, 42), (cx + 6, 58), 3)

        # Tattered armor remnants
        pygame.draw.polygon(surface, PALETTE['leather_dark'], [
            (cx - 8, 30), (cx + 8, 30), (cx + 6, 42), (cx - 6, 42)
        ])

        # Sword
        pygame.draw.rect(surface, PALETTE['steel_base'], (cx + 18, 30, 3, 20))
        pygame.draw.polygon(surface, PALETTE['steel_highlight'], [
            (cx + 17, 30), (cx + 22, 30), (cx + 19, 24)
        ])

        return surface


class GhostSprite(BaseSprite):
    """Translucent ethereal specter."""

    def __init__(self):
        super().__init__('ghost', 'enemy')

    def _generate_base_sprite(self) -> pygame.Surface:
        surface = create_surface(self.base_size)
        cx, cy = 32, 28

        ghost = PALETTE['ghost_blue']
        glow = PALETTE['ghost_glow']

        # Wispy body fading to transparency
        for y in range(30):
            alpha = max(0, 180 - y * 5)
            color = (*ghost[:3], alpha)
            width = 24 - y // 3
            pygame.draw.ellipse(surface, color, (cx - width//2, cy + y - 10, width, 4))

        # Upper body
        pygame.draw.ellipse(surface, (*ghost[:3], 200), (cx - 14, cy - 14, 28, 28))
        pygame.draw.ellipse(surface, (*glow[:3], 100), (cx - 10, cy - 10, 20, 20))

        # Hollow eyes with blue glow
        pygame.draw.ellipse(surface, (20, 20, 40), (cx - 8, cy - 6, 6, 8))
        pygame.draw.ellipse(surface, (20, 20, 40), (cx + 2, cy - 6, 6, 8))
        pygame.draw.circle(surface, PALETTE['eye_glow_blue'], (cx - 5, cy - 2), 2)
        pygame.draw.circle(surface, PALETTE['eye_glow_blue'], (cx + 5, cy - 2), 2)

        # Sad/angry expression - mouth
        pygame.draw.arc(surface, (40, 40, 60), (cx - 4, cy + 4, 8, 6), 0, math.pi, 2)

        # Wispy arms reaching
        pygame.draw.line(surface, (*ghost[:3], 150), (cx - 14, cy), (cx - 24, cy - 8), 3)
        pygame.draw.line(surface, (*ghost[:3], 150), (cx + 14, cy), (cx + 24, cy - 8), 3)

        # Particle effects (small dots around edges)
        for _ in range(8):
            px = cx + random.randint(-20, 20)
            py = cy + random.randint(-16, 20)
            pygame.draw.circle(surface, (*glow[:3], random.randint(50, 150)), (px, py), 1)

        return surface


class BatSprite(BaseSprite):
    """Flying bat with spread wings."""

    def __init__(self):
        super().__init__('bat', 'enemy')

    def _generate_base_sprite(self) -> pygame.Surface:
        surface = create_surface(self.base_size)
        cx, cy = 32, 32

        fur = PALETTE['fur_black']
        wing = (50, 40, 45)

        # Body
        pygame.draw.ellipse(surface, fur, (cx - 6, cy - 4, 12, 16))

        # Head
        pygame.draw.ellipse(surface, fur, (cx - 5, cy - 10, 10, 10))

        # Large ears
        pygame.draw.polygon(surface, fur, [(cx - 4, cy - 10), (cx - 8, cy - 20), (cx - 1, cy - 8)])
        pygame.draw.polygon(surface, fur, [(cx + 4, cy - 10), (cx + 8, cy - 20), (cx + 1, cy - 8)])

        # Red eyes
        pygame.draw.circle(surface, PALETTE['eye_red'], (cx - 3, cy - 6), 2)
        pygame.draw.circle(surface, PALETTE['eye_red'], (cx + 3, cy - 6), 2)

        # Fangs
        draw_pixel(surface, (255, 255, 255), (cx - 1, cy - 2))
        draw_pixel(surface, (255, 255, 255), (cx + 1, cy - 2))

        # Wings - membrane with bone structure
        # Left wing
        pygame.draw.polygon(surface, wing, [
            (cx - 6, cy), (cx - 26, cy - 16), (cx - 22, cy + 4), (cx - 6, cy + 8)
        ])
        pygame.draw.line(surface, fur, (cx - 6, cy), (cx - 24, cy - 14), 1)
        pygame.draw.line(surface, fur, (cx - 6, cy), (cx - 22, cy - 4), 1)
        pygame.draw.line(surface, fur, (cx - 6, cy), (cx - 18, cy + 4), 1)

        # Right wing
        pygame.draw.polygon(surface, wing, [
            (cx + 6, cy), (cx + 26, cy - 16), (cx + 22, cy + 4), (cx + 6, cy + 8)
        ])
        pygame.draw.line(surface, fur, (cx + 6, cy), (cx + 24, cy - 14), 1)
        pygame.draw.line(surface, fur, (cx + 6, cy), (cx + 22, cy - 4), 1)
        pygame.draw.line(surface, fur, (cx + 6, cy), (cx + 18, cy + 4), 1)

        return surface


class TrollSprite(BaseSprite):
    """Massive hunched humanoid with mossy skin."""

    def __init__(self):
        super().__init__('troll', 'enemy')

    def _generate_base_sprite(self) -> pygame.Surface:
        surface = create_surface(self.base_size)
        cx = 32

        skin = (100, 110, 90)
        skin_dark = darken_color(skin, 30)
        moss = PALETTE['moss']

        # Large hunched body
        pygame.draw.ellipse(surface, skin, (cx - 18, 20, 36, 32))

        # Small head
        pygame.draw.ellipse(surface, skin, (cx - 8, 10, 16, 14))

        # Large nose
        pygame.draw.ellipse(surface, skin_dark, (cx - 4, 14, 8, 10))

        # Small eyes
        pygame.draw.circle(surface, PALETTE['eye_yellow'], (cx - 5, 14), 2)
        pygame.draw.circle(surface, PALETTE['eye_yellow'], (cx + 5, 14), 2)

        # Underbite with teeth
        pygame.draw.rect(surface, skin_dark, (cx - 6, 20, 12, 6))
        draw_pixel(surface, PALETTE['bone_white'], (cx - 4, 18))
        draw_pixel(surface, PALETTE['bone_white'], (cx, 18))
        draw_pixel(surface, PALETTE['bone_white'], (cx + 4, 18))

        # Long arms
        pygame.draw.ellipse(surface, skin, (cx - 28, 24, 14, 28))
        pygame.draw.ellipse(surface, skin, (cx + 14, 24, 14, 28))

        # Mossy growth
        for _ in range(6):
            mx = cx + random.randint(-16, 16)
            my = random.randint(22, 40)
            pygame.draw.ellipse(surface, moss, (mx - 3, my, 6, 4))

        # Legs
        pygame.draw.rect(surface, skin_dark, (cx - 12, 48, 10, 12))
        pygame.draw.rect(surface, skin_dark, (cx + 2, 48, 10, 12))

        # Loincloth
        pygame.draw.polygon(surface, PALETTE['leather_dark'], [
            (cx - 14, 46), (cx + 14, 46), (cx + 10, 58), (cx - 10, 58)
        ])

        return surface


class ImpSprite(BaseSprite):
    """Small demonic creature with wings."""

    def __init__(self):
        super().__init__('imp', 'enemy')

    def _generate_base_sprite(self) -> pygame.Surface:
        surface = create_surface(self.base_size)
        cx, cy = 32, 36

        skin = PALETTE['skin_demon']
        skin_dark = darken_color(skin, 30)

        # Small body
        pygame.draw.ellipse(surface, skin, (cx - 8, cy - 4, 16, 18))

        # Head
        pygame.draw.ellipse(surface, skin, (cx - 7, cy - 18, 14, 14))

        # Small horns
        pygame.draw.polygon(surface, skin_dark, [(cx - 5, cy - 18), (cx - 8, cy - 26), (cx - 2, cy - 16)])
        pygame.draw.polygon(surface, skin_dark, [(cx + 5, cy - 18), (cx + 8, cy - 26), (cx + 2, cy - 16)])

        # Glowing yellow eyes
        pygame.draw.ellipse(surface, PALETTE['eye_yellow'], (cx - 5, cy - 14, 4, 4))
        pygame.draw.ellipse(surface, PALETTE['eye_yellow'], (cx + 1, cy - 14, 4, 4))

        # Mischievous grin
        pygame.draw.arc(surface, (0, 0, 0), (cx - 4, cy - 10, 8, 6), math.pi, 2 * math.pi, 1)
        draw_pixel(surface, (255, 255, 255), (cx - 2, cy - 8))
        draw_pixel(surface, (255, 255, 255), (cx + 2, cy - 8))

        # Small bat wings
        pygame.draw.polygon(surface, skin_dark, [
            (cx - 8, cy - 8), (cx - 20, cy - 18), (cx - 16, cy), (cx - 8, cy + 4)
        ])
        pygame.draw.polygon(surface, skin_dark, [
            (cx + 8, cy - 8), (cx + 20, cy - 18), (cx + 16, cy), (cx + 8, cy + 4)
        ])

        # Pointed tail
        pygame.draw.line(surface, skin, (cx, cy + 10), (cx + 12, cy + 18), 2)
        pygame.draw.polygon(surface, skin_dark, [
            (cx + 10, cy + 16), (cx + 16, cy + 20), (cx + 14, cy + 14)
        ])

        # Clawed hands
        pygame.draw.ellipse(surface, skin, (cx - 14, cy - 2, 6, 8))
        pygame.draw.ellipse(surface, skin, (cx + 8, cy - 2, 6, 8))

        # Legs
        pygame.draw.ellipse(surface, skin_dark, (cx - 6, cy + 10, 5, 8))
        pygame.draw.ellipse(surface, skin_dark, (cx + 1, cy + 10, 5, 8))

        return surface


# Factory function to get enemy sprite by name
def get_enemy_sprite(name: str) -> Optional[BaseSprite]:
    """Get an enemy sprite generator by name."""
    sprites = {
        'slime': SlimeSprite,
        'goblin': GoblinSprite,
        'orc': OrcSprite,
        'wolf': WolfSprite,
        'spider': SpiderSprite,
        'skeleton': SkeletonSprite,
        'ghost': GhostSprite,
        'bat': BatSprite,
        'troll': TrollSprite,
        'imp': ImpSprite,
    }

    sprite_class = sprites.get(name.lower())
    if sprite_class:
        return sprite_class()
    return None


# List of all basic enemy names
BASIC_ENEMIES = ['slime', 'goblin', 'orc', 'wolf', 'spider', 'skeleton', 'ghost', 'bat', 'troll', 'imp']
