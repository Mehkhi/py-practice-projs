"""Unit tests for core/dialogue.py - Dialogue tree parsing."""

import json
import os
import tempfile
import unittest

from core.dialogue import (
    DialogueChoice,
    DialogueNode,
    DialogueTree,
    load_dialogue_from_json,
)


class TestDialogueChoice(unittest.TestCase):
    def test_choice_basic(self):
        choice = DialogueChoice(text="Yes")
        self.assertEqual(choice.text, "Yes")
        self.assertIsNone(choice.next_id)
        self.assertIsNone(choice.set_flag)

    def test_choice_with_next_id(self):
        choice = DialogueChoice(text="Continue", next_id="node_2")
        self.assertEqual(choice.next_id, "node_2")

    def test_choice_with_flag(self):
        choice = DialogueChoice(text="Accept quest", set_flag="quest_accepted")
        self.assertEqual(choice.set_flag, "quest_accepted")

    def test_choice_full(self):
        choice = DialogueChoice(
            text="I'll help you",
            next_id="quest_start",
            set_flag="agreed_to_help",
        )
        self.assertEqual(choice.text, "I'll help you")
        self.assertEqual(choice.next_id, "quest_start")
        self.assertEqual(choice.set_flag, "agreed_to_help")


class TestDialogueNode(unittest.TestCase):
    def test_node_basic(self):
        node = DialogueNode(id="intro", text="Hello, traveler!", choices=[])
        self.assertEqual(node.id, "intro")
        self.assertEqual(node.text, "Hello, traveler!")
        self.assertEqual(node.choices, [])

    def test_node_with_speaker(self):
        node = DialogueNode(
            id="npc_talk",
            text="Welcome!",
            choices=[],
            speaker="Old Guide",
            portrait_id="portrait_guide",
        )
        self.assertEqual(node.speaker, "Old Guide")
        self.assertEqual(node.portrait_id, "portrait_guide")

    def test_node_with_choices(self):
        choices = [
            DialogueChoice(text="Yes", next_id="yes_branch"),
            DialogueChoice(text="No", next_id="no_branch"),
        ]
        node = DialogueNode(id="question", text="Do you accept?", choices=choices)
        self.assertEqual(len(node.choices), 2)
        self.assertEqual(node.choices[0].text, "Yes")
        self.assertEqual(node.choices[1].text, "No")

    def test_node_with_flags_after_choice(self):
        node = DialogueNode(
            id="decision",
            text="Make your choice",
            choices=[],
            set_flags_after_choice=["choice_made", "visited_npc"],
        )
        self.assertEqual(len(node.set_flags_after_choice), 2)
        self.assertIn("choice_made", node.set_flags_after_choice)


class TestDialogueTree(unittest.TestCase):
    def setUp(self):
        self.nodes = {
            "start": DialogueNode(
                id="start",
                text="Hello!",
                choices=[DialogueChoice(text="Hi", next_id="response")],
            ),
            "response": DialogueNode(
                id="response",
                text="Nice to meet you!",
                choices=[],
            ),
        }
        self.tree = DialogueTree(self.nodes)

    def test_get_node_exists(self):
        node = self.tree.get_node("start")
        self.assertIsNotNone(node)
        self.assertEqual(node.text, "Hello!")

    def test_get_node_not_exists(self):
        node = self.tree.get_node("nonexistent")
        self.assertIsNone(node)

    def test_has_node_true(self):
        self.assertTrue(self.tree.has_node("start"))
        self.assertTrue(self.tree.has_node("response"))

    def test_has_node_false(self):
        self.assertFalse(self.tree.has_node("missing"))


class TestLoadDialogueFromJson(unittest.TestCase):
    def test_load_empty_dialogue(self):
        data = {"nodes": []}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            temp_path = f.name

        try:
            tree = load_dialogue_from_json(temp_path)
            self.assertEqual(len(tree.nodes), 0)
        finally:
            os.unlink(temp_path)

    def test_load_single_node(self):
        data = {
            "nodes": [
                {"id": "intro", "text": "Welcome!", "choices": []}
            ]
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            temp_path = f.name

        try:
            tree = load_dialogue_from_json(temp_path)
            self.assertTrue(tree.has_node("intro"))
            self.assertEqual(tree.get_node("intro").text, "Welcome!")
        finally:
            os.unlink(temp_path)

    def test_load_node_with_choices(self):
        data = {
            "nodes": [
                {
                    "id": "question",
                    "text": "Do you want to continue?",
                    "choices": [
                        {"text": "Yes", "next_id": "yes_path"},
                        {"text": "No", "next_id": None, "set_flag": "declined"},
                    ],
                }
            ]
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            temp_path = f.name

        try:
            tree = load_dialogue_from_json(temp_path)
            node = tree.get_node("question")
            self.assertEqual(len(node.choices), 2)
            self.assertEqual(node.choices[0].next_id, "yes_path")
            self.assertEqual(node.choices[1].set_flag, "declined")
        finally:
            os.unlink(temp_path)

    def test_load_node_with_speaker_and_portrait(self):
        data = {
            "nodes": [
                {
                    "id": "npc_greeting",
                    "text": "Greetings!",
                    "speaker": "Merchant",
                    "portrait_id": "portrait_merchant",
                    "choices": [],
                }
            ]
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            temp_path = f.name

        try:
            tree = load_dialogue_from_json(temp_path)
            node = tree.get_node("npc_greeting")
            self.assertEqual(node.speaker, "Merchant")
            self.assertEqual(node.portrait_id, "portrait_merchant")
        finally:
            os.unlink(temp_path)

    def test_load_node_with_flags_after_choice(self):
        data = {
            "nodes": [
                {
                    "id": "decision",
                    "text": "Choose wisely",
                    "choices": [],
                    "set_flags_after_choice": ["flag_a", "flag_b"],
                }
            ]
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            temp_path = f.name

        try:
            tree = load_dialogue_from_json(temp_path)
            node = tree.get_node("decision")
            self.assertIn("flag_a", node.set_flags_after_choice)
            self.assertIn("flag_b", node.set_flags_after_choice)
        finally:
            os.unlink(temp_path)

    def test_load_multiple_nodes(self):
        data = {
            "nodes": [
                {"id": "node_1", "text": "First", "choices": []},
                {"id": "node_2", "text": "Second", "choices": []},
                {"id": "node_3", "text": "Third", "choices": []},
            ]
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            temp_path = f.name

        try:
            tree = load_dialogue_from_json(temp_path)
            self.assertEqual(len(tree.nodes), 3)
            self.assertTrue(tree.has_node("node_1"))
            self.assertTrue(tree.has_node("node_2"))
            self.assertTrue(tree.has_node("node_3"))
        finally:
            os.unlink(temp_path)


if __name__ == "__main__":
    unittest.main()
