"""
Action System

This module implements the core action mechanics including states,
phases, visibility, and commitment levels.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, Optional, Any

class ActionStateType(Enum):
    """States an action can be in."""
    FEINT = auto()    # Initial feint state
    COMMIT = auto()   # Committed to action
    RELEASE = auto()  # Action released
    RECOVERY = auto() # Recovery phase

class ActionVisibility(Enum):
    """How visible an action is."""
    TELEGRAPHED = auto()  # Clearly visible
    HIDDEN = auto()       # Stealthy action

class ActionCommitment(Enum):
    """Level of commitment to an action."""
    NONE = auto()     # No commitment
    PARTIAL = auto()  # Partial commitment
    FULL = auto()     # Full commitment

class ActionPhase(Enum):
    """Phases of action execution."""
    STARTUP = auto()   # Initial startup
    ACTIVE = auto()    # Active execution
    RECOVERY = auto()  # Recovery period
    COMPLETE = auto()  # Action completed

@dataclass
class ActionState:
    """Current state of an action."""
    action_type: str
    state: ActionStateType
    phase: ActionPhase
    visibility: ActionVisibility
    commitment: ActionCommitment
    elapsed_time: float = 0.0
    phase_time: float = 0.0
    total_time: float = 0.0
    modifiers: Dict[str, float] = field(default_factory=dict)

class ActionSystem:
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
        
    def start_action(self,
                    action_type: str,
                    visibility: ActionVisibility,
                    commitment: ActionCommitment = ActionCommitment.NONE) -> ActionState:
        """
        Start a new action.
        
        Args:
            action_type: Type of action
            visibility: Action visibility
            commitment: Action commitment level
            
        Returns:
            Initial action state
        """
        return ActionState(
            action_type=action_type,
            state=ActionStateType.FEINT,
            phase=ActionPhase.STARTUP,
            visibility=visibility,
            commitment=commitment,
            elapsed_time=0.0,
            phase_time=0.0,
            total_time=0.0
        )
        
    def update_action(self,
                     state: ActionState,
                     delta_time: float) -> ActionState:
        """
        Update action state.
        
        Args:
            state: Current action state
            delta_time: Time elapsed
            
        Returns:
            Updated action state
        """
        state.elapsed_time += delta_time
        state.phase_time += delta_time
        state.total_time += delta_time
        
        # Calculate phase durations
        startup_time = self.calculate_phase_duration(
            ActionPhase.STARTUP,
            1.0
        )
        active_time = self.calculate_phase_duration(
            ActionPhase.ACTIVE,
            1.0
        )
        recovery_time = self.calculate_phase_duration(
            ActionPhase.RECOVERY,
            1.0
        )
        
        # Update phase and state based on timing
        if state.phase == ActionPhase.STARTUP:
            if state.phase_time >= startup_time:
                state.phase = ActionPhase.ACTIVE
                state.state = ActionStateType.COMMIT
                state.phase_time = 0.0
                
        elif state.phase == ActionPhase.ACTIVE:
            if state.phase_time >= active_time:
                state.phase = ActionPhase.RECOVERY
                state.state = ActionStateType.RELEASE
                state.phase_time = 0.0
                
        elif state.phase == ActionPhase.RECOVERY:
            if state.phase_time >= recovery_time:
                state.phase = ActionPhase.COMPLETE
                state.state = ActionStateType.RECOVERY
                
        return state
