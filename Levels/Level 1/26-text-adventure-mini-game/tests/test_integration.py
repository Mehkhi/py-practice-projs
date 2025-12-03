"""Integration tests for end-to-end workflows across multiple systems."""

import json
import os
import random
import shutil
import tempfile
import unittest
from typing import Dict, List, Optional, Tuple
from unittest.mock import Mock, MagicMock

from core.world import World, Map, Tile
from core.entities import Player, PartyMember
from core.items import Inventory, Item
from core.stats import Stats
from core.quests import QuestManager, QuestStatus, ObjectiveType, Quest, QuestObjective
from core.crafting import CraftingSystem, CraftingProgress, Recipe, discover_recipes_for_player
from core.save_load import SaveManager
from core.skill_tree import SkillTree, SkillNode, SkillTreeProgress, SkillTreeManager

# Fishing system imports
from core.fishing import (
    FishingSystem,
    Fish,
    FishingSpot,
    CaughtFish,
    FishRarity,
    WaterType,
)

# Gambling system imports
from core.gambling import (
    GamblingManager,
    DiceGame,
    BlackjackGame,
    SlotsGame,
    CupsGame,
    GamblingGameType,
)

# Arena system imports
from core.arena import ArenaManager, ArenaFighter, ArenaMatch

# NPC schedule imports
from core.npc_schedules import ScheduleManager, NPCSchedule, ScheduleEntry
from core.time_system import TimeOfDay

# Tutorial system imports
from core.tutorial_system import TutorialManager, TutorialTip, HelpEntry, TipTrigger


class TestQuestCompletionFlow(unittest.TestCase):
    """Integration tests for complete quest workflows."""

    def setUp(self):
        """Set up test fixtures."""
        self.world = World()
        tiles = [[Tile("grass", True, "grass") for _ in range(5)] for _ in range(5)]
        self.world.add_map(Map(map_id="forest_path", width=5, height=5, tiles=tiles))
        tiles2 = [[Tile("grass", True, "grass") for _ in range(5)] for _ in range(5)]
        self.world.add_map(Map(map_id="cave", width=5, height=5, tiles=tiles2))

        self.stats = Stats(100, 100, 50, 50, 10, 5, 8, 7, 5)
        self.inventory = Inventory()
        self.player = Player(
            entity_id="player_1",
            name="Hero",
            x=2, y=2,
            sprite_id="hero",
            stats=self.stats,
            inventory=self.inventory,
        )

        self.quest_manager = QuestManager()

        # Create crafting progress for recipe discovery tests
        self.player.crafting_progress = CraftingProgress()

    def test_quest_prerequisites_unlocking(self):
        """Test that quests unlock when required flags/quests are met."""
        # Create a quest that requires a flag
        quest_data = {
            "id": "test_quest",
            "name": "Test Quest",
            "description": "A test quest",
            "status": "locked",
            "required_flags": ["flag_required"],
            "objectives": [
                {
                    "id": "obj1",
                    "description": "Complete objective",
                    "type": "flag",
                    "target": "objective_flag",
                    "required_count": 1
                }
            ],
            "reward_gold": 100
        }
        quest = Quest.from_definition(quest_data)
        self.quest_manager.quests["test_quest"] = quest

        # Quest should be locked initially
        self.assertEqual(quest.status, QuestStatus.LOCKED)

        # Set the required flag
        self.world.set_flag("flag_required", True)

        # Check prerequisites - quest should unlock
        newly_available = self.quest_manager.check_prerequisites(self.world.flags)
        self.assertIn("test_quest", newly_available)
        self.assertEqual(quest.status, QuestStatus.AVAILABLE)

    def test_quest_prerequisites_with_completed_quest(self):
        """Test that quests unlock when required quests are completed."""
        # Create prerequisite quest
        prereq_quest = Quest(
            id="prereq_quest",
            name="Prerequisite Quest",
            description="Must complete first",
            status=QuestStatus.ACTIVE,
            objectives=[QuestObjective(id="obj1", description="Complete", required_count=1)]
        )
        prereq_quest.objectives[0].set_completed()
        self.quest_manager.quests["prereq_quest"] = prereq_quest
        self.quest_manager.complete_quest("prereq_quest")

        # Create quest that requires the prerequisite
        quest_data = {
            "id": "dependent_quest",
            "name": "Dependent Quest",
            "description": "Requires prereq",
            "status": "locked",
            "required_quests": ["prereq_quest"],
            "objectives": []
        }
        quest = Quest.from_definition(quest_data)
        self.quest_manager.quests["dependent_quest"] = quest

        # Check prerequisites
        newly_available = self.quest_manager.check_prerequisites(self.world.flags)
        self.assertIn("dependent_quest", newly_available)
        self.assertEqual(quest.status, QuestStatus.AVAILABLE)

    def test_quest_prerequisites_with_flags_and_quests(self):
        """Test that quests require BOTH flags AND completed quests to unlock."""
        # Create and complete prerequisite quest
        prereq_quest = Quest(
            id="prereq_quest",
            name="Prerequisite Quest",
            description="Must complete first",
            status=QuestStatus.ACTIVE,
            objectives=[QuestObjective(id="obj1", description="Complete", required_count=1)]
        )
        prereq_quest.objectives[0].set_completed()
        self.quest_manager.quests["prereq_quest"] = prereq_quest
        self.quest_manager.complete_quest("prereq_quest")

        # Create quest requiring both flag and completed quest
        quest_data = {
            "id": "combined_prereq_quest",
            "name": "Combined Prereq Quest",
            "description": "Requires both",
            "status": "locked",
            "required_flags": ["special_flag"],
            "required_quests": ["prereq_quest"],
            "objectives": []
        }
        quest = Quest.from_definition(quest_data)
        self.quest_manager.quests["combined_prereq_quest"] = quest

        # With only quest completed, should NOT unlock
        newly_available = self.quest_manager.check_prerequisites(self.world.flags)
        self.assertNotIn("combined_prereq_quest", newly_available)
        self.assertEqual(quest.status, QuestStatus.LOCKED)

        # Set the flag - now should unlock
        self.world.set_flag("special_flag", True)
        newly_available = self.quest_manager.check_prerequisites(self.world.flags)
        self.assertIn("combined_prereq_quest", newly_available)
        self.assertEqual(quest.status, QuestStatus.AVAILABLE)

    def test_kill_objective_updates_from_enemy_kills(self):
        """Test that KILL objectives update when enemies are killed."""
        quest = Quest(
            id="kill_quest",
            name="Kill Quest",
            description="Kill 5 goblins",
            status=QuestStatus.ACTIVE,
            objectives=[
                QuestObjective(
                    id="kill_goblins",
                    description="Kill 5 goblins",
                    objective_type=ObjectiveType.KILL,
                    target="goblin",
                    required_count=5
                )
            ]
        )
        self.quest_manager.quests["kill_quest"] = quest

        # Kill 4 goblins (not enough to complete)
        for _ in range(4):
            updated_quests = self.quest_manager.on_enemy_killed("goblin")
            # Should not report completion until all 5 are killed
            self.assertNotIn("kill_quest", updated_quests)

        objective = quest.get_objective("kill_goblins")
        self.assertEqual(objective.current_count, 4)
        self.assertFalse(objective.completed)

        # Kill 1 more (total 5) - should complete
        updated_quests = self.quest_manager.on_enemy_killed("goblin")
        self.assertIn("kill_quest", updated_quests)

        objective = quest.get_objective("kill_goblins")
        self.assertEqual(objective.current_count, 5)
        self.assertTrue(objective.completed)

    def test_collect_objective_updates_from_item_collection(self):
        """Test that COLLECT objectives update when items are collected."""
        quest = Quest(
            id="collect_quest",
            name="Collect Quest",
            description="Collect 3 herbs",
            status=QuestStatus.ACTIVE,
            objectives=[
                QuestObjective(
                    id="collect_herbs",
                    description="Collect 3 herbs",
                    objective_type=ObjectiveType.COLLECT,
                    target="herb",
                    required_count=3
                )
            ]
        )
        self.quest_manager.quests["collect_quest"] = quest

        # Collect 2 items (not enough to complete)
        self.inventory.add("herb", 2)
        updated_quests = self.quest_manager.on_item_collected("herb", 2)
        # Should not report completion until all 3 are collected
        self.assertNotIn("collect_quest", updated_quests)

        objective = quest.get_objective("collect_herbs")
        self.assertEqual(objective.current_count, 2)
        self.assertFalse(objective.completed)

        # Collect 1 more (total 3) - should complete
        self.inventory.add("herb", 1)
        updated_quests = self.quest_manager.on_item_collected("herb", 1)
        self.assertIn("collect_quest", updated_quests)

        objective = quest.get_objective("collect_herbs")
        self.assertEqual(objective.current_count, 3)
        self.assertTrue(objective.completed)

    def test_talk_objective_updates_from_npc_interaction(self):
        """Test that TALK objectives update when talking to NPCs."""
        quest = Quest(
            id="talk_quest",
            name="Talk Quest",
            description="Talk to merchant",
            status=QuestStatus.ACTIVE,
            objectives=[
                QuestObjective(
                    id="talk_merchant",
                    description="Talk to merchant",
                    objective_type=ObjectiveType.TALK,
                    target="merchant",
                    required_count=1
                )
            ]
        )
        self.quest_manager.quests["talk_quest"] = quest

        # Talk to NPC
        updated_quests = self.quest_manager.on_npc_talked("merchant")
        self.assertIn("talk_quest", updated_quests)

        objective = quest.get_objective("talk_merchant")
        self.assertTrue(objective.completed)

    def test_reach_objective_updates_from_map_entry(self):
        """Test that REACH objectives update when entering maps."""
        quest = Quest(
            id="reach_quest",
            name="Reach Quest",
            description="Reach the cave",
            status=QuestStatus.ACTIVE,
            objectives=[
                QuestObjective(
                    id="reach_cave",
                    description="Reach the cave",
                    objective_type=ObjectiveType.REACH,
                    target="cave",
                    required_count=1
                )
            ]
        )
        self.quest_manager.quests["reach_quest"] = quest

        # Enter map
        updated_quests = self.quest_manager.on_map_entered("cave")
        self.assertIn("reach_quest", updated_quests)

        objective = quest.get_objective("reach_cave")
        self.assertTrue(objective.completed)

    def test_flag_objective_updates_from_flag_setting(self):
        """Test that FLAG objectives update when flags are set."""
        quest = Quest(
            id="flag_quest",
            name="Flag Quest",
            description="Set the flag",
            status=QuestStatus.ACTIVE,
            objectives=[
                QuestObjective(
                    id="set_flag",
                    description="Set the flag",
                    objective_type=ObjectiveType.FLAG,
                    target="objective_flag",
                    required_count=1
                )
            ]
        )
        self.quest_manager.quests["flag_quest"] = quest

        # Set flag
        self.world.set_flag("objective_flag", True)
        updated_quests = self.quest_manager.check_flag_objectives(self.world.flags)
        self.assertIn("flag_quest", updated_quests)

        objective = quest.get_objective("set_flag")
        self.assertTrue(objective.completed)

    def test_quest_completion_applies_rewards(self):
        """Test that quest completion applies all rewards correctly."""
        # Set up player with initial state
        initial_gold = self.world.flags.get("gold", 0)
        initial_exp = self.player.stats.exp

        quest = Quest(
            id="reward_quest",
            name="Reward Quest",
            description="Complete for rewards",
            status=QuestStatus.ACTIVE,
            objectives=[
                QuestObjective(id="obj1", description="Complete", required_count=1)
            ],
            reward_gold=200,
            reward_exp=100,
            reward_items={"health_potion": 3, "sword": 1},
            reward_flags=["quest_completed_flag"],
            reward_recipes=["health_potion_recipe"]
        )
        quest.objectives[0].set_completed()
        self.quest_manager.quests["reward_quest"] = quest

        # Complete quest
        completed_quest = self.quest_manager.complete_quest("reward_quest")
        self.assertIsNotNone(completed_quest)

        # Apply rewards manually (simulating world_scene._award_quest_rewards)
        # Note: We manually apply rewards here because the actual reward logic
        # is in world_scene._award_quest_rewards, which requires pygame context.
        # This test verifies that each reward type can be applied correctly.
        if completed_quest:
            # Gold
            current_gold = self.world.flags.get("gold", 0)
            self.world.set_flag("gold", current_gold + completed_quest.reward_gold)

            # EXP
            self.player.stats.add_exp(completed_quest.reward_exp)

            # Items
            for item_id, quantity in completed_quest.reward_items.items():
                self.inventory.add(item_id, quantity)

            # Flags
            for flag in completed_quest.reward_flags:
                self.world.set_flag(flag, True)

            # Recipes
            if completed_quest.reward_recipes:
                discover_recipes_for_player(self.player, completed_quest.reward_recipes)

        # Verify rewards
        self.assertEqual(self.world.flags.get("gold", 0), initial_gold + 200)
        self.assertEqual(self.player.stats.exp, initial_exp + 100)
        self.assertEqual(self.inventory.get_quantity("health_potion"), 3)
        self.assertEqual(self.inventory.get_quantity("sword"), 1)
        self.assertTrue(self.world.flags.get("quest_completed_flag", False))
        self.assertIn("health_potion_recipe", self.player.crafting_progress.discovered_recipes)

    def test_quest_completion_unlocks_new_quests(self):
        """Test that completing a quest unlocks dependent quests."""
        # Create first quest
        quest1 = Quest(
            id="quest1",
            name="First Quest",
            description="First quest",
            status=QuestStatus.ACTIVE,
            objectives=[QuestObjective(id="obj1", description="Complete", required_count=1)]
        )
        quest1.objectives[0].set_completed()
        self.quest_manager.quests["quest1"] = quest1
        self.quest_manager.complete_quest("quest1")

        # Create dependent quest
        quest2_data = {
            "id": "quest2",
            "name": "Second Quest",
            "description": "Depends on quest1",
            "status": "locked",
            "required_quests": ["quest1"],
            "objectives": []
        }
        quest2 = Quest.from_definition(quest2_data)
        self.quest_manager.quests["quest2"] = quest2

        # Check prerequisites - quest2 should unlock
        newly_available = self.quest_manager.check_prerequisites(self.world.flags)
        self.assertIn("quest2", newly_available)
        self.assertEqual(quest2.status, QuestStatus.AVAILABLE)


