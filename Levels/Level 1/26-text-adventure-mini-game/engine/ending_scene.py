"""Ending scene for displaying game completion and statistics with cutscene effects."""

import json
import math
import os
import random
from typing import Optional, Dict, List, TYPE_CHECKING

import pygame

from .scene import Scene
from .assets import AssetManager
from .config_loader import load_config
from core.constants import DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT
from core.world import World
from core.entities import Player
from core.logging_utils import log_warning, log_error, log_info
from core.save.context import SaveContext

if TYPE_CHECKING:
    from .scene import SceneManager


class EndingScene(Scene):
    """Displays the ending with cinematic cutscene, credits, and detailed game statistics."""

    # Color palettes for each ending type
    ENDING_THEMES = {
        "good": {
            "bg_top": (20, 45, 80),
            "bg_bottom": (60, 100, 140),
            "accent": (255, 220, 100),
            "text": (255, 255, 240),
            "particle_colors": [(255, 230, 150), (200, 220, 255), (255, 200, 100)],
        },
        "bad": {
            "bg_top": (40, 10, 15),
            "bg_bottom": (80, 25, 35),
            "accent": (200, 50, 50),
            "text": (255, 200, 200),
            "particle_colors": [(200, 50, 50), (150, 30, 30), (100, 20, 20)],
        },
        "neutral": {
            "bg_top": (30, 35, 50),
            "bg_bottom": (60, 70, 90),
            "accent": (180, 180, 200),
            "text": (220, 220, 230),
            "particle_colors": [(180, 180, 200), (150, 160, 180), (200, 200, 220)],
        },
    }

    # Cutscene phases
    PHASE_FADE_IN = 0
    PHASE_TITLE = 1
    PHASE_BLURB = 2
    PHASE_STATS = 3
    PHASE_CREDITS = 4
    PHASE_NG_PLUS = 5
    PHASE_COMPLETE = 6

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
        self._autosaved = False
        self._autosave_message = ""

        # Load config for screen dimensions
        self.config = load_config()
        self.screen_width = self.config.get("window_width", DEFAULT_WINDOW_WIDTH)
        self.screen_height = self.config.get("window_height", DEFAULT_WINDOW_HEIGHT)

        # Load ending data
        self.ending_data = self._load_ending_data()

        # Cutscene state
        self.phase = self.PHASE_FADE_IN
        self.phase_timer = 0.0
        self.total_timer = 0.0
        self.fade_alpha = 255  # Start fully black
        self.text_reveal_progress = 0.0

        # Get theme colors
        self.theme = self.ENDING_THEMES.get(ending_id, self.ENDING_THEMES["neutral"])

        # Generate particles for visual effect
        self.particles = self._generate_particles(40)

        # Pre-render surfaces
        self._gradient_surface: Optional[pygame.Surface] = None

        # New Game+ menu state
        self.ng_plus_selected = 0  # 0 = New Game+, 1 = Return to Title
        self.ng_plus_available = True

        # Post-game unlock tracking
        self._newly_unlocked = []
        self._post_game_unlocks_triggered = False

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

    def _generate_particles(self, count: int) -> List[dict]:
        """Generate floating ambient particles for the ending scene."""
        particles = []
        random.seed(None)  # Use random seed for variety
        for _ in range(count):
            particles.append({
                "x": random.uniform(0, self.screen_width),
                "y": random.uniform(0, self.screen_height),
                "vx": random.uniform(-15, 15),
                "vy": random.uniform(-30, -10),
                "size": random.uniform(1, 4),
                "alpha": random.randint(60, 180),
                "color": random.choice(self.theme["particle_colors"]),
                "phase_offset": random.uniform(0, math.pi * 2),
            })
        return particles

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
        """Update scene state with cutscene progression."""
        self.total_timer += dt
        self.phase_timer += dt

        # Autosave on first update
        if not self._autosaved and self.save_manager and self.manager:
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
                if self.manager:
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

            self._autosaved = True

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

        # Update particles
        for p in self.particles:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            if p["y"] < -10:
                p["y"] = self.screen_height + 10
                p["x"] = random.uniform(0, self.screen_width)
            if p["x"] < -10:
                p["x"] = self.screen_width + 10
            elif p["x"] > self.screen_width + 10:
                p["x"] = -10

        # Phase transitions with timing
        phase_durations = {
            self.PHASE_FADE_IN: 2.0,
            self.PHASE_TITLE: 3.0,
            self.PHASE_BLURB: 4.0,
            self.PHASE_STATS: 4.0,
            self.PHASE_CREDITS: 3.0,
        }

        if self.phase in phase_durations:
            # Update fade for fade-in phase
            if self.phase == self.PHASE_FADE_IN:
                self.fade_alpha = max(0, 255 - int(self.phase_timer * 127.5))

            # Update text reveal progress
            self.text_reveal_progress = min(1.0, self.phase_timer / 1.5)

            # Auto-advance phase
            if self.phase_timer >= phase_durations[self.phase]:
                # Trigger post-game unlocks when credits complete
                if self.phase == self.PHASE_CREDITS and not self._post_game_unlocks_triggered:
                    self._trigger_post_game_unlocks()
                self._advance_phase()

    def _advance_phase(self) -> None:
        """Advance to the next cutscene phase."""
        self.phase += 1
        self.phase_timer = 0.0
        self.text_reveal_progress = 0.0

    def _trigger_post_game_unlocks(self) -> None:
        """Trigger post-game unlocks when credits finish."""
        if self._post_game_unlocks_triggered:
            return

        self._post_game_unlocks_triggered = True

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
            if self.phase < self.PHASE_NG_PLUS:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self._advance_phase()
                elif event.key == pygame.K_ESCAPE:
                    # Skip directly to NG+ menu
                    self.phase = self.PHASE_NG_PLUS
                    self.phase_timer = 0.0

            # Handle NG+ menu
            elif self.phase == self.PHASE_NG_PLUS:
                if event.key == pygame.K_UP:
                    self.ng_plus_selected = (self.ng_plus_selected - 1) % 2
                elif event.key == pygame.K_DOWN:
                    self.ng_plus_selected = (self.ng_plus_selected + 1) % 2
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self._handle_ng_plus_selection()
                elif event.key == pygame.K_ESCAPE:
                    self.ng_plus_selected = 1
                    self._handle_ng_plus_selection()

    def _handle_ng_plus_selection(self) -> None:
        """Handle New Game+ menu selection."""
        if self.ng_plus_selected == 0:
            self._start_new_game_plus()
        else:
            if self.manager:
                self.manager.quit_requested = True

    def _start_new_game_plus(self) -> None:
        """Initialize New Game+ mode."""
        if not self.save_manager:
            if self.manager:
                self.manager.quit_requested = True
            return

        try:
            ng_plus_data = self._create_ng_plus_data()
            self._save_ng_plus_state(self.save_slot, ng_plus_data)
            self._autosave_message = f"New Game+ saved to slot {self.save_slot}"
            self.world.set_flag("new_game_plus_pending", True)
            if self.manager:
                self.manager.quit_requested = True
        except Exception as e:
            log_warning(f"Failed to create New Game+ save: {e}")
            self._autosave_message = "Failed to create New Game+"

    def _create_ng_plus_data(self) -> Dict:
        """Create New Game+ save data with carried over progress."""
        current_cycle = self.world.get_flag("ng_plus_cycle")
        if not isinstance(current_cycle, int):
            current_cycle = 0
        new_cycle = current_cycle + 1

        carry_over = {
            "level": self.player.stats.level if self.player.stats else 1,
            "skills": list(getattr(self.player, "learned_moves", [])),
            "inventory": {},
            "equipment": dict(getattr(self.player, "equipment", {})),
            "endings_seen": [],
            "ng_plus_cycle": new_cycle,
            "ng_plus_stat_bonus": min(new_cycle * 5, 25),
        }

        if self.player.inventory:
            for item_id, qty in self.player.inventory.get_all_items().items():
                carry_over["inventory"][item_id] = min(qty, 10)

        for ending_type in ["good", "bad", "neutral"]:
            if self.world.get_flag(f"ending_{ending_type}_seen"):
                carry_over["endings_seen"].append(ending_type)

        return carry_over

    def _save_ng_plus_state(self, slot: int, ng_plus_data: Dict) -> None:
        """Save New Game+ state to a slot."""
        save_path = os.path.join(self.save_manager.save_dir, f"save_{slot}.json")

        bonus = ng_plus_data["ng_plus_stat_bonus"]
        ng_save = {
            "world": {
                "current_map_id": "forest_path",
                "flags": {
                    "new_game_plus": True,
                    "ng_plus_cycle": ng_plus_data["ng_plus_cycle"],
                    "ng_plus_stat_bonus": bonus,
                    **{f"ending_{e}_seen": True for e in ng_plus_data["endings_seen"]},
                }
            },
            "player": {
                "entity_id": self.player.entity_id,
                "name": self.player.name,
                "x": 7,
                "y": 7,
                "inventory": ng_plus_data["inventory"],
                "equipment": ng_plus_data["equipment"],
                "skills": ng_plus_data["skills"],
                "learned_moves": ng_plus_data["skills"],
                "stats": {
                    "max_hp": 100 + bonus * 2,
                    "hp": 100 + bonus * 2,
                    "max_sp": 30 + bonus,
                    "sp": 30 + bonus,
                    "attack": 10 + bonus,
                    "defense": 8 + bonus,
                    "magic": 8 + bonus,
                    "speed": 10 + bonus // 2,
                    "luck": 5 + bonus // 2,
                    "level": 1,
                    "exp": 0,
                    "status_effects": {}
                },
                "party": [],
                "skill_tree_progress": None,
                "player_class": getattr(self.player, "player_class", None),
                "player_subclass": getattr(self.player, "player_subclass", None)
            }
        }

        try:
            with open(save_path, 'w') as f:
                json.dump(ng_save, f, indent=2)
        except Exception as e:
            log_error(f"Failed to write New Game+ save to {save_path}: {e}")
            raise

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the ending screen with cinematic cutscene effects."""
        width, height = surface.get_size()
        center_x = width // 2

        # Draw themed gradient background
        self._draw_gradient_background(surface)

        # Draw floating particles
        self._draw_particles(surface)

        # Get fonts
        font_large = self.assets.get_font("large", 36) or pygame.font.Font(None, 36)
        font = self.assets.get_font("default", 22) or pygame.font.Font(None, 22)
        small_font = self.assets.get_font("small", 16) or pygame.font.Font(None, 16)

        y_offset = 30

        # Draw content based on current phase
        if self.phase >= self.PHASE_TITLE:
            y_offset = self._draw_title_section(surface, center_x, y_offset, font_large)

        if self.phase >= self.PHASE_BLURB:
            y_offset = self._draw_blurb_section(surface, center_x, y_offset, font)

        if self.phase >= self.PHASE_STATS:
            y_offset = self._draw_stats_section(surface, center_x, y_offset, font, small_font)

        if self.phase >= self.PHASE_CREDITS:
            y_offset = self._draw_credits_section(surface, center_x, y_offset, small_font)

        if self.phase >= self.PHASE_NG_PLUS:
            self._draw_ng_plus_menu(surface, center_x, height - 100, font, small_font)

        # Draw skip hint during cutscene
        if self.phase < self.PHASE_NG_PLUS:
            alpha = int(120 * (0.5 + 0.5 * math.sin(self.total_timer * 3)))
            hint_surf = small_font.render("Press SPACE to continue, ESC to skip", True, (150, 150, 150))
            hint_surf.set_alpha(alpha)
            surface.blit(hint_surf, (center_x - hint_surf.get_width() // 2, height - 30))

        # Draw fade overlay
        if self.fade_alpha > 0:
            fade_surf = pygame.Surface((width, height))
            fade_surf.fill((0, 0, 0))
            fade_surf.set_alpha(self.fade_alpha)
            surface.blit(fade_surf, (0, 0))

    def _draw_gradient_background(self, surface: pygame.Surface) -> None:
        """Draw a smooth vertical gradient background based on ending theme."""
        width, height = surface.get_size()

        if self._gradient_surface is None or self._gradient_surface.get_size() != (width, height):
            self._gradient_surface = pygame.Surface((width, height))
            top = self.theme["bg_top"]
            bottom = self.theme["bg_bottom"]
            for y in range(height):
                ratio = y / height
                ratio = ratio * ratio * (3 - 2 * ratio)  # Smoothstep
                r = int(top[0] + (bottom[0] - top[0]) * ratio)
                g = int(top[1] + (bottom[1] - top[1]) * ratio)
                b = int(top[2] + (bottom[2] - top[2]) * ratio)
                pygame.draw.line(self._gradient_surface, (r, g, b), (0, y), (width, y))

        surface.blit(self._gradient_surface, (0, 0))

    def _draw_particles(self, surface: pygame.Surface) -> None:
        """Draw floating ambient particles."""
        width, height = surface.get_size()
        for p in self.particles:
            x, y = int(p["x"]), int(p["y"])
            if 0 <= x < width and 0 <= y < height:
                size = int(p["size"])
                twinkle = 0.5 + 0.5 * math.sin(self.total_timer * 2 + p["phase_offset"])
                alpha = int(p["alpha"] * twinkle)
                color = (*p["color"], max(20, min(255, alpha)))

                particle_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(particle_surf, color, (size, size), size)
                surface.blit(particle_surf, (x - size, y - size))

    def _draw_title_section(self, surface: pygame.Surface, center_x: int, y: int, font) -> int:
        """Draw the ending title with effects."""
        if self.ending_data:
            title = self.ending_data.get("title", "The End")
        else:
            title = "The End"

        # Animated title with glow
        glow_intensity = 0.7 + 0.3 * math.sin(self.total_timer * 2)
        accent = self.theme["accent"]
        glow_color = (int(accent[0] * glow_intensity), int(accent[1] * glow_intensity), int(accent[2] * glow_intensity))

        # Shadow
        shadow = font.render(title, True, (20, 20, 30))
        surface.blit(shadow, (center_x - shadow.get_width() // 2 + 2, y + 2))

        # Glow
        for offset in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            glow = font.render(title, True, glow_color)
            surface.blit(glow, (center_x - glow.get_width() // 2 + offset[0], y + offset[1]))

        # Main title
        main = font.render(title, True, self.theme["text"])
        surface.blit(main, (center_x - main.get_width() // 2, y))

        return y + 50

    def _draw_blurb_section(self, surface: pygame.Surface, center_x: int, y: int, font) -> int:
        """Draw the ending blurb with word wrap."""
        if self.ending_data:
            blurb = self.ending_data.get("blurb", "")
        else:
            blurb = "Your journey has reached its conclusion."

        # Word wrap
        words = blurb.split()
        lines = []
        current_line = []
        max_width = 500

        for word in words:
            test_line = " ".join(current_line + [word])
            test_surface = font.render(test_line, True, (255, 255, 255))
            if test_surface.get_width() <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]
        if current_line:
            lines.append(" ".join(current_line))

        for line in lines:
            line_surf = font.render(line, True, self.theme["text"])
            surface.blit(line_surf, (center_x - line_surf.get_width() // 2, y))
            y += 24

        return y + 20

    def _draw_stats_section(self, surface: pygame.Surface, center_x: int, y: int, font, small_font) -> int:
        """Draw game statistics."""
        # Section title
        title = font.render("Journey Statistics", True, self.theme["accent"])
        surface.blit(title, (center_x - title.get_width() // 2, y))
        y += 30

        # Get quest stats
        quest_manager = self.get_manager_attr(
            "quest_manager", "_draw_stats_section"
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
            ng_cycle_text = f" (NG+ Cycle {ng_cycle})"

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
            stats.append(("New Game+", ng_cycle_text.strip(" ()")))

        for label, value in stats:
            stat_text = f"{label}: {value}"
            stat_surf = small_font.render(stat_text, True, self.theme["text"])
            surface.blit(stat_surf, (center_x - stat_surf.get_width() // 2, y))
            y += 20

        return y + 15

    def _draw_credits_section(self, surface: pygame.Surface, center_x: int, y: int, font) -> int:
        """Draw credits."""
        if self.ending_data:
            credits_text = self.ending_data.get("credits", "Thank you for playing!")
        else:
            credits_text = "Thank you for playing!"

        credits_surf = font.render(credits_text, True, (180, 180, 180))
        surface.blit(credits_surf, (center_x - credits_surf.get_width() // 2, y))

        return y + 30

    def _draw_ng_plus_menu(self, surface: pygame.Surface, center_x: int, y: int, font, small_font) -> None:
        """Draw the New Game+ menu."""
        # Menu background
        menu_width, menu_height = 250, 100
        menu_rect = pygame.Rect(center_x - menu_width // 2, y, menu_width, menu_height)

        bg_surf = pygame.Surface((menu_width, menu_height), pygame.SRCALPHA)
        pygame.draw.rect(bg_surf, (20, 25, 40, 200), (0, 0, menu_width, menu_height), border_radius=8)
        pygame.draw.rect(bg_surf, (*self.theme["accent"], 150), (0, 0, menu_width, menu_height), width=2, border_radius=8)
        surface.blit(bg_surf, menu_rect.topleft)

        # Menu title
        title = small_font.render("What would you like to do?", True, self.theme["text"])
        surface.blit(title, (center_x - title.get_width() // 2, y + 10))

        # Menu options
        options = ["New Game+", "Return to Title"]
        for i, option in enumerate(options):
            option_y = y + 35 + i * 28
            is_selected = i == self.ng_plus_selected

            if is_selected:
                # Highlight
                highlight_rect = pygame.Rect(center_x - 100, option_y - 2, 200, 24)
                pygame.draw.rect(surface, (*self.theme["accent"][:3], 80), highlight_rect, border_radius=4)

                # Cursor
                cursor_x = center_x - 90 + 3 * math.sin(self.total_timer * 5)
                pygame.draw.polygon(surface, self.theme["accent"], [
                    (cursor_x, option_y + 4),
                    (cursor_x + 8, option_y + 10),
                    (cursor_x, option_y + 16),
                ])

            color = self.theme["accent"] if is_selected else self.theme["text"]
            option_surf = font.render(option, True, color)
            surface.blit(option_surf, (center_x - option_surf.get_width() // 2, option_y))

        # NG+ info
        ng_cycle = self.world.get_flag("ng_plus_cycle")
        if isinstance(ng_cycle, int) and ng_cycle > 0:
            info = small_font.render(f"Current NG+ Cycle: {ng_cycle}", True, (150, 150, 150))
            surface.blit(info, (center_x - info.get_width() // 2, y + menu_height + 5))
