# ClynBoozle Quiz Game

A professional multimedia quiz game application built with Python and Tkinter. Features a modern modular architecture with comprehensive testing and media management capabilities.

## Features

- **Multi-team gameplay** (2-6 teams) with real-time scoring
- **Multimedia support** for image and audio questions
- **Responsive grid-based game board** with dynamic sizing
- **Professional media management** with automatic resizing and caching
- **Question set management** with validation and error handling
- **Comprehensive logging** and error recovery
- **Modern modular architecture** with proper separation of concerns

## Requirements

- Python 3.9 or higher
- PIL/Pillow for image processing
- pygame for audio playback
- tkinter (usually included with Python)

## Installation

### Quick Start
```bash
# Clone the repository
git clone <repository-url>
cd bamboozle-repos

# Set up virtual environment
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# venv\Scripts\activate   # On Windows

# Install dependencies
pip install -r requirements.txt
```

### Using Make (Recommended)
```bash
make setup  # Sets up everything automatically
```

## Usage

### Running the Application
```bash
# Using the launcher script
python run_clynboozle.py

# Or with make
make run

# Development mode with debug logging
make dev
```

### Development Workflow

```bash
# Code quality checks
make format     # Format code with black
make lint       # Check with flake8
make quality    # Run all quality checks

# Testing
make test           # Run all tests
make test-models    # Run model tests only
make test-cov       # Run tests with coverage

# Development setup
make setup      # Complete environment setup
make clean      # Clean temporary files
```

## Architecture

ClynBoozle follows a modern, professional architecture:

- **`src/clynboozle/`** - Main application package
- **`src/clynboozle/models/`** - Business logic models (Question, Team, GameState)
- **`src/clynboozle/services/`** - Business logic services (Game, Media, File operations)
- **`src/clynboozle/ui/`** - User interface components with base classes
- **`src/clynboozle/config/`** - Configuration and settings
- **`src/clynboozle/utils/`** - Utilities and custom exceptions
- **`tests/`** - Comprehensive test suite with pytest

## Testing

The application includes a comprehensive test suite:

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src/clynboozle --cov-report=html

# Run specific test categories
pytest tests/test_models.py      # Model tests
pytest tests/test_services.py    # Service tests
pytest tests/test_integration.py # Integration tests
```

## Building for Distribution

```bash
# Build distributable application
make build

# Or directly with PyInstaller
pyinstaller ClynBoozle.spec
```

The built application will be in `dist/ClynBoozle.app` (macOS) or `dist/ClynBoozle/` (other platforms).

## Development Standards

This project follows professional development standards:

- **Code Quality**: Black formatting, flake8 linting, comprehensive type hints
- **Testing**: 32+ unit tests with pytest, integration tests, >90% coverage
- **Architecture**: SOLID principles, clean separation of concerns
- **Documentation**: Comprehensive docstrings and inline documentation
- **Error Handling**: Graceful degradation with user-friendly error messages

## Game Features

### Question Sets
- Create custom question sets with JSON format
- Import/export question sets with validation
- Support for multimedia questions

### Media Management
- WordPress-style media library with automatic processing
- Support for images (PNG, JPG, GIF, WebP) and audio (WAV, MP3, OGG, FLAC)
- Automatic thumbnail and tile generation
- Intelligent caching and memory management

### Gameplay
- Support for 2-6 teams with validation
- Point-based scoring system with turn management
- Professional game flow with state management
- Audio playback with seeking controls
- Image viewing with zoom and responsive display

## Configuration

Centralized configuration system in `src/clynboozle/config/`:

- **`settings.py`**: Technical settings (colors, fonts, paths, validation rules)
- **`messages.py`**: User-facing text and error messages

## Contributing

1. Ensure you have the development environment set up: `make setup`
2. Run quality checks before committing: `make quality`
3. Ensure all tests pass: `make test`
4. Follow the existing code style and architecture patterns

For detailed development guidance, see `CLAUDE.md` and `roadmap.md`.

## License

This project is licensed under the MIT License.

## Changelog

### Version 2.0.0 (Current)
- **Complete modular refactoring** with professional architecture
- **Comprehensive testing framework** with 32+ unit tests
- **Advanced media management** with WordPress-style system
- **Professional error handling** and logging
- **Type safety** with comprehensive type hints
- **Code quality tools** integration (black, flake8, mypy, pre-commit)
- **Modern packaging** and distribution setup
- **Clean separation of concerns** following SOLID principles

### Version 1.0.0
- Initial monolithic implementation
- Basic quiz functionality
- Multi-team support
