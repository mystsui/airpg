"""
Test Configuration and Fixtures

This module provides shared fixtures and utilities for combat system tests.
"""

import pytest
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from combat.interfaces.combatant import ICombatant, CombatantState as ICombatantState
from datetime import datetime
from combat.lib.action_system import (
    ActionStateType,
    ActionVisibility,
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

class TestCombatant(ICombatant):
    """Test combatant implementation."""
    def __init__(
        self,
        id: str,
        stamina: float = 100.0,
        speed: float = 1.0,
        stealth: float = 1.0,
        position_x: float = 0.0,
        position_y: float = 0.0,
        stats: Dict[str, Any] = None
    ):
        self._id = id
        self._stamina = stamina
        self._speed = speed
        self._stealth = stealth
        self._position_x = position_x
        self._position_y = position_y
        self._stats = stats or {}

    @property
    def id(self) -> str:
        """Get combatant ID."""
        return self._id

    def get_state(self) -> ICombatantState:
        """Get current combatant state."""
        return ICombatantState(
            entity_id=self._id,
            stamina=self._stamina,
            speed=self._speed,
            stealth=self._stealth,
            position_x=self._position_x,
            position_y=self._position_y,
            stats=self._stats.copy()
        )

    def update_state(self, state: ICombatantState) -> None:
        """Update combatant state."""
        self._stamina = state.stamina
        self._speed = state.speed
        self._stealth = state.stealth
        self._position_x = state.position_x
        self._position_y = state.position_y
        self._stats = state.stats.copy()

    def get_stat(self, stat_name: str) -> Optional[Any]:
        """Get a specific stat value."""
        return self._stats.get(stat_name)

    def set_stat(self, stat_name: str, value: Any) -> None:
        """Set a specific stat value."""
        self._stats[stat_name] = value

    def get_position(self) -> tuple[float, float]:
        """Get current position."""
        return (self._position_x, self._position_y)

    def set_position(self, x: float, y: float) -> None:
        """Set current position."""
        self._position_x = x
        self._position_y = y

    def get_stamina(self) -> float:
        """Get current stamina."""
        return self._stamina

    def set_stamina(self, value: float) -> None:
        """Set current stamina."""
        self._stamina = value

    def get_speed(self) -> float:
        """Get current speed."""
        return self._speed

    def set_speed(self, value: float) -> None:
        """Set current speed."""
        self._speed = value

    def get_stealth(self) -> float:
        """Get current stealth."""
        return self._stealth

    def set_stealth(self, value: float) -> None:
        """Set current stealth."""
        self._stealth = value

    def is_defeated(self) -> bool:
        """Check if combatant is defeated."""
        return self._stamina <= 0

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
            },
            # Feint
            {
                "type": "quick_attack",
                "source": attacker_id,
                "target": defender_id,
                "visibility": ActionVisibility.HIDDEN,
            },
            # Block
            {
                "type": "block",
                "source": defender_id,
                "target": None,
                "visibility": ActionVisibility.TELEGRAPHED,
            },
            # Counter
            {
                "type": "parry",
                "source": defender_id,
                "target": attacker_id,
                "visibility": ActionVisibility.TELEGRAPHED,
            },
            # Retreat
            {
                "type": "move_backward",
                "source": defender_id,
                "target": None,
                "visibility": ActionVisibility.TELEGRAPHED,
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
