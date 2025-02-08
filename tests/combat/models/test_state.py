import pytest
from uuid import UUID
from datetime import datetime
from combat.models.state import CombatState
from combat.models.combatant import CombatantState
from combat.models.effects import StatusEffect

class TestCombatState:
    @pytest.fixture
    def sample_combatant(self) -> CombatantState:
        return CombatantState(
            id="test_combatant",
            health=100,
            max_health=100,
            stamina=50,
            max_stamina=50
        )

    @pytest.fixture
    def sample_effect(self) -> StatusEffect:
        return StatusEffect(
            id="test_effect",
            name="Test Effect",
            duration=3,
            strength=1.5
        )

    def test_combat_state_creation(self):
        """Test basic combat state creation."""
        state = CombatState()
        assert isinstance(state.id, UUID)
        assert isinstance(state.timestamp, float)
        assert state.combatants == {}
        assert state.active_effects == []
        assert state.round_number == 0

    def test_combat_state_with_combatants(self, sample_combatant):
        """Test combat state with combatants."""
        state = CombatState(combatants={"fighter1": sample_combatant})
        assert len(state.combatants) == 1
        assert "fighter1" in state.combatants
        assert state.combatants["fighter1"].health == 100

    def test_combat_state_with_effects(self, sample_effect):
        """Test combat state with active effects."""
        state = CombatState(active_effects=[sample_effect])
        assert len(state.active_effects) == 1
        assert state.active_effects[0].name == "Test Effect"

    def test_combat_state_clone(self, sample_combatant, sample_effect):
        """Test combat state cloning."""
        original = CombatState(
            combatants={"fighter1": sample_combatant},
            active_effects=[sample_effect],
            round_number=5
        )
        
        cloned = original.clone()
        
        # Check if it's a different object
        assert cloned is not original
        assert cloned.id == original.id
        assert cloned.timestamp == original.timestamp
        
        # Check combatants
        assert len(cloned.combatants) == len(original.combatants)
        assert cloned.combatants["fighter1"] is not original.combatants["fighter1"]
        assert cloned.combatants["fighter1"].health == original.combatants["fighter1"].health
        
        # Check effects
        assert len(cloned.active_effects) == len(original.active_effects)
        assert cloned.active_effects[0] is not original.active_effects[0]
        assert cloned.active_effects[0].name == original.active_effects[0].name

    def test_combat_state_timestamp(self):
        """Test combat state timestamp is current."""
        before = datetime.now().timestamp()
        state = CombatState()
        after = datetime.now().timestamp()
        
        assert before <= state.timestamp <= after

    def test_combat_state_invalid_combatant(self, sample_combatant):
        """Test adding invalid combatant."""
        with pytest.raises(ValueError):
            CombatState(combatants={"": sample_combatant})

    def test_combat_state_round_increment(self):
        """Test round number increment."""
        state = CombatState()
        assert state.round_number == 0
        
        new_state = CombatState(
            id=state.id,
            timestamp=state.timestamp,
            round_number=state.round_number + 1
        )
        assert new_state.round_number == 1

class TestCombatantState:
    def test_combatant_state_creation(self):
        """Test basic combatant state creation."""
        combatant = CombatantState(
            id="test",
            health=100,
            max_health=100,
            stamina=50,
            max_stamina=50
        )
        assert combatant.id == "test"
        assert combatant.health == 100
        assert combatant.stamina == 50
        assert combatant.position == 0.0
        assert combatant.status_effects == []

    def test_combatant_state_clone(self, sample_effect):
        """Test combatant state cloning."""
        original = CombatantState(
            id="test",
            health=100,
            max_health=100,
            stamina=50,
            max_stamina=50,
            position=2.5,
            status_effects=[sample_effect]
        )
        
        cloned = original.clone()
        
        assert cloned is not original
        assert cloned.id == original.id
        assert cloned.health == original.health
        assert cloned.position == original.position
        assert len(cloned.status_effects) == len(original.status_effects)
        assert cloned.status_effects[0] is not original.status_effects[0]
        assert cloned.status_effects[0].name == original.status_effects[0].name

    def test_combatant_state_invalid_health(self):
        """Test invalid health values."""
        with pytest.raises(ValueError):
            CombatantState(
                id="test",
                health=200,
                max_health=100,
                stamina=50,
                max_stamina=50
            )

    def test_combatant_state_invalid_stamina(self):
        """Test invalid stamina values."""
        with pytest.raises(ValueError):
            CombatantState(
                id="test",
                health=100,
                max_health=100,
                stamina=100,
                max_stamina=50
            )