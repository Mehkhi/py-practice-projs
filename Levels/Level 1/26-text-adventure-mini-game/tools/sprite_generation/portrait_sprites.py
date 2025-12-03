"""
Portrait Sprite Generators

Generates larger character portraits for dialogue and menus.
Portraits are 64x64 (or 128x128) showing head and shoulders with expressions.
"""

import pygame
import math
from typing import List, Optional, Dict

from .base_sprite import BaseSprite
from .utils import create_surface, draw_pixel, darken_color, lighten_color
from .palette import PALETTE


class PortraitSprite:
    """
    Portrait generator for larger character images.
    Supports multiple expressions.
    """

    def __init__(self, name: str, character_type: str):
        self.name = name
        self.character_type = character_type
        self.base_size = 64
        self.expressions = ['neutral', 'happy', 'angry', 'sad', 'surprised']

    def generate_all_expressions(self) -> Dict[str, pygame.Surface]:
        """Generate portraits for all expressions."""
        return {expr: self._generate_portrait(expr) for expr in self.expressions}

    def _generate_portrait(self, expression: str) -> pygame.Surface:
        """Generate a portrait with the given expression. Override in subclass."""
        surface = create_surface(self.base_size)
        return surface

    def save_all(self, output_dir: str):
        """Save all expression variants."""
        import os
        portraits = self.generate_all_expressions()

        char_dir = os.path.join(output_dir, self.character_type, self.name)
        os.makedirs(char_dir, exist_ok=True)

        for expr, surface in portraits.items():
            filepath = os.path.join(char_dir, f'{expr}.png')
            pygame.image.save(surface, filepath)


class WarriorPortrait(PortraitSprite):
    """Portrait for warrior class."""

    def __init__(self):
        super().__init__('warrior', 'party')

    def _generate_portrait(self, expression: str) -> pygame.Surface:
        surface = create_surface(self.base_size)
        cx, cy = 32, 36

        skin = PALETTE['skin_medium']
        armor = PALETTE['steel_base']

        # Shoulders/armor
        pygame.draw.ellipse(surface, armor, (cx - 28, cy + 8, 56, 28))
        pygame.draw.ellipse(surface, darken_color(armor, 30), (cx - 28, cy + 8, 56, 28), 2)

        # Neck
        pygame.draw.rect(surface, skin, (cx - 8, cy - 2, 16, 14))

        # Face
        pygame.draw.ellipse(surface, skin, (cx - 14, cy - 24, 28, 30))

        # Hair
        pygame.draw.ellipse(surface, PALETTE['hair_brown'], (cx - 12, cy - 26, 24, 16))

        # Eyes based on expression
        eye_y = cy - 12
        if expression == 'neutral':
            pygame.draw.ellipse(surface, PALETTE['eye_blue'], (cx - 8, eye_y, 6, 5))
            pygame.draw.ellipse(surface, PALETTE['eye_blue'], (cx + 2, eye_y, 6, 5))
            pygame.draw.circle(surface, (0, 0, 0), (cx - 5, eye_y + 2), 2)
            pygame.draw.circle(surface, (0, 0, 0), (cx + 5, eye_y + 2), 2)
        elif expression == 'happy':
            pygame.draw.arc(surface, (0, 0, 0), (cx - 9, eye_y - 2, 8, 6), 3.14, 6.28, 2)
            pygame.draw.arc(surface, (0, 0, 0), (cx + 1, eye_y - 2, 8, 6), 3.14, 6.28, 2)
        elif expression == 'angry':
            pygame.draw.ellipse(surface, PALETTE['eye_blue'], (cx - 8, eye_y + 1, 6, 4))
            pygame.draw.ellipse(surface, PALETTE['eye_blue'], (cx + 2, eye_y + 1, 6, 4))
            pygame.draw.line(surface, darken_color(skin, 40), (cx - 10, eye_y - 2), (cx - 4, eye_y), 2)
            pygame.draw.line(surface, darken_color(skin, 40), (cx + 10, eye_y - 2), (cx + 4, eye_y), 2)
        elif expression == 'sad':
            pygame.draw.ellipse(surface, PALETTE['eye_blue'], (cx - 8, eye_y + 2, 6, 4))
            pygame.draw.ellipse(surface, PALETTE['eye_blue'], (cx + 2, eye_y + 2, 6, 4))
            pygame.draw.line(surface, darken_color(skin, 40), (cx - 10, eye_y), (cx - 4, eye_y + 2), 2)
            pygame.draw.line(surface, darken_color(skin, 40), (cx + 10, eye_y), (cx + 4, eye_y + 2), 2)
        elif expression == 'surprised':
            pygame.draw.ellipse(surface, PALETTE['eye_blue'], (cx - 9, eye_y - 1, 8, 7))
            pygame.draw.ellipse(surface, PALETTE['eye_blue'], (cx + 1, eye_y - 1, 8, 7))
            pygame.draw.circle(surface, (0, 0, 0), (cx - 5, eye_y + 2), 3)
            pygame.draw.circle(surface, (0, 0, 0), (cx + 5, eye_y + 2), 3)

        # Nose
        pygame.draw.line(surface, darken_color(skin, 20), (cx, cy - 8), (cx, cy - 2), 2)

        # Mouth based on expression
        mouth_y = cy + 2
        if expression == 'neutral':
            pygame.draw.line(surface, darken_color(skin, 40), (cx - 4, mouth_y), (cx + 4, mouth_y), 2)
        elif expression == 'happy':
            pygame.draw.arc(surface, darken_color(skin, 50), (cx - 5, mouth_y - 3, 10, 8), 0, 3.14, 2)
        elif expression == 'angry':
            pygame.draw.arc(surface, darken_color(skin, 50), (cx - 4, mouth_y, 8, 4), 3.14, 6.28, 2)
        elif expression == 'sad':
            pygame.draw.arc(surface, darken_color(skin, 50), (cx - 4, mouth_y + 2, 8, 4), 3.14, 6.28, 2)
        elif expression == 'surprised':
            pygame.draw.ellipse(surface, darken_color(skin, 50), (cx - 3, mouth_y, 6, 6))

        # Scar (character detail)
        pygame.draw.line(surface, darken_color(skin, 30), (cx + 8, cy - 16), (cx + 10, cy - 6), 2)

        return surface


