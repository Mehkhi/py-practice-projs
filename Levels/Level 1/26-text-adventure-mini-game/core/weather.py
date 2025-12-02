"""Weather system for dynamic environmental effects."""

import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Tuple, Optional, List

from .constants import DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT


class WeatherType(Enum):
    """Available weather conditions."""
    CLEAR = "clear"
    CLOUDY = "cloudy"
    RAIN = "rain"
    HEAVY_RAIN = "heavy_rain"
    THUNDERSTORM = "thunderstorm"
    SNOW = "snow"
    BLIZZARD = "blizzard"
    FOG = "fog"
    SANDSTORM = "sandstorm"
    ASH = "ash"  # For volcanic areas


# Visual tints for each weather type (R, G, B, Alpha)
WEATHER_TINTS: Dict[WeatherType, Tuple[int, int, int, int]] = {
    WeatherType.CLEAR: (255, 255, 255, 0),          # No tint
    WeatherType.CLOUDY: (180, 180, 190, 30),        # Slight gray
    WeatherType.RAIN: (100, 110, 130, 40),          # Blue-gray
    WeatherType.HEAVY_RAIN: (70, 80, 100, 60),      # Darker blue-gray
    WeatherType.THUNDERSTORM: (50, 50, 70, 70),     # Dark stormy
    WeatherType.SNOW: (220, 230, 255, 25),          # Cool white-blue
    WeatherType.BLIZZARD: (200, 210, 240, 50),      # Heavier white-blue
    WeatherType.FOG: (200, 200, 210, 80),           # Gray fog
    WeatherType.SANDSTORM: (210, 180, 130, 60),     # Sandy brown
    WeatherType.ASH: (100, 90, 90, 50),             # Dark gray ash
}

# Ambient light modifiers for weather (multiplied with time-of-day ambient)
WEATHER_AMBIENT: Dict[WeatherType, float] = {
    WeatherType.CLEAR: 1.0,
    WeatherType.CLOUDY: 0.85,
    WeatherType.RAIN: 0.7,
    WeatherType.HEAVY_RAIN: 0.55,
    WeatherType.THUNDERSTORM: 0.4,
    WeatherType.SNOW: 0.9,
    WeatherType.BLIZZARD: 0.6,
    WeatherType.FOG: 0.75,
    WeatherType.SANDSTORM: 0.65,
    WeatherType.ASH: 0.7,
}

# Particle density for weather effects (particles per frame at scale 1)
WEATHER_PARTICLE_DENSITY: Dict[WeatherType, int] = {
    WeatherType.CLEAR: 0,
    WeatherType.CLOUDY: 0,
    WeatherType.RAIN: 15,
    WeatherType.HEAVY_RAIN: 30,
    WeatherType.THUNDERSTORM: 25,
    WeatherType.SNOW: 10,
    WeatherType.BLIZZARD: 25,
    WeatherType.FOG: 0,  # Fog uses overlay, not particles
    WeatherType.SANDSTORM: 20,
    WeatherType.ASH: 12,
}

# Combat stat modifiers for weather conditions
# Format: {"stat": modifier} where modifier is added to the stat
WEATHER_COMBAT_EFFECTS: Dict[WeatherType, Dict[str, int]] = {
    WeatherType.CLEAR: {},
    WeatherType.CLOUDY: {},
    WeatherType.RAIN: {"speed": -1, "luck": -1},
    WeatherType.HEAVY_RAIN: {"speed": -2, "luck": -2, "attack": -1},
    WeatherType.THUNDERSTORM: {"speed": -2, "luck": -3, "magic": 2},  # Lightning boosts magic
    WeatherType.SNOW: {"speed": -1},
    WeatherType.BLIZZARD: {"speed": -3, "attack": -2, "defense": -1},
    WeatherType.FOG: {"luck": -2},  # Harder to hit/dodge
    WeatherType.SANDSTORM: {"speed": -2, "luck": -3},
    WeatherType.ASH: {"speed": -1, "luck": -1},
}


@dataclass
class WeatherParticle:
    """A single weather particle for visual effects."""
    x: float
    y: float
    vx: float  # Velocity X
    vy: float  # Velocity Y
    size: int
    alpha: int
    lifetime: float = 0.0
    max_lifetime: float = 2.0


