"""
NPC Sprite Generators

Contains sprite generators for all NPC types including:
- Quest givers and important NPCs
- Merchants and innkeepers
- Town-specific NPCs
"""

import pygame
import random
from typing import Optional, Dict

from .base_sprite import BaseSprite
from .utils import (
    create_surface, draw_pixel, draw_humanoid_base,
    draw_eyes, draw_hair, draw_clothing, draw_weapon, draw_accessory,
    darken_color, lighten_color
)
from .palette import PALETTE


class NPCSprite(BaseSprite):
    """Base class for NPC sprites."""

    def __init__(self, name: str):
        super().__init__(name, 'npc')


class OldGuideSprite(NPCSprite):
    """Tutorial NPC - elderly wise guide."""

    def __init__(self):
        super().__init__('npc_old_guide')

    def _generate_base_sprite(self) -> pygame.Surface:
        surface = create_surface(self.base_size)
        cx = 32

        skin = PALETTE['skin_light']
        robe = PALETTE['cloth_brown']

        # Brown traveling robes
        pygame.draw.polygon(surface, robe, [
            (cx - 12, 22), (cx + 12, 22),
            (cx + 16, 58), (cx - 16, 58)
        ])
        pygame.draw.polygon(surface, darken_color(robe, 30), [
            (cx - 12, 22), (cx + 12, 22),
            (cx + 16, 58), (cx - 16, 58)
        ], 2)

        # Elderly face
        pygame.draw.ellipse(surface, skin, (cx - 8, 8, 16, 16))

        # Kind eyes
        pygame.draw.ellipse(surface, PALETTE['eye_blue'], (cx - 5, 14, 4, 3))
        pygame.draw.ellipse(surface, PALETTE['eye_blue'], (cx + 1, 14, 4, 3))
        draw_pixel(surface, (0, 0, 0), (cx - 3, 15))
        draw_pixel(surface, (0, 0, 0), (cx + 3, 15))

        # Wrinkles
        pygame.draw.line(surface, darken_color(skin, 30), (cx - 6, 12), (cx - 4, 13), 1)
        pygame.draw.line(surface, darken_color(skin, 30), (cx + 4, 13), (cx + 6, 12), 1)

        # Long white beard
        pygame.draw.ellipse(surface, PALETTE['hair_white'], (cx - 6, 18, 12, 20))
        pygame.draw.ellipse(surface, PALETTE['hair_grey'], (cx - 4, 22, 8, 14))

        # Bald head
        pygame.draw.ellipse(surface, skin, (cx - 7, 6, 14, 10))

        # Arms in robes
        pygame.draw.ellipse(surface, robe, (cx - 18, 28, 10, 16))
        pygame.draw.ellipse(surface, robe, (cx + 8, 28, 10, 16))

        # Walking staff with crystal
        pygame.draw.rect(surface, PALETTE['bark_base'], (cx + 18, 10, 4, 48))
        pygame.draw.circle(surface, PALETTE['ice_light'], (cx + 20, 8), 5)
        pygame.draw.circle(surface, (255, 255, 255), (cx + 18, 6), 2)

        return surface


class BlacksmithSprite(NPCSprite):
    """Marcus the Blacksmith."""

    def __init__(self):
        super().__init__('npc_blacksmith')

    def _generate_base_sprite(self) -> pygame.Surface:
        surface = create_surface(self.base_size)
        cx = 32

        skin = PALETTE['skin_tan']
        skin_dark = darken_color(skin, 30)
        apron = PALETTE['leather_base']

        # Muscular body
        pygame.draw.ellipse(surface, skin, (cx - 14, 22, 28, 28))

        # Leather apron
        pygame.draw.polygon(surface, apron, [
            (cx - 10, 26), (cx + 10, 26),
            (cx + 12, 54), (cx - 12, 54)
        ])
        pygame.draw.polygon(surface, darken_color(apron, 30), [
            (cx - 10, 26), (cx + 10, 26),
            (cx + 12, 54), (cx - 12, 54)
        ], 2)

        # Bald head
        pygame.draw.ellipse(surface, skin, (cx - 8, 8, 16, 16))

        # Thick beard
        pygame.draw.ellipse(surface, PALETTE['hair_brown'], (cx - 6, 18, 12, 10))

        # Eyes
        pygame.draw.ellipse(surface, PALETTE['eye_brown'], (cx - 5, 14, 4, 3))
        pygame.draw.ellipse(surface, PALETTE['eye_brown'], (cx + 1, 14, 4, 3))

        # Soot marks
        for _ in range(4):
            sx = cx + random.randint(-12, 12)
            sy = random.randint(14, 48)
            pygame.draw.circle(surface, (40, 40, 45), (sx, sy), random.randint(1, 2))

        # Muscular arms with burn scars
        pygame.draw.ellipse(surface, skin, (cx - 22, 24, 12, 20))
        pygame.draw.ellipse(surface, skin, (cx + 10, 24, 12, 20))
        pygame.draw.line(surface, (180, 100, 80), (cx - 18, 32), (cx - 14, 38), 2)
        pygame.draw.line(surface, (180, 100, 80), (cx + 14, 30), (cx + 18, 36), 2)

        # Hammer in hand
        pygame.draw.rect(surface, PALETTE['bark_dark'], (cx + 18, 36, 4, 16))
        pygame.draw.rect(surface, PALETTE['iron_base'], (cx + 14, 32, 12, 8))

        return surface


