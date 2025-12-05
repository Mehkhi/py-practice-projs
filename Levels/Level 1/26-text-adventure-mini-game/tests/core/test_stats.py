"""Unit tests for core/stats.py - Status effect ticking, damage calculation."""

import unittest

from core.stats import Stats, StatusEffect, EXP_TABLE, MAX_LEVEL, LEVEL_UP_STAT_GAINS


class TestStatusEffect(unittest.TestCase):
    def test_status_effect_creation(self):
        effect = StatusEffect(id="poison", duration=3, stacks=1)
        self.assertEqual(effect.id, "poison")
        self.assertEqual(effect.duration, 3)
        self.assertEqual(effect.stacks, 1)

    def test_status_effect_default_stacks(self):
        effect = StatusEffect(id="bleed", duration=5)
        self.assertEqual(effect.stacks, 1)

    def test_tick_decreases_duration(self):
        effect = StatusEffect(id="poison", duration=3)
        stats = Stats(100, 100, 50, 50, 10, 5, 4, 6, 3)
        effect.tick(stats)
        self.assertEqual(effect.duration, 2)

    def test_tick_poison_applies_damage(self):
        effect = StatusEffect(id="poison", duration=3, stacks=1)
        stats = Stats(100, 100, 50, 50, 10, 0, 4, 6, 3)  # 0 defense
        initial_hp = stats.hp
        effect.tick(stats)
        # Poison does 5 * stacks damage, minus defense (min 1)
        self.assertLess(stats.hp, initial_hp)

    def test_tick_poison_scales_with_stacks(self):
        effect = StatusEffect(id="poison", duration=3, stacks=2)
        stats = Stats(100, 100, 50, 50, 10, 0, 4, 6, 3)
        initial_hp = stats.hp
        effect.tick(stats)
        # 2 stacks = 10 damage (before defense)
        expected_damage = max(1, 10 - stats.get_effective_defense())
        self.assertEqual(stats.hp, initial_hp - expected_damage)

    def test_tick_bleed_applies_damage(self):
        effect = StatusEffect(id="bleed", duration=2, stacks=1)
        stats = Stats(100, 100, 50, 50, 10, 0, 4, 6, 3)
        initial_hp = stats.hp
        effect.tick(stats)
        self.assertLess(stats.hp, initial_hp)

    def test_tick_terror_reduces_sp(self):
        effect = StatusEffect(id="terror", duration=2, stacks=1)
        stats = Stats(100, 100, 50, 50, 10, 5, 4, 6, 3)
        initial_sp = stats.sp
        effect.tick(stats)
        # Terror reduces SP by 2 * stacks
        self.assertEqual(stats.sp, initial_sp - 2)

    def test_tick_returns_true_when_expired(self):
        effect = StatusEffect(id="poison", duration=1)
        stats = Stats(100, 100, 50, 50, 10, 5, 4, 6, 3)
        result = effect.tick(stats)
        self.assertTrue(result)
        self.assertEqual(effect.duration, 0)

    def test_tick_returns_false_when_not_expired(self):
        effect = StatusEffect(id="poison", duration=3)
        stats = Stats(100, 100, 50, 50, 10, 5, 4, 6, 3)
        result = effect.tick(stats)
        self.assertFalse(result)

    def test_permanent_effect_never_expires(self):
        effect = StatusEffect(id="limb_missing", duration=-1)
        stats = Stats(100, 100, 50, 50, 10, 5, 4, 6, 3)
        for _ in range(10):
            result = effect.tick(stats)
            self.assertFalse(result)
        self.assertEqual(effect.duration, -1)

    def test_tick_frozen_applies_damage(self):
        """Frozen deals cold damage per turn."""
        effect = StatusEffect(id="frozen", duration=3, stacks=1)
        stats = Stats(100, 100, 50, 50, 10, 0, 4, 6, 3)
        initial_hp = stats.hp
        effect.tick(stats)
        # Frozen does 2 * stacks damage
        self.assertEqual(stats.hp, initial_hp - 2)

    def test_tick_frozen_scales_with_stacks(self):
        """Frozen damage increases with stacks."""
        effect = StatusEffect(id="frozen", duration=3, stacks=3)
        stats = Stats(100, 100, 50, 50, 10, 0, 4, 6, 3)
        initial_hp = stats.hp
        effect.tick(stats)
        # 3 stacks = 6 damage
        self.assertEqual(stats.hp, initial_hp - 6)

    def test_tick_stun_drains_sp(self):
        """Stun drains SP from mental strain."""
        effect = StatusEffect(id="stun", duration=2, stacks=1)
        stats = Stats(100, 100, 50, 50, 10, 5, 4, 6, 3)
        initial_sp = stats.sp
        effect.tick(stats)
        # Stun drains 1 * stacks SP
        self.assertEqual(stats.sp, initial_sp - 1)

    def test_tick_stun_scales_with_stacks(self):
        """Stun SP drain increases with stacks."""
        effect = StatusEffect(id="stun", duration=2, stacks=4)
        stats = Stats(100, 100, 50, 50, 10, 5, 4, 6, 3)
        initial_sp = stats.sp
        effect.tick(stats)
        # 4 stacks = 4 SP drained
        self.assertEqual(stats.sp, initial_sp - 4)

    def test_tick_confusion_may_apply_damage(self):
        """Confusion has a chance to deal self-damage."""
        from unittest.mock import patch

        effect = StatusEffect(id="confusion", duration=3, stacks=1)
        stats = Stats(100, 100, 50, 50, 10, 0, 4, 6, 3)
        initial_hp = stats.hp

        # Mock random to always trigger damage (return value < 0.3)
        with patch('core.stats.random.random', return_value=0.1):
            effect.tick(stats)
            # Should deal 2 * stacks damage
            self.assertEqual(stats.hp, initial_hp - 2)

    def test_tick_confusion_may_not_apply_damage(self):
        """Confusion damage is probabilistic - may not trigger."""
        from unittest.mock import patch

        effect = StatusEffect(id="confusion", duration=3, stacks=1)
        stats = Stats(100, 100, 50, 50, 10, 0, 4, 6, 3)
        initial_hp = stats.hp

        # Mock random to never trigger damage (return value >= 0.3)
        with patch('core.stats.random.random', return_value=0.5):
            effect.tick(stats)
            # Should not deal damage
            self.assertEqual(stats.hp, initial_hp)

    def test_tick_confusion_scales_with_stacks(self):
        """Confusion self-damage scales with stacks when triggered."""
        from unittest.mock import patch

        effect = StatusEffect(id="confusion", duration=3, stacks=3)
        stats = Stats(100, 100, 50, 50, 10, 0, 4, 6, 3)
        initial_hp = stats.hp

        with patch('core.stats.random.random', return_value=0.1):
            effect.tick(stats)
            # 3 stacks = 6 damage
            self.assertEqual(stats.hp, initial_hp - 6)

