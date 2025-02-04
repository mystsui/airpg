"""
Tests for the awareness system.

These tests verify the functionality of awareness zones,
perception checks, and environmental effects.
"""

import pytest
from math import sqrt
from combat.lib.awareness_system import (
    AwarenessZone,
    PerceptionModifier,
    EnvironmentConditions,
    AwarenessState,
    PerceptionCheck,
    AwarenessSystem
)

class TestPerceptionCheck:
    """Test suite for perception calculations."""

    def test_base_difficulty(self):
        """Test distance-based difficulty calculations."""
        base_range = PerceptionCheck.BASE_PERCEPTION_RANGE
        
        # No penalty within base range
        assert PerceptionCheck.calculate_base_difficulty(base_range * 0.5, base_range) == 0.0
        assert PerceptionCheck.calculate_base_difficulty(base_range, base_range) == 0.0
        
        # Linear scaling in fuzzy range
        fuzzy_range = base_range * PerceptionCheck.FUZZY_RANGE_MULTIPLIER
        mid_fuzzy = (base_range + fuzzy_range) / 2
        assert PerceptionCheck.calculate_base_difficulty(mid_fuzzy, base_range) == 0.5
        
        # Maximum difficulty beyond fuzzy range
        assert PerceptionCheck.calculate_base_difficulty(fuzzy_range * 2, base_range) == 1.0

    def test_angle_modifier(self):
        """Test angle-based modifier calculations."""
        # Front view (no penalty)
        assert PerceptionCheck.apply_angle_modifier(0) == 0.0
        assert PerceptionCheck.apply_angle_modifier(45) == 0.0
        
        # Side view (linear scaling)
        assert PerceptionCheck.apply_angle_modifier(67.5) == 0.5
        assert PerceptionCheck.apply_angle_modifier(90) == 1.0
        
        # Rear quarter (increased penalty)
        assert PerceptionCheck.apply_angle_modifier(112.5) == 1.5
        assert PerceptionCheck.apply_angle_modifier(135) == 2.0
        
        # Rear view (maximum penalty)
        assert PerceptionCheck.apply_angle_modifier(180) == 2.0

    def test_confidence_calculation(self):
        """Test overall confidence calculations."""
        conditions = EnvironmentConditions(
            lighting_level=1.0,
            cover_density=0.0,
            distraction_level=0.0
        )
        
        # Perfect conditions
        confidence = PerceptionCheck.calculate_confidence(
            perception=10.0,
            stealth=1.0,
            distance=10.0,
            angle=0.0,
            conditions=conditions
        )
        assert confidence > 0.9  # Should be very high
        
        # Poor conditions
        confidence = PerceptionCheck.calculate_confidence(
            perception=1.0,
            stealth=10.0,
            distance=100.0,
            angle=180.0,
            conditions=EnvironmentConditions(
                lighting_level=0.2,
                cover_density=0.8,
                distraction_level=0.9
            )
        )
        assert confidence < 0.1  # Should be very low

class TestAwarenessState:
    """Test suite for awareness state management."""

    @pytest.fixture
    def basic_state(self):
        """Create a basic awareness state."""
        return AwarenessState(
            zone=AwarenessZone.FUZZY,
            confidence=0.6,
            last_clear_position=(10.0, 10.0),
            last_update_time=100.0
        )

    def test_state_properties(self, basic_state):
        """Test awareness state property access."""
        assert basic_state.zone == AwarenessZone.FUZZY
        assert basic_state.confidence == 0.6
        assert basic_state.last_clear_position == (10.0, 10.0)
        assert basic_state.last_update_time == 100.0
        assert isinstance(basic_state.modifiers, dict)

