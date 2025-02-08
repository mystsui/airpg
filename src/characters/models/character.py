from dataclasses import dataclass, field
from typing import Dict, List, Optional
from uuid import UUID, uuid4
from enum import Enum

class CharacterClass(Enum):
    """Available character classes."""
    WARRIOR = "warrior"
    ROGUE = "rogue"
    MAGE = "mage"
    RANGER = "ranger"

@dataclass
class CharacterStats:
    """Base character statistics."""
    strength: int = 10
    dexterity: int = 10
    constitution: int = 10
    intelligence: int = 10
    wisdom: int = 10
    charisma: int = 10

    def modify_stat(self, stat_name: str, amount: int) -> None:
        """Modify a stat by the given amount."""
        if hasattr(self, stat_name):
            current_value = getattr(self, stat_name)
            setattr(self, stat_name, max(1, current_value + amount))

@dataclass
class CharacterSkill:
    """Represents a character skill."""
    id: UUID = field(default_factory=uuid4)
    name: str
    description: str
    level: int = 1
    max_level: int = 10
    requirements: Dict[str, int] = field(default_factory=dict)

@dataclass
class Character:
    """Main character class representing an entity in the game."""
    id: UUID = field(default_factory=uuid4)
    name: str
    character_class: CharacterClass
    level: int = 1
    experience: int = 0
    stats: CharacterStats = field(default_factory=CharacterStats)
    skills: List[CharacterSkill] = field(default_factory=list)
    
    # Derived attributes
    max_health: int = field(init=False)
    max_stamina: int = field(init=False)
    
    def __post_init__(self):
        """Initialize derived attributes."""
        self._calculate_derived_stats()

    def _calculate_derived_stats(self) -> None:
        """Calculate stats that depend on base attributes."""
        self.max_health = (self.stats.constitution * 10) + (self.level * 5)
        self.max_stamina = (self.stats.constitution * 5) + (self.stats.dexterity * 3)

    def gain_experience(self, amount: int) -> bool:
        """
        Add experience points and check for level up.
        Returns True if level up occurred.
        """
        self.experience += amount
        return self._check_level_up()

    def _check_level_up(self) -> bool:
        """Check and process level up if applicable."""
        exp_needed = self._calculate_exp_needed()
        if self.experience >= exp_needed:
            self.level += 1
            self._calculate_derived_stats()
            return True
        return False

    def _calculate_exp_needed(self) -> int:
        """Calculate experience needed for next level."""
        return self.level * 1000

    def add_skill(self, skill: CharacterSkill) -> bool:
        """
        Add a new skill if requirements are met.
        Returns True if skill was added successfully.
        """
        if self._meets_skill_requirements(skill):
            self.skills.append(skill)
            return True
        return False

    def _meets_skill_requirements(self, skill: CharacterSkill) -> bool:
        """Check if character meets skill requirements."""
        for stat_name, required_value in skill.requirements.items():
            if hasattr(self.stats, stat_name):
                current_value = getattr(self.stats, stat_name)
                if current_value < required_value:
                    return False
        return True

    def upgrade_skill(self, skill_id: UUID) -> bool:
        """
        Upgrade a skill if possible.
        Returns True if skill was upgraded successfully.
        """
        for skill in self.skills:
            if skill.id == skill_id and skill.level < skill.max_level:
                skill.level += 1
                return True
        return False

    def to_combat_state(self) -> 'CombatantState':
        """Convert character to combat state."""
        from combat.models.combatant import CombatantState
        
        return CombatantState(
            id=str(self.id),
            health=self.max_health,
            max_health=self.max_health,
            stamina=self.max_stamina,
            max_stamina=self.max_stamina
        )

    def can_use_skill(self, skill_id: UUID) -> bool:
        """Check if character can use a specific skill."""
        for skill in self.skills:
            if skill.id == skill_id:
                return self._meets_skill_requirements(skill)
        return False