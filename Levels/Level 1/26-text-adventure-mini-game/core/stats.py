"""Stats and status effects system."""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Callable, Dict, List, Optional, Tuple

if TYPE_CHECKING:
    from typing import TypeAlias

# Status effects that prevent the entity from acting
INCAPACITATING_EFFECTS = frozenset({"stun", "sleep", "frozen"})

# Status effect damage/heal per stack
POISON_DAMAGE_PER_STACK = 5
BLEED_DAMAGE_PER_STACK = 3
TERROR_SP_DRAIN_PER_STACK = 2
BURN_DAMAGE_PER_STACK = 4
SLEEP_HEAL_PER_STACK = 2


# --- Status Effect Tick Handlers ---

def _apply_poison(effect: "StatusEffect", stats: "Stats") -> None:
    """Poison: damage over time, ignores defense."""
    damage = POISON_DAMAGE_PER_STACK * effect.stacks
    stats.hp = max(0, stats.hp - damage)


def _apply_bleed(effect: "StatusEffect", stats: "Stats") -> None:
    """Bleed: damage over time, ignores defense."""
    damage = BLEED_DAMAGE_PER_STACK * effect.stacks
    stats.hp = max(0, stats.hp - damage)


def _apply_terror(effect: "StatusEffect", stats: "Stats") -> None:
    """Terror: drains SP over time."""
    stats.sp = max(0, stats.sp - TERROR_SP_DRAIN_PER_STACK * effect.stacks)


def _apply_burn(effect: "StatusEffect", stats: "Stats") -> None:
    """Burn: fire damage over time, also reduces attack (handled in get_effective_attack)."""
    damage = BURN_DAMAGE_PER_STACK * effect.stacks
    stats.hp = max(0, stats.hp - damage)


def _apply_frozen(effect: "StatusEffect", stats: "Stats") -> None:
    """Frozen: cannot act, but takes no tick damage. Effect handled in combat system."""
    pass


def _apply_stun(effect: "StatusEffect", stats: "Stats") -> None:
    """Stun: cannot act for duration. Effect handled in combat system."""
    pass


def _apply_sleep(effect: "StatusEffect", stats: "Stats") -> None:
    """Sleep: cannot act, but heals slightly each turn. Wakes up when damaged."""
    heal_amount = SLEEP_HEAL_PER_STACK * effect.stacks
    stats.hp = min(stats.max_hp, stats.hp + heal_amount)


def _apply_confusion(effect: "StatusEffect", stats: "Stats") -> None:
    """Confusion: may attack wrong target or self. Effect handled in combat system."""
    pass


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

        # Remove if duration expired (unless permanent)
        if self.duration == 0 and self.duration != -1:
            return True
        return False


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


# --- Enemy Level Scaling ---

# Difficulty multipliers for enemy stats
DIFFICULTY_STAT_MULTIPLIERS: Dict[str, float] = {
    "easy": 0.75,
    "normal": 1.0,
    "hard": 1.25,
    "elite": 1.5,
    "boss": 2.0,
}

# Difficulty multipliers for rewards (EXP, gold, drop rates)
DIFFICULTY_REWARD_MULTIPLIERS: Dict[str, float] = {
    "easy": 0.5,
    "normal": 1.0,
    "hard": 1.5,
    "elite": 2.0,
    "boss": 3.0,
}

# Per-level stat scaling for enemies (percentage increase per level above 1)
ENEMY_LEVEL_STAT_SCALING: Dict[str, float] = {
    "max_hp": 0.15,    # +15% per level
    "attack": 0.10,    # +10% per level
    "defense": 0.10,   # +10% per level
    "magic": 0.10,     # +10% per level
    "speed": 0.05,     # +5% per level
    "luck": 0.05,      # +5% per level
    "max_sp": 0.08,    # +8% per level
}

# Base EXP reward per enemy level
BASE_ENEMY_EXP_PER_LEVEL = 15

# Base gold reward per enemy level
BASE_ENEMY_GOLD_PER_LEVEL = 5


def scale_enemy_stat(base_value: int, enemy_level: int, stat_name: str, difficulty: str = "normal") -> int:
    """
    Scale an enemy's base stat based on their level and difficulty.

    Args:
        base_value: The base stat value defined in the encounter
        enemy_level: The enemy's level (1-10)
        stat_name: The stat being scaled (e.g., "max_hp", "attack")
        difficulty: The enemy's difficulty tier

    Returns:
        The scaled stat value as an integer
    """
    # Get scaling factor for this stat (default to 10% if not specified)
    level_scaling = ENEMY_LEVEL_STAT_SCALING.get(stat_name, 0.10)

    # Calculate level multiplier (level 1 = 1.0, level 2 = 1.0 + scaling, etc.)
    level_multiplier = 1.0 + (enemy_level - 1) * level_scaling

    # Get difficulty multiplier
    difficulty_multiplier = DIFFICULTY_STAT_MULTIPLIERS.get(difficulty, 1.0)

    # Apply both multipliers
    scaled_value = base_value * level_multiplier * difficulty_multiplier

    return max(1, int(scaled_value))


