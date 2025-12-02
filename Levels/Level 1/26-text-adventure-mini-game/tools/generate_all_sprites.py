#!/usr/bin/env python3
"""
Comprehensive sprite generator for the text adventure game.
Generates all missing sprites including enemies, status icons, NPCs, tiles, and more.
"""

import os
import random
import math
from typing import Tuple, Optional

import pygame

# Initialize pygame
pygame.init()

# Setup paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPRITE_DIR = os.path.join(BASE_DIR, "assets", "sprites")
TILESET_DIR = os.path.join(BASE_DIR, "assets", "tilesets", "default")
PORTRAIT_DIR = os.path.join(BASE_DIR, "assets", "sprites", "portraits")

os.makedirs(SPRITE_DIR, exist_ok=True)
os.makedirs(TILESET_DIR, exist_ok=True)
os.makedirs(PORTRAIT_DIR, exist_ok=True)


# ============================================
# PALETTE & UTILS
# ============================================

PALETTE = {
    # Nature
    "grass_base": (34, 139, 34),
    "grass_light": (60, 179, 113),
    "grass_dark": (0, 100, 0),
    "dirt": (101, 67, 33),
    "dirt_light": (139, 69, 19),
    "water": (65, 105, 225),
    "water_light": (135, 206, 250),
    "water_dark": (25, 25, 112),
    "sand": (194, 178, 128),
    "sand_light": (210, 195, 145),

    # Materials
    "stone_base": (112, 128, 144),
    "stone_light": (176, 196, 222),
    "stone_dark": (47, 79, 79),
    "wood": (139, 69, 19),
    "wood_light": (205, 133, 63),
    "wood_dark": (101, 67, 33),

    # Metals
    "steel": (192, 192, 192),
    "steel_light": (220, 220, 220),
    "steel_dark": (105, 105, 105),
    "gold": (255, 215, 0),
    "gold_light": (255, 255, 224),
    "gold_dark": (184, 134, 11),
    "bronze": (205, 127, 50),

    # Magic/Effects
    "fire": (255, 69, 0),
    "fire_light": (255, 140, 0),
    "fire_dark": (178, 34, 34),
    "ice": (224, 255, 255),
    "ice_dark": (100, 149, 237),
    "poison": (148, 0, 211),
    "poison_light": (180, 100, 255),
    "magic": (255, 0, 255),
    "holy": (255, 255, 240),
    "dark": (75, 0, 130),
    "lightning": (255, 255, 100),

    # Status effect colors
    "status_poison": (50, 180, 50),
    "status_burn": (255, 100, 0),
    "status_freeze": (100, 200, 255),
    "status_stun": (255, 255, 0),
    "status_sleep": (150, 150, 200),
    "status_confusion": (200, 100, 200),
    "status_bleed": (180, 0, 0),
    "status_regen": (0, 255, 100),
    "status_shield": (100, 150, 255),
    "status_attack_up": (255, 100, 100),
    "status_defense_up": (100, 100, 255),

    # Creatures
    "snake_green": (50, 120, 50),
    "snake_scales": (80, 160, 80),
    "snake_belly": (150, 180, 130),

    # UI
    "ui_bg": (20, 20, 30),
    "ui_border": (200, 200, 200),
}


def create_surface(size: Tuple[int, int] = (32, 32)) -> pygame.Surface:
    """Create a transparent surface."""
    return pygame.Surface(size, pygame.SRCALPHA)


def add_noise(surface: pygame.Surface, intensity: int = 20) -> None:
    """Add random noise texture to a surface."""
    width, height = surface.get_size()
    for x in range(width):
        for y in range(height):
            color = surface.get_at((x, y))
            if color.a == 0:
                continue
            noise = random.randint(-intensity, intensity)
            r = max(0, min(255, color.r + noise))
            g = max(0, min(255, color.g + noise))
            b = max(0, min(255, color.b + noise))
            surface.set_at((x, y), (r, g, b, color.a))


def draw_pixel(surface: pygame.Surface, color: Tuple, pos: Tuple[int, int]) -> None:
    """Draw a single pixel."""
    if 0 <= pos[0] < surface.get_width() and 0 <= pos[1] < surface.get_height():
        surface.set_at(pos, color)


