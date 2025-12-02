"""Turn-based combat system.

This module provides the main combat system classes and types.
The BattleSystem class is composed from several mixins that handle
different aspects of combat:

- BattleSystemCore: Core battle infrastructure (turn order, state, combos)
- ActionExecutorMixin: Action execution (attack, skill, item, guard, talk, flee)
- BattleAIMixin: AI decision-making (phases, rules, coordination, learning)
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Optional, Dict, Any
import os
import random

from core.entities import Entity
from core.items import Item
from core.stats import Stats
from core.data_loader import load_json_file

# Import from refactored modules
from core.combat_modules.tactics import TacticsCoordinator, CoordinatedTactic, TacticRole
from core.combat_modules.learning_ai import LearningAI, PlayerPattern
from core.combat_modules.actions import ActionExecutorMixin
from core.combat_modules.ai import BattleAIMixin
from core.combat_modules.battle_system import BattleSystemCore
from core.combat_modules.item_effects import execute_item_effect, register_effect, ItemEffectResult


class ActionType(Enum):
    """Types of actions in combat."""
    ATTACK = auto()
    SKILL = auto()
    ITEM = auto()
    GUARD = auto()
    TALK = auto()  # Undertale "Act"/"Mercy" flavor
    FLEE = auto()
    MEMORY = auto()  # Memory operations for calculator-style actions


class MemoryOperation(Enum):
    """Memory operation types."""
    STORE = auto()       # M+ : Store current value
    SUBTRACT = auto()    # M- : Subtract from stored value
    RECALL = auto()      # MR : Recall and apply stored value
    CLEAR = auto()       # MC : Clear memory


@dataclass
class BattleCommand:
    """A command issued in battle."""
    actor_id: str
    action_type: ActionType
    skill_id: Optional[str] = None
    item_id: Optional[str] = None
    target_ids: List[str] = field(default_factory=list)
    memory_operation: Optional[MemoryOperation] = None
    memory_stat: Optional[str] = None


@dataclass
class Skill:
    """A combat skill/ability."""
    id: str
    name: str
    power: int
    cost_sp: int
    element: str  # "physical", "fire", "holy", "trauma"
    target_pattern: str  # "single_enemy", "all_enemies", "self", "single_ally"
    status_inflict_id: Optional[str] = None
    status_chance: float = 0.0


def load_skills_from_json(path: str = os.path.join("data", "skills.json")) -> Dict[str, Skill]:
    """
    Load skills from JSON file.

    Args:
        path: Path to skills JSON file

    Returns:
        Dict mapping skill_id to Skill instances
    """
    skills: Dict[str, Skill] = {}
    data = load_json_file(path, {})

    for skill_data in data.get("skills", []):
        skill = Skill(
            id=skill_data.get("id", ""),
            name=skill_data.get("name", skill_data.get("id", "")),
            power=skill_data.get("power", 10),
            cost_sp=skill_data.get("cost_sp", 10),
            element=skill_data.get("element", "physical"),
            target_pattern=skill_data.get("target_pattern", "single_enemy"),
            status_inflict_id=skill_data.get("status_inflict_id"),
            status_chance=skill_data.get("status_chance", 0.0)
        )
        if skill.id:
            skills[skill.id] = skill

    return skills


@dataclass
class BattleParticipant:
    """A participant in battle."""
    entity: Entity
    stats: Stats
    is_player_side: bool
    action_ready: bool = True
    morale: int = 0  # for Undertale-like "spare" conditions
    guard_bonus: int = 0
    spared: bool = False
    ai_profile: Optional[Dict[str, Any]] = None
    skills: List[str] = field(default_factory=list)
    items: Dict[str, int] = field(default_factory=dict)
    current_phase: Optional[str] = None
    tactic_role: Optional[str] = None  # Role for coordinated tactics
    coordinated_action: Optional[Dict[str, Any]] = None  # Pending coordinated action
    combo_bonus: float = 1.0  # Damage multiplier from coordination
    memory_value: int = 0  # Stored numeric value for memory system
    memory_stat_type: Optional[str] = None  # Name of stat stored in memory
    last_damage_dealt: int = 0
    last_damage_received: int = 0

    def is_alive(self) -> bool:
        """Check if participant is alive."""
        return not self.stats.is_dead() and not self.spared


class BattleState(Enum):
    """Battle state machine states."""
    PLAYER_CHOOSE = auto()
    ENEMY_CHOOSE = auto()
    RESOLVE_ACTIONS = auto()
    VICTORY = auto()
    DEFEAT = auto()
    ESCAPED = auto()


class BattleSystem(BattleSystemCore, ActionExecutorMixin, BattleAIMixin):
    """Manages turn-based combat.

    This class composes functionality from several mixins:
    - BattleSystemCore: Core battle loop, turn order, state management
    - ActionExecutorMixin: Action execution (attack, skill, item, guard, talk, flee)
    - BattleAIMixin: AI decision-making, phases, coordination, learning

    The class provides:
    - Turn-based combat with speed-based turn order
    - Player and enemy action execution
    - Multi-phase AI with conditional rules
    - Coordinated tactics between enemies
    - Learning AI that adapts to player patterns
    - Undertale-style mercy/spare mechanics

    Example usage:
        ```python
        # Create battle system
        battle = BattleSystem(
            players=[player_entity],
            enemies=[enemy1, enemy2],
            skills=skills_dict,
            items=items_dict,
            enable_coordination=True,
            enable_learning=True
        )

        # Player turn - issue command
        cmd = BattleCommand(
            actor_id=player_entity.entity_id,
            action_type=ActionType.ATTACK,
            target_ids=[enemy1.entity_id]
        )
        battle.issue_command(cmd)
        battle.process_turn()

        # Enemy turn - AI automatically selects actions
        battle.perform_enemy_actions()
        battle.process_turn()

        # Check battle state
        if battle.state == BattleState.VICTORY:
            # Handle victory
            pass
        ```

    Attributes:
        players: List of player-side battle participants
        enemies: List of enemy-side battle participants
        skills: Dictionary of available skills (skill_id -> Skill)
        items: Dictionary of available items (item_id -> Item)
        turn_order: List of participants in speed-based order
        state: Current battle state (PLAYER_CHOOSE, ENEMY_CHOOSE, etc.)
        pending_commands: Commands queued for execution
        message_log: Battle messages for UI display
        spare_threshold: Morale threshold for sparing enemies (default: 3)
        turn_counter: Number of turns elapsed
        debug_ai: Enable AI debug logging
        phase_feedback: Enable phase change feedback messages
        rigged: Enable rigged mode (tutorial mode where enemies are weak)
        enable_coordination: Enable coordinated enemy tactics
        enable_learning: Enable learning AI system
        tactics_coordinator: Coordinator for multi-enemy tactics
        learning_ai: Learning AI that adapts to player patterns
    """

    def __init__(
        self,
        players: List[Entity],
        enemies: List[Entity],
        skills: Dict[str, Skill],
        items: Optional[Dict[str, Item]] = None,
        debug_ai: bool = False,
        phase_feedback: bool = False,
        rng: Optional[random.Random] = None,
        enable_coordination: bool = True,
        enable_learning: bool = True,
        rigged: bool = False,
        battle_context: Optional[Dict[str, Any]] = None,
    ):
        """Initialize the battle system.

        Args:
            players: List of player entities
            enemies: List of enemy entities
            skills: Dictionary of available skills
            items: Dictionary of available items
            debug_ai: Enable AI debug logging
            phase_feedback: Enable phase change feedback messages
            rng: Random number generator (for deterministic testing)
            enable_coordination: Enable coordinated enemy tactics
            enable_learning: Enable learning AI system
            rigged: Enable rigged mode (enemy attacks miss/deal minimal damage)
            battle_context: Optional battle context dict with modifier effects
        """
        def _wrap_participant(obj: Any, is_player: bool) -> BattleParticipant:
            if isinstance(obj, BattleParticipant):
                return obj
            participant = BattleParticipant(obj, obj.stats, is_player)
            participant.memory_value = getattr(obj, "memory_value", 0)
            participant.memory_stat_type = getattr(obj, "memory_stat_type", None)
            participant.last_damage_dealt = getattr(obj, "last_damage_dealt", 0)
            participant.last_damage_received = getattr(obj, "last_damage_received", 0)
            return participant

        self.players = [_wrap_participant(p, True) for p in players if getattr(p, "stats", None)]
        self.enemies = [_wrap_participant(e, False) for e in enemies if getattr(e, "stats", None)]
        self.skills = skills
        self.items = items or {}
        self.turn_order: List[BattleParticipant] = []
        self.state = BattleState.PLAYER_CHOOSE
        self.pending_commands: List[BattleCommand] = []
        self.message_log: List[str] = []
        self.spare_threshold = 3
        self.turn_counter = 0
        self.debug_ai = debug_ai
        self.phase_feedback = phase_feedback
        self.rng = rng or random.Random()

        # Rigged mode: enemy attacks always miss or deal minimal damage (for tutorials)
        self.rigged = rigged

        # Coordinated tactics system
        self.enable_coordination = enable_coordination
        self.tactics_coordinator = TacticsCoordinator() if enable_coordination else None

        # Learning AI system
        self.enable_learning = enable_learning
        self.learning_ai = LearningAI() if enable_learning else None

        # Battle context (for challenge dungeon modifiers)
        self.battle_context = battle_context or {}

        # Assign tactic roles to enemies based on their AI profiles
        self._assign_tactic_roles()

        # Compute initial turn order
        self.compute_turn_order()


# Re-export all public types for backward compatibility
__all__ = [
    # Core types
    "ActionType",
    "BattleCommand",
    "BattleParticipant",
    "BattleState",
    "BattleSystem",
    "Skill",
    "MemoryOperation",
    "load_skills_from_json",
    # From combat_modules
    "CoordinatedTactic",
    "LearningAI",
    "PlayerPattern",
    "TacticRole",
    "TacticsCoordinator",
    # Item effects (for extensibility/modding)
    "execute_item_effect",
    "register_effect",
    "ItemEffectResult",
]
