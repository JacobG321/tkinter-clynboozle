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

## Refactoring Roadmap & Project Status

This project follows a comprehensive refactoring roadmap defined in `roadmap.md`. **Always consult the roadmap first** when working on this codebase, as it contains:

### Current Project Phase
The project is in **Phase 5** (Testing & Final Polish) - Near Completion:
- ✅ **Phases 1-3 Complete**: Project structure, business logic separation, and UI architecture
- ✅ **Phase 4.1 Complete**: Logging configuration (`utils/logging_config.py`) and error handling
- 🔄 **Phase 4.2 Partial**: Type hints and documentation (comprehensive type hints exist)
- ✅ **Phase 4.3 Complete**: Performance optimizations (lazy loading, caching)
- ✅ **Phase 5.1 Complete**: Unit testing framework with pytest (32 passing model tests)
- ✅ **Phase 5.3 Complete**: New main application entry point (`src/clynboozle/main.py`)

### Roadmap Guidance
The `roadmap.md` file contains:

1. **Quality Standards**: Function length (20-30 lines max), class length (200-300 lines max), naming conventions
2. **Architecture Principles**: SOLID, DRY, KISS principles with separation of concerns
3. **Development Standards**: Virtual environment setup, testing protocols, code quality commands
4. **Testing Philosophy**: "Test early, test often" with graceful degradation
5. **Success Criteria**: Technical metrics and maintainability improvements

### Key Development Commands from Roadmap
```bash
# Environment verification (always check first)
source venv/bin/activate
python -c "from src.clynboozle.services import MediaService; print('✅ Services import')"

# Code quality checks
black src/clynboozle --line-length=100
flake8 src/clynboozle --max-line-length=100 --ignore=F401,E501
mypy src/clynboozle --ignore-missing-imports

# Service testing patterns
python -c "
from src.clynboozle.services import GameLogicService
from src.clynboozle.models import Question
game_service = GameLogicService()
question = Question(question='Test?', answer='Yes', points=10)
game = game_service.create_game(['Team A'], [question])
game_service.start_game()
print(f'✅ Game works: {game.current_team.name}')
"
```

### Legacy vs Modular Code
- **Legacy Files**: `main.py` (root), `question_set_manager.py`, `media_manager.py`, `media_browser.py`
- **Modular Architecture**: `src/clynboozle/` with proper service separation
- **Transition State**: Both systems coexist during migration

### Common Pitfalls (from Roadmap)
- Use `team.add_points()` not `team.add_score()`
- Must call `game_service.start_game()` before `next_turn()`
- Use `game.current_team` (property) not `game.get_current_team()` (method)
- GameLogicService manages internal state - don't pass game objects to methods

### Next Priority Items
Based on roadmap phases still pending:
1. **Phase 5.2**: Code quality tools integration (linting, formatting, pre-commit hooks)
2. **Phase 5.4**: Migration script for legacy question sets and final cleanup
3. **Phase 4.2**: Complete documentation for public interfaces

### Testing Framework Status
**Phase 5.1 Complete**: Comprehensive testing framework established with pytest:
- **32 passing model tests**: Complete coverage of Question, Team, and GameState models
- **Test fixtures and utilities**: Robust test setup with proper mocking and data generation
- **Integration test framework**: Ready for testing complete workflows
- **Pytest configuration**: Proper markers, filtering, and output configuration
- **Test commands**: `pytest tests/test_models.py -v` for model validation

### Testing Patterns That Work
The established testing framework includes:
- Import layer testing for module independence
- Model validation testing (Question, Team, GameState)
- Business logic testing with proper fixtures
- Error boundary testing for graceful failures
- Service integration testing (framework ready)

**Always reference the roadmap before making architectural decisions or when encountering issues during development.**