#!/usr/bin/env python3
"""
Difficulty Curve Analysis Tool

Analyzes encounter difficulty vs map gating and player progression
to ensure smooth difficulty curve and appropriate level recommendations.
"""

import json
import os
import sys
from typing import Dict, List, Set, Optional, Tuple
from collections import defaultdict

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.data_loader import load_json_file


def load_data() -> Tuple[Dict, Dict, Dict]:
    """Load encounters, maps, and quests data."""
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    encounters = load_json_file(os.path.join(data_dir, 'encounters.json'), {})
    quests = load_json_file(os.path.join(data_dir, 'quests.json'), {})

    # Load all map files
    maps_dir = os.path.join(data_dir, 'maps')
    maps = {}
    if os.path.exists(maps_dir):
        for filename in os.listdir(maps_dir):
            if filename.endswith('.json'):
                map_id = filename[:-5]  # Remove .json extension
                maps[map_id] = load_json_file(os.path.join(maps_dir, filename), {})

    return encounters, maps, quests


def analyze_encounter_difficulty(encounters_data: Dict) -> Dict:
    """Extract enemy levels and difficulty from all encounters."""
    encounters = encounters_data.get('encounters', {})

    encounter_info = {}
    level_distribution = defaultdict(list)
    difficulty_distribution = defaultdict(list)

    for encounter_id, encounter in encounters.items():
        enemies = encounter.get('enemies', [])
        if not enemies:
            continue

        levels = [e.get('level', 1) for e in enemies]
        difficulties = [e.get('difficulty', 'normal') for e in enemies]

        min_level = min(levels)
        max_level = max(levels)
        avg_level = sum(levels) // len(levels)

        # Get highest difficulty
        difficulty_order = ['easy', 'normal', 'hard', 'elite', 'boss']
        max_difficulty = max(difficulties, key=lambda d: difficulty_order.index(d) if d in difficulty_order else 1)

        encounter_info[encounter_id] = {
            'min_level': min_level,
            'max_level': max_level,
            'avg_level': avg_level,
            'difficulty': max_difficulty,
            'enemy_count': len(enemies),
            'levels': levels,
            'difficulties': difficulties
        }

        level_distribution[avg_level].append(encounter_id)
        difficulty_distribution[max_difficulty].append(encounter_id)

    return {
        'encounters': encounter_info,
        'by_level': dict(level_distribution),
        'by_difficulty': dict(difficulty_distribution)
    }


def analyze_map_gating(maps_data: Dict) -> Dict:
    """Identify map gating flags and their requirements."""
    gating_info = {}

    for map_id, map_data in maps_data.items():
        warps = map_data.get('warps', [])
        triggers = map_data.get('triggers', [])

        gating_flags = set()
        required_flags = set()
        blocked_by_flags = set()

        # Check warps for gating
        for warp in warps:
            if 'requires_flag' in warp:
                required_flags.add(warp['requires_flag'])
            if 'blocked_by_flag' in warp:
                blocked_by_flags.add(warp['blocked_by_flag'])

        # Check triggers for gating
        for trigger in triggers:
            trigger_data = trigger.get('data', {})
            if 'requires_flag' in trigger_data:
                required_flags.add(trigger_data['requires_flag'])
            if 'blocked_by_flag' in trigger_data:
                blocked_by_flags.add(trigger_data['blocked_by_flag'])

        if required_flags or blocked_by_flags:
            gating_info[map_id] = {
                'required_flags': list(required_flags),
                'blocked_by_flags': list(blocked_by_flags),
                'all_flags': list(required_flags | blocked_by_flags)
            }

    return gating_info


def map_encounters_to_areas(encounters_data: Dict, maps_data: Dict) -> Dict:
    """Map encounters to areas based on map triggers and enemy spawns."""
    encounter_to_maps = defaultdict(set)

    # Check map triggers for encounter references
    for map_id, map_data in maps_data.items():
        triggers = map_data.get('triggers', [])
        for trigger in triggers:
            trigger_data = trigger.get('data', {})
            encounter_id = trigger_data.get('encounter_id')
            if encounter_id:
                encounter_to_maps[encounter_id].add(map_id)

        # Check enemy spawns
        enemy_spawns = map_data.get('enemy_spawns', [])
        for spawn in enemy_spawns:
            encounter_id = spawn.get('encounter_id')
            if encounter_id:
                encounter_to_maps[encounter_id].add(map_id)

    return dict(encounter_to_maps)


