"""
Tests for the action system.

These tests verify the functionality of action states,
visibility mechanics, and commitment levels.
"""

import pytest
from datetime import datetime
from combat.lib.action_system import (
    ActionStateType,
    ActionVisibility,
    ActionCommitment,
    ActionPhase,
    ActionSystem,
    ActionState
)
from tests.combat.conftest import PerformanceStats

class TestActionStateTransitions:
    """Test suite for action state transitions."""

    @pytest.fixture
    def action_system(self):
        """Create a fresh action system."""
        return ActionSystem()

    def test_state_transitions(self, action_system):
        """Test valid state transitions."""
        # Start with feint
        assert action_system.validate_transition(
            ActionStateType.FEINT,
            ActionStateType.COMMIT
        )
        assert action_system.validate_transition(
            ActionStateType.FEINT,
            ActionStateType.RELEASE
        )
        
        # Commit to release
        assert action_system.validate_transition(
            ActionStateType.COMMIT,
            ActionStateType.RELEASE
        )
        
        # Release to recovery
        assert action_system.validate_transition(
            ActionStateType.RELEASE,
            ActionStateType.RECOVERY
        )
        
        # Can't transition from recovery
        assert not action_system.validate_transition(
            ActionStateType.RECOVERY,
            ActionStateType.FEINT
        )

    def test_invalid_transitions(self, action_system):
        """Test invalid state transitions."""
        # Can't skip states
        assert not action_system.validate_transition(
            ActionStateType.FEINT,
            ActionStateType.RECOVERY
        )
        
        # Can't go backwards
        assert not action_system.validate_transition(
            ActionStateType.COMMIT,
            ActionStateType.FEINT
        )
        assert not action_system.validate_transition(
            ActionStateType.RELEASE,
            ActionStateType.COMMIT
        )
        
    def test_state_properties(self, action_system):
        """Test action state properties."""
        state = action_system.start_action(
            "test",
            ActionVisibility.TELEGRAPHED
        )
        
        # Initial state
        assert state.action_type == "test"
        assert state.state == ActionStateType.FEINT
        assert state.phase == ActionPhase.STARTUP
        assert state.elapsed_time == 0.0
        assert state.phase_time == 0.0
        assert state.total_time == 0.0

class TestActionVisibility:
    """Test suite for action visibility mechanics."""

    @pytest.fixture
    def action_system(self):
        """Create a fresh action system."""
        return ActionSystem()

    def test_visibility_modifiers(self, action_system):
        """Test visibility modifier calculations."""
        # Base visibility
        assert action_system.calculate_visibility(
            ActionVisibility.TELEGRAPHED,
            stealth=1.0,
            movement=0.0
        ) == 1.0
        
        # Hidden action
        assert action_system.calculate_visibility(
            ActionVisibility.HIDDEN,
            stealth=5.0,
            movement=0.0
        ) < 0.5
        
        # Movement reduces stealth
        assert action_system.calculate_visibility(
            ActionVisibility.HIDDEN,
            stealth=5.0,
            movement=1.0
        ) > action_system.calculate_visibility(
            ActionVisibility.HIDDEN,
            stealth=5.0,
            movement=0.0
        )

    def test_visibility_thresholds(self, action_system):
        """Test visibility threshold checks."""
        # Telegraphed actions always visible
        assert action_system.is_visible(
            ActionVisibility.TELEGRAPHED,
            stealth=10.0,
            movement=0.0,
            perception=1.0
        )
        
        # Hidden actions depend on stats
        assert action_system.is_visible(
            ActionVisibility.HIDDEN,
            stealth=1.0,
            movement=0.0,
            perception=5.0
        )
        assert not action_system.is_visible(
            ActionVisibility.HIDDEN,
            stealth=5.0,
            movement=0.0,
            perception=1.0
        )

    def test_edge_cases(self, action_system):
        """Test visibility edge cases."""
        # Zero stats
        assert action_system.calculate_visibility(
            ActionVisibility.HIDDEN,
            stealth=0.0,
            movement=0.0
        ) == 1.0  # Should be fully visible
        
        # Very high stats
        assert action_system.calculate_visibility(
            ActionVisibility.HIDDEN,
            stealth=100.0,
            movement=0.0
        ) < 0.1  # Should be nearly invisible
        
        # Movement cancels stealth
        assert action_system.calculate_visibility(
            ActionVisibility.HIDDEN,
            stealth=100.0,
            movement=2.0
        ) > 0.5  # Should be more visible

class TestActionCommitment:
    """Test suite for action commitment mechanics."""

    @pytest.fixture
    def action_system(self):
        """Create a fresh action system."""
        return ActionSystem()

    def test_commitment_costs(self, action_system):
        """Test commitment level costs."""
        base_cost = 10.0
        
        # No commitment has no extra cost
        assert action_system.calculate_cost(
            base_cost,
            ActionCommitment.NONE
        ) == base_cost
        
        # Partial commitment increases cost
        assert action_system.calculate_cost(
            base_cost,
            ActionCommitment.PARTIAL
        ) > base_cost
        
        # Full commitment has highest cost
        assert action_system.calculate_cost(
            base_cost,
            ActionCommitment.FULL
        ) > action_system.calculate_cost(
            base_cost,
            ActionCommitment.PARTIAL
        )

    def test_commitment_cancellation(self, action_system):
        """Test commitment cancellation rules."""
        # No commitment can always cancel
        assert action_system.can_cancel(ActionCommitment.NONE)
        
        # Partial commitment has cancel cost
        cost = action_system.get_cancel_cost(ActionCommitment.PARTIAL)
        assert cost > 0
        
        # Full commitment cannot cancel
        assert not action_system.can_cancel(ActionCommitment.FULL)
        with pytest.raises(ValueError):
            action_system.get_cancel_cost(ActionCommitment.FULL)

    def test_edge_cases(self, action_system):
        """Test commitment edge cases."""
        # Zero base cost
        assert action_system.calculate_cost(0.0, ActionCommitment.FULL) == 0.0
        
        # Very high base cost
        high_cost = 1000.0
        assert action_system.calculate_cost(
            high_cost,
            ActionCommitment.FULL
        ) == high_cost * action_system.FULL_COMMIT_COST

