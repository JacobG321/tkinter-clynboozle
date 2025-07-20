"""
Main menu UI component for ClynBoozle.
"""

import tkinter as tk
from typing import Any, Callable, Optional

from ..config.settings import ColorConfig, WindowConfig, FontConfig
from .base_frame import BaseFrame


class MainMenuFrame(BaseFrame):
    """
    Main menu frame that provides the primary navigation interface.

    Features:
    - Play Game button (navigates to team setup)
    - Manage Question Sets button (opens question set manager)
    - Quit button (exits application)
    - Responsive design with proper scaling
    """

    def __init__(
        self,
        master: tk.Widget,
        app: Any,
        game_service: Optional[Any] = None,
        media_service: Optional[Any] = None,
        **kwargs,
    ) -> None:
        """
        Initialize the main menu frame.

        Args:
            master: Parent widget
            app: Main application instance
            game_service: Game logic service instance
            media_service: Media management service instance
            **kwargs: Additional arguments passed to BaseFrame
        """
        super().__init__(master, app, **kwargs)

        # Store service dependencies
        self.game_service = game_service
        self.media_service = media_service

        # Store callbacks for navigation
        self.on_play_game: Optional[Callable[[], None]] = None
        self.on_manage_questions: Optional[Callable[[], None]] = None
        self.on_quit: Optional[Callable[[], None]] = None

    def build_ui(self) -> None:
        """Build the main menu UI elements."""
        # Main container with proper spacing
        self.menu_frame = tk.Frame(self, bg=ColorConfig.SECONDARY_BG)
        self.menu_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        # Configure grid weights for proper spacing
        self.menu_frame.grid_rowconfigure(0, weight=1)  # Top spacer
        self.menu_frame.grid_rowconfigure(1, weight=0)  # Title
        self.menu_frame.grid_rowconfigure(2, weight=0)  # Play button
        self.menu_frame.grid_rowconfigure(3, weight=0)  # Manage button
        self.menu_frame.grid_rowconfigure(4, weight=0)  # Quit button
        self.menu_frame.grid_rowconfigure(5, weight=1)  # Bottom spacer
        self.menu_frame.grid_columnconfigure(0, weight=1)

        # Title
        self.title_label = self.create_title_label(
            self.menu_frame, "ClynBoozle", color=ColorConfig.GOLD
        )
        self.title_label.grid(row=1, column=0, pady=(20, 40), sticky="s")

        # Play Game button (using Frame+Label approach for Mac color compatibility)
        self.play_frame, self.play_label = self.create_clickable_frame(
            self.menu_frame,
            "Play Game",
            ColorConfig.SUCCESS_COLOR,
            row=2,
            col=0,
            pady=15,
            command=self._handle_play_game,
            width=250,
            height=60,
            font=(FontConfig.FAMILY, FontConfig.BUTTON_SIZE, "bold"),
        )

        # Manage Question Sets button
        self.manage_frame, self.manage_label = self.create_clickable_frame(
            self.menu_frame,
            "Manage Question Sets",
            ColorConfig.PRIMARY_COLOR,
            row=3,
            col=0,
            pady=15,
            command=self._handle_manage_questions,
            width=250,
            height=60,
            font=(FontConfig.FAMILY, FontConfig.BUTTON_SIZE, "bold"),
        )

        # Quit button
        self.quit_frame, self.quit_label = self.create_clickable_frame(
            self.menu_frame,
            "Quit",
            ColorConfig.ERROR_COLOR,
            row=4,
            col=0,
            pady=15,
            command=self._handle_quit,
            width=250,
            height=60,
            font=(FontConfig.FAMILY, FontConfig.BUTTON_SIZE, "bold"),
        )

    def set_play_game_callback(self, callback: Callable[[], None]) -> None:
        """Set the callback for the play game button."""
        self.on_play_game = callback

    def set_manage_questions_callback(self, callback: Callable[[], None]) -> None:
        """Set the callback for the manage questions button."""
        self.on_manage_questions = callback

    def set_quit_callback(self, callback: Callable[[], None]) -> None:
        """Set the callback for the quit button."""
        self.on_quit = callback

    def _handle_play_game(self) -> None:
        """Handle play game button click."""
        if self.on_play_game:
            self.on_play_game()

    def _handle_manage_questions(self) -> None:
        """Handle manage questions button click."""
        if self.on_manage_questions:
            self.on_manage_questions()

    def _handle_quit(self) -> None:
        """Handle quit button click."""
        if self.on_quit:
            self.on_quit()

    def resize_widgets(self) -> None:
        """Resize widgets for the current window size."""
        if not hasattr(self, "play_frame"):
            return

        # Get current window size for scaling
        try:
            window_width = self.winfo_toplevel().winfo_width()
            window_height = self.winfo_toplevel().winfo_height()
        except tk.TclError:
            return

        # Calculate scaling factor based on window size
        width_scale = window_width / WindowConfig.INITIAL_WIDTH
        height_scale = window_height / WindowConfig.INITIAL_HEIGHT
        scale = min(width_scale, height_scale, 2.0)  # Cap at 2x scaling

        # Scale button dimensions
        base_width = self.active_widgets.get("base_button_width", 250)
        base_height = self.active_widgets.get("base_button_height", 60)

        scaled_width = max(int(base_width * scale), 200)  # Minimum 200px wide
        scaled_height = max(int(base_height * scale), 40)  # Minimum 40px tall

        # Update frame sizes
        for frame in [self.play_frame, self.manage_frame, self.quit_frame]:
            if frame and frame.winfo_exists():
                frame.configure(width=scaled_width, height=scaled_height)

        # Scale fonts
        base_title_size = self.active_widgets.get("base_title_font_size", FontConfig.TITLE_SIZE)
        base_button_size = self.active_widgets.get("base_button_font_size", FontConfig.BUTTON_SIZE)

        scaled_title_size = max(int(base_title_size * scale), 20)
        scaled_button_size = max(int(base_button_size * scale), 12)

        # Update title font
        if self.title_label and self.title_label.winfo_exists():
            self.title_label.configure(font=(FontConfig.FAMILY, scaled_title_size, "bold"))

        # Update button fonts
        for label in [self.play_label, self.manage_label, self.quit_label]:
            if label and label.winfo_exists():
                label.configure(font=(FontConfig.FAMILY, scaled_button_size, "bold"))
