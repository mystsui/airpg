import copy
import random

from combat.lib.actions_library import ACTIONS

class CombatSystem:
    def __init__(self, duration):
        """
        Initialize the battle state.
        
        :param duration: Total duration of the battle in milliseconds.
        """
        self.timer = 0  # Current time
        self.duration = duration  # Total duration of the battle
        self.combatants = []  # List of combatants
        self.distance = 200  # Distance between the two teams
        self.events = []  # Log of processed events (snapshots)
        self.next_event = None  # Reference to the next event to process

    def add_combatant(self, combatant):
        """
        Add a combatant to the battle.
        """
        self.combatants.append(combatant)

    def determine_next_event(self):
        """
        Determine which combatant's action should be processed next.
        """
        # print(f"A: {self.combatants[0].action["combatant"].name}")
        # print(f"B: {self.combatants[1].action["combatant"].name}")
        # Filter combatants with valid actions
        active_combatants = [c.action for c in self.combatants if c.action]
        
        if not active_combatants:
            self.next_event = None
            print("No valid combatant actions found.")
            return

        # Find the action with the earliest time
        self.next_event = min(active_combatants, key=lambda action: action['time'])
        # print(f"Next event: {self.next_event['combatant'].name} at {self.next_event['time']}")

    def update(self):
        """
        Process the next event in the battle.
        """

        if not self.next_event:
            return

        # Jump to the next event's time
        self.timer = self.next_event['time']

        # Process the event
        self.process_event(self.next_event)

        # Log the event
        self.events.append(copy.deepcopy(self.next_event))

        # Determine the next event
        self.determine_next_event()

    def process_event(self, event):
        """
        Process an individual event.
        """
        combatant = event['combatant']
        action_type = event['type']

        if action_type == "attack":
            self.process_attack(combatant, event)
        
        elif action_type == "move_forward":
            event['status'] = "completed"
            combatant.stamina -= ACTIONS["move_forward"]["stamina_cost"]
            self.distance = max(0, self.distance - combatant.mobility)
            print(f"{combatant.name} moved forward (dist: {self.distance}) at {self.timer}")
            
            # Schedule recovery for the combatant
            combatant.apply_action_state(self.timer, ACTIONS["recover"])
            # print(f"{combatant.name}'s next move is going to come at {combatant.action["time"]}.")

        elif action_type == "move_backward":
            event['status'] = "completed"
            combatant.stamina -= ACTIONS["move_backward"]["stamina_cost"]
            self.distance = min(600, self.distance + combatant.mobility)
            print(f"{combatant.name} moved backward (dist: {self.distance}) at {self.timer}")
            
            # Schedule recovery for the combatant
            combatant.apply_action_state(self.timer, ACTIONS["recover"])

        elif action_type == "recover":
            event['status'] = "completed"
            # print(f"{combatant.name} has recovered and is ready to act again at {self.timer}.")
            combatant.stamina += 2

            # After recovery, the combatant should decide the next action
            combatant.decide_action(self.timer, self.distance)
            print(f"{combatant.name}'s has recovered and now has {combatant.stamina} stamina left.")        

        else:
            print(f"Unknown action type: {action_type}")

    def process_attack(self, combatant, event):
        """
        Process an attack action between two combatants.
        """
        target = CombatSystem.find_target(self, combatant)
        combatant.stamina -= ACTIONS["attack"]["stamina_cost"]
        if combatant.range < self.distance:
            event['status'] = "missed"
            print(f"{combatant.name}'s attack missed! Target not in range.")
        else:
            damage = random.randint(combatant.attack_power * combatant.accuracy // 100, combatant.attack_power)
            target.health -= damage
            event['status'] = "hit"
            print(f"{combatant.name} attacked {target.name} for {damage} damage (rem HP: {target.health}).")

        # Schedule recovery for the combatant
        combatant.apply_action_state(self.timer, ACTIONS["recover"])
        
    def find_target(self, combatant):
        """
        Find a target for the given combatant from the opposing team who is not defeated.
        """
        for potential_target in self.combatants:
            if potential_target.team != combatant.team and not potential_target.is_defeated():
                return potential_target
        return None  # No valid target found
            
    def is_battle_over(self):
        """
        Check if the battle is over.
        """
        if self.timer >= self.duration:
            return True

        active_combatants = [c for c in self.combatants if not c.is_defeated()]
        return len(active_combatants) <= 1