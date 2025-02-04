"""
Combat System Interface Definitions

This package contains the core interfaces that define the combat system's architecture.
These interfaces provide the contract for implementing the various components of the system.
"""

from typing import Protocol, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from .timing import CombatTiming
from .action_system import ActionState, ActionVisibility, ActionCommitment
from .awareness_system import AwarenessZone

# Core data structures
@dataclass
class CombatantState:
    """Represents the complete state of a combatant."""
    entity_id: str
    health: float
    max_health: float
    stamina: float
    max_stamina: float
    position: str
    facing: str
    blocking_power: float
    action: Optional[dict] = None
    team: Optional[str] = None
    # New fields for enhanced combat mechanics
    speed: float = 1.0
    stealth: float = 1.0
    perception: float = 1.0
    awareness_zone: Optional[AwarenessZone] = None
    visibility_level: float = 1.0
    last_clear_position: Optional[Tuple[float, float]] = None
    position_x: float = 0.0
    position_y: float = 0.0
    movement: float = 0.0

@dataclass
class Action:
    """Represents a combat action."""
    type: str
    time: float  # in BTUs
    stamina_cost: float
    source_id: str
    target_id: Optional[str] = None
    status: str = "pending"
    result: Optional[str] = None
    # New fields for enhanced action system
    state: ActionState = ActionState.FEINT
    visibility: ActionVisibility = ActionVisibility.TELEGRAPHED
    commitment: ActionCommitment = ActionCommitment.NONE
    phase_duration: float = 1.0  # in BTUs
    feint_cost: float = 0.0
    speed_modifier: float = 1.0

@dataclass
class ActionResult:
    """Represents the result of an action execution."""
    success: bool
    outcome: str
    damage: Optional[float] = None
    state_changes: Optional[dict] = None

@dataclass
class CombatEvent:
    """Represents a combat event."""
    event_id: str
    event_type: str
    timestamp: datetime
    source_id: str
    target_id: Optional[str]
    data: dict

# New interfaces for enhanced systems
class ITimingManager(Protocol):
    """Interface for managing combat timing."""
    
    def convert_to_btu(self, ms: int) -> float:
        """Convert milliseconds to BTUs."""
        ...
    
    def apply_speed(self, btu: float, speed: float) -> float:
        """Apply speed modifier to BTU time."""
        ...
    
    def register_modifier(self, source: str, value: float, duration: Optional[int] = None) -> None:
        """Register a time modifier."""
        ...

class IAwarenessManager(Protocol):
    """Interface for managing combat awareness."""
    
    def update_awareness(self,
                        observer_id: str,
                        target_id: str,
                        observer_stats: dict,
                        target_stats: dict,
                        distance: float,
                        angle: float,
                        current_time: float) -> Any:
        """Update awareness state between combatants."""
        ...
    
    def get_awareness(self,
                     observer_id: str,
                     target_id: str) -> Optional[Any]:
        """Get current awareness state."""
        ...
    
    def clear_awareness(self, combatant_id: str) -> None:
        """Clear all awareness states for a combatant."""
        ...

# Core combat interfaces
class ICombatant(Protocol):
    """Interface for combatant entities."""
    
    def get_state(self) -> CombatantState:
        """Get the current state of the combatant."""
        ...
    
    def apply_action(self, action: Action) -> None:
        """Apply an action to the combatant."""
        ...
    
    def validate_action(self, action: Action) -> bool:
        """Validate if an action can be performed."""
        ...
    
    def is_within_range(self, distance: float) -> bool:
        """Check if target is within attack range."""
        ...
    
    def is_facing_opponent(self, opponent: 'ICombatant') -> bool:
        """Check if facing the opponent."""
        ...
    
    def is_defeated(self) -> bool:
        """Check if combatant is defeated."""
        ...

class IActionResolver(Protocol):
    """Interface for resolving combat actions."""
    
    def resolve(self, action: Action, actor: ICombatant, target: Optional[ICombatant]) -> ActionResult:
        """Resolve an action between combatants."""
        ...
    
    def validate(self, action: Action, actor: ICombatant) -> bool:
        """Validate if an action can be performed."""
        ...
    
    def get_available_actions(self, actor: ICombatant) -> List[Action]:
        """Get list of available actions for a combatant."""
        ...

class IStateManager(Protocol):
    """Interface for managing combat state."""
    
    def get_state(self, entity_id: str) -> Any:
        """Get the current state of an entity."""
        ...
    
    def update_state(self, entity_id: str, new_state: Any) -> None:
        """Update the state of an entity."""
        ...
    
    def validate_state_transition(self, current_state: Any, new_state: Any) -> bool:
        """Validate if a state transition is valid."""
        ...

class IEventDispatcher(Protocol):
    """Interface for combat event handling."""
    
    def dispatch(self, event: CombatEvent) -> None:
        """Dispatch a combat event to registered handlers."""
        ...
    
    def subscribe(self, event_type: str, handler: Callable[[CombatEvent], None]) -> None:
        """Subscribe to combat events."""
        ...
    
    def unsubscribe(self, event_type: str, handler: Callable[[CombatEvent], None]) -> None:
        """Unsubscribe from combat events."""
        ...

# Export all interfaces and types
__all__ = [
    'CombatantState',
    'Action',
    'ActionResult',
    'CombatEvent',
    'ICombatant',
    'IActionResolver',
    'IStateManager',
    'IEventDispatcher',
    'ITimingManager',
    'IAwarenessManager'
]
