"""Quest system for tracking objectives and progression.

This module re-exports all quest-related classes and functions for backward compatibility.
The actual implementations are in:
- core/quest_models.py: QuestStatus, ObjectiveType, QuestObjective, Quest
- core/quest_manager.py: QuestManager, load_quest_manager
"""

# Re-export all quest-related classes and functions for backward compatibility
from .quest_models import (
    ObjectiveType,
    Quest,
    QuestObjective,
    QuestStatus,
)
from .quest_manager import (
    QuestManager,
    load_quest_manager,
)

__all__ = [
    "ObjectiveType",
    "Quest",
    "QuestObjective",
    "QuestManager",
    "QuestStatus",
    "load_quest_manager",
]
