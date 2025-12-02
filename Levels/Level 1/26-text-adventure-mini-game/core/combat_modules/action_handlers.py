"""Action handlers for the combat system.

This module implements the ActionHandler pattern to replace scattered if/elif chains
for action execution and description. Each action type has a dedicated handler that
encapsulates both execution logic and description generation.

Usage:
    from core.combat_modules.action_handlers import get_action_handler_registry

    registry = get_action_handler_registry()
    handler = registry.get_handler(cmd.action_type)
    if handler:
        handler.execute(executor, cmd, actor)
        description = handler.describe(cmd, context)
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Dict, List, Optional, Any

if TYPE_CHECKING:
    from core.combat import ActionType, BattleCommand, BattleParticipant
    from core.combat_modules.actions import ActionExecutorMixin


class ActionHandler(ABC):
    """Abstract base class for battle action handlers.

    Each handler encapsulates the logic for:
    - Checking if it can handle a specific action type
    - Executing the action
    - Generating a human-readable description of the action

    This pattern replaces scattered if/elif chains with a registry-based approach,
    making the code more maintainable and extensible.
    """

    @property
    @abstractmethod
    def action_type(self) -> "ActionType":
        """The ActionType this handler is responsible for."""
        ...

    def can_handle(self, action: "BattleCommand") -> bool:
        """Check if this handler can process the given action.

        Args:
            action: The battle command to check

        Returns:
            True if this handler can process the action
        """
        return action.action_type == self.action_type

    @abstractmethod
    def execute(
        self,
        executor: "ActionExecutorMixin",
        cmd: "BattleCommand",
        actor: "BattleParticipant"
    ) -> None:
        """Execute the action.

        Args:
            executor: The ActionExecutorMixin instance with helper methods
            cmd: The battle command to execute
            actor: The participant executing the action
        """
        ...

    @abstractmethod
    def describe(self, cmd: "BattleCommand", context: Dict[str, Any]) -> str:
        """Generate a human-readable description of the action.

        Args:
            cmd: The battle command to describe
            context: Additional context for description generation, may include:
                - skills: Dict[str, Skill] - Available skills
                - items_db: Dict[str, Item] - Item database
                - moves_db: MovesDatabase - Moves database

        Returns:
            A short description string (e.g., "attacks", "uses Fireball")
        """
        ...


class AttackActionHandler(ActionHandler):
    """Handler for ATTACK actions."""

    @property
    def action_type(self) -> "ActionType":
        from core.combat import ActionType
        return ActionType.ATTACK

    def execute(
        self,
        executor: "ActionExecutorMixin",
        cmd: "BattleCommand",
        actor: "BattleParticipant"
    ) -> None:
        """Execute an attack action."""
        executor._execute_attack(cmd, actor)

    def describe(self, cmd: "BattleCommand", context: Dict[str, Any]) -> str:
        """Describe an attack action."""
        if cmd.skill_id:
            # Attack with a specific move
            moves_db = context.get("moves_db")
            if moves_db:
                move = moves_db.get_move(cmd.skill_id)
                if move:
                    return f"uses {move.name}"
            return f"uses {cmd.skill_id.replace('_', ' ').title()}"
        return "attacks"


class SkillActionHandler(ActionHandler):
    """Handler for SKILL actions."""

    @property
    def action_type(self) -> "ActionType":
        from core.combat import ActionType
        return ActionType.SKILL

    def execute(
        self,
        executor: "ActionExecutorMixin",
        cmd: "BattleCommand",
        actor: "BattleParticipant"
    ) -> None:
        """Execute a skill action."""
        executor._execute_skill(cmd, actor)

    def describe(self, cmd: "BattleCommand", context: Dict[str, Any]) -> str:
        """Describe a skill action."""
        skills = context.get("skills", {})
        skill = skills.get(cmd.skill_id)
        if skill:
            return f"casts {skill.name}"
        return f"uses {cmd.skill_id}" if cmd.skill_id else "uses a skill"


class ItemActionHandler(ActionHandler):
    """Handler for ITEM actions."""

    @property
    def action_type(self) -> "ActionType":
        from core.combat import ActionType
        return ActionType.ITEM

    def execute(
        self,
        executor: "ActionExecutorMixin",
        cmd: "BattleCommand",
        actor: "BattleParticipant"
    ) -> None:
        """Execute an item use action."""
        executor._execute_item(cmd, actor)

    def describe(self, cmd: "BattleCommand", context: Dict[str, Any]) -> str:
        """Describe an item use action."""
        items_db = context.get("items_db", {})
        item = items_db.get(cmd.item_id)
        if item:
            return f"uses {item.name}"
        return f"uses {cmd.item_id}" if cmd.item_id else "uses an item"


class GuardActionHandler(ActionHandler):
    """Handler for GUARD actions."""

    @property
    def action_type(self) -> "ActionType":
        from core.combat import ActionType
        return ActionType.GUARD

    def execute(
        self,
        executor: "ActionExecutorMixin",
        cmd: "BattleCommand",
        actor: "BattleParticipant"
    ) -> None:
        """Execute a guard action."""
        executor._execute_guard(cmd, actor)

    def describe(self, cmd: "BattleCommand", context: Dict[str, Any]) -> str:
        """Describe a guard action."""
        return "guards"


class TalkActionHandler(ActionHandler):
    """Handler for TALK actions (Undertale-style mercy mechanic)."""

    @property
    def action_type(self) -> "ActionType":
        from core.combat import ActionType
        return ActionType.TALK

    def execute(
        self,
        executor: "ActionExecutorMixin",
        cmd: "BattleCommand",
        actor: "BattleParticipant"
    ) -> None:
        """Execute a talk action."""
        executor._execute_talk(cmd, actor)

    def describe(self, cmd: "BattleCommand", context: Dict[str, Any]) -> str:
        """Describe a talk action."""
        return "talks"


class FleeActionHandler(ActionHandler):
    """Handler for FLEE actions."""

    @property
    def action_type(self) -> "ActionType":
        from core.combat import ActionType
        return ActionType.FLEE

    def execute(
        self,
        executor: "ActionExecutorMixin",
        cmd: "BattleCommand",
        actor: "BattleParticipant"
    ) -> None:
        """Execute a flee action."""
        executor._execute_flee(cmd, actor)

    def describe(self, cmd: "BattleCommand", context: Dict[str, Any]) -> str:
        """Describe a flee action."""
        return "flees"


class MemoryActionHandler(ActionHandler):
    """Handler for MEMORY actions (calculator-style memory operations)."""

    @property
    def action_type(self) -> "ActionType":
        from core.combat import ActionType
        return ActionType.MEMORY

    def execute(
        self,
        executor: "ActionExecutorMixin",
        cmd: "BattleCommand",
        actor: "BattleParticipant"
    ) -> None:
        """Execute a memory operation action."""
        executor._execute_memory(cmd, actor)

    def describe(self, cmd: "BattleCommand", context: Dict[str, Any]) -> str:
        """Describe a memory operation action."""
        from core.combat import MemoryOperation

        op = cmd.memory_operation
        if op == MemoryOperation.STORE:
            stat = cmd.memory_stat or "value"
            return f"stores {stat}"
        elif op == MemoryOperation.SUBTRACT:
            stat = cmd.memory_stat or "value"
            return f"subtracts {stat}"
        elif op == MemoryOperation.RECALL:
            return "recalls memory"
        elif op == MemoryOperation.CLEAR:
            return "clears memory"
        return "uses memory"


class ActionHandlerRegistry:
    """Registry for action handlers.

    Manages a collection of ActionHandler instances and provides lookup
    by ActionType. This centralizes the action dispatch logic and makes
    it easy to add new action types.

    Example:
        registry = ActionHandlerRegistry()
        registry.register(AttackActionHandler())
        registry.register(SkillActionHandler())

        handler = registry.get_handler(ActionType.ATTACK)
        if handler:
            handler.execute(executor, cmd, actor)
    """

    def __init__(self) -> None:
        """Initialize an empty registry."""
        self._handlers: Dict["ActionType", ActionHandler] = {}

    def register(self, handler: ActionHandler) -> None:
        """Register a handler for its action type.

        Args:
            handler: The handler to register
        """
        self._handlers[handler.action_type] = handler

    def get_handler(self, action_type: "ActionType") -> Optional[ActionHandler]:
        """Get the handler for a specific action type.

        Args:
            action_type: The action type to look up

        Returns:
            The registered handler, or None if not found
        """
        return self._handlers.get(action_type)

    def get_handler_for_command(self, cmd: "BattleCommand") -> Optional[ActionHandler]:
        """Get the handler for a battle command.

        Args:
            cmd: The battle command

        Returns:
            The handler that can process this command, or None
        """
        return self.get_handler(cmd.action_type)

    def execute(
        self,
        executor: "ActionExecutorMixin",
        cmd: "BattleCommand",
        actor: "BattleParticipant"
    ) -> bool:
        """Execute a command using the appropriate handler.

        Args:
            executor: The ActionExecutorMixin instance
            cmd: The battle command to execute
            actor: The participant executing the action

        Returns:
            True if a handler was found and executed, False otherwise
        """
        handler = self.get_handler(cmd.action_type)
        if handler:
            handler.execute(executor, cmd, actor)
            return True
        return False

    def describe(self, cmd: "BattleCommand", context: Dict[str, Any]) -> str:
        """Describe a command using the appropriate handler.

        Args:
            cmd: The battle command to describe
            context: Additional context for description

        Returns:
            A description string, or "acts" if no handler found
        """
        handler = self.get_handler(cmd.action_type)
        if handler:
            return handler.describe(cmd, context)
        return "acts"

    @property
    def registered_types(self) -> List["ActionType"]:
        """Get all registered action types."""
        return list(self._handlers.keys())


# Module-level singleton registry
_registry: Optional[ActionHandlerRegistry] = None


def get_action_handler_registry() -> ActionHandlerRegistry:
    """Get the global action handler registry.

    Creates and populates the registry on first call.

    Returns:
        The singleton ActionHandlerRegistry instance
    """
    global _registry
    if _registry is None:
        _registry = ActionHandlerRegistry()
        _registry.register(AttackActionHandler())
        _registry.register(SkillActionHandler())
        _registry.register(ItemActionHandler())
        _registry.register(GuardActionHandler())
        _registry.register(TalkActionHandler())
        _registry.register(FleeActionHandler())
        _registry.register(MemoryActionHandler())
    return _registry


def describe_action(cmd: "BattleCommand", context: Dict[str, Any]) -> str:
    """Convenience function to describe a battle command.

    Args:
        cmd: The battle command to describe
        context: Additional context (skills, items_db, moves_db, etc.)

    Returns:
        A human-readable description of the action
    """
    return get_action_handler_registry().describe(cmd, context)