class TestSaveLoadRoundTrip(unittest.TestCase):
    """Integration tests for save/load round-trips."""

    def setUp(self):
        """Set up test fixtures."""
        self.save_dir = tempfile.mkdtemp()
        self.save_manager = SaveManager(save_dir=self.save_dir)

        # Create world
        self.world = World()
        tiles = [[Tile("grass", True, "grass") for _ in range(5)] for _ in range(5)]
        self.world.add_map(Map(map_id="forest_path", width=5, height=5, tiles=tiles))
        tiles2 = [[Tile("grass", True, "grass") for _ in range(5)] for _ in range(5)]
        self.world.add_map(Map(map_id="cave", width=5, height=5, tiles=tiles2))
        self.world.set_flag("test_flag", True)
        self.world.set_flag("gold", 500)
        self.world.current_map_id = "forest_path"

        # Create player
        self.stats = Stats(100, 80, 50, 40, 15, 10, 8, 12, 5)
        self.stats.add_exp(100)
        self.inventory = Inventory()
        self.inventory.add("health_potion", 5)
        self.inventory.add("sword", 1)
        self.inventory.set_hotbar_item(1, "health_potion")

        self.player = Player(
            entity_id="player_1",
            name="TestHero",
            x=3, y=3,
            sprite_id="hero",
            stats=self.stats,
            inventory=self.inventory,
        )
        self.player.base_skills = ["slash", "heal"]
        self.player.skills = ["slash", "heal"]
        self.player.equipment["weapon"] = "sword"
        self.player.player_class = "warrior"
        self.player.player_subclass = "berserker"

        # Create quest manager
        self.quest_manager = QuestManager()
        quest = Quest(
            id="test_quest",
            name="Test Quest",
            description="A test quest",
            status=QuestStatus.ACTIVE,
            objectives=[
                QuestObjective(id="obj1", description="Objective", required_count=3)
            ]
        )
        quest.objectives[0].update_progress(2)
        self.quest_manager.quests["test_quest"] = quest

    def tearDown(self):
        """Clean up temporary directory."""
        import shutil
        shutil.rmtree(self.save_dir, ignore_errors=True)

    def test_world_state_persistence(self):
        """Test that world state persists across save/load."""
        # Save
        self.save_manager.save_to_slot(1, self.world, self.player, self.quest_manager)

        # Create new world and load
        new_world = World()
        tiles = [[Tile("grass", True, "grass") for _ in range(5)] for _ in range(5)]
        new_world.add_map(Map(map_id="forest_path", width=5, height=5, tiles=tiles))
        tiles2 = [[Tile("grass", True, "grass") for _ in range(5)] for _ in range(5)]
        new_world.add_map(Map(map_id="cave", width=5, height=5, tiles=tiles2))

        new_quest_manager = QuestManager()
        loaded_player = self.save_manager.load_from_slot(
            1, new_world, new_quest_manager
        )

        # Verify world state
        self.assertEqual(new_world.current_map_id, "forest_path")
        self.assertTrue(new_world.flags.get("test_flag", False))
        self.assertEqual(new_world.flags.get("gold", 0), 500)

    def test_player_state_persistence(self):
        """Test that player state persists across save/load."""
        # Save
        self.save_manager.save_to_slot(1, self.world, self.player, self.quest_manager)

        # Load
        new_world = World()
        tiles = [[Tile("grass", True, "grass") for _ in range(5)] for _ in range(5)]
        new_world.add_map(Map(map_id="forest_path", width=5, height=5, tiles=tiles))
        tiles2 = [[Tile("grass", True, "grass") for _ in range(5)] for _ in range(5)]
        new_world.add_map(Map(map_id="cave", width=5, height=5, tiles=tiles2))

        new_quest_manager = QuestManager()
        loaded_player = self.save_manager.load_from_slot(
            1, new_world, new_quest_manager
        )

        # Verify player state
        self.assertEqual(loaded_player.entity_id, "player_1")
        self.assertEqual(loaded_player.name, "TestHero")
        self.assertEqual(loaded_player.x, 3)
        self.assertEqual(loaded_player.y, 3)
        # Stats may be modified by equipment, so check base stats or effective stats
        # Equipment modifiers are applied on load, so effective stats may differ
        self.assertGreaterEqual(loaded_player.stats.max_hp, 100)  # May be higher due to equipment
        self.assertEqual(loaded_player.stats.exp, 100)
        self.assertEqual(loaded_player.inventory.get_quantity("health_potion"), 5)
        self.assertEqual(loaded_player.inventory.get_quantity("sword"), 1)
        self.assertEqual(loaded_player.inventory.get_hotbar_item(1), "health_potion")
        self.assertEqual(loaded_player.equipment["weapon"], "sword")
        self.assertIn("slash", loaded_player.skills)
        self.assertIn("heal", loaded_player.skills)
        self.assertEqual(loaded_player.player_class, "warrior")
        self.assertEqual(loaded_player.player_subclass, "berserker")

    def test_quest_state_persistence(self):
        """Test that quest state persists across save/load."""
        # Save
        self.save_manager.save_to_slot(1, self.world, self.player, self.quest_manager)

        # Load
        new_world = World()
        tiles = [[Tile("grass", True, "grass") for _ in range(5)] for _ in range(5)]
        new_world.add_map(Map(map_id="forest_path", width=5, height=5, tiles=tiles))
        tiles2 = [[Tile("grass", True, "grass") for _ in range(5)] for _ in range(5)]
        new_world.add_map(Map(map_id="cave", width=5, height=5, tiles=tiles2))

        new_quest_manager = QuestManager()
        # Load quest definitions first
        quest_data = {
            "id": "test_quest",
            "name": "Test Quest",
            "description": "A test quest",
            "objectives": [
                {
                    "id": "obj1",
                    "description": "Objective",
                    "type": "kill",
                    "target": "goblin",
                    "required_count": 3
                }
            ]
        }
        quest = Quest.from_definition(quest_data)
        new_quest_manager.quests["test_quest"] = quest

        loaded_player = self.save_manager.load_from_slot(
            1, new_world, new_quest_manager
        )

        # Verify quest state
        loaded_quest = new_quest_manager.get_quest("test_quest")
        self.assertIsNotNone(loaded_quest)
        self.assertEqual(loaded_quest.status, QuestStatus.ACTIVE)
        objective = loaded_quest.get_objective("obj1")
        self.assertIsNotNone(objective)
        self.assertEqual(objective.current_count, 2)

    def test_party_state_persistence(self):
        """Test that party state persists across save/load."""
        # Add party member
        member_stats = Stats(80, 80, 40, 40, 8, 4, 6, 6, 4)
        party_member = PartyMember(
            entity_id="luna",
            name="Luna",
            x=0, y=0,
            sprite_id="luna",
            stats=member_stats,
            role="mage"
        )
        party_member.formation_position = "middle"
        self.player.add_party_member(party_member)
        self.player.party_formation["luna"] = "middle"

        # Save
        self.save_manager.save_to_slot(1, self.world, self.player, self.quest_manager)

        # Load
        new_world = World()
        tiles = [[Tile("grass", True, "grass") for _ in range(5)] for _ in range(5)]
        new_world.add_map(Map(map_id="forest_path", width=5, height=5, tiles=tiles))
        tiles2 = [[Tile("grass", True, "grass") for _ in range(5)] for _ in range(5)]
        new_world.add_map(Map(map_id="cave", width=5, height=5, tiles=tiles2))

        new_quest_manager = QuestManager()
        loaded_player = self.save_manager.load_from_slot(
            1, new_world, new_quest_manager
        )

        # Verify party state
        self.assertEqual(len(loaded_player.party), 1)
        loaded_member = loaded_player.get_party_member("luna")
        self.assertIsNotNone(loaded_member)
        self.assertEqual(loaded_member.name, "Luna")
        self.assertEqual(loaded_member.formation_position, "middle")
        self.assertEqual(loaded_player.party_formation.get("luna"), "middle")

    def test_crafting_state_persistence(self):
        """Test that crafting state persists across save/load."""
        # Set up crafting progress
        self.player.crafting_progress = CraftingProgress()
        self.player.crafting_progress.crafting_level = 3
        self.player.crafting_progress.crafting_xp = 75
        self.player.crafting_progress.discover_recipe("health_potion")
        self.player.crafting_progress.record_craft("health_potion")

        # Save
        self.save_manager.save_to_slot(1, self.world, self.player, self.quest_manager)

        # Load
        new_world = World()
        tiles = [[Tile("grass", True, "grass") for _ in range(5)] for _ in range(5)]
        new_world.add_map(Map(map_id="forest_path", width=5, height=5, tiles=tiles))
        tiles2 = [[Tile("grass", True, "grass") for _ in range(5)] for _ in range(5)]
        new_world.add_map(Map(map_id="cave", width=5, height=5, tiles=tiles2))

        new_quest_manager = QuestManager()
        loaded_player = self.save_manager.load_from_slot(
            1, new_world, new_quest_manager
        )

        # Verify crafting state
        self.assertIsNotNone(loaded_player.crafting_progress)
        self.assertEqual(loaded_player.crafting_progress.crafting_level, 3)
        self.assertEqual(loaded_player.crafting_progress.crafting_xp, 75)
        self.assertIn("health_potion", loaded_player.crafting_progress.discovered_recipes)
        self.assertEqual(loaded_player.crafting_progress.crafted_counts.get("health_potion"), 1)

    def test_skill_tree_state_persistence(self):
        """Test that skill tree state persists across save/load."""
        # Set up skill tree progress
        self.player.skill_tree_progress = SkillTreeProgress()
        self.player.skill_tree_progress.skill_points = 5
        self.player.skill_tree_progress.skill_points_total = 10
        self.player.skill_tree_progress.unlocked_nodes["warrior"] = {"node1", "node2"}

        # Save
        self.save_manager.save_to_slot(1, self.world, self.player, self.quest_manager)

        # Load
        new_world = World()
        tiles = [[Tile("grass", True, "grass") for _ in range(5)] for _ in range(5)]
        new_world.add_map(Map(map_id="forest_path", width=5, height=5, tiles=tiles))
        tiles2 = [[Tile("grass", True, "grass") for _ in range(5)] for _ in range(5)]
        new_world.add_map(Map(map_id="cave", width=5, height=5, tiles=tiles2))

        new_quest_manager = QuestManager()
        loaded_player = self.save_manager.load_from_slot(
            1, new_world, new_quest_manager
        )

        # Verify skill tree state
        self.assertIsNotNone(loaded_player.skill_tree_progress)
        self.assertEqual(loaded_player.skill_tree_progress.skill_points, 5)
        self.assertEqual(loaded_player.skill_tree_progress.skill_points_total, 10)
        self.assertIn("node1", loaded_player.skill_tree_progress.unlocked_nodes.get("warrior", set()))
        self.assertIn("node2", loaded_player.skill_tree_progress.unlocked_nodes.get("warrior", set()))

    def test_complex_state_persistence(self):
        """Test that complex game state with multiple systems persists."""
        # Set up complex state
        member_stats = Stats(80, 80, 40, 40, 8, 4, 6, 6, 4)
        party_member = PartyMember(
            entity_id="luna",
            name="Luna",
            x=0, y=0,
            sprite_id="luna",
            stats=member_stats
        )
        self.player.add_party_member(party_member)

        self.player.crafting_progress = CraftingProgress()
        self.player.crafting_progress.discover_recipe("health_potion")

        self.player.skill_tree_progress = SkillTreeProgress()
        self.player.skill_tree_progress.skill_points = 3

        # Save
        self.save_manager.save_to_slot(1, self.world, self.player, self.quest_manager)

        # Load
        new_world = World()
        tiles = [[Tile("grass", True, "grass") for _ in range(5)] for _ in range(5)]
        new_world.add_map(Map(map_id="forest_path", width=5, height=5, tiles=tiles))
        tiles2 = [[Tile("grass", True, "grass") for _ in range(5)] for _ in range(5)]
        new_world.add_map(Map(map_id="cave", width=5, height=5, tiles=tiles2))

        new_quest_manager = QuestManager()
        quest_data = {
            "id": "test_quest",
            "name": "Test Quest",
            "description": "A test quest",
            "objectives": [
                {
                    "id": "obj1",
                    "description": "Objective",
                    "type": "kill",
                    "target": "goblin",
                    "required_count": 3
                }
            ]
        }
        quest = Quest.from_definition(quest_data)
        new_quest_manager.quests["test_quest"] = quest

        loaded_player = self.save_manager.load_from_slot(
            1, new_world, new_quest_manager
        )

        # Verify all state
        self.assertEqual(len(loaded_player.party), 1)
        self.assertIsNotNone(loaded_player.crafting_progress)
        self.assertIsNotNone(loaded_player.skill_tree_progress)
        self.assertEqual(loaded_player.skill_tree_progress.skill_points, 3)


