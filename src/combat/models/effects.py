from dataclasses import dataclass

@dataclass
class StatusEffect:
    """Represents a status effect that can be applied to a combatant."""
    id: str
    name: str
    duration: int
    strength: float
    
    def clone(self) -> 'StatusEffect':
        """Creates a deep copy of the current status effect."""
        return StatusEffect(
            id=self.id,
            name=self.name,
            duration=self.duration,
            strength=self.strength
        )