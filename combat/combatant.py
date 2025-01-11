from combat.lib.actions_library import ACTIONS
import copy

class Combatant:
    def __init__(
        self, 
        name, 
        health, 
        stamina, 
        attack_power, 
        accuracy, 
        blocking_ability,
        evading_ability,
        mobility, 
        range, 
        stamina_recovery):
        """
        Initialize a combatant.
        """
        self.name = name # name of the combatant
        self.health = health # current health
        self.stamina = stamina # current stamina
        self.max_stamina = stamina # maximum stamina
        self.max_health = health # maximum health
        self.attack_power = attack_power
        self.accuracy = accuracy # determines the spread of the attack power (fixed)
        self.blocking_ability = blocking_ability # blocking ability (fixed)
        self.evading_ability = evading_ability # evading ability (fixed)
        self.mobility = mobility # movement speed (fixed)
        self.range = range # attack range (fixed)
        self.stamina_recovery = stamina_recovery # stamina recovery rate
        self.action = None # current action

    def decide_action(self, timer, distance, opponent=None):
        """
        Decide the next action based on the current state.
        This should be a decision tree or a policy network. For now, we will use a simple rule-based system. 

        :param timer: Current battle time.
        :param timer: Current distance between combatants.
        """
        move_forward = ACTIONS["move_forward"]
        move_backward = ACTIONS["move_backward"]
        attack = ACTIONS["attack"]
        recover = ACTIONS["recover"]
        idle = ACTIONS["idle"]
        reset = ACTIONS["reset"]
        try_evade = ACTIONS["try_evade"]
        evading = ACTIONS["evading"]
        try_block = ACTIONS["try_block"]
        blocking = ACTIONS["blocking"]
        

        self.action = {}
        # if distance <= self.range:
        #     if distance + self.mobility <= self.range:
        #         self.action["type"] = "move_backward" if self.stamina >= move_backward["stamina_cost"] else "recover"
        #     else:
        #         self.action["type"] = "attack" if self.stamina >= attack["stamina_cost"] else "recover"
        # elif distance > self.range:
        #     self.action["type"] = "move_forward" if self.stamina >= move_forward["stamina_cost"] else "recover"

        # Step 1: Check stamina first
        if self.stamina < recover["stamina_cost"]:
            self.action["type"] = "recover"

        #Step 2: React to opponent's action
        if opponent:
            opponent_action = opponent.action["type"]
            if opponent_action == "attack":
                # Decide to evade or block if opponent is attacking
                if self.stamina >= try_evade["stamina_cost"]:
                    self.action["type"] = "try_evade"
                elif self.stamina >= try_block["stamina_cost"]:
                    self.action["type"] = "try_block"
                else:
                    # If unable to evade or block, prioritize recovery
                    self.action["type"] = "idle"
            elif opponent_action in ["recover", "reset"]:
                # Exploit opponent's recovery/reset state
                if distance <= self.range and self.stamina >= attack["stamina_cost"]:
                    self.action["type"] = "attack"
                elif distance > self.range and self.stamina >= move_forward["stamina_cost"]:
                    self.action["type"] = "move_forward"

        # Step 3: Default combat logic based on distance
        if distance <= self.range:
            # If in range, decide between attacking or retreating
            if self.stamina >= attack["stamina_cost"]:
                self.action["type"] = "attack"
            elif distance + self.mobility <= self.range and self.stamina >= move_backward["stamina_cost"]:
                self.action["type"] = "move_backward"
            else:
                self.action["type"] = "recover"
        elif distance > self.range:
            # If out of range, decide to close the gap
            self.action["type"] = "move_forward" if self.stamina >= move_forward["stamina_cost"] else "recover"
        else:
            # Default to idle
            self.action["type"] = "idle"
        # self.action["type"] = "recover"
            
        # Set the combatant for the action
        self.action["combatant"] = self

        # Update the action time to the current timer plus the action time
        self.action["time"] = ACTIONS[self.action["type"]]["time"] + timer
        # print(f"{self.name} decided to {self.action['type']} with {self.action["time"]}")

        # Update the action status
        self.action["status"] = "pending"

        # Set the target for the action
        self.action["target"] = None
        
        # print(f"{self.name} decided to {self.action['type']} at time {self.action['time']}")

    def apply_action_state(self, timer, _action):
        """
        Update the action status after each event.
        """
        _action = copy.copy(_action)
        self.action = {
            "time": _action["time"],
            "type": _action["type"],
            "stamina_cost": _action["stamina_cost"],
        }
        self.action["time"] += timer
        self.action["combatant"] = self
        # print(f"!!!{self.name} decided to {self.action['type']} at time {self.action['time']}")

    def get_opponent_data(self, opponent=None):
        """
        Get the opponent's data.
        """
        return

    def is_defeated(self):
        """
        Check if the combatant is defeated.
        """
        return self.health <= 0        
