"""Unit tests for core/skill_tree.py - SkillTree, SkillNode, SkillTreeProgress."""

import json
import os
import tempfile
import unittest

from core.skill_tree import (
    SkillNode,
    SkillTree,
    SkillTreeProgress,
    SkillTreeManager,
    load_skill_node_from_dict,
    load_skill_tree_from_dict,
    load_skill_trees_from_json,
    SKILL_POINTS_PER_LEVEL,
)


class TestSkillNode(unittest.TestCase):
    def test_node_basic(self):
        node = SkillNode(
            id="fireball",
            name="Fireball",
            description="Launches a fireball",
            skill_id="skill_fireball",
            cost=2,
            tier=1,
        )
        self.assertEqual(node.id, "fireball")
        self.assertEqual(node.name, "Fireball")
        self.assertEqual(node.skill_id, "skill_fireball")
        self.assertEqual(node.cost, 2)

    def test_node_defaults(self):
        node = SkillNode(id="test", name="Test", description="")
        self.assertIsNone(node.skill_id)
        self.assertEqual(node.cost, 1)
        self.assertEqual(node.tier, 1)
        self.assertEqual(node.prerequisites, [])
        self.assertEqual(node.stat_bonuses, {})

    def test_can_unlock_no_prerequisites(self):
        node = SkillNode(id="test", name="Test", description="")
        self.assertTrue(node.can_unlock(set()))

    def test_can_unlock_with_prerequisites_met(self):
        node = SkillNode(
            id="advanced_fire",
            name="Advanced Fire",
            description="",
            prerequisites=["fireball", "fire_mastery"],
        )
        unlocked = {"fireball", "fire_mastery", "other_skill"}
        self.assertTrue(node.can_unlock(unlocked))

    def test_can_unlock_prerequisites_not_met(self):
        node = SkillNode(
            id="advanced_fire",
            name="Advanced Fire",
            description="",
            prerequisites=["fireball", "fire_mastery"],
        )
        unlocked = {"fireball"}  # Missing fire_mastery
        self.assertFalse(node.can_unlock(unlocked))


class TestSkillTree(unittest.TestCase):
    def create_test_tree(self):
        nodes = {
            "root1": SkillNode(id="root1", name="Root 1", description="", tier=1),
            "root2": SkillNode(id="root2", name="Root 2", description="", tier=1),
            "child1": SkillNode(
                id="child1", name="Child 1", description="", tier=2, prerequisites=["root1"]
            ),
            "child2": SkillNode(
                id="child2", name="Child 2", description="", tier=2, prerequisites=["root1", "root2"]
            ),
        }
        return SkillTree(
            id="fire_tree",
            name="Fire Magic",
            description="Fire spells and abilities",
            nodes=nodes,
        )

    def test_tree_basic(self):
        tree = self.create_test_tree()
        self.assertEqual(tree.id, "fire_tree")
        self.assertEqual(tree.name, "Fire Magic")
        self.assertEqual(len(tree.nodes), 4)

    def test_tree_identifies_root_nodes(self):
        tree = self.create_test_tree()
        self.assertIn("root1", tree.root_nodes)
        self.assertIn("root2", tree.root_nodes)
        self.assertNotIn("child1", tree.root_nodes)

    def test_get_node(self):
        tree = self.create_test_tree()
        node = tree.get_node("root1")
        self.assertIsNotNone(node)
        self.assertEqual(node.id, "root1")

    def test_get_node_not_found(self):
        tree = self.create_test_tree()
        self.assertIsNone(tree.get_node("nonexistent"))

    def test_get_available_nodes_empty_progress(self):
        tree = self.create_test_tree()
        available = tree.get_available_nodes(set())
        # Should only include root nodes
        available_ids = [n.id for n in available]
        self.assertIn("root1", available_ids)
        self.assertIn("root2", available_ids)
        self.assertNotIn("child1", available_ids)

    def test_get_available_nodes_with_progress(self):
        tree = self.create_test_tree()
        unlocked = {"root1"}
        available = tree.get_available_nodes(unlocked)
        available_ids = [n.id for n in available]
        # root1 is unlocked, root2 and child1 should be available
        self.assertIn("root2", available_ids)
        self.assertIn("child1", available_ids)
        self.assertNotIn("child2", available_ids)  # Needs both roots

    def test_get_nodes_by_tier(self):
        tree = self.create_test_tree()
        tiers = tree.get_nodes_by_tier()
        self.assertEqual(len(tiers[1]), 2)  # root1, root2
        self.assertEqual(len(tiers[2]), 2)  # child1, child2