class MagePortrait(PortraitSprite):
    """Portrait for mage class."""

    def __init__(self):
        super().__init__('mage', 'party')

    def _generate_portrait(self, expression: str) -> pygame.Surface:
        surface = create_surface(self.base_size)
        cx, cy = 32, 36

        skin = PALETTE['skin_pale']
        robe = PALETTE['cloth_blue']

        # Robe collar/shoulders
        pygame.draw.ellipse(surface, robe, (cx - 26, cy + 6, 52, 26))
        pygame.draw.ellipse(surface, darken_color(robe, 30), (cx - 26, cy + 6, 52, 26), 2)

        # Neck
        pygame.draw.rect(surface, skin, (cx - 6, cy - 2, 12, 12))

        # Face
        pygame.draw.ellipse(surface, skin, (cx - 12, cy - 22, 24, 28))

        # Grey hair with slight widow's peak
        pygame.draw.ellipse(surface, PALETTE['hair_grey'], (cx - 10, cy - 24, 20, 14))
        pygame.draw.polygon(surface, PALETTE['hair_grey'], [
            (cx - 6, cy - 18), (cx, cy - 24), (cx + 6, cy - 18)
        ])

        # Mystical purple eyes
        eye_y = cy - 10
        if expression == 'neutral':
            pygame.draw.ellipse(surface, PALETTE['eye_purple'], (cx - 7, eye_y, 5, 5))
            pygame.draw.ellipse(surface, PALETTE['eye_purple'], (cx + 2, eye_y, 5, 5))
        elif expression == 'happy':
            pygame.draw.arc(surface, PALETTE['eye_purple'], (cx - 8, eye_y, 6, 5), 3.14, 6.28, 2)
            pygame.draw.arc(surface, PALETTE['eye_purple'], (cx + 2, eye_y, 6, 5), 3.14, 6.28, 2)
        elif expression == 'angry':
            pygame.draw.ellipse(surface, PALETTE['eye_purple'], (cx - 7, eye_y + 1, 5, 4))
            pygame.draw.ellipse(surface, PALETTE['eye_purple'], (cx + 2, eye_y + 1, 5, 4))
        elif expression == 'sad':
            pygame.draw.ellipse(surface, PALETTE['eye_purple'], (cx - 7, eye_y + 1, 5, 4))
            pygame.draw.ellipse(surface, PALETTE['eye_purple'], (cx + 2, eye_y + 1, 5, 4))
        elif expression == 'surprised':
            pygame.draw.ellipse(surface, PALETTE['eye_purple'], (cx - 8, eye_y - 1, 6, 6))
            pygame.draw.ellipse(surface, PALETTE['eye_purple'], (cx + 2, eye_y - 1, 6, 6))

        # Nose
        pygame.draw.line(surface, darken_color(skin, 15), (cx, cy - 6), (cx, cy), 1)

        # Mouth
        mouth_y = cy + 4
        if expression == 'happy':
            pygame.draw.arc(surface, (0, 0, 0), (cx - 4, mouth_y - 2, 8, 6), 0, 3.14, 1)
        elif expression == 'surprised':
            pygame.draw.ellipse(surface, (0, 0, 0), (cx - 2, mouth_y, 4, 4))
        else:
            pygame.draw.line(surface, (0, 0, 0), (cx - 3, mouth_y), (cx + 3, mouth_y), 1)

        # Arcane glow around eyes (subtle)
        pygame.draw.circle(surface, (*PALETTE['void_glow'][:3], 40), (cx - 5, eye_y + 2), 8)
        pygame.draw.circle(surface, (*PALETTE['void_glow'][:3], 40), (cx + 4, eye_y + 2), 8)

        return surface


