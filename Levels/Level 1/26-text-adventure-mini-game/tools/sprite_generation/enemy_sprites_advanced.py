"""
Advanced Enemy Sprite Generators

Contains mid-tier and elemental enemy sprites:
- Mid-tier: werewolf, mimic, golem, mushroom, harpy, lizardman, cyclops, witch, vampire, necromancer, bandit, dark_knight
- Elemental: fire_elemental, ice_elemental, earth_elemental
- Undead/Demon: demon, wraith, snake
"""

import pygame
import random
import math
from typing import List, Optional

from .base_sprite import BaseSprite
from .utils import (
    create_surface, draw_pixel, draw_gradient_circle,
    lerp_color, darken_color, lighten_color
)
from .palette import PALETTE


class WerewolfSprite(BaseSprite):
    """Bipedal wolf/human hybrid."""

    def __init__(self):
        super().__init__('werewolf', 'enemy')

    def _generate_base_sprite(self) -> pygame.Surface:
        surface = create_surface(self.base_size)
        cx = 32

        fur = PALETTE['fur_brown']
        fur_dark = darken_color(fur, 40)
        fur_light = lighten_color(fur, 20)

        # Hunched muscular body
        pygame.draw.ellipse(surface, fur, (cx - 14, 22, 28, 26))
        pygame.draw.ellipse(surface, fur_light, (cx - 10, 28, 20, 16))

        # Wolf head
        pygame.draw.ellipse(surface, fur, (cx - 10, 8, 20, 18))
        # Snout
        pygame.draw.ellipse(surface, fur_light, (cx - 6, 16, 12, 10))
        draw_pixel(surface, (0, 0, 0), (cx, 20))  # Nose

        # Glowing red eyes
        pygame.draw.ellipse(surface, PALETTE['eye_glow_red'], (cx - 7, 12, 5, 4))
        pygame.draw.ellipse(surface, PALETTE['eye_glow_red'], (cx + 2, 12, 5, 4))

        # Fangs with drool
        draw_pixel(surface, (255, 255, 255), (cx - 4, 24))
        draw_pixel(surface, (255, 255, 255), (cx + 4, 24))
        pygame.draw.line(surface, (200, 200, 220, 150), (cx - 4, 24), (cx - 5, 28), 1)

        # Ears
        pygame.draw.polygon(surface, fur, [(cx - 8, 10), (cx - 12, 2), (cx - 4, 8)])
        pygame.draw.polygon(surface, fur, [(cx + 8, 10), (cx + 12, 2), (cx + 4, 8)])

        # Elongated clawed arms
        pygame.draw.ellipse(surface, fur, (cx - 22, 24, 10, 22))
        pygame.draw.ellipse(surface, fur, (cx + 12, 24, 10, 22))
        # Claws
        for i in range(3):
            pygame.draw.line(surface, (40, 40, 40), (cx - 20 + i*3, 44), (cx - 22 + i*3, 50), 2)
            pygame.draw.line(surface, (40, 40, 40), (cx + 14 + i*3, 44), (cx + 12 + i*3, 50), 2)

        # Legs
        pygame.draw.rect(surface, fur_dark, (cx - 10, 46, 8, 14))
        pygame.draw.rect(surface, fur_dark, (cx + 2, 46, 8, 14))

        # Torn pants
        pygame.draw.polygon(surface, PALETTE['cloth_brown'], [
            (cx - 12, 44), (cx + 12, 44), (cx + 8, 54), (cx - 8, 54)
        ])

        return surface


