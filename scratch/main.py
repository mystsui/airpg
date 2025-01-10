from battle_state import BattleState
from combatant import Combatant

# Initialize battle
battle = BattleState(duration=5000)  # 5 seconds

# Create combatants
combatant_a = Combatant(name="A", health=100, attack_power=10, team="red")
combatant_b = Combatant(name="B", health=80, attack_power=12, team="blue")

# Add combatants to the battle
battle.add_combatant(combatant_a)
battle.add_combatant(combatant_b)

# Initial action decisions
combatant_a.decide_action(timer=0)
combatant_b.decide_action(timer=0)

# Determine the first event
battle.determine_next_event()

# Simulate the battle
while not battle.is_battle_over():
    battle.update()

print("Battle Over!")

# Replay the battle log
battle.replay_log()