class MerchantSprite(NPCSprite):
    """Generic merchant NPC."""

    def __init__(self):
        super().__init__('npc_merchant')

    def _generate_base_sprite(self) -> pygame.Surface:
        surface = create_surface(self.base_size)
        cx = 32

        skin = PALETTE['skin_medium']
        cloth = PALETTE['cloth_green']

        # Body with merchant clothes
        pygame.draw.ellipse(surface, cloth, (cx - 12, 24, 24, 26))

        # Head
        pygame.draw.ellipse(surface, skin, (cx - 8, 10, 16, 16))

        # Friendly smile
        pygame.draw.arc(surface, (0, 0, 0), (cx - 4, 20, 8, 4), 0, 3.14, 1)

        # Eyes
        pygame.draw.ellipse(surface, PALETTE['eye_brown'], (cx - 5, 16, 4, 3))
        pygame.draw.ellipse(surface, PALETTE['eye_brown'], (cx + 1, 16, 4, 3))

        # Hat with feather
        pygame.draw.ellipse(surface, PALETTE['cloth_brown'], (cx - 10, 6, 20, 8))
        pygame.draw.ellipse(surface, darken_color(PALETTE['cloth_brown'], 20),
                          (cx - 6, 2, 12, 8))
        # Feather
        pygame.draw.line(surface, PALETTE['cloth_red'], (cx + 4, 4), (cx + 12, -4), 2)

        # Large backpack with wares
        pygame.draw.ellipse(surface, PALETTE['leather_base'], (cx - 20, 20, 14, 24))
        pygame.draw.rect(surface, PALETTE['gold_shadow'], (cx - 18, 26, 4, 4))
        pygame.draw.rect(surface, PALETTE['steel_shadow'], (cx - 18, 32, 4, 4))

        # Arms
        pygame.draw.ellipse(surface, cloth, (cx - 18, 28, 8, 14))
        pygame.draw.ellipse(surface, cloth, (cx + 10, 28, 8, 14))

        return surface


class GuardSprite(NPCSprite):
    """Town guard NPC."""

    def __init__(self):
        super().__init__('npc_guard')

    def _generate_base_sprite(self) -> pygame.Surface:
        surface = create_surface(self.base_size)
        cx = 32

        skin = PALETTE['skin_medium']
        armor = PALETTE['steel_base']

        # Armored body
        pygame.draw.rect(surface, armor, (cx - 12, 22, 24, 26))
        pygame.draw.rect(surface, darken_color(armor, 30), (cx - 12, 22, 24, 26), 2)

        # Head with helmet
        pygame.draw.ellipse(surface, armor, (cx - 9, 6, 18, 18))
        pygame.draw.rect(surface, (30, 30, 35), (cx - 6, 14, 12, 3))  # Visor

        # Face visible
        pygame.draw.ellipse(surface, skin, (cx - 5, 16, 10, 8))

        # Stern expression
        pygame.draw.line(surface, (0, 0, 0), (cx - 3, 18), (cx - 1, 18), 1)
        pygame.draw.line(surface, (0, 0, 0), (cx + 1, 18), (cx + 3, 18), 1)

        # Spear
        pygame.draw.rect(surface, PALETTE['bark_base'], (cx + 16, 4, 3, 52))
        pygame.draw.polygon(surface, PALETTE['steel_highlight'], [
            (cx + 14, 4), (cx + 21, 4), (cx + 17, -6)
        ])

        # Shield on arm
        pygame.draw.ellipse(surface, armor, (cx - 22, 28, 12, 16))
        pygame.draw.ellipse(surface, PALETTE['cloth_red'], (cx - 20, 32, 8, 8))

        return surface


