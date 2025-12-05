"""Stats and status effects system."""

from dataclasses import dataclass, field
import random
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Tuple

if TYPE_CHECKING:
    from typing import TypeAlias

# Status effects that prevent the entity from acting
INCAPACITATING_EFFECTS = frozenset({"stun", "sleep", "frozen"})

# Status effect damage/heal per stack (imported from constants for single source of truth)
from core.constants import (
    STATUS_POISON_DAMAGE_PER_STACK,
    STATUS_BLEED_DAMAGE_PER_STACK,
    STATUS_TERROR_SP_DRAIN_PER_STACK,
    STATUS_BURN_DAMAGE_PER_STACK,
    STATUS_SLEEP_HEAL_PER_STACK,
    STATUS_FROZEN_DAMAGE_PER_STACK,
    STATUS_STUN_SP_DRAIN_PER_STACK,
    STATUS_CONFUSION_SELF_DAMAGE_PER_STACK,
    STATUS_CONFUSION_DAMAGE_CHANCE,
)


# --- Status Effect Tick Handlers ---

def _apply_poison(effect: "StatusEffect", stats: "Stats") -> None:
    """Poison: damage over time, ignores defense."""
    damage = STATUS_POISON_DAMAGE_PER_STACK * effect.stacks
    stats.hp = max(0, stats.hp - damage)


def _apply_bleed(effect: "StatusEffect", stats: "Stats") -> None:
    """Bleed: damage over time, ignores defense."""
    damage = STATUS_BLEED_DAMAGE_PER_STACK * effect.stacks
    stats.hp = max(0, stats.hp - damage)


def _apply_terror(effect: "StatusEffect", stats: "Stats") -> None:
    """Terror: drains SP over time."""
    stats.sp = max(0, stats.sp - STATUS_TERROR_SP_DRAIN_PER_STACK * effect.stacks)


def _apply_burn(effect: "StatusEffect", stats: "Stats") -> None:
    """Burn: fire damage over time, also reduces attack (handled in get_effective_attack)."""
    damage = STATUS_BURN_DAMAGE_PER_STACK * effect.stacks
    stats.hp = max(0, stats.hp - damage)


def _apply_frozen(effect: "StatusEffect", stats: "Stats") -> None:
    """Frozen: cannot act, takes minor cold damage per turn. Speed penalty handled elsewhere."""
    damage = STATUS_FROZEN_DAMAGE_PER_STACK * effect.stacks
    stats.hp = max(0, stats.hp - damage)


def _apply_stun(effect: "StatusEffect", stats: "Stats") -> None:
    """Stun: cannot act, drains SP from mental strain."""
    stats.sp = max(0, stats.sp - STATUS_STUN_SP_DRAIN_PER_STACK * effect.stacks)


def _apply_sleep(effect: "StatusEffect", stats: "Stats") -> None:
    """Sleep: cannot act, but heals slightly each turn. Wakes up when damaged."""
    heal_amount = STATUS_SLEEP_HEAL_PER_STACK * effect.stacks
    stats.hp = min(stats.max_hp, stats.hp + heal_amount)


def _apply_confusion(effect: "StatusEffect", stats: "Stats") -> None:
    """Confusion: may hurt self each turn due to panic. Attack redirection handled in combat."""
    if random.random() < STATUS_CONFUSION_DAMAGE_CHANCE:
        damage = STATUS_CONFUSION_SELF_DAMAGE_PER_STACK * effect.stacks
        stats.hp = max(0, stats.hp - damage)


# Dispatch dictionary for status effect tick handlers
STATUS_TICK_HANDLERS: Dict[str, Callable[["StatusEffect", "Stats"], None]] = {
    "poison": _apply_poison,
    "bleed": _apply_bleed,
    "terror": _apply_terror,
    "burn": _apply_burn,
    "frozen": _apply_frozen,
    "stun": _apply_stun,
    "sleep": _apply_sleep,
    "confusion": _apply_confusion,
}


@dataclass
class StatusEffect:
    """Represents a status effect applied to an entity."""
    id: str  # e.g. "poison", "bleed", "terror", "stun", "sleep", "burn", "frozen", "confusion"
    duration: int  # turns remaining (-1 for permanent)
    stacks: int = 1

    def tick(self, stats: "Stats") -> bool:
        """
        Apply per-turn effect and decrease duration.
        Returns True if effect should be removed (duration expired).
        """
        if self.duration > 0:
            self.duration -= 1

        # Apply effect using dispatch handler
        handler = STATUS_TICK_HANDLERS.get(self.id)
        if handler:
            handler(self, stats)

        # Remove if duration expired (0 means expired; -1 means permanent)
        return self.duration == 0


