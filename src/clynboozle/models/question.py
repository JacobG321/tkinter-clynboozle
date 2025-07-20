"""Question model for ClynBoozle quiz game."""

from __future__ import annotations
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, field
import json

from ..config.settings import Validation
from ..utils.exceptions import ValidationError


@dataclass
class MediaReference:
    """Represents a reference to a media file in the media manager."""

    media_id: str
    media_type: str  # "image" or "audio"
    filename: Optional[str] = None
    description: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "type": "media_reference",
            "media_id": self.media_id,
            "media_type": self.media_type,
            "filename": self.filename,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> MediaReference:
        """Create MediaReference from dictionary."""
        if data.get("type") != "media_reference":
            raise ValidationError("Invalid media reference format")

        return cls(
            media_id=data["media_id"],
            media_type=data["media_type"],
            filename=data.get("filename"),
            description=data.get("description"),
        )


@dataclass
class Question:
    """Represents a single quiz question with associated media and metadata."""

    question: str
    answer: str
    points: int
    tile_image: Optional[Union[str, MediaReference]] = None
    question_image: Optional[Union[str, MediaReference]] = None
    question_audio: Optional[Union[str, MediaReference]] = None

    # Runtime attributes (not serialized)
    _question_pil: Optional[Any] = field(default=None, repr=False, compare=False)
    _question_audio_data: Optional[bytes] = field(default=None, repr=False, compare=False)
    _audio_filename: Optional[str] = field(default=None, repr=False, compare=False)

    def __post_init__(self) -> None:
        """Validate question data after initialization."""
        self._validate()

    def _validate(self) -> None:
        """Validate question data."""
        if not self.question or not self.question.strip():
            raise ValidationError("Question text cannot be empty")

        if not self.answer or not self.answer.strip():
            raise ValidationError("Answer text cannot be empty")

        if len(self.question) > Validation.MAX_QUESTION_LENGTH:
            raise ValidationError(
                f"Question text too long (max {Validation.MAX_QUESTION_LENGTH} characters)"
            )

        if len(self.answer) > Validation.MAX_ANSWER_LENGTH:
            raise ValidationError(
                f"Answer text too long (max {Validation.MAX_ANSWER_LENGTH} characters)"
            )

        if not (Validation.MIN_POINTS <= self.points <= Validation.MAX_POINTS):
            raise ValidationError(
                f"Points must be between {Validation.MIN_POINTS} and {Validation.MAX_POINTS}"
            )

    def has_tile_image(self) -> bool:
        """Check if question has a tile image."""
        return self.tile_image is not None

    def has_question_image(self) -> bool:
        """Check if question has a question image."""
        return self.question_image is not None

    def has_question_audio(self) -> bool:
        """Check if question has question audio."""
        return self.question_audio is not None

    def get_media_references(self) -> Dict[str, MediaReference]:
        """Get all media references in this question."""
        references = {}

        for attr_name in ["tile_image", "question_image", "question_audio"]:
            value = getattr(self, attr_name)
            if isinstance(value, MediaReference):
                references[attr_name] = value

        return references

    def set_tile_image(self, media_ref: Optional[MediaReference]) -> None:
        """Set tile image media reference."""
        if media_ref is not None and media_ref.media_type != "image":
            raise ValidationError("Tile image must be an image media reference")
        self.tile_image = media_ref

    def set_question_image(self, media_ref: Optional[MediaReference]) -> None:
        """Set question image media reference."""
        if media_ref is not None and media_ref.media_type != "image":
            raise ValidationError("Question image must be an image media reference")
        self.question_image = media_ref

    def set_question_audio(self, media_ref: Optional[MediaReference]) -> None:
        """Set question audio media reference."""
        if media_ref is not None and media_ref.media_type != "audio":
            raise ValidationError("Question audio must be an audio media reference")
        self.question_audio = media_ref

    def to_dict(self) -> Dict[str, Any]:
        """Convert question to dictionary for serialization."""
        data = {
            "question": self.question,
            "answer": self.answer,
            "points": self.points,
        }

        # Handle media references
        for attr_name in ["tile_image", "question_image", "question_audio"]:
            value = getattr(self, attr_name)
            if value is None:
                data[attr_name] = ""
            elif isinstance(value, MediaReference):
                data[attr_name] = value.to_dict()
            else:
                # Legacy string format
                data[attr_name] = str(value)

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Question:
        """Create Question from dictionary."""

        # Handle media references
        def parse_media_field(field_data: Any) -> Optional[Union[str, MediaReference]]:
            if not field_data:
                return None
            elif isinstance(field_data, dict) and field_data.get("type") == "media_reference":
                return MediaReference.from_dict(field_data)
            else:
                # Legacy string format
                return str(field_data) if field_data else None

        return cls(
            question=data["question"],
            answer=data["answer"],
            points=int(data["points"]),
            tile_image=parse_media_field(data.get("tile_image")),
            question_image=parse_media_field(data.get("question_image")),
            question_audio=parse_media_field(data.get("question_audio")),
        )

    def to_json(self) -> str:
        """Convert question to JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> Question:
        """Create Question from JSON string."""
        try:
            data = json.loads(json_str)
            return cls.from_dict(data)
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise ValidationError(f"Invalid question JSON: {e}")

    def copy(self) -> Question:
        """Create a deep copy of the question."""
        return Question.from_dict(self.to_dict())

    def __str__(self) -> str:
        """String representation of the question."""
        return f"Question('{self.question[:50]}...', {self.points} points)"
