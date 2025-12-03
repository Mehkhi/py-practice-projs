"""
Expanded Fantasy Color Palette for Sprite Generation

Contains ~130 carefully selected colors organized by category:
- Skin tones (12 variants)
- Hair colors (10 variants)
- Metals (15 variants)
- Cloth/Leather (20 variants)
- Nature colors (15 variants)
- Elemental colors (20 variants)
- Creature-specific (15 variants)
- Eyes (10 variants)
"""

PALETTE = {
    # =============================================================================
    # SKIN TONES (12 variants)
    # =============================================================================
    "skin_pale": (255, 224, 205),
    "skin_light": (245, 203, 175),
    "skin_medium": (224, 172, 137),
    "skin_tan": (198, 143, 107),
    "skin_brown": (156, 102, 68),
    "skin_dark": (102, 68, 51),
    "skin_orc_light": (143, 168, 95),
    "skin_orc": (107, 142, 71),
    "skin_orc_dark": (71, 107, 47),
    "skin_undead": (180, 190, 175),
    "skin_demon": (180, 80, 80),
    "skin_elemental": (200, 220, 255),

    # =============================================================================
    # HAIR COLORS (10 variants)
    # =============================================================================
    "hair_blonde": (245, 222, 129),
    "hair_brown": (101, 67, 33),
    "hair_black": (35, 30, 35),
    "hair_red": (165, 60, 40),
    "hair_grey": (150, 150, 155),
    "hair_white": (235, 235, 240),
    "hair_blue": (70, 100, 180),
    "hair_green": (60, 120, 70),
    "hair_purple": (100, 60, 130),
    "hair_silver": (192, 200, 210),

    # =============================================================================
    # METALS (15 variants)
    # =============================================================================
    "steel_highlight": (230, 235, 240),
    "steel_base": (180, 185, 195),
    "steel_shadow": (120, 125, 135),
    "steel_dark": (70, 75, 85),
    "gold_highlight": (255, 250, 180),
    "gold_base": (255, 215, 0),
    "gold_shadow": (200, 160, 50),
    "gold_dark": (150, 110, 30),
    "bronze_highlight": (230, 180, 130),
    "bronze_base": (205, 127, 50),
    "bronze_shadow": (150, 90, 40),
    "copper_base": (184, 115, 51),
    "silver_base": (192, 192, 210),
    "iron_base": (100, 100, 110),
    "mythril_base": (150, 220, 255),

    # =============================================================================
    # CLOTH/LEATHER (20 variants)
    # =============================================================================
    "cloth_white": (245, 245, 240),
    "cloth_cream": (240, 230, 210),
    "cloth_red": (180, 50, 50),
    "cloth_red_dark": (120, 30, 30),
    "cloth_blue": (50, 80, 150),
    "cloth_blue_dark": (30, 50, 100),
    "cloth_green": (50, 120, 70),
    "cloth_green_dark": (30, 80, 45),
    "cloth_purple": (100, 50, 130),
    "cloth_purple_dark": (60, 30, 90),
    "cloth_yellow": (230, 200, 80),
    "cloth_orange": (220, 130, 50),
    "cloth_brown": (120, 80, 50),
    "cloth_brown_dark": (80, 50, 30),
    "cloth_grey": (130, 130, 135),
    "cloth_black": (40, 40, 45),
    "leather_light": (160, 120, 80),
    "leather_base": (120, 85, 55),
    "leather_dark": (80, 55, 35),
    "leather_black": (45, 35, 30),

    # =============================================================================
    # NATURE COLORS (15 variants)
    # =============================================================================
    "leaf_light": (140, 200, 100),
    "leaf_base": (80, 150, 60),
    "leaf_dark": (50, 100, 40),
    "bark_light": (140, 100, 70),
    "bark_base": (100, 70, 45),
    "bark_dark": (60, 40, 25),
    "moss": (80, 120, 60),
    "vine": (60, 100, 50),
    "flower_red": (220, 60, 80),
    "flower_blue": (80, 120, 200),
    "flower_yellow": (250, 220, 80),
    "flower_purple": (160, 80, 180),
    "mushroom_cap": (180, 60, 60),
    "mushroom_stem": (230, 220, 200),
    "slime_green": (120, 200, 100),

    # =============================================================================
    # ELEMENTAL COLORS (20 variants)
    # =============================================================================
    # Fire
    "fire_white": (255, 255, 220),
    "fire_yellow": (255, 230, 100),
    "fire_orange": (255, 160, 50),
    "fire_red": (220, 80, 30),
    "fire_dark": (150, 40, 20),
    # Ice
    "ice_white": (240, 250, 255),
    "ice_light": (200, 230, 250),
    "ice_base": (150, 200, 230),
    "ice_dark": (80, 140, 180),
    # Lightning
    "lightning_white": (255, 255, 255),
    "lightning_yellow": (255, 255, 150),
    "lightning_blue": (150, 200, 255),
    # Void/Dark
    "void_purple": (60, 30, 80),
    "void_black": (20, 15, 30),
    "void_glow": (150, 80, 200),
    # Holy
    "holy_white": (255, 255, 240),
    "holy_gold": (255, 230, 150),
    "holy_blue": (200, 220, 255),
    # Nature/Earth
    "earth_light": (180, 150, 110),
    "earth_base": (140, 110, 80),

    # =============================================================================
    # CREATURE-SPECIFIC (15 variants)
    # =============================================================================
    "bone_white": (235, 230, 220),
    "bone_shadow": (190, 180, 165),
    "bone_dark": (140, 130, 115),
    "ghost_blue": (180, 200, 230),
    "ghost_glow": (220, 235, 255),
    "blood_red": (150, 20, 30),
    "blood_dark": (100, 15, 20),
    "scale_green": (80, 130, 70),
    "scale_blue": (60, 100, 140),
    "scale_red": (160, 60, 50),
    "fur_brown": (130, 95, 65),
    "fur_grey": (140, 140, 145),
    "fur_white": (235, 235, 230),
    "fur_black": (40, 35, 35),
    "chitin_black": (30, 30, 35),
    "feather_white": (250, 250, 245),
    "feather_brown": (140, 100, 70),

    # =============================================================================
    # EYES (10 variants)
    # =============================================================================
    "eye_white": (245, 245, 245),
    "eye_blue": (70, 130, 200),
    "eye_green": (70, 160, 90),
    "eye_brown": (120, 80, 50),
    "eye_red": (200, 50, 50),
    "eye_yellow": (240, 200, 50),
    "eye_purple": (140, 80, 180),
    "eye_glow_red": (255, 100, 100),
    "eye_glow_blue": (100, 180, 255),
    "eye_glow_green": (100, 255, 150),
    "eye_grey": (140, 140, 150),
    "eye_black": (30, 30, 35),

    # =============================================================================
    # UTILITY COLORS
    # =============================================================================
    "black": (0, 0, 0),
    "white": (255, 255, 255),
    "transparent": (0, 0, 0, 0),
}


