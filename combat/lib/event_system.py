"""
Enhanced Event System

This module provides an event system with support for categorization,
streaming, compression, and importance-based filtering.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Set, Any, Callable
from datetime import datetime
import json
import zlib
from collections import deque

class EventCategory(Enum):
    """Categories for event classification."""
    COMBAT = auto()    # Combat-related events
    MOVEMENT = auto()  # Movement and positioning
    STATE = auto()     # State changes
    ANIMATION = auto() # Visual effects
    AI = auto()        # AI decision making
    META = auto()      # System events
    DEBUG = auto()     # Debug information

class EventImportance(Enum):
    """Event importance levels."""
    CRITICAL = 4  # Must never be missed
    MAJOR = 3     # Important gameplay events
    MINOR = 2     # Regular updates
    DEBUG = 1     # Debug information

@dataclass
class EnhancedEvent:
    """Enhanced event with categorization and compression."""
    event_id: str
    event_type: str
    category: EventCategory
    importance: EventImportance
    timestamp: datetime
    source_id: str
    target_id: Optional[str]
    data: Dict[str, Any]
    _raw_data: Optional[bytes] = None
    compressed: bool = False
    
    def compress(self) -> None:
        """Compress event data."""
        if not self.compressed and self.data:
            json_data = json.dumps(self.data).encode('utf-8')
            self._raw_data = zlib.compress(json_data)
            self.data = {}
            self.compressed = True
            
    def decompress(self) -> None:
        """Decompress event data."""
        if self.compressed and self._raw_data:
            json_data = zlib.decompress(self._raw_data).decode('utf-8')
            self.data = json.loads(json_data)
            self._raw_data = None
            self.compressed = False

class EventStream:
    """Stream for filtering and storing events."""
    
    def __init__(self,
                name: str,
                categories: Set[EventCategory],
                importance_threshold: EventImportance,
                max_size: int):
        """
        Initialize event stream.
        
        Args:
            name: Stream identifier
            categories: Event categories to include
            importance_threshold: Minimum event importance
            max_size: Maximum events to store
        """
        self.name = name
        self.categories = categories
        self.importance_threshold = importance_threshold
        self.max_size = max_size
        self._events: deque[EnhancedEvent] = deque(maxlen=max_size)
        
    def add_event(self, event: EnhancedEvent) -> bool:
        """
        Add event to stream if it meets criteria.
        
        Args:
            event: Event to add
            
        Returns:
            Whether event was added
        """
        if (event.category in self.categories and
            event.importance.value >= self.importance_threshold.value):
            self._events.append(event)
            return True
        return False
        
    def get_events(self,
                  start_time: Optional[datetime] = None,
                  end_time: Optional[datetime] = None,
                  decompressed: bool = True) -> List[EnhancedEvent]:
        """
        Get events, optionally filtered by time range.
        
        Args:
            start_time: Optional start of time range
            end_time: Optional end of time range
            decompressed: Whether to decompress events
            
        Returns:
            List of matching events
        """
        events = list(self._events)
        
        # Filter by time range
        if start_time:
            events = [e for e in events if e.timestamp >= start_time]
        if end_time:
            events = [e for e in events if e.timestamp <= end_time]
            
        # Decompress if requested
        if decompressed:
            for event in events:
                if event.compressed:
                    event.decompress()
                    
        return events
        
    def clear(self) -> None:
        """Clear all events from stream."""
        self._events.clear()

class EventManager:
    """Manages event streams and routing."""
    
    def __init__(self):
        """Initialize with default streams."""
        self._streams: Dict[str, EventStream] = {}
        self._handlers: Dict[str, List[Callable[[EnhancedEvent], None]]] = {}
        
        # Create default streams
        self.create_stream(
            "combat",
            {EventCategory.COMBAT, EventCategory.STATE},
            EventImportance.MINOR,
            1000
        )
        self.create_stream(
            "animation",
            {EventCategory.ANIMATION, EventCategory.MOVEMENT},
            EventImportance.MINOR,
            500
        )
        self.create_stream(
            "ai_training",
            {EventCategory.COMBAT, EventCategory.STATE, EventCategory.AI},
            EventImportance.MAJOR,
            5000
        )
        self.create_stream(
            "debug",
            {category for category in EventCategory},
            EventImportance.DEBUG,
            200
        )
        
    def create_stream(self,
                     name: str,
                     categories: Set[EventCategory],
                     importance_threshold: EventImportance,
                     max_size: int) -> None:
        """
        Create new event stream.
        
        Args:
            name: Stream identifier
            categories: Event categories to include
            importance_threshold: Minimum event importance
            max_size: Maximum events to store
            
        Raises:
            ValueError: If stream already exists
        """
        if name in self._streams:
            raise ValueError(f"Stream {name} already exists")
            
        self._streams[name] = EventStream(
            name=name,
            categories=categories,
            importance_threshold=importance_threshold,
            max_size=max_size
        )
        
    def dispatch_event(self, event: EnhancedEvent) -> None:
        """
        Dispatch event to appropriate streams.
        
        Args:
            event: Event to dispatch
        """
        # Route to streams
        for stream in self._streams.values():
            stream.add_event(event)
            
        # Notify handlers
        for handler in self._handlers.get(event.event_type, []):
            try:
                handler(event)
            except Exception as e:
                print(f"Error in event handler: {str(e)}")
                
    def subscribe(self, event_type: str, handler: Callable[[EnhancedEvent], None]) -> None:
        """
        Subscribe to events.
        
        Args:
            event_type: Type of events to subscribe to
            handler: Handler function
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
        
    def unsubscribe(self, event_type: str, handler: Callable[[EnhancedEvent], None]) -> None:
        """
        Unsubscribe from events.
        
        Args:
            event_type: Type of events to unsubscribe from
            handler: Handler to remove
        """
        if event_type in self._handlers:
            self._handlers[event_type].remove(handler)
            
    def get_stream(self, name: str) -> EventStream:
        """
        Get stream by name.
        
        Args:
            name: Stream identifier
            
        Returns:
            The requested stream
            
        Raises:
            KeyError: If stream doesn't exist
        """
        if name not in self._streams:
            raise KeyError(f"Stream {name} not found")
        return self._streams[name]
        
    def clear_stream(self, name: str) -> None:
        """
        Clear all events from a stream.
        
        Args:
            name: Stream identifier
        """
        if name in self._streams:
            self._streams[name].clear()