class TestPartyRecruitment(unittest.TestCase):
    """Integration tests for party recruitment and management."""

    def setUp(self):
        """Set up test fixtures."""
        self.world = World()
        tiles = [[Tile("grass", True, "grass") for _ in range(5)] for _ in range(5)]
        self.world.add_map(Map(map_id="forest_path", width=5, height=5, tiles=tiles))

        self.stats = Stats(100, 100, 50, 50, 10, 5, 8, 7, 5)
        self.inventory = Inventory()
        self.player = Player(
            entity_id="player_1",
            name="Hero",
            x=2, y=2,
            sprite_id="hero",
            stats=self.stats,
            inventory=self.inventory,
        )

        # Create party member prototype
        member_stats = Stats(80, 80, 40, 40, 8, 4, 12, 6, 4)
        self.party_prototype = PartyMember(
            entity_id="luna",
            name="Luna",
            x=0, y=0,
            sprite_id="luna",
            stats=member_stats,
            role="mage",
            base_skills=["fireball", "heal"]
        )
        self.party_prototypes = {"luna": self.party_prototype}

    def test_recruitment_via_dialogue_flag(self):
        """Test that dialogue flag triggers party member recruitment."""
        # Simulate dialogue setting recruitment flag
        recruitment_flag = "luna_recruited"
        self.world.set_flag(recruitment_flag, True)

        # Simulate _check_recruitment logic
        if recruitment_flag.endswith("_recruited"):
            member_id = recruitment_flag[:-len("_recruited")]

            if member_id in self.party_prototypes:
                prototype = self.party_prototypes[member_id]

                # Check if already in party
                if not self.player.get_party_member(member_id):
                    # Clone party member
                    new_member = PartyMember(
                        entity_id=prototype.entity_id,
                        name=prototype.name,
                        x=prototype.x,
                        y=prototype.y,
                        sprite_id=prototype.sprite_id,
                        stats=Stats(
                            prototype.stats.max_hp,
                            prototype.stats.hp,
                            prototype.stats.max_sp,
                            prototype.stats.sp,
                            prototype.stats.attack,
                            prototype.stats.defense,
                            prototype.stats.magic,
                            prototype.stats.speed,
                            prototype.stats.luck
                        ),
                        role=prototype.role,
                        base_skills=list(prototype.base_skills) if prototype.base_skills else [],
                        skills=list(prototype.skills) if prototype.skills else []
                    )

                    # Add to party
                    self.player.add_party_member(new_member)

        # Verify recruitment
        member = self.player.get_party_member("luna")
        self.assertIsNotNone(member)
        self.assertEqual(member.name, "Luna")
        self.assertEqual(member.role, "mage")
        self.assertIn("fireball", member.skills)

    def test_party_member_cloning_includes_all_fields(self):
        """Test that party member cloning includes all required fields."""
        # Set formation position on prototype
        self.party_prototype.formation_position = "middle"

        # Clone member
        new_member = PartyMember(
            entity_id=self.party_prototype.entity_id,
            name=self.party_prototype.name,
            x=self.party_prototype.x,
            y=self.party_prototype.y,
            sprite_id=self.party_prototype.sprite_id,
            stats=Stats(
                self.party_prototype.stats.max_hp,
                self.party_prototype.stats.hp,
                self.party_prototype.stats.max_sp,
                self.party_prototype.stats.sp,
                self.party_prototype.stats.attack,
                self.party_prototype.stats.defense,
                self.party_prototype.stats.magic,
                self.party_prototype.stats.speed,
                self.party_prototype.stats.luck
            ),
            role=self.party_prototype.role,
            base_skills=list(self.party_prototype.base_skills) if self.party_prototype.base_skills else [],
            skills=list(self.party_prototype.skills) if self.party_prototype.skills else []
        )
        new_member.formation_position = getattr(self.party_prototype, "formation_position", "front")

        self.player.add_party_member(new_member)

        # Verify all fields
        member = self.player.get_party_member("luna")
        self.assertEqual(member.formation_position, "middle")
        self.assertEqual(member.stats.max_hp, 80)
        self.assertEqual(member.stats.magic, 12)
        self.assertIn("fireball", member.skills)

    def test_party_formation_positions(self):
        """Test that formation positions work correctly."""
        # Add multiple party members with different positions
        member1 = PartyMember(
            entity_id="luna",
            name="Luna",
            x=0, y=0,
            sprite_id="luna",
            stats=Stats(80, 80, 40, 40, 8, 4, 12, 6, 4),
            role="mage"
        )
        member1.formation_position = "back"
        self.player.add_party_member(member1)
        self.player.party_formation["luna"] = "back"

        member2 = PartyMember(
            entity_id="brock",
            name="Brock",
            x=0, y=0,
            sprite_id="brock",
            stats=Stats(120, 120, 25, 25, 14, 10, 2, 5, 4),
            role="fighter"
        )
        member2.formation_position = "front"
        self.player.add_party_member(member2)
        self.player.party_formation["brock"] = "front"

        # Verify formation positions
        luna = self.player.get_party_member("luna")
        brock = self.player.get_party_member("brock")
        self.assertEqual(luna.formation_position, "back")
        self.assertEqual(brock.formation_position, "front")
        self.assertEqual(self.player.party_formation["luna"], "back")
        self.assertEqual(self.player.party_formation["brock"], "front")

    def test_party_save_load_persistence(self):
        """Test that party members persist across save/load."""
        # Add party member
        member = PartyMember(
            entity_id="luna",
            name="Luna",
            x=0, y=0,
            sprite_id="luna",
            stats=Stats(80, 80, 40, 40, 8, 4, 12, 6, 4),
            role="mage"
        )
        member.formation_position = "middle"
        self.player.add_party_member(member)
        self.player.party_formation["luna"] = "middle"

        # Save
        save_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, save_dir, ignore_errors=True)
        save_manager = SaveManager(save_dir=save_dir)
        quest_manager = QuestManager()
        save_manager.save_to_slot(1, self.world, self.player, quest_manager)

        # Load
        new_world = World()
        tiles = [[Tile("grass", True, "grass") for _ in range(5)] for _ in range(5)]
        new_world.add_map(Map(map_id="forest_path", width=5, height=5, tiles=tiles))

        new_quest_manager = QuestManager()
        loaded_player = save_manager.load_from_slot(1, new_world, new_quest_manager)

        # Verify party persistence
        self.assertEqual(len(loaded_player.party), 1)
        loaded_member = loaded_player.get_party_member("luna")
        self.assertIsNotNone(loaded_member)
        self.assertEqual(loaded_member.name, "Luna")
        self.assertEqual(loaded_member.formation_position, "middle")
        self.assertEqual(loaded_player.party_formation.get("luna"), "middle")

    def test_world_scene_check_party_recruitment_adds_member_and_sets_formation(self):
        """WorldScene._check_party_recruitment should add members using prototypes."""
        from engine.world_scene import WorldScene

        # Mark Luna as recruited via world flag
        self.world.set_flag("luna_recruited", True)
        self.world.set_flag("luna_joined", False)

        # Ensure prototype has a distinct formation
        self.party_prototype.formation_position = "back"

        # Dummy manager exposing party_prototypes through get_manager
        class DummyAchievements:
            def __init__(self):
                self.calls: List[str] = []

            def on_party_member_recruited(self, member_id: str) -> None:
                self.calls.append(member_id)

        class DummyManager:
            def __init__(self, party_prototypes, achievement_manager):
                self.party_prototypes = party_prototypes
                self.achievement_manager = achievement_manager

            def get_manager(self, name, caller=""):
                return getattr(self, name, None)

        # Minimal scene stub with the attributes used by _check_party_recruitment
        class DummyScene:
            pass

        messages: List[str] = []

        scene = DummyScene()
        scene.world = self.world
        scene.player = self.player
        scene.items_db = {}
        achievements = DummyAchievements()
        scene.manager = DummyManager(self.party_prototypes, achievements)
        scene._show_inline_message = lambda text: messages.append(text)
        scene.get_manager_attr = lambda name, caller="": scene.manager.get_manager(name, caller)

        # Run recruitment logic
        WorldScene._check_party_recruitment(scene)  # type: ignore[arg-type]

        # Verify party member was added with correct formation
        member = self.player.get_party_member("luna")
        self.assertIsNotNone(member)
        self.assertEqual(member.name, "Luna")
        self.assertEqual(member.formation_position, "back")
        self.assertEqual(self.player.party_formation.get("luna"), "back")
        self.assertTrue(self.world.get_flag("luna_joined"))
        self.assertTrue(any("joined the party" in msg for msg in messages))
        self.assertEqual(achievements.calls, ["luna"])

        # Calling again should not add duplicates
        WorldScene._check_party_recruitment(scene)  # type: ignore[arg-type]
        self.assertEqual(len(self.player.party), 1)
        self.assertEqual(achievements.calls, ["luna"])


