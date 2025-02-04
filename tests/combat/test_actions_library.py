"""
Tests for the actions library.

These tests verify the functionality of predefined actions and their
interactions with the core systems.
"""

import pytest
from combat.lib.actions_library import (
    ACTIONS,
    create_action,
    validate_action_chain,
    get_available_actions
)
from combat.lib.action_system import (
    ActionStateType,
    ActionVisibility,
    ActionCommitment,
    ActionPhase
)
from tests.combat.conftest import create_test_combatant_state

class TestActionDefinitions:
    """Test suite for action definitions."""

    def test_action_properties(self):
        """Test basic action properties."""
        # All actions should have required properties
        for action_type, props in ACTIONS.items():
            assert "stamina_cost" in props
            assert "time" in props
            assert "category" in props
            assert "description" in props

    def test_action_categories(self):
        """Test action categorization."""
        # Check attack actions
        assert ACTIONS["quick_attack"]["category"] == "attack"
        assert ACTIONS["heavy_attack"]["category"] == "attack"
        
        # Check defense actions
        assert ACTIONS["block"]["category"] == "defense"
        assert ACTIONS["parry"]["category"] == "defense"
        
        # Check movement actions
        assert ACTIONS["move_forward"]["category"] == "movement"
        assert ACTIONS["move_backward"]["category"] == "movement"

    def test_action_requirements(self):
        """Test action requirements."""
        # Check stamina costs
        assert ACTIONS["quick_attack"]["stamina_cost"] < ACTIONS["heavy_attack"]["stamina_cost"]
        assert ACTIONS["block"]["stamina_cost"] > 0
        
        # Check timing
        assert ACTIONS["quick_attack"]["time"] < ACTIONS["heavy_attack"]["time"]
        assert ACTIONS["parry"]["time"] < ACTIONS["block"]["time"]

class TestActionCreation:
    """Test suite for action creation."""

    def test_create_basic_action(self):
        """Test basic action creation."""
        action = create_action(
            "quick_attack",
            "attacker_1",
            "defender_1"
        )
        
        assert action.type == "quick_attack"
        assert action.source_id == "attacker_1"
        assert action.target_id == "defender_1"
        assert action.state == ActionStateType.FEINT
        assert action.visibility == ActionVisibility.TELEGRAPHED
        assert action.commitment == ActionCommitment.NONE

    def test_create_advanced_action(self):
        """Test advanced action creation."""
        action = create_action(
            "heavy_attack",
            "attacker_1",
            "defender_1",
            visibility=ActionVisibility.HIDDEN,
            commitment=ActionCommitment.FULL
        )
        
        assert action.type == "heavy_attack"
        assert action.visibility == ActionVisibility.HIDDEN
        assert action.commitment == ActionCommitment.FULL
        assert action.feint_cost > 0

    def test_invalid_action(self):
        """Test invalid action creation."""
        with pytest.raises(ValueError):
            create_action(
                "invalid_action",
                "attacker_1",
                "defender_1"
            )

class TestActionChains:
    """Test suite for action chaining."""

    def test_valid_chain(self):
        """Test valid action chain."""
        chain = [
            create_action("move_forward", "fighter_1"),
            create_action("quick_attack", "fighter_1", "fighter_2"),
            create_action("move_backward", "fighter_1")
        ]
        
        assert validate_action_chain(chain)

    def test_invalid_chain(self):
        """Test invalid action chain."""
        # Can't move backward then forward immediately
        chain = [
            create_action("move_backward", "fighter_1"),
            create_action("move_forward", "fighter_1")
        ]
        
        assert not validate_action_chain(chain)
        
        # Can't attack twice in a row without recovery
        chain = [
            create_action("quick_attack", "fighter_1", "fighter_2"),
            create_action("quick_attack", "fighter_1", "fighter_2")
        ]
        
        assert not validate_action_chain(chain)

    def test_commitment_chain(self):
        """Test chains with commitments."""
        # Can't chain after full commitment
        chain = [
            create_action(
                "heavy_attack",
                "fighter_1",
                "fighter_2",
                commitment=ActionCommitment.FULL
            ),
            create_action("move_backward", "fighter_1")
        ]
        
        assert not validate_action_chain(chain)
        
        # Can chain after partial commitment
        chain = [
            create_action(
                "quick_attack",
                "fighter_1",
                "fighter_2",
                commitment=ActionCommitment.PARTIAL
            ),
            create_action("move_backward", "fighter_1")
        ]
        
        assert validate_action_chain(chain)

