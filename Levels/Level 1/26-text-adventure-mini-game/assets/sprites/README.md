# Sprite Assets Documentation

This directory contains all sprite assets used in the game. Sprites are automatically loaded by the `AssetManager` class and can be referenced by their filename (without extension).

## Directory Structure

- **`assets/sprites/`** - Main sprite directory (loaded recursively)
  - Character sprites (player, NPCs, enemies)
  - Item icons
  - UI elements
  - Background images
  - Status effect icons
  - Map props and decorations
- **`assets/sprites/portraits/`** - Character portrait images
- **`assets/tilesets/default/`** - Tile sprites for map rendering

## Placeholder System

When a sprite is requested but doesn't exist as a file, the `AssetManager._make_placeholder()` function automatically generates a placeholder sprite. This ensures the game never crashes due to missing sprites.

### How Placeholders Work

The placeholder system uses a hash-based color generation algorithm:

1. **Color Generation**: The sprite ID is hashed to generate a consistent color palette
   - Colors are clamped to a visible range (50-205) to avoid near-black or near-white colors
2. **Visual Design**: Creates a pixel-art styled character shape with:
   - A primary color (from hash, clamped for visibility)
   - An accent color (darker version for contrast)
   - A white border outline for visibility
   - A head (circle) and body (oval) shape
   - Transparent corners (not a filled rectangle)
3. **Size**: Default size is 16×16 pixels, but placeholders are generated at the requested size for better fidelity

### Example Placeholder Code

```python
def _make_placeholder(self, sprite_id: str, size: Tuple[int, int] = (16, 16)) -> pygame.Surface:
    """Generate a pixel-art styled placeholder with a hash-based palette."""
    # Hash the sprite ID to get consistent colors
    color_hash = hash(sprite_id) % 0xFFFFFF
    # Clamp to 50-205 range for visibility
    primary = (
        50 + ((color_hash >> 16) & 0xFF) % 156,
        50 + ((color_hash >> 8) & 0xFF) % 156,
        50 + (color_hash & 0xFF) % 156
    )
    # Darker accent color for contrast
    accent = (
        max(0, primary[2] - 50),
        max(0, primary[0] - 50),
        max(0, primary[1] - 50)
    )
    # ... generates character shape with head and body
```

### Identifying Placeholders

Placeholder sprites are visually distinct:
- Character-shaped silhouettes (head + body) with colored fill
- White border outline for visibility
- Transparent corners (not filled rectangles)
- Consistent appearance for the same sprite ID
- Different colors for different sprite IDs
- Colors in a visible mid-range (never too dark or too light)

To see which sprites are placeholders, check `data/SPRITE_MANIFEST.md` which lists all requested sprites and identifies which ones are missing.

## Sprite Categories

### Player/Class Sprites
- **Format**: `player_{class}_{subclass}.png` or `class_{class}.png`
- **Size**: 32×32 pixels (base), scaled as needed
- **Examples**: `player_warrior_mage.png`, `class_bard.png`
- **Status**: Most class combinations exist (100+ sprites)

### Party Member Sprites
- **Format**: `party_{name}.png`
- **Size**: 32×32 pixels
- **Examples**: `party_luna.png`, `party_brock.png`, `party_sage.png`
- **Status**: All 3 party members have sprites

### NPC Sprites
- **Format**: `npc_{type}.png`
- **Size**: 32×32 pixels
- **Examples**: `npc_default.png`, `npc_merchant.png`, `npc_guard.png`
- **Status**: Most NPCs use `npc_default`, some have unique sprites

### Enemy Sprites
- **Format**: `enemy_{type}.png` or just `{type}.png`
- **Size**: 32×32 pixels
- **Examples**: `enemy_slime.png`, `boss.png`, `demon.png`
- **Status**: Most enemies have sprites

### Background Sprites
- **Format**: `bg_{biome}.png`
- **Size**: Variable (typically 640×480 or larger, scaled to screen)
- **Examples**: `bg_forest.png`, `bg_cave.png`, `bg_mountain.png`
- **Status**: 7 biome backgrounds exist

### Item Sprites
- **Format**: `item_{type}.png`
- **Size**: 32×32 pixels
- **Examples**: `item_sword.png`, `item_potion_health.png`, `item_key.png`
- **Status**: Some items use `item_default` placeholder

