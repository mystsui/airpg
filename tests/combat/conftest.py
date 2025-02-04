"""
Test Configuration and Fixtures

This module provides shared fixtures and utilities for combat system tests.
"""

import pytest
from dataclasses import dataclass, field
from typing import Dict, Any
from datetime import datetime
from combat.lib.action_system import (
    ActionStateType,
    ActionVisibility,
    ActionCommitment,
    ActionPhase
)

@dataclass
class PerformanceStats:
    """Track performance statistics."""
    operations: Dict[str, float] = field(default_factory=dict)
    
    def record_operation(self, name: str, duration: float) -> None:
        """Record operation duration."""
        if name not in self.operations:
            self.operations[name] = []
        self.operations[name].append(duration)
        
    def get_average(self, name: str) -> float:
        """Get average duration for operation."""
        if name not in self.operations:
            return 0.0
        return sum(self.operations[name]) / len(self.operations[name])
        
    def get_max(self, name: str) -> float:
        """Get maximum duration for operation."""
        if name not in self.operations:
            return 0.0
        return max(self.operations[name])
        
    def get_min(self, name: str) -> float:
        """Get minimum duration for operation."""
        if name not in self.operations:
            return 0.0
        return min(self.operations[name])

@dataclass
class TestCombatant:
    """Test combatant implementation."""
    id: str
    stamina: float = 100.0
    speed: float = 1.0
    stealth: float = 1.0
    position_x: float = 0.0
    position_y: float = 0.0
    stats: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CombatantState:
    """Test combatant state."""
    entity_id: str
    stamina: float
    speed: float
    stealth: float
    position_x: float
    position_y: float
    stats: Dict[str, Any] = field(default_factory=dict)

@pytest.fixture
def performance_stats():
    """Provide performance tracking."""
    return PerformanceStats()

def create_test_combatant(
    entity_id: str,
    stamina: float = 100.0,
    speed: float = 1.0,
    stealth: float = 1.0,
    position_x: float = 0.0,
    position_y: float = 0.0,
    **stats
) -> TestCombatant:
    """Create a test combatant."""
    return TestCombatant(
        id=entity_id,
        stamina=stamina,
        speed=speed,
        stealth=stealth,
        position_x=position_x,
        position_y=position_y,
        stats=stats
    )

def create_test_combatant_state(
    entity_id: str,
    stamina: float = 100.0,
    speed: float = 1.0,
    stealth: float = 1.0,
    position_x: float = 0.0,
    position_y: float = 0.0,
    **stats
) -> CombatantState:
    """Create a test combatant state."""
    return CombatantState(
        entity_id=entity_id,
        stamina=stamina,
        speed=speed,
        stealth=stealth,
        position_x=position_x,
        position_y=position_y,
        stats=stats
    )

@pytest.fixture
def test_sequence():
    """Provide a test combat sequence."""
    def create_sequence(attacker_id: str, defender_id: str):
        """Create a test sequence."""
        return [
            # Approach
            {
                "type": "move_forward",
                "source": attacker_id,
                "target": None,
                "visibility": ActionVisibility.HIDDEN,
                "commitment": ActionCommitment.NONE
            },
            # Feint
            {
                "type": "quick_attack",
                "source": attacker_id,
                "target": defender_id,
                "visibility": ActionVisibility.HIDDEN,
                "commitment": ActionCommitment.NONE
            },
            # Block
            {
                "type": "block",
                "source": defender_id,
                "target": None,
                "visibility": ActionVisibility.TELEGRAPHED,
                "commitment": ActionCommitment.PARTIAL
            },
            # Counter
            {
                "type": "parry",
                "source": defender_id,
                "target": attacker_id,
                "visibility": ActionVisibility.TELEGRAPHED,
                "commitment": ActionCommitment.PARTIAL
            },
            # Retreat
            {
                "type": "move_backward",
                "source": defender_id,
                "target": None,
                "visibility": ActionVisibility.TELEGRAPHED,
                "commitment": ActionCommitment.NONE
            }
        ]
    return create_sequence

@pytest.fixture
def mock_event_handler():
    """Provide a mock event handler."""
    class MockEventHandler:
        def __init__(self):
            self.events = []
            
        def handle_event(self, event):
            self.events.append(event)
            
        def clear(self):
            self.events.clear()
            
        def get_events(self):
            return self.events
            
    return MockEventHandler()

@pytest.fixture
def mock_state_observer():
    """Provide a mock state observer."""
    class MockStateObserver:
        def __init__(self):
            self.states = []
            
        def observe_state(self, state):
            self.states.append(state)
            
        def clear(self):
            self.states.clear()
            
        def get_states(self):
            return self.states
            
    return MockStateObserver()

@pytest.fixture
def test_environment():
    """Provide test environment conditions."""
    def create_environment(
        lighting: float = 1.0,
        cover: float = 0.0,
        distraction: float = 0.0
    ):
        """Create test environment conditions."""
        from combat.lib.awareness_system import EnvironmentConditions
        return EnvironmentConditions(
            lighting_level=lighting,
            cover_density=cover,
            distraction_level=distraction
        )
    return create_environment
