# Combat System Development Guide

## Overview

This guide provides a step-by-step approach to understanding, debugging, and implementing the combat system. It's designed for developers who are new to the system and need clear explanations of how everything works together.

### What is the Combat System?

The combat system is like a referee in a fighting game. It:
- Manages two fighters (combatants)
- Controls their actions (attacks, blocks, movements)
- Keeps track of their status (health, stamina, position)
- Makes sure everything happens in the right order
- Determines the outcomes of actions

Here's a simple visualization of how it works:

```
[Combatant 1]  ←→  [Combat System]  ←→  [Combatant 2]
    ↓                    ↓                    ↓
Actions              Manages:              Actions
- Attack           - Time                - Block
- Move             - Distance            - Evade
- Block            - Events             - Counter
                   - States
```

### System Architecture Overview

The combat system is built using several interconnected components, like building blocks that work together:

```
┌─────────────────────────────────────────┐
│            Combat System                │
│                                         │
│  ┌─────────┐    ┌─────────┐    ┌────┐  │
│  │ Action  │←→  │ State   │←→  │Event│  │
│  │ System  │    │ Manager │    │System│  │
│  └─────────┘    └─────────┘    └────┘  │
│       ↑             ↑             ↑     │
│       └─────────────┴─────────────┘     │
│              Adapters Layer             │
└─────────────────────────────────────────┘
```

## Understanding the System

### Core Components Explained

1. **CombatSystem** (`combat/combat_system.py`)
   This is like the main referee that:
   - Controls the entire fight
   - Makes sure rules are followed
   - Keeps track of everything happening

   ```python
   # Example of how the CombatSystem works:
   combat = CombatSystem(
       duration=10000,  # Fight lasts 10 seconds
       distance=50,     # Fighters start 50 units apart
       max_distance=100 # Arena size is 100 units
   )
   ```

2. **State Manager**
   Think of this as the scorekeeper that:
   - Records health points
   - Tracks stamina levels
   - Remembers positions
   - Notes current actions

   ```
   State Example:
   Fighter A                Fighter B
   ├── Health: 100         ├── Health: 80
   ├── Stamina: 75         ├── Stamina: 90
   ├── Position: Left      ├── Position: Right
   └── Action: Attacking   └── Action: Blocking
   ```

3. **Action System**
   This is like a move validator that:
   - Checks if moves are legal
   - Makes sure actions happen in order
   - Prevents impossible combinations

   ```
   Action Flow:
   [Start] → Prepare → Commit → Execute → Recover → [End]
      ↑         |
      └─── Can Cancel
   ```

4. **Event System**
   Works like a commentator that:
   - Announces what's happening
   - Keeps a record of all actions
   - Helps other systems react to changes

   ```
   Event Example:
   1. Fighter A starts attack
   2. Fighter B begins blocking
   3. Attack hits block
   4. Both fighters reset positions
   ```

### Current Issues Explained

1. **State Management Problems**
   Imagine a scoreboard that sometimes shows wrong numbers:
   - Sometimes health doesn't update properly
   - Actions might get stuck
   - Game state becomes confused

   ```
   Example Problem:
   Fighter A attacks → Hit lands → Health doesn't update
   Expected: Health 100 → 80
   Actual:   Health 100 → 100 (stuck)
   ```

2. **Action System Issues**
   Like a game that sometimes lets you do impossible moves:
   - Actions don't follow proper order
   - Moves can be done when they shouldn't
   - Some actions get stuck halfway

   ```
   Problem Example:
   Normal Flow:    Attack → Hit → Recover
   Broken Flow:    Attack → ??? → Stuck
   ```

3. **Event System Problems**
   Like a delayed sports commentator:
   - Announcements come too late
   - Some events never get announced
   - Events happen in wrong order

   ```
   Example:
   What Should Happen    What's Happening
   1. Attack starts     1. Attack starts
   2. Block happens     2. Damage happens
   3. Damage happens    3. Block happens (too late!)
   ```

