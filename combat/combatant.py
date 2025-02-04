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
        """Initialize a combatant."""
        self.combatant_id = combatant_id
        self.name = name
        self.health = health
        self.stamina = stamina
        self.max_stamina = stamina
        self.max_health = health
        self.attack_power = attack_power
        self.accuracy = accuracy
        self.blocking_power = blocking_power
        self.evading_ability = evading_ability
        self.mobility = mobility
        self.range = (range_a, range_b)
        self.perception = perception
        self.stealth = stealth
        self.stamina_recovery = stamina_recovery
        self.action = None
        self.position = position
        self.facing = facing
        self.opponent = opponent
        self.team = None

class TestCombatant(Combatant):
    __test__ = False
    
    def force_action(self, action_type, timer=0, event_counter=0, distance=0):
        """Force a specific action to occur at a given time."""
        # Deduct stamina cost when forcing an action
        if action_type in ACTIONS:
            stamina_cost = ACTIONS[action_type]["stamina_cost"]
            self.stamina = max(0, self.stamina - stamina_cost)
            
        action = self.create_action(action_type, timer)
        self.action = action
        return action

    def create_action(self, action_type, timer, target=None):
        """Create standardized action dictionary."""
        if action_type not in ACTIONS:
            raise ValueError(f"Invalid action type: {action_type}")
            
        # For blocking and evading, use current timer to maintain state
        if action_type in ["blocking", "evading"]:
            time = timer
        else:
            # For all other actions, add their duration to current timer
            time = timer + ACTIONS[action_type]["time"]
            
        return {
            "type": action_type,
            "time": time,
            "combatant": self,
            "status": "pending",
            "target": target
        }

    def decide_action(self, timer, event_counter, distance):
        """
        Decide the next action based on the current state.
        This should be a decision tree or a policy network. For now, we will use a simple rule-based system.
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
        
        # Deduct stamina cost when deciding an action
        if action["type"] in ACTIONS:
            stamina_cost = ACTIONS[action["type"]]["stamina_cost"]
            self.stamina = max(0, self.stamina - stamina_cost)
            
        self.action = action
        return action

    def decide_attack_action(self, timer, event_counter, distance):
        """
        Decide whether to release or stop the attack.
        """
        action = self.create_action("release_attack", timer)
        # No stamina cost for release_attack as it's part of the try_attack chain
        self.action = action
        return action
    
    def decide_block_action(self, timer, event_counter, distance):
        """
        Decide whether to keep blocking or stop blocking.
        """
        # Check if we have enough stamina to continue blocking
        if self.stamina >= ACTIONS["keep_blocking"]["stamina_cost"]:
            # Create keep_blocking action with stamina cost
            action = self.create_action("keep_blocking", timer)
            self.stamina = max(0, self.stamina - ACTIONS["keep_blocking"]["stamina_cost"])
        else:
            # Not enough stamina, must stop blocking
            action = self.create_action("idle", timer)
        
        self.action = action
        return action

    def apply_action_state(self, action_type, timer, event_counter, distance):
        """
        Update the action status after each event.
        """
        # Deduct stamina cost when applying an action state
        if action_type in ACTIONS:
            stamina_cost = ACTIONS[action_type]["stamina_cost"]
            self.stamina = max(0, self.stamina - stamina_cost)
            
        self.action = self.create_action(action_type, timer)
        return self.action
    
    def get_available_actions(self):
        """Get a list of actions the combatant can perform based on constraints."""
        return [action for action in ACTIONS if self.can_perform_action(action)]

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

    def is_within_range(self, distance):
        """Check if the opponent is within range."""
        return self.range[0] <= distance <= self.range[1]       

    def is_facing_opponent(self, opponent):
        """Check if the combatant is facing the opponent."""
        return self.facing == opponent.position
    
    def is_defeated(self):
        """Check if the combatant is defeated."""
        return self.health <= 0

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
