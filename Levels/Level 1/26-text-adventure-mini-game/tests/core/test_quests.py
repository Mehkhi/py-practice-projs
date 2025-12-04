"""Unit tests for core/quests.py - QuestSystem, Quest, QuestObjective."""

import json
import os
import tempfile
import unittest

from core.quests import (
    QuestStatus,
    ObjectiveType,
    QuestObjective,
    Quest,
    QuestManager,
    load_quest_manager,
)


class TestQuestObjective(unittest.TestCase):
    def test_objective_basic(self):
        obj = QuestObjective(
            id="kill_goblins",
            description="Kill 5 goblins",
            objective_type=ObjectiveType.KILL,
            target="goblin",
            required_count=5,
        )
        self.assertEqual(obj.id, "kill_goblins")
        self.assertEqual(obj.objective_type, ObjectiveType.KILL)
        self.assertEqual(obj.required_count, 5)
        self.assertEqual(obj.current_count, 0)
        self.assertFalse(obj.completed)

    def test_update_progress(self):
        obj = QuestObjective(
            id="test",
            description="Test",
            required_count=3,
        )
        completed = obj.update_progress(1)
        self.assertFalse(completed)
        self.assertEqual(obj.current_count, 1)

    def test_update_progress_completes(self):
        obj = QuestObjective(
            id="test",
            description="Test",
            required_count=3,
        )
        obj.update_progress(2)
        completed = obj.update_progress(1)
        self.assertTrue(completed)
        self.assertTrue(obj.completed)

    def test_update_progress_already_completed(self):
        obj = QuestObjective(
            id="test",
            description="Test",
            required_count=1,
        )
        obj.update_progress(1)
        result = obj.update_progress(1)
        self.assertFalse(result)  # No change since already completed

    def test_update_progress_caps_at_required(self):
        obj = QuestObjective(
            id="test",
            description="Test",
            required_count=3,
        )
        obj.update_progress(10)
        self.assertEqual(obj.current_count, 3)

    def test_set_completed(self):
        obj = QuestObjective(
            id="test",
            description="Test",
            required_count=5,
        )
        obj.set_completed()
        self.assertTrue(obj.completed)
        self.assertEqual(obj.current_count, 5)

    def test_get_progress_text_single(self):
        obj = QuestObjective(id="test", description="Test", required_count=1)
        self.assertEqual(obj.get_progress_text(), "[ ]")
        obj.set_completed()
        self.assertEqual(obj.get_progress_text(), "[X]")

    def test_get_progress_text_multiple(self):
        obj = QuestObjective(id="test", description="Test", required_count=5)
        self.assertEqual(obj.get_progress_text(), "(0/5)")
        obj.update_progress(3)
        self.assertEqual(obj.get_progress_text(), "(3/5)")

    def test_to_dict(self):
        obj = QuestObjective(id="test", description="Test", required_count=3)
        obj.update_progress(2)
        data = obj.to_dict()
        self.assertEqual(data["id"], "test")
        self.assertEqual(data["current_count"], 2)
        self.assertFalse(data["completed"])

    def test_from_definition(self):
        data = {
            "id": "kill_goblins",
            "description": "Kill 5 goblins",
            "type": "kill",
            "target": "goblin",
            "required_count": 5,
            "optional": True,
        }
        obj = QuestObjective.from_definition(data)
        self.assertEqual(obj.id, "kill_goblins")
        self.assertEqual(obj.objective_type, ObjectiveType.KILL)
        self.assertEqual(obj.target, "goblin")
        self.assertEqual(obj.required_count, 5)
        self.assertTrue(obj.optional)


