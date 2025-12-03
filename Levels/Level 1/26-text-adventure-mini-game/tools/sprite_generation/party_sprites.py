"""
Party Member Sprite Generators

Contains sprite generators for all player/party member classes:
- Warrior (sword and shield)
- Mage (staff and robes)
- Rogue (daggers and hood)
- Cleric (mace and holy symbol)
- Ranger (bow and cloak)
- Paladin (heavy armor and blessed weapon)
"""

import pygame
import random
import math
from typing import List, Optional

from .base_sprite import BaseSprite
from .utils import create_surface, draw_pixel, darken_color, lighten_color
from .palette import PALETTE


class PartySprite(BaseSprite):
    """Base class for party member sprites."""

    def __init__(self, name: str):
        super().__init__(name, 'party')


class WarriorSprite(PartySprite):
    """Heavy armor warrior with sword and shield."""

    def __init__(self):
        super().__init__('warrior')

    def _generate_base_sprite(self) -> pygame.Surface:
        surface = create_surface(self.base_size)
        cx = 32

        skin = PALETTE['skin_medium']
        armor = PALETTE['steel_base']
        armor_dark = PALETTE['steel_shadow']

        # Plate armor body
        pygame.draw.rect(surface, armor, (cx - 12, 22, 24, 26))
        pygame.draw.rect(surface, armor_dark, (cx - 12, 22, 24, 26), 2)

        # Shoulder pads
        pygame.draw.ellipse(surface, armor, (cx - 18, 20, 10, 10))
        pygame.draw.ellipse(surface, armor, (cx + 8, 20, 10, 10))

        # Helmet
        pygame.draw.ellipse(surface, armor, (cx - 9, 6, 18, 18))
        pygame.draw.rect(surface, (30, 30, 35), (cx - 5, 14, 10, 3))  # Visor

        # Face visible
        pygame.draw.ellipse(surface, skin, (cx - 4, 16, 8, 7))
        pygame.draw.ellipse(surface, PALETTE['eye_blue'], (cx - 3, 17, 2, 2))
        pygame.draw.ellipse(surface, PALETTE['eye_blue'], (cx + 1, 17, 2, 2))

        # Helmet crest
        pygame.draw.polygon(surface, PALETTE['cloth_red'], [
            (cx - 2, 6), (cx + 2, 6), (cx, -2)
        ])

        # Arms in armor
        pygame.draw.ellipse(surface, armor, (cx - 20, 24, 10, 18))
        pygame.draw.ellipse(surface, armor, (cx + 10, 24, 10, 18))

        # Longsword
        pygame.draw.rect(surface, PALETTE['steel_highlight'], (cx + 18, 14, 4, 32))
        pygame.draw.polygon(surface, PALETTE['steel_base'], [
            (cx + 17, 14), (cx + 23, 14), (cx + 20, 6)
        ])
        pygame.draw.rect(surface, PALETTE['leather_dark'], (cx + 16, 42, 8, 6))  # Handle

        # Tower shield
        pygame.draw.ellipse(surface, armor, (cx - 26, 24, 12, 22))
        pygame.draw.ellipse(surface, PALETTE['cloth_red'], (cx - 24, 30, 8, 10))
        pygame.draw.circle(surface, PALETTE['gold_base'], (cx - 20, 35), 3)

        # Legs
        pygame.draw.rect(surface, armor_dark, (cx - 10, 46, 8, 12))
        pygame.draw.rect(surface, armor_dark, (cx + 2, 46, 8, 12))

        return surface

    def _generate_attack_frames(self) -> List[pygame.Surface]:
        """Generate sword swing attack animation."""
        frames = []
        base = self._generate_base_sprite()

        # Frame 1: Wind up
        frame1 = base.copy()
        # Sword raised
        pygame.draw.rect(frame1, PALETTE['steel_highlight'], (28, 4, 4, 28))
        pygame.draw.polygon(frame1, PALETTE['steel_base'], [(27, 4), (33, 4), (30, -4)])
        frames.append(frame1)

        # Frame 2: Mid swing
        frame2 = base.copy()
        pygame.draw.rect(frame2, PALETTE['steel_highlight'], (48, 24, 12, 4))
        pygame.draw.polygon(frame2, PALETTE['steel_base'], [(60, 23), (60, 29), (66, 26)])
        frames.append(frame2)

        # Frame 3: Full swing
        frame3 = base.copy()
        pygame.draw.rect(frame3, PALETTE['steel_highlight'], (50, 40, 4, 18))
        pygame.draw.polygon(frame3, PALETTE['steel_base'], [(49, 58), (55, 58), (52, 64)])
        frames.append(frame3)

        # Frame 4: Recovery
        frames.append(base.copy())

        return frames