def calculate_recommended_level(encounter_info: Dict) -> int:
    """Calculate recommended player level for an encounter."""
    avg_level = encounter_info['avg_level']
    difficulty = encounter_info['difficulty']
    enemy_count = encounter_info['enemy_count']

    # Base recommendation on average enemy level
    recommended = avg_level

    # Adjust for difficulty
    difficulty_adjustments = {
        'easy': -1,
        'normal': 0,
        'hard': +1,
        'elite': +2,
        'boss': +2
    }
    recommended += difficulty_adjustments.get(difficulty, 0)

    # Adjust for multiple enemies (slightly higher recommendation)
    if enemy_count > 2:
        recommended += 1

    return max(1, min(10, recommended))


def analyze_progression_path(quests_data: Dict, encounters_data: Dict,
                            maps_data: Dict) -> Dict:
    """Analyze main quest progression path and recommended levels."""
    main_quests = [q for q in quests_data.get('quests', []) if q.get('category') == 'main']

    # Sort by prerequisites
    quest_order = []
    remaining = main_quests.copy()
    processed_ids = set()

    while remaining:
        found_any = False
        for quest in remaining[:]:
            required_quests = quest.get('required_quests', [])
            if not required_quests or all(qid in processed_ids for qid in required_quests):
                quest_order.append(quest)
                processed_ids.add(quest['id'])
                remaining.remove(quest)
                found_any = True
        if not found_any:
            for quest in remaining:
                quest_order.append(quest)
                processed_ids.add(quest['id'])
            break

    progression = []
    encounter_analysis = analyze_encounter_difficulty(encounters_data)
    encounter_to_maps = map_encounters_to_areas(encounters_data, maps_data)

    for quest in quest_order:
        # Find encounters related to this quest's objectives
        objectives = quest.get('objectives', [])
        related_encounters = []

        for obj in objectives:
            if obj.get('type') == 'kill':
                # Find encounters with this enemy type
                target = obj.get('target', '')
                for enc_id, enc_data in encounters_data.get('encounters', {}).items():
                    enemies = enc_data.get('enemies', [])
                    for enemy in enemies:
                        if target in enemy.get('type', '').lower() or target in enemy.get('id', '').lower():
                            related_encounters.append(enc_id)
                            break

        # Get recommended level from related encounters
        recommended_levels = []
        for enc_id in related_encounters:
            if enc_id in encounter_analysis['encounters']:
                rec_level = calculate_recommended_level(encounter_analysis['encounters'][enc_id])
                recommended_levels.append(rec_level)

        recommended_level = max(recommended_levels) if recommended_levels else None

        progression.append({
            'quest_id': quest['id'],
            'quest_name': quest.get('name', quest['id']),
            'recommended_level': recommended_level,
            'related_encounters': list(set(related_encounters))
        })

    return {
        'quests': progression,
        'encounter_analysis': encounter_analysis,
        'encounter_to_maps': encounter_to_maps
    }


