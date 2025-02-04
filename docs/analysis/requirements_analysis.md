# Requirements Analysis

## 1. Current System Analysis

### 1.1 Action Granularity
- **Current Implementation**: Split actions (e.g., try_attack → release_attack)
- **Necessity**: Required for planned stealth mechanics
- **Key Features**:
  * Action concealment (stealth-based)
  * Feint mechanics (tactical gameplay)
  * Action reaction windows
- **Dependencies**:
  * Stealth system implementation
  * Perception mechanics
  * Combat AI decision making

### 1.2 Timing System
- **Current Implementation**: Millisecond precision
- **Necessity**: Required for planned speed mechanics
- **Key Features**:
  * Real-time reaction simulation
  * Speed-based action modifications
  * Physics-like timing system
- **Future Requirements**:
  * Speed stat implementation
  * Action timing calibration
  * Performance optimization

### 1.3 State Tracking
- **Current Implementation**:
  * Full state history
  * Multiple state attributes
  * Comprehensive validation
- **Future Requirements**:
  * Stealth calculations
  * Speed modifications
  * AI training data collection

### 1.4 Event System
- **Current Implementation**:
  * Comprehensive event logging
  * Full history retention
  * Event-driven architecture
- **Primary Uses**:
  * Animation system reference
  * AI training datasets
  * Combat replay system

## 2. Technical Specifications

### 2.1 Base Time Unit (BTU) System

#### Core Components
```python
# combat/lib/timing.py
class CombatTiming:
    BTU = 100  # 1 BTU = 100ms
    
    @staticmethod
    def to_btu(ms: int) -> float:
        return ms / CombatTiming.BTU
        
    @staticmethod
    def from_btu(btu: float) -> int:
        return int(btu * CombatTiming.BTU)
        
    @staticmethod
    def apply_speed(btu: float, speed: float) -> float:
        return btu * (1.0 / speed)
```

#### Dependencies
1. actions_library.py Updates:
```python
ACTIONS = {
    "attack": {
        "base_time": 5.0,  # BTUs
        "speed_modifier": 1.0,
        "stamina_cost": 10,
    }
}
```

2. combat_system.py Updates:
```python
class CombatSystem:
    def __init__(self):
        self.timer = CombatTiming()
        
    def update(self):
        action_time = self.timer.apply_speed(
            self.next_event.base_time,
            self.next_event.actor.speed
        )
```

3. Interface Updates:
```python
@dataclass
class CombatantState:
    speed: float
    base_time: float
    modified_time: float
```

### 2.2 Action System Enhancement

#### Core Components
```python
class ActionState(Enum):
    FEINT = "feint"
    COMMIT = "commit"
    RELEASE = "release"

class ActionVisibility(Enum):
    HIDDEN = "hidden"
    TELEGRAPHED = "telegraphed"
    REVEALED = "revealed"

@dataclass
class EnhancedAction:
    state: ActionState
    visibility: ActionVisibility
    commitment_time: float
    feint_cost: float
```

#### Dependencies
1. Action Resolution:
```python
class ActionResolver:
    def resolve_feint(self, action: EnhancedAction) -> ActionResult:
        if action.state == ActionState.FEINT:
            return self._handle_feint(action)
        return self._handle_commit(action)
```

2. State Management:
```python
class CombatState:
    def update_visibility(self, stealth: float, perception: float):
        self.visibility = self._calculate_visibility(stealth, perception)
```

### 2.3 Awareness System

#### Core Components
```python
class AwarenessZone(Enum):
    CLEAR = "clear"
    FUZZY = "fuzzy"
    HIDDEN = "hidden"

class PerceptionCheck:
    def __init__(self, base_difficulty: float):
        self.difficulty = base_difficulty
        self.modifiers = []
```

#### Dependencies
1. State Tracking:
```python
@dataclass
class CombatantState:
    awareness_zone: AwarenessZone
    visibility_level: float
    perception_bonus: float
```

2. Combat Resolution:
```python
class CombatSystem:
    def update_awareness(self):
        for combatant in self.combatants:
            self._update_zones(combatant)
            self._check_perception(combatant)
```

### 2.4 Event System Enhancement

#### Core Components
```python
class EventCategory(Enum):
    COMBAT = "combat"
    MOVEMENT = "movement"
    STATE = "state"
    META = "meta"

class EventStream:
    def __init__(self, name: str, filters: List[str]):
        self.name = name
        self.filters = filters
        self._events = deque(maxlen=1000)
```

#### Dependencies
1. Event Dispatch:
```python
class EventDispatcher:
    def __init__(self):
        self.streams = {
            "animation": EventStream("animation", ["movement", "combat"]),
            "ai_training": EventStream("ai_training", ["combat", "state"])
        }
```

2. Event Compression:
```python
class CompressedEvent:
    def __init__(self, base_event: CombatEvent):
        self.type = base_event.type
        self.count = 1
        self.start_time = base_event.time
```

## 3. Implementation Strategy

### 3.1 Phase Order
1. Base Time Unit System
   - Foundation for other changes
   - Minimal impact on existing code
   - Easy to test and validate

2. Event System Enhancement
   - Required for action visibility
   - Needed for awareness tracking
   - Supports AI training

3. Action System Enhancement
   - Builds on BTU system
   - Uses enhanced events
   - Core gameplay impact

4. Awareness System
   - Uses all previous systems
   - Most complex integration
   - Final gameplay layer

### 3.2 Critical Path
1. BTU System → Action Timing
2. Event Categories → Action Visibility
3. Action States → Awareness System
4. All Systems → AI Training

### 3.3 Testing Strategy
1. Unit Tests:
   - Time conversion accuracy
   - Event compression integrity
   - State transition validation

2. Integration Tests:
   - Action flow validation
   - Event stream consistency
   - System synchronization

3. Performance Tests:
   - Event throughput
   - State update frequency
   - Memory usage patterns
