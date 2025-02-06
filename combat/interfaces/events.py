"""
Event interfaces for the combat system.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, Optional


class EventCategory(Enum):
    """Categories of combat events."""
    COMBAT = auto()    # Direct combat actions
    MOVEMENT = auto()  # Position changes
    STATE = auto()     # State changes
    ANIMATION = auto() # Visual effects
    AI = auto()        # AI decision making
    META = auto()      # System events
    DEBUG = auto()     # Debug information


class EventImportance(Enum):
    """Importance levels for events."""
    CRITICAL = auto()  # Must be processed
    MAJOR = auto()     # Important events
    MINOR = auto()     # Optional events
    DEBUG = auto()     # Debug information


@dataclass
class CombatEvent:
    """Base event class for combat system."""
    event_id: str
    event_type: str
    category: EventCategory
    importance: EventImportance
    timestamp: datetime
    source_id: str
    target_id: Optional[str]
    data: Dict[str, Any]


@dataclass
class Action:
    """Action definition."""
    action_type: str
    stamina_cost: float
    time_cost: float
    speed_requirement: float
    description: str
    properties: Dict[str, Any]


@dataclass
class ActionResult:
    """Result of an action execution."""
    success: bool
    damage: float
    stamina_cost: float
    effects: Dict[str, Any]
