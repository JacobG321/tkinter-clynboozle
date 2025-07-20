"""Game state model for ClynBoozle quiz game."""

from __future__ import annotations
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import uuid

from .team import Team
from .question import Question
from ..config.settings import GameConfig
from ..utils.exceptions import GameStateError, ValidationError


class GameStatus(Enum):
    """Enumeration of possible game states."""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"


@dataclass
class GameState:
    """Manages the current state of a quiz game."""

    teams: List[Team]
    questions: List[Question]
    status: GameStatus = GameStatus.NOT_STARTED
    current_team_index: int = 0
    used_question_indices: Set[int] = field(default_factory=set)
    game_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __post_init__(self) -> None:
        """Validate game state after initialization."""
        self._validate()

    def _validate(self) -> None:
        """Validate game state data."""
        if not self.teams:
            raise GameStateError("Game must have at least one team")

        if len(self.teams) < GameConfig.MIN_TEAMS:
            raise GameStateError(f"Game must have at least {GameConfig.MIN_TEAMS} teams")

        if len(self.teams) > GameConfig.MAX_TEAMS:
            raise GameStateError(f"Game cannot have more than {GameConfig.MAX_TEAMS} teams")

        if not self.questions:
            raise GameStateError("Game must have at least one question")

        # Check for duplicate team names
        team_names = [team.name.lower() for team in self.teams]
        if len(team_names) != len(set(team_names)):
            raise GameStateError("Team names must be unique")

        # Validate current team index
        if not (0 <= self.current_team_index < len(self.teams)):
            self.current_team_index = 0

        # Validate used question indices
        self.used_question_indices = {
            idx for idx in self.used_question_indices if 0 <= idx < len(self.questions)
        }

    @property
    def current_team(self) -> Team:
        """Get the currently active team."""
        if not self.teams:
            raise GameStateError("No teams available")
        return self.teams[self.current_team_index]

    @property
    def is_game_over(self) -> bool:
        """Check if all questions have been used."""
        return len(self.used_question_indices) >= len(self.questions)

    @property
    def remaining_questions(self) -> int:
        """Get the number of remaining questions."""
        return len(self.questions) - len(self.used_question_indices)

    @property
    def total_questions(self) -> int:
        """Get the total number of questions."""
        return len(self.questions)

    def start_game(self) -> None:
        """Start the game."""
        if self.status != GameStatus.NOT_STARTED:
            raise GameStateError("Game has already been started")

        self.status = GameStatus.IN_PROGRESS
        self.current_team_index = 0
        self.used_question_indices.clear()

        # Reset all team scores
        for team in self.teams:
            team.reset_score()

    def pause_game(self) -> None:
        """Pause the game."""
        if self.status != GameStatus.IN_PROGRESS:
            raise GameStateError("Can only pause a game in progress")
        self.status = GameStatus.PAUSED

    def resume_game(self) -> None:
        """Resume a paused game."""
        if self.status != GameStatus.PAUSED:
            raise GameStateError("Can only resume a paused game")
        self.status = GameStatus.IN_PROGRESS

    def end_game(self) -> None:
        """End the game."""
        self.status = GameStatus.COMPLETED

    def next_team(self) -> Team:
        """Move to the next team's turn."""
        if self.status != GameStatus.IN_PROGRESS:
            raise GameStateError("Cannot change teams when game is not in progress")

        self.current_team_index = (self.current_team_index + 1) % len(self.teams)
        return self.current_team

    def use_question(self, question_index: int) -> None:
        """Mark a question as used."""
        if not (0 <= question_index < len(self.questions)):
            raise GameStateError(f"Invalid question index: {question_index}")

        if question_index in self.used_question_indices:
            raise GameStateError(f"Question {question_index} has already been used")

        self.used_question_indices.add(question_index)

        # Check if game is over
        if self.is_game_over:
            self.end_game()

    def is_question_used(self, question_index: int) -> bool:
        """Check if a question has been used."""
        return question_index in self.used_question_indices

    def get_available_questions(self) -> List[int]:
        """Get list of available (unused) question indices."""
        return [i for i in range(len(self.questions)) if i not in self.used_question_indices]

    def add_team(self, team: Team) -> None:
        """Add a team to the game."""
        if self.status != GameStatus.NOT_STARTED:
            raise GameStateError("Cannot add teams after game has started")

        # Check for duplicate names
        for existing_team in self.teams:
            if existing_team.name.lower() == team.name.lower():
                raise GameStateError(f"Team name '{team.name}' already exists")

        if len(self.teams) >= GameConfig.MAX_TEAMS:
            raise GameStateError(f"Cannot have more than {GameConfig.MAX_TEAMS} teams")

        self.teams.append(team)

    def remove_team(self, team_name: str) -> bool:
        """Remove a team by name. Returns True if team was removed."""
        if self.status != GameStatus.NOT_STARTED:
            raise GameStateError("Cannot remove teams after game has started")

        for i, team in enumerate(self.teams):
            if team.name.lower() == team_name.lower():
                self.teams.pop(i)
                # Adjust current team index if necessary
                if self.current_team_index >= len(self.teams):
                    self.current_team_index = 0
                return True
        return False

    def get_team_by_name(self, team_name: str) -> Optional[Team]:
        """Get a team by name (case-insensitive)."""
        for team in self.teams:
            if team.name.lower() == team_name.lower():
                return team
        return None

    def get_leaderboard(self) -> List[Team]:
        """Get teams sorted by score (descending)."""
        return sorted(self.teams, key=lambda t: t.score, reverse=True)

    def get_winner(self) -> Optional[Team]:
        """Get the winning team (highest score). Returns None if tied."""
        if not self.teams:
            return None

        leaderboard = self.get_leaderboard()
        if len(leaderboard) >= 2 and leaderboard[0].score == leaderboard[1].score:
            return None  # Tie

        return leaderboard[0]

    def reset_game(self) -> None:
        """Reset the game to initial state."""
        self.status = GameStatus.NOT_STARTED
        self.current_team_index = 0
        self.used_question_indices.clear()

        for team in self.teams:
            team.reset_score()

    def to_dict(self) -> Dict[str, Any]:
        """Convert game state to dictionary for serialization."""
        return {
            "game_id": self.game_id,
            "status": self.status.value,
            "current_team_index": self.current_team_index,
            "used_question_indices": list(self.used_question_indices),
            "teams": [team.to_dict() for team in self.teams],
            "questions": [question.to_dict() for question in self.questions],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> GameState:
        """Create GameState from dictionary."""
        teams = [Team.from_dict(team_data) for team_data in data["teams"]]
        questions = [Question.from_dict(q_data) for q_data in data["questions"]]

        game_state = cls(
            teams=teams,
            questions=questions,
            status=GameStatus(data["status"]),
            current_team_index=data["current_team_index"],
            used_question_indices=set(data["used_question_indices"]),
        )

        if "game_id" in data:
            game_state.game_id = data["game_id"]

        return game_state

    def copy(self) -> GameState:
        """Create a deep copy of the game state."""
        return GameState.from_dict(self.to_dict())

    def __str__(self) -> str:
        """String representation of the game state."""
        return (
            f"GameState(teams={len(self.teams)}, "
            f"questions={len(self.questions)}, "
            f"status={self.status.value}, "
            f"used={len(self.used_question_indices)})"
        )
