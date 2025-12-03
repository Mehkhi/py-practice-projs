"""Item and inventory system."""

import os
from enum import Enum
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from .data_loader import load_json_file


class ItemType(str, Enum):
    """Canonical item types for consumables, equipment, and keys."""

    CONSUMABLE = "consumable"
    EQUIPMENT = "equipment"
    KEY = "key"
    FISH = "fish"


@dataclass
class Item:
    """Represents an item in the game."""
    id: str
    name: str
    description: str
    item_type: str  # "consumable", "equipment", "key"
    effect_id: str  # ID wired into combat/world logic
    value: int = 0
    sprite_id: str = "item_default"
    icon_id: str = "item_default"
    target_pattern: str = "self"  # "self", "single_ally"
    equip_slot: str = ""  # "weapon", "armor", "accessory" for equipment
    # Supported stat_modifiers keys: attack, defense, magic, speed, luck
    stat_modifiers: Dict[str, int] = field(default_factory=dict)
    granted_skills: List[str] = field(default_factory=list)
    max_stack_size: Optional[int] = None  # None means unlimited stacking
    # Fishing-specific properties
    rod_quality: Optional[int] = None  # For fishing rods: 1-3
    fishing_bait: bool = False  # True if this item is fishing bait


class Inventory:
    """Player inventory system."""

    def __init__(self):
        self.items: Dict[str, int] = {}  # item_id -> quantity
        self.hotbar_slots: Dict[int, str] = {}  # slot index (1-9) -> item_id

    def add(self, item_id: str, quantity: int = 1, items_db: Optional[Dict[str, "Item"]] = None) -> int:
        """
        Add items to inventory, enforcing max stack size if items_db is provided.

        Args:
            item_id: The item ID to add
            quantity: The quantity to add
            items_db: Optional database of items to check max_stack_size

        Returns:
            The quantity that was actually added (may be less than requested if stack limit reached)
        """
        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            return 0

        if quantity <= 0:
            return 0

        if items_db:
            item = items_db.get(item_id)
            if item and item.max_stack_size is not None:
                current_qty = self.items.get(item_id, 0)
                max_allowed = item.max_stack_size
                space_available = max(0, max_allowed - current_qty)
                quantity_to_add = min(quantity, space_available)

                if quantity_to_add > 0:
                    if item_id in self.items:
                        self.items[item_id] += quantity_to_add
                    else:
                        self.items[item_id] = quantity_to_add
                return quantity_to_add

        # No stack limit or no items_db provided - add normally
        if item_id in self.items:
            self.items[item_id] += quantity
        else:
            self.items[item_id] = quantity
        return quantity

    def get_total_item_count(self) -> int:
        """Get the total count of all items in inventory."""
        return sum(self.items.values())

    def remove(self, item_id: str, quantity: int = 1) -> bool:
        """Remove items from inventory. Returns True if successful."""
        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            return False

        if quantity <= 0:
            return False

        if not self.has(item_id, quantity):
            return False
        self.items[item_id] -= quantity
        if self.items[item_id] <= 0:
            del self.items[item_id]
        return True

    def has(self, item_id: str, quantity: int = 1) -> bool:
        """Check if inventory has enough of an item."""
        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            return False
        if quantity <= 0:
            return False
        return self.items.get(item_id, 0) >= quantity

    def has_item(self, item_id: str, quantity: int = 1) -> bool:
        """Alias for has() to support older call sites."""
        return self.has(item_id, quantity)

    def get_quantity(self, item_id: str) -> int:
        """Get the quantity of an item in inventory."""
        return self.items.get(item_id, 0)

    def get_all_items(self) -> Dict[str, int]:
        """Get all items in inventory."""
        return self.items.copy()

    def clear(self) -> None:
        """Clear all items from inventory."""
        self.items.clear()
        self.hotbar_slots.clear()

    def get_sorted_items(self, sort_by: str = "type", items_db: Optional[Dict[str, "Item"]] = None) -> List[Tuple[str, int]]:
        """
        Get items sorted by the specified criteria.

        Args:
            sort_by: Sort criteria - "name", "type", or "quantity"
            items_db: Optional database of items for name/type sorting

        Returns:
            List of (item_id, quantity) tuples sorted by the criteria
        """
        items_list = list(self.items.items())

        # Helper to get item with fallback for missing items
        def get_item(item_id: str) -> Item:
            if items_db and item_id in items_db:
                return items_db[item_id]
            # Return a default item that sorts last for type, uses id as name
            return Item(id=item_id, name=item_id, description="", item_type="zzz_unknown", effect_id="")

        if sort_by == "quantity":
            # Sort by quantity (descending), then by item_id
            return sorted(items_list, key=lambda x: (-x[1], x[0]))
        elif sort_by == "name" and items_db:
            # Sort by item name (case-insensitive)
            return sorted(items_list, key=lambda x: get_item(x[0]).name.lower())
        elif sort_by == "type" and items_db:
            # Sort by item_type, then by name (case-insensitive)
            return sorted(items_list, key=lambda x: (
                get_item(x[0]).item_type,
                get_item(x[0]).name.lower()
            ))
        else:
            # Default: sort by item_id
            return sorted(items_list)

    def get_filtered_items(self, item_type: Optional[str] = None, items_db: Optional[Dict[str, "Item"]] = None) -> Dict[str, int]:
        """
        Get items filtered by item_type.

        Args:
            item_type: Filter by this item_type (None returns all items)
            items_db: Optional database of items to check item_type

        Returns:
            Dictionary of filtered items
        """
        if item_type is None:
            return self.items.copy()

        if not items_db:
            # Can't filter without items_db, return all
            return self.items.copy()

        # Filter by item_type
        filtered = {}
        for item_id, quantity in self.items.items():
            item = items_db.get(item_id)
            if item and item.item_type == item_type:
                filtered[item_id] = quantity
        return filtered

    def set_hotbar_item(self, slot: int, item_id: Optional[str]) -> bool:
        """
        Set an item in a hotbar slot (1-9).

        Args:
            slot: Hotbar slot number (1-9)
            item_id: Item ID to assign, or None to clear the slot

        Returns:
            True if successful, False if slot is invalid
        """
        if slot < 1 or slot > 9:
            return False

        if item_id is None:
            # Clear the slot
            self.hotbar_slots.pop(slot, None)
        else:
            self.hotbar_slots[slot] = item_id
        return True

    def get_hotbar_item(self, slot: int) -> Optional[str]:
        """
        Get the item ID in a hotbar slot.

        Args:
            slot: Hotbar slot number (1-9)

        Returns:
            Item ID or None if slot is empty/invalid
        """
        if slot < 1 or slot > 9:
            return None
        return self.hotbar_slots.get(slot)

    def clear_hotbar(self) -> None:
        """Clear all hotbar slots."""
        self.hotbar_slots.clear()

    def get_slot_for_item(self, item_id: str) -> Optional[int]:
        """
        Get the hotbar slot number (1-9) for an item.

        Args:
            item_id: The item ID to look up

        Returns:
            Slot number (1-9) or None if item is not assigned to any slot
        """
        for slot, assigned_id in self.hotbar_slots.items():
            if assigned_id == item_id:
                return slot
        return None


