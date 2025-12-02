"""Saveable protocol for game systems that support save/load.

This module defines the Saveable protocol that managers must implement
to participate in the automatic save/load system via SaveContext.
"""

from typing import Protocol, Dict, Any, runtime_checkable


@runtime_checkable
class Saveable(Protocol):
    """Protocol for game systems that support save/load.

    Any manager that wants to be automatically serialized/deserialized
    by SaveContext must implement this protocol:

    1. Define a `save_key` class attribute (str) - the key used in save data
    2. Implement `serialize() -> Dict[str, Any]` - convert state to JSON-safe dict
    3. Implement `deserialize_into(data)` - restore state from saved data

    Example:
        class ArenaManager:
            save_key: str = "arena"

            def serialize(self) -> Dict[str, Any]:
                return {"wins": self.wins, "losses": self.losses}

            def deserialize_into(self, data: Dict[str, Any]) -> None:
                self.wins = data.get("wins", 0)
                self.losses = data.get("losses", 0)

    Note: `deserialize_into` mutates the existing instance rather than creating
    a new one. This is important because managers are often pre-constructed with
    dependencies (fish_db, puzzle_definitions, etc.) before state is loaded.
    """

    save_key: str
    """Unique key for this system in save data (e.g., 'quests', 'arena')."""

    def serialize(self) -> Dict[str, Any]:
        """Serialize state to a JSON-safe dictionary.

        Returns:
            Dictionary containing all state that should be persisted.
        """
        ...

    def deserialize_into(self, data: Dict[str, Any]) -> None:
        """Restore state from saved data (mutates self in-place).

        This differs from a classmethod deserialize() - it updates an existing
        instance rather than creating a new one. This is needed because managers
        are often pre-constructed with dependencies before loading.

        Args:
            data: Previously serialized state dictionary.
        """
        ...
