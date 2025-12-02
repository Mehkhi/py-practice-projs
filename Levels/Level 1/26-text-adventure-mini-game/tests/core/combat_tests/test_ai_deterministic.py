"""Deterministic AI unit tests for enhanced enemy AI."""

import importlib
import os
import random
import sys
import unittest
from unittest.mock import Mock, patch

from core.combat import BattleSystem, BattleCommand, ActionType, Skill, BattleParticipant
from core.entities import Entity, Enemy
from core.stats import Stats
from core.items import Item
from engine.config_loader import apply_debug_ai_override


class TestAIDeterministic(unittest.TestCase):
    """Test AI behavior with deterministic random number generation."""

    def setUp(self):
        """Set up test fixtures with seeded RNG."""
        self.rng = random.Random(42)  # Fixed seed for deterministic tests

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
            "heal_skill": Skill(
                id="heal_skill",
                name="Heal",
                power=15,
                cost_sp=3,
                element="holy",
                target_pattern="single_ally"
            )
        }

        # Create test items
        self.items = {
            "health_potion": Item(
                id="health_potion",
                name="Health Potion",
                description="Restores 50 HP",
                item_type="consumable",
                effect_id="heal_50"
            )
        }

        # Create test player
        player_stats = Stats(100, 100, 50, 50, 10, 5, 8, 6, 4)
        self.player = Entity("player_1", "Hero", 0, 0, "player", stats=player_stats)

        # Create test enemy
        enemy_stats = Stats(50, 20, 15, 15, 8, 3, 5, 7, 3)
        enemy_entity = Enemy("enemy_1", "Test Enemy", 0, 0, "slime", stats=enemy_stats)
        self.enemy = BattleParticipant(enemy_entity, enemy_stats, False)

    def test_fallback_action_honor(self):
        """Test that AI profile fallback_action is honored."""
        ai_profile = {
            "fallback_action": {
                "type": "guard",
                "target_strategy": "self"
            }
        }
        self.enemy.ai_profile = ai_profile

        battle_system = BattleSystem(
            players=[self.player],
            enemies=[self.enemy],
            skills=self.skills,
            items=self.items,
            debug_ai=True,
            rng=self.rng
        )

        # No rules, should use fallback action
        command = battle_system._select_ai_action(self.enemy)

        self.assertIsNotNone(command)
        self.assertEqual(command.action_type, ActionType.GUARD)
        self.assertEqual(command.target_ids, ["enemy_1"])

        # Check debug logging
        debug_messages = [msg for msg in battle_system.message_log if "fallback action" in msg]
        self.assertTrue(len(debug_messages) > 0)

    def test_multi_phase_ai(self):
        """Test multi-phase AI with HP thresholds."""
        ai_profile = {
            "phases": [
                {
                    "name": "phase_1",
                    "hp_threshold": 50,
                    "rules": [
                        {
                            "conditions": {"hp_percent": {"min": 0, "max": 100}},
                            "action": {"type": "attack", "target_strategy": "random_enemy"},
                            "weight": 1
                        }
                    ]
                },
                {
                    "name": "phase_2",
                    "hp_threshold": 25,
                    "rules": [
                        {
                            "conditions": {"hp_percent": {"min": 0, "max": 100}},
                            "action": {"type": "guard", "target_strategy": "self"},
                            "weight": 1
                        }
                    ]
                }
            ]
        }
        self.enemy.ai_profile = ai_profile

        battle_system = BattleSystem(
            players=[self.player],
            enemies=[self.enemy],
            skills=self.skills,
            items=self.items,
            debug_ai=True,
            rng=self.rng
        )

        # Phase 1: HP >= 50%
        self.enemy.stats.hp = 45  # 90% HP
        command = battle_system._select_ai_action(self.enemy)
        self.assertEqual(command.action_type, ActionType.ATTACK)

        # Phase 1: HP still >= 50% (60% is still in phase 1 range)
        self.enemy.stats.hp = 30  # 60% HP
        command = battle_system._select_ai_action(self.enemy)
        self.assertEqual(command.action_type, ActionType.ATTACK)

        # Phase 2: HP < 50% (24% is in phase 2 range)
        self.enemy.stats.hp = 12  # 24% HP
        command = battle_system._select_ai_action(self.enemy)
        self.assertEqual(command.action_type, ActionType.GUARD)

    def test_behavior_type_aggressive(self):
        """Test aggressive behavior type modifies weights."""
        ai_profile = {
            "behavior_type": "aggressive",
            "rules": [
                {
                    "conditions": {"hp_percent": {"min": 0, "max": 100}},
                    "action": {"type": "attack", "target_strategy": "random_enemy"},
                    "weight": 20
                },
                {
                    "conditions": {"hp_percent": {"min": 0, "max": 100}},
                    "action": {"type": "guard", "target_strategy": "self"},
                    "weight": 1
                }
            ]
        }
        self.enemy.ai_profile = ai_profile

        battle_system = BattleSystem(
            players=[self.player],
            enemies=[self.enemy],
            skills=self.skills,
            items=self.items,
            debug_ai=True,
            rng=self.rng
        )

        # With aggressive behavior, attack should be chosen despite lower base weight
        command = battle_system._select_ai_action(self.enemy)
        self.assertEqual(command.action_type, ActionType.ATTACK)

    def test_behavior_type_defensive(self):
        """Test defensive behavior type modifies weights."""
        ai_profile = {
            "behavior_type": "defensive",
            "rules": [
                {
                    "conditions": {"hp_percent": {"min": 0, "max": 100}},
                    "action": {"type": "attack", "target_strategy": "random_enemy"},
                    "weight": 10
                },
                {
                    "conditions": {"hp_percent": {"min": 0, "max": 100}},
                    "action": {"type": "guard", "target_strategy": "self"},
                    "weight": 5
                }
            ]
        }
        self.enemy.ai_profile = ai_profile

        battle_system = BattleSystem(
            players=[self.player],
            enemies=[self.enemy],
            skills=self.skills,
            items=self.items,
            debug_ai=True,
            rng=self.rng
        )

        # With defensive behavior, guard should be chosen despite lower base weight
        command = battle_system._select_ai_action(self.enemy)
        self.assertEqual(command.action_type, ActionType.GUARD)

    def test_deterministic_behavior(self):
        """Test that AI behavior is deterministic with seeded RNG."""
        ai_profile = {
            "rules": [
                {
                    "conditions": {"hp_percent": {"min": 0, "max": 100}},
                    "action": {"type": "attack", "target_strategy": "random_enemy"},
                    "weight": 1
                },
                {
                    "conditions": {"hp_percent": {"min": 0, "max": 100}},
                    "action": {"type": "guard", "target_strategy": "self"},
                    "weight": 1
                }
            ]
        }
        self.enemy.ai_profile = ai_profile

        # Create two identical battle systems with same seed
        battle_system1 = BattleSystem(
            players=[self.player],
            enemies=[self.enemy],
            skills=self.skills,
            items=self.items,
            debug_ai=True,
            rng=random.Random(42)
        )

        battle_system2 = BattleSystem(
            players=[self.player],
            enemies=[self.enemy],
            skills=self.skills,
            items=self.items,
            debug_ai=True,
            rng=random.Random(42)
        )

        # Both should make the same choice
        command1 = battle_system1._select_ai_action(self.enemy)
        command2 = battle_system2._select_ai_action(self.enemy)

        self.assertEqual(command1.action_type, command2.action_type)
        self.assertEqual(command1.target_ids, command2.target_ids)

    def test_skill_validation(self):
        """Test that AI validates skill availability and SP cost."""
        ai_profile = {
            "rules": [
                {
                    "conditions": {"hp_percent": {"min": 0, "max": 100}},
                    "action": {"type": "skill", "skill_id": "attack_skill", "target_strategy": "random_enemy"},
                    "weight": 1
                }
            ]
        }
        self.enemy.ai_profile = ai_profile
        self.enemy.skills = ["attack_skill"]

        battle_system = BattleSystem(
            players=[self.player],
            enemies=[self.enemy],
            skills=self.skills,
            items=self.items,
            debug_ai=True,
            rng=self.rng
        )

        # Test with enough SP
        self.enemy.stats.sp = 10
        command = battle_system._select_ai_action(self.enemy)
        self.assertEqual(command.action_type, ActionType.SKILL)
        self.assertEqual(command.skill_id, "attack_skill")

        # Test with insufficient SP (should use fallback)
        self.enemy.stats.sp = 2
        command = battle_system._select_ai_action(self.enemy)
        self.assertEqual(command.action_type, ActionType.ATTACK)  # Default fallback

    def test_item_validation(self):
        """Test that AI validates item availability."""
        ai_profile = {
            "rules": [
                {
                    "conditions": {"hp_percent": {"min": 0, "max": 100}},
                    "action": {"type": "item", "item_id": "health_potion", "target_strategy": "self"},
                    "weight": 1
                }
            ],
            "fallback_action": {
                "type": "attack",
                "target_strategy": "random_enemy"
            }
        }
        self.enemy.ai_profile = ai_profile
        self.enemy.items = {"health_potion": 1}

        battle_system = BattleSystem(
            players=[self.player],
            enemies=[self.enemy],
            skills=self.skills,
            items=self.items,
            debug_ai=True,
            rng=self.rng
        )

        # Test with item available
        command = battle_system._select_ai_action(self.enemy)
        self.assertEqual(command.action_type, ActionType.ITEM)
        self.assertEqual(command.item_id, "health_potion")

        # Test with no items (should use fallback)
        self.enemy.items = {}
        command = battle_system._select_ai_action(self.enemy)
        self.assertEqual(command.action_type, ActionType.ATTACK)

    def test_contextual_fallback_when_hurt(self):
        """Test that low HP enemies guard via contextual fallback."""
        battle_system = BattleSystem(
            players=[self.player],
            enemies=[self.enemy],
            skills=self.skills,
            items=self.items,
            debug_ai=True,
            rng=self.rng
        )

        self.enemy.stats.hp = 10  # <=35% HP triggers guard fallback
        command = battle_system._select_ai_action(self.enemy)

        self.assertIsNotNone(command)
        self.assertEqual(command.action_type, ActionType.GUARD)
        self.assertEqual(command.target_ids, [self.enemy.entity.entity_id])

    def test_status_aware_party_conditions(self):
        """Test ally/enemy status-aware conditions drive rule selection."""
        ally_stats = Stats(40, 40, 10, 10, 7, 3, 4, 6, 2)
        ally_entity = Enemy("enemy_2", "Wolf Ally", 0, 0, "wolf", stats=ally_stats)
        ally = BattleParticipant(ally_entity, ally_stats, False)
        ally.stats.add_status_effect("poison", duration=2)

        ai_profile = {
            "rules": [
                {
                    "conditions": {"ally_status_effects": {"has": ["poison"]}},
                    "action": {"type": "guard", "target_strategy": "self"},
                    "weight": 5
                },
                {
                    "conditions": {"enemy_status_effects": {"any": ["poison", "bleed"]}},
                    "action": {"type": "attack", "target_strategy": "random_enemy"},
                    "weight": 5
                }
            ]
        }
        self.enemy.ai_profile = ai_profile

        battle_system = BattleSystem(
            players=[self.player],
            enemies=[self.enemy, ally],
            skills=self.skills,
            items=self.items,
            debug_ai=True,
            rng=self.rng
        )

        # Ally is poisoned, so guard should be selected
        command = battle_system._select_ai_action(self.enemy)
        self.assertEqual(command.action_type, ActionType.GUARD)

        # Remove ally poison, apply bleed to player to trigger attack rule
        ally.stats.remove_status_effect("poison")
        self.player.stats.add_status_effect("bleed", duration=2)

        command = battle_system._select_ai_action(self.enemy)
        self.assertEqual(command.action_type, ActionType.ATTACK)

    @patch.dict(os.environ, {"AI_DEBUG": "1"}, clear=False)
    def test_debug_ai_flag_via_config_env(self):
        """Ensure env/config toggles debug_ai and surfaces debug logs."""
        config = apply_debug_ai_override({"debug_ai": False})
        self.assertTrue(config.get("debug_ai"))

        self.enemy.ai_profile = {
            "rules": [
                {
                    "conditions": {"hp_percent": {"min": 0, "max": 100}},
                    "action": {"type": "attack", "target_strategy": "random_enemy"},
                    "weight": 1,
                }
            ]
        }

        battle_system = BattleSystem(
            players=[self.player],
            enemies=[self.enemy],
            skills=self.skills,
            items=self.items,
            debug_ai=config.get("debug_ai", False),
            rng=self.rng,
        )

        battle_system._select_ai_action(self.enemy)
        self.assertTrue(
            any("AI Test Enemy" in msg for msg in battle_system.message_log),
            "Expected debug log entries when debug_ai is enabled via env/config.",
        )

    def test_phase_feedback_flag_filters_messages(self):
        """Phase change messages only surface with flag and boss/alpha enemies."""
        ai_profile = {
            "phases": [
                {
                    "name": "phase_1",
                    "hp_threshold": 50,
                    "rules": [
                        {
                            "conditions": {"hp_percent": {"min": 0, "max": 100}},
                            "action": {"type": "attack", "target_strategy": "random_enemy"},
                            "weight": 1,
                        }
                    ],
                }
            ]
        }

        def make_enemy():
            stats = Stats(60, 60, 10, 10, 5, 3, 2, 4, 1)
            entity = Enemy("boss_enemy", "Alpha Guardian", 0, 0, "boss", stats=stats, enemy_type="boss")
            participant = BattleParticipant(entity, stats, False)
            participant.ai_profile = ai_profile
            return participant

        enemy_no_flag = make_enemy()
        battle_no_flag = BattleSystem(
            players=[self.player],
            enemies=[enemy_no_flag],
            skills=self.skills,
            items=self.items,
            phase_feedback=False,
            rng=self.rng,
        )
        battle_no_flag._select_ai_action(enemy_no_flag)
        self.assertFalse(
            any("shifts tactics" in msg for msg in battle_no_flag.message_log),
            "Phase feedback should not appear when disabled.",
        )

        enemy_flag = make_enemy()
        battle_flag = BattleSystem(
            players=[self.player],
            enemies=[enemy_flag],
            skills=self.skills,
            items=self.items,
            phase_feedback=True,
            rng=self.rng,
        )
        battle_flag._select_ai_action(enemy_flag)
        self.assertTrue(
            any("shifts tactics" in msg for msg in battle_flag.message_log),
            "Phase feedback should appear for boss/alpha when enabled.",
        )


