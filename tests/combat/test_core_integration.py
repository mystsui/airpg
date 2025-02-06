"""
Core Integration Tests

These tests verify the integration between core combat systems.
"""

import pytest
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

def execute_attack_sequence(combat_system, attacker, defender):
    """Execute a complete attack sequence."""
    # Approach sequence
    combat_system.execute_action(
        create_action(
            "move_forward",
            attacker.id,
            visibility=ActionVisibility.HIDDEN
        )
    )
    
    # Feint sequence
    combat_system.execute_action(
        create_action(
            "quick_attack",
            attacker.id,
            defender.id,
            visibility=ActionVisibility.HIDDEN,
            commitment=ActionCommitment.NONE
        )
    )
    
    # Main attack
    combat_system.execute_action(
        create_action(
            "heavy_attack",
            attacker.id,
            defender.id,
            commitment=ActionCommitment.FULL
        )
    )

def execute_defense_sequence(combat_system, defender, attacker):
    """Execute a complete defense sequence."""
    # Initial block
    combat_system.execute_action(
        create_action(
            "block",
            defender.id,
            commitment=ActionCommitment.PARTIAL
        )
    )
    
    # Counter attack
    combat_system.execute_action(
        create_action(
            "parry",
            defender.id,
            attacker.id,
            commitment=ActionCommitment.PARTIAL
        )
    )
    
    # Retreat
    combat_system.execute_action(
        create_action(
            "move_backward",
            defender.id
        )
    )

def execute_movement_sequence(combat_system, mover, target):
    """Execute a complete movement sequence."""
    # Forward movement
    combat_system.execute_action(
        create_action(
            "move_forward",
            mover.id
        )
    )
    
    # Evasive action
    combat_system.execute_action(
        create_action(
            "evade",
            mover.id
        )
    )
    
    # Reposition
    combat_system.execute_action(
        create_action(
            "move_backward",
            mover.id
        )
    )

class TestCombatFlow:
    """Test suite for complete combat flow."""

    @pytest.fixture
    def combat_system(self):
        """Create a fresh combat system."""
        return CombatSystem(
            duration=10000,  # 10 seconds
            distance=50,     # mid-range
            max_distance=100
        )

    def test_complete_combat_flow(self, combat_system):
        """Test a complete combat sequence with all components."""
        # Initialize combatants
        challenger = create_test_combatant(
            "challenger",
            stamina=100.0,
            speed=1.0,
            stealth=1.0
        )
        defender = create_test_combatant(
            "defender",
            stamina=100.0,
            speed=0.8,
            stealth=0.5
        )
        
        # Add combatants
        combat_system.add_combatant(challenger)
        combat_system.add_combatant(defender)
        
        # Verify initial states
        assert combat_system._state_manager.get_state(challenger.id) is not None
        assert combat_system._state_manager.get_state(defender.id) is not None
        
        # Execute combat sequence
        execute_attack_sequence(combat_system, challenger, defender)
        execute_defense_sequence(combat_system, defender, challenger)
        execute_movement_sequence(combat_system, challenger, defender)
        
        # Verify final states
        challenger_state = combat_system._state_manager.get_state(challenger.id)
        defender_state = combat_system._state_manager.get_state(defender.id)
        
        assert challenger_state.stamina < 100.0  # Should have used stamina
        assert defender_state.stamina < 100.0  # Should have used stamina
        
        # Verify event generation
        events = combat_system._event_dispatcher.get_stream("combat").get_events()
        assert len(events) > 0
        
        # Verify awareness states
        awareness = combat_system._awareness_system.get_awareness(
            challenger.id,
            defender.id
        )
        assert awareness is not None

    def test_state_transitions(self, combat_system):
        """Test state transitions through combat flow."""
        # Initialize combatants
        attacker = create_test_combatant("attacker")
        defender = create_test_combatant("defender")
        
        combat_system.add_combatant(attacker)
        combat_system.add_combatant(defender)
        
        # Execute attack action
        action = create_action(
            "quick_attack",
            attacker.id,
            defender.id
        )
        
        # Verify state progression
        combat_system.execute_action(action)
        
        # Should progress through states
        action_state = combat_system._action_system.get_action_state(action.action_id)
        assert action_state.state == ActionStateType.COMMIT
        
        # Complete action
        combat_system.update(1000)  # 1 second
        action_state = combat_system._action_system.get_action_state(action.action_id)
        assert action_state.state == ActionStateType.RECOVERY

    def test_event_propagation(self, combat_system):
        """Test event propagation through combat flow."""
        # Track events
        received_events = []
        
        def event_handler(event):
            received_events.append(event)
            
        # Subscribe to combat events
        combat_system._event_dispatcher.subscribe(
            "combat",
            event_handler
        )
        
        # Initialize combatants
        attacker = create_test_combatant("attacker")
        defender = create_test_combatant("defender")
        
        combat_system.add_combatant(attacker)
        combat_system.add_combatant(defender)
        
        # Execute combat sequence
        execute_attack_sequence(combat_system, attacker, defender)
        
        # Verify events
        assert len(received_events) > 0
        
        # Verify event order
        event_types = [e.event_type for e in received_events]
        assert "move_forward" in event_types
        assert "quick_attack" in event_types
        assert "heavy_attack" in event_types
        
        # Verify event data
        for event in received_events:
            assert event.source_id == attacker.id
            if event.event_type in ["quick_attack", "heavy_attack"]:
                assert event.target_id == defender.id

    def test_system_performance(self, combat_system, performance_stats):
        """Test performance of integrated systems."""
        # Initialize combatants
        attacker = create_test_combatant("attacker")
        defender = create_test_combatant("defender")
        
        combat_system.add_combatant(attacker)
        combat_system.add_combatant(defender)
        
        # Measure action execution
        start_time = datetime.now()
        for _ in range(100):
            execute_attack_sequence(combat_system, attacker, defender)
            combat_system.update(16)  # ~60 FPS
        execution_time = (datetime.now() - start_time).total_seconds()
        
        performance_stats.record_operation(
            "combat_flow",
            execution_time
        )
        
        # Verify performance
        assert execution_time < 1.0  # Should handle 100 sequences quickly
