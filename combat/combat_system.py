import random

from combat.lib.actions_library import ACTIONS

class CombatSystem:
    def __init__(self, duration, distance, max_distance):
        self.timer = 0
        self.duration = duration
        self.combatants = []
        self.distance = distance
        self.max_distance = max_distance
        self.events = []
        self.next_event = None
        self.event_counter = 0

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

    def get_opponent_data(self, combatant, assumed_opponent):
        combatant.opponent = assumed_opponent

    def determine_next_event(self):
        combatants_actions = [c.action for c in self.combatants if c.action]
        self.event_counter += 1

        if not combatants_actions:
            self.next_event = None
            print("No valid combatant actions found.")
            raise ValueError("No valid combatant actions found.")

        # Sort by time first, then by priority for same-time actions
        action_priority = {
            # ATTACK actions
            'try_attack': 1,
            'release_attack': 2,
            'stop_attack': 3,

            # DEFENSE actions
            'try_block': 4,
            'blocking': 5,
            'keep_blocking': 6,

            # EVASION actions
            'try_evade': 7,
            'evading': 8,

            # MOVEMENT actions
            'move_forward': 9,
            'move_backward': 10,
            'turn_around': 11,

            # NEUTRAL actions
            'idle': 12,
            'reset': 13,
            'recover': 14,
            'off_balance': 15
        }

        # Sort by time first, then by priority for same-time actions
        combatants_actions.sort(key=lambda x: (
            x['time'],  # Primary sort by chronological time
            action_priority.get(x['type'], 999)  # Secondary sort by priority (tiebreaker)
        ))

        self.next_event = combatants_actions[0] if combatants_actions else None

    def update(self):
        if not self.next_event:
            return

        # Process the event
        self.process_event(self.next_event)
        
        # Add the action's duration to the timer after processing
        action_duration = ACTIONS[self.next_event['type']]['time']
        self.timer += action_duration

    def process_event(self, event):
        combatant = event['combatant']
        action_type = event['type']
        process_method = getattr(self, f"process_{action_type}", None)
        if process_method:
            process_method(combatant, event)
        else:
            print(f"Unknown action type: {action_type}")

    def find_target(self, combatant):
        for potential_target in self.combatants:
            if potential_target.team != combatant.team and not potential_target.is_defeated():
                return potential_target
        return None
    
    def mark_action_as_completed(self, combatant, event):
        # Create a new event with completed status
        new_event = {
            "type": event["type"],
            "time": self.timer,  # Use current battle timer
            "combatant": event["combatant"],
            "status": "completed",
            "target": event.get("target"),
            "result": event.get("result")
        }
        self.processed_action_log(combatant, new_event)
        
    def process_action(self, combatant, event, action_key, targeted=False):
        # Get initial state before changes
        initial_distance = self.distance
        
        # Process state changes first
        if action_key == "move_forward":
            self.distance = max(0, self.distance - combatant.mobility)
        elif action_key == "move_backward":
            self.distance = min(self.max_distance, self.distance + combatant.mobility)
        
        # Get target based on context
        target = None
        if targeted:
            target = combatant.opponent
        elif len(self.combatants) > 1:
            target = self.find_target(combatant)
            
        # Get action history
        actor_history = []
        opponent_history = []
        for prev_event in reversed(self.events[-5:]):  # Last 5 events
            if 'pre_state' in prev_event:
                if prev_event['pre_state']['actor']['name'] == combatant.name:
                    actor_history.append(prev_event['action']['type'])
                elif target and prev_event['pre_state']['actor']['name'] == target.name:
                    opponent_history.append(prev_event['action']['type'])

        # Create the log
        log = {
            "event_id": f"{self.timer}_{self.event_counter + 1}_{combatant.name}",
            "timestamp": self.timer,
            "sequence_number": self.event_counter + 1,
            "pre_state": {
                "actor": {
                    "name": combatant.name,
                    "health_ratio": combatant.health / combatant.max_health,
                    "stamina_ratio": combatant.stamina / combatant.max_stamina,
                    "position": combatant.position,
                    "facing": combatant.facing,
                    "blocking_power": combatant.blocking_power,
                    "current_action": action_key
                },
                "opponent": {
                    "name": target.name if target else None,
                    "health_ratio": target.health / target.max_health if target else None,
                    "stamina_ratio": target.stamina / target.max_stamina if target else None,
                    "position": target.position if target else None,
                    "facing": target.facing if target else None,
                    "blocking_power": target.blocking_power if target else None,
                    "current_action": target.action['type'] if target and target.action else None
                } if target else None,
                "battle_context": {
                    "distance": self.distance,
                    "max_distance": self.max_distance,
                    "time_remaining": self.duration - self.timer
                }
            },
            "action": {
                "type": action_key,
                "timing": {
                    "start": event["time"],  # Use original event time
                    "duration": 0,  # Instant action
                    "end": event["time"]
                },
                "stamina_cost": ACTIONS[action_key]["stamina_cost"],
                "in_range": combatant.is_within_range(self.distance)
            },
            "result": {
                "status": "completed",
                "outcome": event.get('result'),
                "damage_dealt": event.get('damage'),
                "state_changes": {
                    "actor_stamina_change": -ACTIONS[action_key]["stamina_cost"],
                    "opponent_blocking_power_change": -event.get('damage') if event.get('result') == "blocked" and event.get('damage') is not None else None,
                    "opponent_health_change": -event.get('damage') if event.get('result') in ["hit", "breached"] and event.get('damage') is not None else None,
                    "distance_change": self.distance - initial_distance if action_key in ["move_forward", "move_backward"] else 0
                }
            },
            "action_history": {
                "actor_previous": actor_history[-3:],  # Last 3 actions
                "opponent_previous": opponent_history[-3:] if target else None
            }
        }
        self.events.append(log)
        
        # Process the action
        if action_key == "idle":
            decision = combatant.decide_action(self.timer, self.event_counter, self.distance)
            self.events.append(decision)
            self.update_opponent_perception(combatant)
        else:
            # Chain to idle
            self.apply_action(combatant, "idle")
        
    def apply_action(self, combatant, action_type):
        action = combatant.create_action(action_type, self.timer)
        combatant.action = action
        self.events.append(action)
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
        self.mark_action_as_completed(combatant, event)
        self.apply_action(combatant, "reset")
    
    # MOVEMENT actions processing
    def process_turn_around(self, combatant, event):
        combatant.facing = "right" if combatant.facing == "left" else "left"
        self.mark_action_as_completed(combatant, event)
        self.apply_action(combatant, "idle")

    def process_move_forward(self, combatant, event):
        self.distance = max(0, self.distance - combatant.mobility)
        self.mark_action_as_completed(combatant, event)
        self.apply_action(combatant, "idle")

    def process_move_backward(self, combatant, event):
        self.distance = min(self.max_distance, self.distance + combatant.mobility)
        self.mark_action_as_completed(combatant, event)
        self.apply_action(combatant, "idle")

    # DEFENSE actions processing
    def process_try_block(self, combatant, event):
        self.mark_action_as_completed(combatant, event)
        if combatant.stamina >= ACTIONS["blocking"]["stamina_cost"]:
            self.apply_action(combatant, "blocking")
        else:
            self.apply_action(combatant, "idle")
        
    def process_blocking(self, combatant, event):
        self.mark_action_as_completed(combatant, event)
        # After block duration, must decide to keep blocking or stop
        decision = combatant.decide_block_action(self.timer, self.event_counter, self.distance)
        self.events.append(decision)

    def process_keep_blocking(self, combatant, event):
        self.mark_action_as_completed(combatant, event)
        if combatant.stamina >= ACTIONS["blocking"]["stamina_cost"]:
            self.apply_action(combatant, "blocking")  # Start new block duration
        else:
            self.apply_action(combatant, "idle")
        
    # EVASION actions processing
    def process_try_evade(self, combatant, event):
        self.mark_action_as_completed(combatant, event)
        if combatant.stamina >= ACTIONS["evading"]["stamina_cost"]:
            self.apply_action(combatant, "evading")
        else:
            self.apply_action(combatant, "idle")

    def process_evading(self, combatant, event):
        self.mark_action_as_completed(combatant, event)
        self.apply_action(combatant, "evading")

    # ATTACK actions processing
    def process_try_attack(self, combatant, event):
        self.mark_action_as_completed(combatant, event)
        self.apply_action(combatant, "release_attack")

    def process_release_attack(self, combatant, event):
        # Check if the target is within range of the attack
        if not combatant.is_within_range(self.distance):
            event['result'] = "missed"
            self.mark_action_as_completed(combatant, event)
            self.apply_action(combatant, "off_balance")
            return

        # Get the target for the attack
        target = self.find_target(combatant)
        if not target:
            return

        # Check if target is blocking or evading
        if target.action:
            if target.action['type'] in ["blocking", "keep_blocking"]:  # Check both blocking states
                self.handle_blocking(combatant, target, event)
                return
            elif target.action['type'] == "evading":
                event['result'] = "evaded"
                self.mark_action_as_completed(combatant, event)
                self.apply_action(target, "reset")
                self.apply_action(combatant, "off_balance")
                return

        # If we get here, it's a direct hit
        self.handle_attack_hit(combatant, event)

    def handle_attack_hit(self, combatant, event):
        target = self.find_target(combatant)
        if not target:
            return
            
        # Calculate damage
        damage = random.randint(combatant.attack_power * combatant.accuracy // 100, combatant.attack_power)
        target.health = max(0, target.health - damage)
        
        # Update event
        event['result'] = "hit"
        event['damage'] = damage
        
        # Complete action and apply consequences
        self.mark_action_as_completed(combatant, event)
        self.apply_action(target, "reset")
        self.apply_action(combatant, "reset")
    
    def handle_blocking(self, combatant, target, event):
        # Calculate damage
        damage = random.randint(combatant.attack_power * combatant.accuracy // 100, combatant.attack_power)
        event['damage'] = damage
        
        # Update blocking power before checking breach
        original_blocking_power = target.blocking_power
        target.blocking_power = max(0, target.blocking_power - damage)
        
        # Check if block was breached
        if damage <= original_blocking_power:
            event['result'] = "blocked"
            self.mark_action_as_completed(combatant, event)
            self.apply_action(target, "reset")
            self.apply_action(combatant, "off_balance")
        else:
            event['result'] = "breached"
            breach_damage = damage - original_blocking_power
            target.health = max(0, target.health - breach_damage)
            self.mark_action_as_completed(combatant, event)
            self.apply_action(target, "reset")
            self.apply_action(combatant, "reset")

    def process_stop_attack(self, combatant, event):
        self.mark_action_as_completed(combatant, event)
        self.apply_action(combatant, "idle")
        
    def update_opponent_perception(self, combatant):
        opponent = self.find_target(combatant)
        if opponent:
            opponent.update_combatant_perception(combatant.action)

    def processed_action_log(self, combatant, event, targeted=False):
        # Get target based on context
        target = None
        if targeted:
            target = combatant.opponent
        elif len(self.combatants) > 1:
            target = self.find_target(combatant)
            
        # Get action history
        actor_history = []
        opponent_history = []
        for prev_event in reversed(self.events[-5:]):  # Last 5 events
            if 'pre_state' in prev_event:
                if prev_event['pre_state']['actor']['name'] == combatant.name:
                    actor_history.append(prev_event['action']['type'])
                elif target and prev_event['pre_state']['actor']['name'] == target.name:
                    opponent_history.append(prev_event['action']['type'])

        # Create the log
        log = {
            "event_id": f"{self.timer}_{self.event_counter + 1}_{combatant.name}",
            "timestamp": self.timer,
            "sequence_number": self.event_counter + 1,
            "pre_state": {
                "actor": {
                    "name": combatant.name,
                    "health_ratio": combatant.health / combatant.max_health,
                    "stamina_ratio": combatant.stamina / combatant.max_stamina,
                    "position": combatant.position,
                    "facing": combatant.facing,
                    "blocking_power": combatant.blocking_power,
                    "current_action": event['type']
                },
                "opponent": {
                    "name": target.name if target else None,
                    "health_ratio": target.health / target.max_health if target else None,
                    "stamina_ratio": target.stamina / target.max_stamina if target else None,
                    "position": target.position if target else None,
                    "facing": target.facing if target else None,
                    "blocking_power": target.blocking_power if target else None,
                    "current_action": target.action['type'] if target and target.action else None
                } if target else None,
                "battle_context": {
                    "distance": self.distance,
                    "max_distance": self.max_distance,
                    "time_remaining": self.duration - self.timer
                }
            },
            "action": {
                "type": event['type'],
                "timing": {
                    "start": self.timer,
                    "duration": event['time'] - self.timer,
                    "end": event['time']
                },
                "stamina_cost": ACTIONS[event['type']]["stamina_cost"],
                "in_range": combatant.is_within_range(self.distance)
            },
            "result": {
                "status": event['status'],
                "outcome": event.get('result'),
                "damage_dealt": event.get('damage'),
                "state_changes": {
                    "actor_stamina_change": -ACTIONS[event['type']]["stamina_cost"],
                    "opponent_blocking_power_change": -event.get('damage') if event.get('result') == "blocked" and event.get('damage') is not None else None,
                    "opponent_health_change": -event.get('damage') if event.get('result') in ["hit", "breached"] and event.get('damage') is not None else None,
                    "distance_change": combatant.mobility if event['type'] in ["move_forward", "move_backward"] else 0
                }
            },
            "action_history": {
                "actor_previous": actor_history[-3:],  # Last 3 actions
                "opponent_previous": opponent_history[-3:] if target else None
            }
        }
        self.events.append(log)

    def log_event(self, event_number, timestamp, timeend, combatant, action, distance, status, target=None, result=None, damage=None):
        if not combatant:
            return
            
        # Get action history for both combatants
        actor_history = []
        opponent_history = []
        for event in reversed(self.events[-5:]):  # Last 5 events
            if 'pre_state' in event:
                if event['pre_state']['actor']['name'] == combatant.name:
                    actor_history.append(event['action']['type'])
                elif target and event['pre_state']['actor']['name'] == target.name:
                    opponent_history.append(event['action']['type'])

        log = {
            "event_id": f"{timestamp}_{event_number}_{combatant.name}",
            "timestamp": timestamp,
            "sequence_number": event_number,
            "pre_state": {
                "actor": {
                    "name": combatant.name,
                    "health_ratio": combatant.health / combatant.max_health,
                    "stamina_ratio": combatant.stamina / combatant.max_stamina,
                    "position": combatant.position,
                    "facing": combatant.facing,
                    "blocking_power": combatant.blocking_power,
                    "current_action": action
                },
                "opponent": {
                    "name": target.name if target else None,
                    "health_ratio": target.health / target.max_health if target else None,
                    "stamina_ratio": target.stamina / target.max_stamina if target else None,
                    "position": target.position if target else None,
                    "facing": target.facing if target else None,
                    "blocking_power": target.blocking_power if target else None,
                    "current_action": target.action['type'] if target and target.action else None
                } if target else None,
                "battle_context": {
                    "distance": distance,
                    "max_distance": self.max_distance,
                    "time_remaining": self.duration - timestamp
                }
            },
            "action": {
                "type": action,
                "timing": {
                    "start": timestamp,
                    "duration": timeend - timestamp,
                    "end": timeend
                },
                "stamina_cost": ACTIONS[action]["stamina_cost"],
                "in_range": combatant.is_within_range(distance) if hasattr(combatant, 'is_within_range') else None
            },
            "result": {
                "status": status,
                "outcome": result,
                "damage_dealt": damage,
                "state_changes": {
                    "actor_stamina_change": -ACTIONS[action]["stamina_cost"],
                    "opponent_blocking_power_change": -damage if result == "blocked" and damage is not None else None,
                    "opponent_health_change": -damage if result in ["hit", "breached"] and damage is not None else None,
                    "distance_change": combatant.mobility if action in ["move_forward", "move_backward"] else 0
                }
            },
            "action_history": {
                "actor_previous": actor_history[-3:],  # Last 3 actions
                "opponent_previous": opponent_history[-3:] if target else None
            }
        }
        self.events.append(log)

    # REPLAY
    def replay_log(self):
        print("\n--- Battle Replay ---\n")
        sorted_events = sorted(self.events, key=lambda x: (
            x['timestamp'], 1 if x['result']['status'] == 'pending' else 0, x['sequence_number']
        ))
        for log in sorted_events:
            message = self.message_for_completed_event(log) if log["result"]["status"] == "completed" else self.message_for_pending_event(log)
            if message:
                print(message)
        print("\n--- Replay Complete ---\n")

    def message_for_completed_event(self, log):
        timestamp = log["timestamp"]
        actor = log["pre_state"]["actor"]
        opponent = log["pre_state"]["opponent"]
        action = log["action"]["type"]
        result = log["result"]["outcome"]
        distance = log["pre_state"]["battle_context"]["distance"]
        damage = log["result"]["damage_dealt"]

        message = f"[{timestamp}ms] {actor['name']} "
        if action == "try_attack":
            message += "attempted an attack."
        elif action == "release_attack":
            if result == "hit":
                message += f"attacked {opponent['name']} for {damage} damage (remaining HP: {opponent['health_ratio'] * 100:.0f}%)."
            elif result == "blocked":
                message += f"attacked {opponent['name']}, but the attack was blocked."
            elif result == "breached":
                message += f"attacked {opponent['name']}, and breached his defenses (remaining HP: {opponent['health_ratio'] * 100:.0f}%)."
            elif result == "evaded":
                message += f"attacked {opponent['name']}, but the attack was evaded."
            else:
                message += "attempted an attack, but missed."
        elif action == "stop_attack":
            message += "stopped an attack."
        elif action == "move_forward":
            message += f"moved forward, reducing the distance to {distance}."
        elif action == "move_backward":
            message += f"moved backward, increasing the distance to {distance}."
        elif action == "recover":
            message += f"recovered stamina, now at {actor['stamina_ratio'] * 100:.0f}%."
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
            message += f"took no action ({actor['stamina_ratio'] * 100:.0f}% stamina left)."
        elif action == "reset":
            message += "reset his position and balance."
        elif action == "off_balance":
            message += "got off-balance and has yet to reset."
        elif action == "added_to_battle":
            message += "was added to the battle."
        elif action == "battle_end":
            message = f"Battle ended after {timestamp}ms."
        message += f" [{log['result']['status']}]"
        return message

    def message_for_pending_event(self, log):
        timestamp = log["timestamp"]
        actor = log["pre_state"]["actor"]
        action = log["action"]["type"]
        timeend = log["action"]["timing"]["end"]
        duration = timeend - timestamp

        message = f"[{timestamp}ms] {actor['name']} "
        if action == "try_attack":
            message += f"is attempting an attack which will be released/stopped in {duration}ms."
        elif action == "release_attack":
            message += f"is releasing an attack which will land in {duration}ms."
        elif action == "stop_attack":
            message += f"is stopping an attack which will be completed in {duration}ms."
        elif action == "move_forward":
            message += f"is attempting to move forward which will be completed in {duration}ms."
        elif action == "move_backward":
            message += f"is attempting to move backward which will be completed in {duration}ms."
        elif action == "recover":
            message += f"is attempting to recover stamina which will be completed in {duration}ms."
        elif action == "try_block":
            message += f"decided to block attacks starting in {duration}ms."
        elif action == "try_evade":
            message += f"started an evasive stance which will evade attacks in {duration}ms."
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
        message += f" [{log['result']['status']}]"
        return message

    # BATTLE CONTROL
    def is_battle_over(self):
        if self.timer >= self.duration:
            return True
        active_combatants = [c for c in self.combatants if not c.is_defeated()]
        return len(active_combatants) <= 1