class TestQuest(unittest.TestCase):
    def create_test_quest(self):
        return Quest(
            id="test_quest",
            name="Test Quest",
            description="A test quest",
            objectives=[
                QuestObjective(id="obj1", description="Objective 1", required_count=1),
                QuestObjective(id="obj2", description="Objective 2", required_count=3),
            ],
            status=QuestStatus.ACTIVE,
            reward_gold=100,
            reward_exp=50,
        )

    def test_quest_basic(self):
        quest = self.create_test_quest()
        self.assertEqual(quest.id, "test_quest")
        self.assertEqual(quest.status, QuestStatus.ACTIVE)
        self.assertEqual(len(quest.objectives), 2)
        self.assertEqual(quest.reward_gold, 100)

    def test_is_complete_false(self):
        quest = self.create_test_quest()
        self.assertFalse(quest.is_complete())

    def test_is_complete_true(self):
        quest = self.create_test_quest()
        for obj in quest.objectives:
            obj.set_completed()
        self.assertTrue(quest.is_complete())

    def test_is_complete_optional_not_required(self):
        quest = Quest(
            id="test",
            name="Test",
            description="",
            objectives=[
                QuestObjective(id="required", description="Required", required_count=1),
                QuestObjective(
                    id="optional", description="Optional", required_count=1, optional=True
                ),
            ],
        )
        quest.objectives[0].set_completed()
        # Optional not completed, but quest should still be complete
        self.assertTrue(quest.is_complete())

    def test_get_active_objectives(self):
        quest = self.create_test_quest()
        quest.objectives[0].set_completed()
        active = quest.get_active_objectives()
        self.assertEqual(len(active), 1)
        self.assertEqual(active[0].id, "obj2")

    def test_get_objective(self):
        quest = self.create_test_quest()
        obj = quest.get_objective("obj1")
        self.assertIsNotNone(obj)
        self.assertEqual(obj.id, "obj1")

    def test_get_objective_not_found(self):
        quest = self.create_test_quest()
        obj = quest.get_objective("nonexistent")
        self.assertIsNone(obj)

    def test_update_objective(self):
        quest = self.create_test_quest()
        is_complete = quest.update_objective("obj1", 1)
        self.assertTrue(quest.objectives[0].completed)
        self.assertFalse(is_complete)  # Still have obj2

    def test_update_objective_completes_quest(self):
        quest = self.create_test_quest()
        quest.objectives[0].set_completed()
        is_complete = quest.update_objective("obj2", 3)
        self.assertTrue(is_complete)

    def test_metadata_defaults(self):
        quest = self.create_test_quest()
        self.assertEqual(quest.difficulty, "Normal")
        self.assertEqual(quest.tags, [])
        self.assertIsNone(quest.recommended_level)

    def test_from_definition_parses_metadata(self):
        data = {
            "id": "meta",
            "name": "Meta Quest",
            "description": "Testing metadata",
            "objectives": [],
            "difficulty": "Hard",
            "recommended_level": 9,
            "tags": ["story", "boss"],
        }
        quest = Quest.from_definition(data)
        self.assertEqual(quest.difficulty, "Hard")
        self.assertEqual(quest.recommended_level, 9)
        self.assertIn("boss", quest.tags)

    def test_check_flag_objectives(self):
        quest = Quest(
            id="test",
            name="Test",
            description="",
            objectives=[
                QuestObjective(
                    id="flag_obj",
                    description="Check flag",
                    objective_type=ObjectiveType.FLAG,
                    target="quest_started",
                ),
            ],
            status=QuestStatus.ACTIVE,
        )
        world_flags = {"quest_started": True}
        updated = quest.check_flag_objectives(world_flags)
        self.assertTrue(updated)
        self.assertTrue(quest.objectives[0].completed)

    def test_check_flag_objectives_not_set(self):
        quest = Quest(
            id="test",
            name="Test",
            description="",
            objectives=[
                QuestObjective(
                    id="flag_obj",
                    description="Check flag",
                    objective_type=ObjectiveType.FLAG,
                    target="some_flag",
                ),
            ],
        )
        world_flags = {}
        updated = quest.check_flag_objectives(world_flags)
        self.assertFalse(updated)

    def test_check_failure_conditions_flag(self):
        quest = Quest(
            id="test",
            name="Test",
            description="",
            status=QuestStatus.ACTIVE,
            fail_on_flags=["npc_died"],
        )
        self.assertFalse(quest.check_failure_conditions({}))
        self.assertTrue(quest.check_failure_conditions({"npc_died": True}))

    def test_check_failure_conditions_time_limit(self):
        quest = Quest(
            id="test",
            name="Test",
            description="",
            status=QuestStatus.ACTIVE,
            time_limit_turns=10,
            turns_elapsed=10,
        )
        self.assertTrue(quest.check_failure_conditions({}))

    def test_increment_turn(self):
        quest = Quest(
            id="test",
            name="Test",
            description="",
            status=QuestStatus.ACTIVE,
            time_limit_turns=3,
        )
        self.assertFalse(quest.increment_turn())  # 1
        self.assertFalse(quest.increment_turn())  # 2
        self.assertTrue(quest.increment_turn())   # 3 = limit reached

    def test_increment_turn_no_limit(self):
        quest = Quest(
            id="test",
            name="Test",
            description="",
            status=QuestStatus.ACTIVE,
        )
        self.assertFalse(quest.increment_turn())

    def test_to_dict(self):
        quest = self.create_test_quest()
        quest.tracked = True
        data = quest.to_dict()
        self.assertEqual(data["id"], "test_quest")
        self.assertEqual(data["status"], "active")
        self.assertTrue(data["tracked"])
        self.assertEqual(len(data["objectives"]), 2)

    def test_from_definition(self):
        data = {
            "id": "rescue_princess",
            "name": "Rescue the Princess",
            "description": "Save her from the tower",
            "objectives": [
                {"id": "reach_tower", "description": "Reach the tower", "type": "reach", "target": "tower"},
                {"id": "defeat_dragon", "description": "Defeat the dragon", "type": "kill", "target": "dragon"},
            ],
            "reward_gold": 1000,
            "reward_exp": 500,
            "reward_items": {"legendary_sword": 1},
            "category": "main",
        }
        quest = Quest.from_definition(data)
        self.assertEqual(quest.id, "rescue_princess")
        self.assertEqual(quest.status, QuestStatus.LOCKED)
        self.assertEqual(len(quest.objectives), 2)
        self.assertEqual(quest.reward_gold, 1000)

    def test_get_rewards_for_class(self):
        quest = Quest(
            id="test",
            name="Test",
            description="",
            reward_items={"gold_coin": 100},
            class_rewards={"warrior": {"warrior_helm": 1}},
            subclass_rewards={"paladin": {"holy_shield": 1}},
        )
        rewards = quest.get_rewards_for_class("warrior", "paladin")
        self.assertEqual(rewards["gold_coin"], 100)
        self.assertEqual(rewards["warrior_helm"], 1)
        self.assertEqual(rewards["holy_shield"], 1)


