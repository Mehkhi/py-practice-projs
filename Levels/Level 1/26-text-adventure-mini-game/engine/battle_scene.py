"""Battle scene for turn-based combat."""

import json
import math
import os
import random
import pygame
from typing import Optional, Dict, List, Tuple, Any, TYPE_CHECKING

from .scene import Scene
from .assets import AssetManager
from .ui import Menu, MessageBox, NineSlicePanel, draw_hp_bar, draw_sp_bar, draw_status_icons, CombatLog
from .theme import Colors, Fonts, Layout, Gradients
from .battle import (
    PartyAIMixin,
    BattleAnimationsMixin,
    BattleRendererMixin,
    BattleOutcomesMixin,
    BattleMenuMixin,
    BattleHudMixin,
    BattleUILayoutMixin,
    BIOME_TO_BACKDROP,
    BIOME_GRADIENTS,
    FLASH_INITIAL_INTENSITY,
    FLASH_DECAY_RATE,
    AI_NOTIFICATION_DURATION,
    BattleStateManager,
    BattleRewardsHandler,
)
from .battle.initializer import BattleInitializer
from core.combat import BattleSystem, ActionType, BattleCommand, BattleState, MemoryOperation
from core.data_loader import load_json_file
from core.entities import Player
from core.items import Item
from core.world import World
from core.moves import get_moves_database, Move, MoveAnimation
from core.weather import WeatherType, WEATHER_TINTS, get_biome_for_map
from core.logging_utils import log_warning, log_error
from core.tutorial_system import TipTrigger
from engine.battle.phases import BattlePhaseManager

if TYPE_CHECKING:
    from .scene import SceneManager
    from core.world import Trigger


# Constants imported from engine.battle.constants:
# BIOME_TO_BACKDROP, BIOME_GRADIENTS, FLASH_INITIAL_INTENSITY,
# FLASH_DECAY_RATE, AI_NOTIFICATION_DURATION


