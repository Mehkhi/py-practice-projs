"""Screen transition effects."""

from typing import Callable, Optional, Tuple

import pygame


class TransitionManager:
    """Handles screen transitions (fade in/out)."""

    def __init__(self, default_duration: float = 0.5):
        self.duration = default_duration
        self.timer = 0.0
        self.active = False
        self.mode = "none"  # "fade_in", "fade_out"
        self.on_complete: Optional[Callable[[], None]] = None
        self.color = (0, 0, 0)

    def fade_out(self, duration: Optional[float] = None, on_complete: Optional[Callable[[], None]] = None, color: Tuple[int, int, int] = (0, 0, 0)) -> None:
        """Start fade out (screen goes to black)."""
        self.mode = "fade_out"
        self.duration = duration or 0.5
        self.timer = 0.0
        self.active = True
        self.on_complete = on_complete
        self.color = color

    def fade_in(self, duration: Optional[float] = None, on_complete: Optional[Callable[[], None]] = None, color: Tuple[int, int, int] = (0, 0, 0)) -> None:
        """Start fade in (screen reveals from black)."""
        self.mode = "fade_in"
        self.duration = duration or 0.5
        self.timer = 0.0
        self.active = True
        self.on_complete = on_complete
        self.color = color

    def fade_out_in(self, on_switch: Optional[Callable[[], None]] = None, duration: Optional[float] = None, color: Tuple[int, int, int] = (0, 0, 0)) -> None:
        """Fade out, call on_switch at the midpoint, then fade in."""
        half_duration = (duration or 0.5) / 2.0

        def do_switch_and_fade_in() -> None:
            if on_switch:
                on_switch()
            self.fade_in(duration=half_duration, color=color)

        self.fade_out(duration=half_duration, on_complete=do_switch_and_fade_in, color=color)

    def is_active(self) -> bool:
        """Return whether a transition is currently in progress."""
        return self.active

    def update(self, dt: float) -> None:
        if not self.active:
            return

        self.timer += dt
        if self.timer >= self.duration:
            self.timer = self.duration
            self.active = False
            if self.on_complete:
                self.on_complete()

    def draw(self, surface: pygame.Surface) -> None:
        if self.mode == "none":
            return

        alpha = 0
        if self.mode == "fade_out":
            alpha = int(255 * (self.timer / self.duration))
        elif self.mode == "fade_in":
            alpha = int(255 * (1.0 - (self.timer / self.duration)))

        alpha = max(0, min(255, alpha))

        if alpha > 0:
            overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            overlay.fill((*self.color, alpha))
            surface.blit(overlay, (0, 0))
