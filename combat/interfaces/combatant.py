"""
Combatant interfaces for the combat system.
"""

from dataclasses import dataclass
from typing import Dict, Optional, Protocol, Any, runtime_checkable


@dataclass
class CombatantState:
    """State information for a combatant."""
    entity_id: str
    stamina: float
    speed: float
    stealth: float
    position_x: float
    position_y: float
    stats: Dict[str, Any]


@runtime_checkable
class ICombatant(Protocol):
    """Interface for combatant entities."""
    
    @property
    def id(self) -> str:
        """Get combatant ID."""
        ...

    def get_state(self) -> CombatantState:
        """Get current combatant state."""
        ...

    def update_state(self, state: CombatantState) -> None:
        """Update combatant state."""
        ...

    def get_stat(self, stat_name: str) -> Optional[Any]:
        """Get a specific stat value."""
        ...

    def set_stat(self, stat_name: str, value: Any) -> None:
        """Set a specific stat value."""
        ...

    def get_position(self) -> tuple[float, float]:
        """Get current position."""
        ...

    def set_position(self, x: float, y: float) -> None:
        """Set current position."""
        ...

    def get_stamina(self) -> float:
        """Get current stamina."""
        ...

    def set_stamina(self, value: float) -> None:
        """Set current stamina."""
        ...

    def get_speed(self) -> float:
        """Get current speed."""
        ...

    def set_speed(self, value: float) -> None:
        """Set current speed."""
        ...

    def get_stealth(self) -> float:
        """Get current stealth."""
        ...

    def set_stealth(self, value: float) -> None:
        """Set current stealth."""
        ...
