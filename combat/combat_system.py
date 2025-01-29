import random

from combat.lib.actions_library import ACTIONS

class CombatSystem:
    # Initialize the combat system
    def __init__(self, duration, distance):
        self.timer = 0
        self.duration = duration
        self.combatants = []
        self.distance = distance
        self.events = []
        self.next_event = None
        self.event_counter = 0

    # Add a combatant to the battle
    def add_combatant(self, combatant):
        combatant.team = "challenger" if len(self.combatants) == 0 else "defender"
        self.combatants.append(combatant)
        print(f"Added {combatant} to the team {combatant.team}")

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
            return

        status_priority = {'completed': 0, 'pending': 1}
        action_priority = {
            # NEUTRAL actions
            'idle': 1,
            'reset': 2,
            'recover': 3,
            'off_balance': 4,

            # MOVEMENT actions
            'move_forward': 5,
            'move_backward': 6,
            'turn_around': 7,

            # DEFENSE actions
            'try_block': 8,
            'blocking': 9,
            'keep_blocking': 10,

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
    def process_action(self, combatant, event, action_key, targeted=False):
        event['status'] = "completed"
        self.processed_action_log(combatant, event, targeted)
        decision = combatant.decide_action(self.timer, self.event_counter, self.distance)
        self.events.append(decision)

    # NEUTRAL actions processing
    def process_idle(self, combatant, event):
        self.process_action(combatant, event, "idle")

    def process_reset(self, combatant, event):
        self.process_action(combatant, event, "reset")

    def process_recovery(self, combatant, event):
        self.process_action(combatant, event, "recover")
        combatant.stamina = min(combatant.max_stamina, combatant.stamina + combatant.stamina_recovery)

    def process_off_balance(self, combatant, event):
        self.process_action(combatant, event, "off_balance")
    
    # MOVEMENT actions processing
    def process_turn_around(self, combatant, event):
        self.process_action(combatant, event, "turn_around")
        combatant.facing = "right" if combatant.facing == "left" else "left"

    def process_move_forward(self, combatant, event):
        self.process_action(combatant, event, "move_forward")
        self.distance = max(0, self.distance - combatant.mobility)

    def process_move_backward(self, combatant, event):
        self.process_action(combatant, event, "move_backward")
        self.distance = min(600, self.distance + combatant.mobility)

    # DEFENSE actions processing
    def process_try_block(self, combatant, event):
        self.process_action(combatant, event, "try_block")
        self.events.append(combatant.apply_action_state("blocking", self.timer, self.event_counter, self.distance))

    def process_blocking(self, combatant, event):
        self.process_action(combatant, event, "blocking")

    def process_keep_blocking(self, combatant, event):
        self.process_action(combatant, event, "keep_blocking")
        self.events.append(combatant.apply_action_state("blocking", self.timer, self.event_counter, self.distance))

    # EVASION actions processing
    def process_try_evade(self, combatant, event):
        self.process_action(combatant, event, "try_evade")
        self.events.append(combatant.apply_action_state("evading", self.timer, self.event_counter, self.distance))

    def process_evading(self, combatant, event):
        self.process_action(combatant, event, "evading")

    # ATTACK actions processing
    def process_try_attack(self, combatant, event):
        event['status'] = "completed"
        self.processed_action_log(combatant, event, targeted=False)
        decision = combatant.decide_attack_action(self.timer, self.event_counter, self.distance)
        self.events.append(decision)

    def process_release_attack(self, combatant, event):
        target = combatant.opponent
        event['status'] = "completed"
        event['damage'] = 0
        if not combatant.is_within_range(self.distance):
            event['result'] = "missed"
            self.processed_action_log(combatant, event, targeted=True)
            self.events.append(combatant.apply_action_state("off_balance", self.timer, self.event_counter, self.distance))
        else:
            self.handle_attack_result(combatant, target, event)

    def handle_attack_result(self, combatant, target, event):
        if target.action['type'] == "blocking":
            self.handle_blocking(combatant, target, event)
        elif target.action['type'] == "evading":
            event['result'] = "evaded"
            self.processed_action_log(combatant, event, targeted=True)
            self.events.append(target.apply_action_state("reset", self.timer, self.event_counter, self.distance))
            self.events.append(combatant.apply_action_state("off_balance", self.timer, self.event_counter, self.distance))
        else:
            damage = random.randint(combatant.attack_power * combatant.accuracy // 100, combatant.attack_power)
            target.health = max(0, target.health - damage)
            event['result'] = "hit"
            event['damage'] = damage
            self.processed_action_log(combatant, event, targeted=True)
            self.events.append(target.apply_action_state("off_balance", self.timer, self.event_counter, self.distance))
            self.events.append(combatant.apply_action_state("reset", self.timer, self.event_counter, self.distance))

    def handle_blocking(self, combatant, target, event):
        event['result'] = "blocked"
        damage = random.randint(combatant.attack_power * combatant.accuracy // 100, combatant.attack_power)
        event['damage'] = damage
        if damage <= target.blocking_power:
            self.events.append(combatant.apply_action_state("off_balance", self.timer, self.event_counter, self.distance))
            self.events.append(target.apply_action_state("reset", self.timer, self.event_counter, self.distance))
        else:
            self.events.append(combatant.apply_action_state("reset", self.timer, self.event_counter, self.distance))
            self.events.append(target.apply_action_state("reset", self.timer, self.event_counter, self.distance))
            event['result'] = "breached"
        breach_damage = damage - target.blocking_power
        target.blocking_power = max(0, target.blocking_power - damage)
        target.health = max(0, target.health - breach_damage)
        self.processed_action_log(combatant, event, targeted=True)

    def process_stop_attack(self, combatant, event):
        self.process_action(combatant, event, "stop_attack")

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