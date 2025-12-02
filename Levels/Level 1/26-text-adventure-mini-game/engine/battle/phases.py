"""Battle phase state machine for `BattleScene.update`.

Each phase encapsulates the logic that was previously in `BattleScene.update`
for a specific `BattleState` value. This keeps the scene method small while
preserving behavior.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from core.combat import BattleState
from core.tutorial_system import TipTrigger
from engine.battle import AI_NOTIFICATION_DURATION

if TYPE_CHECKING:
    from engine.battle_scene import BattleScene


class BattlePhase:
    """Base interface for a battle phase."""

    def __init__(self, scene: "BattleScene") -> None:
        self.scene = scene

    def enter(self) -> None:
        """Called when entering this phase."""

    def exit(self) -> None:
        """Called when exiting this phase."""

    def update(self, dt: float) -> None:
        """Per-frame update for this phase."""
        raise NotImplementedError


class PlayerChoosePhase(BattlePhase):
    """Handles player choice phase (menus, auto-battle, phase init)."""

    def update(self, dt: float) -> None:
        scene = self.scene

        if not scene._player_phase_initialized:
            scene._reset_player_phase()

        if (
            scene.battle_system.state == BattleState.PLAYER_CHOOSE
            and scene._player_phase_initialized
            and scene.auto_battle
            and scene.active_player_index is not None
        ):
            scene._process_auto_battle_turn()

        if (
            scene.battle_system.state == BattleState.PLAYER_CHOOSE
            and scene._player_phase_initialized
            and scene.active_player_index is None
        ):
            scene.battle_system.state = BattleState.ENEMY_CHOOSE


class EnemyChoosePhase(BattlePhase):
    """Handles enemy AI decision phase."""

    def update(self, dt: float) -> None:
        self.scene.battle_system.perform_enemy_actions()


class ResolveActionsPhase(BattlePhase):
    """Handles action resolution and post-turn effects."""

    def update(self, dt: float) -> None:
        scene = self.scene
        system = scene.battle_system

        system.perform_turn()

        if not scene._status_effect_triggered:
            has_status = False
            for participant in system.players + system.enemies:
                if participant.stats.status_effects:
                    has_status = True
                    break
            if has_status:
                tutorial_manager = scene.get_manager_attr(
                    "tutorial_manager", "_check_status_effect_tip"
                )
                if tutorial_manager:
                    tutorial_manager.trigger_tip(TipTrigger.FIRST_STATUS_EFFECT)
                    scene._status_effect_triggered = True

        if system.state == BattleState.PLAYER_CHOOSE:
            scene._player_phase_initialized = False

        if system.message_log:
            log = system.message_log

            for msg in log:
                if msg.startswith("COMBO:"):
                    scene.trigger_combo_flash()
                if msg.startswith("TACTIC:"):
                    scene.trigger_coordinated_tactic_flash()
                if msg.startswith("PHASE:"):
                    scene.trigger_phase_transition_flash()

            if system.learning_ai:
                current_level = system.learning_ai.adaptation_level
                if current_level > scene.last_adaptation_level:
                    if system.learning_ai.has_learned_patterns():
                        summary = system.learning_ai.get_adaptation_summary()
                        scene.ai_pattern_notification = summary
                        scene.ai_notification_timer = AI_NOTIFICATION_DURATION
                scene.last_adaptation_level = current_level

            phase_messages = [msg for msg in log if "shifts tactics" in msg]
            if phase_messages:
                last_phase_msg = phase_messages[-1]
                messages_to_show = [last_phase_msg]
                remaining = list(log)
                try:
                    remaining.remove(last_phase_msg)
                except ValueError:
                    pass
                messages_to_show.extend(remaining[-2:])
            else:
                messages_to_show = log[-3:]

            scene.message_box.set_text("\n".join(messages_to_show))
            scene.combat_log.add_messages(log)
            system.message_log.clear()


class VictoryPhase(BattlePhase):
    """Handles victory resolution."""

    def update(self, dt: float) -> None:
        self.scene._handle_victory()


class DefeatPhase(BattlePhase):
    """Handles defeat resolution."""

    def update(self, dt: float) -> None:
        self.scene._handle_defeat()


class EscapedPhase(BattlePhase):
    """Handles escape resolution."""

    def update(self, dt: float) -> None:
        self.scene._handle_escape()


@dataclass
class BattlePhaseManager:
    """Coordinator that maps `BattleState` to phase objects."""

    scene: "BattleScene"

    def __post_init__(self) -> None:
        self._phases = {
            BattleState.PLAYER_CHOOSE: PlayerChoosePhase(self.scene),
            BattleState.ENEMY_CHOOSE: EnemyChoosePhase(self.scene),
            BattleState.RESOLVE_ACTIONS: ResolveActionsPhase(self.scene),
            BattleState.VICTORY: VictoryPhase(self.scene),
            BattleState.DEFEAT: DefeatPhase(self.scene),
            BattleState.ESCAPED: EscapedPhase(self.scene),
        }
        self._current_state: BattleState | None = None

    def update(self, dt: float) -> None:
        """Update the active phase and run common per-frame logic."""
        system = self.scene.battle_system
        state = system.state

        if state != self._current_state:
            if self._current_state is not None:
                self._phases[self._current_state].exit()
            self._current_state = state
            phase = self._phases.get(state)
            if phase:
                phase.enter()

        phase = self._phases.get(state)
        if phase:
            phase.update(dt)
