"""Tests for the battle memory system."""

import unittest

from core.combat import ActionType, BattleCommand, BattleSystem, MemoryOperation
from core.entities import Entity
from core.stats import Stats


class TestMemorySystem(unittest.TestCase):
    """Test memory store/recall/subtract/clear operations."""

    def setUp(self) -> None:
        """Create minimal battle setup."""
        self.player_stats = Stats(
            max_hp=100,
            hp=100,
            max_sp=50,
            sp=50,
            attack=20,
            defense=10,
            magic=15,
            speed=10,
            luck=5,
        )
        self.enemy_stats = Stats(
            max_hp=50,
            hp=50,
            max_sp=20,
            sp=20,
            attack=10,
            defense=5,
            magic=5,
            speed=5,
            luck=3,
        )
        self.player = Entity(
            entity_id="player",
            name="Hero",
            x=0,
            y=0,
            sprite_id="hero",
            stats=self.player_stats,
        )
        self.enemy = Entity(
            entity_id="enemy",
            name="Slime",
            x=1,
            y=0,
            sprite_id="slime",
            stats=self.enemy_stats,
        )
        self.battle = BattleSystem([self.player], [self.enemy], skills={})

    def test_memory_store_attack(self) -> None:
        """Test M+ stores attack stat."""
        cmd = BattleCommand(
            actor_id="player",
            action_type=ActionType.MEMORY,
            memory_operation=MemoryOperation.STORE,
            memory_stat="attack",
        )
        participant = self.battle._find_participant("player")
        self.battle._execute_command(cmd, participant)

        self.assertEqual(participant.memory_value, 20)
        self.assertEqual(participant.memory_stat_type, "attack")

    def test_memory_recall_applies_buff(self) -> None:
        """Test MR applies stored value as buff."""
        participant = self.battle._find_participant("player")
        participant.memory_value = 10
        participant.memory_stat_type = "attack"

        cmd = BattleCommand(
            actor_id="player",
            action_type=ActionType.MEMORY,
            memory_operation=MemoryOperation.RECALL,
        )
        self.battle._execute_command(cmd, participant)

        self.assertIn("memory_attack", participant.stats.equipment_modifiers)
        self.assertIn("memory_boost", participant.stats.status_effects)

    def test_memory_clear(self) -> None:
        """Test MC clears memory."""
        participant = self.battle._find_participant("player")
        participant.memory_value = 50
        participant.memory_stat_type = "defense"

        cmd = BattleCommand(
            actor_id="player",
            action_type=ActionType.MEMORY,
            memory_operation=MemoryOperation.CLEAR,
        )
        self.battle._execute_command(cmd, participant)

        self.assertEqual(participant.memory_value, 0)
        self.assertIsNone(participant.memory_stat_type)

    def test_memory_subtract(self) -> None:
        """Test M- subtracts from stored value."""
        participant = self.battle._find_participant("player")
        participant.memory_value = 30
        participant.memory_stat_type = "attack"

        cmd = BattleCommand(
            actor_id="player",
            action_type=ActionType.MEMORY,
            memory_operation=MemoryOperation.SUBTRACT,
            memory_stat="attack",
        )
        self.battle._execute_command(cmd, participant)

        self.assertEqual(participant.memory_value, 10)

    def test_memory_subtract_floor_zero(self) -> None:
        """Test M- doesn't go below zero."""
        participant = self.battle._find_participant("player")
        participant.memory_value = 5

        cmd = BattleCommand(
            actor_id="player",
            action_type=ActionType.MEMORY,
            memory_operation=MemoryOperation.SUBTRACT,
            memory_stat="attack",
        )
        self.battle._execute_command(cmd, participant)

        self.assertEqual(participant.memory_value, 0)

    def test_memory_store_defense(self) -> None:
        """Test M+ stores defense stat."""
        cmd = BattleCommand(
            actor_id="player",
            action_type=ActionType.MEMORY,
            memory_operation=MemoryOperation.STORE,
            memory_stat="defense",
        )
        participant = self.battle._find_participant("player")
        self.battle._execute_command(cmd, participant)

        self.assertEqual(participant.memory_value, 10)
        self.assertEqual(participant.memory_stat_type, "defense")

    def test_memory_store_magic(self) -> None:
        """Test M+ stores magic stat."""
        cmd = BattleCommand(
            actor_id="player",
            action_type=ActionType.MEMORY,
            memory_operation=MemoryOperation.STORE,
            memory_stat="magic",
        )
        participant = self.battle._find_participant("player")
        self.battle._execute_command(cmd, participant)

        self.assertEqual(participant.memory_value, 15)
        self.assertEqual(participant.memory_stat_type, "magic")

    def test_memory_store_speed(self) -> None:
        """Test M+ stores speed stat."""
        cmd = BattleCommand(
            actor_id="player",
            action_type=ActionType.MEMORY,
            memory_operation=MemoryOperation.STORE,
            memory_stat="speed",
        )
        participant = self.battle._find_participant("player")
        self.battle._execute_command(cmd, participant)

        self.assertEqual(participant.memory_value, 10)
        self.assertEqual(participant.memory_stat_type, "speed")

    def test_memory_store_current_hp(self) -> None:
        """Test M+ stores current HP."""
        participant = self.battle._find_participant("player")
        participant.stats.hp = 75  # Set to non-max HP

        cmd = BattleCommand(
            actor_id="player",
            action_type=ActionType.MEMORY,
            memory_operation=MemoryOperation.STORE,
            memory_stat="current_hp",
        )
        self.battle._execute_command(cmd, participant)

        self.assertEqual(participant.memory_value, 75)
        self.assertEqual(participant.memory_stat_type, "current_hp")

    def test_memory_store_last_damage(self) -> None:
        """Test M+ stores last damage dealt."""
        participant = self.battle._find_participant("player")
        participant.last_damage_dealt = 25

        cmd = BattleCommand(
            actor_id="player",
            action_type=ActionType.MEMORY,
            memory_operation=MemoryOperation.STORE,
            memory_stat="last_damage",
        )
        self.battle._execute_command(cmd, participant)

        self.assertEqual(participant.memory_value, 25)
        self.assertEqual(participant.memory_stat_type, "last_damage")

    def test_memory_recall_empty(self) -> None:
        """Test MR with no stored value shows appropriate message."""
        participant = self.battle._find_participant("player")
        participant.memory_value = 0

        cmd = BattleCommand(
            actor_id="player",
            action_type=ActionType.MEMORY,
            memory_operation=MemoryOperation.RECALL,
        )
        self.battle._execute_command(cmd, participant)

        # Should not apply any buff when memory is empty
        self.assertNotIn("memory_boost", participant.stats.status_effects)
        # Check message log mentions no stored memory
        self.assertTrue(
            any("no stored memory" in msg.lower() for msg in self.battle.message_log)
        )

    def test_memory_recall_defense_buff(self) -> None:
        """Test MR applies defense buff correctly."""
        participant = self.battle._find_participant("player")
        participant.memory_value = 20
        participant.memory_stat_type = "defense"

        cmd = BattleCommand(
            actor_id="player",
            action_type=ActionType.MEMORY,
            memory_operation=MemoryOperation.RECALL,
        )
        self.battle._execute_command(cmd, participant)

        # Recall applies half the stored value as a buff
        self.assertIn("memory_defense", participant.stats.equipment_modifiers)
        self.assertEqual(participant.stats.equipment_modifiers["memory_defense"], 10)
        self.assertIn("memory_boost", participant.stats.status_effects)

    def test_memory_boost_decay(self) -> None:
        """Test memory modifiers are cleared when boost status expires."""
        participant = self.battle._find_participant("player")
        participant.memory_value = 20
        participant.memory_stat_type = "attack"

        # Apply memory recall to add buff
        cmd = BattleCommand(
            actor_id="player",
            action_type=ActionType.MEMORY,
            memory_operation=MemoryOperation.RECALL,
        )
        self.battle._execute_command(cmd, participant)

        # Verify buff is applied
        self.assertIn("memory_attack", participant.stats.equipment_modifiers)
        self.assertIn("memory_boost", participant.stats.status_effects)

        # Simulate status effect expiring by removing it
        participant.stats.remove_status_effect("memory_boost")

        # Trigger decay check
        self.battle._process_memory_boost_decay(participant)

        # Modifiers should be cleared
        self.assertNotIn("memory_attack", participant.stats.equipment_modifiers)

    def test_memory_recall_non_combat_stat(self) -> None:
        """Test MR with non-combat stat shows appropriate message and applies no buff."""
        participant = self.battle._find_participant("player")
        participant.memory_value = 50
        participant.memory_stat_type = "current_hp"

        cmd = BattleCommand(
            actor_id="player",
            action_type=ActionType.MEMORY,
            memory_operation=MemoryOperation.RECALL,
        )
        self.battle._execute_command(cmd, participant)

        # Should not apply any buff for non-combat stat
        self.assertNotIn("memory_current_hp", participant.stats.equipment_modifiers)
        self.assertNotIn("memory_boost", participant.stats.status_effects)
        # Check message log mentions no combat effect
        self.assertTrue(
            any("no combat effect" in msg.lower() for msg in self.battle.message_log)
        )

    def test_memory_recall_last_damage_no_buff(self) -> None:
        """Test MR with last_damage stat shows no combat effect message."""
        participant = self.battle._find_participant("player")
        participant.memory_value = 25
        participant.memory_stat_type = "last_damage"

        cmd = BattleCommand(
            actor_id="player",
            action_type=ActionType.MEMORY,
            memory_operation=MemoryOperation.RECALL,
        )
        self.battle._execute_command(cmd, participant)

        # Should not apply any buff for last_damage
        self.assertNotIn("memory_last_damage", participant.stats.equipment_modifiers)
        self.assertNotIn("memory_boost", participant.stats.status_effects)

    def test_memory_store_overwrites_previous(self) -> None:
        """Test M+ overwrites previous stored value."""
        participant = self.battle._find_participant("player")

        # Store attack first
        cmd1 = BattleCommand(
            actor_id="player",
            action_type=ActionType.MEMORY,
            memory_operation=MemoryOperation.STORE,
            memory_stat="attack",
        )
        self.battle._execute_command(cmd1, participant)
        self.assertEqual(participant.memory_value, 20)
        self.assertEqual(participant.memory_stat_type, "attack")

        # Store defense - should overwrite
        cmd2 = BattleCommand(
            actor_id="player",
            action_type=ActionType.MEMORY,
            memory_operation=MemoryOperation.STORE,
            memory_stat="defense",
        )
        self.battle._execute_command(cmd2, participant)
        self.assertEqual(participant.memory_value, 10)
        self.assertEqual(participant.memory_stat_type, "defense")

    def test_memory_subtract_cumulative(self) -> None:
        """Test multiple M- operations subtract cumulatively."""
        participant = self.battle._find_participant("player")
        participant.memory_value = 50
        participant.memory_stat_type = "attack"

        # First subtract (attack=20)
        cmd = BattleCommand(
            actor_id="player",
            action_type=ActionType.MEMORY,
            memory_operation=MemoryOperation.SUBTRACT,
            memory_stat="attack",
        )
        self.battle._execute_command(cmd, participant)
        self.assertEqual(participant.memory_value, 30)  # 50 - 20

        # Second subtract
        self.battle._execute_command(cmd, participant)
        self.assertEqual(participant.memory_value, 10)  # 30 - 20

        # Third subtract - should floor at 0
        self.battle._execute_command(cmd, participant)
        self.assertEqual(participant.memory_value, 0)  # max(0, 10 - 20)

    def test_memory_recall_shows_half_value_in_message(self) -> None:
        """Test MR message shows the actual applied buff (half of stored value)."""
        participant = self.battle._find_participant("player")
        participant.memory_value = 20
        participant.memory_stat_type = "attack"

        cmd = BattleCommand(
            actor_id="player",
            action_type=ActionType.MEMORY,
            memory_operation=MemoryOperation.RECALL,
        )
        self.battle._execute_command(cmd, participant)

        # The buff applied should be half the stored value (20 // 2 = 10)
        self.assertEqual(participant.stats.equipment_modifiers["memory_attack"], 10)
        # Message should show +10, not +20
        self.assertTrue(
            any("+10 boost" in msg for msg in self.battle.message_log)
        )


if __name__ == "__main__":
    unittest.main()
