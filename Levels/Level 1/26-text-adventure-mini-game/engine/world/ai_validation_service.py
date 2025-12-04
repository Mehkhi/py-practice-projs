"""AI validation service for encounter data validation.

This service handles validation of AI profiles in encounter data,
checking for missing profiles and invalid configurations.
"""

from typing import Any, Dict

from core.combat.ai_validation import (
    iter_ai_actions,
    validate_ai_profile_dict,
    warn_missing_profile,
)


class AIValidationService:
    """Service for validating AI profiles in encounter data."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize AI validation service with configuration.

        Args:
            config: Configuration dictionary containing validation settings
        """
        self.config = config
        self._iter_ai_actions = iter_ai_actions
        self._validate_ai_profile_dict = validate_ai_profile_dict
        self._warn_missing_profile = warn_missing_profile

    def validate_encounters_ai(
        self,
        encounters_data: Dict[str, Any],
        skills: Dict[str, Any],
        items_db: Dict[str, Any]
    ) -> None:
        """Validate AI profiles in encounters data.

        Args:
            encounters_data: Dictionary of encounter definitions
            skills: Dictionary of available skills
            items_db: Dictionary of available items
        """
        if not self.config.get("ai_validation_enabled", True):
            return
        if not encounters_data:
            return

        for encounter_id, encounter in encounters_data.items():
            if not isinstance(encounter, dict):
                continue
            enemies = encounter.get("enemies", [])
            if not isinstance(enemies, list):
                continue
            for enemy_data in enemies:
                if not isinstance(enemy_data, dict):
                    continue
                ai_profile = enemy_data.get("ai_profile")
                enemy_id = enemy_data.get("id", "enemy")
                self._validate_ai_profile_dict(
                    ai_profile,
                    skills,
                    items_db,
                    encounter_id,
                    enemy_id,
                )
                if self.config.get("ai_profile_coverage_check", True):
                    self._warn_missing_profile(encounter_id, enemy_data)

    def validate_single_ai_profile(
        self,
        ai_profile: Any,
        skills: Dict[str, Any],
        items_db: Dict[str, Any],
        encounter_id: str,
        enemy_id: str
    ) -> None:
        """Validate a single AI profile.

        Args:
            ai_profile: AI profile to validate
            skills: Dictionary of available skills
            items_db: Dictionary of available items
            encounter_id: ID of the encounter
            enemy_id: ID of the enemy
        """
        self._validate_ai_profile_dict(
            ai_profile,
            skills,
            items_db,
            encounter_id,
            enemy_id,
        )

    def check_missing_profile(self, encounter_id: str, enemy_data: Dict[str, Any]) -> None:
        """Check and warn about missing AI profile.

        Args:
            encounter_id: ID of the encounter
            enemy_data: Enemy data dictionary
        """
        if self.config.get("ai_profile_coverage_check", True):
            self._warn_missing_profile(encounter_id, enemy_data)

    def is_validation_enabled(self) -> bool:
        """Check if AI validation is enabled in configuration.

        Returns:
            True if validation is enabled, False otherwise
        """
        return self.config.get("ai_validation_enabled", True)

    def is_coverage_check_enabled(self) -> bool:
        """Check if AI profile coverage check is enabled.

        Returns:
            True if coverage check is enabled, False otherwise
        """
        return self.config.get("ai_profile_coverage_check", True)
