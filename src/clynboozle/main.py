"""
Main application entry point for ClynBoozle.

This module provides the clean application startup with dependency injection,
error handling, and proper initialization sequence.
"""

import tkinter as tk
from tkinter import messagebox
import sys
import traceback
import logging
from typing import Optional, List

from .utils.logging_config import LoggingConfig, get_logger
from .config.settings import WindowConfig, GameConfig
from .services.game_logic import GameLogicService
from .services.media_service import MediaService
from .services.audio_service import AudioService
from .services.file_service import FileService
from .services.question_set_service import QuestionSetService
from .ui.main_menu import MainMenuFrame
from .ui.team_setup import TeamSetupFrame
from .ui.question_manager import QuestionManagerFrame
from .ui.question_set_selector import QuestionSetSelectorFrame
from .ui.simple_game_board import SimpleGameBoardFrame


class ClynBoozleApp:
    """
    Main application class with dependency injection and clean initialization.

    This class coordinates all services and UI components, providing a clean
    entry point for the application with proper error handling and logging.
    """

    def __init__(self, debug: bool = False):
        """
        Initialize the ClynBoozle application.

        Args:
            debug: Enable debug logging and development features
        """
        self.debug = debug
        self.logger: Optional[logging.Logger] = None
        self.root: Optional[tk.Tk] = None

        # Services
        self.game_service: Optional[GameLogicService] = None
        self.media_service: Optional[MediaService] = None
        self.audio_service: Optional[AudioService] = None
        self.file_service: Optional[FileService] = None
        self.question_set_service: Optional[QuestionSetService] = None

        # UI State
        self.current_frame: Optional[tk.Frame] = None
        self.is_running = False
        
        # Game state for navigation
        self.selected_teams: Optional[List[str]] = None
        self.selected_question_set: Optional[str] = None

    def run(self) -> int:
        """
        Run the application.

        Returns:
            Exit code (0 for success, non-zero for error)
        """
        try:
            self._setup_logging()
            self.logger = get_logger(__name__)
            self.logger.info("Starting ClynBoozle application")

            self._setup_services()
            self._setup_ui()
            self._start_main_loop()

            return 0

        except KeyboardInterrupt:
            if self.logger:
                self.logger.info("Application interrupted by user")
            return 0

        except Exception as e:
            if self.logger:
                self.logger.error(f"Application error: {e}")
                self.logger.debug(f"Traceback: {traceback.format_exc()}")
            else:
                print(f"Fatal error during startup: {e}")
                traceback.print_exc()
            return 1

        finally:
            self._cleanup()

    def _setup_logging(self) -> None:
        """Setup application logging."""
        if self.debug:
            LoggingConfig.setup_dev_logging()
        else:
            LoggingConfig.setup_production_logging()

    def _setup_services(self) -> None:
        """Initialize all application services."""
        if not self.logger:
            self.logger = get_logger(__name__)
        self.logger.info("Initializing services...")

        # Initialize core services with proper base directory
        import os

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        self.file_service = FileService(base_dir)
        self.media_service = MediaService(base_dir)
        self.audio_service = AudioService()
        self.game_service = GameLogicService()
        self.question_set_service = QuestionSetService(self.file_service)

        self.logger.info("All services initialized successfully")

    def _setup_ui(self) -> None:
        """Setup the main UI window and components."""
        self.logger.info("Initializing UI...")

        self.root = tk.Tk()
        self.root.title("ClynBoozle")
        self.root.configure(bg="#333333")

        # Configure window
        self.root.geometry(f"{WindowConfig.INITIAL_WIDTH}x{WindowConfig.INITIAL_HEIGHT}")
        self.root.minsize(WindowConfig.MIN_WIDTH, WindowConfig.MIN_HEIGHT)
        self.root.resizable(True, True)

        # Setup window grid
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

        # Start with main menu
        self._show_main_menu()

        self.logger.info("UI initialized successfully")

    def _show_main_menu(self) -> None:
        """Show the main menu."""
        if self.current_frame:
            self.current_frame.destroy()

        # Create main menu with service dependencies
        self.current_frame = MainMenuFrame(
            self.root,
            self,  # Pass app instance for navigation
            game_service=self.game_service,
            media_service=self.media_service,
        )

        # Set up navigation callbacks
        self.current_frame.set_play_game_callback(self._handle_play_game)
        self.current_frame.set_manage_questions_callback(self._handle_manage_questions)
        self.current_frame.set_quit_callback(self._handle_quit)

        self.current_frame.grid(row=0, column=0, sticky="nsew")

    def _show_question_manager(self) -> None:
        """Show the question manager screen."""
        if self.current_frame:
            self.current_frame.destroy()

        # Create question manager frame
        self.current_frame = QuestionManagerFrame(
            self.root,
            self,
            question_set_service=self.question_set_service,
        )

        # Set up navigation callbacks (no "use set" button for management screen)
        self.current_frame.set_callbacks(
            on_back=self._handle_back_to_main_menu,
        )

        self.current_frame.grid(row=0, column=0, sticky="nsew")

    def _show_team_setup(self) -> None:
        if self.current_frame:
            self.current_frame.destroy()

        # Create team setup frame
        self.current_frame = TeamSetupFrame(
            self.root,
            self,
        )

        # Set up navigation callbacks
        self.current_frame.set_callbacks(
            on_back=self._handle_back_to_main_menu,
            on_start_game=self._handle_start_new_game,
            on_change_question_set=self._handle_select_question_set,
        )

        self.current_frame.grid(row=0, column=0, sticky="nsew")

    def _show_question_set_selector(self) -> None:
        """Show the question set selector screen for pre-game setup."""
        if self.current_frame:
            self.current_frame.destroy()

        # Create question set selector frame
        self.current_frame = QuestionSetSelectorFrame(
            self.root,
            self,
            question_set_service=self.question_set_service,
        )

        # Set up navigation callbacks
        self.current_frame.set_callbacks(
            on_back=self._handle_back_to_team_setup,
            on_select_set=self._handle_question_set_selected,
        )

        self.current_frame.grid(row=0, column=0, sticky="nsew")

    def _show_game_board(self) -> None:
        """Show the game board screen."""
        if self.current_frame:
            self.current_frame.destroy()

        # Ensure we have teams and a question set
        if not self.selected_teams or not self.selected_question_set:
            self.logger.error("Cannot start game without teams and question set")
            self._show_main_menu()
            return

        # Get the question set
        question_set = self.question_set_service.get_question_set(self.selected_question_set)
        if not question_set:
            self.logger.error(f"Question set not found: {self.selected_question_set}")
            self._show_main_menu()
            return

        # Create game using the game service
        try:
            game = self.game_service.create_game(self.selected_teams, question_set.questions)
            self.game_service.start_game()

            # Create game board frame
            self.current_frame = SimpleGameBoardFrame(
                self.root,
                self,
                teams=self.selected_teams,
                game_service=self.game_service,
                media_service=self.media_service,
                audio_service=self.audio_service,
            )

            # Set up navigation callbacks
            self.current_frame.set_callbacks(
                on_back=self._handle_back_to_main_menu,
                on_new_game=self._handle_new_game,
            )

            self.current_frame.grid(row=0, column=0, sticky="nsew")

        except Exception as e:
            self.logger.error(f"Failed to start game: {e}")
            messagebox.showerror("Game Start Error", f"Failed to start game: {e}")
            self._show_main_menu()

    def _start_main_loop(self) -> None:
        """Start the Tkinter main event loop."""
        self.logger.info("Starting main event loop")
        self.is_running = True

        try:
            self.root.mainloop()
        except Exception as e:
            self.logger.error(f"Error in main loop: {e}")
            raise
        finally:
            self.is_running = False

    def _on_closing(self) -> None:
        """Handle application closing."""
        self.logger.info("Application closing...")
        self.is_running = False
        if self.root:
            self.root.quit()

    def _cleanup(self) -> None:
        """Cleanup resources before exit."""
        if self.logger:
            self.logger.info("Cleaning up resources...")

        # Cleanup audio service
        if self.audio_service:
            try:
                self.audio_service.cleanup()
            except Exception as e:
                if self.logger:
                    self.logger.warning(f"Error cleaning up audio service: {e}")

        # Cleanup media service
        if self.media_service:
            try:
                # Clear any cached images/resources
                if hasattr(self.media_service, "clear_cache"):
                    self.media_service.clear_cache()
            except Exception as e:
                if self.logger:
                    self.logger.warning(f"Error cleaning up media service: {e}")

        if self.logger:
            self.logger.info("Cleanup completed")

    # Navigation callback handlers
    def _handle_play_game(self) -> None:
        """Handle play game button click."""
        if self.logger:
            self.logger.info("Play game button clicked - navigating to team setup")
        self._show_team_setup()

    def _handle_manage_questions(self) -> None:
        """Handle manage questions button click."""
        if self.logger:
            self.logger.info("Manage questions button clicked - navigating to question manager")
        self._show_question_manager()

    def _handle_quit(self) -> None:
        """Handle quit button click."""
        if self.logger:
            self.logger.info("Quit button clicked")
        self._on_closing()

    def _handle_back_to_main_menu(self) -> None:
        """Handle back to main menu navigation."""
        if self.logger:
            self.logger.info("Navigating back to main menu")
        self._show_main_menu()

    def _handle_start_new_game(self, team_names: List[str]) -> None:
        """Handle starting a new game with the provided team names."""
        if self.logger:
            self.logger.info(f"Starting new game with teams: {team_names}")

        # Store team names for game creation
        self.selected_teams = team_names

        # Check if we have a question set selected
        current_set = self.question_set_service.get_current_question_set()
        if current_set:
            # We have a question set, proceed directly to game
            set_name = None
            # Find the set name
            for name, qs in self.question_set_service.get_all_question_sets().items():
                if qs == current_set:
                    set_name = name
                    break
            if set_name:
                self.selected_question_set = set_name
                self._show_game_board()
                return

        # No question set selected, go to selector
        self._show_question_set_selector()

    def _handle_select_question_set(self) -> None:
        """Handle request to select/change question set from team setup."""
        if self.logger:
            self.logger.info("Navigate to question set selector from team setup")
        self._show_question_set_selector()

    def _handle_back_to_team_setup(self) -> None:
        """Handle back to team setup navigation."""
        if self.logger:
            self.logger.info("Navigating back to team setup")
        self._show_team_setup()

    def _handle_question_set_selected(self, set_name: str) -> None:
        """Handle question set selection from selector."""
        if self.logger:
            self.logger.info(f"Question set selected: {set_name}")

        # Store the selected question set
        self.selected_question_set = set_name

        # If we have teams selected, start the game, otherwise go to team setup
        if self.selected_teams:
            self._show_game_board()
        else:
            self._show_team_setup()

    def _handle_new_game(self) -> None:
        """Handle starting a completely new game."""
        if self.logger:
            self.logger.info("Starting new game from game board")
        
        # Clear selections and go to team setup
        self.selected_teams = None
        self.selected_question_set = None
        self._show_team_setup()

    # Navigation methods for UI components
    def show_team_setup(self, team_names: Optional[list] = None) -> None:
        """
        Navigate to team setup screen.

        Args:
            team_names: Optional list of team names to pre-populate
        """
        # This will be implemented as UI components are refactored
        if self.logger:
            self.logger.info("Navigating to team setup")
        # TODO: Implement with proper UI component

    def start_game(self, team_names: list) -> None:
        """
        Start a new game with given teams.

        Args:
            team_names: List of team names for the new game
        """
        if self.logger:
            self.logger.info(f"Starting game with teams: {team_names}")
        # TODO: Implement with proper UI component
        # Use team_names parameter when implementing game start logic

    def show_question_manager(self) -> None:
        """Show the question set manager."""
        if self.logger:
            self.logger.info("Showing question manager")
        # TODO: Implement with proper UI component


def main(debug: bool = False) -> int:
    """
    Main entry point for the application.

    Args:
        debug: Enable debug mode

    Returns:
        Exit code
    """
    app = ClynBoozleApp(debug=debug)
    return app.run()


def dev_main() -> int:
    """Entry point for development with debug logging."""
    return main(debug=True)


if __name__ == "__main__":
    # Check for debug flag
    debug_mode = "--debug" in sys.argv or "-d" in sys.argv
    exit_code = main(debug=debug_mode)
    sys.exit(exit_code)
