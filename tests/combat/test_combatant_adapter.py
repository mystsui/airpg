"""
Tests for the CombatantAdapter class.

These tests verify that the adapter correctly implements the ICombatant interface
and maintains compatibility with the existing combat system.
"""

import pytest
from combat.adapters import CombatantAdapter
from combat.combatant import TestCombatant
from combat.interfaces import Action, CombatantState
from combat.lib.actions_library import ACTIONS

def create_test_combatant():
    """Create a test combatant with standard attributes."""
    return TestCombatant(
        combatant_id=1,
        name="Test Fighter",
        health=100,
        stamina=100,
        attack_power=20,
        accuracy=100,
        blocking_power=30,
        evading_ability=0,
        mobility=50,
        range_a=0,
        range_b=50,
        stamina_recovery=10,
        position="left",
        facing="right",
        perception=0,
        stealth=0
    )

class TestCombatantAdapter:
    """Test suite for CombatantAdapter class."""

    @pytest.fixture
    def adapter(self):
        """Create a fresh adapter instance for each test."""
        combatant = create_test_combatant()
        return CombatantAdapter(combatant)

    def test_get_state(self, adapter):
        """Test that get_state returns correct CombatantState."""
        state = adapter.get_state()
        
        assert isinstance(state, CombatantState)
        assert state.entity_id == "1"
        assert state.health == 100
        assert state.max_health == 100
        assert state.stamina == 100
        assert state.max_stamina == 100
        assert state.position == "left"
        assert state.facing == "right"
        assert state.blocking_power == 30

    def test_apply_action(self, adapter):
        """Test that apply_action correctly updates combatant state."""
        action = Action(
            type="try_attack",
            time=100,
            stamina_cost=ACTIONS["try_attack"]["stamina_cost"],
            source_id="1",
            status="pending"
        )
        
        adapter.apply_action(action)
        
        assert adapter.adaptee.action is not None
        assert adapter.adaptee.action["type"] == "try_attack"
        assert adapter.adaptee.action["time"] == 100
        assert adapter.adaptee.action["status"] == "pending"

    def test_validate_action(self, adapter):
        """Test that validate_action correctly checks action validity."""
        valid_action = Action(
            type="try_attack",
            time=100,
            stamina_cost=ACTIONS["try_attack"]["stamina_cost"],
            source_id="1"
        )
        
        invalid_action = Action(
            type="invalid_action",
            time=100,
            stamina_cost=0,
            source_id="1"
        )
        
        assert adapter.validate_action(valid_action) is True
        assert adapter.validate_action(invalid_action) is False

    def test_is_within_range(self, adapter):
        """Test range validation."""
        # Test combatant has range 0-50
        assert adapter.is_within_range(25) is True
        assert adapter.is_within_range(75) is False

    def test_is_facing_opponent(self, adapter):
        """Test opponent facing check."""
        opponent = create_test_combatant()
        opponent.position = "right"  # Adapter's facing is "right"
        
        assert adapter.is_facing_opponent(CombatantAdapter(opponent)) is True
        
        opponent.position = "left"
        assert adapter.is_facing_opponent(CombatantAdapter(opponent)) is False

    def test_is_defeated(self, adapter):
        """Test defeat condition check."""
        assert adapter.is_defeated() is False
        
        adapter.adaptee.health = 0
        assert adapter.is_defeated() is True

    def test_stamina_requirement(self, adapter):
        """Test that actions are validated against stamina requirements."""
        # Drain stamina
        adapter.adaptee.stamina = 5
        
        # Try attack requires 10 stamina
        action = Action(
            type="try_attack",
            time=100,
            stamina_cost=ACTIONS["try_attack"]["stamina_cost"],
            source_id="1"
        )
        
        assert adapter.validate_action(action) is False

    def test_adapter_maintains_identity(self, adapter):
        """Test that adapter preserves the identity of the adapted combatant."""
        original_id = adapter.adaptee.combatant_id
        original_name = adapter.adaptee.name
        
        state = adapter.get_state()
        
        assert state.entity_id == str(original_id)
        assert adapter.adaptee.name == original_name

    def test_adapter_with_null_action(self, adapter):
        """Test adapter handles null action state correctly."""
        adapter.adaptee.action = None
        state = adapter.get_state()
        
        assert state.action is None

    def test_adapter_with_opponent_interaction(self, adapter):
        """Test adapter interaction with another adapter instance."""
        opponent = CombatantAdapter(create_test_combatant())
        opponent.adaptee.position = "right"
        opponent.adaptee.facing = "left"
        
        # Test mutual facing
        assert adapter.is_facing_opponent(opponent) is True
        assert opponent.is_facing_opponent(adapter) is True
