class Combatant:
    def __init__(self, name, health, attack_power, mobility, range, team):
        """
        Initialize a combatant.
        """
        self.name = name
        self.health = health
        self.attack_power = attack_power
        self.mobility = mobility # movement speed (fixed)
        self.range = range # attack range (fixed)
        self.team = team
        self.action = None  # Current or next action

    def is_defeated(self):
        """
        Check if the combatant is defeated.
        """
        return self.health <= 0

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
        if self.is_defeated():
            return

        # Example: Attack if possible
        if distance <= self.range:
            if distance + self.mobility <= self.range:
                self.action = {
                    "time": timer + 50,  # Move forward happens 50ms from now
                    "type": "move_backward",
                    "combatant": self,
                    "target": None,
                    "status": "pending",
                }
            else:
                self.action = {
                    "time": timer + 300,  # Attack happens 300ms from now
                    "type": "attack",
                    "combatant": self,
                    "target": None,
                    "status": "pending",
                }
        elif distance > self.range:
            self.action = {
                "time": timer + 50,  # Move forward happens 50ms from now
                "type": "move_forward",
                "combatant": self,
                "target": None,
                "status": "pending",
            }

    def apply_action_state(self, timer, _action):
        """
        Update the action status after each event.
        """
        self.action = {
            "time": timer + _action["time"],
            "type": _action["type"],
            "combatant": _action["combatant"],
            "target": _action["target"],
            "status": "pending",
        }        
