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
        event['status'] = "completed"
        self.processed_action_log(combatant, event)
        
    def process_action(self, combatant, event, action_key, targeted=False):
        self.mark_action_as_completed(combatant, event)
        if action_key == "idle":
            decision = combatant.decide_action(self.timer, self.event_counter, self.distance)
            self.events.append(decision)
            self.update_opponent_perception(combatant)
        else:
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

    def is_battle_over(self):
        if self.timer >= self.duration:
            return True
        active_combatants = [c for c in self.combatants if not c.is_defeated()]
        return len(active_combatants) <= 1