def get_color(name: str) -> tuple:
    """
    Get a color from the palette by name.

    Args:
        name: Color name in the palette

    Returns:
        RGB or RGBA tuple

    Raises:
        KeyError: If color name not found
    """
    return PALETTE[name]


def get_color_with_alpha(name: str, alpha: int = 255) -> tuple:
    """
    Get a color from the palette with specified alpha.

    Args:
        name: Color name in the palette
        alpha: Alpha value (0-255)

    Returns:
        RGBA tuple
    """
    color = PALETTE[name]
    if len(color) == 4:
        return (color[0], color[1], color[2], alpha)
    return (color[0], color[1], color[2], alpha)


# Color groups for easy iteration
SKIN_TONES = [
    "skin_pale", "skin_light", "skin_medium", "skin_tan",
    "skin_brown", "skin_dark", "skin_orc_light", "skin_orc",
    "skin_orc_dark", "skin_undead", "skin_demon", "skin_elemental"
]

HAIR_COLORS = [
    "hair_blonde", "hair_brown", "hair_black", "hair_red",
    "hair_grey", "hair_white", "hair_blue", "hair_green",
    "hair_purple", "hair_silver"
]

METAL_COLORS = [
    "steel_highlight", "steel_base", "steel_shadow", "steel_dark",
    "gold_highlight", "gold_base", "gold_shadow", "gold_dark",
    "bronze_highlight", "bronze_base", "bronze_shadow",
    "copper_base", "silver_base", "iron_base", "mythril_base"
]

CLOTH_COLORS = [
    "cloth_white", "cloth_cream", "cloth_red", "cloth_red_dark",
    "cloth_blue", "cloth_blue_dark", "cloth_green", "cloth_green_dark",
    "cloth_purple", "cloth_purple_dark", "cloth_yellow", "cloth_orange",
    "cloth_brown", "cloth_brown_dark", "cloth_grey", "cloth_black",
    "leather_light", "leather_base", "leather_dark", "leather_black"
]

ELEMENTAL_FIRE = ["fire_white", "fire_yellow", "fire_orange", "fire_red", "fire_dark"]
ELEMENTAL_ICE = ["ice_white", "ice_light", "ice_base", "ice_dark"]
ELEMENTAL_LIGHTNING = ["lightning_white", "lightning_yellow", "lightning_blue"]
ELEMENTAL_VOID = ["void_purple", "void_black", "void_glow"]
ELEMENTAL_HOLY = ["holy_white", "holy_gold", "holy_blue"]
