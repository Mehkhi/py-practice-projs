"""Performance profiling script for battle system.

This script measures the performance of battle system AI calculations
to identify bottlenecks and optimization opportunities.
"""

import cProfile
import pstats
import io
import sys
import os
import time
import random
from typing import Dict, List

# Add parent directory to path to import game modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.combat import BattleSystem, BattleState, BattleCommand, ActionType
from core.entities import Player, Enemy
from core.stats import Stats
from core.items import Item
from core.data_loader import load_json_file


def create_test_player() -> Player:
    """Create a test player entity."""
    stats = Stats(200, 200, 50, 50, 15, 12, 10, 8, 5)
    player = Player("player_1", "Test Player", 0, 0, "player", stats=stats)
    return player


def create_test_enemy(enemy_id: str, name: str, ai_profile: Dict) -> Enemy:
    """Create a test enemy with the given AI profile."""
    stats = Stats(100, 100, 30, 30, 10, 8, 6, 5, 3)
    enemy = Enemy(
        entity_id=enemy_id,
        name=name,
        x=0,
        y=0,
        sprite_id="enemy",
        stats=stats,
        enemy_type="test"
    )
    enemy.ai_profile = ai_profile
    enemy.skills = ["fire_bolt", "heal"]
    return enemy


def create_complex_ai_profile() -> Dict:
    """Create a complex multi-phase AI profile for testing."""
    return {
        "phases": [
            {
                "name": "aggressive",
                "hp_threshold": 70,
                "rules": [
                    {
                        "conditions": {
                            "hp_percent": {"min": 70, "max": 100},
                            "sp_percent": {"min": 50, "max": 100}
                        },
                        "action": {
                            "type": "skill",
                            "skill_id": "fire_bolt",
                            "target_strategy": "weakest_enemy"
                        },
                        "weight": 8
                    },
                    {
                        "conditions": {
                            "hp_percent": {"min": 70, "max": 100}
                        },
                        "action": {
                            "type": "attack",
                            "target_strategy": "random_enemy"
                        },
                        "weight": 10
                    }
                ]
            },
            {
                "name": "defensive",
                "hp_threshold": 40,
                "rules": [
                    {
                        "conditions": {
                            "hp_percent": {"min": 40, "max": 69},
                            "sp_percent": {"min": 30, "max": 100}
                        },
                        "action": {
                            "type": "skill",
                            "skill_id": "heal",
                            "target_strategy": "self"
                        },
                        "weight": 9
                    },
                    {
                        "conditions": {
                            "hp_percent": {"min": 40, "max": 69}
                        },
                        "action": {
                            "type": "guard",
                            "target_strategy": "self"
                        },
                        "weight": 7
                    },
                    {
                        "conditions": {
                            "hp_percent": {"min": 40, "max": 69}
                        },
                        "action": {
                            "type": "attack",
                            "target_strategy": "weakest_enemy"
                        },
                        "weight": 5
                    }
                ]
            },
            {
                "name": "desperate",
                "hp_threshold": 0,
                "rules": [
                    {
                        "conditions": {
                            "hp_percent": {"min": 0, "max": 39},
                            "sp_percent": {"min": 20, "max": 100}
                        },
                        "action": {
                            "type": "skill",
                            "skill_id": "fire_bolt",
                            "target_strategy": "weakest_enemy"
                        },
                        "weight": 10
                    },
                    {
                        "conditions": {
                            "hp_percent": {"min": 0, "max": 39}
                        },
                        "action": {
                            "type": "attack",
                            "target_strategy": "weakest_enemy"
                        },
                        "weight": 8
                    }
                ]
            }
        ],
        "behavior_type": "aggressive",
        "fallback_action": {
            "type": "attack",
            "target_strategy": "random_enemy"
        }
    }


def run_battle_turns(battle: BattleSystem, num_turns: int) -> None:
    """Run a specified number of battle turns."""
    for turn in range(num_turns):
        # Player turn - issue a simple attack command
        if battle.state == BattleState.PLAYER_CHOOSE:
            alive_enemies = [e for e in battle.enemies if e.is_alive()]
            if not alive_enemies:
                break

            target = alive_enemies[0]
            cmd = BattleCommand(
                actor_id=battle.players[0].entity.entity_id,
                action_type=ActionType.ATTACK,
                target_ids=[target.entity.entity_id]
            )
            battle.queue_player_command(cmd)

        # Enemy turn - AI selects actions
        if battle.state == BattleState.ENEMY_CHOOSE:
            battle.perform_enemy_actions()

        # Resolve actions
        if battle.state == BattleState.RESOLVE_ACTIONS:
            battle.perform_turn()

        # Check if battle is over
        if battle.state in (BattleState.VICTORY, BattleState.DEFEAT, BattleState.ESCAPED):
            break

        # Simulate some damage to enemies to trigger phase changes
        if turn % 3 == 0:
            for enemy in battle.enemies:
                if enemy.is_alive() and enemy.stats.hp > 10:
                    enemy.stats.hp = max(10, enemy.stats.hp - 20)


