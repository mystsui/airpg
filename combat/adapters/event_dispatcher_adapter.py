"""
Event Dispatcher Adapter Module

This module provides an adapter that implements the IEventDispatcher interface
while maintaining compatibility with the existing event handling logic.
"""

from typing import Dict, List, Callable, Optional, Set
from collections import defaultdict
from combat.interfaces import (
    IEventDispatcher,
    CombatEvent
)
from combat.lib.event_system import (
    EventCategory,
    EventImportance,
    EventStream,
    EventManager
)

class EventDispatcherAdapter(IEventDispatcher):
    """
    Adapter class that implements IEventDispatcher interface while maintaining
    compatibility with existing event handling.
    """
    
    def __init__(self):
        """Initialize the event dispatcher."""
        self._event_manager = EventManager()
        self._handlers: Dict[str, List[Callable[[CombatEvent], None]]] = defaultdict(list)
        self._category_map = {
            "combatant_added": EventCategory.META,
            "action_completed": EventCategory.COMBAT,
            "state_changed": EventCategory.STATE,
            "battle_ended": EventCategory.META,
            "try_attack": EventCategory.COMBAT,
            "release_attack": EventCategory.COMBAT,
            "blocking": EventCategory.COMBAT,
            "evading": EventCategory.COMBAT,
            "move_forward": EventCategory.MOVEMENT,
            "move_backward": EventCategory.MOVEMENT,
            "turn_around": EventCategory.MOVEMENT
        }
        self._importance_map = {
            "battle_ended": EventImportance.CRITICAL,
            "action_completed": EventImportance.MAJOR,
            "state_changed": EventImportance.MAJOR,
            "try_attack": EventImportance.MAJOR,
            "release_attack": EventImportance.MAJOR,
            "blocking": EventImportance.MAJOR,
            "evading": EventImportance.MAJOR,
            "move_forward": EventImportance.MINOR,
            "move_backward": EventImportance.MINOR,
            "turn_around": EventImportance.MINOR,
            "combatant_added": EventImportance.MINOR
        }
        
        # Create default streams
        self._event_manager.create_stream(
            "combat",
            {EventCategory.COMBAT, EventCategory.STATE},
            EventImportance.MINOR,
            1000
        )
        self._event_manager.create_stream(
            "animation",
            {EventCategory.ANIMATION, EventCategory.MOVEMENT},
            EventImportance.MINOR,
            500
        )
        self._event_manager.create_stream(
            "ai_training",
            {EventCategory.COMBAT, EventCategory.STATE, EventCategory.AI},
            EventImportance.MAJOR,
            5000
        )
        self._event_manager.create_stream(
            "debug",
            {category for category in EventCategory},
            EventImportance.DEBUG,
            200
        )

    def dispatch(self, event: CombatEvent) -> None:
        """
        Dispatch a combat event to registered handlers.
        
        Args:
            event: The event to dispatch
        """
        # Enhance event with category and importance
        category = self._category_map.get(event.event_type, EventCategory.META)
        importance = self._importance_map.get(event.event_type, EventImportance.MINOR)
        
        # Create enhanced event
        enhanced_event = {
            "event_id": event.event_id,
            "event_type": event.event_type,
            "category": category,
            "importance": importance,
            "timestamp": event.timestamp,
            "source_id": event.source_id,
            "target_id": event.target_id,
            "data": event.data
        }
        
        # Dispatch to event manager
        self._event_manager.dispatch_event(enhanced_event)
        
        # Notify handlers
        for handler in self._handlers.get(event.event_type, []):
            try:
                handler(event)
            except Exception as e:
                print(f"Error in event handler: {str(e)}")
        
        # Notify wildcard handlers
        for handler in self._handlers.get("*", []):
            try:
                handler(event)
            except Exception as e:
                print(f"Error in wildcard handler: {str(e)}")

    def subscribe(self, event_type: str, handler: Callable[[CombatEvent], None]) -> None:
        """
        Subscribe to combat events.
        
        Args:
            event_type: Type of events to subscribe to
            handler: Handler function
        """
        self._handlers[event_type].append(handler)

    def unsubscribe(self, event_type: str, handler: Callable[[CombatEvent], None]) -> None:
        """
        Unsubscribe from combat events.
        
        Args:
            event_type: Type of events to unsubscribe from
            handler: Handler to remove
        """
        if event_type in self._handlers:
            self._handlers[event_type] = [
                h for h in self._handlers[event_type]
                if h != handler
            ]

    def get_stream(self, name: str) -> EventStream:
        """
        Get an event stream by name.
        
        Args:
            name: Stream identifier
            
        Returns:
            The requested event stream
        """
        return self._event_manager.get_stream(name)

    def get_events(self,
                  stream_name: str,
                  start_time: Optional[float] = None,
                  end_time: Optional[float] = None,
                  decompressed: bool = True) -> List[CombatEvent]:
        """
        Get events from a stream.
        
        Args:
            stream_name: Stream to get events from
            start_time: Optional start of time range
            end_time: Optional end of time range
            decompressed: Whether to decompress events
            
        Returns:
            List of events
        """
        stream = self.get_stream(stream_name)
        return stream.get_events(start_time, end_time, decompressed)

    def clear_stream(self, name: str) -> None:
        """
        Clear all events from a stream.
        
        Args:
            name: Stream identifier
        """
        self._event_manager.clear_stream(name)
