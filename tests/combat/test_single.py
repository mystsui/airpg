import sys
import os
import traceback

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(project_root)

from combat.combat_system import CombatSystem
from combat.combatant import TestCombatant
from combat.lib.actions_library import ACTIONS

def create_attacker():
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

def create_defender():
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

def init_battle(attacker, defender, duration, distance, max_distance):
    battle = CombatSystem(duration=duration, distance=distance, max_distance=max_distance)
    battle.add_combatant(attacker)
    battle.add_combatant(defender)
    battle.get_opponent_data(attacker, defender)
    battle.get_opponent_data(defender, attacker)
    return battle

def process_action(battle):
    print("\nBefore determine_next_event:")
    for c in battle.combatants:
        print(f"{c.name} action: {c.action}")
        if c.action:
            print(f"{c.name} action time: {c.action['time']}")
            print(f"{c.name} action status: {c.action['status']}")
    
    battle.determine_next_event()
    print("\nAfter determine_next_event:")
    print(f"Next event: {battle.next_event}")
    print(f"Battle timer: {battle.timer}")
    
    battle.update()
    print("\nAfter update:")
    print(f"Battle timer: {battle.timer}")
    for c in battle.combatants:
        print(f"{c.name} action: {c.action}")
        if c.action:
            print(f"{c.name} action status: {c.action['status']}")
        print(f"{c.name} stamina: {c.stamina}")
        print(f"{c.name} health: {c.health}")
        if hasattr(c, 'blocking_power'):
            print(f"{c.name} blocking power: {c.blocking_power}")

def test_attack_blocked():
    print("\nTesting attack blocked...")
    attacker = create_attacker()
    defender = create_defender()
    battle = init_battle(attacker, defender, duration=1000, distance=0, max_distance=100)
    
    print("\nInitial state:")
    print(f"Attacker stamina: {attacker.stamina}")
    print(f"Defender blocking power: {defender.blocking_power}")
    
    # Force defender to block
    print("\nForcing defender to block...")
    defender.force_action("blocking", battle.timer, battle.event_counter, battle.distance)
    
    # Process blocking setup
    print("\nProcessing blocking setup...")
    process_action(battle)
    
    # Force attack with higher priority
    print("\nForcing attacker to attack...")
    attacker.force_action("try_attack", battle.timer, battle.event_counter, battle.distance)
    
    # Process actions until attack fully resolves
    while battle.timer < 500 or (attacker.action and attacker.action['type'] in ['try_attack', 'release_attack']):
        print(f"\nProcessing next action at time {battle.timer}...")
        process_action(battle)
    
    print("\nFinal state:")
    print(f"Defender health: {defender.health}")
    print(f"Defender blocking power: {defender.blocking_power}")
    print(f"Attacker action: {attacker.action}")
    print(f"Defender action: {defender.action}")

if __name__ == "__main__":
    try:
        test_attack_blocked()
    except Exception as e:
        print(f"\nTest failed with error: {str(e)}")
        print("\nTraceback:")
        traceback.print_exc()
