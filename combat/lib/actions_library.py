"""
Actions Library

This module defines all available combat actions and their properties,
integrating with the core combat systems.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from combat.lib.action_system import (
    ActionStateType,
    ActionVisibility,
    ActionCommitment,
    ActionPhase,
    ActionState
)

# Action definitions with their base properties
ACTIONS = {
    # Attack actions
    "quick_attack": {
        "category": "attack",
        "stamina_cost": 15,
        "time": 800,  # milliseconds
        "speed_requirement": 0.8,
        "description": "A fast, light attack",
        "properties": {
            "damage_multiplier": 0.8,
            "accuracy": 0.9
        }
    },
    "heavy_attack": {
        "category": "attack",
        "stamina_cost": 30,
        "time": 1500,
        "speed_requirement": 0.6,
        "description": "A slow but powerful attack",
        "properties": {
            "damage_multiplier": 1.5,
            "accuracy": 0.7
        }
    },
    
    # Defense actions
    "block": {
        "category": "defense",
        "stamina_cost": 10,
        "time": 1000,
        "description": "A basic defensive stance",
        "properties": {
            "block_multiplier": 1.0,
            "mobility_penalty": 0.5
        }
    },
    "parry": {
        "category": "defense",
        "stamina_cost": 20,
        "time": 500,
        "speed_requirement": 0.9,
        "description": "A quick defensive counter",
        "properties": {
            "counter_window": 0.2,
            "counter_multiplier": 1.2
        }
    },
    
    # Movement actions
    "move_forward": {
        "category": "movement",
        "stamina_cost": 5,
        "time": 500,
        "description": "Advance toward opponent",
        "properties": {
            "distance": 2.0
        }
    },
    "move_backward": {
        "category": "movement",
        "stamina_cost": 5,
        "time": 600,
        "description": "Retreat from opponent",
        "properties": {
            "distance": 2.0,
            "speed_penalty": 0.8
        }
    },
    
    # Evasion actions
    "evade": {
        "category": "movement",
        "stamina_cost": 15,
        "time": 400,
        "speed_requirement": 0.7,
        "description": "Quick evasive movement",
        "properties": {
            "evasion_bonus": 0.5,
            "distance": 1.5
        }
    },
    
    # Recovery actions
    "recover": {
        "category": "neutral",
        "stamina_cost": 0,
        "time": 1500,
        "description": "Catch breath and recover stamina",
        "properties": {
            "stamina_recovery": 20,
            "vulnerability": 1.5
        }
    }
}

def create_action(
    action_type: str,
    source_id: str,
    target_id: Optional[str] = None,
    visibility: ActionVisibility = ActionVisibility.TELEGRAPHED,
    commitment: ActionCommitment = ActionCommitment.NONE
) -> ActionState:
    """
    Create a new action instance.
    
    Args:
        action_type: Type of action to create
        source_id: ID of action source
        target_id: Optional target ID
        visibility: Action visibility
        commitment: Action commitment level
        
    Returns:
        New action state
        
    Raises:
        ValueError: If action type is invalid
    """
    if action_type not in ACTIONS:
        raise ValueError(f"Invalid action type: {action_type}")
        
    props = ACTIONS[action_type]
    
    # Calculate base stamina cost
    stamina_cost = props["stamina_cost"]
    
    # Apply commitment modifiers
    if commitment == ActionCommitment.PARTIAL:
        stamina_cost *= 1.2  # 20% increase
    elif commitment == ActionCommitment.FULL:
        stamina_cost *= 1.5  # 50% increase
        
    # Calculate feint cost
    feint_cost = stamina_cost * 0.5 if props["category"] == "attack" else 0
    
    return ActionState(
        action_id=f"{source_id}_{action_type}",
        action_type=action_type,
        source_id=source_id,
        target_id=target_id,
        state=ActionStateType.FEINT,
        phase=ActionPhase.STARTUP,
        visibility=visibility,
        commitment=commitment,
        properties={
            "stamina_cost": stamina_cost,
            "feint_cost": feint_cost,
            "speed_requirement": props.get("speed_requirement", 0.0),
            **props["properties"]
        }
    )

def validate_action_chain(actions: List[ActionState]) -> bool:
    """
    Validate a chain of actions.
    
    Args:
        actions: List of actions to validate
        
    Returns:
        Whether chain is valid
    """
    if not actions:
        return True
        
    for i in range(len(actions) - 1):
        current = actions[i]
        next_action = actions[i + 1]
        
        # Can't chain after full commitment
        if current.commitment == ActionCommitment.FULL:
            return False
            
        # Can't chain certain categories
        if current.action_type == next_action.action_type:
            return False
            
        # Movement restrictions
        if (current.action_type == "move_backward" and
            next_action.action_type == "move_forward"):
            return False
            
        # Attack restrictions
        if (ACTIONS[current.action_type]["category"] == "attack" and
            ACTIONS[next_action.action_type]["category"] == "attack"):
            return False
            
    return True

def get_available_actions(state: 'CombatantState') -> List[ActionState]:
    """
    Get list of available actions for a combatant.
    
    Args:
        state: Current combatant state
        
    Returns:
        List of available actions
    """
    available = []
    
    for action_type, props in ACTIONS.items():
        # Check stamina cost
        if state.stamina < props["stamina_cost"]:
            continue
            
        # Check speed requirement
        if "speed_requirement" in props:
            if state.speed < props["speed_requirement"]:
                continue
                
        # Add basic version
        available.append(create_action(
            action_type,
            state.entity_id
        ))
        
        # Add committed versions if enough stamina
        if state.stamina >= props["stamina_cost"] * 1.2:
            available.append(create_action(
                action_type,
                state.entity_id,
                commitment=ActionCommitment.PARTIAL
            ))
            
        if state.stamina >= props["stamina_cost"] * 1.5:
            available.append(create_action(
                action_type,
                state.entity_id,
                commitment=ActionCommitment.FULL
            ))
            
        # Add hidden version for applicable actions
        if props["category"] in ["attack", "movement"]:
            if state.stealth >= 1.0:
                available.append(create_action(
                    action_type,
                    state.entity_id,
                    visibility=ActionVisibility.HIDDEN
                ))
                
    return available
