from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from uuid import UUID, uuid4
from ..models.state import CombatState
from ..models.actions import Action

@dataclass
class CombatEvent:
    """Base class for all combat events."""
    event_type: str
    id: UUID = field(default_factory=uuid4)
    data: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CombatStartEvent:
    """Event generated when combat starts."""
    combat_id: UUID
    participants: List[str]
    initial_state: CombatState
    id: UUID = field(default_factory=uuid4)
    event_type: str = field(default="combat.start", init=False)
    data: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.data.update({
            "combat_id": self.combat_id,
            "participants": self.participants,
            "initial_state": self.initial_state
        })

@dataclass
class CombatEndEvent:
    """Event generated when combat ends."""
    combat_id: UUID
    final_state: CombatState
    id: UUID = field(default_factory=uuid4)
    event_type: str = field(default="combat.end", init=False)
    data: Dict[str, Any] = field(default_factory=dict)
    winner_id: Optional[str] = None

    def __post_init__(self):
        self.data.update({
            "combat_id": self.combat_id,
            "final_state": self.final_state,
            "winner_id": self.winner_id
        })

@dataclass
class ActionEvent:
    """Event generated when an action is executed."""
    action: Action
    actor_id: str
    previous_state: CombatState
    current_state: CombatState
    id: UUID = field(default_factory=uuid4)
    event_type: str = field(default="combat.action", init=False)
    result: Dict[str, Any] = field(default_factory=dict)
    data: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.data.update({
            "action": self.action,
            "actor_id": self.actor_id,
            "pre_state": self.previous_state,
            "post_state": self.current_state,
            "result": self.result
        })

@dataclass
class StateChangeEvent:
    """Event generated when combat state changes."""
    previous_state: CombatState
    current_state: CombatState
    id: UUID = field(default_factory=uuid4)
    event_type: str = field(default="combat.state.change", init=False)
    data: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.data.update({
            "previous_state": self.previous_state,
            "current_state": self.current_state,
            "round_number": self.current_state.round_number,
            "changes": self._calculate_changes()
        })

    def _calculate_changes(self) -> Dict[str, Any]:
        """Calculate state changes between previous and current state."""
        changes = {}
        for cid, current in self.current_state.combatants.items():
            if cid in self.previous_state.combatants:
                prev = self.previous_state.combatants[cid]
                changes[cid] = {
                    "health_delta": current.health - prev.health,
                    "stamina_delta": current.stamina - prev.stamina,
                    "position_delta": current.position - prev.position,
                    "effects_added": [e for e in current.status_effects 
                                    if e not in prev.status_effects],
                    "effects_removed": [e for e in prev.status_effects 
                                      if e not in current.status_effects]
                }
        return changes

@dataclass
class RoundEvent:
    """Event generated for round processing."""
    round_number: int
    state: CombatState
    id: UUID = field(default_factory=uuid4)
    event_type: str = field(default="combat.round", init=False)
    data: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.data.update({
            "round_number": self.round_number,
            "state": self.state,
            "combatants": list(self.state.combatants.keys())
        })

# Alias for backwards compatibility
EventBase = CombatEvent