class MageSprite(PartySprite):
    """Robed mage with staff and spell effects."""

    def __init__(self):
        super().__init__('mage')

    def _generate_base_sprite(self) -> pygame.Surface:
        surface = create_surface(self.base_size)
        cx = 32

        skin = PALETTE['skin_pale']
        robe = PALETTE['cloth_blue']
        robe_dark = darken_color(robe, 30)

        # Flowing robes
        pygame.draw.polygon(surface, robe, [
            (cx - 12, 20), (cx + 12, 20),
            (cx + 18, 58), (cx - 18, 58)
        ])
        pygame.draw.polygon(surface, robe_dark, [
            (cx - 12, 20), (cx + 12, 20),
            (cx + 18, 58), (cx - 18, 58)
        ], 2)

        # Magic runes on robe
        pygame.draw.circle(surface, PALETTE['void_glow'], (cx, 36), 4, 1)
        pygame.draw.line(surface, PALETTE['void_glow'], (cx, 32), (cx, 40), 1)

        # Hood (optional - down for now)
        pygame.draw.ellipse(surface, robe, (cx - 10, 18, 20, 6))

        # Head
        pygame.draw.ellipse(surface, skin, (cx - 7, 8, 14, 14))

        # Mystical purple eyes
        pygame.draw.ellipse(surface, PALETTE['eye_purple'], (cx - 4, 14, 3, 3))
        pygame.draw.ellipse(surface, PALETTE['eye_purple'], (cx + 1, 14, 3, 3))

        # Grey hair
        pygame.draw.ellipse(surface, PALETTE['hair_grey'], (cx - 6, 4, 12, 10))

        # Arms
        pygame.draw.ellipse(surface, robe, (cx - 18, 26, 10, 16))
        pygame.draw.ellipse(surface, robe, (cx + 8, 26, 10, 16))

        # Staff with crystal
        pygame.draw.rect(surface, PALETTE['bark_dark'], (cx + 18, 6, 4, 50))
        pygame.draw.circle(surface, PALETTE['void_glow'], (cx + 20, 4), 6)
        pygame.draw.circle(surface, (255, 200, 255), (cx + 18, 2), 2)

        # Glowing hand
        pygame.draw.ellipse(surface, skin, (cx - 16, 38, 6, 8))
        pygame.draw.circle(surface, (*PALETTE['void_glow'][:3], 100), (cx - 13, 42), 5)

        return surface

    def _generate_attack_frames(self) -> List[pygame.Surface]:
        """Generate spell casting animation."""
        frames = []
        base = self._generate_base_sprite()

        for i in range(4):
            frame = base.copy()
            # Growing magic circle
            radius = 4 + i * 3
            pygame.draw.circle(frame, (*PALETTE['void_glow'][:3], 150 - i * 20),
                             (20, 42), radius, 2)
            # Particles
            for j in range(i + 1):
                angle = (j / (i + 1)) * 6.28
                px = 20 + int(math.cos(angle) * (radius + 4))
                py = 42 + int(math.sin(angle) * (radius + 4))
                pygame.draw.circle(frame, PALETTE['void_glow'], (px, py), 2)
            frames.append(frame)

        return frames


