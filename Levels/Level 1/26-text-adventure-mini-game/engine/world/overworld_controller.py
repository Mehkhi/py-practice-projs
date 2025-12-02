"""Input and movement handling for the overworld scene.

This module handles player input (keyboard events) and movement logic
for the overworld exploration scene. It processes directional input,
validates movement against map and entity collision, and manages
walking animation state.

Dependencies on WorldScene:
    - scene.manager: SceneManager for pushing pause menu
    - scene.world: World state for current map and active enemies
    - scene.player: Player entity with position and movement methods
    - scene.save_manager: SaveManager for pause menu
    - scene.save_slot: int for current save slot
    - scene.assets: AssetManager for pause menu
    - scene.scale: int for display scale
    - scene.items_db: Dict of items for pause menu
    - scene.quest_manager: Optional[QuestManager] for pause menu
    - scene.move_timer: float for movement timing
    - scene.move_delay: float for movement delay threshold
    - scene.anim_time: float for animation timing
    - scene.is_walking: bool for walking animation state
    - scene.walk_anim_time: float for walk animation timing
    - scene.walk_anim_speed: float for walk animation speed
    - scene.walk_frame: int for current walk frame
    - scene.player_facing: str for player direction
    - scene.draw_tile: int for scaled tile size
    - scene.camera_offset: Tuple[int, int] for camera position
    - scene._last_blocked_trigger: Optional[str] for trigger state
    - scene._warp_cooldown_pos: Optional position tuple for warp cooldown
    - scene._interact(): Method to handle interaction
    - scene._get_current_entities(): Returns current map and entities
    - scene.enemy_manager: EnemySpawnManager for enemy battle initiation
"""

import pygame
from typing import TYPE_CHECKING

from ..input_manager import get_input_manager

if TYPE_CHECKING:
    from ..world_scene import WorldScene