class TestCraftingWorkflow(unittest.TestCase):
    """Integration tests for crafting workflows."""

    def setUp(self):
        """Set up test fixtures."""
        self.world = World()
        tiles = [[Tile("grass", True, "grass") for _ in range(5)] for _ in range(5)]
        self.world.add_map(Map(map_id="forest_path", width=5, height=5, tiles=tiles))

        self.stats = Stats(100, 100, 50, 50, 10, 5, 8, 7, 5)
        self.inventory = Inventory()
        self.player = Player(
            entity_id="player_1",
            name="Hero",
            x=2, y=2,
            sprite_id="hero",
            stats=self.stats,
            inventory=self.inventory,
        )

        # Create crafting system
        self.crafting_system = CraftingSystem()
        recipe = Recipe(
            id="health_potion",
            name="Health Potion",
            description="Restores HP",
            category="alchemy",
            ingredients={"herb": 2, "water": 1},
            result_item_id="health_potion",
            result_quantity=1,
            required_level=1
        )
        self.crafting_system.recipes["health_potion"] = recipe
        self.crafting_system.categories["alchemy"] = {"name": "Alchemy"}

        # Create crafting progress
        self.player.crafting_progress = CraftingProgress()

    def test_recipe_discovery_from_quest_rewards(self):
        """Test that recipes are discovered from quest rewards."""
        quest = Quest(
            id="recipe_quest",
            name="Recipe Quest",
            description="Get recipe",
            status=QuestStatus.ACTIVE,
            objectives=[QuestObjective(id="obj1", description="Complete", required_count=1)],
            reward_recipes=["health_potion"]
        )
        quest.objectives[0].set_completed()

        # Simulate quest completion reward
        if quest.reward_recipes:
            newly_discovered = discover_recipes_for_player(self.player, quest.reward_recipes)

        # Verify recipe discovery
        self.assertIn("health_potion", self.player.crafting_progress.discovered_recipes)
        self.assertEqual(len(newly_discovered), 1)
        self.assertIn("health_potion", newly_discovered)

    def test_recipe_discovery_from_dialogue_choice(self):
        """Test that recipes are discovered from dialogue choices."""
        # Simulate dialogue choice with recipe discovery
        recipe_ids = ["health_potion"]
        newly_discovered = discover_recipes_for_player(self.player, recipe_ids)

        # Verify recipe discovery
        self.assertIn("health_potion", self.player.crafting_progress.discovered_recipes)
        self.assertEqual(len(newly_discovered), 1)

    def test_recipe_auto_discovery_from_inventory(self):
        """Test that recipes are auto-discovered from inventory items."""
        # Create a basic recipe that should auto-discover
        basic_recipe = Recipe(
            id="simple_salve",
            name="Simple Salve",
            description="Basic healing item",
            category="basic",  # Basic recipes auto-discover
            ingredients={"herb": 1},
            result_item_id="simple_salve",
            result_quantity=1,
            required_level=1
        )
        self.crafting_system.recipes["simple_salve"] = basic_recipe

        # Add an ingredient - this should trigger discovery of basic recipes
        self.inventory.add("herb", 1)

        # Auto-discover recipes
        newly_discovered = self.crafting_system.discover_recipes_from_items(
            self.player.inventory,
            self.player.crafting_progress
        )

        # Basic recipes with ingredients should be discovered
        self.assertIn("simple_salve", newly_discovered)
        self.assertIn("simple_salve", self.player.crafting_progress.discovered_recipes)

    def test_crafting_process_with_ingredients(self):
        """Test that crafting works when ingredients are available."""
        # Add ingredients
        self.inventory.add("herb", 2)
        self.inventory.add("water", 1)
        self.player.crafting_progress.discover_recipe("health_potion")

        # Craft
        recipe = self.crafting_system.get_recipe("health_potion")
        success, message = self.crafting_system.craft(
            recipe,
            self.player.inventory,
            self.player.crafting_progress
        )

        # Verify crafting
        self.assertTrue(success)
        self.assertEqual(self.inventory.get_quantity("herb"), 0)
        self.assertEqual(self.inventory.get_quantity("water"), 0)
        self.assertEqual(self.inventory.get_quantity("health_potion"), 1)

    def test_crafting_consumes_ingredients(self):
        """Test that crafting consumes ingredients correctly."""
        # Add ingredients
        self.inventory.add("herb", 5)
        self.inventory.add("water", 3)
        self.player.crafting_progress.discover_recipe("health_potion")

        # Craft multiple times
        recipe = self.crafting_system.get_recipe("health_potion")
        self.crafting_system.craft(recipe, self.player.inventory, self.player.crafting_progress)
        self.crafting_system.craft(recipe, self.player.inventory, self.player.crafting_progress)

        # Verify ingredients consumed
        self.assertEqual(self.inventory.get_quantity("herb"), 1)  # 5 - 2*2 = 1
        self.assertEqual(self.inventory.get_quantity("water"), 1)  # 3 - 2*1 = 1
        self.assertEqual(self.inventory.get_quantity("health_potion"), 2)

    def test_crafting_xp_and_level_up(self):
        """Test that crafting grants XP and levels up correctly."""
        initial_level = self.player.crafting_progress.crafting_level
        initial_xp = self.player.crafting_progress.crafting_xp

        # Add ingredients and discover recipe
        self.inventory.add("herb", 10)
        self.inventory.add("water", 10)
        self.player.crafting_progress.discover_recipe("health_potion")

        # Craft multiple times to gain XP
        recipe = self.crafting_system.get_recipe("health_potion")
        for _ in range(5):
            self.crafting_system.craft(recipe, self.player.inventory, self.player.crafting_progress)

        # Verify XP gained
        self.assertGreater(self.player.crafting_progress.crafting_xp, initial_xp)
        # May have leveled up depending on XP required

    def test_crafting_level_requirement_enforced(self):
        """Test that crafting level requirements are enforced."""
        # Create high-level recipe
        high_level_recipe = Recipe(
            id="advanced_potion",
            name="Advanced Potion",
            description="High level potion",
            category="alchemy",
            ingredients={"herb": 1},
            result_item_id="advanced_potion",
            required_level=5
        )
        self.crafting_system.recipes["advanced_potion"] = high_level_recipe

        # Set crafting level to 1
        self.player.crafting_progress.crafting_level = 1
        self.player.crafting_progress.discover_recipe("advanced_potion")

        # Add ingredients
        self.inventory.add("herb", 1)

        # Try to craft - should fail
        success, message = self.crafting_system.craft(
            high_level_recipe,
            self.player.inventory,
            self.player.crafting_progress
        )

        self.assertFalse(success)
        self.assertIn("level", message.lower())
        self.assertEqual(self.inventory.get_quantity("herb"), 1)  # Ingredients not consumed

    def test_crafting_progress_save_load(self):
        """Test that crafting progress persists across save/load."""
        # Set up crafting progress
        self.player.crafting_progress.crafting_level = 3
        self.player.crafting_progress.crafting_xp = 75
        self.player.crafting_progress.discover_recipe("health_potion")
        self.player.crafting_progress.record_craft("health_potion")

        # Save
        save_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, save_dir, ignore_errors=True)
        save_manager = SaveManager(save_dir=save_dir)
        quest_manager = QuestManager()
        save_manager.save_to_slot(1, self.world, self.player, quest_manager)

        # Load
        new_world = World()
        tiles = [[Tile("grass", True, "grass") for _ in range(5)] for _ in range(5)]
        new_world.add_map(Map(map_id="forest_path", width=5, height=5, tiles=tiles))

        new_quest_manager = QuestManager()
        loaded_player = save_manager.load_from_slot(1, new_world, new_quest_manager)

        # Verify crafting progress
        self.assertIsNotNone(loaded_player.crafting_progress)
        self.assertEqual(loaded_player.crafting_progress.crafting_level, 3)
        self.assertEqual(loaded_player.crafting_progress.crafting_xp, 75)
        self.assertIn("health_potion", loaded_player.crafting_progress.discovered_recipes)
        self.assertEqual(loaded_player.crafting_progress.crafted_counts.get("health_potion"), 1)

    def test_crafted_items_usable(self):
        """Test that crafted items are usable (in inventory)."""
        # Craft item
        self.inventory.add("herb", 2)
        self.inventory.add("water", 1)
        self.player.crafting_progress.discover_recipe("health_potion")

        recipe = self.crafting_system.get_recipe("health_potion")
        success, _ = self.crafting_system.craft(
            recipe,
            self.player.inventory,
            self.player.crafting_progress
        )

        # Verify item is in inventory
        self.assertTrue(success)
        self.assertTrue(self.inventory.has("health_potion", 1))
        self.assertEqual(self.inventory.get_quantity("health_potion"), 1)