4. **Integration Issues**
   Different parts of the system aren't talking properly:
   - Components don't share information correctly
   - Some parts don't know what others are doing
   - Systems get out of sync

   ```
   Example:
   State Manager: "Fighter is blocking"
   Action System: "Fighter is attacking"
   Event System: "Fighter is idle"
   (They should all agree!)
   ```

## How to Fix the System

### Understanding the Code Structure

Before we dive into fixes, let's understand how the code is organized:

```
combat/
├── combat_system.py     # Main system code
├── lib/                 # Core functionality
│   ├── action_system.py
│   ├── event_system.py
│   └── timing.py
└── interfaces/         # System contracts
    ├── action_system.py
    └── events.py
```

### 1. Fixing State Management

Think of state management like keeping score in a game. We need to make sure the scoreboard (state) always shows the correct numbers.

#### What's Wrong?
```
Problem:
Fighter A (Health: 100) gets hit for 20 damage
↓
System tries to update health
↓
Something interrupts the update
↓
Health stays at 100 (should be 80)
```

#### The Solution:
We use "transactions" - like in banking, where money transfers either complete fully or not at all.

```python
# In CombatSystem.execute_action()
def execute_action(self, action: ActionState) -> None:
    """
    Execute a combat action safely.
    
    Think of this like making a bank transfer:
    1. Check if you have enough money (validate state)
    2. Start a transaction
    3. Update both accounts (update states)
    4. Only complete if everything succeeds
    """
    # 1. First, check if the action is valid
    source_state = self._state_manager.get_state(action.source_id)
    if not self._validate_action_prerequisites(action, source_state):
        raise ValueError("Can't do this action right now!")
        
    # 2. Start a safe update process
    with self._state_manager.transaction() as state_tx:
        # Prepare the new action state
        new_action_state = self._prepare_action_state(action)
        state_tx.update_action_state(new_action_state)
        
        # Update the fighter's state
        new_combatant_state = self._prepare_combatant_state(source_state, action)
        state_tx.update_combatant_state(new_combatant_state)
        
        # If anything goes wrong, the transaction cancels
        # and no partial updates occur!
```

### 2. Making Actions Work Better

Actions in combat are like a dance - steps must happen in the right order. Let's fix that!

#### What's Wrong?
```
Current Problem:
Fighter can do: Attack → Block → Attack (while still blocking!)
Should be:     Attack → Recovery → Block → Recovery → Attack
```

#### The Solution:
We create a strict set of rules about what moves can follow other moves.

```python
# In ActionSystem
def validate_action_chain(self, action: ActionState) -> bool:
    """
    Check if an action is allowed right now.
    
    Like a dance instructor making sure you're doing
    the right move at the right time!
    """
    # 1. Is this a new action?
    current_state = self.get_action_state(action.action_id)
    if not current_state:
        return True  # New actions are always allowed
        
    # 2. Check if this move can follow the current one
    valid_transitions = {
        # From FEINT (preparing) you can:
        ActionStateType.FEINT: [
            ActionStateType.COMMIT,  # Complete the action
            ActionStateType.RECOVERY # Or cancel it
        ],
        # From COMMIT (locked in) you can:
        ActionStateType.COMMIT: [
            ActionStateType.RELEASE, # Execute the action
            ActionStateType.RECOVERY # Or cancel if allowed
        ],
        # From RELEASE (executing) you can only:
        ActionStateType.RELEASE: [
            ActionStateType.RECOVERY # Must recover after
        ],
        # From RECOVERY you can't do anything yet
        ActionStateType.RECOVERY: []
    }
    
    # Check if the new action is allowed
    return action.state in valid_transitions.get(current_state.state, [])
```

### 3. Making Events Work Reliably

Think of the event system like a sports commentator who needs to announce everything in the right order and make sure everyone hears the announcements.

#### What's Wrong?
```
Current Problems:
1. Events get lost (announcer's mic cuts out)
2. Events arrive late (delayed broadcast)
3. Events happen out of order (replay during live game)
```

#### The Solution:
We create a reliable messaging system that guarantees delivery and proper order.