class TestAIValidationHelpers(unittest.TestCase):
    """Unit tests for AI validation helper utilities."""

    @staticmethod
    def _world_scene_class():
        with patch.dict(sys.modules, {"pygame": Mock()}):
            return importlib.import_module("engine.world_scene").WorldScene

    def test_validation_warns_for_missing_skill_and_item(self):
        WorldScene = self._world_scene_class()
        ai_profile = {
            "rules": [
                {
                    "conditions": {},
                    "action": {"type": "skill", "skill_id": "missing_skill", "target_strategy": "random_enemy"},
                },
                {
                    "conditions": {},
                    "action": {"type": "item", "item_id": "missing_item", "target_strategy": "self"},
                },
            ]
        }
        warnings = []
        WorldScene._validate_ai_profile_dict(
            ai_profile,
            skills={"known": object()},
            items_db={"health_potion": object()},
            encounter_id="encounter_test",
            enemy_id="enemy_test",
            warn=warnings.append,
        )
        self.assertTrue(any("missing_skill" in w for w in warnings))
        self.assertTrue(any("missing_item" in w for w in warnings))

    def test_missing_profile_warning_respects_allow_default(self):
        WorldScene = self._world_scene_class()
        warnings = []
        WorldScene._warn_missing_profile("enc_id", {"id": "enemy_no_ai"}, warn=warnings.append)
        self.assertTrue(warnings)

        warnings.clear()
        WorldScene._warn_missing_profile("enc_id", {"id": "enemy_default", "allow_default_ai": True}, warn=warnings.append)
        self.assertFalse(warnings)


if __name__ == '__main__':
    unittest.main()
