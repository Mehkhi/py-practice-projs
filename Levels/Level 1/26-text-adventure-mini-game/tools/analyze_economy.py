#!/usr/bin/env python3
"""
Economy Analysis Tool

Analyzes gold/EXP flow from encounters and quests vs shop prices
to identify balance issues and grinding requirements.
"""

import json
import os
import sys
from typing import Dict, List, Tuple
from collections import defaultdict

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.data_loader import load_json_file


def load_data() -> Tuple[Dict, Dict, Dict]:
    """Load encounters, quests, and items data."""
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    encounters = load_json_file(os.path.join(data_dir, 'encounters.json'), {})
    quests = load_json_file(os.path.join(data_dir, 'quests.json'), {})
    items = load_json_file(os.path.join(data_dir, 'items.json'), {})
    return encounters, quests, items


def analyze_main_quest_chain(quests_data: Dict) -> Dict:
    """Analyze gold/EXP from main quest chain."""
    main_quests = [q for q in quests_data.get('quests', []) if q.get('category') == 'main']

    # Sort by prerequisites to get order
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
            # Fallback: add remaining quests
            for quest in remaining:
                quest_order.append(quest)
                processed_ids.add(quest['id'])
            break

    cumulative_gold = 0
    cumulative_exp = 0
    progression = []

    for quest in quest_order:
        gold = quest.get('reward_gold', 0)
        exp = quest.get('reward_exp', 0)
        cumulative_gold += gold
        cumulative_exp += exp
        progression.append({
            'quest_id': quest['id'],
            'quest_name': quest.get('name', quest['id']),
            'gold': gold,
            'exp': exp,
            'cumulative_gold': cumulative_gold,
            'cumulative_exp': cumulative_exp
        })

    return {
        'total_gold': cumulative_gold,
        'total_exp': cumulative_exp,
        'quest_count': len(quest_order),
        'progression': progression
    }


def analyze_side_quests(quests_data: Dict) -> Dict:
    """Analyze gold/EXP from side quests."""
    side_quests = [q for q in quests_data.get('quests', []) if q.get('category') != 'main']

    total_gold = sum(q.get('reward_gold', 0) for q in side_quests)
    total_exp = sum(q.get('reward_exp', 0) for q in side_quests)

    by_category = defaultdict(lambda: {'count': 0, 'gold': 0, 'exp': 0})
    for quest in side_quests:
        cat = quest.get('category', 'side')
        by_category[cat]['count'] += 1
        by_category[cat]['gold'] += quest.get('reward_gold', 0)
        by_category[cat]['exp'] += quest.get('reward_exp', 0)

    return {
        'total_gold': total_gold,
        'total_exp': total_exp,
        'quest_count': len(side_quests),
        'by_category': dict(by_category)
    }


