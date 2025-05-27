import tkinter as tk
from tkinter import messagebox, font
from PIL import Image, ImageTk
import io, base64

# Import the QuestionSetManager class from question_set_manager.py
from question_set_manager import QuestionSetManager, QuestionSet

# Default teams (will be customized by the user)
DEFAULT_TEAMS = ["Team 1", "Team 2", "Team 3"]

class MainMenuFrame(tk.Frame):
    """Frame subclass for the Main Menu screen."""

    def __init__(self, master, app):
        super().__init__(master, bg=app.bg_color)
        self.app = app
        self.active_widgets = {}
        self.active_widgets['base_button_width'] = 250
        self.active_widgets['base_button_height'] = 60
        self.active_widgets['base_title_font_size'] = 36
        self.active_widgets['base_button_font_size'] = 18

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.build_ui()

    def build_ui(self):
        """Build UI elements for the main menu."""

        # Main menu container
        menu_frame = tk.Frame(self, bg=self.app.bg_color)
        menu_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        menu_frame.grid_rowconfigure(0, weight=1)  # Title space
        menu_frame.grid_rowconfigure(1, weight=0)  # Play button
        menu_frame.grid_rowconfigure(2, weight=0)  # Manage button
        menu_frame.grid_rowconfigure(3, weight=0)  # Quit button
        menu_frame.grid_rowconfigure(4, weight=1)  # Bottom space
        menu_frame.grid_columnconfigure(0, weight=1)
        self.active_widgets['menu_frame'] = menu_frame

        title_label = tk.Label(
            menu_frame,
            text="ClynBoozle",
            bg=self.app.bg_color,
            fg="#FFD700"  # Gold
        )
        title_label.grid(row=0, column=0, pady=(20, 40), sticky="s")
        self.active_widgets['title_label'] = title_label

        # "Play Game" button
        play_frame, play_label = self._create_clickable_frame(
            menu_frame, "Play Game", "#4CAF50", row=1, col=0, pady=15,
            command=lambda: self.app.show_team_setup()
        )
        self.active_widgets['play_frame'] = play_frame
        self.active_widgets['play_label'] = play_label

        # "Manage Question Sets" button
        manage_frame, manage_label = self._create_clickable_frame(
            menu_frame, "Manage Question Sets", "#2196F3", row=2, col=0, pady=15,
            command=lambda: self.app.question_manager.show_manager()
        )
        self.active_widgets['manage_frame'] = manage_frame
        self.active_widgets['manage_label'] = manage_label

        # "Quit" button
        quit_frame, quit_label = self._create_clickable_frame(
            menu_frame, "Quit", "#F44336", row=3, col=0, pady=15,
            command=lambda: self.app.root.destroy()
        )
        self.active_widgets['quit_frame'] = quit_frame
        self.active_widgets['quit_label'] = quit_label

        self.resize()

    def _create_clickable_frame(self, parent, text, bg, row, col, pady=0, padx=0, command=None):
        """Helper to create a clickable frame + label pattern, to avoid repeated UI code."""
        frame = tk.Frame(parent, bg=bg)
        frame.grid(row=row, column=col, pady=pady, padx=padx)
        frame.pack_propagate(False)

        label = tk.Label(frame, text=text, bg=bg, fg="white")
        label.pack(expand=True, fill=tk.BOTH)

        if command:
            def on_click(_event):
                command()
            frame.bind("<Button-1>", on_click)
            label.bind("<Button-1>", on_click)

        return frame, label

    def resize(self):
        """Resize widgets (except fonts, which are updated globally)."""
        if not self.active_widgets:
            return

        # Scale for button width and height
        btn_w, btn_h = self.app._get_widget_size(
            self.active_widgets.get('base_button_width', 250),
            self.active_widgets.get('base_button_height', 60)
        )

        # Configure the frames
        for frame_key in ['play_frame', 'manage_frame', 'quit_frame']:
            if frame_key in self.active_widgets and self.active_widgets[frame_key].winfo_exists():
                self.active_widgets[frame_key].configure(width=btn_w, height=btn_h)

        # Apply correct font references (the global font object will already be scaled)
        if 'title_label' in self.active_widgets and self.active_widgets['title_label'].winfo_exists():
            self.active_widgets['title_label'].configure(font=self.app.fonts["title_bold"])
        for label_key in ['play_label', 'manage_label', 'quit_label']:
            if label_key in self.active_widgets and self.active_widgets[label_key].winfo_exists():
                self.active_widgets[label_key].configure(font=self.app.fonts["button_bold"])