# EXP required for each level (index = level, value = total EXP needed)
# Level 1 requires 0 EXP, Level 2 requires 100 EXP, etc.
EXP_TABLE: List[int] = [
    0,      # Level 1
    100,    # Level 2
    250,    # Level 3
    450,    # Level 4
    700,    # Level 5
    1000,   # Level 6
    1400,   # Level 7
    1900,   # Level 8
    2500,   # Level 9
    3200,   # Level 10
]

# Stat gains per level-up (base values, can be modified)
LEVEL_UP_STAT_GAINS: Dict[str, int] = {
    "max_hp": 10,
    "max_sp": 5,
    "attack": 2,
    "defense": 2,
    "magic": 2,
    "speed": 1,
    "luck": 1,
}

# Skill points awarded per level-up
# Note: This constant is imported from skill_tree module to maintain single source of truth
from .skill_tree import SKILL_POINTS_PER_LEVEL

DEFAULT_PLAYER_STAT_BLOCK: Tuple[int, ...] = (100, 100, 30, 30, 10, 5, 5, 5, 3)

MAX_LEVEL = len(EXP_TABLE)


# Re-export enemy scaling functions for backward compatibility
# These are now defined in core/enemy_scaling.py
from .enemy_scaling import (
    DIFFICULTY_STAT_MULTIPLIERS,
    DIFFICULTY_REWARD_MULTIPLIERS,
    ENEMY_LEVEL_STAT_SCALING,
    BASE_ENEMY_EXP_PER_LEVEL,
    BASE_ENEMY_GOLD_PER_LEVEL,
    scale_enemy_stat,
    calculate_enemy_exp_reward,
    calculate_enemy_gold_reward,
    get_scaled_enemy_stats,
)

# Element damage multipliers (imported from constants for single source of truth)
from core.constants import (
    ELEMENT_WEAK_MULTIPLIER,
    ELEMENT_RESIST_MULTIPLIER,
    ELEMENT_IMMUNE_MULTIPLIER,
    ELEMENT_ABSORB_MULTIPLIER,
    STAT_REDUCTION_ARM_MISSING,
    STAT_REDUCTION_LEG_MISSING,
    STAT_REDUCTION_BURN_ATTACK_MIN,
    STAT_REDUCTION_BURN_ATTACK_PER_STACK,
    STAT_REDUCTION_FROZEN_SPEED,
)