```python
# In EventDispatcherAdapter
def dispatch_event(self, event: CombatEvent) -> None:
    """
    Send an event reliably to all listeners.
    
    Like a TV broadcast:
    1. Make sure we're showing the right replay
    2. Get all the camera angles ready
    3. Broadcast with backup systems
    """
    # 1. Make sure this event makes sense right now
    if not self._validate_event_sequence(event):
        raise ValueError("This event doesn't make sense here!")
        
    # 2. Get everything ready for broadcast
    context = self._prepare_event_context(event)
    
    # 3. Send it out with guaranteed delivery
    with self._event_lock:  # Like having exclusive broadcast rights
        self._dispatch_with_retry(event, context)  # Try multiple times if needed
        self._update_event_chain(event)  # Record what we've shown
```

### 4. Making Everything Work Together

Think of this like coordinating a big sports event where everyone (referees, commentators, scorekeepers) needs to agree on what's happening.

#### 4.1 Keeping Everyone in Sync
```python
# In CombatSystem
def synchronize_states(self) -> None:
    """
    Make sure everyone agrees on what's happening.
    
    Like checking that:
    - Scoreboard shows correct score
    - Referee sees current game state
    - Commentators know current situation
    """
    # 1. Get everyone's version of events
    action_states = self._action_system.get_all_states()    # What moves are happening
    combatant_states = self._state_manager.get_all_states() # Fighter conditions
    awareness_states = self._awareness_system.get_all_states() # Who sees what
    
    # 2. Look for disagreements
    inconsistencies = self._find_state_inconsistencies(
        action_states,
        combatant_states,
        awareness_states
    )
    
    # 3. Fix any disagreements found
    if inconsistencies:
        self._resolve_state_inconsistencies(inconsistencies)
```

#### 4.2 Handling Action Results
```python
# In CombatSystem
def _handle_action_completed(self, event: CombatEvent) -> None:
    """
    Update everything when an action finishes.
    
    Like when a point is scored:
    1. Make sure it was a valid point
    2. Update the scoreboard
    3. Reset players for next point
    """
    # 1. Make sure this is a valid result
    if not self._validate_event_data(event):
        self._handle_invalid_event(event)
        return
        
    # 2. Update everything at once
    with self._state_manager.transaction() as state_tx:
        # Mark the action as finished
        state_tx.update_action_state(event.action_id, ActionStateType.RECOVERY)
        
        # Update both fighters' states
        for combatant_id, state_changes in event.state_changes.items():
            state_tx.update_combatant_state(combatant_id, state_changes)
```

## Testing Your Changes

Think of testing like being a quality control inspector in a factory. You need to check:
1. Individual parts work (Unit Tests)
2. Parts work together (Integration Tests)
3. Everything runs smoothly (Performance Tests)

### 1. Testing Individual Parts (Unit Tests)
Like checking each LEGO piece before building:

```python
def test_action_state_transitions():
    """
    Check if actions follow the rules.
    
    Like making sure:
    - You can't attack while blocking
    - You must recover after attacking
    - You can't move while attacking
    """
    action_system = ActionSystem()
    
    # Try a normal attack sequence
    print("Testing normal attack...")
    action = create_test_action("attack")
    if action_system.validate_action_chain(action):
        print("✓ Can start an attack from neutral")
    
    # Try an illegal move
    print("Testing illegal action...")
    invalid_action = create_test_action("attack", state=ActionStateType.RECOVERY)
    if not action_system.validate_action_chain(invalid_action):
        print("✓ Can't attack during recovery")
```

### 2. Testing Parts Together (Integration Tests)
Like a practice match to make sure everything works:

