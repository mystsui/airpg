from typing import Optional
from combat.interfaces.awareness import IAwarenessManager, EnvironmentConditions, AwarenessState
from combat.lib.awareness_system import AwarenessSystem

class AwarenessSystemAdapter(IAwarenessManager):
    """Adapter for the AwarenessSystem to implement IAwarenessManager interface."""
    
    def __init__(self):
        self._awareness_system = AwarenessSystem()
    
    def update_awareness(self,
                         observer_id: str,
                         target_id: str,
                         observer_stats: dict,
                         target_stats: dict,
                         distance: float,
                         angle: float,
                         current_time: float) -> AwarenessState:
        """
        Update awareness between entities.
        
        Delegates to the AwarenessSystem implementation.
        """
        return self._awareness_system.update_awareness(
            observer_id, target_id, observer_stats, target_stats, distance, angle, current_time
        )
    
    def get_awareness(self,
                      observer_id: str,
                      target_id: str) -> Optional[AwarenessState]:
        """
        Get the current awareness state between entities.
        """
        return self._awareness_system.get_awareness(observer_id, target_id)
    
    def update_conditions(self, conditions: EnvironmentConditions) -> None:
        """
        Update the environmental conditions used by the awareness system.
        """
        self._awareness_system.update_conditions(conditions)
    
    def calculate_visibility(self,
                             distance: float,
                             angle: float,
                             stealth: float,
                             perception: float,
                             conditions: Optional[EnvironmentConditions] = None) -> float:
        """
        Calculate visibility based on distance, angle, target stealth, observer perception and conditions.
        """
        return self._awareness_system.calculate_visibility(distance, angle, stealth, perception, conditions)