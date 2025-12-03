import os
import pygame
import random
import math

# Initialize pygame
pygame.init()

def draw_pixel(surface, color, pos):
    if 0 <= pos[0] < surface.get_width() and 0 <= pos[1] < surface.get_height():
        surface.set_at(pos, color)

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

# Expanded DawnBringer32-ish palette for cohesive pixel art
PALETTE = {
    # Greys/Blacks
    "black": (0, 0, 0),
    "dark_grey": (34, 32, 52),
    "grey": (69, 40, 60), # Warm grey
    "light_grey": (132, 126, 135), # Steel
    "white": (255, 255, 255),

    # Reds
    "dark_red": (75, 3, 15), # Dried blood
    "red": (172, 50, 50), # Crimson
    "light_red": (217, 87, 99),

    # Greens
    "dark_green": (30, 60, 20), # Swamp
    "green": (55, 148, 110), # Forest
    "light_green": (106, 190, 48), # Lime
    "slime_green": (153, 225, 115),

    # Blues
    "dark_blue": (20, 24, 46), # Void
    "blue": (48, 96, 130), # Deep water
    "light_blue": (91, 110, 225), # Sky/Ice
    "cyan": (99, 155, 255),

    # Yellows/Golds
    "brown": (63, 40, 50), # Wood dark
    "orange": (223, 113, 38), # Rust
    "gold": (251, 242, 54),
    "light_gold": (255, 255, 150),

    # Purples
    "dark_purple": (45, 20, 60),
    "purple": (118, 66, 138),

    # Skin Tones
    "skin_base": (238, 195, 154),
    "skin_shadow": (217, 160, 102),
    "skin_orc": (100, 125, 50),

    # Materials
    "bone": (220, 220, 210),
    "bone_shadow": (160, 160, 150),
    "stone_base": (112, 128, 144), # Slate
    "stone_light": (176, 196, 222),
    "stone_dark": (47, 79, 79),
    "dirt": (101, 67, 33),
    "dirt_light": (139, 69, 19),
    "wood": (139, 69, 19),
    "wood_dark": (101, 67, 33),
}

def apply_dither(surface, color, density=0.5):
    """Apply a checkerboard dither pattern."""
    w, h = surface.get_size()
    for y in range(h):
        for x in range(w):
            if (x + y) % 2 == 0 and random.random() < density:
                # Only draw on non-transparent pixels
                if surface.get_at((x, y)).a > 0:
                    surface.set_at((x, y), color)

def draw_gradient_rect(surface, rect, top_color, bottom_color):
    """Draw a vertical gradient rectangle."""
    r1, g1, b1 = top_color[:3]
    r2, g2, b2 = bottom_color[:3]
    x, y, w, h = rect
    for i in range(h):
        ratio = i / h
        r = int(r1 + (r2 - r1) * ratio)
        g = int(g1 + (g2 - g1) * ratio)
        b = int(b1 + (b2 - b1) * ratio)
        pygame.draw.line(surface, (r, g, b), (x, y+i), (x+w, y+i))

def draw_sphere(surface, color, center, radius, light_dir=(-1, -1)):
    """Draw a sphere with highlight and shadow."""
    cx, cy = center
    # Base
    pygame.draw.circle(surface, color, center, radius)

    # Shadow (bottom right)
    shadow_color = (max(0, color[0]-40), max(0, color[1]-40), max(0, color[2]-40))
    offset = int(radius * 0.3)
    shadow_rect = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
    pygame.draw.circle(shadow_rect, shadow_color, (radius, radius), radius)
    # Mask for crescent shadow
    mask_color = (0, 0, 0, 0)
    pygame.draw.circle(shadow_rect, mask_color, (radius - offset, radius - offset), radius, draw_top_left=True)

    # Highlight (top left)
    highlight_color = (min(255, color[0]+60), min(255, color[1]+60), min(255, color[2]+60))
    hl_radius = max(1, int(radius * 0.3))
    hl_x = cx - int(radius * 0.4)
    hl_y = cy - int(radius * 0.4)
    pygame.draw.circle(surface, highlight_color, (hl_x, hl_y), hl_radius)

def draw_outline(surface, color, thickness=1):
    """Draw an outline around the non-transparent pixels."""
    mask = pygame.mask.from_surface(surface)
    outline_surf = mask.to_surface(setcolor=color, unsetcolor=(0,0,0,0))
    for dx in range(-thickness, thickness+1):
        for dy in range(-thickness, thickness+1):
            if dx == 0 and dy == 0: continue
            surface.blit(outline_surf, (dx, dy), special_flags=pygame.BLEND_PREMULTIPLIED)