def verify_gating_alignment(encounter_analysis: Dict, gating_info: Dict,
                           encounter_to_maps: Dict, encounters_data: Dict) -> List[str]:
    """Verify gating flags align with encounter difficulty.

    This function checks that:
    1. Encounters that SET a flag are at appropriate levels for that progression gate
    2. Content GATED by a flag is appropriately harder than the prerequisite

    The expected_gating dict defines design-target level ranges for encounters
    that should set each flag. These are intentional design constraints to ensure
    smooth difficulty progression.
    """
    issues = []

    # Design-target level ranges for encounters that SET each flag
    # These define the expected player level when completing each milestone
    # Format: flag_name -> {'min_level': X, 'max_level': Y}
    expected_flag_setters = {
        'tutorial_completed': {'min_level': 1, 'max_level': 1, 'description': 'Tutorial battle'},
        'forest_slimes_cleared': {'min_level': 1, 'max_level': 2, 'description': 'Early forest encounter'},
        'forest_wolves_cleared': {'min_level': 2, 'max_level': 3, 'description': 'Forest wolf pack'},
        'werewolves_defeated': {'min_level': 2, 'max_level': 3, 'description': 'Werewolf encounter'},
        'cave_cleared': {'min_level': 3, 'max_level': 4, 'description': 'Cave goblin boss'},
        'goblin_warband_defeated': {'min_level': 4, 'max_level': 5, 'description': 'Goblin warband elite'},
        'swamp_witch_defeated': {'min_level': 5, 'max_level': 7, 'description': 'Swamp witch boss'},
        'ruins_guardian_defeated': {'min_level': 7, 'max_level': 9, 'description': 'Ruins guardian boss'},
        'final_boss_defeated': {'min_level': 8, 'max_level': 10, 'description': 'Final boss'},
    }

    # Build a map of flag -> encounter that sets it
    flag_to_encounter = {}
    encounters = encounters_data.get('encounters', {})
    for enc_id, enc_data in encounters.items():
        rewards = enc_data.get('rewards', {})
        flags = rewards.get('flags', [])
        for flag in flags:
            flag_to_encounter[flag] = enc_id

    # Check 1: Verify encounters that SET flags are at expected levels
    encounters_info = encounter_analysis['encounters']
    for flag, expected in expected_flag_setters.items():
        if flag in flag_to_encounter:
            enc_id = flag_to_encounter[flag]
            if enc_id in encounters_info:
                enc_info = encounters_info[enc_id]
                avg_level = enc_info['avg_level']
                if avg_level < expected['min_level'] or avg_level > expected['max_level']:
                    issues.append(
                        f"Encounter '{enc_id}' sets flag '{flag}' at level {avg_level}, "
                        f"but expected level {expected['min_level']}-{expected['max_level']} "
                        f"({expected['description']})"
                    )

    # Check 2: Verify gated content is harder than prerequisite
    # For each map that requires a flag, check that its encounters are appropriately leveled
    for map_id, gates in gating_info.items():
        required_flags = gates.get('required_flags', [])
        for flag in required_flags:
            if flag in flag_to_encounter:
                prereq_enc_id = flag_to_encounter[flag]
                if prereq_enc_id in encounters_info:
                    prereq_level = encounters_info[prereq_enc_id]['avg_level']

                    # Check encounters in the gated map
                    for enc_id, maps in encounter_to_maps.items():
                        if map_id in maps and enc_id in encounters_info:
                            gated_level = encounters_info[enc_id]['avg_level']
                            # Gated content should be same level or harder (not easier)
                            if gated_level < prereq_level - 1:
                                issues.append(
                                    f"Map '{map_id}' requires '{flag}' (set by level {prereq_level} encounter), "
                                    f"but contains '{enc_id}' at level {gated_level} (too easy for gated content)"
                                )

    return issues


