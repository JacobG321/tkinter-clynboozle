"""Pytest configuration and fixtures for ClynBoozle tests."""

import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Generator, Dict, Any
import sys
import os

# Add src directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from clynboozle.models.question import Question
from clynboozle.models.team import Team
from clynboozle.models.game_state import GameState
from clynboozle.services.game_logic import GameLogicService
from clynboozle.services.file_service import FileService
from clynboozle.utils.logging_config import LoggingConfig


@pytest.fixture(scope="session", autouse=True)
def setup_test_logging():
    """Disable logging during tests to reduce noise."""
    LoggingConfig.disable_logging()
    yield
    LoggingConfig.enable_logging()


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files."""
    temp_dir = Path(tempfile.mkdtemp())
    try:
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def sample_questions() -> list[Question]:
    """Create sample questions for testing."""
    return [
        Question(question="What is 2+2?", answer="4", points=10),
        Question(question="What is the capital of France?", answer="Paris", points=20),
        Question(question="What is H2O?", answer="Water", points=30),
        Question(question="Who wrote Romeo and Juliet?", answer="Shakespeare", points=40),
    ]


@pytest.fixture
def sample_teams() -> list[Team]:
    """Create sample teams for testing."""
    return [
        Team(name="Team Alpha"),
        Team(name="Team Beta"),
        Team(name="Team Gamma"),
    ]


@pytest.fixture
def game_service() -> GameLogicService:
    """Create a GameLogicService instance for testing."""
    return GameLogicService()


@pytest.fixture
def file_service(temp_dir: Path) -> FileService:
    """Create a FileService instance with temporary directory."""
    return FileService(str(temp_dir))


@pytest.fixture
def sample_game_state(sample_teams: list[Team], sample_questions: list[Question]) -> GameState:
    """Create a sample game state for testing."""
    return GameState(teams=sample_teams[:2], questions=sample_questions)


@pytest.fixture
def question_set_data() -> Dict[str, Any]:
    """Sample question set data in JSON format."""
    return {
        "name": "Test Quiz",
        "description": "A test quiz for unit testing",
        "questions": [
            {
                "question": "What is 2+2?",
                "answer": "4", 
                "points": 10,
                "media_id": None
            },
            {
                "question": "What is the capital of France?",
                "answer": "Paris",
                "points": 20,
                "media_id": None
            }
        ]
    }


@pytest.fixture
def mock_media_data() -> Dict[str, Any]:
    """Sample media database data."""
    return {
        "items": {
            "test-id-1": {
                "id": "test-id-1",
                "original_filename": "test_image.png",
                "media_type": "image",
                "file_size": 1024,
                "dimensions": {"width": 800, "height": 600},
                "created_at": "2024-01-01T00:00:00Z",
                "file_variants": {
                    "original": "test-id-1_original.png",
                    "thumbnail": "test-id-1_thumbnail.png",
                    "tile": "test-id-1_tile.png"
                }
            }
        },
        "total_items": 1,
        "total_size": 1024
    }