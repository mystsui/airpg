from combat.lib.actions_library import ACTIONS

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
        range_a,
        range_b, 
        stamina_recovery,
        position,
        facing,
        perception,
        stealth, 
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
        self.range = (range_a, range_b) # attack range (fixed)
        self.perception = perception
        self.stealth = stealth
        self.stamina_recovery = stamina_recovery # stamina recovery rate
        self.action = {"type": "idle", "combatant": self, "time": ACTIONS["idle"]["time"], "status": "pending", "target": None}
        self.position = position # current position
        self.facing = facing # current facing
        self.opponent = opponent

        print(f"{self.name} has been initialized with the position: {self.position} and facing: {self.facing}")

    def create_action(self, action_type, timer, target=None):
        """Create standardized action dictionary."""
        return {
            "type": action_type,
            "time": ACTIONS[action_type]["time"] + timer,
            "combatant": self,
            "status": "pending",
            "target": target
        }

    def can_perform_action(self, action_type):
        """Check if the combatant can perform the given action based on constraints."""
        action = ACTIONS[action_type]
        return self.stamina >= action["stamina_cost"]

    def get_available_actions(self):
        """Get a list of actions the combatant can perform based on constraints."""
        return [action for action in ACTIONS if self.can_perform_action(action)]

    def decide_action(self, timer, event_counter, distance):
        """
        Decide the next action based on the current state.
        This should be a decision tree or a policy network. For now, we will use a simple rule-based system.

        :param timer: Current battle time.
        :param distance: Current distance between combatants.
        :param opponent: Opponent combatant object (read-only for action type).
        """
        available_actions = self.get_available_actions()

        if not self.is_facing_opponent(self.opponent) and "turn_around" in available_actions:
            action = self.create_action("turn_around", timer)
        elif self.is_within_range(distance) and "try_attack" in available_actions:
            action = self.create_action("try_attack", timer, self.opponent)
        elif "move_forward" in available_actions:
            action = self.create_action("move_forward", timer)
        else:
            action = self.create_action("idle", timer)
        
        self.action = action
        log = self.decision_applied_log(timer, event_counter, distance)
        return log

    def decide_attack_action(self, timer, event_counter, distance):
        """
        Decide the next action based on the current state.
        This should be a decision tree or a policy network. For now, we will use a simple rule-based system.

        :param timer: Current battle time.
        :param distance: Current distance between combatants.
        :param opponent: Opponent combatant object (read-only for action type).
        """
        available_actions = self.get_available_actions()

        if self.is_within_range(distance) and "release_attack" in available_actions:
            action = self.create_action("release_attack", timer)
        elif "stop_attack" in available_actions:
            action = self.create_action("stop_attack", timer)
        else:
            action = self.create_action("idle", timer)
        
        self.action = action
        log = self.decision_applied_log(timer, event_counter, distance)
        return log

    def apply_action_state(self, action_type, timer, event_counter, distance):
        """
        Update the action status after each event.
        """
        self.action = self.create_action(action_type, timer)
        log = self.decision_applied_log(timer, event_counter + 1, distance)
        return log

    def decision_applied_log(self, timer, event_counter, distance):
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
                "name": self.opponent.name if self.opponent else None,
                "health": self.opponent.health if self.opponent else None,
                "stamina": self.opponent.stamina if self.opponent else None
            },
            "result": None,
            "damage": None,
        }
        return log

    def update_opponent_action(self, action):
        """
        Update on the combatant's perception the opponent's current action.
        """
        self.opponent["action"] = action

    def update_opponent_data(self, stat, value):
        """
        Get the opponent's data.
        """
        return

    def is_defeated(self):
        """
        Check if the combatant is defeated.
        """
        return self.health <= 0 
    
    def is_within_range(self, distance):
        """
        Check if the opponent is within range.
        """
        return self.range[0] <= distance <= self.range[1]       

    def is_facing_opponent(self, opponent):
        """
        Check if the combatant is facing the opponent.
        """
        return self.facing == opponent.position