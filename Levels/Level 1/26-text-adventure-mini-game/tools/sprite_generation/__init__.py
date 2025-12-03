"""
Sprite Generation Package for Text Adventure Mini Game

This package provides comprehensive sprite generation tools for creating
high-detail 64x64 sprites scaled to 32x32 for game use.

Modules:
    - palette: Expanded fantasy color palette (~130 colors)
    - utils: Drawing utilities and helper functions
    - base_sprite: Base sprite class with scaling and animation support
    - enemy_sprites: Enemy sprite generators
    - npc_sprites: NPC sprite generators
    - party_sprites: Party member sprite generators
    - boss_sprites: Boss sprites with special effects
    - portrait_sprites: Portrait generation for dialogue
    - effects: Auras, particles, and overlays
"""

from .palette import PALETTE
from .utils import (
    create_surface,
    scale_to_game_size,
    draw_pixel,
    draw_thick_pixel,
    lerp_color,
    darken_color,
    lighten_color,
    add_outline,
    add_shadow,
)
from .base_sprite import BaseSprite

# Sprite generators
from .enemy_sprites import get_enemy_sprite, BASIC_ENEMIES
from .enemy_sprites_advanced import get_advanced_enemy_sprite, ADVANCED_ENEMIES
from .boss_sprites import get_boss_sprite, BOSS_SPRITES
from .npc_sprites import get_npc_sprite, NPC_SPRITES
from .party_sprites import get_party_sprite, PARTY_SPRITES
from .portrait_sprites import (
    get_party_portrait, get_boss_portrait, get_npc_portrait,
    PARTY_PORTRAITS, BOSS_PORTRAITS, NPC_PORTRAITS
)

# Effects
from .effects import create_aura, create_particle_effect

__version__ = "1.0.0"
__all__ = [
    # Palette
    "PALETTE",
    # Base
    "BaseSprite",
    # Utils
    "create_surface",
    "scale_to_game_size",
    "draw_pixel",
    "draw_thick_pixel",
    "lerp_color",
    "darken_color",
    "lighten_color",
    "add_outline",
    "add_shadow",
    # Sprite factories
    "get_enemy_sprite",
    "get_advanced_enemy_sprite",
    "get_boss_sprite",
    "get_npc_sprite",
    "get_party_sprite",
    "get_party_portrait",
    "get_boss_portrait",
    "get_npc_portrait",
    # Sprite lists
    "BASIC_ENEMIES",
    "ADVANCED_ENEMIES",
    "BOSS_SPRITES",
    "NPC_SPRITES",
    "PARTY_SPRITES",
    "PARTY_PORTRAITS",
    "BOSS_PORTRAITS",
    "NPC_PORTRAITS",
    # Effects
    "create_aura",
    "create_particle_effect",
]
