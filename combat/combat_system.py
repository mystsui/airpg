"""
Combat System Module

This module implements the core combat system using the new interface-based architecture
while maintaining backward compatibility with existing code.
"""

import random
from typing import Optional, List
from combat.lib.actions_library import ACTIONS
from combat.interfaces import (
    ICombatant,
    IActionResolver,
    IStateManager,
    IEventDispatcher,
    CombatEvent
)
from combat.adapters import (
    CombatantAdapter,
    ActionResolverAdapter,
    StateManagerAdapter,
    EventDispatcherAdapter
)

class CombatSystem:
    """Core combat system implementation."""
    
    def __init__(self, duration: int, distance: float, max_distance: float):
        """
        Initialize the combat system.
        
        Args:
            duration: Maximum battle duration in milliseconds
            distance: Initial distance between combatants
            max_distance: Maximum allowed distance
        """
        self.timer = 0
        self.duration = duration
        self.distance = distance
        self.max_distance = max_distance
        self.event_counter = 0
        
        # Initialize adapters
        self._action_resolver = ActionResolverAdapter()
        self._state_manager = StateManagerAdapter()
        self._event_dispatcher = EventDispatcherAdapter()
        
        # Initialize collections
        self._combatants: List[ICombatant] = []
        self.next_event = None
        
        # Subscribe to events
        self._event_dispatcher.subscribe("action_completed", self._on_action_completed)
        self._event_dispatcher.subscribe("state_changed", self._on_state_changed)

    def add_combatant(self, combatant) -> None:
        """
        Add a combatant to the battle.
        
        Args:
            combatant: The combatant to add (can be legacy Combatant or ICombatant)
        """
        if len(self._combatants) >= 2:
            raise ValueError("Battle is full.")
            
        if not combatant:
            raise ValueError("Invalid combatant.")
            
        # Wrap legacy combatant in adapter if needed
        if not isinstance(combatant, ICombatant):
            combatant = CombatantAdapter(combatant)
            
        # Set team
        state = combatant.get_state()
        new_state = {**state.__dict__}
        new_state["team"] = "challenger" if not self._combatants else "defender"
        
        # Validate combatant hasn't already been added
        if self._combatants:
            if self._combatants[0].get_state().entity_id == state.entity_id:
                raise ValueError("Combatant already added to the battle.")
                
        # Update state and add combatant
        self._state_manager.update_state(state.entity_id, new_state)
        self._combatants.append(combatant)
        
        # Dispatch event
        self._dispatch_event("combatant_added", {
            "combatant_id": state.entity_id,
            "team": new_state["team"]
        })

    def get_opponent_data(self, combatant: ICombatant, assumed_opponent: ICombatant) -> None:
        """Set opponent data for a combatant."""
        if isinstance(combatant, CombatantAdapter):
            combatant.adaptee.opponent = (
                assumed_opponent.adaptee if isinstance(assumed_opponent, CombatantAdapter)
                else assumed_opponent
            )

    def determine_next_event(self) -> None:
        """Determine the next event to process."""
        combatants_actions = [c.get_state().action for c in self._combatants if c.get_state().action]
        self.event_counter += 1
        
        if not combatants_actions:
            self.next_event = None
            raise ValueError("No valid combatant actions found.")
            
        # Sort by time and priority
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
        
        combatants_actions.sort(key=lambda x: (
            x['time'],
            action_priority.get(x['type'], 999)
        ))
        
        self.next_event = combatants_actions[0] if combatants_actions else None

    def update(self) -> None:
        """Update the combat system state."""
        if not self.next_event:
            return
            
        # Process the event
        self.process_event(self.next_event)
        
        # Add action duration to timer
        action_duration = ACTIONS[self.next_event['type']]['time']
        self.timer += action_duration

    def process_event(self, event: dict) -> None:
        """
        Process a combat event.
        
        Args:
            event: The event to process
        """
        combatant = event['combatant']
        action_type = event['type']
        
        # Convert to ICombatant if needed
        if not isinstance(combatant, ICombatant):
            combatant = CombatantAdapter(combatant)
            
        # Get process method
        process_method = getattr(self, f"process_{action_type}", None)
        if process_method:
            process_method(combatant, event)
        else:
            print(f"Unknown action type: {action_type}")

    def _dispatch_event(self, event_type: str, data: dict) -> None:
        """
        Dispatch a combat event.
        
        Args:
            event_type: Type of event
            data: Event data
        """
        event = CombatEvent(
            event_id=f"{self.timer}_{self.event_counter}",
            event_type=event_type,
            timestamp=self.timer,
            source_id=data.get("source_id"),
            target_id=data.get("target_id"),
            data=data
        )
        self._event_dispatcher.dispatch(event)

    def _on_action_completed(self, event: CombatEvent) -> None:
        """Handle action completed events."""
        # Update state based on action result
        if "state_changes" in event.data:
            for entity_id, changes in event.data["state_changes"].items():
                current_state = self._state_manager.get_state(entity_id)
                if current_state:
                    new_state = {**current_state.__dict__, **changes}
                    self._state_manager.update_state(entity_id, new_state)

    def _on_state_changed(self, event: CombatEvent) -> None:
        """Handle state changed events."""
        # Notify relevant systems of state changes
        if "health_changed" in event.data:
            self._check_victory_conditions()

    def _check_victory_conditions(self) -> None:
        """Check if victory conditions are met."""
        if self.timer >= self.duration:
            self._dispatch_event("battle_ended", {"reason": "time_expired"})
            return
            
        active_combatants = [c for c in self._combatants if not c.is_defeated()]
        if len(active_combatants) <= 1:
            self._dispatch_event("battle_ended", {
                "reason": "defeat",
                "victor": active_combatants[0].get_state().entity_id if active_combatants else None
            })

    # Existing process methods remain unchanged but use adapters internally
    # This maintains backward compatibility while using the new architecture
    
    def is_battle_over(self) -> bool:
        """Check if the battle is over."""
        if self.timer >= self.duration:
            return True
        active_combatants = [c for c in self._combatants if not c.is_defeated()]
        return len(active_combatants) <= 1
