"""
Tests for attack actions.

These tests verify the functionality of attack-specific mechanics
including damage calculations, accuracy, and special properties.
"""

import pytest
from datetime import datetime
from combat.lib.actions_library import (
    ACTIONS,
    create_action,
    get_available_actions,
    validate_action_chain
)
from combat.lib.action_system import (
    ActionStateType,
    ActionVisibility,
    ActionCommitment,
    ActionPhase
)
from tests.combat.conftest import create_test_combatant_state

class TestAttackProperties:
    """Test suite for attack action properties."""

    def test_attack_categories(self):
        """Test attack action categorization."""
        # Verify all attack actions
        attack_actions = [
            name for name, props in ACTIONS.items()
            if props["category"] == "attack"
        ]
        
        assert "quick_attack" in attack_actions
        assert "heavy_attack" in attack_actions
        
        # Verify non-attack actions
        assert "block" not in attack_actions
        assert "move_forward" not in attack_actions

    def test_attack_requirements(self):
        """Test attack requirements."""
        # Quick attack requirements
        quick = ACTIONS["quick_attack"]
        assert quick["speed_requirement"] > 0.5  # Should require decent speed
        assert quick["stamina_cost"] > 0  # Should cost stamina
        
        # Heavy attack requirements
        heavy = ACTIONS["heavy_attack"]
        assert heavy["speed_requirement"] < quick["speed_requirement"]  # Slower
        assert heavy["stamina_cost"] > quick["stamina_cost"]  # More costly

    def test_attack_properties(self):
        """Test attack-specific properties."""
        # Quick attack properties
        quick = ACTIONS["quick_attack"]["properties"]
        assert quick["damage_multiplier"] < 1.0  # Lower damage
        assert quick["accuracy"] > 0.8  # High accuracy
        
        # Heavy attack properties
        heavy = ACTIONS["heavy_attack"]["properties"]
        assert heavy["damage_multiplier"] > 1.0  # Higher damage
        assert heavy["accuracy"] < quick["accuracy"]  # Lower accuracy

class TestAttackCreation:
    """Test suite for attack action creation."""

    def test_basic_attack_creation(self):
        """Test basic attack creation."""
        # Create quick attack
        quick = create_action(
            "quick_attack",
            "attacker_1",
            "defender_1"
        )
        assert quick.action_type == "quick_attack"
        assert quick.state == ActionStateType.FEINT
        assert quick.visibility == ActionVisibility.TELEGRAPHED
        
        # Create heavy attack
        heavy = create_action(
            "heavy_attack",
            "attacker_1",
            "defender_1"
        )
        assert heavy.action_type == "heavy_attack"
        assert heavy.modifiers["damage_multiplier"] > quick.modifiers["damage_multiplier"]

    def test_attack_variations(self):
        """Test attack variations."""
        # Hidden quick attack
        hidden = create_action(
            "quick_attack",
            "attacker_1",
            "defender_1",
            visibility=ActionVisibility.HIDDEN
        )
        assert hidden.visibility == ActionVisibility.HIDDEN
        assert hidden.modifiers["feint_cost"] > 0
        
        # Committed heavy attack
        committed = create_action(
            "heavy_attack",
            "attacker_1",
            "defender_1",
            commitment=ActionCommitment.FULL
        )
        assert committed.commitment == ActionCommitment.FULL
        assert committed.modifiers["stamina_cost"] > ACTIONS["heavy_attack"]["stamina_cost"]

class TestAttackAvailability:
    """Test suite for attack availability."""

    def test_stamina_requirements(self):
        """Test stamina-based availability."""
        # Full stamina state
        full = create_test_combatant_state(
            "fighter_1",
            stamina=100.0,
            speed=1.0
        )
        actions = get_available_actions(full)
        assert any(a.type == "quick_attack" for a in actions)
        assert any(a.type == "heavy_attack" for a in actions)
        
        # Low stamina state
        low = create_test_combatant_state(
            "fighter_1",
            stamina=10.0,
            speed=1.0
        )
        actions = get_available_actions(low)
        assert any(a.type == "quick_attack" for a in actions)
        assert not any(a.type == "heavy_attack" for a in actions)

    def test_speed_requirements(self):
        """Test speed-based availability."""
        # High speed state
        fast = create_test_combatant_state(
            "fighter_1",
            stamina=100.0,
            speed=1.0
        )
        actions = get_available_actions(fast)
        assert any(a.type == "quick_attack" for a in actions)
        
        # Low speed state
        slow = create_test_combatant_state(
            "fighter_1",
            stamina=100.0,
            speed=0.5
        )
        actions = get_available_actions(slow)
        assert not any(a.type == "quick_attack" for a in actions)
        assert any(a.type == "heavy_attack" for a in actions)

class TestAttackModifiers:
    """Test suite for attack modifiers."""

    def test_commitment_modifiers(self):
        """Test commitment-based modifiers."""
        base = create_action(
            "quick_attack",
            "attacker_1",
            "defender_1"
        )
        
        partial = create_action(
            "quick_attack",
            "attacker_1",
            "defender_1",
            commitment=ActionCommitment.PARTIAL
        )
        assert partial.modifiers["stamina_cost"] > base.modifiers["stamina_cost"]
        
        full = create_action(
            "quick_attack",
            "attacker_1",
            "defender_1",
            commitment=ActionCommitment.FULL
        )
        assert full.modifiers["stamina_cost"] > partial.modifiers["stamina_cost"]

    def test_visibility_modifiers(self):
        """Test visibility-based modifiers."""
        telegraphed = create_action(
            "heavy_attack",
            "attacker_1",
            "defender_1"
        )
        
        hidden = create_action(
            "heavy_attack",
            "attacker_1",
            "defender_1",
            visibility=ActionVisibility.HIDDEN
        )
        assert hidden.modifiers["feint_cost"] > 0
        assert hidden.modifiers["feint_cost"] > telegraphed.modifiers.get("feint_cost", 0)

