"""Save system package.

This package contains the save/load system split into focused modules:
- protocol: Saveable protocol for managers that support save/load
- context: SaveContext registry for bundling saveable managers
- serializer: Serialization logic for game state
- deserializer: Deserialization logic for loading saves
- migration: Save file version migration
- validation: Save data validation and recovery
"""

from .protocol import Saveable
from .context import SaveContext, KNOWN_MANAGER_ATTRS, SaveContextError
from .serializer import (
    SAVE_FILE_VERSION,
    DEFAULT_STARTING_MAP,
    serialize_entity_stats,
    serialize_skill_tree_progress,
    serialize_party_member,
    serialize_world_runtime_state,
    serialize_crafting_progress,
    serialize_bestiary,
    serialize_state,
    serialize_state_from_context,
)
from .deserializer import (
    DeserializationResources,
    deserialize_stats,
    deserialize_skill_tree_progress,
    deserialize_crafting_progress,
    deserialize_bestiary,
    deserialize_party_member,
    deserialize_world_runtime_state,
    deserialize_puzzle_manager,
    deserialize_brain_teaser_manager,
    deserialize_gambling_manager,
    deserialize_challenge_dungeon_manager,
    deserialize_state,
    deserialize_state_from_context,
)
from .deserializers import (
    DeserializerContext,
    DomainDeserializer,
    run_deserializers,
)
from .migration import (
    get_save_version,
    migrate_save_data,
)
from .validation import (
    validate_save_data,
    ensure_field,
    recover_partial_save,
)

__all__ = [
    # Protocol and Context
    "Saveable",
    "SaveContext",
    "SaveContextError",
    "KNOWN_MANAGER_ATTRS",
    # Constants
    "SAVE_FILE_VERSION",
    "DEFAULT_STARTING_MAP",
    # Serialization
    "serialize_entity_stats",
    "serialize_skill_tree_progress",
    "serialize_party_member",
    "serialize_world_runtime_state",
    "serialize_crafting_progress",
    "serialize_bestiary",
    "serialize_state",
    "serialize_state_from_context",
    # Deserialization
    "deserialize_stats",
    "deserialize_skill_tree_progress",
    "deserialize_crafting_progress",
    "deserialize_bestiary",
    "deserialize_party_member",
    "deserialize_world_runtime_state",
    "deserialize_puzzle_manager",
    "deserialize_brain_teaser_manager",
    "deserialize_gambling_manager",
    "deserialize_challenge_dungeon_manager",
    "deserialize_state",
    "deserialize_state_from_context",
    "DeserializationResources",
    "DeserializerContext",
    "DomainDeserializer",
    "run_deserializers",
    # Migration
    "get_save_version",
    "migrate_save_data",
    # Validation
    "validate_save_data",
    "ensure_field",
    "recover_partial_save",
]
