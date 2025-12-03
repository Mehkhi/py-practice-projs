#!/usr/bin/env python3
"""
Tool to add tile variety to maps by replacing monotonous tiles with decorative variations.
This creates visually interesting maps while maintaining gameplay consistency.

Safer defaults:
- Resolves paths relative to the repo instead of a hardcoded absolute path
- Supports --dry-run to preview changes without touching disk
- Optional --maps-dir and --seed for flexibility/reproducibility
"""

import argparse
import json
import random
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_MAPS_DIR = BASE_DIR / "data" / "maps"

# Define tile variation mappings for each base tile type
# Format: base_tile -> list of (variant_tile, weight) tuples
TILE_VARIATIONS = {
    "grass": [
        ("grass", 50),           # Keep original grass most common
        ("grass_tall", 15),      # Tall grass patches
        ("grass_flowers", 10),   # Flowers scattered throughout
        ("grass_dark", 10),      # Shaded areas
        ("flower_grass", 5),     # Dense flower patches
        ("puddle", 3),           # Occasional puddles
        ("dirt_leaves", 4),      # Fallen leaves
        ("roots", 3),            # Tree roots
    ],
    "stone": [
        ("stone", 60),
        ("stone_floor", 20),
        ("stone_cracked", 15),
        ("moss", 5),
    ],
    "sand": [
        ("sand", 65),
        ("sand_rocky", 25),
        ("dirt", 10),
    ],
    "snow": [
        ("snow", 60),
        ("snow_footprints", 15),
        ("ice", 20),
        ("stone", 5),
    ],
    "swamp": [
        ("swamp", 55),
        ("puddle", 20),
        ("moss", 15),
        ("grass_dark", 10),
    ],
    "ruins": [
        ("ruins", 50),
        ("stone_cracked", 25),
        ("moss", 15),
        ("stone", 10),
    ],
    "lava": [
        ("lava", 60),
        ("lava_rock", 40),
    ],
    "stone_floor": [
        ("stone_floor", 70),
        ("stone_cracked", 20),
        ("stone", 10),
    ],
    "gold_floor": [
        ("gold_floor", 85),
        ("stone_floor", 15),
    ],
}

# Map-specific themes that influence tile distribution
MAP_THEMES = {
    "forest_path": {
        "grass": [("grass", 40), ("grass_tall", 20), ("grass_flowers", 15),
                  ("grass_dark", 10), ("dirt_leaves", 8), ("roots", 5), ("puddle", 2)],
        "dirt_path": [("dirt_path", 70), ("path_cobble", 15), ("dirt", 10), ("dirt_leaves", 5)],
    },
    "secret_garden": {
        "grass": [("grass", 25), ("grass_flowers", 30), ("flower_grass", 25),
                  ("grass_tall", 10), ("puddle", 5), ("moss", 5)],
    },
    "dark_cave": {
        "stone": [("stone", 45), ("stone_cracked", 25), ("moss", 20), ("puddle", 10)],
    },
    "murky_swamp": {
        "swamp": [("swamp", 45), ("puddle", 25), ("moss", 15), ("grass_dark", 10), ("roots", 5)],
    },
    "frozen_tundra": {
        "snow": [("snow", 50), ("ice", 25), ("snow_footprints", 15), ("stone", 10)],
    },
    "desert_oasis": {
        "sand": [("sand", 55), ("sand_rocky", 30), ("dirt", 10), ("puddle", 5)],
    },
    "volcanic_crater": {
        "lava": [("lava", 55), ("lava_rock", 45)],
        "stone": [("lava_rock", 60), ("stone", 30), ("stone_cracked", 10)],
    },
    "ancient_ruins": {
        "ruins": [("ruins", 40), ("stone_cracked", 30), ("moss", 20), ("stone", 10)],
        "stone": [("stone_cracked", 40), ("stone", 35), ("moss", 15), ("ruins", 10)],
    },
    "haunted_crypt": {
        "stone": [("stone", 40), ("stone_cracked", 35), ("moss", 20), ("puddle", 5)],
    },
    "mountain_pass": {
        "stone": [("stone", 55), ("mountain", 25), ("stone_cracked", 15), ("snow", 5)],
        "grass": [("grass", 50), ("grass_dark", 25), ("moss", 15), ("roots", 10)],
    },
    "treasure_chamber": {
        "gold_floor": [("gold_floor", 80), ("stone_floor", 20)],
        "stone": [("stone_floor", 60), ("stone", 30), ("stone_cracked", 10)],
    },
    "demon_fortress": {
        "stone": [("stone", 40), ("stone_cracked", 30), ("lava_rock", 20), ("stone_wall", 10)],
    },
}


