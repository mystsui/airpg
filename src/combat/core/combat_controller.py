from typing import Dict, List, Optional
from uuid import UUID
from ..models.state import CombatState
from ..models.actions import Action, ActionResult
from ..models.combatant import CombatantState
from .engine import CombatEngine
from ..services.state_manager import StateManager

class CombatController:
    """
    High-level combat control interface.
    Manages combat flow and provides API for combat interactions.
    """
    def __init__(self):
        self._engine = CombatEngine()
        self._state_manager = StateManager()
        self._active_combat_id: Optional[UUID] = None
        
        # Register event handlers
        self._engine.subscribe("combat.initialized", self._on_combat_initialized)
        self._engine.subscribe("round.completed", self._on_round_completed)

    def start_combat(self, combatants: Dict[str, CombatantState]) -> UUID:
        """
        Initialize and start a new combat instance.
        Returns the combat ID.
        """
        initial_state = CombatState(combatants=combatants)
        self._engine.initialize_combat(initial_state)
        self._active_combat_id = initial_state.id
        self._state_manager.save_state(initial_state)
        return initial_state.id

    def submit_action(self, combatant_id: str, action: Action) -> bool:
        """
        Submit an action for a combatant.
        Returns True if action was successfully queued.
        """
        if not self._active_combat_id:
            raise RuntimeError("No active combat session")
        
        return self._engine.queue_action(combatant_id, action)

    def advance_round(self) -> List[ActionResult]:
        """
        Process the next round of combat.
        Returns the results of all actions executed.
        """
        if not self._active_combat_id:
            raise RuntimeError("No active combat session")
            
        results = self._engine.process_round()
        self._state_manager.save_state(self._engine.current_state)
        return results

    def get_current_state(self) -> Optional[CombatState]:
        """Get the current combat state."""
        return self._engine.current_state

    def end_combat(self) -> None:
        """End the current combat session."""
        if self._active_combat_id:
            final_state = self._engine.current_state
            self._state_manager.archive_combat(self._active_combat_id)
            self._active_combat_id = None

    def _on_combat_initialized(self, state: CombatState) -> None:
        """Handle combat initialization events."""
        # Add any initialization logging or state tracking here
        pass

    def _on_round_completed(self, state: CombatState) -> None:
        """Handle round completion events."""
        # Add any round completion processing here
        pass

    @property
    def is_combat_active(self) -> bool:
        """Check if there's an active combat session."""
        return self._active_combat_id is not None

    def get_combat_history(self, combat_id: UUID) -> List[CombatState]:
        """Retrieve the history of states for a specific combat."""
        return self._state_manager.get_combat_history(combat_id)