class TestQuestManager(unittest.TestCase):
    def setUp(self):
        self.manager = QuestManager()
        # Manually add quests
        self.manager.quests["quest1"] = Quest(
            id="quest1",
            name="Quest 1",
            description="",
            status=QuestStatus.AVAILABLE,
            giver_npc="npc1",
        )
        self.manager.quests["quest2"] = Quest(
            id="quest2",
            name="Quest 2",
            description="",
            status=QuestStatus.ACTIVE,
            objectives=[
                QuestObjective(id="obj1", description="Kill goblin", objective_type=ObjectiveType.KILL, target="goblin"),
            ],
        )
        self.manager.quests["quest3"] = Quest(
            id="quest3",
            name="Quest 3",
            description="",
            status=QuestStatus.LOCKED,
            required_flags=["quest2_complete"],
        )
        # Rebuild indexes after manually adding quests
        self.manager._rebuild_indexes()

    def test_get_quest(self):
        quest = self.manager.get_quest("quest1")
        self.assertIsNotNone(quest)
        self.assertEqual(quest.id, "quest1")

    def test_get_quest_not_found(self):
        self.assertIsNone(self.manager.get_quest("nonexistent"))

    def test_get_quests_by_status(self):
        active = self.manager.get_quests_by_status(QuestStatus.ACTIVE)
        self.assertEqual(len(active), 1)
        self.assertEqual(active[0].id, "quest2")

    def test_get_active_quests(self):
        active = self.manager.get_active_quests()
        self.assertEqual(len(active), 1)

    def test_get_available_quests(self):
        available = self.manager.get_available_quests()
        self.assertEqual(len(available), 1)
        self.assertEqual(available[0].id, "quest1")

    def test_start_quest(self):
        result = self.manager.start_quest("quest1")
        self.assertTrue(result)
        self.assertEqual(self.manager.quests["quest1"].status, QuestStatus.ACTIVE)

    def test_start_quest_already_active(self):
        result = self.manager.start_quest("quest2")
        self.assertFalse(result)

    def test_complete_quest(self):
        quest = self.manager.quests["quest2"]
        quest.objectives[0].set_completed()
        result = self.manager.complete_quest("quest2")
        self.assertIsNotNone(result)
        self.assertEqual(quest.status, QuestStatus.COMPLETED)

    def test_complete_quest_not_finished(self):
        result = self.manager.complete_quest("quest2")
        self.assertIsNone(result)

    def test_fail_quest(self):
        result = self.manager.fail_quest("quest2")
        self.assertTrue(result)
        self.assertEqual(self.manager.quests["quest2"].status, QuestStatus.FAILED)

    def test_update_objective(self):
        is_complete = self.manager.update_objective("quest2", "obj1", 1)
        self.assertTrue(self.manager.quests["quest2"].objectives[0].completed)
        self.assertTrue(is_complete)

    def test_check_prerequisites(self):
        world_flags = {"quest2_complete": True}
        newly_available = self.manager.check_prerequisites(world_flags)
        self.assertIn("quest3", newly_available)
        self.assertEqual(self.manager.quests["quest3"].status, QuestStatus.AVAILABLE)

    def test_on_enemy_killed(self):
        updated = self.manager.on_enemy_killed("goblin")
        self.assertIn("quest2", updated)
        self.assertTrue(self.manager.quests["quest2"].objectives[0].completed)

    def test_indexes_rebuilt_after_start_quest(self):
        """Test that indexes are rebuilt when a quest becomes active."""
        # Add a quest with kill objective
        quest = Quest(
            id="kill_quest",
            name="Kill Quest",
            description="",
            status=QuestStatus.AVAILABLE,
            objectives=[
                QuestObjective(
                    id="kill_obj",
                    description="Kill wolf",
                    objective_type=ObjectiveType.KILL,
                    target="wolf"
                )
            ]
        )
        self.manager.quests["kill_quest"] = quest

        # Indexes should not have wolf before starting
        self.assertNotIn("wolf", self.manager._kill_objectives_by_target)

        # Start the quest
        self.manager.start_quest("kill_quest")

        # Indexes should now include wolf
        self.assertIn("wolf", self.manager._kill_objectives_by_target)
        self.assertEqual(len(self.manager._kill_objectives_by_target["wolf"]), 1)
        self.assertEqual(self.manager._kill_objectives_by_target["wolf"][0], ("kill_quest", "kill_obj"))

    def test_indexes_rebuilt_after_complete_quest(self):
        """Test that indexes are cleared when a quest is completed."""
        # quest2 is already active with a goblin kill objective
        self.assertIn("goblin", self.manager._kill_objectives_by_target)

        # Complete the objective and quest
        self.manager.quests["quest2"].objectives[0].set_completed()
        self.manager.complete_quest("quest2")

        # Indexes should no longer include goblin
        self.assertNotIn("goblin", self.manager._kill_objectives_by_target)

    def test_indexes_rebuilt_after_fail_quest(self):
        """Test that indexes are cleared when a quest fails."""
        # quest2 is already active with a goblin kill objective
        self.assertIn("goblin", self.manager._kill_objectives_by_target)

        # Fail the quest
        self.manager.fail_quest("quest2")

        # Indexes should no longer include goblin
        self.assertNotIn("goblin", self.manager._kill_objectives_by_target)

    def test_indexes_include_all_objective_types(self):
        """Test that indexes are built for all objective types."""
        quest = Quest(
            id="multi_quest",
            name="Multi Quest",
            description="",
            status=QuestStatus.ACTIVE,
            objectives=[
                QuestObjective(id="kill", description="Kill", objective_type=ObjectiveType.KILL, target="enemy1"),
                QuestObjective(id="talk", description="Talk", objective_type=ObjectiveType.TALK, target="npc1"),
                QuestObjective(id="collect", description="Collect", objective_type=ObjectiveType.COLLECT, target="item1"),
                QuestObjective(id="reach", description="Reach", objective_type=ObjectiveType.REACH, target="map1"),
                QuestObjective(id="flag", description="Flag", objective_type=ObjectiveType.FLAG, target="flag1"),
            ]
        )
        self.manager.quests["multi_quest"] = quest
        self.manager._rebuild_indexes()

        self.assertIn("enemy1", self.manager._kill_objectives_by_target)
        self.assertIn("npc1", self.manager._talk_objectives_by_npc)
        self.assertIn("item1", self.manager._collect_objectives_by_item)
        self.assertIn("map1", self.manager._reach_objectives_by_map)
        self.assertIn("flag1", self.manager._flag_objectives_by_flag)

    def test_indexes_exclude_completed_objectives(self):
        """Test that completed objectives are not included in indexes."""
        quest = Quest(
            id="partial_quest",
            name="Partial Quest",
            description="",
            status=QuestStatus.ACTIVE,
            objectives=[
                QuestObjective(id="kill1", description="Kill 1", objective_type=ObjectiveType.KILL, target="enemy1", completed=True),
                QuestObjective(id="kill2", description="Kill 2", objective_type=ObjectiveType.KILL, target="enemy2", completed=False),
            ]
        )
        self.manager.quests["partial_quest"] = quest
        self.manager._rebuild_indexes()

        # Completed objective should not be in index
        self.assertNotIn("enemy1", self.manager._kill_objectives_by_target)
        # Incomplete objective should be in index
        self.assertIn("enemy2", self.manager._kill_objectives_by_target)

    def test_event_hooks_use_indexes(self):
        """Test that event hooks use indexes for efficient lookups."""
        # Add multiple active quests with different objectives
        quest1 = Quest(
            id="q1",
            name="Quest 1",
            description="",
            status=QuestStatus.ACTIVE,
            objectives=[QuestObjective(id="o1", description="Kill wolf", objective_type=ObjectiveType.KILL, target="wolf")]
        )
        quest2 = Quest(
            id="q2",
            name="Quest 2",
            description="",
            status=QuestStatus.ACTIVE,
            objectives=[QuestObjective(id="o2", description="Talk to npc", objective_type=ObjectiveType.TALK, target="merchant")]
        )
        quest3 = Quest(
            id="q3",
            name="Quest 3",
            description="",
            status=QuestStatus.ACTIVE,
            objectives=[QuestObjective(id="o3", description="Collect item", objective_type=ObjectiveType.COLLECT, target="key")]
        )
        self.manager.quests["q1"] = quest1
        self.manager.quests["q2"] = quest2
        self.manager.quests["q3"] = quest3
        self.manager._rebuild_indexes()

        # Verify indexes are populated
        self.assertIn("wolf", self.manager._kill_objectives_by_target)
        self.assertIn("merchant", self.manager._talk_objectives_by_npc)
        self.assertIn("key", self.manager._collect_objectives_by_item)

        # Test that event hooks work correctly with indexes
        updated = self.manager.on_enemy_killed("wolf")
        self.assertIn("q1", updated)
        self.assertTrue(quest1.objectives[0].completed)

        updated = self.manager.on_npc_talked("merchant")
        self.assertIn("q2", updated)
        self.assertTrue(quest2.objectives[0].completed)

        updated = self.manager.on_item_collected("key")
        self.assertIn("q3", updated)
        self.assertTrue(quest3.objectives[0].completed)

    def test_check_flag_objectives_uses_indexes(self):
        """Test that check_flag_objectives uses indexes efficiently."""
        quest = Quest(
            id="flag_quest",
            name="Flag Quest",
            description="",
            status=QuestStatus.ACTIVE,
            objectives=[
                QuestObjective(id="flag_obj", description="Set flag", objective_type=ObjectiveType.FLAG, target="test_flag")
            ]
        )
        self.manager.quests["flag_quest"] = quest
        self.manager._rebuild_indexes()

        # Verify index is populated
        self.assertIn("test_flag", self.manager._flag_objectives_by_flag)

        # Check flag objectives with only the set flag
        world_flags = {"test_flag": True, "other_flag": False, "unrelated_flag": True}
        updated = self.manager.check_flag_objectives(world_flags)

        self.assertIn("flag_quest", updated)
        self.assertTrue(quest.objectives[0].completed)

    def test_on_enemy_killed_with_progress(self):
        """Test on_enemy_killed with return_progress=True returns detailed info."""
        # Set up a kill objective that requires 3 kills
        self.manager.quests["quest2"].objectives[0] = QuestObjective(
            id="kill",
            description="Kill 3 goblins",
            objective_type=ObjectiveType.KILL,
            target="goblin",
            required_count=3,
        )
        # Rebuild indexes after modifying objectives
        self.manager._rebuild_indexes()

        # First kill - partial progress
        progress = self.manager.on_enemy_killed("goblin", return_progress=True)
        self.assertEqual(len(progress), 1)
        self.assertEqual(progress[0]["quest_name"], "Quest 2")
        self.assertEqual(progress[0]["objective_desc"], "Kill 3 goblins")
        self.assertEqual(progress[0]["current"], 1)
        self.assertEqual(progress[0]["required"], 3)
        self.assertFalse(progress[0]["completed"])

        # Second kill - still partial
        progress = self.manager.on_enemy_killed("goblin", return_progress=True)
        self.assertEqual(progress[0]["current"], 2)
        self.assertFalse(progress[0]["completed"])

        # Third kill - objective completed
        progress = self.manager.on_enemy_killed("goblin", return_progress=True)
        self.assertEqual(progress[0]["current"], 3)
        self.assertTrue(progress[0]["completed"])

        # Fourth kill - no progress (already complete)
        progress = self.manager.on_enemy_killed("goblin", return_progress=True)
        self.assertEqual(len(progress), 0)

    def test_on_item_collected(self):
        self.manager.quests["quest2"].objectives[0] = QuestObjective(
            id="collect",
            description="Collect herbs",
            objective_type=ObjectiveType.COLLECT,
            target="herb",
            required_count=3,
        )
        # Rebuild indexes after modifying objectives
        self.manager._rebuild_indexes()
        updated = self.manager.on_item_collected("herb", 3)
        self.assertIn("quest2", updated)

    def test_on_npc_talked(self):
        self.manager.quests["quest2"].objectives[0] = QuestObjective(
            id="talk",
            description="Talk to elder",
            objective_type=ObjectiveType.TALK,
            target="elder_npc",
        )
        # Rebuild indexes after modifying objectives
        self.manager._rebuild_indexes()
        updated = self.manager.on_npc_talked("elder_npc")
        self.assertIn("quest2", updated)

    def test_on_map_entered(self):
        self.manager.quests["quest2"].objectives[0] = QuestObjective(
            id="reach",
            description="Reach the forest",
            objective_type=ObjectiveType.REACH,
            target="dark_forest",
        )
        # Rebuild indexes after modifying objectives
        self.manager._rebuild_indexes()
        updated = self.manager.on_map_entered("dark_forest")
        self.assertIn("quest2", updated)

    def test_set_tracked_quest(self):
        result = self.manager.set_tracked_quest("quest2")
        self.assertTrue(result)
        self.assertTrue(self.manager.quests["quest2"].tracked)

    def test_get_tracked_quest(self):
        self.manager.quests["quest2"].tracked = True
        tracked = self.manager.get_tracked_quest()
        self.assertEqual(tracked.id, "quest2")

    def test_untrack_all_quests(self):
        self.manager.quests["quest2"].tracked = True
        self.manager.untrack_all_quests()
        self.assertFalse(self.manager.quests["quest2"].tracked)

    def test_get_quests_from_npc(self):
        quests = self.manager.get_quests_from_npc("npc1")
        self.assertEqual(len(quests), 1)
        self.assertEqual(quests[0].id, "quest1")

    def test_get_turn_in_quests_for_npc(self):
        self.manager.quests["quest2"].objectives[0].set_completed()
        self.manager.quests["quest2"].giver_npc = "npc1"
        quests = self.manager.get_turn_in_quests_for_npc("npc1")
        self.assertEqual(len(quests), 1)

    def test_serialize_deserialize(self):
        self.manager.quests["quest2"].tracked = True
        self.manager.quests["quest2"].objectives[0].update_progress(1)

        data = self.manager.serialize_state()

        # Create fresh manager and restore
        new_manager = QuestManager()
        new_manager.quests = {
            "quest2": Quest(
                id="quest2",
                name="Quest 2",
                description="",
                objectives=[QuestObjective(id="obj1", description="Test")],
            )
        }
        new_manager.deserialize_state(data)

        quest = new_manager.quests["quest2"]
        self.assertEqual(quest.status, QuestStatus.ACTIVE)
        self.assertTrue(quest.tracked)

    def test_increment_quest_turns(self):
        self.manager.quests["quest2"].time_limit_turns = 1
        failed = self.manager.increment_quest_turns()
        self.assertIn("quest2", failed)
        self.assertEqual(self.manager.quests["quest2"].status, QuestStatus.FAILED)

    def test_on_npc_death(self):
        self.manager.quests["quest2"].fail_on_npc_death = "important_npc"
        failed = self.manager.on_npc_death("important_npc")
        self.assertIn("quest2", failed)


class TestLoadQuestManager(unittest.TestCase):
    def test_load_from_json(self):
        data = {
            "quests": [
                {
                    "id": "test_quest",
                    "name": "Test Quest",
                    "description": "A test",
                    "objectives": [
                        {"id": "obj1", "description": "Do something"},
                    ],
                    "reward_gold": 50,
                }
            ]
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            temp_path = f.name

        try:
            manager = load_quest_manager(temp_path)
            self.assertIn("test_quest", manager.quests)
            self.assertEqual(manager.quests["test_quest"].reward_gold, 50)
        finally:
            os.unlink(temp_path)

    def test_load_nonexistent_file(self):
        manager = load_quest_manager("/nonexistent/path.json")
        self.assertEqual(len(manager.quests), 0)

    def test_default_data_includes_metadata(self):
        manager = load_quest_manager()
        quest = manager.get_quest("tutorial_quest")
        self.assertIsNotNone(quest)
        self.assertEqual(quest.difficulty, "Easy")
        self.assertEqual(quest.recommended_level, 1)
        self.assertIn("tutorial", quest.tags)


if __name__ == "__main__":
    unittest.main()
