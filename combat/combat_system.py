"""
Combat System Module

This module implements the core combat system using the new interface-based architecture
while maintaining backward compatibility with existing code.
"""

import random
from datetime import datetime
from typing import Optional, List, Dict
from combat.lib.actions_library import ACTIONS
from combat.interfaces import (
    ICombatant,
    IActionResolver,
    IStateManager,
    IEventDispatcher,
    CombatEvent,
    EventCategory,
    EventImportance,
    CombatantState
)
from combat.interfaces.action_system import (
    ActionState,
    ActionStateType,
    ActionVisibility
)
from combat.lib.action_system import ActionSystem
from combat.adapters import (
    CombatantAdapter,
    ActionResolverAdapter,
    StateManagerAdapter,
    EventDispatcherAdapter,
    AwarenessSystemAdapter,
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
        
        # Initialize systems and adapters
        self._action_system = ActionSystem()
        self._action_resolver = ActionResolverAdapter()
        self._state_manager = StateManagerAdapter()
        self._event_dispatcher = EventDispatcherAdapter()
        self._awareness_system = AwarenessSystemAdapter()
        
        # Initialize collections
        self._combatants: List[ICombatant] = []
        self._actions: Dict[str, ActionState] = {}
        self.next_event = None
        
        # Subscribe to events
        self._event_dispatcher.subscribe("action_completed", self._handle_action_completed)
        self._event_dispatcher.subscribe("state_changed", self._handle_state_changed)
        self._event_dispatcher.subscribe("combat", self._handle_combat_event)
        
    def _handle_action_completed(self, event: CombatEvent) -> None:
        """Handle action completion events."""
        action_id = event.data.get("action_id")
        if not action_id:
            return
            
        # Get the action state
        action = self._action_system.get_action_state(action_id)
        if not action:
            return
            
        # Update action state to recovery if needed
        if action.state != ActionStateType.RECOVERY:
            recovery_state = ActionState(
                action_id=action.action_id,
                action_type=action.action_type,
                source_id=action.source_id,
                target_id=action.target_id,
                state=ActionStateType.RECOVERY,
                visibility=action.visibility,
                properties=action.properties
            )
            self._action_system.update_action_state(action_id, recovery_state)
            
    def _handle_state_changed(self, event: CombatEvent) -> None:
        """Handle state change events."""
        # Update awareness based on state changes
        if event.source_id and event.target_id:
            source_state = self._state_manager.get_state(event.source_id)
            target_state = self._state_manager.get_state(event.target_id)
            
            if source_state and target_state:
                self._awareness_system.update_awareness(
                    observer_id=event.source_id,
                    target_id=event.target_id,
                    observer_stats=source_state.stats,
                    target_stats=target_state.stats,
                    distance=self.distance,
                    angle=90.0,  # Default angle
                    current_time=self.timer
                )
                
    def _handle_combat_event(self, event: CombatEvent) -> None:
        """Handle combat events."""
        # This handler is used to track combat events for testing
        pass

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
        new_state = CombatantState(
            entity_id=state.entity_id,
            stamina=state.stamina,
            speed=state.speed,
            stealth=state.stealth,
            position_x=state.position_x,
            position_y=state.position_y,
            stats={
                **state.stats,
                "health": 100.0,  # Initialize health
                "team": "challenger" if not self._combatants else "defender"
            }
        )
        
        # Validate combatant hasn't already been added
        if self._combatants:
            if self._combatants[0].get_state().entity_id == state.entity_id:
                raise ValueError("Combatant already added to the battle.")
                
        # Update state and add combatant
        self._state_manager.update_state(state.entity_id, new_state)
        self._combatants.append(combatant)
        
        # Register combatant in awareness system
        self._awareness_system.register_combatant(state.entity_id)
        
        # Dispatch event
        self._dispatch_event("combatant_added", {
            "combatant_id": state.entity_id,
            "team": new_state.stats["team"]
        })
        
    def cancel_action(self, action_id: str) -> bool:
        """
        Attempt to cancel an action.
        
        Args:
            action_id: The ID of the action to cancel
            
        Returns:
            bool indicating if the action was successfully cancelled
        """
        return self._action_system.cancel_action(action_id)

    def execute_action(self, action: ActionState) -> None:
        """
        Execute a combat action.
        
        Args:
            action: The action to execute
        """
        # Get combatant states
        source_state = self._state_manager.get_state(action.source_id)
        target_state = self._state_manager.get_state(action.target_id) if action.target_id else None
        
        if not source_state:
            raise ValueError(f"Invalid source combatant: {action.source_id}")
                    
        # Update action state to release
        action_to_release = ActionState(
            action_id=action.action_id,
            action_type=action.action_type,
            source_id=action.source_id,
            target_id=action.target_id,
            state=ActionStateType.RELEASE,  # Changed from COMMIT to RELEASE
            visibility=action.visibility,
            properties=action.properties
        )
        
        if not self._action_system.validate_action(action_to_release):
            raise ValueError("Invalid action state transition")
            
        # Update action state
        self._action_system.update_action_state(action.action_id, action_to_release)
            
        # Resolve the action
        result = self._action_resolver.resolve_action(action, source_state, target_state)
        
        # Update awareness if target exists
        if target_state:
            self._awareness_system.update_awareness(
                observer_id=action.source_id,
                target_id=action.target_id,
                observer_stats=source_state.stats,
                target_stats=target_state.stats,
                distance=self.distance,
                angle=90.0,  # Default angle, could be calculated more precisely
                current_time=self.timer
            )
        
        # Update states based on result
        if result.success:
            # Get action properties
            action_data = ACTIONS.get(action.action_type, {})
            stamina_cost = action_data.get('stamina_cost', 0)
            
            # Update source combatant with proper stamina cost
            new_source_state = CombatantState(
                entity_id=source_state.entity_id,
                stamina=max(0, source_state.stamina - stamina_cost),  # Ensure stamina doesn't go negative
                speed=source_state.speed,
                stealth=source_state.stealth,
                position_x=source_state.position_x,
                position_y=source_state.position_y,
                stats=source_state.stats
            )
            self._state_manager.update_state(action.source_id, new_source_state)
            
            # Update target combatant if any
            if target_state and result.damage > 0:
                new_target_state = CombatantState(
                    entity_id=target_state.entity_id,
                    stamina=target_state.stamina,
                    speed=target_state.speed,
                    stealth=target_state.stealth,
                    position_x=target_state.position_x,
                    position_y=target_state.position_y,
                    stats={
                        **target_state.stats,
                        "health": max(0, target_state.stats.get("health", 100) - result.damage)
                    }
                )
                self._state_manager.update_state(action.target_id, new_target_state)
                
            # Prepare state changes
            state_changes = {action.source_id: new_source_state}
            if target_state and result.damage > 0 and 'new_target_state' in locals():
                state_changes[action.target_id] = new_target_state

            # Dispatch action completed event
            self._dispatch_event("action_completed", {
                "action_id": action.action_id,
                "success": True,
                "damage": result.damage,
                "stamina_cost": result.stamina_cost,
                "effects": result.effects,
                "state_changes": state_changes
            })
        else:
            # Dispatch action failed event
            self._dispatch_event("action_failed", {
                "action_id": action.action_id,
                "reason": "Action resolution failed"
            })

    def update(self, delta_time: float) -> None:
        """
        Update the combat system state.
        
        Args:
            delta_time: Time elapsed since last update in milliseconds
        """
        self.timer += delta_time
        
        # Get all active actions
        active_actions = {
            action_id: action 
            for action_id, action in self._action_system._actions.items()
            if action.state != ActionStateType.RECOVERY
        }
        
        # Update each action
        for action_id, action in active_actions.items():
            # Get action timing from actions library
            action_data = ACTIONS.get(action.action_type, {})
            action_duration = action_data.get('time', 1000)  # Default 1 second
            
            # Check if action should transition to recovery
            if self.timer >= action_duration:
                # Create recovery state
                recovery_state = ActionState(
                    action_id=action.action_id,
                    action_type=action.action_type,
                    source_id=action.source_id,
                    target_id=action.target_id,
                    state=ActionStateType.RECOVERY,
                    visibility=action.visibility,
                    properties=action.properties
                )
                
                # Update action state
                self._action_system.update_action_state(action_id, recovery_state)
                
                # Dispatch event
                self._dispatch_event(action.action_type, {
                    "action_id": action_id,
                    "source_id": action.source_id,
                    "target_id": action.target_id,
                    "state": "recovery"
                })

    def _dispatch_event(self, event_type: str, data: dict, category: EventCategory = EventCategory.COMBAT) -> None:
        """
        Dispatch an event with the given type and data.
        
        Args:
            event_type: Type of event
            data: Event data
            category: Event category (defaults to COMBAT)
        """
        # Create unique event ID and use current time
        self.event_counter += 1
        event = CombatEvent(
            event_id=f"{event_type}_{self.event_counter}",
            event_type=event_type,
            category=category,
            importance=EventImportance.MAJOR,  # Use MAJOR for standard combat events
            timestamp=datetime.now(),
            source_id=data.get("source_id"),
            target_id=data.get("target_id"),
            data=data
        )
        self._event_dispatcher.dispatch(event)
