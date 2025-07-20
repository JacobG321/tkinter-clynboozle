"""Question set management service for ClynBoozle application."""

from typing import Dict, List, Optional, Any
import json
from pathlib import Path
import logging

from ..config.settings import Paths, Validation
from ..models.question import Question, MediaReference
from ..utils.exceptions import FileOperationError, ValidationError
from .file_service import FileService


class QuestionSet:
    """Represents a set of quiz questions."""

    def __init__(self, name: str = "New Question Set", questions: Optional[List[Question]] = None):
        """
        Initialize a question set.

        Args:
            name: Name of the question set
            questions: List of questions in the set
        """
        self.name = name
        self.questions = questions or []
        self._validate_name()

    def _validate_name(self) -> None:
        """Validate question set name."""
        if not self.name or not self.name.strip():
            raise ValidationError("Question set name cannot be empty")

        if len(self.name) > Validation.MAX_DESCRIPTION_LENGTH:
            raise ValidationError(
                f"Question set name too long (max {Validation.MAX_DESCRIPTION_LENGTH} characters)"
            )

    def add_question(self, question: Question) -> None:
        """Add a question to the set."""
        if not isinstance(question, Question):
            raise ValidationError("Invalid question object")
        self.questions.append(question)

    def remove_question(self, index: int) -> bool:
        """
        Remove a question by index.

        Args:
            index: Index of question to remove

        Returns:
            True if question was removed, False if index was invalid
        """
        if 0 <= index < len(self.questions):
            del self.questions[index]
            return True
        return False

    def update_question(self, index: int, question: Question) -> bool:
        """
        Update an existing question.

        Args:
            index: Index of question to update
            question: New question data

        Returns:
            True if question was updated, False if index was invalid
        """
        if not isinstance(question, Question):
            raise ValidationError("Invalid question object")

        if 0 <= index < len(self.questions):
            self.questions[index] = question
            return True
        return False

    def get_question(self, index: int) -> Optional[Question]:
        """Get a question by index."""
        if 0 <= index < len(self.questions):
            return self.questions[index]
        return None

    def get_question_count(self) -> int:
        """Get the number of questions in the set."""
        return len(self.questions)

    def clear_questions(self) -> None:
        """Remove all questions from the set."""
        self.questions.clear()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "questions": [q.to_dict() for q in self.questions],
            "version": "2.0",  # Schema version for future compatibility
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "QuestionSet":
        """Create QuestionSet from dictionary."""
        name = data.get("name", "Unknown Set")
        question_data = data.get("questions", [])

        # Convert question dictionaries to Question objects
        questions = []
        for q_data in question_data:
            try:
                question = Question.from_dict(q_data)
                questions.append(question)
            except Exception as e:
                logging.warning(f"Skipping invalid question: {e}")

        return cls(name=name, questions=questions)

    def copy(self) -> "QuestionSet":
        """Create a deep copy of the question set."""
        return QuestionSet.from_dict(self.to_dict())

    def __str__(self) -> str:
        """String representation of the question set."""
        return f"QuestionSet('{self.name}', {len(self.questions)} questions)"


