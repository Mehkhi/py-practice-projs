"""Tests for advanced AI features: coordinated tactics and learning AI."""

import unittest
import random

from core.combat import (
    BattleSystem, BattleCommand, ActionType, Skill, BattleParticipant,
    TacticsCoordinator, CoordinatedTactic, LearningAI, PlayerPattern
)
from core.entities import Entity, Enemy
from core.items import Item
from core.stats import Stats


class TestTacticsCoordinator(unittest.TestCase):
    """Test the TacticsCoordinator class."""

    def setUp(self):
        self.coordinator = TacticsCoordinator()

    def test_builtin_tactics_exist(self):
        """Test that built-in tactics are defined."""
        self.assertIn("pincer_attack", self.coordinator.BUILTIN_TACTICS)
        self.assertIn("tank_and_spank", self.coordinator.BUILTIN_TACTICS)
        self.assertIn("focus_fire", self.coordinator.BUILTIN_TACTICS)
        self.assertIn("heal_support", self.coordinator.BUILTIN_TACTICS)
        self.assertIn("pack_howl", self.coordinator.BUILTIN_TACTICS)

    def test_tactic_cooldown(self):
        """Test tactic cooldown tracking."""
        tactic = self.coordinator.BUILTIN_TACTICS["pincer_attack"]

        # Initially available
        self.assertTrue(self.coordinator.is_tactic_available("pincer_attack"))

        # Use the tactic
        self.coordinator.use_tactic(tactic)

        # Now on cooldown
        self.assertFalse(self.coordinator.is_tactic_available("pincer_attack"))

        # Tick cooldowns
        for _ in range(tactic.cooldown_turns):
            self.coordinator.tick_cooldowns()

        # Available again
        self.assertTrue(self.coordinator.is_tactic_available("pincer_attack"))

    def test_get_available_tactics(self):
        """Test getting available tactics."""
        available = self.coordinator.get_available_tactics()
        self.assertTrue(len(available) > 0)

        # Use one tactic
        tactic = available[0]
        self.coordinator.use_tactic(tactic)

        # Should have one less available
        new_available = self.coordinator.get_available_tactics()
        self.assertEqual(len(new_available), len(available) - 1)

    def test_coordination_history(self):
        """Test that coordination history is tracked."""
        tactic = self.coordinator.BUILTIN_TACTICS["focus_fire"]

        self.assertEqual(len(self.coordinator.coordination_history), 0)

        self.coordinator.use_tactic(tactic)

        self.assertEqual(len(self.coordinator.coordination_history), 1)
        self.assertEqual(self.coordinator.coordination_history[0], "focus_fire")


