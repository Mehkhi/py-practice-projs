import os
import pygame
import random
import math

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

def create_surface(size=(32, 32)):
    return pygame.Surface(size, pygame.SRCALPHA)

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
    "ice": (224, 255, 255),
    "poison": (148, 0, 211),
    "magic": (255, 0, 255),
    "holy": (255, 255, 240),
    "dark": (75, 0, 130),

    # UI
    "ui_bg": (20, 20, 30),
    "ui_border": (200, 200, 200),
}

def add_noise(surface, intensity=20):
    """Add random noise texture to a surface."""
    width, height = surface.get_size()
    for x in range(width):
        for y in range(height):
            color = surface.get_at((x, y))
            if color.a == 0: continue

            noise = random.randint(-intensity, intensity)
            r = max(0, min(255, color.r + noise))
            g = max(0, min(255, color.g + noise))
            b = max(0, min(255, color.b + noise))
            surface.set_at((x, y), (r, g, b, color.a))

def draw_pixel(surface, color, pos):
    if 0 <= pos[0] < surface.get_width() and 0 <= pos[1] < surface.get_height():
        surface.set_at(pos, color)

def draw_rect_outline(surface, color, rect, width=1):
    pygame.draw.rect(surface, color, rect, width)

# ============================================
# TILE GENERATORS (16x16 base)
# ============================================

def generate_tiles():
    print("Generating tiles...")

    tiles = {
        "grass": draw_tile_grass,
        "stone": draw_tile_stone,
        "water": draw_tile_water,
        "dirt": draw_tile_dirt,
        "path": draw_tile_path,
        "wall": draw_tile_wall,
        "lava": draw_tile_lava,
        "wood_floor": draw_tile_wood_floor,
        "void": draw_tile_void,
    }

    for name, func in tiles.items():
        s = func()
        # Save both base and scaled versions
        pygame.image.save(s, os.path.join(TILESET_DIR, f"{name}.png"))

        # Generate variants
        for i in range(3):
            s_var = func(variant=True)
            pygame.image.save(s_var, os.path.join(TILESET_DIR, f"{name}_{i+1}.png"))

def draw_tile_grass(variant=False):
    s = create_surface((16, 16))
    s.fill(PALETTE["grass_base"])
    add_noise(s, 10)

    # Grass blades
    for _ in range(10 if variant else 6):
        x, y = random.randint(0, 15), random.randint(0, 15)
        draw_pixel(s, PALETTE["grass_light"], (x, y))
        draw_pixel(s, PALETTE["grass_dark"], (x, y+1))
        if random.random() > 0.7:
             draw_pixel(s, PALETTE["grass_light"], (x+1, y-1))

    return s

def draw_tile_stone(variant=False):
    s = create_surface((16, 16))
    s.fill(PALETTE["stone_base"])
    add_noise(s, 15)

    # Cracks or stones
    color = PALETTE["stone_dark"]
    highlight = PALETTE["stone_light"]

    if variant:
        # Cracks
        start = (random.randint(2, 14), random.randint(2, 14))
        end = (start[0] + random.randint(-4, 4), start[1] + random.randint(-4, 4))
        pygame.draw.line(s, color, start, end)
    else:
        # Cobblestone pattern
        pygame.draw.rect(s, color, (1, 1, 6, 6), 1)
        pygame.draw.rect(s, color, (8, 8, 7, 7), 1)
        pygame.draw.rect(s, color, (9, 1, 6, 5), 1)
        draw_pixel(s, highlight, (2, 2))
        draw_pixel(s, highlight, (9, 9))

    return s

def draw_tile_water(variant=False):
    s = create_surface((16, 16))
    s.fill(PALETTE["water"])

    # Waves
    color = PALETTE["water_light"]
    dark = PALETTE["water_dark"]

    y_off = random.randint(0, 4) if variant else 0

    # Deep water shading
    for y in range(16):
        if y % 4 == 0:
            pygame.draw.line(s, dark, (0, y), (16, y))

    # Highlights
    pygame.draw.line(s, color, (2, 4+y_off), (8, 4+y_off))
    pygame.draw.line(s, color, (9, 10-y_off), (14, 10-y_off))

    return s

