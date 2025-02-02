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
    assert battle.timer == 10, "Timer should be 10"

    # Check if the combatant has already decided on the next action
    assert attacker.action["status"] == "pending", "Action status should be pending"
    assert attacker.action["type"] != "idle", "Action type should not be idle"

def test_reset(attacker, defender):
    battle = init_battle(attacker, defender, duration=1000, distance=0, max_distance=100)
    attacker.force_action("reset", 0, battle.event_counter, battle.distance)
    process_action(battle)

    # Check timer after reset action
    assert battle.timer == 1000, "Timer should be 1000"

    # Check if the combatant has already decided on the next action
    assert attacker.action["status"] == "pending", "Action status should be pending"
    assert attacker.action["type"] == "idle", "Action type should be idle"

def test_recover(attacker, defender):
    battle = init_battle(attacker, defender, duration=1000, distance=0, max_distance=100)
    
    # Set max stamina to 100
    attacker.max_stamina = 100
    
    # Reduce stamina to 50    
    attacker.stamina = 50
    
    # Force recover action
    attacker.force_action("recover", 0, battle.event_counter, battle.distance)    
    process_action(battle)
            
    # Check stamina after recover action should be higher than before
    assert attacker.stamina > 50, "Stamina should be higher than 50"

    # Check accuracy of stamina recovered
    assert attacker.stamina == 60, "Stamina should be 60"

    # Check timer after recover action
    assert battle.timer == 2000, "Timer should be 2000"

    # Check if the combatant has already decided on the next action
    assert attacker.action["status"] == "pending", "Action status should be pending"
    assert attacker.action["type"] == "idle", "Action type should be idle"
    
    # Set stamina to almost full
    attacker.stamina = attacker.max_stamina - 1  
    
    # Force recover action
    attacker.force_action("recover", battle.timer, battle.event_counter, battle.distance)
    process_action(battle)
    
    # Check stamina after recover action should be higher than before but not more than max stamina
    assert attacker.stamina > attacker.max_stamina - 1 <= attacker.max_stamina, "Stamina should be higher than 99 but not more than 100"
    
    # Check accuracy of stamina recovered
    assert attacker.stamina == 100, "Stamina should be 100"
    
    # Check timer after recover action
    assert battle.timer == 4000, "Timer should be 2000"
    
    # Check if the combatant has already decided on the next action
    assert attacker.action["status"] == "pending", "Action status should be pending"
    assert attacker.action["type"] == "idle", "Action type should be idle"
    
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
