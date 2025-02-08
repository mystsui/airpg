from dataclasses import dataclass, field
from typing import List
from .effects import StatusEffect

@dataclass
class CombatantState:
    """Represents the current state of a combatant."""
    id: str
    health: int
    max_health: int
    stamina: int
    max_stamina: int
    position: float = 0.0
    status_effects: List[StatusEffect] = field(default_factory=list)
    
    def clone(self) -> 'CombatantState':
        """Creates a deep copy of the current combatant state."""
        return CombatantState(
            id=self.id,
            health=self.health,
            max_health=self.max_health,
            stamina=self.stamina,
            max_stamina=self.max_stamina,
            position=self.position,
            status_effects=[effect.clone() for effect in self.status_effects]
        )