class TestFishingIntegration(unittest.TestCase):
    """Integration tests for fishing system records, stats, and serialization."""

    def setUp(self):
        """Set up test fixtures with minimal fish database and spots."""
        # Create minimal fish database
        self.fish_db = {
            "common_carp": Fish(
                fish_id="common_carp",
                name="Common Carp",
                rarity=FishRarity.COMMON,
                base_value=10,
                water_types=[WaterType.FRESHWATER],
                time_periods=[],  # Any time
                min_size=0.5,
                max_size=2.0,
                catch_difficulty=2,
                description="A common freshwater fish.",
                item_id="fish_common_carp",
            ),
            "golden_trout": Fish(
                fish_id="golden_trout",
                name="Golden Trout",
                rarity=FishRarity.RARE,
                base_value=50,
                water_types=[WaterType.FRESHWATER, WaterType.MAGICAL],
                time_periods=["DAWN", "DUSK"],
                min_size=0.3,
                max_size=1.5,
                catch_difficulty=6,
                description="A rare golden fish.",
                item_id="fish_golden_trout",
            ),
        }

        # Create minimal spots
        self.spots = {
            "forest_pond": FishingSpot(
                spot_id="forest_pond",
                name="Forest Pond",
                map_id="forest_path",
                x=5,
                y=5,
                water_type=WaterType.FRESHWATER,
                fish_pool=["common_carp", "golden_trout"],
            ),
            "mystic_spring": FishingSpot(
                spot_id="mystic_spring",
                name="Mystic Spring",
                map_id="enchanted_grove",
                x=10,
                y=10,
                water_type=WaterType.MAGICAL,
                is_premium=True,
                fish_pool=["golden_trout"],
            ),
        }

        self.fishing_system = FishingSystem(self.fish_db, self.spots)

    def test_fishing_records_and_stats_round_trip(self):
        """Test that recording catches updates player_records, total_catches, catches_per_spot, and get_fishing_stats()."""
        # Record first catch at forest_pond
        caught1 = CaughtFish(fish=self.fish_db["common_carp"], size=1.0)
        is_record1 = self.fishing_system.record_catch(caught1, spot_id="forest_pond")

        self.assertTrue(is_record1, "First catch should be a record")
        self.assertEqual(self.fishing_system.total_catches, 1)
        self.assertEqual(self.fishing_system.catches_per_spot.get("forest_pond"), 1)
        self.assertIn("common_carp", self.fishing_system.player_records)
        self.assertEqual(self.fishing_system.player_records["common_carp"].size, 1.0)

        # Record a larger catch of same fish (new record)
        caught2 = CaughtFish(fish=self.fish_db["common_carp"], size=1.8)
        is_record2 = self.fishing_system.record_catch(caught2, spot_id="forest_pond")

        self.assertTrue(is_record2, "Larger catch should be a new record")
        self.assertEqual(self.fishing_system.total_catches, 2)
        self.assertEqual(self.fishing_system.catches_per_spot.get("forest_pond"), 2)
        self.assertEqual(self.fishing_system.player_records["common_carp"].size, 1.8)

        # Record smaller catch (not a record)
        caught3 = CaughtFish(fish=self.fish_db["common_carp"], size=0.8)
        is_record3 = self.fishing_system.record_catch(caught3, spot_id="forest_pond")

        self.assertFalse(is_record3, "Smaller catch should not be a record")
        self.assertEqual(self.fishing_system.total_catches, 3)
        self.assertEqual(self.fishing_system.player_records["common_carp"].size, 1.8)

        # Record different fish at different spot
        caught4 = CaughtFish(fish=self.fish_db["golden_trout"], size=1.2)
        is_record4 = self.fishing_system.record_catch(caught4, spot_id="mystic_spring")

        self.assertTrue(is_record4, "First catch of new fish should be a record")
        self.assertEqual(self.fishing_system.total_catches, 4)
        self.assertEqual(self.fishing_system.catches_per_spot.get("mystic_spring"), 1)
        self.assertIn("golden_trout", self.fishing_system.player_records)

        # Verify get_fishing_stats returns consistent values
        stats = self.fishing_system.get_fishing_stats()
        self.assertEqual(stats["total_caught"], 4)
        self.assertEqual(stats["records"]["common_carp"], 1.8)
        self.assertEqual(stats["records"]["golden_trout"], 1.2)
        self.assertEqual(stats["catches_per_spot"]["forest_pond"], 3)
        self.assertEqual(stats["catches_per_spot"]["mystic_spring"], 1)

    def test_fishing_serialize_deserialize_round_trip(self):
        """Test that serialize/deserialize preserves all fishing state."""
        # Record some catches
        caught1 = CaughtFish(fish=self.fish_db["common_carp"], size=1.5)
        caught2 = CaughtFish(fish=self.fish_db["golden_trout"], size=0.9)
        self.fishing_system.record_catch(caught1, spot_id="forest_pond")
        self.fishing_system.record_catch(caught2, spot_id="mystic_spring")

        # Record another catch to ensure total_catches is correct
        caught3 = CaughtFish(fish=self.fish_db["common_carp"], size=1.0)
        self.fishing_system.record_catch(caught3, spot_id="forest_pond")

        # Serialize
        data = self.fishing_system.serialize()

        # Verify serialized data structure
        self.assertIn("player_records", data)
        self.assertIn("total_catches", data)
        self.assertIn("catches_per_spot", data)
        self.assertEqual(data["total_catches"], 3)

        # Deserialize into a new system
        new_system = FishingSystem.deserialize(data, self.fish_db, self.spots)

        # Verify all state is restored
        self.assertEqual(new_system.total_catches, 3)
        self.assertEqual(len(new_system.player_records), 2)
        self.assertIn("common_carp", new_system.player_records)
        self.assertIn("golden_trout", new_system.player_records)
        self.assertEqual(new_system.player_records["common_carp"].size, 1.5)
        self.assertEqual(new_system.player_records["golden_trout"].size, 0.9)
        self.assertEqual(new_system.catches_per_spot.get("forest_pond"), 2)
        self.assertEqual(new_system.catches_per_spot.get("mystic_spring"), 1)