class TeamSetupFrame(tk.Frame):
    """Frame subclass for the Team Setup screen."""

    def __init__(self, master, app, initial_names: list[str] = None):
        super().__init__(master, bg=app.bg_color)
        self.app = app
        self.initial_names = initial_names or []
        initial_count = len(self.initial_names) if self.initial_names else 3
        self.num_teams = tk.IntVar(value=initial_count)
        
        self.active_widgets = {}
        self.team_entries = []

        # Store base sizes
        self.active_widgets['base_title_font_size'] = 24
        self.active_widgets['base_label_font_size'] = 16
        self.active_widgets['base_small_label_font_size'] = 14
        self.active_widgets['base_button_font_size'] = 16
        self.active_widgets['base_entry_font_size'] = 14
        self.active_widgets['base_team_num_button_size'] = 40
        self.active_widgets['base_change_set_button_width'] = 180
        self.active_widgets['base_change_set_button_height'] = 40
        self.active_widgets['base_bottom_button_width'] = 150
        self.active_widgets['base_bottom_button_height'] = 50

        self._build_layout()

    def _build_layout(self):
        """Build the layout for team setup."""
        # Grid settings
        self.grid_rowconfigure(0, weight=0)  # Title
        self.grid_rowconfigure(1, weight=0)  # Question Set Info
        self.grid_rowconfigure(2, weight=0)  # Change Set Button
        self.grid_rowconfigure(3, weight=0)  # Num Teams Label
        self.grid_rowconfigure(4, weight=0)  # Num Teams Buttons
        self.grid_rowconfigure(5, weight=1)  # Team Entries
        self.grid_rowconfigure(6, weight=0)  # Bottom Buttons
        self.grid_columnconfigure(0, weight=1)

        # Title label
        title_label = tk.Label(self, text="ClynBoozle Setup", bg=self.app.bg_color, fg="#FFD700")
        title_label.grid(row=0, column=0, pady=(10, 20), sticky="n")
        self.active_widgets['title_label'] = title_label

        # Question set name
        current_set_name = self.app.question_manager.current_set.name if self.app.question_manager.current_set else "Unknown"
        qset_label = tk.Label(self, text=f"Question Set: {current_set_name}", bg=self.app.bg_color, fg="#2196F3")
        qset_label.grid(row=1, column=0, pady=(0, 5), sticky="n")
        self.active_widgets['qset_label'] = qset_label

        # Change set button
        change_set_frame = tk.Frame(self, bg="#2196F3")
        change_set_frame.grid(row=2, column=0, pady=(0, 15), sticky="n")
        change_set_frame.pack_propagate(False)
        change_set_label = tk.Label(change_set_frame, text="Change Question Set", bg="#2196F3", fg="white")
        change_set_label.pack(expand=True, fill=tk.BOTH)
        change_set_frame.bind("<Button-1>", lambda _event: self.app.question_manager.show_manager())
        change_set_label.bind("<Button-1>", lambda _event: self.app.question_manager.show_manager())
        self.active_widgets['change_set_frame'] = change_set_frame
        self.active_widgets['change_set_label'] = change_set_label

        # Number of teams
        num_teams_title_label = tk.Label(self, text="Number of Teams:", bg=self.app.bg_color, fg="white")
        num_teams_title_label.grid(row=3, column=0, pady=(10, 5), sticky="n")
        self.active_widgets['num_teams_title_label'] = num_teams_title_label

        num_teams_frame = tk.Frame(self, bg=self.app.bg_color)
        num_teams_frame.grid(row=4, column=0, pady=(0, 15), sticky="n")
        self.active_widgets['num_teams_frame'] = num_teams_frame

        self.active_widgets['team_num_buttons'] = []

        for i in range(2, 7):
            is_selected = (i == self.num_teams.get())
            bg_color   = "#2196F3" if is_selected else self.app.button_color

            btn_frame = tk.Frame(
                num_teams_frame,
                bg=bg_color,
                highlightbackground="black",
                highlightthickness=1
            )
            btn_frame.pack(side=tk.LEFT, padx=10)
            btn_frame.pack_propagate(False)

            lbl = tk.Label(btn_frame, text=str(i),
                           fg="white", bg=bg_color)
            lbl.pack(expand=True, fill=tk.BOTH)

            btn_frame.bind("<Button-1>",
                           lambda _e, num=i: self.update_team_count(num))
            lbl.bind("<Button-1>",
                     lambda _e, num=i: self.update_team_count(num))

            self.active_widgets['team_num_buttons'].append({
                'frame': btn_frame,
                'label': lbl
            })

        # Team entries area
        teams_entry_frame = tk.Frame(self, bg=self.app.bg_color)
        teams_entry_frame.grid(row=5, column=0, pady=10, sticky="nsew", padx=20)
        teams_entry_frame.grid_columnconfigure(0, weight=1)
        self.active_widgets['teams_entry_frame'] = teams_entry_frame

        # Bottom buttons
        button_frame = tk.Frame(self, bg=self.app.bg_color)
        button_frame.grid(row=6, column=0, pady=(10, 10), sticky="sew", padx=20)
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        self.active_widgets['bottom_button_frame'] = button_frame

        back_frame = tk.Frame(button_frame, bg="#F44336")
        back_frame.grid(row=0, column=0, padx=(0, 10), sticky="w")
        back_frame.pack_propagate(False)
        back_label = tk.Label(back_frame, text="Back", bg="#F44336", fg="white")
        back_label.pack(expand=True, fill=tk.BOTH)
        back_frame.bind("<Button-1>", lambda _event: self.app.show_main_menu())
        back_label.bind("<Button-1>", lambda _event: self.app.show_main_menu())
        self.active_widgets['back_frame'] = back_frame
        self.active_widgets['back_label'] = back_label

        start_frame = tk.Frame(button_frame, bg="#4CAF50")
        start_frame.grid(row=0, column=1, padx=(10, 0), sticky="e")
        start_frame.pack_propagate(False)
        start_label = tk.Label(start_frame, text="Start Game", bg="#4CAF50", fg="white")
        start_label.pack(expand=True, fill=tk.BOTH)
        start_frame.bind("<Button-1>", lambda _event: self.finish_setup())
        start_label.bind("<Button-1>", lambda _event: self.finish_setup())
        self.active_widgets['start_frame'] = start_frame
        self.active_widgets['start_label'] = start_label

        # Build the default team entries
        self.create_team_entries()
        self.resize()

    def create_team_entries(self):
        """Create entry fields for team names (pre-filled from initial_names)."""
        frame = self.active_widgets['teams_entry_frame']
        # clear out any old widgets
        for w in frame.winfo_children():
            w.destroy()

        self.team_entries = []
        self.active_widgets['team_entry_widgets'] = []

        # title for the block
        teams_entry_title_label = tk.Label(frame, text="Team Names:", bg=self.app.bg_color, fg="white", font=self.app.fonts["label"])
        teams_entry_title_label.pack(pady=(0,10))
        self.active_widgets['teams_entry_title_label'] = teams_entry_title_label

        # build each team entry
        for i in range(self.num_teams.get()):
            default = (self.initial_names[i]
                    if i < len(self.initial_names)
                    else f"Team {i+1}")

            team_frame = tk.Frame(frame, bg=self.app.bg_color)
            team_frame.pack(pady=5, fill=tk.X, padx=20)

            lbl = tk.Label(team_frame, text=f"Team {i+1}:", bg=self.app.bg_color,
                        fg="white", width=10, anchor="e")
            lbl.pack(side=tk.LEFT, padx=(0,10))

            entry_holder = tk.Frame(team_frame, bg="white",
                                    highlightbackground="gray",
                                    highlightthickness=1)
            entry_holder.pack(side=tk.LEFT, fill=tk.X, expand=True)
            entry_holder.pack_propagate(False)

            var = tk.StringVar(value=default)
            entry = tk.Entry(entry_holder,
                            textvariable=var,
                            border=0, highlightthickness=0,
                            bg="white", fg="black")
            entry.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)

            # store references
            self.team_entries.append(var)
            self.active_widgets['team_entry_widgets'].append({
                'frame': team_frame,
                'label': lbl,
                'entry_frame': entry_holder,
                'entry': entry
            })

        # layout/size them correctly
        self.resize()

        # after everything is drawn, force all entries to black text
        self.after_idle(lambda: [
            wdict['entry'].configure(fg="black")
            for wdict in self.active_widgets['team_entry_widgets']
        ])

        # do a full update so that our idle callback fires immediately
        self.update()


    def update_team_count(self, num):
        """Update the number of teams and refresh the UI."""
        if self.num_teams.get() == num:
            return

        self.num_teams.set(num)

        if 'team_num_buttons' in self.active_widgets:
            buttons = self.active_widgets['team_num_buttons']
            for i, btn_dict in enumerate(buttons):
                target_bg = "#2196F3" if i == num - 2 else self.app.button_color
                btn_dict['frame'].configure(bg=target_bg)
                btn_dict['label'].configure(bg=target_bg)

        self.create_team_entries()
        self.resize()

    def finish_setup(self):
        """Collect team names and start the game."""
        team_names = [entry.get() for entry in self.team_entries]
        for i, name in enumerate(team_names):
            if not name.strip():
                team_names[i] = f"Team {i+1}"
        unique_names = {}
        final_team_names = []
        for name in team_names:
            base_name = name
            count = unique_names.get(base_name, 0)
            while name in final_team_names:
                count += 1
                name = f"{base_name} ({count})"
            unique_names[base_name] = count
            final_team_names.append(name)

        self.app.start_game(final_team_names)

    def resize(self):
        """Resize widgets (except fonts, which are updated globally)."""
        # Scale dimensions
        team_num_btn_size, _ = self.app._get_widget_size(
            self.active_widgets.get('base_team_num_button_size', 40),
            self.active_widgets.get('base_team_num_button_size', 40)
        )
        change_set_w, change_set_h = self.app._get_widget_size(
            self.active_widgets.get('base_change_set_button_width', 180),
            self.active_widgets.get('base_change_set_button_height', 40)
        )
        bottom_btn_w, bottom_btn_h = self.app._get_widget_size(
            self.active_widgets.get('base_bottom_button_width', 150),
            self.active_widgets.get('base_bottom_button_height', 50)
        )

        # Adjust frames
        if 'change_set_frame' in self.active_widgets and self.active_widgets['change_set_frame'].winfo_exists():
            self.active_widgets['change_set_frame'].configure(width=change_set_w, height=change_set_h)

        if 'team_num_buttons' in self.active_widgets:
            for btn_dict in self.active_widgets['team_num_buttons']:
                if btn_dict['frame'].winfo_exists():
                    btn_dict['frame'].configure(width=team_num_btn_size, height=team_num_btn_size)

        if 'back_frame' in self.active_widgets and self.active_widgets['back_frame'].winfo_exists():
            self.active_widgets['back_frame'].configure(width=bottom_btn_w, height=bottom_btn_h)
        if 'start_frame' in self.active_widgets and self.active_widgets['start_frame'].winfo_exists():
            self.active_widgets['start_frame'].configure(width=int(bottom_btn_w * 1.2), height=bottom_btn_h)

        # Apply scaled fonts (they are already scaled globally, so just configure the references)
        if 'title_label' in self.active_widgets and self.active_widgets['title_label'].winfo_exists():
            self.active_widgets['title_label'].configure(font=self.app.fonts["title_bold"])
        if 'qset_label' in self.active_widgets and self.active_widgets['qset_label'].winfo_exists():
            self.active_widgets['qset_label'].configure(font=self.app.fonts["small_label"])
        if 'num_teams_title_label' in self.active_widgets and self.active_widgets['num_teams_title_label'].winfo_exists():
            self.active_widgets['num_teams_title_label'].configure(font=self.app.fonts["label"])

        if 'change_set_label' in self.active_widgets and self.active_widgets['change_set_label'].winfo_exists():
            self.active_widgets['change_set_label'].configure(font=self.app.fonts["small_label_bold"])

        if 'teams_entry_title_label' in self.active_widgets and self.active_widgets['teams_entry_title_label'].winfo_exists():
            self.active_widgets['teams_entry_title_label'].configure(font=self.app.fonts["label"])

        if 'team_entry_widgets' in self.active_widgets:
            for entry_dict in self.active_widgets['team_entry_widgets']:
                # labels
                if entry_dict['label'].winfo_exists():
                    entry_dict['label'].configure(font=self.app.fonts["small_label"])
                # entries
                if entry_dict['entry'].winfo_exists():
                    entry_dict['entry'].configure(font=self.app.fonts["entry"])
                # frame height
                entry_fs = self.app._get_font_size(self.active_widgets.get('base_entry_font_size', 14))
                entry_frame_h = max(20, int(entry_fs * 2.2))
                if entry_dict['entry_frame'].winfo_exists():
                    entry_dict['entry_frame'].configure(height=entry_frame_h)

        if 'back_label' in self.active_widgets and self.active_widgets['back_label'].winfo_exists():
            self.active_widgets['back_label'].configure(font=self.app.fonts["button_bold"])
        if 'start_label' in self.active_widgets and self.active_widgets['start_label'].winfo_exists():
            self.active_widgets['start_label'].configure(font=self.app.fonts["button_bold"])


