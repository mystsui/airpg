"""
Adapter Integration Tests

These tests verify the integration between adapters and core systems.
"""

import pytest
from datetime import datetime
from combat.combat_system import CombatSystem
from combat.adapters.combatant_adapter import CombatantAdapter
from combat.adapters.action_resolver_adapter import ActionResolverAdapter
from combat.adapters.state_manager_adapter import StateManagerAdapter
from combat.adapters.event_dispatcher_adapter import EventDispatcherAdapter
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

class TestAdapterIntegration:
    """Test suite for adapter integration."""

    @pytest.fixture
    def combat_system(self):
        """Create a fresh combat system."""
        return CombatSystem(
            duration=10000,  # 10 seconds
            distance=50,     # mid-range
            max_distance=100
        )

    def test_combatant_adapter_integration(self, combat_system):
        """Test CombatantAdapter integration."""
        # Create legacy combatant
        legacy_combatant = create_test_combatant(
            "legacy",
            stamina=100.0,
            speed=1.0
        )
        
        # Create adapter
        adapter = CombatantAdapter(legacy_combatant)
        
        # Add to system
        combat_system.add_combatant(adapter)
        
        # Verify state management
        state = combat_system._state_manager.get_state(adapter.id)
        assert state is not None
        assert state.stamina == 100.0
        assert state.speed == 1.0
        
        # Execute action through adapter
        action = create_action(
            "quick_attack",
            adapter.id,
            "target"
        )
        combat_system.execute_action(action)
        
        # Verify state update
        updated_state = combat_system._state_manager.get_state(adapter.id)
        assert updated_state.stamina < 100.0  # Should have used stamina

    def test_action_resolver_integration(self, combat_system):
        """Test ActionResolverAdapter integration."""
        # Create combatants
        attacker = create_test_combatant("attacker")
        defender = create_test_combatant("defender")
        
        combat_system.add_combatant(attacker)
        combat_system.add_combatant(defender)
        
        # Create action
        action = create_action(
            "heavy_attack",
            attacker.id,
            defender.id,
            commitment=ActionCommitment.FULL
        )
        
        # Execute through resolver
        result = combat_system._action_resolver.resolve_action(
            action,
            combat_system._state_manager.get_state(attacker.id),
            combat_system._state_manager.get_state(defender.id)
        )
        
        # Verify resolution
        assert result is not None
        assert result.success
        assert result.damage > 0
        assert result.stamina_cost > 0

    def test_state_manager_integration(self, combat_system):
        """Test StateManagerAdapter integration."""
        # Create combatant
        combatant = create_test_combatant("test")
        combat_system.add_combatant(combatant)
        
        # Get initial state
        initial_state = combat_system._state_manager.get_state(combatant.id)
        
        # Create state update
        updated_state = create_test_combatant_state(
            combatant.id,
            stamina=initial_state.stamina - 10,
            speed=initial_state.speed * 0.8
        )
        
        # Apply update
        combat_system._state_manager.update_state(updated_state)
        
        # Verify update
        current_state = combat_system._state_manager.get_state(combatant.id)
        assert current_state.stamina == updated_state.stamina
        assert current_state.speed == updated_state.speed
        
        # Verify history
        history = combat_system._state_manager.get_state_history(combatant.id)
        assert len(history) == 2  # Initial + update
        assert history[0].stamina == initial_state.stamina
        assert history[1].stamina == updated_state.stamina

    def test_event_dispatcher_integration(self, combat_system):
        """Test EventDispatcherAdapter integration."""
        # Track events
        combat_events = []
        movement_events = []
        
        def combat_handler(event):
            combat_events.append(event)
            
        def movement_handler(event):
            movement_events.append(event)
            
        # Subscribe to different categories
        combat_system._event_dispatcher.subscribe("combat", combat_handler)
        combat_system._event_dispatcher.subscribe("movement", movement_handler)
        
        # Create combatant
        combatant = create_test_combatant("test")
        combat_system.add_combatant(combatant)
        
        # Generate events
        combat_event = EnhancedEvent(
            event_id="test_1",
            event_type="attack",
            category=EventCategory.COMBAT,
            importance=EventImportance.MAJOR,
            timestamp=datetime.now(),
            source_id=combatant.id,
            target_id=None,
            data={"damage": 50}
        )
        
        movement_event = EnhancedEvent(
            event_id="test_2",
            event_type="move",
            category=EventCategory.MOVEMENT,
            importance=EventImportance.MINOR,
            timestamp=datetime.now(),
            source_id=combatant.id,
            target_id=None,
            data={"distance": 2}
        )
        
        # Dispatch events
        combat_system._event_dispatcher.dispatch_event(combat_event)
        combat_system._event_dispatcher.dispatch_event(movement_event)
        
        # Verify routing
        assert len(combat_events) == 1
        assert len(movement_events) == 1
        assert combat_events[0].event_type == "attack"
        assert movement_events[0].event_type == "move"

    def test_adapter_performance(self, combat_system, performance_stats):
        """Test adapter performance."""
        # Create test data
        combatant = create_test_combatant("test")
        combat_system.add_combatant(combatant)
        
        # Measure state updates
        start_time = datetime.now()
        for i in range(1000):
            state = create_test_combatant_state(
                combatant.id,
                stamina=100.0 - i * 0.1,
                speed=1.0
            )
            combat_system._state_manager.update_state(state)
        state_time = (datetime.now() - start_time).total_seconds()
        performance_stats.record_operation("state_updates", state_time)
        
        # Measure event dispatch
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
        event_time = (datetime.now() - start_time).total_seconds()
        performance_stats.record_operation("event_dispatch", event_time)
        
        # Verify performance
        assert state_time < 0.1  # Should handle 1000 updates quickly
        assert event_time < 0.1  # Should handle 1000 events quickly

    def test_adapter_error_handling(self, combat_system):
        """Test adapter error handling."""
        # Test invalid state update
        with pytest.raises(ValueError):
            combat_system._state_manager.update_state(None)
            
        # Test invalid action resolution
        with pytest.raises(ValueError):
            combat_system._action_resolver.resolve_action(
                None,
                None,
                None
            )
            
        # Test invalid event dispatch
        with pytest.raises(ValueError):
            combat_system._event_dispatcher.dispatch_event(None)
            
        # Test recovery after errors
        combatant = create_test_combatant("test")
        combat_system.add_combatant(combatant)
        
        # Should still work after errors
        state = combat_system._state_manager.get_state(combatant.id)
        assert state is not None
