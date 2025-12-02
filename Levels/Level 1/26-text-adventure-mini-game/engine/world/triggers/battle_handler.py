"""Battle trigger handler implementation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .base import TriggerContext, TriggerHandlerStrategy

if TYPE_CHECKING:
    from core.world import Trigger


@dataclass
class BattleTriggerHandler(TriggerHandlerStrategy):
    """Handles `battle` triggers by starting encounters."""

    trigger_type: str = "battle"

    def handle(self, trigger: "Trigger", context: TriggerContext) -> None:
        scene = context.scene
        if scene._battle_available(trigger):
            scene._start_battle(trigger.data.get("encounter_id", "default"), trigger)


__all__ = ["BattleTriggerHandler"]
