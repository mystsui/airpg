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

def test_try_block(attacker, defender):
    battle = init_battle(attacker, defender, duration=1000, distance=0, max_distance=100)
    
    # Get initial stamina
    initial_stamina = defender.stamina
    
    # Force try_block action
    defender.force_action("try_block", 0, battle.event_counter, battle.distance)
    
    # Check stamina cost
    assert defender.stamina == initial_stamina - ACTIONS["try_block"]["stamina_cost"], "Stamina should decrease by try_block cost"
    
    # Process action
    process_action(battle)
    
    # Check timer after try_block
    assert battle.timer == ACTIONS["try_block"]["time"], "Timer should be try_block duration"
    
    # Check if defender is now in blocking state
    assert defender.action["status"] == "pending", "Action status should be pending"
    assert defender.action["type"] == "blocking", "Action should be blocking"

def test_blocking(attacker, defender):
    battle = init_battle(attacker, defender, duration=1000, distance=0, max_distance=100)
    
    # Force blocking action
    defender.force_action("blocking", 0, battle.event_counter, battle.distance)
    
    # Get initial stamina
    initial_stamina = defender.stamina
    
    # Process action
    process_action(battle)
    
    # Check timer after blocking
    assert battle.timer == ACTIONS["blocking"]["time"], "Timer should be blocking duration"
    
    # Check stamina cost
    assert defender.stamina == initial_stamina - ACTIONS["blocking"]["stamina_cost"], "Stamina should decrease by blocking cost"
    
    # Check if defender decided to keep blocking or stop
    assert defender.action["status"] == "pending", "Action status should be pending"
    assert defender.action["type"] in ["keep_blocking", "idle"], "Action should be keep_blocking or idle"

def test_keep_blocking(attacker, defender):
    battle = init_battle(attacker, defender, duration=1000, distance=0, max_distance=100)
    
    # Force keep_blocking action
    defender.force_action("keep_blocking", 0, battle.event_counter, battle.distance)
    
    # Get initial stamina
    initial_stamina = defender.stamina
    
    # Process action
    process_action(battle)
    
    # Check timer after keep_blocking
    assert battle.timer == ACTIONS["keep_blocking"]["time"], "Timer should be keep_blocking duration"
    
    # Check stamina cost
    assert defender.stamina == initial_stamina - ACTIONS["keep_blocking"]["stamina_cost"], "Stamina should decrease by keep_blocking cost"
    
    # Check if defender is back in blocking state
    assert defender.action["status"] == "pending", "Action status should be pending"
    assert defender.action["type"] == "blocking", "Action should be blocking"

def test_block_damage_calculation(attacker, defender):
    battle = init_battle(attacker, defender, duration=1000, distance=0, max_distance=100)
    
    # Force defender to block
    defender.force_action("blocking", 0, battle.event_counter, battle.distance)
    
    # Get initial health and blocking power
    initial_health = defender.health
    initial_blocking_power = defender.blocking_power
    
    # Force attacker to attack
    attacker.force_action("try_attack", 0, battle.event_counter, battle.distance)
    
    # Process try_attack
    process_action(battle)
    
    # Process release_attack
    process_action(battle)
    
    # Check if attack was blocked
    assert defender.blocking_power < initial_blocking_power, "Blocking power should decrease"
    assert defender.health == initial_health, "Health should not change if block was successful"

def test_block_breach(attacker, defender):
    battle = init_battle(attacker, defender, duration=1000, distance=0, max_distance=100)
    
    # Set attacker's power higher than defender's blocking power
    attacker.attack_power = 40  # Higher than defender's blocking_power of 30
    
    # Force defender to block
    defender.force_action("blocking", 0, battle.event_counter, battle.distance)
    
    # Get initial health and blocking power
    initial_health = defender.health
    initial_blocking_power = defender.blocking_power
    
    # Force attacker to attack
    attacker.force_action("try_attack", 0, battle.event_counter, battle.distance)
    
    # Process try_attack
    process_action(battle)
    
    # Process release_attack
    process_action(battle)
    
    # Check if block was breached
    assert defender.blocking_power < initial_blocking_power, "Blocking power should decrease"
    assert defender.health < initial_health, "Health should decrease when block is breached"
    assert defender.health == initial_health - (40 - initial_blocking_power), "Damage should be attack_power minus blocking_power"

def test_block_stamina_depletion(attacker, defender):
    battle = init_battle(attacker, defender, duration=1000, distance=0, max_distance=100)
    
    # Set defender's stamina low
    defender.stamina = ACTIONS["try_block"]["stamina_cost"]
    
    # Force try_block action
    defender.force_action("try_block", 0, battle.event_counter, battle.distance)
    
    # Process try_block
    process_action(battle)
    
    # Force keep_blocking but with no stamina
    defender.stamina = 0
    defender.force_action("keep_blocking", battle.timer, battle.event_counter, battle.distance)
    
    # Process keep_blocking
    process_action(battle)
    
    # Check if defender was forced to stop blocking due to stamina depletion
    assert defender.action["type"] == "idle", "Should switch to idle when out of stamina"

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