def weighted_choice(variants):
    """Choose a tile variant based on weights."""
    total = sum(weight for _, weight in variants)
    r = random.uniform(0, total)
    cumulative = 0
    for tile_id, weight in variants:
        cumulative += weight
        if r <= cumulative:
            return tile_id
    return variants[0][0]  # Fallback


def get_variants_for_tile(tile_id, map_id):
    """Get appropriate variants for a tile based on map theme."""
    # Check map-specific theme first
    if map_id in MAP_THEMES:
        theme = MAP_THEMES[map_id]
        if tile_id in theme:
            return theme[tile_id]

    # Fall back to global variations
    if tile_id in TILE_VARIATIONS:
        return TILE_VARIATIONS[tile_id]

    # No variations - keep original
    return [(tile_id, 100)]


def add_variety_to_map(map_data):
    """Add tile variety to a map's tiles."""
    map_id = map_data.get("map_id", "unknown")
    tiles = map_data.get("tiles", [])

    modified = False
    for row_idx, row in enumerate(tiles):
        for col_idx, tile in enumerate(row):
            original_tile_id = tile.get("tile_id")

            # Get variants and choose one
            variants = get_variants_for_tile(original_tile_id, map_id)
            new_tile_id = weighted_choice(variants)

            if new_tile_id != original_tile_id:
                tile["tile_id"] = new_tile_id
                tile["sprite_id"] = new_tile_id  # Update sprite to match
                modified = True

    return modified


def process_map_file(map_path, dry_run=False):
    """Process a single map file to add variety."""
    with open(map_path, 'r') as f:
        map_data = json.load(f)

    map_id = map_data.get("map_id", map_path.stem)

    # Add variety
    modified = add_variety_to_map(map_data)

    if modified and not dry_run:
        # Save updated map
        with open(map_path, 'w') as f:
            json.dump(map_data, f, indent=2)
        return True

    return False


def analyze_map(map_path):
    """Analyze tile distribution in a map."""
    with open(map_path, 'r') as f:
        map_data = json.load(f)

    tile_counts = {}
    for row in map_data.get("tiles", []):
        for tile in row:
            tile_id = tile.get("tile_id")
            tile_counts[tile_id] = tile_counts.get(tile_id, 0) + 1

    return tile_counts


def main():
    parser = argparse.ArgumentParser(description="Add decorative tile variety to maps.")
    parser.add_argument(
        "--maps-dir",
        default=str(DEFAULT_MAPS_DIR),
        help="Directory containing map JSON files (default: data/maps relative to repo)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for deterministic variants (default: 42)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without writing files",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("MAP TILE VARIETY GENERATOR")
    print("=" * 60)

    random.seed(args.seed)

    maps_dir = Path(args.maps_dir).expanduser().resolve()
    if not maps_dir.exists():
        raise SystemExit(f"Map directory not found: {maps_dir}")

    map_files = list(maps_dir.glob("*.json"))
    print(f"\nFound {len(map_files)} map files in {maps_dir}")

    for map_path in sorted(map_files):
        print(f"\n--- Processing: {map_path.name} ---")

        # Analyze before
        before = analyze_map(map_path)
        print(f"Before: {len(before)} unique tiles - {dict(sorted(before.items(), key=lambda x: -x[1])[:5])}...")

        # Add variety
        modified = process_map_file(map_path, dry_run=args.dry_run)

        # Analyze after
        after = analyze_map(map_path)
        print(f"After:  {len(after)} unique tiles - {dict(sorted(after.items(), key=lambda x: -x[1])[:5])}...")

        if modified:
            if args.dry_run:
                print("✓ (dry-run) Would update map with variety")
            else:
                print("✓ Map updated with variety")
        else:
            print("- No changes needed")

    print("\n" + "=" * 60)
    if args.dry_run:
        print("DRY RUN COMPLETE - no files were modified.")
    else:
        print("COMPLETE! All maps have been updated with tile variety.")
    print("=" * 60)


if __name__ == "__main__":
    main()