def calculate_enemy_exp_reward(enemy_level: int, difficulty: str = "normal", base_exp: int = 0) -> int:
    """
    Calculate EXP reward for defeating an enemy.

    Args:
        enemy_level: The enemy's level
        difficulty: The enemy's difficulty tier
        base_exp: Optional base EXP override (if 0, uses formula)

    Returns:
        EXP reward as an integer
    """
    if base_exp > 0:
        # Scale provided base EXP by level and difficulty
        level_multiplier = 1.0 + (enemy_level - 1) * 0.20  # +20% per level
        difficulty_multiplier = DIFFICULTY_REWARD_MULTIPLIERS.get(difficulty, 1.0)
        return max(1, int(base_exp * level_multiplier * difficulty_multiplier))

    # Calculate from formula: base per level * level * difficulty
    base = BASE_ENEMY_EXP_PER_LEVEL * enemy_level
    difficulty_multiplier = DIFFICULTY_REWARD_MULTIPLIERS.get(difficulty, 1.0)
    return max(1, int(base * difficulty_multiplier))


def calculate_enemy_gold_reward(enemy_level: int, difficulty: str = "normal", base_gold: int = 0) -> int:
    """
    Calculate gold reward for defeating an enemy.

    Args:
        enemy_level: The enemy's level
        difficulty: The enemy's difficulty tier
        base_gold: Optional base gold override (if 0, uses formula)

    Returns:
        Gold reward as an integer
    """
    if base_gold > 0:
        # Scale provided base gold by level and difficulty
        level_multiplier = 1.0 + (enemy_level - 1) * 0.15  # +15% per level
        difficulty_multiplier = DIFFICULTY_REWARD_MULTIPLIERS.get(difficulty, 1.0)
        return max(1, int(base_gold * level_multiplier * difficulty_multiplier))

    # Calculate from formula: base per level * level * difficulty
    base = BASE_ENEMY_GOLD_PER_LEVEL * enemy_level
    difficulty_multiplier = DIFFICULTY_REWARD_MULTIPLIERS.get(difficulty, 1.0)
    return max(1, int(base * difficulty_multiplier))


def get_scaled_enemy_stats(
    base_stats: Dict[str, int],
    enemy_level: int,
    difficulty: str = "normal"
) -> Dict[str, int]:
    """
    Scale all enemy stats based on level and difficulty.

    Args:
        base_stats: Dictionary of base stat values
        enemy_level: The enemy's level
        difficulty: The enemy's difficulty tier

    Returns:
        Dictionary of scaled stat values
    """
    scaled = {}
    for stat_name, base_value in base_stats.items():
        scaled[stat_name] = scale_enemy_stat(base_value, enemy_level, stat_name, difficulty)

    # Ensure HP starts at max
    if "max_hp" in scaled and "hp" in scaled:
        scaled["hp"] = scaled["max_hp"]
    if "max_sp" in scaled and "sp" in scaled:
        scaled["sp"] = scaled["max_sp"]

    return scaled


# Element damage multipliers
ELEMENT_WEAK_MULTIPLIER = 1.5  # 50% more damage when hitting weakness
ELEMENT_RESIST_MULTIPLIER = 0.5  # 50% less damage when hitting resistance
ELEMENT_IMMUNE_MULTIPLIER = 0.0  # No damage when immune
ELEMENT_ABSORB_MULTIPLIER = -0.5  # Heals for 50% of damage when absorbing


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
        return self.hp

    def heal(self, amount: int) -> int:
        """Heal HP."""
        self.hp = min(self.max_hp, self.hp + amount)
        return self.hp

    def restore_sp(self, amount: int) -> int:
        """Restore SP."""
        self.sp = min(self.max_sp, self.sp + amount)
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

    def remove_status_effect(self, status_id: str) -> bool:
        """Remove a status effect."""
        if status_id in self.status_effects:
            del self.status_effects[status_id]
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

    def get_effective_attack(self) -> int:
        """Get attack value with equipment and status effect modifiers."""
        attack = self._get_base_with_equipment("attack")
        # Limb missing reduces attack
        if "limb_arm_left_missing" in self.status_effects:
            attack = int(attack * 0.7)  # 30% reduction
        if "limb_arm_right_missing" in self.status_effects:
            attack = int(attack * 0.7)
        # Burn reduces attack by 20% per stack
        if "burn" in self.status_effects:
            burn_stacks = self.status_effects["burn"].stacks
            attack = int(attack * max(0.2, 1.0 - 0.2 * burn_stacks))
        return attack

    def get_effective_defense(self) -> int:
        """Get defense value with equipment modifiers."""
        return self._get_base_with_equipment("defense")

    def get_effective_magic(self) -> int:
        """Get magic value with equipment modifiers."""
        return self._get_base_with_equipment("magic")

    def get_effective_speed(self) -> int:
        """Get speed value with equipment and status effect modifiers."""
        speed = self._get_base_with_equipment("speed")
        # Leg missing reduces speed
        if "limb_leg_left_missing" in self.status_effects:
            speed = int(speed * 0.6)
        if "limb_leg_right_missing" in self.status_effects:
            speed = int(speed * 0.6)
        # Frozen drastically reduces speed
        if "frozen" in self.status_effects:
            speed = int(speed * 0.1)  # 90% reduction
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
        if "sleep" in self.status_effects:
            del self.status_effects["sleep"]
            return True
        return False

    def get_effective_luck(self) -> int:
        """Get luck value with equipment modifiers."""
        return self._get_base_with_equipment("luck")

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
