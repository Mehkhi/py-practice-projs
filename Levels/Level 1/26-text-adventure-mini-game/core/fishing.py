"""Fishing mini-game system for catching fish."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple
import random


class FishRarity(Enum):
    """Rarity levels for fish."""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    LEGENDARY = "legendary"


class WaterType(Enum):
    """Types of water where fishing is possible."""
    FRESHWATER = "freshwater"  # Rivers, lakes, ponds
    SALTWATER = "saltwater"    # Ocean, sea
    SWAMP = "swamp"            # Murky swamp water
    MAGICAL = "magical"        # Enchanted pools


@dataclass
class Fish:
    """A fish that can be caught."""
    fish_id: str
    name: str
    rarity: FishRarity
    base_value: int  # Gold value when sold
    water_types: List[WaterType]  # Where it can be found
    time_periods: List[str]  # When it can be caught (TimeOfDay values, empty = any)
    min_size: float  # Minimum size in units
    max_size: float  # Maximum size
    catch_difficulty: int  # 1-10, affects mini-game difficulty
    description: str
    item_id: str  # Corresponding item ID when in inventory


@dataclass
class FishingSpot:
    """A location where fishing is possible."""
    spot_id: str
    name: str
    map_id: str
    x: int
    y: int
    water_type: WaterType
    is_premium: bool = False  # Premium spots have better rates
    fish_pool: List[str] = field(default_factory=list)  # Fish IDs available here
    rarity_modifiers: Dict[str, float] = field(default_factory=dict)  # Rarity -> multiplier


@dataclass
class CaughtFish:
    """A specific fish that was caught."""
    fish: Fish
    size: float  # Actual size caught

    @property
    def value(self) -> int:
        """Calculate value based on size (larger = more valuable)."""
        size_ratio = self.size / self.fish.max_size
        multiplier = 0.5 + (size_ratio * 1.0)  # 0.5x to 1.5x base value
        return int(self.fish.base_value * multiplier)

    @property
    def size_category(self) -> str:
        """Get size description."""
        if self.fish.max_size == self.fish.min_size:
            return "medium"
        ratio = (self.size - self.fish.min_size) / (self.fish.max_size - self.fish.min_size)
        if ratio < 0.25:
            return "tiny"
        elif ratio < 0.5:
            return "small"
        elif ratio < 0.75:
            return "medium"
        elif ratio < 0.95:
            return "large"
        else:
            return "enormous"


class FishingSystem:
    """Manages fishing mechanics.

    Implements the Saveable protocol for automatic save/load via SaveContext.
    """

    save_key: str = "fishing"

    def __init__(self, fish_db: Dict[str, Fish], spots: Dict[str, FishingSpot]):
        self.fish_db = fish_db
        self.spots = spots
        self.player_records: Dict[str, CaughtFish] = {}  # Best catch per fish type
        self.total_catches: int = 0
        self.catches_per_spot: Dict[str, int] = {}

    def get_spot_at(self, map_id: str, x: int, y: int) -> Optional[FishingSpot]:
        """Get fishing spot at given location."""
        for spot in self.spots.values():
            if spot.map_id == map_id and spot.x == x and spot.y == y:
                return spot
        return None

    def get_available_fish(self, spot: FishingSpot, time_of_day: str) -> List[Fish]:
        """Get fish that can be caught at this spot at this time."""
        available = []
        for fish_id in spot.fish_pool:
            fish = self.fish_db.get(fish_id)
            if not fish:
                continue

            # Check water type compatibility
            if spot.water_type not in fish.water_types:
                continue

            # Check time restrictions (empty list = any time)
            if fish.time_periods and time_of_day not in fish.time_periods:
                continue

            available.append(fish)
        return available

    def calculate_catch_chance(self, fish: Fish, spot: FishingSpot,
                               has_bait: bool = False, rod_quality: int = 1) -> float:
        """
        Calculate probability of catching a specific fish.

        Factors: rarity, spot modifiers, bait, rod quality
        """
        # Base chance inversely related to rarity
        rarity_base_chances = {
            FishRarity.COMMON: 0.8,
            FishRarity.UNCOMMON: 0.5,
            FishRarity.RARE: 0.2,
            FishRarity.LEGENDARY: 0.05,
        }
        base_chance = rarity_base_chances.get(fish.rarity, 0.5)

        # Apply spot rarity modifiers
        rarity_str = fish.rarity.value
        modifier = spot.rarity_modifiers.get(rarity_str, 1.0)
        chance = base_chance * modifier

        # Bait bonus
        if has_bait:
            chance += 0.2

        # Rod quality bonus (0.1 per level, max 1.0)
        rod_bonus = min(0.1 * rod_quality, 1.0)
        chance += rod_bonus

        # Cap at 0.0-1.0
        return max(0.0, min(1.0, chance))

    def roll_for_fish(self, spot: FishingSpot, time_of_day: str,
                      has_bait: bool = False, rod_quality: int = 1) -> Optional[Fish]:
        """
        Attempt to determine what fish bites.

        Returns None if nothing bites.
        """
        available_fish = self.get_available_fish(spot, time_of_day)
        if not available_fish:
            return None

        # Base chance that any fish bites (70%)
        if random.random() > 0.7:
            return None

        # Calculate catch chances for each fish
        fish_chances = []
        for fish in available_fish:
            chance = self.calculate_catch_chance(fish, spot, has_bait, rod_quality)
            fish_chances.append((fish, chance))

        # Weight by catch chance and select
        total_weight = sum(chance for _, chance in fish_chances)
        if total_weight <= 0:
            return None

        # Normalize weights
        weights = [chance / total_weight for _, chance in fish_chances]

        # Select fish by weighted probability
        selected = random.choices(
            [fish for fish, _ in fish_chances],
            weights=weights,
            k=1
        )[0]

        return selected

    def generate_fish_size(self, fish: Fish) -> float:
        """Generate random size within fish's range."""
        return random.uniform(fish.min_size, fish.max_size)

    def record_catch(self, caught: CaughtFish, spot_id: Optional[str] = None) -> bool:
        """
        Record a catch. Returns True if it's a new personal record.
        """
        fish_id = caught.fish.fish_id
        existing_record = self.player_records.get(fish_id)

        self.total_catches += 1
        if spot_id:
            self.catches_per_spot[spot_id] = self.catches_per_spot.get(spot_id, 0) + 1

        new_record = False
        if existing_record is None or caught.size > existing_record.size:
            self.player_records[fish_id] = caught
            new_record = True
        return new_record

    def get_fishing_stats(self) -> Dict:
        """Get player's fishing statistics."""
        return {
            "total_caught": self.total_catches,
            "records": {fid: c.size for fid, c in self.player_records.items()},
            "catches_per_spot": dict(self.catches_per_spot),
        }

    def serialize(self) -> Dict:
        """Serialize fishing state for saving."""
        return {
            "player_records": {
                fish_id: {
                    "fish_id": caught.fish.fish_id,
                    "size": caught.size,
                }
                for fish_id, caught in self.player_records.items()
            },
            "total_catches": self.total_catches,
            "catches_per_spot": dict(self.catches_per_spot),
        }

    @classmethod
    def deserialize(cls, data: Dict, fish_db: Dict[str, Fish],
                    spots: Dict[str, FishingSpot]) -> "FishingSystem":
        """Deserialize from save data."""
        system = cls(fish_db, spots)
        records_data = data.get("player_records", {})

        for fish_id, record_data in records_data.items():
            fish = fish_db.get(record_data["fish_id"])
            if fish:
                caught = CaughtFish(fish=fish, size=record_data["size"])
                system.player_records[fish_id] = caught

        system.total_catches = data.get("total_catches", 0)
        system.catches_per_spot = data.get("catches_per_spot", {})

        return system

    def deserialize_into(self, data: Dict) -> None:
        """Restore state from saved data (Saveable protocol)."""
        records_data = data.get("player_records", {})
        self.player_records.clear()

        for fish_id, record_data in records_data.items():
            fish = self.fish_db.get(record_data["fish_id"])
            if fish:
                caught = CaughtFish(fish=fish, size=record_data["size"])
                self.player_records[fish_id] = caught

        self.total_catches = data.get("total_catches", 0)
        self.catches_per_spot = data.get("catches_per_spot", {})
