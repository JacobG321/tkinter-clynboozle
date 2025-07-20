"""Tests for ClynBoozle business logic models."""

import pytest
from clynboozle.models.question import Question
from clynboozle.models.team import Team
from clynboozle.models.game_state import GameState
from clynboozle.utils.exceptions import ValidationError, GameStateError


class TestQuestion:
    """Test cases for Question model."""

    def test_question_creation_valid(self):
        """Test creating a valid question."""
        question = Question(question="What is 2+2?", answer="4", points=10)

        assert question.question == "What is 2+2?"
        assert question.answer == "4"
        assert question.points == 10
        assert question.tile_image is None
        assert question.question_image is None
        assert question.question_audio is None

    def test_question_creation_with_media(self):
        """Test creating a question with media."""
        from clynboozle.models.question import MediaReference

        media_ref = MediaReference(media_id="test-id", media_type="image")
        question = Question(
            question="What is this image?", answer="A cat", points=20, question_image=media_ref
        )

        assert question.question_image == media_ref
        assert question.has_question_image()

    def test_question_validation_empty_question(self):
        """Test validation fails for empty question."""
        with pytest.raises(ValidationError, match="Question text cannot be empty"):
            Question(question="", answer="4", points=10)

    def test_question_validation_empty_answer(self):
        """Test validation fails for empty answer."""
        with pytest.raises(ValidationError, match="Answer text cannot be empty"):
            Question(question="What is 2+2?", answer="", points=10)

    def test_question_validation_negative_points(self):
        """Test validation fails for negative points."""
        with pytest.raises(ValidationError, match="Points must be between"):
            Question(question="What is 2+2?", answer="4", points=-10)

    def test_question_validation_zero_points(self):
        """Test validation fails for zero points."""
        with pytest.raises(ValidationError, match="Points must be between"):
            Question(question="What is 2+2?", answer="4", points=0)

    def test_question_to_dict(self):
        """Test question serialization."""
        question = Question(question="What is 2+2?", answer="4", points=10)
        result = question.to_dict()

        assert result["question"] == "What is 2+2?"
        assert result["answer"] == "4"
        assert result["points"] == 10
        assert result["tile_image"] == ""
        assert result["question_image"] == ""
        assert result["question_audio"] == ""

    def test_question_from_dict(self):
        """Test question deserialization."""
        data = {
            "question": "What is 2+2?",
            "answer": "4",
            "points": 10,
            "tile_image": "",
            "question_image": "",
            "question_audio": "",
        }

        question = Question.from_dict(data)
        assert question.question == "What is 2+2?"
        assert question.answer == "4"
        assert question.points == 10
        assert question.tile_image is None
        assert question.question_image is None
        assert question.question_audio is None


class TestTeam:
    """Test cases for Team model."""

    def test_team_creation_valid(self):
        """Test creating a valid team."""
        team = Team(name="Team Alpha")

        assert team.name == "Team Alpha"
        assert team.score == 0

    def test_team_validation_empty_name(self):
        """Test validation fails for empty name."""
        with pytest.raises(ValidationError, match="Team name cannot be empty"):
            Team(name="")

    def test_team_validation_whitespace_name(self):
        """Test validation fails for whitespace-only name."""
        with pytest.raises(ValidationError, match="Team name cannot be empty"):
            Team(name="   ")

    def test_team_add_points(self):
        """Test adding points to team."""
        team = Team(name="Team Alpha")
        team.add_points(50)

        assert team.score == 50

    def test_team_add_multiple_points(self):
        """Test adding points multiple times."""
        team = Team(name="Team Alpha")
        team.add_points(30)
        team.add_points(20)

        assert team.score == 50

    def test_team_subtract_points(self):
        """Test subtracting points from team."""
        team = Team(name="Team Alpha")
        team.add_points(100)
        team.subtract_points(30)

        assert team.score == 70

    def test_team_add_negative_points_fails(self):
        """Test that adding negative points fails."""
        team = Team(name="Team Alpha")
        with pytest.raises(ValidationError, match="Cannot add negative points"):
            team.add_points(-30)

    def test_team_reset_score(self):
        """Test resetting team score."""
        team = Team(name="Team Alpha")
        team.add_points(100)
        team.reset_score()

        assert team.score == 0

    def test_team_equality(self):
        """Test team equality comparison."""
        team1 = Team(name="Team Alpha")
        team2 = Team(name="Team Alpha")
        team3 = Team(name="Team Beta")

        assert team1 == team2
        assert team1 != team3

    def test_team_string_representation(self):
        """Test team string representation."""
        team = Team(name="Team Alpha")
        team.add_points(50)

        assert str(team) == "Team Alpha: 50"


