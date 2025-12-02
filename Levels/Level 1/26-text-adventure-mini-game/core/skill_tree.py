"""Skill tree system for character progression and skill customization."""

import json
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, TYPE_CHECKING
from .logging_utils import log_warning

if TYPE_CHECKING:
    from .stats import Stats


@dataclass
class SkillNode:
    """A single node in a skill tree."""
    id: str
    name: str
    description: str
    skill_id: Optional[str] = None  # The skill granted when unlocked (if any)
    cost: int = 1  # Skill points required to unlock
    tier: int = 1  # Visual tier (1 = root, higher = further from root)
    prerequisites: List[str] = field(default_factory=list)  # Node IDs that must be unlocked first
    stat_bonuses: Dict[str, int] = field(default_factory=dict)  # Passive stat bonuses
    icon_id: Optional[str] = None  # For UI display

    def can_unlock(self, unlocked_nodes: Set[str]) -> bool:
        """Check if this node can be unlocked given current progress."""
        if not self.prerequisites:
            return True
        return all(prereq in unlocked_nodes for prereq in self.prerequisites)


@dataclass
class SkillTree:
    """A complete skill tree containing multiple nodes."""
    id: str
    name: str
    description: str
    nodes: Dict[str, SkillNode] = field(default_factory=dict)
    root_nodes: List[str] = field(default_factory=list)  # Entry point nodes (no prerequisites)

    def __post_init__(self):
        """Identify root nodes after initialization."""
        if not self.root_nodes:
            self.root_nodes = [
                node_id for node_id, node in self.nodes.items()
                if not node.prerequisites
            ]

    def get_node(self, node_id: str) -> Optional[SkillNode]:
        """Get a node by ID."""
        return self.nodes.get(node_id)

    def get_available_nodes(self, unlocked_nodes: Set[str]) -> List[SkillNode]:
        """Get all nodes that can currently be unlocked."""
        available = []
        for node_id, node in self.nodes.items():
            if node_id not in unlocked_nodes and node.can_unlock(unlocked_nodes):
                available.append(node)
        return available

    def get_nodes_by_tier(self) -> Dict[int, List[SkillNode]]:
        """Group nodes by their tier for UI display."""
        tiers: Dict[int, List[SkillNode]] = {}
        for node in self.nodes.values():
            if node.tier not in tiers:
                tiers[node.tier] = []
            tiers[node.tier].append(node)
        return tiers


@dataclass
class SkillTreeProgress:
    """Tracks a character's progress in skill trees."""
    skill_points: int = 0
    skill_points_total: int = 0  # Total ever earned (for tracking)
    unlocked_nodes: Dict[str, Set[str]] = field(default_factory=dict)  # tree_id -> set of node_ids

    def get_unlocked_for_tree(self, tree_id: str) -> Set[str]:
        """Get all unlocked nodes for a specific tree."""
        return self.unlocked_nodes.get(tree_id, set())

    def can_unlock_node(self, tree: SkillTree, node_id: str) -> Tuple[bool, str]:
        """
        Check if a node can be unlocked.

        Returns (can_unlock, reason) tuple.
        """
        node = tree.get_node(node_id)
        if not node:
            return False, "Node not found"

        unlocked = self.get_unlocked_for_tree(tree.id)

        if node_id in unlocked:
            return False, "Already unlocked"

        if not node.can_unlock(unlocked):
            missing = [p for p in node.prerequisites if p not in unlocked]
            prereq_names = ", ".join(missing)
            return False, f"Missing prerequisites: {prereq_names}"

        if self.skill_points < node.cost:
            return False, f"Need {node.cost} skill points (have {self.skill_points})"

        return True, "Can unlock"

    def unlock_node(self, tree: SkillTree, node_id: str) -> Tuple[bool, str, Optional[SkillNode]]:
        """
        Attempt to unlock a node.

        Returns (success, message, node) tuple.
        """
        can_unlock, reason = self.can_unlock_node(tree, node_id)
        if not can_unlock:
            return False, reason, None

        node = tree.get_node(node_id)
        if not node:
            return False, "Node not found", None

        # Deduct skill points
        self.skill_points -= node.cost

        # Add to unlocked nodes
        if tree.id not in self.unlocked_nodes:
            self.unlocked_nodes[tree.id] = set()
        self.unlocked_nodes[tree.id].add(node_id)

        return True, f"Unlocked {node.name}!", node

    def add_skill_points(self, amount: int) -> int:
        """Add skill points and return new total."""
        self.skill_points += amount
        self.skill_points_total += amount
        return self.skill_points

    def get_total_stat_bonuses(self, trees: Dict[str, SkillTree]) -> Dict[str, int]:
        """Calculate total stat bonuses from all unlocked nodes."""
        bonuses: Dict[str, int] = {}

        for tree_id, node_ids in self.unlocked_nodes.items():
            tree = trees.get(tree_id)
            if not tree:
                continue

            for node_id in node_ids:
                node = tree.get_node(node_id)
                if node and node.stat_bonuses:
                    for stat, value in node.stat_bonuses.items():
                        bonuses[stat] = bonuses.get(stat, 0) + value

        return bonuses

    def get_all_unlocked_skills(self, trees: Dict[str, SkillTree]) -> List[str]:
        """Get all skill IDs granted by unlocked nodes."""
        skills = []

        for tree_id, node_ids in self.unlocked_nodes.items():
            tree = trees.get(tree_id)
            if not tree:
                continue

            for node_id in node_ids:
                node = tree.get_node(node_id)
                if node and node.skill_id:
                    skills.append(node.skill_id)

        return skills

    def serialize(self) -> Dict:
        """Serialize progress to JSON-safe dict."""
        return {
            "skill_points": self.skill_points,
            "skill_points_total": self.skill_points_total,
            "unlocked_nodes": {
                tree_id: list(nodes)
                for tree_id, nodes in self.unlocked_nodes.items()
            }
        }

    @classmethod
    def deserialize(cls, data: Dict) -> "SkillTreeProgress":
        """Deserialize progress from dict."""
        progress = cls(
            skill_points=data.get("skill_points", 0),
            skill_points_total=data.get("skill_points_total", 0)
        )

        for tree_id, node_list in data.get("unlocked_nodes", {}).items():
            progress.unlocked_nodes[tree_id] = set(node_list)

        return progress


