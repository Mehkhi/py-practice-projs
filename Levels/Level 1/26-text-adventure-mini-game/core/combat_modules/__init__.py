"""Combat system package - refactored modules.

This package contains the modular components of the combat system:
- tactics.py: Coordinated enemy tactics system
- learning_ai.py: Adaptive AI that learns player patterns
- actions.py: Action execution (attack, skill, item, guard, talk, flee)
- action_handlers.py: ActionHandler pattern for action dispatch
- ai.py: AI decision-making (phases, rules, coordination)
- conditions.py: Condition evaluators for AI rule evaluation
- targeting.py: Target selection strategies for AI
- battle_system.py: Core battle infrastructure (turn order, state, combos)
- item_effects.py: Item effect handlers with registry pattern
"""

# Export the refactored modules
from .tactics import TacticsCoordinator, CoordinatedTactic, TacticRole
from .learning_ai import LearningAI, PlayerPattern
from .actions import ActionExecutorMixin
from .action_handlers import (
    ActionHandler,
    ActionHandlerRegistry,
    AttackActionHandler,
    SkillActionHandler,
    ItemActionHandler,
    GuardActionHandler,
    TalkActionHandler,
    FleeActionHandler,
    MemoryActionHandler,
    get_action_handler_registry,
    describe_action,
)
from .ai import BattleAIMixin
from .conditions import ConditionEvaluatorMixin
from .targeting import TargetingMixin
from .battle_system import BattleSystemCore
from .item_effects import execute_item_effect, register_effect, ItemEffectResult

__all__ = [
    # Tactics
    "CoordinatedTactic",
    "TacticRole",
    "TacticsCoordinator",
    # Learning AI
    "LearningAI",
    "PlayerPattern",
    # Mixins
    "ActionExecutorMixin",
    "BattleAIMixin",
    "ConditionEvaluatorMixin",
    "TargetingMixin",
    "BattleSystemCore",
    # Action Handlers
    "ActionHandler",
    "ActionHandlerRegistry",
    "AttackActionHandler",
    "SkillActionHandler",
    "ItemActionHandler",
    "GuardActionHandler",
    "TalkActionHandler",
    "FleeActionHandler",
    "MemoryActionHandler",
    "get_action_handler_registry",
    "describe_action",
    # Item Effects
    "execute_item_effect",
    "register_effect",
    "ItemEffectResult",
]