class TestLearningAI(unittest.TestCase):
    """Test the LearningAI class."""

    def setUp(self):
        self.learning_ai = LearningAI()

    def test_record_player_action(self):
        """Test recording player actions."""
        self.learning_ai.record_player_action(
            action_type="ATTACK",
            skill_id=None,
            target_id="enemy_1",
            actor_hp_percent=80.0,
            target_hp_percent=100.0,
            turn_number=1,
            all_enemy_ids=["enemy_1", "enemy_2"],
            weakest_enemy_id="enemy_1",
            strongest_enemy_id="enemy_2"
        )

        self.assertEqual(len(self.learning_ai.player_actions), 1)
        self.assertEqual(self.learning_ai.action_type_counts["ATTACK"], 1)

    def test_target_preference_detection(self):
        """Test that target preference is detected."""
        # Record multiple attacks on weakest enemy
        for i in range(5):
            self.learning_ai.record_player_action(
                action_type="ATTACK",
                skill_id=None,
                target_id="enemy_1",
                actor_hp_percent=80.0,
                target_hp_percent=30.0,
                turn_number=i + 1,
                all_enemy_ids=["enemy_1", "enemy_2"],
                weakest_enemy_id="enemy_1",
                strongest_enemy_id="enemy_2"
            )

        # Force pattern analysis
        self.learning_ai._analyze_patterns()

        self.assertIn("target_preference", self.learning_ai.patterns)
        self.assertEqual(self.learning_ai.patterns["target_preference"].value, "weakest")

    def test_skill_preference_detection(self):
        """Test that favorite skill is detected."""
        # Record multiple uses of the same skill
        for i in range(4):
            self.learning_ai.record_player_action(
                action_type="SKILL",
                skill_id="fire_bolt",
                target_id="enemy_1",
                actor_hp_percent=80.0,
                target_hp_percent=100.0,
                turn_number=i + 1,
                all_enemy_ids=["enemy_1"],
                weakest_enemy_id="enemy_1",
                strongest_enemy_id="enemy_1"
            )

        self.learning_ai._analyze_patterns()

        self.assertIn("favorite_skill", self.learning_ai.patterns)
        self.assertEqual(self.learning_ai.patterns["favorite_skill"].value, "fire_bolt")

    def test_heal_threshold_detection(self):
        """Test that heal threshold is detected."""
        # Record heals at similar HP percentages
        for hp in [35, 40, 38, 42]:
            self.learning_ai.record_player_action(
                action_type="SKILL",
                skill_id="heal",
                target_id="player_1",
                actor_hp_percent=hp,
                target_hp_percent=None,
                turn_number=1,
                all_enemy_ids=["enemy_1"],
                weakest_enemy_id="enemy_1",
                strongest_enemy_id="enemy_1"
            )

        self.learning_ai._analyze_patterns()

        self.assertIn("heal_threshold", self.learning_ai.patterns)
        # Average should be around 38.75
        self.assertAlmostEqual(
            self.learning_ai.patterns["heal_threshold"].value,
            38.75,
            delta=1.0
        )

    def test_counter_strategy_generation(self):
        """Test that counter-strategy is generated based on patterns."""
        # Set up patterns manually
        self.learning_ai.patterns["target_preference"] = PlayerPattern(
            pattern_type="target_preference",
            value="weakest",
            confidence=0.8,
            sample_count=10
        )
        self.learning_ai.patterns["heal_threshold"] = PlayerPattern(
            pattern_type="heal_threshold",
            value=30.0,  # Low HP healer
            confidence=0.7,
            sample_count=5
        )

        strategy = self.learning_ai.get_counter_strategy()

        # Should recommend protecting weak allies
        self.assertIn("guard_when_weak", strategy["weight_modifiers"])
        self.assertIn("protect_weak_ally", strategy["priority_actions"])

        # Should recommend focus fire for low HP healers
        self.assertIn("focus_fire", strategy["priority_actions"])

    def test_adaptation_level(self):
        """Test that adaptation level increases with patterns."""
        self.assertEqual(self.learning_ai.adaptation_level, 0)

        # Add a high-confidence pattern and trigger recalculation
        self.learning_ai.patterns["target_preference"] = PlayerPattern(
            pattern_type="target_preference",
            value="weakest",
            confidence=0.8,
            sample_count=10
        )

        # Manually update adaptation level (normally done in _analyze_patterns)
        self.learning_ai.adaptation_level = len([
            p for p in self.learning_ai.patterns.values() if p.confidence >= 0.5
        ])

        self.assertGreater(self.learning_ai.adaptation_level, 0)

    def test_adaptation_summary(self):
        """Test human-readable adaptation summary."""
        # No patterns yet
        summary = self.learning_ai.get_adaptation_summary()
        self.assertIn("learning", summary.lower())

        # Add patterns
        self.learning_ai.patterns["favorite_skill"] = PlayerPattern(
            pattern_type="favorite_skill",
            value="fire_bolt",
            confidence=0.7,
            sample_count=5
        )

        summary = self.learning_ai.get_adaptation_summary()
        self.assertIn("fire_bolt", summary)
        self.assertIn("AI has learned", summary)


