class Combatant:
    def __init__(self, name, health, attack_power, team):
        """
        Initialize a combatant.
        """
        self.name = name
        self.health = health
        self.attack_power = attack_power
        self.team = team
        self.action = None  # Current or next action

    def is_defeated(self):
        """
        Check if the combatant is defeated.
        """
        return self.health <= 0

    def decide_action(self, timer):
        """
        Decide the next action based on the current state.
        
        :param timer: Current battle time.
        """
        if self.is_defeated():
            return
        
        # if self.action["type"] == "recover":
        #     return

        # Example: Attack if possible
        self.action = {
            "time": timer + 300,  # Attack happens 300ms from now
            "type": "attack",
            "combatant": self,
            "target": None,
            "status": "pending",
        }

    def update_action(self, timer, _action):
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