@dataclass
class Stats:
    """Combat and character statistics."""
    max_hp: int
    hp: int
    max_sp: int  # "soul points" / mana / sanity pool
    sp: int
    attack: int
    defense: int
    magic: int
    speed: int
    luck: int

    # Experience and leveling
    level: int = 1
    exp: int = 0

    equipment_modifiers: Dict[str, int] = field(default_factory=dict)
    skill_tree_modifiers: Dict[str, int] = field(default_factory=dict)
    status_effects: Dict[str, StatusEffect] = field(default_factory=dict)

    # Elemental affinities: elements this entity is weak to, resists, immune to, or absorbs
    weaknesses: List[str] = field(default_factory=list)  # Takes extra damage
    resistances: List[str] = field(default_factory=list)  # Takes reduced damage
    immunities: List[str] = field(default_factory=list)  # Takes no damage
    absorbs: List[str] = field(default_factory=list)  # Heals from damage

    # Performance optimization: per-stat cache invalidation tracking
    # Set of stat keys that need recomputation (empty = all stats are valid)
    _invalidated_stats: set = field(default_factory=lambda: {"attack", "defense", "magic", "speed", "luck"})
    # Version counter to detect status effect changes for caching
    status_effects_version: int = 0

    def _invalidate_all_stats(self) -> None:
        """Mark all stats as needing recomputation."""
        self._invalidated_stats = {"attack", "defense", "magic", "speed", "luck"}

    def get_element_multiplier(self, element: str) -> Tuple[float, str]:
        """
        Get the damage multiplier for an incoming element.

        Returns (multiplier, affinity_type) where affinity_type is one of:
        'weak', 'resist', 'immune', 'absorb', or 'neutral'.
        """
        if element in self.absorbs:
            return (ELEMENT_ABSORB_MULTIPLIER, "absorb")
        if element in self.immunities:
            return (ELEMENT_IMMUNE_MULTIPLIER, "immune")
        if element in self.resistances:
            return (ELEMENT_RESIST_MULTIPLIER, "resist")
        if element in self.weaknesses:
            return (ELEMENT_WEAK_MULTIPLIER, "weak")
        return (1.0, "neutral")

    def _get_base_with_modifiers(self, stat_name: str) -> int:
        """Return base stat plus equipment and skill tree modifiers."""
        base = getattr(self, stat_name)
        equipment_bonus = self.equipment_modifiers.get(stat_name, 0)
        memory_bonus = self.equipment_modifiers.get(f"memory_{stat_name}", 0)
        skill_tree_bonus = self.skill_tree_modifiers.get(stat_name, 0)
        return base + equipment_bonus + skill_tree_bonus + memory_bonus

    def _get_base_with_equipment(self, stat_name: str) -> int:
        """Return base stat plus any equipment modifier for that stat (legacy alias)."""
        return self._get_base_with_modifiers(stat_name)

    def is_dead(self) -> bool:
        """Check if the entity is dead."""
        return self.hp <= 0

    def apply_damage(self, amount: int) -> int:
        """Apply damage, accounting for defense."""
        # Simple damage calculation: damage = amount - effective defense
        actual_damage = max(1, amount - self.get_effective_defense())
        self.hp = max(0, self.hp - actual_damage)
        # Invalidate caches when HP changes (status effects may affect stats)
        self._invalidate_all_stats()
        return self.hp

    def heal(self, amount: int) -> int:
        """Heal HP."""
        self.hp = min(self.max_hp, self.hp + amount)
        # Invalidate caches when HP changes
        self._invalidate_all_stats()
        return self.hp

    def restore_sp(self, amount: int) -> int:
        """Restore SP."""
        self.sp = min(self.max_sp, self.sp + amount)
        # Invalidate caches when SP changes
        self._invalidate_all_stats()
        return self.sp

    def add_status_effect(self, status_id: str, duration: int, stacks: int = 1) -> None:
        """Add or stack a status effect."""
        if status_id in self.status_effects:
            # Stack existing effect
            existing = self.status_effects[status_id]
            existing.stacks += stacks
            existing.duration = max(existing.duration, duration)
        else:
            # New effect
            self.status_effects[status_id] = StatusEffect(
                id=status_id,
                duration=duration,
                stacks=stacks
            )
        # Invalidate all stat caches when status effects change
        self.status_effects_version += 1
        self._invalidate_all_stats()

    def remove_status_effect(self, status_id: str) -> bool:
        """Remove a status effect."""
        if status_id in self.status_effects:
            del self.status_effects[status_id]
            # Invalidate all stat caches when status effects change
            self.status_effects_version += 1
            self._invalidate_all_stats()
            return True
        return False

    def tick_status_effects(self) -> None:
        """Process all status effects for one turn."""
        to_remove = []
        for status_id, effect in self.status_effects.items():
            if effect.tick(self):
                to_remove.append(status_id)

        for status_id in to_remove:
            self.remove_status_effect(status_id)
        # Invalidate all caches in case HP/SP changed from tick effects
        if to_remove or any(effect.id in ("poison", "bleed", "burn", "terror", "sleep")
                           for effect in self.status_effects.values()):
            self._invalidate_all_stats()

    def get_effective_attack(self, use_cache: bool = True, cache_turn: int = -1, cached_stats: Optional[Dict[str, Any]] = None) -> int:
        """Get attack value with equipment and status effect modifiers.

        Args:
            use_cache: If True, use cached value if available and valid
            cache_turn: Current turn number for cache validation
            cached_stats: Optional cache dict to store/retrieve values

        Returns:
            Effective attack value
        """
        cache_key = "effective_attack"
        stat_key = "attack"
        cache_turn_key = "_cache_turn_attack"  # Per-stat turn stamp
        if use_cache and cached_stats is not None:
            if cache_turn_key in cached_stats and cached_stats[cache_turn_key] == cache_turn:
                if cache_key in cached_stats and stat_key not in self._invalidated_stats:
                    return cached_stats[cache_key]

        attack = self._get_base_with_equipment("attack")
        # Limb missing reduces attack
        if "limb_arm_left_missing" in self.status_effects:
            attack = int(attack * STAT_REDUCTION_ARM_MISSING)
        if "limb_arm_right_missing" in self.status_effects:
            attack = int(attack * STAT_REDUCTION_ARM_MISSING)
        # Burn reduces attack per stack
        if "burn" in self.status_effects:
            burn_stacks = self.status_effects["burn"].stacks
            attack = int(attack * max(STAT_REDUCTION_BURN_ATTACK_MIN, 1.0 - STAT_REDUCTION_BURN_ATTACK_PER_STACK * burn_stacks))

        if use_cache and cached_stats is not None:
            cached_stats[cache_key] = attack
            cached_stats[cache_turn_key] = cache_turn
            self._invalidated_stats.discard(stat_key)

        return attack

    def get_effective_defense(self, use_cache: bool = True, cache_turn: int = -1, cached_stats: Optional[Dict[str, Any]] = None) -> int:
        """Get defense value with equipment modifiers.

        Args:
            use_cache: If True, use cached value if available and valid
            cache_turn: Current turn number for cache validation
            cached_stats: Optional cache dict to store/retrieve values

        Returns:
            Effective defense value
        """
        cache_key = "effective_defense"
        stat_key = "defense"
        cache_turn_key = "_cache_turn_defense"  # Per-stat turn stamp
        if use_cache and cached_stats is not None:
            if cache_turn_key in cached_stats and cached_stats[cache_turn_key] == cache_turn:
                if cache_key in cached_stats and stat_key not in self._invalidated_stats:
                    return cached_stats[cache_key]

        defense = self._get_base_with_equipment("defense")

        if use_cache and cached_stats is not None:
            cached_stats[cache_key] = defense
            cached_stats[cache_turn_key] = cache_turn
            self._invalidated_stats.discard(stat_key)

        return defense

    def get_effective_magic(self, use_cache: bool = True, cache_turn: int = -1, cached_stats: Optional[Dict[str, Any]] = None) -> int:
        """Get magic value with equipment modifiers.

        Args:
            use_cache: If True, use cached value if available and valid
            cache_turn: Current turn number for cache validation
            cached_stats: Optional cache dict to store/retrieve values

        Returns:
            Effective magic value
        """
        cache_key = "effective_magic"
        stat_key = "magic"
        cache_turn_key = "_cache_turn_magic"  # Per-stat turn stamp
        if use_cache and cached_stats is not None:
            if cache_turn_key in cached_stats and cached_stats[cache_turn_key] == cache_turn:
                if cache_key in cached_stats and stat_key not in self._invalidated_stats:
                    return cached_stats[cache_key]

        magic = self._get_base_with_equipment("magic")

        if use_cache and cached_stats is not None:
            cached_stats[cache_key] = magic
            cached_stats[cache_turn_key] = cache_turn
            self._invalidated_stats.discard(stat_key)

        return magic

    def get_effective_speed(self, use_cache: bool = True, cache_turn: int = -1, cached_stats: Optional[Dict[str, Any]] = None) -> int:
        """Get speed value with equipment and status effect modifiers.

        Args:
            use_cache: If True, use cached value if available and valid
            cache_turn: Current turn number for cache validation
            cached_stats: Optional cache dict to store/retrieve values

        Returns:
            Effective speed value
        """
        cache_key = "effective_speed"
        stat_key = "speed"
        cache_turn_key = "_cache_turn_speed"  # Per-stat turn stamp
        if use_cache and cached_stats is not None:
            if cache_turn_key in cached_stats and cached_stats[cache_turn_key] == cache_turn:
                if cache_key in cached_stats and stat_key not in self._invalidated_stats:
                    return cached_stats[cache_key]

        speed = self._get_base_with_equipment("speed")
        # Leg missing reduces speed
        if "limb_leg_left_missing" in self.status_effects:
            speed = int(speed * STAT_REDUCTION_LEG_MISSING)
        if "limb_leg_right_missing" in self.status_effects:
            speed = int(speed * STAT_REDUCTION_LEG_MISSING)
        # Frozen drastically reduces speed
        if "frozen" in self.status_effects:
            speed = int(speed * STAT_REDUCTION_FROZEN_SPEED)

        if use_cache and cached_stats is not None:
            cached_stats[cache_key] = speed
            cached_stats[cache_turn_key] = cache_turn
            self._invalidated_stats.discard(stat_key)

        return speed

    def can_act(self) -> bool:
        """Check if the entity can act this turn (not incapacitated)."""
        for effect_id in INCAPACITATING_EFFECTS:
            if effect_id in self.status_effects:
                return False
        return True

    def is_confused(self) -> bool:
        """Check if the entity is confused."""
        return "confusion" in self.status_effects

    def wake_from_sleep(self) -> bool:
        """Wake up from sleep if sleeping. Returns True if was sleeping."""
        return self.remove_status_effect("sleep")

    def get_effective_luck(self, use_cache: bool = True, cache_turn: int = -1, cached_stats: Optional[Dict[str, Any]] = None) -> int:
        """Get luck value with equipment modifiers.

        Args:
            use_cache: If True, use cached value if available and valid
            cache_turn: Current turn number for cache validation
            cached_stats: Optional cache dict to store/retrieve values

        Returns:
            Effective luck value
        """
        cache_key = "effective_luck"
        stat_key = "luck"
        cache_turn_key = "_cache_turn_luck"  # Per-stat turn stamp
        if use_cache and cached_stats is not None:
            if cache_turn_key in cached_stats and cached_stats[cache_turn_key] == cache_turn:
                if cache_key in cached_stats and stat_key not in self._invalidated_stats:
                    return cached_stats[cache_key]

        luck = self._get_base_with_equipment("luck")

        if use_cache and cached_stats is not None:
            cached_stats[cache_key] = luck
            cached_stats[cache_turn_key] = cache_turn
            self._invalidated_stats.discard(stat_key)

        return luck

    # --- Experience and Leveling ---

    def exp_to_next_level(self) -> int:
        """Return EXP needed to reach the next level, or 0 if at max level."""
        if self.level >= MAX_LEVEL:
            return 0
        return EXP_TABLE[self.level] - self.exp

    def exp_for_current_level(self) -> int:
        """Return total EXP required for current level."""
        if self.level <= 1:
            return 0
        return EXP_TABLE[self.level - 1]

    def exp_for_next_level(self) -> int:
        """Return total EXP required for next level."""
        if self.level >= MAX_LEVEL:
            return EXP_TABLE[-1]
        return EXP_TABLE[self.level]

    def add_exp(self, amount: int) -> List[Tuple[int, Dict[str, int], int]]:
        """
        Add experience points and handle level-ups.

        Returns a list of (new_level, stat_gains, skill_points_earned) tuples for each level gained.
        """
        if amount <= 0 or self.level >= MAX_LEVEL:
            return []

        self.exp += amount
        level_ups: List[Tuple[int, Dict[str, int], int]] = []

        # Check for level-ups (can gain multiple levels at once)
        while self.level < MAX_LEVEL and self.exp >= EXP_TABLE[self.level]:
            self.level += 1
            gains = self._apply_level_up_stats()
            level_ups.append((self.level, gains, SKILL_POINTS_PER_LEVEL))

        return level_ups

    def _apply_level_up_stats(self) -> Dict[str, int]:
        """
        Apply stat increases for a single level-up.

        Returns a dict of stat_name -> amount_gained.
        """
        gains: Dict[str, int] = {}

        for stat_name, base_gain in LEVEL_UP_STAT_GAINS.items():
            if hasattr(self, stat_name):
                current = getattr(self, stat_name)
                setattr(self, stat_name, current + base_gain)
                gains[stat_name] = base_gain

        # Fully restore HP and SP on level-up
        self.hp = self.max_hp
        self.sp = self.max_sp

        return gains

    def get_level_progress(self) -> float:
        """
        Return progress to next level as a float between 0.0 and 1.0.
        Returns 1.0 if at max level.
        """
        if self.level >= MAX_LEVEL:
            return 1.0

        current_threshold = self.exp_for_current_level()
        next_threshold = self.exp_for_next_level()
        range_size = next_threshold - current_threshold

        if range_size <= 0:
            return 1.0

        progress_in_range = self.exp - current_threshold
        return min(1.0, max(0.0, progress_in_range / range_size))


def create_default_player_stats() -> Stats:
    """Return baseline stats for initializing or recovering a player."""
    return Stats(*DEFAULT_PLAYER_STAT_BLOCK)
