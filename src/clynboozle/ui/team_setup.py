"""Team setup UI component for the ClynBoozle quiz game."""

import tkinter as tk
from tkinter import messagebox
from typing import List, Optional, Callable, Any

from .base_frame import BaseFrame
from ..config.settings import ColorConfig, FontConfig, WindowConfig


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
        # Update active widgets with team setup specific sizes (in character units)
        self.active_widgets.update(
            {
                "base_team_num_button_size": 3,  # 3 characters wide for team count buttons
                "base_change_set_button_width": 20,  # 20 characters wide
                "base_change_set_button_height": 2,  # 2 lines tall
                "base_bottom_button_width": 15,  # 15 characters wide
                "base_bottom_button_height": 2,  # 2 lines tall
            }
        )

        # Main container with better centering
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Main content frame - centered with max width
        main_frame = tk.Frame(self, bg=ColorConfig.SECONDARY_BG)
        main_frame.grid(
            row=0, column=0, sticky="", padx=40, pady=30
        )  # Center instead of sticky="nsew"
        main_frame.grid_columnconfigure(0, weight=1)

        # Add some spacing between sections
        for i in range(5):
            main_frame.grid_rowconfigure(i, weight=0, minsize=20)

        # Title
        self.title_label = self.create_title_label(main_frame, "Team Setup")
        self.title_label.grid(row=0, column=0, pady=(0, 20))

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

        # Force UI update to ensure entry fields are visible
        self.update_idletasks()

    def resize_widgets(self) -> None:
        """Resize widgets for the current window size."""
        if not hasattr(self, "team_number_frames"):
            return

        # Get current window size for scaling
        try:
            window_width = self.winfo_toplevel().winfo_width()
            window_height = self.winfo_toplevel().winfo_height()
        except tk.TclError:
            return

        # Calculate scaling factor
        width_scale = window_width / WindowConfig.INITIAL_WIDTH
        height_scale = window_height / WindowConfig.INITIAL_HEIGHT
        scale = min(width_scale, height_scale, 2.0)

        # Scale team count buttons
        base_btn_size = 40
        scaled_btn_size = max(int(base_btn_size * scale), 30)

        for frame in self.team_number_frames:
            if frame and frame.winfo_exists():
                frame.configure(width=scaled_btn_size, height=scaled_btn_size)

        # Scale main action buttons
        base_width, base_height = 150, 50
        scaled_width = max(int(base_width * scale), 120)
        scaled_height = max(int(base_height * scale), 35)

        if hasattr(self, "back_frame") and self.back_frame.winfo_exists():
            self.back_frame.configure(width=scaled_width, height=scaled_height)
        if hasattr(self, "start_frame") and self.start_frame.winfo_exists():
            self.start_frame.configure(width=scaled_width, height=scaled_height)
        if hasattr(self, "change_set_frame") and self.change_set_frame.winfo_exists():
            change_width = max(int(200 * scale), 150)
            change_height = max(int(40 * scale), 30)
            self.change_set_frame.configure(width=change_width, height=change_height)

        # Scale fonts
        base_button_size = FontConfig.BUTTON_SIZE
        base_label_size = FontConfig.LABEL_SIZE
        base_title_size = FontConfig.TITLE_SIZE

        scaled_button_font = max(int(base_button_size * scale), 10)
        scaled_label_font = max(int(base_label_size * scale), 10)
        scaled_title_font = max(int(base_title_size * scale), 16)

        # Update button fonts
        for label in self.team_number_labels:
            if label and label.winfo_exists():
                label.configure(font=(FontConfig.FAMILY, scaled_button_font, "bold"))

        if hasattr(self, "back_label") and self.back_label.winfo_exists():
            self.back_label.configure(font=(FontConfig.FAMILY, scaled_button_font, "bold"))
        if hasattr(self, "start_label") and self.start_label.winfo_exists():
            self.start_label.configure(font=(FontConfig.FAMILY, scaled_button_font, "bold"))
        if hasattr(self, "change_set_label") and self.change_set_label.winfo_exists():
            self.change_set_label.configure(font=(FontConfig.FAMILY, scaled_button_font, "bold"))

        # Update static text labels
        if hasattr(self, "teams_count_label") and self.teams_count_label.winfo_exists():
            self.teams_count_label.configure(font=(FontConfig.FAMILY, scaled_label_font, "normal"))
        if hasattr(self, "question_set_label") and self.question_set_label.winfo_exists():
            self.question_set_label.configure(font=(FontConfig.FAMILY, scaled_label_font, "normal"))

        # Update team name labels
        for entry_info in self.team_entry_widgets:
            if "label" in entry_info and entry_info["label"].winfo_exists():
                entry_info["label"].configure(font=(FontConfig.FAMILY, scaled_label_font, "normal"))
            # Also scale the entry field fonts
            if "entry" in entry_info and entry_info["entry"].winfo_exists():
                entry_info["entry"].configure(font=(FontConfig.FAMILY, scaled_label_font, "normal"))

        # Scale title if it exists
        if hasattr(self, "title_label") and self.title_label.winfo_exists():
            self.title_label.configure(font=(FontConfig.FAMILY, scaled_title_font, "bold"))

    def _create_team_count_section(self, parent: tk.Widget, row: int):
        """Create the team count selection section."""
        count_frame = tk.Frame(parent, bg=ColorConfig.SECONDARY_BG)
        count_frame.grid(row=row, column=0, sticky="ew", pady=(0, 20))
        count_frame.grid_columnconfigure(1, weight=1)

        # Label
        self.teams_count_label = tk.Label(
            count_frame,
            text="Number of Teams:",
            bg=ColorConfig.SECONDARY_BG,
            fg=ColorConfig.PRIMARY_TEXT,
            font=("Arial", FontConfig.LABEL_SIZE),
        )
        self.teams_count_label.grid(row=0, column=0, padx=(0, 10), sticky="w")

        # Buttons frame
        buttons_frame = tk.Frame(count_frame, bg=ColorConfig.SECONDARY_BG)
        buttons_frame.grid(row=0, column=1, sticky="w")

        # Create team count buttons (2-6 teams) using Frame+Label for Mac compatibility
        self.team_number_buttons = []
        self.team_number_frames = []
        self.team_number_labels = []

        for i in range(2, 7):
            frame, label = self.create_clickable_frame(
                buttons_frame,
                text=str(i),
                bg_color=ColorConfig.SECONDARY_COLOR,
                row=0,
                col=i - 2,
                padx=2,
                command=lambda n=i: self._set_team_count(n),
                width=40,
                height=40,
                font=(FontConfig.FAMILY, FontConfig.BUTTON_SIZE, "bold"),
            )
            self.team_number_buttons.append((frame, label))  # Store both for compatibility
            self.team_number_frames.append(frame)
            self.team_number_labels.append(label)

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
        self.question_set_label = tk.Label(
            qs_frame,
            text=f"Question Set: {current_set_name}",
            bg=ColorConfig.SECONDARY_BG,
            fg=ColorConfig.PRIMARY_TEXT,
            font=("Arial", FontConfig.LABEL_SIZE),
        )
        self.question_set_label.grid(row=0, column=0, pady=(0, 10))

        # Change set button (using Frame+Label for Mac color compatibility)
        self.change_set_frame, self.change_set_label = self.create_clickable_frame(
            qs_frame,
            "Change Question Set",
            ColorConfig.PRIMARY_COLOR,
            row=1,
            col=0,
            command=self._handle_change_question_set,
            width=200,
            height=40,
            font=(FontConfig.FAMILY, FontConfig.SMALL_SIZE, "bold"),
        )

    def _create_action_buttons(self, parent: tk.Widget, row: int):
        """Create the action buttons (Back and Start Game)."""
        button_frame = tk.Frame(parent, bg=ColorConfig.SECONDARY_BG)
        button_frame.grid(row=row, column=0, sticky="ew", pady=(20, 0))
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)

        # Back button (using Frame+Label for Mac color compatibility)
        self.back_frame, self.back_label = self.create_clickable_frame(
            button_frame,
            "Back",
            ColorConfig.SECONDARY_COLOR,
            row=0,
            col=0,
            padx=(0, 10),
            command=self._handle_back,
            width=150,
            height=50,
            font=(FontConfig.FAMILY, FontConfig.BUTTON_SIZE, "bold"),
        )

        # Start game button (using Frame+Label for Mac color compatibility)
        self.start_frame, self.start_label = self.create_clickable_frame(
            button_frame,
            "Start Game",
            ColorConfig.SUCCESS_COLOR,
            row=0,
            col=1,
            padx=(10, 0),
            command=self._handle_start_game,
            width=150,
            height=50,
            font=(FontConfig.FAMILY, FontConfig.BUTTON_SIZE, "bold"),
        )

    def _set_team_count(self, count: int):
        """Set the number of teams and update UI."""
        self.num_teams.set(count)
        self._update_team_count_buttons()
        self._update_team_entries()
        
        # Force widget resizing after creating new team entries
        self.update_idletasks()
        self.resize_widgets()

    def _update_team_count_buttons(self):
        """Update the visual state of team count buttons."""
        current_count = self.num_teams.get()
        for i, (frame, label) in enumerate(self.team_number_buttons):
            if i + 2 == current_count:
                # Selected button - blue background
                frame.configure(bg=ColorConfig.PRIMARY_COLOR)
                label.configure(bg=ColorConfig.PRIMARY_COLOR, fg="white")
            else:
                # Unselected button - gray background
                frame.configure(bg=ColorConfig.SECONDARY_COLOR)
                label.configure(bg=ColorConfig.SECONDARY_COLOR, fg=ColorConfig.PRIMARY_TEXT)

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
                bg="white",  # Use white background for better visibility
                fg="black",  # Use black text for contrast
                insertbackground="black",  # Black cursor
                highlightthickness=2,
                highlightcolor=ColorConfig.PRIMARY_COLOR,  # Blue border when focused
                highlightbackground=ColorConfig.ENTRY_BORDER,  # Gray border when not focused
                relief="solid",
                bd=1,
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
