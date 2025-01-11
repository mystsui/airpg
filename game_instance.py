from combat.combat_system import CombatSystem
from combat.combatant import Combatant
import time

# Initialize battle
battle = CombatSystem(duration=50000)  # 5 seconds

# Create combatants
combatant_a = Combatant(name="A", health=100, stamina=50, attack_power=9, accuracy=70, mobility=50, range=50, team="challenger")
combatant_b = Combatant(name="B", health=81, stamina=80, attack_power=6, accuracy=85, mobility=60, range=110, team="defender")

# Add combatants to the battle
battle.add_combatant(combatant_a)
battle.add_combatant(combatant_b)

# Initial action decisions
combatant_a.decide_action(timer=0, distance=200)
combatant_b.decide_action(timer=0, distance=200)

# Determine the first event
battle.determine_next_event()

# Simulate the battle
while not battle.is_battle_over():
    battle.update()
    time.sleep(0)  # 100ms delay between ticks

print("Battle Over!")
