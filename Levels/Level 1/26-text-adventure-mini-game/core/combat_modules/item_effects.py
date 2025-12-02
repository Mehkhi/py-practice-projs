"""Item effect handlers for the combat system.

This module provides a registry-based approach for item effects, replacing
the large if/elif chain in ActionExecutorMixin._execute_item.

Usage:
    result = execute_item_effect(effect_id, actor, target, item, context)
    if result.success:
        # Item was consumed
    else:
        # Item was not consumed (e.g., revive on living target)
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional

if TYPE_CHECKING:
    from core.combat import BattleParticipant, BattleState
    from core.items import Item


@dataclass
class ItemEffectResult:
    """Result of executing an item effect."""
    success: bool  # True if item should be consumed
    messages: List[str]  # Messages to add to battle log
    state_change: Optional[str] = None  # "escaped" if battle ended


# Type alias for effect handler functions
EffectHandler = Callable[
    ["BattleParticipant", "BattleParticipant", "Item", Dict[str, Any]],
    ItemEffectResult
]


# Registry of effect handlers
_EFFECT_HANDLERS: Dict[str, EffectHandler] = {}


def register_effect(effect_id: str) -> Callable[[EffectHandler], EffectHandler]:
    """Decorator to register an item effect handler."""
    def decorator(func: EffectHandler) -> EffectHandler:
        _EFFECT_HANDLERS[effect_id] = func
        return func
    return decorator


def execute_item_effect(
    effect_id: str,
    actor: "BattleParticipant",
    target: "BattleParticipant",
    item: "Item",
    context: Dict[str, Any]
) -> ItemEffectResult:
    """Execute an item effect by looking up its handler.

    Args:
        effect_id: The effect ID to execute
        actor: The battle participant using the item
        target: The battle participant being targeted
        item: The item being used
        context: Additional context (participants list, is_boss_battle, etc.)

    Returns:
        ItemEffectResult with success flag, messages, and optional state change
    """
    handler = _EFFECT_HANDLERS.get(effect_id)
    if handler:
        return handler(actor, target, item, context)

    # Generic fallback for unknown effects
    return ItemEffectResult(
        success=True,
        messages=[f"{actor.entity.name} uses {item.name} on {target.entity.name}."]
    )


# =============================================================================
# HEALING EFFECTS
# =============================================================================

@register_effect("heal_50")
def _heal_50(
    actor: "BattleParticipant",
    target: "BattleParticipant",
    item: "Item",
    context: Dict[str, Any]
) -> ItemEffectResult:
    before = target.stats.hp
    target.stats.heal(50)
    healed = target.stats.hp - before
    return ItemEffectResult(
        success=True,
        messages=[f"{actor.entity.name} uses {item.name} on {target.entity.name} and heals {healed} HP!"]
    )


@register_effect("heal_100")
def _heal_100(
    actor: "BattleParticipant",
    target: "BattleParticipant",
    item: "Item",
    context: Dict[str, Any]
) -> ItemEffectResult:
    before = target.stats.hp
    target.stats.heal(100)
    healed = target.stats.hp - before
    return ItemEffectResult(
        success=True,
        messages=[f"{actor.entity.name} uses {item.name} on {target.entity.name} and heals {healed} HP!"]
    )


@register_effect("heal_full")
def _heal_full(
    actor: "BattleParticipant",
    target: "BattleParticipant",
    item: "Item",
    context: Dict[str, Any]
) -> ItemEffectResult:
    target.stats.hp = target.stats.max_hp
    return ItemEffectResult(
        success=True,
        messages=[f"{actor.entity.name} uses {item.name} on {target.entity.name} and fully restores HP!"]
    )


@register_effect("heal_all_50")
def _heal_all_50(
    actor: "BattleParticipant",
    target: "BattleParticipant",
    item: "Item",
    context: Dict[str, Any]
) -> ItemEffectResult:
    participants = context.get("participants", [])
    for ally in participants:
        if ally.is_player_side and ally.is_alive():
            ally.stats.heal(50)
    return ItemEffectResult(
        success=True,
        messages=[f"{actor.entity.name} uses {item.name}! All allies recover 50 HP!"]
    )


# =============================================================================
# SP RESTORATION EFFECTS
# =============================================================================

@register_effect("restore_sp_20")
def _restore_sp_20(
    actor: "BattleParticipant",
    target: "BattleParticipant",
    item: "Item",
    context: Dict[str, Any]
) -> ItemEffectResult:
    before = target.stats.sp
    target.stats.restore_sp(20)
    restored = target.stats.sp - before
    return ItemEffectResult(
        success=True,
        messages=[f"{actor.entity.name} helps {target.entity.name} recover {restored} SP!"]
    )


@register_effect("restore_sp_30")
def _restore_sp_30(
    actor: "BattleParticipant",
    target: "BattleParticipant",
    item: "Item",
    context: Dict[str, Any]
) -> ItemEffectResult:
    before = target.stats.sp
    target.stats.restore_sp(30)
    restored = target.stats.sp - before
    return ItemEffectResult(
        success=True,
        messages=[f"{actor.entity.name} uses {item.name} on {target.entity.name} and restores {restored} SP!"]
    )


@register_effect("restore_sp_60")
def _restore_sp_60(
    actor: "BattleParticipant",
    target: "BattleParticipant",
    item: "Item",
    context: Dict[str, Any]
) -> ItemEffectResult:
    before = target.stats.sp
    target.stats.restore_sp(60)
    restored = target.stats.sp - before
    return ItemEffectResult(
        success=True,
        messages=[f"{actor.entity.name} uses {item.name} on {target.entity.name} and restores {restored} SP!"]
    )


@register_effect("restore_sp_full")
def _restore_sp_full(
    actor: "BattleParticipant",
    target: "BattleParticipant",
    item: "Item",
    context: Dict[str, Any]
) -> ItemEffectResult:
    before = target.stats.sp
    target.stats.sp = target.stats.max_sp
    restored = target.stats.sp - before
    return ItemEffectResult(
        success=True,
        messages=[f"{actor.entity.name} uses {item.name} on {target.entity.name} and fully restores SP!"]
    )


# =============================================================================
# COMBINED HP/SP RESTORATION
# =============================================================================

@register_effect("restore_hp_sp")
def _restore_hp_sp(
    actor: "BattleParticipant",
    target: "BattleParticipant",
    item: "Item",
    context: Dict[str, Any]
) -> ItemEffectResult:
    before_hp = target.stats.hp
    before_sp = target.stats.sp
    target.stats.heal(100)
    target.stats.restore_sp(50)
    healed = target.stats.hp - before_hp
    restored = target.stats.sp - before_sp
    return ItemEffectResult(
        success=True,
        messages=[f"{actor.entity.name} uses {item.name} on {target.entity.name}! Recovered {healed} HP and {restored} SP!"]
    )


# =============================================================================
# STATUS CURE EFFECTS
# =============================================================================

@register_effect("cure_poison")
def _cure_poison(
    actor: "BattleParticipant",
    target: "BattleParticipant",
    item: "Item",
    context: Dict[str, Any]
) -> ItemEffectResult:
    if target.stats.remove_status_effect("poison"):
        return ItemEffectResult(
            success=True,
            messages=[f"{actor.entity.name} uses {item.name}! {target.entity.name} is cured of poison!"]
        )
    return ItemEffectResult(
        success=True,
        messages=[f"{actor.entity.name} uses {item.name}, but {target.entity.name} wasn't poisoned."]
    )


@register_effect("cure_burn")
def _cure_burn(
    actor: "BattleParticipant",
    target: "BattleParticipant",
    item: "Item",
    context: Dict[str, Any]
) -> ItemEffectResult:
    if target.stats.remove_status_effect("burn"):
        return ItemEffectResult(
            success=True,
            messages=[f"{actor.entity.name} uses {item.name}! {target.entity.name} is no longer burning!"]
        )
    return ItemEffectResult(
        success=True,
        messages=[f"{actor.entity.name} uses {item.name}, but {target.entity.name} wasn't burning."]
    )


@register_effect("cure_frozen")
def _cure_frozen(
    actor: "BattleParticipant",
    target: "BattleParticipant",
    item: "Item",
    context: Dict[str, Any]
) -> ItemEffectResult:
    if target.stats.remove_status_effect("frozen"):
        return ItemEffectResult(
            success=True,
            messages=[f"{actor.entity.name} uses {item.name}! {target.entity.name} thaws out!"]
        )
    return ItemEffectResult(
        success=True,
        messages=[f"{actor.entity.name} uses {item.name}, but {target.entity.name} wasn't frozen."]
    )


@register_effect("cure_incapacitate")
def _cure_incapacitate(
    actor: "BattleParticipant",
    target: "BattleParticipant",
    item: "Item",
    context: Dict[str, Any]
) -> ItemEffectResult:
    cured_sleep = target.stats.remove_status_effect("sleep")
    cured_stun = target.stats.remove_status_effect("stun")
    if cured_sleep or cured_stun:
        return ItemEffectResult(
            success=True,
            messages=[f"{actor.entity.name} uses {item.name}! {target.entity.name} snaps back to attention!"]
        )
    return ItemEffectResult(
        success=True,
        messages=[f"{actor.entity.name} uses {item.name}, but {target.entity.name} was already alert."]
    )


@register_effect("cure_confusion")
def _cure_confusion(
    actor: "BattleParticipant",
    target: "BattleParticipant",
    item: "Item",
    context: Dict[str, Any]
) -> ItemEffectResult:
    if target.stats.remove_status_effect("confusion"):
        return ItemEffectResult(
            success=True,
            messages=[f"{actor.entity.name} uses {item.name}! {target.entity.name}'s mind clears!"]
        )
    return ItemEffectResult(
        success=True,
        messages=[f"{actor.entity.name} uses {item.name}, but {target.entity.name} wasn't confused."]
    )


@register_effect("cure_all")
def _cure_all(
    actor: "BattleParticipant",
    target: "BattleParticipant",
    item: "Item",
    context: Dict[str, Any]
) -> ItemEffectResult:
    ailments = ["poison", "burn", "frozen", "stun", "sleep", "confusion", "bleed", "terror"]
    cured_any = False
    for ailment in ailments:
        if target.stats.remove_status_effect(ailment):
            cured_any = True
    if cured_any:
        return ItemEffectResult(
            success=True,
            messages=[f"{actor.entity.name} uses {item.name}! {target.entity.name} is cleansed of all ailments!"]
        )
    return ItemEffectResult(
        success=True,
        messages=[f"{actor.entity.name} uses {item.name}, but {target.entity.name} had no ailments."]
    )


# =============================================================================
# BUFF EFFECTS
# =============================================================================

@register_effect("buff_attack")
def _buff_attack(
    actor: "BattleParticipant",
    target: "BattleParticipant",
    item: "Item",
    context: Dict[str, Any]
) -> ItemEffectResult:
    target.stats.add_status_effect("attack_up", duration=3, stacks=1)
    target.stats.attack += 5
    return ItemEffectResult(
        success=True,
        messages=[f"{actor.entity.name} uses {item.name}! {target.entity.name}'s attack power surges!"]
    )


@register_effect("buff_defense")
def _buff_defense(
    actor: "BattleParticipant",
    target: "BattleParticipant",
    item: "Item",
    context: Dict[str, Any]
) -> ItemEffectResult:
    target.stats.add_status_effect("defense_up", duration=3, stacks=1)
    target.stats.defense += 5
    return ItemEffectResult(
        success=True,
        messages=[f"{actor.entity.name} uses {item.name}! {target.entity.name}'s defense hardens!"]
    )


@register_effect("buff_speed")
def _buff_speed(
    actor: "BattleParticipant",
    target: "BattleParticipant",
    item: "Item",
    context: Dict[str, Any]
) -> ItemEffectResult:
    target.stats.add_status_effect("speed_up", duration=3, stacks=1)
    target.stats.speed += 5
    return ItemEffectResult(
        success=True,
        messages=[f"{actor.entity.name} uses {item.name}! {target.entity.name} feels quicker!"]
    )


@register_effect("buff_magic")
def _buff_magic(
    actor: "BattleParticipant",
    target: "BattleParticipant",
    item: "Item",
    context: Dict[str, Any]
) -> ItemEffectResult:
    target.stats.add_status_effect("magic_up", duration=3, stacks=1)
    target.stats.magic += 5
    return ItemEffectResult(
        success=True,
        messages=[f"{actor.entity.name} uses {item.name}! {target.entity.name}'s magic intensifies!"]
    )


# =============================================================================
# REVIVAL EFFECTS
# =============================================================================

@register_effect("revive_25")
def _revive_25(
    actor: "BattleParticipant",
    target: "BattleParticipant",
    item: "Item",
    context: Dict[str, Any]
) -> ItemEffectResult:
    if target.stats.hp <= 0:
        revive_hp = max(1, target.stats.max_hp // 4)
        target.stats.hp = revive_hp
        return ItemEffectResult(
            success=True,
            messages=[f"{actor.entity.name} uses {item.name}! {target.entity.name} is revived with {revive_hp} HP!"]
        )
    return ItemEffectResult(
        success=False,
        messages=[f"{actor.entity.name} tries to use {item.name}, but {target.entity.name} is still conscious!"]
    )


@register_effect("revive_50")
def _revive_50(
    actor: "BattleParticipant",
    target: "BattleParticipant",
    item: "Item",
    context: Dict[str, Any]
) -> ItemEffectResult:
    if target.stats.hp <= 0:
        revive_hp = max(1, target.stats.max_hp // 2)
        target.stats.hp = revive_hp
        return ItemEffectResult(
            success=True,
            messages=[f"{actor.entity.name} uses {item.name}! {target.entity.name} is revived with {revive_hp} HP!"]
        )
    return ItemEffectResult(
        success=False,
        messages=[f"{actor.entity.name} tries to use {item.name}, but {target.entity.name} is still conscious!"]
    )


# =============================================================================
# ESCAPE EFFECTS
# =============================================================================

@register_effect("escape_battle")
def _escape_battle(
    actor: "BattleParticipant",
    target: "BattleParticipant",
    item: "Item",
    context: Dict[str, Any]
) -> ItemEffectResult:
    """Attempt to escape battle using an escape item.

    Design decision: Escape items are NOT consumed if escape is blocked
    (e.g., in boss battles). This is intentional because:
    1. The item implies guaranteed escape, so not working feels like a bug
    2. Consuming on failure would be frustrating in an unwinnable situation
    3. Players learn escape is impossible without losing their item

    Returns success=False if blocked, which prevents item consumption.
    """
    is_boss_battle = context.get("is_boss_battle", False)
    if not is_boss_battle:
        return ItemEffectResult(
            success=True,
            messages=[f"{actor.entity.name} throws a {item.name}! The party escapes in the confusion!"],
            state_change="escaped"
        )
    return ItemEffectResult(
        success=False,
        messages=[f"{actor.entity.name} throws a {item.name}, but there's no escaping this battle!"]
    )
