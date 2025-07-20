"""
Base dialog class for consistent modal dialog behavior across the application.
"""

import tkinter as tk
from abc import ABC, abstractmethod
from typing import Optional, Callable, Any

from ..config.settings import WindowConfig, ColorConfig, FontConfig


class BaseDialog(tk.Toplevel, ABC):
    """
    Base class for all modal dialogs in the application.
    
    Provides:
    - Consistent modal behavior
    - Standard dialog styling
    - Automatic centering
    - Standard button layouts
    - Result handling
    - Window management
    """
    
    def __init__(
        self,
        parent: tk.Widget,
        title: str = "",
        modal: bool = True,
        resizable: bool = False,
        width: int = 400,
        height: int = 300,
        min_width: int = 300,
        min_height: int = 200
    ):
        """
        Initialize the base dialog.
        
        Args:
            parent: Parent window
            title: Dialog title
            modal: Whether dialog should be modal
            resizable: Whether dialog can be resized
            width: Initial width
            height: Initial height
            min_width: Minimum width
            min_height: Minimum height
        """
        super().__init__(parent)
        
        self.parent = parent
        self.result = None
        self._result_callback: Optional[Callable[[Any], None]] = None
        
        # Configure window
        self.title(title)
        self.configure(bg=ColorConfig.SECONDARY_BG)
        
        # Set size and constraints
        self.geometry(f"{width}x{height}")
        if not resizable:
            self.resizable(False, False)
        else:
            self.minsize(min_width, min_height)
        
        # Make modal if requested
        if modal:
            self.transient(parent)
            self.grab_set()
        
        # Center the dialog
        self._center_dialog()
        
        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # Create UI
        self._create_ui()
        
        # Focus the dialog
        self.focus_set()
    
    def _center_dialog(self) -> None:
        """Center the dialog on the parent window."""
        self.update_idletasks()
        
        # Get parent window position and size
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        # Get dialog size
        dialog_width = self.winfo_reqwidth()
        dialog_height = self.winfo_reqheight()
        
        # Calculate center position
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        # Ensure dialog is on screen
        x = max(0, x)
        y = max(0, y)
        
        self.geometry(f"+{x}+{y}")
    
    def _create_ui(self) -> None:
        """Create the dialog UI structure."""
        # Main container
        self.main_frame = tk.Frame(
            self,
            bg=ColorConfig.SECONDARY_BG,
            padx=WindowConfig.PADDING_LARGE,
            pady=WindowConfig.PADDING_LARGE
        )
        self.main_frame.pack(fill="both", expand=True)
        
        # Content area (to be filled by subclasses)
        self.content_frame = tk.Frame(
            self.main_frame,
            bg=ColorConfig.SECONDARY_BG
        )
        self.content_frame.pack(fill="both", expand=True, pady=(0, WindowConfig.PADDING_LARGE))
        
        # Button frame
        self.button_frame = tk.Frame(
            self.main_frame,
            bg=ColorConfig.SECONDARY_BG
        )
        self.button_frame.pack(fill="x")
        
        # Build the specific content
        self.build_content()
        
        # Build the buttons
        self.build_buttons()
    
    @abstractmethod
    def build_content(self) -> None:
        """Build the main content of the dialog. Must be implemented by subclasses."""
        pass
    
    def build_buttons(self) -> None:
        """
        Build the button area. Can be overridden by subclasses.
        Default implementation creates OK and Cancel buttons.
        """
        # Cancel button
        cancel_button = self.create_button(
            self.button_frame,
            "Cancel",
            self.cancel,
            style="secondary"
        )
        cancel_button.pack(side="right", padx=(WindowConfig.PADDING_SMALL, 0))
        
        # OK button
        ok_button = self.create_button(
            self.button_frame,
            "OK",
            self.ok,
            style="primary"
        )
        ok_button.pack(side="right", padx=(0, WindowConfig.PADDING_SMALL))
        
        # Make OK the default button
        self.bind('<Return>', lambda e: self.ok())
        self.bind('<Escape>', lambda e: self.cancel())
    
    def create_button(
        self,
        parent: tk.Widget,
        text: str,
        command: Callable[[], None],
        style: str = "primary"
    ) -> tk.Button:
        """
        Create a styled button.
        
        Args:
            parent: Parent widget
            text: Button text
            command: Button command
            style: Button style ("primary" or "secondary")
        
        Returns:
            The created button
        """
        if style == "primary":
            bg_color = ColorConfig.PRIMARY_COLOR
            fg_color = ColorConfig.PRIMARY_TEXT
            active_bg = ColorConfig.HOVER_COLOR
        else:
            bg_color = ColorConfig.SECONDARY_BG
            fg_color = ColorConfig.PRIMARY_TEXT
            active_bg = ColorConfig.HOVER_COLOR
        
        button = tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg_color,
            fg=fg_color,
            activebackground=active_bg,
            activeforeground=ColorConfig.PRIMARY_TEXT,
            font=(FontConfig.FAMILY, FontConfig.BUTTON_SIZE, "bold"),
            padx=WindowConfig.PADDING_MEDIUM,
            pady=WindowConfig.PADDING_SMALL,
            relief="flat",
            borderwidth=1,
            cursor="hand2",
            width=WindowConfig.DEFAULT_BUTTON_WIDTH,
            height=WindowConfig.DEFAULT_BUTTON_HEIGHT
        )
        
        # Add hover effects
        def on_enter(event):
            button.configure(bg=active_bg)
        
        def on_leave(event):
            button.configure(bg=bg_color)
        
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
        
        return button
    
    def create_label(
        self,
        parent: tk.Widget,
        text: str,
        font_size: str = "label",
        bold: bool = False,
        color: str = None
    ) -> tk.Label:
        """
        Create a styled label.
        
        Args:
            parent: Parent widget
            text: Label text
            font_size: Font size key from FontConfig
            bold: Whether text should be bold
            color: Text color (defaults to PRIMARY_TEXT)
        
        Returns:
            The created label
        """
        if color is None:
            color = ColorConfig.PRIMARY_TEXT
        
        # Get font info from config
        if font_size in FontConfig.BASE_SIZES:
            size, weight = FontConfig.BASE_SIZES[font_size]
        else:
            size = getattr(FontConfig, f"{font_size.upper()}_SIZE", FontConfig.LABEL_SIZE)
            weight = "bold" if bold else "normal"
        
        if bold:
            weight = "bold"
        
        label = tk.Label(
            parent,
            text=text,
            bg=ColorConfig.SECONDARY_BG,
            fg=color,
            font=(FontConfig.FAMILY, size, weight)
        )
        
        return label
    
    def create_entry(
        self,
        parent: tk.Widget,
        placeholder: str = "",
        width: int = 30
    ) -> tk.Entry:
        """
        Create a styled entry widget.
        
        Args:
            parent: Parent widget
            placeholder: Placeholder text
            width: Entry width
        
        Returns:
            The created entry
        """
        entry = tk.Entry(
            parent,
            bg=ColorConfig.ENTRY_BG,
            fg=ColorConfig.PRIMARY_TEXT,
            font=(FontConfig.FAMILY, FontConfig.BASE_SIZES["entry"][0]),
            relief="solid",
            borderwidth=1,
            width=width,
            insertbackground=ColorConfig.PRIMARY_TEXT
        )
        
        # Add placeholder functionality if provided
        if placeholder:
            self._add_placeholder(entry, placeholder)
        
        return entry
    
    def _add_placeholder(self, entry: tk.Entry, placeholder: str) -> None:
        """Add placeholder functionality to an entry widget."""
        entry.placeholder = placeholder
        entry.placeholder_color = ColorConfig.SECONDARY_TEXT
        entry.normal_color = ColorConfig.PRIMARY_TEXT
        
        def on_focus_in(event):
            if entry.get() == placeholder:
                entry.delete(0, tk.END)
                entry.configure(fg=entry.normal_color)
        
        def on_focus_out(event):
            if not entry.get():
                entry.insert(0, placeholder)
                entry.configure(fg=entry.placeholder_color)
        
        # Set initial placeholder
        entry.insert(0, placeholder)
        entry.configure(fg=entry.placeholder_color)
        
        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)
    
    def ok(self) -> None:
        """Handle OK button press. Can be overridden by subclasses."""
        self.result = self.get_result()
        self._call_result_callback()
        self.destroy()
    
    def cancel(self) -> None:
        """Handle Cancel button press. Can be overridden by subclasses."""
        self.result = None
        self._call_result_callback()
        self.destroy()
    
    def get_result(self) -> Any:
        """
        Get the dialog result. Should be overridden by subclasses.
        
        Returns:
            The dialog result (None by default)
        """
        return None
    
    def set_result_callback(self, callback: Callable[[Any], None]) -> None:
        """
        Set a callback to be called when the dialog is closed with a result.
        
        Args:
            callback: Function to call with the result
        """
        self._result_callback = callback
    
    def _call_result_callback(self) -> None:
        """Call the result callback if set."""
        if self._result_callback:
            self._result_callback(self.result)
    
    def _on_close(self) -> None:
        """Handle window close event."""
        self.cancel()
    
    def show_modal(self) -> Any:
        """
        Show the dialog modally and return the result.
        
        Returns:
            The dialog result
        """
        self.wait_window()
        return self.result


