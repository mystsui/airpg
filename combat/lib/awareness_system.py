"""
Combat Awareness System

This module implements awareness zones and perception mechanics
for the combat system.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, Optional, Tuple, Any
from math import sqrt, cos, radians

class AwarenessZone(Enum):
    """Zones of awareness around a combatant."""
    CLEAR = auto()      # Full awareness
    FUZZY = auto()      # Partial awareness
    HIDDEN = auto()     # No awareness
    PERIPHERAL = auto() # Edge of awareness

class PerceptionModifier(Enum):
    """Factors affecting perception."""
    DISTANCE = "distance"          # Distance between combatants
    ANGLE = "angle"               # Viewing angle
    LIGHTING = "lighting"         # Environmental lighting
    COVER = "cover"               # Physical obstacles
    MOVEMENT = "movement"         # Target movement
    STEALTH = "stealth"          # Target stealth rating
    DISTRACTION = "distraction"   # Environmental distractions

@dataclass
class EnvironmentConditions:
    """Environmental conditions affecting awareness."""
    lighting_level: float = 1.0  # 0.0 (dark) to 1.0 (bright)
    cover_density: float = 0.0   # 0.0 (open) to 1.0 (dense)
    distraction_level: float = 0.0  # 0.0 (calm) to 1.0 (chaotic)
    visibility_range: float = 100.0  # Maximum visibility distance

@dataclass
class AwarenessState:
    """Current awareness state of a combatant."""
    zone: AwarenessZone
    confidence: float  # 0.0 to 1.0
    last_clear_position: Optional[Tuple[float, float]] = None
    last_update_time: float = 0.0
    modifiers: Dict[PerceptionModifier, float] = field(default_factory=dict)

class PerceptionCheck:
    """Handles perception checks and calculations."""
    
    BASE_PERCEPTION_RANGE = 50.0  # Base range for clear perception
    FUZZY_RANGE_MULTIPLIER = 1.5  # Multiplier for fuzzy perception range
    PERIPHERAL_RANGE_MULTIPLIER = 2.0  # Multiplier for peripheral range
    
    @staticmethod
    def calculate_base_difficulty(distance: float, base_range: float) -> float:
        """
        Calculate base difficulty based on distance.
        
        Args:
            distance: Distance to target
            base_range: Base perception range
            
        Returns:
            Base difficulty value
        """
        if distance <= base_range:
            return 0.0  # No penalty within base range
        elif distance <= base_range * PerceptionCheck.FUZZY_RANGE_MULTIPLIER:
            return (distance - base_range) / base_range  # Linear scaling
        else:
            return 1.0  # Maximum difficulty beyond fuzzy range

    @staticmethod
    def apply_angle_modifier(angle: float) -> float:
        """
        Calculate modifier based on viewing angle.
        
        Args:
            angle: Angle in degrees (0 is direct view)
            
        Returns:
            Angle modifier value
        """
        if angle <= 45:
            return 0.0  # No penalty for front view
        elif angle <= 90:
            return (angle - 45) / 45  # Linear scaling to side view
        elif angle <= 135:
            return 1.0 + (angle - 90) / 45  # Increased penalty for rear quarter
        else:
            return 2.0  # Maximum penalty for rear view

    @staticmethod
    def calculate_confidence(
        perception: float,
        stealth: float,
        distance: float,
        angle: float,
        conditions: EnvironmentConditions
    ) -> float:
        """
        Calculate confidence in target detection.
        
        Args:
            perception: Observer's perception stat
            stealth: Target's stealth stat
            distance: Distance to target
            angle: Viewing angle
            conditions: Environmental conditions
            
        Returns:
            Confidence value (0.0 to 1.0)
        """
        # Base detection chance
        base_confidence = max(0.0, min(1.0, perception / (stealth + 1.0)))
        
        # Apply distance modifier
        distance_mod = PerceptionCheck.calculate_base_difficulty(
            distance, 
            PerceptionCheck.BASE_PERCEPTION_RANGE
        )
        
        # Apply angle modifier
        angle_mod = PerceptionCheck.apply_angle_modifier(angle)
        
        # Apply environmental modifiers
        env_mod = (
            (1.0 - conditions.cover_density) *
            conditions.lighting_level *
            (1.0 - conditions.distraction_level)
        )
        
        # Calculate final confidence
        confidence = base_confidence * (
            1.0 - distance_mod * 0.5 -  # Distance has 50% impact
            angle_mod * 0.3 -           # Angle has 30% impact
            (1.0 - env_mod) * 0.2       # Environment has 20% impact
        )
        
        return max(0.0, min(1.0, confidence))

class AwarenessSystem:
    """Manages awareness states and updates."""
    
    def __init__(self, conditions: Optional[EnvironmentConditions] = None):
        """
        Initialize the awareness system.
        
        Args:
            conditions: Environmental conditions
        """
        self._conditions = conditions or EnvironmentConditions()
        self._awareness_states: Dict[str, Dict[str, AwarenessState]] = {}
        
    def register_combatant(self, combatant_id: str) -> None:
        """
        Register a new combatant.
        
        Args:
            combatant_id: Unique combatant identifier
        """
        if combatant_id not in self._awareness_states:
            self._awareness_states[combatant_id] = {}
            
    def update_awareness(self,
                        observer_id: str,
                        target_id: str,
                        observer_stats: dict,
                        target_stats: dict,
                        distance: float,
                        angle: float,
                        current_time: float) -> AwarenessState:
        """
        Update awareness state between combatants.
        
        Args:
            observer_id: Observer's identifier
            target_id: Target's identifier
            observer_stats: Observer's current stats
            target_stats: Target's current stats
            distance: Distance between combatants
            angle: Viewing angle
            current_time: Current time in BTUs
            
        Returns:
            Updated awareness state
        """
        if observer_id not in self._awareness_states:
            self.register_combatant(observer_id)
            
        if target_id not in self._awareness_states[observer_id]:
            self._awareness_states[observer_id][target_id] = AwarenessState(
                zone=AwarenessZone.HIDDEN,
                confidence=0.0
            )
            
        state = self._awareness_states[observer_id][target_id]
        
        # Calculate new confidence
        confidence = PerceptionCheck.calculate_confidence(
            observer_stats.get("perception", 1.0),
            target_stats.get("stealth", 1.0),
            distance,
            angle,
            self._conditions
        )
        
        # Update modifiers
        state.modifiers = {
            PerceptionModifier.DISTANCE: distance / self._conditions.visibility_range,
            PerceptionModifier.ANGLE: angle / 180.0,
            PerceptionModifier.LIGHTING: self._conditions.lighting_level,
            PerceptionModifier.COVER: self._conditions.cover_density,
            PerceptionModifier.MOVEMENT: target_stats.get("movement", 0.0),
            PerceptionModifier.STEALTH: target_stats.get("stealth", 1.0),
            PerceptionModifier.DISTRACTION: self._conditions.distraction_level
        }
        
        # Determine awareness zone
        if confidence >= 0.8:
            state.zone = AwarenessZone.CLEAR
            state.last_clear_position = (
                target_stats.get("position_x", 0.0),
                target_stats.get("position_y", 0.0)
            )
        elif confidence >= 0.5:
            state.zone = AwarenessZone.FUZZY
        elif confidence >= 0.2:
            state.zone = AwarenessZone.PERIPHERAL
        else:
            state.zone = AwarenessZone.HIDDEN
            
        state.confidence = confidence
        state.last_update_time = current_time
        
        return state
        
    def get_awareness(self,
                     observer_id: str,
                     target_id: str) -> Optional[AwarenessState]:
        """
        Get current awareness state.
        
        Args:
            observer_id: Observer's identifier
            target_id: Target's identifier
            
        Returns:
            Current awareness state or None if not found
        """
        return (
            self._awareness_states.get(observer_id, {}).get(target_id)
        )
        
    def clear_awareness(self, combatant_id: str) -> None:
        """
        Clear all awareness states for a combatant.
        
        Args:
            combatant_id: Combatant identifier
        """
        # Clear as observer
        if combatant_id in self._awareness_states:
            del self._awareness_states[combatant_id]
            
        # Clear as target
        for observer_states in self._awareness_states.values():
            if combatant_id in observer_states:
                del observer_states[combatant_id]
                
    def update_conditions(self, conditions: EnvironmentConditions) -> None:
        """
        Update environmental conditions.
        
        Args:
            conditions: New environmental conditions
        """
        self._conditions = conditions
