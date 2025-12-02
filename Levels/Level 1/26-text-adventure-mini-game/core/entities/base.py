"""Base entity class and shared combat mixins."""

from dataclasses import dataclass, field
from typing import Dict, Optional, List, Tuple, TYPE_CHECKING

from ..constants import SUPPORTED_EQUIP_SLOTS
from ..stats import Stats
from ..logging_utils import log_warning as _raw_log_warning

ALLOWED_EQUIP_STATS = {"attack", "defense", "magic", "speed", "luck"}
EQUIPMENT_LOG_PREFIX = "[Equipment]"


def _get_log_warning():
    """
    Resolve the log_warning function used for equipment messages.

    Tests patch core.entities.log_warning, so we first try to import that
    re-export. If unavailable (during early import), fall back to the
    raw logger from core.logging_utils.
    """
    try:
        # Import from package re-export so tests can patch core.entities.log_warning
        from . import log_warning as exported_log_warning  # type: ignore

        return exported_log_warning
    except Exception:
        return _raw_log_warning


def _log_equipment_warning(entity_id: str, entity_name: str, message: str) -> None:
    """Consistent equipment warning output for grep-friendly debugging."""
    logger = _get_log_warning()
    logger(f"{EQUIPMENT_LOG_PREFIX} {entity_name} ({entity_id}): {message}")


def _sync_base_and_current_skills(obj: "Entity") -> None:
    """Ensure base_skills and skills stay in sync for entities that have them."""
    base_skills = getattr(obj, "base_skills", None)
    skills = getattr(obj, "skills", None)
    if base_skills is None or skills is None:
        return
    if base_skills and not skills:
        obj.skills = list(base_skills)
    elif skills and not base_skills:
        obj.base_skills = list(skills)


if TYPE_CHECKING:
    from ..items import Inventory, Item


@dataclass
class Entity:
    """Base entity class for all game objects."""

    entity_id: str
    name: str
    x: int
    y: int
    sprite_id: str
    solid: bool = True  # blocks movement?
    stats: Optional["Stats"] = None
    faction: str = "neutral"  # "player", "enemy", "npc"
    equipment: Dict[str, Optional[str]] = field(
        default_factory=lambda: {slot: None for slot in SUPPORTED_EQUIP_SLOTS}
    )

    def move(self, dx: int, dy: int) -> None:
        """Move the entity by delta."""
        self.x += dx
        self.y += dy

    def set_position(self, x: int, y: int) -> None:
        """Set the entity's position."""
        self.x = x
        self.y = y

    def equip(self, item: "Item", slot: Optional[str] = None) -> bool:
        """
        Equip an item into a slot.

        Notes:
        - Only equipment items are allowed.
        - Slot must be valid and match item.equip_slot (if provided).
        - Replaces any currently-equipped item in that slot.
        - Does NOT check or mutate inventory; callers must enforce ownership.
        - Call recompute_equipment(items_db) after using this to apply changes.
        """
        if item.item_type != "equipment":
            return False

        target_slot = slot or item.equip_slot
        if not target_slot or target_slot not in SUPPORTED_EQUIP_SLOTS:
            return False
        if item.equip_slot and target_slot != item.equip_slot:
            return False

        self.equipment[target_slot] = item.id
        return True

    def unequip(self, slot: str) -> Optional[str]:
        """
        Unequip an item from a slot.

        Returns the removed item_id if any. Does NOT mutate inventory.
        Call recompute_equipment(items_db) after use to apply changes.
        """
        if slot not in SUPPORTED_EQUIP_SLOTS:
            return None
        previous = self.equipment.get(slot)
        self.equipment[slot] = None
        return previous

    def get_equipped_item_id(self, slot: str) -> Optional[str]:
        """Return the item_id currently equipped in the given slot, if any."""
        if slot not in SUPPORTED_EQUIP_SLOTS:
            return None
        return self.equipment.get(slot)

    def recompute_equipment(self, items_db: Dict[str, "Item"]) -> None:
        """
        Rebuild equipment modifiers and granted skills from equipped items.

        Must be called after any equipment change (equip/unequip/load). Inventory
        is never mutated here. Logs and ignores invalid/non-equipment entries.
        """
        if not self.stats:
            return

        modifiers: Dict[str, int] = {}
        granted_skills = set()
        bad_slots: List[str] = []

        for slot, item_id in (self.equipment or {}).items():
            if not item_id:
                continue
            item = items_db.get(item_id)
            if not item:
                _log_equipment_warning(
                    self.entity_id,
                    self.name,
                    f"unknown item_id '{item_id}' in slot '{slot}' (clearing slot)",
                )
                bad_slots.append(slot)
                continue
            if item.item_type != "equipment":
                _log_equipment_warning(
                    self.entity_id,
                    self.name,
                    f"non-equipment item '{item_id}' in slot '{slot}' (item_type={item.item_type}); clearing slot",
                )
                bad_slots.append(slot)
                continue
            for stat_name, delta in item.stat_modifiers.items():
                if stat_name not in ALLOWED_EQUIP_STATS:
                    _log_equipment_warning(
                        self.entity_id,
                        self.name,
                        f"unsupported modifier '{stat_name}' on item '{item.id}' (ignored)",
                    )
                    continue
                modifiers[stat_name] = modifiers.get(stat_name, 0) + int(delta)
            for skill_id in item.granted_skills:
                granted_skills.add(skill_id)

        for slot in bad_slots:
            self.equipment[slot] = None

        self.stats.equipment_modifiers = modifiers

        base_skills = getattr(self, "base_skills", None)
        if base_skills is not None and hasattr(self, "skills"):
            combined = list(dict.fromkeys(list(base_skills) + list(granted_skills)))
            self.skills = combined


# Maximum number of moves a character can know at once
MAX_LEARNED_MOVES = 4


class CombatantMixin:
    """Shared behavior for entities that participate in combat.

    This mixin provides:
    - Memory system fields (memory_value, memory_stat_type) for calculator-style stat manipulation
    - Move management methods (can_learn_move, learn_move, forget_move, replace_move)

    Classes using this mixin must define:
    - learned_moves: List[str]  (dataclass field)
    - memory_value: int = 0  (dataclass field)
    - memory_stat_type: Optional[str] = None  (dataclass field)
    """

    # Type hints for mixin - actual fields defined in dataclass subclasses
    learned_moves: List[str]
    memory_value: int
    memory_stat_type: Optional[str]

    def can_learn_move(self) -> bool:
        """Check if entity can learn a new move (has room)."""
        return len(self.learned_moves) < MAX_LEARNED_MOVES

    def learn_move(self, move_id: str) -> bool:
        """Learn a new move if there's room. Returns True if successful."""
        if move_id in self.learned_moves:
            return False  # Already knows this move
        if not self.can_learn_move():
            return False  # No room
        self.learned_moves.append(move_id)
        return True

    def forget_move(self, move_id: str) -> bool:
        """Forget a move. Returns True if successful."""
        if move_id not in self.learned_moves:
            return False
        self.learned_moves.remove(move_id)
        return True

    def replace_move(self, old_move_id: str, new_move_id: str) -> bool:
        """Replace an existing move with a new one."""
        if old_move_id not in self.learned_moves:
            return False
        if new_move_id in self.learned_moves:
            return False  # Already knows new move
        idx = self.learned_moves.index(old_move_id)
        self.learned_moves[idx] = new_move_id
        return True