class QuestionSetService:
    """Service for managing question sets - loading, saving, and CRUD operations."""

    def __init__(self, file_service: FileService):
        """
        Initialize the question set service.

        Args:
            file_service: File service for I/O operations
        """
        self.file_service = file_service
        self.logger = logging.getLogger(__name__)
        self._question_sets: Dict[str, QuestionSet] = {}
        self._current_set_name: Optional[str] = None

        # Ensure question sets directory exists
        self._ensure_question_sets_directory()

        # Load existing question sets
        self._load_all_question_sets()

        # Create default set if none exist
        if not self._question_sets:
            self._create_default_question_set()

    def _ensure_question_sets_directory(self) -> None:
        """Ensure the question sets directory exists."""
        question_sets_dir = self.file_service.get_question_sets_dir()
        self.file_service.create_directory(question_sets_dir)

    def _load_all_question_sets(self) -> None:
        """Load all question sets from the question sets directory."""
        question_sets_dir = self.file_service.get_question_sets_dir()
        json_files = self.file_service.list_files(question_sets_dir, "*.json")

        for file_path in json_files:
            try:
                self._load_question_set_file(file_path)
            except Exception as e:
                self.logger.warning(f"Failed to load question set {file_path}: {e}")

    def _load_question_set_file(self, file_path: Path) -> None:
        """Load a single question set file."""
        try:
            data = self.file_service.read_json_file(file_path)
            question_set = QuestionSet.from_dict(data)

            # Use filename as key (without extension)
            set_key = file_path.stem
            self._question_sets[set_key] = question_set

            # Set as current if it's the first one loaded
            if self._current_set_name is None:
                self._current_set_name = set_key

        except Exception as e:
            raise FileOperationError(f"Failed to load question set from {file_path}: {e}")

    def _create_default_question_set(self) -> None:
        """Create a default question set with sample questions."""
        default_set = QuestionSet("Sample Animals")

        # Add sample questions
        sample_questions = [
            ("I live on a farm and make milk.", "Cow", 15),
            ("I have a long neck and eat leaves.", "Giraffe", 20),
            ("I can fly and chirp.", "Bird", 10),
            ("I am man's best friend.", "Dog", 10),
            ("I say 'meow'.", "Cat", 10),
            ("I have stripes and run fast.", "Zebra", 15),
            ("I swim and have fins.", "Fish", 10),
            ("I jump and live in ponds.", "Frog", 10),
            ("I have a trunk and big ears.", "Elephant", 25),
        ]

        for question_text, answer, points in sample_questions:
            question = Question(question=question_text, answer=answer, points=points)
            default_set.add_question(question)

        # Save and add to memory
        self.save_question_set(default_set, "sample_animals")
        self._current_set_name = "sample_animals"

    def _generate_filename(self, name: str) -> str:
        """Generate a safe filename from question set name."""
        # Sanitize name for filename
        safe_name = "".join(c if c in Validation.SAFE_FILENAME_CHARS else "_" for c in name.lower())

        # Remove multiple underscores
        while "__" in safe_name:
            safe_name = safe_name.replace("__", "_")

        # Remove leading/trailing underscores
        safe_name = safe_name.strip("_")

        # Ensure it's not empty
        if not safe_name:
            safe_name = "question_set"

        return f"{safe_name}.json"

    def get_all_question_sets(self) -> Dict[str, QuestionSet]:
        """Get all loaded question sets."""
        return self._question_sets.copy()

    def get_question_set_names(self) -> List[str]:
        """Get list of all question set names."""
        return list(self._question_sets.keys())

    def get_question_set(self, set_name: str) -> Optional[QuestionSet]:
        """Get a specific question set by name."""
        return self._question_sets.get(set_name)

    def get_current_question_set(self) -> Optional[QuestionSet]:
        """Get the currently selected question set."""
        if self._current_set_name:
            return self._question_sets.get(self._current_set_name)
        return None

    def set_current_question_set(self, set_name: str) -> bool:
        """
        Set the current question set.

        Args:
            set_name: Name of the question set to make current

        Returns:
            True if set was found and set as current, False otherwise
        """
        if set_name in self._question_sets:
            self._current_set_name = set_name
            return True
        return False

    def create_question_set(self, name: str) -> str:
        """
        Create a new question set.

        Args:
            name: Name for the new question set

        Returns:
            The key/identifier for the new question set
        """
        question_set = QuestionSet(name)

        # Generate unique key
        base_key = self.file_service.sanitize_filename(name.lower())
        key = base_key
        counter = 1
        while key in self._question_sets:
            key = f"{base_key}_{counter}"
            counter += 1

        self._question_sets[key] = question_set
        self._current_set_name = key

        return key

    def save_question_set(self, question_set: QuestionSet, set_name: Optional[str] = None) -> str:
        """
        Save a question set to disk.

        Args:
            question_set: The question set to save
            set_name: Optional name to save under (defaults to current)

        Returns:
            The key/identifier used for the saved set
        """
        if set_name is None and self._current_set_name:
            set_name = self._current_set_name
        elif set_name is None:
            set_name = self.file_service.sanitize_filename(question_set.name.lower())

        # Update in memory
        self._question_sets[set_name] = question_set

        # Save to file
        question_sets_dir = self.file_service.get_question_sets_dir()
        filename = self._generate_filename(question_set.name)
        file_path = question_sets_dir / filename

        try:
            self.file_service.write_json_file(file_path, question_set.to_dict())
            self.logger.info(f"Saved question set '{question_set.name}' to {file_path}")
        except Exception as e:
            raise FileOperationError(f"Failed to save question set: {e}")

        return set_name

    def delete_question_set(self, set_name: str) -> bool:
        """
        Delete a question set.

        Args:
            set_name: Name of the question set to delete

        Returns:
            True if set was deleted, False if it didn't exist
        """
        if set_name not in self._question_sets:
            return False

        question_set = self._question_sets[set_name]

        # Remove from memory
        del self._question_sets[set_name]

        # Remove file
        question_sets_dir = self.file_service.get_question_sets_dir()
        filename = self._generate_filename(question_set.name)
        file_path = question_sets_dir / filename

        try:
            if self.file_service.file_exists(file_path):
                self.file_service.delete_file(file_path)
        except Exception as e:
            self.logger.warning(f"Failed to delete question set file: {e}")

        # Update current set if needed
        if self._current_set_name == set_name:
            if self._question_sets:
                self._current_set_name = next(iter(self._question_sets.keys()))
            else:
                self._current_set_name = None

        return True

    def reload_question_sets(self) -> None:
        """Reload all question sets from disk."""
        self._question_sets.clear()
        self._current_set_name = None
        self._load_all_question_sets()

        if not self._question_sets:
            self._create_default_question_set()

    def import_question_set(self, file_path: Path) -> str:
        """
        Import a question set from a file.

        Args:
            file_path: Path to the question set file to import

        Returns:
            The key/identifier for the imported set
        """
        try:
            data = self.file_service.read_json_file(file_path)
            question_set = QuestionSet.from_dict(data)

            # Generate unique key
            base_key = self.file_service.sanitize_filename(question_set.name.lower())
            key = base_key
            counter = 1
            while key in self._question_sets:
                key = f"{base_key}_{counter}"
                counter += 1

            # Save the imported set
            return self.save_question_set(question_set, key)

        except Exception as e:
            raise FileOperationError(f"Failed to import question set: {e}")

    def export_question_set(self, set_name: str, export_path: Path) -> None:
        """
        Export a question set to a file.

        Args:
            set_name: Name of the question set to export
            export_path: Path where to save the exported file
        """
        if set_name not in self._question_sets:
            raise ValidationError(f"Question set '{set_name}' not found")

        question_set = self._question_sets[set_name]

        try:
            self.file_service.write_json_file(export_path, question_set.to_dict())
            self.logger.info(f"Exported question set '{question_set.name}' to {export_path}")
        except Exception as e:
            raise FileOperationError(f"Failed to export question set: {e}")
