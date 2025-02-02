import random

from combat.lib.actions_library import ACTIONS

class CombatSystem:
    # Initialize the combat system
    def __init__(self, duration, distance, max_distance):
        self.timer = 0
        self.duration = duration
        self.combatants = []
        self.distance = distance
        self.max_distance = max_distance
        self.events = []
        self.next_event = None
        self.event_counter = 0

    # Add a combatant to the battle
    def add_combatant(self, combatant):
        if len(self.combatants) >= 2:
            raise ValueError("Battle is full.")
        
        if not combatant:
            raise ValueError("Invalid combatant.")
        else:         
            combatant.team = "challenger" if len(self.combatants) == 0 else "defender"
            if len(self.combatants) == 0:
                combatant.team = "challenger"
            else:
                combatant.team = "defender"
                if self.combatants[0].combatant_id == combatant.combatant_id:
                    raise ValueError("Combatant already added to the battle.")
            self.combatants.append(combatant)

    # Start the battle
    def get_opponent_data(self, combatant, assumed_opponent):
        combatant.opponent = assumed_opponent

    # Determine the next event according to the time and priority
    def determine_next_event(self):
        combatants_actions = [c.action for c in self.combatants if c.action]
        self.event_counter += 1

        if not combatants_actions:
            self.next_event = None
            print("No valid combatant actions found.")
            raise ValueError("No valid combatant actions found.")

        status_priority = {'completed': 0, 'pending': 1}
        action_priority = {
            # NEUTRAL actions
            'idle': 1, # Final action in the chain
            'reset': 2, # Pre-final action in the chain succeeded by idle
            'recover': 3, # Pre-final action in the chain succeeded by idle
            'off_balance': 4, # Succeeded by reset and then idle

            # MOVEMENT actions
            'move_forward': 5, # Final action in the chain
            'move_backward': 6, # Final action in the chain
            'turn_around': 7, # Final action in the chain

            # DEFENSE actions
            'try_block': 8, # Pre-final action in the chain succeeded by blocking
            'blocking': 9, # Final action in the blocking action chain
            'keep_blocking': 10, # Pre-final action in the chain succeeded by blocking

            # EVASION actions
            'try_evade': 11,
            'evading': 12,

            # ATTACK actions
            'try_attack': 13,
            'release_attack': 14,
            'stop_attack': 15
        }

        combatants_actions.sort(key=lambda x: (
            x['time'], status_priority[x['status']], action_priority[x['type']]
        ))

        self.next_event = combatants_actions[0] if combatants_actions else None
        # print(f"Next event: {self.next_event} ({self.next_event['time']}ms) with #{self.event_counter} by {self.next_event['combatant'].name}")

    # Update the battle state
    def update(self):
        if not self.next_event:
            return

        self.timer = self.next_event['time']
        self.process_event(self.next_event)
        self.determine_next_event()

    # Process the event
    def process_event(self, event):
        combatant = event['combatant']
        action_type = event['type']
        process_method = getattr(self, f"process_{action_type}", None)
        if process_method:
            process_method(combatant, event)
        else:
            print(f"Unknown action type: {action_type}")

    # Method to find the target for targeting actions
    def find_target(self, combatant):
        for potential_target in self.combatants:
            if potential_target.team != combatant.team and not potential_target.is_defeated():
                return potential_target
        return None
    
    # GENERIC actions processing
    
    # Method to mark the action as completed and log the event
    def mark_action_as_completed(self, combatant, event):
        event['status'] = "completed"
        self.processed_action_log(combatant, event)
        
    # Method to process the actions which are final in the action chain
    def process_action(self, combatant, event, action_key, targeted=False):
        self.mark_action_as_completed(combatant, event)
        if action_key == "idle":
            decision = combatant.decide_action(self.timer, self.event_counter, self.distance)
            self.events.append(decision)
            self.update_opponent_perception(combatant)
        else:
            self.apply_action(combatant, "idle")
        
    # Method to automatically apply the action state to the combatant
    def apply_action(self, combatant, action_type):
        self.events.append(combatant.apply_action_state(action_type, self.timer, self.event_counter, self.distance))
        self.update_opponent_perception(combatant)

    # NEUTRAL actions processing
    def process_idle(self, combatant, event):
        self.process_action(combatant, event, "idle")

    def process_reset(self, combatant, event):
        self.process_action(combatant, event, "reset")

    def process_recover(self, combatant, event):
        combatant.stamina = min(combatant.max_stamina, combatant.stamina + combatant.stamina_recovery)
        self.process_action(combatant, event, "recover")

    def process_off_balance(self, combatant, event):
        # Off-balance combatants will have to reset their position and balance
        # Chain the reset action after the off-balance action
        self.mark_action_as_completed(combatant, event)
        self.apply_action(combatant, "reset")
    
    # MOVEMENT actions processing
    def process_turn_around(self, combatant, event):
        combatant.facing = "right" if combatant.facing == "left" else "left"
        self.process_action(combatant, event, "turn_around")

    def process_move_forward(self, combatant, event):
        self.distance = max(0, self.distance - combatant.mobility)
        self.process_action(combatant, event, "move_forward")

    def process_move_backward(self, combatant, event):
        self.distance = min(self.max_distance, self.distance + combatant.mobility)
        self.process_action(combatant, event, "move_backward")

    # DEFENSE actions processing
    def process_try_block(self, combatant, event):
        # Mark the action as completed and apply the blocking action
        # The try_block always resolve to a blocking action unless interrupted
        # with an applied (forced) action
        self.mark_action_as_completed(combatant, event)
        self.apply_action(combatant, "blocking")
        
    def process_blocking(self, combatant, event):
        self.mark_action_as_completed(combatant, event)
        
        # Resolving blocking action will not go through the process_action method
        # as it is not the final action in the blocking action chain for the combatant
        # Instead, the combatant will have to decide whether to keep blocking or stop blocking
        decision = combatant.decide_block_action(self.timer, self.event_counter, self.distance)
        self.events.append(decision)

    def process_keep_blocking(self, combatant, event):
        # Mark the action as completed and apply the blocking action
        self.mark_action_as_completed(combatant, event)
        self.apply_action(combatant, "blocking")
        
    # EVASION actions processing
    def process_try_evade(self, combatant, event):
        # Mark the action as completed and apply the evading action
        # The try_evade always resolve to an evading action unless interrupted
        # with an applied (forced) action
        self.mark_action_as_completed(combatant, event)
        self.apply_action(combatant, "evading")

    def process_evading(self, combatant, event):
        # Unlike blocking, evading is a one-time action and the combatant will
        # not have the option to keep evading
        self.process_action(combatant, event, "evading")

    # ATTACK actions processing
    def process_try_attack(self, combatant, event):
        self.mark_action_as_completed(combatant, event)
        
        # Resolving try_attack action will not go through the process_action method
        # as it is not the final action in the attack action chain for the combatant
        # Instead, the combatant will have to decide whether to release or stop the attack
        decision = combatant.decide_attack_action(self.timer, self.event_counter, self.distance)
        self.events.append(decision)

    # Method to process the release of an attack
    def process_release_attack(self, combatant, event):
        # Check if the target is within range of the attack
        if not combatant.is_within_range(self.distance):
            # Mark the attack event as missed
            event['result'] = "missed"
            # Mark the action as completed and log the event
            self.mark_action_as_completed(combatant, event)
            # Apply the reset action to the combatant as a consequence of the missed attack
            self.apply_action(combatant, "off_balance")
        else:
            # Since the target is within range, the attack shall be resolved to by handle_attack
            self.handle_attack_hit(combatant, event)

    def handle_attack_hit(self, combatant, event):
        # Get the target for the attack
        target = self.find_target(combatant)
        # If the attack is BLOCKED
        if target.action['type'] == "blocking": # Resolve in handle_blocking method
            self.handle_blocking(combatant, target, event)
        # If the attack is EVADED
        elif target.action['type'] == "evading": # Resolve in handle_evading method
            # Mark the attack event as evaded
            event['result'] = "evaded"
            
            #Mark the action as completed and log the event
            self.mark_action_as_completed(combatant, event)
            
            # Apply the reset action to the target which opens up an opportunity for the target to perform
            # a counter-attack or any other action first
            self.apply_action(target, "reset")
            
            # Apply the off_balance action to the combatant as a consequence of the evaded attack
            self.apply_action(combatant, "off_balance")
        # If the attack HITS
        else:
            # Calculate the damage dealt by the attack
            damage = random.randint(combatant.attack_power * combatant.accuracy // 100, combatant.attack_power)
            
            # Apply the damage to the target
            target.health = max(0, target.health - damage)
            
            # Mark the attack event as hit
            event['result'] = "hit"
            
            # Set the damage dealt by the attack in the event
            event['damage'] = damage
            
            # Mark the action as completed and log the event
            self.mark_action_as_completed(combatant, event)
            
            # Apply the reset action to the target as a consequence of being hit
            self.apply_action(target, "reset")
            
            # Apply the reset action to the combatant
            self.apply_action(combatant, "reset")
    
    # Method to handle the blocking action
    def handle_blocking(self, combatant, target, event):
        # Mark the attack event as blocked
        event['result'] = "blocked"
        
        # Calculate the damage dealt by the attack
        damage = random.randint(combatant.attack_power * combatant.accuracy // 100, combatant.attack_power)
        event['damage'] = damage
        
        # If the damage is less than or equal to the target's blocking power
        if damage <= target.blocking_power:
            
            # Apply the reset action to the target
            self.apply_action(target, "reset")
            
            # Apply the reset action to the combatant as a consequence of the blocked attack
            self.apply_action(combatant, "off_balance")
            
        # If the damage is greater than the target's blocking power
        else:
            # Mark the attack event as breached
            event['result'] = "breached"
            
            # Apply the reset action to the target and the combatant
            self.apply_action(target, "reset")
            self.apply_action(combatant, "reset")
            
            # Calculate the breach damage and apply it to the target's health
            breach_damage = damage - target.blocking_power
            target.health = max(0, target.health - breach_damage)
        
        # Update the blocking power of the target after the attack was blocked
        target.blocking_power = max(0, target.blocking_power - damage)
        
        # Mark the action as completed and log the event
        self.mark_action_as_completed(combatant, event)

    # Method to handle the stopping of an attack
    def process_stop_attack(self, combatant, event):
        self.process_action(combatant, event, "stop_attack")
        
    # OPPONENT PERCEPTION
    def update_opponent_perception(self, combatant):
        opponent = self.find_target(combatant)
        opponent.update_combatant_perception(combatant.action)

    # LOGGING
    def processed_action_log(self, combatant, event, targeted=False):
        self.log_event(
            timestamp=self.timer,
            event_number=self.event_counter + 1,
            timeend=event['time'],
            combatant=combatant,
            action=event['type'],
            distance=self.distance,
            status=event['status'],
            target=combatant.opponent if targeted else None,
            result=event.get('result'),
            damage=event.get('damage')
        )

    def log_event(self, event_number, timestamp, timeend, combatant, action, distance, status, target=None, result=None, damage=None):
        if not combatant:
            return
        log = {
            "timestamp": timestamp,
            "event_number": event_number,
            "timeend": timeend,
            "combatant": {
                "name": combatant.name,
                "health": combatant.health,
                "stamina": combatant.stamina
            },
            "action": action,
            "distance": distance,
            "status": status,
            "target": {
                "name": target.name if target else None,
                "health": target.health if target else None,
                "stamina": target.stamina if target else None
            },
            "result": result,
            "damage": damage
        }
        self.events.append(log)

    # REPLAY
    def replay_log(self):
        print("\n--- Battle Replay ---\n")
        sorted_events = sorted(self.events, key=lambda x: (
            x['timestamp'], 1 if x['status'] == 'pending' else 0, x['event_number']
        ))
        for log in sorted_events:
            message = self.message_for_completed_event(log) if log["status"] == "completed" else self.message_for_pending_event(log)
            if message:
                print(message)
        print("\n--- Replay Complete ---\n")

    def message_for_completed_event(self, log):
        timestamp = log["timestamp"]
        combatant = log["combatant"]
        target = log["target"]
        action = log["action"]
        result = log["result"]
        distance = log["distance"]
        damage = log.get("damage", None)

        message = f"[{timestamp}ms] {combatant['name']} "
        if action == "try_attack":
            message += "attempted an attack."
        elif action == "release_attack":
            if result == "hit":
                message += f"attacked {target['name']} for {damage} damage (remaining HP: {target['health']})."
            elif result == "blocked":
                message += f"attacked {target['name']}, but the attack was blocked."
            elif result == "breached":
                message += f"attacked {target['name']}, and breached his defenses (remaining HP: {target['health']})."
            elif result == "evaded":
                message += f"attacked {target['name']}, but the attack was evaded."
            else:
                message += "attempted an attack, but missed."
        elif action == "stop_attack":
            message += "stopped an attack."
        elif action == "move_forward":
            message += f"moved forward, reducing the distance to {distance}."
        elif action == "move_backward":
            message += f"moved backward, increasing the distance to {distance}."
        elif action == "recover":
            message += f"recovered stamina, now at {combatant['stamina']}."
        elif action == "try_block":
            message += "started a blocking stance."
        elif action == "try_evade":
            message += "started an evasive stance."
        elif action == "blocking":
            message += "stopped blocking."
        elif action == "keep_blocking":
            message += "kept blocking."
        elif action == "evading":
            message += "stopped evading."
        elif action == "turn_around":
            message += "turned around."
        elif action == "idle":
            message += f"took no action ({combatant['stamina']} left)."
        elif action == "reset":
            message += "reset his position and balance."
        elif action == "off_balance":
            message += "got off-balance and has yet to reset."
        elif action == "added_to_battle":
            message += "was added to the battle."
        elif action == "battle_end":
            message = f"Battle ended after {timestamp}ms."
        message += f" [{log['status']}]"
        return message

    def message_for_pending_event(self, log):
        timestamp = log["timestamp"]
        combatant = log["combatant"]
        action = log["action"]
        timeend = log["timeend"]

        message = f"[{timestamp}ms] {combatant['name']} "
        if action == "try_attack":
            message += f"is attempting an attack which will be released/stopped in {timeend}ms."
        elif action == "release_attack":
            message += f"is releasing an attack which will land in {timeend}ms."
        elif action == "stop_attack":
            message += f"is stopping an attack which will be completed in {timeend}ms."
        elif action == "move_forward":
            message += f"is attempting to move forward which will be completed in {timeend}ms."
        elif action == "move_backward":
            message += f"is attempting to move backward which will be completed in {timeend}ms."
        elif action == "recover":
            message += f"is attempting to recover stamina which will be completed in {timeend}ms."
        elif action == "try_block":
            message += f"decided to block attacks starting {timeend}ms."
        elif action == "try_evade":
            message += f"started an evasive stance which will evade attacks in {timeend}ms."
        elif action == "blocking":
            message += "is blocking."
        elif action == "keep_blocking":
            message += "decided to keep blocking."
        elif action == "turn_around":
            message += "is going to turn around."
        elif action == "idle":
            message += "is idling."
        elif action == "reset":
            message += "is resetting his position and balance."
        elif action == "off_balance":
            message += "is off-balance"
        message += f" [{log['status']}]"
        return message

    # BATTLE CONTROL
    def is_battle_over(self):
        if self.timer >= self.duration:
            return True
        active_combatants = [c for c in self.combatants if not c.is_defeated()]
        return len(active_combatants) <= 1