class MessageDialog(BaseDialog):
    """Simple message dialog with customizable buttons."""
    
    def __init__(
        self,
        parent: tk.Widget,
        title: str,
        message: str,
        buttons: list = None,
        icon: str = None
    ):
        """
        Initialize message dialog.
        
        Args:
            parent: Parent window
            title: Dialog title
            message: Message to display
            buttons: List of button texts (defaults to ["OK"])
            icon: Icon type (not implemented yet)
        """
        self.message = message
        self.buttons = buttons or ["OK"]
        self.icon = icon
        self.clicked_button = None
        
        # Calculate size based on message length
        width = min(600, max(300, len(message) * 8))
        height = min(400, max(150, message.count('\n') * 30 + 150))
        
        super().__init__(parent, title, width=width, height=height)
    
    def build_content(self) -> None:
        """Build the message content."""
        message_label = self.create_label(
            self.content_frame,
            self.message,
            font_size="label"
        )
        message_label.pack(expand=True, fill="both", pady=WindowConfig.PADDING_MEDIUM)
    
    def build_buttons(self) -> None:
        """Build the button area with custom buttons."""
        for i, button_text in enumerate(reversed(self.buttons)):
            button = self.create_button(
                self.button_frame,
                button_text,
                lambda text=button_text: self._button_clicked(text),
                style="primary" if i == 0 else "secondary"
            )
            button.pack(side="right", padx=(WindowConfig.PADDING_SMALL, 0))
        
        # Set up keyboard shortcuts
        if len(self.buttons) == 1:
            self.bind('<Return>', lambda e: self._button_clicked(self.buttons[0]))
        else:
            self.bind('<Return>', lambda e: self._button_clicked(self.buttons[0]))
        
        self.bind('<Escape>', lambda e: self.cancel())
    
    def _button_clicked(self, button_text: str) -> None:
        """Handle button click."""
        self.clicked_button = button_text
        self.result = button_text
        self._call_result_callback()
        self.destroy()
    
    def get_result(self) -> str:
        """Return the clicked button text."""
        return self.clicked_button


