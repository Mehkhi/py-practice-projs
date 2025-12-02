"""Centralized input manager with remappable controls."""

import json
import os
import pygame
from typing import Dict, List, Optional, Set

from core.logging_utils import log_warning


# Default key bindings
DEFAULT_BINDINGS = {
    "up": pygame.K_UP,
    "down": pygame.K_DOWN,
    "left": pygame.K_LEFT,
    "right": pygame.K_RIGHT,
    "confirm": pygame.K_RETURN,
    "cancel": pygame.K_ESCAPE,
    "menu": pygame.K_ESCAPE,
    "interact": pygame.K_SPACE,
    "run": pygame.K_LSHIFT,
}

# Human-readable names for actions
ACTION_NAMES = {
    "up": "Move Up",
    "down": "Move Down",
    "left": "Move Left",
    "right": "Move Right",
    "confirm": "Confirm/Select",
    "cancel": "Cancel/Back",
    "menu": "Open Menu",
    "interact": "Interact",
    "run": "Run",
}

# Keys that can be bound (excludes system keys)
BINDABLE_KEYS = {
    pygame.K_a, pygame.K_b, pygame.K_c, pygame.K_d, pygame.K_e, pygame.K_f,
    pygame.K_g, pygame.K_h, pygame.K_i, pygame.K_j, pygame.K_k, pygame.K_l,
    pygame.K_m, pygame.K_n, pygame.K_o, pygame.K_p, pygame.K_q, pygame.K_r,
    pygame.K_s, pygame.K_t, pygame.K_u, pygame.K_v, pygame.K_w, pygame.K_x,
    pygame.K_y, pygame.K_z,
    pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4,
    pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9,
    pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT,
    pygame.K_RETURN, pygame.K_SPACE, pygame.K_TAB,
    pygame.K_LSHIFT, pygame.K_RSHIFT, pygame.K_LCTRL, pygame.K_RCTRL,
    pygame.K_LALT, pygame.K_RALT,
    pygame.K_BACKSPACE, pygame.K_DELETE,
    pygame.K_HOME, pygame.K_END, pygame.K_PAGEUP, pygame.K_PAGEDOWN,
    pygame.K_INSERT,
    pygame.K_F1, pygame.K_F2, pygame.K_F3, pygame.K_F4, pygame.K_F5,
    pygame.K_F6, pygame.K_F7, pygame.K_F8, pygame.K_F9, pygame.K_F10,
    pygame.K_F11, pygame.K_F12,
    pygame.K_COMMA, pygame.K_PERIOD, pygame.K_SLASH, pygame.K_SEMICOLON,
    pygame.K_QUOTE, pygame.K_LEFTBRACKET, pygame.K_RIGHTBRACKET,
    pygame.K_BACKSLASH, pygame.K_MINUS, pygame.K_EQUALS,
    pygame.K_BACKQUOTE,
}

ALTERNATE_DIRECTION_KEYS = {
    "up": {pygame.K_w},
    "down": {pygame.K_s},
    "left": {pygame.K_a},
    "right": {pygame.K_d},
}

# Default gamepad bindings (buttons and axes are based on typical Xbox/PlayStation layouts)
DEFAULT_GAMEPAD_BUTTONS = {
    "confirm": [0],     # A / Cross
    "cancel": [1],      # B / Circle
    "menu": [7, 9],     # Start / Options
    "interact": [2],    # X / Square
    "run": [4, 5],      # LB / RB
}

DEFAULT_DIRECTION_AXES = {
    "left": (0, -1.0),
    "right": (0, 1.0),
    "up": (1, -1.0),
    "down": (1, 1.0),
}

DEFAULT_DIRECTION_HATS = {
    "left": (0, -1),
    "right": (0, 1),
    "up": (1, 1),
    "down": (1, -1),
}

GAMEPAD_DEADZONE = 0.35


def get_key_name(key: int) -> str:
    """Get a human-readable name for a pygame key constant."""
    name = pygame.key.name(key)
    # Capitalize and clean up the name
    if name.startswith('['):
        return name  # Already formatted (e.g., "[1]" for numpad)
    return name.upper() if len(name) == 1 else name.replace(' ', '').title()


