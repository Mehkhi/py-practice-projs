"""Target selection strategies for AI combat decisions.

This module provides targeting logic for AI enemies, including:
- Target strategy application (weakest, random, highest HP, etc.)
- Role matching for coordinated tactics
- Role assignment based on AI profiles

Note on deferred imports:
    This module uses TYPE_CHECKING to avoid circular import issues with
    core.combat types.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

if TYPE_CHECKING:
    from core.combat import BattleParticipant


class TargetingMixin:
    """Mixin providing target selection methods for AI systems.

    This mixin assumes the host class has:
    - self.players: List[BattleParticipant]
    - self.enemies: List[BattleParticipant]
    - self.rng: random.Random
    """

    def _apply_target_strategy(
        self,
        strategy: str,
        enemy: "BattleParticipant"
    ) -> List[str]:
        """Apply target strategy to return list of target IDs.

        Strategies:
        - self: Target the acting enemy itself
        - weakest_ally: Target the ally (enemy) with lowest HP
        - random_ally: Target a random ally (enemy)
        - weakest_enemy: Target the player with lowest HP
        - random_enemy: Target a random player
        - highest_hp_enemy: Target the player with highest HP

        Args:
            strategy: Target selection strategy string
            enemy: The enemy participant performing the action

        Returns:
            List of target entity IDs. Empty list if no valid targets.
        """
        if strategy == 'self':
            return [enemy.entity.entity_id]

        elif strategy == 'weakest_ally':
            allies = [e for e in self.enemies if e.is_alive() and e != enemy]
            if allies:
                weakest = min(allies, key=lambda a: a.stats.hp)
                return [weakest.entity.entity_id]
            return [enemy.entity.entity_id]  # Fallback to self

        elif strategy == 'random_ally':
            allies = [e for e in self.enemies if e.is_alive() and e != enemy]
            if allies:
                target = self.rng.choice(allies)
                return [target.entity.entity_id]
            return [enemy.entity.entity_id]  # Fallback to self

        elif strategy == 'weakest_enemy':
            enemies = [p for p in self.players if p.is_alive()]
            if enemies:
                weakest = min(enemies, key=lambda e: e.stats.hp)
                return [weakest.entity.entity_id]
            return []  # No valid targets

        elif strategy == 'random_enemy':
            enemies = [p for p in self.players if p.is_alive()]
            if enemies:
                target = self.rng.choice(enemies)
                return [target.entity.entity_id]
            return []  # No valid targets

        elif strategy == 'highest_hp_enemy':
            enemies = [p for p in self.players if p.is_alive()]
            if enemies:
                highest = max(enemies, key=lambda e: e.stats.hp)
                return [highest.entity.entity_id]
            return []  # No valid targets

        # Default fallback
        return []

    def _assign_tactic_roles(self) -> None:
        """Assign tactic roles to enemies based on their AI profiles.

        Role assignment priority:
        1. Explicit role in AI profile ('tactic_role' field)
        2. Inferred from behavior type (aggressive->dps, defensive->tank, etc.)
        3. Inferred from available skills (heal->healer, poison->debuffer)
        4. Special roles for alpha/leader enemies

        This method should be called at battle start before coordinated
        tactics can be attempted.
        """
        for enemy in self.enemies:
            if enemy.ai_profile:
                # Check for explicit role assignment
                role = enemy.ai_profile.get('tactic_role')
                if role:
                    enemy.tactic_role = role
                    continue

                # Infer role from behavior type and skills
                behavior = enemy.ai_profile.get('behavior_type', 'balanced')
                if behavior == 'aggressive':
                    enemy.tactic_role = 'dps'
                elif behavior == 'defensive':
                    enemy.tactic_role = 'tank'
                elif behavior == 'support':
                    enemy.tactic_role = 'healer'
                else:
                    # Check skills for role inference
                    if 'heal' in enemy.skills:
                        enemy.tactic_role = 'healer'
                    elif any('poison' in s or 'bleed' in s for s in enemy.skills):
                        enemy.tactic_role = 'debuffer'
                    else:
                        enemy.tactic_role = 'dps'

                # Special role for alpha/boss enemies
                name_lower = enemy.entity.name.lower()
                if 'alpha' in name_lower or 'leader' in name_lower:
                    enemy.tactic_role = 'alpha'

    def _match_roles_to_enemies(
        self,
        required_roles: List[str],
        available_enemies: List["BattleParticipant"],
        already_assigned: set
    ) -> Optional[Dict[str, "BattleParticipant"]]:
        """Match required roles to available enemies.

        Attempts to find enemies that can fill each required role for a
        coordinated tactic. Each enemy can only fill one role.

        Args:
            required_roles: List of role IDs needed (e.g., ["dps", "dps", "healer"])
            available_enemies: Enemies that can potentially fill roles
            already_assigned: Set of entity IDs already assigned to other tactics

        Returns:
            Dict mapping role keys to BattleParticipant, or None if roles
            cannot be filled. For duplicate roles, uses indexed keys
            (e.g., "dps", "dps_1", "dps_2").
        """
        assignments: Dict[str, "BattleParticipant"] = {}
        used_enemies: set = set()

        # Count how many of each role we need
        role_counts: Dict[str, int] = {}
        for role in required_roles:
            role_counts[role] = role_counts.get(role, 0) + 1

        for role, count in role_counts.items():
            matched = 0
            for enemy in available_enemies:
                if enemy.entity.entity_id in already_assigned:
                    continue
                if enemy.entity.entity_id in used_enemies:
                    continue

                # Check if enemy can fill this role
                if self._enemy_can_fill_role(enemy, role):
                    # For duplicate roles, use indexed keys
                    key = role if matched == 0 else f"{role}_{matched}"
                    assignments[key] = enemy
                    used_enemies.add(enemy.entity.entity_id)
                    matched += 1
                    if matched >= count:
                        break

            if matched < count:
                return None  # Can't fill all required roles

        return assignments if assignments else None

    def _enemy_can_fill_role(self, enemy: "BattleParticipant", role: str) -> bool:
        """Check if an enemy can fill a specific tactic role.

        Uses flexible role matching - enemies may qualify for roles beyond
        their assigned role based on skills and compatibility.

        Role compatibility:
        - dps: dps, debuffer, or unassigned enemies
        - pack: Any non-alpha enemy
        - tank: tank or dps enemies
        - healer: healer role or enemies with heal skill
        - debuffer: debuffer role or enemies with poison/bleed skills

        Args:
            enemy: The enemy participant to check
            role: The role ID to check compatibility for

        Returns:
            True if the enemy can fill the role, False otherwise
        """
        if enemy.tactic_role == role:
            return True

        # Flexible role matching
        if role == 'dps':
            return enemy.tactic_role in ('dps', 'debuffer', None)
        elif role == 'pack':
            return enemy.tactic_role != 'alpha'  # Any non-alpha can be pack
        elif role == 'tank':
            return enemy.tactic_role in ('tank', 'dps')
        elif role == 'healer':
            return enemy.tactic_role == 'healer' or 'heal' in enemy.skills
        elif role == 'debuffer':
            return (
                enemy.tactic_role == 'debuffer' or
                any('poison' in s or 'bleed' in s for s in enemy.skills)
            )

        return False