class RogueSprite(PartySprite):
    """Hooded rogue with daggers."""

    def __init__(self):
        super().__init__('rogue')

    def _generate_base_sprite(self) -> pygame.Surface:
        surface = create_surface(self.base_size)
        cx = 32

        skin = PALETTE['skin_tan']
        cloak = PALETTE['cloth_brown']
        cloak_dark = darken_color(cloak, 40)

        # Leather armor body
        pygame.draw.ellipse(surface, PALETTE['leather_base'], (cx - 10, 24, 20, 24))

        # Cloak
        pygame.draw.polygon(surface, cloak, [
            (cx - 14, 18), (cx + 14, 18),
            (cx + 20, 54), (cx - 20, 54)
        ])
        pygame.draw.polygon(surface, cloak_dark, [
            (cx - 14, 18), (cx + 14, 18),
            (cx + 20, 54), (cx - 20, 54)
        ], 2)

        # Hood up
        pygame.draw.ellipse(surface, cloak, (cx - 10, 4, 20, 18))

        # Face in shadow
        pygame.draw.ellipse(surface, cloak_dark, (cx - 6, 10, 12, 12))

        # Glinting eyes
        pygame.draw.ellipse(surface, PALETTE['eye_green'], (cx - 4, 14, 3, 2))
        pygame.draw.ellipse(surface, PALETTE['eye_green'], (cx + 1, 14, 3, 2))

        # Mask over lower face
        pygame.draw.rect(surface, (20, 20, 25), (cx - 4, 18, 8, 4))

        # Arms
        pygame.draw.ellipse(surface, cloak, (cx - 18, 24, 10, 16))
        pygame.draw.ellipse(surface, cloak, (cx + 8, 24, 10, 16))

        # Dual daggers
        pygame.draw.rect(surface, PALETTE['steel_highlight'], (cx + 16, 36, 2, 12))
        pygame.draw.polygon(surface, PALETTE['steel_base'], [(cx + 15, 36), (cx + 19, 36), (cx + 17, 30)])
        pygame.draw.rect(surface, PALETTE['steel_highlight'], (cx - 18, 36, 2, 12))
        pygame.draw.polygon(surface, PALETTE['steel_base'], [(cx - 19, 36), (cx - 15, 36), (cx - 17, 30)])

        # Belt with pouches
        pygame.draw.rect(surface, PALETTE['leather_dark'], (cx - 10, 44, 20, 4))
        pygame.draw.rect(surface, PALETTE['leather_base'], (cx - 8, 44, 4, 6))
        pygame.draw.rect(surface, PALETTE['leather_base'], (cx + 4, 44, 4, 6))

        return surface