class OverworldController:
    """Handles input and movement for the overworld scene."""

    def __init__(self, scene: "WorldScene"):
        """Initialize controller with reference to the world scene."""
        self.scene = scene
        self.input_manager = get_input_manager()

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle input events."""
        if self.input_manager.is_action_pressed(event, "menu"):
            # Open pause menu if we're the current scene and no other overlay is active
            if self.scene.manager and self.scene.manager.current() is self.scene:
                self._open_pause_menu()
        if self.input_manager.is_action_pressed(event, "interact") or self.input_manager.is_action_pressed(event, "confirm"):
            self.scene._interact()

    def _open_pause_menu(self) -> None:
        """Open the pause menu overlay."""
        from ..pause_menu_scene import PauseMenuScene

        # Get save_manager from manager or fall back to instance variable
        save_manager = self.scene.get_manager_attr(
            "save_manager", "_open_pause_menu"
        )
        if not save_manager:
            save_manager = self.scene.save_manager

        pause_scene = PauseMenuScene(
            self.scene.manager,
            self.scene.world,
            self.scene.player,
            save_manager,
            assets=self.scene.assets,
            scale=self.scene.scale,
            save_slot=self.scene.save_slot,
            items_db=self.scene.items_db,
            quest_manager=self.scene.quest_manager,
        )
        self.scene.manager.push(pause_scene)

    def update_movement(self, dt: float) -> None:
        """Update movement state and handle input."""
        self.scene.move_timer += dt
        self.scene.anim_time += dt

        # Update walking animation
        if self.scene.is_walking:
            self.scene.walk_anim_time += dt
            # Calculate current walk frame (4-frame cycle)
            self.scene.walk_frame = int(self.scene.walk_anim_time * self.scene.walk_anim_speed) % 4
            # Stop walking animation after a short duration
            if self.scene.walk_anim_time >= 0.15:
                self.scene.is_walking = False
                self.scene.walk_frame = 0

        # Handle movement input
        up = self.input_manager.is_action_active("up")
        down = self.input_manager.is_action_active("down")
        left = self.input_manager.is_action_active("left")
        right = self.input_manager.is_action_active("right")
        dx, dy = 0, 0

        # Update facing direction even when not moving (for idle animation)
        if up:
            self.scene.player_facing = "up"
        elif down:
            self.scene.player_facing = "down"
        elif left:
            self.scene.player_facing = "left"
        elif right:
            self.scene.player_facing = "right"

        if self.scene.move_timer >= self.scene.move_delay:
            if up:
                dy = -1
            elif down:
                dy = 1
            elif left:
                dx = -1
            elif right:
                dx = 1

            if dx != 0 or dy != 0:
                self._try_move(dx, dy)
                self.scene.move_timer = 0.0

    def _try_move(self, dx: int, dy: int) -> None:
        """Attempt to move the player."""
        current_map = self.scene.world.get_current_map()
        new_x = self.scene.player.x + dx
        new_y = self.scene.player.y + dy

        # Update player facing direction
        if dx > 0:
            self.scene.player_facing = "right"
        elif dx < 0:
            self.scene.player_facing = "left"
        elif dy > 0:
            self.scene.player_facing = "down"
        elif dy < 0:
            self.scene.player_facing = "up"

        # Check if blocked by an overworld enemy
        active_enemies = self.scene.world.get_active_overworld_enemies(current_map.map_id)
        for enemy in active_enemies:
            if enemy.x == new_x and enemy.y == new_y:
                # Walking into an enemy triggers battle
                self.scene.enemy_manager._start_battle_from_enemy(enemy)
                return

        # Check if blocked by a solid entity (NPC, etc.)
        _, entities = self.scene._get_current_entities()
        for entity in entities:
            if entity.solid and entity.x == new_x and entity.y == new_y:
                return  # Blocked by solid entity

        # Check for puzzle interactions (block pushing) if target is not walkable
        if not current_map.is_walkable(new_x, new_y):
            # Determine direction string for puzzle interaction
            direction = None
            if dx > 0:
                direction = "right"
            elif dx < 0:
                direction = "left"
            elif dy > 0:
                direction = "down"
            elif dy < 0:
                direction = "up"

            if direction and self.scene.trigger_handler._check_puzzle_interaction(direction):
                # Puzzle interaction occurred (block was pushed), don't move player
                return

        if current_map.is_walkable(new_x, new_y):
            # Check for ice sliding
            puzzle_manager = getattr(self.scene, 'puzzle_manager', None)
            if puzzle_manager and puzzle_manager.is_on_ice(current_map.map_id, new_x, new_y):
                # Player is on ice - calculate slide destination
                direction = None
                if dx > 0:
                    direction = "right"
                elif dx < 0:
                    direction = "left"
                elif dy > 0:
                    direction = "down"
                elif dy < 0:
                    direction = "up"

                if direction:
                    dx_map = {"left": -1, "right": 1, "up": 0, "down": 0}
                    dy_map = {"left": 0, "right": 0, "up": -1, "down": 1}
                    slide_dx = dx_map.get(direction, 0)
                    slide_dy = dy_map.get(direction, 0)
                    final_x, final_y = puzzle_manager.calculate_player_slide_destination(
                        new_x, new_y, slide_dx, slide_dy, self.scene.world
                    )
                    self.scene.player.set_position(final_x, final_y)
                else:
                    self.scene.player.move(dx, dy)
            else:
                self.scene.player.move(dx, dy)

            self.scene._last_blocked_trigger = None
            # Clear warp cooldown once player moves
            self.scene._warp_cooldown_pos = None
            self.scene.is_walking = True
            self.scene.walk_anim_time = 0.0

    def _update_camera(self) -> None:
        """Update camera to center on player."""
        screen_width, screen_height = pygame.display.get_surface().get_size()
        target_x = self.scene.player.x * self.scene.draw_tile + self.scene.draw_tile // 2 - screen_width // 2
        target_y = self.scene.player.y * self.scene.draw_tile + self.scene.draw_tile // 2 - screen_height // 2

        map_px_w = self.scene.world.get_current_map().width * self.scene.draw_tile
        map_px_h = self.scene.world.get_current_map().height * self.scene.draw_tile

        clamped_x = max(0, min(target_x, max(0, map_px_w - screen_width)))
        clamped_y = max(0, min(target_y, max(0, map_px_h - screen_height)))
        self.scene.camera_offset = (clamped_x, clamped_y)
