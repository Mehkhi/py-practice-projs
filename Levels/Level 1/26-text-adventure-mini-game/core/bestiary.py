"""Bestiary system for tracking discovered enemies."""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum


class DiscoveryLevel(Enum):
    """How much information is known about an enemy."""
    UNKNOWN = 0      # Never encountered
    ENCOUNTERED = 1  # Seen in battle but not defeated
    DEFEATED = 2     # Defeated at least once
    STUDIED = 3      # Defeated multiple times, full info revealed


# Thresholds for discovery levels
DEFEAT_THRESHOLD_STUDIED = 5  # Defeats needed for full info


@dataclass
class BestiaryEntry:
    """A single entry in the bestiary for one enemy type."""
    enemy_type: str  # Unique identifier (e.g., "slime", "goblin")
    name: str  # Display name
    sprite_id: str = "enemy"

    # Discovery tracking
    times_encountered: int = 0
    times_defeated: int = 0
    discovery_level: DiscoveryLevel = field(default=DiscoveryLevel.UNKNOWN)

    # Base stats (revealed progressively)
    base_hp: int = 0
    base_sp: int = 0
    base_attack: int = 0
    base_defense: int = 0
    base_magic: int = 0
    base_speed: int = 0

    # Elemental properties
    weaknesses: List[str] = field(default_factory=list)
    resistances: List[str] = field(default_factory=list)
    immunities: List[str] = field(default_factory=list)
    absorbs: List[str] = field(default_factory=list)

    # Flavor text
    description: str = ""
    category: str = "monster"  # e.g., "beast", "undead", "humanoid", "elemental"

    # Locations where encountered
    locations: List[str] = field(default_factory=list)

    # Drops/rewards observed
    observed_drops: List[str] = field(default_factory=list)

    def record_encounter(self) -> None:
        """Record that this enemy was encountered in battle."""
        self.times_encountered += 1
        if self.discovery_level == DiscoveryLevel.UNKNOWN:
            self.discovery_level = DiscoveryLevel.ENCOUNTERED

    def record_defeat(self) -> None:
        """Record that this enemy was defeated."""
        self.times_defeated += 1
        if self.discovery_level.value < DiscoveryLevel.DEFEATED.value:
            self.discovery_level = DiscoveryLevel.DEFEATED
        if self.times_defeated >= DEFEAT_THRESHOLD_STUDIED:
            self.discovery_level = DiscoveryLevel.STUDIED

    def add_location(self, location: str) -> None:
        """Add a location where this enemy was encountered."""
        if location and location not in self.locations:
            self.locations.append(location)

    def add_observed_drop(self, item_id: str) -> None:
        """Record an item drop from this enemy."""
        if item_id and item_id not in self.observed_drops:
            self.observed_drops.append(item_id)

    def get_visible_stats(self) -> Dict[str, Any]:
        """Get stats visible at current discovery level."""
        if self.discovery_level == DiscoveryLevel.UNKNOWN:
            return {}

        result = {
            "name": self.name,
            "times_encountered": self.times_encountered,
            "times_defeated": self.times_defeated,
        }

        if self.discovery_level.value >= DiscoveryLevel.ENCOUNTERED.value:
            result["category"] = self.category
            result["sprite_id"] = self.sprite_id
            if self.description:
                result["description"] = self.description

        if self.discovery_level.value >= DiscoveryLevel.DEFEATED.value:
            result["base_hp"] = self.base_hp
            result["weaknesses"] = self.weaknesses
            result["locations"] = self.locations
            if self.observed_drops:
                result["observed_drops"] = self.observed_drops

        if self.discovery_level == DiscoveryLevel.STUDIED:
            result["base_sp"] = self.base_sp
            result["base_attack"] = self.base_attack
            result["base_defense"] = self.base_defense
            result["base_magic"] = self.base_magic
            result["base_speed"] = self.base_speed
            result["resistances"] = self.resistances
            result["immunities"] = self.immunities
            result["absorbs"] = self.absorbs

        return result

    def serialize(self) -> Dict[str, Any]:
        """Serialize entry to JSON-safe dict."""
        return {
            "enemy_type": self.enemy_type,
            "name": self.name,
            "sprite_id": self.sprite_id,
            "times_encountered": self.times_encountered,
            "times_defeated": self.times_defeated,
            "discovery_level": self.discovery_level.value,
            "base_hp": self.base_hp,
            "base_sp": self.base_sp,
            "base_attack": self.base_attack,
            "base_defense": self.base_defense,
            "base_magic": self.base_magic,
            "base_speed": self.base_speed,
            "weaknesses": self.weaknesses,
            "resistances": self.resistances,
            "immunities": self.immunities,
            "absorbs": self.absorbs,
            "description": self.description,
            "category": self.category,
            "locations": self.locations,
            "observed_drops": self.observed_drops,
        }

    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> "BestiaryEntry":
        """Deserialize entry from dict."""
        entry = cls(
            enemy_type=data["enemy_type"],
            name=data["name"],
            sprite_id=data.get("sprite_id", "enemy"),
        )
        entry.times_encountered = data.get("times_encountered", 0)
        entry.times_defeated = data.get("times_defeated", 0)
        entry.discovery_level = DiscoveryLevel(data.get("discovery_level", 0))
        entry.base_hp = data.get("base_hp", 0)
        entry.base_sp = data.get("base_sp", 0)
        entry.base_attack = data.get("base_attack", 0)
        entry.base_defense = data.get("base_defense", 0)
        entry.base_magic = data.get("base_magic", 0)
        entry.base_speed = data.get("base_speed", 0)
        entry.weaknesses = list(data.get("weaknesses", []))
        entry.resistances = list(data.get("resistances", []))
        entry.immunities = list(data.get("immunities", []))
        entry.absorbs = list(data.get("absorbs", []))
        entry.description = data.get("description", "")
        entry.category = data.get("category", "monster")
        entry.locations = list(data.get("locations", []))
        entry.observed_drops = list(data.get("observed_drops", []))
        return entry


