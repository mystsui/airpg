"""
Base Time Unit (BTU) System

This module provides the core timing utilities for the combat system,
including time conversions, speed modifications, and time modifiers.
"""

from dataclasses import dataclass
from typing import Dict, Optional
from datetime import datetime

@dataclass
class TimeModifier:
    """Represents a time modification effect."""
    value: float  # Multiplier value
    duration: Optional[int] = None  # Duration in milliseconds
    start_time: Optional[datetime] = None  # When the modifier was applied
    category: str = "general"  # Category for stacking rules

class TimingSystem:
    """Manages combat timing and time modifications."""
    
    def __init__(self):
        """Initialize the timing system."""
        self._modifiers: Dict[str, TimeModifier] = {}
        self._last_update = datetime.now()
        
    def convert_to_btu(self, ms: int) -> float:
        """
        Convert milliseconds to Base Time Units.
        
        Args:
            ms: Time in milliseconds
            
        Returns:
            Time in BTUs (1 BTU = 1 second)
        """
        return float(ms) / 1000.0
        
    def apply_speed(self, btu: float, speed: float) -> float:
        """
        Apply speed modifier to BTU time.
        
        Args:
            btu: Time in BTUs
            speed: Speed modifier (1.0 = normal speed)
            
        Returns:
            Modified time in BTUs
            
        Raises:
            ValueError: If speed is zero or negative
        """
        if speed <= 0:
            raise ValueError("Speed must be positive")
            
        return btu / speed
        
    def register_modifier(self,
                        source: str,
                        value: float,
                        duration: Optional[int] = None,
                        category: str = "general") -> None:
        """
        Register a time modifier.
        
        Args:
            source: Identifier for the modifier source
            value: Modifier multiplier value
            duration: Optional duration in milliseconds
            category: Modifier category for stacking rules
        """
        self._modifiers[source] = TimeModifier(
            value=value,
            duration=duration,
            start_time=datetime.now() if duration else None,
            category=category
        )
        
    def update(self, elapsed_ms: int) -> None:
        """
        Update time modifiers.
        
        Args:
            elapsed_ms: Elapsed time in milliseconds
        """
        current_time = datetime.now()
        
        # Remove expired modifiers
        expired = []
        for source, modifier in self._modifiers.items():
            if modifier.duration and modifier.start_time:
                elapsed = (current_time - modifier.start_time).total_seconds() * 1000
                if elapsed >= modifier.duration:
                    expired.append(source)
                    
        for source in expired:
            del self._modifiers[source]
            
        self._last_update = current_time
        
    def get_total_modifier(self) -> float:
        """
        Calculate total time modification.
        
        Returns:
            Combined modifier value
        """
        if not self._modifiers:
            return 1.0
            
        # Group modifiers by category
        categories: Dict[str, list[float]] = {}
        for modifier in self._modifiers.values():
            if modifier.category not in categories:
                categories[modifier.category] = []
            categories[modifier.category].append(modifier.value)
            
        # Apply stacking rules
        total = 1.0
        for category_values in categories.values():
            if len(category_values) == 1:
                total *= category_values[0]
            else:
                # Same category: take highest value
                total *= max(category_values)
                
        return total
        
    def get_modifier(self, source: str) -> Optional[TimeModifier]:
        """
        Get a specific modifier.
        
        Args:
            source: Modifier source identifier
            
        Returns:
            The modifier if found, None otherwise
        """
        return self._modifiers.get(source)
        
    def remove_modifier(self, source: str) -> None:
        """
        Remove a specific modifier.
        
        Args:
            source: Modifier source identifier
        """
        if source in self._modifiers:
            del self._modifiers[source]
            
    def clear_modifiers(self) -> None:
        """Remove all modifiers."""
        self._modifiers.clear()
        
    @property
    def active_modifiers(self) -> Dict[str, TimeModifier]:
        """Get all active modifiers."""
        return self._modifiers.copy()