class TestSkillTreeProgress(unittest.TestCase):
    def setUp(self):
        self.progress = SkillTreeProgress()
        nodes = {
            "root": SkillNode(id="root", name="Root", description="", cost=1, stat_bonuses={"attack": 5}),
            "child": SkillNode(
                id="child", name="Child", description="", cost=2, prerequisites=["root"], skill_id="skill1"
            ),
        }
        self.tree = SkillTree(id="test_tree", name="Test", description="", nodes=nodes)

    def test_progress_defaults(self):
        self.assertEqual(self.progress.skill_points, 0)
        self.assertEqual(self.progress.skill_points_total, 0)
        self.assertEqual(self.progress.unlocked_nodes, {})

    def test_add_skill_points(self):
        result = self.progress.add_skill_points(5)
        self.assertEqual(result, 5)
        self.assertEqual(self.progress.skill_points, 5)
        self.assertEqual(self.progress.skill_points_total, 5)

    def test_add_skill_points_cumulative(self):
        self.progress.add_skill_points(3)
        self.progress.add_skill_points(2)
        self.assertEqual(self.progress.skill_points, 5)
        self.assertEqual(self.progress.skill_points_total, 5)

    def test_get_unlocked_for_tree_empty(self):
        unlocked = self.progress.get_unlocked_for_tree("test_tree")
        self.assertEqual(unlocked, set())

    def test_can_unlock_node_success(self):
        self.progress.skill_points = 1
        can_unlock, reason = self.progress.can_unlock_node(self.tree, "root")
        self.assertTrue(can_unlock)
        self.assertEqual(reason, "Can unlock")

    def test_can_unlock_node_not_found(self):
        can_unlock, reason = self.progress.can_unlock_node(self.tree, "nonexistent")
        self.assertFalse(can_unlock)
        self.assertIn("not found", reason.lower())

    def test_can_unlock_node_already_unlocked(self):
        self.progress.skill_points = 5
        self.progress.unlocked_nodes["test_tree"] = {"root"}
        can_unlock, reason = self.progress.can_unlock_node(self.tree, "root")
        self.assertFalse(can_unlock)
        self.assertIn("Already", reason)

    def test_can_unlock_node_missing_prerequisites(self):
        self.progress.skill_points = 5
        can_unlock, reason = self.progress.can_unlock_node(self.tree, "child")
        self.assertFalse(can_unlock)
        self.assertIn("prerequisites", reason.lower())

    def test_can_unlock_node_insufficient_points(self):
        self.progress.skill_points = 0
        can_unlock, reason = self.progress.can_unlock_node(self.tree, "root")
        self.assertFalse(can_unlock)
        self.assertIn("skill points", reason.lower())

    def test_unlock_node_success(self):
        self.progress.skill_points = 3
        success, message, node = self.progress.unlock_node(self.tree, "root")
        self.assertTrue(success)
        self.assertIn("Unlocked", message)
        self.assertEqual(node.id, "root")
        self.assertEqual(self.progress.skill_points, 2)  # 3 - 1 cost
        self.assertIn("root", self.progress.get_unlocked_for_tree("test_tree"))

    def test_unlock_node_failure(self):
        self.progress.skill_points = 0
        success, message, node = self.progress.unlock_node(self.tree, "root")
        self.assertFalse(success)
        self.assertIsNone(node)

    def test_unlock_node_chain(self):
        self.progress.skill_points = 5
        # Unlock root first
        self.progress.unlock_node(self.tree, "root")
        # Now child should be unlockable
        success, _, node = self.progress.unlock_node(self.tree, "child")
        self.assertTrue(success)
        self.assertEqual(self.progress.skill_points, 2)  # 5 - 1 - 2

    def test_get_total_stat_bonuses(self):
        self.progress.skill_points = 5
        self.progress.unlock_node(self.tree, "root")
        bonuses = self.progress.get_total_stat_bonuses({"test_tree": self.tree})
        self.assertEqual(bonuses.get("attack"), 5)

    def test_get_total_stat_bonuses_multiple_nodes(self):
        # Add another node with bonuses
        self.tree.nodes["bonus_node"] = SkillNode(
            id="bonus_node",
            name="Bonus",
            description="",
            stat_bonuses={"attack": 3, "defense": 2},
        )
        self.progress.skill_points = 10
        self.progress.unlock_node(self.tree, "root")
        self.progress.unlock_node(self.tree, "bonus_node")
        bonuses = self.progress.get_total_stat_bonuses({"test_tree": self.tree})
        self.assertEqual(bonuses.get("attack"), 8)  # 5 + 3
        self.assertEqual(bonuses.get("defense"), 2)

    def test_get_all_unlocked_skills(self):
        self.progress.skill_points = 10
        self.progress.unlock_node(self.tree, "root")
        self.progress.unlock_node(self.tree, "child")
        skills = self.progress.get_all_unlocked_skills({"test_tree": self.tree})
        self.assertIn("skill1", skills)

    def test_serialize(self):
        self.progress.skill_points = 5
        self.progress.skill_points_total = 10
        self.progress.unlocked_nodes["test_tree"] = {"root", "child"}

        data = self.progress.serialize()

        self.assertEqual(data["skill_points"], 5)
        self.assertEqual(data["skill_points_total"], 10)
        self.assertIn("root", data["unlocked_nodes"]["test_tree"])

    def test_deserialize(self):
        data = {
            "skill_points": 7,
            "skill_points_total": 15,
            "unlocked_nodes": {"tree1": ["node1", "node2"]},
        }
        progress = SkillTreeProgress.deserialize(data)
        self.assertEqual(progress.skill_points, 7)
        self.assertEqual(progress.skill_points_total, 15)
        self.assertIn("node1", progress.unlocked_nodes["tree1"])


