"""World and runtime state deserialization."""

from typing import Any, Dict

from ...world import World
from .base import DeserializationResources, DeserializerContext, DomainDeserializer


def deserialize_world_runtime_state(world: World, runtime_data: Dict[str, Any]) -> None:
    """Restore world runtime state: triggers and enemies."""
    trigger_states = runtime_data.get("trigger_states", {})
    for map_id, fired_triggers in trigger_states.items():
        if map_id in world.maps:
            for trigger in world.maps[map_id].triggers:
                if trigger.id in fired_triggers:
                    trigger.fired = True

    enemy_states = runtime_data.get("enemy_states", {})
    for map_id, defeated_enemies in enemy_states.items():
        enemies = world.get_map_overworld_enemies(map_id)
        for enemy in enemies:
            if enemy.entity_id in defeated_enemies:
                enemy.defeated = True


def _restore_world_base(world_data: Dict[str, Any], context: DeserializerContext) -> None:
    world = context.world
    if "current_map_id" in world_data:
        map_id = world_data["current_map_id"]
        if map_id in world.maps:
            world.set_current_map(map_id)
        else:
            world.current_map_id = map_id
    if "flags" in world_data:
        world.flags = world_data["flags"]
    if "visited_maps" in world_data:
        world.visited_maps = set(world_data["visited_maps"])
    else:
        world.mark_map_visited(world.current_map_id)


def _restore_world_runtime(world_data: Dict[str, Any], context: DeserializerContext) -> None:
    if "runtime_state" in world_data:
        deserialize_world_runtime_state(context.world, world_data["runtime_state"])


def _restore_schedule(data: Dict[str, Any], context: DeserializerContext) -> None:
    if context.schedule_manager and "npc_schedules" in data:
        context.schedule_manager.deserialize_into(data["npc_schedules"])


class WorldDeserializer(DomainDeserializer):
    """Deserialize world state and schedules."""

    def deserialize(self, data: Dict[str, Any], context: DeserializerContext, resources: DeserializationResources) -> None:
        world_data = data.get("world", {})
        _restore_world_base(world_data, context)
        _restore_world_runtime(world_data, context)
        _restore_schedule(data, context)
