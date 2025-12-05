"""Main game class and pygame loop."""

import os
from datetime import datetime
from typing import Any, Dict, List, Optional, TYPE_CHECKING

import pygame

from .scene import SceneManager
from core.logging_utils import log_warning, log_error
from .world_scene import WorldScene
from .name_entry_scene import NameEntryScene
from .title_scene import TitleScene
from .options_scene import OptionsScene
from .class_selection_scene import ClassSelectionScene, SubclassSelectionScene
from .config_loader import load_config
from .event_bus import EventBus
from core.constants import DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT
from core.save_load import SaveManager
from core.items import load_items_from_json, Item
from core.time_system import DayNightCycle
from core.weather import WeatherSystem
from core.encounters import create_encounter_from_data
from core.mod_loader import ModLoader
from core.replay import ReplayRecorder
from .input_manager import get_input_manager
from .player_factory import PlayerFactory
from .save_coordinator import SaveCoordinator

if TYPE_CHECKING:
    from core.dialogue import DialogueTree
    from core.quests import QuestManager
    from core.achievements import AchievementManager

from core.data_loader import load_npc_schedules, warm_data_caches
from core.loaders import build_bestiary_metadata
from core.tutorial_system import TipTrigger
from core.time_system import TimeOfDay
from engine.ui.toast import ToastNotification
from core.constants import NPC_SCHEDULES_JSON
from .game_loaders import (
    create_day_night_cycle,
    create_tutorial_manager,
    create_weather_system,
    load_achievement_manager_safe,
    load_arena_manager,
    load_brain_teaser_manager,
    load_challenge_dungeon_manager,
    load_dialogue,
    load_encounters_data,
    load_fishing_system,
    load_gambling_manager,
    load_hint_manager,
    load_items_db,
    load_party_prototypes,
    load_quest_manager_safe,
    load_post_game_manager,
    load_secret_boss_manager,
    load_world,
)


