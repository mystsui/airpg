"""
System Health Tests

These tests verify memory usage, timing, and edge cases
across the entire combat system.
"""

import pytest
import gc
import psutil
import os
from datetime import datetime
from combat.combat_system import CombatSystem
from combat.lib.action_system import (
    ActionStateType,
    ActionVisibility,
    ActionCommitment,
    ActionPhase
)
from combat.lib.event_system import (
    EventCategory,
    EventImportance,
    EnhancedEvent
)
from combat.lib.awareness_system import (
    AwarenessZone,
    EnvironmentConditions
)
from combat.lib.actions_library import (
    create_action,
    validate_action_chain
)
from tests.combat.conftest import (
    create_test_combatant,
    create_test_combatant_state,
    PerformanceStats
)

def get_process_memory():
    """Get current process memory usage."""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss

class TestMemoryUsage:
    """Test suite for memory usage patterns."""

    @pytest.fixture
    def combat_system(self):
        """Create a fresh combat system."""
        return CombatSystem(
            duration=10000,  # 10 seconds
            distance=50,     # mid-range
            max_distance=100
        )

    def test_object_creation(self, combat_system, performance_stats):
        """Test memory usage during object creation."""
        initial_memory = get_process_memory()
        
        # Create many combatants
        for i in range(100):
            combatant = create_test_combatant(f"test_{i}")
            combat_system.add_combatant(combatant)
            
        # Force garbage collection
        gc.collect()
        
        # Measure memory increase
        memory_increase = get_process_memory() - initial_memory
        performance_stats.record_operation("object_creation_memory", memory_increase)
        
        # Memory increase should be reasonable
        assert memory_increase < 10 * 1024 * 1024  # Less than 10MB

    def test_state_copies(self, combat_system, performance_stats):
        """Test memory usage during state management."""
        initial_memory = get_process_memory()
        
        # Create combatant
        combatant = create_test_combatant("test")
        combat_system.add_combatant(combatant)
        
        # Generate many state updates
        for i in range(1000):
            state = create_test_combatant_state(
                combatant.id,
                stamina=100.0 - i * 0.1,
                speed=1.0
            )
            combat_system._state_manager.update_state(state)
            
        # Force garbage collection
        gc.collect()
        
        # Measure memory increase
        memory_increase = get_process_memory() - initial_memory
        performance_stats.record_operation("state_copies_memory", memory_increase)
        
        # Memory increase should be reasonable
        assert memory_increase < 5 * 1024 * 1024  # Less than 5MB

    def test_event_accumulation(self, combat_system, performance_stats):
        """Test memory usage during event accumulation."""
        initial_memory = get_process_memory()
        
        # Create combatant
        combatant = create_test_combatant("test")
        combat_system.add_combatant(combatant)
        
        # Generate many events
        for i in range(1000):
            event = EnhancedEvent(
                event_id=f"test_{i}",
                event_type="test",
                category=EventCategory.COMBAT,
                importance=EventImportance.MINOR,
                timestamp=datetime.now(),
                source_id=combatant.id,
                target_id=None,
                data={"index": i}
            )
            combat_system._event_dispatcher.dispatch_event(event)
            
        # Force garbage collection
        gc.collect()
        
        # Measure memory increase
        memory_increase = get_process_memory() - initial_memory
        performance_stats.record_operation("event_memory", memory_increase)
        
        # Memory increase should be reasonable
        assert memory_increase < 5 * 1024 * 1024  # Less than 5MB

