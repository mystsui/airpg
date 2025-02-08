from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from uuid import UUID, uuid4
from ..models.actions import Action
from ..models.state import CombatState

@dataclass
class CombatEventBase:
    event_type: str = field(init=False)
    id: UUID = field(default_factory=uuid4, init=False)
    data: Dict[str, Any] = field(default_factory=dict, init=False)

    def __post_init__(self):
        self.event_type = "combat.generic"

@dataclass
class CombatEvent(CombatEventBase):
    """Generic combat event."""
    def __post_init__(self):
        super().__post_init__()
        if not self.event_type:
            self.event_type = "combat.generic"

@dataclass
class StateChangeEvent(CombatEventBase):
    """Base class for events that involve state changes."""
    previous_state: CombatState
    current_state: CombatState

    def __post_init__(self):
        super().__post_init__()
        self.event_type = "combat.state_change"
        self.data.update({
            "round_number": self.current_state.round_number,
            "combatant_count": len(self.current_state.combatants),
            "active_effects_count": len(self.current_state.active_effects)
        })

@dataclass
class ActionEvent(StateChangeEvent):
    """Event generated when an action is executed."""
    action: Action
    actor_id: str
    result: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        super().__post_init__()
        self.event_type = "combat.action"
        self.data.update({
            "action": self.action,
            "actor_id": self.actor_id,
            "result": self.result
        })

@dataclass
class CombatStartEvent(CombatEventBase):
    """Event generated when combat starts."""
    combat_id: UUID
    participants: List[str]
    initial_state: CombatState

    def __post_init__(self):
        super().__post_init__()
        self.event_type = "combat.start"
        self.data.update({
            "combat_id": self.combat_id,
            "participants": self.participants
        })

@dataclass
class CombatEndEvent(CombatEventBase):
    """Event generated when combat ends."""
    combat_id: UUID
    final_state: CombatState
    winner_id: Optional[str] = None

    def __post_init__(self):
        super().__post_init__()
        self.event_type = "combat.end"
        self.data.update({
            "combat_id": self.combat_id,
            "winner_id": self.winner_id
        })

@dataclass
class CombatantEvent(CombatEventBase):
    """Event generated for combatant-specific occurrences."""
    combatant_id: str
    event_subtype: str
    state_before: Dict[str, Any]
    state_after: Dict[str, Any]
    
    def __post_init__(self):
        super().__post_init__()
        self.event_type = f"combat.combatant.{self.event_subtype}"
        self.data = {
            "combatant_id": self.combatant_id,
            "changes": {
                k: {"before": self.state_before.get(k), "after": self.state_after.get(k)}
                for k in set(self.state_before) | set(self.state_after)
            }
        }

def create_death_event(combatant_id: str, final_state: CombatState) -> CombatantEvent:
    """Create an event for combatant death."""
    return CombatantEvent(
        combatant_id=combatant_id,
        event_subtype="death",
        state_before={"alive": True},
        state_after={"alive": False}
    )

def create_status_effect_event(
    combatant_id: str,
    effect_name: str,
    added: bool
) -> CombatantEvent:
    """Create an event for status effect changes."""
    return CombatantEvent(
        combatant_id=combatant_id,
        event_subtype="status_effect",
        state_before={"effects": [] if added else [effect_name]},
        state_after={"effects": [effect_name] if added else []}
    )

# Expose base event class under the expected name
EventBase = CombatEventBase