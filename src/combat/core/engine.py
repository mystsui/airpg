from typing import Dict, List, Optional, Tuple
from ..models.state import CombatState
from ..models.actions import Action, ActionResult
from ..models.combatant import CombatantState
from ..events.event import CombatEvent
from ..events.event_bus import EventBus

class CombatEngine:
    """
    Core combat simulation engine.
    Handles the execution of combat actions and maintains combat state.
    """
    def __init__(self):
        self._event_bus = EventBus()
        self._current_state: Optional[CombatState] = None
        self._action_queue: List[Tuple[str, Action]] = []

    def initialize_combat(self, initial_state: CombatState) -> None:
        """Initialize a new combat instance with the given state."""
        self._current_state = initial_state
        self._action_queue.clear()
        
        # Create event data
        event_data = {
            "combat_id": initial_state.id,
            "participants": list(initial_state.combatants.keys()),
            "initial_state": initial_state,
            "type": "combat.initialized"  # Add type field
        }
        
        self._event_bus.publish("combat.initialized", event_data)
        self._event_bus.publish("combat.start", event_data)

    def queue_action(self, combatant_id: str, action: Action) -> bool:
        """
        Queue an action for execution.
        Returns True if action was successfully queued.
        """
        if not self._current_state:
            raise RuntimeError("Combat not initialized")

        if combatant_id not in self._current_state.combatants:
            return False

        combatant = self._current_state.combatants[combatant_id]
        if not action.validate(combatant):
            return False

        self._action_queue.append((combatant_id, action))
        self._event_bus.publish("action.queued", {"combatant_id": combatant_id, "action": action})
        return True

    def process_round(self) -> List[ActionResult]:
        """
        Process a single round of combat.
        Returns the results of all actions executed.
        """
        if not self._current_state:
            raise RuntimeError("Combat not initialized")

        # Sort actions by priority
        self._action_queue.sort(key=lambda x: x[1].priority.value, reverse=True)
        
        results: List[ActionResult] = []
        new_state = self._current_state.clone()

        # Process each action
        for combatant_id, action in self._action_queue:
            result = self._execute_action(new_state, combatant_id, action)
            results.append(result)
            
            # Publish event for action completion
            event = CombatEvent(
                action=action,
                result=result,
                pre_state=self._current_state,
                post_state=new_state
            )
            self._event_bus.publish("action.completed", event)

        # Update state and clear queue
        self._current_state = new_state
        self._current_state.round_number += 1
        self._action_queue.clear()

        # Publish round completion event
        self._event_bus.publish("round.completed", self._current_state)
        return results

    def _execute_action(
        self, 
        state: CombatState, 
        combatant_id: str, 
        action: Action
    ) -> ActionResult:
        """Execute a single action and return its result."""
        actor = state.combatants[combatant_id]
        target = state.combatants.get(action.target_id) if action.target_id else None

        # Validate action can still be performed
        if not action.validate(actor, target):
            return ActionResult(
                action_id=action.id,
                success=False,
                messages=["Action requirements not met"]
            )

        # Apply action costs
        actor.stamina -= action.costs.stamina
        actor.health -= action.costs.health

        # TODO: Implement specific action type handling
        # This will be expanded based on ActionType implementations

        return ActionResult(
            action_id=action.id,
            success=True,
            effects={"stamina_cost": action.costs.stamina}
        )

    @property
    def current_state(self) -> Optional[CombatState]:
        """Get the current combat state."""
        return self._current_state

    def subscribe(self, event_type: str, handler) -> None:
        """Subscribe to combat events."""
        self._event_bus.subscribe(event_type, handler)