class RoguePortrait(PortraitSprite):
    """Portrait for rogue class."""

    def __init__(self):
        super().__init__('rogue', 'party')

    def _generate_portrait(self, expression: str) -> pygame.Surface:
        surface = create_surface(self.base_size)
        cx, cy = 32, 36

        skin = PALETTE['skin_tan']
        cloak = PALETTE['cloth_brown']

        # Hood/cloak
        pygame.draw.ellipse(surface, cloak, (cx - 24, cy + 4, 48, 24))
        pygame.draw.ellipse(surface, cloak, (cx - 16, cy - 20, 32, 28))

        # Face in shadow
        pygame.draw.ellipse(surface, darken_color(skin, 20), (cx - 10, cy - 16, 20, 24))

        # Mask over lower face
        pygame.draw.rect(surface, (30, 30, 35), (cx - 8, cy + 2, 16, 8))

        # Sharp green eyes
        eye_y = cy - 8
        if expression in ['neutral', 'angry']:
            pygame.draw.ellipse(surface, PALETTE['eye_green'], (cx - 7, eye_y, 5, 4))
            pygame.draw.ellipse(surface, PALETTE['eye_green'], (cx + 2, eye_y, 5, 4))
            pygame.draw.ellipse(surface, (0, 0, 0), (cx - 5, eye_y + 1, 2, 2))
            pygame.draw.ellipse(surface, (0, 0, 0), (cx + 4, eye_y + 1, 2, 2))
        elif expression == 'happy':
            pygame.draw.arc(surface, PALETTE['eye_green'], (cx - 8, eye_y - 1, 6, 5), 3.14, 6.28, 2)
            pygame.draw.arc(surface, PALETTE['eye_green'], (cx + 2, eye_y - 1, 6, 5), 3.14, 6.28, 2)
        elif expression == 'surprised':
            pygame.draw.ellipse(surface, PALETTE['eye_green'], (cx - 8, eye_y - 1, 6, 6))
            pygame.draw.ellipse(surface, PALETTE['eye_green'], (cx + 2, eye_y - 1, 6, 6))
        else:
            pygame.draw.ellipse(surface, PALETTE['eye_green'], (cx - 7, eye_y + 1, 5, 3))
            pygame.draw.ellipse(surface, PALETTE['eye_green'], (cx + 2, eye_y + 1, 5, 3))

        # Eyebrows
        if expression == 'angry':
            pygame.draw.line(surface, (0, 0, 0), (cx - 8, eye_y - 3), (cx - 3, eye_y - 1), 2)
            pygame.draw.line(surface, (0, 0, 0), (cx + 8, eye_y - 3), (cx + 3, eye_y - 1), 2)

        return surface