def analyze_encounter_rewards(encounters_data: Dict) -> Dict:
    """Analyze gold/EXP from encounters."""
    encounters = encounters_data.get('encounters', {})

    total_gold = 0
    total_exp = 0
    by_difficulty = defaultdict(lambda: {'count': 0, 'gold': 0, 'exp': 0})
    by_level = defaultdict(lambda: {'count': 0, 'gold': 0, 'exp': 0})

    for encounter_id, encounter in encounters.items():
        rewards = encounter.get('rewards', {})
        gold = rewards.get('gold', 0)
        exp = rewards.get('exp', 0)

        total_gold += gold
        total_exp += exp

        # Analyze by enemy difficulty
        enemies = encounter.get('enemies', [])
        if enemies:
            # Use highest difficulty in encounter
            difficulties = [e.get('difficulty', 'normal') for e in enemies]
            difficulty = max(difficulties, key=lambda d: ['easy', 'normal', 'hard', 'elite', 'boss'].index(d) if d in ['easy', 'normal', 'hard', 'elite', 'boss'] else 1)
            by_difficulty[difficulty]['count'] += 1
            by_difficulty[difficulty]['gold'] += gold
            by_difficulty[difficulty]['exp'] += exp

            # Use average level
            levels = [e.get('level', 1) for e in enemies]
            avg_level = sum(levels) // len(levels) if levels else 1
            level_tier = (avg_level // 2) * 2 + 1  # Group into tiers: 1-2, 3-4, 5-6, etc.
            by_level[level_tier]['count'] += 1
            by_level[level_tier]['gold'] += gold
            by_level[level_tier]['exp'] += exp

    return {
        'total_gold': total_gold,
        'total_exp': total_exp,
        'encounter_count': len(encounters),
        'by_difficulty': dict(by_difficulty),
        'by_level': dict(by_level)
    }


def analyze_equipment_pricing(items_data: Dict) -> Dict:
    """Analyze equipment prices and categorize by tier."""
    items = items_data.get('items', [])
    equipment = [i for i in items if i.get('item_type') == 'equipment']

    tiers = {
        'starter': {'min': 0, 'max': 15, 'items': []},
        'early': {'min': 15, 'max': 50, 'items': []},
        'mid': {'min': 50, 'max': 200, 'items': []},
        'late': {'min': 200, 'max': 500, 'items': []},
        'legendary': {'min': 500, 'max': float('inf'), 'items': []}
    }

    for item in equipment:
        price = item.get('value', 0)
        stat_total = sum(item.get('stat_modifiers', {}).values())

        item_info = {
            'id': item['id'],
            'name': item.get('name', item['id']),
            'price': price,
            'stat_total': stat_total,
            'stat_modifiers': item.get('stat_modifiers', {})
        }

        for tier_name, tier_data in tiers.items():
            if tier_data['min'] <= price < tier_data['max']:
                tier_data['items'].append(item_info)
                break

    return tiers


def calculate_affordability(available_gold: int, equipment_tiers: Dict) -> Dict:
    """Calculate what equipment is affordable at given gold amount."""
    affordable = {
        'starter': [],
        'early': [],
        'mid': [],
        'late': [],
        'legendary': []
    }

    for tier_name, tier_data in equipment_tiers.items():
        for item in tier_data['items']:
            if item['price'] <= available_gold:
                affordable[tier_name].append(item)

    return affordable


def generate_report(main_quest: Dict, side_quests: Dict, encounters: Dict,
                   equipment: Dict) -> str:
    """Generate comprehensive economy analysis report."""
    report = []
    report.append("=" * 80)
    report.append("ECONOMY ANALYSIS REPORT")
    report.append("=" * 80)
    report.append("")

    # Main Quest Chain Analysis
    report.append("MAIN QUEST CHAIN")
    report.append("-" * 80)
    report.append(f"Total Quests: {main_quest['quest_count']}")
    report.append(f"Total Gold: {main_quest['total_gold']}")
    report.append(f"Total EXP: {main_quest['total_exp']}")
    report.append("")
    report.append("Progression:")
    for step in main_quest['progression']:
        report.append(f"  {step['quest_name']}: +{step['gold']}g, +{step['exp']}exp "
                     f"(Total: {step['cumulative_gold']}g, {step['cumulative_exp']}exp)")
    report.append("")

    # Side Quests Analysis
    report.append("SIDE QUESTS")
    report.append("-" * 80)
    report.append(f"Total Quests: {side_quests['quest_count']}")
    report.append(f"Total Gold: {side_quests['total_gold']}")
    report.append(f"Total EXP: {side_quests['total_exp']}")
    report.append("")
    report.append("By Category:")
    for cat, data in side_quests['by_category'].items():
        report.append(f"  {cat}: {data['count']} quests, {data['gold']}g, {data['exp']}exp")
    report.append("")

    # Encounters Analysis
    report.append("ENCOUNTERS")
    report.append("-" * 80)
    report.append(f"Total Encounters: {encounters['encounter_count']}")
    report.append(f"Total Gold: {encounters['total_gold']}")
    report.append(f"Total EXP: {encounters['total_exp']}")
    report.append("")
    report.append("By Difficulty:")
    for diff in ['easy', 'normal', 'hard', 'elite', 'boss']:
        if diff in encounters['by_difficulty']:
            data = encounters['by_difficulty'][diff]
            report.append(f"  {diff}: {data['count']} encounters, {data['gold']}g, {data['exp']}exp")
    report.append("")
    report.append("By Level Tier:")
    for level in sorted(encounters['by_level'].keys()):
        data = encounters['by_level'][level]
        report.append(f"  Level {level}-{level+1}: {data['count']} encounters, {data['gold']}g, {data['exp']}exp")
    report.append("")

    # Total Economy
    total_gold = main_quest['total_gold'] + side_quests['total_gold'] + encounters['total_gold']
    total_exp = main_quest['total_exp'] + side_quests['total_exp'] + encounters['total_exp']
    report.append("TOTAL ECONOMY")
    report.append("-" * 80)
    report.append(f"Total Gold Available: {total_gold}")
    report.append(f"Total EXP Available: {total_exp}")
    report.append("")

    # Equipment Pricing Analysis
    report.append("EQUIPMENT PRICING")
    report.append("-" * 80)
    for tier_name, tier_data in equipment.items():
        if tier_data['items']:
            report.append(f"{tier_name.upper()} Tier ({tier_data['min']}-{tier_data['max'] if tier_data['max'] != float('inf') else '∞'} gold):")
            for item in sorted(tier_data['items'], key=lambda x: x['price']):
                stats_str = ', '.join(f"{k}+{v}" for k, v in item['stat_modifiers'].items())
                report.append(f"  {item['name']}: {item['price']}g ({stats_str}, total: {item['stat_total']})")
            report.append("")

    # Affordability at Progression Points
    report.append("AFFORDABILITY AT PROGRESSION POINTS")
    report.append("-" * 80)

    # After tutorial
    tutorial_gold = main_quest['progression'][0]['cumulative_gold'] if main_quest['progression'] else 0
    affordable = calculate_affordability(tutorial_gold, equipment)
    report.append(f"After Tutorial ({tutorial_gold}g):")
    for tier in ['starter', 'early', 'mid', 'late', 'legendary']:
        if affordable[tier]:
            report.append(f"  {tier}: {len(affordable[tier])} items")
    report.append("")

    # After first 3 main quests
    if len(main_quest['progression']) >= 3:
        quest3_gold = main_quest['progression'][2]['cumulative_gold']
        affordable = calculate_affordability(quest3_gold, equipment)
        report.append(f"After 3 Main Quests ({quest3_gold}g):")
        for tier in ['starter', 'early', 'mid', 'late', 'legendary']:
            if affordable[tier]:
                report.append(f"  {tier}: {len(affordable[tier])} items")
        report.append("")

    # After all main quests
    final_gold = main_quest['total_gold']
    affordable = calculate_affordability(final_gold, equipment)
    report.append(f"After All Main Quests ({final_gold}g):")
    for tier in ['starter', 'early', 'mid', 'late', 'legendary']:
        if affordable[tier]:
            report.append(f"  {tier}: {len(affordable[tier])} items")
    report.append("")

    # Recommendations
    report.append("RECOMMENDATIONS")
    report.append("-" * 80)

    # Check starter equipment affordability
    starter_items = equipment['starter']['items']
    starter_prices = [i['price'] for i in starter_items]
    if starter_prices and min(starter_prices) > tutorial_gold:
        report.append(f"⚠️  Starter equipment ({min(starter_prices)}g) not affordable after tutorial ({tutorial_gold}g)")
    else:
        report.append(f"✓ Starter equipment affordable after tutorial")

    # Check mid-tier affordability (only if we have 3+ quests)
    mid_items = equipment['mid']['items']
    if mid_items and len(main_quest['progression']) >= 3:
        quest3_gold = main_quest['progression'][2]['cumulative_gold']
        mid_prices = [i['price'] for i in mid_items]
        if quest3_gold < min(mid_prices):
            report.append(f"⚠️  Mid-tier equipment ({min(mid_prices)}g) not affordable after 3 quests ({quest3_gold}g)")
        else:
            report.append(f"✓ Mid-tier equipment affordable after 3 quests")
    elif mid_items:
        report.append(f"⚠️  Less than 3 main quests - cannot verify mid-tier affordability")

    # Check legendary affordability
    legendary_items = equipment['legendary']['items']
    if legendary_items:
        legendary_prices = [i['price'] for i in legendary_items]
        if final_gold < min(legendary_prices):
            report.append(f"⚠️  Legendary equipment ({min(legendary_prices)}g) not affordable after main quests ({final_gold}g)")
        else:
            report.append(f"✓ Legendary equipment affordable after main quests")

    report.append("")
    report.append("=" * 80)

    return "\n".join(report)


def main():
    """Main entry point."""
    print("Loading data...")
    encounters_data, quests_data, items_data = load_data()

    print("Analyzing main quest chain...")
    main_quest = analyze_main_quest_chain(quests_data)

    print("Analyzing side quests...")
    side_quests = analyze_side_quests(quests_data)

    print("Analyzing encounters...")
    encounters = analyze_encounter_rewards(encounters_data)

    print("Analyzing equipment pricing...")
    equipment = analyze_equipment_pricing(items_data)

    print("Generating report...")
    report = generate_report(main_quest, side_quests, encounters, equipment)

    print("\n" + report)

    # Save report to file
    report_path = os.path.join(os.path.dirname(__file__), '..', 'ECONOMY_ANALYSIS.md')
    with open(report_path, 'w') as f:
        f.write(report)
    print(f"\nReport saved to: {report_path}")


if __name__ == '__main__':
    main()
