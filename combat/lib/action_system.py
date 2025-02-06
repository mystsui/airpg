"""
Action System

This module implements the core action mechanics including states,
phases, visibility, and commitment levels.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, Any

from combat.interfaces import (
    ActionState,
    ActionStateType,
    ActionVisibility,
    ActionCommitment,
    ActionPhase,
    IActionSystem
)

class ActionSystem(IActionSystem):
    """Manages action execution and state transitions."""
    
    # Phase timing constants
    STARTUP_DURATION = 0.3   # 300ms startup
    ACTIVE_DURATION = 0.5    # 500ms active
    RECOVERY_DURATION = 0.2  # 200ms recovery
    
    # Commitment modifiers
    PARTIAL_COMMIT_COST = 1.2  # 20% extra cost
    FULL_COMMIT_COST = 1.5     # 50% extra cost
    PARTIAL_CANCEL_COST = 0.5  # 50% stamina cost to cancel
    
    def __init__(self):
        """Initialize the action system."""
        self._valid_transitions = {
            ActionStateType.FEINT: {ActionStateType.COMMIT, ActionStateType.RELEASE},
            ActionStateType.COMMIT: {ActionStateType.RELEASE},
            ActionStateType.RELEASE: {ActionStateType.RECOVERY},
            ActionStateType.RECOVERY: set()  # No transitions from recovery
        }
        self._actions: Dict[str, ActionState] = {}
        
    def validate_transition(self,
                          current: ActionStateType,
                          next_state: ActionStateType) -> bool:
        """
        Validate state transition.
        
        Args:
            current: Current action state
            next_state: Desired next state
            
        Returns:
            Whether transition is valid
        """
        return next_state in self._valid_transitions.get(current, set())
        
    def calculate_visibility(self,
                           visibility: ActionVisibility,
                           stealth: float,
                           movement: float) -> float:
        """
        Calculate action visibility level.
        
        Args:
            visibility: Base visibility type
            stealth: Stealth stat
            movement: Movement amount
            
        Returns:
            Visibility level (0.0 to 1.0)
        """
        if visibility == ActionVisibility.TELEGRAPHED:
            return 1.0
            
        # Hidden actions affected by stealth and movement
        base_visibility = 1.0 / (stealth + 1.0)
        movement_penalty = movement * 0.5  # Movement reduces stealth
        
        return min(1.0, base_visibility + movement_penalty)
        
    def is_visible(self,
                  visibility: ActionVisibility,
                  stealth: float,
                  movement: float,
                  perception: float) -> bool:
        """
        Check if action is visible.
        
        Args:
            visibility: Base visibility type
            stealth: Stealth stat
            movement: Movement amount
            perception: Observer's perception
            
        Returns:
            Whether action is visible
        """
        if visibility == ActionVisibility.TELEGRAPHED:
            return True
            
        visibility_level = self.calculate_visibility(
            visibility,
            stealth,
            movement
        )
        
        return visibility_level * perception >= 0.5
        
    def calculate_cost(self,
                      base_cost: float,
                      commitment: ActionCommitment) -> float:
        """
        Calculate total action cost.
        
        Args:
            base_cost: Base stamina cost
            commitment: Commitment level
            
        Returns:
            Total cost including commitment
        """
        if commitment == ActionCommitment.PARTIAL:
            return base_cost * self.PARTIAL_COMMIT_COST
        elif commitment == ActionCommitment.FULL:
            return base_cost * self.FULL_COMMIT_COST
        return base_cost
        
    def can_cancel(self, commitment: ActionCommitment) -> bool:
        """
        Check if action can be cancelled.
        
        Args:
            commitment: Action commitment level
            
        Returns:
            Whether action can be cancelled
        """
        return commitment != ActionCommitment.FULL
        
    def get_cancel_cost(self, commitment: ActionCommitment) -> float:
        """
        Get cost to cancel action.
        
        Args:
            commitment: Action commitment level
            
        Returns:
            Stamina cost to cancel
            
        Raises:
            ValueError: If action cannot be cancelled
        """
        if not self.can_cancel(commitment):
            raise ValueError("Cannot cancel fully committed action")
            
        if commitment == ActionCommitment.PARTIAL:
            return self.PARTIAL_CANCEL_COST
        return 0.0
        
    def calculate_phase_duration(self,
                               phase: ActionPhase,
                               base_duration: float) -> float:
        """
        Calculate phase duration.
        
        Args:
            phase: Action phase
            base_duration: Base action duration
            
        Returns:
            Phase duration in seconds
        """
        if phase == ActionPhase.STARTUP:
            return base_duration * self.STARTUP_DURATION
        elif phase == ActionPhase.ACTIVE:
            return base_duration * self.ACTIVE_DURATION
        elif phase == ActionPhase.RECOVERY:
            return base_duration * self.RECOVERY_DURATION
        return 0.0
        
    def can_interrupt(self,
                     phase: ActionPhase,
                     commitment: Optional[ActionCommitment] = None) -> bool:
        """
        Check if phase can be interrupted.
        
        Args:
            phase: Current action phase
            commitment: Optional commitment level
            
        Returns:
            Whether phase can be interrupted
        """
        if phase == ActionPhase.STARTUP:
            return True
        elif phase == ActionPhase.ACTIVE:
            return False  # Active phase cannot be interrupted
        elif phase == ActionPhase.RECOVERY:
            return not commitment or commitment != ActionCommitment.FULL
        return False

    def create_action(self, action_type: str, source_id: str, target_id: Optional[str] = None) -> ActionState:
        """Create a new action."""
        action = ActionState(
            action_id=f"{action_type}_{len(self._actions)}",
            action_type=action_type,
            source_id=source_id,
            target_id=target_id,
            state=ActionStateType.FEINT,
            phase=ActionPhase.STARTUP,
            visibility=ActionVisibility.TELEGRAPHED,
            commitment=ActionCommitment.NONE,
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
        if not action:
            return False
        if not self.can_cancel(action.commitment):
            return False
        del self._actions[action_id]
        return True