def load_items_from_json(
    path: str = os.path.join("data", "items.json"),
    data: Optional[Dict[str, Any]] = None
) -> Dict[str, Item]:
    """Load item definitions from JSON into a mapping."""
    items: Dict[str, Item] = {}
    data_source = data if data is not None else load_json_file(path, default={}, context="Loading items")

    for item_data in data_source.get("items", []):
        max_stack_size = item_data.get("max_stack_size")
        if max_stack_size is not None:
            max_stack_size = int(max_stack_size)

        item = Item(
            id=item_data["id"],
            name=item_data.get("name", item_data["id"]),
            description=item_data.get("description", ""),
            item_type=item_data.get("item_type", "consumable"),
            effect_id=item_data.get("effect_id", ""),
            value=item_data.get("value", 0),
            sprite_id=item_data.get("sprite_id", item_data.get("icon_id", "item_default")),
            icon_id=item_data.get("icon_id", item_data.get("sprite_id", "item_default")),
            target_pattern=item_data.get("target_pattern", "self"),
            equip_slot=item_data.get("equip_slot", ""),
            stat_modifiers=item_data.get("stat_modifiers", {}),
            granted_skills=item_data.get("granted_skills", []),
            max_stack_size=max_stack_size,
            rod_quality=item_data.get("rod_quality"),
            fishing_bait=item_data.get("fishing_bait", False),
        )
        items[item.id] = item
    return items