class TestActionAvailability:
    """Test suite for action availability."""

    def test_available_actions(self):
        """Test getting available actions."""
        state = create_test_combatant_state(
            "fighter_1",
            stamina=100.0,
            speed=1.0
        )
        
        actions = get_available_actions(state)
        
        # Should have basic actions
        assert any(a.type == "quick_attack" for a in actions)
        assert any(a.type == "block" for a in actions)
        assert any(a.type == "move_forward" for a in actions)

    def test_stamina_restrictions(self):
        """Test stamina-based restrictions."""
        # Low stamina state
        low_stamina = create_test_combatant_state(
            "fighter_1",
            stamina=5.0
        )
        
        actions = get_available_actions(low_stamina)
        
        # Should not have high-cost actions
        assert not any(a.type == "heavy_attack" for a in actions)
        assert not any(
            a.type == "quick_attack" and a.commitment == ActionCommitment.FULL
            for a in actions
        )

    def test_speed_restrictions(self):
        """Test speed-based restrictions."""
        # Low speed state
        low_speed = create_test_combatant_state(
            "fighter_1",
            speed=0.5
        )
        
        actions = get_available_actions(low_speed)
        
        # Should not have quick actions
        assert not any(a.type == "quick_attack" for a in actions)
        assert not any(a.type == "parry" for a in actions)

class TestIntegration:
    """Integration tests for actions library."""

    def test_realistic_combat_sequence(self):
        """Test a realistic combat sequence."""
        fighter_1 = create_test_combatant_state("fighter_1")
        fighter_2 = create_test_combatant_state("fighter_2")
        
        # Create an exchange sequence
        sequence = [
            # Fighter 1 advances and attacks
            create_action("move_forward", "fighter_1"),
            create_action(
                "quick_attack",
                "fighter_1",
                "fighter_2",
                commitment=ActionCommitment.PARTIAL
            ),
            
            # Fighter 2 blocks and counters
            create_action(
                "block",
                "fighter_2",
                commitment=ActionCommitment.PARTIAL
            ),
            create_action(
                "quick_attack",
                "fighter_2",
                "fighter_1"
            ),
            
            # Fighter 1 evades and retreats
            create_action("evade", "fighter_1"),
            create_action("move_backward", "fighter_1")
        ]
        
        # Sequence should be valid
        assert validate_action_chain(sequence)
        
        # Each action should be available when it's used
        for action in sequence:
            if action.source_id == "fighter_1":
                state = fighter_1
            else:
                state = fighter_2
                
            available = get_available_actions(state)
            assert any(
                a.type == action.type and
                a.commitment == action.commitment
                for a in available
            )

    def test_performance(self, performance_stats):
        """Test actions library performance."""
        # Measure action creation performance
        start_time = datetime.now()
        for _ in range(1000):
            create_action("quick_attack", "fighter_1", "fighter_2")
        creation_time = (datetime.now() - start_time).total_seconds()
        performance_stats.record_operation("action_creation", creation_time)
        
        # Measure chain validation performance
        chain = [
            create_action("move_forward", "fighter_1"),
            create_action("quick_attack", "fighter_1", "fighter_2"),
            create_action("move_backward", "fighter_1")
        ]
        
        start_time = datetime.now()
        for _ in range(1000):
            validate_action_chain(chain)
        validation_time = (datetime.now() - start_time).total_seconds()
        performance_stats.record_operation("chain_validation", validation_time)
        
        # Verify performance
        assert creation_time < 0.1  # Should create actions quickly
        assert validation_time < 0.1  # Should validate chains quickly