class TestGamblingIntegration(unittest.TestCase):
    """Integration tests for gambling system bet/win/loss flows and serialization."""

    def setUp(self):
        """Set up test fixtures with a world stub and GamblingManager."""
        # Create a simple world stub with get_flag/set_flag
        self.world = World()
        self.world.set_flag("gold", 1000)

        self.gambling_manager = GamblingManager()

    def test_gambling_bet_win_flow_updates_gold_and_stats(self):
        """Test that placing a bet and winning updates gold and all relevant stats."""
        initial_gold = self.world.get_flag("gold", 0)

        # Place a bet
        bet_amount = 100
        success = self.gambling_manager.place_bet(bet_amount, self.world)

        self.assertTrue(success, "Bet should succeed with enough gold")
        self.assertEqual(self.world.get_flag("gold", 0), initial_gold - bet_amount)
        self.assertEqual(self.gambling_manager.current_bet, bet_amount)
        self.assertEqual(self.gambling_manager.stats.total_wagered, bet_amount)

        # Win with 2x multiplier
        winnings = self.gambling_manager.win(2.0, self.world)

        self.assertEqual(winnings, 200, "Winnings should be bet * multiplier")
        self.assertEqual(self.world.get_flag("gold", 0), initial_gold - bet_amount + winnings)
        self.assertEqual(self.gambling_manager.stats.total_won, 200)
        self.assertEqual(self.gambling_manager.stats.games_played, 1)
        self.assertEqual(self.gambling_manager.stats.biggest_win, 100)  # profit
        self.assertEqual(self.gambling_manager.stats.current_streak, 1)
        self.assertEqual(self.gambling_manager.stats.best_streak, 1)
        self.assertEqual(self.gambling_manager.current_bet, 0, "Current bet should reset after win")

        # Win again to test streak
        self.gambling_manager.place_bet(50, self.world)
        self.gambling_manager.win(3.0, self.world)

        self.assertEqual(self.gambling_manager.stats.games_played, 2)
        self.assertEqual(self.gambling_manager.stats.current_streak, 2)
        self.assertEqual(self.gambling_manager.stats.best_streak, 2)
        self.assertEqual(self.gambling_manager.stats.biggest_win, 100)  # 150-50 = 100, still max

    def test_gambling_bet_loss_flow_updates_stats(self):
        """Test that placing a bet and losing updates stats without changing gold (already deducted)."""
        initial_gold = self.world.get_flag("gold", 0)

        # Place a bet
        bet_amount = 150
        self.gambling_manager.place_bet(bet_amount, self.world)

        gold_after_bet = self.world.get_flag("gold", 0)
        self.assertEqual(gold_after_bet, initial_gold - bet_amount)

        # Lose the bet
        self.gambling_manager.lose()

        # Gold should not change (already deducted)
        self.assertEqual(self.world.get_flag("gold", 0), gold_after_bet)
        self.assertEqual(self.gambling_manager.stats.total_lost, bet_amount)
        self.assertEqual(self.gambling_manager.stats.games_played, 1)
        self.assertEqual(self.gambling_manager.stats.biggest_loss, bet_amount)
        self.assertEqual(self.gambling_manager.stats.current_streak, -1)
        self.assertEqual(self.gambling_manager.stats.worst_streak, -1)
        self.assertEqual(self.gambling_manager.current_bet, 0, "Current bet should reset after loss")

        # Lose again to test negative streak
        self.gambling_manager.place_bet(75, self.world)
        self.gambling_manager.lose()

        self.assertEqual(self.gambling_manager.stats.games_played, 2)
        self.assertEqual(self.gambling_manager.stats.current_streak, -2)
        self.assertEqual(self.gambling_manager.stats.worst_streak, -2)

    def test_gambling_push_restores_bet(self):
        """Test that a push (tie) returns the bet amount to player."""
        initial_gold = self.world.get_flag("gold", 0)
        bet_amount = 200

        # Place a bet
        self.gambling_manager.place_bet(bet_amount, self.world)
        gold_after_bet = self.world.get_flag("gold", 0)
        self.assertEqual(gold_after_bet, initial_gold - bet_amount)

        # Push (tie)
        self.gambling_manager.push(self.world)

        # Gold should be restored
        self.assertEqual(self.world.get_flag("gold", 0), initial_gold)
        self.assertEqual(self.gambling_manager.stats.games_played, 1)
        self.assertEqual(self.gambling_manager.current_bet, 0)
        # total_wagered should still reflect the bet
        self.assertEqual(self.gambling_manager.stats.total_wagered, bet_amount)

    def test_gambling_serialize_deserialize_round_trip(self):
        """Test that serialize/deserialize preserves all gambling stats."""
        # Set up some gambling history
        self.gambling_manager.place_bet(100, self.world)
        self.gambling_manager.win(2.0, self.world)
        self.gambling_manager.track_game_win(GamblingGameType.BLACKJACK)

        self.gambling_manager.place_bet(50, self.world)
        self.gambling_manager.lose()

        self.gambling_manager.place_bet(75, self.world)
        self.gambling_manager.win(1.5, self.world)
        self.gambling_manager.track_game_win(GamblingGameType.DICE_ROLL)

        # Serialize
        data = self.gambling_manager.serialize()

        # Verify serialized structure
        self.assertIn("total_wagered", data)
        self.assertIn("total_won", data)
        self.assertIn("games_played", data)
        self.assertIn("blackjack_wins", data)

        # Deserialize
        new_manager = GamblingManager.deserialize(data)

        # Verify all stats match
        self.assertEqual(new_manager.stats.total_wagered, self.gambling_manager.stats.total_wagered)
        self.assertEqual(new_manager.stats.total_won, self.gambling_manager.stats.total_won)
        self.assertEqual(new_manager.stats.total_lost, self.gambling_manager.stats.total_lost)
        self.assertEqual(new_manager.stats.games_played, self.gambling_manager.stats.games_played)
        self.assertEqual(new_manager.stats.biggest_win, self.gambling_manager.stats.biggest_win)
        self.assertEqual(new_manager.stats.biggest_loss, self.gambling_manager.stats.biggest_loss)
        self.assertEqual(new_manager.stats.current_streak, self.gambling_manager.stats.current_streak)
        self.assertEqual(new_manager.stats.best_streak, self.gambling_manager.stats.best_streak)
        self.assertEqual(new_manager.stats.worst_streak, self.gambling_manager.stats.worst_streak)
        self.assertEqual(new_manager.stats.blackjack_wins, 1)
        self.assertEqual(new_manager.stats.dice_wins, 1)


