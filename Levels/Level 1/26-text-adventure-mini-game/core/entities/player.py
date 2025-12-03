"""Player and party member entity definitions."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, TYPE_CHECKING

from ..constants import DEFAULT_FORMATION_POSITION, FORMATION_POSITIONS, SUPPORTED_EQUIP_SLOTS
from ..bestiary import Bestiary
from ..skill_tree import SkillTreeProgress
from .base import (
    CombatantMixin,
    Entity,
    MAX_LEARNED_MOVES,
    _sync_base_and_current_skills,
)

if TYPE_CHECKING:
    from ..items import Inventory
    from ..crafting import CraftingProgress
    from ..stats import Stats


@dataclass
class Player(CombatantMixin, Entity):
    """Player character entity.

    Inherits from CombatantMixin for:
    - Memory system fields (memory_value, memory_stat_type)
    - Move management methods (can_learn_move, learn_move, forget_move, replace_move)
    """

    inventory: "Inventory" = field(default_factory=lambda: None)
    party: List["PartyMember"] = field(default_factory=list)  # companions if any
    base_skills: List[str] = field(default_factory=list)  # permanent learned/innate skills
    skills: List[str] = field(
        default_factory=list
    )  # derived: base_skills + equipment-granted + skill tree
    max_party_size: int = 3  # maximum number of party members (excluding player)
    skill_tree_progress: SkillTreeProgress = field(default_factory=SkillTreeProgress)
    player_class: Optional[str] = None  # primary class id (e.g., "warrior", "mage")
    player_subclass: Optional[str] = None  # secondary class id for hybrid builds
    learned_moves: List[str] = field(default_factory=list)  # attack moves (max 4)
    pending_move_learn: Optional[str] = None  # move waiting to be learned on level-up
    formation_position: str = (
        "front"  # Player's own formation position (typically front as leader)
    )
    # Authoritative formation positions for party members (member_id -> position).
    # PartyMember.formation_position is used only at creation/clone time; this dict
    # is the source of truth for get_member_formation().
    party_formation: Dict[str, str] = field(default_factory=dict)
    crafting_progress: Optional["CraftingProgress"] = None  # Crafting system progress
    bestiary: Bestiary = field(default_factory=Bestiary)  # Enemy compendium
    # Memory system fields (used by calculator-style stat manipulation in combat)
    memory_value: int = 0
    memory_stat_type: Optional[str] = None

    def __init__(
        self,
        entity_id: str,
        x: int,
        y: int,
        sprite_id: str = "player",
        name: Optional[str] = None,
        stats: Optional["Stats"] = None,
        inventory: Optional["Inventory"] = None,
        party: Optional[List["PartyMember"]] = None,
        base_skills: Optional[List[str]] = None,
        skills: Optional[List[str]] = None,
        max_party_size: int = 3,
        skill_tree_progress: Optional[SkillTreeProgress] = None,
        player_class: Optional[str] = None,
        player_subclass: Optional[str] = None,
        learned_moves: Optional[List[str]] = None,
        pending_move_learn: Optional[str] = None,
        formation_position: str = "front",
        party_formation: Optional[Dict[str, str]] = None,
        crafting_progress: Optional["CraftingProgress"] = None,
        bestiary: Optional[Bestiary] = None,
        memory_value: int = 0,
        memory_stat_type: Optional[str] = None,
        faction: str = "player",
        solid: bool = True,
    ) -> None:
        """
        Allow simple construction with (entity_id, x, y) while keeping full configurability.
        Missing name defaults to entity_id; inventory/skill defaults are created automatically.
        """
        # Core entity fields
        self.entity_id = entity_id
        self.name = name or entity_id
        self.x = x
        self.y = y
        self.sprite_id = sprite_id
        self.solid = solid
        self.stats = stats
        self.faction = faction
        self.equipment = {slot: None for slot in SUPPORTED_EQUIP_SLOTS}

        # Player-specific collections
        if inventory is None:
            from ..items import Inventory

            self.inventory = Inventory()
        else:
            self.inventory = inventory

        self.party = list(party) if party else []
        self.base_skills = list(base_skills) if base_skills else []
        self.skills = list(skills) if skills else list(self.base_skills)
        self.max_party_size = max_party_size
        self.skill_tree_progress = skill_tree_progress or SkillTreeProgress()
        self.player_class = player_class
        self.player_subclass = player_subclass
        self.learned_moves = list(learned_moves) if learned_moves else []
        self.pending_move_learn = pending_move_learn
        self.formation_position = formation_position
        self.party_formation = dict(party_formation) if party_formation else {}
        self.crafting_progress = crafting_progress
        self.bestiary = bestiary or Bestiary()
        self.memory_value = memory_value
        self.memory_stat_type = memory_stat_type

        # Keep skills and learned move limits consistent with mixin helpers
        self.__post_init__()

    def __post_init__(self) -> None:
        """Initialize player-specific defaults."""
        if self.faction == "neutral":
            self.faction = "player"
        if self.inventory is None:
            from ..items import Inventory

            self.inventory = Inventory()
        _sync_base_and_current_skills(self)
        # Ensure learned_moves doesn't exceed max
        if len(self.learned_moves) > MAX_LEARNED_MOVES:
            self.learned_moves = self.learned_moves[:MAX_LEARNED_MOVES]

    # Move management methods (can_learn_move, learn_move, forget_move, replace_move)
    # are inherited from CombatantMixin

    def can_interact(self) -> bool:
        """Check if player can interact with objects."""
        return not self.is_dead() if self.stats else True

    def is_dead(self) -> bool:
        """Check if player is dead."""
        return self.stats.is_dead() if self.stats else False

    def add_party_member(self, member: "PartyMember") -> bool:
        """
        Add a party member to the party.

        Returns True if successful, False if party is full or member already in party.
        """
        if len(self.party) >= self.max_party_size:
            return False
        if any(m.entity_id == member.entity_id for m in self.party):
            return False
        self.party.append(member)
        return True

    def remove_party_member(self, member_id: str) -> Optional["PartyMember"]:
        """
        Remove a party member by ID.

        Returns the removed member or None if not found.
        """
        for i, member in enumerate(self.party):
            if member.entity_id == member_id:
                return self.party.pop(i)
        return None

    def get_party_member(self, member_id: str) -> Optional["PartyMember"]:
        """Get a party member by ID."""
        for member in self.party:
            if member.entity_id == member_id:
                return member
        return None

    def get_alive_party_members(self) -> List["PartyMember"]:
        """Get all alive party members."""
        return [m for m in self.party if m.is_alive()]

    def get_battle_party(self) -> List[Entity]:
        """
        Get the full battle party (player + alive party members).

        Returns a list with the player first, followed by alive party members.
        """
        return [self] + self.get_alive_party_members()

    def is_party_wiped(self) -> bool:
        """Check if the entire party (including player) is dead."""
        if not self.is_dead():
            return False
        return all(m.is_dead() for m in self.party)

    def set_member_formation(self, member_id: str, position: str) -> bool:
        """
        Set a party member's formation position.

        Args:
            member_id: The entity ID of the party member
            position: One of "front", "middle", or "back"

        Returns:
            True if successful, False if invalid position or member not found
        """
        if position not in FORMATION_POSITIONS:
            return False
        member = self.get_party_member(member_id)
        if not member:
            return False
        self.party_formation[member_id] = position
        return True

    def get_member_formation(self, member_id: str) -> str:
        """Get a party member's formation position (defaults to middle)."""
        return self.party_formation.get(member_id, DEFAULT_FORMATION_POSITION)

    def get_formation_modifiers(self, entity_id: str) -> Dict[str, float]:
        """
        Get combat modifiers for an entity based on their formation position.

        Returns dict with keys: defense_mod, attack_mod, aggro_mod
        """
        if entity_id == self.entity_id:
            position = self.formation_position
        else:
            position = self.get_member_formation(entity_id)
        return FORMATION_POSITIONS.get(
            position, FORMATION_POSITIONS[DEFAULT_FORMATION_POSITION]
        )


