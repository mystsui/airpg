# test_combat.py
import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from combat.combat_system import CombatSystem
from combat.combatant import TestCombatant

@pytest.fixture
def attacker():
    return TestCombatant(
        combatant_id=1,
        name="Attacker",
        health=100,
        stamina=100,
        attack_power=20,
        accuracy=100,  # Guarantee hits
        blocking_power=0,
        evading_ability=0,
        mobility=50,
        range_a=0,
        range_b=50,
        stamina_recovery=0,
        position="left",
        facing="right",
        perception=0,
        stealth=0
    )

@pytest.fixture
def defender():
    return TestCombatant(
        combatant_id=2,
        name="Defender",
        health=100,
        stamina=100,
        attack_power=0,
        accuracy=0,
        blocking_power=30,  # Initial blocking power
        evading_ability=0,
        mobility=50,
        range_a=0,
        range_b=50,
        stamina_recovery=0,
        position="right",
        facing="left",
        perception=0,
        stealth=0
    )

def test_battle_initialization(attacker, defender):
    # Test basic initialization
    battle = init_battle(attacker, defender, duration=10000, distance=100, max_distance=1200)
    assert battle.duration == 10000, "Battle duration should be 10000"
    assert battle.distance == 100, "Initial distance should be 100"
    assert battle.max_distance == 1200, "Max distance should be 1200"
    
    # Test combatants added correctly
    assert len(battle.combatants) == 2, "Battle should have 2 combatants"
    assert battle.combatants[0] == attacker, "First combatant should be attacker"
    assert battle.combatants[1] == defender, "Second combatant should be defender"
    
    # Test opponent data setup
    assert attacker.opponent == defender, "Attacker's opponent should be defender"
    assert defender.opponent == attacker, "Defender's opponent should be attacker"
    
    # Test initial positions
    assert attacker.position == "left", "Attacker should be on left"
    assert defender.position == "right", "Defender should be on right"
    
    # Test initial battle state
    assert battle.event_counter == 0, "Event counter should start at 0"
    assert not battle.is_battle_over(), "Battle should not be over initially"

def test_battle_initialization_errors(attacker, defender):
    # Test invalid combatant addition
    battle = init_battle(attacker, defender, duration=10000, distance=100, max_distance=1200) 
    with pytest.raises(ValueError):
        battle.add_combatant(None)
    
    # Test duplicate combatant addition
    with pytest.raises(ValueError):
        battle = init_battle(attacker, attacker, duration=10000, distance=100, max_distance=1200) 

    # Test more than 2 combatants added
    with pytest.raises(ValueError):
        battle = init_battle(attacker, defender, duration=10000, distance=100, max_distance=1200)
        battle.add_combatant(attacker)

def test_initial_event_queue(attacker, defender):
    """Test event queue initialization"""
    battle = init_battle(attacker, defender, duration=1000, distance=100, max_distance=1200)
    assert len(battle.events) == 0, "Event queue should start empty"
    assert battle.next_event is None, "No initial event should be scheduled"

def test_battle_state_initialization(attacker, defender):
    """Test initial battle state flags and counters"""
    battle = init_battle(attacker, defender, duration=1000, distance=100, max_distance=1200)
    assert battle.timer == 0, "Timer should start at 0"
    assert not hasattr(battle, 'is_finished'), "Battle should not be marked as finished"
    assert attacker.action is None, "Combatant should have no initial action"
    assert defender.action is None, "Combatant should have no initial action"
    
# Helpers    
def init_battle(attacker, defender, duration, distance, max_distance):
    battle = CombatSystem(duration=duration, distance=distance, max_distance=max_distance)
    battle.add_combatant(attacker)
    battle.add_combatant(defender)
    battle.get_opponent_data(attacker, defender)
    battle.get_opponent_data(defender, attacker)
    return battle

def process_action(battle):
    battle.determine_next_event()
    battle.update()