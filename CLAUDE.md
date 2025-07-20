# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ClynBoozle is a multimedia quiz game application built with Python and Tkinter. It supports creating custom question sets with images, audio, and multi-team gameplay. The project is version 2.0.0 and has been fully refactored with a modular architecture.

## Development Commands

### Environment Setup
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# venv\Scripts\activate   # On Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development tools
```

### Running the Application
```bash
# From root directory
python main.py

# Or using the package
python -m clynboozle
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/clynboozle --cov-report=html --cov-report=term-missing

# Run specific test markers
pytest -m "not slow"     # Skip slow tests
pytest -m integration    # Run integration tests only
pytest -m gui           # Run GUI tests only
```

### Code Quality
```bash
# Format code
black src/ tests/

# Type checking
mypy src/

# Linting
flake8 src/ tests/
```

### Building
```bash
# Build with PyInstaller (creates distributable app)
pyinstaller ClynBoozle.spec

# The built app will be in dist/ClynBoozle.app (macOS) or dist/ClynBoozle/ (other platforms)
```

## Architecture Overview

### Modular Structure
The codebase follows a clean, modular architecture with clear separation of concerns:

- **`src/clynboozle/`** - Main application package
- **`src/clynboozle/config/`** - Configuration constants and settings
- **`src/clynboozle/models/`** - Business logic models (Game state, Teams, Questions)
- **`src/clynboozle/services/`** - Business logic services (Game logic, Media handling, File operations)
- **`src/clynboozle/ui/`** - User interface components (Tkinter-based UI classes)
- **`src/clynboozle/utils/`** - Utility functions and custom exceptions

### Key Components

#### Configuration System
- **`config/settings.py`** - Centralized configuration with typed classes for Colors, Fonts, Window settings, Game rules, and Media processing
- Uses class-based configuration for better organization and type safety

#### Data Models
- **`models/game_state.py`** - Core game state management with validation
- **`models/team.py`** - Team data and scoring logic
- **`models/question.py`** - Question data structure with media support

#### Services Layer
- **`services/game_logic.py`** - Game flow control, scoring, and turn management
- **`services/media_service.py`** - Media file processing and management
- **`services/file_service.py`** - File I/O operations for question sets

#### UI Framework
- **`ui/base_frame.py`** - Base UI component with common functionality
- **`ui/game_board.py`** - Main game board with tile grid and scoring
- **`ui/main_menu.py`** - Application entry point and navigation
- Responsive design system with automatic scaling based on window size

### Media Management System
The application uses a WordPress-style media management system:
- **Media Database** - JSON-based database (`uploads/media_database.json`) tracks all media files
- **Multiple Image Sizes** - Automatic generation of thumbnails, tiles, and display sizes
- **Media References** - Questions reference media by ID rather than direct file paths
- **Supported Formats** - Images (PNG, JPG, GIF, WebP) and Audio (WAV, MP3, OGG, FLAC)

### Game Flow Architecture
1. **Question Set Management** - JSON-based question sets with media references
2. **Team Setup** - Dynamic team creation with validation (2-6 teams)
3. **Game Board** - Grid-based layout with automatic sizing based on question count
4. **Question Display** - Modal windows with image zoom, audio playback, and answer tracking
5. **Scoring System** - Real-time score tracking with turn-based gameplay

### Legacy Integration
- **`main.py`** - Legacy monolithic file that contains the complete original application
- **`question_set_manager.py`** - Legacy question set management (being replaced by modular services)
- **`media_manager.py`** - Legacy media handling (being replaced by media service)

The new modular architecture coexists with legacy code during the transition period.

## Development Notes

### Font and Scaling System
The application uses a sophisticated responsive design system:
- Base font sizes are defined in `config/settings.py`
- Dynamic scaling based on window size with minimum thresholds
- All UI components implement `resize()` methods for responsive behavior

### Media Processing Pipeline
- Images are automatically resized to multiple variants (tile, question, thumbnail)
- Audio files are processed and stored with metadata
- Media IDs provide stable references that persist across file system changes

### Error Handling
- Custom exception hierarchy in `utils/exceptions.py`
- Comprehensive validation in models and services
- Graceful degradation for missing media files

### Testing Strategy
- Pytest with coverage reporting
- Separate markers for slow, integration, and GUI tests
- Test fixtures for game state and media handling

## Project Status & Development Standards

### Current Project Status
**🎉 REFACTORING COMPLETE - PROFESSIONAL MODULAR ARCHITECTURE 🎉**

The project has completed a comprehensive refactoring from a monolithic application to a professional modular architecture:

- ✅ **Project Structure**: Proper package structure with `src/clynboozle/` organization
- ✅ **Business Logic Separation**: Models, services, and UI layers cleanly separated
- ✅ **Code Quality**: Type hints, logging, error handling, and testing framework
- ✅ **UI Architecture**: Modular UI components with proper navigation
- ✅ **Development Tools**: Makefile, pre-commit hooks, code quality tools
- ✅ **Testing Framework**: 32 passing unit tests with comprehensive coverage
- ✅ **Legacy Cleanup**: All monolithic files removed, clean architecture established

### Core Development Principles
- **KISS (Keep It Simple, Stupid)**: Simplify complex logic, reduce cognitive load
- **DRY (Don't Repeat Yourself)**: Eliminate code duplication, create reusable components
- **SOLID Principles**: Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion
- **Clean Code**: Readable, self-documenting code with clear naming conventions
- **Separation of Concerns**: Business logic separate from UI, clear module boundaries
- **Testability**: Code structure that enables unit testing
- **Type Safety**: Comprehensive type hints for better IDE support and error prevention

### Quality Standards
- **Maximum function length**: 20-30 lines
- **Maximum class length**: 200-300 lines
- **Clear, descriptive naming** (no abbreviations unless standard)
- **Comprehensive error handling** with user-friendly messages
- **Proper logging** for debugging and monitoring
- **Documentation** for all public interfaces

### Virtual Environment & Dependency Management
- **Always use virtual environment**: Create with `python3 -m venv venv` and activate with `source venv/bin/activate`
- **Install dependencies in order**: First upgrade pip, then install `requirements.txt`, then `requirements-dev.txt`
- **Test environment setup**: Verify all core modules import correctly before proceeding with development
- **Dependency verification**: Test that optional dependencies (PIL/Pillow, pygame) work gracefully when missing

### Code Quality Standards & Testing Protocol
- **Import testing**: After creating/refactoring modules, always test imports with simple Python commands
- **Functionality testing**: Create small test scripts to verify business logic works as expected
- **Code formatting**: Use `black` for consistent formatting across all Python files
- **Linting standards**: Use `flake8` with `--max-line-length=100 --ignore=F401,E501` for quality checks
- **Type checking**: Run `mypy` with `--ignore-missing-imports` to catch type issues (expect some PIL/pygame warnings in dev)

### Modern Development Commands
```bash
# Environment setup
make setup          # Complete development environment setup
source venv/bin/activate