class MimicSprite(BaseSprite):
    """Treasure chest with monstrous features."""

    def __init__(self):
        super().__init__('mimic', 'enemy')

    def _generate_base_sprite(self) -> pygame.Surface:
        surface = create_surface(self.base_size)
        cx, cy = 32, 38

        wood = PALETTE['leather_base']
        wood_dark = PALETTE['leather_dark']
        gold = PALETTE['gold_base']

        # Chest body (open)
        pygame.draw.rect(surface, wood, (cx - 16, cy - 4, 32, 20))
        pygame.draw.rect(surface, wood_dark, (cx - 16, cy - 4, 32, 20), 2)

        # Lid (open, tilted back)
        pygame.draw.polygon(surface, wood, [
            (cx - 16, cy - 4), (cx + 16, cy - 4),
            (cx + 14, cy - 18), (cx - 14, cy - 18)
        ])
        pygame.draw.polygon(surface, wood_dark, [
            (cx - 16, cy - 4), (cx + 16, cy - 4),
            (cx + 14, cy - 18), (cx - 14, cy - 18)
        ], 2)

        # Gold trim (lure)
        pygame.draw.rect(surface, gold, (cx - 14, cy - 2, 28, 3))
        pygame.draw.rect(surface, gold, (cx - 12, cy - 16, 24, 3))

        # Rows of teeth inside
        for i in range(8):
            tx = cx - 12 + i * 3
            # Top teeth
            pygame.draw.polygon(surface, (255, 255, 240), [
                (tx, cy - 4), (tx + 2, cy - 4), (tx + 1, cy - 10)
            ])
            # Bottom teeth
            pygame.draw.polygon(surface, (255, 255, 240), [
                (tx, cy + 2), (tx + 2, cy + 2), (tx + 1, cy + 8)
            ])

        # Single large eye inside
        pygame.draw.circle(surface, PALETTE['eye_yellow'], (cx, cy - 2), 6)
        pygame.draw.circle(surface, (0, 0, 0), (cx, cy - 2), 3)
        pygame.draw.circle(surface, (255, 255, 255), (cx - 2, cy - 4), 1)

        # Long sticky tongue
        pygame.draw.line(surface, (200, 80, 100), (cx, cy + 6), (cx - 10, cy + 20), 3)
        pygame.draw.ellipse(surface, (220, 100, 120), (cx - 14, cy + 18, 8, 6))

        # Small legs underneath
        pygame.draw.ellipse(surface, wood_dark, (cx - 14, cy + 12, 8, 6))
        pygame.draw.ellipse(surface, wood_dark, (cx + 6, cy + 12, 8, 6))

        return surface


class GolemSprite(BaseSprite):
    """Stone construct with glowing runes."""

    def __init__(self):
        super().__init__('golem', 'enemy')

    def _generate_base_sprite(self) -> pygame.Surface:
        surface = create_surface(self.base_size)
        cx = 32

        stone = PALETTE['earth_base']
        stone_dark = darken_color(stone, 40)
        rune_glow = PALETTE['fire_orange']

        # Blocky body
        pygame.draw.rect(surface, stone, (cx - 14, 22, 28, 28))
        pygame.draw.rect(surface, stone_dark, (cx - 14, 22, 28, 28), 2)

        # Head (rectangular)
        pygame.draw.rect(surface, stone, (cx - 10, 8, 20, 16))
        pygame.draw.rect(surface, stone_dark, (cx - 10, 8, 20, 16), 2)

        # Glowing eyes
        pygame.draw.rect(surface, rune_glow, (cx - 7, 14, 5, 4))
        pygame.draw.rect(surface, rune_glow, (cx + 2, 14, 5, 4))

        # Rune on forehead
        pygame.draw.circle(surface, rune_glow, (cx, 12), 3)
        pygame.draw.circle(surface, stone, (cx, 12), 2)

        # Rune on chest
        pygame.draw.polygon(surface, rune_glow, [
            (cx, 28), (cx - 6, 38), (cx, 34), (cx + 6, 38)
        ])

        # Cracks with inner glow
        pygame.draw.line(surface, rune_glow, (cx + 8, 26), (cx + 12, 36), 1)
        pygame.draw.line(surface, rune_glow, (cx - 10, 32), (cx - 6, 44), 1)

        # Heavy stone fists
        pygame.draw.rect(surface, stone, (cx - 22, 28, 10, 16))
        pygame.draw.rect(surface, stone, (cx + 12, 28, 10, 16))
        pygame.draw.rect(surface, stone_dark, (cx - 22, 28, 10, 16), 1)
        pygame.draw.rect(surface, stone_dark, (cx + 12, 28, 10, 16), 1)

        # Legs
        pygame.draw.rect(surface, stone, (cx - 12, 48, 10, 12))
        pygame.draw.rect(surface, stone, (cx + 2, 48, 10, 12))

        # Moss/lichen
        for _ in range(4):
            mx = cx + random.randint(-12, 12)
            my = random.randint(24, 46)
            pygame.draw.circle(surface, PALETTE['moss'], (mx, my), random.randint(2, 4))

        return surface