```python
def test_complete_combat_sequence():
    """
    Test a complete fight sequence.
    
    Like checking:
    - Fighter A can attack
    - Fighter B can block
    - Damage is calculated correctly
    - States update properly
    """
    print("Setting up test fight...")
    combat_system = CombatSystem(
        duration=10000,  # 10 second fight
        distance=50      # Start at medium range
    )
    
    # Create test fighters
    attacker = create_test_combatant(
        "Fighter A",
        stamina=100,
        health=100
    )
    defender = create_test_combatant(
        "Fighter B",
        stamina=100,
        health=100
    )
    
    print("Running attack sequence...")
    execute_attack_sequence(combat_system, attacker, defender)
    
    # Check results
    print("Verifying results...")
    if assert_combat_state_valid(combat_system):
        print("✓ Combat state is valid")
    if assert_event_chain_complete(combat_system):
        print("✓ All events processed correctly")
```

### 3. Testing Performance (Speed Tests)
Like stress testing a car engine:

```python
def test_system_performance():
    """
    Make sure the system runs fast enough.
    
    Like checking:
    - Game runs at 60 FPS
    - No memory leaks
    - Handles many actions smoothly
    """
    print("Running performance test...")
    with PerformanceStats() as stats:
        # Run lots of fights
        for i in range(100):
            print(f"Test fight {i+1}/100...")
            execute_combat_sequence()
            
        # Check if it's fast enough
        print("\nChecking results:")
        if stats.average_execution_time < 16.0:
            print("✓ Runs at 60+ FPS")
        if stats.max_memory_usage < 1024 * 1024:
            print("✓ Memory usage OK")
```

## Finding and Fixing Problems

When something goes wrong, you need tools to figure out what happened. Here are your detective tools:

### 1. Checking the Current State
Like taking a snapshot of the game to see what's wrong:

```python
def debug_system_state(combat_system):
    """
    Print out everything about the current game state.
    
    Like checking:
    - Where are the fighters?
    - How much health/stamina left?
    - What are they doing right now?
    """
    print("\n=== Combat System State ===")
    print(f"Fight Timer: {combat_system.timer}ms")
    print(f"Fighter Distance: {combat_system.distance} units")
    
    # Check each fighter
    for combatant in combat_system._combatants:
        state = combat_system._state_manager.get_state(combatant.id)
        print(f"\nFighter: {combatant.id}")
        print(f"├── Health: {state.stats.get('health', 'N/A')}")
        print(f"├── Stamina: {state.stamina}")
        print(f"├── Position: {state.position_x}, {state.position_y}")
        print(f"└── Current Action: {combat_system._action_system.get_current_action(combatant.id)}")
```

### 2. Watching Events Happen
Like having a slow-motion replay of the fight:

```python
def enable_event_tracing(combat_system):
    """
    Watch every event as it happens.
    
    Like a play-by-play announcer:
    - What just happened?
    - Who did it?
    - What were the results?
    """
    def trace_handler(event):
        print("\n🎯 New Event:")
        print(f"├── Type: {event.event_type}")
        print(f"├── From: {event.source_id}")
        print(f"├── To: {event.target_id if event.target_id else 'N/A'}")
        print(f"└── Details: {event.data}")
            
    combat_system._event_dispatcher.subscribe("*", trace_handler)
    print("Event tracing enabled - watching all actions!")
```

### 3. Checking Performance
Like using diagnostic tools on a car:

```python
def monitor_performance():
    """
    Check if the system is running well.
    
    Like checking:
    - Is it running smoothly?
    - Is it using too much memory?
    - Are there any bottlenecks?
    """
    print("\n🔍 Starting Performance Check...")
    with PerformanceStats() as stats:
        # Run your code here
        print("\nResults:")
        print(f"├── Time per frame: {stats.execution_time}ms")
        print(f"├── Memory used: {stats.memory_usage}MB")
        print(f"├── Events processed: {stats.event_count}")
        print(f"└── Status: {'✓ Good' if stats.execution_time < 16.0 else '⚠ Too Slow'}")
```

## Detailed Implementation Plan

### Phase 1: Core Fixes

#### 1. State Management Fixes
Location: `combat/combat_system.py`

