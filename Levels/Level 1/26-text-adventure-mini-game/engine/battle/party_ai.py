"""Party member AI logic for battle scenes.

This module contains AI decision-making logic for party members,
allowing them to act autonomously based on their role and situation.
"""

import random
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from core.combat import BattleCommand, BattleParticipant, BattleSystem

# AI thresholds
MIN_SP_PERCENT_FOR_SKILLS = 30  # Minimum SP percentage to use offensive skills


class PartyAIMixin:
    """Mixin providing party member AI logic for BattleScene.

    This mixin handles automatic action selection for party members
    based on their role (fighter, mage, healer, support).

    Attributes expected from host class:
        battle_system: BattleSystem instance with skills database
    """

    def _select_party_ai_action(self, actor: "BattleParticipant") -> Optional["BattleCommand"]:
        """
        Select an AI action for a party member based on their role.

        Roles:
        - fighter: Prioritize attacks, use skills when advantageous
        - mage: Prioritize offensive skills, conserve SP
        - healer: Prioritize healing allies, support when healthy
        - support: Buff allies, debuff enemies, attack as fallback

        Args:
            actor: The party member's BattleParticipant

        Returns:
            A BattleCommand for the action to take, or None if no valid action
        """
        from core.combat import ActionType, BattleCommand

        entity = actor.entity
        role = getattr(entity, "role", "fighter")
        alive_enemies = self._alive_enemies()
        alive_allies = self._alive_allies()

        if not alive_enemies:
            return None

        # Check ally health for healing decisions
        wounded_allies = [a for a in alive_allies if a.stats.hp < a.stats.max_hp * 0.5]
        critical_allies = [a for a in alive_allies if a.stats.hp < a.stats.max_hp * 0.25]

        if role == "healer":
            return self._healer_ai(actor, alive_enemies, alive_allies, wounded_allies, critical_allies)
        elif role == "mage":
            return self._mage_ai(actor, alive_enemies, alive_allies, wounded_allies)
        elif role == "support":
            return self._support_ai(actor, alive_enemies, alive_allies, wounded_allies)
        else:  # fighter or default
            return self._fighter_ai(actor, alive_enemies, alive_allies, critical_allies)

    def _fighter_ai(
        self,
        actor: "BattleParticipant",
        alive_enemies: List["BattleParticipant"],
        alive_allies: List["BattleParticipant"],
        critical_allies: List["BattleParticipant"]
    ) -> Optional["BattleCommand"]:
        """Fighter AI: Aggressive attacker, protects critically wounded allies."""
        from core.combat import ActionType, BattleCommand

        # If an ally is critical and we have a guard-like skill, consider protecting
        if critical_allies and actor.stats.sp >= 5:
            for skill_id in getattr(actor.entity, "skills", []):
                skill = self.battle_system.skills.get(skill_id)
                if skill and skill.target_pattern == "single_ally" and actor.stats.sp >= skill.cost_sp:
                    target = critical_allies[0]
                    return BattleCommand(
                        actor_id=actor.entity.entity_id,
                        action_type=ActionType.SKILL,
                        skill_id=skill_id,
                        target_ids=[target.entity.entity_id]
                    )

        # Prefer attacking weakest enemy
        target = min(alive_enemies, key=lambda e: e.stats.hp)

        # Use a learned move if available
        learned_moves = getattr(actor.entity, "learned_moves", [])
        if learned_moves:
            move_id = random.choice(learned_moves)
            return BattleCommand(
                actor_id=actor.entity.entity_id,
                action_type=ActionType.ATTACK,
                skill_id=move_id,
                target_ids=[target.entity.entity_id]
            )

        # Basic attack
        return BattleCommand(
            actor_id=actor.entity.entity_id,
            action_type=ActionType.ATTACK,
            target_ids=[target.entity.entity_id]
        )

    def _mage_ai(
        self,
        actor: "BattleParticipant",
        alive_enemies: List["BattleParticipant"],
        alive_allies: List["BattleParticipant"],
        wounded_allies: List["BattleParticipant"]
    ) -> Optional["BattleCommand"]:
        """Mage AI: Use offensive skills, conserve SP when low."""
        from core.combat import ActionType, BattleCommand

        sp_percent = (actor.stats.sp / actor.stats.max_sp * 100) if actor.stats.max_sp > 0 else 0

        # Find offensive skills
        offensive_skills = []
        for skill_id in getattr(actor.entity, "skills", []):
            skill = self.battle_system.skills.get(skill_id)
            if skill and skill.target_pattern in ("single_enemy", "all_enemies"):
                if actor.stats.sp >= skill.cost_sp:
                    offensive_skills.append((skill_id, skill))

        # Use skills if SP is above threshold
        if offensive_skills and sp_percent > MIN_SP_PERCENT_FOR_SKILLS:
            skill_id, skill = random.choice(offensive_skills)
            if skill.target_pattern == "all_enemies":
                target_ids = [e.entity.entity_id for e in alive_enemies]
            else:
                target = max(alive_enemies, key=lambda e: e.stats.hp)  # Target highest HP
                target_ids = [target.entity.entity_id]

            return BattleCommand(
                actor_id=actor.entity.entity_id,
                action_type=ActionType.SKILL,
                skill_id=skill_id,
                target_ids=target_ids
            )

        # Fallback to basic attack
        target = min(alive_enemies, key=lambda e: e.stats.hp)
        return BattleCommand(
            actor_id=actor.entity.entity_id,
            action_type=ActionType.ATTACK,
            target_ids=[target.entity.entity_id]
        )

    def _healer_ai(
        self,
        actor: "BattleParticipant",
        alive_enemies: List["BattleParticipant"],
        alive_allies: List["BattleParticipant"],
        wounded_allies: List["BattleParticipant"],
        critical_allies: List["BattleParticipant"]
    ) -> Optional["BattleCommand"]:
        """Healer AI: Prioritize healing, especially critical allies."""
        from core.combat import ActionType, BattleCommand

        # Find healing skills
        healing_skills = []
        for skill_id in getattr(actor.entity, "skills", []):
            skill = self.battle_system.skills.get(skill_id)
            if skill and skill.element == "holy" and skill.target_pattern in ("single_ally", "self"):
                if actor.stats.sp >= skill.cost_sp:
                    healing_skills.append((skill_id, skill))

        # Heal critical allies first
        if critical_allies and healing_skills:
            skill_id, skill = healing_skills[0]
            target = critical_allies[0]
            return BattleCommand(
                actor_id=actor.entity.entity_id,
                action_type=ActionType.SKILL,
                skill_id=skill_id,
                target_ids=[target.entity.entity_id]
            )

        # Heal wounded allies
        if wounded_allies and healing_skills:
            skill_id, skill = healing_skills[0]
            target = min(wounded_allies, key=lambda a: a.stats.hp)
            return BattleCommand(
                actor_id=actor.entity.entity_id,
                action_type=ActionType.SKILL,
                skill_id=skill_id,
                target_ids=[target.entity.entity_id]
            )

        # If everyone is healthy, attack
        target = min(alive_enemies, key=lambda e: e.stats.hp)
        return BattleCommand(
            actor_id=actor.entity.entity_id,
            action_type=ActionType.ATTACK,
            target_ids=[target.entity.entity_id]
        )

    def _support_ai(
        self,
        actor: "BattleParticipant",
        alive_enemies: List["BattleParticipant"],
        alive_allies: List["BattleParticipant"],
        wounded_allies: List["BattleParticipant"]
    ) -> Optional["BattleCommand"]:
        """Support AI: Buff allies, debuff enemies, heal if needed."""
        from core.combat import ActionType, BattleCommand

        # Find buff/debuff skills
        buff_skills = []
        debuff_skills = []
        heal_skills = []

        for skill_id in getattr(actor.entity, "skills", []):
            skill = self.battle_system.skills.get(skill_id)
            if not skill or actor.stats.sp < skill.cost_sp:
                continue

            if skill.target_pattern == "single_ally" and skill.element == "holy":
                heal_skills.append((skill_id, skill))
            elif skill.target_pattern in ("single_ally", "self"):
                buff_skills.append((skill_id, skill))
            elif skill.target_pattern == "single_enemy" and skill.status_inflict_id:
                debuff_skills.append((skill_id, skill))

        # Heal wounded allies first
        if wounded_allies and heal_skills:
            skill_id, skill = heal_skills[0]
            target = min(wounded_allies, key=lambda a: a.stats.hp)
            return BattleCommand(
                actor_id=actor.entity.entity_id,
                action_type=ActionType.SKILL,
                skill_id=skill_id,
                target_ids=[target.entity.entity_id]
            )

        # Apply debuffs to enemies
        if debuff_skills and random.random() < 0.6:
            skill_id, skill = random.choice(debuff_skills)
            target = max(alive_enemies, key=lambda e: e.stats.hp)
            return BattleCommand(
                actor_id=actor.entity.entity_id,
                action_type=ActionType.SKILL,
                skill_id=skill_id,
                target_ids=[target.entity.entity_id]
            )

        # Apply buffs to allies
        if buff_skills and random.random() < 0.4:
            skill_id, skill = random.choice(buff_skills)
            # Buff the fighter/attacker if possible
            fighters = [a for a in alive_allies if getattr(a.entity, "role", "fighter") == "fighter"]
            target = fighters[0] if fighters else alive_allies[0]
            return BattleCommand(
                actor_id=actor.entity.entity_id,
                action_type=ActionType.SKILL,
                skill_id=skill_id,
                target_ids=[target.entity.entity_id]
            )

        # Fallback to attack
        target = min(alive_enemies, key=lambda e: e.stats.hp)
        return BattleCommand(
            actor_id=actor.entity.entity_id,
            action_type=ActionType.ATTACK,
            target_ids=[target.entity.entity_id]
        )

    def _describe_auto_action(self, cmd: "BattleCommand") -> str:
        """Generate a description of an auto-selected action.

        Uses the ActionHandler pattern to generate descriptions, consolidating
        the logic previously scattered across multiple if/elif chains.

        Args:
            cmd: The BattleCommand to describe

        Returns:
            Human-readable description of the action
        """
        from core.combat_modules.action_handlers import describe_action

        # Build context with available databases
        context = {
            "skills": self.battle_system.skills,
            "items_db": getattr(self, "items_db", {}),
            "moves_db": getattr(self, "moves_db", None),
        }

        return describe_action(cmd, context)
