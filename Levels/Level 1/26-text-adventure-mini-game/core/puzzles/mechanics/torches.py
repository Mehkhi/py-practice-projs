"""Torch lighting mechanics."""

from typing import TYPE_CHECKING

from ..models import PuzzleElement, PuzzleElementType, DungeonPuzzle

if TYPE_CHECKING:
    from ...entities.player import Player


def light_torch(element: PuzzleElement, player: "Player", puzzle: DungeonPuzzle) -> bool:
    """Light torch if player has torch item. Returns True if successful."""
    if element.element_type != PuzzleElementType.TORCH_HOLDER:
        return False

    if element.state == "lit":
        return True  # Already lit

    # Check if player has torch or lantern
    if not player.inventory:
        return False

    has_torch = player.inventory.has("torch") or player.inventory.has("lantern")
    if not has_torch:
        return False

    # Consume the item
    if player.inventory.has("torch"):
        player.inventory.remove("torch", 1)
    elif player.inventory.has("lantern"):
        player.inventory.remove("lantern", 1)

    element.state = "lit"
    return True