a) Add Transaction Support
```python
# Add to CombatSystem class
def _start_transaction(self):
    """Start a new atomic transaction."""
    return self._state_manager.transaction()

def _update_states_atomically(self, updates):
    """Apply multiple state updates as one atomic operation."""
    with self._start_transaction() as tx:
        for entity_id, new_state in updates.items():
            tx.update_state(entity_id, new_state)
```

b) Fix State Validation
```python
# Add to CombatSystem class
def _validate_state_update(self, old_state, new_state):
    """
    Validate state changes before applying them.
    Returns: (bool, str) - (is_valid, error_message)
    """
    if new_state.stamina < 0:
        return False, "Stamina cannot be negative"
    if new_state.stats.get('health', 0) < 0:
        return False, "Health cannot be negative"
    # Add more validation as needed
    return True, ""
```

#### 2. Action System Improvements
Location: `combat/lib/action_system.py`

a) Add Action State Machine
```python
class ActionStateMachine:
    """Manages action state transitions."""
    
    def __init__(self):
        self.valid_transitions = {
            ActionStateType.FEINT: {
                ActionStateType.COMMIT: ["has_stamina", "not_interrupted"],
                ActionStateType.RECOVERY: ["any"]  # Can always cancel
            },
            ActionStateType.COMMIT: {
                ActionStateType.RELEASE: ["has_stamina", "not_interrupted"],
                ActionStateType.RECOVERY: ["is_cancellable"]
            },
            ActionStateType.RELEASE: {
                ActionStateType.RECOVERY: ["any"]  # Must recover after release
            }
        }
    
    def can_transition(self, from_state, to_state, conditions):
        """Check if state transition is allowed."""
        if from_state not in self.valid_transitions:
            return False
        if to_state not in self.valid_transitions[from_state]:
            return False
        required_conditions = self.valid_transitions[from_state][to_state]
        return all(conditions.get(cond, False) for cond in required_conditions)
```

b) Implement Action Validation
```python
# Add to ActionSystem class
def validate_action(self, action, combatant_state):
    """
    Comprehensive action validation.
    Returns: (bool, str) - (is_valid, error_message)
    """
    # Check stamina cost
    stamina_cost = ACTIONS[action.action_type].get('stamina_cost', 0)
    if combatant_state.stamina < stamina_cost:
        return False, "Insufficient stamina"
        
    # Check action prerequisites
    if not self._check_action_prerequisites(action, combatant_state):
        return False, "Prerequisites not met"
        
    # Validate state transition
    if not self.state_machine.can_transition(
        action.current_state,
        action.next_state,
        self._get_transition_conditions(combatant_state)
    ):
        return False, "Invalid state transition"
        
    return True, ""
```

#### 3. Event System Reliability
Location: `combat/lib/event_system.py`

a) Add Event Queue
```python
class EventQueue:
    """Reliable event queue with guaranteed delivery."""
    
    def __init__(self):
        self.pending_events = []
        self.processed_events = []
        self.event_lock = threading.Lock()
    
    def enqueue(self, event):
        """Add event to queue with retry logic."""
        with self.event_lock:
            self.pending_events.append(event)
            self._try_process_events()
    
    def _try_process_events(self):
        """Process events with retry on failure."""
        for event in self.pending_events[:]:
            try:
                self._process_event(event)
                self.pending_events.remove(event)
                self.processed_events.append(event)
            except Exception as e:
                logger.error(f"Event processing failed: {e}")
                # Will retry on next attempt
```

b) Implement Event Ordering
```python
# Add to EventSystem class
def _order_events(self, events):
    """
    Order events by priority and dependencies.
    Returns: List of ordered events
    """
    # Sort by timestamp first
    events.sort(key=lambda e: e.timestamp)
    
    # Group by priority
    priority_groups = {
        EventPriority.HIGH: [],
        EventPriority.MEDIUM: [],
        EventPriority.LOW: []
    }
    
    for event in events:
        priority_groups[event.priority].append(event)
    
    # Maintain order within priority groups
    ordered_events = []
    for priority in [EventPriority.HIGH, EventPriority.MEDIUM, EventPriority.LOW]:
        ordered_events.extend(priority_groups[priority])
    
    return ordered_events
```