class InputManager:
    """
    Manages input bindings and provides a unified interface for checking inputs.

    Usage:
        input_mgr = InputManager()

        # In event handling:
        if input_mgr.is_action_pressed(event, "confirm"):
            # Handle confirm action

        # For held keys (in update loop):
        keys = pygame.key.get_pressed()
        if input_mgr.is_action_held(keys, "run"):
            # Handle running
    """

    _instance: Optional["InputManager"] = None

    def __new__(cls) -> "InputManager":
        """Singleton pattern - only one input manager should exist."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        # Current key bindings (action -> key)
        self.bindings: Dict[str, int] = dict(DEFAULT_BINDINGS)

        # Reverse lookup (key -> set of actions)
        self._key_to_actions: Dict[int, Set[str]] = {}
        self._rebuild_reverse_lookup()

        # Gamepad support
        self.joysticks: List[pygame.joystick.Joystick] = []
        self.gamepad_buttons: Dict[str, List[int]] = dict(DEFAULT_GAMEPAD_BUTTONS)
        self.gamepad_deadzone = GAMEPAD_DEADZONE
        self._init_gamepads()

        # Path for saving/loading bindings
        self.bindings_path = os.path.join("data", "keybindings.json")

        # Load saved bindings if they exist
        self.load_bindings()

    def _rebuild_reverse_lookup(self) -> None:
        """Rebuild the key-to-actions reverse lookup table."""
        self._key_to_actions.clear()
        for action, key in self.bindings.items():
            if key not in self._key_to_actions:
                self._key_to_actions[key] = set()
            self._key_to_actions[key].add(action)

    def get_key_for_action(self, action: str) -> Optional[int]:
        """Get the key bound to an action."""
        return self.bindings.get(action)

    def get_actions_for_key(self, key: int) -> Set[str]:
        """Get all actions bound to a key."""
        return self._key_to_actions.get(key, set())

    def is_action_pressed(self, event: pygame.event.Event, action: str) -> bool:
        """Check if an action's key was just pressed (for KEYDOWN events)."""
        if event.type == pygame.KEYDOWN:
            bound_key = self.bindings.get(action)
            return bound_key is not None and event.key == bound_key

        if event.type in (pygame.JOYBUTTONDOWN, pygame.JOYHATMOTION, pygame.JOYAXISMOTION):
            return action in self.get_actions_from_event(event)
        return False

    def is_action_held(self, keys: pygame.key.ScancodeWrapper, action: str) -> bool:
        """Check if an action's key is currently held (for continuous input)."""
        bound_key = self.bindings.get(action)
        return bound_key is not None and keys[bound_key]

    def is_action_active(self, action: str) -> bool:
        """Check if an action is active from keyboard or any connected gamepad."""
        keys = pygame.key.get_pressed()
        bound_key = self.bindings.get(action)
        if bound_key is not None and keys[bound_key]:
            return True

        # Support alternate WASD keys for movement without overriding user bindings
        alt_keys = ALTERNATE_DIRECTION_KEYS.get(action, set())
        for alt_key in alt_keys:
            if keys[alt_key]:
                return True

        return self._is_action_active_from_gamepad(action)

    def is_any_direction_pressed(self, event: pygame.event.Event) -> Optional[str]:
        """Check if any direction key was pressed, return direction name or None."""
        if event.type != pygame.KEYDOWN:
            return None
        for direction in ("up", "down", "left", "right"):
            if event.key == self.bindings.get(direction):
                return direction
        return None

    def rebind_action(self, action: str, new_key: int) -> bool:
        """
        Rebind an action to a new key.

        Returns True if successful, False if the key is not bindable.
        """
        if action not in self.bindings:
            return False
        if new_key not in BINDABLE_KEYS:
            return False

        # Remove old binding from reverse lookup
        old_key = self.bindings[action]
        if old_key in self._key_to_actions:
            self._key_to_actions[old_key].discard(action)
            if not self._key_to_actions[old_key]:
                del self._key_to_actions[old_key]

        # Set new binding
        self.bindings[action] = new_key

        # Add to reverse lookup
        if new_key not in self._key_to_actions:
            self._key_to_actions[new_key] = set()
        self._key_to_actions[new_key].add(action)

        return True

    def reset_to_defaults(self) -> None:
        """Reset all bindings to defaults."""
        self.bindings = dict(DEFAULT_BINDINGS)
        self._rebuild_reverse_lookup()

    def save_bindings(self) -> bool:
        """Save current bindings to file."""
        try:
            os.makedirs(os.path.dirname(self.bindings_path), exist_ok=True)
            with open(self.bindings_path, 'w') as f:
                json.dump(self.bindings, f, indent=2)
            return True
        except Exception as e:
            log_warning(f"Failed to save key bindings to {self.bindings_path}: {e}")
            return False

    def load_bindings(self) -> bool:
        """Load bindings from file."""
        if not os.path.exists(self.bindings_path):
            return False
        try:
            with open(self.bindings_path, 'r') as f:
                loaded = json.load(f)
            # Validate and apply loaded bindings
            for action, key in loaded.items():
                if action in DEFAULT_BINDINGS and isinstance(key, int):
                    self.bindings[action] = key
            self._rebuild_reverse_lookup()
            return True
        except Exception as e:
            log_warning(f"Failed to load key bindings from {self.bindings_path}: {e}")
            return False

    def get_binding_display(self, action: str) -> str:
        """Get a display string for an action's current binding."""
        key = self.bindings.get(action)
        if key is None:
            return "Unbound"
        return get_key_name(key)

    def get_all_actions(self) -> list:
        """Get list of all remappable actions."""
        return list(DEFAULT_BINDINGS.keys())

    def get_action_name(self, action: str) -> str:
        """Get human-readable name for an action."""
        return ACTION_NAMES.get(action, action.replace('_', ' ').title())

    def translate_event(self, event: pygame.event.Event) -> List[pygame.event.Event]:
        """
        Translate joystick events into equivalent KEYDOWN events.

        Returns a list so callers can dispatch both original and translated events.
        """
        translated: List[pygame.event.Event] = []

        if event.type in (pygame.JOYBUTTONDOWN, pygame.JOYHATMOTION, pygame.JOYAXISMOTION):
            actions = self.get_actions_from_event(event)
            for action in actions:
                bound_key = self.bindings.get(action)
                if bound_key is not None:
                    translated.append(pygame.event.Event(pygame.KEYDOWN, key=bound_key))
            return translated

        translated.append(event)
        return translated

    def get_actions_from_event(self, event: pygame.event.Event) -> List[str]:
        """Map a pygame event (keyboard or joystick) to a list of logical actions."""
        actions: List[str] = []
        if event.type == pygame.KEYDOWN:
            actions.extend(self.get_actions_for_key(event.key))
            return actions

        if event.type == pygame.JOYBUTTONDOWN:
            button = getattr(event, "button", -1)
            for action, buttons in self.gamepad_buttons.items():
                if button in buttons:
                    actions.append(action)
            return actions

        if event.type == pygame.JOYHATMOTION:
            hat_value = getattr(event, "value", (0, 0))
            if hat_value:
                hx, hy = hat_value
                if hx < 0:
                    actions.append("left")
                elif hx > 0:
                    actions.append("right")
                if hy > 0:
                    actions.append("up")
                elif hy < 0:
                    actions.append("down")
        elif event.type == pygame.JOYAXISMOTION:
            axis = getattr(event, "axis", -1)
            value = getattr(event, "value", 0.0)
            for direction, (axis_idx, axis_dir) in DEFAULT_DIRECTION_AXES.items():
                if axis != axis_idx:
                    continue
                if axis_dir < 0 and value <= -self.gamepad_deadzone:
                    actions.append(direction)
                elif axis_dir > 0 and value >= self.gamepad_deadzone:
                    actions.append(direction)
        return actions

    def _is_action_active_from_gamepad(self, action: str) -> bool:
        """Check if an action is active from any connected gamepad."""
        if not self.joysticks:
            return False

        # Buttons for non-directional actions
        if action in self.gamepad_buttons:
            for joystick in self.joysticks:
                for button_idx in self.gamepad_buttons[action]:
                    try:
                        if joystick.get_button(button_idx):
                            return True
                    except pygame.error:
                        continue

        # Directional checks via hat and axes
        for joystick in self.joysticks:
            # HAT (D-Pad)
            for hat_index in range(joystick.get_numhats()):
                try:
                    hx, hy = joystick.get_hat(hat_index)
                except pygame.error:
                    continue
                target_hat = DEFAULT_DIRECTION_HATS.get(action)
                if target_hat:
                    axis_idx, desired = target_hat
                    value = hx if axis_idx == 0 else hy
                    if desired < 0 and value < 0:
                        return True
                    if desired > 0 and value > 0:
                        return True

            # Axes (analog stick)
            axis_binding = DEFAULT_DIRECTION_AXES.get(action)
            if axis_binding is None:
                continue
            axis_idx, axis_dir = axis_binding
            try:
                axis_value = joystick.get_axis(axis_idx)
            except pygame.error:
                continue
            if axis_dir < 0 and axis_value <= -self.gamepad_deadzone:
                return True
            if axis_dir > 0 and axis_value >= self.gamepad_deadzone:
                return True

        return False

    def _init_gamepads(self) -> None:
        """Initialize and cache connected gamepads."""
        try:
            pygame.joystick.init()
            for idx in range(pygame.joystick.get_count()):
                try:
                    joystick = pygame.joystick.Joystick(idx)
                    joystick.init()
                    self.joysticks.append(joystick)
                except pygame.error as exc:
                    log_warning(f"Failed to initialize gamepad {idx}: {exc}")
        except pygame.error as exc:
            log_warning(f"Failed to initialize gamepad subsystem: {exc}")


# Global instance accessor
def get_input_manager() -> InputManager:
    """Get the global InputManager instance."""
    return InputManager()
