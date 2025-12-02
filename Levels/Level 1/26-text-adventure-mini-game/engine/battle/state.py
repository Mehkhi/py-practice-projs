"""Battle state management.

This module provides a centralized state manager for battle scene state,
reducing the number of instance variables scattered across the BattleScene class.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, List, Tuple, Any, TYPE_CHECKING

if TYPE_CHECKING:
    import pygame
    from core.combat import MemoryOperation


@dataclass
class AnimationState:
    """State for battle animations."""

    current_animation: Optional[Dict[str, Any]] = None
    animation_timer: float = 0.0
    animation_target_pos: Optional[Tuple[int, int]] = None

    # Screen shake
    screen_shake: float = 0.0
    screen_shake_offset: Tuple[int, int] = (0, 0)
    shake_offset: Tuple[int, int] = (0, 0)
    shake_timer: float = 0.0
    shake_intensity: float = 0.0

    # Flash effects
    flash_timer: float = 0.0
    combo_flash: float = 0.0
    coordinated_tactic_flash: float = 0.0
    phase_transition_flash: float = 0.0

    # Damage numbers: {x, y, text, color, timer, velocity}
    damage_numbers: List[Dict[str, Any]] = field(default_factory=list)

    def reset(self) -> None:
        """Reset all animation state to defaults."""
        self.current_animation = None
        self.animation_timer = 0.0
        self.animation_target_pos = None
        self.screen_shake = 0.0
        self.screen_shake_offset = (0, 0)
        self.shake_offset = (0, 0)
        self.shake_timer = 0.0
        self.shake_intensity = 0.0
        self.flash_timer = 0.0
        self.combo_flash = 0.0
        self.coordinated_tactic_flash = 0.0
        self.phase_transition_flash = 0.0
        self.damage_numbers.clear()


@dataclass
class MenuState:
    """State for battle menu navigation and target selection."""

    # Menu mode: "main", "skill", "item", "target", "move", "memory", "memory_stat"
    menu_mode: str = "main"

    # Target selection
    waiting_for_target: bool = False
    target_type: Optional[str] = None
    target_index: int = 0
    target_side: Optional[str] = None  # "enemy" or "ally"

    # Pending actions
    pending_skill_id: Optional[str] = None
    pending_item_id: Optional[str] = None
    pending_move_id: Optional[str] = None
    _pending_memory_op: Optional["MemoryOperation"] = None

    # Menu index mappings
    item_menu_mapping: Dict[int, str] = field(default_factory=dict)
    move_menu_mapping: Dict[int, str] = field(default_factory=dict)

    def reset_to_main(self) -> None:
        """Reset menu state back to main menu."""
        self.menu_mode = "main"
        self.waiting_for_target = False
        self.target_type = None
        self.target_index = 0
        self.target_side = None
        self.pending_skill_id = None
        self.pending_item_id = None
        self.pending_move_id = None
        self._pending_memory_op = None
        self.item_menu_mapping.clear()
        self.move_menu_mapping.clear()


@dataclass
class BattleProgressState:
    """State tracking battle progress and outcomes."""

    # Active player tracking
    active_player_index: Optional[int] = 0
    _player_phase_initialized: bool = False

    # Outcome tracking
    _rewards_applied: bool = False
    _outcome_finalized: bool = False
    _victory_spared: bool = False

    # Pending move learns for level-up: (entity, move) tuples
    _pending_move_learns: List[Tuple[Any, Any]] = field(default_factory=list)

    def reset(self) -> None:
        """Reset battle progress state."""
        self.active_player_index = 0
        self._player_phase_initialized = False
        self._rewards_applied = False
        self._outcome_finalized = False
        self._victory_spared = False
        self._pending_move_learns.clear()


@dataclass
class AIDebugState:
    """State for AI debug overlay and notifications."""

    show_ai_debug: bool = False
    last_adaptation_level: int = 0
    ai_pattern_notification: Optional[str] = None
    ai_notification_timer: float = 0.0

    def reset(self) -> None:
        """Reset AI debug state."""
        self.show_ai_debug = False
        self.last_adaptation_level = 0
        self.ai_pattern_notification = None
        self.ai_notification_timer = 0.0


@dataclass
class BattleStateManager:
    """Centralized manager for all battle scene state.

    This class consolidates the various state variables used by BattleScene
    into organized, logical groupings for better maintainability.

    Usage:
        state = BattleStateManager()
        state.animation.current_animation = {...}
        state.menu.menu_mode = "skill"
        state.progress._rewards_applied = True
    """

    animation: AnimationState = field(default_factory=AnimationState)
    menu: MenuState = field(default_factory=MenuState)
    progress: BattleProgressState = field(default_factory=BattleProgressState)
    ai_debug: AIDebugState = field(default_factory=AIDebugState)

    def reset_all(self) -> None:
        """Reset all state to initial values."""
        self.animation.reset()
        self.menu.reset_to_main()
        self.progress.reset()
        self.ai_debug.reset()

    def reset_for_new_turn(self) -> None:
        """Reset state appropriate for a new turn."""
        self.menu.reset_to_main()
