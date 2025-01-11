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
        combatant.team = "challenger" if len(self.combatants) == 0 else "defender"
        self.combatants.append(combatant)
        print(f"Added {combatant} to the team {combatant.team}")

    def determine_next_event(self):
        """
        Determine which combatant's action should be processed next.
        """
        # Filter combatants with valid actions
        active_combatants = [c.action for c in self.combatants if c.action]
        
        if not active_combatants:
            self.next_event = None
            print("No valid combatant actions found.")
            return
        
        # print(f"Active combatants: Challenger: {self.combatants[0].action} Defender: {self.combatants[1].action}")

        # Find the action with the earliest time
        self.next_event = min(active_combatants, key=lambda action: action['time'])
        
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
            self.process_move_forward(combatant, event)
            
        elif action_type == "move_backward":
            self.process_move_backward(combatant, event)

        elif action_type == "recover":
            self.process_recovery(combatant, event)
        
        elif action_type == "idle":
            self.process_idle(combatant, event)
        
        elif action_type == "reset":
            self.process_reset(combatant, event)
            
        elif action_type == "try_block":
            self.process_block(combatant, event)
        
        elif action_type == "try_evade":
            self.process_evade(combatant, event)
            
        elif action_type == "blocking":
            self.process_blocking(combatant, event)
            
        elif action_type == "evading":
            self.process_evading(combatant, event)
            
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
            if target.action['type'] == "blocking":
                event['status'] = "blocked"
                print(f"{combatant.name}'s attack was blocked by {target.name}.")
            elif target.action['type'] == "evading":
                event['status'] = "evaded"
                print(f"{combatant.name}'s attack was evaded by {target.name}.")
            else:
                damage = random.randint(combatant.attack_power * combatant.accuracy // 100, combatant.attack_power)
                target.health = max(0, target.health - damage)
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
        
    def process_move_forward(self, combatant, event):
        """
        Process a move forward action for a combatant.
        """
        event['status'] = "completed"
        combatant.stamina -= ACTIONS["move_forward"]["stamina_cost"]
        self.distance = max(0, self.distance - combatant.mobility)
        print(f"{combatant.name} moved forward (dist: {self.distance}) at {self.timer}")

        # Schedule recovery for the combatant
        combatant.apply_action_state(self.timer, ACTIONS["recover"])
    
    def process_move_backward(self, combatant, event):
        """
        Process a move backward action for a combatant.
        """
        event['status'] = "completed"
        combatant.stamina -= ACTIONS["move_backward"]["stamina_cost"]
        self.distance = min(600, self.distance + combatant.mobility)
        print(f"{combatant.name} moved backward (dist: {self.distance}) at {self.timer}")

        # Schedule recovery for the combatant
        combatant.apply_action_state(self.timer, ACTIONS["recover"])
        
    def process_recovery(self, combatant, event):
        """
        Process a recovery action for a combatant.
        """
        event['status'] = "completed"
        combatant.stamina = min(combatant.max_stamina, combatant.stamina + combatant.stamina_recovery)
        print(f"{combatant.name} recovered stamina ({combatant.stamina}) at {self.timer}")

        # Schedule the next action for the combatant
        combatant.decide_action(self.timer, self.distance, copy.copy(self.find_target(combatant)))
        
    def process_idle(self, combatant, event):
        """
        Process an idle action for a combatant.
        """
        event['status'] = "completed"
        print(f"{combatant.name} idled at {self.timer}")

        # Schedule the next action for the combatant
        combatant.decide_action(self.timer, self.distance, copy.copy(self.find_target(combatant)))
        
    def process_reset(self, combatant, event):
        """
        Process a reset action for a combatant.
        """
        event['status'] = "completed"
        print(f"{combatant.name} reset at {self.timer}")

        # Schedule the next action for the combatant
        combatant.decide_action(self.timer, self.distance, copy.copy(self.find_target(combatant)))
        
    def process_block(self, combatant, event):
        """
        Process a block action for a combatant.
        """
        event['status'] = "completed"
        combatant.stamina -= ACTIONS["try_block"]["stamina_cost"]
        print(f"{combatant.name} tried to block at {self.timer}")

        # Start the blocking action
        blocking_action = copy.copy(ACTIONS["blocking"])
        blocking_action["time"] = self.timer + combatant.blocking_ability
        combatant.apply_action_state(self.timer, blocking_action)
        
    def process_blocking(self, combatant, event):
        """
        Process a blocking action for a combatant.
        """
        event['status'] = "completed"
        print(f"{combatant.name} stopped blocking at {self.timer}")

        # Schedule recovery for the combatant
        combatant.apply_action_state(self.timer, ACTIONS["reset"])
        
    def process_evade(self, combatant, event):
        """
        Process an evade action for a combatant.
        """
        event['status'] = "completed"
        combatant.stamina -= ACTIONS["try_evade"]["stamina_cost"]
        print(f"{combatant.name} tried to evade at {self.timer}")

        # Start the evading action
        evading_action = copy.copy(ACTIONS["evading"])
        evading_action["time"] = self.timer + combatant.evading_ability
        combatant.apply_action_state(self.timer, evading_action)
        
    def process_evading(self, combatant, event):
        """
        Process an evading action for a combatant.
        """
        event['status'] = "completed"
        print(f"{combatant.name} stopped evading at {self.timer}")

        # Schedule recovery for the combatant
        combatant.apply_action_state(self.timer, ACTIONS["reset"])
            
    def is_battle_over(self):
        """
        Check if the battle is over.
        """
        if self.timer >= self.duration:
            return True

        active_combatants = [c for c in self.combatants if not c.is_defeated()]
        return len(active_combatants) <= 1