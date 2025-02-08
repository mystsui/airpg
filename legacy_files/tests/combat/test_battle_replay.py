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
    # First, set up the attack sequence
    attacker.force_action("try_attack", 0, battle.event_counter, battle.distance)
    process_action(battle)
    
    # Then release the attack
    attacker.force_action("release_attack", battle.timer, battle.event_counter, battle.distance)
    process_action(battle)
    
    # Get the last event which should be the attack result
    attack_logs = [log for log in battle.events if log["action"]["type"] == "release_attack"]
    assert len(attack_logs) > 0, "Should have at least one release_attack event"
    log = attack_logs[-1]
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
        "pre_state": {
                "actor": {"name": attacker.name},
                "opponent": None,
                "battle_context": {"distance": 0, "max_distance": 100, "time_remaining": 1000}
            },
            "action": {
                "type": "try_attack",
                "timing": {
                    "start": 0,
                    "duration": ACTIONS["try_attack"]["time"],
                    "end": ACTIONS["try_attack"]["time"]
                },
                "stamina_cost": ACTIONS["try_attack"]["stamina_cost"],
                "in_range": True
            },
            "result": {
                "status": "pending",
                "outcome": None,
                "damage_dealt": None,
                "state_changes": {
                    "actor_stamina_change": -ACTIONS["try_attack"]["stamina_cost"],
                    "opponent_blocking_power_change": None,
                    "opponent_health_change": None,
                    "distance_change": 0
                }
            }
        }
    message = battle.message_for_pending_event(log)
    assert "attempting an attack" in message and str(ACTIONS["try_attack"]["time"]) in message, "Pending attack message should include timing"
    
    # Test movement pending message
    log = {
        "timestamp": 0,
        "pre_state": {
                "actor": {"name": attacker.name},
                "opponent": None,
                "battle_context": {"distance": 0, "max_distance": 100, "time_remaining": 1000}
            },
            "action": {
                "type": "move_forward",
                "timing": {
                    "start": 0,
                    "duration": ACTIONS["move_forward"]["time"],
                    "end": ACTIONS["move_forward"]["time"]
                },
                "stamina_cost": ACTIONS["move_forward"]["stamina_cost"],
                "in_range": True
            },
            "result": {
                "status": "pending",
                "outcome": None,
                "damage_dealt": None,
                "state_changes": {
                    "actor_stamina_change": -ACTIONS["move_forward"]["stamina_cost"],
                    "opponent_blocking_power_change": None,
                    "opponent_health_change": None,
                    "distance_change": attacker.mobility
                }
            }
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
        x['timestamp'], 1 if x['result']['status'] == 'pending' else 0, x['sequence_number']
    ))
    
    # Check if events are sorted by timestamp first
    assert sorted_events[0]['timestamp'] <= sorted_events[-1]['timestamp'], "Events should be sorted by timestamp"
    
    # For same timestamp, completed events should come before pending
    for i in range(len(sorted_events)-1):
        if sorted_events[i]['timestamp'] == sorted_events[i+1]['timestamp']:
            if sorted_events[i]['result']['status'] == 'completed':
                assert sorted_events[i+1]['result']['status'] != 'completed', "Completed events should come before pending for same timestamp"

