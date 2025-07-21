"""Simple game board UI component for testing the navigation flow."""

import tkinter as tk
from tkinter import messagebox
from typing import Dict, List, Optional, Callable, Any

from .base_frame import BaseFrame
from ..config.settings import ColorConfig, FontConfig, WindowConfig


class SimpleGameBoardFrame(BaseFrame):
    """Simple game board frame for testing navigation flow."""

    def __init__(self, master: tk.Widget, app: Any, teams: List[str], 
                 game_service=None, media_service=None, audio_service=None, **kwargs):
        """Initialize the simple game board."""
        # Store services and teams
        self.teams = teams
        self.game_service = game_service
        self.media_service = media_service
        self.audio_service = audio_service

        # Callbacks
        self.on_back: Optional[Callable[[], None]] = None
        self.on_new_game: Optional[Callable[[], None]] = None

        super().__init__(master, app, **kwargs)

    def build_ui(self) -> None:
        """Build the simple game board UI."""
        # Configure main grid
        self.grid_rowconfigure(0, weight=0)  # Header
        self.grid_rowconfigure(1, weight=1)  # Content
        self.grid_rowconfigure(2, weight=0)  # Footer
        self.grid_columnconfigure(0, weight=1)

        self._build_header()
        self._build_content()
        self._build_footer()

    def _build_header(self) -> None:
        """Build the header section."""
        header_frame = tk.Frame(self, bg=ColorConfig.PRIMARY_BG)
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=10)

        # Title
        title_label = self.create_title_label(
            header_frame, "Game Board", color=ColorConfig.GOLD
        )
        title_label.pack(pady=10)

        # Current game info
        if self.game_service and hasattr(self.game_service, 'game'):
            game = self.game_service.game
            if game:
                current_team = game.current_team.name if game.current_team else "Unknown"
                info_text = f"Current Team: {current_team}"
            else:
                info_text = "Game not started"
        else:
            info_text = "Game service not available"

        info_label = tk.Label(
            header_frame,
            text=info_text,
            font=(FontConfig.FAMILY, FontConfig.LABEL_SIZE),
            bg=ColorConfig.PRIMARY_BG,
            fg=ColorConfig.PRIMARY_TEXT,
        )
        info_label.pack(pady=5)

    def _build_content(self) -> None:
        """Build the main content area."""
        content_frame = tk.Frame(self, bg=ColorConfig.SECONDARY_BG, relief=tk.RAISED, bd=2)
        content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)

        # Team scores section
        scores_frame = tk.Frame(content_frame, bg=ColorConfig.SECONDARY_BG)
        scores_frame.pack(fill=tk.X, padx=20, pady=20)

        scores_title = tk.Label(
            scores_frame,
            text="Team Scores:",
            font=(FontConfig.FAMILY, FontConfig.TITLE_SIZE, "bold"),
            bg=ColorConfig.SECONDARY_BG,
            fg=ColorConfig.PRIMARY_TEXT,
        )
        scores_title.pack(pady=(0, 10))

        # Show team scores
        if self.game_service and hasattr(self.game_service, 'game'):
            game = self.game_service.game
            if game and game.teams:
                for team in game.teams:
                    team_frame = tk.Frame(scores_frame, bg=ColorConfig.ENTRY_BG, relief=tk.RIDGE, bd=1)
                    team_frame.pack(fill=tk.X, pady=2)

                    team_label = tk.Label(
                        team_frame,
                        text=f"{team.name}: {team.score} points",
                        font=(FontConfig.FAMILY, FontConfig.LABEL_SIZE),
                        bg=ColorConfig.ENTRY_BG,
                        fg=ColorConfig.PRIMARY_TEXT,
                        anchor="w",
                    )
                    team_label.pack(side=tk.LEFT, padx=10, pady=5)
            else:
                no_game_label = tk.Label(
                    scores_frame,
                    text="No active game",
                    font=(FontConfig.FAMILY, FontConfig.LABEL_SIZE),
                    bg=ColorConfig.SECONDARY_BG,
                    fg=ColorConfig.MUTED_TEXT,
                )
                no_game_label.pack(pady=10)

        # Game actions section
        actions_frame = tk.Frame(content_frame, bg=ColorConfig.SECONDARY_BG)
        actions_frame.pack(fill=tk.X, padx=20, pady=20)

        actions_title = tk.Label(
            actions_frame,
            text="Game Actions:",
            font=(FontConfig.FAMILY, FontConfig.TITLE_SIZE, "bold"),
            bg=ColorConfig.SECONDARY_BG,
            fg=ColorConfig.PRIMARY_TEXT,
        )
        actions_title.pack(pady=(0, 10))

        # Sample question button
        question_container = tk.Frame(actions_frame, bg=ColorConfig.SECONDARY_BG)
        question_container.pack(pady=5)

        self.question_frame, self.question_label = self.create_clickable_frame(
            question_container,
            "Show Sample Question",
            ColorConfig.PRIMARY_COLOR,
            row=0,
            col=0,
            command=self._show_sample_question,
            width=200,
            height=40,
            font=(FontConfig.FAMILY, FontConfig.BUTTON_SIZE, "bold"),
        )

        # Next team button
        next_team_container = tk.Frame(actions_frame, bg=ColorConfig.SECONDARY_BG)
        next_team_container.pack(pady=5)

        self.next_team_frame, self.next_team_label = self.create_clickable_frame(
            next_team_container,
            "Next Team",
            ColorConfig.SUCCESS_COLOR,
            row=0,
            col=0,
            command=self._next_team,
            width=150,
            height=40,
            font=(FontConfig.FAMILY, FontConfig.BUTTON_SIZE, "bold"),
        )

    def _build_footer(self) -> None:
        """Build the footer with action buttons."""
        footer_frame = tk.Frame(self, bg=ColorConfig.PRIMARY_BG)
        footer_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=10)

        # Back to menu button
        back_container = tk.Frame(footer_frame, bg=ColorConfig.PRIMARY_BG)
        back_container.pack(side=tk.LEFT)

        self.back_frame, self.back_label = self.create_clickable_frame(
            back_container,
            "Back to Menu",
            ColorConfig.SECONDARY_COLOR,
            row=0,
            col=0,
            command=self._handle_back,
            width=120,
            height=40,
            font=(FontConfig.FAMILY, FontConfig.BUTTON_SIZE, "bold"),
        )

        # New game button
        new_game_container = tk.Frame(footer_frame, bg=ColorConfig.PRIMARY_BG)
        new_game_container.pack(side=tk.RIGHT)

        self.new_game_frame, self.new_game_label = self.create_clickable_frame(
            new_game_container,
            "New Game",
            ColorConfig.WARNING_COLOR,
            row=0,
            col=0,
            command=self._handle_new_game,
            width=120,
            height=40,
            font=(FontConfig.FAMILY, FontConfig.BUTTON_SIZE, "bold"),
        )

    def set_callbacks(self, on_back=None, on_new_game=None):
        """Set navigation callbacks."""
        if on_back is not None:
            self.on_back = on_back
        if on_new_game is not None:
            self.on_new_game = on_new_game

    def _show_sample_question(self):
        """Show a sample question."""
        if self.game_service and hasattr(self.game_service, 'game'):
            game = self.game_service.game
            if game and game.questions:
                question = game.questions[0]  # Show first question
                messagebox.showinfo(
                    "Sample Question",
                    f"Question: {question.question}\n\nAnswer: {question.answer}\n\nPoints: {question.points}"
                )
            else:
                messagebox.showwarning("No Questions", "No questions available in the current game.")
        else:
            messagebox.showwarning("No Game", "No active game found.")

    def _next_team(self):
        """Move to the next team."""
        if self.game_service and hasattr(self.game_service, 'game'):
            try:
                self.game_service.next_turn()
                # Refresh the display
                self._refresh_display()
                messagebox.showinfo("Next Team", f"It's now {self.game_service.game.current_team.name}'s turn!")
            except Exception as e:
                messagebox.showerror("Error", f"Could not advance to next team: {e}")
        else:
            messagebox.showwarning("No Game", "No active game found.")

    def _refresh_display(self):
        """Refresh the display (rebuild the UI)."""
        # Clear current content and rebuild
        for widget in self.winfo_children():
            widget.destroy()
        self.build_ui()

    def _handle_back(self):
        """Handle back button click."""
        if self.on_back:
            self.on_back()

    def _handle_new_game(self):
        """Handle new game button click."""
        if self.on_new_game:
            self.on_new_game()

    def resize_widgets(self) -> None:
        """Resize widgets for the current window size."""
        # Placeholder for responsive design
        pass