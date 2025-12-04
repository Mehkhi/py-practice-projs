"""Ending scene for displaying game completion and statistics with cutscene effects."""

import json
import os
from typing import Optional, Dict, List, TYPE_CHECKING

import pygame

from .scene import Scene
from .assets import AssetManager
from .config_loader import load_config
from .cutscene_controller import CutsceneController
from .ng_plus import NewGamePlusManager
from .ending_renderer import EndingRenderer
from core.constants import DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT
from core.world import World
from core.entities import Player
from core.logging_utils import log_warning, log_error, log_info
from core.save.context import SaveContext

if TYPE_CHECKING:
    from .scene import SceneManager


class EndingScene(Scene):
    """Displays the ending with cinematic cutscene, credits, and detailed game statistics.

    This scene coordinates three specialized components:
    - CutsceneController: Manages phase timing and advancement
    - NewGamePlusManager: Handles NG+ data creation and persistence
    - EndingRenderer: Handles all drawing and visual effects
    """

    def __init__(
        self,
        manager: Optional["SceneManager"],
        world: World,
        player: Player,
        ending_id: str,
        scale: int = 2,
        assets: Optional[AssetManager] = None,
        save_manager=None,
        save_slot: int = 1,
    ):
        super().__init__(manager)
        self.world = world
        self.player = player
        self.ending_id = ending_id
        self.scale = max(1, int(scale))
        self.assets = assets or AssetManager(scale=self.scale)
        self.save_manager = save_manager
        self.save_slot = max(1, int(save_slot))
        self._autosave_message = ""

        # Load config for screen dimensions
        self.config = load_config()
        self.screen_width = self.config.get("window_width", DEFAULT_WINDOW_WIDTH)
        self.screen_height = self.config.get("window_height", DEFAULT_WINDOW_HEIGHT)

        # Load ending data
        self.ending_data = self._load_ending_data()

        # Initialize specialized components
        self._init_components()

        # Post-game unlock tracking
        self._newly_unlocked = []

    def _init_components(self) -> None:
        """Initialize the specialized components for ending scene management."""
        # Get theme colors for particles
        theme = EndingRenderer.ENDING_THEMES.get(
            self.ending_id,
            EndingRenderer.ENDING_THEMES["neutral"]
        )

        # Initialize cutscene controller
        self.cutscene_controller = CutsceneController(
            screen_width=self.screen_width,
            screen_height=self.screen_height,
            particle_colors=theme["particle_colors"],
            autosave_callback=self._perform_autosave,
            post_game_unlock_callback=self._trigger_post_game_unlocks,
        )

        # Initialize NG+ manager
        self.ng_plus_manager = NewGamePlusManager(
            world=self.world,
            player=self.player,
            save_manager=self.save_manager,
        )

        # Initialize renderer
        self.renderer = EndingRenderer(
            ending_id=self.ending_id,
            assets=self.assets,
            screen_width=self.screen_width,
            screen_height=self.screen_height,
        )

    def _load_ending_data(self) -> Optional[Dict]:
        """Load ending data from JSON."""
        path = os.path.join("data", "endings.json")
        if not os.path.exists(path):
            return None
        try:
            with open(path, "r") as f:
                data = json.load(f)
                endings = data.get("endings", [])
                # Find ending by ID in the array format
                for ending in endings:
                    if ending.get("id") == self.ending_id:
                        return ending
                return None
        except Exception as e:
            log_warning(f"Failed to load ending data from {path}: {e}")
            return None

    def _get_all_ending_types(self) -> List[str]:
        """Get all ending type IDs from the endings.json data."""
        path = os.path.join("data", "endings.json")
        if not os.path.exists(path):
            return ["good", "bad", "neutral"]  # Fallback
        try:
            with open(path, "r") as f:
                data = json.load(f)
                endings = data.get("endings", [])
                return [ending.get("id") for ending in endings if ending.get("id")]
        except Exception as e:
            log_warning(f"Failed to load ending types: {e}")
            return ["good", "bad", "neutral"]  # Fallback



    def _format_time(self, seconds: float) -> str:
        """Format seconds as MM:SS."""
        if not isinstance(seconds, (int, float)):
            seconds = 0.0
        total_seconds = int(seconds)
        minutes = total_seconds // 60
        secs = total_seconds % 60
        return f"{minutes:02d}:{secs:02d}"

    def _get_flag_value(self, flag_name: str, default=0):
        """Get a flag value, handling type conversion."""
        value = self.world.get_flag(flag_name)
        if value is False or value is True:
            return 1 if value else 0
        if not isinstance(value, (int, float)):
            return default
        return value

    def _get_bool_flag(self, flag_name: str) -> bool:
        """Get a boolean flag value."""
        return bool(self.world.get_flag(flag_name))

    def update(self, dt: float) -> None:
        """Update scene state using cutscene controller."""
        # Delegate to cutscene controller for all timing and phase logic
        self.cutscene_controller.update(dt)

    def _perform_autosave(self) -> None:
        """Perform autosave of ending state."""
        if not self.save_manager or not self.manager:
            return

        # Mark ending as completed for NG+
        self.world.set_flag("game_completed", True)
        self.world.set_flag(f"ending_{self.ending_id}_seen", True)

        # Check NG+ cycle once and reuse
        ng_cycle = self.world.get_flag("ng_plus_cycle")
        is_ng_plus = isinstance(ng_cycle, int) and ng_cycle > 0

        # Mark NG+ cycle as complete if in NG+
        if is_ng_plus:
            self.world.set_flag(f"ng_plus_cycle_{ng_cycle}_complete", True)

        # Perform autosave using SaveContext
        try:
            # Build context from scene manager's registered managers
            context = SaveContext(world=self.world, player=self.player)

            # Register managers from scene manager
            for attr_name in [
                'quest_manager', 'day_night_cycle', 'achievement_manager',
                'weather_system', 'schedule_manager', 'fishing_system',
                'puzzle_manager', 'brain_teaser_manager', 'gambling_manager',
                'arena_manager', 'challenge_dungeon_manager', 'secret_boss_manager',
                'hint_manager', 'post_game_manager', 'tutorial_manager',
            ]:
                manager_obj = self.manager.get_manager(
                    attr_name, "ending_autosave"
                )
                if manager_obj is not None:
                    context.register_if_saveable(manager_obj)

            self.save_manager.save_to_slot_with_context(self.save_slot, context)
            self._autosave_message = f"Ending saved to slot {self.save_slot}"
        except Exception as e:
            log_warning(f"Failed to autosave ending state: {e}")
            self._autosave_message = "Failed to save ending"

        # Notify achievement system of game completion (separate try block)
        achievement_manager = self.get_manager_attr(
            "achievement_manager", "ending_autosave"
        )
        bus = getattr(self.manager, "event_bus", None) if self.manager else None
        if achievement_manager:
            try:
                # Notify achievements about game completion via event bus
                if bus:
                    bus.publish("game_completed", ending_id=self.ending_id)

                # Build stats dict from world flags for stat-based achievements
                # Include both canonical names and aliases for flexibility
                enemies_defeated = self._get_flag_value("enemies_defeated_total", 0)
                total_gold = self._get_flag_value("gold", 0)
                battles_won = self._get_flag_value("battles_won", 0)
                enemies_spared = self._get_flag_value("enemies_spared_total", 0)
                play_time = self._get_flag_value("play_time_seconds", 0.0)

                stats = {
                    # Primary keys
                    "enemies_defeated_total": enemies_defeated,
                    "total_gold_earned": total_gold,
                    "gold": total_gold,  # Alias
                    "battles_won": battles_won,
                    "enemies_spared_total": enemies_spared,
                    "play_time_seconds": play_time,
                    # Aliases for common achievement trigger targets
                    "total_kills": enemies_defeated,
                    "kills": enemies_defeated,
                    "gold_earned": total_gold,
                    "battles": battles_won,
                    "spared": enemies_spared,
                    "play_time": play_time,
                }

                # Try to get quest completion count if available
                quest_manager = self.get_manager_attr(
                    "quest_manager", "_notify_completion_stats"
                )
                if quest_manager:
                    completed_quests = quest_manager.get_completed_quests()
                    stats["quests_completed"] = len(completed_quests)
                    stats["total_quests_completed"] = len(completed_quests)  # Alias
                    # Count side quests separately (use getattr for safety)
                    side_quests_completed = sum(
                        1 for q in completed_quests
                        if getattr(q, 'category', None) == "side"
                    )
                    stats["side_quests_completed"] = side_quests_completed

                # Count endings seen
                endings_seen = 0
                for ending_type in self._get_all_ending_types():
                    if self.world.get_flag(f"ending_{ending_type}_seen"):
                        endings_seen += 1
                stats["endings_seen"] = endings_seen
                stats["endings_unlocked"] = endings_seen  # Alias

                # Check stat-based achievements
                achievement_manager.check_stat_achievements(stats)

                # Track NG+ cycle completion (reuse ng_cycle from above)
                if is_ng_plus and bus:
                    flag_name = f"ng_plus_cycle_{ng_cycle}_complete"
                    bus.publish("flag_set", flag_name=flag_name, flag_value=True)
            except Exception as e:
                log_warning(f"Failed to notify achievements of game completion: {e}")

    def _trigger_post_game_unlocks(self) -> None:
        """Trigger post-game unlocks when credits finish."""
        # Get post-game manager from scene manager
        post_game_manager = self.get_manager_attr(
            "post_game_manager", "_trigger_post_game_unlocks"
        )
        if not post_game_manager:
            return

        # Trigger post-game unlocks
        self._newly_unlocked = post_game_manager.on_final_boss_defeated(self.ending_id)

        # Set world flag (already done in autosave, but ensure it's set)
        self.world.set_flag("final_boss_defeated", True)
        self.world.set_flag(f"ending_{self.ending_id}_seen", True)

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle input events for cutscene progression."""
        if event.type == pygame.KEYDOWN:
            # Skip to NG+ menu phase if not already there
            if not self.cutscene_controller.is_in_ng_plus_phase():
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self.cutscene_controller.advance_phase()
                elif event.key == pygame.K_ESCAPE:
                    # Skip directly to NG+ menu
                    self.cutscene_controller.skip_to_ng_plus_menu()

            # Handle NG+ menu
            elif self.cutscene_controller.is_in_ng_plus_phase():
                if event.key == pygame.K_UP:
                    self.ng_plus_manager.handle_menu_navigation("up")
                elif event.key == pygame.K_DOWN:
                    self.ng_plus_manager.handle_menu_navigation("down")
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    should_quit, message = self.ng_plus_manager.handle_menu_selection(self.save_slot)
                    self._autosave_message = message
                    if should_quit and self.manager:
                        self.manager.quit_requested = True
                elif event.key == pygame.K_ESCAPE:
                    # Force return to title
                    if self.manager:
                        self.manager.quit_requested = True

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the ending screen using the renderer component."""
        # Draw background
        self.renderer.draw_gradient_background(surface)

        # Draw particles
        self.renderer.draw_particles(
            surface,
            self.cutscene_controller.particles,
            self.cutscene_controller.total_timer
        )

        # Get phase visibility
        visibility = self.cutscene_controller.get_phase_visibility()
        center_x = surface.get_width() // 2
        y_offset = 30

        # Draw content based on current phase
        if visibility[self.cutscene_controller.PHASE_TITLE]:
            y_offset = self.renderer.draw_title_section(
                surface,
                self.ending_data,
                self.cutscene_controller.total_timer
            )

        if visibility[self.cutscene_controller.PHASE_BLURB]:
            y_offset = self.renderer.draw_blurb_section(
                surface,
                self.ending_data,
                y_offset
            )

        if visibility[self.cutscene_controller.PHASE_STATS]:
            stats = self._get_stats_data()
            y_offset = self.renderer.draw_stats_section(
                surface,
                stats,
                y_offset
            )

        if visibility[self.cutscene_controller.PHASE_CREDITS]:
            y_offset = self.renderer.draw_credits_section(
                surface,
                self.ending_data,
                y_offset
            )

        if visibility[self.cutscene_controller.PHASE_NG_PLUS]:
            menu_options = self.ng_plus_manager.get_menu_options()
            selected = self.ng_plus_manager.selected_option
            cycle_info = self.ng_plus_manager.get_current_cycle_info()
            self.renderer.draw_ng_plus_menu(
                surface,
                menu_options,
                selected,
                self.cutscene_controller.total_timer,
                cycle_info
            )

        # Draw skip hint during cutscene
        if self.cutscene_controller.should_show_skip_hint():
            self.renderer.draw_skip_hint(
                surface,
                self.cutscene_controller.total_timer
            )

        # Draw fade overlay
        self.renderer.draw_fade_overlay(
            surface,
            self.cutscene_controller.fade_alpha
        )

    def _get_stats_data(self) -> List[tuple]:
        """Get statistics data for rendering."""
        # Get quest stats
        quest_manager = self.get_manager_attr(
            "quest_manager", "_get_stats_data"
        )
        total_quests = 0
        side_quests = 0
        if quest_manager:
            completed_quests = quest_manager.get_completed_quests()
            total_quests = len(completed_quests)
            # Use getattr for safety in case quest objects lack category attribute
            side_quests = sum(
                1 for q in completed_quests
                if getattr(q, 'category', None) == "side"
            )

        # Count endings seen dynamically
        all_ending_types = self._get_all_ending_types()
        total_endings = len(all_ending_types)
        endings_seen = 0
        for ending_type in all_ending_types:
            if self.world.get_flag(f"ending_{ending_type}_seen"):
                endings_seen += 1

        # Get NG+ cycle
        ng_cycle = self.world.get_flag("ng_plus_cycle")
        ng_cycle_text = ""
        if isinstance(ng_cycle, int) and ng_cycle > 0:
            ng_cycle_text = f"NG+ Cycle {ng_cycle}"

        stats = [
            ("Play Time", self._format_time(self._get_flag_value("play_time_seconds", 0.0))),
            ("Battles Won", str(self._get_flag_value("battles_won", 0))),
            ("Enemies Defeated", str(self._get_flag_value("enemies_defeated_total", 0))),
            ("Enemies Spared", str(self._get_flag_value("enemies_spared_total", 0))),
            ("Total Gold Earned", str(self._get_flag_value("gold", 0))),
            ("Quests Completed", f"{total_quests} (Side: {side_quests})"),
            ("Endings Seen", f"{endings_seen}/{total_endings}"),
        ]

        if ng_cycle_text:
            stats.append(("New Game+", ng_cycle_text))

        return stats
