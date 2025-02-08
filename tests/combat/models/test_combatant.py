import pytest
from uuid import UUID
from combat.models.combatant import CombatantState
from combat.models.effects import StatusEffect
from common.errors import ValidationError

class TestCombatant:
    @pytest.fixture
    def basic_combatant(self) -> CombatantState:
        """Create a basic combatant for testing."""
        return CombatantState(
            id="test_fighter",
            health=100,
            max_health=100,
            stamina=50,
            max_stamina=50
        )

    @pytest.fixture
    def status_effect(self) -> StatusEffect:
        """Create a sample status effect."""
        return StatusEffect(
            id="effect_1",
            name="Test Effect",
            duration=3,
            strength=1.5
        )

    def test_combatant_creation(self):
        """Test basic combatant creation with valid parameters."""
        combatant = CombatantState(
            id="fighter_1",
            health=100,
            max_health=100,
            stamina=50,
            max_stamina=50
        )
        
        assert combatant.id == "fighter_1"
        assert combatant.health == 100
        assert combatant.max_health == 100
        assert combatant.stamina == 50
        assert combatant.max_stamina == 50
        assert combatant.position == 0.0
        assert len(combatant.status_effects) == 0

    def test_invalid_health_values(self):
        """Test combatant creation with invalid health values."""
        with pytest.raises(ValueError, match="Health cannot exceed max health"):
            CombatantState(
                id="fighter_1",
                health=150,
                max_health=100,
                stamina=50,
                max_stamina=50
            )

    def test_invalid_stamina_values(self):
        """Test combatant creation with invalid stamina values."""
        with pytest.raises(ValueError, match="Stamina cannot exceed max stamina"):
            CombatantState(
                id="fighter_1",
                health=100,
                max_health=100,
                stamina=75,
                max_stamina=50
            )

    def test_negative_values(self):
        """Test combatant creation with negative values."""
        with pytest.raises(ValueError):
            CombatantState(
                id="fighter_1",
                health=-10,
                max_health=100,
                stamina=50,
                max_stamina=50
            )

    def test_add_status_effect(self, basic_combatant, status_effect):
        """Test adding status effects to combatant."""
        basic_combatant.status_effects.append(status_effect)
        assert len(basic_combatant.status_effects) == 1
        assert basic_combatant.status_effects[0].name == "Test Effect"

    def test_status_effect_duration(self, basic_combatant, status_effect):
        """Test status effect duration management."""
        basic_combatant.status_effects.append(status_effect)
        assert basic_combatant.status_effects[0].duration == 3
        
        # Simulate duration decrease
        basic_combatant.status_effects[0].duration -= 1
        assert basic_combatant.status_effects[0].duration == 2

    def test_move_position(self, basic_combatant):
        """Test combatant movement."""
        initial_pos = basic_combatant.position
        basic_combatant.position += 5.0
        assert basic_combatant.position == initial_pos + 5.0

    def test_clone_combatant(self, basic_combatant, status_effect):
        """Test cloning combatant with all attributes."""
        basic_combatant.status_effects.append(status_effect)
        basic_combatant.position = 3.5
        
        cloned = basic_combatant.clone()
        
        assert cloned is not basic_combatant
        assert cloned.id == basic_combatant.id
        assert cloned.health == basic_combatant.health
        assert cloned.max_health == basic_combatant.max_health
        assert cloned.stamina == basic_combatant.stamina
        assert cloned.max_stamina == basic_combatant.max_stamina
        assert cloned.position == basic_combatant.position
        assert len(cloned.status_effects) == len(basic_combatant.status_effects)
        
        # Verify status effects are deep copied
        assert cloned.status_effects[0] is not basic_combatant.status_effects[0]
        assert cloned.status_effects[0].name == basic_combatant.status_effects[0].name

    def test_take_damage(self, basic_combatant):
        """Test damage application."""
        initial_health = basic_combatant.health
        damage = 30
        
        basic_combatant.health = max(0, basic_combatant.health - damage)
        assert basic_combatant.health == initial_health - damage

    def test_heal(self, basic_combatant):
        """Test healing application."""
        basic_combatant.health = 50  # Set initial damage
        heal_amount = 20
        
        basic_combatant.health = min(basic_combatant.max_health, 
                                   basic_combatant.health + heal_amount)
        assert basic_combatant.health == 70

    def test_zero_health(self, basic_combatant):
        """Test health cannot go below zero."""
        basic_combatant.health = 0
        assert basic_combatant.health == 0
        
        # Try to reduce health below zero
        basic_combatant.health = max(0, basic_combatant.health - 50)
        assert basic_combatant.health == 0

    def test_use_stamina(self, basic_combatant):
        """Test stamina consumption."""
        initial_stamina = basic_combatant.stamina
        cost = 20
        
        basic_combatant.stamina = max(0, basic_combatant.stamina - cost)
        assert basic_combatant.stamina == initial_stamina - cost

    def test_invalid_id(self):
        """Test combatant creation with invalid ID."""
        with pytest.raises(ValueError, match="Combatant ID cannot be empty"):
            CombatantState(
                id="",
                health=100,
                max_health=100,
                stamina=50,
                max_stamina=50
            )