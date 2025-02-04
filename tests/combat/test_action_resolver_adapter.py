"""
Tests for the ActionResolverAdapter class.

These tests verify that the adapter correctly implements the IActionResolver interface
and maintains the expected action resolution behavior.
"""

import pytest
from combat.adapters import ActionResolverAdapter, CombatantAdapter
from combat.interfaces import Action, ActionResult
from combat.lib.actions_library import ACTIONS
from .test_combatant_adapter import create_test_combatant

class TestActionResolverAdapter:
    """Test suite for ActionResolverAdapter class."""

    @pytest.fixture
    def resolver(self):
        """Create a fresh resolver instance for each test."""
        return ActionResolverAdapter()

    @pytest.fixture
    def attacker(self):
        """Create an attacking combatant."""
        return CombatantAdapter(create_test_combatant())

    @pytest.fixture
    def defender(self):
        """Create a defending combatant."""
        combatant = create_test_combatant()
        combatant.position = "right"
        combatant.facing = "left"
        return CombatantAdapter(combatant)

    def test_validate_action(self, resolver, attacker):
        """Test that validate_action correctly validates actions."""
        # Valid action
        valid_action = Action(
            type="try_attack",
            time=100,
            stamina_cost=ACTIONS["try_attack"]["stamina_cost"],
            source_id="1"
        )
        assert resolver.validate(valid_action, attacker) is True

        # Invalid action type
        invalid_action = Action(
            type="invalid_action",
            time=100,
            stamina_cost=0,
            source_id="1"
        )
        assert resolver.validate(invalid_action, attacker) is False

        # Insufficient stamina
        attacker.adaptee.stamina = 0
        assert resolver.validate(valid_action, attacker) is False

    def test_get_available_actions(self, resolver, attacker):
        """Test that get_available_actions returns correct actions."""
        actions = resolver.get_available_actions(attacker)
        
        # Should have all actions initially (full stamina)
        assert len(actions) == len(ACTIONS)
        
        # Drain stamina
        attacker.adaptee.stamina = 5
        limited_actions = resolver.get_available_actions(attacker)
        
        # Should only have actions with stamina cost <= 5
        assert len(limited_actions) < len(ACTIONS)
        assert all(action.stamina_cost <= 5 for action in limited_actions)

    def test_resolve_attack_hit(self, resolver, attacker, defender):
        """Test resolving a successful attack."""
        action = Action(
            type="release_attack",
            time=100,
            stamina_cost=0,
            source_id=attacker.get_state().entity_id,
            target_id=defender.get_state().entity_id
        )
        
        result = resolver.resolve(action, attacker, defender)
        
        assert result.success is True
        assert result.outcome == "hit"
        assert result.damage > 0
        assert "target_health" in result.state_changes

    def test_resolve_attack_blocked(self, resolver, attacker, defender):
        """Test resolving an attack against a blocking defender."""
        # Set up blocking state
        defender.adaptee.action = {
            "type": "blocking",
            "time": 100,
            "status": "pending"
        }
        
        action = Action(
            type="release_attack",
            time=100,
            stamina_cost=0,
            source_id=attacker.get_state().entity_id,
            target_id=defender.get_state().entity_id
        )
        
        result = resolver.resolve(action, attacker, defender)
        
        if result.outcome == "blocked":
            assert result.success is False
            assert "target_blocking_power" in result.state_changes
        else:  # breached
            assert result.success is True
            assert "target_blocking_power" in result.state_changes
            assert "target_health" in result.state_changes

    def test_resolve_attack_evaded(self, resolver, attacker, defender):
        """Test resolving an attack against an evading defender."""
        defender.adaptee.action = {
            "type": "evading",
            "time": 100,
            "status": "pending"
        }
        
        action = Action(
            type="release_attack",
            time=100,
            stamina_cost=0,
            source_id=attacker.get_state().entity_id,
            target_id=defender.get_state().entity_id
        )
        
        result = resolver.resolve(action, attacker, defender)
        
        assert result.success is False
        assert result.outcome == "evaded"
        assert result.damage == 0

    def test_resolve_movement(self, resolver, attacker):
        """Test resolving movement actions."""
        # Test move forward
        forward_action = Action(
            type="move_forward",
            time=100,
            stamina_cost=ACTIONS["move_forward"]["stamina_cost"],
            source_id=attacker.get_state().entity_id
        )
        
        result = resolver.resolve(forward_action, attacker, None)
        
        assert result.success is True
        assert result.outcome == "move_forward"
        assert "distance" in result.state_changes
        assert result.state_changes["distance"] < 0  # Moving forward reduces distance

        # Test move backward
        backward_action = Action(
            type="move_backward",
            time=100,
            stamina_cost=ACTIONS["move_backward"]["stamina_cost"],
            source_id=attacker.get_state().entity_id
        )
        
        result = resolver.resolve(backward_action, attacker, None)
        
        assert result.success is True
        assert result.outcome == "move_backward"
        assert "distance" in result.state_changes
        assert result.state_changes["distance"] > 0  # Moving backward increases distance

    def test_resolve_neutral_actions(self, resolver, attacker):
        """Test resolving neutral actions."""
        # Test recover action
        recover_action = Action(
            type="recover",
            time=100,
            stamina_cost=ACTIONS["recover"]["stamina_cost"],
            source_id=attacker.get_state().entity_id
        )
        
        result = resolver.resolve(recover_action, attacker, None)
        
        assert result.success is True
        assert result.outcome == "recover"
        assert "actor_stamina" in result.state_changes
        assert result.state_changes["actor_stamina"] > 0  # Recovery adds stamina

    def test_resolve_block(self, resolver, attacker):
        """Test resolving block actions."""
        block_action = Action(
            type="blocking",
            time=100,
            stamina_cost=ACTIONS["blocking"]["stamina_cost"],
            source_id=attacker.get_state().entity_id
        )
        
        result = resolver.resolve(block_action, attacker, None)
        
        assert result.success is True
        assert result.outcome == "blocking"
        assert "actor_stamina" in result.state_changes
        assert result.state_changes["actor_stamina"] < 0  # Blocking costs stamina

    def test_resolve_evade(self, resolver, attacker):
        """Test resolving evade actions."""
        evade_action = Action(
            type="evading",
            time=100,
            stamina_cost=ACTIONS["evading"]["stamina_cost"],
            source_id=attacker.get_state().entity_id
        )
        
        result = resolver.resolve(evade_action, attacker, None)
        
        assert result.success is True
        assert result.outcome == "evading"
        assert "actor_stamina" in result.state_changes
        assert result.state_changes["actor_stamina"] < 0  # Evading costs stamina
