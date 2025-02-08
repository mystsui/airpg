from typing import Dict, List, Callable, Any
from collections import defaultdict
import logging
from .event import (
    EventBase, CombatEvent, ActionEvent, 
    CombatStartEvent, CombatEndEvent
)

class EventBus:
    """
    Event bus for handling combat event publication and subscription.
    Implements the observer pattern for event handling.
    """
    def __init__(self):
        self._subscribers: Dict[str, List[Callable[[EventBase], None]]] = defaultdict(list)
        self._logger = logging.getLogger(__name__)

    def subscribe(self, event_type: str, handler: Callable[[CombatEvent], None]) -> None:
        """
        Subscribe a handler to a specific event type.
        
        Args:
            event_type: Type of event to subscribe to
            handler: Callback function to handle the event
        """
        self._subscribers[event_type].append(handler)
        self._logger.debug(f"Handler {handler.__name__} subscribed to {event_type}")

    def unsubscribe(self, event_type: str, handler: Callable[[CombatEvent], None]) -> None:
        """
        Unsubscribe a handler from a specific event type.
        
        Args:
            event_type: Type of event to unsubscribe from
            handler: Handler to remove
        """
        if event_type in self._subscribers:
            self._subscribers[event_type] = [
                h for h in self._subscribers[event_type] if h != handler
            ]
            self._logger.debug(f"Handler {handler.__name__} unsubscribed from {event_type}")

    def publish(self, event_type: str, data: dict) -> None:
        """
        Publish an event to all subscribed handlers.
        
        Args:
            event_type: The event to publish
            data: The data associated with the event
        """
        if event_type in self._subscribers:
            event = self._create_event(event_type, data)
            for handler in self._subscribers[event_type]:
                handler(event)

    def _create_event(self, event_type: str, data: dict) -> EventBase:
        """
        Create the appropriate event object based on type.
        
        Args:
            event_type: The type of event
            data: The data associated with the event
            
        Returns:
            The created event object
        """
        try:
            if event_type == "combat.start":
                return CombatStartEvent(
                    combat_id=data["combat_id"],
                    participants=data["participants"],
                    initial_state=data["initial_state"]
                )
            elif event_type == "combat.end":
                return CombatEndEvent(
                    combat_id=data["combat_id"],
                    final_state=data["final_state"],
                    winner_id=data.get("winner_id")
                )
            elif event_type == "combat.action":
                return ActionEvent(
                    action=data["action"],
                    actor_id=data["actor_id"],
                    previous_state=data["pre_state"],
                    current_state=data["post_state"],
                    result=data.get("result", {})
                )
            else:
                return CombatEvent(event_type=event_type)
        except KeyError as e:
            self._logger.error(f"Missing required data field: {e}")
            raise ValueError(f"Missing required data field: {e}")

    def _get_handlers_for_event(self, event_type: str) -> List[Callable[[CombatEvent], None]]:
        """
        Get all handlers for a specific event type, including wildcard subscribers.
        
        Args:
            event_type: The event type to get handlers for
            
        Returns:
            List of handler functions
        """
        # Get specific handlers
        handlers = self._subscribers.get(event_type, []).copy()
        
        # Get wildcard handlers
        handlers.extend(self._subscribers.get("*", []))
        
        return handlers

class EventBusMiddleware:
    """
    Middleware for intercepting and modifying events before they reach handlers.
    """
    def __init__(self, event_bus: EventBus):
        self._event_bus = event_bus
        self._middleware: List[Callable[[CombatEvent], CombatEvent]] = []

    def add_middleware(self, middleware: Callable[[CombatEvent], CombatEvent]) -> None:
        """
        Add a middleware function to the processing chain.
        
        Args:
            middleware: Function that takes and returns a CombatEvent
        """
        self._middleware.append(middleware)

    def publish(self, event: CombatEvent) -> None:
        """
        Publish an event through the middleware chain.
        
        Args:
            event: The event to publish
        """
        processed_event = self._process_middleware(event)
        self._event_bus.publish(processed_event)

    def _process_middleware(self, event: CombatEvent) -> CombatEvent:
        """
        Process an event through all middleware functions.
        
        Args:
            event: The event to process
            
        Returns:
            The processed event
        """
        current_event = event
        for middleware in self._middleware:
            current_event = middleware(current_event)
        return current_event

# Example middleware functions
def logging_middleware(event: CombatEvent) -> CombatEvent:
    """Log all events passing through the system."""
    logging.info(f"Event processed: {event.event_type} - {event.data}")
    return event

def validation_middleware(event: CombatEvent) -> CombatEvent:
    """Validate event data before processing."""
    if not hasattr(event, 'event_type'):
        raise ValueError("Event must have event_type")
    if not hasattr(event, 'data'):
        raise ValueError("Event must have data")
    return event