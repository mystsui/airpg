# Changelog
All notable changes to the combat system will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Base Time Unit (BTU) System:
  * Core timing utilities and conversions
  * Speed modification system
  * Time modifier framework
  * Action timing management
  * Comprehensive timing tests
    - BTU conversion accuracy
    - Speed modifier stacking
    - Time modifier persistence
    - Performance benchmarks
- Enhanced Actions Library:
  * Converted all timings to BTUs
  * Added speed modifiers
  * Action categorization
  * Action chaining system
  * Detailed action tests
    - Attack mechanics
    - Defense mechanics
    - Movement mechanics
    - Chain validation
- Enhanced Event System:
  * Event categorization (Combat, Movement, State, etc.)
  * Event importance levels
  * Event streaming with filtering
  * Event compression for storage
  * Multiple stream support (Combat, Animation, AI Training)
  * Event system tests
    - Event compression
    - Stream filtering
    - Event routing
    - Handler management
    - Performance metrics
- Enhanced Action System:
  * Action state machine (Feint/Commit/Release/Recovery)
  * Action visibility system
  * Commitment mechanics
  * Cancellation costs
  * Cooldown management
  * Stat requirements
  * Action system tests
    - State transitions
    - Visibility calculations
    - Commitment validation
    - Chain verification
- Awareness System:
  * Awareness zones (Clear/Fuzzy/Hidden/Peripheral)
  * Dynamic perception checks
  * Environmental conditions
  * Stealth mechanics
  * Position tracking
  * Confidence calculations
  * Awareness tests
    - Zone transitions
    - Perception modifiers
    - Environmental effects
    - Movement detection
- Test Infrastructure:
  * Comprehensive test fixtures
  * Mock implementations
  * Performance monitoring
  * Test data generators
  * Integration test suites
    - Combat flow tests
    - State transition tests
    - Event propagation tests
    - Performance benchmarks
- Integration Tests:
  * Core System Integration:
    - Complete combat flow testing
    - State transition verification
    - Event propagation validation
    - Cross-system interaction tests
  * Adapter Integration:
    - CombatantAdapter integration
    - ActionResolverAdapter integration
    - StateManagerAdapter integration
    - EventDispatcherAdapter integration
  * System Health:
    - Memory usage monitoring
    - Performance profiling
    - Edge case handling
    - Error recovery testing

- New interfaces directory structure
- Core interface definitions:
  * ICombatant: Base interface for combatant entities
  * IActionResolver: Interface for action resolution
  * IStateManager: Interface for state management
  * IEventDispatcher: Interface for event handling
- Core data structures:
  * CombatantState: Immutable state representation
  * Action: Action definition structure
  * ActionResult: Action resolution result
  * CombatEvent: Combat event structure
- Adapter implementations:
  * CombatantAdapter: Adapts existing Combatant class
    - Full ICombatant interface implementation
    - Backward compatibility layer
  * ActionResolverAdapter: Adapts action resolution logic
    - Implements IActionResolver interface
    - Maintains existing resolution rules
    - Supports all action types
  * StateManagerAdapter: Manages combat state
    - Implements IStateManager interface
    - State transition validation
    - State history tracking
    - Rollback capability
  * EventDispatcherAdapter: Handles system events
    - Implements IEventDispatcher interface
    - Thread-safe event dispatching
    - Event history tracking
    - Flexible subscription model
    - Batch event processing
- Comprehensive test suites:
  * CombatantAdapter tests
  * ActionResolverAdapter tests
    - Action validation
    - Action resolution
    - State changes
    - Combat outcomes
  * StateManagerAdapter tests
    - State transitions
    - Validation rules
    - History management
    - Rollback functionality
  * EventDispatcherAdapter tests
    - Event dispatching
    - Subscription management
    - Thread safety
    - Exception handling
    - Batch operations

### Changed
- Refactoring components to use interfaces
- Implementing dependency injection system
- Enhanced type safety with Protocol classes
- Improved state management with immutable structures
- Integrated interface-based architecture with CombatSystem:
  * Adapter initialization and dependency injection
  * Event-driven state management
  * Backward compatibility layer
  * Thread-safe event handling
- Action System Improvements:
  * Millisecond to BTU conversion
  * Speed-based timing calculations
  * Action chain validation
  * Enhanced action properties
- Event System Improvements:
  * Efficient event storage
  * Automatic compression
  * Stream-based filtering
  * Time-range queries
- Action System Improvements:
  * State-based action resolution
  * Stealth-perception calculations
  * Action phase management
  * Stamina cost system
- Awareness System Improvements:
  * Distance-based difficulty scaling
  * Angle-based perception modifiers
  * Environmental condition effects
  * Movement detection
- Adapter Integration:
  * CombatantAdapter:
    - Support for enhanced action states
    - Awareness state management
    - Position tracking
    - Movement calculations
  * ActionResolverAdapter:
    - Action phase resolution
    - Visibility-based modifiers
    - Commitment handling
    - Enhanced combat mechanics
  * StateManagerAdapter:
    - Action state transitions
    - Commitment validation
    - Enhanced state tracking
    - Position state management
  * EventDispatcherAdapter:
    - Event categorization
    - Importance-based filtering
    - Stream management
    - Event compression

### Deprecated
- Direct component coupling
- Static action resolution
- Direct state mutation

### Removed
- None (maintaining compatibility)

### Fixed
- Component coupling issues through interfaces
- State management inconsistencies with immutable states
- Type safety improvements with Protocol classes
