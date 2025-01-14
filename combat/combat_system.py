import copy
import random
import sys

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
        self.event_counter = 0  # Initialize counter


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

        if self.event_counter == 0:
            for c in self.combatants:
                c.apply_action_state(ACTIONS["idle"], self.timer, self.event_counter, self.distance, copy.copy(self.find_target(c)))
        
        # Filter combatants with valid actions
        combatants_actions = [c.action for c in self.combatants if c.action]
        self.event_counter += 1

        if not combatants_actions:
            self.next_event = None
            print("No valid combatant actions found.")
            return
        
        # print(f"Active combatants: Challenger: {self.combatants[0].action} Defender: {self.combatants[1].action}")

        # Find the action with the earliest time
        # Sort actions happening at the same time based on priority
        action_priority = {
            'off_balance': 1, 'idle': 2, 'reset': 3,
            'move_forward': 4, 'move_backward': 4, 'attack': 5,
            'evading': 6, 'blocking': 7, 'try_evade': 8,
            'try_block': 9, 'recover': 10
        }

        # When actions occur at same time, prioritize the 'completed' actions while using priority order to break ties
        # Sort actions: completed actions first, then pending actions
        completed_actions = [a for a in combatants_actions if a['status'] == 'completed']
        pending_actions = [a for a in combatants_actions if a['status'] != 'completed']
        
        # Sort each group by time and priority
        completed_actions.sort(key=lambda x: (x['time'], action_priority[x['type']]))
        pending_actions.sort(key=lambda x: (x['time'], action_priority[x['type']]))
        
        # Combine the sorted lists with completed actions first
        combatants_actions = completed_actions + pending_actions
        
        # Set next event to first action after sorting
        self.next_event = combatants_actions[0] if combatants_actions else None

        # self.next_event = min(combatants_actions, key=lambda action: action['time'])
        

        print(self.next_event)
        
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
        # self.events.append(copy.deepcopy(self.next_event))

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
            self.process_try_block(combatant, event)
        
        elif action_type == "try_evade":
            self.process_try_evade(combatant, event)
            
        elif action_type == "blocking":
            self.process_blocking(combatant, event)
            
        elif action_type == "evading":
            self.process_evading(combatant, event)
            
        elif action_type == "off_balance":
            self.process_off_balance(combatant, event)
            
        else:
            print(f"Unknown action type: {action_type}")

    def process_attack(self, combatant, event):
        """
        Process an attack action between two combatants.
        """
        target = CombatSystem.find_target(self, combatant)
        event['status'] = "completed"
        event['damage'] = 0
        combatant.stamina -= ACTIONS["attack"]["stamina_cost"]
        if combatant.range < self.distance:
            event['result'] = "missed"
            # print(f"{combatant.name}'s attack missed! Target not in range.")
            applied_action_combatant = combatant.apply_action_state(ACTIONS["off_balance"], self.timer, self.event_counter, self.distance, copy.copy(self.find_target(combatant)))
            self.events.append(applied_action_combatant)
        else:
            if target.action['type'] == "blocking":
                event['result'] = "blocked"
                event['target'] = target
                self.processed_action_log(combatant, event, targeted=True)

                applied_action_target = target.apply_action_state(ACTIONS["reset"], self.timer, self.event_counter, self.distance, copy.copy(self.find_target(combatant)))
                self.events.append(applied_action_target)
                
                applied_action_combatant = combatant.apply_action_state(ACTIONS["off_balance"], self.timer, self.event_counter, self.distance, copy.copy(self.find_target(combatant)))
                self.events.append(applied_action_combatant)
                # print(f"{combatant.name}'s attack was blocked by {target.name}. at {self.timer}")
            elif target.action['type'] == "evading":
                event['result'] = "evaded"
                self.processed_action_log(combatant, event, targeted=True)

                applied_action_target = target.apply_action_state(ACTIONS["reset"], self.timer, self.event_counter, self.distance, copy.copy(self.find_target(combatant)))
                self.events.append(applied_action_target)
                
                combatant.apply_action_state(ACTIONS["off_balance"], self.timer, self.event_counter, self.distance, copy.copy(self.find_target(combatant)))
                self.events.append(applied_action_combatant)
                # print(f"{combatant.name}'s attack was evaded by {target.name}.")
            else:
                damage = random.randint(combatant.attack_power * combatant.accuracy // 100, combatant.attack_power)
                target.health = max(0, target.health - damage)
                event['result'] = "hit"
                event['damage'] = damage
                self.processed_action_log(combatant, event, targeted=True)
                
                # Upon getting hit, the target is reset
                applied_action_target = target.apply_action_state(ACTIONS["off_balance"], self.timer, self.event_counter, self.distance, copy.copy(self.find_target(combatant)))
                self.events.append(applied_action_target)

                applied_action_combatant = combatant.apply_action_state(ACTIONS["reset"], self.timer, self.event_counter, self.distance, copy.copy(self.find_target(combatant)))
                self.events.append(applied_action_combatant)
                # print(f"{combatant.name} attacked {target.name} for {damage} damage (rem HP: {target.health}).")
        
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
        self.processed_action_log(combatant, event, targeted=False)
        # print(f"{combatant.name} moved forward (dist: {self.distance}) at {self.timer}")

        # Schedule recovery for the combatant
        applied_action_combatant = combatant.apply_action_state(ACTIONS["reset"], self.timer, self.event_counter, self.distance, copy.copy(self.find_target(combatant)))
        self.events.append(applied_action_combatant)

    def process_move_backward(self, combatant, event):
        """
        Process a move backward action for a combatant.
        """
        event['status'] = "completed"
        combatant.stamina -= ACTIONS["move_backward"]["stamina_cost"]
        self.distance = min(600, self.distance + combatant.mobility)
        self.processed_action_log(combatant, event, targeted=False)
        # print(f"{combatant.name} moved backward (dist: {self.distance}) at {self.timer}")

        # Schedule recovery for the combatant
        applied_action_combatant = combatant.apply_action_state(self.timer, self.event_counter, ACTIONS["reset"])
        self.events.append(applied_action_combatant)

    def process_recovery(self, combatant, event):
        """
        Process a recovery action for a combatant.
        """
        event['status'] = "completed"
        combatant.stamina = min(combatant.max_stamina, combatant.stamina + combatant.stamina_recovery)
        self.processed_action_log(combatant, event, targeted=False)
        # print(f"{combatant.name} recovered stamina ({combatant.stamina}) at {self.timer}")

        # Schedule the next action for the combatant
        decision = combatant.decide_action(self.timer, self.event_counter, self.distance, copy.copy(self.find_target(combatant)))
        self.events.append(decision)
    
    def process_idle(self, combatant, event):
        """
        Process an idle action for a combatant.
        """
        event['status'] = "completed"
        self.processed_action_log(combatant, event, targeted=False)
        # print(f"{combatant.name} idled at {self.timer}")

        # Schedule the next action for the combatant
        decision = combatant.decide_action(self.timer, self.event_counter, self.distance, copy.copy(self.find_target(combatant)))
        self.events.append(decision)
    
    def process_reset(self, combatant, event):
        """
        Process a reset action for a combatant.
        """
        event['status'] = "completed"
        self.processed_action_log(combatant, event, targeted=False)
        # print(f"{combatant.name} reset at {self.timer}")

        # Schedule the next action for the combatant
        decision = combatant.decide_action(self.timer, self.event_counter, self.distance, copy.copy(self.find_target(combatant)))
        self.events.append(decision)
    
    def process_try_block(self, combatant, event):
        """
        Process a block action for a combatant.
        """
        event['status'] = "completed"
        combatant.stamina -= ACTIONS["try_block"]["stamina_cost"]
        self.processed_action_log(combatant, event, targeted=False)
        # print(f"{combatant.name} tried to block at {self.timer}")

        # Start the blocking action
        blocking_action = copy.copy(ACTIONS["blocking"])
        blocking_action["time"] = combatant.blocking_ability
        applied_action_combatant = combatant.apply_action_state(blocking_action, self.timer, self.event_counter, self.distance, copy.copy(self.find_target(combatant)))
        self.events.append(applied_action_combatant)
        # print(f"{combatant.name} started blocking at {self.timer} with {combatant.blocking_ability} duration")
    
    def process_blocking(self, combatant, event):
        """
        Process a blocking action for a combatant.
        """
        event['status'] = "completed"
        self.processed_action_log(combatant, event, targeted=False)
        # print(f"{combatant.name} stopped blocking at {self.timer}")

        # Schedule recovery for the combatant
        applied_action_combatant = combatant.apply_action_state(ACTIONS["reset"], self.timer, self.event_counter, self.distance, copy.copy(self.find_target(combatant)))
        self.events.append(applied_action_combatant)

    def process_try_evade(self, combatant, event):
        """
        Process an evade action for a combatant.
        """
        event['status'] = "completed"
        combatant.stamina -= ACTIONS["try_evade"]["stamina_cost"]
        self.processed_action_log(combatant, event, targeted=False)
        # print(f"{combatant.name} tried to evade at {self.timer}")

        # Start the evading action
        evading_action = copy.copy(ACTIONS["evading"])
        evading_action["time"] = combatant.evading_ability
        applied_action_combatant = combatant.apply_action_state(evading_action, self.timer, self.event_counter, self.distance, copy.copy(self.find_target(combatant)))
        self.events.append(applied_action_combatant)
        # print(f"{combatant.name} started evading at {self.timer} with {combatant.evading_ability} duration")
    
    def process_evading(self, combatant, event):
        """
        Process an evading action for a combatant.
        """
        event['status'] = "completed"
        self.processed_action_log(combatant, event, targeted=False)
        # print(f"{combatant.name} stopped evading at {self.timer}")

        # Schedule recovery for the combatant
        applied_actions_combatant = combatant.apply_action_state(ACTIONS["reset"], self.timer, self.event_counter, self.distance, copy.copy(self.find_target(combatant)))
        self.events.append(applied_actions_combatant)

    def process_off_balance(self, combatant, event):
        """
        Process an off-balance action for a combatant.
        """
        event['status'] = "completed"
        self.processed_action_log(combatant, event, targeted=False)
        # print(f"{combatant.name} is off-balance at {self.timer}")

        # Schedule recovery for the combatant
        applied_action_combatant = combatant.apply_action_state(ACTIONS["reset"], self.timer, self.event_counter, self.distance, copy.copy(self.find_target(combatant)))
        self.events.append(applied_action_combatant)

    def processed_action_log(self, combatant, event, targeted=False):
        """
        Append a log entry to the battle log.
        """
        target = None
        if targeted:
            target = event['target']
            
        self.log_event(
                timestamp=self.timer,
                event_number=self.event_counter + 1,
                timeend=event['time'],
                combatant=combatant,
                action=event['type'],
                distance=self.distance,
                status=event['status'],
                target=target,
                result=event['result'] if 'result' in event else None,
                damage=event['damage'] if 'damage' in event else None,
            )

        
    def log_event(
        self,
        event_number, 
        timestamp,
        timeend, 
        combatant, 
        action,
        distance,
        status, 
        target=None, 
        result=None,
        damage=None, 
        # **kwargs
    ):
        """
        Logs a combat event with all details for front-end display.

        :param timestamp: The time of the event in milliseconds.
        :param combatant: The combatant performing the action.
        :param action: The action type (e.g., attack, evade).
        :param target: The target of the action (if applicable).
        :param result: The result of the action (e.g., hit, miss, blocked).
        :param kwargs: Additional details about the event (e.g., damage, distance).
        """
        if not combatant:
            return
        # if action == "attack":
        #     print(f"{combatant.name} attacked {target.name} for {damage} damage.")
        #     # sys.exit(1)
            
        log = {
            "timestamp": timestamp,
            "event_number": event_number,
            "timeend": timeend,
            "combatant": {
                "name": combatant.name,
                "health": combatant.health,
                "stamina": combatant.stamina
            } if combatant else None,
            "action": action,
            "distance": distance,
            "status": status,
            "target": {
                "name": target.name if target else None,
                "health": target.health if target else None,
                "stamina": target.stamina if target else None
            },
            "result": result,
            "damage": damage,
            # "details": kwargs  # Additional information like damage, distance, etc.
        }
        self.events.append(log)
        
    def replay_log(self):
        """
        Replay the battle log, presenting each action in a human-readable format.
        """
        print("\n--- Battle Replay ---\n")
        # print(self.events)
        for log in self.events:
            print(f"{log['event_number']}: {log["action"]} at {log["timestamp"]} is {log["status"]}")
        for log in self.events:
            # Build the replay message
            if log["status"] == "completed":
                message = self.message_for_completed_event(log)
                
            else:
                message = self.message_for_pending_event(log)
                
                
            # Print the formatted message
            print(message)

        print("\n--- Replay Complete ---\n")

    def message_for_completed_event(self, log):
        timestamp = log["timestamp"]
        timeend = log["timeend"]
        combatant = log["combatant"]
        target = log["target"]
        action = log["action"]
        result = log["result"]
        distance = log["distance"]
        status = log["status"]
        damage = log.get("damage", None)

        message = f"[{timestamp}ms] {combatant['name']} "

        if action == "attack":                    
            if result == "hit":
                message += f"attacked {target['name']} for {damage} damage (remaining HP: {target['health']})."
            elif result == "blocked":
                message += f"attacked {target['name']}, but the attack was blocked."
            elif result == "evaded":
                message += f"attacked {target['name']}, but the attack was evaded."
            else:
                message += f"attempted an attack, but missed."

        elif action == "move_forward":
            message += f"moved forward, reducing the distance to {distance}."

        elif action == "move_backward":
            message += f"moved backward, increasing the distance to {distance}."

        elif action == "recover":
            message += f"recovered stamina, now at {combatant['stamina']}."

        elif action == "try_block":
            message += f"started a blocking stance."

        elif action == "try_evade":
            message += f"started an evasive stance."

        elif action == "blocking":
            message += f"stopped blocking."

        elif action == "evading":
            message += f"stopped evading."

        elif action == "idle":
            message += f"took no action ({combatant["stamina"]} left)."

        elif action == "reset":
            message += f"reset his position and balance."
        
        elif action == "off_balance":
            message += f"got off-balance and has yet to reset."

        elif action == "added_to_battle":
            message += f"was added to the battle."

        elif action == "battle_end":
            message = f"Battle ended after {timestamp}ms."

        message += f" [{status}]"
        return message
    
    def message_for_pending_event(self, log):
        timestamp = log["timestamp"]
        timeend = log["timeend"]
        combatant = log["combatant"]
        target = log["target"]
        action = log["action"]
        result = log["result"]
        distance = log["distance"]
        status = log["status"]
        damage = log.get("damage", None)

        message = f"[{timestamp}ms] {combatant['name']} "

        if action == "attack":                    
            message += f"is attempting an attack which will land in {timeend}ms."

        elif action == "move_forward":
            message += f"is attempting to move forward which will be completed in {timeend}ms."

        elif action == "move_backward":
            message += f"is attempting to move backward which will be completed in {timeend}ms."

        elif action == "recover":
            message += f"is attempting to recover stamina which will be completed in {timeend}ms."

        elif action == "try_block":
            message += f"started a blocking stance which will block attacks in {timeend}ms."

        elif action == "try_evade":
            message += f"started an evasive stance which will evade attacks in {timeend}ms."

        # elif action == "blocking":
        #     message += f"stopped blocking."

        # elif action == "evading":
        #     message += f"stopped evading."

        elif action == "idle":
            message += f"is undecided."

        elif action == "reset":
            message += f"is resetting his position and balance."
        
        elif action == "off_balance":
            message += f"is off-balance"
        
        message += f" [{status}]"
        return message

            
    def is_battle_over(self):
        """
        Check if the battle is over.
        """
        if self.timer >= self.duration:
            return True

        active_combatants = [c for c in self.combatants if not c.is_defeated()]
        return len(active_combatants) <= 1