class TestStats(unittest.TestCase):
    def setUp(self):
        self.stats = Stats(
            max_hp=100,
            hp=100,
            max_sp=50,
            sp=50,
            attack=15,
            defense=10,
            magic=8,
            speed=12,
            luck=5,
        )

    def test_stats_creation(self):
        self.assertEqual(self.stats.max_hp, 100)
        self.assertEqual(self.stats.hp, 100)
        self.assertEqual(self.stats.attack, 15)
        self.assertEqual(self.stats.defense, 10)

    def test_is_dead_false(self):
        self.assertFalse(self.stats.is_dead())

    def test_is_dead_true(self):
        self.stats.hp = 0
        self.assertTrue(self.stats.is_dead())

    def test_apply_damage(self):
        # damage = amount - defense, min 1
        self.stats.apply_damage(20)
        expected_damage = max(1, 20 - self.stats.defense)
        self.assertEqual(self.stats.hp, 100 - expected_damage)

    def test_apply_damage_minimum_one(self):
        self.stats.defense = 100
        self.stats.apply_damage(5)
        self.assertEqual(self.stats.hp, 99)  # min 1 damage

    def test_apply_damage_cannot_go_below_zero(self):
        self.stats.apply_damage(1000)
        self.assertEqual(self.stats.hp, 0)

    def test_heal(self):
        self.stats.hp = 50
        self.stats.heal(30)
        self.assertEqual(self.stats.hp, 80)

    def test_heal_cannot_exceed_max(self):
        self.stats.hp = 90
        self.stats.heal(50)
        self.assertEqual(self.stats.hp, 100)

    def test_restore_sp(self):
        self.stats.sp = 20
        self.stats.restore_sp(15)
        self.assertEqual(self.stats.sp, 35)

    def test_restore_sp_cannot_exceed_max(self):
        self.stats.sp = 45
        self.stats.restore_sp(20)
        self.assertEqual(self.stats.sp, 50)

    def test_add_status_effect_new(self):
        self.stats.add_status_effect("poison", duration=3, stacks=1)
        self.assertIn("poison", self.stats.status_effects)
        self.assertEqual(self.stats.status_effects["poison"].duration, 3)

    def test_add_status_effect_stacks(self):
        self.stats.add_status_effect("poison", duration=3, stacks=1)
        self.stats.add_status_effect("poison", duration=2, stacks=2)
        effect = self.stats.status_effects["poison"]
        self.assertEqual(effect.stacks, 3)  # 1 + 2
        self.assertEqual(effect.duration, 3)  # max(3, 2)

    def test_remove_status_effect(self):
        self.stats.add_status_effect("poison", duration=3)
        result = self.stats.remove_status_effect("poison")
        self.assertTrue(result)
        self.assertNotIn("poison", self.stats.status_effects)

    def test_remove_status_effect_not_present(self):
        result = self.stats.remove_status_effect("nonexistent")
        self.assertFalse(result)

    def test_tick_status_effects_removes_expired(self):
        self.stats.add_status_effect("poison", duration=1)
        self.stats.tick_status_effects()
        self.assertNotIn("poison", self.stats.status_effects)

    def test_tick_status_effects_keeps_active(self):
        self.stats.add_status_effect("poison", duration=5)
        self.stats.tick_status_effects()
        self.assertIn("poison", self.stats.status_effects)
        self.assertEqual(self.stats.status_effects["poison"].duration, 4)

    def test_tick_multiple_status_effects(self):
        self.stats.add_status_effect("poison", duration=2)
        self.stats.add_status_effect("bleed", duration=1)
        self.stats.tick_status_effects()
        self.assertIn("poison", self.stats.status_effects)
        self.assertNotIn("bleed", self.stats.status_effects)


