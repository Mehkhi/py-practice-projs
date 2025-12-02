"""SaveContext - Registry container for saveable game state.

This module provides SaveContext, a dataclass that bundles the core game state
(world, player) with a registry of Saveable managers. This eliminates the need
for 15+ optional parameters across serialize/deserialize function signatures.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Tuple, TYPE_CHECKING

from .protocol import Saveable

if TYPE_CHECKING:
    from core.world import World
    from core.entities import Player


class SaveContextError(Exception):
    """Raised when one or more managers fail during save/load."""

    def __init__(self, failures: List[Tuple[str, Exception]], operation: str):
        self.failures = failures
        self.operation = operation
        message = "; ".join(f"{key}: {exc}" for key, exc in failures)
        super().__init__(f"{operation} failed for managers -> {message}")


# Known manager attribute names on Game class for auto-registration
KNOWN_MANAGER_ATTRS: List[str] = [
    "quest_manager",
    "day_night_cycle",
    "achievement_manager",
    "weather_system",
    "schedule_manager",
    "fishing_system",
    "puzzle_manager",
    "brain_teaser_manager",
    "gambling_manager",
    "arena_manager",
    "challenge_dungeon_manager",
    "secret_boss_manager",
    "hint_manager",
    "post_game_manager",
    "tutorial_manager",
]


@dataclass
class SaveContext:
    """Container for all saveable game state.

    SaveContext bundles the core game objects (world, player) with a registry
    of Saveable managers. Instead of passing 15+ optional manager parameters
    to serialize/deserialize functions, you pass a single SaveContext.

    Usage:
        # Create context with core objects
        context = SaveContext(world=game.world, player=game.player)

        # Register managers (they must implement Saveable protocol)
        context.register(game.quest_manager)
        context.register(game.arena_manager)

        # Or use convenience factory for Game instances
        context = SaveContext.from_game(game)

        # Serialize all registered managers
        data = context.serialize_managers()

        # Deserialize into all registered managers
        context.deserialize_managers(saved_data)

    Attributes:
        world: World object containing map and flag state
        player: Player object containing inventory, stats, party, etc.
    """

    world: "World"
    player: "Player"
    _registry: Dict[str, Saveable] = field(default_factory=dict, repr=False)

    def register(self, manager: Saveable) -> None:
        """Register a saveable manager.

        Args:
            manager: A manager implementing the Saveable protocol.

        Raises:
            ValueError: If manager doesn't have a save_key attribute.
        """
        if not hasattr(manager, 'save_key'):
            raise ValueError(
                f"Manager {type(manager).__name__} missing save_key attribute. "
                "It must implement the Saveable protocol."
            )
        self._registry[manager.save_key] = manager

    def register_if_saveable(self, manager: Any) -> bool:
        """Register a manager if it implements the Saveable protocol.

        This is a safe version of register() that doesn't raise if the manager
        doesn't implement Saveable. Useful for optional managers that may not
        support saving.

        Args:
            manager: Any object, will only be registered if it has save_key
                    and the required serialize/deserialize_into methods.

        Returns:
            True if the manager was registered, False otherwise.
        """
        if manager is None:
            return False
        if not hasattr(manager, 'save_key'):
            return False
        if not hasattr(manager, 'serialize') or not callable(getattr(manager, 'serialize')):
            return False
        if not hasattr(manager, 'deserialize_into') or not callable(getattr(manager, 'deserialize_into')):
            return False
        self._registry[manager.save_key] = manager
        return True

    def register_all(self, *managers: Optional[Saveable]) -> None:
        """Register multiple managers at once (None values are skipped).

        Args:
            *managers: Saveable managers to register. None values are ignored.
        """
        for manager in managers:
            if manager is not None:
                self.register(manager)

    def get(self, key: str) -> Optional[Saveable]:
        """Get a registered manager by its save_key.

        Args:
            key: The save_key of the manager (e.g., 'arena', 'quests').

        Returns:
            The registered manager, or None if not found.
        """
        return self._registry.get(key)

    def keys(self) -> List[str]:
        """Get all registered save keys.

        Returns:
            List of registered save_key values.
        """
        return list(self._registry.keys())

    def serialize_managers(self) -> Dict[str, Dict[str, Any]]:
        """Serialize all registered managers.

        Returns:
            Dictionary mapping save_key -> serialized state for each manager.

        Raises:
            SaveContextError: If any manager serialization fails.
        """
        result: Dict[str, Dict[str, Any]] = {}
        failures: List[Tuple[str, Exception]] = []
        for key, manager in self._registry.items():
            try:
                result[key] = manager.serialize()
            except Exception as e:
                # Log and aggregate failures so callers can surface them
                from core.logging_utils import log_warning
                log_warning(f"Failed to serialize {key}: {e}")
                failures.append((key, e))
        if failures:
            raise SaveContextError(failures, "serialize")
        return result

    def deserialize_managers(self, data: Dict[str, Any]) -> None:
        """Deserialize state into all registered managers.

        Only managers that are both registered AND have data in the save file
        will be updated. Missing data is silently skipped (for backward compat
        with saves made before a manager was added).

        Args:
            data: The complete save data dictionary.

        Raises:
            SaveContextError: If any manager deserialization fails.
        """
        from core.logging_utils import log_warning

        failures: List[Tuple[str, Exception]] = []
        for key, manager in self._registry.items():
            if key in data:
                try:
                    manager.deserialize_into(data[key])
                except Exception as e:
                    log_warning(f"Failed to deserialize {key}: {e}")
                    failures.append((key, e))
        if failures:
            raise SaveContextError(failures, "deserialize")

    @classmethod
    def from_game(cls, game: Any) -> "SaveContext":
        """Build context from a Game instance (convenience factory).

        This automatically registers all known manager attributes found on
        the game object that implement the Saveable protocol.

        Args:
            game: A Game instance (or any object with world, player, and
                  manager attributes).

        Returns:
            SaveContext with world, player, and all found Saveable managers.
        """
        context = cls(world=game.world, player=game.player)

        for attr_name in KNOWN_MANAGER_ATTRS:
            manager = getattr(game, attr_name, None)
            if manager is not None:
                context.register_if_saveable(manager)

        return context

    @classmethod
    def from_managers(
        cls,
        world: "World",
        player: "Player",
        **managers: Optional[Saveable]
    ) -> "SaveContext":
        """Build context from explicit manager kwargs.

        This is useful for call sites that have managers as local variables
        rather than attributes on a game object.

        Args:
            world: World object.
            player: Player object.
            **managers: Keyword arguments mapping names to Saveable managers.
                       None values are skipped.

        Returns:
            SaveContext with all provided managers registered.
        """
        context = cls(world=world, player=player)
        for manager in managers.values():
            if manager is not None:
                context.register_if_saveable(manager)
        return context
