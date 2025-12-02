"""Trigger handler registry and shared handler instances."""

from __future__ import annotations

from typing import Optional

from .base import TriggerContext, TriggerHandlerStrategy, TriggerRegistry
from .battle_handler import BattleTriggerHandler
from .dialogue_handler import DialogueTriggerHandler, FlagTriggerHandler
from .npc_handler import ItemTriggerHandler, NpcInteractionHandler
from .puzzle_handler import BrainTeaserTriggerHandler, FishingTriggerHandler, PuzzleInteractionHandler
from .shop_handler import ShopInteractionHandler
from .warp_handler import AUTO_SAVE_MANAGER_ATTRS, ChallengeSelectTriggerHandler, WarpHandler, WarpTriggerHandler

_registry = TriggerRegistry()
_warp_handler = WarpHandler()
_shop_handler = ShopInteractionHandler()
_puzzle_handler = PuzzleInteractionHandler()
_npc_handler = NpcInteractionHandler(shop_handler=_shop_handler)

for handler in (
    BattleTriggerHandler(),
    DialogueTriggerHandler(),
    WarpTriggerHandler(_warp_handler),
    ChallengeSelectTriggerHandler(),
    ItemTriggerHandler(),
    FlagTriggerHandler(),
    FishingTriggerHandler(_puzzle_handler),
    BrainTeaserTriggerHandler(_puzzle_handler),
):
    _registry.register(handler)


def get_handler_for_trigger_type(trigger_type: str) -> Optional[TriggerHandlerStrategy]:
    """Return the handler registered for the given trigger type."""
    return _registry.get(trigger_type)


def get_warp_handler() -> WarpHandler:
    return _warp_handler


def get_puzzle_handler() -> PuzzleInteractionHandler:
    return _puzzle_handler


def get_shop_handler() -> ShopInteractionHandler:
    return _shop_handler


def get_npc_handler() -> NpcInteractionHandler:
    return _npc_handler


__all__ = [
    "AUTO_SAVE_MANAGER_ATTRS",
    "TriggerContext",
    "TriggerHandlerStrategy",
    "TriggerRegistry",
    "get_handler_for_trigger_type",
    "get_npc_handler",
    "get_puzzle_handler",
    "get_shop_handler",
    "get_warp_handler",
]
