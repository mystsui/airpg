from combat.lib.actions_library import ACTIONS
import copy

class Combatant:
    def __init__(self, name, health, stamina, attack_power, accuracy, mobility, range, team, opponent=None):
        """
        Initialize a combatant.
        """
        self.name = name # name of the combatant
        self.opponent_data = self.get_opponent_data(opponent) # an instance of Combatant representing the opponent
        self.health = health # current health
        self.stamina = stamina # current stamina
        self.max_stamina = stamina # maximum stamina
        self.max_health = health # maximum health
        self.attack_power = attack_power
        self.accuracy = accuracy # determines the spread of the attack power (fixed)
        self.mobility = mobility # movement speed (fixed)
        self.range = range # attack range (fixed)
        self.team = team # team color
        self.action = None # current action

    def decide_action(self, timer, distance):
        """
        Decide the next action based on the current state.
        This should be a decision tree or a policy network. For now, we will use a simple rule-based system. 
        Default action is to attack.
        The combatant's range and the opponent's target range should be considered.
        The combatant's mobility and the opponent's target mobility should be considered.
        The combatant's health and the opponent's target health should be considered.
        The combatant's attack power and the opponent's target health should be considered.                
        Moving forward reduces the distance between combatants by the combatant's mobility.
        Moving backward increases the distance between combatants by the combatant's mobility.
        Recovering takes time and does not restore health. It is some kind of cooldown. It shall not be chosen here.
        Moving takes 50 time.
        Attacking takes 300 time.
        :param timer: Current battle time.
        :param timer: Current distance between combatants.
        """
        move_forward = ACTIONS["move_forward"]
        move_backward = ACTIONS["move_backward"]
        attack = ACTIONS["attack"]
        recover = ACTIONS["recover"]

        self.action = {}
        if distance <= self.range:
            if distance + self.mobility <= self.range:
                self.action["type"] = "move_backward" if self.stamina >= move_backward["stamina_cost"] else "recover"
            else:
                self.action["type"] = "attack" if self.stamina >= attack["stamina_cost"] else "recover"
        elif distance > self.range:
            self.action["type"] = "move_forward" if self.stamina >= move_forward["stamina_cost"] else "recover"

        # Set the combatant for the action
        self.action["combatant"] = self

        # Update the action time to the current timer plus the action time
        self.action["time"] = ACTIONS[self.action["type"]]["time"] + timer

        # Update the action status
        self.action["status"] = "pending"

        # Set the target for the action
        self.action["target"] = None

    def apply_action_state(self, timer, _action):
        """
        Update the action status after each event.
        """
        _action = copy.copy(_action)
        self.action = {
            "time": _action["time"],
            "type": _action["type"],
            "combatant": self,
            "target": None,
            "status": "pending",
        }
        self.action["time"] += timer

    def get_opponent_data(self, opponent=None):
        """
        Get the opponent's data.
        """
        return

    def update_opponent_data(self, opponent_data):
        """
        Update the opponent's data.
        """
        self.opponent_data = opponent_data

    def is_defeated(self):
        """
        Check if the combatant is defeated.
        """
        return self.health <= 0        
