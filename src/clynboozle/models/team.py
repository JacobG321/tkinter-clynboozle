"""Team model for ClynBoozle quiz game."""

from __future__ import annotations
from typing import Dict, Any
from dataclasses import dataclass
import re

from ..config.settings import Validation
from ..utils.exceptions import ValidationError


@dataclass
class Team:
    """Represents a team in the quiz game."""

    name: str
    score: int = 0

    def __post_init__(self) -> None:
        """Validate team data after initialization."""
        self._validate_name()

    def _validate_name(self) -> None:
        """Validate team name."""
        if not self.name or not self.name.strip():
            raise ValidationError("Team name cannot be empty")

        # Remove leading/trailing whitespace
        self.name = self.name.strip()

        if len(self.name) > Validation.MAX_TEAM_NAME_LENGTH:
            raise ValidationError(
                f"Team name too long (max {Validation.MAX_TEAM_NAME_LENGTH} characters)"
            )

        # Check for valid characters (allow letters, numbers, spaces, and common punctuation)
        if not re.match(r"^[a-zA-Z0-9\s\-_\.\'\"]+$", self.name):
            raise ValidationError(
                "Team name contains invalid characters. Use letters, numbers, spaces, and basic punctuation only."
            )

    def add_points(self, points: int) -> None:
        """Add points to the team's score."""
        if points < 0:
            raise ValidationError("Cannot add negative points")
        self.score += points

    def subtract_points(self, points: int) -> None:
        """Subtract points from the team's score."""
        if points < 0:
            raise ValidationError("Cannot subtract negative points")
        self.score = max(0, self.score - points)  # Don't allow negative scores

    def reset_score(self) -> None:
        """Reset the team's score to zero."""
        self.score = 0

    def rename(self, new_name: str) -> None:
        """Rename the team with validation."""
        old_name = self.name
        self.name = new_name
        try:
            self._validate_name()
        except ValidationError:
            # Restore old name if validation fails
            self.name = old_name
            raise

    def to_dict(self) -> Dict[str, Any]:
        """Convert team to dictionary for serialization."""
        return {
            "name": self.name,
            "score": self.score,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Team:
        """Create Team from dictionary."""
        return cls(
            name=data["name"],
            score=data.get("score", 0),
        )

    def copy(self) -> Team:
        """Create a copy of the team."""
        return Team(name=self.name, score=self.score)

    def __str__(self) -> str:
        """String representation of the team."""
        return f"{self.name}: {self.score}"

    def __eq__(self, other: object) -> bool:
        """Check equality based on team name (case-insensitive)."""
        if not isinstance(other, Team):
            return NotImplemented
        return self.name.lower() == other.name.lower()

    def __hash__(self) -> int:
        """Hash based on team name (case-insensitive)."""
        return hash(self.name.lower())

    def __lt__(self, other: Team) -> bool:
        """Compare teams by score (for sorting)."""
        return self.score < other.score
