from dataclasses import dataclass, field
from typing import Dict, List
from uuid import UUID, uuid4
from datetime import datetime
from .combatant import CombatantState
from .effects import StatusEffect

@dataclass
class CombatState:
    """Represents the current state of combat."""
    id: UUID = field(default_factory=uuid4)
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())
    combatants: Dict[str, CombatantState] = field(default_factory=dict)
    active_effects: List[StatusEffect] = field(default_factory=list)
    round_number: int = 0
    
    def clone(self) -> 'CombatState':
        """Creates a deep copy of the current combat state."""
        return CombatState(
            id=self.id,
            timestamp=self.timestamp,
            combatants={k: v.clone() for k, v in self.combatants.items()},
            active_effects=[effect.clone() for effect in self.active_effects],
            round_number=self.round_number
        )