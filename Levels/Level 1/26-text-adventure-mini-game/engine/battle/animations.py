"""Battle animation effects and visual feedback.

This module contains animation drawing logic and effect management
for battle scenes, including attack animations, damage numbers,
and special effect flashes.
"""

import math
import random
from typing import Callable, Dict, List, Optional, Tuple, TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from core.moves import Move

# Flash effect constants
FLASH_INITIAL_INTENSITY = 1.0  # Starting intensity for flash effects (0.0 to 1.0)
FLASH_DECAY_RATE = 2.0  # Rate at which flash effects fade (intensity per second)
AI_NOTIFICATION_DURATION = 3.0  # Duration in seconds for AI pattern notifications

# Type alias for animation draw functions
AnimationDrawFunc = Callable[[pygame.Surface, int, int, Tuple[int, int, int], float], None]


class BattleAnimationsMixin:
    """Mixin providing animation effects for BattleScene.

    This mixin handles visual feedback during combat including:
    - Attack/skill animations
    - Damage number popups
    - Screen shake effects
    - Combo/coordination/phase flash effects

    Attributes expected from host class:
        current_animation: Optional[Dict] - Current animation state
        animation_timer: float - Timer for animation progress
        screen_shake: float - Current shake intensity
        screen_shake_offset: Tuple[int, int] - Current shake offset
        damage_numbers: List[Dict] - Active damage number popups
        combo_flash: float - Combo effect intensity
        coordinated_tactic_flash: float - Coordination effect intensity
        phase_transition_flash: float - Phase transition effect intensity
    """

    def _get_animation_registry(self) -> Dict[str, AnimationDrawFunc]:
        """Get the animation type to draw function registry.

        Returns a mapping of animation type names to their draw methods.
        Using a method instead of class attribute allows proper binding of self.
        """
        return {
            "slash": self._draw_slash_animation,
            "impact": self._draw_impact_animation,
            "fire": self._draw_fire_animation,
            "ice": self._draw_ice_animation,
            "lightning": self._draw_lightning_animation,
            "dark": self._draw_dark_animation,
            "holy": self._draw_holy_animation,
            "burst": self._draw_burst_animation,
            "ultimate": self._draw_ultimate_animation,
            "charge": self._draw_charge_animation,
            "bite": self._draw_bite_animation,
        }

    def _start_move_animation(self, move: "Move", target) -> None:
        """Start an animation for a move.

        Args:
            move: The Move being executed
            target: The target BattleParticipant
        """
        from core.moves import MoveAnimation

        if not move.animation:
            return

        anim = move.animation
        anim_type = getattr(anim, "anim_type", None)
        if anim_type is None:
            anim_type = getattr(anim, "type", None)
        if hasattr(anim_type, "value"):
            anim_type = anim_type.value
        sound_id = getattr(anim, "sound_id", None)

        self.current_animation = {
            "type": anim_type,
            "color": getattr(anim, "color", (255, 255, 255)),
            "frames": getattr(anim, "frames", 0),
            "duration": getattr(anim, "duration", 0.0),
            "sound": sound_id
        }
        self.animation_timer = 0.0

        # Play sound if available
        if sound_id:
            try:
                self.assets.play_sound(sound_id)
            except Exception:
                pass  # Sound not found, continue silently

    def _draw_animations(self, surface: pygame.Surface) -> None:
        """Wrapper for _draw_animation."""
        self._draw_animation(surface)

    def _draw_animation(self, surface: pygame.Surface) -> None:
        """Draw current attack animation if any.

        Uses a registry pattern to dispatch to the appropriate animation
        draw function based on the animation type.
        """
        if not self.current_animation:
            return

        anim = self.current_animation
        duration = anim.get("duration", 0.0) or 0.0
        if duration <= 0:
            # Guard against zero-duration animations to avoid division errors
            self.current_animation = None
            return

        progress = min(1.0, self.animation_timer / duration)

        if progress >= 1.0:
            self.current_animation = None
            return

        # Get animation parameters
        anim_type = anim["type"]
        color = anim["color"]

        # Calculate target position (center of enemy area) with screen shake offset
        offset_x, offset_y = getattr(self, "screen_shake_offset", (0, 0))
        target_x = 180 + offset_x
        target_y = 150 + offset_y

        # Look up draw function in registry
        registry = self._get_animation_registry()
        draw_func = registry.get(anim_type, self._draw_impact_animation)

        # Call the appropriate draw function
        draw_func(surface, target_x, target_y, color, progress)

    def _draw_slash_animation(
        self, surface: pygame.Surface, x: int, y: int,
        color: Tuple[int, int, int], progress: float
    ) -> None:
        """Draw a slash animation."""
        slash_length = 60 + int(40 * progress)
        start_x = x - slash_length // 2
        start_y = y - slash_length // 2
        end_x = x + slash_length // 2
        end_y = y + slash_length // 2

        # Draw multiple lines for thickness
        for offset in range(-2, 3):
            pygame.draw.line(surface, color,
                           (start_x + offset, start_y),
                           (end_x + offset, end_y), 3)

    def _draw_impact_animation(
        self, surface: pygame.Surface, x: int, y: int,
        color: Tuple[int, int, int], progress: float
    ) -> None:
        """Draw an impact/hit animation."""
        radius = int(20 + 40 * progress)
        pygame.draw.circle(surface, color, (x, y), radius, 4)
        if radius > 10:
            pygame.draw.circle(surface, color, (x, y), radius - 10, 2)

    def _draw_fire_animation(
        self, surface: pygame.Surface, x: int, y: int,
        color: Tuple[int, int, int], progress: float
    ) -> None:
        """Draw a fire animation."""
        for i in range(5):
            offset_x = int(math.sin(progress * 10 + i) * 20)
            offset_y = int(-progress * 40 - i * 10)
            size = max(5, int(15 * (1 - progress)))
            flame_color = (255, 100 + int(100 * progress), 50) if color is None else (
                min(255, color[0]),
                min(255, color[1] + int(50 * progress)),
                min(255, color[2])
            )
            pygame.draw.circle(surface, flame_color, (x + offset_x, y + offset_y), size)

    def _draw_ice_animation(
        self, surface: pygame.Surface, x: int, y: int,
        color: Tuple[int, int, int], progress: float
    ) -> None:
        """Draw an ice animation."""
        shard_color = color or (100, 200, 255)
        for i in range(6):
            angle = (i / 6) * 2 * math.pi + progress * 2
            dist = 30 + int(20 * progress)
            px = x + int(math.cos(angle) * dist)
            py = y + int(math.sin(angle) * dist)
            size = max(3, int(10 * (1 - progress)))
            pygame.draw.polygon(surface, shard_color, [
                (px, py - size),
                (px + size, py),
                (px, py + size),
                (px - size, py)
            ])

    def _draw_lightning_animation(
        self, surface: pygame.Surface, x: int, y: int,
        color: Tuple[int, int, int], progress: float
    ) -> None:
        """Draw a lightning animation."""
        bolt_color = color or (255, 255, 100)
        points = [(x, y - 60)]
        curr_y = y - 60
        while curr_y < y + 20:
            curr_y += 15
            offset = int(math.sin(curr_y * 0.5 + progress * 20) * 15)
            points.append((x + offset, curr_y))

        if len(points) > 1:
            pygame.draw.lines(surface, bolt_color, False, points, 3)
            pygame.draw.lines(surface, (255, 255, 200), False, points, 1)

    def _draw_dark_animation(
        self, surface: pygame.Surface, x: int, y: int,
        color: Tuple[int, int, int], progress: float
    ) -> None:
        """Draw a dark/shadow animation."""
        shadow_color = color or (80, 50, 120)
        for i in range(8):
            angle = (i / 8) * 2 * math.pi - progress * 4
            dist = 20 + int(30 * math.sin(progress * math.pi))
            px = x + int(math.cos(angle) * dist)
            py = y + int(math.sin(angle) * dist)
            size = max(3, int(8 * (1 - abs(progress - 0.5) * 2)))
            pygame.draw.circle(surface, shadow_color, (px, py), size)

    def _draw_holy_animation(
        self, surface: pygame.Surface, x: int, y: int,
        color: Tuple[int, int, int], progress: float
    ) -> None:
        """Draw a holy/light animation."""
        ray_color = color or (255, 255, 200)
        for i in range(8):
            angle = (i / 8) * 2 * math.pi
            length = 40 + int(30 * progress)
            end_x = x + int(math.cos(angle) * length)
            end_y = y + int(math.sin(angle) * length)
            pygame.draw.line(surface, ray_color, (x, y), (end_x, end_y), 2)
        radius = int(15 + 10 * math.sin(progress * math.pi))
        pygame.draw.circle(surface, (255, 255, 255), (x, y), radius)

    def _draw_burst_animation(
        self, surface: pygame.Surface, x: int, y: int,
        color: Tuple[int, int, int], progress: float
    ) -> None:
        """Draw an energy burst animation."""
        radius = int(10 + 50 * progress)
        pygame.draw.circle(surface, color, (x, y), radius, 3)
        for i in range(12):
            angle = (i / 12) * 2 * math.pi + progress * 3
            dist = radius + 10
            px = x + int(math.cos(angle) * dist)
            py = y + int(math.sin(angle) * dist)
            pygame.draw.circle(surface, color, (px, py), 4)

    def _draw_ultimate_animation(
        self, surface: pygame.Surface, x: int, y: int,
        color: Tuple[int, int, int], progress: float
    ) -> None:
        """Draw an ultimate attack animation."""
        if progress < 0.2:
            flash_alpha = int(200 * (1 - progress / 0.2))
            flash_surf = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            flash_surf.fill((255, 255, 255, flash_alpha))
            surface.blit(flash_surf, (0, 0))

        for i in range(3):
            ring_progress = max(0, progress - i * 0.15)
            if ring_progress > 0:
                radius = int(20 + 80 * ring_progress)
                ring_color = (
                    min(255, color[0]) if color else 255,
                    max(0, (color[1] - i * 50) if color else 200 - i * 50),
                    min(255, color[2]) if color else 100,
                )
                pygame.draw.circle(surface, ring_color, (x, y), radius, 4 - i)

    def _draw_charge_animation(
        self, surface: pygame.Surface, x: int, y: int,
        color: Tuple[int, int, int], progress: float
    ) -> None:
        """Draw a charging/tackle animation."""
        start_x = x - 80 + int(160 * progress)
        pygame.draw.line(surface, color, (start_x - 20, y - 10), (start_x, y), 4)
        pygame.draw.line(surface, color, (start_x - 20, y + 10), (start_x, y), 4)
        for i in range(3):
            trail_x = start_x - 15 * (i + 1)
            pygame.draw.circle(surface, color, (trail_x, y), 5 - i)

    def _draw_bite_animation(
        self, surface: pygame.Surface, x: int, y: int,
        color: Tuple[int, int, int], progress: float
    ) -> None:
        """Draw a bite animation."""
        jaw_open = abs(math.sin(progress * math.pi * 3)) * 20
        pygame.draw.polygon(surface, color, [
            (x - 20, y - int(jaw_open)),
            (x, y - int(jaw_open) - 15),
            (x + 20, y - int(jaw_open))
        ])
        pygame.draw.polygon(surface, color, [
            (x - 20, y + int(jaw_open)),
            (x, y + int(jaw_open) + 15),
            (x + 20, y + int(jaw_open))
        ])

    def _update_animation_effects(self, dt: float) -> None:
        """Update all enhanced animation effects.

        Args:
            dt: Delta time in seconds since last update
        """
        # Apply battle speed multiplier (only during auto-battle)
        speed_multiplier = getattr(self, 'battle_speed', 1) if getattr(self, 'auto_battle', False) else 1
        scaled_dt = dt * speed_multiplier

        # Update screen shake
        if self.screen_shake > 0:
            self.screen_shake = max(0, self.screen_shake - scaled_dt * 20)
            intensity = int(self.screen_shake)
            self.screen_shake_offset = (
                random.randint(-intensity, intensity),
                random.randint(-intensity, intensity)
            )
        else:
            self.screen_shake_offset = (0, 0)

        # Keep legacy shake_intensity in sync for callers that still check it
        self.shake_intensity = self.screen_shake

        # Update damage numbers (use scaled dt for faster fade)
        for popup in self.damage_numbers[:]:
            popup["timer"] -= scaled_dt
            popup["y"] -= scaled_dt * 40  # Float upward faster at higher speeds
            if popup["timer"] <= 0:
                self.damage_numbers.remove(popup)

        # Update combo flash
        if self.combo_flash > 0:
            self.combo_flash = max(0, self.combo_flash - scaled_dt * FLASH_DECAY_RATE)

        # Update coordinated tactic flash
        if self.coordinated_tactic_flash > 0:
            self.coordinated_tactic_flash = max(0, self.coordinated_tactic_flash - scaled_dt * FLASH_DECAY_RATE)

        # Update phase transition flash
        if self.phase_transition_flash > 0:
            self.phase_transition_flash = max(0, self.phase_transition_flash - scaled_dt * FLASH_DECAY_RATE)

        # Update AI notification timer
        if self.ai_notification_timer > 0:
            self.ai_notification_timer -= scaled_dt
            if self.ai_notification_timer <= 0:
                self.ai_pattern_notification = None

    def trigger_screen_shake(self, intensity: float = 5.0) -> None:
        """Trigger a screen shake effect.

        Args:
            intensity: Shake intensity (pixels of maximum offset)
        """
        self.screen_shake = max(self.screen_shake, intensity)

    def add_damage_number(
        self, text: str, x: int, y: int,
        color: Tuple[int, int, int] = (255, 255, 255)
    ) -> None:
        """Add a floating damage number popup.

        Args:
            text: The text to display
            x: X position
            y: Y position
            color: Text color (default white)
        """
        self.damage_numbers.append({
            "text": text,
            "x": x,
            "y": y,
            "timer": 1.5,  # Duration in seconds
            "color": color
        })

    def trigger_combo_flash(self) -> None:
        """Trigger the combo attack flash effect."""
        self.combo_flash = FLASH_INITIAL_INTENSITY

    def trigger_coordinated_tactic_flash(self) -> None:
        """Trigger the coordinated tactic flash effect."""
        self.coordinated_tactic_flash = FLASH_INITIAL_INTENSITY

    def trigger_phase_transition_flash(self) -> None:
        """Trigger the phase transition flash effect."""
        self.phase_transition_flash = FLASH_INITIAL_INTENSITY
