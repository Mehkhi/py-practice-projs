import argparse
import json
from pathlib import Path

# Configuration for buildings
BUILDINGS = {
    "riverside_town": [
        {
            "name": "Riverside Blacksmith",
            "map_id": "riverside_blacksmith",
            "npc_id": "riverside_blacksmith",
            "town_x": 3, "town_y": 4, "width": 5, "height": 4,
            "door_rel_x": 2, "door_rel_y": 3,
            "interior_npc_x": 4, "interior_npc_y": 2
        },
        {
            "name": "Riverside Inn",
            "map_id": "riverside_inn",
            "npc_id": "riverside_innkeeper",
            "town_x": 7, "town_y": 5, "width": 5, "height": 4,
            "door_rel_x": 2, "door_rel_y": 3,
            "interior_npc_x": 4, "interior_npc_y": 2
        },
        {
            "name": "Riverside Merchant",
            "map_id": "riverside_merchant",
            "npc_id": "riverside_merchant",
            "town_x": 5, "town_y": 10, "width": 5, "height": 4,
            "door_rel_x": 2, "door_rel_y": 3,
            "interior_npc_x": 4, "interior_npc_y": 2
        },
        {
            "name": "Riverside Fisherman",
            "map_id": "riverside_fisherman",
            "npc_id": "riverside_fisherman",
            "town_x": 10, "town_y": 8, "width": 5, "height": 4,
            "door_rel_x": 2, "door_rel_y": 3,
            "interior_npc_x": 4, "interior_npc_y": 2
        }
    ],
    "shadowfen_town": [
        {
            "name": "Shadowfen Alchemist",
            "map_id": "shadowfen_alchemist",
            "npc_id": "shadowfen_alchemist",
            "town_x": 5, "town_y": 4, "width": 5, "height": 4,
            "door_rel_x": 2, "door_rel_y": 3,
            "interior_npc_x": 4, "interior_npc_y": 2
        },
        {
            "name": "Shadowfen Inn",
            "map_id": "shadowfen_inn",
            "npc_id": "shadowfen_innkeeper",
            "town_x": 7, "town_y": 6, "width": 5, "height": 4,
            "door_rel_x": 2, "door_rel_y": 3,
            "interior_npc_x": 4, "interior_npc_y": 2
        },
        {
            "name": "Shadowfen Hunter",
            "map_id": "shadowfen_hunter",
            "npc_id": "shadowfen_hunter",
            "town_x": 10, "town_y": 10, "width": 5, "height": 4,
            "door_rel_x": 2, "door_rel_y": 3,
            "interior_npc_x": 4, "interior_npc_y": 2
        },
        {
            "name": "Shadowfen Potion Shop",
            "map_id": "shadowfen_potion",
            "npc_id": "shadowfen_potion_seller",
            "town_x": 8, "town_y": 12, "width": 5, "height": 4,
            "door_rel_x": 2, "door_rel_y": 3,
            "interior_npc_x": 4, "interior_npc_y": 2
        }
    ]
}

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_MAPS_DIR = BASE_DIR / "data" / "maps"


