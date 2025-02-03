import sys
import os
import traceback

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

print("Current working directory:", os.getcwd())
print("Project root:", project_root)
print("Python path:", sys.path)

try:
    print("\nImporting required modules...")
    from combat.lib.actions_library import ACTIONS
    from combat.combat_system import CombatSystem
    from combat.combatant import TestCombatant
    print("All modules imported successfully")

    print("\nCreating test fixtures...")
    def create_attacker():
        attacker = TestCombatant(
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
        print(f"Created attacker with stamina: {attacker.stamina}")
        return attacker

    def create_defender():
        defender = TestCombatant(
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
        print(f"Created defender with health: {defender.health}")
        return defender  # Fixed: was returning attacker instead of defender

    print("\nInitializing battle...")
    battle = CombatSystem(duration=1000, distance=0, max_distance=100)
    attacker = create_attacker()
    defender = create_defender()
    
    print("Adding combatants to battle...")
    battle.add_combatant(attacker)
    battle.add_combatant(defender)
    battle.get_opponent_data(attacker, defender)
    battle.get_opponent_data(defender, attacker)
    print("Battle initialized")

    print("\nStarting attack sequence...")
    print("Initial state:")
    print(f"Attacker stamina: {attacker.stamina}")
    print(f"Defender health: {defender.health}")
    print(f"Battle distance: {battle.distance}")

    # Force try_attack action
    print("\nForcing try_attack action...")
    attacker.force_action("try_attack", 0, battle.event_counter, battle.distance)
    print(f"Attacker action: {attacker.action}")

    # Force defender to do recovery action
    print("\nForcing defender recovery action...")
    defender.force_action("recover", 0, battle.event_counter, battle.distance)
    print(f"Defender action: {defender.action}")

    # Process try_attack
    print("\nProcessing try_attack...")
    battle.determine_next_event()
    battle.update()
    print(f"Timer after try_attack: {battle.timer}")
    print(f"Attacker action: {attacker.action}")

    # Process release_attack
    print("\nProcessing release_attack...")
    battle.determine_next_event()
    battle.update()
    print(f"Timer after release_attack: {battle.timer}")
    print(f"Attacker action: {attacker.action}")
    print(f"Defender health: {defender.health}")

    print("\nTest completed successfully!")

except Exception as e:
    print(f"\nTest failed with error: {str(e)}")
    print("\nTraceback:")
    traceback.print_exc()
