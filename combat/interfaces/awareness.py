"""
Awareness system interfaces for the combat system.
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, Optional, Protocol, Any


class AwarenessZone(Enum):
    """Zones of awareness."""
    CLEAR = auto()      # Full awareness
    FUZZY = auto()      # Partial awareness
    HIDDEN = auto()     # No awareness
    PERIPHERAL = auto() # Edge of awareness


@dataclass
class EnvironmentConditions:
    """Environmental conditions affecting awareness."""
    lighting_level: float    # 0.0 to 1.0
    cover_density: float     # 0.0 to 1.0
    distraction_level: float # 0.0 to 1.0


@dataclass
class AwarenessState:
    """Current awareness state between two entities."""
    observer_id: str
    target_id: str
    confidence: float        # 0.0 to 1.0
    zone: AwarenessZone
    last_update_time: float
    conditions: Optional[EnvironmentConditions] = None


class IAwarenessManager(Protocol):
    """Interface for managing awareness between entities."""
    
    def update_awareness(self,
                        observer_id: str,
                        target_id: str,
                        observer_stats: Dict[str, Any],
                        target_stats: Dict[str, Any],
                        distance: float,
                        angle: float,
                        current_time: float) -> AwarenessState:
        """
        Update awareness between entities.
        
        Args:
            observer_id: Observer entity ID
            target_id: Target entity ID
            observer_stats: Observer's stats
            target_stats: Target's stats
            distance: Distance between entities
            angle: Angle between entities
            current_time: Current time
            
        Returns:
            Updated awareness state
        """
        ...

    def get_awareness(self,
                     observer_id: str,
                     target_id: str) -> Optional[AwarenessState]:
        """
        Get current awareness state.
        
        Args:
            observer_id: Observer entity ID
            target_id: Target entity ID
            
        Returns:
            Current awareness state or None
        """
        ...

    def update_conditions(self, conditions: EnvironmentConditions) -> None:
        """
        Update environmental conditions.
        
        Args:
            conditions: New conditions
        """
        ...

    def calculate_visibility(self,
                           distance: float,
                           angle: float,
                           stealth: float,
                           perception: float,
                           conditions: Optional[EnvironmentConditions] = None) -> float:
        """
        Calculate visibility level.
        
        Args:
            distance: Distance between entities
            angle: Angle between entities
            stealth: Target's stealth stat
            perception: Observer's perception stat
            conditions: Optional environmental conditions
            
        Returns:
            Visibility level (0.0 to 1.0)
        """
        ...