class TestSkillTreeManager(unittest.TestCase):
    def setUp(self):
        nodes = {
            "root": SkillNode(id="root", name="Root", description=""),
        }
        self.tree = SkillTree(id="test_tree", name="Test Tree", description="", nodes=nodes)
        self.manager = SkillTreeManager(trees={"test_tree": self.tree})

    def test_get_tree(self):
        tree = self.manager.get_tree("test_tree")
        self.assertIsNotNone(tree)
        self.assertEqual(tree.id, "test_tree")

    def test_get_tree_not_found(self):
        self.assertIsNone(self.manager.get_tree("nonexistent"))

    def test_get_available_trees(self):
        trees = self.manager.get_available_trees()
        self.assertEqual(len(trees), 1)

    def test_apply_skill_tree_bonuses(self):
        # Create a mock stats object
        class MockStats:
            pass

        stats = MockStats()
        progress = SkillTreeProgress()
        progress.unlocked_nodes["test_tree"] = set()

        self.manager.apply_skill_tree_bonuses(stats, progress)
        self.assertTrue(hasattr(stats, "skill_tree_modifiers"))


class TestLoadFunctions(unittest.TestCase):
    def test_load_skill_node_from_dict(self):
        data = {
            "id": "test_node",
            "name": "Test Node",
            "description": "A test",
            "skill_id": "skill_test",
            "cost": 3,
            "tier": 2,
            "prerequisites": ["prereq1"],
            "stat_bonuses": {"attack": 5},
            "icon_id": "icon_test",
        }
        node = load_skill_node_from_dict(data)
        self.assertEqual(node.id, "test_node")
        self.assertEqual(node.skill_id, "skill_test")
        self.assertEqual(node.cost, 3)
        self.assertEqual(node.stat_bonuses["attack"], 5)

    def test_load_skill_tree_from_dict(self):
        data = {
            "id": "fire_tree",
            "name": "Fire Magic",
            "description": "Fire spells",
            "nodes": [
                {"id": "fireball", "name": "Fireball", "description": ""},
                {"id": "flame_wave", "name": "Flame Wave", "description": "", "prerequisites": ["fireball"]},
            ],
        }
        tree = load_skill_tree_from_dict(data)
        self.assertEqual(tree.id, "fire_tree")
        self.assertEqual(len(tree.nodes), 2)
        self.assertIn("fireball", tree.nodes)

    def test_load_skill_trees_from_json(self):
        data = {
            "skill_trees": [
                {
                    "id": "warrior_tree",
                    "name": "Warrior",
                    "description": "Warrior skills",
                    "nodes": [
                        {"id": "slash", "name": "Slash", "description": ""},
                    ],
                }
            ]
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            temp_path = f.name

        try:
            trees = load_skill_trees_from_json(temp_path)
            self.assertIn("warrior_tree", trees)
            self.assertEqual(trees["warrior_tree"].name, "Warrior")
        finally:
            os.unlink(temp_path)

    def test_load_skill_trees_nonexistent_file(self):
        trees = load_skill_trees_from_json("/nonexistent/path.json")
        self.assertEqual(len(trees), 0)


class TestConstants(unittest.TestCase):
    def test_skill_points_per_level(self):
        self.assertEqual(SKILL_POINTS_PER_LEVEL, 1)


if __name__ == "__main__":
    unittest.main()