class TestArenaIntegration(unittest.TestCase):
    """Integration tests for arena match generation, betting, resolution, and serialization."""

    def setUp(self):
        """Set up test fixtures with arena fighters and world stub."""
        # Preserve global RNG state so seeding in tests doesn't leak to others
        self._random_state = random.getstate()

        # Create arena fighters
        self.fighter_defs = {
            "dragon_whelp": ArenaFighter(
                fighter_id="dragon_whelp",
                name="Dragon Whelp",
                sprite_id="dragon_whelp",
                stats={"hp": 100, "attack": 15, "defense": 10, "speed": 8},
                skills=["fire_breath"],
                odds=2.0,
            ),
            "stone_golem": ArenaFighter(
                fighter_id="stone_golem",
                name="Stone Golem",
                sprite_id="stone_golem",
                stats={"hp": 150, "attack": 12, "defense": 20, "speed": 3},
                skills=["rock_smash"],
                odds=1.8,
            ),
            "shadow_wolf": ArenaFighter(
                fighter_id="shadow_wolf",
                name="Shadow Wolf",
                sprite_id="shadow_wolf",
                stats={"hp": 80, "attack": 18, "defense": 5, "speed": 15},
                skills=["shadow_bite"],
                odds=2.5,
            ),
        }

        self.arena_schedule = {
            "match_times": ["MORNING", "AFTERNOON", "EVENING"],
        }

        self.arena_manager = ArenaManager(self.fighter_defs, self.arena_schedule)

        # Create world stub with gold
        self.world = World()
        self.world.set_flag("gold", 500)

    def tearDown(self):
        """Restore RNG state to avoid test order coupling."""
        random.setstate(self._random_state)

    def test_arena_generate_matches_and_get_current_match(self):
        """Test that generate_matches creates distinct matches and get_current_match returns correct match."""
        # Seed random for determinism
        random.seed(42)

        matches = self.arena_manager.generate_matches(count=2)

        self.assertEqual(len(matches), 2, "Should generate 2 matches")

        # Check that matches have distinct fighters
        for match in matches:
            self.assertIsNotNone(match.fighter_a)
            self.assertIsNotNone(match.fighter_b)
            self.assertNotEqual(
                match.fighter_a.fighter_id,
                match.fighter_b.fighter_id,
                "Match should have distinct fighters",
            )

        # Test get_current_match for configured time slots
        # With 2 matches and 3 time slots (MORNING, AFTERNOON, EVENING), first 2 slots should have matches
        match_morning = self.arena_manager.get_current_match(TimeOfDay.MORNING)
        self.assertIsNotNone(match_morning, "Should have a match at MORNING")

        match_afternoon = self.arena_manager.get_current_match(TimeOfDay.AFTERNOON)
        self.assertIsNotNone(match_afternoon, "Should have a match at AFTERNOON (2nd match)")

        # Third slot (EVENING) should be None since we only generated 2 matches
        match_evening = self.arena_manager.get_current_match(TimeOfDay.EVENING)
        self.assertIsNone(match_evening, "Should not have a match at EVENING (only 2 matches generated)")

        # Test no match at unconfigured time
        match_midnight = self.arena_manager.get_current_match(TimeOfDay.MIDNIGHT)
        self.assertIsNone(match_midnight, "Should not have match at MIDNIGHT")

    def test_arena_betting_and_resolution_affects_gold_and_history(self):
        """Test betting on a match, simulating it, and resolving bets."""
        random.seed(123)

        # Generate a single match
        matches = self.arena_manager.generate_matches(count=1)
        self.assertEqual(len(matches), 1)
        match = matches[0]

        initial_gold = self.world.get_flag("gold", 0)

        # Place bet on fighter_a
        bet = self.arena_manager.place_bet(match, match.fighter_a.fighter_id, 100, self.world)

        self.assertIsNotNone(bet, "Bet should be placed successfully")
        self.assertEqual(self.world.get_flag("gold", 0), initial_gold - 100)
        self.assertEqual(len(self.arena_manager.active_bets), 1)

        # Simulate match (deterministic with seed)
        winner_id, battle_log = self.arena_manager.simulate_match(match)

        self.assertIn(
            winner_id,
            [match.fighter_a.fighter_id, match.fighter_b.fighter_id],
            "Winner should be one of the fighters",
        )
        self.assertGreater(len(battle_log), 0, "Battle log should have entries")

        # Resolve bets
        gold_before_resolve = self.world.get_flag("gold", 0)
        results = self.arena_manager.resolve_bets(match, winner_id, self.world)

        self.assertEqual(len(results), 1, "Should have one bet result")
        self.assertEqual(len(self.arena_manager.active_bets), 0, "Active bets should be cleared for resolved match")

        # Check gold change based on win/loss
        bet_result, winnings = results[0]
        if bet_result.fighter_id == winner_id:
            self.assertGreater(winnings, 0, "Should have winnings if bet on winner")
            self.assertEqual(
                self.world.get_flag("gold", 0),
                gold_before_resolve + winnings,
            )
        else:
            self.assertEqual(winnings, 0, "Should have no winnings if bet on loser")

        # Check match history
        self.assertEqual(len(self.arena_manager.match_history), 1)
        history_entry = self.arena_manager.match_history[0]
        self.assertEqual(history_entry["winner"], winner_id)
        self.assertIn("bets", history_entry)

    def test_arena_serialize_deserialize_round_trip(self):
        """Test that serialize/deserialize preserves arena state."""
        random.seed(456)

        # Generate matches and simulate one
        self.arena_manager.generate_matches(count=2)
        match = self.arena_manager.current_matches[0]

        # Place a bet
        self.arena_manager.place_bet(match, match.fighter_a.fighter_id, 50, self.world)

        # Simulate and resolve
        winner_id, _ = self.arena_manager.simulate_match(match)
        self.arena_manager.resolve_bets(match, winner_id, self.world)

        # Place another bet on second match (stays active)
        if len(self.arena_manager.current_matches) > 1:
            match2 = self.arena_manager.current_matches[1]
            self.arena_manager.place_bet(match2, match2.fighter_b.fighter_id, 25, self.world)

        # Serialize
        data = self.arena_manager.serialize()

        # Verify structure
        self.assertIn("fighters", data)
        self.assertIn("current_matches", data)
        self.assertIn("active_bets", data)
        self.assertIn("match_history", data)

        # Deserialize
        new_manager = ArenaManager.deserialize(data, self.fighter_defs)

        # Verify fighter records (wins/losses/odds)
        for fighter_id, fighter in self.fighter_defs.items():
            original = self.arena_manager.fighters[fighter_id]
            restored = new_manager.fighters[fighter_id]
            self.assertEqual(restored.wins, original.wins)
            self.assertEqual(restored.losses, original.losses)

        # Verify current matches restored
        self.assertEqual(
            len(new_manager.current_matches),
            len(self.arena_manager.current_matches),
        )

        # Verify active bets
        self.assertEqual(
            len(new_manager.active_bets),
            len(self.arena_manager.active_bets),
        )

        # Verify match history
        self.assertEqual(
            len(new_manager.match_history),
            len(self.arena_manager.match_history),
        )


class TestNPCScheduleIntegration(unittest.TestCase):
    """Integration tests for NPC schedule management and serialization."""

    def setUp(self):
        """Set up test fixtures with NPC schedules and world stub."""
        # Create NPC schedules
        self.schedules = {
            "merchant_bob": NPCSchedule(
                npc_id="merchant_bob",
                default_map_id="town_square",
                default_x=5,
                default_y=5,
                entries=[
                    ScheduleEntry(
                        time_periods=[TimeOfDay.MORNING, TimeOfDay.NOON, TimeOfDay.AFTERNOON],
                        map_id="market",
                        x=10,
                        y=8,
                        activity="selling",
                        shop_available=True,
                    ),
                    ScheduleEntry(
                        time_periods=[TimeOfDay.EVENING, TimeOfDay.NIGHT],
                        map_id="tavern",
                        x=3,
                        y=4,
                        activity="relaxing",
                        shop_available=False,
                        alternative_dialogue_id="merchant_closed",
                    ),
                    ScheduleEntry(
                        time_periods=[TimeOfDay.MIDNIGHT, TimeOfDay.DAWN],
                        map_id="home",
                        x=2,
                        y=2,
                        activity="sleeping",
                        shop_available=False,
                    ),
                ],
            ),
            "guard_alice": NPCSchedule(
                npc_id="guard_alice",
                default_map_id="barracks",
                default_x=3,
                default_y=3,
                entries=[
                    ScheduleEntry(
                        time_periods=[TimeOfDay.MORNING, TimeOfDay.AFTERNOON],
                        map_id="town_gate",
                        x=0,
                        y=5,
                        activity="patrolling",
                    ),
                    ScheduleEntry(
                        time_periods=[TimeOfDay.NIGHT, TimeOfDay.MIDNIGHT],
                        map_id="watchtower",
                        x=8,
                        y=8,
                        activity="watching",
                    ),
                ],
            ),
        }

        self.schedule_manager = ScheduleManager(self.schedules)

        # Create a lightweight world stub
        self._setup_world_stub()

    def _setup_world_stub(self):
        """Create a minimal world with maps and NPCs for testing."""
        self.world = World()

        # Create simple maps
        map_ids = ["town_square", "market", "tavern", "home", "barracks", "town_gate", "watchtower"]
        for map_id in map_ids:
            tiles = [[Tile("grass", True, "grass") for _ in range(20)] for _ in range(20)]
            self.world.add_map(Map(map_id=map_id, width=20, height=20, tiles=tiles))

        # Create mock NPCs and add to maps
        self.npcs = {}
        for npc_id in ["merchant_bob", "guard_alice"]:
            npc = Mock()
            npc.entity_id = npc_id
            npc.x = 0
            npc.y = 0
            self.npcs[npc_id] = npc

        # Add NPCs to their default maps
        self.world.maps["town_square"].entities.append(self.npcs["merchant_bob"])
        self.world.maps["barracks"].entities.append(self.npcs["guard_alice"])

        # Mock world methods for NPC movement
        def get_entity_by_id(entity_id):
            for map_id, game_map in self.world.maps.items():
                for entity in game_map.entities:
                    if getattr(entity, "entity_id", None) == entity_id:
                        return (map_id, entity)
            return None

        def move_entity_to_map(entity_id, from_map_id, to_map_id, x, y):
            result = get_entity_by_id(entity_id)
            if not result:
                return False
            current_map_id, entity = result
            # Remove from current map
            self.world.maps[current_map_id].entities.remove(entity)
            # Add to new map
            entity.x = x
            entity.y = y
            self.world.maps[to_map_id].entities.append(entity)
            return True

        self.world.get_entity_by_id = get_entity_by_id
        self.world.move_entity_to_map = move_entity_to_map
        self.world.npc_interaction_active = False

    def test_npc_locations_and_map_membership_by_time(self):
        """Test get_npc_location, get_npcs_on_map, get_npc_activity, and is_shop_available."""
        # Test merchant location at MORNING
        loc = self.schedule_manager.get_npc_location("merchant_bob", TimeOfDay.MORNING)
        self.assertEqual(loc, ("market", 10, 8))

        activity = self.schedule_manager.get_npc_activity("merchant_bob", TimeOfDay.MORNING)
        self.assertEqual(activity, "selling")

        shop_available = self.schedule_manager.is_shop_available("merchant_bob", TimeOfDay.MORNING)
        self.assertTrue(shop_available)

        # Test merchant at NIGHT (shop closed)
        loc_night = self.schedule_manager.get_npc_location("merchant_bob", TimeOfDay.NIGHT)
        self.assertEqual(loc_night, ("tavern", 3, 4))

        shop_night = self.schedule_manager.is_shop_available("merchant_bob", TimeOfDay.NIGHT)
        self.assertFalse(shop_night)

        # Test NPCs on market map at NOON
        npcs_on_market = self.schedule_manager.get_npcs_on_map("market", TimeOfDay.NOON)
        self.assertIn("merchant_bob", npcs_on_market)
        self.assertNotIn("guard_alice", npcs_on_market)

        # Test guard at MORNING (should be at town_gate)
        guard_loc = self.schedule_manager.get_npc_location("guard_alice", TimeOfDay.MORNING)
        self.assertEqual(guard_loc, ("town_gate", 0, 5))

        # Test default fallback when no schedule matches
        # guard_alice has no DAWN schedule, should use default
        guard_dawn = self.schedule_manager.get_npc_location("guard_alice", TimeOfDay.DAWN)
        self.assertEqual(guard_dawn, ("barracks", 3, 3))

        # Test get_npcs_on_map with default fallback
        npcs_barracks_dawn = self.schedule_manager.get_npcs_on_map("barracks", TimeOfDay.DAWN)
        self.assertIn("guard_alice", npcs_barracks_dawn)

    def test_schedule_update_moves_npcs_between_maps(self):
        """Test that update() moves NPCs between maps correctly."""
        # Initial state: merchant at town_square, guard at barracks
        self.assertEqual(
            self.world.get_entity_by_id("merchant_bob")[0],
            "town_square",
        )

        # Update for MORNING time
        moved_npcs = self.schedule_manager.update(self.world, TimeOfDay.MORNING)

        # Merchant should have moved to market
        self.assertIn("merchant_bob", moved_npcs)
        merchant_loc = self.world.get_entity_by_id("merchant_bob")
        self.assertEqual(merchant_loc[0], "market")
        self.assertEqual(merchant_loc[1].x, 10)
        self.assertEqual(merchant_loc[1].y, 8)

        # Guard should have moved to town_gate
        self.assertIn("guard_alice", moved_npcs)
        guard_loc = self.world.get_entity_by_id("guard_alice")
        self.assertEqual(guard_loc[0], "town_gate")

        # Update again with same time (should not move)
        moved_npcs_same = self.schedule_manager.update(self.world, TimeOfDay.MORNING)
        self.assertEqual(moved_npcs_same, [], "No NPCs should move when time hasn't changed")

        # Update for NIGHT time
        moved_npcs_night = self.schedule_manager.update(self.world, TimeOfDay.NIGHT)
        self.assertIn("merchant_bob", moved_npcs_night)
        merchant_night = self.world.get_entity_by_id("merchant_bob")
        self.assertEqual(merchant_night[0], "tavern")

    def test_npc_schedule_serialize_deserialize_round_trip(self):
        """Test that serialize/deserialize_into restores schedule manager state."""
        # Update to set _last_time_period and _npc_positions
        self.schedule_manager.update(self.world, TimeOfDay.AFTERNOON)

        # Pre-populate some state
        self.schedule_manager._npc_positions["merchant_bob"] = ("market", 10, 8)
        self.schedule_manager._npc_positions["guard_alice"] = ("town_gate", 0, 5)

        # Serialize
        data = self.schedule_manager.serialize()

        # Verify structure
        self.assertIn("last_time_period", data)
        self.assertIn("npc_positions", data)
        self.assertEqual(data["last_time_period"], "afternoon")

        # Create new manager and deserialize
        new_manager = ScheduleManager(self.schedules)
        new_manager.deserialize_into(data)

        # Verify restored state
        self.assertEqual(new_manager._last_time_period, TimeOfDay.AFTERNOON)
        self.assertIn("merchant_bob", new_manager._npc_positions)
        self.assertEqual(new_manager._npc_positions["merchant_bob"], ("market", 10, 8))

        # Check flags are set for position restore
        self.assertTrue(new_manager._pending_position_restore)


