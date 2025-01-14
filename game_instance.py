from combat.combat_system import CombatSystem
from combat.combatant import Combatant
import time

# Initialize battle
battle = CombatSystem(duration=10000)  # 10 seconds

# Create combatants
combatant_a = Combatant(name="A", 
                        health=100, 
                        stamina=150, 
                        attack_power=9, 
                        accuracy=70,
                        blocking_ability=2,
                        evading_ability=1,
                        mobility=50, 
                        range=50, 
                        stamina_recovery=15)

combatant_b = Combatant(name="B", 
                        health=81, 
                        stamina=100, 
                        attack_power=6, 
                        accuracy=85,
                        blocking_ability=1,
                        evading_ability=2, 
                        mobility=60, 
                        range=110, 
                        stamina_recovery=20)

# Add combatants to the battle
battle.add_combatant(combatant_a)
battle.add_combatant(combatant_b)

# Initial action decisions
# combatant_a.decide_action(timer=0, event_counter=0, distance=200, opponent=combatant_b)
# combatant_b.decide_action(timer=0, event_counter=2, distance=200, opponent=combatant_a)

# Determine the first event
battle.determine_next_event()

# Simulate the battle
while not battle.is_battle_over():
    battle.update()
    time.sleep(0)  # 100ms delay between ticks

battle.replay_log()
print("Battle Over!")