class ClericSprite(PartySprite):
    """Holy cleric with mace and symbol."""

    def __init__(self):
        super().__init__('cleric')

    def _generate_base_sprite(self) -> pygame.Surface:
        surface = create_surface(self.base_size)
        cx = 32

        skin = PALETTE['skin_light']
        robe = PALETTE['cloth_white']
        gold = PALETTE['gold_base']

        # White robes with gold trim
        pygame.draw.polygon(surface, robe, [
            (cx - 12, 22), (cx + 12, 22),
            (cx + 14, 58), (cx - 14, 58)
        ])
        pygame.draw.rect(surface, gold, (cx - 10, 26, 20, 3))
        pygame.draw.rect(surface, gold, (cx - 10, 44, 20, 3))

        # Shoulder cape
        pygame.draw.polygon(surface, PALETTE['cloth_blue'], [
            (cx - 14, 22), (cx + 14, 22),
            (cx + 10, 38), (cx - 10, 38)
        ])

        # Head
        pygame.draw.ellipse(surface, skin, (cx - 7, 10, 14, 14))

        # Serene expression
        pygame.draw.ellipse(surface, PALETTE['eye_blue'], (cx - 4, 16, 3, 2))
        pygame.draw.ellipse(surface, PALETTE['eye_blue'], (cx + 1, 16, 3, 2))
        pygame.draw.arc(surface, (0, 0, 0), (cx - 3, 20, 6, 3), 0, 3.14, 1)

        # Holy headband
        pygame.draw.rect(surface, gold, (cx - 6, 8, 12, 3))
        pygame.draw.circle(surface, PALETTE['holy_gold'], (cx, 9), 3)

        # Light brown hair
        pygame.draw.ellipse(surface, PALETTE['hair_brown'], (cx - 5, 4, 10, 8))

        # Arms
        pygame.draw.ellipse(surface, robe, (cx - 18, 26, 10, 14))
        pygame.draw.ellipse(surface, robe, (cx + 8, 26, 10, 14))

        # Holy mace
        pygame.draw.rect(surface, gold, (cx + 16, 24, 3, 22))
        pygame.draw.ellipse(surface, gold, (cx + 13, 18, 9, 10))

        # Holy symbol (on chest)
        pygame.draw.line(surface, gold, (cx, 30), (cx, 40), 2)
        pygame.draw.line(surface, gold, (cx - 4, 34), (cx + 4, 34), 2)

        return surface

    def _generate_attack_frames(self) -> List[pygame.Surface]:
        """Generate healing/smite animation."""
        frames = []
        base = self._generate_base_sprite()

        for i in range(4):
            frame = base.copy()
            # Holy light aura
            alpha = 100 + i * 30
            radius = 16 - i * 2
            pygame.draw.circle(frame, (*PALETTE['holy_gold'][:3], min(alpha, 200)),
                             (32, 32), radius)
            # Light rays
            for j in range(8):
                angle = (j / 8) * 6.28 + i * 0.2
                length = 20 + i * 4
                end_x = 32 + int(math.cos(angle) * length)
                end_y = 32 + int(math.sin(angle) * length)
                pygame.draw.line(frame, (*PALETTE['holy_gold'][:3], 150),
                               (32, 32), (end_x, end_y), 1)
            frames.append(frame)

        return frames


class RangerSprite(PartySprite):
    """Forest ranger with bow and cloak."""

    def __init__(self):
        super().__init__('ranger')

    def _generate_base_sprite(self) -> pygame.Surface:
        surface = create_surface(self.base_size)
        cx = 32

        skin = PALETTE['skin_tan']
        cloak = PALETTE['cloth_green']
        leather = PALETTE['leather_base']

        # Leather armor
        pygame.draw.ellipse(surface, leather, (cx - 10, 24, 20, 22))

        # Green cloak
        pygame.draw.polygon(surface, cloak, [
            (cx - 12, 20), (cx + 12, 20),
            (cx + 16, 52), (cx - 16, 52)
        ])

        # Hood down
        pygame.draw.ellipse(surface, cloak, (cx - 10, 18, 20, 6))

        # Head
        pygame.draw.ellipse(surface, skin, (cx - 7, 8, 14, 14))

        # Sharp eyes
        pygame.draw.ellipse(surface, PALETTE['eye_green'], (cx - 4, 14, 3, 3))
        pygame.draw.ellipse(surface, PALETTE['eye_green'], (cx + 1, 14, 3, 3))

        # Short hair
        pygame.draw.ellipse(surface, PALETTE['hair_brown'], (cx - 6, 4, 12, 10))

        # Quiver on back
        pygame.draw.rect(surface, leather, (cx - 18, 22, 6, 20))
        for i in range(3):
            pygame.draw.line(surface, PALETTE['bark_base'],
                           (cx - 16, 22), (cx - 16, 18 - i * 2), 2)
            pygame.draw.polygon(surface, PALETTE['feather_white'],
                              [(cx - 17, 18 - i * 2), (cx - 15, 18 - i * 2),
                               (cx - 16, 14 - i * 2)])

        # Arms
        pygame.draw.ellipse(surface, cloak, (cx - 16, 26, 8, 14))
        pygame.draw.ellipse(surface, cloak, (cx + 8, 26, 8, 14))

        # Bow
        pygame.draw.arc(surface, PALETTE['bark_base'],
                       (cx + 14, 16, 12, 32), 1.57, 4.71, 3)
        pygame.draw.line(surface, PALETTE['steel_shadow'],
                        (cx + 20, 18), (cx + 20, 46), 1)

        # Bracer
        pygame.draw.rect(surface, leather, (cx + 10, 34, 6, 6))

        return surface


