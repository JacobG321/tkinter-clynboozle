"""Game board UI component for the ClynBoozle quiz game."""

import tkinter as tk
from tkinter import font
from typing import Dict, List, Tuple, Optional, Any
from PIL import Image, ImageTk

from .base_frame import BaseFrame


class GameBoardFrame(BaseFrame):
    """Frame subclass for the main Game Board screen."""

    def __init__(self, master, app, teams: Dict[str, int], **kwargs):
        self.teams = teams  # dict {team_name: score}
        self.grid_rows = 1
        self.grid_cols = 1
        self.used_tiles = set()
        self.current_team = None
        self.tile_images = {}  # Store tile images by question index

        # UI element references
        self.team_number_buttons: List[dict] = []
        self.team_entry_widgets: List[dict] = []

        super().__init__(master, app, **kwargs)

    def build_ui(self):
        """Build the game board user interface."""
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

        self.active_widgets["base_score_font_size"] = 14
        self.active_widgets["base_menu_button_font_size"] = 12
        self.active_widgets["base_menu_button_width"] = 100
        self.active_widgets["base_menu_button_height"] = 30
        self.active_widgets["base_tile_font_size"] = 20

        # Score frame
        score_frame = tk.Frame(self, bg=self.app.bg_color)
        score_frame.grid(row=0, column=0, sticky="new", padx=10, pady=(10, 5))
        self.active_widgets["score_frame"] = score_frame

        num_teams = len(self.teams)
        for i in range(num_teams + 1):
            score_frame.grid_columnconfigure(i, weight=1)

        self.active_widgets["score_labels"] = {}
        for i, team in enumerate(self.teams):
            label = tk.Label(score_frame, text=f"{team}: 0", bg=self.app.bg_color, fg="white")
            label.grid(row=0, column=i, padx=5, pady=5, sticky="w")
            self.active_widgets["score_labels"][team] = label

        # Board frame
        board_frame = tk.Frame(self, bg=self.app.bg_color)
        board_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(5, 10))
        self.active_widgets["board_frame"] = board_frame

        for i in range(self.grid_rows):
            board_frame.grid_rowconfigure(i, weight=1)
        for j in range(self.grid_cols):
            board_frame.grid_columnconfigure(j, weight=1)

        self.active_widgets["buttons"] = []
        for i in range(self.grid_rows):
            row_widgets = []
            for j in range(self.grid_cols):
                idx = i * self.grid_cols + j
                if idx >= len(self.app.questions):
                    row_widgets.append(None)
                    continue

                btn_frame = tk.Frame(
                    board_frame,
                    bg=self.app.button_color,
                    highlightbackground="black",
                    highlightthickness=1,
                )
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
                    image_loaded = False

                    # Handle media reference system only
                    if (
                        isinstance(tile_image_data, dict)
                        and tile_image_data.get("type") == "media_reference"
                    ):
                        try:
                            media_id = tile_image_data.get("media_id")
                            if media_id:
                                # Get the tile-sized image path
                                image_path = self.app.media_manager.get_image_path(media_id, "tile")
                                if image_path:
                                    img = Image.open(image_path)
                                    # Store original image for later resizing
                                    self.tile_images[idx] = img
                                    image_loaded = True
                        except Exception as e:
                            print(f"Error loading tile image for question {idx}: {e}")

                    if image_loaded:
                        # Create container frame for vertical layout
                        content_frame = tk.Frame(inner_frame, bg=self.app.button_color)
                        content_frame.pack(expand=True, fill=tk.BOTH)
                        content_frame.pack_propagate(False)

                        # Create label for image (will be sized in resize method)
                        btn_label = tk.Label(content_frame, bg=self.app.button_color)
                        btn_label.pack(expand=True, fill=tk.BOTH)

                        # Create label for points below image
                        points_label = tk.Label(
                            content_frame,
                            text=str(question["points"]),
                            bg=self.app.button_color,
                            fg="white",
                        )
                        points_label.pack(side=tk.BOTTOM, pady=(0, 2))
                    else:
                        # Fallback to text only
                        btn_label = tk.Label(
                            inner_frame,
                            text=str(question["points"]),
                            bg=self.app.button_color,
                            fg="white",
                        )
                        btn_label.pack(expand=True, fill=tk.BOTH)
                else:
                    # No tile image, show points
                    btn_label = tk.Label(
                        inner_frame,
                        text=str(question["points"]),
                        bg=self.app.button_color,
                        fg="white",
                    )
                    btn_label.pack(expand=True, fill=tk.BOTH)

                # Bind click events to all elements
                btn_frame.bind("<Button-1>", lambda _event, i=idx: self.app.reveal_question(i))
                btn_label.bind("<Button-1>", lambda _event, i=idx: self.app.reveal_question(i))
                inner_frame.bind("<Button-1>", lambda _event, i=idx: self.app.reveal_question(i))
                if points_label:
                    points_label.bind(
                        "<Button-1>", lambda _event, i=idx: self.app.reveal_question(i)
                    )
                # Bind to content_frame if it exists
                if "content_frame" in locals():
                    content_frame.bind(
                        "<Button-1>", lambda _event, i=idx: self.app.reveal_question(i)
                    )

                row_widgets.append((btn_frame, btn_label, inner_frame, points_label))
            self.active_widgets["buttons"].append(row_widgets)

        # Menu button
        menu_frame = tk.Frame(score_frame, bg="#2196F3")
        menu_frame.grid(row=0, column=num_teams, padx=5, pady=5, sticky="e")
        menu_frame.grid_propagate(False)
        self.active_widgets["menu_frame"] = menu_frame

        menu_label = tk.Label(menu_frame, text="Menu", bg="#2196F3", fg="white")
        menu_label.pack(expand=True, fill=tk.BOTH)
        self.active_widgets["menu_label"] = menu_label

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
        board_frame = self.active_widgets.get("board_frame", None)
        if not board_frame or not board_frame.winfo_exists():
            return

        # Score frame and board sizing
        score_frame = self.active_widgets.get("score_frame", None)
        score_frame_height = (
            score_frame.winfo_height() if score_frame and score_frame.winfo_exists() else 30
        )
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
        tile_size = max(
            8, int(self.active_widgets.get("base_tile_font_size", 20) * font_scale_factor)
        )
        self.app.fonts["tile"].configure(size=tile_size)

        # Update each button
        if "buttons" in self.active_widgets:
            for i in range(self.app.grid_rows):
                for j in range(self.app.grid_cols):
                    idx = i * self.app.grid_cols + j
                    if idx < len(self.app.questions) and i < len(self.active_widgets["buttons"]):
                        btn_tuple = self.active_widgets["buttons"][i][j]
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
                                    target_h = (
                                        btn_h - points_height - 10
                                    )  # Subtract points area and padding

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
                                        points_font = font.Font(
                                            family="Arial", size=points_font_size, weight="bold"
                                        )
                                        points_label.configure(font=points_font)
                                except Exception as e:
                                    print(f"Error resizing tile image: {e}")
                                    # Fallback to text
                                    btn_label.configure(
                                        image="",
                                        text=str(self.app.questions[idx]["points"]),
                                        font=self.app.fonts["tile"],
                                    )
                                    if points_label:
                                        points_label.pack_forget()
                            else:
                                current_text = btn_label.cget("text")
                                if current_text.isdigit() or current_text == "":
                                    btn_label.configure(font=self.app.fonts["tile"])
                                elif current_text in ["✓", "✗"]:
                                    symbol_font = font.Font(
                                        family="Arial", size=int(tile_size * 1.2), weight="bold"
                                    )
                                    btn_label.configure(font=symbol_font)

        # Scale score fonts
        score_font_size = self.app._get_font_size(
            self.active_widgets.get("base_score_font_size", 14)
        )
        self.app.fonts["score"].configure(size=score_font_size)
        self.app.fonts["score_bold"].configure(size=score_font_size)

        if "score_labels" in self.active_widgets:
            for team, label in self.active_widgets["score_labels"].items():
                if label and label.winfo_exists():
                    if team == self.app.current_team:
                        label.configure(font=self.app.fonts["score_bold"], fg="#FFD700")
                    else:
                        label.configure(font=self.app.fonts["score"], fg="white")

        # Scale menu button
        menu_btn_w, menu_btn_h = self.app._get_widget_size(
            self.active_widgets.get("base_menu_button_width", 100),
            self.active_widgets.get("base_menu_button_height", 30),
        )
        menu_font_size = self.app._get_font_size(
            self.active_widgets.get("base_menu_button_font_size", 12)
        )
        self.app.fonts["menu_button"].configure(size=menu_font_size)

        if "menu_frame" in self.active_widgets and self.active_widgets["menu_frame"].winfo_exists():
            self.active_widgets["menu_frame"].configure(width=menu_btn_w, height=menu_btn_h)
        if "menu_label" in self.active_widgets and self.active_widgets["menu_label"].winfo_exists():
            self.active_widgets["menu_label"].configure(font=self.app.fonts["menu_button"])
