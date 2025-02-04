# Combat System

A sophisticated turn-based combat engine designed for role-playing games, featuring strategic depth and tactical complexity.

## Quick Start

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Make the development helper script executable:
```bash
chmod +x dev.py
```
4. Run development tasks:
```bash
# Run all tests
./dev.py test

# Run tests with coverage
./dev.py test -c

# Run performance tests
./dev.py test --performance

# Format code
./dev.py format

# Run linting
./dev.py lint

# Run all checks (format, lint, test)
./dev.py check
```

## Documentation

### Core Documentation
- [Developer Guide](docs/developer_guide.md) - Comprehensive guide to the combat system
- [Test Execution Guide](docs/test_execution_guide.md) - Detailed testing instructions
- [Game Document](docs/game_document.md) - Core game mechanics and concepts

### Analysis Documents
- [Analysis Index](docs/analysis/00_analysis_index.md) - Overview of all analysis documents
- [Structural Analysis](docs/analysis/01_structural_analysis.md) - System architecture
- [Performance Evaluation](docs/analysis/02_performance_evaluation.md) - Performance analysis
- [Design Patterns](docs/analysis/03_design_patterns.md) - Pattern usage and recommendations
- [Modularity & Testability](docs/analysis/04_modularity_testability.md) - Code quality analysis
- [Game Mechanics](docs/analysis/05_game_mechanics.md) - Gameplay systems analysis

### Implementation
- [Implementation Schedule](docs/analysis/implementation_schedule.md) - Development roadmap
- [Integration Test Plan](docs/analysis/integration_test_plan.md) - Testing strategy
- [Requirements Analysis](docs/analysis/requirements_analysis.md) - System requirements
- [Optimization Targets](docs/analysis/optimization_targets.md) - Performance goals

## Project Structure

```
combat/
├── __init__.py
├── combat_system.py     # Main system implementation
├── combatant.py        # Base combatant class
├── adapters/           # Interface adapters
│   ├── __init__.py
│   ├── combatant_adapter.py
│   ├── action_resolver_adapter.py
│   ├── state_manager_adapter.py
│   └── event_dispatcher_adapter.py
├── interfaces/         # Core interfaces
│   └── __init__.py
└── lib/               # Core systems
    ├── timing.py      # BTU system
    ├── event_system.py
    ├── action_system.py
    ├── awareness_system.py
    └── actions_library.py

tests/
└── combat/            # Test suites
    ├── conftest.py    # Test fixtures
    ├── mocks.py       # Mock implementations
    ├── test_core_integration.py
    ├── test_adapter_integration.py
    ├── test_system_health.py
    └── ... (other test files)

docs/
├── developer_guide.md
├── test_execution_guide.md
├── game_document.md
└── analysis/          # Analysis documents
    ├── 00_analysis_index.md
    └── ... (analysis files)
```

## Core Systems

1. **BTU (Base Time Unit) System**
   - Fundamental timing system
   - Speed and time modifications
   - Action timing management

2. **Event System**
   - Event-driven architecture
   - Event categorization
   - Event streaming and filtering

3. **Action System**
   - State machine implementation
   - Action visibility and commitment
   - Action phase management

4. **Awareness System**
   - Perception mechanics
   - Environmental effects
   - Position tracking

## Development Workflow

1. Read the [Developer Guide](docs/developer_guide.md)
2. Set up your development environment
3. Run the test suite
4. Make changes following the guidelines
5. Update documentation
6. Submit changes

## Testing

See the [Test Execution Guide](docs/test_execution_guide.md) for detailed testing instructions.

Quick test commands:
```bash
# Run all tests
pytest tests/combat/

# Run with coverage
pytest --cov=combat tests/combat/

# Run specific test category
pytest tests/combat/test_core_integration.py
```

## Contributing

1. Follow the coding standards
2. Write tests for new features
3. Update documentation
4. Maintain backward compatibility
5. Consider performance implications

## Current Status

- Phase 1-3 (Core Systems, Integration Layer, Integration Tests) completed
- Phase 4 (Combat AI System) in progress
- See [Implementation Schedule](docs/analysis/implementation_schedule.md) for details

## License

This project is licensed under the MIT License - see the LICENSE file for details.