class TestAttackChaining:
    """Test suite for attack action chaining."""
    
    def test_chain_timing(self):
        """Test timing between chained attacks."""
        # Create a chain with recovery time
        chain = [
            create_action("quick_attack", "fighter_1", "fighter_2"),
            create_action("recover", "fighter_1"),
            create_action("quick_attack", "fighter_1", "fighter_2")
        ]
        assert validate_action_chain(chain)
        
        # Create a chain without recovery time
        chain = [
            create_action("quick_attack", "fighter_1", "fighter_2"),
            create_action("quick_attack", "fighter_1", "fighter_2")
        ]
        assert not validate_action_chain(chain)

    def test_valid_attack_chains(self):
        """Test valid attack combinations."""
        # Attack after movement
        chain = [
            create_action("move_forward", "fighter_1"),
            create_action("quick_attack", "fighter_1", "fighter_2")
        ]
        assert validate_action_chain(chain)
        
        # Attack into movement
        chain = [
            create_action("quick_attack", "fighter_1", "fighter_2"),
            create_action("move_backward", "fighter_1")
        ]
        assert validate_action_chain(chain)

    def test_invalid_attack_chains(self):
        """Test invalid attack combinations."""
        # Double attack
        chain = [
            create_action("quick_attack", "fighter_1", "fighter_2"),
            create_action("heavy_attack", "fighter_1", "fighter_2")
        ]
        assert not validate_action_chain(chain)
        
        # Attack after committed attack
        chain = [
            create_action(
                "heavy_attack",
                "fighter_1",
                "fighter_2",
                commitment=ActionCommitment.FULL
            ),
            create_action("quick_attack", "fighter_1", "fighter_2")
        ]
        assert not validate_action_chain(chain)

class TestIntegration:
    """Integration tests for attack actions."""
    
    def test_complex_attack_sequence(self):
        """Test a complex attack sequence with multiple combatants."""
        fighter_1 = create_test_combatant_state(
            "fighter_1",
            stamina=100.0,
            speed=1.0,
            stealth=1.0
        )
        
        fighter_2 = create_test_combatant_state(
            "fighter_2",
            stamina=100.0,
            speed=0.8,
            stealth=0.5
        )
        
        # Create interleaved sequence
        sequence = [
            # Fighter 1's opening
            create_action(
                "move_forward",
                "fighter_1",
                visibility=ActionVisibility.HIDDEN
            ),
            
            # Fighter 2's response
            create_action(
                "block",
                "fighter_2",
                commitment=ActionCommitment.PARTIAL
            ),
            
            # Fighter 1's feint
            create_action(
                "quick_attack",
                "fighter_1",
                "fighter_2",
                visibility=ActionVisibility.HIDDEN
            ),
            
            # Fighter 2's counter
            create_action(
                "parry",
                "fighter_2",
                commitment=ActionCommitment.PARTIAL
            ),
            
            # Fighter 1's true attack
            create_action(
                "heavy_attack",
                "fighter_1",
                "fighter_2",
                commitment=ActionCommitment.FULL
            )
        ]
        
        # Verify sequence validity
        assert validate_action_chain(sequence[:2])  # First exchange
        assert validate_action_chain(sequence[2:4])  # Second exchange
        assert validate_action_chain(sequence[4:])  # Final attack
        
        # Verify action availability for each fighter
        available_1 = get_available_actions(fighter_1)
        available_2 = get_available_actions(fighter_2)
        
        for action in sequence:
            if action.source_id == "fighter_1":
                assert any(
                    a.type == action.type and
                    a.visibility == action.visibility and
                    a.commitment == action.commitment
                    for a in available_1
                )
            else:
                assert any(
                    a.type == action.type and
                    a.visibility == action.visibility and
                    a.commitment == action.commitment
                    for a in available_2
                )

    def test_realistic_attack_sequence(self):
        """Test a realistic attack sequence."""
        attacker = create_test_combatant_state(
            "attacker",
            stamina=100.0,
            speed=1.0,
            stealth=1.0
        )
        
        # Create an attack sequence
        sequence = [
            # Approach stealthily
            create_action(
                "move_forward",
                "attacker",
                visibility=ActionVisibility.HIDDEN
            ),
            
            # Quick feint
            create_action(
                "quick_attack",
                "attacker",
                "defender",
                visibility=ActionVisibility.HIDDEN,
                commitment=ActionCommitment.NONE
            ),
            
            # Committed heavy attack
            create_action(
                "heavy_attack",
                "attacker",
                "defender",
                commitment=ActionCommitment.FULL
            )
        ]
        
        # Verify sequence validity
        assert validate_action_chain(sequence)
        
        # Verify action availability
        available = get_available_actions(attacker)
        for action in sequence:
            assert any(
                a.type == action.type and
                a.visibility == action.visibility and
                a.commitment == action.commitment
                for a in available
            )
