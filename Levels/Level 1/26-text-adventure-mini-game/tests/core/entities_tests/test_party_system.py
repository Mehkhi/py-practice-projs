"""Tests for the party system."""

import copy
import json
import os
import tempfile
import unittest

from core.entities import (
    Player, PartyMember, Entity,
    load_party_members_from_json, SUPPORTED_EQUIP_SLOTS
)
from core.stats import Stats
from core.save_load import SaveManager
from core.world import World, Map, Tile


class TestPartyMember(unittest.TestCase):
    """Test PartyMember class."""

    def test_create_party_member(self):
        """Test creating a basic party member."""
        stats = Stats(100, 100, 50, 50, 10, 5, 8, 7, 5)
        member = PartyMember(
            entity_id="test_member",
            name="Test Member",
            x=0, y=0,
            sprite_id="party_member",
            stats=stats,
            role="fighter"
        )

        self.assertEqual(member.entity_id, "test_member")
        self.assertEqual(member.name, "Test Member")
        self.assertEqual(member.role, "fighter")
        self.assertEqual(member.faction, "player")
        self.assertTrue(member.is_alive())
        self.assertFalse(member.is_dead())

    def test_party_member_death(self):
        """Test party member death state."""
        stats = Stats(100, 0, 50, 50, 10, 5, 8, 7, 5)  # HP = 0
        member = PartyMember(
            entity_id="dead_member",
            name="Dead Member",
            x=0, y=0,
            sprite_id="party_member",
            stats=stats
        )

        self.assertTrue(member.is_dead())
        self.assertFalse(member.is_alive())

    def test_party_member_skills(self):
        """Test party member skills initialization."""
        stats = Stats(100, 100, 50, 50, 10, 5, 8, 7, 5)
        member = PartyMember(
            entity_id="mage",
            name="Mage",
            x=0, y=0,
            sprite_id="party_mage",
            stats=stats,
            role="mage",
            base_skills=["fireball", "heal"]
        )

        self.assertEqual(member.base_skills, ["fireball", "heal"])
        self.assertEqual(member.skills, ["fireball", "heal"])


class TestPlayerPartyManagement(unittest.TestCase):
    """Test Player party management methods."""

    def setUp(self):
        """Set up test fixtures."""
        self.player_stats = Stats(100, 100, 50, 50, 10, 5, 8, 7, 5)
        self.player = Player(
            entity_id="player",
            name="Hero",
            x=0, y=0,
            sprite_id="player",
            stats=self.player_stats
        )

    def _create_member(self, member_id: str, name: str) -> PartyMember:
        """Helper to create a party member."""
        stats = Stats(80, 80, 40, 40, 8, 4, 6, 6, 4)
        return PartyMember(
            entity_id=member_id,
            name=name,
            x=0, y=0,
            sprite_id="party_member",
            stats=stats
        )

    def test_add_party_member(self):
        """Test adding a party member."""
        member = self._create_member("luna", "Luna")

        result = self.player.add_party_member(member)

        self.assertTrue(result)
        self.assertEqual(len(self.player.party), 1)
        self.assertEqual(self.player.party[0].name, "Luna")

    def test_add_duplicate_party_member(self):
        """Test that duplicate party members are rejected."""
        member = self._create_member("luna", "Luna")

        self.player.add_party_member(member)
        result = self.player.add_party_member(member)

        self.assertFalse(result)
        self.assertEqual(len(self.player.party), 1)

    def test_party_size_limit(self):
        """Test that party size is limited."""
        for i in range(self.player.max_party_size):
            member = self._create_member(f"member_{i}", f"Member {i}")
            self.assertTrue(self.player.add_party_member(member))

        # Try to add one more
        extra_member = self._create_member("extra", "Extra")
        result = self.player.add_party_member(extra_member)

        self.assertFalse(result)
        self.assertEqual(len(self.player.party), self.player.max_party_size)

    def test_remove_party_member(self):
        """Test removing a party member."""
        member = self._create_member("luna", "Luna")
        self.player.add_party_member(member)

        removed = self.player.remove_party_member("luna")

        self.assertIsNotNone(removed)
        self.assertEqual(removed.name, "Luna")
        self.assertEqual(len(self.player.party), 0)

    def test_remove_nonexistent_member(self):
        """Test removing a member that doesn't exist."""
        removed = self.player.remove_party_member("nonexistent")

        self.assertIsNone(removed)

    def test_get_party_member(self):
        """Test getting a party member by ID."""
        member = self._create_member("luna", "Luna")
        self.player.add_party_member(member)

        found = self.player.get_party_member("luna")

        self.assertIsNotNone(found)
        self.assertEqual(found.name, "Luna")

    def test_get_alive_party_members(self):
        """Test getting only alive party members."""
        alive_member = self._create_member("alive", "Alive")
        dead_stats = Stats(80, 0, 40, 40, 8, 4, 6, 6, 4)
        dead_member = PartyMember(
            entity_id="dead",
            name="Dead",
            x=0, y=0,
            sprite_id="party_member",
            stats=dead_stats
        )

        self.player.add_party_member(alive_member)
        self.player.add_party_member(dead_member)

        alive = self.player.get_alive_party_members()

        self.assertEqual(len(alive), 1)
        self.assertEqual(alive[0].name, "Alive")

    def test_get_battle_party(self):
        """Test getting the full battle party."""
        member1 = self._create_member("luna", "Luna")
        member2 = self._create_member("brock", "Brock")

        self.player.add_party_member(member1)
        self.player.add_party_member(member2)

        battle_party = self.player.get_battle_party()

        self.assertEqual(len(battle_party), 3)
        self.assertEqual(battle_party[0], self.player)
        self.assertEqual(battle_party[1].name, "Luna")
        self.assertEqual(battle_party[2].name, "Brock")

    def test_is_party_wiped(self):
        """Test party wipe detection."""
        member = self._create_member("luna", "Luna")
        self.player.add_party_member(member)

        # Party is not wiped when player is alive
        self.assertFalse(self.player.is_party_wiped())

        # Kill the player
        self.player.stats.hp = 0

        # Party is not wiped if member is alive
        self.assertFalse(self.player.is_party_wiped())

        # Kill the member
        member.stats.hp = 0

        # Now party is wiped
        self.assertTrue(self.player.is_party_wiped())


