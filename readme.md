
# ClynBoozle

A multimedia quiz game application built with Python and Tkinter. ClynBoozle allows you to create, manage, and play custom quiz games with support for images, audio, and various question formats.

## Features

- 📝 Create and manage custom question sets
- 🖼️ Support for images (tile images and question images)
- 🎵 Audio support for questions
- 👥 Multi-team gameplay (2-6 teams)
- 💾 WordPress-style media management
- 📱 Responsive UI with scaling support
- 🎨 Modern, clean interface

## Project Structure

```
clynboozle/
├── src/clynboozle/          # Main application package
│   ├── config/              # Configuration and constants
│   ├── models/              # Business models
│   ├── services/            # Business logic services
│   ├── ui/                  # User interface components
│   └── utils/               # Utility functions
├── tests/                   # Unit and integration tests
├── question_sets/           # Question set files (JSON)
├── uploads/                 # Media files and database
└── requirements.txt         # Python dependencies
```

## Installation

### Prerequisites

- Python 3.9 or higher
- pip (Python package installer)

### Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd clynboozle
   ```

2. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   ```

3. **Activate the virtual environment:**
   ```bash
   # On macOS/Linux:
   source venv/bin/activate
   
   # On Windows:
   venv\Scripts\activate
   ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Install development dependencies (optional):**
   ```bash
   pip install -r requirements-dev.txt
   ```

## Usage

### Running the Application

```bash
# From the root directory
python main.py

# Or using the package (after installation)
python -m clynboozle
```

### Development

#### Running Tests

```bash
pytest
```

#### Code Formatting

```bash
black src/ tests/
```

#### Type Checking

```bash
mypy src/
```

#### Linting

```bash
flake8 src/ tests/
```

## Building for Distribution

### Using PyInstaller

```bash
# Install build dependencies
pip install -r requirements.txt pyinstaller

# Build the application
pyinstaller ClynBoozle.spec
```

The built application will be available in the `dist/` directory.

## Game Features

### Question Sets
- Create custom question sets with JSON format
- Import/export question sets
- Support for multiple question types

### Media Management
- Upload and organize images and audio files
- Automatic image resizing for different use cases
- WordPress-style media library interface

### Gameplay
- Support for 2-6 teams
- Point-based scoring system
- Turn-based gameplay
- Audio playback controls
- Image viewing with zoom functionality

## Configuration

The application uses a centralized configuration system located in `src/clynboozle/config/`:

- `settings.py`: Application constants and configuration
- `messages.py`: UI text and error messages

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes following the coding standards
4. Run tests and ensure they pass
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Coding Standards

- Follow PEP 8 style guidelines
- Use type hints for all functions
- Write docstrings for all classes and functions
- Maintain test coverage above 90%
- Use meaningful variable and function names

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Changelog

### Version 2.0.0
- Complete codebase refactoring for maintainability
- Modular architecture with separation of concerns
- Improved error handling and logging
- Enhanced type safety with comprehensive type hints
- Modern Python packaging with pyproject.toml

### Version 1.0.0
- Initial release with basic quiz functionality
- Media management system
- Multi-team support
