"""Cutscene phase controller for ending scenes.

This module handles phase timing, advancement logic, and cutscene state management
for ending scenes, providing a clean separation between timing logic and rendering.
"""

import math
import random
from typing import Dict, List, Optional, Callable

from core.logging_utils import log_warning


class CutsceneController:
    """Manages cutscene phase timing and advancement logic.

    Handles:
    - Phase timing and automatic advancement
    - Particle system updates
    - Autosave triggering coordination
    - Post-game unlock triggering
    - Text reveal progress tracking
    """

    # Cutscene phase constants
    PHASE_FADE_IN = 0
    PHASE_TITLE = 1
    PHASE_BLURB = 2
    PHASE_STATS = 3
    PHASE_CREDITS = 4
    PHASE_NG_PLUS = 5
    PHASE_COMPLETE = 6

    def __init__(
        self,
        screen_width: int,
        screen_height: int,
        particle_colors: List[tuple],
        phase_durations: Optional[Dict[int, float]] = None,
        autosave_callback: Optional[Callable[[], None]] = None,
        post_game_unlock_callback: Optional[Callable[[], None]] = None,
    ):
        """Initialize the cutscene controller.

        Args:
            screen_width: Screen width for particle bounds
            screen_height: Screen height for particle bounds
            particle_colors: List of RGB colors for particles
            phase_durations: Custom timing for phases (defaults to standard timing)
            autosave_callback: Function to call for autosave triggering
            post_game_unlock_callback: Function to call for post-game unlocks
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.particle_colors = particle_colors

        # Phase timing
        self.phase_durations = phase_durations or {
            self.PHASE_FADE_IN: 2.0,
            self.PHASE_TITLE: 3.0,
            self.PHASE_BLURB: 4.0,
            self.PHASE_STATS: 4.0,
            self.PHASE_CREDITS: 3.0,
        }

        # Callbacks
        self.autosave_callback = autosave_callback
        self.post_game_unlock_callback = post_game_unlock_callback

        # State
        self.phase = self.PHASE_FADE_IN
        self.phase_timer = 0.0
        self.total_timer = 0.0
        self.fade_alpha = 255  # Start fully black
        self.text_reveal_progress = 0.0
        self.autosave_triggered = False
        self.post_game_unlocks_triggered = False

        # Generate particles
        self.particles = self._generate_particles(40)

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
                "color": random.choice(self.particle_colors),
                "phase_offset": random.uniform(0, math.pi * 2),
            })
        return particles

    def update(self, dt: float) -> None:
        """Update cutscene state and handle phase transitions.

        Args:
            dt: Delta time in seconds
        """
        self.total_timer += dt
        self.phase_timer += dt

        # Trigger autosave on first update
        if not self.autosave_triggered and self.autosave_callback:
            try:
                self.autosave_callback()
                self.autosave_triggered = True
            except Exception as e:
                log_warning(f"Failed to trigger autosave: {e}")
                self.autosave_triggered = True  # Don't retry

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

        # Handle phase-specific updates
        if self.phase in self.phase_durations:
            # Update fade for fade-in phase
            if self.phase == self.PHASE_FADE_IN:
                self.fade_alpha = max(0, 255 - int(self.phase_timer * 127.5))

            # Update text reveal progress
            self.text_reveal_progress = min(1.0, self.phase_timer / 1.5)

            # Auto-advance phase
            if self.phase_timer >= self.phase_durations[self.phase]:
                # Trigger post-game unlocks when credits complete
                if (self.phase == self.PHASE_CREDITS and
                    not self.post_game_unlocks_triggered and
                    self.post_game_unlock_callback):
                    try:
                        self.post_game_unlock_callback()
                        self.post_game_unlocks_triggered = True
                    except Exception as e:
                        log_warning(f"Failed to trigger post-game unlocks: {e}")
                        self.post_game_unlocks_triggered = True

                self.advance_phase()

    def advance_phase(self) -> None:
        """Advance to the next cutscene phase."""
        self.phase += 1
        self.phase_timer = 0.0
        self.text_reveal_progress = 0.0

    def skip_to_ng_plus_menu(self) -> None:
        """Skip directly to the NG+ menu phase."""
        self.phase = self.PHASE_NG_PLUS
        self.phase_timer = 0.0
        self.text_reveal_progress = 0.0

    def is_in_ng_plus_phase(self) -> bool:
        """Check if currently in the NG+ menu phase."""
        return self.phase >= self.PHASE_NG_PLUS

    def should_show_skip_hint(self) -> bool:
        """Check if skip hint should be displayed."""
        return self.phase < self.PHASE_NG_PLUS

    def get_phase_visibility(self) -> Dict[int, bool]:
        """Get visibility flags for each content phase."""
        return {
            self.PHASE_TITLE: self.phase >= self.PHASE_TITLE,
            self.PHASE_BLURB: self.phase >= self.PHASE_BLURB,
            self.PHASE_STATS: self.phase >= self.PHASE_STATS,
            self.PHASE_CREDITS: self.phase >= self.PHASE_CREDITS,
            self.PHASE_NG_PLUS: self.phase >= self.PHASE_NG_PLUS,
        }
