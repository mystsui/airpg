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
    CombatEvent,
    EventCategory,
    EventImportance,
    CombatantState
)
from combat.interfaces.action_system import ActionState, ActionStateType, ActionPhase
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
        self.next_event = None
        
        # Subscribe to events
        self._event_dispatcher.subscribe("action_completed", self._handle_action_completed)
        self._event_dispatcher.subscribe("state_changed", self._handle_state_changed)

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
            
        # Create and track action in action system
        system_action = self._action_system.create_action(
            action_type=action.action_type,
            source_id=action.source_id,
            target_id=action.target_id
        )
        
        # Update action state with commit state
        action_with_commit = ActionState(
            action_id=system_action.action_id,
            action_type=action.action_type,
            source_id=action.source_id,
            target_id=action.target_id,
            state=ActionStateType.COMMIT,
            phase=ActionPhase.ACTIVE,
            visibility=action.visibility,
            commitment=action.commitment,
            properties=action.properties
        )
        
        if not self._action_system.validate_action(action_with_commit):
            raise ValueError("Invalid action state transition")
            
        self._action_system.update_action_state(system_action.action_id, action_with_commit)
            
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
        
        # Rest of the method remains the same as in the previous implementation
        # (Keeping the existing action resolution and state update logic)
        
        # Update states based on result
        if result.success:
            # Update source combatant
            new_source_state = CombatantState(
                entity_id=source_state.entity_id,
                stamina=source_state.stamina - result.stamina_cost,
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
                "action_id": system_action.action_id,
                "success": True,
                "damage": result.damage,
                "stamina_cost": result.stamina_cost,
                "effects": result.effects,
                "state_changes": state_changes
            })
        else:
            # Dispatch action failed event
            self._dispatch_event("action_failed", {
                "action_id": system_action.action_id,
                "reason": "Action resolution failed"
            })

    # Rest of the methods remain the same as in the previous implementation
