"""
Tests for the StateManagerAdapter class.

These tests verify that the adapter correctly implements the IStateManager interface
and maintains proper state management with validation rules.
"""

import pytest
from combat.adapters import StateManagerAdapter
from combat.interfaces import CombatantState, Action
from combat.lib.actions_library import ACTIONS
from tests.combat.test_combatant_adapter import create_test_combatant

class TestStateManagerAdapter:
    """Test suite for StateManagerAdapter class."""

    @pytest.fixture
    def manager(self):
        """Create a fresh state manager instance for each test."""
        return StateManagerAdapter()

    @pytest.fixture
    def base_state(self):
        """Create a base combatant state for testing."""
        return CombatantState(
            entity_id="test_1",
            stamina=100,
            speed=1.0,
            stealth=1.0,
            position_x=0.0,
            position_y=0.0,
            stats={
                "health": 100,
                "max_health": 100,
                "max_stamina": 100,
                "blocking_power": 30,
                "team": "challenger",
                "facing": "right"
            }
        )

    def test_get_state_nonexistent(self, manager):
        """Test getting state for nonexistent entity."""
        assert manager.get_state("nonexistent") is None

    def test_initial_state_update(self, manager, base_state):
        """Test initial state update."""
        manager.update_state(base_state.entity_id, base_state)
        stored_state = manager.get_state(base_state.entity_id)
        assert stored_state == base_state

    def test_valid_health_transition(self, manager, base_state):
        """Test valid health reduction."""
        manager.update_state(base_state.entity_id, base_state)
        
        # Valid health reduction
        new_state = CombatantState(
            **{**base_state.__dict__, 
               "stats": {**base_state.stats, "health": 80}
            }
        )
        manager.update_state(base_state.entity_id, new_state)
        assert manager.get_state(base_state.entity_id).health == 80

    def test_invalid_health_increase(self, manager, base_state):
        """Test invalid health increase without recovery action."""
        manager.update_state(base_state.entity_id, base_state)
        
        # Health increase without recovery action
        new_state = CombatantState(
            **{**base_state.__dict__,
               "stats": {**base_state.stats, "health": 120}
            }
        )
        with pytest.raises(Exception):
            manager.update_state(base_state.entity_id, new_state)

    def test_valid_stamina_recovery(self, manager, base_state):
        """Test valid stamina recovery."""
        # Set initial low stamina
        initial_state = CombatantState(
            **{**base_state.__dict__, 
               "stamina": 50,
               "stats": {**base_state.stats}
            }
        )
        manager.update_state(base_state.entity_id, initial_state)
        
        # Valid recovery action
        recovery_state = CombatantState(
            **{**initial_state.__dict__,
               "stamina": 60,
               "stats": {
                   **initial_state.stats,
                   "current_action": {"type": "recover", "time": 100}
               }
            }
        )
        manager.update_state(base_state.entity_id, recovery_state)
        assert manager.get_state(base_state.entity_id).stamina == 60

    def test_attack_transition_rules(self, manager, base_state):
        """Test attack transition validation rules."""
        manager.update_state(base_state.entity_id, base_state)
        
        # Can't attack while already attacking
        attacking_state = CombatantState(
            **{**base_state.__dict__,
               "stats": {
                   **base_state.stats,
                   "current_action": {"type": "try_attack", "time": 100}
               }
            }
        )
        manager.update_state(base_state.entity_id, attacking_state)
        
        # Attempt another attack
        with pytest.raises(Exception):
            new_attack_state = CombatantState(
                **{**attacking_state.__dict__,
                   "stats": {
                       **attacking_state.stats,
                       "current_action": {"type": "try_attack", "time": 200}
                   }
                }
            )
            manager.update_state(base_state.entity_id, new_attack_state)

    def test_block_transition_rules(self, manager, base_state):
        """Test blocking transition validation rules."""
        manager.update_state(base_state.entity_id, base_state)
        
        # Can't block with insufficient stamina
        low_stamina_state = CombatantState(
            **{**base_state.__dict__, 
               "stamina": 0,
               "stats": {**base_state.stats}
            }
        )
        manager.update_state(base_state.entity_id, low_stamina_state)
        
        with pytest.raises(Exception):
            blocking_state = CombatantState(
                **{**low_stamina_state.__dict__,
                   "stats": {
                       **low_stamina_state.stats,
                       "current_action": {"type": "blocking", "time": 100}
                   }
                }
            )
            manager.update_state(base_state.entity_id, blocking_state)

    def test_movement_transition_rules(self, manager, base_state):
        """Test movement transition validation rules."""
        manager.update_state(base_state.entity_id, base_state)
        
        # Can't move while blocking
        blocking_state = CombatantState(
            **{**base_state.__dict__,
               "stats": {
                   **base_state.stats,
                   "current_action": {"type": "blocking", "time": 100}
               }
            }
        )
        manager.update_state(base_state.entity_id, blocking_state)
        
        with pytest.raises(Exception):
            movement_state = CombatantState(
                **{**blocking_state.__dict__,
                   "stats": {
                       **blocking_state.stats,
                       "current_action": {"type": "move_forward", "time": 200}
                   }
                }
            )
            manager.update_state(base_state.entity_id, movement_state)

    def test_state_history(self, manager, base_state):
        """Test state history tracking."""
        manager.update_state(base_state.entity_id, base_state)
        
        # Create a series of states
        states = []
        current_health = 100
        for i in range(5):
            current_health -= 20
            state = CombatantState(
                **{**base_state.__dict__,
                   "stats": {**base_state.stats, "health": current_health}
                }
            )
            states.append(state)
            manager.update_state(base_state.entity_id, state)
            
        # Check history
        history = manager.get_state_history(base_state.entity_id)
        assert len(history) == 5
        assert history[0].health == 100  # Original state
        assert history[-1].health == 40  # Second to last state

    def test_state_rollback(self, manager, base_state):
        """Test state rollback functionality."""
        manager.update_state(base_state.entity_id, base_state)
        
        # Create a new state
        new_state = CombatantState(
            **{**base_state.__dict__,
               "stats": {**base_state.stats, "health": 80}
            }
        )
        manager.update_state(base_state.entity_id, new_state)
        
        # Rollback
        assert manager.rollback_state(base_state.entity_id)
        current_state = manager.get_state(base_state.entity_id)
        assert current_state.health == 100

    def test_clear_history(self, manager, base_state):
        """Test history clearing."""
        manager.update_state(base_state.entity_id, base_state)
        
        # Create some history
        for health in [80, 60, 40]:
            state = CombatantState(
                **{**base_state.__dict__,
                   "stats": {**base_state.stats, "health": health}
                }
            )
            manager.update_state(base_state.entity_id, state)
            
        # Clear history
        manager.clear_history(base_state.entity_id)
        assert len(manager.get_state_history(base_state.entity_id)) == 0

    def test_multiple_entities(self, manager, base_state):
        """Test managing multiple entities."""
        # Create two entities
        entity1_id = "entity1"
        entity2_id = "entity2"
        
        state1 = CombatantState(
            **{**base_state.__dict__,
               "entity_id": entity1_id,
               "stats": {**base_state.stats}
            }
        )
        state2 = CombatantState(
            **{**base_state.__dict__,
               "entity_id": entity2_id,
               "stats": {**base_state.stats}
            }
        )
        
        # Update both entities
        manager.update_state(entity1_id, state1)
        manager.update_state(entity2_id, state2)
        
        # Modify one entity
        new_state1 = CombatantState(
            **{**state1.__dict__,
               "stats": {**state1.stats, "health": 80}
            }
        )
        manager.update_state(entity1_id, new_state1)
        
        # Check states are independent
        assert manager.get_state(entity1_id).health == 80
        assert manager.get_state(entity2_id).health == 100