@dataclass
class PartyMember(CombatantMixin, Entity):
    """A companion character that can join the player's party.

    Inherits from CombatantMixin for:
    - Memory system fields (memory_value, memory_stat_type)
    - Move management methods (can_learn_move, learn_move, forget_move, replace_move)
    """

    base_skills: List[str] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)
    role: str = "fighter"  # "fighter", "mage", "healer", "support"
    portrait_id: Optional[str] = None
    skill_tree_progress: SkillTreeProgress = field(default_factory=SkillTreeProgress)
    learned_moves: List[str] = field(default_factory=list)  # attack moves (max 4)
    pending_move_learn: Optional[str] = None  # move waiting to be learned on level-up
    # Initial formation position; Player.party_formation is authoritative after recruitment
    formation_position: str = "middle"
    # Memory system fields (used by calculator-style stat manipulation in combat)
    memory_value: int = 0
    memory_stat_type: Optional[str] = None

    def __post_init__(self) -> None:
        """Initialize party member defaults."""
        if self.faction == "neutral":
            self.faction = "player"
        _sync_base_and_current_skills(self)

        # Ensure learned_moves has at least base skills if empty
        if not self.learned_moves and self.base_skills:
            # Take up to MAX_LEARNED_MOVES from base_skills
            self.learned_moves = self.base_skills[:MAX_LEARNED_MOVES]

        # Ensure learned_moves doesn't exceed max
        if len(self.learned_moves) > MAX_LEARNED_MOVES:
            self.learned_moves = self.learned_moves[:MAX_LEARNED_MOVES]

    # Move management methods (can_learn_move, learn_move, forget_move, replace_move)
    # are inherited from CombatantMixin

    def is_dead(self) -> bool:
        """Check if party member is dead."""
        return self.stats.is_dead() if self.stats else False

    def is_alive(self) -> bool:
        """Check if party member is alive."""
        return not self.is_dead()