class TestTutorialSystemIntegration(unittest.TestCase):
    """Integration tests for tutorial tips, prerequisites, help entries, and serialization."""

    def setUp(self):
        """Set up test fixtures with TutorialManager and various tips/help entries."""
        self.tutorial_manager = TutorialManager()

        # Register tips with dependencies
        self.base_battle_tip = TutorialTip(
            tip_id="battle_basics",
            trigger=TipTrigger.FIRST_BATTLE,
            title="Battle Basics",
            content="Press A to attack!",
            priority=5,
            category="combat",
        )

        self.advanced_battle_tip = TutorialTip(
            tip_id="battle_advanced",
            trigger=TipTrigger.FIRST_BATTLE,
            title="Advanced Combat",
            content="Use skills for more damage!",
            priority=7,
            category="combat",
            requires_tips=["battle_basics"],
        )

        self.shop_tip = TutorialTip(
            tip_id="shop_basics",
            trigger=TipTrigger.FIRST_SHOP_VISIT,
            title="Shopping",
            content="Buy items with gold!",
            priority=5,
            category="exploration",
        )

        self.fishing_tip = TutorialTip(
            tip_id="fishing_basics",
            trigger=TipTrigger.FIRST_FISHING_SPOT,
            title="Fishing",
            content="Press F to fish!",
            priority=6,
            category="minigames",
        )

        self.tutorial_manager.register_tip(self.base_battle_tip)
        self.tutorial_manager.register_tip(self.advanced_battle_tip)
        self.tutorial_manager.register_tip(self.shop_tip)
        self.tutorial_manager.register_tip(self.fishing_tip)

        # Register help entries
        self.help_combat1 = HelpEntry(
            entry_id="help_combat_basics",
            title="Combat Basics",
            content="How to fight enemies.",
            category="Combat",
            order=1,
        )

        self.help_combat2 = HelpEntry(
            entry_id="help_combat_skills",
            title="Using Skills",
            content="How to use skills in battle.",
            category="Combat",
            order=2,
        )

        self.help_exploration = HelpEntry(
            entry_id="help_exploration",
            title="Exploring the World",
            content="How to explore.",
            category="Exploration",
            order=1,
        )

        self.tutorial_manager.register_help_entry(self.help_combat1)
        self.tutorial_manager.register_help_entry(self.help_combat2)
        self.tutorial_manager.register_help_entry(self.help_exploration)

    def test_trigger_tip_respects_prerequisites_and_dismissals(self):
        """Test that tips respect prerequisites and permanent dismissals."""
        # Initially, trigger FIRST_BATTLE
        tip = self.tutorial_manager.trigger_tip(TipTrigger.FIRST_BATTLE)

        # Should return base tip (advanced requires base to be seen)
        self.assertIsNotNone(tip)
        self.assertEqual(tip.tip_id, "battle_basics")

        # Advanced tip should not be showable yet
        self.assertFalse(self.tutorial_manager.can_show_tip("battle_advanced"))

        # Dismiss base tip (seen)
        self.tutorial_manager.dismiss_tip("battle_basics")

        self.assertIn("battle_basics", self.tutorial_manager.seen_tips)
        self.assertNotIn("battle_basics", self.tutorial_manager.dismissed_tips)

        # Now advanced tip should be showable
        self.assertTrue(self.tutorial_manager.can_show_tip("battle_advanced"))

        # Trigger again - should return advanced tip
        tip2 = self.tutorial_manager.trigger_tip(TipTrigger.FIRST_BATTLE)
        self.assertIsNotNone(tip2)
        self.assertEqual(tip2.tip_id, "battle_advanced")

        # Permanently dismiss advanced tip
        self.tutorial_manager.dismiss_tip("battle_advanced", permanently=True)

        self.assertIn("battle_advanced", self.tutorial_manager.dismissed_tips)
        self.assertFalse(self.tutorial_manager.can_show_tip("battle_advanced"))

    def test_pending_tip_queue_orders_by_priority(self):
        """Test that pending tips are ordered by priority."""
        # Clear pending tips
        self.tutorial_manager.pending_tips = []

        # Trigger multiple events that enqueue tips
        self.tutorial_manager.trigger_tip(TipTrigger.FIRST_SHOP_VISIT)  # priority 5
        self.tutorial_manager.trigger_tip(TipTrigger.FIRST_FISHING_SPOT)  # priority 6
        self.tutorial_manager.trigger_tip(TipTrigger.FIRST_BATTLE)  # priority 5 (base)

        # Check pending queue order (highest priority first)
        self.assertGreater(len(self.tutorial_manager.pending_tips), 0)

        # Get tips in order
        tip1 = self.tutorial_manager.get_pending_tip()
        self.assertEqual(tip1.tip_id, "fishing_basics")  # priority 6

        tip2 = self.tutorial_manager.get_pending_tip()
        # Next should be priority 5 tips (order may vary)
        self.assertIn(tip2.tip_id, ["battle_basics", "shop_basics"])

    def test_help_entries_grouping_and_ordering(self):
        """Test that help entries are grouped by category and sorted by order."""
        grouped = self.tutorial_manager.get_help_entries_by_category()

        # Check categories exist
        self.assertIn("Combat", grouped)
        self.assertIn("Exploration", grouped)

        # Check Combat category order
        combat_entries = grouped["Combat"]
        self.assertEqual(len(combat_entries), 2)
        self.assertEqual(combat_entries[0].entry_id, "help_combat_basics")  # order 1
        self.assertEqual(combat_entries[1].entry_id, "help_combat_skills")  # order 2

        # Check Exploration category
        exploration_entries = grouped["Exploration"]
        self.assertEqual(len(exploration_entries), 1)
        self.assertEqual(exploration_entries[0].entry_id, "help_exploration")

    def test_tutorial_serialize_deserialize_round_trip(self):
        """Test that serialize/deserialize preserves tutorial state."""
        # Set up some state
        self.tutorial_manager.tips_enabled = False
        self.tutorial_manager.seen_tips = {"battle_basics", "shop_basics"}
        self.tutorial_manager.dismissed_tips = {"battle_basics"}

        # Serialize
        data = self.tutorial_manager.serialize()

        # Verify structure
        self.assertIn("tips_enabled", data)
        self.assertIn("seen_tips", data)
        self.assertIn("dismissed_tips", data)
        self.assertFalse(data["tips_enabled"])
        self.assertIn("battle_basics", data["seen_tips"])
        self.assertIn("battle_basics", data["dismissed_tips"])

        # Deserialize
        new_manager = TutorialManager.deserialize(
            data,
            tips={t.tip_id: t for t in [self.base_battle_tip, self.advanced_battle_tip, self.shop_tip, self.fishing_tip]},
            help_entries={e.entry_id: e for e in [self.help_combat1, self.help_combat2, self.help_exploration]},
        )

        # Verify all state fields match
        self.assertFalse(new_manager.tips_enabled)
        self.assertEqual(new_manager.seen_tips, {"battle_basics", "shop_basics"})
        self.assertEqual(new_manager.dismissed_tips, {"battle_basics"})

        # Verify tips and help entries are available
        self.assertIn("battle_basics", new_manager.tips)
        self.assertIn("help_combat_basics", new_manager.help_entries)


if __name__ == "__main__":
    unittest.main()
