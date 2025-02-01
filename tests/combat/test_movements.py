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

def test_move_forward(attacker, defender):
    battle = init_battle(attacker, defender, duration=10000, distance=100, max_distance=1200)
    last_known_distance = battle.distance
    
    # Force move forward action
    attacker.force_action("move_forward", 0, battle.event_counter, battle.distance)
    process_action(battle)

    # Check distance increased/reduced by mobility
    assert battle.distance == last_known_distance - attacker.mobility, "Distance should decrease by attacker mobility"

def test_move_backward(attacker, defender):
    battle = init_battle(attacker, defender, duration=10000, distance=100, max_distance=1200)
    last_known_distance = battle.distance
        
    # Force move backward action
    attacker.force_action("move_backward", 0, battle.event_counter, battle.distance)
    process_action(battle)

    # Check distance increased/reduced by mobility
    assert battle.distance == last_known_distance + attacker.mobility, "Distance should increase by attacker mobility"

def test_move_forward_max(attacker, defender):
    # Initialize battle with distance set to only 10 units.
    battle = init_battle(attacker, defender, duration=10000, distance=10, max_distance=1200) 
    
    # Force move forward action
    attacker.force_action("move_forward", 0, battle.event_counter, battle.distance)
    process_action(battle)

    # Check distance increased/reduced by mobility
    # Attacker's mobility is greater than the distance, so it should be reduced to 0.
    assert battle.distance == 0, "Distance should decrease by attacker mobility but not go below 0"

def test_move_backward_max(attacker, defender):
    # Initialize battle with distance set to the maximum of 1,200 units.
    battle = init_battle(attacker, defender, duration=10000, distance=1200, max_distance=1200) 
    
    # Force move backward action
    attacker.force_action("move_backward", 0, battle.event_counter, battle.distance)
    process_action(battle)

    # Check distance increased/reduced by mobility
    # Attacker's mobility is greater than the max_distance - last_known_distance, so it should be capped at 1,200.
    assert battle.distance == 1200, "Distance should increase by attacker mobility but not go above 1,200"

    
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
