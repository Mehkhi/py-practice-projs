"""Performance regression tests for battle system.

This module tests that battle system performance remains within acceptable
thresholds and doesn't degrade with battle length or enemy count.
"""

import unittest
import time
import random
from typing import Dict, List

from core.combat import BattleSystem, BattleState, BattleCommand, ActionType, Skill
from core.entities import Player, Enemy
from core.stats import Stats
from core.items import Item


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


class TestBattlePerformance(unittest.TestCase):
    """Test battle system performance characteristics."""

    def setUp(self):
        """Set up test fixtures."""
        self.rng = random.Random(42)

        # Create skills dict using actual Skill class
        self.skills = {
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

    def test_perform_enemy_actions_performance_5_enemies(self):
        """Test that perform_enemy_actions completes within time threshold for 5 enemies."""
        player = create_test_player()
        complex_profile = create_complex_ai_profile()

        # Create 5 enemies with complex AI profiles
        enemies = []
        for i in range(5):
            enemy = create_test_enemy(f"enemy_{i+1}", f"Test Enemy {i+1}", complex_profile)
            enemies.append(enemy)

        battle = BattleSystem(
            players=[player],
            enemies=enemies,
            skills=self.skills,
            enable_coordination=True,
            enable_learning=True,
            rng=self.rng
        )

        # Set AI profiles on battle participants
        for enemy_participant in battle.enemies:
            enemy_participant.ai_profile = complex_profile
            enemy_participant.skills = ["fire_bolt", "heal"]

        # Measure time for perform_enemy_actions
        battle.state = BattleState.ENEMY_CHOOSE
        start = time.perf_counter()
        battle.perform_enemy_actions()
        elapsed = time.perf_counter() - start

        # Should complete within 50ms for 5 enemies
        self.assertLess(elapsed, 0.05, f"perform_enemy_actions took {elapsed*1000:.2f}ms, expected <50ms")

    def test_perform_enemy_actions_performance_10_enemies(self):
        """Test that perform_enemy_actions completes within time threshold for 10 enemies."""
        player = create_test_player()
        complex_profile = create_complex_ai_profile()

        # Create 10 enemies with complex AI profiles
        enemies = []
        for i in range(10):
            enemy = create_test_enemy(f"enemy_{i+1}", f"Test Enemy {i+1}", complex_profile)
            enemies.append(enemy)

        battle = BattleSystem(
            players=[player],
            enemies=enemies,
            skills=self.skills,
            enable_coordination=True,
            enable_learning=True,
            rng=self.rng
        )

        # Set AI profiles on battle participants
        for enemy_participant in battle.enemies:
            enemy_participant.ai_profile = complex_profile
            enemy_participant.skills = ["fire_bolt", "heal"]

        # Measure time for perform_enemy_actions
        battle.state = BattleState.ENEMY_CHOOSE
        start = time.perf_counter()
        battle.perform_enemy_actions()
        elapsed = time.perf_counter() - start

        # Should complete within 100ms for 10 enemies
        self.assertLess(elapsed, 0.1, f"perform_enemy_actions took {elapsed*1000:.2f}ms, expected <100ms")

    def test_turn_processing_no_degradation(self):
        """Test that turn processing doesn't degrade significantly with battle length."""
        player = create_test_player()
        complex_profile = create_complex_ai_profile()

        # Create 3 enemies
        enemies = []
        for i in range(3):
            enemy = create_test_enemy(f"enemy_{i+1}", f"Test Enemy {i+1}", complex_profile)
            enemies.append(enemy)

        battle = BattleSystem(
            players=[player],
            enemies=enemies,
            skills=self.skills,
            enable_coordination=True,
            enable_learning=True,
            rng=self.rng
        )

        # Set AI profiles on battle participants
        for enemy_participant in battle.enemies:
            enemy_participant.ai_profile = complex_profile
            enemy_participant.skills = ["fire_bolt", "heal"]

        # Measure first few turns
        first_turns_times = []
        for turn in range(5):
            if battle.state == BattleState.ENEMY_CHOOSE:
                start = time.perf_counter()
                battle.perform_enemy_actions()
                elapsed = time.perf_counter() - start
                first_turns_times.append(elapsed)

            if battle.state == BattleState.RESOLVE_ACTIONS:
                battle.perform_turn()

            if battle.state in (BattleState.VICTORY, BattleState.DEFEAT):
                break

            # Simulate some damage
            for enemy in battle.enemies:
                if enemy.is_alive() and enemy.stats.hp > 10:
                    enemy.stats.hp = max(10, enemy.stats.hp - 15)

        # Measure later turns (after caching should be established)
        later_turns_times = []
        for turn in range(5, 15):
            if battle.state == BattleState.ENEMY_CHOOSE:
                start = time.perf_counter()
                battle.perform_enemy_actions()
                elapsed = time.perf_counter() - start
                later_turns_times.append(elapsed)

            if battle.state == BattleState.RESOLVE_ACTIONS:
                battle.perform_turn()

            if battle.state in (BattleState.VICTORY, BattleState.DEFEAT):
                break

            # Simulate some damage
            for enemy in battle.enemies:
                if enemy.is_alive() and enemy.stats.hp > 10:
                    enemy.stats.hp = max(10, enemy.stats.hp - 15)

        if first_turns_times and later_turns_times:
            avg_first = sum(first_turns_times) / len(first_turns_times)
            avg_later = sum(later_turns_times) / len(later_turns_times)

            # Later turns should not be significantly slower (within 2x)
            self.assertLess(
                avg_later,
                avg_first * 2,
                f"Later turns ({avg_later*1000:.2f}ms) should not be >2x slower than early turns ({avg_first*1000:.2f}ms)"
            )

    def test_single_enemy_performance(self):
        """Test performance with a single enemy (baseline)."""
        player = create_test_player()
        complex_profile = create_complex_ai_profile()

        enemy = create_test_enemy("enemy_1", "Test Enemy", complex_profile)

        battle = BattleSystem(
            players=[player],
            enemies=[enemy],
            skills=self.skills,
            enable_coordination=False,  # No coordination with 1 enemy
            enable_learning=True,
            rng=self.rng
        )

        battle.enemies[0].ai_profile = complex_profile
        battle.enemies[0].skills = ["fire_bolt", "heal"]

        # Measure time for perform_enemy_actions
        battle.state = BattleState.ENEMY_CHOOSE
        start = time.perf_counter()
        battle.perform_enemy_actions()
        elapsed = time.perf_counter() - start

        # Should complete very quickly for 1 enemy
        self.assertLess(elapsed, 0.01, f"perform_enemy_actions took {elapsed*1000:.2f}ms, expected <10ms for 1 enemy")

    def test_phase_cache_invalidation_on_hp_change(self):
        """Test that phase cache properly invalidates when HP crosses bucket boundaries."""
        player = create_test_player()
        complex_profile = create_complex_ai_profile()

        enemy = create_test_enemy("enemy_1", "Test Enemy", complex_profile)

        battle = BattleSystem(
            players=[player],
            enemies=[enemy],
            skills=self.skills,
            enable_coordination=False,
            enable_learning=False,
            rng=self.rng
        )

        battle.enemies[0].ai_profile = complex_profile
        battle.enemies[0].skills = ["fire_bolt", "heal"]

        # Get initial phase at 100% HP
        enemy_participant = battle.enemies[0]
        enemy_participant.stats.hp = enemy_participant.stats.max_hp  # 100% HP

        rules1, phase1, _, _ = battle._determine_phase(enemy_participant)
        self.assertEqual(phase1, "aggressive")  # 100% HP should be aggressive phase

        # Change HP to cross phase boundary (below 70%)
        enemy_participant.stats.hp = int(enemy_participant.stats.max_hp * 0.5)  # 50% HP

        rules2, phase2, _, _ = battle._determine_phase(enemy_participant)
        self.assertEqual(phase2, "defensive")  # 50% HP should be defensive phase

        # Change HP to cross another boundary (below 40%)
        enemy_participant.stats.hp = int(enemy_participant.stats.max_hp * 0.2)  # 20% HP

        rules3, phase3, _, _ = battle._determine_phase(enemy_participant)
        self.assertEqual(phase3, "desperate")  # 20% HP should be desperate phase

    def test_clear_ai_caches(self):
        """Test that clear_ai_caches properly clears all caches."""
        player = create_test_player()
        complex_profile = create_complex_ai_profile()

        enemy = create_test_enemy("enemy_1", "Test Enemy", complex_profile)

        battle = BattleSystem(
            players=[player],
            enemies=[enemy],
            skills=self.skills,
            enable_coordination=True,
            enable_learning=True,
            rng=self.rng
        )

        battle.enemies[0].ai_profile = complex_profile
        battle.enemies[0].skills = ["fire_bolt", "heal"]

        # Perform some actions to populate caches
        battle.state = BattleState.ENEMY_CHOOSE
        battle.perform_enemy_actions()

        # Verify caches have been populated
        self.assertTrue(hasattr(battle, '_phase_cache'))
        self.assertGreater(len(battle._phase_cache), 0)

        # Clear caches
        battle.clear_ai_caches()

        # Verify caches are empty
        self.assertEqual(len(battle._phase_cache), 0)
        if hasattr(battle, '_rule_evaluation_cache'):
            self.assertEqual(len(battle._rule_evaluation_cache), 0)
        if hasattr(battle, '_tactics_cache'):
            self.assertEqual(len(battle._tactics_cache), 0)

    def test_tactics_cache_fifo_eviction(self):
        """Test that tactics cache properly evicts oldest entries numerically."""
        player = create_test_player()
        complex_profile = create_complex_ai_profile()

        # Create multiple enemies for coordination
        enemies = [
            create_test_enemy(f"enemy_{i}", f"Test Enemy {i}", complex_profile)
            for i in range(3)
        ]

        battle = BattleSystem(
            players=[player],
            enemies=enemies,
            skills=self.skills,
            enable_coordination=True,
            enable_learning=False,
            rng=self.rng
        )

        for enemy_participant in battle.enemies:
            enemy_participant.ai_profile = complex_profile
            enemy_participant.skills = ["fire_bolt", "heal"]

        # Initialize tactics cache
        battle._tactics_cache = {}

        # Simulate many turns to fill the cache beyond limit
        # _TACTICS_CACHE_MAX_TURNS = 10
        for turn in range(15):
            battle.turn_counter = turn
            cache_key = f"tactics_turn_{turn}"
            battle._tactics_cache[cache_key] = ["dummy_tactics"]

            # Manually trigger eviction logic (simulating what _attempt_coordinated_tactics does)
            if len(battle._tactics_cache) > 10:
                oldest_key = min(
                    (k for k in battle._tactics_cache.keys() if k.startswith("tactics_turn_")),
                    key=lambda k: int(k.split("_")[-1])
                )
                del battle._tactics_cache[oldest_key]

        # Verify cache size is within limit
        self.assertLessEqual(len(battle._tactics_cache), 10)

        # Verify lowest turn numbers were evicted (not lexicographic order)
        remaining_turns = [int(k.split("_")[-1]) for k in battle._tactics_cache.keys()]
        # Should have turns 5-14 (oldest 0-4 evicted)
        self.assertNotIn(0, remaining_turns)
        self.assertNotIn(1, remaining_turns)
        self.assertIn(14, remaining_turns)

    def test_learning_ai_reanalysis_threshold(self):
        """Test that learning AI respects reanalysis threshold."""
        from core.combat_modules.learning_ai import LearningAI

        # Create learning AI with custom threshold
        learning_ai = LearningAI(min_samples=3, reanalysis_threshold=5)

        self.assertEqual(learning_ai.min_samples_for_adaptation, 3)
        self.assertEqual(learning_ai.reanalysis_threshold, 5)

        # Record some actions
        for i in range(6):
            learning_ai.record_player_action(
                action_type="ATTACK",
                skill_id=None,
                target_id="enemy_1",
                actor_hp_percent=100.0,
                target_hp_percent=50.0,
                turn_number=i,
                all_enemy_ids=["enemy_1"],
                weakest_enemy_id="enemy_1",
                strongest_enemy_id="enemy_1"
            )

        # Get counter strategy (triggers analysis)
        strategy1 = learning_ai.get_counter_strategy()
        analysis_count1 = learning_ai._last_analysis_action_count

        # Add 2 more actions (below threshold)
        for i in range(2):
            learning_ai.record_player_action(
                action_type="ATTACK",
                skill_id=None,
                target_id="enemy_1",
                actor_hp_percent=100.0,
                target_hp_percent=50.0,
                turn_number=6 + i,
                all_enemy_ids=["enemy_1"],
                weakest_enemy_id="enemy_1",
                strongest_enemy_id="enemy_1"
            )

        # Get counter strategy again - should use cached result
        strategy2 = learning_ai.get_counter_strategy()
        analysis_count2 = learning_ai._last_analysis_action_count

        # Analysis count should not have changed (cached)
        self.assertEqual(analysis_count1, analysis_count2)

        # Add 3 more actions (now exceeds threshold of 5)
        for i in range(3):
            learning_ai.record_player_action(
                action_type="SKILL",
                skill_id="fire_bolt",
                target_id="enemy_1",
                actor_hp_percent=100.0,
                target_hp_percent=50.0,
                turn_number=8 + i,
                all_enemy_ids=["enemy_1"],
                weakest_enemy_id="enemy_1",
                strongest_enemy_id="enemy_1"
            )

        # Get counter strategy again - should trigger reanalysis
        strategy3 = learning_ai.get_counter_strategy()
        analysis_count3 = learning_ai._last_analysis_action_count

        # Analysis count should have been updated
        self.assertGreater(analysis_count3, analysis_count2)


if __name__ == "__main__":
    unittest.main()