class GameBoardFrame(tk.Frame):
    """Frame subclass for the main Game Board screen."""

    def __init__(self, master, app, teams):
        super().__init__(master, bg=app.bg_color)
        self.app = app
        self.teams = teams  # dict {team_name: score}
        self.grid_rows = 1
        self.grid_cols = 1
        self.used_tiles = set()
        self.current_team = None
        self.active_widgets = {}
        self.tile_images = {}  # Store tile images by question index

        self._prepare_layout()

    def _prepare_layout(self):
        """Prepare main UI layout for the game board."""
        # Calculate a grid dimension from the question list
        self.app.calculate_grid_dimensions()
        self.grid_rows = self.app.grid_rows
        self.grid_cols = self.app.grid_cols

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.active_widgets['base_score_font_size'] = 14
        self.active_widgets['base_menu_button_font_size'] = 12
        self.active_widgets['base_menu_button_width'] = 100
        self.active_widgets['base_menu_button_height'] = 30
        self.active_widgets['base_tile_font_size'] = 20

        # Score frame
        score_frame = tk.Frame(self, bg=self.app.bg_color)
        score_frame.grid(row=0, column=0, sticky="new", padx=10, pady=(10, 5))
        self.active_widgets['score_frame'] = score_frame

        num_teams = len(self.teams)
        for i in range(num_teams + 1):
            score_frame.grid_columnconfigure(i, weight=1)

        self.active_widgets['score_labels'] = {}
        for i, team in enumerate(self.teams):
            label = tk.Label(score_frame, text=f"{team}: 0", bg=self.app.bg_color, fg="white")
            label.grid(row=0, column=i, padx=5, pady=5, sticky="w")
            self.active_widgets['score_labels'][team] = label

        # Board frame
        board_frame = tk.Frame(self, bg=self.app.bg_color)
        board_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(5, 10))
        self.active_widgets['board_frame'] = board_frame

        for i in range(self.grid_rows):
            board_frame.grid_rowconfigure(i, weight=1)
        for j in range(self.grid_cols):
            board_frame.grid_columnconfigure(j, weight=1)

        self.active_widgets['buttons'] = []
        for i in range(self.grid_rows):
            row_widgets = []
            for j in range(self.grid_cols):
                idx = i * self.grid_cols + j
                if idx >= len(self.app.questions):
                    row_widgets.append(None)
                    continue

                btn_frame = tk.Frame(board_frame, bg=self.app.button_color,
                                    highlightbackground="black",
                                    highlightthickness=1)
                btn_frame.grid(row=i, column=j, padx=5, pady=5, sticky="nsew")
                btn_frame.grid_propagate(False)

                # Check if this question has a tile image
                question = self.app.questions[idx]
                tile_image_data = question.get("tile_image", "")
                points_label = None  # Initialize here
                
                # Create inner frame for image and points
                inner_frame = tk.Frame(btn_frame, bg=self.app.button_color)
                inner_frame.pack(expand=True, fill=tk.BOTH, padx=2, pady=2)
                inner_frame.pack_propagate(False)  # IMPORTANT: Prevent inner frame from expanding
                
                if tile_image_data:
                    # Handle both string and dict formats
                    if isinstance(tile_image_data, dict):
                        image_str = tile_image_data.get("data", "")
                    else:
                        image_str = tile_image_data
                    
                    if image_str:
                        try:
                            # Convert base64 to image
                            img_data = base64.b64decode(image_str)
                            img = Image.open(io.BytesIO(img_data))
                            # Store original image for later resizing
                            self.tile_images[idx] = img
                            
                            # Create container frame for vertical layout
                            content_frame = tk.Frame(inner_frame, bg=self.app.button_color)
                            content_frame.pack(expand=True, fill=tk.BOTH)
                            content_frame.pack_propagate(False)
                            
                            # Create label for image (will be sized in resize method)
                            btn_label = tk.Label(content_frame, bg=self.app.button_color)
                            btn_label.pack(expand=True, fill=tk.BOTH)
                            
                            # Create label for points below image
                            points_label = tk.Label(content_frame, text=str(question["points"]),
                                                bg=self.app.button_color, fg="white")
                            points_label.pack(side=tk.BOTTOM, pady=(0, 2))
                        except Exception as e:
                            print(f"Error loading tile image for question {idx}: {e}")
                            # Fallback to text only
                            btn_label = tk.Label(inner_frame, text=str(question["points"]),
                                                bg=self.app.button_color, fg="white")
                            btn_label.pack(expand=True, fill=tk.BOTH)
                    else:
                        # No image data, use text
                        btn_label = tk.Label(inner_frame, text=str(question["points"]),
                                            bg=self.app.button_color, fg="white")
                        btn_label.pack(expand=True, fill=tk.BOTH)
                else:
                    # No tile image, show points
                    btn_label = tk.Label(inner_frame, text=str(question["points"]),
                                        bg=self.app.button_color, fg="white")
                    btn_label.pack(expand=True, fill=tk.BOTH)

                # Bind click events to all elements
                btn_frame.bind("<Button-1>", lambda _event, i=idx: self.app.reveal_question(i))
                btn_label.bind("<Button-1>", lambda _event, i=idx: self.app.reveal_question(i))
                inner_frame.bind("<Button-1>", lambda _event, i=idx: self.app.reveal_question(i))
                if points_label:
                    points_label.bind("<Button-1>", lambda _event, i=idx: self.app.reveal_question(i))
                # Bind to content_frame if it exists
                if 'content_frame' in locals():
                    content_frame.bind("<Button-1>", lambda _event, i=idx: self.app.reveal_question(i))

                row_widgets.append((btn_frame, btn_label, inner_frame, points_label))
            self.active_widgets['buttons'].append(row_widgets)

        # Menu button
        menu_frame = tk.Frame(score_frame, bg="#2196F3")
        menu_frame.grid(row=0, column=num_teams, padx=5, pady=5, sticky="e")
        menu_frame.grid_propagate(False)
        self.active_widgets['menu_frame'] = menu_frame

        menu_label = tk.Label(menu_frame, text="Menu", bg="#2196F3", fg="white")
        menu_label.pack(expand=True, fill=tk.BOTH)
        self.active_widgets['menu_label'] = menu_label

        menu_frame.bind("<Button-1>", lambda _event: self.app.show_game_menu())
        menu_label.bind("<Button-1>", lambda _event: self.app.show_game_menu())

        if self.teams:
            self.current_team = list(self.teams.keys())[0]
        self.app.next_team(first_turn=True)

    def resize(self):
        """Resize the game board layout (except fonts, which are updated globally)."""
        if not self.active_widgets:
            return

        # Retrieve references
        board_frame = self.active_widgets.get('board_frame', None)
        if not board_frame or not board_frame.winfo_exists():
            return

        # Score frame and board sizing
        score_frame = self.active_widgets.get('score_frame', None)
        score_frame_height = score_frame.winfo_height() if score_frame and score_frame.winfo_exists() else 30
        window_width = self.app.root.winfo_width()
        available_height = self.app.root.winfo_height() - score_frame_height - 20

        board_width = board_frame.winfo_width()
        board_height = available_height

        if self.app.grid_cols <= 0 or self.app.grid_rows <= 0:
            btn_w, btn_h = 50, 30  # fallback size
        else:
            btn_w = max(40, (board_width // self.app.grid_cols) - 10)
            btn_h = max(30, (board_height // self.app.grid_rows) - 10)

        # Scale tile font
        font_scale_factor = btn_h / 80
        tile_size = max(8, int(self.active_widgets.get('base_tile_font_size', 20) * font_scale_factor))
        self.app.fonts["tile"].configure(size=tile_size)

        # Update each button
        if 'buttons' in self.active_widgets:
            for i in range(self.app.grid_rows):
                for j in range(self.app.grid_cols):
                    idx = i * self.app.grid_cols + j
                    if idx < len(self.app.questions) and i < len(self.active_widgets['buttons']):
                        btn_tuple = self.active_widgets['buttons'][i][j]
                        if btn_tuple is None:
                            continue
                        
                        # Handle both old (2-tuple) and new (4-tuple) formats
                        if len(btn_tuple) == 2:
                            btn_frame, btn_label = btn_tuple
                            inner_frame = None
                            points_label = None
                        else:
                            btn_frame, btn_label, inner_frame, points_label = btn_tuple
                        
                        if btn_frame and btn_frame.winfo_exists():
                            btn_frame.configure(width=btn_w, height=btn_h)
                        if btn_label and btn_label.winfo_exists():
                            # Check if we have a tile image for this index
                            if idx in self.tile_images and idx not in self.used_tiles:
                                try:
                                    # Resize image to fit the button
                                    img = self.tile_images[idx].copy()
                                    # Calculate size maintaining aspect ratio
                                    img_w, img_h = img.size
                                    aspect = img_w / img_h
                                    
                                    # Calculate points label height
                                    points_font_size = max(8, int(tile_size * 0.7))
                                    points_height = points_font_size + 8  # Font size + padding
                                    
                                    # Leave space for points text below image
                                    target_w = btn_w - 10
                                    target_h = btn_h - points_height - 10  # Subtract points area and padding
                                    
                                    # Ensure we have positive dimensions
                                    if target_w > 0 and target_h > 0:
                                        if target_w / target_h > aspect:
                                            # Height constrained
                                            new_h = target_h
                                            new_w = int(new_h * aspect)
                                        else:
                                            # Width constrained
                                            new_w = target_w
                                            new_h = int(new_w / aspect)
                                        
                                        # Ensure image doesn't exceed target dimensions
                                        new_w = min(new_w, target_w)
                                        new_h = min(new_h, target_h)
                                        
                                        img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                                        photo = ImageTk.PhotoImage(img)
                                        btn_label.configure(image=photo, text="")
                                        btn_label.image = photo  # Keep a reference
                                    else:
                                        # Tile too small for image, just show points
                                        btn_label.configure(image="", text="")
                                    
                                    # Update points label font
                                    if points_label and points_label.winfo_exists():
                                        points_font = font.Font(family="Arial", size=points_font_size, weight="bold")
                                        points_label.configure(font=points_font)
                                except Exception as e:
                                    print(f"Error resizing tile image: {e}")
                                    # Fallback to text
                                    btn_label.configure(image="", text=str(self.app.questions[idx]["points"]), font=self.app.fonts["tile"])
                                    if points_label:
                                        points_label.pack_forget()
                            else:
                                current_text = btn_label.cget("text")
                                if current_text.isdigit() or current_text == "":
                                    btn_label.configure(font=self.app.fonts["tile"])
                                elif current_text in ["✓", "✗"]:
                                    symbol_font = font.Font(family="Arial",
                                                            size=int(tile_size * 1.2),
                                                            weight="bold")
                                    btn_label.configure(font=symbol_font)

        # Scale score fonts
        score_font_size = self.app._get_font_size(self.active_widgets.get('base_score_font_size', 14))
        self.app.fonts["score"].configure(size=score_font_size)
        self.app.fonts["score_bold"].configure(size=score_font_size)

        if 'score_labels' in self.active_widgets:
            for team, label in self.active_widgets['score_labels'].items():
                if label and label.winfo_exists():
                    if team == self.app.current_team:
                        label.configure(font=self.app.fonts["score_bold"], fg="#FFD700")
                    else:
                        label.configure(font=self.app.fonts["score"], fg="white")

        # Scale menu button
        menu_btn_w, menu_btn_h = self.app._get_widget_size(
            self.active_widgets.get('base_menu_button_width', 100),
            self.active_widgets.get('base_menu_button_height', 30)
        )
        menu_font_size = self.app._get_font_size(self.active_widgets.get('base_menu_button_font_size', 12))
        self.app.fonts["menu_button"].configure(size=menu_font_size)

        if 'menu_frame' in self.active_widgets and self.active_widgets['menu_frame'].winfo_exists():
            self.active_widgets['menu_frame'].configure(width=menu_btn_w, height=menu_btn_h)
        if 'menu_label' in self.active_widgets and self.active_widgets['menu_label'].winfo_exists():
            self.active_widgets['menu_label'].configure(font=self.app.fonts["menu_button"])


class QuizGame:
    def __init__(self, root):
        self.root = root
        self.root.title("ClynBoozle")

        # Colors and sizing
        self.bg_color = "#333333"   # Dark gray background
        self.button_color = "#666666"  # Medium gray for buttons
        self.root.configure(bg=self.bg_color)
        self.root.resizable(True, True)
        self.min_width = 800
        self.min_height = 600
        self.root.minsize(self.min_width, self.min_height)
        self.initial_width = self.min_width
        self.initial_height = self.min_height

        # Team names
        self.saved_team_names = []

        # Question set manager
        self.question_manager = QuestionSetManager(root, self.on_question_set_selected)

        # Current screen tracking
        self.current_view = None
        self.active_frame = None
        self._resizing = False
        self._resize_job = None

        # We'll keep track of questions
        self.questions = []

        # Grid dimension for game board
        self.grid_rows = 1
        self.grid_cols = 1

        # Create dictionary of font objects (avoid re-creating on each resize)
        # Base sizes are used to scale the fonts dynamically
        self.base_sizes = {
            "title_bold": (36, "bold"),
            "button_bold": (18, "bold"),
            "label": (16, "normal"),
            "small_label": (14, "normal"),
            "small_label_bold": (14, "bold"),
            "entry": (14, "normal"),
            "tile": (20, "normal"),
            "score": (14, "normal"),
            "score_bold": (14, "bold"),
            "menu_button": (12, "normal"),
        }
        self.fonts = {}
        for key, (base_size, style) in self.base_sizes.items():
            wt = "normal" if style == "normal" else "bold"
            self.fonts[key] = font.Font(family="Arial", size=base_size, weight=wt)

        # Bind the configure event
        self.root.bind("<Configure>", self.handle_resize)

        # Show main menu
        self.show_main_menu()

        # Update geometry and do an initial resize
        self.root.update_idletasks()
        self.handle_resize(None)

    def on_question_set_selected(self, questions):
        """Callback when a question set is selected in the manager."""

        self.questions = questions
        for q in self.questions:
            qimg = q.get("question_image", "")
            if isinstance(qimg, dict) and qimg.get("data"):
                try:
                    raw = base64.b64decode(qimg["data"])
                    pil = Image.open(io.BytesIO(raw))
                    q["_question_pil"] = pil   # stash the PIL.Image
                except Exception:
                    q["_question_pil"] = None
            else:
                q["_question_pil"] = None


    def clear_root(self):
        """Destroy all children of the root (clears current frame)."""
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_main_menu(self):
        """Display the main menu screen."""
        self.clear_root()
        self.current_view = "main_menu"
        self.root.grid_rowconfigure(0, weight=1);  self.root.grid_columnconfigure(0, weight=1)
        self.active_frame = MainMenuFrame(self.root, self)
        self.active_frame.grid(row=0, column=0, sticky="nsew")

    def show_team_setup(self, saved_names: list[str] = None):
        """Display the team setup screen, optionally pre‑populating with saved_names."""
        # if coming from "Play Again", remember that list
        if saved_names is not None:
            self.saved_team_names = saved_names
        else:
            self.saved_team_names = []

        # ensure questions are loaded
        if not self.questions:
            if self.question_manager.current_set:
                self.questions = self.question_manager.current_set.questions
            else:
                messagebox.showerror("No Questions",
                                     "Please create or select a question set first.")
                return

        self.clear_root()
        self.current_view = "team_setup"
        # allow the single cell to expand
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # hand saved_team_names into the frame
        self.active_frame = TeamSetupFrame(self.root,
                                           self,
                                           initial_names=self.saved_team_names)
        self.active_frame.grid(row=0, column=0, sticky="nsew")

        # force one resize pass so entries get their height immediately
        self.update_font_sizes()
        self.resize_active_frame()

    def start_game(self, teams: list[str]):
        """Start the game with given team names, and stash them for "Play Again"."""
        self.saved_team_names = list(teams)

        self.clear_root()
        self.current_view = "game_board"
        self.teams = {team: 0 for team in teams}
        self.current_team = None

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.active_frame = GameBoardFrame(self.root, self, self.teams)
        self.active_frame.grid(row=0, column=0, sticky="nsew")
        self.resize_active_frame()

    def reveal_question(self, idx):
        """Display a question when a tile is clicked (auto-sizing window to content)."""
        if idx in self.active_frame.used_tiles:
            return

        question_data = self.questions[idx]
        row, col = divmod(idx, self.grid_cols)

        # Defensive check
        if row >= len(self.active_frame.active_widgets['buttons']):
            return
        btn_tuple = self.active_frame.active_widgets['buttons'][row][col]
        if not btn_tuple:
            return

        # Unpack frame & label
        if len(btn_tuple) == 2:
            btn_frame, btn_label = btn_tuple
            inner_frame = points_label = None
        else:
            btn_frame, btn_label, inner_frame, points_label = btn_tuple

        # --- Create question window ---
        question_window = tk.Toplevel(self.root)
        question_window.title("Question")
        question_window.configure(bg=self.bg_color)
        question_window.resizable(True, True)
        question_window.minsize(400, 300)

        content_frame = tk.Frame(question_window, bg=self.bg_color)
        content_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        # --- Image display ---
        original_img = question_data.get("_question_pil", None)
        img_label = None
        if original_img:
            img_frame = tk.Frame(content_frame, bg=self.bg_color)
            img_frame.pack(pady=(0, 10), fill=tk.BOTH, expand=True)

            img_label = tk.Label(img_frame, bg=self.bg_color, cursor="hand2")
            img_label.pack(expand=True)

            hint = tk.Label(
                img_frame,
                text="Click image to enlarge",
                font=("Arial", 10),
                fg="#888888",
                bg=self.bg_color
            )
            hint.pack()

            # Debounced resize logic
            def do_resize():
                if not img_label.winfo_exists():
                    return
                w = img_frame.winfo_width() - 20
                h = img_frame.winfo_height() - 30
                if w < 10 or h < 10:
                    return

                iw, ih = original_img.size
                aspect = iw / ih
                if w / h > aspect:
                    new_h = h
                    new_w = int(h * aspect)
                else:
                    new_w = w
                    new_h = int(w / aspect)

                resized = original_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(resized)
                img_label.configure(image=photo)
                img_label.image = photo

            def schedule_resize(event=None):
                # cancel previous job
                if hasattr(question_window, "_resize_job"):
                    question_window.after_cancel(question_window._resize_job)
                question_window._resize_job = question_window.after(100, do_resize)

            question_window.bind("<Configure>", schedule_resize)
            question_window.update_idletasks()
            do_resize()

            # Enlarged click handler
            def show_enlarged(event=None):
                ew = tk.Toplevel(question_window)
                ew.title("Enlarged Image")
                ew.configure(bg=self.bg_color)
                ew.transient(question_window)

                sw, sh = ew.winfo_screenwidth(), ew.winfo_screenheight()
                iw, ih = original_img.size
                aspect = iw / ih
                max_w, max_h = int(sw * 0.9), int(sh * 0.9)

                if max_w / max_h > aspect:
                    nh = max_h
                    nw = int(max_h * aspect)
                else:
                    nw = max_w
                    nh = int(max_w / aspect)

                enlarged = original_img.resize((nw, nh), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(enlarged)

                lbl = tk.Label(ew, image=photo, bg=self.bg_color)
                lbl.image = photo
                lbl.pack(padx=10, pady=10)

                # center
                ew.update_idletasks()
                x = (sw - ew.winfo_width()) // 2
                y = (sh - ew.winfo_height()) // 2
                ew.geometry(f"+{x}+{y}")

                lbl.bind("<Button-1>", lambda e: ew.destroy())
                ew.bind("<Escape>", lambda e: ew.destroy())

            img_label.bind("<Button-1>", show_enlarged)

        # --- Question text ---
        max_wrap = 500
        qlabel = tk.Label(
            content_frame,
            text=question_data["question"],
            font=("Arial", 16),
            bg=self.bg_color,
            fg="white",
            wraplength=max_wrap,
            justify="center"
        )
        qlabel.pack(pady=10)
        question_window.update_idletasks()

        # --- Answer / scoring handlers ---
        def mark_correct():
            self.active_frame.used_tiles.add(idx)
            self.teams[self.current_team] += question_data["points"]
            self.update_scores()
            btn_frame.configure(bg="#4CAF50")
            btn_label.configure(bg="#4CAF50", text="✓", image="")
            if inner_frame:
                inner_frame.configure(bg="#4CAF50")
                if points_label:
                    points_label.configure(bg="#4CAF50", text="")
            question_window.destroy()
            self.next_team()
            if len(self.active_frame.used_tiles) == len(self.questions):
                self.show_game_over()

        def mark_wrong():
            self.active_frame.used_tiles.add(idx)
            btn_frame.configure(bg="#F44336")
            btn_label.configure(bg="#F44336", text="✗", image="")
            if inner_frame:
                inner_frame.configure(bg="#F44336")
                if points_label:
                    points_label.configure(bg="#F44336", text="")
            question_window.destroy()
            self.next_team()
            if len(self.active_frame.used_tiles) == len(self.questions):
                self.show_game_over()

        # --- Reveal answer button ---
        def reveal_answer():
            if hasattr(question_window, "_answer_revealed"):
                return
            question_window._answer_revealed = True

            ans_lbl = tk.Label(
                content_frame,
                text=f"Answer: {question_data['answer']}",
                font=("Arial", 14, "bold"),
                fg="#2196F3",
                bg=self.bg_color,
                wraplength=max_wrap,
                justify="center"
            )
            ans_lbl.pack(pady=10)
            question_window.update_idletasks()

            action = tk.Frame(content_frame, bg=self.bg_color)
            action.pack(pady=10, fill=tk.X)

            # Correct
            cf = tk.Frame(action, bg="#4CAF50", width=120, height=40)
            cf.pack(side=tk.LEFT, padx=20, expand=True, fill=tk.X)
            cf.pack_propagate(False)
            cl = tk.Label(cf, text="✓ Correct", font=("Arial", 12, "bold"), bg="#4CAF50", fg="white")
            cl.pack(expand=True, fill=tk.BOTH)
            cf.bind("<Button-1>", lambda e: mark_correct())
            cl.bind("<Button-1>", lambda e: mark_correct())

            # Wrong
            wf = tk.Frame(action, bg="#F44336", width=120, height=40)
            wf.pack(side=tk.RIGHT, padx=20, expand=True, fill=tk.X)
            wf.pack_propagate(False)
            wl = tk.Label(wf, text="✗ Wrong", font=("Arial", 12, "bold"), bg="#F44336", fg="white")
            wl.pack(expand=True, fill=tk.BOTH)
            wf.bind("<Button-1>", lambda e: mark_wrong())
            wl.bind("<Button-1>", lambda e: mark_wrong())

            question_window.update_idletasks()
            w, h = max(400, question_window.winfo_reqwidth()), question_window.winfo_reqheight()
            self.center_window(question_window, w, h)
            question_window.minsize(w, h)

        # Reveal-Answer UI
        rf = tk.Frame(content_frame, bg="#2196F3", width=150, height=40)
        rf.pack(pady=10)
        rf.pack_propagate(False)
        rl = tk.Label(rf, text="Reveal Answer", font=("Arial", 12, "bold"), bg="#2196F3", fg="white")
        rl.pack(expand=True, fill=tk.BOTH)
        rf.bind("<Button-1>", lambda e: reveal_answer())
        rl.bind("<Button-1>", lambda e: reveal_answer())

        # Final center
        question_window.update_idletasks()
        w, h = max(400, question_window.winfo_reqwidth()), question_window.winfo_reqheight()
        self.center_window(question_window, w, h)
        question_window.minsize(w, h)


    def show_game_menu(self):
        """Show an in-game menu as a Toplevel."""
        menu_window = tk.Toplevel(self.root)
        menu_window.title("Game Menu")
        menu_window.configure(bg=self.bg_color)
        menu_window.resizable(False, False)
        self.center_window(menu_window, 300, 300)
        menu_window.transient(self.root)
        menu_window.grab_set()

        tk.Label(
            menu_window,
            text="Game Menu",
            font=("Arial", 20, "bold"),
            bg=self.bg_color,
            fg="#FFD700"
        ).pack(pady=(20, 30))

        btn_width, btn_height = 200, 40

        # Continue
        continue_frame = tk.Frame(menu_window, bg="#4CAF50", width=btn_width, height=btn_height)
        continue_frame.pack(pady=10)
        continue_frame.pack_propagate(False)
        continue_label = tk.Label(continue_frame, text="Continue Game", font=("Arial", 14),
                                  bg="#4CAF50", fg="white")
        continue_label.pack(expand=True, fill=tk.BOTH)
        continue_frame.bind("<Button-1>", lambda _event: menu_window.destroy())
        continue_label.bind("<Button-1>", lambda _event: menu_window.destroy())

        # New Game
        new_game_frame = tk.Frame(menu_window, bg="#2196F3", width=btn_width, height=btn_height)
        new_game_frame.pack(pady=10)
        new_game_frame.pack_propagate(False)
        new_game_label = tk.Label(new_game_frame, text="New Game", font=("Arial", 14),
                                  bg="#2196F3", fg="white")
        new_game_label.pack(expand=True, fill=tk.BOTH)

        def start_new_game():
            menu_window.destroy()
            self.show_team_setup()

        new_game_frame.bind("<Button-1>", lambda _event: start_new_game())
        new_game_label.bind("<Button-1>", lambda _event: start_new_game())

        # Change Question Set
        question_set_frame = tk.Frame(menu_window, bg="#FF9800", width=btn_width, height=btn_height)
        question_set_frame.pack(pady=10)
        question_set_frame.pack_propagate(False)
        question_set_label = tk.Label(question_set_frame, text="Change Question Set",
                                      font=("Arial", 14), bg="#FF9800", fg="white")
        question_set_label.pack(expand=True, fill=tk.BOTH)

        def change_question_set():
            menu_window.destroy()
            self.question_manager.show_manager()

        question_set_frame.bind("<Button-1>", lambda _event: change_question_set())
        question_set_label.bind("<Button-1>", lambda _event: change_question_set())

        # Main Menu
        main_menu_frame = tk.Frame(menu_window, bg="#F44336", width=btn_width, height=btn_height)
        main_menu_frame.pack(pady=10)
        main_menu_frame.pack_propagate(False)
        main_menu_label = tk.Label(main_menu_frame, text="Main Menu", font=("Arial", 14),
                                   bg="#F44336", fg="white")
        main_menu_label.pack(expand=True, fill=tk.BOTH)

        def go_to_main_menu():
            if messagebox.askyesno("Return to Main Menu", "Are you sure you want to end the current game?"):
                menu_window.destroy()
                self.show_main_menu()

        main_menu_frame.bind("<Button-1>", lambda _event: go_to_main_menu())
        main_menu_label.bind("<Button-1>", lambda _event: go_to_main_menu())

    def show_game_over(self):
        """Display a 'Game Over' dialog with Play Again + Exit to Main Menu."""
        game_over_window = tk.Toplevel(self.root)
        game_over_window.title("Game Over!")
        game_over_window.configure(bg=self.bg_color)
        game_over_window.resizable(False, False)
        self.center_window(game_over_window, 500, 400)
        game_over_window.transient(self.root)
        game_over_window.grab_set()

        # — title & scores (unchanged) —
        tk.Label(
            game_over_window,
            text="GAME OVER!",
            font=("Arial", 24, "bold"),
            bg=self.bg_color, fg="#FFD700"
        ).pack(pady=(30, 20))

        final_scores = sorted(self.teams.items(), key=lambda x: x[1], reverse=True)
        winner_team, winner_score = final_scores[0]

        tk.Label(
            game_over_window,
            text=f"Winner: {winner_team}",
            font=("Arial", 20, "bold"),
            bg=self.bg_color, fg="#4CAF50"
        ).pack(pady=10)
        tk.Label(
            game_over_window,
            text=f"Score: {winner_score} points",
            font=("Arial", 16),
            bg=self.bg_color, fg="white"
        ).pack(pady=5)

        # — final‑scores list (unchanged) —
        scores_frame = tk.Frame(game_over_window, bg=self.bg_color)
        scores_frame.pack(pady=20, fill=tk.X)
        tk.Label(
            scores_frame,
            text="Final Scores:",
            font=("Arial", 16, "bold"),
            bg=self.bg_color, fg="white"
        ).pack(pady=(10,5))
        for i, (team, score) in enumerate(final_scores):
            color = ("#FFD700", "#C0C0C0", "#CD7F32")[i] if i<3 else "white"
            tk.Label(
                scores_frame,
                text=f"{team}: {score} points",
                font=("Arial", 14),
                bg=self.bg_color, fg=color
            ).pack(pady=3)

        # — buttons row —
        button_frame = tk.Frame(game_over_window, bg=self.bg_color)
        button_frame.pack(pady=20, fill=tk.X)

        # Play Again → back to setup with same names
        play_again = tk.Frame(button_frame, bg="#2196F3", width=150, height=40)
        play_again.pack(side=tk.LEFT, padx=20)
        play_again.pack_propagate(False)
        pa_lbl = tk.Label(play_again, text="Play Again", font=("Arial",14,"bold"),
                          bg="#2196F3", fg="white")
        pa_lbl.pack(expand=True, fill=tk.BOTH)
        play_again.bind("<Button-1>", lambda e: (game_over_window.destroy(),
                                                 self.show_team_setup(self.saved_team_names)))
        pa_lbl.bind(    "<Button-1>", lambda e: (game_over_window.destroy(),
                                                 self.show_team_setup(self.saved_team_names)))

        # Exit to Main Menu
        exit_btn = tk.Frame(button_frame, bg="#F44336", width=150, height=40)
        exit_btn.pack(side=tk.RIGHT, padx=20)
        exit_btn.pack_propagate(False)
        ex_lbl = tk.Label(exit_btn, text="Main Menu", font=("Arial",14,"bold"),
                          bg="#F44336", fg="white")
        ex_lbl.pack(expand=True, fill=tk.BOTH)
        exit_btn.bind("<Button-1>", lambda e: (game_over_window.destroy(),
                                               self.show_main_menu()))
        ex_lbl.bind(    "<Button-1>", lambda e: (game_over_window.destroy(),
                                               self.show_main_menu()))

    def reset_game(self, game_over_window=None):
        """Reset scores and used tiles; keep same set of questions."""
        for team in self.teams:
            self.teams[team] = 0
        self.active_frame.used_tiles.clear()

        if 'buttons' in self.active_frame.active_widgets:
            for i in range(len(self.active_frame.active_widgets['buttons'])):
                for j in range(len(self.active_frame.active_widgets['buttons'][i])):
                    idx = i * self.grid_cols + j
                    if idx < len(self.questions):
                        btn_tuple = self.active_frame.active_widgets['buttons'][i][j]
                        if not btn_tuple:
                            continue
                        
                        # Handle both old and new tuple formats
                        if len(btn_tuple) == 2:
                            btn_frame, btn_label = btn_tuple
                            inner_frame = None
                            points_label = None
                        else:
                            btn_frame, btn_label, inner_frame, points_label = btn_tuple
                        
                        btn_frame.configure(bg=self.button_color)
                        if inner_frame:
                            inner_frame.configure(bg=self.button_color)
                        
                        # Reset button to show either tile image or points
                        if idx in self.active_frame.tile_images:
                            # Trigger resize to redraw the image
                            self.active_frame.resize()
                        else:
                            btn_label.configure(bg=self.button_color, text=str(self.questions[idx]["points"]), image="")
                        
                        # Restore points label if it exists
                        if points_label:
                            points_label.configure(bg=self.button_color, text=str(self.questions[idx]["points"]), fg="white")

        self.update_scores()
        if self.teams:
            self.current_team = list(self.teams.keys())[0]
        self.next_team(first_turn=True)

        if game_over_window:
            game_over_window.destroy()

    def return_to_main_menu(self, window=None):
        """Return to the main menu."""
        if window:
            window.destroy()
        self.show_main_menu()

    def update_scores(self):
        """Refresh score display on the scoreboard."""
        if self.active_frame and hasattr(self.active_frame, "active_widgets"):
            score_labels = self.active_frame.active_widgets.get('score_labels', {})
            for team, score in self.teams.items():
                if team in score_labels and score_labels[team].winfo_exists():
                    score_labels[team].config(text=f"{team}: {score}")

    def next_team(self, first_turn=False):
        """Move to the next team's turn."""
        if not hasattr(self, 'teams') or not self.teams:
            return

        teams = list(self.teams.keys())
        if not hasattr(self, 'current_team') or not self.current_team:
            self.current_team = teams[0]
        elif not first_turn:
            current_index = teams.index(self.current_team)
            self.current_team = teams[(current_index + 1) % len(teams)]

        # Update scoreboard highlight
        if self.active_frame and hasattr(self.active_frame, "active_widgets"):
            score_labels = self.active_frame.active_widgets.get('score_labels', {})
            for team, label in score_labels.items():
                if team == self.current_team:
                    label.configure(font=self.fonts["score_bold"], fg="#FFD700")
                else:
                    label.configure(font=self.fonts["score"], fg="white")

    def calculate_grid_dimensions(self):
        """Calculate a 'best-fit' grid dimension for the question set."""
        if not self.questions:
            self.grid_rows = 1
            self.grid_cols = 1
            return
        num_questions = len(self.questions)
        if num_questions <= 0:
            self.grid_rows = 1
            self.grid_cols = 1
            return
        self.grid_cols = int(num_questions ** 0.5)
        if self.grid_cols == 0:
            self.grid_cols = 1
        self.grid_rows = (num_questions + self.grid_cols - 1) // self.grid_cols
        if self.grid_rows == 0:
            self.grid_rows = 1
        while self.grid_rows * self.grid_cols < num_questions:
            self.grid_cols += 1
            self.grid_rows = (num_questions + self.grid_cols - 1) // self.grid_cols
            if self.grid_rows == 0:
                self.grid_rows = 1

    def handle_resize(self, event):
        """Delay the resize to avoid flooding events."""
        if event is not None and event.widget is not self.root:
            return
        if self._resize_job:
            self.root.after_cancel(self._resize_job)
        self._resize_job = self.root.after(50, self._do_resize)

    def _do_resize(self):
        self.update_font_sizes()
        self.resize_active_frame()

    def resize_active_frame(self):
        """Triggers the current frame's 'resize' method if present."""
        if self.active_frame and hasattr(self.active_frame, "resize"):
            self.active_frame.resize()

    def _get_scale_factor(self):
        """Calculates a scaling factor based on current vs initial window size."""
        current_width = self.root.winfo_width()
        current_height = self.root.winfo_height()
        scale_w = current_width / self.initial_width
        scale_h = current_height / self.initial_height
        return min(scale_w, scale_h)

    def _get_font_size(self, base_size):
        """Calculate scaled font size with a minimum of 8."""
        scale = self._get_scale_factor()
        return max(8, int(base_size * scale))

    def _get_widget_size(self, base_width, base_height):
        """Calculate scaled widget dimensions with a minimum of 10."""
        scale = self._get_scale_factor()
        return max(10, int(base_width * scale)), max(10, int(base_height * scale))

    def update_font_sizes(self):
        """Update all stored Font objects based on the current scaling factor."""
        scale = self._get_scale_factor()
        for key, (base_size, style) in self.base_sizes.items():
            new_size = max(8, int(base_size * scale))
            wt = "normal" if style == "normal" else "bold"
            self.fonts[key].configure(size=new_size, weight=wt)

    def center_window(self, window, width, height):
        """Centers a window on top of the main root window."""
        parent_x = self.root.winfo_rootx()
        parent_y = self.root.winfo_rooty()
        parent_width = self.root.winfo_width()
        parent_height = self.root.winfo_height()

        x = parent_x + (parent_width - width) // 2
        y = parent_y + (parent_height - height) // 2
        window.geometry(f"{width}x{height}+{x}+{y}")

        window.update_idletasks()
        x = parent_x + (parent_width - window.winfo_width()) // 2
        y = parent_y + (parent_height - window.winfo_height()) // 2
        window.geometry(f"+{x}+{y}")


if __name__ == "__main__":
    root = tk.Tk()
    app = QuizGame(root)
    root.mainloop()