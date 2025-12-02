"""High-level helpers for equipment + inventory interactions."""

from typing import Dict, Optional

from .constants import SUPPORTED_EQUIP_SLOTS
from .entities import EQUIPMENT_LOG_PREFIX, Entity, Player
from .items import Item, Inventory
from .logging_utils import log_warning


def equip_item_from_inventory(
    entity: Entity,
    item_id: str,
    items_db: Dict[str, Item],
    slot: Optional[str] = None,
    inventory: Optional[Inventory] = None,
) -> bool:
    """
    Equip an item from inventory with strict ownership semantics.

    Args:
        entity: The entity to equip (Player or PartyMember)
        item_id: The item to equip
        items_db: Database of all items
        slot: Target slot (optional, uses item's default slot)
        inventory: Inventory to use (defaults to entity's inventory if available)

    Option B (strict quantity enforcement):
    - Newly equipped items are removed from inventory.
    - Any item displaced from the target slot is returned to inventory.
    - UI should present equipped items separately from inventory counts.
    """
    item = items_db.get(item_id)
    if not item:
        log_warning(f"{EQUIPMENT_LOG_PREFIX} equip: unknown item_id '{item_id}' requested")
        return False

    # Use provided inventory or entity's inventory
    inv = inventory or getattr(entity, "inventory", None)
    if not inv or not inv.has(item_id):
        log_warning(f"{EQUIPMENT_LOG_PREFIX} equip: lacks '{item_id}' to equip")
        return False

    target_slot = slot or item.equip_slot
    previous_item_id = entity.get_equipped_item_id(target_slot) if target_slot else None

    equipped = entity.equip(item, slot)
    if not equipped:
        log_warning(
            f"{EQUIPMENT_LOG_PREFIX} equip: failed to equip '{item_id}' to slot '{target_slot}'"
        )
        return False

    if not inv.remove(item_id, 1):
        # Roll back equipment change if inventory mutation fails unexpectedly
        if target_slot in SUPPORTED_EQUIP_SLOTS:
            entity.equipment[target_slot] = previous_item_id
        entity.recompute_equipment(items_db)
        return False

    if previous_item_id and previous_item_id != item_id:
        inv.add(previous_item_id, 1)

    entity.recompute_equipment(items_db)
    return True


def unequip_item_to_inventory(
    entity: Entity,
    slot: str,
    items_db: Dict[str, Item],
    inventory: Optional[Inventory] = None,
) -> bool:
    """
    Unequip an item from a slot and return it to inventory.

    Args:
        entity: The entity to unequip from (Player or PartyMember)
        slot: The equipment slot to unequip
        items_db: Database of all items
        inventory: Inventory to return item to (defaults to entity's inventory)

    - Removes item from the specified equipment slot.
    - Adds the unequipped item back to inventory.
    - Recomputes equipment modifiers after change.
    """
    if slot not in SUPPORTED_EQUIP_SLOTS:
        log_warning(f"{EQUIPMENT_LOG_PREFIX} unequip: invalid slot '{slot}'")
        return False

    item_id = entity.get_equipped_item_id(slot)
    if not item_id:
        log_warning(f"{EQUIPMENT_LOG_PREFIX} unequip: slot '{slot}' is already empty")
        return False

    removed_id = entity.unequip(slot)
    if not removed_id:
        return False

    # Use provided inventory or entity's inventory
    inv = inventory or getattr(entity, "inventory", None)
    if inv:
        inv.add(removed_id, 1)

    entity.recompute_equipment(items_db)
    return True


def get_equippable_items(
    entity: Entity,
    items_db: Dict[str, Item],
    slot: Optional[str] = None,
    inventory: Optional[Inventory] = None,
) -> Dict[str, Item]:
    """
    Get all equippable items from inventory.

    Args:
        entity: The entity to check equipment compatibility for
        items_db: Database of all items
        slot: Filter to specific slot (optional)
        inventory: Inventory to check (defaults to entity's inventory)

    If slot is specified, only returns items that can be equipped to that slot.
    """
    equippable: Dict[str, Item] = {}
    inv = inventory or getattr(entity, "inventory", None)
    if not inv:
        return equippable

    for item_id, qty in inv.get_all_items().items():
        if qty <= 0:
            continue
        item = items_db.get(item_id)
        if not item or item.item_type != "equipment":
            continue
        if slot and item.equip_slot != slot:
            continue
        equippable[item_id] = item

    return equippable
