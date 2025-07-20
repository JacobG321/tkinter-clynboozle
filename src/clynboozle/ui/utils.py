"""UI utility functions for ClynBoozle."""

import tkinter as tk
from tkinter import font
from typing import Tuple, Optional, Union
import math

from ..config.settings import Colors, WindowConfig, FontConfig


def scale_font_size(base_size: int, scale_factor: float = 1.0) -> int:
    """
    Scale a font size based on a scaling factor.

    Args:
        base_size: Base font size
        scale_factor: Scaling factor (1.0 = no change)

    Returns:
        Scaled font size (minimum 8)
    """
    scaled = int(base_size * scale_factor)
    return max(8, scaled)  # Minimum readable size


def get_scaled_font(
    family: str = FontConfig.DEFAULT_FAMILY,
    size: int = FontConfig.DEFAULT_SIZE,
    weight: str = "normal",
    scale_factor: float = 1.0,
) -> font.Font:
    """
    Create a scaled font object.

    Args:
        family: Font family name
        size: Base font size
        weight: Font weight (normal, bold)
        scale_factor: Scaling factor

    Returns:
        Configured Font object
    """
    scaled_size = scale_font_size(size, scale_factor)
    return font.Font(family=family, size=scaled_size, weight=weight)


def calculate_window_scaling(window: tk.Widget) -> float:
    """
    Calculate appropriate scaling factor based on window size.

    Args:
        window: Window widget to measure

    Returns:
        Scaling factor between 0.7 and 2.0
    """
    try:
        window_width = window.winfo_width()

        # Base calculation on width primarily
        base_width = WindowConfig.DEFAULT_WIDTH
        width_ratio = window_width / base_width

        # Constrain scaling to reasonable bounds
        scale_factor = max(0.7, min(2.0, width_ratio))
        return scale_factor
    except Exception:
        return 1.0  # Default scale if measurement fails


def center_window(window: tk.Toplevel, width: int, height: int) -> None:
    """
    Center a window on the screen.

    Args:
        window: Window to center
        width: Window width
        height: Window height
    """
    try:
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()

        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        window.geometry(f"{width}x{height}+{x}+{y}")
    except Exception:
        # Fallback to default positioning
        window.geometry(f"{width}x{height}")


def center_window_on_parent(child: tk.Toplevel, parent: tk.Widget) -> None:
    """
    Center a child window on its parent.

    Args:
        child: Child window to center
        parent: Parent window
    """
    try:
        child.update_idletasks()
        parent.update_idletasks()

        # Get parent position and size
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()

        # Get child size
        child_width = child.winfo_width()
        child_height = child.winfo_height()

        # Calculate center position
        x = parent_x + (parent_width - child_width) // 2
        y = parent_y + (parent_height - child_height) // 2

        # Ensure window stays on screen
        screen_width = child.winfo_screenwidth()
        screen_height = child.winfo_screenheight()

        x = max(0, min(x, screen_width - child_width))
        y = max(0, min(y, screen_height - child_height))

        child.geometry(f"+{x}+{y}")
    except Exception:
        # Fallback to screen center
        center_window(child, child.winfo_width(), child.winfo_height())


def calculate_grid_dimensions(total_items: int) -> Tuple[int, int]:
    """
    Calculate optimal grid dimensions for a given number of items.

    Args:
        total_items: Total number of items to arrange

    Returns:
        Tuple of (rows, columns)
    """
    if total_items <= 0:
        return (1, 1)

    # Try to make a roughly square grid
    sqrt_items = math.sqrt(total_items)
    rows = int(sqrt_items)
    cols = math.ceil(total_items / rows)

    # Adjust for better proportions (prefer wider than tall)
    if rows * cols < total_items:
        if cols * rows < total_items:
            rows += 1

    # Ensure we don't have empty rows
    while rows > 1 and (rows - 1) * cols >= total_items:
        rows -= 1

    return (rows, cols)


