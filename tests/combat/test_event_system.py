"""
Tests for the enhanced event system.

These tests verify the functionality of event categorization,
streaming, and compression capabilities.
"""

import pytest
from datetime import datetime, timedelta
from combat.lib.event_system import (
    EventCategory,
    EventImportance,
    EnhancedEvent,
    EventStream,
    EventManager
)
from tests.combat.conftest import PerformanceStats
from tests.combat.mocks import MockEventDispatcher

class TestEnhancedEvent:
    """Test suite for enhanced events."""
    
    def test_event_creation(self):
        """Test basic event creation."""
        event = EnhancedEvent(
            event_id="test_1",
            event_type="attack",
            category=EventCategory.COMBAT,
            importance=EventImportance.MAJOR,
            timestamp=datetime.now(),
            source_id="attacker_1",
            target_id="defender_1",
            data={"damage": 50, "type": "slash"}
        )
        
        assert event.event_id == "test_1"
        assert event.category == EventCategory.COMBAT
        assert event.importance == EventImportance.MAJOR
        assert event.data["damage"] == 50

    @pytest.fixture
    def sample_event(self):
        """Create a sample event for testing."""
        return EnhancedEvent(
            event_id="test_1",
            event_type="attack",
            category=EventCategory.COMBAT,
            importance=EventImportance.MAJOR,
            timestamp=datetime.now(),
            source_id="attacker_1",
            target_id="defender_1",
            data={"damage": 50, "type": "slash"}
        )

    def test_event_compression(self, sample_event):
        """Test event data compression."""
        # Initial state
        assert not sample_event.compressed
        assert sample_event._raw_data is None
        
        # Compress
        sample_event.compress()
        assert sample_event.compressed
        assert sample_event._raw_data is not None
        assert not sample_event.data  # Data cleared after compression
        
        # Decompress
        sample_event.decompress()
        assert not sample_event.compressed
        assert sample_event._raw_data is None
        assert sample_event.data == {"damage": 50, "type": "slash"}

class TestEventStream:
    """Test suite for event streams."""
    
    def test_stream_configuration(self):
        """Test stream configuration options."""
        stream = EventStream(
            name="test_stream",
            categories={EventCategory.COMBAT, EventCategory.STATE},
            importance_threshold=EventImportance.MINOR,
            max_size=5
        )
        
        assert stream.name == "test_stream"
        assert EventCategory.COMBAT in stream.categories
        assert stream.importance_threshold == EventImportance.MINOR
        assert stream.max_size == 5

    @pytest.fixture
    def combat_stream(self):
        """Create a combat event stream."""
        return EventStream(
            name="combat",
            categories={EventCategory.COMBAT, EventCategory.STATE},
            importance_threshold=EventImportance.MINOR,
            max_size=5
        )

    def test_event_filtering(self, combat_stream, sample_event):
        """Test event filtering by category and importance."""
        # Valid event
        assert combat_stream.add_event(sample_event)
        
        # Wrong category
        debug_event = EnhancedEvent(
            event_id="debug_1",
            event_type="log",
            category=EventCategory.DEBUG,
            importance=EventImportance.MINOR,
            timestamp=datetime.now(),
            source_id="system",
            target_id=None,
            data={"message": "test"}
        )
        assert not combat_stream.add_event(debug_event)
        
        # Too low importance
        low_importance = EnhancedEvent(
            event_id="minor_1",
            event_type="move",
            category=EventCategory.COMBAT,
            importance=EventImportance.DEBUG,
            timestamp=datetime.now(),
            source_id="player",
            target_id=None,
            data={"distance": 1}
        )
        assert not combat_stream.add_event(low_importance)

    def test_max_size_limit(self, combat_stream):
        """Test stream size limiting."""
        # Add more events than max_size
        for i in range(10):
            event = EnhancedEvent(
                event_id=f"test_{i}",
                event_type="attack",
                category=EventCategory.COMBAT,
                importance=EventImportance.MAJOR,
                timestamp=datetime.now(),
                source_id="attacker",
                target_id="defender",
                data={"index": i}
            )
            combat_stream.add_event(event)
            
        # Should only keep last 5
        events = combat_stream.get_events()
        assert len(events) == 5
        assert events[-1].data["index"] == 9  # Last event added

    def test_time_range_filtering(self, combat_stream):
        """Test event filtering by time range."""
        base_time = datetime.now()
        
        # Add events at different times
        for i in range(5):
            event = EnhancedEvent(
                event_id=f"test_{i}",
                event_type="attack",
                category=EventCategory.COMBAT,
                importance=EventImportance.MAJOR,
                timestamp=base_time + timedelta(minutes=i),
                source_id="attacker",
                target_id="defender",
                data={"index": i}
            )
            combat_stream.add_event(event)
            
        # Get events in range
        events = combat_stream.get_events(
            start_time=base_time + timedelta(minutes=1),
            end_time=base_time + timedelta(minutes=3)
        )
        assert len(events) == 3
        assert events[0].data["index"] == 1
        assert events[-1].data["index"] == 3

