"""Core domain model for the JRPG engine."""

from .endings import (
    load_endings_data,
    evaluate_condition,
    determine_ending,
)

from .skill_tree import (
    SkillNode,
    SkillTree,
    SkillTreeProgress,
    SkillTreeManager,
    load_skill_trees_from_json,
    SKILL_POINTS_PER_LEVEL,
)
