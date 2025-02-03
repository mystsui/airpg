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
    
def test_try_attack_hit(attacker, defender):
    battle = init_battle(attacker, defender, duration=1000, distance=0, max_distance=100)
    
    # Force try_attack action
    attacker.force_action("try_attack", 0, battle.event_counter, battle.distance)

    # Force defender to do recovery action
    defender.force_action("recover", 0, battle.event_counter, battle.distance)

    # Check stamina cost
    assert attacker.stamina == attacker.max_stamina - ACTIONS["try_attack"]["stamina_cost"], "Stamina should decrease by the try_attack stamina cost"

    # Get attacker stamina before releasing/stopping the attack
    attacker_stamina_before_deciding = attacker.stamina

    # Process action
    process_action(battle)

    # Check timer after try_attack action
    assert battle.timer == ACTIONS["try_attack"]["time"], "Timer should be try_attack duration time"
    timer_after_try_attack = battle.timer
    
    # Check if the combatant has already decided on the next action
    chosen_action = attacker.action["type"]
    assert attacker.action["status"] == "pending", "Action status should be pending"
    assert chosen_action == "release_attack" or chosen_action == "stop_attack", "Action should be either release_attack or stop_attack"

    # Get defender health before attack lands
    defender_health_before = defender.health

    # Get defender action before attack lands
    defender_action_before = defender.action["type"]
    
    if chosen_action == "release_attack":
        process_action(battle)
        assert battle.timer == ACTIONS["release_attack"]["time"] + timer_after_try_attack, "Timer should be current action plus release_attack duration time"
        # Since the the opponent is within range, the attack should hit
        # Also, since the opponent is not blocking, the attack should not be blocked
        # Also, since the opponent is not evading, the attack should not be evaded

        # Get approximate damage
        approx_damage = random.randint(attacker.attack_power * attacker.accuracy // 100, attacker.attack_power)
        
        # Get defender health after attack lands
        defender_health_after = defender.health
        assert (defender_health_before - defender_health_after) == pytest.approx(approx_damage, rel=0.1), "Defender health should decrease by the attack power"

        # Check if the combatant has already been applied the appropriate automatic action
        assert attacker.action["status"] == "pending", "Action status should be pending"
        assert attacker.action["type"] == "reset", "Action should be reset"
    else:
        process_action(battle)
        
        # Check defender health
        assert defender.health == defender_health_before, "Defender health should not change"

        # Check defender action
        assert defender.action["type"] == defender_action_before, "Defender action should not change"

        # Check if the combatant has already been applied the appropriate automatic action
        assert attacker.action["status"] == "pending", "Action status should be pending"
        assert attacker.action["type"] == "idle", "Action should be idle"

    # Check stamina change
    assert attacker.stamina == attacker_stamina_before_deciding - ACTIONS[chosen_action]["stamina_cost"], "Stamina should decrease by the stop_attack stamina cost"

    
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
