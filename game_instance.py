from combat.combat_system import CombatSystem
from combat.combatant import Combatant
import time

# Initialize battle
battle = CombatSystem(duration=10000, distance=10)  # 10 seconds

# Create combatants
combatant_a = Combatant(name="A", 
                        health=100, #primarily person-based (Endurance)
                        stamina=150, #primarily person-based (Reflexes)
                        # energy=0, #primarily person-based (Synapse) affected by accessories
                        accuracy=70, #primarily person-based (Precision) affected by weapon
                        #breakpoint_probability=0, #primarily person-based (Entropy) affected by weapon
                        stamina_recovery=15, #person-based (Reflexes)
                        #speed=0, #primarily person-based (Reflexes) affected by weight
                        perception=0, #person-based (chance/rate of taking notice of the opponent's action)
                        stealth=0, #primarily person-based (chance/rate of hiding an action)

                        #gear_capacity (not for battles, just needed for equipping gears) (Synapse) (only for cyberpunk)
                        #breakpoint_multiplier=0, #gear-based
                        #armor=0, #primarily gear-based
                        #armor_penetration=0, #gear-based (secondary precision)
                        #weight=0, #gear-based                        
                        attack_power=15, #gear-based
                        blocking_power=5, #gear-based (secondary endurance)
                        evading_ability=10, #(not needed currently since evade times are uniform)
                        mobility=50, #primarily gear-based (countered by weight)
                        range_a=0,
                        range_b=50,
                        position="left",
                        facing="right"
                        )

combatant_b = Combatant(name="B", 
                        health=81, 
                        stamina=100, 
                        attack_power=11, 
                        accuracy=85,
                        blocking_power=100,
                        evading_ability=20, 
                        mobility=60, 
                        range_a=30,
                        range_b=150,
                        perception=0,
                        stealth=0,  
                        position="right",
                        facing="left",
                        stamina_recovery=20)

# Add combatants to the battle
battle.add_combatant(combatant_a)
battle.add_combatant(combatant_b)

# Initialize opponent data
assumed_a = Combatant(
    name="A", 
    health=500, #primarily person-based (Endurance)
    stamina=150, #primarily person-based (Reflexes)
    # energy=0, #primarily person-based (Synapse) affected by accessories
    accuracy=70, #primarily person-based (Precision) affected by weapon
    #breakpoint_probability=0, #primarily person-based (Entropy) affected by weapon
    stamina_recovery=15, #person-based (Reflexes)
    #speed=0, #primarily person-based (Reflexes) affected by weight
    perception=0, #person-based (chance/rate of taking notice of the opponent's action)
    stealth=0, #primarily person-based (chance/rate of hiding an action)

    #gear_capacity (not for battles, just needed for equipping gears) (Synapse) (only for cyberpunk)
    #breakpoint_multiplier=0, #gear-based
    #armor=0, #primarily gear-based
    #armor_penetration=0, #gear-based (secondary precision)
    #weight=0, #gear-based                        
    attack_power=15, #gear-based
    blocking_power=5, #gear-based (secondary endurance)
    evading_ability=10, #(not needed currently since evade times are uniform)
    mobility=50, #primarily gear-based (countered by weight)
    range_a=0,
    range_b=100,
    position="left",
    facing="right",
    action=None,
)

assumed_b = Combatant(
    name="B", 
    health=500, #primarily person-based (Endurance)
    stamina=150, #primarily person-based (Reflexes)
    # energy=0, #primarily person-based (Synapse) affected by accessories
    accuracy=70, #primarily person-based (Precision) affected by weapon
    #breakpoint_probability=0, #primarily person-based (Entropy) affected by weapon
    stamina_recovery=15, #person-based (Reflexes)
    #speed=0, #primarily person-based (Reflexes) affected by weight
    perception=0, #person-based (chance/rate of taking notice of the opponent's action)
    stealth=0, #primarily person-based (chance/rate of hiding an action)

    #gear_capacity (not for battles, just needed for equipping gears) (Synapse) (only for cyberpunk)
    #breakpoint_multiplier=0, #gear-based
    #armor=0, #primarily gear-based
    #armor_penetration=0, #gear-based (secondary precision)
    #weight=0, #gear-based                        
    attack_power=15, #gear-based
    blocking_power=5, #gear-based (secondary endurance)
    evading_ability=10, #(not needed currently since evade times are uniform)
    mobility=50, #primarily gear-based (countered by weight)
    range_a=0,
    range_b=100,
    position="right",
    facing="left",
    action=None
)

battle.get_opponent_data(combatant_a, assumed_b)
battle.get_opponent_data(combatant_b, assumed_a)

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

