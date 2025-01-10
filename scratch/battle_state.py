import copy


class BattleState:
    def __init__(self, duration):
        """
        Initialize the battle state.
        
        :param duration: Total duration of the battle in milliseconds.
        """
        self.timer = 0  # Current time
        self.duration = duration  # Total duration of the battle
        self.combatants = []  # List of combatants
        self.events = []  # Log of processed events (snapshots)
        self.next_event = None  # Reference to the next event to process

    def add_combatant(self, combatant):
        """
        Add a combatant to the battle.
        """
        self.combatants.append(combatant)

    def determine_next_event(self):
        """
        Determine which combatant's action should be processed next.
        """
        # Filter combatants with valid actions
        active_combatants = [
            c for c in self.combatants if c.action and c.action['time'] >= self.timer
        ]

        if not active_combatants:
            self.next_event = None
            print("No valid combatant actions found.")
            return

        # Find the action with the earliest time
        self.next_event = min(
            active_combatants, key=lambda c: c.action['time']
        ).action

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
        self.events.append(copy.deepcopy(self.next_event))

        # Determine the next event
        self.determine_next_event()

    def process_event(self, event):
        """
        Process an individual event.
        """
        combatant = event['combatant']
        action_type = event['type']

        if action_type == "attack":
            target = BattleState.find_target(self, combatant)
            if target.is_defeated():
                event['status'] = "missed"
                print(f"{combatant.name}'s attack missed! Target already defeated.")
            else:
                damage = combatant.attack_power
                target.health -= damage
                event['status'] = "hit"
                print(f"{combatant.name} attacked {target.name} for {damage} damage.")

            # Schedule recovery for the combatant
            # combatant.action = {
            #     "time": self.timer + 100,  # 100ms recovery
            #     "type": "recover",
            #     "combatant": combatant,
            #     "status": "pending",
            # }
            combatant.update_action(self.timer, {
                "time": self.timer + 100,
                "type": "recover",
                "combatant": combatant,
                "target": None,
                "status": "pending",
            })

        elif action_type == "recover":
            event['status'] = "completed"
            print(f"{combatant.name} has recovered and is ready to act again.")

            # After recovery, the combatant should decide the next action
            combatant.decide_action(self.timer)

        else:
            print(f"Unknown action type: {action_type}")
            

    def is_battle_over(self):
        """
        Check if the battle is over.
        """
        if self.timer >= self.duration:
            return True

        active_combatants = [c for c in self.combatants if not c.is_defeated()]
        return len(active_combatants) <= 1
    
    def replay_log(self):
            """
            Replay the events log, simulating the battle as a chronological narrative.
            """
            print("\n=== Replay of the Battle ===")
            for event in self.events:
                if event['type'] == "attack":
                    status = event['status']
                    if status == "hit":
                        print(f"At {event['time']}ms: {event['combatant'].name} attacked "
                            f"{event['target'].name} for {event['combatant'].attack_power} damage.")
                    elif status == "missed":
                        print(f"At {event['time']}ms: {event['combatant'].name} attempted to attack "
                            f"{event['target'].name} but missed.")
                elif event['type'] == "recover":
                    print(f"At {event['time']}ms: {event['combatant'].name} recovered and is ready to act.")
                else:
                    print(f"At {event['time']}ms: Unknown action '{event['type']}' occurred.")

            print("=== End of Replay ===\n")

    def find_target(self, combatant):
        """
        Find a target for the given combatant from the opposing team who is not defeated.
        """
        for potential_target in self.combatants:
            if potential_target.team != combatant.team and not potential_target.is_defeated():
                return potential_target
        return None  # No valid target found