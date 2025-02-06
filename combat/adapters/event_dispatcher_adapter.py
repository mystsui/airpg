"""
Event dispatcher adapter implementation.
"""

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from combat.interfaces import IEventDispatcher, CombatEvent

@dataclass
class EventStream:
    """Wrapper for event streams."""
    events: List[CombatEvent]
    
    def get_events(self) -> List[CombatEvent]:
        """Get all events in the stream."""
        return self.events


class EventDispatcherAdapter(IEventDispatcher):
    """Adapter for event dispatching system."""
    
    def __init__(self):
        """Initialize event dispatcher."""
        self._subscribers: Dict[str, List[Callable]] = {}
        self._event_streams: Dict[str, List[CombatEvent]] = {}
        
    def dispatch_event(self, event: CombatEvent) -> None:
        """
        Dispatch a combat event.
        
        Args:
            event: Event to dispatch
        """
        # Add to relevant streams
        stream_key = event.category.name.lower()
        if stream_key not in self._event_streams:
            self._event_streams[stream_key] = []
        self._event_streams[stream_key].append(event)
        
        # Notify subscribers
        if event.event_type in self._subscribers:
            for handler in self._subscribers[event.event_type]:
                handler(event)
                
    def subscribe(self, event_type: str, handler: Callable) -> None:
        """
        Subscribe to events.
        
        Args:
            event_type: Type of events to subscribe to
            handler: Event handler function
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)
        
    def unsubscribe(self, event_type: str, handler: Callable) -> None:
        """
        Unsubscribe from events.
        
        Args:
            event_type: Event type to unsubscribe from
            handler: Handler to remove
        """
        if event_type in self._subscribers:
            self._subscribers[event_type].remove(handler)
            if not self._subscribers[event_type]:
                del self._subscribers[event_type]
                
    def get_stream(self, stream_name: str) -> EventStream:
        """
        Get an event stream.
        
        Args:
            stream_name: Name of stream
            
        Returns:
            EventStream containing events
        """
        return EventStream(self._event_streams.get(stream_name, []))
