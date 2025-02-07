"""
Action system interfaces for the combat system.
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import Dict, Optional, Protocol


class ActionStateType(Enum):
    """Possible states for an action."""
    FEINT = auto()      # Initial state, can be cancelled
    COMMIT = auto()     # Action is committed, may be cancellable
    RELEASE = auto()    # Action is executing
    RECOVERY = auto()   # Post-action recovery phase
    COMPLETE = auto()   # Action is finished


class ActionVisibility(Enum):
    """How visible an action is to opponents."""
    TELEGRAPHED = auto()  # Clearly visible
    HIDDEN = auto()       # Stealthy action

@dataclass
class ActionState:
    """State information for an action."""
    action_id: str
    action_type: str
    source_id: str
    target_id: Optional[str]
    state: ActionStateType
    visibility: ActionVisibility
    properties: Dict[str, any]


class IActionSystem(Protocol):
    """Interface for the action system."""
    
    def create_action(self, action_type: str, source_id: str, target_id: Optional[str] = None) -> ActionState:
        """Create a new action."""
        ...

    def get_action_state(self, action_id: str) -> Optional[ActionState]:
        """Get the current state of an action."""
        ...

    def update_action_state(self, action_id: str, new_state: ActionState) -> None:
        """Update the state of an action."""
        ...

    def validate_action(self, action: ActionState) -> bool:
        """Validate if an action can be executed."""
        ...

    def cancel_action(self, action_id: str) -> bool:
        """Attempt to cancel an action."""
        ...