class TestTimingPerformance:
    """Test suite for timing-critical operations."""

    @pytest.fixture
    def combat_system(self):
        """Create a fresh combat system."""
        return CombatSystem(
            duration=10000,  # 10 seconds
            distance=50,     # mid-range
            max_distance=100
        )

    def test_action_resolution_timing(self, combat_system, performance_stats):
        """Test action resolution timing."""
        # Create combatants
        attacker = create_test_combatant("attacker")
        defender = create_test_combatant("defender")
        
        combat_system.add_combatant(attacker)
        combat_system.add_combatant(defender)
        
        # Measure resolution time
        start_time = datetime.now()
        for _ in range(1000):
            action = create_action(
                "quick_attack",
                attacker.id,
                defender.id
            )
            combat_system.execute_action(action)
            combat_system.update(16)  # ~60 FPS
            
        resolution_time = (datetime.now() - start_time).total_seconds()
        performance_stats.record_operation("action_resolution", resolution_time)
        
        # Should handle 1000 resolutions quickly
        assert resolution_time < 1.0

    def test_state_transition_timing(self, combat_system, performance_stats):
        """Test state transition timing."""
        # Create combatant
        combatant = create_test_combatant("test")
        combat_system.add_combatant(combatant)
        
        # Measure transition time
        start_time = datetime.now()
        for i in range(1000):
            state = create_test_combatant_state(
                combatant.id,
                stamina=100.0 - i * 0.1,
                speed=1.0
            )
            combat_system._state_manager.update_state(state)
            
        transition_time = (datetime.now() - start_time).total_seconds()
        performance_stats.record_operation("state_transition", transition_time)
        
        # Should handle 1000 transitions quickly
        assert transition_time < 0.5

    def test_event_dispatch_timing(self, combat_system, performance_stats):
        """Test event dispatch timing."""
        # Create combatant
        combatant = create_test_combatant("test")
        combat_system.add_combatant(combatant)
        
        # Add many handlers
        for i in range(10):
            combat_system._event_dispatcher.subscribe(
                "test",
                lambda e: None
            )
            
        # Measure dispatch time
        start_time = datetime.now()
        for i in range(1000):
            event = EnhancedEvent(
                event_id=f"test_{i}",
                event_type="test",
                category=EventCategory.COMBAT,
                importance=EventImportance.MINOR,
                timestamp=datetime.now(),
                source_id=combatant.id,
                target_id=None,
                data={"index": i}
            )
            combat_system._event_dispatcher.dispatch_event(event)
            
        dispatch_time = (datetime.now() - start_time).total_seconds()
        performance_stats.record_operation("event_dispatch", dispatch_time)
        
        # Should handle 1000 dispatches quickly
        assert dispatch_time < 0.5

class TestEdgeCases:
    """Test suite for system edge cases."""

    @pytest.fixture
    def combat_system(self):
        """Create a fresh combat system."""
        return CombatSystem(
            duration=10000,  # 10 seconds
            distance=50,     # mid-range
            max_distance=100
        )

    def test_resource_boundaries(self, combat_system):
        """Test system resource boundaries."""
        # Test zero stamina
        combatant = create_test_combatant(
            "test",
            stamina=0.0
        )
        combat_system.add_combatant(combatant)
        
        # Should not allow stamina-using actions
        action = create_action(
            "heavy_attack",
            combatant.id,
            "target"
        )
        result = combat_system.execute_action(action)
        assert not result.success
        
        # Test maximum distance
        far_combatant = create_test_combatant("far")
        combat_system.add_combatant(far_combatant)
        combat_system._state_manager.update_position(
            far_combatant.id,
            combat_system.max_distance + 1,
            0
        )
        
        # Should not allow actions beyond max distance
        action = create_action(
            "quick_attack",
            far_combatant.id,
            "target"
        )
        result = combat_system.execute_action(action)
        assert not result.success

    def test_timing_boundaries(self, combat_system):
        """Test system timing boundaries."""
        combatant = create_test_combatant("test")
        combat_system.add_combatant(combatant)
        
        # Test zero time update
        combat_system.update(0)
        
        # Test very small time step
        combat_system.update(0.001)
        
        # Test very large time step
        combat_system.update(1000.0)
        
        # System should remain stable
        assert combat_system._state_manager.get_state(combatant.id) is not None

    def test_system_recovery(self, combat_system):
        """Test system recovery from errors."""
        combatant = create_test_combatant("test")
        combat_system.add_combatant(combatant)
        
        # Force some errors
        try:
            combat_system._state_manager.update_state(None)
        except ValueError:
            pass
            
        try:
            combat_system._event_dispatcher.dispatch_event(None)
        except ValueError:
            pass
            
        # System should still function
        state = combat_system._state_manager.get_state(combatant.id)
        assert state is not None
        
        # Should handle new events
        event = EnhancedEvent(
            event_id="test",
            event_type="test",
            category=EventCategory.COMBAT,
            importance=EventImportance.MINOR,
            timestamp=datetime.now(),
            source_id=combatant.id,
            target_id=None,
            data={}
        )
        combat_system._event_dispatcher.dispatch_event(event)