class MushroomSprite(BaseSprite):
    """Large toadstool creature with face."""

    def __init__(self):
        super().__init__('mushroom', 'enemy')

    def _generate_base_sprite(self) -> pygame.Surface:
        surface = create_surface(self.base_size)
        cx, cy = 32, 40

        cap = PALETTE['mushroom_cap']
        stem = PALETTE['mushroom_stem']
        spots = (255, 255, 240)

        # Stem/body
        pygame.draw.ellipse(surface, stem, (cx - 10, cy - 8, 20, 24))
        pygame.draw.ellipse(surface, darken_color(stem, 20), (cx - 8, cy + 8, 16, 8))

        # Cap
        pygame.draw.ellipse(surface, cap, (cx - 18, cy - 28, 36, 24))
        pygame.draw.ellipse(surface, darken_color(cap, 30), (cx - 16, cy - 18, 32, 8))

        # Spots on cap
        pygame.draw.circle(surface, spots, (cx - 8, cy - 22), 4)
        pygame.draw.circle(surface, spots, (cx + 6, cy - 24), 3)
        pygame.draw.circle(surface, spots, (cx + 10, cy - 18), 2)
        pygame.draw.circle(surface, spots, (cx - 12, cy - 16), 2)

        # Sleepy face on stem
        pygame.draw.ellipse(surface, (0, 0, 0), (cx - 6, cy - 4, 4, 3))
        pygame.draw.ellipse(surface, (0, 0, 0), (cx + 2, cy - 4, 4, 3))
        pygame.draw.arc(surface, (0, 0, 0), (cx - 3, cy + 2, 6, 4), 0, math.pi, 1)

        # Root feet
        pygame.draw.ellipse(surface, darken_color(stem, 30), (cx - 12, cy + 12, 8, 6))
        pygame.draw.ellipse(surface, darken_color(stem, 30), (cx + 4, cy + 12, 8, 6))

        # Spore particles
        for _ in range(6):
            sx = cx + random.randint(-20, 20)
            sy = cy + random.randint(-30, -10)
            pygame.draw.circle(surface, (*cap[:3], 100), (sx, sy), 1)

        return surface


class FireElementalSprite(BaseSprite):
    """Humanoid made of flames."""

    def __init__(self):
        super().__init__('fire_elemental', 'enemy')

    def _generate_base_sprite(self) -> pygame.Surface:
        surface = create_surface(self.base_size)
        cx, cy = 32, 36

        core = PALETTE['fire_white']
        mid = PALETTE['fire_yellow']
        outer = PALETTE['fire_orange']
        edge = PALETTE['fire_red']

        # Outer flame shape
        points = []
        for i in range(12):
            angle = (i / 12) * 2 * math.pi - math.pi / 2
            radius = 20 + random.randint(-4, 8)
            x = cx + int(math.cos(angle) * radius)
            y = cy + int(math.sin(angle) * radius * 0.8)
            points.append((x, y))
        pygame.draw.polygon(surface, (*edge[:3], 180), points)

        # Middle layer
        pygame.draw.ellipse(surface, (*outer[:3], 200), (cx - 14, cy - 12, 28, 28))

        # Inner layer
        pygame.draw.ellipse(surface, (*mid[:3], 220), (cx - 10, cy - 8, 20, 20))

        # Core
        pygame.draw.ellipse(surface, core, (cx - 6, cy - 4, 12, 12))

        # Eyes
        pygame.draw.ellipse(surface, (255, 255, 255), (cx - 6, cy - 6, 5, 4))
        pygame.draw.ellipse(surface, (255, 255, 255), (cx + 1, cy - 6, 5, 4))

        # Flame wisps rising
        for i in range(4):
            wx = cx + random.randint(-10, 10)
            wy = cy - 16 - random.randint(0, 12)
            pygame.draw.ellipse(surface, (*mid[:3], 150), (wx - 3, wy, 6, 10))

        # Ember particles
        for _ in range(8):
            px = cx + random.randint(-18, 18)
            py = cy + random.randint(-20, 10)
            pygame.draw.circle(surface, mid, (px, py), 1)

        return surface


