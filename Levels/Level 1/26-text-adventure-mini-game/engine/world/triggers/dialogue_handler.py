"""Dialogue and flag trigger handlers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .base import TriggerContext, TriggerHandlerStrategy

if TYPE_CHECKING:
    from core.world import Trigger


@dataclass
class DialogueTriggerHandler(TriggerHandlerStrategy):
    """Opens dialogue scenes for dialogue triggers."""

    trigger_type: str = "dialogue"

    def handle(self, trigger: "Trigger", context: TriggerContext) -> None:
        dialogue_id = trigger.data.get("dialogue_id")
        if dialogue_id:
            context.scene._start_dialogue(dialogue_id)
            trigger.fired = trigger.once


@dataclass
class FlagTriggerHandler(TriggerHandlerStrategy):
    """Sets world flags for `flag` triggers."""

    trigger_type: str = "flag"

    def handle(self, trigger: "Trigger", context: TriggerContext) -> None:
        flag_name = trigger.data.get("flag_name")
        flag_value = trigger.data.get("flag_value", True)

        if flag_name:
            context.scene.world.set_flag(flag_name, flag_value)
            trigger.fired = trigger.once


__all__ = ["DialogueTriggerHandler", "FlagTriggerHandler"]