# Default descriptions for enemy categories
CATEGORY_DESCRIPTIONS = {
    "slime": "A gelatinous creature that absorbs nutrients from anything it touches.",
    "goblin": "Small, cunning creatures that live in caves and raid travelers.",
    "wolf": "Fierce pack hunters that roam the wilderness.",
    "spider": "Venomous arachnids that spin webs to trap prey.",
    "plant": "Dangerous flora that has developed predatory instincts.",
    "humanoid": "Intelligent beings with human-like form.",
    "beast": "Wild creatures driven by primal instincts.",
    "undead": "Creatures that have risen from death, animated by dark magic.",
    "elemental": "Beings of pure elemental energy.",
    "demon": "Malevolent entities from the dark realms.",
    "giant": "Massive creatures of tremendous strength.",
    "construct": "Artificial beings created through magic or craftsmanship.",
    "reptile": "Cold-blooded creatures with scales and sharp claws.",
    "monster": "A dangerous creature of unknown origin.",
    "human": "A hostile human adversary.",
    "orc": "Brutish warriors known for their strength and aggression.",
}


class Bestiary:
    """Manages the player's discovered enemy compendium."""

    def __init__(self):
        self.entries: Dict[str, BestiaryEntry] = {}

    def get_or_create_entry(
        self,
        enemy_type: str,
        name: str,
        sprite_id: str = "enemy",
        category: str = "monster",
        base_stats: Optional[Dict[str, int]] = None,
        weaknesses: Optional[List[str]] = None,
        resistances: Optional[List[str]] = None,
        immunities: Optional[List[str]] = None,
        absorbs: Optional[List[str]] = None,
    ) -> BestiaryEntry:
        """Get existing entry or create new one for an enemy type."""
        if enemy_type not in self.entries:
            entry = BestiaryEntry(
                enemy_type=enemy_type,
                name=name,
                sprite_id=sprite_id,
                category=category,
                description=CATEGORY_DESCRIPTIONS.get(category, CATEGORY_DESCRIPTIONS["monster"]),
            )

            # Set base stats if provided
            if base_stats:
                entry.base_hp = base_stats.get("max_hp", 0)
                entry.base_sp = base_stats.get("max_sp", 0)
                entry.base_attack = base_stats.get("attack", 0)
                entry.base_defense = base_stats.get("defense", 0)
                entry.base_magic = base_stats.get("magic", 0)
                entry.base_speed = base_stats.get("speed", 0)

            # Set elemental properties
            if weaknesses:
                entry.weaknesses = list(weaknesses)
            if resistances:
                entry.resistances = list(resistances)
            if immunities:
                entry.immunities = list(immunities)
            if absorbs:
                entry.absorbs = list(absorbs)

            self.entries[enemy_type] = entry

        return self.entries[enemy_type]

    def record_encounter(
        self,
        enemy_type: str,
        name: str,
        sprite_id: str = "enemy",
        category: str = "monster",
        location: Optional[str] = None,
        base_stats: Optional[Dict[str, int]] = None,
        weaknesses: Optional[List[str]] = None,
        resistances: Optional[List[str]] = None,
        immunities: Optional[List[str]] = None,
        absorbs: Optional[List[str]] = None,
    ) -> BestiaryEntry:
        """Record an encounter with an enemy."""
        entry = self.get_or_create_entry(
            enemy_type=enemy_type,
            name=name,
            sprite_id=sprite_id,
            category=category,
            base_stats=base_stats,
            weaknesses=weaknesses,
            resistances=resistances,
            immunities=immunities,
            absorbs=absorbs,
        )
        entry.record_encounter()
        if location:
            entry.add_location(location)
        return entry

    def record_defeat(
        self,
        enemy_type: str,
        name: str,
        sprite_id: str = "enemy",
        category: str = "monster",
        drops: Optional[List[str]] = None,
        base_stats: Optional[Dict[str, int]] = None,
        weaknesses: Optional[List[str]] = None,
        resistances: Optional[List[str]] = None,
        immunities: Optional[List[str]] = None,
        absorbs: Optional[List[str]] = None,
    ) -> BestiaryEntry:
        """Record defeating an enemy."""
        entry = self.get_or_create_entry(
            enemy_type=enemy_type,
            name=name,
            sprite_id=sprite_id,
            category=category,
            base_stats=base_stats,
            weaknesses=weaknesses,
            resistances=resistances,
            immunities=immunities,
            absorbs=absorbs,
        )
        entry.record_defeat()
        if drops:
            for item_id in drops:
                entry.add_observed_drop(item_id)
        return entry

    def get_entry(self, enemy_type: str) -> Optional[BestiaryEntry]:
        """Get a bestiary entry by enemy type."""
        return self.entries.get(enemy_type)

    def get_all_entries(self) -> List[BestiaryEntry]:
        """Get all bestiary entries, sorted by name."""
        return sorted(self.entries.values(), key=lambda e: e.name)

    def get_discovered_entries(self) -> List[BestiaryEntry]:
        """Get only entries that have been discovered (encountered at least once)."""
        return sorted(
            [e for e in self.entries.values() if e.discovery_level != DiscoveryLevel.UNKNOWN],
            key=lambda e: e.name
        )

    def get_entries_by_category(self, category: str) -> List[BestiaryEntry]:
        """Get all entries of a specific category."""
        return sorted(
            [e for e in self.entries.values() if e.category == category],
            key=lambda e: e.name
        )

    def get_discovery_stats(self) -> Dict[str, int]:
        """Get statistics about bestiary completion."""
        total = len(self.entries)
        encountered = sum(1 for e in self.entries.values() if e.discovery_level.value >= DiscoveryLevel.ENCOUNTERED.value)
        defeated = sum(1 for e in self.entries.values() if e.discovery_level.value >= DiscoveryLevel.DEFEATED.value)
        studied = sum(1 for e in self.entries.values() if e.discovery_level == DiscoveryLevel.STUDIED)

        return {
            "total": total,
            "encountered": encountered,
            "defeated": defeated,
            "studied": studied,
        }

    def get_categories(self) -> List[str]:
        """Get list of all categories with discovered entries."""
        categories = set()
        for entry in self.entries.values():
            if entry.discovery_level != DiscoveryLevel.UNKNOWN:
                categories.add(entry.category)
        return sorted(categories)

    def serialize(self) -> Dict[str, Any]:
        """Serialize bestiary to JSON-safe dict."""
        return {
            "entries": {
                enemy_type: entry.serialize()
                for enemy_type, entry in self.entries.items()
            }
        }

    def deserialize(self, data: Dict[str, Any]) -> None:
        """Deserialize bestiary from dict."""
        self.entries.clear()
        entries_data = data.get("entries", {})
        for enemy_type, entry_data in entries_data.items():
            self.entries[enemy_type] = BestiaryEntry.deserialize(entry_data)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Bestiary":
        """Create bestiary from serialized dict."""
        bestiary = cls()
        bestiary.deserialize(data)
        return bestiary

    def seed_from_encounter_data(
        self,
        encounters_data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> int:
        """
        Seed the bestiary with all unique enemies from encounter data.

        Creates entries for enemies that haven't been encountered yet,
        setting them to DiscoveryLevel.UNKNOWN. This allows the bestiary
        to show accurate completion stats (discovered vs total).

        Args:
            encounters_data: Dict of encounter_id -> encounter definition,
                             each containing an 'enemies' list.

        Returns:
            Number of new entries added.
        """
        added = 0
        seen_types: set = set()
        metadata = metadata or {}

        for encounter_id, encounter in encounters_data.items():
            if not isinstance(encounter, dict):
                continue
            enemies = encounter.get("enemies", [])
            if not isinstance(enemies, list):
                continue

            for enemy_data in enemies:
                if not isinstance(enemy_data, dict):
                    continue

                # Use 'name' as the unique identifier for enemy type
                # Fall back to 'id' if name not present
                enemy_name = enemy_data.get("name", "")
                enemy_type = enemy_data.get("type", enemy_name.lower().replace(" ", "_"))
                if not enemy_type or enemy_type in seen_types:
                    continue
                seen_types.add(enemy_type)

                # Apply metadata to existing entries and skip creation
                existing_entry = self.entries.get(enemy_type)
                if existing_entry:
                    meta = metadata.get(enemy_type)
                    if meta:
                        self._apply_metadata(existing_entry, meta)
                    continue

                # Create entry with UNKNOWN discovery level
                entry = BestiaryEntry(
                    enemy_type=enemy_type,
                    name=enemy_name or enemy_type.replace("_", " ").title(),
                    sprite_id=enemy_data.get("sprite_id", "enemy"),
                    category=enemy_data.get("type", "monster"),
                    description=CATEGORY_DESCRIPTIONS.get(
                        enemy_data.get("type", "monster"),
                        CATEGORY_DESCRIPTIONS["monster"]
                    ),
                )

                # Set base stats from enemy data
                entry.base_hp = enemy_data.get("max_hp", 0)
                entry.base_sp = enemy_data.get("max_sp", 0)
                entry.base_attack = enemy_data.get("attack", 0)
                entry.base_defense = enemy_data.get("defense", 0)
                entry.base_magic = enemy_data.get("magic", 0)
                entry.base_speed = enemy_data.get("speed", 0)

                # Set elemental properties
                entry.weaknesses = list(enemy_data.get("weaknesses", []))
                entry.resistances = list(enemy_data.get("resistances", []))
                entry.immunities = list(enemy_data.get("immunities", []))
                entry.absorbs = list(enemy_data.get("absorbs", []))

                # Entry stays at UNKNOWN discovery level
                meta = metadata.get(enemy_type)
                if meta:
                    self._apply_metadata(entry, meta)

                self.entries[enemy_type] = entry
                added += 1

        return added

    def _apply_metadata(self, entry: BestiaryEntry, metadata: Dict[str, Any]) -> None:
        """Populate entry fields with aggregated metadata if missing."""
        default_description = CATEGORY_DESCRIPTIONS.get(entry.category, CATEGORY_DESCRIPTIONS["monster"])
        meta_description = metadata.get("description")
        if meta_description and (not entry.description or entry.description == default_description):
            entry.description = meta_description

        sprite_candidate = metadata.get("sprite_id")
        if sprite_candidate and entry.sprite_id == "enemy":
            entry.sprite_id = sprite_candidate

        category_candidate = metadata.get("category")
        if category_candidate:
            entry.category = category_candidate

        for attr in ("weaknesses", "resistances", "immunities", "absorbs"):
            current = getattr(entry, attr)
            if not current and metadata.get(attr):
                setattr(entry, attr, list(metadata[attr]))

        for location in metadata.get("locations", []):
            entry.add_location(location)

        for drop in metadata.get("drops", []):
            entry.add_observed_drop(drop)

    def get_all_entries_including_unknown(self) -> List[BestiaryEntry]:
        """Get all bestiary entries including undiscovered ones, sorted by name."""
        return sorted(self.entries.values(), key=lambda e: e.name)
