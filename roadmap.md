# ClynBoozle Refactoring Roadmap

## Project Goals & Criteria

This refactoring aims to transform the current codebase into a maintainable, professional-grade Python application following senior-level development standards.

### Core Principles
- **KISS (Keep It Simple, Stupid)**: Simplify complex logic, reduce cognitive load
- **DRY (Don't Repeat Yourself)**: Eliminate code duplication, create reusable components
- **SOLID Principles**: Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion
- **Clean Code**: Readable, self-documenting code with clear naming conventions
- **Separation of Concerns**: Business logic separate from UI, clear module boundaries
- **Testability**: Code structure that enables unit testing
- **Type Safety**: Comprehensive type hints for better IDE support and error prevention

### Quality Standards
- Maximum function length: 20-30 lines
- Maximum class length: 200-300 lines
- Clear, descriptive naming (no abbreviations unless standard)
- Comprehensive error handling with user-friendly messages
- Proper logging for debugging and monitoring
- Documentation for all public interfaces

---

## Phase 1: Project Structure & Configuration Foundation

### 1.1 Project Structure Setup
- [x] Create proper package structure with `__init__.py` files
  - [x] `src/` directory for all source code
  - [x] `src/clynboozle/` main package
  - [x] `src/clynboozle/ui/` for UI components
  - [x] `src/clynboozle/models/` for business models
  - [x] `src/clynboozle/services/` for business logic services
  - [x] `src/clynboozle/utils/` for utility functions
  - [x] `src/clynboozle/config/` for configuration
  - [x] `tests/` directory for unit tests

### 1.2 Configuration & Constants Extraction
- [x] Create `src/clynboozle/config/settings.py` with all constants
  - [x] Color scheme constants
  - [x] Font configurations
  - [x] Window dimensions and sizing
  - [x] File paths and directories
  - [x] Media format configurations
  - [x] Game default values
- [x] Create `src/clynboozle/config/messages.py` for UI text and error messages
- [x] Update `.gitignore` to include new structure considerations

### 1.3 Dependencies & Environment
- [x] Review and update `requirements.txt`
- [x] Add development dependencies (testing, linting)
- [x] Create `setup.py` or `pyproject.toml` for package management
- [x] Update README.md with new structure and setup instructions

---

## Phase 2: Business Logic Separation & Models

### 2.1 Core Business Models
- [x] Extract `Question` class to `src/clynboozle/models/question.py`
  - [x] Add type hints and validation
  - [x] Add methods for serialization/deserialization
  - [x] Add media reference handling
- [x] Create `Team` class in `src/clynboozle/models/team.py`
  - [x] Encapsulate team data and scoring logic
  - [x] Add validation for team names
- [x] Create `GameState` class in `src/clynboozle/models/game_state.py`
  - [x] Track current game status, teams, scores
  - [x] Handle turn management
  - [x] Manage used tiles and game progression

### 2.2 Service Layer Creation
- [x] Create `AudioService` in `src/clynboozle/services/audio_service.py`
  - [x] Encapsulate pygame audio functionality
  - [x] Add proper error handling for audio initialization
  - [x] Implement seeking, play, pause, stop functionality
- [x] Create `ImageService` in `src/clynboozle/services/image_service.py`
  - [x] Handle image loading, resizing, caching
  - [x] Manage PIL operations
  - [x] Optimize memory usage
- [x] Create `FileService` in `src/clynboozle/services/file_service.py`
  - [x] Handle all file I/O operations
  - [x] Centralize path management
  - [x] Add robust error handling
- [x] Create `GameLogicService` in `src/clynboozle/services/game_logic.py`
  - [x] Game flow control (start, next turn, scoring)
  - [x] Grid calculation logic
  - [x] Win condition checking

### 2.3 Enhanced Media Management
- [x] Refactor `MediaManager` class
  - [x] Add comprehensive type hints
  - [x] Improve error handling
  - [x] Add validation for media formats
  - [x] Optimize database operations

---

## Phase 3: UI Architecture Refactoring

### 3.1 UI Base Classes & Components
- [x] Create `BaseFrame` in `src/clynboozle/ui/base_frame.py`
  - [x] Common frame functionality (resize handling, styling)
  - [x] Shared widget creation methods
  - [x] Consistent event binding patterns
- [x] Create `BaseDialog` in `src/clynboozle/ui/base_dialog.py`
  - [x] Modal dialog common functionality
  - [x] Centering and positioning logic
  - [x] Standard button layouts
- [x] Create reusable UI components in `src/clynboozle/ui/components/`
  - [x] `MessageDialog` component for alerts and confirmations
  - [x] `InputDialog` component for text input
  - [x] UI package structure with proper imports
  - [x] Test script to validate components work correctly

### 3.2 Main UI Modules Extraction
- [x] Extract `MainMenuFrame` to `src/clynboozle/ui/main_menu.py`
  - [x] Inherit from BaseFrame
  - [x] Simplify button creation with components
  - [x] Remove business logic dependencies
- [x] Extract `TeamSetupFrame` to `src/clynboozle/ui/team_setup.py`
  - [x] Inherit from BaseFrame
  - [x] Separate validation logic
  - [x] Improve form handling
- [x] Extract `GameBoardFrame` to `src/clynboozle/ui/game_board.py`
  - [x] Inherit from BaseFrame
  - [x] Simplify tile creation and management
  - [x] Separate game logic from display logic
- [x] Extract question dialog to `src/clynboozle/ui/question_dialog.py`
  - [x] Inherit from BaseDialog
  - [x] Separate media handling logic
  - [x] Improve layout and responsiveness

### 3.3 UI Utilities & Helpers
- [x] Create `src/clynboozle/ui/utils.py`
  - [x] Font scaling utilities
  - [x] Window positioning helpers
  - [x] Color and theme utilities
- [x] Create `src/clynboozle/ui/styles.py`
  - [x] Centralized styling functions
  - [x] Theme management
  - [x] Consistent styling application

---

## Phase 4: Code Quality & Robustness

### 4.1 Error Handling & Logging
- [x] Create logging configuration in `src/clynboozle/utils/logging_config.py`
  - [x] Set up file and console logging
  - [x] Configure log levels and formatting
- [x] Add comprehensive error handling throughout codebase
  - [x] Try-catch blocks around file operations
  - [x] User-friendly error messages via message service
  - [x] Graceful degradation for missing media
- [x] Create custom exception classes in `src/clynboozle/utils/exceptions.py`
  - [x] `MediaLoadError`
  - [x] `QuestionSetError`
  - [x] `GameStateError`

### 4.2 Type Hints & Documentation
- [ ] Add comprehensive type hints to all modules
  - [ ] Function parameters and return types
  - [ ] Class attributes and properties
  - [ ] Complex type annotations where needed
- [ ] Add docstrings to all classes and public methods
  - [ ] Follow Google or NumPy docstring format
  - [ ] Include parameter descriptions and examples
  - [ ] Document exceptions that may be raised
- [ ] Update README.md with comprehensive documentation
  - [ ] Installation and setup instructions
  - [ ] Architecture overview
  - [ ] Contributing guidelines

### 4.3 Performance & Memory Optimization
- [x] Implement lazy loading for images
  - [x] Load images only when needed
  - [x] Cache frequently used images
  - [x] Implement image cleanup on game end
- [x] Optimize resize handling
  - [x] Debounce resize events properly
  - [x] Cache calculated dimensions
  - [x] Minimize unnecessary redraws
- [x] Memory management improvements
  - [x] Proper cleanup of pygame resources
  - [x] Image reference management
  - [x] Temporary file cleanup

---

## Phase 5: Testing & Final Polish

### 5.1 Unit Testing Setup
- [x] Set up testing framework (pytest)
- [x] Create test utilities and fixtures
- [x] Add tests for business logic classes
  - [x] Question, Team, GameState models
  - [x] Service layer functionality (framework ready)
  - [x] Utility functions
- [x] Add integration tests for critical workflows
  - [x] Game flow from start to finish
  - [x] Media loading and management
  - [x] File operations and persistence

### 5.2 Code Quality Tools
- [ ] Set up linting with flake8 or pylint
- [ ] Configure black for code formatting
- [ ] Add pre-commit hooks for quality checks
- [ ] Set up mypy for static type checking

### 5.3 Final Application Assembly
- [x] Create new main application entry point
  - [x] Clean separation of initialization logic
  - [x] Dependency injection setup
  - [x] Error handling for startup failures
- [ ] Update packaging and distribution
  - [ ] Update PyInstaller spec if needed
  - [ ] Test application building and distribution
  - [ ] Update documentation for end users

### 5.4 Migration & Cleanup
- [ ] Create migration script for existing question sets
- [ ] Verify backward compatibility with existing data
- [ ] Remove old monolithic files
- [ ] Final testing of complete application

---

## Success Criteria

### Technical Metrics
- [ ] Codebase reduced from 1750+ line main.py to modular structure
- [ ] No function longer than 30 lines
- [ ] No class longer than 300 lines
- [ ] 100% type hint coverage
- [ ] 90%+ test coverage for business logic
- [ ] Zero linting errors
- [ ] All magic numbers and strings extracted to configuration

### Maintainability Improvements
- [ ] New features can be added without modifying existing code (Open/Closed Principle)
- [ ] Business logic can be tested without UI dependencies
- [ ] UI components are reusable across different screens
- [ ] Configuration changes don't require code modifications
- [ ] Error messages are user-friendly and actionable

### Performance & User Experience
- [ ] Application startup time improved or maintained
- [ ] Memory usage optimized (no memory leaks)
- [ ] Responsive UI during media loading
- [ ] Graceful handling of missing or corrupted media files
- [ ] Consistent visual styling across all screens

---

## Development Standards & Testing Guidelines

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

### Testing Commands Used Successfully
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

### Error Handling & Resolution Patterns
- **Import errors**: Expected for optional dependencies (PIL, pygame) - code should handle gracefully
- **Duplicate class definitions**: Check for accidental duplications when refactoring config files
- **Method signature mismatches**: Always verify service method signatures before calling them
- **Type hint issues**: Use `Optional[Any]` for complex return types from optional dependencies

### Testing Philosophy
- **Test early, test often**: After each major component creation, run import and basic functionality tests
- **Graceful degradation**: All services should work even when optional dependencies are missing
- **Real-world scenarios**: Test with actual game flow (create game, start, take turns, score points)
- **Error recovery**: Verify that error conditions are handled appropriately

### Quality Metrics Validation
- **No bare except clauses**: Use `except Exception:` instead of `except:`
- **No duplicate class definitions**: Watch for copy-paste errors in config files
- **Clean imports**: Remove unused imports flagged by linting tools
- **Type safety**: Comprehensive type hints with proper Optional handling

### Code Quality Insights Discovered
- **Black formatting**: Automatically handles most PEP 8 compliance, run before linting
- **Flake8 configuration**: `--max-line-length=100 --ignore=F401,E501` works well for this codebase
- **MyPy limitations**: Some PIL/pygame type issues are expected in development environment
- **Import organization**: Use try-catch for optional dependencies with graceful fallbacks
- **Class design**: Keep classes under 300 lines, methods under 30 lines for maintainability

### Successful Refactoring Patterns Used
1. **Config extraction**: Move all constants to `settings.py` classes (Colors, WindowConfig, etc.)
2. **Service pattern**: Create services that manage state internally, expose clean public APIs
3. **Dataclass usage**: Use `@dataclass` for models with validation in `__post_init__`
4. **Path handling**: Use `pathlib.Path` instead of string concatenation for cross-platform support
5. **Error hierarchies**: Custom exceptions with clear inheritance (ValidationError, MediaLoadError, etc.)

### Module Organization That Works
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

### Architecture Validation Approach
1. **Import layer testing**: Verify all modules can be imported independently
2. **Service layer testing**: Test that services can be instantiated and basic methods work
3. **Business logic testing**: Verify game flow, team management, and scoring logic
4. **Integration testing**: Test that services work together (e.g., game service with models)
5. **Error boundary testing**: Verify graceful handling of missing dependencies and invalid inputs

### Specific Testing Patterns That Work
```python
# Pattern 1: Basic service instantiation and stats
media_service = MediaService()
stats = media_service.get_storage_stats()
print(f'✅ MediaService: {stats.total_items} items')

# Pattern 2: Complete game flow testing
game_service = GameLogicService()
question = Question(question='What is 2+2?', answer='4', points=10)
game = game_service.create_game(['Team Alpha', 'Team Beta'], [question])
game_service.start_game()  # Required before turn operations
next_team = game_service.next_turn()
print(f'✅ Game flow: {game.current_team.name} -> {next_team.name}')

# Pattern 3: Team scoring validation
team = Team(name='Test Team')
team.add_points(100)  # Note: method is add_points, not add_score
print(f'✅ Team scoring: {team.name} has {team.score} points')

# Pattern 4: Error handling verification
try:
    invalid_team = Team(name='')  # Should raise ValidationError
except ValidationError as e:
    print(f'✅ Validation works: {e}')
```

### Common Pitfalls to Avoid
- **Method name confusion**: Use `team.add_points()` not `team.add_score()`
- **Game state requirement**: Must call `game_service.start_game()` before `next_turn()`
- **Property vs method**: Use `game.current_team` (property) not `game.get_current_team()` (method)
- **Service pattern**: GameLogicService manages internal state, don't pass game objects to methods
- **Question model**: No `category` field, only `question`, `answer`, `points` are required

### Terminal Command Best Practices
- **Always check working directory**: Use `ls -la` to confirm location before commands
- **Always check if a venv is already running, or available to run**: `echo $VIRTUAL_ENV`
- **If not active, activate virtual environment**: Every terminal session needs `source venv/bin/activate`
- **Use descriptive explanations**: Each `run_in_terminal` call should explain what it does
- **Handle command failures**: Check exit codes and provide fallback approaches
- **Test incrementally**: Don't run large test suites; test components individually first

### Development Environment Standards
- **Python version**: 3.9+ (tested with 3.13.3)
- **Required dependencies**: pillow, pygame for core functionality
- **Development dependencies**: pytest, black, flake8, mypy, pre-commit for code quality
- **IDE compatibility**: Type hints and structure designed for VS Code IntelliSense
- **Cross-platform**: Path handling uses pathlib.Path for Windows/macOS/Linux compatibility

---

## Notes

- Each checkbox represents a discrete, testable milestone
- Items should be completed in order within each phase
- Testing should be done after each major component is refactored
- Commit frequently with descriptive messages
- Document any architectural decisions or tradeoffs made during refactoring
- **Follow the testing protocols above when continuing development**
- **Always verify virtual environment is activated before running commands**
- **Test both success and failure cases for robust error handling**
