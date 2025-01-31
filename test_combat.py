# test_combat.py
import pytest
from combat.combatant import TestCombatant
from combat.combat_system import CombatSystem

@pytest.fixture
def attacker():
    return TestCombatant(
        name="Attacker",
        health=100,
        stamina=100,
        attack_power=20,
        accuracy=100,  # Guarantee hits
        blocking_power=0,
        evading_ability=0,
        mobility=10,
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
        name="Defender",
        health=100,
        stamina=100,
        attack_power=0,
        accuracy=0,
        blocking_power=30,  # Initial blocking power
        evading_ability=0,
        mobility=0,
        range_a=0,
        range_b=50,
        stamina_recovery=0,
        position="right",
        facing="left",
        perception=0,
        stealth=0
    )
    
def init_battle(attacker, defender):
    battle = CombatSystem(duration=10000, distance=10)
    battle.add_combatant(attacker)
    battle.add_combatant(defender)
    battle.get_opponent_data(attacker, defender)
    battle.get_opponent_data(defender, attacker)
    return battle

def test_basic_movement(attacker, defender):
    battle = init_battle(attacker, defender)
    initial_distance = battle.distance
    
    # Force move forward action
    attacker.force_action("move_forward", 0, battle.event_counter, battle.distance)
    battle.determine_next_event()
    battle.update()
    
    # Check distance reduced by mobility
    assert battle.distance == initial_distance - attacker.mobility

# def test_block_mechanic(attacker, defender):
#     # Initialize battle
#     battle = CombatSystem(duration=10000, distance=10)
#     battle.add_combatant(attacker)
#     battle.add_combatant(defender)  # Typo fixed from earlier
#     battle.get_opponent_data(attacker, defender)
#     battle.get_opponent_data(defender, attacker)

#     # Force actions explicitly
#     attacker.force_action("try_attack", timer=0)
#     defender.force_action("try_block", timer=0)

#     # Manually trigger combat steps
#     battle.determine_next_event()  # Find first event
#     battle.update()  # Process the event

#     # Assertions
#     assert defender.health == 100, "Block should prevent health loss"
#     assert defender.blocking_power == 10, "Blocking power should reduce by attack damage (30 - 20 = 10)"
#     assert attacker.stamina == 90, "Attacker stamina should deduct for try_attack (100 - 10)"
#     assert defender.stamina == 97, "Defender stamina should deduct for try_block (100 - 3)"