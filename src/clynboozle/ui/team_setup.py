"""Team setup UI component for the ClynBoozle quiz game."""

import tkinter as tk
from tkinter import messagebox
from typing import List, Optional, Callable, Any

from .base_frame import BaseFrame
from ..config.settings import ColorConfig, FontConfig


class TeamSetupFrame(BaseFrame):
    """Frame for team setup with dynamic team count and name entry."""

    def __init__(
        self, master: tk.Widget, app: Any, initial_names: Optional[List[str]] = None, **kwargs
    ) -> None:
        # Team configuration - set these BEFORE calling super().__init__()
        self.initial_names = initial_names or []
        initial_count = len(self.initial_names) if self.initial_names else 3
        self.num_teams = tk.IntVar(value=initial_count)
        self.team_entries: List[tk.StringVar] = []

        # Callbacks
        self.on_back: Optional[Callable[[], None]] = None
        self.on_start_game: Optional[Callable[[List[str]], None]] = None
        self.on_change_question_set: Optional[Callable[[], None]] = None

        # UI element references
        self.team_number_buttons: List[tk.Widget] = []
        self.team_entry_widgets: List[dict] = []

        # Now call super().__init__() which will call build_ui()
        super().__init__(master, app, **kwargs)

    def build_ui(self):
        """Build the team setup user interface."""
        # Update active widgets with team setup specific sizes
        self.active_widgets.update(
            {
                "base_team_num_button_size": 40,
                "base_change_set_button_width": 180,
                "base_change_set_button_height": 40,
                "base_bottom_button_width": 150,
                "base_bottom_button_height": 50,
            }
        )

        # Main container with padding
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        main_frame = tk.Frame(self, bg=ColorConfig.SECONDARY_BG)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=1)

        # Title
        title_label = self.create_title_label(main_frame, "Team Setup")
        title_label.grid(row=0, column=0, pady=(0, 20))

        # Number of teams section
        self._create_team_count_section(main_frame, row=1)

        # Team name entries section
        self._create_team_entries_section(main_frame, row=2)

        # Question set section
        self._create_question_set_section(main_frame, row=3)

        # Action buttons
        self._create_action_buttons(main_frame, row=4)

        # Initialize team entries
        self._update_team_entries()

    def _create_team_count_section(self, parent: tk.Widget, row: int):
        """Create the team count selection section."""
        count_frame = tk.Frame(parent, bg=ColorConfig.SECONDARY_BG)
        count_frame.grid(row=row, column=0, sticky="ew", pady=(0, 20))
        count_frame.grid_columnconfigure(1, weight=1)

        # Label
        label = tk.Label(
            count_frame,
            text="Number of Teams:",
            bg=ColorConfig.SECONDARY_BG,
            fg=ColorConfig.PRIMARY_TEXT,
            font=("Arial", FontConfig.LABEL_SIZE),
        )
        label.grid(row=0, column=0, padx=(0, 10), sticky="w")

        # Buttons frame
        buttons_frame = tk.Frame(count_frame, bg=ColorConfig.SECONDARY_BG)
        buttons_frame.grid(row=0, column=1, sticky="w")

        # Create team count buttons (2-6 teams)
        self.team_number_buttons = []
        for i in range(2, 7):
            btn = self.create_styled_button(
                buttons_frame,
                text=str(i),
                command=lambda n=i: self._set_team_count(n),
                width=self.active_widgets["base_team_num_button_size"],
                height=self.active_widgets["base_team_num_button_size"],
            )
            btn.grid(row=0, column=i - 2, padx=2)
            self.team_number_buttons.append(btn)

        # Update button states
        self._update_team_count_buttons()

    def _create_team_entries_section(self, parent: tk.Widget, row: int):
        """Create the team name entry section."""
        # Container for team entries
        self.entries_frame = tk.Frame(parent, bg=ColorConfig.SECONDARY_BG)
        self.entries_frame.grid(row=row, column=0, sticky="ew", pady=(0, 20))
        self.entries_frame.grid_columnconfigure(0, weight=1)

    def _create_question_set_section(self, parent: tk.Widget, row: int):
        """Create the question set display and change button."""
        qs_frame = tk.Frame(parent, bg=ColorConfig.SECONDARY_BG)
        qs_frame.grid(row=row, column=0, sticky="ew", pady=(0, 20))
        qs_frame.grid_columnconfigure(0, weight=1)

        # Get current question set name
        current_set_name = "No question set selected"
        if hasattr(self.app, "question_manager") and self.app.question_manager.current_set:
            current_set_name = self.app.question_manager.current_set.name

        # Question set label
        label = tk.Label(
            qs_frame,
            text=f"Question Set: {current_set_name}",
            bg=ColorConfig.SECONDARY_BG,
            fg=ColorConfig.PRIMARY_TEXT,
            font=("Arial", FontConfig.LABEL_SIZE),
        )
        label.grid(row=0, column=0, pady=(0, 10))

        # Change set button
        btn = self.create_styled_button(
            qs_frame,
            text="Change Question Set",
            command=self._handle_change_question_set,
            width=self.active_widgets["base_change_set_button_width"],
            height=self.active_widgets["base_change_set_button_height"],
        )
        btn.grid(row=1, column=0)

    def _create_action_buttons(self, parent: tk.Widget, row: int):
        """Create the action buttons (Back and Start Game)."""
        button_frame = tk.Frame(parent, bg=ColorConfig.SECONDARY_BG)
        button_frame.grid(row=row, column=0, sticky="ew", pady=(20, 0))
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)

        # Back button
        back_btn = self.create_styled_button(
            button_frame,
            text="Back",
            command=self._handle_back,
            width=self.active_widgets["base_bottom_button_width"],
            height=self.active_widgets["base_bottom_button_height"],
        )
        back_btn.grid(row=0, column=0, padx=(0, 10))

        # Start game button
        start_btn = self.create_styled_button(
            button_frame,
            text="Start Game",
            command=self._handle_start_game,
            width=self.active_widgets["base_bottom_button_width"],
            height=self.active_widgets["base_bottom_button_height"],
        )
        start_btn.grid(row=0, column=1, padx=(10, 0))

    def _set_team_count(self, count: int):
        """Set the number of teams and update UI."""
        self.num_teams.set(count)
        self._update_team_count_buttons()
        self._update_team_entries()

    def _update_team_count_buttons(self):
        """Update the visual state of team count buttons."""
        current_count = self.num_teams.get()
        for i, btn in enumerate(self.team_number_buttons):
            if i + 2 == current_count:
                btn.configure(bg=ColorConfig.PRIMARY_COLOR, fg="white")
            else:
                btn.configure(bg=ColorConfig.SECONDARY_COLOR, fg=ColorConfig.PRIMARY_TEXT)

    def _update_team_entries(self):
        """Update the team name entry widgets based on current team count."""
        # Clear existing entries
        for widget_info in self.team_entry_widgets:
            widget_info["frame"].destroy()
        self.team_entry_widgets.clear()
        self.team_entries.clear()

        # Create new entries
        count = self.num_teams.get()
        for i in range(count):
            # Create StringVar for this team
            team_var = tk.StringVar()
            if i < len(self.initial_names):
                team_var.set(self.initial_names[i])
            else:
                team_var.set(f"Team {i + 1}")
            self.team_entries.append(team_var)

            # Create entry frame
            entry_frame = tk.Frame(self.entries_frame, bg=ColorConfig.SECONDARY_BG)
            entry_frame.grid(row=i, column=0, sticky="ew", pady=2)
            entry_frame.grid_columnconfigure(1, weight=1)

            # Team label
            label = tk.Label(
                entry_frame,
                text=f"Team {i + 1}:",
                bg=ColorConfig.SECONDARY_BG,
                fg=ColorConfig.PRIMARY_TEXT,
                font=("Arial", FontConfig.LABEL_SIZE),
                anchor="w",
            )
            label.grid(row=0, column=0, padx=(0, 10), sticky="w")

            # Team name entry
            entry = tk.Entry(
                entry_frame,
                textvariable=team_var,
                font=("Arial", FontConfig.SMALL_SIZE),
                bg=ColorConfig.SECONDARY_BG,
                fg=ColorConfig.PRIMARY_TEXT,
                insertbackground=ColorConfig.PRIMARY_TEXT,
            )
            entry.grid(row=0, column=1, sticky="ew", padx=(10, 0))

            # Store widget references
            self.team_entry_widgets.append(
                {"frame": entry_frame, "label": label, "entry": entry, "var": team_var}
            )

    def _handle_change_question_set(self):
        """Handle changing the question set."""
        if self.on_change_question_set:
            self.on_change_question_set()

    def _handle_back(self):
        """Handle back button click."""
        if self.on_back:
            self.on_back()

    def _handle_start_game(self):
        """Handle start game button click."""
        # Validate team names
        team_names = []
        for var in self.team_entries:
            name = var.get().strip()
            if not name:
                messagebox.showwarning("Invalid Team Name", "All teams must have names.")
                return
            if name in team_names:
                messagebox.showwarning(
                    "Duplicate Team Name", f"Team name '{name}' is used more than once."
                )
                return
            team_names.append(name)

        if self.on_start_game:
            self.on_start_game(team_names)

    def get_team_names(self) -> List[str]:
        """Get the current list of team names."""
        return [var.get().strip() for var in self.team_entries]

    def set_callbacks(
        self,
        on_back: Optional[Callable[[], None]] = None,
        on_start_game: Optional[Callable[[List[str]], None]] = None,
        on_change_question_set: Optional[Callable[[], None]] = None,
    ):
        """Set callback functions for UI interactions."""
        if on_back is not None:
            self.on_back = on_back
        if on_start_game is not None:
            self.on_start_game = on_start_game
        if on_change_question_set is not None:
            self.on_change_question_set = on_change_question_set
