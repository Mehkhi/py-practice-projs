"""Coordinated tactics system for multi-enemy combat coordination."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass
class TacticRole:
    """Defines a role an enemy can play in coordinated tactics."""
    role_id: str  # "tank", "dps", "healer", "debuffer", "support"
    priority: int = 1  # Higher = acts first in coordination


@dataclass
class CoordinatedTactic:
    """A coordinated multi-enemy tactic."""
    tactic_id: str
    name: str
    required_roles: List[str]  # e.g., ["tank", "dps"] or ["healer", "dps", "dps"]
    min_enemies: int = 2
    cooldown_turns: int = 0  # Turns before tactic can be used again
    trigger_conditions: Dict[str, Any] = field(default_factory=dict)
    actions: Dict[str, Dict[str, Any]] = field(default_factory=dict)  # role -> action
    combo_bonus: float = 1.2  # Damage/effect multiplier when coordinated


class TacticsCoordinator:
    """Coordinates multi-enemy tactics during combat.

    This class manages coordinated tactics that allow multiple enemies to
    work together for enhanced combat effectiveness. Coordinated tactics
    provide combo bonuses and strategic enemy behavior.

    Features:
    - Built-in tactics (pincer attack, tank and spank, focus fire, etc.)
    - Custom tactics from enemy AI profiles
    - Cooldown management to prevent tactic spam
    - History tracking for variety

    Built-in tactics:
    - pincer_attack: Two DPS enemies attack same target (1.3x damage)
    - tank_and_spank: Tank guards while DPS attacks
    - focus_fire: Multiple enemies focus weakest player (1.5x damage, requires player HP < 50%)
    - heal_support: Healer heals while DPS attacks (requires ally HP < 40%)
    - debuff_combo: Debuffer applies status while DPS attacks
    - pack_howl: Alpha buffs pack members (1.4x damage, early battle only)

    Example usage:
        ```python
        coordinator = TacticsCoordinator()

        # Get available tactics (off cooldown)
        available = coordinator.get_available_tactics(custom_tactics)

        # Check if tactic can be used
        if coordinator.is_tactic_available("pincer_attack"):
            # Execute tactic...
            coordinator.use_tactic(pincer_tactic)

        # Tick cooldowns each turn
        coordinator.tick_cooldowns()
        ```

    Attributes:
        tactic_cooldowns: Dict mapping tactic_id to turns remaining on cooldown
        last_coordinated_turn: Last turn number when coordination occurred
        coordination_history: List of tactic IDs used (for variety tracking)
    """

    # Built-in coordinated tactics
    BUILTIN_TACTICS = {
        "pincer_attack": CoordinatedTactic(
            tactic_id="pincer_attack",
            name="Pincer Attack",
            required_roles=["dps", "dps"],
            min_enemies=2,
            cooldown_turns=2,
            trigger_conditions={"enemies_alive": {"min": 2}},
            actions={
                "dps": {"type": "attack", "target_strategy": "weakest_enemy", "sync": True}
            },
            combo_bonus=1.3
        ),
        "tank_and_spank": CoordinatedTactic(
            tactic_id="tank_and_spank",
            name="Tank and Spank",
            required_roles=["tank", "dps"],
            min_enemies=2,
            cooldown_turns=1,
            trigger_conditions={},
            actions={
                "tank": {"type": "guard", "target_strategy": "self", "taunt": True},
                "dps": {"type": "attack", "target_strategy": "weakest_enemy"}
            },
            combo_bonus=1.0
        ),
        "focus_fire": CoordinatedTactic(
            tactic_id="focus_fire",
            name="Focus Fire",
            required_roles=["dps", "dps"],
            min_enemies=2,
            cooldown_turns=3,
            trigger_conditions={"player_hp_percent": {"max": 50}},
            actions={
                "dps": {"type": "attack", "target_strategy": "weakest_enemy", "sync": True}
            },
            combo_bonus=1.5
        ),
        "heal_support": CoordinatedTactic(
            tactic_id="heal_support",
            name="Heal Support",
            required_roles=["healer", "dps"],
            min_enemies=2,
            cooldown_turns=2,
            trigger_conditions={"ally_hp_percent": {"max": 40}},
            actions={
                "healer": {"type": "skill", "skill_id": "heal", "target_strategy": "weakest_ally"},
                "dps": {"type": "attack", "target_strategy": "random_enemy"}
            },
            combo_bonus=1.0
        ),
        "debuff_combo": CoordinatedTactic(
            tactic_id="debuff_combo",
            name="Debuff Combo",
            required_roles=["debuffer", "dps"],
            min_enemies=2,
            cooldown_turns=3,
            trigger_conditions={"enemy_status_effects": {"none": ["poison", "bleed"]}},
            actions={
                "debuffer": {"type": "skill", "skill_id": "poison_strike", "target_strategy": "highest_hp_enemy"},
                "dps": {"type": "attack", "target_strategy": "highest_hp_enemy"}
            },
            combo_bonus=1.2
        ),
        "pack_howl": CoordinatedTactic(
            tactic_id="pack_howl",
            name="Pack Howl",
            required_roles=["alpha", "pack"],
            min_enemies=2,
            cooldown_turns=4,
            trigger_conditions={"turn_number": {"min": 1, "max": 2}},
            actions={
                "alpha": {"type": "skill", "skill_id": "war_cry", "target_strategy": "self", "buff_allies": True},
                "pack": {"type": "attack", "target_strategy": "random_enemy"}
            },
            combo_bonus=1.4
        )
    }

    def __init__(self):
        """Initialize the tactics coordinator with empty cooldowns and history."""
        self.tactic_cooldowns: Dict[str, int] = {}  # tactic_id -> turns remaining
        self.last_coordinated_turn: int = 0
        self.coordination_history: List[str] = []  # Track which tactics were used

    def tick_cooldowns(self) -> None:
        """Reduce all tactic cooldowns by 1 and remove expired cooldowns.

        This method should be called at the start of each enemy turn to
        decrement cooldown timers. When a cooldown reaches 0, it is removed
        from the cooldowns dict, making the tactic available again.
        """
        for tactic_id in list(self.tactic_cooldowns.keys()):
            self.tactic_cooldowns[tactic_id] -= 1
            if self.tactic_cooldowns[tactic_id] <= 0:
                del self.tactic_cooldowns[tactic_id]

    def is_tactic_available(self, tactic_id: str) -> bool:
        """Check if a tactic is off cooldown and can be used.

        Args:
            tactic_id: ID of the tactic to check

        Returns:
            True if the tactic is available (not on cooldown), False otherwise
        """
        return tactic_id not in self.tactic_cooldowns

    def use_tactic(self, tactic: CoordinatedTactic) -> None:
        """Mark a tactic as used and start its cooldown timer.

        Args:
            tactic: The tactic that was executed

        The tactic is added to coordination_history for variety tracking.
        If the tactic has a cooldown > 0, it is added to tactic_cooldowns.
        """
        if tactic.cooldown_turns > 0:
            self.tactic_cooldowns[tactic.tactic_id] = tactic.cooldown_turns
        self.coordination_history.append(tactic.tactic_id)

    def get_available_tactics(self, custom_tactics: Optional[List[CoordinatedTactic]] = None) -> List[CoordinatedTactic]:
        """Get all tactics that are currently available (off cooldown).

        Args:
            custom_tactics: Additional custom tactics to include alongside
                built-in tactics. These are typically loaded from enemy AI profiles.

        Returns:
            List of CoordinatedTactic instances that can be used this turn.
            Includes both built-in tactics and any provided custom tactics
            that are not currently on cooldown.
        """
        all_tactics = list(self.BUILTIN_TACTICS.values())
        if custom_tactics:
            all_tactics.extend(custom_tactics)
        return [t for t in all_tactics if self.is_tactic_available(t.tactic_id)]