# ============================================
# BITMAP TEMPLATES
# ============================================

TEMPLATES = {
    "werewolf": [
        "......HHH.......",
        ".....HHH.....H..",
        "...HHHHH....HH..",
        "..HHHHHHHHHHH...",
        "..HHYYHHHHHH....",
        ".HHYYYHHHHHH....",
        ".HHHHHHHHHH.....",
        ".HHHHHHHHHH.....",
        ".HHHHHHHHHH.....",
        "..HHHHHHHH......",
        "..H.H..H.H......",
        ".HH.H..H.HH.....",
        ".C..C..C..C.....",
        "................",
    ],
    "goblin": [
        "................",
        ".....GGGGG......",
        "....GGGGGGG.....",
        "...EGGYGGYGE....",
        "....GGGGGGG.....",
        ".....GGGGG......",
        "....VVVVVVV.....",
        "....GVVVVVG.....",
        "....GG.B.GG.....",
        ".......B........",
        "......L.L.......",
        ".....B...B......",
        "................",
        "................",
    ],
    "skeleton": [
        "......WW........",
        ".....W..W.......",
        "....W.RR.W......",
        "....W....W......",
        "......SS........",
        "....RRRRRR......",
        "....R.SS.R......",
        "......PP........",
        ".....L..L.......",
        ".....L..L.......",
        "....B....B......",
        "................",
        "................",
    ],
    "orc": [
        "................",
        ".....HHHH.......",
        "....HHHHHH......",
        "...HHHAAHHH.....",
        "...HHYAAHYH.....",
        "...HHTAATHH.....",
        "....AAAAAA......",
        "...AAAHHAAA.....",
        "..AAAAHHAAAA....",
        "..AAAA..AAAA....",
        "......LL........",
        ".....L..L.......",
        "....BB..BB......",
        "................",
    ]
}

def draw_from_template(surface, template, color_map, offset=(0,0)):
    """Draw sprite from a string template."""
    ox, oy = offset
    for y, row in enumerate(template):
        for x, char in enumerate(row):
            if char in color_map:
                draw_pixel(surface, color_map[char], (ox + x, oy + y))

# ============================================
# TILE GENERATORS (Detailed)
# ============================================

