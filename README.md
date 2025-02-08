# AIRPG - AI-Driven Real-Time Tactical Combat System

## Overview
AIRPG is a Python-based real-time tactical combat system featuring dynamic character interactions and AI-driven decision making. The system emphasizes modular design, type safety, and clean architecture principles.

## Features
- Real-time combat system
- Dynamic character interactions
- Status effect system
- Modular action system
- Event-driven architecture
- Comprehensive test coverage

## Requirements
- Python 3.10 or higher
- Dependencies listed in `requirements.txt`

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/airpg.git
cd airpg
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
.\venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Project Structure
```
airpg/
├── src/
│   ├── combat/            # Combat system
│   ├── characters/        # Character system
│   └── common/           # Shared utilities
├── tests/                # Test suite
└── docs/                # Documentation
```

## Development

### Running Tests
```bash
pytest
```

### Code Quality
```bash
# Format code
black src tests

# Sort imports
isort src tests

# Type checking
mypy src
```

## Contributing
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Testing
The project uses pytest for testing. To run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/combat/test_engine.py
```

## Code Style
This project follows:
- Black code formatting
- Type hints (enforced by MyPy)
- PEP 8 guidelines

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Contact
Your Name - suimyst@gmail.com
Project Link: [https://github.com/mystsui/airpg](https://github.com/mystsui/airpg)