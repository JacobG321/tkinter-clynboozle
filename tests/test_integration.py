"""Integration tests for ClynBoozle application workflows."""

import pytest
import json
from pathlib import Path

from clynboozle.services.game_logic import GameLogicService
from clynboozle.services.file_service import FileService
from clynboozle.models.question import Question
from clynboozle.models.team import Team
from clynboozle.utils.exceptions import ValidationError


class TestGameWorkflow:
    """Test complete game workflow from start to finish."""

    def test_complete_game_workflow(self, sample_questions):
        """Test a complete game from creation to finish."""
        game_service = GameLogicService()
        team_names = ["Team Alpha", "Team Beta", "Team Gamma"]
        
        # 1. Create game
        game = game_service.create_game(team_names, sample_questions)
        assert len(game.teams) == 3
        assert len(game.questions) == 4
        assert not game.is_started
        
        # 2. Start game
        game_service.start_game()
        assert game.is_started
        assert game.current_team.name == "Team Alpha"
        
        # 3. Play several rounds
        initial_team = game.current_team
        
        # Team Alpha scores
        game_service.award_points(20)
        assert initial_team.score == 20
        
        # Move to Team Beta
        next_team = game_service.next_turn()
        assert next_team.name == "Team Beta"
        game_service.award_points(30)
        assert next_team.score == 30
        
        # Move to Team Gamma
        next_team = game_service.next_turn()
        assert next_team.name == "Team Gamma"
        game_service.award_points(10)
        assert next_team.score == 10
        
        # Back to Team Alpha
        next_team = game_service.next_turn()
        assert next_team.name == "Team Alpha"
        game_service.award_points(40)  # Alpha now has 60 total
        
        # 4. Check standings
        stats = game_service.get_game_stats()
        assert stats["highest_score"] == 60
        
        # 5. Check winner
        winner = game.check_win_condition()
        assert winner.name == "Team Alpha"
        assert winner.score == 60

    def test_game_with_tile_management(self, sample_questions):
        """Test game workflow with tile usage tracking."""
        game_service = GameLogicService()
        team_names = ["Team Alpha", "Team Beta"]
        
        game = game_service.create_game(team_names, sample_questions)
        game_service.start_game()
        
        # Calculate grid dimensions
        rows, cols = game_service.calculate_grid_dimensions(len(sample_questions))
        assert rows * cols >= len(sample_questions)
        
        # Mark some tiles as used
        game.mark_tile_used(0, 0)
        game.mark_tile_used(1, 1)
        
        assert game.is_tile_used(0, 0)
        assert game.is_tile_used(1, 1)
        assert not game.is_tile_used(0, 1)
        
        # Verify used tiles persist through turns
        game_service.next_turn()
        assert game.is_tile_used(0, 0)

    def test_game_reset_workflow(self, sample_questions):
        """Test game reset functionality."""
        game_service = GameLogicService()
        team_names = ["Team Alpha", "Team Beta"]
        
        # Setup and play game
        game = game_service.create_game(team_names, sample_questions)
        game_service.start_game()
        game_service.award_points(50)
        game_service.next_turn()
        game.mark_tile_used(0, 0)
        
        # Verify game state before reset
        assert game.is_started
        assert game.teams[0].score == 50
        assert game.current_team_index == 1
        assert len(game.used_tiles) == 1
        
        # Reset game
        game_service.reset_game()
        
        # Verify everything is reset
        assert not game.is_started
        assert not game.is_finished
        assert game.current_team_index == 0
        assert all(team.score == 0 for team in game.teams)
        assert len(game.used_tiles) == 0

    def test_error_handling_workflow(self, sample_questions):
        """Test error handling in game workflow."""
        game_service = GameLogicService()
        
        # Try operations without creating game
        with pytest.raises(ValidationError):
            game_service.start_game()
        
        with pytest.raises(ValidationError):
            game_service.next_turn()
        
        # Create game but don't start
        game_service.create_game(["Team A", "Team B"], sample_questions)
        
        with pytest.raises(ValidationError):
            game_service.next_turn()


