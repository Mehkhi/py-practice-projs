#!/usr/bin/env python3
"""Analyze sprite usage across the codebase and generate a manifest.

Scans data files, engine code, and existing sprite files to identify:
- All sprite IDs referenced in the codebase
- Existing sprite files
- Placeholder sprites (requested but missing)
- Categorization by type
"""

import json
import os
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Base directory (project root)
BASE_DIR = Path(__file__).parent.parent

# Cache for dynamically loaded enemy IDs
_ENEMY_IDS_CACHE: Set[str] = set()


def load_enemy_ids_from_data() -> Set[str]:
    """Load enemy sprite IDs from data files (encounters.json, entities.json)."""
    global _ENEMY_IDS_CACHE
    if _ENEMY_IDS_CACHE:
        return _ENEMY_IDS_CACHE

    enemy_ids: Set[str] = set()

    # Load from encounters.json
    encounters_path = BASE_DIR / "data" / "encounters.json"
    if encounters_path.exists():
        try:
            with open(encounters_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for encounter in data.get("encounters", {}).values():
                    for enemy in encounter.get("enemies", []):
                        if "sprite_id" in enemy and enemy["sprite_id"]:
                            enemy_ids.add(enemy["sprite_id"])
                        # Also add the enemy type as a potential sprite ID
                        if "type" in enemy and enemy["type"]:
                            enemy_ids.add(enemy["type"])
        except Exception as e:
            print(f"Warning: Failed to parse encounters.json: {e}")

    # Load from entities.json if it has enemies
    entities_path = BASE_DIR / "data" / "entities.json"
    if entities_path.exists():
        try:
            with open(entities_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for entity in data.get("enemies", []):
                    if "sprite_id" in entity and entity["sprite_id"]:
                        enemy_ids.add(entity["sprite_id"])
        except Exception as e:
            print(f"Warning: Failed to parse entities.json: {e}")

    # Add common enemy prefixes that are always enemies
    enemy_ids.add("enemy")
    enemy_ids.add("boss")

    _ENEMY_IDS_CACHE = enemy_ids
    return enemy_ids


def get_existing_sprites() -> Dict[str, Set[str]]:
    """Scan assets directories for existing sprite files."""
    sprites_dir = BASE_DIR / "assets" / "sprites"
    tileset_dir = BASE_DIR / "assets" / "tilesets" / "default"

    existing = {
        "sprites": set(),
        "tilesets": set(),
        "portraits": set(),
    }

    # Scan main sprites directory (recursive)
    if sprites_dir.exists():
        for root, dirs, files in os.walk(sprites_dir):
            for file in files:
                if file.lower().endswith((".png", ".jpg", ".bmp")):
                    sprite_id = os.path.splitext(file)[0]
                    rel_path = os.path.relpath(root, sprites_dir)
                    if rel_path == ".":
                        existing["sprites"].add(sprite_id)
                    elif rel_path == "portraits":
                        existing["portraits"].add(sprite_id)
                    else:
                        existing["sprites"].add(sprite_id)

    # Scan tileset directory
    if tileset_dir.exists():
        for file in os.listdir(tileset_dir):
            if file.lower().endswith((".png", ".jpg", ".bmp")):
                sprite_id = os.path.splitext(file)[0]
                existing["tilesets"].add(sprite_id)

    return existing


def extract_sprite_ids_from_json(data: any, path: str = "") -> Set[str]:
    """Recursively extract sprite_id values from JSON data."""
    sprite_ids = set()

    if isinstance(data, dict):
        # Check for sprite_id field
        if "sprite_id" in data and data["sprite_id"]:
            sprite_ids.add(data["sprite_id"])
        if "icon_id" in data and data["icon_id"]:
            sprite_ids.add(data["icon_id"])
        if "backdrop_id" in data and data["backdrop_id"]:
            sprite_ids.add(data["backdrop_id"])

        # Recursively check nested structures
        for key, value in data.items():
            sprite_ids.update(extract_sprite_ids_from_json(value, f"{path}.{key}"))

    elif isinstance(data, list):
        for i, item in enumerate(data):
            sprite_ids.update(extract_sprite_ids_from_json(item, f"{path}[{i}]"))

    return sprite_ids


def scan_json_files() -> Set[str]:
    """Scan all JSON files in data/ directory for sprite_id references."""
    data_dir = BASE_DIR / "data"
    sprite_ids = set()

    if not data_dir.exists():
        return sprite_ids

    for json_file in data_dir.rglob("*.json"):
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                found = extract_sprite_ids_from_json(data, str(json_file))
                sprite_ids.update(found)
        except Exception as e:
            print(f"Warning: Failed to parse {json_file}: {e}")

    return sprite_ids


def scan_python_files() -> Set[str]:
    """Scan Python files for get_image() calls and hardcoded sprite IDs."""
    sprite_ids = set()

    # False positives to exclude (JSON field names, dict keys, variable names, etc.)
    EXCLUDE_IDS = {
        "backdrop_id", "sprite_id", "icon_id",  # JSON field names
        "bg_top", "bg_bottom",  # Gradient color keys (not sprite IDs)
        "status_effects", "status_chance", "status_inflict_id",  # JSON fields
        "status_icons.json",  # File path
        "entity", "entry", "prop", "sprite_name",  # Variable names
    }

    # Patterns to match sprite ID references
    patterns = [
        r'get_image\(["\']([^"\']+)["\']',  # get_image("sprite_id")
        r'get_image\(([a-zA-Z_][a-zA-Z0-9_]*)',  # get_image(sprite_var)
        r'sprite_id\s*[:=]\s*["\']([^"\']+)["\']',  # sprite_id: "id" or sprite_id = "id"
        r'["\'](bg_[^"\']+)["\']',  # Background IDs
        r'["\'](ui_[^"\']+)["\']',  # UI sprite IDs
        r'["\'](status_[^"\']+)["\']',  # Status effect IDs
    ]

    # Directories to scan
    scan_dirs = [
        BASE_DIR / "engine",
        BASE_DIR / "core",
    ]

    for scan_dir in scan_dirs:
        if not scan_dir.exists():
            continue

        for py_file in scan_dir.rglob("*.py"):
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()

                    # Apply patterns
                    for pattern in patterns:
                        matches = re.findall(pattern, content)
                        for match in matches:
                            if isinstance(match, tuple):
                                match = match[0] if match else ""
                            if match and match not in EXCLUDE_IDS and match not in ["self", "sprite_id", "sprite"]:
                                sprite_ids.add(match)
            except Exception as e:
                print(f"Warning: Failed to read {py_file}: {e}")

    # Also check battle_scene.py for biome backdrop mapping
    battle_scene = BASE_DIR / "engine" / "battle_scene.py"
    if battle_scene.exists():
        try:
            with open(battle_scene, "r", encoding="utf-8") as f:
                content = f.read()
                # Extract backdrop IDs from BIOME_TO_BACKDROP dict
                backdrop_matches = re.findall(r'"bg_[^"]+"', content)
                for match in backdrop_matches:
                    sprite_ids.add(match.strip('"'))
        except Exception as e:
            print(f"Warning: Failed to read battle_scene.py: {e}")

    return sprite_ids


def categorize_sprite(sprite_id: str) -> str:
    """Categorize a sprite ID by its prefix/pattern."""
    if sprite_id.startswith("player_"):
        if "_" in sprite_id[7:]:  # player_class_subclass
            return "player_class_combo"
        return "player"
    elif sprite_id.startswith("class_"):
        return "class"
    elif sprite_id.startswith("party_"):
        return "party"
    elif sprite_id.startswith("npc_"):
        return "npc"
    elif sprite_id.startswith("enemy_") or sprite_id in load_enemy_ids_from_data():
        return "enemy"
    elif sprite_id.startswith("bg_"):
        return "background"
    elif sprite_id.startswith("item_"):
        return "item"
    elif sprite_id.startswith("ui_"):
        return "ui"
    elif sprite_id.startswith("status_"):
        return "status"
    elif sprite_id.startswith("prop_"):
        return "prop"
    elif sprite_id.startswith("portrait_"):
        return "portrait"
    elif sprite_id in ["grass", "dirt", "stone", "water", "wall", "lava", "snow", "swamp",
                        "ruins", "moss", "mountain", "tree", "ice", "puddle", "sand", "roots",
                        "wood_floor", "stone_floor", "stone_wall", "stone_cracked", "path",
                        "dirt_path", "path_cobble", "gold_floor", "void"] or any(
                        sprite_id.startswith(p) for p in ["grass_", "dirt_", "stone_", "water_",
                        "wall_", "lava_", "wood_floor_", "path_", "void_"]):
        return "tile"
    else:
        return "other"


def determine_priority(sprite_id: str, category: str) -> str:
    """Determine priority level for a sprite."""
    # Critical: Core gameplay sprites
    if category in ["player", "class", "enemy", "ui"]:
        return "critical"

    # High: Frequently used
    if category in ["party", "npc", "background", "item"]:
        return "high"

    # Medium: Used but not essential
    if category in ["status", "prop", "tile"]:
        return "medium"

    # Low: Rarely used or decorative
    if category in ["portrait", "player_class_combo", "other"]:
        return "low"

    return "medium"


def find_usage_context(sprite_id: str) -> List[str]:
    """Find where a sprite ID is used in the codebase."""
    contexts = []

    # Check data files
    data_dir = BASE_DIR / "data"
    if data_dir.exists():
        for json_file in data_dir.rglob("*.json"):
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    if sprite_id in content:
                        rel_path = os.path.relpath(json_file, BASE_DIR)
                        contexts.append(rel_path)
            except Exception:
                pass

    # Check Python files
    for scan_dir in [BASE_DIR / "engine", BASE_DIR / "core"]:
        if not scan_dir.exists():
            continue
        for py_file in scan_dir.rglob("*.py"):
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    if sprite_id in content:
                        rel_path = os.path.relpath(py_file, BASE_DIR)
                        contexts.append(rel_path)
            except Exception:
                pass

    return sorted(set(contexts))[:5]  # Limit to 5 examples


def main():
    """Main analysis function."""
    print("Analyzing sprite usage...")

    # Get existing sprites
    print("Scanning existing sprite files...")
    existing = get_existing_sprites()
    all_existing = existing["sprites"] | existing["tilesets"] | existing["portraits"]
    print(f"Found {len(all_existing)} existing sprite files")

    # Get requested sprites
    print("Scanning JSON files for sprite references...")
    json_sprites = scan_json_files()
    print(f"Found {len(json_sprites)} sprite IDs in JSON files")

    print("Scanning Python files for sprite references...")
    python_sprites = scan_python_files()
    print(f"Found {len(python_sprites)} sprite IDs in Python files")

    # Combine all requested sprites
    all_requested = json_sprites | python_sprites
    print(f"Total unique requested sprite IDs: {len(all_requested)}")

    # Identify placeholders
    placeholders = all_requested - all_existing
    print(f"Placeholder sprites (requested but missing): {len(placeholders)}")

    # Categorize sprites
    categories = defaultdict(list)
    for sprite_id in all_requested:
        category = categorize_sprite(sprite_id)
        categories[category].append(sprite_id)

    # Generate manifest data
    manifest_data = {
        "summary": {
            "total_existing": len(all_existing),
            "total_requested": len(all_requested),
            "total_placeholders": len(placeholders),
            "categories": {cat: len(sprites) for cat, sprites in categories.items()}
        },
        "existing_sprites": sorted(all_existing),
        "requested_sprites": sorted(all_requested),
        "placeholder_sprites": sorted(placeholders),
        "categories": {cat: sorted(sprites) for cat, sprites in categories.items()},
    }

    # Save JSON manifest
    manifest_json = BASE_DIR / "data" / "sprite_manifest.json"
    with open(manifest_json, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2, ensure_ascii=False)
    print(f"\nSaved JSON manifest to {manifest_json}")

    # Generate markdown manifest
    generate_markdown_manifest(manifest_data, existing, all_existing, placeholders)

    print("\nAnalysis complete!")


def generate_markdown_manifest(manifest_data: Dict, existing: Dict[str, Set[str]],
                                all_existing: Set[str], placeholders: Set[str]) -> None:
    """Generate markdown manifest document."""
    manifest_md = BASE_DIR / "data" / "SPRITE_MANIFEST.md"

    # Categorize existing sprites for summary
    existing_by_category = defaultdict(list)
    for sprite_id in all_existing:
        category = categorize_sprite(sprite_id)
        existing_by_category[category].append(sprite_id)

    with open(manifest_md, "w", encoding="utf-8") as f:
        f.write("# Sprite Manifest\n\n")
        f.write("Comprehensive documentation of all sprites used in the game.\n\n")

        # Summary
        f.write("## Summary\n\n")
        f.write(f"- **Total Existing Sprites**: {manifest_data['summary']['total_existing']}\n")
        f.write(f"- **Total Requested Sprites**: {manifest_data['summary']['total_requested']}\n")
        f.write(f"- **Placeholder Sprites** (requested but missing): {manifest_data['summary']['total_placeholders']}\n\n")

        f.write("### Requested Sprites by Category\n\n")
        f.write("Sprites referenced in the codebase, grouped by category:\n\n")
        for cat, count in sorted(manifest_data['summary']['categories'].items()):
            f.write(f"- **{cat}**: {count} sprites\n")
        f.write("\n")

        f.write("### Existing Sprites by Category\n\n")
        f.write("Sprite files that exist on disk, grouped by category:\n\n")
        for cat in sorted(existing_by_category.keys()):
            count = len(existing_by_category[cat])
            f.write(f"- **{cat}**: {count} sprites\n")
        f.write("\n")

        # Placeholder sprites by category
        f.write("## Placeholder Sprites (Need Real Assets)\n\n")
        f.write("These sprites are referenced in the codebase but don't exist as files. ")
        f.write("They will use the `_make_placeholder()` function which generates hash-based colored shapes.\n\n")

        placeholder_by_category = defaultdict(list)
        for sprite_id in placeholders:
            category = categorize_sprite(sprite_id)
            placeholder_by_category[category].append(sprite_id)

        if not placeholder_by_category:
            f.write("*No placeholder sprites - all requested sprites have files!*\n\n")
        else:
            for category in sorted(placeholder_by_category.keys()):
                sprites = sorted(placeholder_by_category[category])
                priority = determine_priority(sprites[0] if sprites else "", category)
                f.write(f"### {category.title()} ({len(sprites)} placeholders, Priority: {priority})\n\n")
                for sprite_id in sprites[:20]:  # Limit display
                    f.write(f"- `{sprite_id}`\n")
                if len(sprites) > 20:
                    f.write(f"- ... and {len(sprites) - 20} more\n")
                f.write("\n")

        # Existing sprites by category
        f.write("## Existing Sprites\n\n")
        f.write("These sprites exist as files in `assets/sprites/` or `assets/tilesets/default/`.\n\n")

        for category in sorted(existing_by_category.keys()):
            sprites = sorted(existing_by_category[category])
            f.write(f"### {category.title()} ({len(sprites)} sprites)\n\n")
            # Show first 30, then summarize
            for sprite_id in sprites[:30]:
                f.write(f"- `{sprite_id}`\n")
            if len(sprites) > 30:
                f.write(f"- ... and {len(sprites) - 30} more\n")
            f.write("\n")

        # All requested sprites (full list)
        f.write("## All Requested Sprite IDs\n\n")
        f.write("Complete list of all sprite IDs referenced in the codebase:\n\n")
        for sprite_id in sorted(manifest_data['requested_sprites']):
            exists = "✓" if sprite_id in all_existing else "✗"
            category = categorize_sprite(sprite_id)
            f.write(f"- {exists} `{sprite_id}` ({category})\n")

        f.write("\n## Notes\n\n")
        f.write("- ✓ = Sprite file exists\n")
        f.write("- ✗ = Placeholder (file missing)\n")
        f.write("- Sprites are automatically loaded from `assets/sprites/` (recursive) and `assets/tilesets/default/`\n")
        f.write("- Missing sprites use `AssetManager._make_placeholder()` which generates colored shapes\n")
        f.write("- Priority levels: critical > high > medium > low\n")

    print(f"Saved markdown manifest to {manifest_md}")


if __name__ == "__main__":
    main()
