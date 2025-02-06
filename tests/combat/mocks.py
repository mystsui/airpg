"""
Mock implementations for testing.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from combat.lib.action_system import (
    ActionStateType,
    ActionVisibility,
    ActionCommitment,
    ActionPhase,
    ActionState
)
from combat.lib.event_system import (
    EventCategory,
    EventImportance,
    EnhancedEvent
)
from combat.interfaces.timing import CombatTiming, ITimingManager


class MockTimingManager:
    """Mock implementation of ITimingManager."""
    
    def __init__(self):
        self.timings: Dict[str, CombatTiming] = {}
        self.remaining_times: Dict[str, float] = {}

    def get_action_timing(self, action_id: str) -> Optional[CombatTiming]:
        """Get timing information for an action."""
        return self.timings.get(action_id)

    def update_timing(self, action_id: str, timing: CombatTiming) -> None:
        """Update timing information for an action."""
        self.timings[action_id] = timing
        self.remaining_times[action_id] = timing.total_time

    def add_modifier(self, action_id: str, modifier_name: str, value: float) -> None:
        """Add a named time modifier to an action."""
        if action_id in self.timings:
            self.timings[action_id].time_modifiers[modifier_name] = value
            self.remaining_times[action_id] = self.timings[action_id].total_time

    def remove_modifier(self, action_id: str, modifier_name: str) -> None:
        """Remove a named time modifier from an action."""
        if action_id in self.timings:
            if modifier_name in self.timings[action_id].time_modifiers:
                del self.timings[action_id].time_modifiers[modifier_name]
                self.remaining_times[action_id] = self.timings[action_id].total_time

    def clear_modifiers(self, action_id: str) -> None:
        """Clear all time modifiers for an action."""
        if action_id in self.timings:
            self.timings[action_id].time_modifiers.clear()
            self.remaining_times[action_id] = self.timings[action_id].total_time

    def get_remaining_time(self, action_id: str) -> Optional[float]:
        """Get remaining time for an action."""
        return self.remaining_times.get(action_id)


class MockEventDispatcher:
    """Mock event dispatcher for testing."""
    
    def __init__(self):
        self.events = []
        self.subscribers = {}
        self.streams = {}
        
    def dispatch_event(self, event: EnhancedEvent) -> None:
        """Record dispatched event."""
        self.events.append(event)
        
        # Notify subscribers
        if event.event_type in self.subscribers:
            for handler in self.subscribers[event.event_type]:
                handler(event)
                
    def subscribe(self, event_type: str, handler: callable) -> None:
        """Record subscription."""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)
        
    def unsubscribe(self, event_type: str, handler: callable) -> None:
        """Remove subscription."""
        if event_type in self.subscribers:
            self.subscribers[event_type].remove(handler)
            
    def get_events(self) -> List[EnhancedEvent]:
        """Get recorded events."""
        return self.events
        
    def clear(self) -> None:
        """Clear recorded events."""
        self.events.clear()


class MockActionResolver:
    """Mock action resolver for testing."""
    
    def __init__(self):
        self.resolved_actions = []
        self.results = {}
        
    def resolve_action(self,
                      action: ActionState,
                      source_state: Any,
                      target_state: Optional[Any] = None) -> Any:
        """Record resolved action."""
        self.resolved_actions.append({
            "action": action,
            "source": source_state,
            "target": target_state
        })
        
        # Return predefined result if available
        if action.action_type in self.results:
            return self.results[action.action_type]
            
        # Default success result
        return type("ActionResult", (), {
            "success": True,
            "damage": 10,
            "stamina_cost": 5
        })()
        
    def set_result(self, action_type: str, result: Any) -> None:
        """Set predefined result."""
        self.results[action_type] = result
        
    def get_resolved_actions(self) -> List[dict]:
        """Get resolved actions."""
        return self.resolved_actions
        
    def clear(self) -> None:
        """Clear resolved actions."""
        self.resolved_actions.clear()
        self.results.clear()


class MockStateManager:
    """Mock state manager for testing."""
    
    def __init__(self):
        self.states = {}
        self.history = {}
        
    def update_state(self, state: Any) -> None:
        """Record state update."""
        entity_id = state.entity_id
        
        if entity_id not in self.history:
            self.history[entity_id] = []
            
        self.history[entity_id].append(state)
        self.states[entity_id] = state
        
    def get_state(self, entity_id: str) -> Optional[Any]:
        """Get current state."""
        return self.states.get(entity_id)
        
    def get_state_history(self, entity_id: str) -> List[Any]:
        """Get state history."""
        return self.history.get(entity_id, [])
        
    def clear(self) -> None:
        """Clear all states."""
        self.states.clear()
        self.history.clear()


class MockAwarenessSystem:
    """Mock awareness system for testing."""
    
    def __init__(self):
        self.awareness_states = {}
        self.conditions = None
        
    def update_awareness(self,
                        observer_id: str,
                        target_id: str,
                        observer_stats: dict,
                        target_stats: dict,
                        distance: float,
                        angle: float,
                        current_time: float) -> Any:
        """Record awareness update."""
        key = (observer_id, target_id)
        
        if key not in self.awareness_states:
            self.awareness_states[key] = []
            
        state = type("AwarenessState", (), {
            "confidence": 0.8,
            "zone": "CLEAR",
            "last_update_time": current_time
        })()
        
        self.awareness_states[key].append(state)
        return state
        
    def get_awareness(self,
                     observer_id: str,
                     target_id: str) -> Optional[Any]:
        """Get current awareness state."""
        key = (observer_id, target_id)
        states = self.awareness_states.get(key, [])
        return states[-1] if states else None
        
    def update_conditions(self, conditions: Any) -> None:
        """Update environment conditions."""
        self.conditions = conditions
        
    def clear(self) -> None:
        """Clear all states."""
        self.awareness_states.clear()
        self.conditions = None


class MockCombatSystem:
    """Mock combat system for testing."""
    
    def __init__(self):
        self.event_dispatcher = MockEventDispatcher()
        self.action_resolver = MockActionResolver()
        self.state_manager = MockStateManager()
        self.awareness_system = MockAwarenessSystem()
        self.timing_manager = MockTimingManager()
        self.combatants = {}
        self.current_time = 0.0
        
    def add_combatant(self, combatant: Any) -> None:
        """Add combatant to system."""
        self.combatants[combatant.id] = combatant
        
    def execute_action(self, action: ActionState) -> Any:
        """Execute combat action."""
        source = self.combatants.get(action.source_id)
        target = self.combatants.get(action.target_id) if action.target_id else None
        
        source_state = self.state_manager.get_state(action.source_id)
        target_state = self.state_manager.get_state(action.target_id) if action.target_id else None
        
        result = self.action_resolver.resolve_action(
            action,
            source_state,
            target_state
        )
        
        # Generate event
        event = EnhancedEvent(
            event_id=f"test_{len(self.event_dispatcher.events)}",
            event_type=action.action_type,
            category=EventCategory.COMBAT,
            importance=EventImportance.MAJOR,
            timestamp=datetime.now(),
            source_id=action.source_id,
            target_id=action.target_id,
            data={"result": result}
        )
        self.event_dispatcher.dispatch_event(event)
        
        return result
        
    def update(self, delta_time: float) -> None:
        """Update system state."""
        self.current_time += delta_time
        
    def clear(self) -> None:
        """Clear system state."""
        self.event_dispatcher.clear()
        self.action_resolver.clear()
        self.state_manager.clear()
        self.awareness_system.clear()
        self.combatants.clear()
        self.current_time = 0.0