class TestStatsEffectiveValues(unittest.TestCase):
    def setUp(self):
        self.stats = Stats(100, 100, 50, 50, 10, 5, 8, 12, 4)

    def test_get_effective_attack_base(self):
        self.assertEqual(self.stats.get_effective_attack(), 10)

    def test_get_effective_attack_with_equipment(self):
        self.stats.equipment_modifiers["attack"] = 5
        self.assertEqual(self.stats.get_effective_attack(), 15)

    def test_get_effective_attack_limb_missing(self):
        self.stats.add_status_effect("limb_arm_left_missing", duration=-1)
        attack = self.stats.get_effective_attack()
        self.assertEqual(attack, int(10 * 0.7))

    def test_get_effective_attack_both_arms_missing(self):
        self.stats.add_status_effect("limb_arm_left_missing", duration=-1)
        self.stats.add_status_effect("limb_arm_right_missing", duration=-1)
        attack = self.stats.get_effective_attack()
        self.assertEqual(attack, int(int(10 * 0.7) * 0.7))

    def test_get_effective_defense_base(self):
        self.assertEqual(self.stats.get_effective_defense(), 5)

    def test_get_effective_defense_with_equipment(self):
        self.stats.equipment_modifiers["defense"] = 3
        self.assertEqual(self.stats.get_effective_defense(), 8)

    def test_get_effective_magic_base(self):
        self.assertEqual(self.stats.get_effective_magic(), 8)

    def test_get_effective_magic_with_equipment(self):
        self.stats.equipment_modifiers["magic"] = 4
        self.assertEqual(self.stats.get_effective_magic(), 12)

    def test_get_effective_speed_base(self):
        self.assertEqual(self.stats.get_effective_speed(), 12)

    def test_get_effective_speed_with_equipment(self):
        self.stats.equipment_modifiers["speed"] = 2
        self.assertEqual(self.stats.get_effective_speed(), 14)

    def test_get_effective_speed_leg_missing(self):
        self.stats.add_status_effect("limb_leg_left_missing", duration=-1)
        speed = self.stats.get_effective_speed()
        self.assertEqual(speed, int(12 * 0.6))

    def test_get_effective_luck_base(self):
        self.assertEqual(self.stats.get_effective_luck(), 4)

    def test_get_effective_luck_with_equipment(self):
        self.stats.equipment_modifiers["luck"] = 2
        self.assertEqual(self.stats.get_effective_luck(), 6)