class BattleScene(
    PartyAIMixin,
    BattleAnimationsMixin,
    BattleRendererMixin,
    BattleOutcomesMixin,
    BattleMenuMixin,
    BattleHudMixin,
    BattleUILayoutMixin,
    Scene,
):
    """Turn-based battle UI scene.

    Inherits functionality from:
    - PartyAIMixin: AI logic for party member actions
    - BattleAnimationsMixin: Attack animations and visual effects
    - BattleRendererMixin: Flash effects, damage numbers, debug overlays
    - BattleOutcomesMixin: Victory, defeat, escape handling
    - BattleMenuMixin: Menu input handling and state machine
    - BattleHudMixin: HUD rendering (HP/SP bars, status icons, hotbar)
    """

    def __init__(
        self,
        manager: Optional["SceneManager"],
        battle_system: BattleSystem,
        world: World,
        player: Player,
        assets: Optional[AssetManager] = None,
        scale: int = 2,
        rewards: Optional[Dict[str, Any]] = None,
        items_db: Optional[Dict[str, Item]] = None,
        backdrop_id: Optional[str] = None,
        source_trigger: Optional["Trigger"] = None,
        encounter_id: Optional[str] = None,
    ):
        super().__init__(manager)
        self.battle_system = battle_system
        self.world = world
        self.player = player
        self.scale = max(1, int(scale))
        self.assets = assets
        self.panel: Optional[NineSlicePanel] = None
        self.rewards = rewards if rewards is not None else self._default_rewards()
        self.items_db = items_db
        self.backdrop_id = backdrop_id
        self.source_trigger = source_trigger
        self.encounter_id = encounter_id

        # Rewards / outcome handler
        self.rewards_handler = BattleRewardsHandler(
            world=self.world,
            player=self.player,
            battle_system=self.battle_system,
            scene=self,
            rewards=self.rewards,
        )

        # Delegate detailed setup to initializer helper
        BattleInitializer().initialize(self)

        # Phase manager for update flow
        self.phase_manager = BattlePhaseManager(self)

    def _default_rewards(self) -> Dict[str, Any]:
        """Return base rewards structure when none is provided."""
        return {"items": {}, "flags": []}

    def _get_moves_db(self):
        """Helper to obtain the moves database.

        Separated for easier overriding/mocking in tests.
        """
        return get_moves_database()

    def _get_backdrop_id(self) -> Optional[str]:
        """
        Determine the backdrop sprite ID for the battle background.

        Priority:
        1. Explicit backdrop_id passed to the scene (from encounter data)
        2. Derived from current map's biome
        3. None (will use gradient fallback)
        """
        # Use explicit backdrop if provided
        if self.backdrop_id:
            return self.backdrop_id

        # Derive from current map biome
        if self.world and self.world.current_map_id:
            biome = get_biome_for_map(self.world.current_map_id)
            if biome:
                return BIOME_TO_BACKDROP.get(biome)

        return None

    def _get_biome(self) -> Optional[str]:
        """Get the current biome for gradient/tint selection."""
        if self.world and self.world.current_map_id:
            return get_biome_for_map(self.world.current_map_id)
        return None

    # Menu handling methods (_queue_attack through _queue_memory_operation)
    # are now in BattleMenuMixin - see engine/battle/menu.py
    # The following methods are provided by BattleMenuMixin:
    #   handle_event, _handle_main_menu_selection, _queue_attack, _handle_move_selection,
    #   _show_skill_menu, _handle_skill_selection, _show_item_menu, _use_hotbar_item,
    #   _handle_item_selection, _queue_guard, _queue_talk, _queue_flee, _queue_auto_action,
    #   _show_memory_menu, _handle_memory_selection, _show_memory_stat_menu,
    #   _handle_memory_stat_selection, _queue_memory_operation, _begin_target_selection,
    #   _move_target_selection, _select_target, _alive_enemies, _alive_allies,
    #   _find_next_alive_index, _current_actor, _reset_player_phase, _advance_actor_after_command,
    #   _describe_auto_action
    # Party AI methods (_select_party_ai_action, _fighter_ai, _mage_ai, _healer_ai, _support_ai)
    #   now in PartyAIMixin (engine/battle/party_ai.py)
    # Menu helper methods (_describe_auto_action through _select_target) now in BattleMenuMixin
    # HUD helper (_collect_status_icons) now in BattleHudMixin
    # Animation methods (_start_move_animation, _draw_*_animation, trigger_* effects)
    #   now in BattleAnimationsMixin (engine/battle/animations.py)

    def update(self, dt: float) -> None:
        """Update battle state."""
        # Apply battle speed multiplier for animations (only during auto-battle)
        speed_multiplier = self.battle_speed if self.auto_battle else 1
        scaled_dt = dt * speed_multiplier

        # Update animation timer with speed multiplier
        if self.current_animation:
            self.animation_timer += scaled_dt

        # Update enhanced animation effects (uses scaled_dt internally)
        self._update_animation_effects(dt)

        # Delegate state-specific behavior to phase manager
        self._check_resource_warnings()
        self.phase_manager.update(dt)

        if self.battle_system.state != BattleState.PLAYER_CHOOSE:
            self._player_phase_initialized = False

    def _process_auto_battle_turn(self) -> None:
        """Process auto-battle by queuing AI actions for all remaining party members."""
        from core.combat import ActionType, BattleCommand

        # Queue actions for all remaining party members in the turn
        while self.active_player_index is not None:
            actor = self._current_actor()
            if not actor:
                break

            # Use party AI to select action
            cmd = self._select_party_ai_action(actor)
            if cmd:
                self.battle_system.queue_player_command(cmd)
                action_desc = self._describe_auto_action(cmd)
                # Add to combat log instead of message box (less spam)
                if hasattr(self, 'combat_log') and self.combat_log:
                    self.combat_log.add_message(f"{actor.entity.name}: {action_desc}")
            else:
                # Fallback to guard
                cmd = BattleCommand(
                    actor_id=actor.entity.entity_id,
                    action_type=ActionType.GUARD
                )
                self.battle_system.queue_player_command(cmd)
                if hasattr(self, 'combat_log') and self.combat_log:
                    self.combat_log.add_message(f"{actor.entity.name}: Guards!")

            self._advance_actor_after_command()

    def _check_resource_warnings(self) -> None:
        """Trigger low HP/SP tutorial tips when thresholds are crossed."""
        if self.battle_system.state in (BattleState.VICTORY, BattleState.DEFEAT, BattleState.ESCAPED):
            return

        tutorial_manager = self.get_manager_attr(
            "tutorial_manager", "_check_resource_warnings"
        )
        if not tutorial_manager:
            return

        for participant in self.battle_system.players:
            stats = getattr(participant, "stats", None)
            if not stats:
                continue

            if stats.max_hp > 0 and not self._low_hp_tip_triggered:
                hp_percent = (stats.hp / stats.max_hp) * 100 if stats.max_hp else 0
                if hp_percent <= 25:
                    tutorial_manager.trigger_tip(TipTrigger.LOW_HP_WARNING)
                    self._low_hp_tip_triggered = True

            if stats.max_sp and stats.max_sp > 0 and not self._low_sp_tip_triggered:
                sp_percent = (stats.sp / stats.max_sp) * 100 if stats.max_sp else 0
                if sp_percent <= 20:
                    tutorial_manager.trigger_tip(TipTrigger.LOW_SP_WARNING)
                    self._low_sp_tip_triggered = True

    def _handle_victory(self) -> None:
        """Handle battle victory."""
        self._finalize_outcome("victory")

        # Revive all defeated party members after victory
        self._revive_defeated_party_members()

        if not self._rewards_applied:
            self._rewards_applied = True  # Set first to prevent re-entry
            reward_message_set = self._apply_rewards()
        else:
            reward_message_set = False

        # Set final_boss_defeated flag for final boss encounters
        if self.encounter_id == "final_boss" and self.battle_system.state == BattleState.VICTORY:
            self.world.set_flag("final_boss_defeated", True)

        # Check if this is the final boss and transition to ending immediately
        if self.encounter_id == "final_boss" and self.battle_system.state == BattleState.VICTORY:
            self._transition_to_ending()
            return

        if not reward_message_set:
            # Build enhanced victory message with battle summary
            summary = self._build_battle_summary()
            if self._victory_spared:
                self.message_box.set_text(f"You spared your foes. Peace wins the day!\n{summary}\nPress Enter to continue...")
            else:
                self.message_box.set_text(f"Victory! {summary}\nPress Enter to continue...")

    def _handle_defeat(self) -> None:
        """Handle battle defeat."""
        self._finalize_outcome("defeat")

        if not self._defeat_tip_triggered:
            tutorial_manager = self.get_manager_attr(
                "tutorial_manager", "_handle_defeat"
            )
            if tutorial_manager:
                tutorial_manager.trigger_tip(TipTrigger.FIRST_DEATH)
                self._defeat_tip_triggered = True

        # Build informative defeat message with length safety
        alive_enemies = [e for e in self.battle_system.enemies if e.is_alive()]
        enemy_count = len(alive_enemies)
        # Truncate enemy names to prevent overflow (max 15 chars each)
        enemy_names = [e.entity.name[:15] for e in alive_enemies[:3]]

        if enemy_count == 0:
            defeat_msg = "Defeat! All enemies fell, but so did your party.\n"
        elif enemy_count == 1:
            defeat_msg = f"Defeat! {enemy_names[0]} remains.\n"
        elif enemy_count <= 3:
            defeat_msg = f"Defeat! {', '.join(enemy_names)} remain.\n"
        else:
            defeat_msg = f"Defeat! {enemy_count} enemies remain.\n"

        # Keep tip concise to avoid message box overflow
        defeat_msg += "Tip: Level up or try new strategies.\nPress Enter to continue..."
        self.message_box.set_text(defeat_msg)

    def _handle_escape(self) -> None:
        """Handle successful escape."""
        self._finalize_outcome("escaped")

        # Build informative escape message with consequences
        alive_players = [p for p in self.battle_system.players if p.is_alive()]
        alive_count = len(alive_players)
        total_players = len(self.battle_system.players)

        escape_msg = "You escaped the battle!\n"

        if alive_count < total_players:
            escape_msg += f"Warning: {total_players - alive_count} party member(s) are unconscious.\n"

        # Show HP status
        if self.player.stats:
            hp_percent = (self.player.stats.hp / self.player.stats.max_hp * 100) if self.player.stats.max_hp > 0 else 0
            if hp_percent < 25:
                escape_msg += f"Your HP is critically low ({int(hp_percent)}%).\n"
            elif hp_percent < 50:
                escape_msg += f"Your HP is low ({int(hp_percent)}%).\n"

        escape_msg += "No rewards were earned. Press Enter to continue..."
        self.message_box.set_text(escape_msg)

    def _get_flag_as_int(self, flag_name: str, default: int = 0) -> int:
        """Safely get a world flag value as an integer.

        Handles cases where flags may be boolean, string, or other types
        by returning the default value for non-numeric types.

        Args:
            flag_name: The name of the flag to retrieve
            default: Default value if flag is missing or non-numeric

        Returns:
            The flag value as an integer, or the default
        """
        value = self.world.get_flag(flag_name)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return default
        return int(value)

    def _increment_flag(self, flag_name: str, amount: int = 1) -> None:
        """Increment an integer world flag safely.

        Args:
            flag_name: The name of the flag to increment
            amount: Amount to add (default 1)
        """
        current = self._get_flag_as_int(flag_name, 0)
        self.world.set_flag(flag_name, current + amount)

    def _revive_defeated_party_members(self) -> None:
        """Revive all defeated party members after winning a battle."""
        # Revive player if somehow dead (shouldn't happen on victory, but safety check)
        if self.player.stats and self.player.stats.hp <= 0:
            log_warning("Player was dead on victory - this indicates a logic error")
            self.player.stats.hp = max(1, self.player.stats.max_hp // 4)

        # Revive all defeated party members with 1 HP
        for member in getattr(self.player, "party", []):
            if member and member.stats and member.stats.hp <= 0:
                member.stats.hp = 1

    def _build_battle_summary(self) -> str:
        """Build a summary of battle statistics."""
        parts = []

        # Turns taken
        turns = self.battle_system.turn_counter
        if turns > 0:
            parts.append(f"Turns: {turns}")

        # Enemies spared vs defeated
        spared_count = sum(1 for e in self.battle_system.enemies if getattr(e, "spared", False))
        defeated_count = sum(1 for e in self.battle_system.enemies if not e.is_alive() and not getattr(e, "spared", False))

        if spared_count > 0 and defeated_count > 0:
            parts.append(f"Enemies: {spared_count} spared, {defeated_count} defeated")
        elif spared_count > 0:
            parts.append(f"Enemies: {spared_count} spared")
        elif defeated_count > 0:
            parts.append(f"Enemies: {defeated_count} defeated")

        # Party status
        alive_count = sum(1 for p in self.battle_system.players if p.is_alive())
        total_count = len(self.battle_system.players)
        if alive_count < total_count:
            parts.append(f"Party: {alive_count}/{total_count} standing")

        if parts:
            return " | ".join(parts)
        return ""

    def _finalize_outcome(self, outcome: str) -> None:
        """Record outcome once and update flags/triggers via rewards handler."""
        self.rewards_handler.finalize_outcome(outcome)
        self._victory_spared = self.rewards_handler._victory_spared
        self._outcome_finalized = self.rewards_handler._outcome_finalized

    def _track_battle_achievements(self, outcome: str) -> None:
        """Backward-compatible wrapper.

        Achievements are handled inside the rewards handler; this method remains
        for external callers but simply delegates.
        """
        self.rewards_handler._track_battle_achievements(outcome)

    def _record_enemy_encounters(self) -> None:
        """Backward-compatible no-op.

        Encounter recording now happens during initialization via `BattleInitializer`.
        """
        return

    def _record_enemy_defeats(self) -> None:
        """Backward-compatible wrapper around rewards handler defeat recording."""
        # Defeat recording is performed inside `BattleRewardsHandler.finalize_outcome`.
        return

    def _determine_ending(self) -> str:
        """Determine which ending to show based on world flags using data-driven conditions."""
        from core.endings import determine_ending
        return determine_ending(self.world)

    def _transition_to_ending(self) -> None:
        """Transition to the ending scene after final boss victory."""
        ending_id = self._determine_ending()

        # Set ending metadata flags
        self.world.set_flag("ending_last_id", ending_id)
        self.world.set_flag("ending_good_unlocked", ending_id == "good")
        self.world.set_flag("ending_neutral_unlocked", ending_id == "neutral")
        self.world.set_flag("ending_bad_unlocked", ending_id == "bad")

        # Create and transition to ending scene
        from .ending_scene import EndingScene

        save_manager = self.get_manager_attr(
            "save_manager", "_transition_to_ending"
        )
        save_slot = self.manager.save_slot if self.manager else 1

        ending_scene = EndingScene(
            self.manager,
            self.world,
            self.player,
            ending_id,
            scale=self.scale,
            assets=self.assets,
            save_manager=save_manager,
            save_slot=save_slot
        )

        self.manager.replace(ending_scene)

    def _return_to_title_screen(self) -> None:
        """Return to the title screen after defeat so player can continue from last save."""
        from .title_scene import TitleScene

        save_manager = self.get_manager_attr(
            "save_manager", "_return_to_title_screen"
        )

        # Reset all trigger fired states so battles can be re-encountered
        # when the player continues or starts a new game
        for map_obj in self.world.maps.values():
            for trigger in map_obj.triggers:
                trigger.fired = False

        # Reset overworld enemy defeated states so they respawn
        for map_id in self.world.map_overworld_enemies:
            for enemy in self.world.get_map_overworld_enemies(map_id):
                enemy.defeated = False

        title_scene = TitleScene(
            self.manager,
            save_manager=save_manager,
            scale=self.scale,
            assets=self.assets,
        )

        # Clear the scene stack and replace with title screen
        while len(self.manager.stack) > 1:
            self.manager.stack.pop()
        self.manager.replace(title_scene)

    def _apply_rewards(self) -> bool:
        """Grant encounter rewards (items, flags, EXP, gold)."""
        result = self.rewards_handler.apply_rewards()
        self._pending_move_learns = self.rewards_handler._pending_move_learns
        return result

    def _check_new_move_for_level(self, entity, level: int) -> Optional[Move]:
        """Check if entity can learn a new move at this level via rewards handler."""
        return self.rewards_handler._check_new_move_for_level(entity, level)

    def _trigger_next_move_learn(self) -> None:
        """Trigger the move learning scene for the next pending move."""
        self.rewards_handler.trigger_next_move_learn()

    # _draw_party_hud now in BattleHudMixin

    def _draw_background(self, surface: pygame.Surface, shake_offset: Tuple[int, int] = (0, 0)) -> None:
        """
        Draw the battle background.

        Priority for background rendering:
        1. Use backdrop sprite if available (from encounter or biome mapping)
        2. Fall back to biome-specific gradient
        3. Fall back to default dark gradient

        Also applies:
        - Weather/time tint overlay
        - Screen shake offset

        Args:
            surface: The surface to draw on
            shake_offset: (x, y) offset for screen shake effect
        """
        width, height = surface.get_size()
        shake_x, shake_y = shake_offset

        # Determine the backdrop to use
        backdrop_id = self._get_backdrop_id()
        biome = self._get_biome()

        # Cache key to detect when we need to regenerate the background
        cache_key = (backdrop_id, biome, width, height)

        if self._bg_surface is None or getattr(self, '_bg_cache_key', None) != cache_key:
            self._bg_surface = pygame.Surface((width, height))
            self._bg_cache_key = cache_key

            backdrop_loaded = False

            # Try to load backdrop image
            if backdrop_id:
                try:
                    # Get the backdrop image scaled to screen size
                    backdrop = self.assets.get_image(backdrop_id, (width // self.scale, height // self.scale))
                    if backdrop:
                        # Scale to fill screen
                        scaled_backdrop = pygame.transform.scale(backdrop, (width, height))
                        self._bg_surface.blit(scaled_backdrop, (0, 0))
                        backdrop_loaded = True
                except Exception as e:
                    log_warning(f"Failed to load backdrop '{backdrop_id}': {e}")
                    backdrop_loaded = False

            # Fallback to gradient if no backdrop loaded
            if not backdrop_loaded:
                # Use biome-specific gradient if available
                if biome and biome in BIOME_GRADIENTS:
                    top_color, bottom_color = BIOME_GRADIENTS[biome]
                else:
                    top_color = Colors.BG_DARK
                    bottom_color = Colors.BG_MAIN

                Gradients.vertical(self._bg_surface, top_color, bottom_color)

                # Add subtle atmospheric grid pattern
                grid_surface = pygame.Surface((width, height), pygame.SRCALPHA)
                grid_alpha = 8  # Very subtle
                grid_color = (255, 255, 255, grid_alpha)

                for x in range(0, width, 40):
                    pygame.draw.line(grid_surface, grid_color, (x, 0), (x, height))
                for y in range(0, height, 40):
                    pygame.draw.line(grid_surface, grid_color, (0, y), (width, y))

                self._bg_surface.blit(grid_surface, (0, 0))

        # Draw the cached background with shake offset
        surface.blit(self._bg_surface, (shake_x, shake_y))

        # Apply weather tint overlay if weather system is available
        self._draw_weather_overlay(surface, width, height)

    def _draw_weather_overlay(self, surface: pygame.Surface, width: int, height: int) -> None:
        """Apply weather-based tint overlay to the battle background."""
        if not self.world:
            return

        weather_system = getattr(self.world, 'weather_system', None)
        if not weather_system:
            return

        current_weather = getattr(weather_system, 'current_weather', None)
        if not current_weather:
            return

        # Get the weather tint
        tint = WEATHER_TINTS.get(current_weather)
        if not tint or len(tint) < 4 or tint[3] <= 0:
            return  # No tint or fully transparent

        # Create and apply the overlay
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill(tint)
        surface.blit(overlay, (0, 0))

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the battle scene."""
        width, height = surface.get_size()

        # Define hp_font for use throughout draw method
        # Use SIZE_BODY (20) instead of SIZE_SMALL (16) for better readability
        hp_font = self.assets.get_font(size=Fonts.SIZE_BODY)

        # Apply screen shake
        shake_x, shake_y = 0, 0
        if self.shake_intensity > 0:
            shake_x = random.randint(-int(self.shake_intensity), int(self.shake_intensity))
            shake_y = random.randint(-int(self.shake_intensity), int(self.shake_intensity))

        # Draw background first (with screen shake applied)
        self._draw_background(surface, shake_offset=(shake_x, shake_y))

        # Draw enemies with coordination effects and phase badges
        self._draw_enemies(surface, hp_font)
        self._draw_enemy_hud(surface, hp_font)

        # --- Draw allies / party members ---
        ally_base_x, ally_y = self._get_ally_base_position()
        ally_spacing = self._get_ally_spacing()

        alive_allies = self._alive_allies()
        selected_ally_id = None
        if self.waiting_for_target and self.target_side == "ally" and alive_allies:
            selected = alive_allies[self.target_index % len(alive_allies)]
            selected_ally_id = selected.entity.entity_id
        active_actor = self._current_actor() if self.battle_system.state == BattleState.PLAYER_CHOOSE else None
        active_actor_id = active_actor.entity.entity_id if active_actor else None

        for idx, ally in enumerate(alive_allies):
            ally_surface = self.assets.get_image(
                ally.entity.sprite_id,
                (self.sprite_size, self.sprite_size)
            )
            # Apply colorkey to remove black background from battle sprites
            ally_surface.set_colorkey((0, 0, 0))
            ally_x = ally_base_x + idx * ally_spacing
            surface.blit(ally_surface, (ally_x, ally_y))

            # Ally selection or active highlight
            if selected_ally_id and ally.entity.entity_id == selected_ally_id:
                highlight_rect = pygame.Rect(
                    ally_x - 4,
                    ally_y - 4,
                    self.draw_size + 8,
                    self.draw_size + 8
                )
                pygame.draw.rect(surface, (255, 255, 0), highlight_rect, 2)
            elif active_actor_id and ally.entity.entity_id == active_actor_id:
                active_rect = pygame.Rect(
                    ally_x - 6,
                    ally_y - 6,
                    self.draw_size + 12,
                    self.draw_size + 12
                )
                sp_color = Colors.get_sp_color()
                pygame.draw.rect(surface, sp_color, active_rect, 2)

            # Ally HP bar + status icons
            if ally.stats:
                bar_height = 6
                bar_y = ally_y - 12
                # Draw ally name above sprite
                if hp_font:
                    name_surf = hp_font.render(ally.entity.name, True, (255, 255, 255))
                    name_shadow = hp_font.render(ally.entity.name, True, (0, 0, 0))
                    name_x = ally_x + (self.draw_size - name_surf.get_width()) // 2
                    name_padding = 4
                    hp_padding = 4

                    # Precompute positions so name, HP, and bar never overlap
                    hp_text = f"{ally.stats.hp}/{ally.stats.max_hp}"
                    hp_surf = hp_font.render(hp_text, True, (255, 255, 255))
                    hp_shadow = hp_font.render(hp_text, True, (0, 0, 0))
                    hp_x = ally_x + (self.draw_size - hp_surf.get_width()) // 2

                    hp_box_height = hp_surf.get_height() + hp_padding * 2
                    name_box_height = name_surf.get_height() + name_padding * 2
                    hp_y = bar_y - hp_box_height - Layout.ELEMENT_GAP_SMALL
                    name_y = hp_y - name_box_height - Layout.ELEMENT_GAP_SMALL

                    # Draw semi-transparent name tag background matching weather/time styling
                    name_bg_rect = pygame.Rect(
                        name_x - name_padding,
                        name_y - name_padding,
                        name_surf.get_width() + name_padding * 2,
                        name_surf.get_height() + name_padding * 2
                    )
                    from engine.world.overworld_renderer import draw_rounded_panel
                    PANEL_BG = (20, 25, 40, 180)
                    draw_rounded_panel(
                        surface,
                        name_bg_rect,
                        PANEL_BG,
                        Colors.BORDER,
                        border_width=Layout.BORDER_WIDTH_THIN,
                        radius=Layout.CORNER_RADIUS_SMALL
                    )

                    surface.blit(name_shadow, (name_x + 1, name_y + 1))
                    surface.blit(name_surf, (name_x, name_y))

                    # Draw HP numbers below name with spacing from bar
                    hp_bg_rect = pygame.Rect(
                        hp_x - hp_padding,
                        hp_y - hp_padding,
                        hp_surf.get_width() + hp_padding * 2,
                        hp_surf.get_height() + hp_padding * 2
                    )
                    from engine.world.overworld_renderer import draw_rounded_panel
                    PANEL_BG = (20, 25, 40, 180)
                    draw_rounded_panel(
                        surface,
                        hp_bg_rect,
                        PANEL_BG,
                        Colors.BORDER,
                        border_width=Layout.BORDER_WIDTH_THIN,
                        radius=Layout.CORNER_RADIUS_SMALL
                    )

                    surface.blit(hp_shadow, (hp_x + 1, hp_y + 1))
                    surface.blit(hp_surf, (hp_x, hp_y))

                # Draw HP bar (small, no text)
                draw_hp_bar(
                    surface,
                    ally_x,
                    bar_y,
                    self.draw_size,
                    bar_height,
                    ally.stats.hp,
                    ally.stats.max_hp,
                    "",
                    font=hp_font,
                    show_text=False,
                )
                icons = self._collect_status_icons(ally.stats.status_effects)
                if icons:
                    draw_status_icons(
                        surface,
                        icons,
                        (ally_x, ally_y + self.draw_size + 4)
                    )

        # --- Party HUD (player + party members) ---
        self._draw_party_hud(surface, hp_font)

        # --- Calculate UI positions first to avoid race conditions ---
        # Calculate message box position BEFORE drawing menus so menu can use correct position
        width, height = surface.get_size()
        if hasattr(self, 'combat_log') and self.combat_log:
            message_box_height = self.combat_log.expanded_height if self.combat_log.expanded else self.combat_log.collapsed_height
        else:
            message_box_height = self.message_box.height
        calculated_message_box_pos = self._get_message_box_position(
            screen_height=height,
            message_box_height=message_box_height
        )

        # --- Draw UI elements ---
        self._draw_menus(surface, hp_font, message_box_y=calculated_message_box_pos[1])
        self._draw_message_box(surface, hp_font, precalculated_position=calculated_message_box_pos)
        self._draw_hotbar(surface, hp_font)
        self._draw_auto_battle_indicator(surface, hp_font)

        # --- Draw animations and effects (on top of everything) ---
        self._draw_animations(surface)
        self._draw_damage_numbers(surface)
        self._draw_combo_flash(surface)
        self._draw_coordinated_tactic_flash(surface)
        self._draw_phase_transition_flash(surface)
        self._draw_ai_debug_overlay(surface, hp_font)
        self._draw_ai_notification(surface, hp_font)

    def _draw_enemies(self, surface: pygame.Surface, font=None) -> None:
        """Draw all enemy sprites with coordination effects and target highlighting."""
        enemy_x, enemy_y = self._get_enemy_base_position()
        alive_index = 0
        alive_enemies = self._alive_enemies()

        for enemy in self.battle_system.enemies:
            if enemy.is_alive():
                # Draw shadow
                shadow_rect = pygame.Rect(enemy_x + 10, enemy_y + self.sprite_size - 6, self.sprite_size - 20, 8)
                s = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
                pygame.draw.ellipse(s, (0, 0, 0, 100), (0, 0, shadow_rect.width, shadow_rect.height))
                surface.blit(s, shadow_rect.topleft)

                # Draw coordinating enemy indicator (blue glow/outline)
                if enemy.coordinated_action:
                    glow_rect = pygame.Rect(
                        enemy_x - 4,
                        enemy_y - 4,
                        self.sprite_size + 8,
                        self.sprite_size + 8
                    )
                    glow_surf = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
                    # Draw blue glow
                    for i in range(3):
                        alpha = 100 - (i * 30)
                        pygame.draw.rect(
                            glow_surf,
                            (100, 150, 255, alpha),
                            pygame.Rect(i, i, glow_rect.width - i*2, glow_rect.height - i*2),
                            2
                        )
                    surface.blit(glow_surf, glow_rect.topleft)

                # Draw sprite
                enemy_surface = self.assets.get_image(
                    enemy.entity.sprite_id,
                    (self.sprite_size, self.sprite_size)
                )
                # Apply colorkey to remove black background from battle sprites
                enemy_surface.set_colorkey((0, 0, 0))
                surface.blit(enemy_surface, (enemy_x, enemy_y))

                # Enemy target highlight
                if self.waiting_for_target and self.target_side == "enemy":
                    if alive_index == (self.target_index % len(alive_enemies) if alive_enemies else 0):
                        self._draw_target_cursor(
                            surface, enemy_x + self.sprite_size // 2, enemy_y
                        )

                enemy_x += self._get_enemy_spacing()
                alive_index += 1

    # _draw_enemy_hud now in BattleHudMixin

    # _draw_menus now in BattleHudMixin

    # _draw_message_box now in BattleHudMixin

    # _draw_hotbar now in BattleHudMixin

    # Animation drawing methods (_draw_animations, _draw_*_animation, _draw_damage_numbers,
    # _draw_combo_flash, _draw_coordinated_tactic_flash, _draw_phase_transition_flash,
    # _draw_ai_debug_overlay, _draw_ai_notification) now in BattleAnimationsMixin

    # Animation effect methods (_update_animation_effects, trigger_screen_shake,
    # add_damage_number, trigger_combo_flash, trigger_coordinated_tactic_flash,
    # trigger_phase_transition_flash) now in BattleAnimationsMixin