class TestPartySaveLoad(unittest.TestCase):
    """Test saving and loading party members."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.save_manager = SaveManager(save_dir=self.temp_dir)

        # Create a simple world with a test map
        self.world = World()
        test_tiles = [[Tile("grass", True, "grass") for _ in range(10)] for _ in range(10)]
        test_map = Map("forest_path", 10, 10, test_tiles)
        self.world.add_map(test_map)

        # Create player with party
        self.player_stats = Stats(100, 100, 50, 50, 10, 5, 8, 7, 5)
        self.player = Player(
            entity_id="player",
            name="Hero",
            x=5, y=5,
            sprite_id="player",
            stats=self.player_stats
        )

        # Add party members
        member_stats = Stats(80, 75, 40, 35, 8, 4, 10, 6, 4)
        self.member = PartyMember(
            entity_id="luna",
            name="Luna",
            x=0, y=0,
            sprite_id="party_luna",
            stats=member_stats,
            role="mage",
            base_skills=["fireball", "heal"]
        )
        self.player.add_party_member(self.member)

    def test_serialize_party(self):
        """Test serializing party members."""
        data = self.save_manager.serialize_state(self.world, self.player)

        self.assertIn("party", data["player"])
        self.assertEqual(len(data["player"]["party"]), 1)

        party_data = data["player"]["party"][0]
        self.assertEqual(party_data["entity_id"], "luna")
        self.assertEqual(party_data["name"], "Luna")
        self.assertEqual(party_data["role"], "mage")
        self.assertEqual(party_data["stats"]["hp"], 75)
        self.assertEqual(party_data["base_skills"], ["fireball", "heal"])

    def test_deserialize_party(self):
        """Test deserializing party members."""
        # Serialize
        data = self.save_manager.serialize_state(self.world, self.player)

        # Create a new world for deserialization with the same map
        new_world = World()
        new_world.maps = self.world.maps.copy()

        # Deserialize
        loaded_player = self.save_manager.deserialize_state(data, new_world)

        self.assertEqual(len(loaded_player.party), 1)
        loaded_member = loaded_player.party[0]

        self.assertEqual(loaded_member.entity_id, "luna")
        self.assertEqual(loaded_member.name, "Luna")
        self.assertEqual(loaded_member.role, "mage")
        self.assertEqual(loaded_member.stats.hp, 75)
        self.assertEqual(loaded_member.base_skills, ["fireball", "heal"])

    def test_save_and_load_slot(self):
        """Test full save/load cycle with party."""
        # Save
        self.save_manager.save_to_slot(1, self.world, self.player)

        # Load
        new_world = World()
        new_world.maps = self.world.maps.copy()
        loaded_player = self.save_manager.load_from_slot(1, new_world)

        self.assertEqual(len(loaded_player.party), 1)
        self.assertEqual(loaded_player.party[0].name, "Luna")


class TestLoadPartyMembersFromJson(unittest.TestCase):
    """Test loading party members from JSON file."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.json_path = os.path.join(self.temp_dir, "party_members.json")

        # Create test JSON data
        self.test_data = {
            "party_members": {
                "test_mage": {
                    "entity_id": "test_mage",
                    "name": "Test Mage",
                    "sprite_id": "party_mage",
                    "role": "mage",
                    "base_skills": ["fireball"],
                    "stats": {
                        "max_hp": 80,
                        "hp": 80,
                        "max_sp": 50,
                        "sp": 50,
                        "attack": 5,
                        "defense": 4,
                        "magic": 12,
                        "speed": 8,
                        "luck": 6
                    }
                }
            }
        }

        with open(self.json_path, "w") as f:
            json.dump(self.test_data, f)

    def test_load_party_members(self):
        """Test loading party members from JSON."""
        members = load_party_members_from_json(self.json_path)

        self.assertEqual(len(members), 1)
        self.assertIn("test_mage", members)

        mage = members["test_mage"]
        self.assertEqual(mage.name, "Test Mage")
        self.assertEqual(mage.role, "mage")
        self.assertEqual(mage.stats.magic, 12)
        self.assertEqual(mage.base_skills, ["fireball"])

    def test_load_nonexistent_file(self):
        """Test loading from a nonexistent file returns empty dict."""
        members = load_party_members_from_json("/nonexistent/path.json")
        self.assertEqual(members, {})