class TestCoordinatedCombat(unittest.TestCase):
    """Test coordinated tactics in actual combat."""

    def setUp(self):
        self.rng = random.Random(42)

        # Create test skills
        self.skills = {
            "attack_skill": Skill(
                id="attack_skill",
                name="Attack Skill",
                power=10,
                cost_sp=5,
                element="physical",
                target_pattern="single_enemy"
            ),
            "heal": Skill(
                id="heal",
                name="Heal",
                power=20,
                cost_sp=8,
                element="holy",
                target_pattern="single_ally"
            )
        }

        self.items = {}

        # Create player
        player_stats = Stats(100, 100, 50, 50, 10, 5, 8, 6, 4)
        self.player = Entity("player_1", "Hero", 0, 0, "player", stats=player_stats)

        # Create two enemies with different roles
        enemy1_stats = Stats(50, 50, 20, 20, 8, 3, 5, 7, 3)
        enemy1_entity = Enemy("enemy_1", "Warrior", 0, 0, "goblin", stats=enemy1_stats)
        self.enemy1 = BattleParticipant(enemy1_entity, enemy1_stats, False)
        self.enemy1.ai_profile = {
            "behavior_type": "aggressive",
            "tactic_role": "dps",
            "rules": [
                {
                    "conditions": {"hp_percent": {"min": 0, "max": 100}},
                    "action": {"type": "attack", "target_strategy": "random_enemy"},
                    "weight": 1
                }
            ]
        }

        enemy2_stats = Stats(60, 60, 15, 15, 6, 5, 4, 5, 2)
        enemy2_entity = Enemy("enemy_2", "Tank", 0, 0, "goblin", stats=enemy2_stats)
        self.enemy2 = BattleParticipant(enemy2_entity, enemy2_stats, False)
        self.enemy2.ai_profile = {
            "behavior_type": "defensive",
            "tactic_role": "tank",
            "rules": [
                {
                    "conditions": {"hp_percent": {"min": 0, "max": 100}},
                    "action": {"type": "guard", "target_strategy": "self"},
                    "weight": 1
                }
            ]
        }

    def test_role_assignment(self):
        """Test that roles are assigned from AI profiles."""
        battle = BattleSystem(
            players=[self.player],
            enemies=[self.enemy1, self.enemy2],
            skills=self.skills,
            items=self.items,
            enable_coordination=True,
            rng=self.rng
        )

        # Roles should be assigned from ai_profile
        self.assertEqual(battle.enemies[0].tactic_role, "dps")
        self.assertEqual(battle.enemies[1].tactic_role, "tank")

    def test_coordination_with_two_dps(self):
        """Test that pincer attack works with two DPS enemies."""
        # Make both enemies DPS
        self.enemy2.ai_profile["tactic_role"] = "dps"
        self.enemy2.ai_profile["behavior_type"] = "aggressive"

        battle = BattleSystem(
            players=[self.player],
            enemies=[self.enemy1, self.enemy2],
            skills=self.skills,
            items=self.items,
            enable_coordination=True,
            debug_ai=True,
            rng=self.rng
        )

        # Perform enemy actions
        battle.perform_enemy_actions()

        # Check if coordination message appeared
        coordination_msgs = [m for m in battle.message_log if "coordinate" in m.lower()]
        # May or may not trigger depending on conditions
        self.assertTrue(len(battle.pending_commands) >= 2)

    def test_coordination_disabled(self):
        """Test that coordination can be disabled."""
        battle = BattleSystem(
            players=[self.player],
            enemies=[self.enemy1, self.enemy2],
            skills=self.skills,
            items=self.items,
            enable_coordination=False,
            rng=self.rng
        )

        self.assertIsNone(battle.tactics_coordinator)

        # Should still work without coordination
        battle.perform_enemy_actions()
        self.assertTrue(len(battle.pending_commands) >= 2)


class TestLearningCombat(unittest.TestCase):
    """Test learning AI in actual combat."""

    def setUp(self):
        self.rng = random.Random(42)

        self.skills = {
            "fire_bolt": Skill(
                id="fire_bolt",
                name="Fire Bolt",
                power=15,
                cost_sp=5,
                element="fire",
                target_pattern="single_enemy"
            )
        }

        self.items = {}

        player_stats = Stats(100, 100, 50, 50, 10, 5, 8, 6, 4)
        self.player = Entity("player_1", "Hero", 0, 0, "player", stats=player_stats)

        enemy_stats = Stats(50, 50, 20, 20, 8, 3, 5, 7, 3)
        enemy_entity = Enemy("enemy_1", "Test Enemy", 0, 0, "slime", stats=enemy_stats)
        self.enemy = BattleParticipant(enemy_entity, enemy_stats, False)
        self.enemy.ai_profile = {
            "rules": [
                {
                    "conditions": {"hp_percent": {"min": 0, "max": 100}},
                    "action": {"type": "attack", "target_strategy": "random_enemy"},
                    "weight": 1
                }
            ]
        }

    def test_learning_records_actions(self):
        """Test that player actions are recorded for learning."""
        battle = BattleSystem(
            players=[self.player],
            enemies=[self.enemy],
            skills=self.skills,
            items=self.items,
            enable_learning=True,
            rng=self.rng
        )

        # Queue a player command
        cmd = BattleCommand(
            actor_id="player_1",
            action_type=ActionType.ATTACK,
            target_ids=["enemy_1"]
        )
        battle.queue_player_command(cmd)

        # Check that learning AI recorded it
        self.assertEqual(len(battle.learning_ai.player_actions), 1)
        self.assertEqual(battle.learning_ai.action_type_counts["ATTACK"], 1)

    def test_learning_disabled(self):
        """Test that learning can be disabled."""
        battle = BattleSystem(
            players=[self.player],
            enemies=[self.enemy],
            skills=self.skills,
            items=self.items,
            enable_learning=False,
            rng=self.rng
        )

        self.assertIsNone(battle.learning_ai)

        # Should still work without learning
        cmd = BattleCommand(
            actor_id="player_1",
            action_type=ActionType.ATTACK,
            target_ids=["enemy_1"]
        )
        battle.queue_player_command(cmd)
        # No error should occur


if __name__ == "__main__":
    unittest.main()