class RpgGame:
    """Main game class managing pygame and game state."""

    def __init__(self):
        self._pygame_initialized = False
        self._init_error: Optional[str] = None

        # Initialize all attributes to None/defaults for cleanup safety
        self.config: Dict[str, Any] = {}
        self.screen: Optional[pygame.Surface] = None
        self.clock: Optional[pygame.time.Clock] = None
        self.running = False
        self.event_bus: Optional[EventBus] = None
        self.world = None
        self.player = None
        self.save_manager = None
        self.save_coordinator = None
        self.quest_manager = None
        self.day_night_cycle = None
        self.weather_system = None
        self.achievement_manager = None
        self.party_prototypes = None
        self.schedule_manager = None
        self.tutorial_manager = None
        self.fishing_system = None
        self.brain_teaser_manager = None
        self.gambling_manager = None
        self.arena_manager = None
        self.challenge_dungeon_manager = None
        self.post_game_manager = None
        self.secret_boss_manager = None
        self.hint_manager = None
        self.scene_manager = None
        self._last_time_period: Optional[TimeOfDay] = None
        self._toast_notifications: List[ToastNotification] = []

        # Stage 1: Initialize pygame
        try:
            pygame.init()
            self._pygame_initialized = True
        except pygame.error as e:
            self._init_error = f"Failed to initialize pygame: {e}"
            log_error(self._init_error)
            raise RuntimeError(self._init_error) from e
        except Exception as e:
            self._init_error = f"Unexpected error initializing pygame: {e}"
            log_error(self._init_error)
            raise RuntimeError(self._init_error) from e

        # Stage 2: Load configuration
        try:
            self.config = self._load_config()
        except FileNotFoundError as e:
            log_warning(f"Config file not found, using defaults: {e}")
            self.config = {}
        except (ValueError, KeyError) as e:
            log_warning(f"Invalid config format, using defaults: {e}")
            self.config = {}
        except Exception as e:
            log_warning(f"Unexpected error loading config, using defaults: {e}")
            self.config = {}

        # Stage 3: Initialize display
        try:
            self._init_display()
        except pygame.error as e:
            self._cleanup_on_failure()
            self._init_error = f"Failed to initialize display: {e}"
            log_error(self._init_error)
            raise RuntimeError(self._init_error) from e
        except Exception as e:
            self._cleanup_on_failure()
            self._init_error = f"Unexpected error initializing display: {e}"
            log_error(self._init_error)
            raise RuntimeError(self._init_error) from e

        # Stage 4: Initialize input and mods (non-critical)
        try:
            self._init_input_and_mods()
        except Exception as e:
            log_warning(f"Failed to initialize input/mods, continuing with defaults: {e}")
            self.input_manager = get_input_manager()
            self.mods_enabled = False
            self.mod_loader = ModLoader(enabled=False)

        # Stage 5: Initialize replay system (non-critical)
        try:
            self._init_replay()
        except Exception as e:
            log_warning(f"Failed to initialize replay system: {e}")
            self.replay_recorder = ReplayRecorder(enabled=False, metadata={})
            self.replay_output_path = None

        # Stage 6: Initialize event bus
        try:
            self.event_bus = EventBus()
        except Exception as e:
            self._cleanup_on_failure()
            self._init_error = f"Failed to create event bus: {e}"
            log_error(self._init_error)
            raise RuntimeError(self._init_error) from e

        # Stage 7: Load domain data (world, items, etc.)
        try:
            self._load_domain_data()
        except Exception as e:
            self._cleanup_on_failure()
            self._init_error = f"Failed to load domain data: {e}"
            log_error(self._init_error)
            raise RuntimeError(self._init_error) from e

        # Stage 8: Warm data caches (non-critical)
        try:
            warm_data_caches()
        except Exception as e:
            log_warning(f"Failed to warm data caches: {e}")

        # Stage 9: Initialize save system
        try:
            self.save_manager = SaveManager()
            self.save_coordinator = SaveCoordinator(self, self.save_manager)
        except Exception as e:
            self._cleanup_on_failure()
            self._init_error = f"Failed to initialize save system: {e}"
            log_error(self._init_error)
            raise RuntimeError(self._init_error) from e

        # Stage 10: Initialize quest manager (non-critical)
        try:
            self.quest_manager = load_quest_manager_safe(self.world.flags)
        except Exception as e:
            log_warning(f"Failed to load quest manager: {e}")
            self.quest_manager = None

        # Wire up quest manager to listen to flag changes
        def on_flag_change(flag_name: str, flag_value: bool) -> None:
            """Callback for flag changes to check flag-based quest objectives."""
            if flag_value and self.quest_manager is not None:  # Only check when flag is set (truthy) and manager exists
                self.quest_manager.check_flag_objectives(self.world.flags)
        self.world.set_flag_change_callback(on_flag_change)

        # Stage 11: Initialize game subsystems (non-critical - use safe defaults)
        try:
            self.day_night_cycle = create_day_night_cycle(self.config)
        except Exception as e:
            log_warning(f"Failed to create day/night cycle: {e}")
            self.day_night_cycle = None

        try:
            self.weather_system = create_weather_system(self.config)
        except Exception as e:
            log_warning(f"Failed to create weather system: {e}")
            self.weather_system = None

        try:
            self.achievement_manager = load_achievement_manager_safe(self.event_bus)
        except Exception as e:
            log_warning(f"Failed to load achievement manager: {e}")
            self.achievement_manager = None

        try:
            self.party_prototypes = load_party_prototypes(self.items_db)
        except Exception as e:
            log_warning(f"Failed to load party prototypes: {e}")
            self.party_prototypes = {}

        try:
            self.schedule_manager = load_npc_schedules(NPC_SCHEDULES_JSON)
        except Exception as e:
            log_warning(f"Failed to load NPC schedules: {e}")
            self.schedule_manager = None

        try:
            self.tutorial_manager = create_tutorial_manager()
        except Exception as e:
            log_warning(f"Failed to create tutorial manager: {e}")
            self.tutorial_manager = None

        try:
            self.fishing_system = load_fishing_system()
        except Exception as e:
            log_warning(f"Failed to load fishing system: {e}")
            self.fishing_system = None

        try:
            self.brain_teaser_manager = load_brain_teaser_manager()
        except Exception as e:
            log_warning(f"Failed to load brain teaser manager: {e}")
            self.brain_teaser_manager = None

        try:
            self.gambling_manager = load_gambling_manager()
        except Exception as e:
            log_warning(f"Failed to load gambling manager: {e}")
            self.gambling_manager = None

        try:
            self.arena_manager = load_arena_manager()
        except Exception as e:
            log_warning(f"Failed to load arena manager: {e}")
            self.arena_manager = None

        try:
            self.challenge_dungeon_manager = load_challenge_dungeon_manager()
        except Exception as e:
            log_warning(f"Failed to load challenge dungeon manager: {e}")
            self.challenge_dungeon_manager = None

        try:
            self.post_game_manager = load_post_game_manager()
        except Exception as e:
            log_warning(f"Failed to load post-game manager: {e}")
            self.post_game_manager = None

        try:
            self.secret_boss_manager = load_secret_boss_manager()
        except Exception as e:
            log_warning(f"Failed to load secret boss manager: {e}")
            self.secret_boss_manager = None

        try:
            self.hint_manager = load_hint_manager()
        except Exception as e:
            log_warning(f"Failed to load hint manager: {e}")
            self.hint_manager = None

        # Stage 12: Build scene manager (critical)
        try:
            self.scene_manager = self._build_scene_manager()
        except Exception as e:
            self._cleanup_on_failure()
            self._init_error = f"Failed to build scene manager: {e}"
            log_error(self._init_error)
            raise RuntimeError(self._init_error) from e

    def _cleanup_on_failure(self) -> None:
        """Clean up resources if initialization fails."""
        if self._pygame_initialized:
            try:
                pygame.quit()
            except Exception:
                pass  # Ignore cleanup errors
        self._pygame_initialized = False

    def _load_config(self) -> Dict[str, Any]:
        """Load game configuration from JSON."""
        return load_config()

    def _init_display(self) -> None:
        """Initialize display and timing."""
        self.tile_size = self.config.get("tile_size", 32)
        self.sprite_size = self.config.get("sprite_size", 32)
        self.scale = max(1, int(self.config.get("scale", 2)))
        self.save_slot = max(1, int(self.config.get("save_slot", 1)))
        window_w = self.config.get("window_width", DEFAULT_WINDOW_WIDTH)
        window_h = self.config.get("window_height", DEFAULT_WINDOW_HEIGHT)

        self.screen = pygame.display.set_mode((window_w, window_h))
        pygame.display.set_caption(self.config.get("window_title", "JRPG Adventure"))
        self.clock = pygame.time.Clock()
        self.running = True

    def _init_input_and_mods(self) -> None:
        """Initialize input manager and mod loader."""
        self.input_manager = get_input_manager()
        self.mods_enabled = bool(self.config.get("mods_enabled", True))
        self.mod_loader = ModLoader(enabled=self.mods_enabled)
        self.mod_loader.discover_mods()

    def _init_replay(self) -> None:
        """Configure replay recording."""
        record_replay = bool(
            self.config.get("replay_record", False)
            or str(os.environ.get("REPLAY_RECORD", "")).lower() in ("1", "true", "yes", "on")
        )
        self.replay_output_path = os.environ.get("REPLAY_OUTPUT")
        self.replay_recorder = ReplayRecorder(enabled=record_replay, metadata={"save_slot": self.save_slot})

    def _load_domain_data(self) -> None:
        """Load world, items, encounters, and player."""
        self.world = load_world(self.config)
        if "gold" not in self.world.flags:
            self.world.set_flag("gold", self.config.get("starting_gold", 20))
        self.dialogue_tree = load_dialogue()
        self.items_db = load_items_db(self.mod_loader, self.mods_enabled)
        self.encounters_data = load_encounters_data(self.mod_loader, self.mods_enabled)
        self.bestiary_metadata = build_bestiary_metadata(self.encounters_data or {})
        self.player_factory = PlayerFactory(
            self.config,
            items_db=self.items_db,
            encounters_data=self.encounters_data,
            bestiary_metadata=self.bestiary_metadata,
        )
        self.player = self.player_factory.create_default_player()

    def _build_scene_manager(self) -> SceneManager:
        """Create the initial scene manager with all systems attached."""
        initial_scene = TitleScene(
            manager=None,
            save_manager=self.save_manager,
            scale=self.scale
        )
        scene_manager = SceneManager(
            initial_scene,
            save_manager=self.save_manager,
            save_slot=self.save_slot,
            quest_manager=self.quest_manager,
            day_night_cycle=self.day_night_cycle,
            weather_system=self.weather_system,
            achievement_manager=self.achievement_manager,
            party_prototypes=self.party_prototypes,
            items_db=self.items_db,
            schedule_manager=self.schedule_manager,
            tutorial_manager=self.tutorial_manager,
            fishing_system=self.fishing_system,
            brain_teaser_manager=self.brain_teaser_manager,
            gambling_manager=self.gambling_manager,
            arena_manager=self.arena_manager,
            challenge_dungeon_manager=self.challenge_dungeon_manager,
            secret_boss_manager=self.secret_boss_manager,
            hint_manager=self.hint_manager,
            post_game_manager=self.post_game_manager,
            encounters_data=self.encounters_data,
            event_bus=self.event_bus,
        )
        initial_scene.manager = scene_manager
        return scene_manager

    def _take_screenshot(self) -> None:
        """Capture a screenshot and save it to the screenshots directory."""
        # Ensure screenshots directory exists
        screenshots_dir = "screenshots"
        try:
            if not os.path.exists(screenshots_dir):
                os.makedirs(screenshots_dir, exist_ok=True)
        except PermissionError as e:
            # Permission errors are system-level issues users can't fix - log only
            log_error(f"Permission denied creating screenshots directory {screenshots_dir}: {e}")
            return
        except OSError as e:
            # Other OS errors might be transient - notify user
            log_error(f"Failed to create screenshots directory {screenshots_dir}: {e}")
            toast = ToastNotification("Screenshot failed: Cannot create directory", duration=2.0, position="top-center")
            self._toast_notifications.append(toast)
            return

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        filepath = os.path.join(screenshots_dir, filename)

        try:
            pygame.image.save(self.screen, filepath)
            # Show toast notification
            toast = ToastNotification(f"Screenshot saved: {filename}", duration=2.0, position="top-center")
            self._toast_notifications.append(toast)
        except pygame.error as e:
            log_error(f"Pygame error saving screenshot to {filepath}: {e}")
            toast = ToastNotification("Screenshot failed: Pygame error", duration=2.0, position="top-center")
            self._toast_notifications.append(toast)
        except PermissionError as e:
            # Permission errors are system-level - log only, no toast
            log_error(f"Permission denied saving screenshot to {filepath}: {e}")
        except OSError as e:
            log_error(f"File system error saving screenshot to {filepath}: {e}")
            toast = ToastNotification("Screenshot failed: File system error", duration=2.0, position="top-center")
            self._toast_notifications.append(toast)
        except Exception as e:
            log_error(f"Unexpected error saving screenshot to {filepath}: {e}")
            toast = ToastNotification("Screenshot failed!", duration=2.0, position="top-center")
            self._toast_notifications.append(toast)

    def _record_replay_event(self, event: pygame.event.Event) -> None:
        """Record translated input events when replay recording is enabled."""
        if not self.replay_recorder or not getattr(self.replay_recorder, "enabled", False):
            return
        if event.type != pygame.KEYDOWN:
            return

        actions = self.input_manager.get_actions_from_event(event)
        payload: Dict[str, Any] = {"actions": actions}
        if hasattr(event, "key"):
            payload["key"] = event.key
        self.replay_recorder.record_event("input", payload)

    def _flush_replay(self) -> None:
        """Persist the replay log to disk if recording is active.

        Always cleans up the replay recorder after attempting to save,
        regardless of success or failure, to prevent resource leaks.
        """
        if not self.replay_recorder or not getattr(self.replay_recorder, "enabled", False):
            return

        target_path = self.replay_output_path or os.path.join(
            "replays",
            f"replay_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        target_dir = os.path.dirname(target_path) or "."

        try:
            os.makedirs(target_dir, exist_ok=True)
        except PermissionError as e:
            log_error(f"Permission denied creating replay directory {target_dir}: {e}")
            self._cleanup_replay_recorder()
            return
        except OSError as e:
            log_error(f"OS error creating replay directory {target_dir}: {e}")
            self._cleanup_replay_recorder()
            return
        except Exception as e:
            log_error(f"Unexpected error creating replay directory {target_dir}: {e}")
            self._cleanup_replay_recorder()
            return

        try:
            if not self.replay_recorder.save(target_path):
                log_warning(f"Replay recording failed to save to {target_path}")
        except Exception as e:
            log_error(f"Exception saving replay to {target_path}: {e}")
        finally:
            # Always clean up the recorder to prevent resource leaks
            self._cleanup_replay_recorder()

    def _cleanup_replay_recorder(self) -> None:
        """Disable and clean up the replay recorder to release resources."""
        if self.replay_recorder:
            self.replay_recorder.enabled = False
            # Clear any buffered events to free memory
            if hasattr(self.replay_recorder, 'events'):
                self.replay_recorder.events.clear()
            if hasattr(self.replay_recorder, 'clear'):
                self.replay_recorder.clear()

    def run(self) -> None:
        """Main game loop."""
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            self._update_time_systems(dt)
            if self._scene_quit_requested():
                break

            self._process_events()
            if not self.running:
                break

            self._handle_scene_transitions()
            self.scene_manager.current().update(dt)
            self._update_toasts(dt)
            self._render()

        self._flush_replay()
        pygame.quit()

    def _handle_title_selection(self, action: str) -> None:
        """Handle title screen menu selection."""
        if action == "New Game":
            # Transition to name entry scene
            name_scene = NameEntryScene(
                manager=self.scene_manager,
                scale=self.scale
            )
            self.scene_manager.replace(name_scene)

        elif action == "Continue":
            self.save_coordinator.open_load_slot_selection()

        elif action == "Options":
            options_scene = OptionsScene(
                manager=self.scene_manager,
                scale=self.scale,
                config=self.config,
            )
            self.scene_manager.push(options_scene)

        elif action == "Quit":
            self.running = False

    def _update_time_systems(self, dt: float) -> None:
        """Advance world time, schedules, and weather."""
        current_playtime = self.world.get_flag("play_time_seconds", 0.0)
        self.world.set_flag("play_time_seconds", float(current_playtime) + dt)

        if self.day_night_cycle and not self.day_night_cycle.paused:
            self.day_night_cycle.update(dt)
            current_time_period = self.day_night_cycle.get_time_of_day()
            if current_time_period != self._last_time_period:
                if self.schedule_manager:
                    self.schedule_manager.update(self.world, current_time_period)
                if self.tutorial_manager and current_time_period in (TimeOfDay.NIGHT, TimeOfDay.MIDNIGHT):
                    self.tutorial_manager.trigger_tip(TipTrigger.NIGHT_TIME_FIRST)
                self._last_time_period = current_time_period

        if self.weather_system and self.weather_system.enabled:
            screen_w, screen_h = self.screen.get_size()
            self.weather_system.update(dt, screen_w, screen_h)

    def _scene_quit_requested(self) -> bool:
        """Check if the active scene has requested the game to quit."""
        return bool(getattr(self.scene_manager, "quit_requested", False))

    def _process_events(self) -> None:
        """Process pygame events and forward to the current scene."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                continue

            translated_events = self.input_manager.translate_event(event)
            for translated_event in translated_events:
                if translated_event.type == pygame.KEYDOWN and translated_event.key == pygame.K_F12:
                    self._take_screenshot()
                    continue
                self._record_replay_event(translated_event)
                self.scene_manager.current().handle_event(translated_event)

    def _handle_scene_transitions(self) -> None:
        """Handle transitions between title, name entry, and class selection scenes."""
        current_scene = self.scene_manager.current()
        if isinstance(current_scene, TitleScene) and current_scene.selection_made:
            self._handle_title_selection(current_scene.selected_action)
            current_scene.selection_made = False
        elif isinstance(current_scene, NameEntryScene) and current_scene.name_confirmed:
            self._handle_name_confirmed(current_scene.player_name.strip())
        elif isinstance(current_scene, ClassSelectionScene) and current_scene.selection_confirmed:
            self._handle_class_selected(current_scene.player_name, current_scene.selected_class)
        elif isinstance(current_scene, SubclassSelectionScene) and current_scene.selection_confirmed:
            self._handle_subclass_selected(
                current_scene.player_name,
                current_scene.primary_class,
                current_scene.selected_subclass
            )

    def _update_toasts(self, dt: float) -> None:
        """Update transient toast notifications."""
        # Update all toasts first
        for toast in self._toast_notifications:
            toast.update(dt)
        # Remove inactive toasts in-place (reverse iteration to avoid index issues)
        for i in range(len(self._toast_notifications) - 1, -1, -1):
            if not self._toast_notifications[i].active:
                del self._toast_notifications[i]

    def _render(self) -> None:
        """Render the current scene and any overlays."""
        self.screen.fill((0, 0, 0))
        self.scene_manager.current().draw(self.screen)
        for toast in self._toast_notifications:
            toast.draw(self.screen)
        pygame.display.flip()

    def _handle_name_confirmed(self, player_name: str) -> None:
        """Handle name confirmation: transition to class selection."""
        # Store player name temporarily (will be applied after class selection)
        validated_name = player_name if player_name else "Hero"

        # Transition to class selection scene
        class_scene = ClassSelectionScene(
            manager=self.scene_manager,
            player_name=validated_name,
            scale=self.scale
        )
        self.scene_manager.replace(class_scene)

    def _handle_class_selected(self, player_name: str, selected_class: str) -> None:
        """Handle class selection: transition to subclass selection."""
        # Transition to subclass selection scene
        subclass_scene = SubclassSelectionScene(
            manager=self.scene_manager,
            player_name=player_name,
            primary_class=selected_class,
            scale=self.scale
        )
        self.scene_manager.replace(subclass_scene)

    def _handle_subclass_selected(self, player_name: str, primary_class: str, subclass: str) -> None:
        """Handle subclass selection: apply class stats, create player, start tutorial."""
        self.player = self.player_factory.create_with_class(player_name, primary_class, subclass)
        self.save_coordinator.save_current_slot()
        self._start_tutorial_battle()

    def _start_tutorial_battle(self) -> None:
        """Start the tutorial battle scene."""
        from .tutorial_battle_scene import TutorialBattleScene
        from .assets import AssetManager
        from core.combat import BattleSystem, load_skills_from_json

        # Create encounter using shared factory
        enemies, rewards, backdrop_id, ai_metadata = create_encounter_from_data(
            encounter_id="tutorial_battle",
            encounters_data=self.encounters_data,
            items_db=self.items_db,
        )

        # Load skills for battle
        skills = load_skills_from_json()

        # Create battle system (rigged=True makes enemy attacks miss/deal minimal damage)
        party_members = self.player.get_battle_party()
        battle_system = BattleSystem(
            players=party_members,
            enemies=enemies,
            skills=skills,
            items=self.items_db,
            debug_ai=self.config.get('debug_ai', False),
            phase_feedback=self.config.get('ai_phase_feedback', False),
            rigged=True
        )

        # Apply AI metadata from factory
        for metadata in ai_metadata:
            enemy_index = metadata["enemy_index"]
            if enemy_index < len(battle_system.enemies):
                enemy_participant = battle_system.enemies[enemy_index]
                enemy_participant.ai_profile = metadata["ai_profile"]
                computed_skills = metadata["skills"] or getattr(enemy_participant.entity, "skills", [])
                enemy_participant.skills = list(dict.fromkeys(computed_skills))
                enemy_participant.items = metadata["items"]

        # Create tutorial battle scene
        assets = AssetManager(
            scale=self.scale,
            tile_size=self.tile_size,
            sprite_size=self.sprite_size,
        )
        tutorial_scene = TutorialBattleScene(
            self.scene_manager,
            battle_system,
            self.world,
            self.player,
            scale=self.scale,
            assets=assets,
            rewards=rewards,
            items_db=self.items_db,
            backdrop_id=backdrop_id,
            encounter_id="tutorial_battle"
        )

        # Replace name entry scene with tutorial battle
        self.scene_manager.replace(tutorial_scene)
