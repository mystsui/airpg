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
        blocking_power,
        evading_ability,
        mobility, 
        range, 
        stamina_recovery,
        opponent=None):
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
        self.blocking_power = blocking_power # blocking ability (fixed)
        self.evading_ability = evading_ability # evading ability (fixed)
        self.mobility = mobility # movement speed (fixed)
        self.range = range # attack range (fixed)
        self.stamina_recovery = stamina_recovery # stamina recovery rate
        self.action = {"type": "idle", "combatant": self, "time": ACTIONS["idle"]["time"], "status": "pending", "target": None}
        self.opponent = opponent

    def decide_action(self, timer, event_counter, distance, opponent):
        """
        Decide the next action based on the current state.
        This should be a decision tree or a policy network. For now, we will use a simple rule-based system.

        :param timer: Current battle time.
        :param distance: Current distance between combatants.
        :param opponent: Opponent combatant object (read-only for action type).
        """
        # Load action definitions
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
        keep_blocking = ACTIONS["keep_blocking"]
        stop_blocking = ACTIONS["stop_blocking"]
        
        current_action = self.action
        # Initialize action dictionary
        self.action = {}
        
        # Blocking tests
        if self.name == "A":
            if distance > self.range:
                self.action["type"] = "move_forward"
                self.action["time"] = move_forward["time"] + timer
            else:
                self.action["type"] = "attack"
                self.action["time"] = attack["time"] + timer
                self.action["target"] = opponent
        else:
            if current_action["type"] == "blocking":
                self.action["type"] = "keep_blocking"
                self.action["time"] = keep_blocking["time"] + timer
            else:
                self.action["type"] = "try_block"
                self.action["time"] = try_block["time"] + timer
                
            
        # Set the combatant for the action
        self.action["combatant"] = self

        # Update the action time to the current timer plus the action time
        # self.action["time"] = ACTIONS[self.action["type"]]["time"] + timer
        # print(f"{self.name} decided to {self.action['type']} with {self.action["time"]}")

        # Update the action status
        self.action["status"] = "pending"

        # Set the target for the action
        self.action["target"] = opponent
        
        # print(f"{self.name} decided to {self.action['type']} effective at time {self.action['time']} while having {self.stamina} stamina at {timer}")

        log = self.decision_applied_log(timer, event_counter, distance, opponent)
        return log
    
    def decision_applied_log(self, timer, event_counter, distance, opponent):
        """
        Prepare the decision log for the combatant.
        """
        
        log = {
            "timestamp": timer,
            "event_number": event_counter + 1,
            "timeend": self.action["time"],
            "combatant": {
                "name": self.name,
                "health": self.health,
                "stamina": self.stamina
            } if self else None,
            "action": self.action["type"],
            "distance": distance,
            "status": "pending",
            "target": {
                "name": opponent.name if opponent else None,
                "health": opponent.health if opponent else None,
                "stamina": opponent.stamina if opponent else None
            },
            "result": None,
            "damage": None,
            # "details": kwargs  # Additional information like damage, distance, etc.
        }
        return log

    def apply_action_state(self, _action, timer, event_counter, distance, opponent):
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
        self.action["status"] = "pending"
        self.action["target"] = None

        log = self.decision_applied_log(timer, event_counter, distance, opponent)
        return log
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