class MageNPCSprite(NPCSprite):
    """Mage/wizard NPC."""

    def __init__(self):
        super().__init__('npc_mage')

    def _generate_base_sprite(self) -> pygame.Surface:
        surface = create_surface(self.base_size)
        cx = 32

        skin = PALETTE['skin_pale']
        robe = PALETTE['cloth_blue']

        # Blue robes
        pygame.draw.polygon(surface, robe, [
            (cx - 12, 20), (cx + 12, 20),
            (cx + 16, 58), (cx - 16, 58)
        ])

        # Hood
        pygame.draw.ellipse(surface, robe, (cx - 10, 4, 20, 18))

        # Face
        pygame.draw.ellipse(surface, skin, (cx - 6, 10, 12, 12))

        # Wise eyes
        pygame.draw.ellipse(surface, PALETTE['eye_purple'], (cx - 4, 14, 3, 3))
        pygame.draw.ellipse(surface, PALETTE['eye_purple'], (cx + 1, 14, 3, 3))

        # Grey beard
        pygame.draw.ellipse(surface, PALETTE['hair_grey'], (cx - 4, 18, 8, 8))

        # Staff with orb
        pygame.draw.rect(surface, PALETTE['bark_dark'], (cx + 16, 8, 4, 48))
        pygame.draw.circle(surface, PALETTE['void_glow'], (cx + 18, 6), 5)

        # Glowing hands
        pygame.draw.ellipse(surface, skin, (cx - 16, 34, 6, 8))
        pygame.draw.ellipse(surface, skin, (cx + 10, 34, 6, 8))
        pygame.draw.circle(surface, (*PALETTE['void_glow'][:3], 100), (cx - 13, 38), 4)

        return surface


class PriestSprite(NPCSprite):
    """Priest/cleric NPC."""

    def __init__(self):
        super().__init__('npc_priest')

    def _generate_base_sprite(self) -> pygame.Surface:
        surface = create_surface(self.base_size)
        cx = 32

        skin = PALETTE['skin_light']
        robe = PALETTE['cloth_white']

        # White robes
        pygame.draw.polygon(surface, robe, [
            (cx - 12, 20), (cx + 12, 20),
            (cx + 14, 58), (cx - 14, 58)
        ])
        pygame.draw.polygon(surface, darken_color(robe, 20), [
            (cx - 12, 20), (cx + 12, 20),
            (cx + 14, 58), (cx - 14, 58)
        ], 2)

        # Gold trim
        pygame.draw.rect(surface, PALETTE['gold_base'], (cx - 10, 24, 20, 3))

        # Head
        pygame.draw.ellipse(surface, skin, (cx - 7, 8, 14, 14))

        # Serene expression
        pygame.draw.ellipse(surface, PALETTE['eye_blue'], (cx - 4, 14, 3, 2))
        pygame.draw.ellipse(surface, PALETTE['eye_blue'], (cx + 1, 14, 3, 2))
        pygame.draw.arc(surface, (0, 0, 0), (cx - 3, 18, 6, 3), 0, 3.14, 1)

        # Sun symbol headpiece
        pygame.draw.circle(surface, PALETTE['gold_base'], (cx, 4), 5)
        for i in range(8):
            angle = (i / 8) * 6.28
            end_x = cx + int(5 * 1.5 * (1 if i % 2 == 0 else 0.7) *
                           (1 if abs(angle - 3.14) > 1 else 0.5) *
                           (0.8 if i < 4 else 1) + 0.5)
            # Simplified rays
            pygame.draw.line(surface, PALETTE['gold_shadow'],
                           (cx, 4), (cx + (i - 4) * 2, -2), 1)

        # Staff
        pygame.draw.rect(surface, PALETTE['gold_shadow'], (cx + 14, 12, 3, 44))
        pygame.draw.circle(surface, PALETTE['holy_gold'], (cx + 15, 10), 4)

        return surface


class VillagerSprite(NPCSprite):
    """Generic villager NPC."""

    def __init__(self, variant: str = 'default'):
        super().__init__(f'npc_villager_{variant}' if variant != 'default' else 'npc_villager')
        self.variant = variant

    def _generate_base_sprite(self) -> pygame.Surface:
        surface = create_surface(self.base_size)
        cx = 32

        skin = PALETTE['skin_medium']
        cloth = PALETTE['cloth_brown']

        # Simple clothes
        pygame.draw.ellipse(surface, cloth, (cx - 10, 24, 20, 24))

        # Head
        pygame.draw.ellipse(surface, skin, (cx - 7, 10, 14, 14))

        # Simple face
        draw_pixel(surface, PALETTE['eye_brown'], (cx - 3, 16))
        draw_pixel(surface, PALETTE['eye_brown'], (cx + 3, 16))
        draw_pixel(surface, darken_color(skin, 20), (cx, 18))

        # Hair
        pygame.draw.ellipse(surface, PALETTE['hair_brown'], (cx - 6, 8, 12, 8))

        # Arms
        pygame.draw.ellipse(surface, cloth, (cx - 16, 28, 8, 12))
        pygame.draw.ellipse(surface, cloth, (cx + 8, 28, 8, 12))

        # Legs
        pygame.draw.rect(surface, darken_color(cloth, 20), (cx - 6, 46, 5, 12))
        pygame.draw.rect(surface, darken_color(cloth, 20), (cx + 1, 46, 5, 12))

        return surface