@dataclass
class WeatherSystem:
    """
    Manages weather conditions and transitions.

    Implements the Saveable protocol for automatic save/load via SaveContext.

    Weather can change naturally over time or be set for specific maps.
    Supports smooth transitions between weather states.

    Attributes:
        current_weather: The current weather condition
        transition_weather: Weather we're transitioning to (if any)
        transition_progress: Progress of weather transition (0.0 to 1.0)
        change_timer: Time until next potential weather change
        enabled: Whether weather system is active
        save_key: Key used for this manager in save data ('weather')
    """
    current_weather: WeatherType = WeatherType.CLEAR
    transition_weather: Optional[WeatherType] = None
    transition_progress: float = 0.0
    transition_duration: float = 5.0  # Seconds for weather transition
    change_timer: float = 300.0  # Seconds until next weather check
    min_change_interval: float = 180.0  # Minimum seconds between changes
    max_change_interval: float = 600.0  # Maximum seconds between changes
    enabled: bool = True
    paused: bool = False

    # Class attribute for Saveable protocol
    save_key: str = "weather"

    # Map-specific weather override
    map_weather_override: Optional[WeatherType] = None

    # Particles for visual effects
    particles: List[WeatherParticle] = field(default_factory=list)
    max_particles: int = 200

    # Lightning flash state (for thunderstorms)
    lightning_flash: float = 0.0
    lightning_cooldown: float = 0.0

    # Weather probabilities for natural changes (can be overridden per biome)
    weather_weights: Dict[WeatherType, float] = field(default_factory=lambda: {
        WeatherType.CLEAR: 0.4,
        WeatherType.CLOUDY: 0.25,
        WeatherType.RAIN: 0.15,
        WeatherType.HEAVY_RAIN: 0.08,
        WeatherType.THUNDERSTORM: 0.05,
        WeatherType.FOG: 0.07,
    })

    def update(self, dt: float, screen_width: int = DEFAULT_WINDOW_WIDTH, screen_height: int = DEFAULT_WINDOW_HEIGHT) -> None:
        """
        Update weather state and particles.

        Args:
            dt: Delta time in seconds
            screen_width: Screen width for particle bounds
            screen_height: Screen height for particle bounds
        """
        if not self.enabled or self.paused:
            return

        # Update weather transition
        if self.transition_weather is not None:
            self.transition_progress += dt / self.transition_duration
            if self.transition_progress >= 1.0:
                self.current_weather = self.transition_weather
                self.transition_weather = None
                self.transition_progress = 0.0

        # Update change timer (only if no map override)
        if self.map_weather_override is None:
            self.change_timer -= dt
            if self.change_timer <= 0:
                self._try_change_weather()
                self.change_timer = random.uniform(
                    self.min_change_interval,
                    self.max_change_interval
                )

        # Update particles
        self._update_particles(dt, screen_width, screen_height)

        # Update lightning for thunderstorms
        self._update_lightning(dt)

    def _try_change_weather(self) -> None:
        """Attempt to change weather based on probabilities."""
        if not self.weather_weights:
            return

        # Weighted random selection
        total = sum(self.weather_weights.values())
        if total <= 0:
            return

        roll = random.uniform(0, total)
        cumulative = 0.0

        for weather, weight in self.weather_weights.items():
            cumulative += weight
            if roll <= cumulative:
                if weather != self.current_weather:
                    self.transition_to(weather)
                break

    def _update_particles(self, dt: float, screen_width: int, screen_height: int) -> None:
        """Update weather particles."""
        active_weather = self._get_effective_weather()
        density = WEATHER_PARTICLE_DENSITY.get(active_weather, 0)

        # Spawn new particles
        if density > 0 and len(self.particles) < self.max_particles:
            spawn_count = min(density, self.max_particles - len(self.particles))
            for _ in range(spawn_count):
                particle = self._create_particle(active_weather, screen_width, screen_height)
                if particle:
                    self.particles.append(particle)

        # Update existing particles
        particles_to_remove = []
        for particle in self.particles:
            particle.x += particle.vx * dt
            particle.y += particle.vy * dt
            particle.lifetime += dt

            # Remove particles that are off-screen or expired
            if (particle.y > screen_height + 20 or
                particle.x < -20 or particle.x > screen_width + 20 or
                particle.lifetime > particle.max_lifetime):
                particles_to_remove.append(particle)

        for particle in particles_to_remove:
            self.particles.remove(particle)

    def _create_particle(
        self,
        weather: WeatherType,
        screen_width: int,
        screen_height: int
    ) -> Optional[WeatherParticle]:
        """Create a new weather particle based on weather type."""
        if weather == WeatherType.RAIN or weather == WeatherType.HEAVY_RAIN:
            return WeatherParticle(
                x=random.uniform(0, screen_width),
                y=random.uniform(-50, -10),
                vx=random.uniform(-20, -10),  # Slight wind
                vy=random.uniform(400, 600),  # Fast falling
                size=random.randint(2, 4),
                alpha=random.randint(100, 180),
                max_lifetime=2.0,
            )
        elif weather == WeatherType.THUNDERSTORM:
            return WeatherParticle(
                x=random.uniform(0, screen_width),
                y=random.uniform(-50, -10),
                vx=random.uniform(-40, -20),  # More wind
                vy=random.uniform(450, 650),
                size=random.randint(2, 5),
                alpha=random.randint(120, 200),
                max_lifetime=2.0,
            )
        elif weather == WeatherType.SNOW:
            return WeatherParticle(
                x=random.uniform(0, screen_width),
                y=random.uniform(-30, -5),
                vx=random.uniform(-30, 30),  # Drifting
                vy=random.uniform(40, 80),  # Slow falling
                size=random.randint(2, 5),
                alpha=random.randint(180, 255),
                max_lifetime=5.0,
            )
        elif weather == WeatherType.BLIZZARD:
            return WeatherParticle(
                x=random.uniform(0, screen_width),
                y=random.uniform(-30, -5),
                vx=random.uniform(-100, -50),  # Strong wind
                vy=random.uniform(60, 120),
                size=random.randint(3, 6),
                alpha=random.randint(200, 255),
                max_lifetime=3.0,
            )
        elif weather == WeatherType.SANDSTORM:
            return WeatherParticle(
                x=random.uniform(-20, 0),  # Come from left
                y=random.uniform(0, screen_height),
                vx=random.uniform(150, 250),  # Fast horizontal
                vy=random.uniform(-20, 20),  # Slight vertical drift
                size=random.randint(2, 4),
                alpha=random.randint(100, 160),
                max_lifetime=3.0,
            )
        elif weather == WeatherType.ASH:
            return WeatherParticle(
                x=random.uniform(0, screen_width),
                y=random.uniform(-30, -5),
                vx=random.uniform(-20, 20),
                vy=random.uniform(30, 60),  # Slow falling
                size=random.randint(2, 4),
                alpha=random.randint(80, 140),
                max_lifetime=4.0,
            )
        return None

    def _update_lightning(self, dt: float) -> None:
        """Update lightning flash effect for thunderstorms."""
        active_weather = self._get_effective_weather()

        # Decay existing flash
        if self.lightning_flash > 0:
            self.lightning_flash = max(0, self.lightning_flash - dt * 5)

        # Update cooldown
        if self.lightning_cooldown > 0:
            self.lightning_cooldown -= dt

        # Trigger new lightning
        if active_weather == WeatherType.THUNDERSTORM and self.lightning_cooldown <= 0:
            if random.random() < 0.01:  # 1% chance per frame
                self.lightning_flash = 1.0
                self.lightning_cooldown = random.uniform(3.0, 10.0)

    def _get_effective_weather(self) -> WeatherType:
        """Get the current effective weather (considering transitions)."""
        if self.map_weather_override is not None:
            return self.map_weather_override
        return self.current_weather

    def transition_to(self, weather: WeatherType, duration: float = 5.0) -> None:
        """
        Begin transitioning to a new weather type.

        Args:
            weather: Target weather type
            duration: Transition duration in seconds
        """
        if weather == self.current_weather:
            return

        self.transition_weather = weather
        self.transition_progress = 0.0
        self.transition_duration = duration

    def set_weather(self, weather: WeatherType) -> None:
        """Immediately set weather without transition."""
        self.current_weather = weather
        self.transition_weather = None
        self.transition_progress = 0.0
        self.particles.clear()

    def set_map_override(self, weather: Optional[WeatherType]) -> None:
        """
        Set a map-specific weather override.

        Args:
            weather: Weather type to force, or None to use natural weather
        """
        if weather != self.map_weather_override:
            self.map_weather_override = weather
            self.particles.clear()  # Clear particles for new weather

    def clear_map_override(self) -> None:
        """Remove map weather override and return to natural weather."""
        self.map_weather_override = None

    def set_biome_weights(self, biome: str) -> None:
        """
        Set weather probabilities based on biome type.

        Args:
            biome: Biome identifier (e.g., "forest", "desert", "tundra")
        """
        biome_weights = {
            "forest": {
                WeatherType.CLEAR: 0.35,
                WeatherType.CLOUDY: 0.25,
                WeatherType.RAIN: 0.20,
                WeatherType.HEAVY_RAIN: 0.10,
                WeatherType.THUNDERSTORM: 0.05,
                WeatherType.FOG: 0.05,
            },
            "desert": {
                WeatherType.CLEAR: 0.70,
                WeatherType.CLOUDY: 0.10,
                WeatherType.SANDSTORM: 0.15,
                WeatherType.FOG: 0.05,  # Morning fog
            },
            "tundra": {
                WeatherType.CLEAR: 0.25,
                WeatherType.CLOUDY: 0.20,
                WeatherType.SNOW: 0.30,
                WeatherType.BLIZZARD: 0.15,
                WeatherType.FOG: 0.10,
            },
            "volcanic": {
                WeatherType.CLEAR: 0.30,
                WeatherType.CLOUDY: 0.25,
                WeatherType.ASH: 0.35,
                WeatherType.FOG: 0.10,
            },
            "swamp": {
                WeatherType.CLEAR: 0.15,
                WeatherType.CLOUDY: 0.20,
                WeatherType.RAIN: 0.25,
                WeatherType.HEAVY_RAIN: 0.15,
                WeatherType.FOG: 0.25,
            },
            "mountain": {
                WeatherType.CLEAR: 0.30,
                WeatherType.CLOUDY: 0.25,
                WeatherType.RAIN: 0.15,
                WeatherType.SNOW: 0.15,
                WeatherType.FOG: 0.10,
                WeatherType.THUNDERSTORM: 0.05,
            },
        }

        self.weather_weights = biome_weights.get(biome, self.weather_weights)

    def get_tint_color(self) -> Tuple[int, int, int, int]:
        """
        Get the current weather tint color with transition blending.

        Returns:
            RGBA tuple for the overlay tint
        """
        active_weather = self._get_effective_weather()
        current_tint = WEATHER_TINTS.get(active_weather, (255, 255, 255, 0))

        # Blend with transition weather if transitioning
        if self.transition_weather is not None and self.map_weather_override is None:
            target_tint = WEATHER_TINTS.get(self.transition_weather, (255, 255, 255, 0))
            return self._lerp_color(current_tint, target_tint, self.transition_progress)

        return current_tint

    def get_ambient_modifier(self) -> float:
        """
        Get the ambient light modifier for current weather.

        Returns:
            Float multiplier for ambient light (0.0 to 1.0)
        """
        active_weather = self._get_effective_weather()
        current_ambient = WEATHER_AMBIENT.get(active_weather, 1.0)

        # Blend with transition weather if transitioning
        if self.transition_weather is not None and self.map_weather_override is None:
            target_ambient = WEATHER_AMBIENT.get(self.transition_weather, 1.0)
            return current_ambient + (target_ambient - current_ambient) * self.transition_progress

        return current_ambient

    def get_combat_modifiers(self) -> Dict[str, int]:
        """
        Get stat modifiers for combat based on current weather.

        Returns:
            Dictionary of stat name to modifier value
        """
        active_weather = self._get_effective_weather()
        return WEATHER_COMBAT_EFFECTS.get(active_weather, {}).copy()

    def _lerp_color(
        self,
        c1: Tuple[int, int, int, int],
        c2: Tuple[int, int, int, int],
        t: float
    ) -> Tuple[int, int, int, int]:
        """Linearly interpolate between two RGBA colors."""
        return (
            int(c1[0] + (c2[0] - c1[0]) * t),
            int(c1[1] + (c2[1] - c1[1]) * t),
            int(c1[2] + (c2[2] - c1[2]) * t),
            int(c1[3] + (c2[3] - c1[3]) * t),
        )

    def get_weather_name(self) -> str:
        """Get a display-friendly name for the current weather."""
        active_weather = self._get_effective_weather()
        names = {
            WeatherType.CLEAR: "Clear",
            WeatherType.CLOUDY: "Cloudy",
            WeatherType.RAIN: "Rain",
            WeatherType.HEAVY_RAIN: "Heavy Rain",
            WeatherType.THUNDERSTORM: "Thunderstorm",
            WeatherType.SNOW: "Snow",
            WeatherType.BLIZZARD: "Blizzard",
            WeatherType.FOG: "Fog",
            WeatherType.SANDSTORM: "Sandstorm",
            WeatherType.ASH: "Ash Fall",
        }
        return names.get(active_weather, "Unknown")

    def serialize(self) -> Dict[str, Any]:
        """Serialize weather state for saving."""
        return {
            "current_weather": self.current_weather.value,
            "transition_weather": self.transition_weather.value if self.transition_weather else None,
            "transition_progress": self.transition_progress,
            "change_timer": self.change_timer,
            "enabled": self.enabled,
            "paused": self.paused,
        }

    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> "WeatherSystem":
        """Deserialize weather state from saved data."""
        current = WeatherType(data.get("current_weather", "clear"))
        transition_val = data.get("transition_weather")
        transition = WeatherType(transition_val) if transition_val else None

        return cls(
            current_weather=current,
            transition_weather=transition,
            transition_progress=data.get("transition_progress", 0.0),
            change_timer=data.get("change_timer", 300.0),
            enabled=data.get("enabled", True),
            paused=data.get("paused", False),
        )

    def deserialize_into(self, data: Dict[str, Any]) -> None:
        """Restore state from saved data (Saveable protocol)."""
        self.current_weather = WeatherType(data.get("current_weather", "clear"))
        transition_val = data.get("transition_weather")
        self.transition_weather = WeatherType(transition_val) if transition_val else None
        self.transition_progress = data.get("transition_progress", 0.0)
        self.change_timer = data.get("change_timer", 300.0)
        self.enabled = data.get("enabled", True)
        self.paused = data.get("paused", False)


