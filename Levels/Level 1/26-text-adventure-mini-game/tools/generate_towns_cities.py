#!/usr/bin/env python3
"""Generate town and city maps with NPCs and class-specific quests."""

import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
MAPS_DIR = os.path.join(DATA_DIR, "maps")


def generate_tile_grid(width: int, height: int, tile_id: str = "grass") -> list:
    """Generate a grid of tiles."""
    tile = {"tile_id": tile_id, "walkable": True, "sprite_id": tile_id}
    return [[tile.copy() for _ in range(width)] for _ in range(height)]


def create_map(map_id, name, width, height, tile_type, warps, entities, props):
    """Create a map dictionary."""
    return {
        "map_id": map_id,
        "name": name,
        "width": width,
        "height": height,
        "tiles": generate_tile_grid(width, height, tile_type),
        "warps": warps,
        "triggers": [],
        "entities": entities,
        "enemy_spawns": [],
        "props": props
    }


def main():
    # Towns (15x15)
    towns = [
        ("riverside_town", "Riverside Town", 15, 15, "grass",
         [{"x": 7, "y": 14, "target_map_id": "forest_path", "target_x": 7, "target_y": 0},
          {"x": 0, "y": 7, "target_map_id": "ironhold_city", "target_x": 19, "target_y": 10}],
         [{"entity_id": "riverside_blacksmith", "x": 3, "y": 4},
          {"entity_id": "riverside_fisherman", "x": 10, "y": 8}],
         [{"prop_id": "well_1", "x": 7, "y": 7, "sprite_id": "prop_rock", "solid": True}]),

        ("hillcrest_town", "Hillcrest Town", 15, 15, "grass",
         [{"x": 7, "y": 0, "target_map_id": "mountain_pass", "target_x": 7, "target_y": 14},
          {"x": 14, "y": 7, "target_map_id": "crystalspire_city", "target_x": 0, "target_y": 10}],
         [{"entity_id": "hillcrest_herbalist", "x": 4, "y": 5},
          {"entity_id": "hillcrest_miner", "x": 11, "y": 9}],
         [{"prop_id": "fountain_1", "x": 7, "y": 7, "sprite_id": "prop_rock", "solid": True}]),

        ("shadowfen_town", "Shadowfen Town", 15, 15, "grass",
         [{"x": 7, "y": 14, "target_map_id": "murky_swamp", "target_x": 7, "target_y": 0},
          {"x": 0, "y": 7, "target_map_id": "nighthaven_city", "target_x": 19, "target_y": 10}],
         [{"entity_id": "shadowfen_alchemist", "x": 5, "y": 4},
          {"entity_id": "shadowfen_hunter", "x": 10, "y": 10}],
         [{"prop_id": "cauldron_1", "x": 4, "y": 4, "sprite_id": "prop_rock", "solid": True}])
    ]

    # Cities (20x20)
    cities = [
        ("ironhold_city", "Ironhold City", 20, 20, "grass",
         [{"x": 19, "y": 10, "target_map_id": "riverside_town", "target_x": 0, "target_y": 7},
          {"x": 10, "y": 0, "target_map_id": "frozen_tundra", "target_x": 7, "target_y": 14}],
         [{"entity_id": "ironhold_commander", "x": 10, "y": 5},
          {"entity_id": "ironhold_weaponsmith", "x": 4, "y": 8},
          {"entity_id": "ironhold_arena_master", "x": 15, "y": 12}],
         [{"prop_id": "statue_1", "x": 10, "y": 10, "sprite_id": "prop_rock", "solid": True}]),

        ("crystalspire_city", "Crystalspire City", 20, 20, "grass",
         [{"x": 0, "y": 10, "target_map_id": "hillcrest_town", "target_x": 14, "target_y": 7},
          {"x": 10, "y": 19, "target_map_id": "ancient_ruins", "target_x": 7, "target_y": 0}],
         [{"entity_id": "crystalspire_archmage", "x": 10, "y": 6},
          {"entity_id": "crystalspire_enchanter", "x": 5, "y": 12},
          {"entity_id": "crystalspire_librarian", "x": 15, "y": 8}],
         [{"prop_id": "crystal_1", "x": 10, "y": 10, "sprite_id": "prop_rock", "solid": True}]),

        ("nighthaven_city", "Nighthaven City", 20, 20, "grass",
         [{"x": 19, "y": 10, "target_map_id": "shadowfen_town", "target_x": 0, "target_y": 7},
          {"x": 10, "y": 0, "target_map_id": "haunted_crypt", "target_x": 7, "target_y": 14}],
         [{"entity_id": "nighthaven_shadow_broker", "x": 10, "y": 8},
          {"entity_id": "nighthaven_fence", "x": 5, "y": 14},
          {"entity_id": "nighthaven_informant", "x": 16, "y": 6}],
         [{"prop_id": "fountain_dark_1", "x": 10, "y": 10, "sprite_id": "prop_rock", "solid": True}]),

        ("sunharbor_city", "Sunharbor City", 20, 20, "grass",
         [{"x": 10, "y": 19, "target_map_id": "desert_oasis", "target_x": 7, "target_y": 0},
          {"x": 0, "y": 10, "target_map_id": "volcanic_crater", "target_x": 14, "target_y": 7}],
         [{"entity_id": "sunharbor_high_priest", "x": 10, "y": 5},
          {"entity_id": "sunharbor_merchant_prince", "x": 6, "y": 12},
          {"entity_id": "sunharbor_ship_captain", "x": 15, "y": 15}],
         [{"prop_id": "temple_altar_1", "x": 10, "y": 4, "sprite_id": "prop_rock", "solid": True}])
    ]

    # Generate map files
    for map_data in towns + cities:
        map_dict = create_map(*map_data)
        path = os.path.join(MAPS_DIR, f"{map_data[0]}.json")
        with open(path, "w") as f:
            json.dump(map_dict, f, indent=2)
        print(f"Created: {path}")


if __name__ == "__main__":
    main()
