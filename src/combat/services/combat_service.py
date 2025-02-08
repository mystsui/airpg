from typing import Dict, List, Optional
from uuid import UUID

from ..core.combat_controller import CombatController
from ..core.combat_processor import CombatProcessor
from ..models.state import CombatState
from ..models.actions import Action, ActionResult
from ..models.combatant import CombatantState
from ..events.event_bus import EventBus
from ..events.event import CombatStartEvent, CombatEndEvent

class CombatService:
    """
    High-level service for managing combat operations.
    Provides a simplified interface for combat interactions.
    """
    
    def __init__(self):
        self._event_bus = EventBus()
        self._combat_controller = CombatController()
        self._combat_processor = CombatProcessor()
        self._active_combats: Dict[UUID, CombatState] = {}

    def initialize_combat(self, combatants: Dict[str, CombatantState]) -> UUID:
        """
        Initialize a new combat instance.
        
        Args:
            combatants: Dictionary of combatant IDs to their initial states
            
        Returns:
            UUID of the created combat instance
        """
        combat_id = self._combat_controller.start_combat(combatants)
        initial_state = self._combat_controller.get_current_state()
        
        if initial_state:
            self._active_combats[combat_id] = initial_state
            self._event_bus.publish(CombatStartEvent(initial_state=initial_state))
            
        return combat_id

    def submit_action(self, combat_id: UUID, actor_id: str, action: Action) -> bool:
        """
        Submit an action for a combatant in a specific combat instance.
        
        Args:
            combat_id: ID of the combat instance
            actor_id: ID of the acting combatant
            action: Action to perform
            
        Returns:
            True if action was successfully submitted
        """
        if combat_id not in self._active_combats:
            raise ValueError(f"No active combat with ID: {combat_id}")
            
        return self._combat_controller.submit_action(actor_id, action)

    def process_round(self, combat_id: UUID) -> List[ActionResult]:
        """
        Process the next round of combat for a specific instance.
        
        Args:
            combat_id: ID of the combat instance
            
        Returns:
            List of action results from the round
        """
        if combat_id not in self._active_combats:
            raise ValueError(f"No active combat with ID: {combat_id}")
            
        results = self._combat_controller.advance_round()
        new_state = self._combat_controller.get_current_state()
        
        if new_state:
            self._active_combats[combat_id] = new_state
            self._check_combat_end(combat_id, new_state)
            
        return results

    def get_combat_state(self, combat_id: UUID) -> Optional[CombatState]:
        """
        Get the current state of a combat instance.
        
        Args:
            combat_id: ID of the combat instance
            
        Returns:
            Current combat state or None if not found
        """
        return self._active_combats.get(combat_id)

    def end_combat(self, combat_id: UUID, winner_id: Optional[str] = None) -> None:
        """
        End a combat instance.
        
        Args:
            combat_id: ID of the combat instance
            winner_id: Optional ID of the winning combatant
        """
        if combat_id not in self._active_combats:
            raise ValueError(f"No active combat with ID: {combat_id}")
            
        final_state = self._active_combats[combat_id]
        self._event_bus.publish(CombatEndEvent(
            final_state=final_state,
            winner_id=winner_id
        ))
        
        del self._active_combats[combat_id]
        self._combat_controller.end_combat()

    def _check_combat_end(self, combat_id: UUID, state: CombatState) -> None:
        """
        Check if combat should end and determine winner.
        
        Args:
            combat_id: ID of the combat instance
            state: Current combat state
        """
        alive_combatants = [
            cid for cid, combatant in state.combatants.items()
            if combatant.health > 0
        ]
        
        if len(alive_combatants) <= 1:
            winner_id = alive_combatants[0] if alive_combatants else None
            self.end_combat(combat_id, winner_id)

    def subscribe_to_events(self, event_type: str, handler) -> None:
        """
        Subscribe to combat events.
        
        Args:
            event_type: Type of events to subscribe to
            handler: Event handler function
        """
        self._event_bus.subscribe(event_type, handler)

    def get_combat_history(self, combat_id: UUID) -> List[CombatState]:
        """
        Get the history of states for a combat instance.
        
        Args:
            combat_id: ID of the combat instance
            
        Returns:
            List of historical combat states
        """
        return self._combat_controller.get_combat_history(combat_id)