def get_weather_for_map(map_id: str, map_data: Optional[Dict] = None) -> Optional[WeatherType]:
    """
    Determine weather override for a specific map.

    Args:
        map_id: The map identifier
        map_data: Optional map data dictionary with weather config

    Returns:
        Weather type to force, or None for natural weather
    """
    # Check map data for explicit weather setting
    if map_data and "weather" in map_data:
        weather_str = map_data["weather"]
        try:
            return WeatherType(weather_str)
        except ValueError:
            pass

    # Default weather for certain map types based on name
    map_lower = map_id.lower()

    if "tundra" in map_lower or "frozen" in map_lower or "ice" in map_lower:
        return WeatherType.SNOW
    elif "volcano" in map_lower or "volcanic" in map_lower or "lava" in map_lower:
        return WeatherType.ASH
    elif "desert" in map_lower or "sand" in map_lower:
        return None  # Let natural weather handle it with desert biome
    elif "swamp" in map_lower or "marsh" in map_lower:
        return WeatherType.FOG
    elif "cave" in map_lower or "dungeon" in map_lower or "crypt" in map_lower:
        return WeatherType.CLEAR  # Indoor areas are clear

    return None  # Use natural weather


def get_biome_for_map(map_id: str, map_data: Optional[Dict] = None) -> str:
    """
    Determine biome type for a map (affects weather probabilities).

    Args:
        map_id: The map identifier
        map_data: Optional map data dictionary with biome config

    Returns:
        Biome identifier string
    """
    # Check map data for explicit biome setting
    if map_data and "biome" in map_data:
        return map_data["biome"]

    # Infer biome from map name
    map_lower = map_id.lower()

    if "tundra" in map_lower or "frozen" in map_lower or "ice" in map_lower:
        return "tundra"
    elif "volcano" in map_lower or "volcanic" in map_lower or "crater" in map_lower:
        return "volcanic"
    elif "desert" in map_lower or "sand" in map_lower or "oasis" in map_lower:
        return "desert"
    elif "swamp" in map_lower or "marsh" in map_lower:
        return "swamp"
    elif "mountain" in map_lower or "peak" in map_lower or "pass" in map_lower:
        return "mountain"

    return "forest"  # Default biome