### UI Sprites
- **Format**: `ui_{element}.png`
- **Size**: Variable (typically 24×24 for nine-slice panels)
- **Examples**: `ui_panel.png`, `ui_cursor.png`
- **Status**: Core UI elements exist

### Status Effect Sprites
- **Format**: `status_{effect}.png`
- **Size**: 16×16 pixels
- **Examples**: `status_poison.png`, `status_bleed.png`, `status_terror.png`
- **Status**: 4 status effect icons exist

### Tile Sprites
- **Location**: `assets/tilesets/default/`
- **Size**: 16×16 pixels (base tile size)
- **Format**: `{terrain_type}.png` or `{terrain_type}_{variant}.png`
- **Examples**: `grass.png`, `stone.png`, `water.png`, `wall_1.png`
- **Status**: Comprehensive tile set exists with variants

### Map Props
- **Format**: `prop_{type}.png`
- **Size**: 32×32 pixels
- **Examples**: `prop_barrel.png`, `prop_crate.png`, `prop_statue.png`
- **Status**: 15+ prop sprites exist

## Sprite Requirements

### File Format
- **Supported**: PNG (recommended), JPG, BMP
- **Transparency**: PNG with alpha channel recommended for sprites with transparency
- **Color Depth**: 32-bit RGBA recommended

### Naming Conventions
- Use lowercase letters, numbers, and underscores only
- No spaces or special characters
- Descriptive names that match sprite ID usage in code
- Example: `enemy_slime.png` not `Enemy Slime.png`

### Size Guidelines
- **Character Sprites**: 32×32 pixels (base size, scaled as needed)
- **Item Icons**: 32×32 pixels
- **Status Icons**: 16×16 pixels
- **Tiles**: 16×16 pixels
- **UI Elements**: Variable (match design requirements)
- **Backgrounds**: Variable (typically 640×480 or screen resolution)

### Style Guidelines
- **Pixel Art**: Game uses pixel-art aesthetic
- **Consistency**: Maintain consistent style across sprite categories
- **Color Palette**: Use colors that match the game's theme
- **Transparency**: Use alpha channel for non-rectangular sprites

## Adding New Sprites

1. **Place File**: Add sprite file to appropriate directory:
   - Character/enemy/item sprites → `assets/sprites/`
   - Portraits → `assets/sprites/portraits/`
   - Tiles → `assets/tilesets/default/`

2. **Naming**: Use the exact sprite ID expected by the code
   - Check `data/SPRITE_MANIFEST.md` for requested sprite IDs
   - Match naming conventions (lowercase, underscores)

3. **Reference**: Update data files (JSON) to reference the sprite:
   - `data/entities.json` for NPCs/enemies
   - `data/encounters.json` for battle enemies
   - `data/items.json` for items
   - Map JSON files for tiles/props

4. **Test**: The sprite will be automatically loaded on next game start
   - No code changes needed if sprite ID matches
   - Placeholder will be replaced automatically

## Sprite Manifest

For a complete list of all sprites (existing, requested, and placeholders), see:
- **`data/SPRITE_MANIFEST.md`** - Human-readable manifest with categories
- **`data/sprite_manifest.json`** - Machine-readable JSON data

The manifest is generated by running:
```bash
.venv/bin/python3 tools/analyze_sprites.py
```

## Common Issues

### Sprite Not Appearing
- Check that filename matches sprite ID exactly (case-sensitive)
- Verify file is in correct directory
- Check file format is supported (PNG/JPG/BMP)
- Ensure file isn't corrupted

### Placeholder Still Showing
- Verify sprite file exists in correct location
- Check sprite ID in code/data matches filename (without extension)
- Clear any cached assets if using asset caching
- Run sprite analysis tool to verify sprite is detected

### Wrong Sprite Displayed
- Verify sprite ID is unique and not conflicting
- Check that sprite file isn't overwriting another sprite
- Ensure data files reference correct sprite ID

## Tools

- **`tools/analyze_sprites.py`** - Analyzes sprite usage and generates manifest
- **`tools/generate_sprites.py`** - Generates placeholder sprites programmatically

## Notes

- Sprites are loaded recursively from `assets/sprites/` directory
- Subdirectories (like `portraits/`) are automatically scanned
- Sprite IDs are case-sensitive
- Missing sprites automatically use placeholder system (no errors)
- The game will function with placeholders, but real sprites improve visual quality