class IceElementalSprite(BaseSprite):
    """Crystalline ice humanoid."""

    def __init__(self):
        super().__init__('ice_elemental', 'enemy')

    def _generate_base_sprite(self) -> pygame.Surface:
        surface = create_surface(self.base_size)
        cx, cy = 32, 36

        ice = PALETTE['ice_base']
        ice_light = PALETTE['ice_light']
        ice_dark = PALETTE['ice_dark']
        core = PALETTE['eye_glow_blue']

        # Main crystalline body
        pygame.draw.polygon(surface, ice, [
            (cx, cy - 20), (cx + 14, cy - 4), (cx + 10, cy + 16),
            (cx - 10, cy + 16), (cx - 14, cy - 4)
        ])

        # Inner glow
        pygame.draw.polygon(surface, (*core[:3], 100), [
            (cx, cy - 14), (cx + 8, cy - 2), (cx + 6, cy + 10),
            (cx - 6, cy + 10), (cx - 8, cy - 2)
        ])

        # Crystal spikes on shoulders
        pygame.draw.polygon(surface, ice_light, [
            (cx - 14, cy - 4), (cx - 22, cy - 16), (cx - 10, cy - 8)
        ])
        pygame.draw.polygon(surface, ice_light, [
            (cx + 14, cy - 4), (cx + 22, cy - 16), (cx + 10, cy - 8)
        ])

        # Crystal spikes on head
        pygame.draw.polygon(surface, ice_light, [
            (cx - 4, cy - 20), (cx - 6, cy - 32), (cx, cy - 22)
        ])
        pygame.draw.polygon(surface, ice_light, [
            (cx + 4, cy - 20), (cx + 6, cy - 32), (cx, cy - 22)
        ])

        # Glowing blue eyes
        pygame.draw.ellipse(surface, core, (cx - 6, cy - 10, 5, 4))
        pygame.draw.ellipse(surface, core, (cx + 1, cy - 10, 5, 4))

        # Frost patterns
        pygame.draw.line(surface, ice_dark, (cx - 8, cy - 6), (cx - 4, cy + 4), 1)
        pygame.draw.line(surface, ice_dark, (cx + 8, cy - 6), (cx + 4, cy + 4), 1)

        # Snow particles
        for _ in range(6):
            px = cx + random.randint(-16, 16)
            py = cy + random.randint(-18, 14)
            pygame.draw.circle(surface, ice_light, (px, py), 1)

        return surface


class EarthElementalSprite(BaseSprite):
    """Bulky humanoid of rock and dirt."""

    def __init__(self):
        super().__init__('earth_elemental', 'enemy')

    def _generate_base_sprite(self) -> pygame.Surface:
        surface = create_surface(self.base_size)
        cx = 32

        rock = PALETTE['earth_base']
        rock_dark = darken_color(rock, 40)
        rock_light = PALETTE['earth_light']
        core = PALETTE['fire_orange']

        # Massive rocky body
        pygame.draw.ellipse(surface, rock, (cx - 16, 20, 32, 32))

        # Boulder segments
        pygame.draw.circle(surface, rock_light, (cx - 8, 28), 8)
        pygame.draw.circle(surface, rock, (cx + 6, 32), 10)
        pygame.draw.circle(surface, rock_dark, (cx - 4, 42), 7)

        # Head boulder
        pygame.draw.circle(surface, rock, (cx, 14), 12)

        # Glowing cracks
        pygame.draw.line(surface, core, (cx - 8, 26), (cx - 2, 36), 2)
        pygame.draw.line(surface, core, (cx + 4, 30), (cx + 10, 42), 2)
        pygame.draw.line(surface, core, (cx - 4, 10), (cx + 2, 18), 1)

        # Glowing eyes
        pygame.draw.ellipse(surface, core, (cx - 6, 12, 5, 4))
        pygame.draw.ellipse(surface, core, (cx + 1, 12, 5, 4))

        # Arm boulders
        pygame.draw.circle(surface, rock, (cx - 20, 30), 10)
        pygame.draw.circle(surface, rock, (cx + 20, 30), 10)

        # Moss and roots
        for _ in range(4):
            mx = cx + random.randint(-14, 14)
            my = random.randint(24, 48)
            pygame.draw.ellipse(surface, PALETTE['moss'], (mx - 3, my, 6, 4))

        # Crystal formations on back
        pygame.draw.polygon(surface, PALETTE['gold_shadow'], [
            (cx + 10, 22), (cx + 16, 10), (cx + 14, 24)
        ])

        # Dust particles
        for _ in range(5):
            px = cx + random.randint(-18, 18)
            py = 52 + random.randint(0, 6)
            pygame.draw.circle(surface, rock_light, (px, py), 1)

        return surface