class SkillTreeManager:
    """Manages skill trees and character progression."""

    def __init__(self, trees: Optional[Dict[str, SkillTree]] = None):
        self.trees: Dict[str, SkillTree] = trees or {}

    def get_tree(self, tree_id: str) -> Optional[SkillTree]:
        """Get a skill tree by ID."""
        return self.trees.get(tree_id)

    def get_available_trees(self, role: Optional[str] = None) -> List[SkillTree]:
        """Get all available skill trees, optionally filtered by role."""
        if role is None:
            return list(self.trees.values())

        # Filter by role if tree has role restrictions
        return [
            tree for tree in self.trees.values()
            if not hasattr(tree, 'roles') or role in getattr(tree, 'roles', [])
        ]

    def apply_skill_tree_bonuses(self, stats: "Stats", progress: SkillTreeProgress) -> None:
        """Apply all stat bonuses from unlocked skill tree nodes to stats."""
        bonuses = progress.get_total_stat_bonuses(self.trees)

        # Store bonuses in a dedicated field for tracking
        if not hasattr(stats, 'skill_tree_modifiers'):
            stats.skill_tree_modifiers = {}

        stats.skill_tree_modifiers = bonuses


def load_skill_node_from_dict(data: Dict) -> SkillNode:
    """Create a SkillNode from a dictionary."""
    return SkillNode(
        id=data["id"],
        name=data["name"],
        description=data.get("description", ""),
        skill_id=data.get("skill_id"),
        cost=data.get("cost", 1),
        tier=data.get("tier", 1),
        prerequisites=data.get("prerequisites", []),
        stat_bonuses=data.get("stat_bonuses", {}),
        icon_id=data.get("icon_id")
    )


def load_skill_tree_from_dict(data: Dict) -> SkillTree:
    """Create a SkillTree from a dictionary."""
    nodes = {}
    for node_data in data.get("nodes", []):
        node = load_skill_node_from_dict(node_data)
        nodes[node.id] = node

    return SkillTree(
        id=data["id"],
        name=data["name"],
        description=data.get("description", ""),
        nodes=nodes,
        root_nodes=data.get("root_nodes", [])
    )


def load_skill_trees_from_json(path: str = os.path.join("data", "skill_trees.json")) -> Dict[str, SkillTree]:
    """Load all skill trees from a JSON file."""
    trees: Dict[str, SkillTree] = {}

    if not os.path.exists(path):
        return trees

    try:
        with open(path, "r") as f:
            data = json.load(f)
    except Exception as exc:
        log_warning(f"Failed to load skill trees: {exc}")
        return trees

    for tree_data in data.get("skill_trees", []):
        tree = load_skill_tree_from_dict(tree_data)
        trees[tree.id] = tree

    return trees


# Skill points awarded per level-up
SKILL_POINTS_PER_LEVEL = 1
