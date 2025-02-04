# Combat System Developer Guide

## Overview

The Combat System is a sophisticated turn-based combat engine designed for role-playing games. It features a unique blend of strategic depth and tactical complexity, powered by several interconnected systems that handle timing, actions, events, and awareness.

### Key Concepts

1. **BTU (Base Time Unit)**
   - The fundamental unit of time in the combat system
   - All actions and effects are measured in BTUs
   - Allows for precise timing and speed calculations
   - Example: A quick attack might take 3 BTUs, while a heavy attack takes 5 BTUs

2. **Action States**
   - **Feint**: Initial action state, can be cancelled or committed
   - **Commit**: Action is locked in, some commitment levels allow cancellation
   - **Release**: Action is executing
   - **Recovery**: Post-action recovery phase

3. **Combat Flow**
   ```
   [Start] -> Feint -> Commit -> Release -> Recovery -> [End]
                ↑        |
                |        |
             (Cancel) (Cancel*)
             
   * Cancel availability depends on commitment level
   ```

## Core Systems

### 1. BTU System (`combat/lib/timing.py`)
The BTU system manages all timing-related aspects of combat.

```python
# Example: Converting real time to BTUs
def real_time_to_btu(milliseconds: float) -> float:
    return milliseconds / BTU_MILLISECONDS

# Example: Applying speed modifiers
def apply_speed_modifier(base_time: float, speed: float) -> float:
    return base_time * (1.0 / speed)
```

Key Features:
- Time conversion utilities
- Speed modification system
- Time modifier framework
- Action timing management

### 2. Event System (`combat/lib/event_system.py`)
The event system handles all combat-related events and their propagation.

Event Categories:
- `COMBAT`: Direct combat actions
- `MOVEMENT`: Position changes
- `STATE`: State changes
- `ANIMATION`: Visual effects
- `AI`: AI decision making
- `META`: System events
- `DEBUG`: Debug information

Example Event Flow:
```python
# Creating and dispatching an event
event = EnhancedEvent(
    event_id="attack_1",
    event_type="quick_attack",
    category=EventCategory.COMBAT,
    importance=EventImportance.MAJOR,
    timestamp=datetime.now(),
    source_id="attacker",
    target_id="defender",
    data={"damage": 50}
)
event_dispatcher.dispatch_event(event)
```

### 3. Action System (`combat/lib/action_system.py`)
The action system manages all combat actions and their execution.

Key Components:
1. **Visibility**
   - `TELEGRAPHED`: Clearly visible to opponents
   - `HIDDEN`: Stealthy actions that may be harder to detect

2. **Commitment Levels**
   - `NONE`: Can be cancelled anytime
   - `PARTIAL`: Limited cancellation with cost
   - `FULL`: Cannot be cancelled

Example Action Creation:
```python
# Creating a basic attack action
action = create_action(
    "quick_attack",
    source_id="fighter_1",
    target_id="fighter_2",
    visibility=ActionVisibility.TELEGRAPHED,
    commitment=ActionCommitment.PARTIAL
)
```

### 4. Awareness System (`combat/lib/awareness_system.py`)
The awareness system handles perception and visibility between combatants.

Awareness Zones:
- `CLEAR`: Full awareness
- `FUZZY`: Partial awareness
- `HIDDEN`: No awareness
- `PERIPHERAL`: Edge of awareness

Example Usage:
```python
# Updating awareness between combatants
awareness = awareness_system.update_awareness(
    observer_id="fighter_1",
    target_id="fighter_2",
    distance=10.0,
    angle=45.0,
    current_time=1000
)
```

## Integration Layer

### Interfaces (`combat/interfaces/`)
The system uses interfaces to define clear contracts between components:

1. `ICombatant`
   - Base interface for all combatant entities
   - Defines required stats and methods
   - Ensures consistent interaction

2. `IActionResolver`
   - Handles action resolution
   - Determines success/failure
   - Calculates effects

3. `IStateManager`
   - Manages combat state
   - Handles state transitions
   - Maintains history

4. `IEventDispatcher`
   - Manages event flow
   - Handles subscriptions
   - Routes events

### Adapters (`combat/adapters/`)
Adapters provide implementation of interfaces:

```python
# Example adapter usage
class CombatantAdapter(ICombatant):
    def __init__(self, legacy_combatant):
        self.combatant = legacy_combatant
        
    def get_stats(self) -> Dict[str, float]:
        return {
            "stamina": self.combatant.stamina,
            "speed": self.combatant.speed,
            "stealth": self.combatant.stealth
        }
```

## Development Workflow

### 1. Making Changes

1. Update Documentation:
   - Update relevant analysis docs in `docs/analysis/`
   - Update CHANGELOG.md
   - Update implementation schedule

2. Write Tests:
   - Unit tests for new functionality
   - Integration tests for system interaction
   - Performance tests if needed

3. Implement Changes:
   - Follow existing patterns
   - Use interfaces and adapters
   - Maintain backward compatibility

### 2. Testing Process

1. Run Unit Tests:
```bash
pytest tests/combat/test_timing.py
pytest tests/combat/test_event_system.py
pytest tests/combat/test_action_system.py
pytest tests/combat/test_awareness_system.py
```

2. Run Integration Tests:
```bash
pytest tests/combat/test_core_integration.py
pytest tests/combat/test_adapter_integration.py
pytest tests/combat/test_system_health.py
```

3. Check Performance:
```bash
pytest tests/combat/test_system_health.py::TestTimingPerformance
```

### 3. Common Tasks

#### Adding a New Action
1. Define action in `combat/lib/actions_library.py`:
```python
ACTIONS["new_action"] = {
    "category": "attack",
    "stamina_cost": 20,
    "time": 1000,
    "speed_requirement": 0.7,
    "description": "New action description",
    "properties": {
        "damage_multiplier": 1.2,
        "accuracy": 0.8
    }
}
```

2. Add tests in `tests/combat/test_actions_library.py`
3. Update documentation

#### Modifying Combat Rules
1. Identify affected systems
2. Update relevant configuration
3. Add/modify tests
4. Update documentation

## Debugging Tips

1. Use Event Streams:
```python
events = combat_system._event_dispatcher.get_stream("combat").get_events()
for event in events:
    print(f"{event.event_type}: {event.data}")
```

2. Check State History:
```python
history = combat_system._state_manager.get_state_history(combatant_id)
for state in history:
    print(f"Time: {state.timestamp}, Stamina: {state.stamina}")
```

3. Monitor Performance:
```python
with PerformanceStats() as stats:
    # Your code here
    print(f"Operation took: {stats.get_last_operation_time()}ms")
```

## Best Practices

1. Always use interfaces for new components
2. Write tests before implementation
3. Document changes in CHANGELOG.md
4. Update analysis docs for significant changes
5. Use type hints and docstrings
6. Follow existing patterns and naming conventions
7. Consider performance implications
8. Maintain backward compatibility

## Next Steps

See `docs/analysis/implementation_schedule.md` for upcoming features and improvements.
