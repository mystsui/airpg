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
        stamina_recovery=10,
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
        stamina_recovery=10,
        position="right",
        facing="left",
        perception=0,
        stealth=0
    )

def test_no_actions(attacker, defender):
    battle = init_battle(attacker, defender, duration=1000, distance=0, max_distance=100)
    with pytest.raises(ValueError):
        process_action(battle)

def test_idle(attacker, defender):
    battle = init_battle(attacker, defender, duration=1000, distance=0, max_distance=100)
    attacker.force_action("idle", 0, battle.event_counter, battle.distance)
    process_action(battle)

    # Check timer after idle action
    assert battle.timer == 100, "Timer should be 100"

    # Check if the combatant has already decided on the next action
    assert attacker.action["status"] == "pending", "Action status should be pending"

def test_reset(attacker, defender):
    battle = init_battle(attacker, defender, duration=1000, distance=0, max_distance=100)
    attacker.force_action("reset", 0, battle.event_counter, battle.distance)
    process_action(battle)

    # Check timer after reset action
    assert battle.timer == 1000, "Timer should be 1000"

    # Check if the combatant has already decided on the next action
    assert attacker.action["status"] == "pending", "Action status should be pending"

def test_recover(attacker, defender):
    battle = init_battle(attacker, defender, duration=1000, distance=0, max_distance=100)
    
    print(f"\nInitial stamina: {attacker.stamina}")
    
    attacker.stamina = 50
    print(f"Reduced stamina: {attacker.stamina}")
    
    attacker.force_action("recover", 0, battle.event_counter, battle.distance)
    print(f"Before process_action stamina: {attacker.stamina}")
    
    process_action(battle)
    print(f"After process_action stamina: {attacker.stamina}")
    
    # Add assertions
    assert attacker.stamina == 60, f"Expected 60 stamina but got {attacker.stamina}"


    # Check timer after recover action
    assert battle.timer == 2000, "Timer should be 2000"

    # Check if the combatant has already decided on the next action
    assert attacker.action["status"] == "pending", "Action status should be pending"  
    
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