### Phase 2: Integration

#### 1. Adapter Implementation
Location: `combat/adapters/`

a) Complete State Manager Adapter
```python
# In state_manager_adapter.py
class StateManagerAdapter(IStateManager):
    def __init__(self):
        self.states = {}
        self.history = defaultdict(list)
        self.lock = threading.Lock()
    
    def get_state(self, entity_id):
        with self.lock:
            return self.states.get(entity_id)
    
    def update_state(self, entity_id, new_state):
        with self.lock:
            old_state = self.states.get(entity_id)
            self.history[entity_id].append(old_state)
            self.states[entity_id] = new_state
    
    def rollback(self, entity_id, steps=1):
        """Rollback state changes."""
        with self.lock:
            if len(self.history[entity_id]) >= steps:
                for _ in range(steps):
                    self.states[entity_id] = self.history[entity_id].pop()
```

b) Enhance Event Dispatcher Adapter
```python
# In event_dispatcher_adapter.py
class EventDispatcherAdapter(IEventDispatcher):
    def __init__(self):
        self.subscribers = defaultdict(list)
        self.event_queue = EventQueue()
        self.retry_policy = RetryPolicy(max_attempts=3)
    
    def dispatch(self, event):
        """Dispatch event with retry logic."""
        def dispatch_with_retry():
            for attempt in range(self.retry_policy.max_attempts):
                try:
                    self._do_dispatch(event)
                    return True
                except Exception as e:
                    if attempt == self.retry_policy.max_attempts - 1:
                        raise
                    time.sleep(self.retry_policy.delay)
            return False
            
        self.event_queue.enqueue(dispatch_with_retry)
```

#### 2. Error Handling
Location: Various files

a) Add Error Types
```python
# In combat/lib/errors.py
class CombatError(Exception):
    """Base class for combat system errors."""
    pass

class StateError(CombatError):
    """State-related errors."""
    pass

class ActionError(CombatError):
    """Action-related errors."""
    pass

class EventError(CombatError):
    """Event-related errors."""
    pass
```

b) Implement Error Handlers
```python
# Add to CombatSystem class
def _handle_error(self, error, context=None):
    """
    Handle system errors gracefully.
    Logs error, attempts recovery if possible.
    """
    logger.error(f"Combat system error: {error}")
    
    if isinstance(error, StateError):
        self._handle_state_error(error, context)
    elif isinstance(error, ActionError):
        self._handle_action_error(error, context)
    elif isinstance(error, EventError):
        self._handle_event_error(error, context)
    else:
        raise error  # Unhandled error type
```

### Phase 3: Testing

#### 1. Core Test Suite
Location: `tests/combat/`

a) Add State Tests
```python
# In test_combat_system.py
def test_state_transitions():
    """Test all possible state transitions."""
    combat_system = CombatSystem(duration=1000, distance=10)
    
    # Test each state transition
    transitions = [
        (ActionStateType.FEINT, ActionStateType.COMMIT),
        (ActionStateType.COMMIT, ActionStateType.RELEASE),
        (ActionStateType.RELEASE, ActionStateType.RECOVERY)
    ]
    
    for from_state, to_state in transitions:
        # Setup test state
        action = create_test_action("attack", from_state)
        
        # Attempt transition
        result = combat_system._action_system.validate_action_chain(action)
        
        # Verify result
        assert result, f"Failed to transition from {from_state} to {to_state}"
```

b) Add Integration Tests
```python
# In test_core_integration.py
def test_complete_combat_sequence():
    """Test a complete combat sequence."""
    combat_system = CombatSystem(duration=5000, distance=20)
    
    # Create combatants
    attacker = create_test_combatant("attacker", stamina=100)
    defender = create_test_combatant("defender", stamina=100)
    
    # Add combatants
    combat_system.add_combatant(attacker)
    combat_system.add_combatant(defender)
    
    # Execute attack sequence
    actions = [
        ("move_forward", attacker.id),
        ("quick_attack", attacker.id, defender.id),
        ("block", defender.id)
    ]
    
    # Execute and verify each action
    for action_type, *args in actions:
        action = create_action(action_type, *args)
        combat_system.execute_action(action)
        
        # Verify system state after each action
        assert_system_state_valid(combat_system)
```

