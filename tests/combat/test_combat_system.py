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
        accuracy=100,
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
        blocking_power=30,
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

def test_determine_next_event_priority(attacker, defender):
    battle = init_battle(attacker, defender, duration=1000, distance=0, max_distance=100)
    
    # Force multiple actions with different priorities
    attacker.force_action("try_attack", 0, battle.event_counter, battle.distance)  # Higher priority
    defender.force_action("move_backward", 0, battle.event_counter, battle.distance)  # Lower priority
    
    # Determine next event
    battle.determine_next_event()
    
    # Check if higher priority action was chosen
    assert battle.next_event["type"] == "try_attack", "Higher priority action should be chosen"
    assert battle.next_event["combatant"] == attacker, "Attacker's action should be chosen"

def test_determine_next_event_timing(attacker, defender):
    battle = init_battle(attacker, defender, duration=1000, distance=0, max_distance=100)
    
    # Force actions with different timings
    attacker.force_action("try_attack", 100, battle.event_counter, battle.distance)  # Later time
    defender.force_action("move_backward", 0, battle.event_counter, battle.distance)  # Earlier time
    
    # Determine next event
    battle.determine_next_event()
    
    # Check if earlier action was chosen
    assert battle.next_event["type"] == "move_backward", "Earlier action should be chosen"
    assert battle.next_event["combatant"] == defender, "Defender's action should be chosen"

def test_process_event(attacker, defender):
    battle = init_battle(attacker, defender, duration=1000, distance=0, max_distance=100)
    
    # Force an action
    attacker.force_action("move_forward", 0, battle.event_counter, battle.distance)
    initial_distance = battle.distance
    
    # Process the event
    battle.determine_next_event()
    battle.update()
    
    # Check if action was processed correctly
    assert battle.distance == initial_distance - attacker.mobility, "Distance should be updated after movement"
    assert len(battle.events) > 0, "Event should be logged"

def test_find_target(attacker, defender):
    battle = init_battle(attacker, defender, duration=1000, distance=0, max_distance=100)
    
    # Test normal target finding
    target = battle.find_target(attacker)
    assert target == defender, "Should find defender as target"
    
    # Test when target is defeated
    defender.health = 0
    target = battle.find_target(attacker)
    assert target is None, "Should not find defeated target"

def test_battle_duration(attacker, defender):
    battle = init_battle(attacker, defender, duration=1000, distance=0, max_distance=100)
    
    # Force actions until duration is exceeded
    while not battle.is_battle_over():
        attacker.force_action("idle", battle.timer, battle.event_counter, battle.distance)
        defender.force_action("idle", battle.timer, battle.event_counter, battle.distance)
        battle.determine_next_event()
        battle.update()
    
    assert battle.timer >= battle.duration, "Battle should end when duration is exceeded"

def test_battle_victory_conditions(attacker, defender):
    battle = init_battle(attacker, defender, duration=1000, distance=0, max_distance=100)
    
    # Test victory by defeat
    defender.health = 0
    assert battle.is_battle_over(), "Battle should end when a combatant is defeated"
    
    # Test both defeated
    attacker.health = 0
    assert battle.is_battle_over(), "Battle should end when both combatants are defeated"

def test_battle_log(attacker, defender):
    battle = init_battle(attacker, defender, duration=1000, distance=0, max_distance=100)
    
    # Force an action
    attacker.force_action("try_attack", 0, battle.event_counter, battle.distance)
    
    # Process actions
    battle.determine_next_event()
    battle.update()
    
    # Check log entries
    assert len(battle.events) > 0, "Events should be logged"
    log_entry = battle.events[0]
    assert "timestamp" in log_entry, "Log should include timestamp"
    assert "combatant" in log_entry, "Log should include combatant info"
    assert "action" in log_entry, "Log should include action info"
    assert "status" in log_entry, "Log should include status"

def test_opponent_perception_update(attacker, defender):
    battle = init_battle(attacker, defender, duration=1000, distance=0, max_distance=100)
    
    # Force an action for attacker
    action = attacker.force_action("try_attack", 0, battle.event_counter, battle.distance)
    
    # Update opponent perception
    battle.update_opponent_perception(attacker)
    
    # Check if defender's perception of attacker is updated
    assert defender.opponent.action == action, "Defender should be aware of attacker's action"

def test_invalid_actions(attacker, defender):
    battle = init_battle(attacker, defender, duration=1000, distance=0, max_distance=100)
    
    # Test with no actions
    with pytest.raises(ValueError):
        battle.determine_next_event()
    
    # Test with invalid action type
    with pytest.raises(AttributeError):
        attacker.force_action("invalid_action", 0, battle.event_counter, battle.distance)
        battle.determine_next_event()
        battle.update()

def test_simultaneous_actions(attacker, defender):
    battle = init_battle(attacker, defender, duration=1000, distance=0, max_distance=100)
    
    # Force simultaneous actions
    attacker.force_action("try_attack", 0, battle.event_counter, battle.distance)
    defender.force_action("try_block", 0, battle.event_counter, battle.distance)
    
    # Process first action
    battle.determine_next_event()
    battle.update()
    
    # Check if actions were processed in correct order based on priority
    first_event = battle.events[0]
    assert first_event["action"] in ["try_attack", "try_block"], "First action should be either attack or block"
    
    # Process second action
    battle.determine_next_event()
    battle.update()
    
    # Check if both actions were processed
    assert len(battle.events) >= 2, "Both actions should be processed"

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