def generate_tiles():
    print("Generating detailed tiles...")

    # Helper to save
    def save(s, name):
        pygame.image.save(s, os.path.join(TILESET_DIR, f"{name}.png"))

    # Grass
    s = create_surface()
    s.fill(PALETTE["green"])
    # Blades
    for _ in range(40):
        x, y = random.randint(0, 31), random.randint(0, 31)
        color = PALETTE["light_green"] if random.random() > 0.5 else PALETTE["dark_green"]
        pygame.draw.line(s, color, (x, y), (x, y-2), 1)
    save(s, "grass")

    # Stone (Cobblestone)
    s = create_surface()
    s.fill(PALETTE["stone_base"])
    for _ in range(10):
        x, y = random.randint(0, 28), random.randint(0, 28)
        w, h = random.randint(4, 8), random.randint(4, 8)
        rect = (x, y, w, h)
        pygame.draw.rect(s, PALETTE["stone_light"], rect)
        pygame.draw.rect(s, PALETTE["stone_dark"], rect, 1)
    save(s, "stone")

    # Water (Animated look)
    s = create_surface()
    s.fill(PALETTE["blue"])
    for _ in range(10):
        x, y = random.randint(0, 28), random.randint(0, 31)
        w = random.randint(4, 10)
        pygame.draw.line(s, PALETTE["light_blue"], (x, y), (x+w, y), 1)
    save(s, "water")

    # Wall (Brick)
    s = create_surface()
    s.fill(PALETTE["stone_dark"])
    for y in range(0, 32, 8):
        offset = 8 if (y//8) % 2 else 0
        for x in range(-8, 32, 16):
            r = (x+offset, y, 15, 7)
            draw_gradient_rect(s, r, PALETTE["stone_light"], PALETTE["stone_base"])
            pygame.draw.rect(s, (0,0,0), r, 1)
    save(s, "wall")

    # Dirt
    s = create_surface()
    s.fill(PALETTE["dirt"])
    apply_dither(s, PALETTE["dirt_light"], 0.2)
    save(s, "dirt")

    # Lava
    s = create_surface()
    draw_gradient_rect(s, (0,0,32,32), PALETTE["red"], PALETTE["orange"])
    for _ in range(5):
        x, y = random.randint(5, 25), random.randint(5, 25)
        draw_sphere(s, PALETTE["gold"], (x, y), 3)
    save(s, "lava")

# ... (Imports and Palette remain the same)

# ============================================
# BITMAP ART SYSTEM
# ============================================

def draw_from_template(surface, template, color_map, offset=(0,0)):
    """
    Draw sprite from a string template.
    template: list of strings
    color_map: dict mapping chars to colors
    """
    ox, oy = offset
    for y, row in enumerate(template):
        for x, char in enumerate(row):
            if char in color_map:
                draw_pixel(surface, color_map[char], (ox + x, oy + y))

# Templates are designed for 16x16 or similar, scaled up effectively by the 32x32 canvas
# We will center them.

TEMPLATES = {
    "werewolf": [
        "......HHH.......",
        ".....HHHHH......",
        "....HHHHHH......",
        "...HHHHYHH......",
        "...HHHHHHH......",
        "..HHHHHHHH......",
        "..HHHHHHHHH.....",
        ".HHHHHHHHHH.....",
        ".HHH...HHHH.....",
        ".HH.....HHH.....",
        ".H......HHH.....",
        "........H.H.....",
        ".......CC.CC....",
    ],
    "goblin": [
        "......GG........",
        ".....GGGG.......",
        "....EGGGGE......",
        "....GGYGGE......",
        ".....GGGG.......",
        ".....VVVV.......",
        "....GVVVVG......",
        "....G.VV.G......",
        "......LL........",
        ".....L..L.......",
        ".....B..B.......",
    ],
    "skeleton": [
        "......WW........",
        ".....W..W.......",
        ".....W..W.......",
        "......WW........",
        "......SS........",
        "....W.SS.W......",
        "....W.SS.W......",
        "......PP........",
        "......B.B.......",
        ".....B...B......",
    ],
    "orc": [
        "......HH........",
        ".....HHHH.......",
        "....HHHHHH......",
        "....HHYHHH......",
        "....HHTTHH......",
        "....AAAAAA......",
        "...AAAHHAAA.....",
        "...AA.AA.AA.....",
        "......LL........",
        ".....L..L.......",
        "....BB..BB......",
    ]
}

# ... (Rest of code)

# ============================================
# ADVANCED ENEMY GENERATORS (Bitmap Based)
# ============================================

def draw_advanced_slime(color_base=PALETTE["slime_green"]):
    s = create_surface()
    # Translucent body
    body_color = (*color_base[:3], 200)
    pygame.draw.circle(s, body_color, (16, 20), 10) # Base
    pygame.draw.circle(s, body_color, (16, 16), 8) # Upper

    # Core (Darker)
    core_color = (max(0, color_base[0]-50), max(0, color_base[1]-50), max(0, color_base[2]-50))
    pygame.draw.circle(s, core_color, (16, 18), 5)

    # Highlight (Shiny)
    pygame.draw.ellipse(s, (255, 255, 255, 180), (10, 12, 6, 6))

    # Eyes
    draw_pixel(s, PALETTE["black"], (13, 16))
    draw_pixel(s, PALETTE["black"], (19, 16))

    return s

def draw_bitmap_enemy(name, colors):
    s = create_surface()
    if name not in TEMPLATES:
        # Fallback to generic shape if template missing
        pygame.draw.circle(s, colors.get("H", (100,100,100)), (16,16), 10)
        return s

    template = TEMPLATES[name]
    # Center the template
    h = len(template)
    w = len(template[0])
    off_x = (32 - w * 2) // 2 # Scale 2x essentially
    off_y = (32 - h * 2) // 2

    # Draw scaled 2x for pixel art look
    for y, row in enumerate(template):
        for x, char in enumerate(row):
            if char in colors:
                color = colors[char]
                # Draw 2x2 block
                pygame.draw.rect(s, color, (off_x + x*2, off_y + y*2, 2, 2))

    return s

def draw_advanced_werewolf():
    colors = {
        "H": PALETTE["brown"],      # Hair/Fur
        "Y": PALETTE["red"],        # Eye (Yellow/Red)
        "C": PALETTE["light_grey"]  # Claws
    }
    return draw_bitmap_enemy("werewolf", colors)

def draw_advanced_goblin():
    colors = {
        "G": PALETTE["green"],
        "E": PALETTE["light_green"], # Ears
        "Y": PALETTE["gold"],        # Eyes
        "V": PALETTE["brown"],       # Vest
        "L": PALETTE["green"],       # Legs
        "B": PALETTE["dark_grey"]    # Boots
    }
    return draw_bitmap_enemy("goblin", colors)

def draw_advanced_skeleton():
    colors = {
        "W": PALETTE["bone"],
        "S": PALETTE["bone_shadow"], # Spine
        "P": PALETTE["bone"],        # Pelvis
        "B": PALETTE["bone"]
    }
    return draw_bitmap_enemy("skeleton", colors)

def draw_advanced_orc():
    colors = {
        "H": PALETTE["dark_green"],
        "Y": PALETTE["red"],
        "T": PALETTE["white"],       # Tusks
        "A": PALETTE["light_grey"],  # Armor
        "L": PALETTE["dark_green"],  # Legs
        "B": PALETTE["brown"]        # Boots
    }
    return draw_bitmap_enemy("orc", colors)

# ... (Keep existing generators for non-templated ones like slime, or convert them too)


def draw_advanced_dragon():
    s = create_surface()
    scale = PALETTE["red"]
    belly = PALETTE["orange"]

    # Body
    pygame.draw.ellipse(s, scale, (8, 14, 16, 12))
    pygame.draw.ellipse(s, belly, (10, 16, 12, 8))

    # Neck
    pygame.draw.line(s, scale, (12, 16), (10, 8), 4)

    # Head
    pygame.draw.polygon(s, scale, [(8, 4), (16, 6), (10, 10)])
    draw_pixel(s, PALETTE["gold"], (11, 6)) # Eye

    # Wings
    pygame.draw.polygon(s, PALETTE["dark_red"], [(14, 16), (28, 4), (24, 20)])

    # Tail
    pygame.draw.arc(s, scale, (4, 20, 10, 10), 0, 3.14, 3)

    # Fire breath
    for i in range(5):
        x, y = random.randint(2, 6), random.randint(6, 10)
        draw_pixel(s, PALETTE["gold"], (x, y))

    return s

def draw_advanced_elemental(variant="fire"):
    s = create_surface()
    center = (16, 16)

    if variant == "fire":
        primary = PALETTE["orange"]
        secondary = PALETTE["gold"]
        core = PALETTE["red"]
    elif variant == "ice":
        primary = PALETTE["light_blue"]
        secondary = PALETTE["white"]
        core = PALETTE["blue"]
    else: # void
        primary = PALETTE["dark_purple"]
        secondary = PALETTE["purple"]
        core = PALETTE["black"]

    # Swirling particles
    for i in range(20):
        angle = i * (math.pi / 10) + random.random()
        dist = random.randint(4, 12)
        x = int(center[0] + math.cos(angle) * dist)
        y = int(center[1] + math.sin(angle) * dist)
        color = primary if i % 2 == 0 else secondary
        pygame.draw.circle(s, color, (x, y), random.randint(1, 3))

    # Core face
    pygame.draw.circle(s, core, center, 6)
    draw_pixel(s, PALETTE["white"], (14, 15))
    draw_pixel(s, PALETTE["white"], (18, 15))

    return s

def draw_advanced_humanoid(role="villager"):
    s = create_surface()
    skin = PALETTE["skin_base"]

    # Colors based on role
    if role == "guard":
        cloth = PALETTE["light_grey"] # Armor
        weapon = "spear"
    elif role == "mage":
        cloth = PALETTE["purple"] # Robe
        weapon = "staff"
    elif role == "rogue":
        cloth = PALETTE["brown"] # Leather
        weapon = "dagger"
    else:
        cloth = PALETTE["green"] # Tunic
        weapon = None

    # Legs
    pygame.draw.rect(s, PALETTE["dark_grey"], (12, 22, 3, 8))
    pygame.draw.rect(s, PALETTE["dark_grey"], (17, 22, 3, 8))

    # Body
    pygame.draw.rect(s, cloth, (11, 12, 10, 10), border_radius=2)
    if role == "guard":
        draw_pixel(s, PALETTE["white"], (13, 14)) # Shine

    # Head
    pygame.draw.rect(s, skin, (12, 4, 8, 8), border_radius=2)
    draw_pixel(s, PALETTE["black"], (14, 7))
    draw_pixel(s, PALETTE["black"], (17, 7))

    # Hat/Helmet
    if role == "guard":
        pygame.draw.rect(s, PALETTE["light_grey"], (11, 3, 10, 4))
    elif role == "mage":
        pygame.draw.polygon(s, PALETTE["dark_purple"], [(11, 4), (21, 4), (16, 0)])

    # Arms
    pygame.draw.rect(s, cloth, (8, 13, 3, 8))
    pygame.draw.rect(s, cloth, (21, 13, 3, 8))

    # Weapon
    if weapon == "staff":
        pygame.draw.line(s, PALETTE["brown"], (22, 24), (22, 4), 2)
        draw_sphere(s, PALETTE["red"], (22, 4), 3)
    elif weapon == "spear":
        pygame.draw.line(s, PALETTE["brown"], (22, 24), (22, 4), 1)
        pygame.draw.polygon(s, PALETTE["light_grey"], [(21, 4), (23, 4), (22, 0)])
    elif weapon == "dagger":
        pygame.draw.line(s, PALETTE["light_grey"], (22, 18), (25, 15), 2)

    return s

def draw_advanced_wolf():
    s = create_surface()
    fur = PALETTE["grey"]

    # Body
    pygame.draw.ellipse(s, fur, (8, 12, 16, 10))
    # Head
    pygame.draw.circle(s, fur, (22, 14), 6)
    # Snout
    pygame.draw.polygon(s, fur, [(24, 12), (30, 14), (26, 16)])
    # Ears
    pygame.draw.polygon(s, fur, [(20, 8), (22, 10), (18, 10)])

    # Legs
    pygame.draw.rect(s, fur, (10, 20, 3, 8))
    pygame.draw.rect(s, fur, (20, 20, 3, 8))

    # Tail
    pygame.draw.polygon(s, fur, [(8, 14), (2, 12), (4, 18)])

    # Eye
    draw_pixel(s, PALETTE["gold"], (24, 13))

    return s

def draw_advanced_werewolf():
    s = create_surface()
    fur = PALETTE["brown"]

    # Hunched Body
    pygame.draw.ellipse(s, fur, (8, 10, 16, 14))

    # Head
    pygame.draw.circle(s, fur, (16, 8), 6)
    # Snout
    pygame.draw.rect(s, fur, (14, 10, 4, 4))
    # Ears (Pointy)
    pygame.draw.polygon(s, fur, [(12, 6), (10, 2), (14, 6)])
    pygame.draw.polygon(s, fur, [(20, 6), (22, 2), (18, 6)])

    # Arms (Long)
    pygame.draw.line(s, fur, (10, 14), (4, 24), 3)
    pygame.draw.line(s, fur, (22, 14), (28, 24), 3)

    # Legs (Digitigrade)
    pygame.draw.line(s, fur, (12, 22), (10, 30), 3)
    pygame.draw.line(s, fur, (20, 22), (22, 30), 3)

    # Claws
    draw_pixel(s, PALETTE["light_grey"], (4, 25))
    draw_pixel(s, PALETTE["light_grey"], (28, 25))

    # Eyes
    draw_pixel(s, PALETTE["red"], (14, 7))
    draw_pixel(s, PALETTE["red"], (18, 7))

    return s

# ============================================
# BASIC GENERATORS (Legacy/Simple)
# ============================================

def draw_spider():
    s = create_surface()
    body = PALETTE["black"]
    # Legs
    for i in range(4):
        y = 8 + i * 6
        pygame.draw.line(s, body, (16, 16), (4, y), 1)
        pygame.draw.line(s, body, (16, 16), (28, y), 1)
    pygame.draw.circle(s, body, (16, 16), 6)
    draw_pixel(s, PALETTE["red"], (15, 14))
    draw_pixel(s, PALETTE["red"], (17, 14))
    return s

def draw_ghost():
    s = create_surface()
    # Layered transparency
    for i in range(5):
        alpha = 150 - i * 30
        color = (*PALETTE["light_blue"][:3], alpha)
        radius = 12 - i
        pygame.draw.circle(s, color, (16, 14), radius)
    # Face
    draw_pixel(s, PALETTE["black"], (13, 12))
    draw_pixel(s, PALETTE["black"], (19, 12))
    return s

def draw_bat():
    s = create_surface()
    color = PALETTE["dark_grey"]
    pygame.draw.circle(s, color, (16, 16), 6)
    pygame.draw.polygon(s, color, [(10, 16), (2, 10), (6, 20)])
    pygame.draw.polygon(s, color, [(22, 16), (30, 10), (26, 20)])
    draw_pixel(s, PALETTE["red"], (14, 15))
    draw_pixel(s, PALETTE["red"], (18, 15))
    return s

def draw_troll():
    s = create_surface()
    skin = PALETTE["grey"]
    pygame.draw.rect(s, skin, (8, 10, 16, 14))
    pygame.draw.circle(s, skin, (16, 8), 6)
    pygame.draw.rect(s, PALETTE["brown"], (8, 20, 16, 6))
    return s

def draw_imp():
    s = create_surface()
    skin = PALETTE["red"]
    pygame.draw.circle(s, skin, (16, 16), 8)
    draw_pixel(s, PALETTE["gold"], (14, 14))
    draw_pixel(s, PALETTE["gold"], (18, 14))
    return s

def draw_mimic():
    s = create_surface()
    pygame.draw.rect(s, PALETTE["brown"], (6, 10, 20, 14))
    pygame.draw.rect(s, PALETTE["gold"], (6, 10, 20, 14), 1)
    draw_pixel(s, PALETTE["red"], (14, 16))
    draw_pixel(s, PALETTE["red"], (18, 16))
    return s

def draw_golem():
    s = create_surface()
    stone = PALETTE["light_grey"]
    pygame.draw.rect(s, stone, (8, 8, 16, 16))
    draw_pixel(s, PALETTE["cyan"], (12, 12))
    draw_pixel(s, PALETTE["cyan"], (20, 12))
    return s

def draw_mushroom():
    s = create_surface()
    pygame.draw.rect(s, PALETTE["white"], (14, 18, 4, 10))
    pygame.draw.ellipse(s, PALETTE["purple"], (8, 10, 16, 10))
    return s

def draw_harpy():
    s = create_surface()
    skin = PALETTE["skin_base"]
    pygame.draw.circle(s, skin, (16, 10), 6)
    pygame.draw.ellipse(s, PALETTE["light_blue"], (8, 14, 16, 12)) # Wings
    return s

def draw_lizardman():
    s = create_surface()
    scale = PALETTE["green"]
    pygame.draw.rect(s, scale, (12, 10, 8, 14))
    pygame.draw.circle(s, scale, (16, 8), 5)
    return s

def draw_cyclops():
    s = create_surface()
    skin = PALETTE["skin_base"]
    pygame.draw.rect(s, skin, (8, 8, 16, 16))
    pygame.draw.circle(s, PALETTE["white"], (16, 14), 4)
    draw_pixel(s, PALETTE["black"], (16, 14))
    return s

def draw_wyrm():
    s = create_surface()
    pygame.draw.circle(s, PALETTE["green"], (16, 16), 10)
    return s

# ============================================
# UI GENERATOR (Mystic Theme)
# ============================================

def generate_ui():
    print("Generating Detailed UI...")

    # Panel (Nine-slice source 24x24)
    s = create_surface((24, 24))

    # Background: Textured Dark Slate
    bg_color = PALETTE["dark_grey"]
    s.fill(bg_color)
    apply_dither(s, (40, 40, 60), 0.3)

    # Border System
    # 1. Outer dark edge
    pygame.draw.rect(s, PALETTE["black"], (0, 0, 24, 24), 1)

    # 2. Gold Trim (3D effect)
    # Top/Left = Light Gold
    pygame.draw.line(s, PALETTE["gold"], (1, 1), (22, 1))
    pygame.draw.line(s, PALETTE["gold"], (1, 1), (1, 22))
    # Bottom/Right = Dark Gold
    pygame.draw.line(s, PALETTE["orange"], (1, 22), (22, 22))
    pygame.draw.line(s, PALETTE["orange"], (22, 1), (22, 22))

    # 3. Inner Bevel
    pygame.draw.rect(s, (50, 50, 70), (2, 2, 20, 20), 1)

    # 4. Fancy Corners
    for cx, cy in [(1,1), (22,1), (1,22), (22,22)]:
        draw_pixel(s, PALETTE["white"], (cx, cy))

    save_img(s, "ui_panel")

    # Cursor (Gauntlet)
    c = create_surface((16, 16))
    # Outline
    points = [(2, 2), (12, 8), (6, 12)]
    pygame.draw.polygon(c, PALETTE["black"], points)
    # Fill
    inner_points = [(3, 3), (10, 8), (6, 10)]
    pygame.draw.polygon(c, PALETTE["cyan"], inner_points)
    save_img(c, "ui_cursor")

def save_img(s, name):
    pygame.image.save(s, os.path.join(SPRITE_DIR, f"{name}.png"))

# ============================================
# MAIN GENERATION LOOP
# ============================================

def generate_all_sprites():
    print("Generating all sprites with high detail...")
    generate_tiles()
    generate_ui()

    # Mapping for all enemies in data/encounters.json
    # Format: "filename": (function, kwargs)
    mapping = {
        # Basic
        "slime": (draw_advanced_slime, {}),
        "goblin": (draw_advanced_goblin, {}),
        "orc": (draw_advanced_orc, {}),
        "wolf": (draw_advanced_wolf, {}),
        "spider": (draw_spider, {}), # Reuse basic but polished
        "skeleton": (draw_advanced_skeleton, {}),
        "ghost": (draw_ghost, {}),
        "bat": (draw_bat, {}),
        "troll": (draw_troll, {}),
        "imp": (draw_imp, {}),
        "werewolf": (draw_advanced_werewolf, {}),

        # Variants
        "mimic": (draw_mimic, {}),
        "golem": (draw_golem, {}),
        "mushroom": (draw_mushroom, {}),
        "harpy": (draw_harpy, {}),
        "lizardman": (draw_lizardman, {}),
        "cyclops": (draw_cyclops, {}),

        # Humanoids
        "bandit": (draw_advanced_humanoid, {"role": "rogue"}),
        "witch": (draw_advanced_humanoid, {"role": "mage"}),
        "necromancer": (draw_advanced_humanoid, {"role": "mage"}),
        "vampire": (draw_advanced_humanoid, {"role": "mage"}),
        "dark_knight": (draw_advanced_humanoid, {"role": "guard"}),

        # Elementals
        "fire_elemental": (draw_advanced_elemental, {"variant": "fire"}),
        "ice_elemental": (draw_advanced_elemental, {"variant": "ice"}),

        # Special/Bosses
        "demon": (draw_advanced_elemental, {"variant": "fire"}), # Placeholder
        "wraith": (draw_ghost, {}),
        "snake": (draw_wyrm, {}),
        "boss": (draw_advanced_orc, {}),
        "boss_wyrm": (draw_advanced_dragon, {}),
        "boss_shadow": (draw_advanced_elemental, {"variant": "void"}),
        "boss_unknown": (draw_advanced_elemental, {"variant": "void"}),
        "boss_champion": (draw_advanced_humanoid, {"role": "guard"}),
        "boss_void": (draw_advanced_elemental, {"variant": "void"}),
        "boss_primordial": (draw_advanced_elemental, {"variant": "fire"}),
        "mirror_player": (draw_advanced_humanoid, {"role": "guard"}),

        # Player Characters (reusing humanoid gen)
        "player_warrior": (draw_advanced_humanoid, {"role": "guard"}),
        "player_mage": (draw_advanced_humanoid, {"role": "mage"}),
        "player_rogue": (draw_advanced_humanoid, {"role": "rogue"}),
        "player_cleric": (draw_advanced_humanoid, {"role": "villager"}),
        "player": (draw_advanced_humanoid, {"role": "guard"}),

        # NPCs
        "npc_villager": (draw_advanced_humanoid, {"role": "villager"}),
        "npc_guard": (draw_advanced_humanoid, {"role": "guard"}),
        "npc_merchant": (draw_advanced_humanoid, {"role": "villager"}),
        "npc_default": (draw_advanced_humanoid, {"role": "villager"}),
        "party_luna": (draw_advanced_humanoid, {"role": "mage"}),
        "party_brock": (draw_advanced_humanoid, {"role": "guard"}),
        "party_sage": (draw_advanced_humanoid, {"role": "mage"}),
    }

    for name, (func, kwargs) in mapping.items():
        s = func(**kwargs)
        save_img(s, name)

    # Fallback
    save_img(draw_advanced_slime(), "enemy")

    print("All sprites regenerated successfully.")

if __name__ == "__main__":
    generate_all_sprites()
