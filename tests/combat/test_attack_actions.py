# test_combat.py
import pytest
import random
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
    
def test_attack_hit(attacker, defender):
    print("\nTesting attack hit...")
    battle = init_battle(attacker, defender, duration=1000, distance=0, max_distance=100)
    
    # Force try_attack action
    attacker.force_action("try_attack", 0, battle.event_counter, battle.distance)
    print(f"Attacker action after force: {attacker.action}")

    # Force defender to do recovery action
    defender.force_action("recover", 0, battle.event_counter, battle.distance)
    print(f"Defender action after force: {defender.action}")

    # Check stamina cost
    print(f"Attacker stamina before: {attacker.stamina}, cost: {ACTIONS['try_attack']['stamina_cost']}")
    assert attacker.stamina == attacker.max_stamina - ACTIONS["try_attack"]["stamina_cost"], "Stamina should decrease by the try_attack stamina cost"

    # Get attacker stamina before releasing/stopping the attack
    attacker_stamina_before_deciding = attacker.stamina

    # Process try_attack
    process_action(battle)
    print(f"Timer after try_attack: {battle.timer}")
    print(f"Attacker action after try_attack: {attacker.action}")
    assert battle.timer == ACTIONS["try_attack"]["time"], "Timer should be try_attack duration"

    # Process release_attack
    process_action(battle)
    print(f"Timer after release_attack: {battle.timer}")
    print(f"Attacker action after release_attack: {attacker.action}")
    assert battle.timer == ACTIONS["try_attack"]["time"] + ACTIONS["release_attack"]["time"], "Timer should include both actions"

    # Check damage calculation
    expected_damage = random.randint(attacker.attack_power * attacker.accuracy // 100, attacker.attack_power)
    print(f"Expected damage: {expected_damage}, Defender health: {defender.health}")
    assert defender.health == defender.max_health - expected_damage, "Defender health should decrease by attack damage"

    # Check final states
    print(f"Final attacker action: {attacker.action}")
    print(f"Final defender action: {defender.action}")
    assert attacker.action["type"] == "reset", "Attacker should reset after hit"
    assert defender.action["type"] == "reset", "Defender should reset after being hit"

def test_attack_miss(attacker, defender):
    print("\nTesting attack miss...")
    # Set distance beyond attack range
    battle = init_battle(attacker, defender, duration=1000, distance=100, max_distance=200)
    
    # Force try_attack action
    attacker.force_action("try_attack", 0, battle.event_counter, battle.distance)
    initial_health = defender.health
    print(f"Initial defender health: {initial_health}")
    
    # Process try_attack and release_attack
    process_action(battle)
    print(f"Action after try_attack: {attacker.action}")
    process_action(battle)
    print(f"Action after release_attack: {attacker.action}")
    print(f"Final defender health: {defender.health}")
    
    # Check miss results
    assert defender.health == initial_health, "No damage should be dealt on miss"
    assert attacker.action["type"] == "off_balance", "Attacker should be off balance after miss"

def test_attack_blocked(attacker, defender):
    print("\nTesting attack blocked...")
    battle = init_battle(attacker, defender, duration=1000, distance=0, max_distance=100)
    
    # Force defender to block
    defender.force_action("blocking", 0, battle.event_counter, battle.distance)
    process_action(battle)
    print(f"Defender action after blocking: {defender.action}")
    
    # Store initial values
    initial_health = defender.health
    initial_blocking = defender.blocking_power
    print(f"Initial blocking power: {initial_blocking}")
    
    # Force attack
    attacker.force_action("try_attack", battle.timer, battle.event_counter, battle.distance)
    process_action(battle)
    print(f"Action after try_attack: {attacker.action}")
    process_action(battle)
    print(f"Action after release_attack: {attacker.action}")
    print(f"Final blocking power: {defender.blocking_power}")
    
    # Check block results
    assert defender.health == initial_health, "No damage should be dealt if blocked"
    assert defender.blocking_power < initial_blocking, "Blocking power should decrease"
    assert attacker.action["type"] == "off_balance", "Attacker should be off balance after blocked attack"

def test_attack_evaded(attacker, defender):
    print("\nTesting attack evaded...")
    battle = init_battle(attacker, defender, duration=1000, distance=0, max_distance=100)
    
    # Force defender to evade
    defender.force_action("evading", 0, battle.event_counter, battle.distance)
    process_action(battle)
    print(f"Defender action after evading: {defender.action}")
    
    # Store initial health
    initial_health = defender.health
    print(f"Initial defender health: {initial_health}")
    
    # Force attack
    attacker.force_action("try_attack", battle.timer, battle.event_counter, battle.distance)
    process_action(battle)
    print(f"Action after try_attack: {attacker.action}")
    process_action(battle)
    print(f"Action after release_attack: {attacker.action}")
    print(f"Final defender health: {defender.health}")
    
    # Check evasion results
    assert defender.health == initial_health, "No damage should be dealt if evaded"
    assert attacker.action["type"] == "off_balance", "Attacker should be off balance after evaded attack"
    assert defender.action["type"] == "reset", "Defender should reset after successful evasion"

def test_attack_stamina_chain(attacker, defender):
    print("\nTesting attack stamina chain...")
    battle = init_battle(attacker, defender, duration=1000, distance=0, max_distance=100)
    
    # Set attacker's stamina to exactly enough for try_attack
    attacker.stamina = ACTIONS["try_attack"]["stamina_cost"]
    print(f"Initial stamina: {attacker.stamina}")
    
    # Force try_attack
    attacker.force_action("try_attack", 0, battle.event_counter, battle.distance)
    process_action(battle)
    print(f"Stamina after try_attack: {attacker.stamina}")
    
    # Verify stamina consumption
    assert attacker.stamina == 0, "Stamina should be depleted after try_attack"
    
    # Process release_attack
    process_action(battle)
    print(f"Final action: {attacker.action}")
    
    # Check if attack chain completed despite no stamina
    assert attacker.action["type"] == "reset", "Attack chain should complete even with no stamina"

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
