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

__version__ = "1.0.0"
__all__ = [
    "PALETTE",
    "BaseSprite",
    "create_surface",
    "scale_to_game_size",
    "draw_pixel",
    "draw_thick_pixel",
    "lerp_color",
    "darken_color",
    "lighten_color",
    "add_outline",
    "add_shadow",
]