class TestActionPhases:
    """Test suite for action phase mechanics."""

    @pytest.fixture
    def action_system(self):
        """Create a fresh action system."""
        return ActionSystem()

    def test_phase_timing(self, action_system):
        """Test phase timing calculations."""
        base_duration = 1.0
        
        # Startup phase
        startup = action_system.calculate_phase_duration(
            ActionPhase.STARTUP,
            base_duration
        )
        assert startup > 0
        
        # Active phase
        active = action_system.calculate_phase_duration(
            ActionPhase.ACTIVE,
            base_duration
        )
        assert active > startup
        
        # Recovery phase
        recovery = action_system.calculate_phase_duration(
            ActionPhase.RECOVERY,
            base_duration
        )
        assert recovery > 0

    def test_phase_interruption(self, action_system):
        """Test phase interruption rules."""
        # Can interrupt startup
        assert action_system.can_interrupt(ActionPhase.STARTUP)
        
        # Can't interrupt active without commitment
        assert not action_system.can_interrupt(ActionPhase.ACTIVE)
        
        # Recovery depends on commitment
        assert action_system.can_interrupt(
            ActionPhase.RECOVERY,
            commitment=ActionCommitment.NONE
        )
        assert not action_system.can_interrupt(
            ActionPhase.RECOVERY,
            commitment=ActionCommitment.FULL
        )

    def test_edge_cases(self, action_system):
        """Test phase timing edge cases."""
        # Zero duration
        assert action_system.calculate_phase_duration(
            ActionPhase.STARTUP,
            0.0
        ) == 0.0
        
        # Very short duration
        assert action_system.calculate_phase_duration(
            ActionPhase.ACTIVE,
            0.001
        ) > 0.0
        
        # Very long duration
        long_duration = 1000.0
        assert action_system.calculate_phase_duration(
            ActionPhase.RECOVERY,
            long_duration
        ) == long_duration * action_system.RECOVERY_DURATION

class TestIntegration:
    """Integration tests for action system."""

    @pytest.fixture
    def action_system(self):
        """Create a fresh action system."""
        return ActionSystem()

    def test_complete_action_flow(self, action_system):
        """Test complete action execution flow."""
        # Initial state
        state = action_system.start_action(
            action_type="attack",
            visibility=ActionVisibility.TELEGRAPHED,
            commitment=ActionCommitment.PARTIAL
        )
        assert state.phase == ActionPhase.STARTUP
        assert state.state == ActionStateType.FEINT
        
        # Progress through phases
        state = action_system.update_action(state, 0.5)  # Half startup time
        assert state.phase == ActionPhase.STARTUP
        
        state = action_system.update_action(state, 1.0)  # Complete startup
        assert state.phase == ActionPhase.ACTIVE
        assert state.state == ActionStateType.COMMIT
        
        state = action_system.update_action(state, 2.0)  # Complete active
        assert state.phase == ActionPhase.RECOVERY
        assert state.state == ActionStateType.RELEASE
        
        state = action_system.update_action(state, 3.0)  # Complete recovery
        assert state.phase == ActionPhase.COMPLETE
        assert state.state == ActionStateType.RECOVERY

    def test_performance(self, action_system, performance_stats):
        """Test action system performance."""
        # Measure state update performance
        start_time = datetime.now()
        state = action_system.start_action("test", ActionVisibility.TELEGRAPHED)
        for _ in range(1000):
            state = action_system.update_action(state, 0.016)  # 60 FPS
        update_time = (datetime.now() - start_time).total_seconds()
        performance_stats.record_operation("action_update", update_time)
        
        # Measure validation performance
        start_time = datetime.now()
        for _ in range(1000):
            action_system.validate_transition(
                ActionStateType.FEINT,
                ActionStateType.COMMIT
            )
        validation_time = (datetime.now() - start_time).total_seconds()
        performance_stats.record_operation("state_validation", validation_time)
        
        # Verify performance
        assert update_time < 0.1  # Should handle 1000 updates quickly
        assert validation_time < 0.1  # Should validate quickly

    def test_edge_cases(self, action_system):
        """Test integration edge cases."""
        # Zero time update
        state = action_system.start_action(
            "test",
            ActionVisibility.TELEGRAPHED
        )
        updated = action_system.update_action(state, 0.0)
        assert updated.phase_time == 0.0
        assert updated.total_time == 0.0
        
        # Very small time step
        updated = action_system.update_action(state, 0.0001)
        assert updated.phase_time > 0.0
        assert updated.total_time > 0.0
        
        # Very large time step
        updated = action_system.update_action(state, 1000.0)
        assert updated.phase == ActionPhase.COMPLETE
        assert updated.state == ActionStateType.RECOVERY