def lerp_color(c1: Tuple, c2: Tuple, t: float) -> Tuple:
    """Linear interpolation between two colors."""
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def save_sprite(surface: pygame.Surface, name: str, directory: str = None) -> None:
    """Save a sprite to file."""
    if directory is None:
        directory = SPRITE_DIR
    path = os.path.join(directory, f"{name}.png")
    pygame.image.save(surface, path)
    print(f"  Created: {name}.png")


# ============================================
# ENEMY GENERATORS
# ============================================

def draw_snake() -> pygame.Surface:
    """Draw a snake/serpent enemy."""
    s = create_surface((32, 32))

    body_color = PALETTE["snake_green"]
    scales = PALETTE["snake_scales"]
    belly = PALETTE["snake_belly"]

    # Coiled body - draw from bottom up
    # Bottom coil
    pygame.draw.ellipse(s, body_color, (6, 20, 20, 10))
    pygame.draw.ellipse(s, scales, (8, 22, 16, 6))

    # Middle coil
    pygame.draw.ellipse(s, body_color, (4, 14, 18, 10))
    pygame.draw.ellipse(s, scales, (6, 16, 14, 6))

    # Top coil / neck
    pygame.draw.ellipse(s, body_color, (8, 8, 12, 10))

    # Head
    pygame.draw.ellipse(s, body_color, (16, 4, 12, 10))
    pygame.draw.ellipse(s, scales, (18, 6, 8, 6))

    # Eyes (red, menacing)
    draw_pixel(s, (255, 0, 0), (20, 7))
    draw_pixel(s, (255, 0, 0), (24, 7))

    # Tongue
    pygame.draw.line(s, (255, 50, 50), (26, 9), (30, 8), 1)
    pygame.draw.line(s, (255, 50, 50), (30, 8), (31, 6), 1)
    pygame.draw.line(s, (255, 50, 50), (30, 8), (31, 10), 1)

    # Scale details
    for i in range(3):
        x = 10 + i * 4
        draw_pixel(s, belly, (x, 24))
        draw_pixel(s, belly, (x + 1, 18))

    return s


def draw_earth_elemental() -> pygame.Surface:
    """Draw an earth elemental."""
    s = create_surface((32, 32))

    brown = (101, 67, 33)
    light = (139, 90, 43)
    dark = (60, 40, 20)
    rock = PALETTE["stone_base"]

    # Body - rocky humanoid shape
    pygame.draw.rect(s, brown, (10, 10, 12, 16), border_radius=3)

    # Rock texture
    pygame.draw.circle(s, rock, (12, 14), 3)
    pygame.draw.circle(s, rock, (19, 18), 4)
    pygame.draw.circle(s, dark, (14, 22), 2)

    # Head
    pygame.draw.circle(s, brown, (16, 8), 6)
    pygame.draw.circle(s, rock, (14, 6), 2)

    # Eyes (glowing)
    draw_pixel(s, (200, 150, 50), (14, 8))
    draw_pixel(s, (200, 150, 50), (18, 8))

    # Arms
    pygame.draw.rect(s, brown, (5, 12, 5, 10))
    pygame.draw.rect(s, brown, (22, 12, 5, 10))

    # Legs
    pygame.draw.rect(s, brown, (11, 26, 4, 6))
    pygame.draw.rect(s, brown, (17, 26, 4, 6))

    add_noise(s, 15)
    return s


# ============================================
# STATUS ICON GENERATORS (16x16)
# ============================================

def draw_status_poison() -> pygame.Surface:
    """Poison status - skull with green tint."""
    s = create_surface((16, 16))
    color = PALETTE["status_poison"]
    dark = (30, 100, 30)

    # Skull shape
    pygame.draw.circle(s, color, (8, 7), 5)
    pygame.draw.rect(s, color, (6, 10, 4, 4))

    # Eye sockets
    draw_pixel(s, dark, (6, 6))
    draw_pixel(s, dark, (10, 6))

    # Drip effect
    pygame.draw.line(s, color, (8, 14), (8, 15), 1)
    draw_pixel(s, dark, (8, 15))

    return s