class TestEventManager:
    """Test suite for event manager."""
    
    def test_manager_initialization(self):
        """Test event manager initialization."""
        manager = EventManager()
        
        # Verify default streams
        assert "combat" in manager._streams
        assert "animation" in manager._streams
        assert "ai_training" in manager._streams
        assert "debug" in manager._streams
        
        # Verify stream configurations
        combat_stream = manager.get_stream("combat")
        assert EventCategory.COMBAT in combat_stream.categories
        assert combat_stream.importance_threshold == EventImportance.MINOR

    @pytest.fixture
    def manager(self):
        """Create an event manager."""
        return EventManager()

    def test_stream_creation(self, manager):
        """Test stream creation and validation."""
        # Create custom stream
        manager.create_stream(
            "custom",
            {EventCategory.META},
            EventImportance.CRITICAL,
            100
        )
        
        # Verify stream creation
        assert "custom" in manager._streams
        custom_stream = manager.get_stream("custom")
        assert EventCategory.META in custom_stream.categories
        assert custom_stream.importance_threshold == EventImportance.CRITICAL
        
        # Create new stream
        manager.create_stream(
            "custom",
            {EventCategory.META},
            EventImportance.CRITICAL,
            100
        )
        assert "custom" in manager._streams
        
        # Duplicate stream should fail
        with pytest.raises(ValueError):
            manager.create_stream(
                "custom",
                {EventCategory.META},
                EventImportance.CRITICAL,
                100
            )

    def test_event_routing(self, manager):
        """Test event routing to appropriate streams."""
        # Create test event
        event = EnhancedEvent(
            event_id="test_1",
            event_type="attack",
            category=EventCategory.COMBAT,
            importance=EventImportance.MAJOR,
            timestamp=datetime.now(),
            source_id="attacker",
            target_id="defender",
            data={"damage": 50}
        )
        
        # Dispatch event
        manager.dispatch_event(event)
        
        # Verify routing
        assert len(manager.get_stream("combat").get_events()) == 1
        assert len(manager.get_stream("ai_training").get_events()) == 1
        assert len(manager.get_stream("animation").get_events()) == 0
        
        manager.dispatch_event(event)
        
        # Should be in combat and ai_training streams
        assert len(manager.get_stream("combat").get_events()) == 1
        assert len(manager.get_stream("ai_training").get_events()) == 1
        # Should not be in animation stream
        assert len(manager.get_stream("animation").get_events()) == 0

    def test_event_handlers(self, manager):
        """Test event handler registration and execution."""
        # Set up test handler
        received_events = []
        def handler(event):
            received_events.append(event)
            
        # Subscribe handler
        manager.subscribe("attack", handler)
            
        # Subscribe to attacks
        manager.subscribe("attack", handler)
        
        # Dispatch events
        attack_event = EnhancedEvent(
            event_id="attack_1",
            event_type="attack",
            category=EventCategory.COMBAT,
            importance=EventImportance.MAJOR,
            timestamp=datetime.now(),
            source_id="attacker",
            target_id="defender",
            data={"damage": 50}
        )
        
        move_event = EnhancedEvent(
            event_id="move_1",
            event_type="move",
            category=EventCategory.MOVEMENT,
            importance=EventImportance.MINOR,
            timestamp=datetime.now(),
            source_id="player",
            target_id=None,
            data={"distance": 1}
        )
        
        manager.dispatch_event(attack_event)
        manager.dispatch_event(move_event)
        
        # Should only receive attack event
        assert len(received_events) == 1
        assert received_events[0].event_type == "attack"

    def test_error_handling(self, manager):
        """Test handler error handling."""
        # Set up handlers
        def failing_handler(event):
            raise Exception("Handler failure")
            
        def working_handler(event):
            pass  # This should still be called
            
        # Subscribe both handlers
        manager.subscribe("test", failing_handler)
        manager.subscribe("test", working_handler)
            
        manager.subscribe("test", failing_handler)
        manager.subscribe("test", working_handler)
        
        # Should not raise exception
        event = EnhancedEvent(
            event_id="test_1",
            event_type="test",
            category=EventCategory.DEBUG,
            importance=EventImportance.DEBUG,
            timestamp=datetime.now(),
            source_id="system",
            target_id=None,
            data={}
        )
        manager.dispatch_event(event)  # Should not raise

    def test_stream_clearing(self, manager):
        """Test stream clearing."""
        # Create and dispatch test event
        event = EnhancedEvent(
            event_id="test_1",
            event_type="test",
            category=EventCategory.COMBAT,
            importance=EventImportance.MAJOR,
            timestamp=datetime.now(),
            source_id="test",
            target_id=None,
            data={}
        )
        manager.dispatch_event(event)
        
        # Verify event was dispatched
        assert len(manager.get_stream("combat").get_events()) == 1
        
        # Clear stream
        manager.clear_stream("combat")
        assert len(manager.get_stream("combat").get_events()) == 0

    def test_performance(self, manager, performance_stats):
        """Test event system performance."""
        # Measure event dispatch performance
        start_time = datetime.now()
        for i in range(1000):
            event = EnhancedEvent(
                event_id=f"perf_{i}",
                event_type="test",
                category=EventCategory.COMBAT,
                importance=EventImportance.MINOR,
                timestamp=datetime.now(),
                source_id="test",
                target_id=None,
                data={"index": i}
            )
            manager.dispatch_event(event)
        dispatch_time = (datetime.now() - start_time).total_seconds()
        performance_stats.record_operation("event_dispatch", dispatch_time)
        
        # Measure event retrieval performance
        start_time = datetime.now()
        for _ in range(100):
            manager.get_stream("combat").get_events()
        retrieval_time = (datetime.now() - start_time).total_seconds()
        performance_stats.record_operation("event_retrieval", retrieval_time)
        
        # Verify performance
        assert dispatch_time < 1.0  # Should handle 1000 events quickly
        assert retrieval_time < 0.1  # Should retrieve events efficiently
        
        manager.dispatch_event(event)
        assert len(manager.get_stream("combat").get_events()) == 1
        
        manager.clear_stream("combat")
        assert len(manager.get_stream("combat").get_events()) == 0
