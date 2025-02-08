# test_combat.py
import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from combat.combat_system import CombatSystem
from combat.combatant import TestCombatant
from combat.lib.actions_library import ACTIONS

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
        blocking_power=0,
        evading_ability=80,  # High evading ability
        mobility=50,
        range_a=0,
        range_b=50,
        stamina_recovery=10,
        position="right",
        facing="left",
        perception=0,
        stealth=0
    )

def test_try_evade(attacker, defender):
    battle = init_battle(attacker, defender, duration=1000, distance=0, max_distance=100)
    
    # Get initial stamina
    initial_stamina = defender.stamina
    
    # Force try_evade action
    defender.force_action("try_evade", 0, battle.event_counter, battle.distance)
    
    # Check stamina cost
    assert defender.stamina == initial_stamina - ACTIONS["try_evade"]["stamina_cost"], "Stamina should decrease by try_evade cost"
    
    # Process action
    process_action(battle)
    
    # Check timer after try_evade
    assert battle.timer == ACTIONS["try_evade"]["time"], "Timer should be try_evade duration"
    
    # Check if defender is now in evading state
    assert defender.action["status"] == "pending", "Action status should be pending"
    assert defender.action["type"] == "evading", "Action should be evading"

def test_evading(attacker, defender):
    battle = init_battle(attacker, defender, duration=1000, distance=0, max_distance=100)
    
    # Force evading action
    defender.force_action("evading", 0, battle.event_counter, battle.distance)
    
    # Get initial stamina
    initial_stamina = defender.stamina
    
    # Process action
    process_action(battle)
    
    # Check timer after evading
    assert battle.timer == ACTIONS["evading"]["time"], "Timer should be evading duration"
    
    # Check stamina cost
    assert defender.stamina == initial_stamina - ACTIONS["evading"]["stamina_cost"], "Stamina should decrease by evading cost"
    
    # Check if defender transitions to idle after evading
    assert defender.action["status"] == "pending", "Action status should be pending"
    assert defender.action["type"] == "idle", "Action should be idle"

def test_successful_evasion(attacker, defender):
    battle = init_battle(attacker, defender, duration=1000, distance=0, max_distance=100)
    
    # Force defender to evade
    defender.force_action("evading", 0, battle.event_counter, battle.distance)
    
    # Get initial health
    initial_health = defender.health
    
    # Force attacker to attack
    attacker.force_action("try_attack", 0, battle.event_counter, battle.distance)
    
    # Process try_attack
    process_action(battle)
    
    # Process release_attack
    process_action(battle)
    
    # Check if attack was evaded
    assert defender.health == initial_health, "Health should not change if attack was evaded"
    assert defender.action["type"] == "reset", "Defender should reset after successful evasion"
    assert attacker.action["type"] == "off_balance", "Attacker should be off balance after evaded attack"

def test_evade_stamina_depletion(attacker, defender):
    battle = init_battle(attacker, defender, duration=1000, distance=0, max_distance=100)
    
    # Set defender's stamina to exactly the cost of try_evade
    defender.stamina = ACTIONS["try_evade"]["stamina_cost"]
    
    # Force try_evade action
    defender.force_action("try_evade", 0, battle.event_counter, battle.distance)
    
    # Process try_evade
    process_action(battle)
    
    # Check if defender can still evade with no stamina
    assert defender.stamina == 0, "Stamina should be depleted"
    assert defender.action["type"] == "evading", "Should still transition to evading"
    
    # Process evading
    process_action(battle)
    
    # Check if defender was forced to stop evading due to stamina depletion
    assert defender.action["type"] == "idle", "Should switch to idle when out of stamina"

def test_multiple_evasions(attacker, defender):
    battle = init_battle(attacker, defender, duration=1000, distance=0, max_distance=100)
    
    # First evasion
    defender.force_action("try_evade", 0, battle.event_counter, battle.distance)
    process_action(battle)  # Process try_evade
    process_action(battle)  # Process evading
    
    # Second evasion attempt immediately after
    defender.force_action("try_evade", battle.timer, battle.event_counter, battle.distance)
    process_action(battle)
    
    # Check if second evasion works normally
    assert defender.action["type"] == "evading", "Should be able to evade multiple times"

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
