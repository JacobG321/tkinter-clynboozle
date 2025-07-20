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
        **kwargs
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

        # Play Game button
        self.play_button = self.create_styled_button(
            self.menu_frame,
            "Play Game",
            command=self._handle_play_game,
            bg_color=ColorConfig.SUCCESS_COLOR,
            font=(FontConfig.FAMILY, FontConfig.BUTTON_SIZE, "bold"),
            width=self.active_widgets["base_button_width"],
            height=self.active_widgets["base_button_height"],
        )
        self.play_button.grid(row=2, column=0, pady=15, sticky="")

        # Manage Question Sets button
        self.manage_button = self.create_styled_button(
            self.menu_frame,
            "Manage Question Sets",
            command=self._handle_manage_questions,
            bg_color=ColorConfig.PRIMARY_COLOR,
            font=(FontConfig.FAMILY, FontConfig.BUTTON_SIZE, "bold"),
            width=self.active_widgets["base_button_width"],
            height=self.active_widgets["base_button_height"],
        )
        self.manage_button.grid(row=3, column=0, pady=15, sticky="")

        # Quit button
        self.quit_button = self.create_styled_button(
            self.menu_frame,
            "Quit",
            command=self._handle_quit,
            bg_color=ColorConfig.ERROR_COLOR,
            font=(FontConfig.FAMILY, FontConfig.BUTTON_SIZE, "bold"),
            width=self.active_widgets["base_button_width"],
            height=self.active_widgets["base_button_height"],
        )
        self.quit_button.grid(row=4, column=0, pady=15, sticky="")

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
        if not hasattr(self, "play_button"):
            return

        # Get scaled button dimensions
        if hasattr(self.app, "_get_widget_size"):
            btn_w, btn_h = self.app._get_widget_size(
                self.active_widgets.get("base_button_width", WindowConfig.DEFAULT_BUTTON_WIDTH),
                self.active_widgets.get("base_button_height", WindowConfig.DEFAULT_BUTTON_HEIGHT),
            )
        else:
            # Fallback to configured sizes
            btn_w = self.active_widgets.get("base_button_width", WindowConfig.DEFAULT_BUTTON_WIDTH)
            btn_h = self.active_widgets.get(
                "base_button_height", WindowConfig.DEFAULT_BUTTON_HEIGHT
            )

        # Update button sizes
        for button in [self.play_button, self.manage_button, self.quit_button]:
            if button and button.winfo_exists():
                button.configure(
                    width=btn_w // 10, height=btn_h // 20
                )  # Adjust for character units

        # Update fonts if app provides them
        if hasattr(self.app, "fonts"):
            if self.title_label and self.title_label.winfo_exists():
                self.title_label.configure(font=self.app.fonts.get("title_bold"))

            button_font = self.app.fonts.get("button_bold")
            for button in [self.play_button, self.manage_button, self.quit_button]:
                if button and button.winfo_exists():
                    button.configure(font=button_font)