def draw_status_burn() -> pygame.Surface:
    """Burn status - flame icon."""
    s = create_surface((16, 16))
    orange = PALETTE["status_burn"]
    yellow = (255, 200, 0)
    red = (200, 50, 0)

    # Flame shape
    pygame.draw.polygon(s, red, [(8, 2), (4, 10), (6, 8), (5, 14), (8, 10), (11, 14), (10, 8), (12, 10)])
    pygame.draw.polygon(s, orange, [(8, 4), (5, 10), (7, 8), (6, 12), (8, 9), (10, 12), (9, 8), (11, 10)])
    pygame.draw.polygon(s, yellow, [(8, 6), (6, 10), (8, 8), (10, 10)])

    return s


def draw_status_freeze() -> pygame.Surface:
    """Freeze/frozen status - snowflake."""
    s = create_surface((16, 16))
    color = PALETTE["status_freeze"]
    light = (200, 230, 255)

    # Snowflake - 6 arms
    center = (8, 8)
    for angle in range(0, 360, 60):
        rad = math.radians(angle)
        end_x = int(center[0] + 6 * math.cos(rad))
        end_y = int(center[1] + 6 * math.sin(rad))
        pygame.draw.line(s, color, center, (end_x, end_y), 1)

        # Branch details
        mid_x = int(center[0] + 3 * math.cos(rad))
        mid_y = int(center[1] + 3 * math.sin(rad))
        branch_rad = math.radians(angle + 45)
        branch_x = int(mid_x + 2 * math.cos(branch_rad))
        branch_y = int(mid_y + 2 * math.sin(branch_rad))
        pygame.draw.line(s, light, (mid_x, mid_y), (branch_x, branch_y), 1)

    # Center
    draw_pixel(s, light, center)

    return s


def draw_status_stun() -> pygame.Surface:
    """Stun status - stars/dizzy effect."""
    s = create_surface((16, 16))
    color = PALETTE["status_stun"]

    # Draw stars
    star_positions = [(4, 4), (12, 4), (8, 10)]
    for pos in star_positions:
        # 4-pointed star
        pygame.draw.line(s, color, (pos[0]-2, pos[1]), (pos[0]+2, pos[1]), 1)
        pygame.draw.line(s, color, (pos[0], pos[1]-2), (pos[0], pos[1]+2), 1)
        draw_pixel(s, (255, 255, 255), pos)

    return s


def draw_status_sleep() -> pygame.Surface:
    """Sleep status - Zzz."""
    s = create_surface((16, 16))
    color = PALETTE["status_sleep"]

    # Draw Z's
    # Big Z
    pygame.draw.line(s, color, (4, 4), (10, 4), 2)
    pygame.draw.line(s, color, (10, 4), (4, 10), 2)
    pygame.draw.line(s, color, (4, 10), (10, 10), 2)

    # Small z
    pygame.draw.line(s, (180, 180, 220), (10, 10), (14, 10), 1)
    pygame.draw.line(s, (180, 180, 220), (14, 10), (10, 14), 1)
    pygame.draw.line(s, (180, 180, 220), (10, 14), (14, 14), 1)

    return s


def draw_status_confusion() -> pygame.Surface:
    """Confusion status - spiral/question marks."""
    s = create_surface((16, 16))
    color = PALETTE["status_confusion"]

    # Spiral
    cx, cy = 8, 8
    for i in range(20):
        angle = i * 0.5
        radius = 1 + i * 0.25
        x = int(cx + radius * math.cos(angle))
        y = int(cy + radius * math.sin(angle))
        if 0 <= x < 16 and 0 <= y < 16:
            alpha = 255 - i * 10
            draw_pixel(s, (*color, max(50, alpha)), (x, y))

    # Question mark
    pygame.draw.arc(s, color, (10, 2, 4, 4), 0, 3.14, 1)
    draw_pixel(s, color, (12, 6))
    draw_pixel(s, color, (12, 8))

    return s


def draw_status_bleed() -> pygame.Surface:
    """Bleed status - blood drop."""
    s = create_surface((16, 16))
    color = PALETTE["status_bleed"]
    light = (220, 50, 50)

    # Blood drop shape
    pygame.draw.polygon(s, color, [(8, 2), (4, 10), (8, 14), (12, 10)])
    pygame.draw.circle(s, color, (8, 10), 4)

    # Highlight
    draw_pixel(s, light, (6, 8))

    return s


