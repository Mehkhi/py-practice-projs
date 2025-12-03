#!/usr/bin/env python3
"""
Main Sprite Generation Script

Generates all game sprites using the sprite generation system.
Run with --help for usage information.

Outputs:
- Static sprites: assets/sprites/{name}.png (e.g., skeleton.png)
- Animation frames: assets/sprites/animations/{name}/ (e.g., animations/skeleton/)
- Sprite sheets: assets/sprites/sheets/{name}_sheet.png
- Metadata: assets/sprites/meta/{name}_meta.json
"""

import os
import sys
import json
import argparse
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

# Ensure pygame is available
try:
    import pygame
    pygame.init()
except ImportError:
    print("Error: pygame is required. Install with: pip install pygame")
    sys.exit(1)

# Import sprite generators
from .enemy_sprites import get_enemy_sprite, BASIC_ENEMIES
from .enemy_sprites_advanced import get_advanced_enemy_sprite, ADVANCED_ENEMIES
from .boss_sprites import get_boss_sprite, BOSS_SPRITES
from .npc_sprites import get_npc_sprite, NPC_SPRITES
from .party_sprites import get_party_sprite, PARTY_SPRITES
from .utils import scale_to_game_size


# Default output directory
DEFAULT_OUTPUT_BASE = "assets/sprites"


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Load sprite configuration from JSON file."""
    if config_path is None:
        config_path = os.path.join(os.path.dirname(__file__), 'sprite_config.json')

    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)

    # Return default config if file doesn't exist
    return {
        "output_base": DEFAULT_OUTPUT_BASE,
        "generate_animations": True,
        "generate_sprite_sheets": True,
        "scale_to_game_size": True,
        "save_metadata": True
    }


def save_sprite_files(sprite, output_dir: str, config: Dict[str, Any]) -> Dict[str, str]:
    """
    Save sprite files in the correct structure for the game.

    Output structure:
    - Static: {output_dir}/{name}.png
    - Animations: {output_dir}/animations/{name}/{name}_{state}_{frame}.png
    - Sheet: {output_dir}/sheets/{name}_sheet.png
    - Metadata: {output_dir}/meta/{name}_meta.json

    Args:
        sprite: The sprite generator instance
        output_dir: Base output directory (e.g., assets/sprites)
        config: Configuration dict

    Returns:
        Dict mapping file types to paths
    """
    saved_files = {}
    name = sprite.name
    scale = config.get('scale_to_game_size', True)

    # Generate all frames
    sprite.generate_all_frames()

    # 1. Save static sprite at root level
    if sprite.frames['idle']:
        static = sprite.frames['idle'][0]
        if scale:
            static = scale_to_game_size(static, sprite.game_size)

        static_path = os.path.join(output_dir, f"{name}.png")
        pygame.image.save(static, static_path)
        saved_files['static'] = static_path

    # 2. Save animation frames if enabled
    if config.get('generate_animations', True):
        anim_dir = os.path.join(output_dir, 'animations', name)
        os.makedirs(anim_dir, exist_ok=True)

        for state, frames in sprite.frames.items():
            for i, frame in enumerate(frames):
                if scale:
                    frame = scale_to_game_size(frame, sprite.game_size)

                frame_name = f"{name}_{state}_{i}.png"
                frame_path = os.path.join(anim_dir, frame_name)
                pygame.image.save(frame, frame_path)

        saved_files['anim_dir'] = anim_dir

    # 3. Save sprite sheet if enabled
    if config.get('generate_sprite_sheets', True):
        sheets_dir = os.path.join(output_dir, 'sheets')
        os.makedirs(sheets_dir, exist_ok=True)

        sheet = sprite._create_sprite_sheet(scale)
        if sheet:
            sheet_path = os.path.join(sheets_dir, f"{name}_sheet.png")
            pygame.image.save(sheet, sheet_path)
            saved_files['sheet'] = sheet_path

    # 4. Save metadata if enabled
    if config.get('save_metadata', True):
        meta_dir = os.path.join(output_dir, 'meta')
        os.makedirs(meta_dir, exist_ok=True)

        meta = sprite._create_metadata()
        meta_path = os.path.join(meta_dir, f"{name}_meta.json")
        with open(meta_path, 'w') as f:
            json.dump(meta, f, indent=2)
        saved_files['meta'] = meta_path

    return saved_files


def generate_enemies(output_dir: str, config: Dict[str, Any],
                     specific: Optional[List[str]] = None) -> int:
    """Generate all enemy sprites."""
    count = 0

    # Combine basic and advanced enemies
    all_enemies = BASIC_ENEMIES + ADVANCED_ENEMIES

    if specific:
        all_enemies = [e for e in all_enemies if e in specific]

    for enemy_name in all_enemies:
        print(f"  Generating {enemy_name}...")

        # Try basic first, then advanced
        sprite = get_enemy_sprite(enemy_name)
        if sprite is None:
            sprite = get_advanced_enemy_sprite(enemy_name)

        if sprite:
            save_sprite_files(sprite, output_dir, config)
            count += 1
        else:
            print(f"    Warning: No sprite generator for {enemy_name}")

    return count


def generate_bosses(output_dir: str, config: Dict[str, Any],
                    specific: Optional[List[str]] = None) -> int:
    """Generate all boss sprites."""
    count = 0

    bosses = BOSS_SPRITES if specific is None else [b for b in BOSS_SPRITES if b in specific]

    for boss_name in bosses:
        print(f"  Generating {boss_name}...")

        sprite = get_boss_sprite(boss_name)
        if sprite:
            save_sprite_files(sprite, output_dir, config)
            count += 1
        else:
            print(f"    Warning: No sprite generator for {boss_name}")

    return count


def generate_npcs(output_dir: str, config: Dict[str, Any],
                  specific: Optional[List[str]] = None) -> int:
    """Generate all NPC sprites."""
    count = 0

    npcs = NPC_SPRITES if specific is None else [n for n in NPC_SPRITES if n in specific]

    for npc_name in npcs:
        print(f"  Generating {npc_name}...")

        sprite = get_npc_sprite(npc_name)
        if sprite:
            save_sprite_files(sprite, output_dir, config)
            count += 1
        else:
            print(f"    Warning: No sprite generator for {npc_name}")

    return count


def generate_party(output_dir: str, config: Dict[str, Any],
                   specific: Optional[List[str]] = None) -> int:
    """Generate all party member sprites."""
    count = 0

    party = PARTY_SPRITES if specific is None else [p for p in PARTY_SPRITES if p in specific]

    for member_name in party:
        print(f"  Generating {member_name}...")

        sprite = get_party_sprite(member_name)
        if sprite:
            save_sprite_files(sprite, output_dir, config)
            count += 1
        else:
            print(f"    Warning: No sprite generator for {member_name}")

    return count


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Generate game sprites using the sprite generation system.'
    )

    parser.add_argument(
        '--output', '-o',
        default=None,
        help='Output directory for sprites (default: from config)'
    )

    parser.add_argument(
        '--config', '-c',
        default=None,
        help='Path to sprite_config.json'
    )

    parser.add_argument(
        '--type', '-t',
        choices=['all', 'enemies', 'bosses', 'npcs', 'party'],
        default='all',
        help='Type of sprites to generate (portraits skipped - use existing)'
    )

    parser.add_argument(
        '--specific', '-s',
        nargs='+',
        default=None,
        help='Specific sprite names to generate'
    )

    parser.add_argument(
        '--no-animations',
        action='store_true',
        help='Skip animation frame generation'
    )

    parser.add_argument(
        '--no-sheets',
        action='store_true',
        help='Skip sprite sheet generation'
    )

    parser.add_argument(
        '--no-scale',
        action='store_true',
        help='Skip scaling to game size (keep 64x64)'
    )

    parser.add_argument(
        '--no-metadata',
        action='store_true',
        help='Skip metadata JSON generation'
    )

    parser.add_argument(
        '--list',
        action='store_true',
        help='List all available sprites and exit'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )

    args = parser.parse_args()

    # List mode
    if args.list:
        print("Available Sprites:")
        print("\nEnemies (Basic):", ', '.join(BASIC_ENEMIES))
        print("\nEnemies (Advanced):", ', '.join(ADVANCED_ENEMIES))
        print("\nBosses:", ', '.join(BOSS_SPRITES))
        print("\nNPCs:", ', '.join(NPC_SPRITES))
        print("\nParty Members:", ', '.join(PARTY_SPRITES))
        print("\nNote: Portraits are skipped - using existing portrait files.")
        return 0

    # Load configuration
    config = load_config(args.config)

    # Override config with command line args
    if args.no_animations:
        config['generate_animations'] = False
    if args.no_sheets:
        config['generate_sprite_sheets'] = False
    if args.no_scale:
        config['scale_to_game_size'] = False
    if args.no_metadata:
        config['save_metadata'] = False

    # Set output directory
    output_base = args.output or config.get('output_base', DEFAULT_OUTPUT_BASE)

    # Get project root (assumes we're in tools/sprite_generation)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))

    output_dir = os.path.join(project_root, output_base)

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    print(f"Sprite Generation System")
    print(f"========================")
    print(f"Output directory: {output_dir}")
    print(f"Animations: {config.get('generate_animations', True)}")
    print(f"Sprite sheets: {config.get('generate_sprite_sheets', True)}")
    print(f"Scale to 32x32: {config.get('scale_to_game_size', True)}")
    print()

    start_time = time.time()
    total_count = 0

    try:
        if args.type in ['all', 'enemies']:
            print("Generating enemy sprites...")
            count = generate_enemies(output_dir, config, args.specific)
            print(f"  Generated {count} enemy sprites")
            total_count += count

        if args.type in ['all', 'bosses']:
            print("Generating boss sprites...")
            count = generate_bosses(output_dir, config, args.specific)
            print(f"  Generated {count} boss sprites")
            total_count += count

        if args.type in ['all', 'npcs']:
            print("Generating NPC sprites...")
            count = generate_npcs(output_dir, config, args.specific)
            print(f"  Generated {count} NPC sprites")
            total_count += count

        if args.type in ['all', 'party']:
            print("Generating party member sprites...")
            count = generate_party(output_dir, config, args.specific)
            print(f"  Generated {count} party sprites")
            total_count += count

    except Exception as e:
        print(f"\nError during generation: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

    elapsed = time.time() - start_time
    print()
    print(f"Generation complete!")
    print(f"Total sprites generated: {total_count}")
    print(f"Time elapsed: {elapsed:.2f} seconds")
    print()
    print(f"Output structure:")
    print(f"  Static sprites: {output_dir}/<name>.png")
    print(f"  Animations:     {output_dir}/animations/<name>/")
    print(f"  Sprite sheets:  {output_dir}/sheets/<name>_sheet.png")
    print(f"  Metadata:       {output_dir}/meta/<name>_meta.json")

    return 0


if __name__ == '__main__':
    sys.exit(main())
