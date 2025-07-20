"""Base UI frame class for ClynBoozle application."""

from __future__ import annotations
from typing import Any, Callable, Dict, Optional, Tuple
import tkinter as tk
from abc import ABC, abstractmethod

from ..config.settings import WindowConfig, ColorConfig, FontConfig


class BaseFrame(tk.Frame, ABC):
    """Base class for all main UI frames in the application.

    Provides common functionality like resize handling, styling,
    shared widget creation methods, and consistent event binding patterns.
    """

    def __init__(self, master: tk.Widget, app: Any, **kwargs) -> None:
        """Initialize the base frame.

        Args:
            master: Parent widget
            app: Main application instance
            **kwargs: Additional arguments passed to tk.Frame
        """
        # Set default background color
        kwargs.setdefault("bg", ColorConfig.SECONDARY_BG)
        super().__init__(master, **kwargs)

        self.app = app
        self.active_widgets: Dict[str, Any] = {}

        # Base sizing configuration
        self.active_widgets.update(
            {
                "base_button_width": WindowConfig.DEFAULT_BUTTON_WIDTH,
                "base_button_height": WindowConfig.DEFAULT_BUTTON_HEIGHT,
                "base_title_font_size": FontConfig.TITLE_SIZE,
                "base_button_font_size": FontConfig.BUTTON_SIZE,
            }
        )

        # Configure grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Build the UI (implemented by subclasses)
        self.build_ui()

        # Bind resize events automatically
        self.bind_resize_events()

    @abstractmethod
    def build_ui(self) -> None:
        """Build the UI elements for this frame.

        Must be implemented by subclasses.
        """
        pass

    def create_clickable_frame(
        self,
        parent: tk.Widget,
        text: str,
        bg_color: str,
        row: int,
        col: int,
        pady: int = 0,
        padx: int = 0,
        command: Optional[Callable[[], None]] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        font: Optional[Tuple[str, int, str]] = None,
    ) -> Tuple[tk.Frame, tk.Label]:
        """Create a clickable frame with label pattern.

        This is a common UI pattern used throughout the application.

        Args:
            parent: Parent widget
            text: Text to display on the button
            bg_color: Background color
            row: Grid row position
            col: Grid column position
            pady: Vertical padding
            padx: Horizontal padding
            command: Function to call when clicked
            width: Fixed width (optional)
            height: Fixed height (optional)

        Returns:
            Tuple of (frame, label) widgets
        """
        frame = tk.Frame(parent, bg=bg_color)
        frame.grid(row=row, column=col, pady=pady, padx=padx)

        # Set fixed size if provided
        if width or height:
            frame.pack_propagate(False)
            if width:
                frame.configure(width=width)
            if height:
                frame.configure(height=height)

        # Create label with optional font styling
        label_font = font or (FontConfig.FAMILY, FontConfig.BUTTON_SIZE, "bold")
        label = tk.Label(
            frame, text=text, bg=bg_color, fg=ColorConfig.PRIMARY_TEXT, font=label_font
        )
        label.pack(expand=True, fill=tk.BOTH)

        # Bind click events if command provided
        if command:

            def on_click(event: tk.Event) -> None:
                command()

            frame.bind("<Button-1>", on_click)
            label.bind("<Button-1>", on_click)

            # Add hover effects
            def on_enter(event: tk.Event) -> None:
                frame.configure(relief="raised", bd=2)

            def on_leave(event: tk.Event) -> None:
                frame.configure(relief="flat", bd=0)

            frame.bind("<Enter>", on_enter)
            frame.bind("<Leave>", on_leave)
            label.bind("<Enter>", on_enter)
            label.bind("<Leave>", on_leave)

        return frame, label

    def create_styled_button(
        self,
        parent: tk.Widget,
        text: str,
        command: Optional[Callable[[], None]] = None,
        bg_color: str = ColorConfig.SECONDARY_COLOR,
        fg_color: str = ColorConfig.PRIMARY_TEXT,
        **kwargs,
    ) -> tk.Button:
        """Create a consistently styled button.

        Args:
            parent: Parent widget
            text: Button text
            command: Function to call when clicked
            bg_color: Background color
            fg_color: Foreground (text) color
            **kwargs: Additional button options

        Returns:
            Configured tk.Button widget
        """
        button = tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg_color,
            fg=fg_color,
            relief="flat",
            bd=0,
            highlightthickness=0,  # Remove focus border
            activebackground=bg_color,  # Keep same color when clicked
            activeforeground=fg_color,  # Keep same text color when clicked
            **kwargs,
        )

        # Force color update (needed on some systems)
        button.update_idletasks()

        # Add hover effects
        def on_enter(event: tk.Event) -> None:
            # Darken the background color slightly for hover effect
            button.configure(relief="raised", bd=1)

        def on_leave(event: tk.Event) -> None:
            button.configure(relief="flat", bd=0)

        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)

        return button

    def create_title_label(
        self, parent: tk.Widget, text: str, color: str = ColorConfig.GOLD
    ) -> tk.Label:
        """Create a consistently styled title label.

        Args:
            parent: Parent widget
            text: Title text
            color: Text color

        Returns:
            Configured tk.Label widget
        """
        return tk.Label(
            parent,
            text=text,
            bg=ColorConfig.SECONDARY_BG,
            fg=color,
            font=("Arial", self.active_widgets["base_title_font_size"], "bold"),
        )

    def create_section_frame(
        self,
        parent: tk.Widget,
        row: int,
        col: int,
        rowspan: int = 1,
        colspan: int = 1,
        sticky: str = "nsew",
        **kwargs,
    ) -> tk.Frame:
        """Create a section frame with consistent styling.

        Args:
            parent: Parent widget
            row: Grid row
            col: Grid column
            rowspan: Number of rows to span
            colspan: Number of columns to span
            sticky: Grid sticky option
            **kwargs: Additional frame options

        Returns:
            Configured tk.Frame widget
        """
        kwargs.setdefault("bg", ColorConfig.SECONDARY_BG)

        frame = tk.Frame(parent, **kwargs)
        frame.grid(
            row=row,
            column=col,
            rowspan=rowspan,
            columnspan=colspan,
            sticky=sticky,
            padx=WindowConfig.DEFAULT_PADDING,
            pady=WindowConfig.DEFAULT_PADDING,
        )

        return frame

    def resize(self) -> None:
        """Handle resize events for responsive UI.

        Updates widget sizes based on current window dimensions.
        Should be called when the window is resized.
        """
        if not self.active_widgets:
            return

        # Get current window size
        try:
            window_width = self.winfo_width()
            window_height = self.winfo_height()
        except tk.TclError:
            # Widget not yet mapped
            return

        if window_width <= 1 or window_height <= 1:
            return

        # Calculate scaling factors
        width_scale = window_width / WindowConfig.INITIAL_WIDTH
        height_scale = window_height / WindowConfig.INITIAL_HEIGHT
        scale = min(width_scale, height_scale, 2.0)  # Cap scaling at 2x

        # Update button dimensions
        new_button_width = max(
            int(self.active_widgets["base_button_width"] * scale), WindowConfig.MIN_BUTTON_WIDTH
        )
        new_button_height = max(
            int(self.active_widgets["base_button_height"] * scale), WindowConfig.MIN_BUTTON_HEIGHT
        )

        # Apply sizing to widgets (subclasses can override this)
        self._apply_sizing(new_button_width, new_button_height, scale)

    def _apply_sizing(self, width: int, height: int, scale: float) -> None:
        """Apply calculated sizing to widgets.

        Can be overridden by subclasses for custom sizing logic.

        Args:
            width: New button width
            height: New button height
            scale: Overall scale factor
        """
        # Update stored dimensions
        self.active_widgets["current_button_width"] = width
        self.active_widgets["current_button_height"] = height
        self.active_widgets["current_scale"] = scale

        # Apply to clickable frames
        for key, widget in self.active_widgets.items():
            if key.endswith("_frame") and isinstance(widget, tk.Frame):
                try:
                    widget.configure(width=width, height=height)
                except tk.TclError:
                    pass  # Widget may not support sizing

        # Call subclass-specific resize method if available
        if hasattr(self, "resize_widgets"):
            self.resize_widgets()

    def bind_resize_events(self) -> None:
        """Bind resize events to this frame.

        Should be called after the frame is properly displayed.
        """

        def on_configure(event: tk.Event) -> None:
            if event.widget == self:
                self.resize()

        self.bind("<Configure>", on_configure)

    def cleanup(self) -> None:
        """Cleanup resources when frame is destroyed.

        Can be overridden by subclasses for custom cleanup.
        """
        self.active_widgets.clear()
