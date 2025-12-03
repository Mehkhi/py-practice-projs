"""Interactive fishing mini-game scene."""

import random
import math
from enum import Enum, auto
from typing import Optional, TYPE_CHECKING

import pygame

from .scene import Scene
from .assets import AssetManager
from .theme import Colors, Fonts, Layout
from .ui import draw_hp_bar
from .input_manager import get_input_manager
from core.fishing import FishingSystem, FishingSpot, Fish, CaughtFish, FishRarity
from core.world import World
from core.logging_utils import log_warning
from core.tutorial_system import TipTrigger

if TYPE_CHECKING:
    from .scene import SceneManager
    from core.entities import Player


class FishingPhase(Enum):
    """Phases of the fishing mini-game."""
    WAITING = auto()      # Waiting for a bite
    HOOKING = auto()      # Fish is biting, press button quickly!
    REELING = auto()      # Mini-game: keep fish in zone
    CAUGHT = auto()       # Successfully caught
    ESCAPED = auto()      # Fish got away
    CANCELLED = auto()    # Player gave up


class FishingScene(Scene):
    """
    Interactive fishing mini-game scene.

    Phases:
    1. WAITING: Watch bobber, random wait time (3-15 seconds)
    2. HOOKING: "!" appears, player must press SPACE within 0.5 seconds
    3. REELING: Keep moving bar in "sweet spot" zone as fish struggles
    4. CAUGHT/ESCAPED: Show result
    """

    def __init__(
        self,
        manager: Optional["SceneManager"],
        fishing_system: FishingSystem,
        spot: FishingSpot,
        player: "Player",
        world: World,
        assets: Optional[AssetManager] = None,
        scale: int = 2,
    ):
        super().__init__(manager)
        self.fishing_system = fishing_system
        self.spot = spot
        self.player = player
        self.world = world
        self.scale = max(1, int(scale))
        self.assets = assets or AssetManager(scale=self.scale)
        self.input_manager = get_input_manager()

        self.phase = FishingPhase.WAITING
        self.current_fish: Optional[Fish] = None
        self.wait_timer = random.uniform(3.0, 15.0)
        self.hook_window = 0.5  # Seconds to react
        self.hook_timer = 0.0

        # Reeling mini-game state
        self.reel_position = 0.5  # 0.0 to 1.0
        self.fish_position = 0.5  # Target zone center
        self.fish_velocity = 0.0
        self.tension = 50.0  # 0-100, too high = line breaks, too low = fish escapes
        self.catch_progress = 0.0  # 0-100, reach 100 to catch
        self.sweet_spot_size = 0.15  # Size of the catch zone

        # Difficulty scaling
        self.difficulty = 1  # Set based on fish.catch_difficulty

        # Animation state
        self.bobber_offset = 0.0  # For bobber animation
        self.animation_time = 0.0

        # Equipment state
        self.rod_quality = 1
        self.has_bait = False
        self._check_equipment()

        # Result state
        self.caught_fish: Optional[CaughtFish] = None
        self.is_record = False

        # Initialize waiting phase
        self._start_waiting()

    def _check_equipment(self) -> None:
        """Check player's equipped rod and bait."""
        # Check for equipped rod (using accessory slot)
        rod_id = self.player.get_equipped_item_id("accessory")

        if rod_id:
            items_db = self.get_manager_attr("items_db", "_check_equipment")
            rod_item = items_db.get(rod_id) if items_db else None
            if rod_item and hasattr(rod_item, 'rod_quality') and rod_item.rod_quality is not None:
                self.rod_quality = rod_item.rod_quality
            else:
                self.rod_quality = 1  # Default if no rod equipped or no quality specified

        # Check for bait in inventory
        if self.player.inventory:
            # Check for fishing_bait or premium_bait items
            self.has_bait = (
                self.player.inventory.has("fishing_bait") or
                self.player.inventory.has("premium_bait")
            )

    def _start_waiting(self) -> None:
        """Initialize waiting phase."""
        self.phase = FishingPhase.WAITING
        self.wait_timer = random.uniform(3.0, 15.0)
        self.bobber_offset = 0.0
        self.animation_time = 0.0

    def _fish_bites(self) -> None:
        """A fish bites! Transition to hooking phase."""
        day_night_cycle = self.get_manager_attr(
            "day_night_cycle", "_fish_bites"
        )
        if not day_night_cycle:
            log_warning("FishingScene: No day_night_cycle available")
            time_of_day = "DAY"
        else:
            time_of_day = day_night_cycle.get_time_of_day().value

        self.current_fish = self.fishing_system.roll_for_fish(
            self.spot, time_of_day, has_bait=self.has_bait, rod_quality=self.rod_quality
        )
        if self.current_fish:
            self.phase = FishingPhase.HOOKING
            self.hook_timer = self.hook_window
            # Play bite sound
            try:
                self.assets.play_sound("bite")
            except Exception:
                pass  # Sound may not exist
        else:
            # Nothing bit, show message and restart waiting
            self._show_no_bite_message()

    def _show_no_bite_message(self) -> None:
        """Show message that no fish bit, then restart waiting."""
        # For now, just restart waiting (could show a message overlay)
        self._start_waiting()

    def _attempt_hook(self) -> bool:
        """Player pressed button during hook window. Returns True if successful."""
        if self.phase == FishingPhase.HOOKING and self.hook_timer > 0:
            self.phase = FishingPhase.REELING
            if self.current_fish:
                self.difficulty = self.current_fish.catch_difficulty
            self._init_reeling()
            return True
        return False

    def _init_reeling(self) -> None:
        """Initialize the reeling mini-game."""
        self.reel_position = 0.5
        self.fish_position = 0.5
        self.fish_velocity = 0.0
        self.tension = 50.0
        self.catch_progress = 0.0
        # Fish movement pattern based on difficulty
        # Higher difficulty = faster, more erratic movement

    def _update_reeling(self, dt: float, reeling: bool) -> None:
        """
        Update the reeling mini-game.

        - Fish moves erratically based on difficulty
        - Player moves reel_position with UP/DOWN or SPACE
        - If reel_position near fish_position: catch_progress increases
        - If too far: catch_progress decreases
        - Tension increases when reeling, decreases when not
        - Tension too high (>100): line breaks, fish escapes
        - Tension too low (<0): fish escapes
        - catch_progress reaches 100: caught!
        """
        # Fish movement: erratic pattern based on difficulty
        # Use sine waves with random frequency and phase
        difficulty_factor = self.difficulty / 10.0  # 0.1 to 1.0
        movement_speed = 0.3 + (difficulty_factor * 0.5)  # 0.3 to 0.8

        # Add some randomness to fish movement
        self.fish_velocity += random.uniform(-0.5, 0.5) * difficulty_factor * dt * 10
        self.fish_velocity = max(-2.0, min(2.0, self.fish_velocity))  # Clamp velocity

        # Update fish position
        self.fish_position += self.fish_velocity * dt * movement_speed
        self.fish_position = max(0.1, min(0.9, self.fish_position))  # Keep in bounds

        # Player reel control
        reel_speed = 1.5  # How fast the reel moves
        if reeling:
            # Reeling increases tension
            self.tension += 30.0 * dt
            # Move reel up (toward 1.0)
            self.reel_position += reel_speed * dt
        else:
            # Not reeling decreases tension
            self.tension -= 20.0 * dt
            # Reel drifts down (toward 0.0)
            self.reel_position -= 0.3 * dt

        # Clamp positions
        self.reel_position = max(0.0, min(1.0, self.reel_position))
        self.tension = max(0.0, min(100.0, self.tension))

        # Check catch progress
        distance = abs(self.reel_position - self.fish_position)
        if distance < self.sweet_spot_size:
            # In sweet spot - increase progress
            progress_rate = (1.0 - (distance / self.sweet_spot_size)) * 20.0  # Faster when closer
            self.catch_progress += progress_rate * dt
        else:
            # Too far - decrease progress
            self.catch_progress -= 10.0 * dt

        self.catch_progress = max(0.0, min(100.0, self.catch_progress))

        # Check win/lose conditions
        if self.tension >= 100.0:
            # Line broke!
            self.phase = FishingPhase.ESCAPED
            self.current_fish = None
        elif self.tension <= 0.0:
            # Fish escaped!
            self.phase = FishingPhase.ESCAPED
            self.current_fish = None
        elif self.catch_progress >= 100.0:
            # Caught!
            self._complete_catch()

    def _complete_catch(self) -> None:
        """Complete the catch and record it."""
        if not self.current_fish:
            self.phase = FishingPhase.ESCAPED
            return

        # Generate fish size
        size = self.fishing_system.generate_fish_size(self.current_fish)
        self.caught_fish = CaughtFish(fish=self.current_fish, size=size)

        # Record catch
        self.is_record = self.fishing_system.record_catch(self.caught_fish, spot_id=self.spot.spot_id)

        # Add fish item to inventory
        if self.player.inventory and self.current_fish.item_id:
            self.player.inventory.add(self.current_fish.item_id, 1)

        # Consume bait if used
        if self.has_bait and self.player.inventory:
            if self.player.inventory.has("premium_bait"):
                self.player.inventory.remove("premium_bait", 1)
            elif self.player.inventory.has("fishing_bait"):
                self.player.inventory.remove("fishing_bait", 1)

        # Track achievements via event bus
        if self.manager and getattr(self.manager, "event_bus", None):
            day_night_cycle = self.get_manager_attr(
                "day_night_cycle", "_complete_catch"
            )
            if day_night_cycle:
                time_of_day = day_night_cycle.get_time_of_day().value
            else:
                time_of_day = "DAY"

            unique_species_count = len(self.fishing_system.player_records)

            self.manager.event_bus.publish(
                "fish_caught",
                fish_id=self.current_fish.fish_id,
                rarity=self.current_fish.rarity.value,
                size_category=self.caught_fish.size_category,
                time_of_day=time_of_day,
                unique_species_count=unique_species_count,
            )

        self._trigger_fishing_tutorials()
        self.phase = FishingPhase.CAUGHT

    def _trigger_fishing_tutorials(self) -> None:
        """Trigger tutorial tips for fishing catches."""
        tutorial_manager = self.get_manager_attr(
            "tutorial_manager", "_trigger_fishing_tutorials"
        )
        if not tutorial_manager or not self.world:
            return

        if self.caught_fish and not self.world.get_flag("_tutorial_first_fish_caught", False):
            self.world.set_flag("_tutorial_first_fish_caught", True)
            tutorial_manager.trigger_tip(TipTrigger.FIRST_FISH_CAUGHT)

        if (
            self.current_fish
            and self.current_fish.rarity == FishRarity.LEGENDARY
            and not self.world.get_flag("_tutorial_first_legendary_fish", False)
        ):
            self.world.set_flag("_tutorial_first_legendary_fish", True)
            tutorial_manager.trigger_tip(TipTrigger.FIRST_LEGENDARY_FISH)

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle pygame events."""
        if self.input_manager.is_action_pressed(event, "cancel") or self.input_manager.is_action_pressed(event, "menu"):
            if self.phase in (FishingPhase.CAUGHT, FishingPhase.ESCAPED):
                self._exit()
            else:
                self.phase = FishingPhase.CANCELLED
                self._exit()
            return

        if self.phase == FishingPhase.WAITING:
            # ESC/menu to cancel, otherwise wait
            return

        if self.phase == FishingPhase.HOOKING:
            if self.input_manager.is_action_pressed(event, "interact") or self.input_manager.is_action_pressed(event, "confirm"):
                self._attempt_hook()

        elif self.phase in (FishingPhase.CAUGHT, FishingPhase.ESCAPED):
            if self.input_manager.is_action_pressed(event, "interact") or self.input_manager.is_action_pressed(event, "confirm"):
                self._exit()

    def update(self, dt: float) -> None:
        """Update scene state."""
        self.animation_time += dt

        if self.phase == FishingPhase.WAITING:
            self.wait_timer -= dt
            # Animate bobber
            self.bobber_offset = math.sin(self.animation_time * 2.0) * 2.0
            if self.wait_timer <= 0:
                self._fish_bites()

        elif self.phase == FishingPhase.HOOKING:
            self.hook_timer -= dt
            if self.hook_timer <= 0:
                # Missed the hook!
                self.phase = FishingPhase.ESCAPED
                self.current_fish = None

        elif self.phase == FishingPhase.REELING:
            reeling = (
                self.input_manager.is_action_active("interact")
                or self.input_manager.is_action_active("confirm")
                or self.input_manager.is_action_active("up")
            )
            self._update_reeling(dt, reeling)

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the fishing scene.

        WAITING:
        - Water background with bobber animation
        - "Waiting for a bite..." text
        - Bobber occasionally ripples

        HOOKING:
        - Big "!" exclamation
        - Bobber splashing
        - "Press SPACE!" prompt

        REELING:
        - Vertical bar showing fish zone and player reel position
        - Tension meter
        - Progress bar to catch
        - Fish struggling animation

        CAUGHT:
        - Fish sprite and details
        - Size, value, record status

        ESCAPED:
        - "The fish got away!" message
        """
        width, height = surface.get_size()

        # Draw water background
        water_color = (30, 60, 120)
        surface.fill(water_color)

        # Draw phase-specific content
        if self.phase == FishingPhase.WAITING:
            self._draw_waiting(surface, width, height)
        elif self.phase == FishingPhase.HOOKING:
            self._draw_hooking(surface, width, height)
        elif self.phase == FishingPhase.REELING:
            self._draw_reeling(surface, width, height)
        elif self.phase == FishingPhase.CAUGHT:
            self._draw_caught(surface, width, height)
        elif self.phase == FishingPhase.ESCAPED:
            self._draw_escaped(surface, width, height)

    def _draw_waiting(self, surface: pygame.Surface, width: int, height: int) -> None:
        """Draw waiting phase."""
        # Draw bobber
        bobber_x = width // 2
        bobber_y = height // 2 + int(self.bobber_offset)
        pygame.draw.circle(surface, Colors.WHITE, (bobber_x, bobber_y), 8)
        pygame.draw.circle(surface, Colors.BLACK, (bobber_x, bobber_y), 8, 2)

        # Draw line
        line_start_y = height // 4
        pygame.draw.line(surface, Colors.WHITE, (bobber_x, line_start_y), (bobber_x, bobber_y), 2)

        # Draw text
        font = self.assets.get_font(size=24)
        text = font.render("Waiting for a bite...", True, Colors.TEXT_PRIMARY)
        text_rect = text.get_rect(center=(width // 2, height - 60))
        surface.blit(text, text_rect)

        # Draw hint
        hint_font = self.assets.get_font(size=16)
        hint_text = hint_font.render("Press ESC to cancel", True, Colors.TEXT_SECONDARY)
        hint_rect = hint_text.get_rect(center=(width // 2, height - 30))
        surface.blit(hint_text, hint_rect)

    def _draw_hooking(self, surface: pygame.Surface, width: int, height: int) -> None:
        """Draw hooking phase."""
        # Draw large exclamation mark
        font = self.assets.get_font(size=120)
        exclamation = font.render("!", True, Colors.TEXT_ERROR)
        exclamation_rect = exclamation.get_rect(center=(width // 2, height // 2 - 40))
        surface.blit(exclamation, exclamation_rect)

        # Draw prompt
        prompt_font = self.assets.get_font(size=32)
        prompt_text = prompt_font.render("Press SPACE!", True, Colors.TEXT_HIGHLIGHT)
        prompt_rect = prompt_text.get_rect(center=(width // 2, height // 2 + 40))
        surface.blit(prompt_text, prompt_rect)

        # Draw timer
        timer_font = self.assets.get_font(size=20)
        timer_ratio = self.hook_timer / self.hook_window
        timer_text = timer_font.render(f"{self.hook_timer:.2f}", True, Colors.TEXT_SECONDARY)
        timer_rect = timer_text.get_rect(center=(width // 2, height // 2 + 80))
        surface.blit(timer_text, timer_rect)

        # Draw bobber splash effect
        bobber_x = width // 2
        bobber_y = height // 2 + 60
        for i in range(3):
            radius = 10 + i * 5
            alpha = 200 - i * 60
            splash_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(splash_surface, (*Colors.WATER, alpha), (radius, radius), radius)
            splash_rect = splash_surface.get_rect(center=(bobber_x, bobber_y))
            surface.blit(splash_surface, splash_rect)

    def _draw_reeling(self, surface: pygame.Surface, width: int, height: int) -> None:
        """Draw reeling mini-game."""
        bar_width = 40
        bar_height = 300
        bar_x = width // 2 - bar_width // 2
        bar_y = (height - bar_height) // 2

        # Draw background bar
        bar_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(surface, Colors.BAR_BG, bar_rect)
        pygame.draw.rect(surface, Colors.BORDER, bar_rect, 2)

        # Draw sweet spot zone (around fish position)
        sweet_spot_height = int(bar_height * self.sweet_spot_size)
        sweet_spot_y = bar_y + int((1.0 - self.fish_position) * bar_height) - sweet_spot_height // 2
        sweet_spot_rect = pygame.Rect(bar_x, sweet_spot_y, bar_width, sweet_spot_height)
        pygame.draw.rect(surface, (*Colors.TEXT_SUCCESS, 100), sweet_spot_rect)

        # Draw fish position indicator
        fish_y = bar_y + int((1.0 - self.fish_position) * bar_height)
        pygame.draw.circle(surface, Colors.TEXT_INFO, (bar_x + bar_width // 2, fish_y), 8)
        pygame.draw.circle(surface, Colors.BLACK, (bar_x + bar_width // 2, fish_y), 8, 2)

        # Draw reel position indicator
        reel_y = bar_y + int((1.0 - self.reel_position) * bar_height)
        pygame.draw.circle(surface, Colors.ACCENT, (bar_x + bar_width // 2, reel_y), 10)
        pygame.draw.circle(surface, Colors.BLACK, (bar_x + bar_width // 2, reel_y), 10, 2)

        # Draw tension meter (horizontal bar at bottom)
        tension_bar_width = 200
        tension_bar_height = 20
        tension_bar_x = (width - tension_bar_width) // 2
        tension_bar_y = height - 100

        tension_rect = pygame.Rect(tension_bar_x, tension_bar_y, tension_bar_width, tension_bar_height)
        pygame.draw.rect(surface, Colors.BAR_BG, tension_rect)
        pygame.draw.rect(surface, Colors.BORDER, tension_rect, 2)

        # Tension fill (green -> yellow -> red)
        tension_ratio = self.tension / 100.0
        tension_fill_width = int(tension_bar_width * tension_ratio)
        if tension_ratio < 0.5:
            tension_color = Colors.HP_HIGH
        elif tension_ratio < 0.8:
            tension_color = Colors.HP_MID
        else:
            tension_color = Colors.HP_LOW

        if tension_fill_width > 0:
            tension_fill_rect = pygame.Rect(tension_bar_x, tension_bar_y, tension_fill_width, tension_bar_height)
            pygame.draw.rect(surface, tension_color, tension_fill_rect)

        # Tension label
        tension_font = self.assets.get_font(size=16)
        tension_text = tension_font.render(f"Tension: {self.tension:.0f}", True, Colors.TEXT_PRIMARY)
        tension_text_rect = tension_text.get_rect(center=(width // 2, tension_bar_y - 20))
        surface.blit(tension_text, tension_text_rect)

        # Draw catch progress bar
        progress_bar_width = 200
        progress_bar_height = 20
        progress_bar_x = (width - progress_bar_width) // 2
        progress_bar_y = height - 60

        progress_rect = pygame.Rect(progress_bar_x, progress_bar_y, progress_bar_width, progress_bar_height)
        pygame.draw.rect(surface, Colors.BAR_BG, progress_rect)
        pygame.draw.rect(surface, Colors.BORDER, progress_rect, 2)

        progress_fill_width = int(progress_bar_width * (self.catch_progress / 100.0))
        if progress_fill_width > 0:
            progress_fill_rect = pygame.Rect(progress_bar_x, progress_bar_y, progress_fill_width, progress_bar_height)
            pygame.draw.rect(surface, Colors.TEXT_SUCCESS, progress_fill_rect)

        # Progress label
        progress_font = self.assets.get_font(size=16)
        progress_text = progress_font.render(f"Catch: {self.catch_progress:.0f}%", True, Colors.TEXT_PRIMARY)
        progress_text_rect = progress_text.get_rect(center=(width // 2, progress_bar_y - 20))
        surface.blit(progress_text, progress_text_rect)

        # Instructions
        inst_font = self.assets.get_font(size=14)
        inst_text = inst_font.render("Hold SPACE/UP to reel in", True, Colors.TEXT_SECONDARY)
        inst_rect = inst_text.get_rect(center=(width // 2, height - 30))
        surface.blit(inst_text, inst_rect)

    def _draw_caught(self, surface: pygame.Surface, width: int, height: int) -> None:
        """Draw caught fish result."""
        if not self.caught_fish:
            return

        font = self.assets.get_font(size=32)
        title_text = font.render("Caught!", True, Colors.TEXT_SUCCESS)
        title_rect = title_text.get_rect(center=(width // 2, 60))
        surface.blit(title_text, title_rect)

        # Fish name
        name_font = self.assets.get_font(size=24)
        name_text = name_font.render(self.caught_fish.fish.name, True, Colors.TEXT_PRIMARY)
        name_rect = name_text.get_rect(center=(width // 2, 120))
        surface.blit(name_text, name_rect)

        # Fish details
        details_font = self.assets.get_font(size=18)
        size_text = details_font.render(f"Size: {self.caught_fish.size:.2f} ({self.caught_fish.size_category})", True, Colors.TEXT_SECONDARY)
        size_rect = size_text.get_rect(center=(width // 2, 160))
        surface.blit(size_text, size_rect)

        value_text = details_font.render(f"Value: {self.caught_fish.value} gold", True, Colors.TEXT_HIGHLIGHT)
        value_rect = value_text.get_rect(center=(width // 2, 190))
        surface.blit(value_text, value_rect)

        if self.is_record:
            record_font = self.assets.get_font(size=20)
            record_text = record_font.render("NEW RECORD!", True, Colors.TEXT_SUCCESS)
            record_rect = record_text.get_rect(center=(width // 2, 230))
            surface.blit(record_text, record_rect)

        # Continue prompt
        prompt_font = self.assets.get_font(size=16)
        prompt_text = prompt_font.render("Press SPACE to continue", True, Colors.TEXT_SECONDARY)
        prompt_rect = prompt_text.get_rect(center=(width // 2, height - 30))
        surface.blit(prompt_text, prompt_rect)

    def _draw_escaped(self, surface: pygame.Surface, width: int, height: int) -> None:
        """Draw escaped fish message."""
        font = self.assets.get_font(size=32)
        text = font.render("The fish got away!", True, Colors.TEXT_ERROR)
        text_rect = text.get_rect(center=(width // 2, height // 2))
        surface.blit(text, text_rect)

        # Continue prompt
        prompt_font = self.assets.get_font(size=16)
        prompt_text = prompt_font.render("Press SPACE to continue", True, Colors.TEXT_SECONDARY)
        prompt_rect = prompt_text.get_rect(center=(width // 2, height - 30))
        surface.blit(prompt_text, prompt_rect)

    def _exit(self) -> None:
        """Exit fishing scene, return to world."""
        if self.manager:
            self.manager.pop()
