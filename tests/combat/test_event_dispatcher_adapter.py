"""
Tests for the EventDispatcherAdapter class.

These tests verify that the adapter correctly implements the IEventDispatcher interface
and maintains proper event handling with thread safety.
"""

import pytest
from threading import Thread
from queue import Queue
import time
from combat.adapters import EventDispatcherAdapter
from combat.interfaces import CombatEvent
from datetime import datetime

class TestEventDispatcherAdapter:
    """Test suite for EventDispatcherAdapter class."""

    @pytest.fixture
    def dispatcher(self):
        """Create a fresh event dispatcher instance for each test."""
        return EventDispatcherAdapter()

    @pytest.fixture
    def sample_event(self):
        """Create a sample combat event for testing."""
        return CombatEvent(
            event_id="test_1",
            event_type="test_event",
            timestamp=datetime.now(),
            source_id="source_1",
            target_id="target_1",
            data={"test": "data"}
        )

    def test_subscribe_and_dispatch(self, dispatcher, sample_event):
        """Test basic subscription and event dispatch."""
        received_events = []
        
        def handler(event):
            received_events.append(event)
            
        dispatcher.subscribe("test_event", handler)
        dispatcher.dispatch(sample_event)
        
        assert len(received_events) == 1
        assert received_events[0] == sample_event

    def test_unsubscribe(self, dispatcher, sample_event):
        """Test unsubscribing from events."""
        received_events = []
        
        def handler(event):
            received_events.append(event)
            
        dispatcher.subscribe("test_event", handler)
        dispatcher.unsubscribe("test_event", handler)
        dispatcher.dispatch(sample_event)
        
        assert len(received_events) == 0

    def test_multiple_subscribers(self, dispatcher, sample_event):
        """Test multiple subscribers for same event."""
        received_events_1 = []
        received_events_2 = []
        
        def handler1(event):
            received_events_1.append(event)
            
        def handler2(event):
            received_events_2.append(event)
            
        dispatcher.subscribe("test_event", handler1)
        dispatcher.subscribe("test_event", handler2)
        dispatcher.dispatch(sample_event)
        
        assert len(received_events_1) == 1
        assert len(received_events_2) == 1

    def test_event_history(self, dispatcher, sample_event):
        """Test event history tracking."""
        dispatcher.dispatch(sample_event)
        
        history = dispatcher.get_event_history()
        assert len(history) == 1
        assert history[0] == sample_event
        
        # Test history limit
        history_limited = dispatcher.get_event_history(limit=1)
        assert len(history_limited) == 1

    def test_clear_history(self, dispatcher, sample_event):
        """Test clearing event history."""
        dispatcher.dispatch(sample_event)
        dispatcher.clear_history()
        
        history = dispatcher.get_event_history()
        assert len(history) == 0

    def test_subscriber_count(self, dispatcher):
        """Test subscriber counting."""
        def handler1(event): pass
        def handler2(event): pass
        
        dispatcher.subscribe("test_event", handler1)
        assert dispatcher.get_subscriber_count("test_event") == 1
        
        dispatcher.subscribe("test_event", handler2)
        assert dispatcher.get_subscriber_count("test_event") == 2

    def test_get_all_event_types(self, dispatcher):
        """Test retrieving all event types."""
        def handler(event): pass
        
        dispatcher.subscribe("event1", handler)
        dispatcher.subscribe("event2", handler)
        
        event_types = dispatcher.get_all_event_types()
        assert "event1" in event_types
        assert "event2" in event_types
        assert len(event_types) == 2

    def test_has_subscribers(self, dispatcher):
        """Test checking for subscribers."""
        def handler(event): pass
        
        dispatcher.subscribe("test_event", handler)
        assert dispatcher.has_subscribers("test_event") is True
        assert dispatcher.has_subscribers("nonexistent") is False

    def test_subscribe_multiple(self, dispatcher, sample_event):
        """Test subscribing to multiple event types."""
        received_events = []
        
        def handler(event):
            received_events.append(event)
            
        event_types = ["event1", "event2"]
        dispatcher.subscribe_multiple(event_types, handler)
        
        event1 = CombatEvent(
            event_id="test_1",
            event_type="event1",
            timestamp=datetime.now(),
            source_id="source_1",
            target_id="target_1",
            data={}
        )
        
        event2 = CombatEvent(
            event_id="test_2",
            event_type="event2",
            timestamp=datetime.now(),
            source_id="source_1",
            target_id="target_1",
            data={}
        )
        
        dispatcher.dispatch(event1)
        dispatcher.dispatch(event2)
        
        assert len(received_events) == 2

    def test_unsubscribe_all(self, dispatcher):
        """Test unsubscribing from all event types."""
        def handler(event): pass
        
        dispatcher.subscribe("event1", handler)
        dispatcher.subscribe("event2", handler)
        
        dispatcher.unsubscribe_all(handler)
        
        assert dispatcher.has_subscribers("event1") is False
        assert dispatcher.has_subscribers("event2") is False

    def test_dispatch_batch(self, dispatcher):
        """Test batch event dispatching."""
        received_events = []
        
        def handler(event):
            received_events.append(event)
            
        dispatcher.subscribe("test_event", handler)
        
        events = [
            CombatEvent(
                event_id=f"test_{i}",
                event_type="test_event",
                timestamp=datetime.now(),
                source_id="source_1",
                target_id="target_1",
                data={}
            )
            for i in range(3)
        ]
        
        dispatcher.dispatch_batch(events)
        
        assert len(received_events) == 3
        assert len(dispatcher.get_event_history()) == 3

    def test_thread_safety(self, dispatcher):
        """Test thread-safe event dispatching and subscription."""
        received_events = Queue()
        
        def handler(event):
            received_events.put(event)
            
        dispatcher.subscribe("test_event", handler)
        
        def dispatch_events():
            for i in range(100):
                event = CombatEvent(
                    event_id=f"test_{i}",
                    event_type="test_event",
                    timestamp=datetime.now(),
                    source_id="source_1",
                    target_id="target_1",
                    data={"count": i}
                )
                dispatcher.dispatch(event)
                
        # Create multiple dispatch threads
        threads = [Thread(target=dispatch_events) for _ in range(5)]
        
        # Start all threads
        for thread in threads:
            thread.start()
            
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
            
        # Verify all events were received
        assert received_events.qsize() == 500  # 5 threads * 100 events each

    def test_handler_exception_handling(self, dispatcher, sample_event):
        """Test that handler exceptions don't affect other handlers."""
        received_events = []
        
        def failing_handler(event):
            raise Exception("Handler failure")
            
        def working_handler(event):
            received_events.append(event)
            
        dispatcher.subscribe("test_event", failing_handler)
        dispatcher.subscribe("test_event", working_handler)
        
        # Should not raise exception and working handler should still receive event
        dispatcher.dispatch(sample_event)
        
        assert len(received_events) == 1
