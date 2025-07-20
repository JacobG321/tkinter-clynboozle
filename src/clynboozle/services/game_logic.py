"""Game logic service for ClynBoozle application."""

from typing import List, Tuple, Optional
import math

from ..models.game_state import GameState, GameStatus
from ..models.team import Team
from ..models.question import Question
from ..config.settings import GameConfig
from ..utils.exceptions import GameStateError


class GameLogicService:
    """Service for handling game flow and logic operations."""

    def __init__(self) -> None:
        """Initialize the game logic service."""
        self._current_game: Optional[GameState] = None

    @property
    def current_game(self) -> Optional[GameState]:
        """Get the current game state."""
        return self._current_game

    def create_game(self, team_names: List[str], questions: List[Question]) -> GameState:
        """Create a new game with teams and questions."""
        if not team_names:
            raise GameStateError("At least one team is required")

        if not questions:
            raise GameStateError("At least one question is required")

        # Create teams from names
        teams = []
        seen_names = set()

        for name in team_names:
            name = name.strip()
            if not name:
                continue

            # Ensure unique names
            original_name = name
            counter = 1
            while name.lower() in seen_names:
                name = f"{original_name} ({counter})"
                counter += 1

            seen_names.add(name.lower())
            teams.append(Team(name=name))

        # Create game state
        self._current_game = GameState(teams=teams, questions=questions.copy())
        return self._current_game

    def start_game(self) -> None:
        """Start the current game."""
        if not self._current_game:
            raise GameStateError("No game to start")

        self._current_game.start_game()

    def end_game(self) -> None:
        """End the current game."""
        if not self._current_game:
            raise GameStateError("No game to end")

        self._current_game.end_game()

    def pause_game(self) -> None:
        """Pause the current game."""
        if not self._current_game:
            raise GameStateError("No game to pause")

        self._current_game.pause_game()

    def resume_game(self) -> None:
        """Resume the current game."""
        if not self._current_game:
            raise GameStateError("No game to resume")

        self._current_game.resume_game()

    def next_turn(self) -> Team:
        """Move to the next team's turn."""
        if not self._current_game:
            raise GameStateError("No active game")

        return self._current_game.next_team()

    def answer_question(
        self, question_index: int, is_correct: bool, team: Optional[Team] = None
    ) -> None:
        """Process a question answer."""
        if not self._current_game:
            raise GameStateError("No active game")

        if self._current_game.status != GameStatus.IN_PROGRESS:
            raise GameStateError("Game is not in progress")

        if question_index < 0 or question_index >= len(self._current_game.questions):
            raise GameStateError("Invalid question index")

        if self._current_game.is_question_used(question_index):
            raise GameStateError("Question has already been answered")

        # Use current team if none specified
        if team is None:
            team = self._current_game.current_team

        # Award points if correct
        if is_correct:
            question = self._current_game.questions[question_index]
            team.add_points(question.points)

        # Mark question as used
        self._current_game.use_question(question_index)

    def calculate_grid_dimensions(self, num_questions: int) -> Tuple[int, int]:
        """Calculate optimal grid dimensions for the question board."""
        if num_questions <= 0:
            return (1, 1)

        # Try to create a roughly square grid
        cols = int(math.sqrt(num_questions))
        if cols == 0:
            cols = 1

        rows = math.ceil(num_questions / cols)

        # Adjust to minimize empty cells while keeping reasonable proportions
        best_rows, best_cols = rows, cols
        min_empty = rows * cols - num_questions

        # Try a few different column counts around the square root
        for test_cols in range(max(1, cols - 2), cols + 3):
            test_rows = math.ceil(num_questions / test_cols)
            empty_cells = test_rows * test_cols - num_questions

            # Prefer fewer empty cells, but also reasonable aspect ratios
            aspect_ratio = test_rows / test_cols
            if empty_cells < min_empty or (empty_cells == min_empty and 0.5 <= aspect_ratio <= 2.0):
                best_rows, best_cols = test_rows, test_cols
                min_empty = empty_cells

        return (best_rows, best_cols)

    def get_available_questions(self) -> List[int]:
        """Get indices of available (unused) questions."""
        if not self._current_game:
            return []

        return self._current_game.get_available_questions()

    def get_leaderboard(self) -> List[Team]:
        """Get teams sorted by score."""
        if not self._current_game:
            return []

        return self._current_game.get_leaderboard()

    def get_winner(self) -> Optional[Team]:
        """Get the winning team."""
        if not self._current_game:
            return None

        return self._current_game.get_winner()

    def is_game_over(self) -> bool:
        """Check if the game is over."""
        if not self._current_game:
            return False

        return self._current_game.is_game_over

    def get_game_progress(self) -> Tuple[int, int]:
        """Get game progress as (answered_questions, total_questions)."""
        if not self._current_game:
            return (0, 0)

        total = self._current_game.total_questions
        answered = total - self._current_game.remaining_questions
        return (answered, total)

    def reset_current_game(self) -> None:
        """Reset the current game to initial state."""
        if not self._current_game:
            raise GameStateError("No game to reset")

        self._current_game.reset_game()

    def create_game_from_template(
        self, team_names: List[str], question_set_name: str, questions: List[Question]
    ) -> GameState:
        """Create a game from a question set template."""
        game = self.create_game(team_names, questions)

        # Add metadata about the question set
        # This could be extended to store additional game configuration
        return game

    def validate_team_names(self, team_names: List[str]) -> List[str]:
        """Validate and clean team names."""
        if not team_names:
            raise GameStateError("At least one team name is required")

        cleaned_names = []
        seen_names = set()

        for name in team_names:
            name = name.strip()
            if not name:
                continue

            # Ensure unique names (case-insensitive)
            original_name = name
            counter = 1
            while name.lower() in seen_names:
                name = f"{original_name} ({counter})"
                counter += 1

            seen_names.add(name.lower())

            # Validate the name using Team class validation
            try:
                test_team = Team(name=name)
                cleaned_names.append(test_team.name)
            except Exception as e:
                raise GameStateError(f"Invalid team name '{original_name}': {e}")

        if len(cleaned_names) < GameConfig.MIN_TEAMS:
            raise GameStateError(f"At least {GameConfig.MIN_TEAMS} teams are required")

        if len(cleaned_names) > GameConfig.MAX_TEAMS:
            raise GameStateError(f"Maximum {GameConfig.MAX_TEAMS} teams allowed")

        return cleaned_names

    def get_team_by_name(self, team_name: str) -> Optional[Team]:
        """Get a team by name from the current game."""
        if not self._current_game:
            return None

        return self._current_game.get_team_by_name(team_name)

    def add_bonus_points(self, team_name: str, points: int) -> None:
        """Add bonus points to a team."""
        if not self._current_game:
            raise GameStateError("No active game")

        team = self.get_team_by_name(team_name)
        if not team:
            raise GameStateError(f"Team '{team_name}' not found")

        team.add_points(points)

    def subtract_penalty_points(self, team_name: str, points: int) -> None:
        """Subtract penalty points from a team."""
        if not self._current_game:
            raise GameStateError("No active game")

        team = self.get_team_by_name(team_name)
        if not team:
            raise GameStateError(f"Team '{team_name}' not found")

        team.subtract_points(points)

    def clear_current_game(self) -> None:
        """Clear the current game."""
        self._current_game = None
