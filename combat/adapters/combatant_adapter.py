"""
Combatant Adapter Module

This module provides an adapter that makes the existing Combatant class
compatible with the new ICombatant interface, including enhanced combat mechanics.
"""

from typing import Optional, Tuple
from combat.interfaces import (
    ICombatant,
    CombatantState,
    Action,
    ITimingManager,
    IAwarenessManager
)
from combat.lib.timing import TimingSystem
from combat.lib.awareness_system import AwarenessSystem, AwarenessZone
from combat.combatant import Combatant

class CombatantAdapter(ICombatant):
    """
    Adapter class that makes the existing Combatant class compatible with ICombatant.
    This allows for gradual migration to the new interface-based system while
    maintaining backward compatibility.
    """
    
    def __init__(self, adaptee: Combatant):
        """
        Initialize the adapter with an existing Combatant instance.
        
        Args:
            adaptee: The existing Combatant instance to adapt
        """
        self._adaptee = adaptee
        self._timing_manager: ITimingManager = TimingSystem()
        self._awareness_manager: IAwarenessManager = AwarenessSystem()
        self._last_clear_position: Optional[Tuple[float, float]] = None

    def get_state(self) -> CombatantState:
        """
        Get the current state of the combatant.
        
        Returns:
            CombatantState object representing current combatant state
        """
        # Parse position into x,y coordinates
        try:
            x, y = map(float, self._adaptee.position.split(','))
        except (ValueError, AttributeError):
            x, y = 0.0, 0.0

        # Calculate movement based on position change
        movement = 0.0
        if hasattr(self._adaptee, 'previous_position'):
            prev_x, prev_y = map(float, self._adaptee.previous_position.split(','))
            movement = ((x - prev_x) ** 2 + (y - prev_y) ** 2) ** 0.5

        return CombatantState(
            entity_id=str(self._adaptee.combatant_id),
            health=self._adaptee.health,
            max_health=self._adaptee.max_health,
            stamina=self._adaptee.stamina,
            max_stamina=self._adaptee.max_stamina,
            position=self._adaptee.position,
            facing=self._adaptee.facing,
            blocking_power=self._adaptee.blocking_power,
            action=self._adaptee.action,
            team=self._adaptee.team,
            # New fields
            speed=getattr(self._adaptee, 'speed', 1.0),
            stealth=getattr(self._adaptee, 'stealth', 1.0),
            perception=getattr(self._adaptee, 'perception', 1.0),
            awareness_zone=getattr(self._adaptee, 'awareness_zone', AwarenessZone.CLEAR),
            visibility_level=getattr(self._adaptee, 'visibility_level', 1.0),
            last_clear_position=self._last_clear_position,
            position_x=x,
            position_y=y,
            movement=movement
        )

    def apply_action(self, action: Action) -> None:
        """
        Apply an action to the combatant.
        
        Args:
            action: The action to apply
        """
        # Convert time to BTUs
        btu_time = self._timing_manager.convert_to_btu(int(action.time))
        
        # Apply speed modifier
        modified_time = self._timing_manager.apply_speed(
            btu_time,
            self.get_state().speed * action.speed_modifier
        )
        
        # Convert new Action type to old action dictionary format
        legacy_action = {
            "type": action.type,
            "time": modified_time,
            "combatant": self._adaptee,
            "status": action.status,
            "target": None,  # Target handling will need to be updated
            "state": action.state.value,
            "visibility": action.visibility.value,
            "commitment": action.commitment.value,
            "phase_duration": action.phase_duration,
            "feint_cost": action.feint_cost
        }
        
        # Store current position for movement calculation
        self._adaptee.previous_position = self._adaptee.position
        
        # Use existing action application logic
        self._adaptee.action = legacy_action

    def validate_action(self, action: Action) -> bool:
        """
        Validate if an action can be performed.
        
        Args:
            action: The action to validate
            
        Returns:
            bool: True if the action can be performed, False otherwise
        """
        from combat.lib.actions_library import ACTIONS
        
        # Check if action exists in actions library
        if action.type not in ACTIONS:
            return False
            
        # Get current state
        state = self.get_state()
            
        # Check stamina requirements
        total_stamina_cost = ACTIONS[action.type]["stamina_cost"]
        if action.state == ActionState.FEINT:
            total_stamina_cost += action.feint_cost
            
        if state.stamina < total_stamina_cost:
            return False
            
        # Check speed requirements
        if "speed_requirement" in ACTIONS[action.type]:
            if state.speed < ACTIONS[action.type]["speed_requirement"]:
                return False
                
        return True

    def is_within_range(self, distance: float) -> bool:
        """
        Check if target is within attack range.
        
        Args:
            distance: The current distance to check
            
        Returns:
            bool: True if within range, False otherwise
        """
        return self._adaptee.is_within_range(distance)

    def is_facing_opponent(self, opponent: ICombatant) -> bool:
        """
        Check if facing the opponent.
        
        Args:
            opponent: The opponent to check facing against
            
        Returns:
            bool: True if facing opponent, False otherwise
        """
        # If opponent is also an adapter, get the underlying Combatant
        if isinstance(opponent, CombatantAdapter):
            opponent = opponent._adaptee
            
        return self._adaptee.is_facing_opponent(opponent)

    def is_defeated(self) -> bool:
        """
        Check if combatant is defeated.
        
        Returns:
            bool: True if defeated, False otherwise
        """
        return self._adaptee.is_defeated()

    def update_awareness(self, 
                        target: ICombatant,
                        distance: float,
                        angle: float,
                        current_time: float) -> None:
        """
        Update awareness state for a target.
        
        Args:
            target: The target combatant
            distance: Distance to target
            angle: Viewing angle to target
            current_time: Current time in BTUs
        """
        # Get states
        observer_state = self.get_state()
        target_state = target.get_state()
        
        # Update awareness
        awareness = self._awareness_manager.update_awareness(
            observer_id=observer_state.entity_id,
            target_id=target_state.entity_id,
            observer_stats={"perception": observer_state.perception},
            target_stats={
                "stealth": target_state.stealth,
                "movement": target_state.movement,
                "position_x": target_state.position_x,
                "position_y": target_state.position_y
            },
            distance=distance,
            angle=angle,
            current_time=current_time
        )
        
        # Update last clear position
        if awareness.zone == AwarenessZone.CLEAR:
            self._last_clear_position = (target_state.position_x, target_state.position_y)
            
        # Update adaptee
        self._adaptee.awareness_zone = awareness.zone
        self._adaptee.visibility_level = awareness.confidence

    @property
    def adaptee(self) -> Combatant:
        """
        Get the underlying Combatant instance.
        
        Returns:
            The adapted Combatant instance
        """
        return self._adaptee