class InputDialog(BaseDialog):
    """Dialog for getting text input from the user."""
    
    def __init__(
        self,
        parent: tk.Widget,
        title: str,
        prompt: str,
        initial_value: str = "",
        placeholder: str = ""
    ):
        """
        Initialize input dialog.
        
        Args:
            parent: Parent window
            title: Dialog title
            prompt: Prompt text
            initial_value: Initial input value
            placeholder: Placeholder text
        """
        self.prompt = prompt
        self.initial_value = initial_value
        self.placeholder = placeholder
        self.entry = None
        
        super().__init__(parent, title, width=400, height=200)
    
    def build_content(self) -> None:
        """Build the input content."""
        # Prompt label
        prompt_label = self.create_label(
            self.content_frame,
            self.prompt,
            font_size="label"
        )
        prompt_label.pack(pady=(0, WindowConfig.PADDING_MEDIUM))
        
        # Input entry
        self.entry = self.create_entry(
            self.content_frame,
            placeholder=self.placeholder,
            width=40
        )
        self.entry.pack(fill="x", pady=WindowConfig.PADDING_SMALL)
        
        # Set initial value if provided
        if self.initial_value:
            if self.placeholder and self.entry.get() == self.placeholder:
                self.entry.delete(0, tk.END)
                self.entry.configure(fg=self.entry.normal_color)
            self.entry.insert(0, self.initial_value)
        
        # Focus the entry
        self.entry.focus_set()
        
        # Select all text if there's an initial value
        if self.initial_value:
            self.entry.select_range(0, tk.END)
    
    def get_result(self) -> str:
        """Return the entered text."""
        if self.entry:
            text = self.entry.get()
            # Don't return placeholder text
            if hasattr(self.entry, 'placeholder') and text == self.entry.placeholder:
                return ""
            return text
        return ""
