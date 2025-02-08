from typing import Dict, List, Optional
from uuid import UUID
import json
from datetime import datetime
from pathlib import Path
from ..models.state import CombatState
from ..common.errors import StateManagementError

class StateManager:
    """
    Manages the persistence and retrieval of combat states.
    Handles state history, archiving, and restoration.
    """
    
    def __init__(self, storage_path: Optional[Path] = None):
        self._storage_path = storage_path or Path("combat_states")
        self._active_states: Dict[UUID, List[CombatState]] = {}
        self._initialize_storage()

    def _initialize_storage(self) -> None:
        """Initialize the storage directory structure."""
        try:
            # Create main storage directory
            self._storage_path.mkdir(parents=True, exist_ok=True)
            
            # Create subdirectories
            (self._storage_path / "active").mkdir(exist_ok=True)
            (self._storage_path / "archived").mkdir(exist_ok=True)
        except Exception as e:
            raise StateManagementError(f"Failed to initialize storage: {str(e)}")

    def save_state(self, state: CombatState) -> None:
        """
        Save a combat state to active storage.
        
        Args:
            state: Combat state to save
        """
        try:
            if state.id not in self._active_states:
                self._active_states[state.id] = []
            
            self._active_states[state.id].append(state)
            self._persist_state(state)
            
        except Exception as e:
            raise StateManagementError(f"Failed to save state: {str(e)}")

    def get_combat_history(self, combat_id: UUID) -> List[CombatState]:
        """
        Retrieve the history of states for a combat instance.
        
        Args:
            combat_id: ID of the combat instance
            
        Returns:
            List of historical combat states
        """
        return self._active_states.get(combat_id, []).copy()

    def archive_combat(self, combat_id: UUID) -> None:
        """
        Archive a completed combat's state history.
        
        Args:
            combat_id: ID of the combat instance to archive
        """
        try:
            if combat_id not in self._active_states:
                return

            states = self._active_states[combat_id]
            archive_path = self._get_archive_path(combat_id)
            
            self._save_to_archive(states, archive_path)
            self._cleanup_active_state(combat_id)
            
        except Exception as e:
            raise StateManagementError(f"Failed to archive combat: {str(e)}")

    def load_archived_combat(self, combat_id: UUID) -> List[CombatState]:
        """
        Load an archived combat's state history.
        
        Args:
            combat_id: ID of the archived combat
            
        Returns:
            List of historical combat states
        """
        try:
            archive_path = self._get_archive_path(combat_id)
            if not archive_path.exists():
                return []

            return self._load_from_archive(archive_path)
            
        except Exception as e:
            raise StateManagementError(f"Failed to load archived combat: {str(e)}")

    def _persist_state(self, state: CombatState) -> None:
        """Persist a state to the file system."""
        state_path = self._get_state_path(state.id)
        state_data = self._serialize_state(state)
        
        with open(state_path, 'w') as f:
            json.dump(state_data, f, indent=2)

    def _get_state_path(self, combat_id: UUID) -> Path:
        """Get the file path for an active combat state."""
        return self._storage_path / "active" / f"{str(combat_id)}.json"

    def _get_archive_path(self, combat_id: UUID) -> Path:
        """Get the file path for an archived combat."""
        return self._storage_path / "archived" / f"{str(combat_id)}.json"

    def _serialize_state(self, state: CombatState) -> dict:
        """Convert a combat state to a serializable format."""
        return {
            "id": str(state.id),
            "timestamp": state.timestamp,
            "round_number": state.round_number,
            "combatants": {
                cid: self._serialize_combatant(combatant)
                for cid, combatant in state.combatants.items()
            },
            "active_effects": [
                self._serialize_effect(effect)
                for effect in state.active_effects
            ]
        }

    def _serialize_combatant(self, combatant) -> dict:
        """Convert a combatant state to a serializable format."""
        return {
            "id": combatant.id,
            "health": combatant.health,
            "max_health": combatant.max_health,
            "stamina": combatant.stamina,
            "max_stamina": combatant.max_stamina,
            "position": combatant.position,
            "status_effects": [
                self._serialize_effect(effect)
                for effect in combatant.status_effects
            ]
        }

    def _serialize_effect(self, effect) -> dict:
        """Convert a status effect to a serializable format."""
        return {
            "id": effect.id,
            "name": effect.name,
            "duration": effect.duration,
            "strength": effect.strength
        }

    def _save_to_archive(self, states: List[CombatState], archive_path: Path) -> None:
        """Save combat states to archive."""
        archive_data = {
            "combat_id": str(states[0].id),
            "archived_at": datetime.now().isoformat(),
            "states": [
                self._serialize_state(state)
                for state in states
            ]
        }
        
        with open(archive_path, 'w') as f:
            json.dump(archive_data, f, indent=2)

    def _cleanup_active_state(self, combat_id: UUID) -> None:
        """Remove active state data after archiving."""
        state_path = self._get_state_path(combat_id)
        if state_path.exists():
            state_path.unlink()
        
        if combat_id in self._active_states:
            del self._active_states[combat_id]

    def _load_from_archive(self, archive_path: Path) -> List[CombatState]:
        """Load combat states from archive."""
        with open(archive_path, 'r') as f:
            archive_data = json.load(f)
            
        return [
            self._deserialize_state(state_data)
            for state_data in archive_data["states"]
        ]

    def _deserialize_state(self, state_data: dict) -> CombatState:
        """Convert serialized data back to a CombatState."""
        # Implementation depends on CombatState constructor
        # This is a placeholder for the actual deserialization logic
        pass