class PaladinSprite(PartySprite):
    """Holy warrior with heavy armor and blessed weapon."""

    def __init__(self):
        super().__init__('paladin')

    def _generate_base_sprite(self) -> pygame.Surface:
        surface = create_surface(self.base_size)
        cx = 32

        skin = PALETTE['skin_light']
        armor = PALETTE['steel_highlight']
        armor_dark = PALETTE['steel_base']
        gold = PALETTE['gold_base']

        # Ornate plate armor
        pygame.draw.rect(surface, armor, (cx - 12, 22, 24, 26))
        pygame.draw.rect(surface, armor_dark, (cx - 12, 22, 24, 26), 2)

        # Gold trim
        pygame.draw.rect(surface, gold, (cx - 10, 26, 20, 2))
        pygame.draw.rect(surface, gold, (cx - 10, 42, 20, 2))

        # Holy symbol on chest
        pygame.draw.line(surface, gold, (cx, 30), (cx, 40), 2)
        pygame.draw.line(surface, gold, (cx - 4, 34), (cx + 4, 34), 2)

        # Shoulder pads with wings motif
        pygame.draw.ellipse(surface, armor, (cx - 18, 18, 12, 12))
        pygame.draw.ellipse(surface, armor, (cx + 6, 18, 12, 12))
        pygame.draw.polygon(surface, gold, [(cx - 14, 18), (cx - 18, 12), (cx - 10, 18)])
        pygame.draw.polygon(surface, gold, [(cx + 14, 18), (cx + 18, 12), (cx + 10, 18)])

        # Helmet with holy crest
        pygame.draw.ellipse(surface, armor, (cx - 9, 4, 18, 18))
        pygame.draw.rect(surface, (30, 30, 35), (cx - 5, 12, 10, 4))  # Visor

        # Face
        pygame.draw.ellipse(surface, skin, (cx - 4, 14, 8, 8))
        pygame.draw.ellipse(surface, PALETTE['eye_blue'], (cx - 3, 16, 2, 2))
        pygame.draw.ellipse(surface, PALETTE['eye_blue'], (cx + 1, 16, 2, 2))

        # Holy crest
        pygame.draw.polygon(surface, gold, [(cx - 2, 4), (cx + 2, 4), (cx, -4)])

        # Arms
        pygame.draw.ellipse(surface, armor, (cx - 20, 24, 10, 16))
        pygame.draw.ellipse(surface, armor, (cx + 10, 24, 10, 16))

        # Blessed greatsword
        pygame.draw.rect(surface, PALETTE['steel_highlight'], (cx + 18, 8, 5, 40))
        pygame.draw.polygon(surface, PALETTE['steel_base'],
                          [(cx + 17, 8), (cx + 24, 8), (cx + 20, -2)])
        pygame.draw.line(surface, PALETTE['holy_gold'], (cx + 20, 14), (cx + 20, 42), 1)
        pygame.draw.rect(surface, gold, (cx + 16, 44, 10, 6))  # Crossguard

        # Holy aura (subtle)
        pygame.draw.circle(surface, (*PALETTE['holy_gold'][:3], 30), (cx, 32), 24)

        return surface


# Factory function
def get_party_sprite(name: str) -> Optional[PartySprite]:
    """Get a party member sprite generator by name."""
    sprites = {
        'warrior': WarriorSprite,
        'mage': MageSprite,
        'rogue': RogueSprite,
        'cleric': ClericSprite,
        'ranger': RangerSprite,
        'paladin': PaladinSprite,
    }

    sprite_class = sprites.get(name.lower())
    if sprite_class:
        return sprite_class()
    return None


PARTY_SPRITES = ['warrior', 'mage', 'rogue', 'cleric', 'ranger', 'paladin']