def draw_status_regen() -> pygame.Surface:
    """Regen status - healing heart/plus."""
    s = create_surface((16, 16))
    color = PALETTE["status_regen"]
    light = (100, 255, 150)

    # Plus/cross shape
    pygame.draw.rect(s, color, (6, 2, 4, 12))
    pygame.draw.rect(s, color, (2, 6, 12, 4))

    # Sparkle effects
    draw_pixel(s, light, (3, 3))
    draw_pixel(s, light, (12, 3))
    draw_pixel(s, light, (3, 12))
    draw_pixel(s, light, (12, 12))

    return s


def draw_status_shield() -> pygame.Surface:
    """Shield/barrier status - shield icon."""
    s = create_surface((16, 16))
    color = PALETTE["status_shield"]
    light = (150, 200, 255)

    # Shield shape
    pygame.draw.polygon(s, color, [
        (8, 2), (14, 4), (14, 8), (8, 14), (2, 8), (2, 4)
    ])

    # Inner highlight
    pygame.draw.polygon(s, light, [
        (8, 4), (11, 5), (11, 8), (8, 11), (5, 8), (5, 5)
    ])

    # Center emblem
    draw_pixel(s, (255, 255, 255), (8, 7))

    return s


def draw_status_attack_up() -> pygame.Surface:
    """Attack up - sword with up arrow."""
    s = create_surface((16, 16))
    color = PALETTE["status_attack_up"]

    # Sword
    pygame.draw.line(s, PALETTE["steel"], (8, 4), (8, 14), 2)
    pygame.draw.line(s, PALETTE["gold"], (5, 10), (11, 10), 2)

    # Up arrow
    pygame.draw.polygon(s, color, [(12, 6), (14, 6), (13, 2)])

    return s


def draw_status_defense_up() -> pygame.Surface:
    """Defense up - shield with up arrow."""
    s = create_surface((16, 16))
    color = PALETTE["status_defense_up"]

    # Mini shield
    pygame.draw.polygon(s, PALETTE["steel"], [
        (6, 4), (10, 4), (10, 10), (8, 12), (6, 10)
    ])
    pygame.draw.polygon(s, color, [
        (7, 5), (9, 5), (9, 9), (8, 10), (7, 9)
    ])

    # Up arrow
    pygame.draw.polygon(s, (100, 255, 100), [(12, 8), (14, 8), (13, 4)])

    return s


def draw_status_taunt() -> pygame.Surface:
    """Taunt status - angry face/exclamation."""
    s = create_surface((16, 16))
    red = (255, 50, 50)

    # Angry face circle
    pygame.draw.circle(s, red, (8, 8), 6, 1)

    # Angry eyebrows
    pygame.draw.line(s, red, (4, 5), (7, 7), 1)
    pygame.draw.line(s, red, (12, 5), (9, 7), 1)

    # Eyes
    draw_pixel(s, red, (6, 8))
    draw_pixel(s, red, (10, 8))

    # Angry mouth
    pygame.draw.line(s, red, (6, 11), (10, 11), 1)

    return s


def draw_status_barrier() -> pygame.Surface:
    """Barrier status - magical shield bubble."""
    s = create_surface((16, 16))
    color = (100, 150, 255, 150)
    light = (200, 220, 255, 200)

    # Bubble
    pygame.draw.circle(s, color, (8, 8), 6)
    pygame.draw.circle(s, light, (8, 8), 6, 1)

    # Sparkles
    draw_pixel(s, (255, 255, 255), (5, 5))
    draw_pixel(s, (255, 255, 255), (10, 4))

    return s


# ============================================
# NPC GENERATORS
# ============================================