class TestStatsDamageCalculation(unittest.TestCase):
    def test_damage_with_zero_defense(self):
        stats = Stats(100, 100, 50, 50, 10, 0, 4, 6, 3)
        stats.apply_damage(25)
        # damage = 25 - 0 = 25, min 1
        self.assertEqual(stats.hp, 75)

    def test_damage_with_high_defense(self):
        stats = Stats(100, 100, 50, 50, 10, 20, 4, 6, 3)
        stats.apply_damage(15)
        # damage = max(1, 15 - 20) = 1
        self.assertEqual(stats.hp, 99)

    def test_damage_equals_defense(self):
        stats = Stats(100, 100, 50, 50, 10, 10, 4, 6, 3)
        stats.apply_damage(10)
        # damage = max(1, 10 - 10) = 1
        self.assertEqual(stats.hp, 99)

    def test_lethal_damage(self):
        stats = Stats(100, 50, 50, 50, 10, 5, 4, 6, 3)
        stats.apply_damage(100)
        self.assertEqual(stats.hp, 0)
        self.assertTrue(stats.is_dead())


class TestLevelingSystem(unittest.TestCase):
    """Tests for the EXP and leveling system."""

    def setUp(self):
        self.stats = Stats(
            max_hp=100,
            hp=100,
            max_sp=50,
            sp=50,
            attack=10,
            defense=5,
            magic=8,
            speed=6,
            luck=3,
        )

    def test_initial_level_and_exp(self):
        self.assertEqual(self.stats.level, 1)
        self.assertEqual(self.stats.exp, 0)

    def test_exp_to_next_level(self):
        # At level 1 with 0 EXP, need 100 EXP to reach level 2
        self.assertEqual(self.stats.exp_to_next_level(), EXP_TABLE[1])

    def test_add_exp_no_level_up(self):
        level_ups = self.stats.add_exp(50)
        self.assertEqual(self.stats.exp, 50)
        self.assertEqual(self.stats.level, 1)
        self.assertEqual(len(level_ups), 0)

    def test_add_exp_single_level_up(self):
        level_ups = self.stats.add_exp(100)
        self.assertEqual(self.stats.level, 2)
        self.assertEqual(self.stats.exp, 100)
        self.assertEqual(len(level_ups), 1)
        self.assertEqual(level_ups[0][0], 2)  # new level

    def test_add_exp_multiple_level_ups(self):
        # Add enough EXP to go from level 1 to level 3
        level_ups = self.stats.add_exp(250)
        self.assertEqual(self.stats.level, 3)
        self.assertEqual(len(level_ups), 2)

    def test_level_up_stat_increases(self):
        initial_max_hp = self.stats.max_hp
        initial_attack = self.stats.attack
        self.stats.add_exp(100)  # Level up to 2
        self.assertEqual(self.stats.max_hp, initial_max_hp + LEVEL_UP_STAT_GAINS["max_hp"])
        self.assertEqual(self.stats.attack, initial_attack + LEVEL_UP_STAT_GAINS["attack"])

    def test_level_up_restores_hp_sp(self):
        self.stats.hp = 50
        self.stats.sp = 20
        self.stats.add_exp(100)  # Level up
        self.assertEqual(self.stats.hp, self.stats.max_hp)
        self.assertEqual(self.stats.sp, self.stats.max_sp)

    def test_max_level_cap(self):
        # Set to max level
        self.stats.level = MAX_LEVEL
        self.stats.exp = EXP_TABLE[-1]
        level_ups = self.stats.add_exp(1000)
        self.assertEqual(self.stats.level, MAX_LEVEL)
        self.assertEqual(len(level_ups), 0)

    def test_exp_to_next_level_at_max(self):
        self.stats.level = MAX_LEVEL
        self.assertEqual(self.stats.exp_to_next_level(), 0)

    def test_get_level_progress(self):
        # At level 1 with 50 EXP, progress should be 50/100 = 0.5
        self.stats.exp = 50
        progress = self.stats.get_level_progress()
        self.assertAlmostEqual(progress, 0.5, places=2)

    def test_get_level_progress_at_max(self):
        self.stats.level = MAX_LEVEL
        self.assertEqual(self.stats.get_level_progress(), 1.0)

    def test_negative_exp_ignored(self):
        level_ups = self.stats.add_exp(-50)
        self.assertEqual(self.stats.exp, 0)
        self.assertEqual(len(level_ups), 0)


if __name__ == "__main__":
    unittest.main()
