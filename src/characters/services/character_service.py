from typing import Dict, List, Optional
from uuid import UUID

from ..models.character import Character, CharacterClass, CharacterSkill
from ..models.stats import Stats, StatType, StatModifier
from combat.models.combatant import CombatantState

class CharacterService:
    """
    Service layer for character management operations.
    Handles character creation, modification, and stat management.
    """
    
    def __init__(self):
        self._characters: Dict[UUID, Character] = {}
        self._starting_stats = {
            CharacterClass.WARRIOR: {
                StatType.STRENGTH: 14,
                StatType.CONSTITUTION: 12,
                StatType.DEXTERITY: 10,
                StatType.INTELLIGENCE: 8,
                StatType.WISDOM: 10,
                StatType.CHARISMA: 10
            },
            CharacterClass.ROGUE: {
                StatType.STRENGTH: 10,
                StatType.CONSTITUTION: 10,
                StatType.DEXTERITY: 14,
                StatType.INTELLIGENCE: 12,
                StatType.WISDOM: 8,
                StatType.CHARISMA: 10
            },
            CharacterClass.MAGE: {
                StatType.STRENGTH: 8,
                StatType.CONSTITUTION: 10,
                StatType.DEXTERITY: 10,
                StatType.INTELLIGENCE: 14,
                StatType.WISDOM: 12,
                StatType.CHARISMA: 10
            },
            CharacterClass.RANGER: {
                StatType.STRENGTH: 10,
                StatType.CONSTITUTION: 10,
                StatType.DEXTERITY: 14,
                StatType.INTELLIGENCE: 10,
                StatType.WISDOM: 12,
                StatType.CHARISMA: 8
            }
        }

    def create_character(
        self,
        name: str,
        character_class: CharacterClass
    ) -> Character:
        """
        Create a new character with default stats based on class.
        
        Args:
            name: Character name
            character_class: Selected character class
            
        Returns:
            Newly created character
        """
        stats = Stats()
        for stat_type, value in self._starting_stats[character_class].items():
            stats.set_base_stat(stat_type, value)

        character = Character(
            name=name,
            character_class=character_class,
            stats=stats
        )
        
        self._characters[character.id] = character
        return character

    def get_character(self, character_id: UUID) -> Optional[Character]:
        """Retrieve a character by ID."""
        return self._characters.get(character_id)

    def level_up_character(self, character_id: UUID) -> bool:
        """
        Process character level up.
        
        Args:
            character_id: ID of character to level up
            
        Returns:
            True if level up was successful
        """
        character = self._characters.get(character_id)
        if not character:
            return False

        # Apply level-up bonuses based on class
        stat_increases = self._get_level_up_stats(character.character_class)
        for stat_type, increase in stat_increases.items():
            current = character.stats.get_base_stat(stat_type)
            character.stats.set_base_stat(stat_type, current + increase)

        character._calculate_derived_stats()
        return True

    def add_skill(
        self,
        character_id: UUID,
        skill: CharacterSkill
    ) -> bool:
        """
        Add a skill to a character.
        
        Args:
            character_id: Target character ID
            skill: Skill to add
            
        Returns:
            True if skill was added successfully
        """
        character = self._characters.get(character_id)
        if not character:
            return False

        return character.add_skill(skill)

    def apply_modifier(
        self,
        character_id: UUID,
        stat_type: StatType,
        modifier: StatModifier
    ) -> bool:
        """
        Apply a stat modifier to a character.
        
        Args:
            character_id: Target character ID
            stat_type: Stat to modify
            modifier: Modifier to apply
            
        Returns:
            True if modifier was applied successfully
        """
        character = self._characters.get(character_id)
        if not character:
            return False

        character.stats.add_modifier(stat_type, modifier)
        character._calculate_derived_stats()
        return True

    def prepare_for_combat(self, character_id: UUID) -> Optional[CombatantState]:
        """
        Convert character to combat state.
        
        Args:
            character_id: Character to convert
            
        Returns:
            Combat state for the character
        """
        character = self._characters.get(character_id)
        if not character:
            return None

        return character.to_combat_state()

    def _get_level_up_stats(self, character_class: CharacterClass) -> Dict[StatType, int]:
        """Get stat increases for level up based on class."""
        if character_class == CharacterClass.WARRIOR:
            return {
                StatType.STRENGTH: 2,
                StatType.CONSTITUTION: 2,
                StatType.DEXTERITY: 1
            }
        elif character_class == CharacterClass.ROGUE:
            return {
                StatType.DEXTERITY: 2,
                StatType.INTELLIGENCE: 2,
                StatType.STRENGTH: 1
            }
        elif character_class == CharacterClass.MAGE:
            return {
                StatType.INTELLIGENCE: 2,
                StatType.WISDOM: 2,
                StatType.CONSTITUTION: 1
            }
        else:  # RANGER
            return {
                StatType.DEXTERITY: 2,
                StatType.WISDOM: 2,
                StatType.STRENGTH: 1
            }