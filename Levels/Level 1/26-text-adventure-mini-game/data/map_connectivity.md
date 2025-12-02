# Map Connectivity Documentation

This document describes the map connectivity structure, dead ends, and special cases in the game world.

## Map Categories

### Starting Area
- **forest_path**: The starting map where the player begins the game.

### Towns
- **riverside_town**: Starting town, accessible from forest_path
- **hillcrest_town**: Mountain town, accessible via mountain_pass
- **shadowfen_town**: Swamp town, accessible via murky_swamp
- **nighthaven_city**: Dark city, accessible via haunted_crypt

### Cities
- **ironhold_city**: Industrial city, accessible via frozen_tundra
- **crystalspire_city**: Crystal city, accessible via ancient_ruins
- **sunharbor_city**: Desert port city, accessible via desert_oasis

### Overworld Areas
- **mountain_pass**: Mountain path connecting multiple areas
- **desert_oasis**: Desert area with oasis
- **murky_swamp**: Swamp area
- **frozen_tundra**: Frozen wasteland
- **secret_garden**: Hidden garden area (conditional access)

### Dungeons
- **dark_cave**: Starting dungeon, accessible from forest_path (conditional)
- **ancient_ruins**: Ancient ruins with multiple exits
- **haunted_crypt**: Crypt with undead enemies
- **volcanic_crater**: Volcanic area
- **demon_fortress**: Final boss area (conditional access only)

### Special Areas
- **treasure_chamber**: Secret treasure room (conditional access only)

### Interior Maps (Buildings)
These maps are accessed from their parent towns and always have return warps:
- **riverside_inn**, **riverside_merchant**, **riverside_blacksmith**, **riverside_fisherman**: Riverside Town buildings
- **hillcrest_inn**, **hillcrest_bakery**: Hillcrest Town buildings
- **shadowfen_inn**, **shadowfen_alchemist**, **shadowfen_hunter**, **shadowfen_potion**: Shadowfen Town buildings

## Connectivity Analysis

### Dead Ends
**None found.** All maps have at least one exit, though some exits may be conditional.

### Disconnected Maps
The following maps are unreachable from the starting map (`forest_path`) via non-conditional warps:
- **demon_fortress**: Only accessible via conditional warps from volcanic_crater or treasure_chamber
- **treasure_chamber**: Only accessible via conditional warps from ancient_ruins, dark_cave, or demon_fortress

These maps are intentionally gated behind quest flags or special conditions, making them late-game or secret areas.

### Conditional Warps
Many warps have requirements (flags, items, or blocked-by flags). These include:
- **forest_path → dark_cave**: Requires `forest_wolves_cleared` flag
- **forest_path → secret_garden**: Conditional
- **forest_path → mountain_pass**: Conditional
- **forest_path → desert_oasis**: Conditional
- **ancient_ruins → treasure_chamber**: Conditional
- **ancient_ruins → haunted_crypt**: Conditional
- **dark_cave → treasure_chamber**: Conditional
- **dark_cave → murky_swamp**: Conditional
- **demon_fortress → treasure_chamber**: Conditional
- **desert_oasis → haunted_crypt**: Conditional
- **frozen_tundra → volcanic_crater**: Conditional
- **haunted_crypt → frozen_tundra**: Conditional
- **mountain_pass → ancient_ruins**: Conditional
- **mountain_pass → frozen_tundra**: Conditional
- **murky_swamp → ancient_ruins**: Conditional
- **secret_garden → mountain_pass**: Conditional
- **volcanic_crater → demon_fortress**: Conditional

### Map Graph Structure
The world is structured as a hub-and-spoke model with towns as hubs:
- **forest_path** (starting area) connects to riverside_town and several conditional areas
- **riverside_town** connects to forest_path, ironhold_city, and interior buildings
- **mountain_pass** serves as a central connector between multiple regions
- **ancient_ruins** connects to multiple areas including crystalspire_city
- Interior maps (buildings) are always bidirectional with their parent towns

## Special Cases

### Interior Maps
Interior maps (buildings) typically have:
- Two warps at coordinates (3, 7) and (4, 7) that return to the parent town
- These warps may appear on non-walkable tiles (walls/doors), which is expected behavior
- The parent town has warps to enter these buildings at various coordinates

### Boss/Secret Areas
- **demon_fortress**: Final boss area, only accessible after meeting certain conditions
- **treasure_chamber**: Secret treasure room, accessible via multiple conditional paths
- These areas are intentionally disconnected from the main world graph to maintain game progression

### Quest-Gated Areas
Several areas are gated behind quest flags:
- **dark_cave**: Requires `forest_wolves_cleared` flag
- Other conditional warps may require specific flags, items, or quest completion

## Notes

- All maps are properly connected via warps
- No orphaned maps (all maps are referenced as warp targets)
- Interior building maps are expected to have warps on non-walkable tiles (doors/walls)
- Conditional warps provide progression gating and quest-based access control