# Running the application
make run            # Run the application
make dev            # Run with debug logging
python run_clynboozle.py

# Code quality (all integrated)
make quality        # Format + lint in one command
make format         # Black code formatting
make lint           # Flake8 linting
make type-check     # MyPy type checking

# Testing
make test           # Run all tests
make test-models    # Run core business logic tests
make test-cov       # Test with coverage report

# Building
make build          # Build distributable with PyInstaller
make clean          # Clean temporary files
```

### Essential Testing Commands
```bash
# Environment setup
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Import verification
python -c "from src.clynboozle.services import MediaService, AudioService; print('✅ Services import')"
python -c "from src.clynboozle.models import Question, Team, GameState; print('✅ Models import')"
python -c "from src.clynboozle.config import settings, messages; print('✅ Config imports')"

# Functionality testing
python -c "
from src.clynboozle.services import GameLogicService
from src.clynboozle.models import Question
game_service = GameLogicService()
question = Question(question='Test?', answer='Yes', points=10)
game = game_service.create_game(['Team A', 'Team B'], [question])
game_service.start_game()
print(f'✅ Game works: {game.current_team.name} playing')
"

# Code quality checks
black src/clynboozle --line-length=100
flake8 src/clynboozle --max-line-length=100 --ignore=F401,E501 --statistics
mypy src/clynboozle --ignore-missing-imports
```

### Successful Refactoring Patterns
1. **Config extraction**: Move all constants to `settings.py` classes (Colors, WindowConfig, etc.)
2. **Service pattern**: Create services that manage state internally, expose clean public APIs
3. **Dataclass usage**: Use `@dataclass` for models with validation in `__post_init__`
4. **Path handling**: Use `pathlib.Path` instead of string concatenation for cross-platform support
5. **Error hierarchies**: Custom exceptions with clear inheritance (ValidationError, MediaLoadError, etc.)

### Module Organization Architecture
```
src/clynboozle/
├── config/          # All constants and configuration
│   ├── settings.py  # Technical settings (colors, sizes, paths)
│   └── messages.py  # User-facing text and error messages
├── models/          # Business data models
│   ├── question.py  # Question and MediaReference dataclasses
│   ├── team.py      # Team dataclass with scoring logic
│   └── game_state.py # GameState with turn management
├── services/        # Business logic services
│   ├── audio_service.py    # Pygame audio management
│   ├── image_service.py    # PIL image processing
│   ├── file_service.py     # File I/O operations
│   ├── game_logic.py       # Game flow control
│   └── media_service.py    # Media library management
└── utils/           # Utilities and exceptions
    └── exceptions.py # Custom exception hierarchy