class DemonSprite(BaseSprite):
    """Large muscular demon with wings."""

    def __init__(self):
        super().__init__('demon', 'enemy')

    def _generate_base_sprite(self) -> pygame.Surface:
        surface = create_surface(self.base_size)
        cx = 32

        skin = PALETTE['skin_demon']
        skin_dark = darken_color(skin, 40)

        # Muscular body
        pygame.draw.ellipse(surface, skin, (cx - 14, 22, 28, 28))

        # Head
        pygame.draw.ellipse(surface, skin, (cx - 10, 8, 20, 16))

        # Large curved horns
        pygame.draw.polygon(surface, (60, 40, 40), [
            (cx - 8, 10), (cx - 18, 2), (cx - 14, 14)
        ])
        pygame.draw.polygon(surface, (60, 40, 40), [
            (cx + 8, 10), (cx + 18, 2), (cx + 14, 14)
        ])

        # Glowing orange eyes
        pygame.draw.ellipse(surface, PALETTE['fire_orange'], (cx - 6, 14, 5, 4))
        pygame.draw.ellipse(surface, PALETTE['fire_orange'], (cx + 1, 14, 5, 4))

        # Fanged mouth
        pygame.draw.rect(surface, (40, 20, 20), (cx - 4, 20, 8, 4))
        draw_pixel(surface, (255, 255, 240), (cx - 2, 20))
        draw_pixel(surface, (255, 255, 240), (cx + 2, 20))

        # Bat wings
        pygame.draw.polygon(surface, skin_dark, [
            (cx - 14, 24), (cx - 28, 8), (cx - 24, 36), (cx - 14, 44)
        ])
        pygame.draw.polygon(surface, skin_dark, [
            (cx + 14, 24), (cx + 28, 8), (cx + 24, 36), (cx + 14, 44)
        ])

        # Clawed hands
        pygame.draw.ellipse(surface, skin, (cx - 20, 36, 8, 10))
        pygame.draw.ellipse(surface, skin, (cx + 12, 36, 8, 10))

        # Cloven hooves
        pygame.draw.rect(surface, (40, 30, 30), (cx - 10, 48, 8, 10))
        pygame.draw.rect(surface, (40, 30, 30), (cx + 2, 48, 8, 10))

        # Barbed tail
        pygame.draw.line(surface, skin, (cx, 48), (cx + 16, 56), 3)
        pygame.draw.polygon(surface, skin_dark, [
            (cx + 14, 54), (cx + 22, 58), (cx + 18, 52)
        ])

        # Fire emanating
        for _ in range(4):
            fx = cx + random.randint(-12, 12)
            fy = random.randint(26, 44)
            pygame.draw.circle(surface, PALETTE['fire_orange'], (fx, fy), 2)

        return surface