def profile_battle_performance(num_enemies: int = 5, num_turns: int = 30) -> None:
    """Profile battle system performance with cProfile."""
    print(f"Profiling battle system with {num_enemies} enemies for {num_turns} turns...")
    print("=" * 70)

    # Create test entities
    player = create_test_player()
    from core.combat import Skill
    skills = {
        "fire_bolt": Skill(
            id='fire_bolt',
            name='Fire Bolt',
            power=20,
            cost_sp=10,
            element='fire',
            target_pattern='single_enemy',
            status_inflict_id=None,
            status_chance=0.0
        ),
        "heal": Skill(
            id='heal',
            name='Heal',
            power=30,
            cost_sp=15,
            element='holy',
            target_pattern='self',
            status_inflict_id=None,
            status_chance=0.0
        )
    }

    # Create enemies with complex AI profiles
    enemies = []
    complex_profile = create_complex_ai_profile()
    for i in range(num_enemies):
        enemy = create_test_enemy(
            f"enemy_{i+1}",
            f"Test Enemy {i+1}",
            complex_profile
        )
        enemies.append(enemy)

    # Create battle system
    battle = BattleSystem(
        players=[player],
        enemies=enemies,
        skills=skills,
        enable_coordination=True,
        enable_learning=True,
        rng=random.Random(42)
    )

    # Set AI profiles on battle participants
    for i, enemy_participant in enumerate(battle.enemies):
        enemy_participant.ai_profile = complex_profile
        enemy_participant.skills = ["fire_bolt", "heal"]

    # Profile the battle
    profiler = cProfile.Profile()
    profiler.enable()

    run_battle_turns(battle, num_turns)

    profiler.disable()

    # Generate report
    s = io.StringIO()
    stats = pstats.Stats(profiler, stream=s)
    stats.sort_stats('cumulative')
    stats.print_stats(30)  # Top 30 functions

    print("\nTop 30 functions by cumulative time:")
    print("=" * 70)
    print(s.getvalue())

    # Also print by total time
    s2 = io.StringIO()
    stats2 = pstats.Stats(profiler, stream=s2)
    stats2.sort_stats('tottime')
    stats2.print_stats(30)

    print("\nTop 30 functions by total time (excluding subcalls):")
    print("=" * 70)
    print(s2.getvalue())

    # Measure specific functions
    print("\nDetailed timing for key functions:")
    print("=" * 70)

    # Re-run with timing for specific measurements
    battle2 = BattleSystem(
        players=[player],
        enemies=enemies,
        skills=skills,
        enable_coordination=True,
        enable_learning=True,
        rng=random.Random(42)
    )

    for i, enemy_participant in enumerate(battle2.enemies):
        enemy_participant.ai_profile = complex_profile
        enemy_participant.skills = ["fire_bolt", "heal"]

    # Time perform_enemy_actions
    total_enemy_time = 0
    enemy_action_count = 0

    for turn in range(min(num_turns, 10)):  # Sample 10 turns
        if battle2.state == BattleState.ENEMY_CHOOSE:
            start = time.perf_counter()
            battle2.perform_enemy_actions()
            elapsed = time.perf_counter() - start
            total_enemy_time += elapsed
            enemy_action_count += 1

        if battle2.state == BattleState.RESOLVE_ACTIONS:
            battle2.perform_turn()

        if battle2.state in (BattleState.VICTORY, BattleState.DEFEAT):
            break

        if turn % 3 == 0:
            for enemy in battle2.enemies:
                if enemy.is_alive() and enemy.stats.hp > 10:
                    enemy.stats.hp = max(10, enemy.stats.hp - 20)

    if enemy_action_count > 0:
        avg_time = total_enemy_time / enemy_action_count
        print(f"perform_enemy_actions(): {avg_time*1000:.2f}ms average per call")
        print(f"  Total: {total_enemy_time*1000:.2f}ms for {enemy_action_count} calls")

    print("\n" + "=" * 70)
    print("Profiling complete!")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Profile battle system performance")
    parser.add_argument(
        "--enemies",
        type=int,
        default=5,
        help="Number of enemies in battle (default: 5)"
    )
    parser.add_argument(
        "--turns",
        type=int,
        default=30,
        help="Number of turns to simulate (default: 30)"
    )

    args = parser.parse_args()

    profile_battle_performance(num_enemies=args.enemies, num_turns=args.turns)