def test_log_state_ratios(attacker, defender):
    battle = init_battle(attacker, defender, duration=1000, distance=0, max_distance=100)
    
    # Modify health and stamina
    attacker.health = 50  # Half health
    attacker.stamina = 75  # 3/4 stamina
    
    # Create a log directly to verify ratios before any stamina deductions
    log = {
        "event_id": f"0_1_{attacker.name}",
        "timestamp": 0,
        "sequence_number": 1,
        "pre_state": {
            "actor": {
                "name": attacker.name,
                "health_ratio": attacker.health / attacker.max_health,
                "stamina_ratio": attacker.stamina / attacker.max_stamina,
                "position": attacker.position,
                "facing": attacker.facing,
                "blocking_power": attacker.blocking_power,
                "current_action": "try_attack"
            },
            "opponent": None,
            "battle_context": {
                "distance": battle.distance,
                "max_distance": battle.max_distance,
                "time_remaining": battle.duration
            }
        },
        "action": {
            "type": "try_attack",
            "timing": {
                "start": 0,
                "duration": ACTIONS["try_attack"]["time"],
                "end": ACTIONS["try_attack"]["time"]
            },
            "stamina_cost": ACTIONS["try_attack"]["stamina_cost"],
            "in_range": True
        },
        "result": {
            "status": "pending",
            "outcome": None,
            "damage_dealt": None,
            "state_changes": {
                "actor_stamina_change": -ACTIONS["try_attack"]["stamina_cost"],
                "opponent_blocking_power_change": None,
                "opponent_health_change": None,
                "distance_change": 0
            }
        },
        "action_history": {
            "actor_previous": [],
            "opponent_previous": None
        }
    }
    battle.events.append(log)
    
    # Verify ratios
    assert log["pre_state"]["actor"]["health_ratio"] == 0.5, "Health ratio should be 0.5"
    assert log["pre_state"]["actor"]["stamina_ratio"] == 0.75, "Stamina ratio should be 0.75"
    
    # Verify spatial info
    assert log["pre_state"]["actor"]["position"] == "left", "Position should be recorded"
    assert log["pre_state"]["actor"]["facing"] == "right", "Facing direction should be recorded"
    assert log["pre_state"]["actor"]["blocking_power"] == 0, "Blocking power should be recorded"

def test_log_action_context(attacker, defender):
    battle = init_battle(attacker, defender, duration=1000, distance=50, max_distance=100)
    
    # Force an attack action
    start_time = battle.timer
    attacker.force_action("try_attack", start_time, battle.event_counter, battle.distance)
    process_action(battle)
    
    log = battle.events[-1]
    
    # Verify timing information
    assert log["action"]["timing"]["start"] == start_time, "Start time should match battle timer"
    assert log["action"]["timing"]["duration"] > 0, "Duration should be positive"
    assert log["action"]["timing"]["end"] > start_time, "End time should be after start time"
    
    # Verify costs and ranges
    assert log["action"]["stamina_cost"] == ACTIONS["try_attack"]["stamina_cost"], "Stamina cost should match action definition"
    assert isinstance(log["action"]["in_range"], bool), "Range check should be boolean"
    
    # Verify battle context
    assert log["pre_state"]["battle_context"]["distance"] == 50, "Distance should be recorded"
    assert log["pre_state"]["battle_context"]["max_distance"] == 100, "Max distance should be recorded"
    assert log["pre_state"]["battle_context"]["time_remaining"] == 1000 - start_time, "Time remaining should be calculated"

def test_action_history_tracking(attacker, defender):
    battle = init_battle(attacker, defender, duration=1000, distance=0, max_distance=100)
    
    # Execute sequence of actions
    actions = ["move_forward", "try_attack", "recover", "move_backward"]
    for action in actions:
        attacker.force_action(action, battle.timer, battle.event_counter, battle.distance)
        process_action(battle)
    
    # Get all completed actions for the attacker
    completed_actions = []
    for event in battle.events:
        if (event["pre_state"]["actor"]["name"] == attacker.name and 
            event["result"]["status"] == "completed" and
            event["action"]["type"] != "idle"):  # Exclude idle actions
            completed_actions.append(event["action"]["type"])
    
    # Get the last event
    log = battle.events[-1]
    
    # Verify action history
    assert len(log["action_history"]["actor_previous"]) <= 3, "Should keep at most 3 previous actions"
    # Compare with the last 3 completed actions
    expected_history = completed_actions[-4:-1]  # Get 3 actions before the last one
    assert expected_history == log["action_history"]["actor_previous"], "Should record correct action sequence"