class WraithSprite(BaseSprite):
    """Hooded dark specter with chains."""

    def __init__(self):
        super().__init__('wraith', 'enemy')

    def _generate_base_sprite(self) -> pygame.Surface:
        surface = create_surface(self.base_size)
        cx, cy = 32, 32

        dark = PALETTE['void_black']
        glow = PALETTE['void_glow']

        # Wispy lower body
        for y in range(20):
            alpha = max(0, 150 - y * 6)
            width = 20 - y // 2
            color = (*dark[:3], alpha)
            pygame.draw.ellipse(surface, color, (cx - width//2, cy + y, width, 4))

        # Hooded upper body
        pygame.draw.ellipse(surface, (*dark[:3], 220), (cx - 14, cy - 16, 28, 32))

        # Hood
        pygame.draw.ellipse(surface, dark, (cx - 12, cy - 20, 24, 20))

        # Dark void inside hood
        pygame.draw.ellipse(surface, (10, 8, 15), (cx - 8, cy - 14, 16, 14))

        # Glowing eyes
        pygame.draw.circle(surface, glow, (cx - 4, cy - 8), 3)
        pygame.draw.circle(surface, glow, (cx + 4, cy - 8), 3)

        # Skeletal hands reaching
        bone = PALETTE['bone_shadow']
        pygame.draw.line(surface, bone, (cx - 14, cy), (cx - 24, cy - 10), 2)
        pygame.draw.line(surface, bone, (cx + 14, cy), (cx + 24, cy - 10), 2)
        # Fingers
        for i in range(3):
            pygame.draw.line(surface, bone, (cx - 24, cy - 10), (cx - 28 + i*2, cy - 16), 1)
            pygame.draw.line(surface, bone, (cx + 24, cy - 10), (cx + 28 - i*2, cy - 16), 1)

        # Chains
        chain_color = (80, 80, 90)
        for i in range(4):
            cy_chain = cy - 8 + i * 6
            pygame.draw.ellipse(surface, chain_color, (cx - 18, cy_chain, 6, 4), 1)
            pygame.draw.ellipse(surface, chain_color, (cx + 12, cy_chain, 6, 4), 1)

        # Dark energy
        for _ in range(6):
            px = cx + random.randint(-16, 16)
            py = cy + random.randint(-12, 16)
            pygame.draw.circle(surface, (*glow[:3], 80), (px, py), random.randint(1, 3))

        return surface


class SnakeSprite(BaseSprite):
    """Large coiled serpent."""

    def __init__(self):
        super().__init__('snake', 'enemy')

    def _generate_base_sprite(self) -> pygame.Surface:
        surface = create_surface(self.base_size)
        cx, cy = 32, 40

        scale = PALETTE['scale_green']
        scale_dark = darken_color(scale, 40)
        scale_light = lighten_color(scale, 30)

        # Coiled body
        pygame.draw.ellipse(surface, scale, (cx - 16, cy - 8, 32, 24))
        pygame.draw.ellipse(surface, scale_dark, (cx - 12, cy - 4, 24, 16))
        pygame.draw.ellipse(surface, scale, (cx - 8, cy, 16, 10))

        # Head raised with hood (cobra-like)
        pygame.draw.ellipse(surface, scale, (cx - 10, cy - 28, 20, 24))
        # Hood flared
        pygame.draw.ellipse(surface, scale_light, (cx - 14, cy - 22, 28, 16))

        # Pattern on hood
        pygame.draw.circle(surface, scale_dark, (cx - 6, cy - 16), 3)
        pygame.draw.circle(surface, scale_dark, (cx + 6, cy - 16), 3)

        # Face
        pygame.draw.ellipse(surface, scale, (cx - 6, cy - 26, 12, 14))

        # Yellow slit eyes
        pygame.draw.ellipse(surface, PALETTE['eye_yellow'], (cx - 4, cy - 22, 4, 5))
        pygame.draw.ellipse(surface, PALETTE['eye_yellow'], (cx, cy - 22, 4, 5))
        pygame.draw.line(surface, (0, 0, 0), (cx - 2, cy - 24), (cx - 2, cy - 18), 1)
        pygame.draw.line(surface, (0, 0, 0), (cx + 2, cy - 24), (cx + 2, cy - 18), 1)

        # Fangs
        draw_pixel(surface, (255, 255, 255), (cx - 2, cy - 14))
        draw_pixel(surface, (255, 255, 255), (cx + 2, cy - 14))

        # Forked tongue
        pygame.draw.line(surface, (200, 80, 100), (cx, cy - 12), (cx, cy - 8), 1)
        pygame.draw.line(surface, (200, 80, 100), (cx, cy - 8), (cx - 2, cy - 6), 1)
        pygame.draw.line(surface, (200, 80, 100), (cx, cy - 8), (cx + 2, cy - 6), 1)

        # Scale pattern on body
        for i in range(3):
            for j in range(4):
                sx = cx - 10 + j * 6
                sy = cy - 2 + i * 6
                pygame.draw.ellipse(surface, scale_dark, (sx, sy, 4, 3))

        return surface


class VampireSprite(BaseSprite):
    """Elegant vampire with cape."""

    def __init__(self):
        super().__init__('vampire', 'enemy')

    def _generate_base_sprite(self) -> pygame.Surface:
        surface = create_surface(self.base_size)
        cx = 32

        skin = PALETTE['skin_pale']
        cape = PALETTE['cloth_purple_dark']
        cape_inner = PALETTE['cloth_red_dark']

        # Cape (flowing)
        pygame.draw.polygon(surface, cape, [
            (cx - 16, 20), (cx + 16, 20), (cx + 20, 58), (cx - 20, 58)
        ])
        # Cape inner red
        pygame.draw.polygon(surface, cape_inner, [
            (cx - 12, 24), (cx + 12, 24), (cx + 14, 54), (cx - 14, 54)
        ])

        # Body underneath
        pygame.draw.rect(surface, PALETTE['cloth_black'], (cx - 8, 26, 16, 24))

        # Head
        pygame.draw.ellipse(surface, skin, (cx - 8, 8, 16, 18))

        # Slicked hair
        pygame.draw.ellipse(surface, PALETTE['hair_black'], (cx - 8, 6, 16, 10))
        pygame.draw.polygon(surface, PALETTE['hair_black'], [
            (cx - 6, 10), (cx, 4), (cx + 6, 10)
        ])

        # Glowing red eyes
        pygame.draw.ellipse(surface, PALETTE['eye_glow_red'], (cx - 5, 14, 4, 3))
        pygame.draw.ellipse(surface, PALETTE['eye_glow_red'], (cx + 1, 14, 4, 3))

        # Pale face features
        draw_pixel(surface, darken_color(skin, 20), (cx, 18))  # Nose

        # Fanged smile
        pygame.draw.line(surface, (60, 20, 20), (cx - 3, 22), (cx + 3, 22), 1)
        draw_pixel(surface, (255, 255, 255), (cx - 2, 22))
        draw_pixel(surface, (255, 255, 255), (cx + 2, 22))

        # Cape collar high
        pygame.draw.polygon(surface, cape, [
            (cx - 10, 20), (cx - 16, 12), (cx - 8, 18)
        ])
        pygame.draw.polygon(surface, cape, [
            (cx + 10, 20), (cx + 16, 12), (cx + 8, 18)
        ])

        # Hands visible
        pygame.draw.ellipse(surface, skin, (cx - 16, 40, 6, 8))
        pygame.draw.ellipse(surface, skin, (cx + 10, 40, 6, 8))

        return surface


class NecromancerSprite(BaseSprite):
    """Hooded skeletal mage."""

    def __init__(self):
        super().__init__('necromancer', 'enemy')

    def _generate_base_sprite(self) -> pygame.Surface:
        surface = create_surface(self.base_size)
        cx = 32

        robe = PALETTE['cloth_purple_dark']
        robe_dark = darken_color(robe, 30)
        bone = PALETTE['bone_white']

        # Dark robes
        pygame.draw.polygon(surface, robe, [
            (cx - 14, 20), (cx + 14, 20), (cx + 18, 58), (cx - 18, 58)
        ])
        pygame.draw.polygon(surface, robe_dark, [
            (cx - 14, 20), (cx + 14, 20), (cx + 18, 58), (cx - 18, 58)
        ], 2)

        # Skull motifs on robe
        pygame.draw.circle(surface, bone, (cx, 38), 4)
        pygame.draw.rect(surface, (20, 20, 30), (cx - 2, 36, 2, 2))
        pygame.draw.rect(surface, (20, 20, 30), (cx, 36, 2, 2))

        # Hood
        pygame.draw.ellipse(surface, robe, (cx - 12, 6, 24, 20))
        pygame.draw.ellipse(surface, (10, 10, 15), (cx - 8, 10, 16, 14))

        # Glowing eyes under hood
        pygame.draw.circle(surface, PALETTE['eye_glow_green'], (cx - 4, 16), 2)
        pygame.draw.circle(surface, PALETTE['eye_glow_green'], (cx + 4, 16), 2)

        # Skeletal hands
        pygame.draw.ellipse(surface, bone, (cx - 20, 34, 8, 10))
        pygame.draw.ellipse(surface, bone, (cx + 12, 34, 8, 10))

        # Staff with skull
        pygame.draw.rect(surface, PALETTE['bark_dark'], (cx + 20, 14, 4, 42))
        pygame.draw.circle(surface, bone, (cx + 22, 12), 6)
        pygame.draw.rect(surface, (20, 20, 30), (cx + 19, 10, 3, 2))
        pygame.draw.rect(surface, (20, 20, 30), (cx + 23, 10, 3, 2))

        # Ghostly energy around hands
        for _ in range(4):
            gx = cx + random.choice([-16, 16]) + random.randint(-4, 4)
            gy = 36 + random.randint(-4, 4)
            pygame.draw.circle(surface, (*PALETTE['ghost_blue'][:3], 100), (gx, gy), 3)

        # Floating bone fragments
        for _ in range(3):
            bx = cx + random.randint(-12, 12)
            by = random.randint(24, 48)
            pygame.draw.ellipse(surface, bone, (bx, by, 3, 2))

        return surface


class DarkKnightSprite(BaseSprite):
    """Black armored knight with dark aura."""

    def __init__(self):
        super().__init__('dark_knight', 'enemy')

    def _generate_base_sprite(self) -> pygame.Surface:
        surface = create_surface(self.base_size)
        cx = 32

        armor = PALETTE['steel_dark']
        armor_light = PALETTE['steel_shadow']
        glow = PALETTE['eye_glow_red']

        # Full plate armor body
        pygame.draw.rect(surface, armor, (cx - 12, 22, 24, 28))
        pygame.draw.rect(surface, armor_light, (cx - 12, 22, 24, 28), 2)

        # Shoulder pads with spikes
        pygame.draw.ellipse(surface, armor, (cx - 18, 20, 12, 10))
        pygame.draw.ellipse(surface, armor, (cx + 6, 20, 12, 10))
        pygame.draw.polygon(surface, armor_light, [(cx - 14, 18), (cx - 16, 10), (cx - 10, 18)])
        pygame.draw.polygon(surface, armor_light, [(cx + 14, 18), (cx + 16, 10), (cx + 10, 18)])

        # Helmet with glowing visor
        pygame.draw.ellipse(surface, armor, (cx - 10, 6, 20, 18))
        pygame.draw.rect(surface, (20, 20, 25), (cx - 6, 14, 12, 4))  # Visor slit
        pygame.draw.rect(surface, glow, (cx - 5, 15, 4, 2))  # Glowing eyes
        pygame.draw.rect(surface, glow, (cx + 1, 15, 4, 2))

        # Helmet crest
        pygame.draw.polygon(surface, armor_light, [
            (cx - 2, 6), (cx + 2, 6), (cx, -2)
        ])

        # Tattered dark cape
        pygame.draw.polygon(surface, PALETTE['void_black'], [
            (cx - 10, 24), (cx + 10, 24), (cx + 14, 58), (cx - 14, 58)
        ])

        # Massive sword
        pygame.draw.rect(surface, armor_light, (cx + 16, 16, 5, 36))
        pygame.draw.polygon(surface, PALETTE['steel_base'], [
            (cx + 15, 16), (cx + 22, 16), (cx + 18, 6)
        ])
        pygame.draw.rect(surface, PALETTE['cloth_red_dark'], (cx + 14, 48, 8, 4))  # Handle

        # Dark aura
        for _ in range(6):
            ax = cx + random.randint(-16, 16)
            ay = random.randint(10, 50)
            pygame.draw.circle(surface, (*PALETTE['void_purple'][:3], 60), (ax, ay), 3)

        return surface


# Factory and list exports
def get_advanced_enemy_sprite(name: str) -> Optional[BaseSprite]:
    """Get an advanced enemy sprite generator by name."""
    sprites = {
        'werewolf': WerewolfSprite,
        'mimic': MimicSprite,
        'golem': GolemSprite,
        'mushroom': MushroomSprite,
        'fire_elemental': FireElementalSprite,
        'ice_elemental': IceElementalSprite,
        'earth_elemental': EarthElementalSprite,
        'demon': DemonSprite,
        'wraith': WraithSprite,
        'snake': SnakeSprite,
        'vampire': VampireSprite,
        'necromancer': NecromancerSprite,
        'dark_knight': DarkKnightSprite,
    }

    sprite_class = sprites.get(name.lower())
    if sprite_class:
        return sprite_class()
    return None


ADVANCED_ENEMIES = [
    'werewolf', 'mimic', 'golem', 'mushroom',
    'fire_elemental', 'ice_elemental', 'earth_elemental',
    'demon', 'wraith', 'snake', 'vampire', 'necromancer', 'dark_knight'
]
