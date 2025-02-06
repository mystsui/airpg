"""
Timing interfaces for the combat system.
"""

from dataclasses import dataclass
from typing import Dict, Optional, Protocol


@dataclass
class CombatTiming:
    """Timing information for combat actions."""
    base_time: float  # Base time in BTUs
    speed_modifier: float = 1.0  # Speed modifier (1.0 = normal speed)
    time_modifiers: Dict[str, float] = None  # Named time modifiers

    def __post_init__(self):
        if self.time_modifiers is None:
            self.time_modifiers = {}

    @property
    def total_time(self) -> float:
        """Calculate total time including all modifiers."""
        modified_time = self.base_time / self.speed_modifier
        for modifier in self.time_modifiers.values():
            modified_time *= modifier
        return modified_time


class ITimingManager(Protocol):
    """Interface for managing combat timing."""
    
    def get_action_timing(self, action_id: str) -> Optional[CombatTiming]:
        """Get timing information for an action."""
        ...

    def update_timing(self, action_id: str, timing: CombatTiming) -> None:
        """Update timing information for an action."""
        ...

    def add_modifier(self, action_id: str, modifier_name: str, value: float) -> None:
        """Add a named time modifier to an action."""
        ...

    def remove_modifier(self, action_id: str, modifier_name: str) -> None:
        """Remove a named time modifier from an action."""
        ...

    def clear_modifiers(self, action_id: str) -> None:
        """Clear all time modifiers for an action."""
        ...

    def get_remaining_time(self, action_id: str) -> Optional[float]:
        """Get remaining time for an action."""
        ...