def create_interior_map(config, town_id, output_dir: Path, dry_run: bool):
    width = 8
    height = 8

    # Create tiles
    tiles = []
    for y in range(height):
        row = []
        for x in range(width):
            if x == 0 or x == width - 1 or y == 0 or y == height - 1:
                row.append({"tile_id": "stone_wall", "walkable": False, "sprite_id": "stone_wall"})
            else:
                row.append({"tile_id": "stone_floor", "walkable": True, "sprite_id": "stone_floor"})
        tiles.append(row)

    # Create warp back to town
    warps = [
        {
            "x": 3, "y": 7,
            "target_map_id": town_id,
            "target_x": config['town_x'] + config['door_rel_x'],
            "target_y": config['town_y'] + config['door_rel_y'] + 1
        },
        {
            "x": 4, "y": 7,
            "target_map_id": town_id,
            "target_x": config['town_x'] + config['door_rel_x'],
            "target_y": config['town_y'] + config['door_rel_y'] + 1
        }
    ]

    # Create entity
    entities = [
        {
            "entity_id": config['npc_id'],
            "x": config['interior_npc_x'],
            "y": config['interior_npc_y']
        }
    ]

    map_data = {
        "map_id": config['map_id'],
        "name": config['name'],
        "width": width,
        "height": height,
        "tiles": tiles,
        "warps": warps,
        "triggers": [],
        "entities": entities,
        "enemy_spawns": [],
        "props": []
    }

    path = output_dir / f"{config['map_id']}.json"
    if dry_run:
        print(f"[dry-run] Would write {path}")
        return

    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        json.dump(map_data, f, indent=2)
    print(f"Created {path}")

def update_town_map(town_id, buildings, output_dir: Path, dry_run: bool):
    path = output_dir / f"{town_id}.json"
    if not path.exists():
        raise FileNotFoundError(f"Missing town map to update: {path}")

    with open(path, 'r') as f:
        data = json.load(f)

    # Helper to set tile
    def set_tile(x, y, tile_id, walkable, sprite_id):
        if 0 <= y < len(data['tiles']) and 0 <= x < len(data['tiles'][0]):
            data['tiles'][y][x] = {
                "tile_id": tile_id,
                "walkable": walkable,
                "sprite_id": sprite_id
            }

    npcs_to_remove = []

    for b in buildings:
        # Determine style based on town name or random
        is_shadowfen = "shadowfen" in town_id

        roof_tile = "roof_blue" if is_shadowfen else "roof_red"
        wall_tile = "wall_wood" if is_shadowfen else "wall_brick"

        # Build structure
        for y in range(b['town_y'], b['town_y'] + b['height']):
            for x in range(b['town_x'], b['town_x'] + b['width']):
                rel_y = y - b['town_y']
                rel_x = x - b['town_x']

                # Roof (top row)
                if rel_y == 0:
                    set_tile(x, y, roof_tile, False, roof_tile)
                # Walls (rest)
                else:
                    # Add windows on the second row, but not on corners
                    if rel_y == 1 and 0 < rel_x < b['width'] - 1:
                         # Middle of wall could have a window
                         if rel_x % 2 == 1:
                             set_tile(x, y, wall_tile, False, "window_lit")
                         else:
                             set_tile(x, y, wall_tile, False, wall_tile)
                    else:
                        set_tile(x, y, wall_tile, False, wall_tile)

        # Build door
        door_x = b['town_x'] + b['door_rel_x']
        door_y = b['town_y'] + b['door_rel_y']
        set_tile(door_x, door_y, "stone_floor", True, "door_closed")

        # Add warp
        data['warps'].append({
            "x": door_x,
            "y": door_y,
            "target_map_id": b['map_id'],
            "target_x": 4,
            "target_y": 7
        })

        npcs_to_remove.append(b['npc_id'])

    # Remove NPCs
    data['entities'] = [e for e in data['entities'] if e['entity_id'] not in npcs_to_remove]

    if dry_run:
        print(f"[dry-run] Would update {path}")
        return

    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Updated {path}")

def main():
    parser = argparse.ArgumentParser(
        description="Generate building interiors and wire up town maps."
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_MAPS_DIR),
        help="Directory containing map JSON files (default: data/maps)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview writes without modifying files",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir).expanduser().resolve()
    if not output_dir.exists():
        raise SystemExit(f"Output directory not found: {output_dir}")

    for town_id, buildings in BUILDINGS.items():
        for b in buildings:
            create_interior_map(b, town_id, output_dir, args.dry_run)
        update_town_map(town_id, buildings, output_dir, args.dry_run)

    if args.dry_run:
        print("\nDry run complete - no files were written.")

if __name__ == "__main__":
    main()