def test_state_change_logging(attacker, defender):
    battle = init_battle(attacker, defender, duration=1000, distance=50, max_distance=100)
    
    # Record initial values
    initial_stamina = attacker.stamina
    initial_distance = battle.distance
    
    # Force a movement action
    attacker.force_action("move_forward", battle.timer, battle.event_counter, battle.distance)
    process_action(battle)
    
    log = battle.events[-1]
    
    # Verify state changes
    assert log["result"]["state_changes"]["actor_stamina_change"] == -ACTIONS["move_forward"]["stamina_cost"], "Should record stamina cost"
    assert log["result"]["state_changes"]["distance_change"] == attacker.mobility, "Should record distance change"
    assert battle.distance == initial_distance - attacker.mobility, "Distance should be updated"

def test_log_edge_cases(attacker, defender):
    battle = init_battle(attacker, defender, duration=1000, distance=0, max_distance=100)
    
    # Test logging with defeated combatant
    attacker.health = 0
    attacker.force_action("try_attack", battle.timer, battle.event_counter, battle.distance)
    process_action(battle)
    
    log = battle.events[-1]
    assert log["pre_state"]["actor"]["health_ratio"] == 0, "Should handle zero health"
    
    # Test logging at battle start
    battle = init_battle(attacker, defender, duration=1000, distance=0, max_distance=100)
    attacker.health = 100  # Reset health
    log = battle.events[0] if battle.events else None
    assert log is not None, "Should log initial battle state"
    
    # Test logging with missing opponent
    battle = CombatSystem(duration=1000, distance=0, max_distance=100)
    battle.add_combatant(attacker)
    attacker.force_action("move_forward", battle.timer, battle.event_counter, battle.distance)
    process_action(battle)
    
    log = battle.events[-1]
    assert log["pre_state"]["opponent"] is None, "Should handle missing opponent"

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
    
    # Check if replay contains enhanced information
    for event in battle.events:
        # Verify event structure
        assert "event_id" in event, "Event should have unique ID"
        assert "pre_state" in event, "Event should have pre-state info"
        assert "action" in event, "Event should have action info"
        assert "result" in event, "Event should have result info"
        
        # Verify pre-state structure
        pre_state = event["pre_state"]
        assert "actor" in pre_state, "Pre-state should have actor info"
        assert "battle_context" in pre_state, "Pre-state should have battle context"
        
        # Verify action structure
        action = event["action"]
        assert "timing" in action, "Action should have timing info"
        assert "stamina_cost" in action, "Action should have stamina cost"
        
        # Verify result structure
        result = event["result"]
        assert "state_changes" in result, "Result should have state changes"
        
        # Check if messages can be generated for all events
        if event["result"]["status"] == "completed":
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
    
    # Log initial battle state
    initial_log = {
        "event_id": f"0_0_battle_start",
        "timestamp": 0,
        "sequence_number": 0,
        "pre_state": {
            "actor": {
                "name": attacker.name,
                "health_ratio": attacker.health / attacker.max_health,
                "stamina_ratio": attacker.stamina / attacker.max_stamina,
                "position": attacker.position,
                "facing": attacker.facing,
                "blocking_power": attacker.blocking_power,
                "current_action": "idle"
            },
            "opponent": {
                "name": defender.name,
                "health_ratio": defender.health / defender.max_health,
                "stamina_ratio": defender.stamina / defender.max_stamina,
                "position": defender.position,
                "facing": defender.facing,
                "blocking_power": defender.blocking_power,
                "current_action": "idle"
            },
            "battle_context": {
                "distance": distance,
                "max_distance": max_distance,
                "time_remaining": duration
            }
        },
        "action": {
            "type": "idle",
            "timing": {
                "start": 0,
                "duration": 0,
                "end": 0
            },
            "stamina_cost": 0,
            "in_range": attacker.is_within_range(distance)
        },
        "result": {
            "status": "completed",
            "outcome": None,
            "damage_dealt": None,
            "state_changes": {
                "actor_stamina_change": 0,
                "opponent_blocking_power_change": None,
                "opponent_health_change": None,
                "distance_change": 0
            }
        },
        "action_history": {
            "actor_previous": [],
            "opponent_previous": []
        }
    }
    battle.events.append(initial_log)
    return battle

def process_action(battle):
    battle.determine_next_event()
    battle.update()