def generate_report(encounter_analysis: Dict, gating_info: Dict,
                   progression: Dict, issues: List[str]) -> str:
    """Generate comprehensive difficulty curve analysis report."""
    report = []
    report.append("=" * 80)
    report.append("DIFFICULTY CURVE ANALYSIS REPORT")
    report.append("=" * 80)
    report.append("")

    # Encounter Difficulty Distribution
    report.append("ENCOUNTER DIFFICULTY DISTRIBUTION")
    report.append("-" * 80)
    report.append(f"Total Encounters: {len(encounter_analysis['encounters'])}")
    report.append("")
    report.append("By Average Enemy Level:")
    for level in sorted(encounter_analysis['by_level'].keys()):
        encounters = encounter_analysis['by_level'][level]
        report.append(f"  Level {level}: {len(encounters)} encounters")
        for enc_id in encounters[:5]:  # Show first 5
            enc_info = encounter_analysis['encounters'][enc_id]
            report.append(f"    - {enc_id}: {enc_info['enemy_count']} enemies, "
                         f"difficulty {enc_info['difficulty']}")
        if len(encounters) > 5:
            report.append(f"    ... and {len(encounters) - 5} more")
    report.append("")

    report.append("By Difficulty Tier:")
    for diff in ['easy', 'normal', 'hard', 'elite', 'boss']:
        if diff in encounter_analysis['by_difficulty']:
            encounters = encounter_analysis['by_difficulty'][diff]
            report.append(f"  {diff}: {len(encounters)} encounters")
    report.append("")

    # Map Gating Analysis
    report.append("MAP GATING FLAGS")
    report.append("-" * 80)
    if gating_info:
        for map_id, gates in sorted(gating_info.items()):
            if gates.get('required_flags'):
                report.append(f"{map_id}:")
                report.append(f"  Requires: {', '.join(gates['required_flags'])}")
            if gates.get('blocked_by_flags'):
                report.append(f"  Blocked by: {', '.join(gates['blocked_by_flags'])}")
    else:
        report.append("No gating flags found.")
    report.append("")

    # Progression Path
    report.append("MAIN QUEST PROGRESSION PATH")
    report.append("-" * 80)
    for quest in progression['quests']:
        report.append(f"{quest['quest_name']}:")
        if quest['recommended_level']:
            report.append(f"  Recommended Level: {quest['recommended_level']}")
        if quest['related_encounters']:
            report.append(f"  Related Encounters: {', '.join(quest['related_encounters'][:3])}")
            if len(quest['related_encounters']) > 3:
                report.append(f"    ... and {len(quest['related_encounters']) - 3} more")
    report.append("")

    # Level Recommendations by Area
    report.append("RECOMMENDED LEVEL BY AREA")
    report.append("-" * 80)

    # Group encounters by map
    map_to_encounters = defaultdict(list)
    for enc_id, maps in progression['encounter_to_maps'].items():
        for map_id in maps:
            map_to_encounters[map_id].append(enc_id)

    for map_id in sorted(map_to_encounters.keys()):
        encounters = map_to_encounters[map_id]
        levels = []
        for enc_id in encounters:
            if enc_id in encounter_analysis['encounters']:
                rec_level = calculate_recommended_level(encounter_analysis['encounters'][enc_id])
                levels.append(rec_level)

        if levels:
            min_rec = min(levels)
            max_rec = max(levels)
            avg_rec = sum(levels) // len(levels)
            report.append(f"{map_id}: Level {min_rec}-{max_rec} (avg: {avg_rec})")
    report.append("")

    # Issues
    if issues:
        report.append("ISSUES FOUND")
        report.append("-" * 80)
        for issue in issues:
            report.append(f"⚠️  {issue}")
        report.append("")
    else:
        report.append("✓ No major gating alignment issues found")
        report.append("")

    # Recommendations
    report.append("RECOMMENDATIONS")
    report.append("-" * 80)

    # Check for difficulty spikes
    levels = sorted(encounter_analysis['by_level'].keys())
    if len(levels) > 1:
        for i in range(len(levels) - 1):
            level_diff = levels[i + 1] - levels[i]
            if level_diff > 2:
                report.append(f"⚠️  Large level jump detected: Level {levels[i]} to {levels[i + 1]} "
                             f"(gap of {level_diff} levels)")

    report.append("")
    report.append("=" * 80)

    return "\n".join(report)


def main():
    """Main entry point."""
    print("Loading data...")
    encounters_data, maps_data, quests_data = load_data()

    print("Analyzing encounter difficulty...")
    encounter_analysis = analyze_encounter_difficulty(encounters_data)

    print("Analyzing map gating...")
    gating_info = analyze_map_gating(maps_data)

    print("Mapping encounters to areas...")
    encounter_to_maps = map_encounters_to_areas(encounters_data, maps_data)

    print("Analyzing progression path...")
    progression = analyze_progression_path(quests_data, encounters_data, maps_data)
    progression['encounter_to_maps'] = encounter_to_maps

    print("Verifying gating alignment...")
    issues = verify_gating_alignment(encounter_analysis, gating_info, encounter_to_maps, encounters_data)

    print("Generating report...")
    report = generate_report(encounter_analysis, gating_info, progression, issues)

    print("\n" + report)

    # Save report to file
    report_path = os.path.join(os.path.dirname(__file__), '..', 'DIFFICULTY_CURVE_ANALYSIS.md')
    with open(report_path, 'w') as f:
        f.write(report)
    print(f"\nReport saved to: {report_path}")


if __name__ == '__main__':
    main()