class TestFileOperationWorkflow:
    """Test file operation workflows."""

    def test_question_set_lifecycle(self, file_service, temp_dir):
        """Test complete question set lifecycle."""
        # 1. Create question set data
        question_set = {
            "name": "Integration Test Quiz",
            "description": "A quiz for testing complete workflow",
            "questions": [
                {
                    "question": "What is 1+1?",
                    "answer": "2",
                    "points": 10,
                    "media_id": None
                },
                {
                    "question": "What is the square root of 16?",
                    "answer": "4",
                    "points": 20,
                    "media_id": None
                }
            ]
        }
        
        filename = "integration_test.json"
        
        # 2. Save question set
        file_path = file_service.save_question_set(filename, question_set)
        assert file_path.exists()
        
        # 3. Verify it appears in list
        question_sets = file_service.list_question_sets()
        assert filename in question_sets
        
        # 4. Load and verify content
        loaded_data = file_service.load_question_set(filename)
        assert loaded_data == question_set
        
        # 5. Create backup
        backup_path = file_service.backup_question_set(filename)
        assert backup_path.exists()
        
        # 6. Delete original
        file_service.delete_question_set(filename)
        assert not file_path.exists()
        
        # 7. Verify backup still exists
        assert backup_path.exists()

    def test_question_set_validation_workflow(self, file_service):
        """Test question set validation workflow."""
        # Valid question set
        valid_set = {
            "name": "Valid Quiz",
            "description": "A valid quiz",
            "questions": [
                {
                    "question": "Test question?",
                    "answer": "Test answer",
                    "points": 10,
                    "media_id": None
                }
            ]
        }
        
        # Should validate without error
        file_service.validate_question_set(valid_set)
        
        # Invalid question sets
        invalid_sets = [
            # Missing name
            {
                "description": "Missing name",
                "questions": []
            },
            # Missing questions
            {
                "name": "No questions",
                "description": "Test"
            },
            # Invalid question (empty question text)
            {
                "name": "Invalid question",
                "description": "Test",
                "questions": [
                    {
                        "question": "",
                        "answer": "Test",
                        "points": 10
                    }
                ]
            }
        ]
        
        for invalid_set in invalid_sets:
            with pytest.raises(ValidationError):
                file_service.validate_question_set(invalid_set)


class TestDataPersistenceWorkflow:
    """Test data persistence across operations."""

    def test_game_data_persistence(self, file_service, temp_dir):
        """Test that game data persists correctly through file operations."""
        # Create questions through file service
        question_set_data = {
            "name": "Persistence Test",
            "description": "Testing data persistence",
            "questions": [
                {
                    "question": "What is persistence?",
                    "answer": "Data that survives",
                    "points": 25,
                    "media_id": None
                },
                {
                    "question": "Why test persistence?",
                    "answer": "To ensure reliability",
                    "points": 35,
                    "media_id": None
                }
            ]
        }
        
        filename = "persistence_test.json"
        file_service.save_question_set(filename, question_set_data)
        
        # Load questions and create game
        loaded_data = file_service.load_question_set(filename)
        questions = [
            Question.from_dict(q_data) for q_data in loaded_data["questions"]
        ]
        
        game_service = GameLogicService()
        game = game_service.create_game(["Team A", "Team B"], questions)
        
        # Verify questions were loaded correctly
        assert len(game.questions) == 2
        assert game.questions[0].question == "What is persistence?"
        assert game.questions[0].points == 25
        assert game.questions[1].question == "Why test persistence?"
        assert game.questions[1].points == 35
        
        # Play game and verify scoring
        game_service.start_game()
        game_service.award_points(25)  # First question points
        
        assert game.current_team.score == 25
        
        # Verify total possible score calculation
        assert game.total_possible_score == 60  # 25 + 35

    def test_cross_service_integration(self, temp_dir):
        """Test integration between multiple services."""
        file_service = FileService(str(temp_dir))
        game_service = GameLogicService()
        
        # Create test data through file service
        question_set = {
            "name": "Cross-Service Test",
            "description": "Testing service integration",
            "questions": [
                {
                    "question": "Service integration question 1?",
                    "answer": "Answer 1",
                    "points": 15,
                    "media_id": None
                },
                {
                    "question": "Service integration question 2?",
                    "answer": "Answer 2", 
                    "points": 25,
                    "media_id": None
                },
                {
                    "question": "Service integration question 3?",
                    "answer": "Answer 3",
                    "points": 35,
                    "media_id": None
                }
            ]
        }
        
        # Save through file service
        filename = "cross_service_test.json"
        file_service.save_question_set(filename, question_set)
        
        # Load through file service
        loaded_data = file_service.load_question_set(filename)
        
        # Convert to Question objects
        questions = [Question.from_dict(q) for q in loaded_data["questions"]]
        
        # Create and run game through game service
        game = game_service.create_game(["Alpha", "Beta", "Gamma"], questions)
        game_service.start_game()
        
        # Verify everything works together
        assert len(game.teams) == 3
        assert len(game.questions) == 3
        assert game.total_possible_score == 75  # 15 + 25 + 35
        
        # Play through all teams
        for i, question in enumerate(questions):
            current_team = game.current_team
            game_service.award_points(question.points)
            assert current_team.score == question.points
            
            if i < len(questions) - 1:  # Don't advance after last question
                game_service.next_turn()
        
        # Verify final scores
        assert game.teams[0].score == 15
        assert game.teams[1].score == 25  
        assert game.teams[2].score == 35
        
        # Verify winner
        winner = game.check_win_condition()
        assert winner == game.teams[2]  # Team with 35 points