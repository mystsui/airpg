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

def test_message_for_completed_event(attacker, defender):
    battle = init_battle(attacker, defender, duration=1000, distance=0, max_distance=100)
    
    # Test attack hit message
    attacker.force_action("release_attack", 0, battle.event_counter, battle.distance)
    process_action(battle)
    log = battle.events[-1]
    message = battle.message_for_completed_event(log)
    assert "attacked" in message and "damage" in message, "Attack hit message should include damage dealt"
    
    # Test movement message
    attacker.force_action("move_forward", battle.timer, battle.event_counter, battle.distance)
    process_action(battle)
    log = battle.events[-1]
    message = battle.message_for_completed_event(log)
    assert "moved forward" in message and str(battle.distance) in message, "Movement message should include distance"
    
    # Test recovery message
    attacker.force_action("recover", battle.timer, battle.event_counter, battle.distance)
    process_action(battle)
    log = battle.events[-1]
    message = battle.message_for_completed_event(log)
    assert "recovered stamina" in message and str(attacker.stamina) in message, "Recovery message should include stamina"

def test_message_for_pending_event(attacker, defender):
    battle = init_battle(attacker, defender, duration=1000, distance=0, max_distance=100)
    
    # Test try_attack pending message
    attacker.force_action("try_attack", 0, battle.event_counter, battle.distance)
    log = {
        "timestamp": 0,
        "combatant": {"name": attacker.name},
        "action": "try_attack",
        "timeend": ACTIONS["try_attack"]["time"],
        "status": "pending"
    }
    message = battle.message_for_pending_event(log)
    assert "attempting an attack" in message and str(ACTIONS["try_attack"]["time"]) in message, "Pending attack message should include timing"
    
    # Test movement pending message
    log = {
        "timestamp": 0,
        "combatant": {"name": attacker.name},
        "action": "move_forward",
        "timeend": ACTIONS["move_forward"]["time"],
        "status": "pending"
    }
    message = battle.message_for_pending_event(log)
    assert "attempting to move forward" in message and str(ACTIONS["move_forward"]["time"]) in message, "Pending movement message should include timing"

def test_replay_log_sorting(attacker, defender):
    battle = init_battle(attacker, defender, duration=1000, distance=0, max_distance=100)
    
    # Create events with different timestamps and status
    attacker.force_action("try_attack", 100, battle.event_counter, battle.distance)
    process_action(battle)
    
    attacker.force_action("move_forward", 50, battle.event_counter, battle.distance)
    process_action(battle)
    
    # Sort events and verify order
    sorted_events = sorted(battle.events, key=lambda x: (
        x['timestamp'], 1 if x['status'] == 'pending' else 0, x['event_number']
    ))
    
    # Check if events are sorted by timestamp first
    assert sorted_events[0]['timestamp'] <= sorted_events[-1]['timestamp'], "Events should be sorted by timestamp"
    
    # For same timestamp, completed events should come before pending
    for i in range(len(sorted_events)-1):
        if sorted_events[i]['timestamp'] == sorted_events[i+1]['timestamp']:
            if sorted_events[i]['status'] == 'completed':
                assert sorted_events[i+1]['status'] != 'completed', "Completed events should come before pending for same timestamp"

def test_full_battle_replay(attacker, defender):
    battle = init_battle(attacker, defender, duration=1000, distance=0, max_distance=100)
    
    # Simulate a sequence of actions
    actions = [
        ("try_attack", attacker),
        ("try_block", defender),
        ("move_backward", attacker),
        ("recover", defender)
    ]
    
    # Execute actions
    for action, combatant in actions:
        combatant.force_action(action, battle.timer, battle.event_counter, battle.distance)
        process_action(battle)
    
    # Verify replay contains all actions in correct order
    assert len(battle.events) >= len(actions), "Replay should contain all actions"
    
    # Check if replay contains essential information
    for event in battle.events:
        assert "timestamp" in event, "Event should have timestamp"
        assert "combatant" in event, "Event should have combatant info"
        assert "action" in event, "Event should have action type"
        assert "status" in event, "Event should have status"
        
        # Check if messages can be generated for all events
        if event["status"] == "completed":
            message = battle.message_for_completed_event(event)
        else:
            message = battle.message_for_pending_event(event)
        assert message is not None and len(message) > 0, "Should generate message for event"

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