```

### Testing Philosophy & Patterns
- **Test early, test often**: After each major component creation, run import and basic functionality tests
- **Graceful degradation**: All services should work even when optional dependencies are missing
- **Real-world scenarios**: Test with actual game flow (create game, start, take turns, score points)
- **Error recovery**: Verify that error conditions are handled appropriately

### Common API Pitfalls to Avoid
- **Method name confusion**: Use `team.add_points()` not `team.add_score()`
- **Game state requirement**: Must call `game_service.start_game()` before `next_turn()`
- **Property vs method**: Use `game.current_team` (property) not `game.get_current_team()` (method)
- **Service pattern**: GameLogicService manages internal state, don't pass game objects to methods
- **Question model**: No `category` field, only `question`, `answer`, `points` are required
- **UI Button sizing**: Use character units (width=20) not pixel units (width=250) for tkinter Button widgets

### Terminal Command Best Practices
- **Always check working directory**: Use `ls -la` to confirm location before commands
- **Always check if a venv is already running**: `echo $VIRTUAL_ENV`
- **If not active, activate virtual environment**: Every terminal session needs `source venv/bin/activate`
- **Use descriptive explanations**: Each command should explain what it does
- **Handle command failures**: Check exit codes and provide fallback approaches
- **Test incrementally**: Don't run large test suites; test components individually first

### Development Environment Standards
- **Python version**: 3.9+ (tested with 3.13.3)
- **Required dependencies**: pillow, pygame for core functionality
- **Development dependencies**: pytest, black, flake8, mypy, pre-commit for code quality
- **IDE compatibility**: Type hints and structure designed for VS Code IntelliSense
- **Cross-platform**: Path handling uses pathlib.Path for Windows/macOS/Linux compatibility

### Current Limitations & Known Issues
- **Question set management**: UI components exist but not fully integrated into navigation flow
- **Button color issues**: Some platforms may not render button colors correctly (tkinter system theme overrides)
- **Game board**: Exists but not yet integrated into the main application flow
- **Media management**: Full media browser and question set editor need navigation integration

### UI Development Notes
- **Button sizing**: Always use character units for tkinter Button `width`/`height` parameters
- **Color consistency**: Use `activebackground` and `activeforeground` to maintain button colors
- **Platform differences**: macOS may override button styling - test on target platforms
- **Navigation flow**: Use callback pattern for screen transitions, avoid direct UI dependencies
