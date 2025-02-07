"""
Action System - Simplified state management
"""

from typing import Dict, Optional
from combat.interfaces import (
    ActionState,
    ActionStateType,
    ActionVisibility,
    IActionSystem
)

from combat.lib.actions_library import determine_action_visibility

class ActionSystem(IActionSystem):
    """Manages action execution and state transitions."""
    
    def __init__(self):
        """Initialize the action system."""
        self._valid_transitions = {
            ActionStateType.FEINT: {ActionStateType.RELEASE, ActionStateType.COMPLETE},  # Can release or cancel
            ActionStateType.RELEASE: {ActionStateType.RECOVERY},  # Released actions go to recovery
            ActionStateType.RECOVERY: {ActionStateType.COMPLETE},  # Recovery leads to completion
            ActionStateType.COMPLETE: set()  # Terminal state
        }
        self._actions: Dict[str, ActionState] = {}
        
    def validate_transition(self, current: ActionStateType, next_state: ActionStateType) -> bool:
        """Validate state transition."""
        return next_state in self._valid_transitions.get(current, set())
        
    def calculate_visibility(self, visibility: ActionVisibility, stealth: float, movement: float) -> float:
        """Calculate action visibility level."""
        if visibility == ActionVisibility.TELEGRAPHED:
            return 1.0
            
        base_visibility = 1.0 / (stealth + 1.0)
        movement_penalty = movement * 0.5
        return min(1.0, base_visibility + movement_penalty)
        
    def is_visible(self, action: ActionState, stealth: float, perception: float) -> bool:
        """Check if action is visible."""
        if action.visibility == ActionVisibility.TELEGRAPHED:
            return True
            
        visibility_level = self.calculate_visibility(
            action.visibility,
            stealth,
            0.0  # Movement handled separately
        )
        return visibility_level * perception >= 0.5

    def can_cancel(self, action: ActionState) -> bool:
        """Check if action can be cancelled."""
        return action.state == ActionStateType.FEINT

    def create_action(self, action_type: str, source_id: str, target_id: Optional[str] = None) -> ActionState:
        """Create a new action."""
        action = ActionState(
            action_id=f"{action_type}_{len(self._actions)}",
            action_type=action_type,
            source_id=source_id,
            target_id=target_id,
            state=ActionStateType.FEINT,
            visibility=determine_action_visibility(action_type),
            properties={}
        )
        
        self._actions[action.action_id] = action
        return action

    def get_action_state(self, action_id: str) -> Optional[ActionState]:
        """Get the current state of an action."""
        return self._actions.get(action_id)

    def update_action_state(self, action_id: str, new_state: ActionState) -> None:
        """Update the state of an action."""
        if action_id not in self._actions:
            raise ValueError(f"No action found with id {action_id}")
            
        current_state = self._actions[action_id]
        if not self.validate_transition(current_state.state, new_state.state):
            raise ValueError(f"Invalid state transition from {current_state.state} to {new_state.state}")
            
        self._actions[action_id] = new_state

    def validate_action(self, action: ActionState) -> bool:
        """Validate if an action can be executed."""
        current_state = self._actions.get(action.action_id)
        if not current_state:
            return True  # New actions are always valid
        return self.validate_transition(current_state.state, action.state)

    def cancel_action(self, action_id: str) -> bool:
        """Attempt to cancel an action."""
        action = self._actions.get(action_id)
        if not action or not self.can_cancel(action):
            return False
            
        # Create completed state
        cancelled_state = ActionState(
            action_id=action.action_id,
            action_type=action.action_type,
            source_id=action.source_id,
            target_id=action.target_id,
            state=ActionStateType.COMPLETE,
            visibility=action.visibility,
            properties=action.properties
        )
        
        self._actions[action_id] = cancelled_state
        return True