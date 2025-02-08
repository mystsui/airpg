from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional

class StatType(Enum):
    """Base statistic types."""
    STRENGTH = "strength"
    DEXTERITY = "dexterity"
    CONSTITUTION = "constitution"
    INTELLIGENCE = "intelligence"
    WISDOM = "wisdom"
    CHARISMA = "charisma"

@dataclass
class StatModifier:
    """Represents a modification to a stat."""
    value: int
    source: str
    duration: Optional[int] = None  # None means permanent
    is_percentage: bool = False

@dataclass
class Stats:
    """
    Comprehensive character statistics system.
    Handles base stats, modifiers, and derived attributes.
    """
    base_stats: Dict[StatType, int] = field(default_factory=lambda: {
        stat_type: 10 for stat_type in StatType
    })
    
    modifiers: Dict[StatType, list[StatModifier]] = field(
        default_factory=lambda: {stat_type: [] for stat_type in StatType}
    )

    def get_base_stat(self, stat_type: StatType) -> int:
        """Get the base value of a stat."""
        return self.base_stats.get(stat_type, 0)

    def set_base_stat(self, stat_type: StatType, value: int) -> None:
        """Set the base value of a stat."""
        self.base_stats[stat_type] = max(1, min(value, 100))

    def add_modifier(self, stat_type: StatType, modifier: StatModifier) -> None:
        """Add a modifier to a stat."""
        self.modifiers[stat_type].append(modifier)

    def remove_modifier(self, stat_type: StatType, source: str) -> None:
        """Remove all modifiers from a specific source."""
        self.modifiers[stat_type] = [
            mod for mod in self.modifiers[stat_type]
            if mod.source != source
        ]

    def get_total_stat(self, stat_type: StatType) -> int:
        """Calculate total stat value including modifiers."""
        base_value = self.base_stats[stat_type]
        flat_bonus = sum(
            mod.value for mod in self.modifiers[stat_type]
            if not mod.is_percentage
        )
        
        percentage_multiplier = 1.0 + sum(
            mod.value / 100.0 for mod in self.modifiers[stat_type]
            if mod.is_percentage
        )
        
        return int((base_value + flat_bonus) * percentage_multiplier)

    def update_durations(self) -> None:
        """Update duration of temporary modifiers."""
        for stat_type in StatType:
            remaining_mods = []
            for mod in self.modifiers[stat_type]:
                if mod.duration is None:
                    remaining_mods.append(mod)
                elif mod.duration > 0:
                    mod.duration -= 1
                    remaining_mods.append(mod)
            self.modifiers[stat_type] = remaining_mods

@dataclass
class DerivedStats:
    """Stats derived from base statistics."""
    
    def __init__(self, base_stats: Stats):
        self._stats = base_stats
        self._calculate_derived_stats()

    def _calculate_derived_stats(self) -> None:
        """Calculate all derived statistics."""
        self.max_health = self._calculate_max_health()
        self.max_stamina = self._calculate_max_stamina()
        self.physical_defense = self._calculate_physical_defense()
        self.magical_defense = self._calculate_magical_defense()
        self.initiative = self._calculate_initiative()

    def _calculate_max_health(self) -> int:
        """Calculate maximum health."""
        constitution = self._stats.get_total_stat(StatType.CONSTITUTION)
        return constitution * 10

    def _calculate_max_stamina(self) -> int:
        """Calculate maximum stamina."""
        constitution = self._stats.get_total_stat(StatType.CONSTITUTION)
        dexterity = self._stats.get_total_stat(StatType.DEXTERITY)
        return (constitution * 5) + (dexterity * 3)

    def _calculate_physical_defense(self) -> int:
        """Calculate physical defense."""
        constitution = self._stats.get_total_stat(StatType.CONSTITUTION)
        strength = self._stats.get_total_stat(StatType.STRENGTH)
        return int((constitution + strength) * 0.5)

    def _calculate_magical_defense(self) -> int:
        """Calculate magical defense."""
        wisdom = self._stats.get_total_stat(StatType.WISDOM)
        intelligence = self._stats.get_total_stat(StatType.INTELLIGENCE)
        return int((wisdom + intelligence) * 0.5)

    def _calculate_initiative(self) -> int:
        """Calculate combat initiative."""
        dexterity = self._stats.get_total_stat(StatType.DEXTERITY)
        wisdom = self._stats.get_total_stat(StatType.WISDOM)
        return int((dexterity * 0.7) + (wisdom * 0.3))

    def update(self) -> None:
        """Update all derived stats."""
        self._calculate_derived_stats()