class TestPartyInCombat(unittest.TestCase):
    """Test party members in combat scenarios."""

    def setUp(self):
        """Set up test fixtures."""
        from core.combat import BattleSystem, Skill
        from core.entities import Enemy

        # Create player with party
        self.player_stats = Stats(100, 100, 50, 50, 10, 5, 8, 7, 5)
        self.player = Player(
            entity_id="player",
            name="Hero",
            x=0, y=0,
            sprite_id="player",
            stats=self.player_stats
        )

        # Add party member
        member_stats = Stats(80, 80, 40, 40, 8, 4, 10, 6, 4)
        self.member = PartyMember(
            entity_id="luna",
            name="Luna",
            x=0, y=0,
            sprite_id="party_luna",
            stats=member_stats,
            role="mage",
            base_skills=["fireball"]
        )
        self.player.add_party_member(self.member)

        # Create enemy
        enemy_stats = Stats(50, 50, 20, 20, 8, 3, 5, 7, 3)
        self.enemy = Enemy(
            entity_id="slime",
            name="Slime",
            x=0, y=0,
            sprite_id="enemy",
            stats=enemy_stats
        )

        # Create skills
        self.skills = {
            "fireball": Skill(
                id="fireball",
                name="Fireball",
                power=15,
                cost_sp=10,
                element="fire",
                target_pattern="single_enemy"
            )
        }

    def test_battle_system_with_party(self):
        """Test that battle system accepts party members."""
        from core.combat import BattleSystem

        battle_party = self.player.get_battle_party()
        battle_system = BattleSystem(
            players=battle_party,
            enemies=[self.enemy],
            skills=self.skills
        )

        # Should have 2 player-side participants
        self.assertEqual(len(battle_system.players), 2)
        self.assertEqual(battle_system.players[0].entity.name, "Hero")
        self.assertEqual(battle_system.players[1].entity.name, "Luna")

    def test_party_member_can_act(self):
        """Test that party members can take actions in battle."""
        from core.combat import BattleSystem, BattleCommand, ActionType

        battle_party = self.player.get_battle_party()
        battle_system = BattleSystem(
            players=battle_party,
            enemies=[self.enemy],
            skills=self.skills
        )

        # Queue attack from party member
        cmd = BattleCommand(
            actor_id="luna",
            action_type=ActionType.ATTACK,
            target_ids=["slime"]
        )
        battle_system.queue_player_command(cmd)

        # Should have 1 pending command
        self.assertEqual(len(battle_system.pending_commands), 1)


if __name__ == "__main__":
    unittest.main()
