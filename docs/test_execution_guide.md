# Test Execution Guide

## Overview

This guide provides detailed instructions for running tests, analyzing results, and debugging issues in the combat system. It's designed to be used alongside the developer guide.

## Test Organization

### 1. Unit Tests
Located in `tests/combat/` with prefix `test_`:

- Core Systems:
  * `test_timing.py` - BTU system tests
  * `test_event_system.py` - Event system tests
  * `test_action_system.py` - Action system tests
  * `test_awareness_system.py` - Awareness system tests
  * `test_actions_library.py` - Actions library tests

- Action Types:
  * `test_attack_actions.py` - Attack action tests
  * `test_defense_actions.py` - Defense action tests
  * `test_movement_actions.py` - Movement action tests
  * `test_neutral_actions.py` - Utility action tests

### 2. Integration Tests
- `test_core_integration.py` - Core systems integration
- `test_adapter_integration.py` - Adapter integration
- `test_system_health.py` - System health and performance

### 3. Adapter Tests
- `test_combatant_adapter.py`
- `test_action_resolver_adapter.py`
- `test_state_manager_adapter.py`
- `test_event_dispatcher_adapter.py`

## Running Tests

### 1. Running All Tests
```bash
# From project root
pytest tests/combat/

# With coverage
pytest --cov=combat tests/combat/
```

### 2. Running Specific Test Categories
```bash
# Core systems
pytest tests/combat/test_timing.py tests/combat/test_event_system.py tests/combat/test_action_system.py tests/combat/test_awareness_system.py

# Integration tests
pytest tests/combat/test_core_integration.py tests/combat/test_adapter_integration.py tests/combat/test_system_health.py

# Adapter tests
pytest tests/combat/test_*_adapter.py
```

### 3. Running Individual Test Cases
```bash
# Run specific test class
pytest tests/combat/test_action_system.py::TestActionStateTransitions

# Run specific test method
pytest tests/combat/test_action_system.py::TestActionStateTransitions::test_state_transitions
```

### 4. Running Performance Tests
```bash
# Run all performance tests
pytest tests/combat/test_system_health.py::TestTimingPerformance

# Run with detailed output
pytest -v tests/combat/test_system_health.py::TestTimingPerformance
```

## Test Configuration

### 1. Test Fixtures (`conftest.py`)
Common test fixtures and utilities:
- `performance_stats` - Performance tracking
- `test_sequence` - Combat sequence generation
- `mock_event_handler` - Event handling mocks
- `mock_state_observer` - State observation mocks
- `test_environment` - Environment condition setup

### 2. Mock Objects (`mocks.py`)
Available mock implementations:
- `MockEventDispatcher` - Event system mocking
- `MockActionResolver` - Action resolution mocking
- `MockStateManager` - State management mocking
- `MockAwarenessSystem` - Awareness system mocking
- `MockCombatSystem` - Full system mocking

## Analyzing Results

### 1. Test Output Analysis
```bash
# Run tests with detailed output
pytest -v tests/combat/

# Run tests with failure details
pytest -v --tb=short tests/combat/

# Run tests with full traceback
pytest -v --tb=long tests/combat/
```

### 2. Coverage Analysis
```bash
# Generate coverage report
pytest --cov=combat --cov-report=term-missing tests/combat/

# Generate HTML coverage report
pytest --cov=combat --cov-report=html tests/combat/
```

### 3. Performance Analysis
```python
# Example performance test analysis
def analyze_performance_results(performance_stats):
    print("Performance Results:")
    print(f"Average action update time: {performance_stats.get_average('action_update')}ms")
    print(f"Maximum action update time: {performance_stats.get_max('action_update')}ms")
    print(f"Minimum action update time: {performance_stats.get_min('action_update')}ms")
```

## Debugging Tests

### 1. Using PDB
```bash
# Run tests with debugger
pytest --pdb tests/combat/

# Set breakpoint in test
import pdb; pdb.set_trace()
```

### 2. Verbose Output
```bash
# Run with maximum verbosity
pytest -vv tests/combat/

# Show local variables in tracebacks
pytest --showlocals tests/combat/
```

### 3. Common Debug Patterns

#### Event Flow Debugging
```python
def test_event_flow(combat_system, mock_event_handler):
    # Set up event tracking
    combat_system._event_dispatcher.subscribe("*", mock_event_handler.handle_event)
    
    # Execute test sequence
    execute_test_sequence(combat_system)
    
    # Analyze events
    events = mock_event_handler.get_events()
    for event in events:
        print(f"Event: {event.event_type}")
        print(f"Data: {event.data}")
        print(f"Time: {event.timestamp}")
```

#### State Transition Debugging
```python
def test_state_transitions(combat_system, mock_state_observer):
    # Set up state tracking
    combat_system._state_manager.add_observer(mock_state_observer)
    
    # Execute test sequence
    execute_test_sequence(combat_system)
    
    # Analyze state changes
    states = mock_state_observer.get_states()
    for state in states:
        print(f"State: {state.state}")
        print(f"Phase: {state.phase}")
        print(f"Time: {state.total_time}")
```

## Performance Benchmarks

### 1. Expected Performance
- Action resolution: < 0.1ms per action
- State updates: < 0.05ms per update
- Event dispatch: < 0.01ms per event
- Memory usage: < 10MB for 1000 actions

### 2. Performance Test Cases
```python
def test_action_performance(combat_system, performance_stats):
    # Measure action creation and execution
    start_time = datetime.now()
    for _ in range(1000):
        action = create_action("quick_attack", "fighter_1", "fighter_2")
        combat_system.execute_action(action)
    execution_time = (datetime.now() - start_time).total_seconds()
    
    # Record metrics
    performance_stats.record_operation("action_execution", execution_time)
    assert execution_time < 1.0  # Should handle 1000 actions in under 1 second
```

## Troubleshooting Common Issues

### 1. Test Failures
- Check test fixtures and mock objects
- Verify system state before test
- Check for timing-sensitive tests
- Validate test data

### 2. Performance Issues
- Profile slow tests
- Check memory usage
- Verify test isolation
- Check for resource leaks

### 3. Integration Issues
- Verify adapter configurations
- Check interface implementations
- Validate event flow
- Check state management

## Best Practices

1. Always run the full test suite before committing
2. Write tests for new features before implementation
3. Keep tests focused and independent
4. Use appropriate fixtures and mocks
5. Monitor and maintain performance benchmarks
6. Document test requirements and assumptions
7. Regular test maintenance and cleanup
8. Keep test code as clean as production code