class TestAwarenessSystem:
    """Test suite for the awareness system."""

    @pytest.fixture
    def system(self):
        """Create a fresh awareness system."""
        return AwarenessSystem(EnvironmentConditions())

    @pytest.fixture
    def observer_stats(self):
        """Create sample observer stats."""
        return {
            "perception": 5.0,
            "position_x": 0.0,
            "position_y": 0.0
        }

    @pytest.fixture
    def target_stats(self):
        """Create sample target stats."""
        return {
            "stealth": 3.0,
            "position_x": 10.0,
            "position_y": 0.0,
            "movement": 0.5
        }

    def test_combatant_registration(self, system):
        """Test combatant registration."""
        system.register_combatant("observer1")
        assert "observer1" in system._awareness_states
        assert isinstance(system._awareness_states["observer1"], dict)

    def test_awareness_update(self, system, observer_stats, target_stats):
        """Test awareness state updates."""
        state = system.update_awareness(
            observer_id="observer1",
            target_id="target1",
            observer_stats=observer_stats,
            target_stats=target_stats,
            distance=10.0,
            angle=0.0,
            current_time=100.0
        )
        
        assert isinstance(state, AwarenessState)
        assert state.zone in AwarenessZone
        assert 0.0 <= state.confidence <= 1.0
        assert state.last_update_time == 100.0

    def test_awareness_zones(self, system, observer_stats, target_stats):
        """Test zone transitions based on confidence."""
        # Test clear zone (high confidence)
        state = system.update_awareness(
            "observer1", "target1",
            observer_stats, target_stats,
            distance=10.0, angle=0.0, current_time=100.0
        )
        assert state.zone == AwarenessZone.CLEAR
        
        # Test fuzzy zone (medium confidence)
        state = system.update_awareness(
            "observer1", "target1",
            observer_stats, target_stats,
            distance=75.0, angle=45.0, current_time=100.0
        )
        assert state.zone == AwarenessZone.FUZZY
        
        # Test hidden zone (low confidence)
        state = system.update_awareness(
            "observer1", "target1",
            observer_stats, target_stats,
            distance=150.0, angle=180.0, current_time=100.0
        )
        assert state.zone == AwarenessZone.HIDDEN

    def test_environmental_effects(self, system, observer_stats, target_stats):
        """Test environmental condition effects."""
        # Test good conditions
        system.update_conditions(EnvironmentConditions(
            lighting_level=1.0,
            cover_density=0.0,
            distraction_level=0.0
        ))
        
        good_state = system.update_awareness(
            "observer1", "target1",
            observer_stats, target_stats,
            distance=50.0, angle=45.0, current_time=100.0
        )
        
        # Test poor conditions
        system.update_conditions(EnvironmentConditions(
            lighting_level=0.2,
            cover_density=0.8,
            distraction_level=0.9
        ))
        
        poor_state = system.update_awareness(
            "observer1", "target1",
            observer_stats, target_stats,
            distance=50.0, angle=45.0, current_time=101.0
        )
        
        assert good_state.confidence > poor_state.confidence

    def test_awareness_persistence(self, system, observer_stats, target_stats):
        """Test awareness state persistence."""
        # Initial update
        system.update_awareness(
            "observer1", "target1",
            observer_stats, target_stats,
            distance=10.0, angle=0.0, current_time=100.0
        )
        
        # Get stored state
        state = system.get_awareness("observer1", "target1")
        assert state is not None
        assert state.zone == AwarenessZone.CLEAR
        
        # Clear awareness
        system.clear_awareness("observer1")
        assert system.get_awareness("observer1", "target1") is None

    def test_realistic_scenario(self, system):
        """Test a realistic combat scenario."""
        # Scenario: Two combatants moving and hiding
        
        # Initial positions (face to face)
        observer = {
            "perception": 5.0,
            "position_x": 0.0,
            "position_y": 0.0
        }
        
        target = {
            "stealth": 3.0,
            "position_x": 20.0,
            "position_y": 0.0,
            "movement": 0.0
        }
        
        # Initial awareness (clear view)
        state = system.update_awareness(
            "observer", "target",
            observer, target,
            distance=20.0, angle=0.0, current_time=0.0
        )
        assert state.zone == AwarenessZone.CLEAR
        
        # Target moves behind cover
        target["position_x"] = 40.0
        system.update_conditions(EnvironmentConditions(cover_density=0.8))
        
        state = system.update_awareness(
            "observer", "target",
            observer, target,
            distance=40.0, angle=0.0, current_time=1.0
        )
        assert state.zone in {AwarenessZone.FUZZY, AwarenessZone.PERIPHERAL}
        
        # Target starts sneaking
        target["stealth"] = 8.0
        target["movement"] = 0.2
        
        state = system.update_awareness(
            "observer", "target",
            observer, target,
            distance=40.0, angle=0.0, current_time=2.0
        )
        assert state.zone == AwarenessZone.HIDDEN
