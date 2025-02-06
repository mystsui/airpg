"""
Action resolver interfaces for the combat system.
"""

from typing import Any, Optional, Protocol
from .action_system import ActionState


class IActionResolver(Protocol):
    """Interface for resolving combat actions."""
    
    def resolve_action(self,
                      action: ActionState,
                      source_state: Any,
                      target_state: Optional[Any] = None) -> Any:
        """
        Resolve a combat action.
        
        Args:
            action: Action to resolve
            source_state: State of action source
            target_state: Optional state of action target
            
        Returns:
            Resolution result
        """
        ...

    def validate_action(self, action: ActionState) -> bool:
        """
        Validate if an action can be executed.
        
        Args:
            action: Action to validate
            
        Returns:
            Whether action is valid
        """
        ...

    def calculate_cost(self, action: ActionState) -> float:
        """
        Calculate action cost.
        
        Args:
            action: Action to calculate cost for
            
        Returns:
            Action cost
        """
        ...


class IStateManager(Protocol):
    """Interface for managing combat state."""
    
    def get_state(self, entity_id: str) -> Optional[Any]:
        """
        Get current state for an entity.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            Current state or None
        """
        ...

    def update_state(self, state: Any) -> None:
        """
        Update entity state.
        
        Args:
            state: New state
        """
        ...

    def get_state_history(self, entity_id: str) -> list[Any]:
        """
        Get state history for an entity.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            List of historical states
        """
        ...

    def rollback_state(self, entity_id: str, timestamp: float) -> bool:
        """
        Rollback entity state to a previous time.
        
        Args:
            entity_id: Entity ID
            timestamp: Time to rollback to
            
        Returns:
            Whether rollback succeeded
        """
        ...


class IEventDispatcher(Protocol):
    """Interface for dispatching combat events."""
    
    def dispatch_event(self, event: Any) -> None:
        """
        Dispatch a combat event.
        
        Args:
            event: Event to dispatch
        """
        ...

    def subscribe(self, event_type: str, handler: callable) -> None:
        """
        Subscribe to events.
        
        Args:
            event_type: Type of events to subscribe to
            handler: Event handler function
        """
        ...

    def unsubscribe(self, event_type: str, handler: callable) -> None:
        """
        Unsubscribe from events.
        
        Args:
            event_type: Event type to unsubscribe from
            handler: Handler to remove
        """
        ...

    def get_stream(self, stream_name: str) -> Any:
        """
        Get an event stream.
        
        Args:
            stream_name: Name of stream
            
        Returns:
            Event stream
        """
        ...
