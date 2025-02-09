from typing import Dict, List, Optional, Tuple, Protocol
from dataclasses import dataclass
from ..models.state import CombatState
from ..models.actions import Action, ActionResult, ActionType, ActionCosts
from ..models.combatant import CombatantState
from ..models.effects import StatusEffect
from common.errors import CombatProcessingError

class DamageCalculator(Protocol):
    """Protocol for damage calculation strategies."""
    def calculate(self, attacker: CombatantState, defender: CombatantState, base_damage: int) -> int:
        """Calculate final damage based on attacker and defender states."""
        ...

@dataclass
class StandardDamageCalculator:
    """Standard implementation of damage calculations."""
    def calculate(self, attacker: CombatantState, defender: CombatantState, base_damage: int) -> int:
        attack_modifier = self._get_attack_modifier(attacker)
        defense_modifier = self._get_defense_modifier(defender)
        
        final_damage = int(base_damage * attack_modifier / defense_modifier)
        return max(0, final_damage)
    
    def _get_attack_modifier(self, attacker: CombatantState) -> float:
        modifier = 1.0
        for effect in attacker.status_effects:
            if effect.name == "Attack Up":
                modifier *= effect.strength
        return modifier
    
    def _get_defense_modifier(self, defender: CombatantState) -> float:
        modifier = 1.0
        for effect in defender.status_effects:
            if effect.name == "Defending":
                modifier *= effect.strength
        return modifier

class CombatProcessor:
    """Core combat processing logic."""
    
    def __init__(self, damage_calculator: Optional[DamageCalculator] = None):
        self._damage_calculator = damage_calculator or StandardDamageCalculator()
        self._processors = {
            ActionType.ATTACK: self._process_attack,
            ActionType.DEFEND: self._process_defend,
            ActionType.MOVE: self._process_move,
            ActionType.SKILL: self._process_skill,
            ActionType.ITEM: self._process_item,
            # ActionType.WAIT: self._process_wait
        }

    def process_action(self, state: CombatState, actor_id: str, action: Action) -> Tuple[CombatState, ActionResult]:
        """Process a combat action and return the new state and result."""
        if actor_id not in state.combatants:
            raise CombatProcessingError(f"Invalid actor ID: {actor_id}")

        new_state = state.clone()
        
        try:
            processor = self._processors.get(action.type)
            if not processor:
                raise CombatProcessingError(f"No processor for action type: {action.type}")

            result = processor(new_state, actor_id, action)
            new_state = self._apply_post_processing(new_state, result)
            
            return new_state, result

        except Exception as e:
            raise CombatProcessingError(f"Error processing action: {str(e)}")

    def _process_attack(self, state: CombatState, actor_id: str, action: Action) -> ActionResult:
        """Process attack actions."""
        actor = state.combatants[actor_id]
        target = state.combatants.get(action.target_id)
        
        if not target:
            return ActionResult(
                action_id=action.id,
                success=False,
                messages=["Invalid target"]
            )

        base_damage = action.parameters.get("damage", 0)
        final_damage = self._damage_calculator.calculate(actor, target, base_damage)
        
        # Apply damage
        target.health = max(0, target.health - final_damage)
        
        # Apply stamina cost
        actor.stamina = max(0, actor.stamina - action.costs.stamina)

        return ActionResult(
            action_id=action.id,
            success=True,
            effects={
                "damage_dealt": final_damage,
                "stamina_cost": action.costs.stamina
            },
            messages=[f"Dealt {final_damage} damage to {target.id}"]
        )

    def _process_defend(self, state: CombatState, actor_id: str, action: Action) -> ActionResult:
        """Process defend actions."""
        actor = state.combatants[actor_id]
        defense_bonus = action.parameters.get("defense_bonus", 1.5)
        
        defense_effect = StatusEffect(
            id="defend",
            name="Defending",
            duration=1,
            strength=defense_bonus
        )
        
        actor.status_effects.append(defense_effect)
        actor.stamina = max(0, actor.stamina - action.costs.stamina)

        return ActionResult(
            action_id=action.id,
            success=True,
            effects={
                "defense_bonus": defense_bonus,
                "stamina_cost": action.costs.stamina
            },
            messages=[f"{actor_id} assumes a defensive stance"]
        )

    def _process_move(self, state: CombatState, actor_id: str, action: Action) -> ActionResult:
        """Process movement actions."""
        actor = state.combatants[actor_id]
        distance = action.parameters.get("distance", 0)
        
        actor.position += distance
        actor.stamina = max(0, actor.stamina - action.costs.stamina)

        return ActionResult(
            action_id=action.id,
            success=True,
            effects={
                "distance_moved": distance,
                "stamina_cost": action.costs.stamina
            },
            messages=[f"{actor_id} moved {distance} units"]
        )

    def _process_skill(self, state: CombatState, actor_id: str, action: Action) -> ActionResult:
        """Process skill actions."""
        # To be implemented based on skill system design
        return ActionResult(
            action_id=action.id,
            success=False,
            messages=["Skill system not implemented"]
        )

    def _process_item(self, state: CombatState, actor_id: str, action: Action) -> ActionResult:
        """Process item actions."""
        # To be implemented based on inventory system design
        return ActionResult(
            action_id=action.id,
            success=False,
            messages=["Item system not implemented"]
        )

    def _process_wait(self, state: CombatState, actor_id: str, action: Action) -> ActionResult:
        """Process wait actions."""
        actor = state.combatants[actor_id]
        stamina_recovery = action.parameters.get("stamina_recovery", 5)
        
        actor.stamina = min(actor.max_stamina, actor.stamina + stamina_recovery)

        return ActionResult(
            action_id=action.id,
            success=True,
            effects={"stamina_recovered": stamina_recovery},
            messages=[f"{actor_id} recovers {stamina_recovery} stamina"]
        )

    def _apply_post_processing(self, state: CombatState, result: ActionResult) -> CombatState:
        """Apply post-action processing and state cleanup."""
        for combatant in state.combatants.values():
            # Update status effects
            remaining_effects = []
            for effect in combatant.status_effects:
                if effect.duration > 0:
                    effect.duration -= 1
                    remaining_effects.append(effect)
            combatant.status_effects = remaining_effects

        return state