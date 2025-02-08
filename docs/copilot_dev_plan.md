I'll help analyze and enhance the combat system following the provided guidelines. Let's break this down systematically.

# 1. Current System Analysis

## Core Components Overview
From the provided codebase, we have:

1. **Combat System** (`combat/combat_system.py`)
   - Manages battle state and flow
   - Handles action resolution
   - Processes events
   - Manages combat logging

2. **Combatant** (`combat/combatant.py`)
   - Handles character state
   - Manages resources (health, stamina)
   - Controls action decisions
   - Tracks combat stats

3. **Action System**
   - Predefined action types
   - Action chaining
   - Priority-based execution
   - Resource costs

## Strengths
1. **Well-defined action flow**
   - Clear priority system
   - Structured action chains
   - Comprehensive event logging

2. **Resource Management**
   - Health and stamina systems
   - Blocking power mechanics
   - Distance-based positioning

3. **State Tracking**
   - Detailed event logging
   - Combat state preservation
   - Action history tracking

## Key Issues

### 1. Architectural Concerns
```markdown
1. High Coupling
   - CombatSystem directly manipulates Combatant states
   - Tight integration between components
   - Mixed responsibilities in event handling

2. State Management
   - Mutable state modifications
   - Scattered state tracking
   - Complex state synchronization

3. Type Safety
   - Heavy reliance on dictionaries
   - Implicit data structures
   - Limited validation
```

### 2. Missing Features
```markdown
1. Error Handling
   - Limited validation
   - No recovery mechanisms
   - Incomplete state verification

2. Combat Mechanics
   - Basic positioning system
   - Limited tactical options
   - No combo system
   - No environmental factors

3. State Management
   - No serialization support
   - Limited state rollback
   - No pause/resume functionality
```

# 2. Proposed Enhancement Strategy

## Phase 1: Core Architecture

### 1. Service Layer Architecture
```python
from typing import Optional, List
from dataclasses import dataclass
from ..models.combat_state import CombatState
from ..models.action import Action
from ..models.event import CombatEvent

@dataclass
class CombatService:
    """Service layer for combat operations."""
    
    def process_action(self, state: CombatState, action: Action) -> CombatEvent:
        """Process a combat action and return the resulting event."""
        # Validate action
        if not self._validate_action(state, action):
            raise InvalidActionError(f"Invalid action: {action}")
            
        # Create event
        event = self._create_event(state, action)
        
        # Apply state changes
        new_state = self._apply_state_changes(state, event)
        
        # Log event
        self._log_event(event)
        
        return event
```

### 2. Event System Enhancement
```python
from dataclasses import dataclass
from typing import Dict, Any, Optional
from .action import Action
from .combat_state import CombatState

@dataclass(frozen=True)
class CombatEvent:
    """Immutable combat event."""
    id: str
    timestamp: int
    action: Action
    pre_state: CombatState
    post_state: CombatState
    result: Dict[str, Any]
    
    @property
    def state_changes(self) -> Dict[str, Any]:
        """Calculate state changes from pre and post states."""
        return self._calculate_changes(self.pre_state, self.post_state)
```

### Code File Structure

airpg/
├── src/
│   ├── combat/
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── state.py
│   │   │   ├── combatant.py
│   │   │   ├── effects.py
│   │   │   └── actions.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── engine.py
│   │   │   ├── combat_controller.py
│   │   │   └── combat_processor.py
│   │   ├── events/
│   │   │   ├── __init__.py
│   │   │   ├── event.py
│   │   │   └── event_bus.py
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── combat_service.py
│   │       └── state_manager.py
│   ├── characters/
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── character.py
│   │   │   └── stats.py
│   │   └── services/
│   │       ├── __init__.py
│   │       └── character_service.py
│   └── common/
│       ├── __init__.py
│       ├── errors.py
│       ├── constants.py
│       └── utils/
│           ├── __init__.py
│           ├── logger.py
│           └── validators.py
├── tests/
│   ├── combat/
│   │   ├── __init__.py
│   │   ├── models/
│   │   │   ├── test_state.py
│   │   │   └── test_combatant.py
│   │   ├── core/
│   │   │   └── test_engine.py
│   │   └── services/
│   │       └── test_combat_service.py
│   └── characters/
│       ├── __init__.py
│       └── models/
│           └── test_character.py
├── .gitignore
├── pyproject.toml
├── README.md
└── requirements.txt