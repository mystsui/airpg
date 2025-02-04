"""
Tests for the BTU (Base Time Unit) system.

These tests verify the functionality of time conversions,
speed modifications, and time modifiers.
"""

import pytest
from datetime import datetime
from combat.lib.timing import TimingSystem, TimeModifier
from tests.combat.mocks import MockTimingManager
from tests.combat.conftest import PerformanceStats

class TestTimeConversion:
    """Test suite for time conversion functionality."""
    """Test suite for time conversion functionality."""

    @pytest.fixture
    def timing_system(self):
        """Create a fresh timing system."""
        return TimingSystem()

    def test_ms_to_btu_conversion(self, timing_system):
        """Test millisecond to BTU conversion."""
        # Basic conversions
        assert timing_system.convert_to_btu(1000) == 1.0  # 1 second = 1 BTU
        assert timing_system.convert_to_btu(500) == 0.5   # 500ms = 0.5 BTU
        assert timing_system.convert_to_btu(2000) == 2.0  # 2 seconds = 2 BTU
        
        # Edge cases
        assert timing_system.convert_to_btu(0) == 0.0     # Zero case
        assert timing_system.convert_to_btu(1) == 0.001   # Minimum case
        assert timing_system.convert_to_btu(10000) == 10.0  # Large case

    def test_speed_modification(self, timing_system):
        """Test speed modifier application."""
        base_btu = 1.0  # 1 second worth of BTUs
        
        # Normal speed
        assert timing_system.apply_speed(base_btu, 1.0) == 1.0
        
        # Double speed
        assert timing_system.apply_speed(base_btu, 2.0) == 0.5
        
        # Half speed
        assert timing_system.apply_speed(base_btu, 0.5) == 2.0
        
        # Edge cases
        with pytest.raises(ValueError):
            timing_system.apply_speed(base_btu, 0.0)  # Zero speed
        with pytest.raises(ValueError):
            timing_system.apply_speed(base_btu, -1.0)  # Negative speed

class TestTimeModifiers:
    """Test suite for time modification system."""

    @pytest.fixture
    def timing_system(self):
        """Create a fresh timing system."""
        return TimingSystem()

    def test_modifier_registration(self, timing_system):
        """Test registering time modifiers."""
        # Register permanent modifier
        timing_system.register_modifier("haste", 1.5)
        assert timing_system.get_total_modifier() == 1.5
        
        # Register temporary modifier
        timing_system.register_modifier("speed_potion", 1.2, 1000)  # 1 second duration
        assert timing_system.get_total_modifier() == 1.8  # 1.5 * 1.2
        
        # Register debuff
        timing_system.register_modifier("slow", 0.5)
        assert timing_system.get_total_modifier() == 0.9  # 1.5 * 1.2 * 0.5

    def test_modifier_stacking(self, timing_system):
        """Test modifier stacking rules."""
        # Same type modifiers don't stack
        timing_system.register_modifier("haste_1", 1.5)
        timing_system.register_modifier("haste_2", 1.3)
        assert timing_system.get_total_modifier() == 1.5  # Takes highest
        
        # Different type modifiers multiply
        timing_system.register_modifier("speed_potion", 1.2)
        assert timing_system.get_total_modifier() == 1.8  # 1.5 * 1.2
        
        # Debuffs stack with buffs
        timing_system.register_modifier("slow", 0.8)
        assert timing_system.get_total_modifier() == 1.44  # 1.5 * 1.2 * 0.8

    def test_temporary_modifiers(self, timing_system):
        """Test temporary modifier duration."""
        # Add temporary modifier
        timing_system.register_modifier("speed_potion", 1.5, 1000)  # 1 second
        assert timing_system.get_total_modifier() == 1.5
        
        # Update time
        timing_system.update(500)  # 500ms elapsed
        assert timing_system.get_total_modifier() == 1.5
        
        # Expire modifier
        timing_system.update(500)  # Another 500ms
        assert timing_system.get_total_modifier() == 1.0

class TestIntegration:
    """Integration tests for timing system."""

    @pytest.fixture
    def timing_system(self):
        """Create a fresh timing system."""
        return TimingSystem()

    def test_complete_timing_flow(self, timing_system):
        """Test complete timing system flow."""
        # Initial conversion
        base_time = timing_system.convert_to_btu(1000)  # 1 second
        assert base_time == 1.0
        
        # Apply speed
        timing_system.register_modifier("haste", 1.5)
        modified_time = timing_system.apply_speed(base_time, 1.0)
        assert modified_time == 0.667  # Approximately 1.0 / 1.5
        
        # Add temporary buff
        timing_system.register_modifier("speed_potion", 1.2, 2000)
        modified_time = timing_system.apply_speed(base_time, 1.0)
        assert modified_time == 0.556  # Approximately 1.0 / (1.5 * 1.2)
        
        # Time passes
        timing_system.update(2000)  # Speed potion expires
        modified_time = timing_system.apply_speed(base_time, 1.0)
        assert modified_time == 0.667  # Back to just haste

    def test_performance(self, timing_system, performance_stats):
        """Test timing system performance."""
        # Measure conversion performance
        start_time = datetime.now()
        for _ in range(1000):
            timing_system.convert_to_btu(1000)
        conversion_time = (datetime.now() - start_time).total_seconds()
        performance_stats.record_operation("btu_conversion", conversion_time)
        
        # Measure modifier performance
        start_time = datetime.now()
        for i in range(100):
            timing_system.register_modifier(f"mod_{i}", 1.1, 1000)
            timing_system.update(10)
        modifier_time = (datetime.now() - start_time).total_seconds()
        performance_stats.record_operation("modifier_update", modifier_time)
        
        # Verify performance
        assert conversion_time < 0.1  # Should be very fast
        assert modifier_time < 0.1  # Should handle many modifiers efficiently

    def test_edge_cases(self, timing_system):
        """Test edge cases and boundary conditions."""
        # Very large time values
        large_time = timing_system.convert_to_btu(1_000_000_000)  # 1000 seconds
        assert large_time == 1000.0
        
        # Very small time values
        small_time = timing_system.convert_to_btu(1)  # 1 millisecond
        assert small_time == 0.001
        
        # Fractional speed values
        assert timing_system.apply_speed(1.0, 0.1) == 10.0  # Very slow
        assert timing_system.apply_speed(1.0, 10.0) == 0.1  # Very fast
        
        # Multiple stacked modifiers
        timing_system.register_modifier("buff1", 2.0)
        timing_system.register_modifier("buff2", 3.0)
        timing_system.register_modifier("debuff1", 0.5)
        timing_system.register_modifier("debuff2", 0.25)
        
        total_mod = timing_system.get_total_modifier()
        assert 0.1 <= total_mod <= 10.0  # Should be within reasonable bounds