def calculate_widget_size(
    container_width: int, container_height: int, grid_rows: int, grid_cols: int, padding: int = 10
) -> Tuple[int, int]:
    """
    Calculate optimal widget size for a grid layout.

    Args:
        container_width: Container width
        container_height: Container height
        grid_rows: Number of rows
        grid_cols: Number of columns
        padding: Padding between widgets

    Returns:
        Tuple of (widget_width, widget_height)
    """
    if grid_rows <= 0 or grid_cols <= 0:
        return (100, 50)  # Default size

    # Calculate available space
    available_width = container_width - (padding * (grid_cols + 1))
    available_height = container_height - (padding * (grid_rows + 1))

    # Calculate widget dimensions
    widget_width = max(50, available_width // grid_cols)
    widget_height = max(30, available_height // grid_rows)

    return (widget_width, widget_height)


def validate_color(color: str) -> bool:
    """
    Validate if a color string is valid for Tkinter.

    Args:
        color: Color string to validate

    Returns:
        True if valid, False otherwise
    """
    try:
        # Create a temporary widget to test the color
        temp = tk.Label()
        temp.configure(bg=color)
        temp.destroy()
        return True
    except tk.TclError:
        return False


def ensure_visible(window: tk.Widget) -> None:
    """
    Ensure a window is visible on screen.

    Args:
        window: Window to make visible
    """
    try:
        window.update_idletasks()

        # Get window position and size
        x = window.winfo_rootx()
        y = window.winfo_rooty()
        width = window.winfo_width()
        height = window.winfo_height()

        # Get screen dimensions
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()

        # Adjust position if window is off-screen
        new_x = max(0, min(x, screen_width - width))
        new_y = max(0, min(y, screen_height - height))

        if new_x != x or new_y != y:
            window.geometry(f"+{new_x}+{new_y}")

    except Exception:
        pass  # Ignore errors in positioning


def create_tooltip(widget: tk.Widget, text: str) -> None:
    """
    Create a simple tooltip for a widget.

    Args:
        widget: Widget to add tooltip to
        text: Tooltip text
    """

    def show_tooltip(event):
        tooltip = tk.Toplevel(widget)
        tooltip.wm_overrideredirect(True)
        tooltip.configure(bg=Colors.TOOLTIP_BG)

        label = tk.Label(
            tooltip,
            text=text,
            bg=Colors.TOOLTIP_BG,
            fg=Colors.TOOLTIP_TEXT,
            font=("Arial", 9),
            padx=5,
            pady=3,
        )
        label.pack()

        # Position tooltip
        x = event.x_root + 10
        y = event.y_root + 10
        tooltip.geometry(f"+{x}+{y}")

        # Auto-hide after 3 seconds
        tooltip.after(3000, tooltip.destroy)

    def hide_tooltip(event):
        # Find and destroy any existing tooltips
        for child in widget.winfo_toplevel().winfo_children():
            if isinstance(child, tk.Toplevel) and child.wm_overrideredirect():
                try:
                    child.destroy()
                except Exception:
                    pass

    widget.bind("<Enter>", show_tooltip)
    widget.bind("<Leave>", hide_tooltip)


def create_separator(parent: tk.Widget, orientation: str = "horizontal") -> tk.Frame:
    """
    Create a visual separator.

    Args:
        parent: Parent widget
        orientation: "horizontal" or "vertical"

    Returns:
        Separator frame
    """
    if orientation == "horizontal":
        separator = tk.Frame(parent, height=1, bg=Colors.SEPARATOR)
        separator.pack(fill=tk.X, pady=5)
    else:
        separator = tk.Frame(parent, width=1, bg=Colors.SEPARATOR)
        separator.pack(fill=tk.Y, padx=5)

    return separator


def bind_mousewheel(widget: tk.Widget, target: Optional[tk.Widget] = None) -> None:
    """
    Bind mousewheel scrolling to a widget.

    Args:
        widget: Widget to bind events to
        target: Target widget to scroll (defaults to widget)
    """
    if target is None:
        target = widget

    def on_mousewheel(event):
        try:
            # Different platforms handle mousewheel differently
            if event.delta:
                delta = -1 * (event.delta / 120)
            else:
                delta = -1 if event.num == 4 else 1

            if hasattr(target, "yview_scroll"):
                target.yview_scroll(int(delta), "units")
        except Exception:
            pass

    # Bind for different platforms
    widget.bind("<MouseWheel>", on_mousewheel)  # Windows/Mac
    widget.bind("<Button-4>", on_mousewheel)  # Linux
    widget.bind("<Button-5>", on_mousewheel)  # Linux


def get_text_dimensions(text: str, font_obj: font.Font) -> Tuple[int, int]:
    """
    Get the dimensions of text with a specific font.

    Args:
        text: Text to measure
        font_obj: Font object

    Returns:
        Tuple of (width, height) in pixels
    """
    try:
        width = font_obj.measure(text)
        height = font_obj.metrics("linespace")
        return (width, height)
    except Exception:
        return (100, 20)  # Default dimensions


def wrap_text(text: str, max_width: int, font_obj: font.Font) -> str:
    """
    Wrap text to fit within a maximum width.

    Args:
        text: Text to wrap
        max_width: Maximum width in pixels
        font_obj: Font object for measurement

    Returns:
        Wrapped text with newlines
    """
    if not text:
        return ""

    words = text.split()
    lines = []
    current_line = []

    for word in words:
        # Test adding this word to current line
        test_line = " ".join(current_line + [word])
        width, _ = get_text_dimensions(test_line, font_obj)

        if width <= max_width or not current_line:
            current_line.append(word)
        else:
            # Start new line
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]

    # Add final line
    if current_line:
        lines.append(" ".join(current_line))

    return "\n".join(lines)