def draw_humanoid(
    color_skin: Tuple,
    color_clothes: Tuple,
    color_hair: Tuple,
    accessory: Optional[str] = None,
) -> pygame.Surface:
    """Draw a humanoid NPC sprite."""
    s = create_surface((32, 32))

    # Shadow
    pygame.draw.ellipse(s, (0, 0, 0, 100), (8, 28, 16, 4))

    c_cloth_dark = tuple(max(0, c - 40) for c in color_clothes)

    # Legs
    pygame.draw.rect(s, c_cloth_dark, (11, 22, 4, 8))
    pygame.draw.rect(s, c_cloth_dark, (17, 22, 4, 8))

    # Torso
    pygame.draw.rect(s, color_clothes, (10, 12, 12, 11), border_radius=2)

    # Belt
    pygame.draw.rect(s, (60, 40, 20), (10, 20, 12, 2))

    # Head
    pygame.draw.rect(s, color_skin, (11, 4, 10, 9), border_radius=2)

    # Hair
    pygame.draw.rect(s, color_hair, (10, 2, 12, 4))
    pygame.draw.rect(s, color_hair, (9, 3, 2, 6))
    pygame.draw.rect(s, color_hair, (21, 3, 2, 6))

    # Arms
    pygame.draw.rect(s, color_clothes, (7, 13, 3, 8))
    pygame.draw.rect(s, color_clothes, (22, 13, 3, 8))

    # Hands
    pygame.draw.rect(s, color_skin, (7, 21, 3, 3))
    pygame.draw.rect(s, color_skin, (22, 21, 3, 3))

    # Face
    draw_pixel(s, (0, 0, 0), (13, 8))
    draw_pixel(s, (0, 0, 0), (17, 8))

    # Accessories
    if accessory == "hat":
        pygame.draw.rect(s, (60, 40, 20), (8, 0, 16, 3))
        pygame.draw.rect(s, (60, 40, 20), (10, 0, 12, 5))
    elif accessory == "hood":
        pygame.draw.polygon(s, c_cloth_dark, [(10, 2), (22, 2), (24, 10), (8, 10)])
    elif accessory == "crown":
        pygame.draw.rect(s, PALETTE["gold"], (10, 0, 12, 3))
        draw_pixel(s, PALETTE["gold"], (12, -1))
        draw_pixel(s, PALETTE["gold"], (16, -1))
        draw_pixel(s, PALETTE["gold"], (20, -1))
    elif accessory == "helmet":
        pygame.draw.rect(s, PALETTE["steel"], (9, 1, 14, 8))
        pygame.draw.line(s, PALETTE["steel_dark"], (9, 7), (23, 7), 2)

    return s


def generate_npc_variants() -> None:
    """Generate various NPC sprite variants."""
    print("Generating NPC variants...")

    npcs = {
        "npc_elder": ((200, 170, 140), (80, 60, 100), (200, 200, 200), None),
        "npc_child": ((255, 210, 180), (100, 150, 200), (100, 60, 30), None),
        "npc_farmer": ((200, 160, 120), (100, 80, 60), (80, 60, 40), "hat"),
        "npc_priest": ((240, 220, 200), (255, 255, 255), (50, 40, 30), "hood"),
        "npc_noble": ((250, 230, 210), (120, 20, 80), (40, 30, 20), "crown"),
        "npc_knight": ((200, 180, 160), (100, 100, 120), (60, 40, 30), "helmet"),
        "npc_mage": ((220, 200, 180), (60, 40, 120), (150, 150, 170), "hood"),
        "npc_thief": ((180, 150, 120), (40, 40, 50), (30, 30, 30), "hood"),
        "npc_barmaid": ((255, 210, 190), (150, 80, 80), (180, 100, 50), None),
        "npc_sailor": ((200, 160, 130), (40, 60, 100), (50, 40, 30), None),
    }

    for name, (skin, clothes, hair, acc) in npcs.items():
        sprite = draw_humanoid(skin, clothes, hair, acc)
        save_sprite(sprite, name)


# ============================================
# PROP GENERATORS
# ============================================

def draw_tree() -> pygame.Surface:
    """Draw a tree prop."""
    s = create_surface((32, 32))

    trunk = PALETTE["wood_dark"]
    leaves = PALETTE["grass_base"]
    leaves_light = PALETTE["grass_light"]

    # Trunk
    pygame.draw.rect(s, trunk, (13, 18, 6, 14))
    pygame.draw.rect(s, PALETTE["wood"], (14, 20, 4, 10))

    # Foliage - layered circles
    pygame.draw.circle(s, leaves, (16, 10), 10)
    pygame.draw.circle(s, leaves, (10, 14), 7)
    pygame.draw.circle(s, leaves, (22, 14), 7)
    pygame.draw.circle(s, leaves_light, (14, 8), 5)
    pygame.draw.circle(s, leaves_light, (20, 12), 4)

    add_noise(s, 10)
    return s


# ============================================
# BACKDROP GENERATORS (320x180)
# ============================================