class TestGameState:
    """Test cases for GameState model."""

    def test_game_state_creation(self, sample_teams, sample_questions):
        """Test creating a game state."""
        teams = sample_teams[:2]  # Use first 2 teams
        game = GameState(teams=teams, questions=sample_questions)

        assert len(game.teams) == 2
        assert len(game.questions) == 4
        assert game.current_team_index == 0
        assert game.current_team == teams[0]
        assert game.status.value == "not_started"
        assert len(game.used_question_indices) == 0

    def test_game_state_validation_insufficient_teams(self, sample_questions):
        """Test validation fails with insufficient teams."""
        with pytest.raises(GameStateError, match="Game must have at least"):
            GameState(teams=[Team(name="Solo Team")], questions=sample_questions)

    def test_game_state_validation_too_many_teams(self, sample_questions):
        """Test validation fails with too many teams."""
        teams = [Team(name=f"Team {i}") for i in range(7)]  # 7 teams
        with pytest.raises(GameStateError, match="Game cannot have more than"):
            GameState(teams=teams, questions=sample_questions)

    def test_game_state_validation_no_questions(self, sample_teams):
        """Test validation fails with no questions."""
        with pytest.raises(GameStateError, match="Game must have at least one question"):
            GameState(teams=sample_teams[:2], questions=[])

    def test_game_state_start_game(self, sample_game_state):
        """Test starting a game."""
        game = sample_game_state
        game.start_game()

        assert game.status.value == "in_progress"

    def test_game_state_next_turn(self, sample_game_state):
        """Test advancing to next turn."""
        game = sample_game_state
        game.start_game()

        first_team = game.current_team
        next_team = game.next_team()

        assert game.current_team != first_team
        assert game.current_team == next_team
        assert game.current_team_index == 1

    def test_game_state_turn_wrapping(self, sample_game_state):
        """Test turn wrapping back to first team."""
        game = sample_game_state
        game.start_game()

        # Advance through all teams
        game.next_team()  # To team 1
        next_team = game.next_team()  # Should wrap to team 0

        assert game.current_team_index == 0
        assert game.current_team == game.teams[0]
        assert next_team == game.teams[0]

    def test_game_state_use_question(self, sample_game_state):
        """Test using questions."""
        game = sample_game_state
        game.start_game()
        game.use_question(0)
        game.use_question(2)

        assert 0 in game.used_question_indices
        assert 2 in game.used_question_indices
        assert len(game.used_question_indices) == 2

    def test_game_state_is_question_used(self, sample_game_state):
        """Test checking if question is used."""
        game = sample_game_state
        game.use_question(0)

        assert game.is_question_used(0)
        assert not game.is_question_used(1)

    def test_game_state_get_team_by_name(self, sample_game_state):
        """Test getting team by name."""
        game = sample_game_state

        team = game.get_team_by_name("Team Alpha")
        assert team is not None
        assert team.name == "Team Alpha"

        missing_team = game.get_team_by_name("Missing Team")
        assert missing_team is None

    def test_game_state_get_winner_no_winner(self, sample_game_state):
        """Test winner detection with no clear winner."""
        game = sample_game_state

        # Equal scores
        game.teams[0].add_points(100)
        game.teams[1].add_points(100)

        winner = game.get_winner()
        assert winner is None

    def test_game_state_get_winner_clear_winner(self, sample_game_state):
        """Test winner detection with clear winner."""
        game = sample_game_state

        # Unequal scores
        game.teams[0].add_points(150)
        game.teams[1].add_points(100)

        winner = game.get_winner()
        assert winner == game.teams[0]

    def test_game_state_total_questions(self, sample_game_state):
        """Test getting total question count."""
        game = sample_game_state

        assert game.total_questions == len(game.questions)
        assert game.total_questions == 4

    def test_game_state_reset(self, sample_game_state):
        """Test resetting game state."""
        game = sample_game_state
        game.start_game()
        game.next_team()
        game.use_question(0)
        game.teams[0].add_points(50)

        game.reset_game()

        assert game.status.value == "not_started"
        assert game.current_team_index == 0
        assert len(game.used_question_indices) == 0
        assert all(team.score == 0 for team in game.teams)