class ElderSprite(NPCSprite):
    """Village elder NPC."""

    def __init__(self):
        super().__init__('npc_elder')

    def _generate_base_sprite(self) -> pygame.Surface:
        surface = create_surface(self.base_size)
        cx = 32

        skin = PALETTE['skin_light']
        robe = PALETTE['cloth_purple']

        # Distinguished robes
        pygame.draw.polygon(surface, robe, [
            (cx - 12, 22), (cx + 12, 22),
            (cx + 14, 58), (cx - 14, 58)
        ])

        # Elderly face
        pygame.draw.ellipse(surface, skin, (cx - 7, 10, 14, 14))

        # Wise eyes with wrinkles
        pygame.draw.ellipse(surface, PALETTE['eye_grey'], (cx - 4, 16, 3, 2))
        pygame.draw.ellipse(surface, PALETTE['eye_grey'], (cx + 1, 16, 3, 2))

        # White hair
        pygame.draw.ellipse(surface, PALETTE['hair_white'], (cx - 6, 6, 12, 10))

        # White beard
        pygame.draw.ellipse(surface, PALETTE['hair_white'], (cx - 5, 20, 10, 12))

        # Walking cane
        pygame.draw.rect(surface, PALETTE['bark_dark'], (cx + 14, 20, 3, 38))
        pygame.draw.ellipse(surface, PALETTE['bark_base'], (cx + 12, 16, 8, 6))

        return surface


class NobleSprite(NPCSprite):
    """Noble/aristocrat NPC."""

    def __init__(self):
        super().__init__('npc_noble')

    def _generate_base_sprite(self) -> pygame.Surface:
        surface = create_surface(self.base_size)
        cx = 32

        skin = PALETTE['skin_pale']
        cloth = PALETTE['cloth_purple']

        # Fancy clothes
        pygame.draw.ellipse(surface, cloth, (cx - 12, 24, 24, 26))
        pygame.draw.rect(surface, PALETTE['gold_base'], (cx - 10, 28, 20, 3))

        # Head
        pygame.draw.ellipse(surface, skin, (cx - 7, 10, 14, 14))

        # Smug expression
        pygame.draw.ellipse(surface, PALETTE['eye_blue'], (cx - 4, 16, 3, 2))
        pygame.draw.ellipse(surface, PALETTE['eye_blue'], (cx + 1, 16, 3, 2))
        pygame.draw.arc(surface, (0, 0, 0), (cx - 3, 20, 6, 2), 3.14, 6.28, 1)

        # Fancy hair
        pygame.draw.ellipse(surface, PALETTE['hair_black'], (cx - 6, 6, 12, 10))

        # Jeweled rings on hands
        pygame.draw.ellipse(surface, skin, (cx - 16, 36, 6, 8))
        pygame.draw.ellipse(surface, skin, (cx + 10, 36, 6, 8))
        pygame.draw.circle(surface, PALETTE['gold_base'], (cx - 13, 40), 2)
        pygame.draw.circle(surface, PALETTE['eye_red'], (cx - 13, 40), 1)

        return surface


# Factory function
def get_npc_sprite(name: str) -> Optional[NPCSprite]:
    """Get an NPC sprite generator by name."""
    sprites = {
        'npc_old_guide': OldGuideSprite,
        'npc_blacksmith': BlacksmithSprite,
        'npc_merchant': MerchantSprite,
        'npc_guard': GuardSprite,
        'npc_mage': MageNPCSprite,
        'npc_priest': PriestSprite,
        'npc_villager': VillagerSprite,
        'npc_elder': ElderSprite,
        'npc_noble': NobleSprite,
    }

    sprite_class = sprites.get(name.lower())
    if sprite_class:
        return sprite_class()
    return None


NPC_SPRITES = [
    'npc_old_guide', 'npc_blacksmith', 'npc_merchant', 'npc_guard',
    'npc_mage', 'npc_priest', 'npc_villager', 'npc_elder', 'npc_noble'
]