class ClericPortrait(PortraitSprite):
    """Portrait for cleric class."""

    def __init__(self):
        super().__init__('cleric', 'party')

    def _generate_portrait(self, expression: str) -> pygame.Surface:
        surface = create_surface(self.base_size)
        cx, cy = 32, 36

        skin = PALETTE['skin_light']
        robe = PALETTE['cloth_white']
        gold = PALETTE['gold_base']

        # White robe shoulders with gold trim
        pygame.draw.ellipse(surface, robe, (cx - 26, cy + 6, 52, 24))
        pygame.draw.rect(surface, gold, (cx - 24, cy + 16, 48, 3))

        # Neck
        pygame.draw.rect(surface, skin, (cx - 6, cy - 2, 12, 12))

        # Face
        pygame.draw.ellipse(surface, skin, (cx - 12, cy - 22, 24, 28))

        # Light brown hair
        pygame.draw.ellipse(surface, PALETTE['hair_brown'], (cx - 10, cy - 24, 20, 14))

        # Holy headband with gem
        pygame.draw.rect(surface, gold, (cx - 10, cy - 18, 20, 3))
        pygame.draw.circle(surface, PALETTE['holy_gold'], (cx, cy - 17), 3)

        # Kind blue eyes
        eye_y = cy - 10
        if expression == 'neutral':
            pygame.draw.ellipse(surface, PALETTE['eye_blue'], (cx - 7, eye_y, 5, 5))
            pygame.draw.ellipse(surface, PALETTE['eye_blue'], (cx + 2, eye_y, 5, 5))
        elif expression == 'happy':
            pygame.draw.arc(surface, PALETTE['eye_blue'], (cx - 8, eye_y, 6, 5), 3.14, 6.28, 2)
            pygame.draw.arc(surface, PALETTE['eye_blue'], (cx + 2, eye_y, 6, 5), 3.14, 6.28, 2)
        elif expression == 'sad':
            pygame.draw.ellipse(surface, PALETTE['eye_blue'], (cx - 7, eye_y + 1, 5, 4))
            pygame.draw.ellipse(surface, PALETTE['eye_blue'], (cx + 2, eye_y + 1, 5, 4))
            pygame.draw.line(surface, darken_color(skin, 30), (cx - 9, eye_y - 1), (cx - 4, eye_y + 1), 1)
            pygame.draw.line(surface, darken_color(skin, 30), (cx + 9, eye_y - 1), (cx + 4, eye_y + 1), 1)
        else:
            pygame.draw.ellipse(surface, PALETTE['eye_blue'], (cx - 7, eye_y, 5, 5))
            pygame.draw.ellipse(surface, PALETTE['eye_blue'], (cx + 2, eye_y, 5, 5))

        # Nose
        pygame.draw.line(surface, darken_color(skin, 15), (cx, cy - 6), (cx, cy), 1)

        # Serene smile
        mouth_y = cy + 4
        if expression in ['neutral', 'happy']:
            pygame.draw.arc(surface, (0, 0, 0), (cx - 4, mouth_y - 2, 8, 5), 0, 3.14, 1)
        elif expression == 'sad':
            pygame.draw.arc(surface, (0, 0, 0), (cx - 4, mouth_y + 1, 8, 4), 3.14, 6.28, 1)
        else:
            pygame.draw.line(surface, (0, 0, 0), (cx - 3, mouth_y), (cx + 3, mouth_y), 1)

        return surface


class BossPortrait(PortraitSprite):
    """Base portrait for boss characters."""

    def __init__(self, name: str):
        super().__init__(name, 'boss')


