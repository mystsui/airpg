from combat.lib.actions_library import ACTIONS

class Combatant:
    def __init__(
        self,
        combatant_id, 
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
        self.combatant_id = combatant_id
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
        # self.action = {"type": "idle", "combatant": self, "time": ACTIONS["idle"]["time"], "status": "pending", "target": None}
        self.action = None # current action
        self.position = position # current position
        self.facing = facing # current facing
        self.opponent = opponent

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
        self.deduct_stamina(action["type"])
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

        # if self.is_within_range(distance) and "release_attack" in available_actions:
        #     action = self.create_action("release_attack", timer)
        # elif "stop_attack" in available_actions:
        #     action = self.create_action("stop_attack", timer)
        # else:
        #     action = self.create_action("idle", timer)

        action = self.create_action("release_attack", timer)  # Changed to release_attack
        
        self.action = action
        self.deduct_stamina(action["type"])
        log = self.decision_applied_log(timer, event_counter, distance)
        return log
    
    def decide_block_action(self, timer, event_counter, distance):
        """
        Decide the next action based on the current state.
        This should be a decision tree or a policy network. For now, we will use a simple rule-based system.

        :param timer: Current battle time.
        :param distance: Current distance between combatants.
        :param opponent: Opponent combatant object (read-only for action type).
        """
        available_actions = self.get_available_actions()

        if "keep_blocking" in available_actions:
            action = self.create_action("keep_blocking", timer)
        else:
            action = self.create_action("idle", timer)
        
        self.action = action
        self.deduct_stamina(action["type"])
        log = self.decision_applied_log(timer, event_counter, distance)
        return log

    def apply_action_state(self, action_type, timer, event_counter, distance):
        """
        Update the action status after each event.
        """
        self.action = self.create_action(action_type, timer)
        log = self.decision_applied_log(timer, event_counter + 1, distance)
        return log
    
    def deduct_stamina(self, action_type):
        """Deduct stamina based on the action type."""
        self.stamina -= ACTIONS[action_type]["stamina_cost"]

    def decision_applied_log(self, timer, event_counter, distance):
        """
        Prepare the decision log for the combatant with enhanced AI training data.
        """
        # Get action history from previous events
        actor_history = []
        opponent_history = []
        if hasattr(self, 'previous_actions'):
            actor_history = self.previous_actions[-3:]  # Last 3 actions
        if self.opponent and hasattr(self.opponent, 'previous_actions'):
            opponent_history = self.opponent.previous_actions[-3:]  # Last 3 actions

        # Update action history
        if not hasattr(self, 'previous_actions'):
            self.previous_actions = []
        self.previous_actions.append(self.action["type"])

        log = {
            "event_id": f"{timer}_{event_counter + 1}_{self.name}",
            "timestamp": timer,
            "sequence_number": event_counter + 1,
            "timeend": self.action["time"],
            "pre_state": {
                "actor": {
                    "name": self.name,
                    "health_ratio": self.health / self.max_health,
                    "stamina_ratio": self.stamina / self.max_stamina,
                    "position": self.position,
                    "facing": self.facing,
                    "blocking_power": self.blocking_power,
                    "current_action": self.action["type"]
                },
                "opponent": {
                    "name": self.opponent.name if self.opponent else None,
                    "health_ratio": self.opponent.health / self.opponent.max_health if self.opponent else None,
                    "stamina_ratio": self.opponent.stamina / self.opponent.max_stamina if self.opponent else None,
                    "position": self.opponent.position if self.opponent else None,
                    "facing": self.opponent.facing if self.opponent else None,
                    "blocking_power": self.opponent.blocking_power if self.opponent else None,
                    "current_action": self.opponent.action["type"] if self.opponent and self.opponent.action else None
                } if self.opponent else None,
                "battle_context": {
                    "distance": distance,
                    "max_distance": self.opponent.range[1] if self.opponent else None,
                    "time_remaining": None  # Combat system duration not accessible here
                }
            },
            "action": {
                "type": self.action["type"],
                "timing": {
                    "start": timer,
                    "duration": self.action["time"] - timer,
                    "end": self.action["time"]
                },
                "stamina_cost": ACTIONS[self.action["type"]]["stamina_cost"],
                "in_range": self.is_within_range(distance)
            },
            "result": {
                "status": "pending",
                "outcome": None,
                "damage_dealt": None,
                "state_changes": {
                    "actor_stamina_change": -ACTIONS[self.action["type"]]["stamina_cost"],
                    "opponent_blocking_power_change": None,
                    "opponent_health_change": None,
                    "distance_change": self.mobility if self.action["type"] in ["move_forward", "move_backward"] else 0
                }
            },
            "action_history": {
                "actor_previous": actor_history,
                "opponent_previous": opponent_history
            }
        }
        return log

    def update_combatant_perception(self, opponent_action):
        """
        Update on the combatant's perception the opponent's current action.
        """
        self.opponent.action = opponent_action

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
    
# FOR TESTING PURPOSES
# combatant.py (add to bottom)
class TestCombatant(Combatant):
    __test__ = False  # Add this line
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.forced_actions = []  # Queue of actions to force

    def force_action(self, action_type, timer=0, event_counter=0, distance=0):
        """Force a specific action to occur at a given time."""
        # Create the action before deducting stamina to capture pre-state accurately
        action = self.create_action(action_type, timer)
        
        # Get action history from previous events
        actor_history = []
        opponent_history = []
        if hasattr(self, 'previous_actions'):
            actor_history = self.previous_actions[-3:]  # Last 3 actions
        if self.opponent and hasattr(self.opponent, 'previous_actions'):
            opponent_history = self.opponent.previous_actions[-3:]  # Last 3 actions

        # Create the log before deducting stamina to capture pre-state accurately
        log = {
            "event_id": f"{timer}_{event_counter + 1}_{self.name}",
            "timestamp": timer,
            "sequence_number": event_counter + 1,
            "pre_state": {
                "actor": {
                    "name": self.name,
                    "health_ratio": self.health / self.max_health,
                    "stamina_ratio": self.stamina / self.max_stamina,
                    "position": self.position,
                    "facing": self.facing,
                    "blocking_power": self.blocking_power,
                    "current_action": action_type
                },
                "opponent": {
                    "name": self.opponent.name if self.opponent else None,
                    "health_ratio": self.opponent.health / self.opponent.max_health if self.opponent else None,
                    "stamina_ratio": self.opponent.stamina / self.opponent.max_stamina if self.opponent else None,
                    "position": self.opponent.position if self.opponent else None,
                    "facing": self.opponent.facing if self.opponent else None,
                    "blocking_power": self.opponent.blocking_power if self.opponent else None,
                    "current_action": self.opponent.action["type"] if self.opponent and self.opponent.action else None
                } if self.opponent else None,
                "battle_context": {
                    "distance": distance,
                    "max_distance": self.opponent.range[1] if self.opponent else None,
                    "time_remaining": None  # Combat system duration not accessible here
                }
            },
            "action": {
                "type": action_type,
                "timing": {
                    "start": timer,
                    "duration": action["time"] - timer,
                    "end": action["time"]
                },
                "stamina_cost": ACTIONS[action_type]["stamina_cost"],
                "in_range": self.is_within_range(distance)
            },
            "result": {
                "status": "pending",
                "outcome": None,
                "damage_dealt": None,
                "state_changes": {
                    "actor_stamina_change": -ACTIONS[action_type]["stamina_cost"],
                    "opponent_blocking_power_change": None,
                    "opponent_health_change": None,
                    "distance_change": self.mobility if action_type in ["move_forward", "move_backward"] else 0
                }
            },
            "action_history": {
                "actor_previous": actor_history,
                "opponent_previous": opponent_history
            }
        }
        
        # Update action history and state after creating the log
        if not hasattr(self, 'previous_actions'):
            self.previous_actions = []
        self.previous_actions.append(action_type)
        self.action = action
        self.deduct_stamina(action_type)
        
        return log
