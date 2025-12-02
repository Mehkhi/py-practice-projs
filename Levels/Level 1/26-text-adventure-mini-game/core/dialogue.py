"""Dialogue and choice system."""

import os
from dataclasses import dataclass, field
from typing import List, Optional, Dict

from .data_loader import load_json_file


@dataclass
class DialogueChoice:
    """A choice option in a dialogue node."""
    text: str
    next_id: Optional[str] = None
    set_flag: Optional[str] = None  # world flag to set when chosen
    discover_recipes: List[str] = field(default_factory=list)  # Recipe IDs to discover when chosen


@dataclass
class DialogueNode:
    """A single dialogue node with text and choices."""
    id: str
    text: str
    choices: List[DialogueChoice]
    speaker: Optional[str] = None
    portrait_id: Optional[str] = None
    set_flags_after_choice: Optional[List[str]] = None
    discover_recipes: List[str] = field(default_factory=list)  # Recipe IDs to discover when node is reached


class DialogueTree:
    """Manages a dialogue tree structure."""

    def __init__(self, nodes: Dict[str, DialogueNode]):
        self.nodes = nodes

    def get_node(self, node_id: str) -> Optional[DialogueNode]:
        """Get a dialogue node by ID."""
        return self.nodes.get(node_id)

    def has_node(self, node_id: str) -> bool:
        """Check if a node exists."""
        return node_id in self.nodes


def load_dialogue_from_json(
    json_path: str = os.path.join("data", "dialogue.json")
) -> DialogueTree:
    """Load a dialogue tree from a JSON file."""
    data = load_json_file(json_path, default={}, context="Loading dialogue")

    nodes = {}
    for node_data in data.get('nodes', []):
        choices = []
        for choice_data in node_data.get('choices', []):
            choices.append(DialogueChoice(
                text=choice_data['text'],
                next_id=choice_data.get('next_id'),
                set_flag=choice_data.get('set_flag'),
                discover_recipes=choice_data.get('discover_recipes', [])
            ))

        nodes[node_data['id']] = DialogueNode(
            id=node_data['id'],
            text=node_data['text'],
            choices=choices,
            speaker=node_data.get('speaker'),
            portrait_id=node_data.get('portrait_id'),
            set_flags_after_choice=node_data.get('set_flags_after_choice'),
            discover_recipes=node_data.get('discover_recipes', [])
        )

    return DialogueTree(nodes)
