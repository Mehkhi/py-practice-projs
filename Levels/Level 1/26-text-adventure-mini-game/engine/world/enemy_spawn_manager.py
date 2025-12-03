"""Enemy spawn and management for the overworld scene.

This module handles overworld enemy updates, detection, and battle initiation.
It manages enemy movement, player detection, and coordinates with the battle
system when enemies spot the player.

Dependencies on WorldScene:
    - scene.world: World state for active enemies and current map
    - scene.player: Player entity with position
    - scene._get_current_entities(): Returns current map entities
    - scene._encounter_already_cleared(): Checks if encounter was completed
    - scene._start_battle(): Starts a battle encounter
    - scene._pending_enemy_defeat: Tracks pending enemy defeat after battle
"""

from typing import TYPE_CHECKING

from core.entities import OverworldEnemy

if TYPE_CHECKING:
    from ..world_scene import WorldScene


class _PseudoTrigger:
    """Pseudo-trigger for compatibility with the battle system.

    This class mimics a map trigger to allow overworld enemies to
    integrate with the existing battle trigger system without requiring
    separate handling code.

    Attributes:
        id: Entity ID of the enemy
        data: Dict containing encounter_id
        once: Whether this is a one-time encounter
        fired: Whether the trigger has been activated
        _enemy_ref: Reference to the OverworldEnemy
    """

    def __init__(self, enemy_ref: OverworldEnemy):
        self.id = enemy_ref.entity_id
        self.data = {"encounter_id": enemy_ref.encounter_id}
        self.once = enemy_ref.once
        self.fired = False
        self._enemy_ref = enemy_ref


class EnemySpawnManager:
    """Manages overworld enemy spawning and updates."""

    def __init__(self, scene: "WorldScene"):
        """Initialize enemy manager with reference to the world scene."""
        self.scene = scene

    def update(self, dt: float) -> None:
        """Update all overworld enemies on the current map."""
        try:
            current_map = self.scene.world.get_current_map()
        except Exception:
            return
        active_enemies = self.scene.world.get_active_overworld_enemies(current_map.map_id)

        # Build set of blocked positions (player + NPCs + other enemies)
        blocked_positions = {(self.scene.player.x, self.scene.player.y)}
        _, entities = self.scene._get_current_entities()
        for entity in entities:
            if entity.solid:
                blocked_positions.add((entity.x, entity.y))
        for enemy in active_enemies:
            blocked_positions.add((enemy.x, enemy.y))

        # Update each enemy
        for enemy in active_enemies:
            # Remove self from blocked positions for movement check
            blocked_positions.discard((enemy.x, enemy.y))
            enemy.update(dt, current_map, blocked_positions)
            blocked_positions.add((enemy.x, enemy.y))

            # Check if enemy can see the player
            if enemy.can_see_position(self.scene.player.x, self.scene.player.y):
                self._start_battle_from_enemy(enemy)
                return  # Only trigger one battle at a time

    def _start_battle_from_enemy(self, enemy: OverworldEnemy) -> None:
        """Start a battle triggered by an overworld enemy detecting the player."""
        encounter_id = enemy.encounter_id

        trigger = _PseudoTrigger(enemy)

        # Check if encounter is already cleared (for once-only encounters)
        if enemy.once and self.scene._encounter_already_cleared(encounter_id):
            enemy.defeated = True
            return

        # Start the battle
        self.scene._start_battle(encounter_id, trigger)

        # Mark enemy as defeated if it's a once-only encounter
        # (The actual defeat will be confirmed after battle victory)
        self.scene._pending_enemy_defeat = enemy
