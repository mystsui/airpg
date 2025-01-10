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

    def decide_action(self, timer, target):
        """
        Decide the next action based on the current state.
        
        :param timer: Current battle time.
        :param target: Target combatant.
        """
        if self.is_defeated():
            return

        # Example: Attack if possible
        self.action = {
            "time": timer + 300,  # Attack happens 300ms from now
            "type": "attack",
            "combatant": self,
            "target": target,
            "status": "pending",
        }

    def update_action(self, timer):
        """
        Update the action status after each event.
        """
        if self.action and self.action['time'] <= timer:
            # Clear action after it is processed
            self.action = None

        # If no action is scheduled, decide a new action
        if self.action is None:
            # Decide the next action (attack for now)
            target = self._find_target()  # Add logic to identify the target
            if target:
                self.decide_action(timer, target)

    def _find_target(self):
        """
        Placeholder to find a target.
        """
        # You should pass in a method or logic to determine the current target.
        return None  # Replace with actual target selection logic.
