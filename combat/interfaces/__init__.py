"""
Combat system interfaces.
"""

from .action_system import (
    ActionState,
    ActionStateType,
    ActionVisibility,
    ActionCommitment,
    ActionPhase,
    IActionSystem
)

from .timing import (
    CombatTiming,
    ITimingManager
)

from .combatant import (
    CombatantState,
    ICombatant
)

from .resolvers import (
    IActionResolver,
    IStateManager,
    IEventDispatcher
)

from .events import (
    EventCategory,
    EventImportance,
    CombatEvent,
    Action,
    ActionResult
)

from .awareness import (
    AwarenessZone,
    EnvironmentConditions,
    AwarenessState,
    IAwarenessManager
)

__all__ = [
    # Action System
    'ActionState',
    'ActionStateType',
    'ActionVisibility',
    'ActionCommitment',
    'ActionPhase',
    'IActionSystem',
    
    # Timing System
    'CombatTiming',
    'ITimingManager',
    
    # Combatant System
    'CombatantState',
    'ICombatant',
    
    # Resolver System
    'IActionResolver',
    'IStateManager',
    'IEventDispatcher',
    
    # Event System
    'EventCategory',
    'EventImportance',
    'CombatEvent',
    'Action',
    'ActionResult',
    
    # Awareness System
    'AwarenessZone',
    'EnvironmentConditions',
    'AwarenessState',
    'IAwarenessManager'
]
