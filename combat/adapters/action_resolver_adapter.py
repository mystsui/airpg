"""
Action Resolver Adapter Module

This module provides an adapter that implements the IActionResolver interface
while maintaining compatibility with the existing action resolution logic.
"""

import random
import math
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from combat.interfaces import (
    IActionResolver,
    ICombatant,
    Action,
    ActionResult,
    ITimingManager,
    IAwarenessManager
)
from combat.lib.timing import TimingSystem
from combat.lib.awareness_system import AwarenessSystem, AwarenessZone
from combat.lib.action_system import (
    ActionState,
    ActionVisibility,
    ActionCommitment,
    ActionStateType
)
from combat.lib.actions_library import ACTIONS

@dataclass
class ActionResult:
    """Result of an action execution."""
    success: bool
    outcome: str
    damage: float = 0.0
    stamina_cost: float = 0.0
    effects: Dict[str, Any] = None

class ActionResolverAdapter(IActionResolver):
    """
    Adapter class that implements IActionResolver interface while maintaining
    compatibility with existing action resolution logic, with enhanced combat mechanics.
    """
    
    def __init__(self):
        """Initialize the action resolver adapter."""
        self._timing_manager: ITimingManager = TimingSystem()
        self._awareness_manager: IAwarenessManager = AwarenessSystem()
    
    def resolve_action(self, action: ActionState, source_state: Any, target_state: Optional[Any] = None) -> ActionResult:
        """
        Resolve an action between combatants.
        
        Args:
            action: The action to resolve
            actor: The combatant performing the action
            target: Optional target combatant
            
        Returns:
            ActionResult containing the outcome of the action
        """
        if action.action_type == "release_attack":
            return self._resolve_attack(action, source_state, target_state)
        elif action.action_type.startswith("block"):
            return self._resolve_block(action, source_state, target_state)
        elif action.action_type.startswith("evade"):
            return self._resolve_evade(action, source_state)
        elif action.action_type.startswith("move"):
            return self._resolve_movement(action, source_state)
        else:
            return self._resolve_neutral(action, source_state)

    def validate(self, action: Action, actor: ICombatant) -> bool:
        """
        Validate if an action can be performed.
        
        Args:
            action: The action to validate
            actor: The combatant attempting the action
            
        Returns:
            bool indicating if the action is valid
        """
        # Check if action exists
        if action.type not in ACTIONS:
            return False
            
        # Get actor state
        actor_state = actor.get_state()
            
        # Check stamina requirements
        total_stamina_cost = action.stamina_cost
        if action.state == ActionState.FEINT:
            total_stamina_cost += action.feint_cost
            
        if actor_state.stamina < total_stamina_cost:
            return False
            
        # Check speed requirements
        action_props = ACTIONS[action.type]
        if "speed_requirement" in action_props:
            if actor_state.speed < action_props["speed_requirement"]:
                return False
                
        # Check commitment state
        if action.commitment == ActionCommitment.FULL:
            # Can't cancel fully committed actions
            if "cancel" in action.type:
                return False
                
        return True

    def get_available_actions(self, actor: ICombatant) -> List[Action]:
        """
        Get list of available actions for a combatant.
        
        Args:
            actor: The combatant to get actions for
            
        Returns:
            List of available actions
        """
        available = []
        actor_state = actor.get_state()
        
        for action_type, properties in ACTIONS.items():
            if actor_state.stamina >= properties["stamina_cost"]:
                action = Action(
                    type=action_type,
                    time=properties["time"],
                    stamina_cost=properties["stamina_cost"],
                    source_id=actor_state.entity_id
                )
                available.append(action)
                
        return available

    def _resolve_attack(self, action: ActionState, source_state: Any, target_state: Optional[Any]) -> ActionResult:
        """Resolve attack action."""
        if not target_state:
            return ActionResult(success=False, outcome="missed", damage=0)
        
        # Calculate base damage
        damage = 10  # Base damage for now
        
        # Apply modifiers based on state
        if action.state == ActionStateType.COMMIT:
            damage *= 1.2  # 20% bonus for committed attacks
        elif action.state == ActionStateType.RELEASE:
            damage *= 1.5  # 50% bonus for released attacks
            
        # Apply visibility modifier
        if action.visibility == ActionVisibility.HIDDEN:
            damage *= 1.3  # 30% bonus for hidden attacks
            
        return ActionResult(
            success=True,
            outcome="hit",
            damage=damage,
            stamina_cost=action.properties.get("stamina_cost", 0),
            effects={}
        )

    def _resolve_blocked_attack(self, actor_state: 'CombatantState', target_state: 'CombatantState') -> ActionResult:
        """Resolve an attack against a blocking target."""
        damage = random.randint(
            actor_state.attack_power * actor_state.accuracy // 100,
            actor_state.attack_power
        )
        
        if damage <= target_state.blocking_power:
            return ActionResult(
                success=False,
                outcome="blocked",
                damage=damage,
                state_changes={
                    "target_blocking_power": -damage
                }
            )
        else:
            breach_damage = damage - target_state.blocking_power
            return ActionResult(
                success=True,
                outcome="breached",
                damage=damage,
                state_changes={
                    "target_blocking_power": -target_state.blocking_power,
                    "target_health": -breach_damage
                }
            )

    def _resolve_block(self, action: ActionState, source_state: Any, target_state: Optional[Any]) -> ActionResult:
        """Resolve block action."""
        return ActionResult(
            success=True,
            outcome="blocking",
            damage=0,
            stamina_cost=action.properties.get("stamina_cost", 0),
            effects={"blocking": True}
        )

    def _resolve_evade(self, action: ActionState, source_state: Any) -> ActionResult:
        """Resolve evade action."""
        return ActionResult(
            success=True,
            outcome="evading",
            damage=0,
            stamina_cost=action.properties.get("stamina_cost", 0),
            effects={"evading": True}
        )

    def _resolve_movement(self, action: ActionState, source_state: Any) -> ActionResult:
        """Resolve movement action."""
        return ActionResult(
            success=True,
            outcome=action.action_type,
            damage=0,
            stamina_cost=action.properties.get("stamina_cost", 0),
            effects={"moved": True}
        )

    def _resolve_neutral(self, action: ActionState, source_state: Any) -> ActionResult:
        """Resolve neutral action."""
        return ActionResult(
            success=True,
            outcome=action.action_type,
            damage=0,
            stamina_cost=action.properties.get("stamina_cost", 0),
            effects={}
        )