class AncientGuardianPortrait(BossPortrait):
    """Portrait for the Ancient Guardian boss."""

    def __init__(self):
        super().__init__('boss')

    def _generate_portrait(self, expression: str) -> pygame.Surface:
        surface = create_surface(self.base_size)
        cx, cy = 32, 32

        metal = PALETTE['steel_base']
        gold = PALETTE['gold_base']
        rune = PALETTE['holy_gold']

        # Armored helmet/head
        pygame.draw.ellipse(surface, metal, (cx - 20, cy - 16, 40, 40))
        pygame.draw.ellipse(surface, darken_color(metal, 30), (cx - 20, cy - 16, 40, 40), 3)

        # Ornate details
        pygame.draw.rect(surface, gold, (cx - 16, cy - 8, 32, 4))

        # Central glowing eye
        pygame.draw.rect(surface, (20, 20, 25), (cx - 10, cy - 2, 20, 10))

        if expression in ['neutral', 'happy']:
            pygame.draw.ellipse(surface, rune, (cx - 6, cy, 12, 6))
            pygame.draw.ellipse(surface, (255, 255, 255), (cx - 2, cy + 1, 4, 4))
        elif expression == 'angry':
            pygame.draw.ellipse(surface, PALETTE['fire_orange'], (cx - 6, cy, 12, 6))
            pygame.draw.ellipse(surface, PALETTE['fire_yellow'], (cx - 2, cy + 1, 4, 4))
        else:
            pygame.draw.ellipse(surface, rune, (cx - 5, cy + 1, 10, 4))

        # Runes around helmet
        for i in range(3):
            rx = cx - 14 + i * 12
            pygame.draw.circle(surface, rune, (rx, cy + 16), 3, 1)

        return surface


class NPCPortrait(PortraitSprite):
    """Base portrait for NPC characters."""

    def __init__(self, name: str):
        super().__init__(name, 'npc')


class OldGuidePortrait(NPCPortrait):
    """Portrait for the tutorial guide NPC."""

    def __init__(self):
        super().__init__('old_guide')

    def _generate_portrait(self, expression: str) -> pygame.Surface:
        surface = create_surface(self.base_size)
        cx, cy = 32, 34

        skin = PALETTE['skin_light']
        robe = PALETTE['cloth_brown']

        # Robe collar
        pygame.draw.ellipse(surface, robe, (cx - 24, cy + 8, 48, 22))

        # Neck
        pygame.draw.rect(surface, skin, (cx - 5, cy, 10, 12))

        # Elderly face with wrinkles
        pygame.draw.ellipse(surface, skin, (cx - 12, cy - 20, 24, 26))

        # Wrinkle lines
        pygame.draw.line(surface, darken_color(skin, 25), (cx - 10, cy - 8), (cx - 6, cy - 6), 1)
        pygame.draw.line(surface, darken_color(skin, 25), (cx + 10, cy - 8), (cx + 6, cy - 6), 1)

        # Bald head
        pygame.draw.ellipse(surface, skin, (cx - 10, cy - 22, 20, 14))

        # Kind blue eyes
        eye_y = cy - 8
        pygame.draw.ellipse(surface, PALETTE['eye_blue'], (cx - 7, eye_y, 5, 4))
        pygame.draw.ellipse(surface, PALETTE['eye_blue'], (cx + 2, eye_y, 5, 4))

        # Long white beard
        pygame.draw.ellipse(surface, PALETTE['hair_white'], (cx - 10, cy, 20, 24))
        pygame.draw.ellipse(surface, PALETTE['hair_grey'], (cx - 6, cy + 6, 12, 14))

        # Nose
        pygame.draw.line(surface, darken_color(skin, 20), (cx, cy - 4), (cx, cy + 2), 2)

        # Gentle smile under beard
        if expression == 'happy':
            pygame.draw.arc(surface, darken_color(skin, 40), (cx - 4, cy - 1, 8, 4), 0, 3.14, 1)

        return surface


# Factory functions
def get_party_portrait(name: str) -> Optional[PortraitSprite]:
    """Get a party member portrait generator by name."""
    portraits = {
        'warrior': WarriorPortrait,
        'mage': MagePortrait,
        'rogue': RoguePortrait,
        'cleric': ClericPortrait,
    }

    portrait_class = portraits.get(name.lower())
    if portrait_class:
        return portrait_class()
    return None


def get_boss_portrait(name: str) -> Optional[PortraitSprite]:
    """Get a boss portrait generator by name."""
    portraits = {
        'boss': AncientGuardianPortrait,
    }

    portrait_class = portraits.get(name.lower())
    if portrait_class:
        return portrait_class()
    return None


def get_npc_portrait(name: str) -> Optional[PortraitSprite]:
    """Get an NPC portrait generator by name."""
    portraits = {
        'old_guide': OldGuidePortrait,
    }

    portrait_class = portraits.get(name.lower())
    if portrait_class:
        return portrait_class()
    return None


PARTY_PORTRAITS = ['warrior', 'mage', 'rogue', 'cleric']
BOSS_PORTRAITS = ['boss']
NPC_PORTRAITS = ['old_guide']
