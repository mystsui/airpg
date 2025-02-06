"""
State Manager Adapter Module

This module provides an adapter that implements the IStateManager interface
while maintaining compatibility with the existing state management logic.
"""

from typing import Any, Dict, Optional, Tuple
from dataclasses import replace
from combat.interfaces import (
    IStateManager,
    CombatantState,
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

class StateTransitionError(Exception):
    """Raised when a state transition is invalid."""
    pass

class StateManagerAdapter(IStateManager):
    """
    Adapter class that implements IStateManager interface while maintaining
    compatibility with existing state management.
    """
    
    def __init__(self):
        """Initialize the state manager."""
        self._states: Dict[str, Any] = {}
        self._state_history: Dict[str, list] = {}
        self._timing_manager: ITimingManager = TimingSystem()
        self._awareness_manager: IAwarenessManager = AwarenessSystem()
        self._transition_rules = {
            "try_attack": self._validate_attack_transition,
            "blocking": self._validate_block_transition,
            "evading": self._validate_evade_transition,
            "move_forward": self._validate_movement_transition,
            "move_backward": self._validate_movement_transition
        }

    def get_state(self, entity_id: str) -> Any:
        """
        Get the current state of an entity.
        
        Args:
            entity_id: The ID of the entity
            
        Returns:
            The current state of the entity
        """
        return self._states.get(entity_id)

    def update_state(self, entity_id: str, new_state: Any) -> None:
        """
        Update the state of an entity.
        
        Args:
            entity_id: The ID of the entity
            new_state: The new state to apply
            
        Raises:
            StateTransitionError: If the state transition is invalid
        """
        current_state = self._states.get(entity_id)
        
        # Validate state transition if current state exists
        if current_state:
            if not self.validate_state_transition(current_state, new_state):
                raise StateTransitionError(
                    f"Invalid state transition for entity {entity_id}"
                )
            
            # Store in history
            if entity_id not in self._state_history:
                self._state_history[entity_id] = []
            self._state_history[entity_id].append(current_state)
            
        # Update state
        self._states[entity_id] = new_state

    def validate_state_transition(self, current_state: Any, new_state: Any) -> bool:
        """
        Validate if a state transition is valid.
        
        Args:
            current_state: The current state
            new_state: The proposed new state
            
        Returns:
            bool indicating if the transition is valid
        """
        # Handle CombatantState transitions
        if isinstance(current_state, CombatantState) and isinstance(new_state, CombatantState):
            return self._validate_combatant_transition(current_state, new_state)
            
        # Handle other state types
        return True

    def _validate_combatant_transition(self, current: CombatantState, new: CombatantState) -> bool:
        """Validate transitions between combatant states."""
        # Validate health changes
        new_health = new.stats.get("health", 100)
        current_health = current.stats.get("health", 100)
        if new_health > current_health:
            # Health can only increase through healing actions
            new_action = new.stats.get("action")
            if not (new_action and new_action.get("type") == "recover"):
                return False
                
        # Validate stamina changes
        if new.stamina > current.stamina:
            # Stamina can only increase through recovery
            new_action = new.stats.get("action")
            if not (new_action and new_action.get("type") == "recover"):
                return False
                
        # Validate action transitions
        current_action = current.stats.get("action")
        new_action = new.stats.get("action")
        if current_action and new_action:
            current_type = current_action.get("type")
            new_type = new_action.get("type")
            current_state = current_action.get("state")
            new_state = new_action.get("state")
            
            # Validate action state transitions
            if current_state and new_state:
                if not self._validate_action_state_transition(
                    ActionState(current_state),
                    ActionState(new_state),
                    current_action.get("commitment") if current_action else None
                ):
                    return False
            
            # Use transition rules if available
            if new_type and new_type in self._transition_rules:
                return self._transition_rules[new_type](current, new)
                
        return True

    def _validate_action_state_transition(self,
                                       current_state: ActionState,
                                       new_state: ActionState,
                                       commitment: Optional[str]) -> bool:
        """Validate action state transitions."""
        # Can't transition if fully committed
        if commitment == ActionCommitment.FULL.value:
            return False
            
        # Valid state progressions
        valid_transitions = {
            ActionState.FEINT: {ActionState.COMMIT, ActionState.RELEASE},
            ActionState.COMMIT: {ActionState.RELEASE},
            ActionState.RELEASE: {ActionState.RECOVERY},
            ActionState.RECOVERY: set()  # Can't transition from recovery
        }
        
        return new_state in valid_transitions.get(current_state, set())

    def _validate_attack_transition(self, current: CombatantState, new: CombatantState) -> bool:
        """Validate attack-related transitions."""
        current_action = current.stats.get("action")
        current_type = current_action.get("type") if current_action else None
        current_commitment = current_action.get("commitment") if current_action else None
        
        # Can't attack if fully committed to another action
        if current_commitment == ActionCommitment.FULL.value:
            return False
            
        # Can only attack if not already attacking or blocking
        if current_type in ["try_attack", "release_attack", "blocking"]:
            return False
            
        return True

    def _validate_block_transition(self, current: CombatantState, new: CombatantState) -> bool:
        """Validate block-related transitions."""
        current_action = current.stats.get("action")
        current_type = current_action.get("type") if current_action else None
        current_commitment = current_action.get("commitment") if current_action else None
        
        # Can't block if fully committed
        if current_commitment == ActionCommitment.FULL.value:
            return False
            
        # Can't block while attacking
        if current_type in ["try_attack", "release_attack"]:
            return False
            
        # Can't block with insufficient stamina
        if new.stamina < 1:  # Minimum stamina for blocking
            return False
            
        return True

    def _validate_evade_transition(self, current: CombatantState, new: CombatantState) -> bool:
        """Validate evasion-related transitions."""
        current_action = current.stats.get("action")
        current_type = current_action.get("type") if current_action else None
        current_commitment = current_action.get("commitment") if current_action else None
        
        # Can't evade if fully committed
        if current_commitment == ActionCommitment.FULL.value:
            return False
            
        # Can't evade while attacking or blocking
        if current_type in ["try_attack", "release_attack", "blocking"]:
            return False
            
        # Can't evade with insufficient stamina
        if new.stamina < 3:  # Minimum stamina for evading
            return False
            
        return True

    def _validate_movement_transition(self, current: CombatantState, new: CombatantState) -> bool:
        """Validate movement-related transitions."""
        current_action = current.stats.get("action")
        current_type = current_action.get("type") if current_action else None
        current_commitment = current_action.get("commitment") if current_action else None
        
        # Can't move if fully committed
        if current_commitment == ActionCommitment.FULL.value:
            return False
            
        # Can't move while in certain states
        if current_type in ["try_attack", "release_attack", "blocking", "evading"]:
            return False
            
        # Can't move with insufficient stamina
        if new.stamina < 4:  # Minimum stamina for movement
            return False
            
        return True

    def get_state_history(self, entity_id: str, limit: Optional[int] = None) -> list:
        """
        Get the state history for an entity.
        
        Args:
            entity_id: The ID of the entity
            limit: Optional limit on number of historical states to return
            
        Returns:
            List of historical states
        """
        history = self._state_history.get(entity_id, [])
        if limit:
            return history[-limit:]
        return history.copy()

    def rollback_state(self, entity_id: str) -> bool:
        """
        Rollback to the previous state for an entity.
        
        Args:
            entity_id: The ID of the entity
            
        Returns:
            bool indicating if rollback was successful
        """
        history = self._state_history.get(entity_id, [])
        if not history:
            return False
            
        previous_state = history.pop()
        self._states[entity_id] = previous_state
        return True

    def clear_history(self, entity_id: str) -> None:
        """
        Clear the state history for an entity.
        
        Args:
            entity_id: The ID of the entity
        """
        if entity_id in self._state_history:
            self._state_history[entity_id] = []