#### 2. Performance Tests
Location: `tests/combat/test_system_health.py`

```python
def test_system_performance():
    """Test system performance under load."""
    combat_system = CombatSystem(duration=60000, distance=30)
    
    # Setup performance monitoring
    with PerformanceStats() as stats:
        # Run stress test
        for _ in range(1000):
            # Execute random combat sequence
            execute_random_combat_sequence(combat_system)
            
        # Verify performance metrics
        assert stats.average_frame_time < 16.0, "Frame time too high"
        assert stats.peak_memory < 100_000_000, "Memory usage too high"
        assert stats.event_latency < 5.0, "Event latency too high"
```

### Phase 4: Optimization

#### 1. Performance Optimization
Location: Various files

a) State Updates
```python
# In state_manager_adapter.py
class StateManagerAdapter(IStateManager):
    def __init__(self):
        self.states = {}
        self._cache = LRUCache(maxsize=1000)
    
    def get_state(self, entity_id):
        # Check cache first
        if entity_id in self._cache:
            return self._cache[entity_id]
            
        # Fall back to main storage
        state = self.states.get(entity_id)
        if state:
            self._cache[entity_id] = state
        return state
```

b) Event Processing
```python
# In event_system.py
class EventSystem:
    def __init__(self):
        self.event_pools = {
            EventType.COMBAT: ObjectPool(maxsize=1000),
            EventType.MOVEMENT: ObjectPool(maxsize=1000),
            EventType.STATE: ObjectPool(maxsize=1000)
        }
    
    def create_event(self, event_type, **kwargs):
        """Create event from pool for better performance."""
        event = self.event_pools[event_type].acquire()
        event.reset(**kwargs)
        return event
    
    def release_event(self, event):
        """Return event to pool."""
        self.event_pools[event.type].release(event)
```

#### 2. Memory Optimization
Location: Various files

a) Object Pooling
```python
# In combat/lib/pooling.py
class ObjectPool:
    """Generic object pool for reusing objects."""
    
    def __init__(self, factory, maxsize=1000):
        self.factory = factory
        self.maxsize = maxsize
        self.pool = Queue(maxsize=maxsize)
        
    def acquire(self):
        """Get an object from the pool or create new."""
        try:
            return self.pool.get_nowait()
        except Empty:
            return self.factory()
            
    def release(self, obj):
        """Return object to pool if not full."""
        try:
            self.pool.put_nowait(obj)
        except Full:
            pass  # Pool is full, let object be garbage collected
```

b) Memory Management
```python
# Add to CombatSystem class
def _cleanup_resources(self):
    """
    Clean up unused resources periodically.
    Call this after major operations or time intervals.
    """
    # Clear old state history
    self._state_manager.trim_history(max_age=60)  # Keep last 60 seconds
    
    # Release unused event objects
    self._event_system.cleanup_pools()
    
    # Clear action cache
    self._action_system.clear_old_actions(max_age=30)
```

Follow this implementation plan in order, making sure to:
1. Test each change thoroughly before moving to the next
2. Keep the documentation updated
3. Monitor system performance throughout
4. Handle errors appropriately at each step

## Best Practices

1. **State Management**
   - Always use transactions for state updates
   - Validate state transitions
   - Maintain state consistency across systems

2. **Event Handling**
   - Implement proper error handling
   - Use event chains for complex sequences
   - Monitor event propagation

3. **Testing**
   - Write tests before implementing features
   - Include edge cases
   - Monitor performance metrics

4. **Code Organization**
   - Follow existing patterns
   - Document complex logic
   - Use type hints and interfaces

## Next Steps

1. Review and understand the current codebase
2. Set up your development environment
3. Start with Phase 1 fixes
4. Run tests frequently
5. Document all changes
6. Monitor performance impacts
