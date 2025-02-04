"""
Action Resolver Adapter Module

This module provides an adapter that implements the IActionResolver interface
while maintaining compatibility with the existing action resolution logic.
"""

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
    ActionCommitment
)
from combat.lib.actions_library import ACTIONS
import random
import math

class ActionResolverAdapter(IActionResolver):
    """
    Adapter class that implements IActionResolver interface while maintaining
    compatibility with existing action resolution logic, with enhanced combat mechanics.
    """
    
    def __init__(self):
        """Initialize the action resolver adapter."""
        self._timing_manager: ITimingManager = TimingSystem()
        self._awareness_manager: IAwarenessManager = AwarenessSystem()
    
    def resolve(self, action: Action, actor: ICombatant, target: Optional[ICombatant]) -> ActionResult:
        """
        Resolve an action between combatants.
        
        Args:
            action: The action to resolve
            actor: The combatant performing the action
            target: Optional target combatant
            
        Returns:
            ActionResult containing the outcome of the action
        """
        if action.type == "release_attack":
            return self._resolve_attack(action, actor, target)
        elif action.type.startswith("block"):
            return self._resolve_block(action, actor, target)
        elif action.type.startswith("evade"):
            return self._resolve_evade(action, actor)
        elif action.type.startswith("move"):
            return self._resolve_movement(action, actor)
        else:
            return self._resolve_neutral(action, actor)

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

    def _resolve_attack(self, action: Action, actor: ICombatant, target: Optional[ICombatant]) -> ActionResult:
        """Resolve attack action."""
        if not target:
            return ActionResult(success=False, outcome="missed", damage=0)
            
        actor_state = actor.get_state()
        target_state = target.get_state()
        
        # Check range
        if not actor.is_within_range(50):  # TODO: Get actual distance from combat system
            return ActionResult(success=False, outcome="missed", damage=0)
            
        # Check visibility and awareness
        if action.state == ActionState.FEINT:
            # Feints can be detected based on perception
            detection_chance = min(1.0, target_state.perception / (actor_state.stealth * 2))
            if random.random() < detection_chance:
                return ActionResult(
                    success=False,
                    outcome="feint_detected",
                    state_changes={
                        "actor_stamina": -action.feint_cost
                    }
                )
                
        # Check commitment and interruption
        if target_state.action:
            target_action = target_state.action
            if target_action.get("commitment") == ActionCommitment.FULL.value:
                # Can't interrupt fully committed actions
                pass
            elif target_action.get("type") in ["blocking", "keep_blocking"]:
                return self._resolve_blocked_attack(actor_state, target_state)
            elif target_action.get("type") == "evading":
                return ActionResult(success=False, outcome="evaded", damage=0)
                
        # Calculate base damage
        damage = random.randint(
            actor_state.attack_power * actor_state.accuracy // 100,
            actor_state.attack_power
        )
        
        # Apply modifiers based on state
        if action.state == ActionState.COMMIT:
            damage *= 1.2  # 20% bonus for committed attacks
        elif action.state == ActionState.RELEASE:
            damage *= 1.5  # 50% bonus for released attacks
            
        # Apply visibility modifier
        if action.visibility == ActionVisibility.HIDDEN:
            damage *= 1.3  # 30% bonus for hidden attacks
            
        return ActionResult(
            success=True,
            outcome="hit",
            damage=damage,
            state_changes={
                "target_health": -damage,
                "actor_stamina": -action.stamina_cost
            }
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

    def _resolve_block(self, action: Action, actor: ICombatant, target: Optional[ICombatant]) -> ActionResult:
        """Resolve block action."""
        actor_state = actor.get_state()
        
        # Calculate block effectiveness based on commitment
        block_power = actor_state.blocking_power
        if action.commitment == ActionCommitment.FULL:
            block_power *= 1.5  # 50% bonus for full commitment
        elif action.commitment == ActionCommitment.PARTIAL:
            block_power *= 1.2  # 20% bonus for partial commitment
            
        return ActionResult(
            success=True,
            outcome="blocking",
            state_changes={
                "actor_stamina": -action.stamina_cost,
                "actor_blocking_power": block_power
            }
        )

    def _resolve_evade(self, action: Action, actor: ICombatant) -> ActionResult:
        """Resolve evade action."""
        actor_state = actor.get_state()
        
        # Calculate evasion success chance based on speed and commitment
        base_chance = actor_state.speed / 10.0  # 10% per point of speed
        if action.commitment == ActionCommitment.FULL:
            base_chance *= 1.5  # 50% bonus for full commitment
            
        # Apply stealth modifier
        if action.visibility == ActionVisibility.HIDDEN:
            base_chance *= 1.3  # 30% bonus for hidden evasion
            
        success = random.random() < base_chance
        
        return ActionResult(
            success=success,
            outcome="evading" if success else "failed_evasion",
            state_changes={
                "actor_stamina": -action.stamina_cost,
                "actor_movement": 2.0 if success else 0.0  # Movement bonus on successful evasion
            }
        )

    def _resolve_movement(self, action: Action, actor: ICombatant) -> ActionResult:
        """Resolve movement action."""
        actor_state = actor.get_state()
        
        # Calculate movement distance based on speed and commitment
        base_distance = actor_state.mobility
        if action.commitment == ActionCommitment.FULL:
            base_distance *= 1.5  # 50% bonus for full commitment
            
        # Apply stealth modifier
        stealth_mod = 1.0
        if action.visibility == ActionVisibility.HIDDEN:
            stealth_mod = 0.7  # 30% penalty for stealthy movement
            base_distance *= stealth_mod
            
        # Calculate position change
        distance_change = base_distance
        if action.type == "move_backward":
            distance_change *= 0.8  # 20% penalty for backward movement
            
        # Calculate new position
        angle = math.radians(0 if action.type == "move_forward" else 180)
        dx = distance_change * math.cos(angle)
        dy = distance_change * math.sin(angle)
        
        state_changes = {
            "actor_stamina": -action.stamina_cost,
            "actor_position_x": actor_state.position_x + dx,
            "actor_position_y": actor_state.position_y + dy,
            "actor_movement": base_distance * stealth_mod
        }
            
        return ActionResult(
            success=True,
            outcome=action.type,
            state_changes=state_changes
        )

    def _resolve_neutral(self, action: Action, actor: ICombatant) -> ActionResult:
        """Resolve neutral action."""
        actor_state = actor.get_state()
        
        state_changes = {
            "actor_stamina": -action.stamina_cost
        }
        
        if action.type == "recover":
            # Recovery effectiveness based on commitment
            recovery_amount = actor_state.stamina_recovery
            if action.commitment == ActionCommitment.FULL:
                recovery_amount *= 1.5  # 50% bonus for full commitment
            state_changes["actor_stamina"] = recovery_amount
            
        elif action.type == "reset":
            # Reset all modifiers and return to neutral state
            state_changes.update({
                "actor_blocking_power": actor_state.max_blocking_power,
                "actor_movement": 0.0,
                "actor_visibility_level": 1.0
            })
            
        return ActionResult(
            success=True,
            outcome=action.type,
            state_changes=state_changes
        )