def draw_tile_dirt(variant=False):
    s = create_surface((16, 16))
    s.fill(PALETTE["dirt"])
    add_noise(s, 25)

    # Pebbles
    for _ in range(3):
        x, y = random.randint(0, 15), random.randint(0, 15)
        draw_pixel(s, PALETTE["dirt_light"], (x, y))

    return s

def draw_tile_path(variant=False):
    s = create_surface((16, 16))
    s.fill(PALETTE["dirt"])
    add_noise(s, 10)

    # Worn path center
    pygame.draw.rect(s, PALETTE["dirt_light"], (4, 0, 8, 16))
    add_noise(s, 15)

    # Stones embedded
    for _ in range(4):
        x, y = random.randint(2, 13), random.randint(2, 13)
        color = (160, 140, 120)
        draw_pixel(s, color, (x, y))

    return s

def draw_tile_wall(variant=False):
    s = create_surface((16, 16))
    s.fill(PALETTE["stone_dark"])

    # Bricks
    brick_color = PALETTE["stone_base"]
    highlight = PALETTE["stone_light"]

    for y in range(0, 16, 4):
        offset = 4 if (y//4) % 2 else 0
        for x in range(-4, 16, 8):
            rect = (x+offset, y, 7, 3)
            pygame.draw.rect(s, brick_color, rect)
            # Highlight top-left
            draw_pixel(s, highlight, (x+offset, y))

    add_noise(s, 10)
    return s

def draw_tile_lava(variant=False):
    s = create_surface((16, 16))
    s.fill(PALETTE["fire"])
    add_noise(s, 30)

    # Bubbles/Crust
    for _ in range(5):
        x, y = random.randint(0, 14), random.randint(0, 14)
        if random.random() > 0.5:
            # Dark crust
            pygame.draw.rect(s, (100, 20, 0), (x, y, 3, 2))
        else:
            # Bright bubble
            draw_pixel(s, PALETTE["gold"], (x, y))

    return s

def draw_tile_wood_floor(variant=False):
    s = create_surface((16, 16))
    s.fill(PALETTE["wood"])

    # Planks
    line_color = PALETTE["wood_dark"]
    highlight = PALETTE["wood_light"]

    for x in range(0, 16, 4):
        pygame.draw.line(s, line_color, (x, 0), (x, 15))
        # Wood grain
        draw_pixel(s, highlight, (x+1, random.randint(0, 15)))
        draw_pixel(s, highlight, (x+2, random.randint(0, 15)))
        # Nail heads
        draw_pixel(s, (80, 50, 20), (x+2, 2))
        draw_pixel(s, (80, 50, 20), (x+2, 13))

    add_noise(s, 5)
    return s

def draw_tile_void(variant=False):
    s = create_surface((16, 16))
    s.fill((0, 0, 0))
    return s


# ============================================
# CHARACTER GENERATORS (32x32)
# ============================================

def draw_humanoid(color_skin, color_clothes, color_hair, weapon_type=None):
    s = create_surface((32, 32))

    # Shadow
    pygame.draw.ellipse(s, (0, 0, 0, 100), (8, 28, 16, 4))

    # Colors
    c_skin = color_skin
    c_cloth = color_clothes
    c_cloth_dark = (max(0, c_cloth[0]-40), max(0, c_cloth[1]-40), max(0, c_cloth[2]-40))
    c_hair = color_hair

    # Body (Head, Torso, Legs)

    # Legs
    pygame.draw.rect(s, c_cloth_dark, (11, 22, 4, 8))
    pygame.draw.rect(s, c_cloth_dark, (17, 22, 4, 8))

    # Torso
    pygame.draw.rect(s, c_cloth, (10, 12, 12, 11), border_radius=2)
    # Belt
    pygame.draw.rect(s, (60, 40, 20), (10, 20, 12, 2))

    # Head
    pygame.draw.rect(s, c_skin, (11, 4, 10, 9), border_radius=2)

    # Hair
    pygame.draw.rect(s, c_hair, (10, 2, 12, 4)) # Top
    pygame.draw.rect(s, c_hair, (9, 3, 2, 8))  # Side L
    pygame.draw.rect(s, c_hair, (21, 3, 2, 8)) # Side R

    # Arms
    pygame.draw.rect(s, c_cloth, (7, 13, 3, 8))
    pygame.draw.rect(s, c_cloth, (22, 13, 3, 8))

    # Hands
    pygame.draw.rect(s, c_skin, (7, 21, 3, 3))
    pygame.draw.rect(s, c_skin, (22, 21, 3, 3))

    # Face details
    draw_pixel(s, (0, 0, 0), (13, 8)) # Eye L
    draw_pixel(s, (0, 0, 0), (17, 8)) # Eye R

    # Weapon
    if weapon_type == "sword":
        # Blade
        pygame.draw.line(s, PALETTE["steel"], (24, 22), (30, 10), 2)
        pygame.draw.line(s, PALETTE["steel_light"], (25, 22), (31, 10), 1)
        # Hilt
        pygame.draw.line(s, PALETTE["wood_dark"], (23, 23), (24, 22), 2)
        # Guard
        pygame.draw.line(s, PALETTE["gold"], (22, 20), (26, 24), 2)

    elif weapon_type == "staff":
        pygame.draw.line(s, PALETTE["wood"], (24, 8), (24, 28), 2)
        # Gem
        pygame.draw.circle(s, PALETTE["magic"], (24, 8), 3)
        draw_pixel(s, (255, 255, 255), (23, 7))

    elif weapon_type == "dagger":
        pygame.draw.line(s, PALETTE["steel"], (24, 22), (28, 18), 2)
        pygame.draw.line(s, PALETTE["wood_dark"], (23, 23), (24, 22), 2)

    elif weapon_type == "mace":
        pygame.draw.line(s, PALETTE["steel_dark"], (24, 14), (24, 26), 2)
        pygame.draw.circle(s, PALETTE["steel"], (24, 14), 4)

    return s

def generate_characters():
    print("Generating characters...")

    # Player classes
    classes = {
        "warrior": {
            "skin": (255, 200, 150), "clothes": (100, 40, 40),
            "hair": (50, 30, 10), "weapon": "sword"
        },
        "mage": {
            "skin": (240, 220, 180), "clothes": (40, 40, 120),
            "hair": (200, 200, 200), "weapon": "staff"
        },
        "rogue": {
            "skin": (200, 160, 120), "clothes": (40, 80, 40),
            "hair": (100, 50, 20), "weapon": "dagger"
        },
        "cleric": {
            "skin": (180, 140, 100), "clothes": (220, 220, 220),
            "hair": (220, 180, 50), "weapon": "mace"
        }
    }

    for name, props in classes.items():
        s = draw_humanoid(props["skin"], props["clothes"], props["hair"], props["weapon"])
        pygame.image.save(s, os.path.join(SPRITE_DIR, f"player_{name}.png"))
        # Also save generic player
        if name == "warrior":
            pygame.image.save(s, os.path.join(SPRITE_DIR, "player.png"))

    # NPCs
    npcs = [
        ("villager", (100, 100, 100)),
        ("merchant", (120, 60, 120)),
        ("guard", (150, 150, 160)),
    ]
    for name, clothes in npcs:
        s = draw_humanoid((255, 200, 150), clothes, (80, 60, 40))
        pygame.image.save(s, os.path.join(SPRITE_DIR, f"npc_{name}.png"))

# ============================================
# ENEMY GENERATORS
# ============================================

def draw_slime():
    s = create_surface((32, 32))
    color = (50, 200, 50)
    light = (100, 255, 100)

    # Body
    pygame.draw.ellipse(s, color, (6, 14, 20, 14))
    # Highlight
    pygame.draw.ellipse(s, light, (8, 16, 6, 6))

    # Eyes
    draw_pixel(s, (0,0,0), (10, 20))
    draw_pixel(s, (0,0,0), (20, 20))

    # Drip
    pygame.draw.circle(s, color, (24, 26), 2)

    return s

def draw_skeleton():
    s = create_surface((32, 32))
    white = (240, 240, 230)
    grey = (180, 180, 170)

    # Skull
    pygame.draw.circle(s, white, (16, 8), 6)
    # Eyes
    draw_pixel(s, (0,0,0), (14, 8))
    draw_pixel(s, (0,0,0), (18, 8))

    # Ribs
    pygame.draw.line(s, grey, (16, 14), (16, 22), 2) # Spine
    pygame.draw.line(s, white, (12, 16), (20, 16), 1)
    pygame.draw.line(s, white, (13, 18), (19, 18), 1)
    pygame.draw.line(s, white, (14, 20), (18, 20), 1)

    # Limbs
    pygame.draw.line(s, white, (13, 15), (10, 22), 2) # Arm L
    pygame.draw.line(s, white, (19, 15), (22, 22), 2) # Arm R
    pygame.draw.line(s, white, (15, 22), (14, 30), 2) # Leg L
    pygame.draw.line(s, white, (17, 22), (18, 30), 2) # Leg R

    # Weapon (Rusty sword)
    pygame.draw.line(s, (150, 100, 100), (22, 22), (22, 10), 2)

    return s

def draw_bat():
    s = create_surface((32, 32))
    color = (60, 30, 60)
    dark = (40, 20, 40)

    # Wings
    pygame.draw.polygon(s, dark, [(16, 16), (4, 6), (8, 20)])
    pygame.draw.polygon(s, dark, [(16, 16), (28, 6), (24, 20)])

    # Body
    pygame.draw.circle(s, color, (16, 16), 5)

    # Eyes
    draw_pixel(s, (255, 0, 0), (14, 15))
    draw_pixel(s, (255, 0, 0), (18, 15))

    # Fangs
    draw_pixel(s, (255, 255, 255), (15, 18))
    draw_pixel(s, (255, 255, 255), (17, 18))

    return s

def draw_spider():
    s = create_surface((32, 32))
    black = (30, 30, 30)
    grey = (60, 60, 60)

    # Legs (4 per side)
    for i in range(4):
        # Left
        pygame.draw.line(s, black, (16, 16), (4, 8 + i*6), 2)
        pygame.draw.line(s, black, (4, 8 + i*6), (2, 12 + i*6), 1)
        # Right
        pygame.draw.line(s, black, (16, 16), (28, 8 + i*6), 2)
        pygame.draw.line(s, black, (28, 8 + i*6), (30, 12 + i*6), 1)

    # Abdomen
    pygame.draw.circle(s, black, (16, 18), 7)
    # Markings
    draw_pixel(s, (255, 0, 0), (16, 16))
    draw_pixel(s, (255, 0, 0), (16, 18))
    draw_pixel(s, (255, 0, 0), (16, 20))

    # Head
    pygame.draw.circle(s, grey, (16, 12), 4)

    # Eyes (red glowing)
    draw_pixel(s, (255, 0, 0), (15, 11))
    draw_pixel(s, (255, 0, 0), (17, 11))

    return s

def draw_ghost():
    s = create_surface((32, 32))
    white = (220, 220, 255, 180) # Semi-transparent

    # Body
    pygame.draw.rect(s, white, (10, 6, 12, 18), border_top_left_radius=6, border_top_right_radius=6)

    # Tail (wisps)
    pygame.draw.circle(s, white, (11, 24), 2)
    pygame.draw.circle(s, white, (16, 26), 3)
    pygame.draw.circle(s, white, (21, 24), 2)

    # Face
    draw_pixel(s, (0, 0, 0), (13, 12))
    draw_pixel(s, (0, 0, 0), (18, 12))
    draw_pixel(s, (0, 0, 0), (16, 16)) # Mouth

    return s

def generate_enemies():
    print("Generating enemies...")
    generators = {
        "slime": draw_slime,
        "skeleton": draw_skeleton,
        "bat": draw_bat,
        "spider": draw_spider,
        "ghost": draw_ghost,
    }

    # Also add generic enemy placeholders if needed
    for name, func in generators.items():
        s = func()
        pygame.image.save(s, os.path.join(SPRITE_DIR, f"enemy_{name}.png"))

    # Default fallback
    pygame.image.save(draw_slime(), os.path.join(SPRITE_DIR, "enemy.png"))

# ============================================
# UI & ITEM GENERATORS
# ============================================

def generate_ui():
    print("Generating UI assets...")

    # UI Panel (Nine-slice source 24x24)
    # Using new theme colors: Dark BG, Light Border
    s = create_surface((24, 24))
    s.fill(PALETTE["ui_bg"]) # BG
    pygame.draw.rect(s, PALETTE["ui_border"], (0, 0, 24, 24), 2) # Border
    pygame.draw.rect(s, (50, 50, 60), (2, 2, 20, 20), 1) # Inner bevel
    pygame.image.save(s, os.path.join(SPRITE_DIR, "ui_panel.png"))

    # Cursor
    c = create_surface((16, 16))
    pygame.draw.polygon(c, PALETTE["gold"], [(0, 0), (12, 6), (4, 8), (6, 14)])
    pygame.draw.polygon(c, (255, 255, 200), [(1, 1), (10, 6), (4, 7), (5, 12)])
    pygame.image.save(c, os.path.join(SPRITE_DIR, "ui_cursor.png"))

    # Items
    items = {
        "potion_health": ((255, 50, 50), "bottle"),
        "potion_mana": ((50, 50, 255), "bottle"),
        "sword": (PALETTE["steel"], "sword"),
        "shield": (PALETTE["steel"], "shield"),
        "key": (PALETTE["gold"], "key"),
        "armor": (PALETTE["steel"], "armor"),
        "helmet": (PALETTE["steel"], "helmet"),
    }

    for name, (color, shape) in items.items():
        icon = create_surface((32, 32))

        if shape == "bottle":
            pygame.draw.circle(icon, (200, 200, 200), (16, 20), 8) # Base
            pygame.draw.circle(icon, color, (16, 20), 6) # Liquid
            pygame.draw.rect(icon, (200, 200, 200), (14, 10, 4, 6)) # Neck
            draw_pixel(icon, (255, 255, 255), (14, 18)) # Shine

        elif shape == "sword":
            pygame.draw.line(icon, color, (26, 6), (6, 26), 3)
            pygame.draw.line(icon, PALETTE["wood_dark"], (10, 22), (6, 26), 3) # Hilt
            pygame.draw.line(icon, PALETTE["gold"], (12, 20), (8, 24), 5) # Guard

        elif shape == "shield":
            pygame.draw.rect(icon, color, (8, 6, 16, 20), border_bottom_left_radius=8, border_bottom_right_radius=8)
            pygame.draw.rect(icon, PALETTE["gold"], (8, 6, 16, 20), 2, border_bottom_left_radius=8, border_bottom_right_radius=8)
            # Cross design
            pygame.draw.line(icon, PALETTE["gold_dark"], (16, 8), (16, 24), 2)
            pygame.draw.line(icon, PALETTE["gold_dark"], (10, 14), (22, 14), 2)

        elif shape == "key":
            pygame.draw.circle(icon, color, (20, 10), 4, 2)
            pygame.draw.line(icon, color, (18, 13), (10, 24), 2)
            pygame.draw.line(icon, color, (10, 24), (14, 24), 2)

        elif shape == "armor":
            pygame.draw.rect(icon, color, (8, 6, 16, 20), border_radius=4)
            pygame.draw.rect(icon, PALETTE["gold"], (12, 6, 8, 20)) # Trim

        elif shape == "helmet":
            pygame.draw.circle(icon, color, (16, 16), 10)
            pygame.draw.line(icon, (0, 0, 0), (12, 16), (20, 16), 2) # Visor
            pygame.draw.line(icon, PALETTE["gold"], (16, 6), (16, 16), 2) # Crest

        pygame.image.save(icon, os.path.join(SPRITE_DIR, f"item_{name}.png"))

# ============================================
# MAIN
# ============================================

def main():
    print(f"Generating sprites in {SPRITE_DIR}")
    generate_tiles()
    generate_characters()
    generate_enemies()
    generate_ui()
    print("Done!")

if __name__ == "__main__":
    main()