def draw_backdrop_desert() -> pygame.Surface:
    """Draw desert battle backdrop."""
    s = create_surface((320, 180))

    # Sky gradient
    for y in range(90):
        t = y / 90
        color = lerp_color((135, 206, 235), (255, 200, 150), t)
        pygame.draw.line(s, color, (0, y), (320, y))

    # Sand dunes
    for y in range(90, 180):
        t = (y - 90) / 90
        color = lerp_color((210, 180, 140), (180, 150, 100), t)
        pygame.draw.line(s, color, (0, y), (320, y))

    # Dune curves
    pygame.draw.ellipse(s, (200, 170, 130), (-50, 100, 200, 100))
    pygame.draw.ellipse(s, (190, 160, 120), (150, 110, 220, 90))

    # Sun
    pygame.draw.circle(s, (255, 220, 100), (280, 30), 20)

    # Cacti silhouettes
    pygame.draw.rect(s, (100, 80, 60), (50, 110, 8, 40))
    pygame.draw.rect(s, (100, 80, 60), (42, 120, 8, 20))
    pygame.draw.rect(s, (100, 80, 60), (58, 125, 8, 15))

    add_noise(s, 5)
    return s


def draw_backdrop_city() -> pygame.Surface:
    """Draw city/town battle backdrop."""
    s = create_surface((320, 180))

    # Sky
    for y in range(100):
        t = y / 100
        color = lerp_color((135, 180, 220), (200, 180, 160), t)
        pygame.draw.line(s, color, (0, y), (320, y))

    # Ground
    pygame.draw.rect(s, (100, 90, 80), (0, 100, 320, 80))

    # Cobblestone pattern
    for x in range(0, 320, 20):
        for y in range(100, 180, 15):
            offset = 10 if (y // 15) % 2 else 0
            pygame.draw.rect(s, (80, 70, 60), (x + offset, y, 18, 13), 1)

    # Buildings in background
    buildings = [
        (10, 60, 50, 40, (120, 100, 90)),
        (70, 50, 40, 50, (110, 90, 80)),
        (120, 40, 60, 60, (130, 110, 100)),
        (190, 55, 45, 45, (115, 95, 85)),
        (250, 45, 55, 55, (125, 105, 95)),
    ]
    for x, y, w, h, color in buildings:
        pygame.draw.rect(s, color, (x, y, w, h))
        # Windows
        for wx in range(x + 5, x + w - 5, 12):
            for wy in range(y + 5, y + h - 10, 12):
                pygame.draw.rect(s, (200, 180, 100), (wx, wy, 6, 8))

    add_noise(s, 5)
    return s


def draw_backdrop_dungeon() -> pygame.Surface:
    """Draw dungeon/indoor battle backdrop."""
    s = create_surface((320, 180))

    # Dark walls
    s.fill((30, 25, 35))

    # Stone wall pattern
    for x in range(0, 320, 40):
        for y in range(0, 100, 25):
            offset = 20 if (y // 25) % 2 else 0
            color = (40 + random.randint(-5, 5), 35 + random.randint(-5, 5), 45 + random.randint(-5, 5))
            pygame.draw.rect(s, color, (x + offset, y, 38, 23))

    # Floor
    pygame.draw.rect(s, (50, 45, 55), (0, 100, 320, 80))

    # Floor tiles
    for x in range(0, 320, 32):
        for y in range(100, 180, 32):
            pygame.draw.rect(s, (40, 35, 45), (x, y, 30, 30))

    # Torches on walls
    for x in [60, 160, 260]:
        pygame.draw.rect(s, (80, 60, 40), (x, 60, 6, 15))
        pygame.draw.circle(s, (255, 150, 50), (x + 3, 58), 8)
        pygame.draw.circle(s, (255, 200, 100), (x + 3, 56), 5)

    add_noise(s, 8)
    return s


def draw_backdrop_volcano() -> pygame.Surface:
    """Draw volcanic battle backdrop."""
    s = create_surface((320, 180))

    # Smoky sky
    for y in range(100):
        t = y / 100
        color = lerp_color((80, 40, 30), (40, 20, 20), t)
        pygame.draw.line(s, color, (0, y), (320, y))

    # Lava ground
    for y in range(100, 180):
        t = (y - 100) / 80
        color = lerp_color((200, 80, 20), (150, 50, 10), t)
        pygame.draw.line(s, color, (0, y), (320, y))

    # Lava pools
    for _ in range(5):
        x = random.randint(20, 300)
        y = random.randint(110, 170)
        w = random.randint(30, 60)
        h = random.randint(10, 20)
        pygame.draw.ellipse(s, (255, 100, 0), (x, y, w, h))
        pygame.draw.ellipse(s, (255, 200, 50), (x + 5, y + 2, w - 10, h - 4))

    # Rocky formations
    pygame.draw.polygon(s, (60, 40, 30), [(0, 100), (40, 60), (80, 100)])
    pygame.draw.polygon(s, (50, 30, 25), [(240, 100), (280, 50), (320, 100)])

    add_noise(s, 10)
    return s


# ============================================
# MAIN GENERATION FUNCTIONS
# ============================================

def generate_missing_enemies() -> None:
    """Generate missing enemy sprites."""
    print("\nGenerating missing enemy sprites...")

    # Snake (used by sea serpents)
    save_sprite(draw_snake(), "snake")

    # Earth elemental (may be needed)
    if not os.path.exists(os.path.join(SPRITE_DIR, "earth_elemental.png")):
        save_sprite(draw_earth_elemental(), "earth_elemental")


def generate_status_icons() -> None:
    """Generate all status effect icons."""
    print("\nGenerating status icons...")

    icons = {
        "status_poison": draw_status_poison,
        "status_burn": draw_status_burn,
        "status_frozen": draw_status_freeze,
        "status_freeze": draw_status_freeze,  # Alias
        "status_stun": draw_status_stun,
        "status_sleep": draw_status_sleep,
        "status_confusion": draw_status_confusion,
        "status_bleed": draw_status_bleed,
        "status_regen": draw_status_regen,
        "status_shield": draw_status_shield,
        "status_barrier": draw_status_barrier,
        "status_attack_up": draw_status_attack_up,
        "status_defense_up": draw_status_defense_up,
        "status_taunt": draw_status_taunt,
    }

    for name, func in icons.items():
        save_sprite(func(), name)


def generate_props() -> None:
    """Generate missing prop sprites."""
    print("\nGenerating prop sprites...")

    # Tree
    if not os.path.exists(os.path.join(SPRITE_DIR, "prop_tree.png")):
        save_sprite(draw_tree(), "prop_tree")


def generate_backdrops() -> None:
    """Generate additional battle backdrops."""
    print("\nGenerating battle backdrops...")

    backdrops = {
        "bg_desert": draw_backdrop_desert,
        "bg_city": draw_backdrop_city,
        "bg_dungeon": draw_backdrop_dungeon,
        "bg_volcano": draw_backdrop_volcano,
    }

    for name, func in backdrops.items():
        save_sprite(func(), name)


def update_status_icons_json() -> None:
    """Update status_icons.json with all status effects."""
    import json

    print("\nUpdating status_icons.json...")

    status_icons = {
        # Debuffs
        "poison": "status_poison",
        "bleed": "status_bleed",
        "burn": "status_burn",
        "frozen": "status_frozen",
        "freeze": "status_frozen",
        "stun": "status_stun",
        "sleep": "status_sleep",
        "confusion": "status_confusion",
        "terror": "status_terror",
        "taunt": "status_taunt",

        # Buffs
        "regen": "status_regen",
        "barrier": "status_barrier",
        "shield": "status_shield",
        "attack_up": "status_attack_up",
        "defense_up": "status_defense_up",

        # Limb status
        "limb_arm_left_missing": "status_limb_arm",
        "limb_arm_right_missing": "status_limb_arm",
        "limb_leg_left_missing": "status_limb_leg",
        "limb_leg_right_missing": "status_limb_leg",

        # Summon statuses (no icon needed, but map for completeness)
        "summon_skeleton": "status_regen",
        "summon_elemental": "status_regen",
    }

    path = os.path.join(BASE_DIR, "data", "status_icons.json")
    with open(path, "w") as f:
        json.dump(status_icons, f, indent=2)

    print(f"  Updated: {path}")


def main() -> None:
    """Main entry point."""
    print("=" * 50)
    print("Comprehensive Sprite Generator")
    print("=" * 50)

    generate_missing_enemies()
    generate_status_icons()
    generate_npc_variants()
    generate_props()
    generate_backdrops()
    update_status_icons_json()

    print("\n" + "=" * 50)
    print("Sprite generation complete!")
    print("=" * 50)


if __name__ == "__main__":
    main()
