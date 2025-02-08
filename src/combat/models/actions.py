from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, Optional, Any
from uuid import UUID, uuid4
from .combatant import CombatantState

class ActionType(Enum):
    """Types of actions that can be performed in combat."""
    ATTACK = auto()
    DEFEND = auto()
    SKILL = auto()
    ITEM = auto()
    MOVE = auto()

    # Priority levels
    LOW = 0
    NORMAL = 1
    HIGH = 2

@dataclass
class ActionRequirements:
    """Requirements for executing an action."""
    min_stamina: int = 0
    min_health: int = 0
    target_required: bool = False
    weapon_required: bool = False
    min_distance: float = 0.0
    max_distance: float = float('inf')

@dataclass
class ActionCosts:
    """Costs associated with executing an action."""
    stamina: int = 0
    health: int = 0

@dataclass
class Action:
    """Represents a combat action."""
    type: ActionType
    name: str
    parameters: Dict[str, Any]
    target_id: Optional[str] = None
    id: UUID = field(default_factory=uuid4)
    priority: ActionType = ActionType.NORMAL
    requirements: ActionRequirements = field(default_factory=ActionRequirements)
    costs: ActionCosts = field(default_factory=ActionCosts)

    def validate(self, actor_state: CombatantState, target_state: Optional[CombatantState] = None) -> bool:
        """Validates if the action can be performed."""
        if actor_state.stamina < self.requirements.min_stamina:
            return False
        if actor_state.health < self.requirements.min_health:
            return False
        if self.requirements.target_required and not target_state:
            return False
        if target_state and self.target_id:
            distance = abs(actor_state.position - target_state.position)
            if not (self.requirements.min_distance <= distance <= self.requirements.max_distance):
                return False
        return True

@dataclass
class ActionResult:
    """Result of an action execution."""
    action_id: UUID
    success: bool
    effects: Dict[str, Any] = field(default_factory=dict)
    messages: list[str] = field(default_factory=list)