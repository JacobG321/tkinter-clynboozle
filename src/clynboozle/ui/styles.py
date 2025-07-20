"""Centralized styling functions and theme management for ClynBoozle."""

import tkinter as tk
from tkinter import ttk, font
from typing import Dict, Any, Optional
from ..config.settings import Colors, FontConfig, WindowConfig


class StyleManager:
    """Manages application-wide styling and theming."""

    def __init__(self):
        """Initialize the style manager."""
        self._current_theme = "default"
        self._style_cache = {}
        self._ttk_style = None

    def initialize_ttk_styles(self, root: tk.Tk) -> None:
        """Initialize TTK styles for the application."""
        self._ttk_style = ttk.Style(root)

        # Configure button style
        self._ttk_style.configure(
            "ClynBoozle.TButton",
            background=Colors.BUTTON,
            foreground=Colors.BUTTON_TEXT,
            borderwidth=1,
            focuscolor="none",
            padding=(10, 5),
        )

        self._ttk_style.map(
            "ClynBoozle.TButton",
            background=[("active", Colors.BUTTON_HOVER), ("pressed", Colors.BUTTON_ACTIVE)],
            foreground=[("active", Colors.BUTTON_TEXT), ("pressed", Colors.BUTTON_TEXT)],
        )

        # Configure scale (slider) style
        self._ttk_style.configure(
            "ClynBoozle.TScale",
            background=Colors.BACKGROUND,
            troughcolor=Colors.SEPARATOR,
            borderwidth=0,
            lightcolor=Colors.BUTTON,
            darkcolor=Colors.BUTTON,
        )

    def get_button_style(
        self,
        size: str = "normal",
        variant: str = "primary",
        custom_colors: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Get button styling configuration.

        Args:
            size: Button size ("small", "normal", "large")
            variant: Button variant ("primary", "secondary", "success", "danger")
            custom_colors: Optional custom color overrides

        Returns:
            Dictionary of style properties
        """
        # Base configuration
        styles = {
            "font": self._get_font_for_size(size),
            "borderwidth": 1,
            "relief": "raised",
            "cursor": "hand2",
            "activebackground": Colors.BUTTON_HOVER,
            "activeforeground": Colors.BUTTON_TEXT,
        }

        # Size-specific settings
        if size == "small":
            styles.update({"padx": 8, "pady": 4, "font": self._get_font_for_size("small")})
        elif size == "large":
            styles.update({"padx": 20, "pady": 12, "font": self._get_font_for_size("large")})
        else:  # normal
            styles.update({"padx": 15, "pady": 8, "font": self._get_font_for_size("normal")})

        # Variant-specific colors
        if variant == "primary":
            styles.update({"bg": Colors.BUTTON, "fg": Colors.BUTTON_TEXT})
        elif variant == "secondary":
            styles.update({"bg": Colors.BACKGROUND, "fg": Colors.TEXT, "relief": "solid"})
        elif variant == "success":
            styles.update({"bg": "#28a745", "fg": "white"})
        elif variant == "danger":
            styles.update({"bg": "#dc3545", "fg": "white"})

        # Apply custom colors if provided
        if custom_colors:
            styles.update(custom_colors)

        return styles

    def get_label_style(
        self,
        size: str = "normal",
        variant: str = "normal",
        custom_colors: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Get label styling configuration.

        Args:
            size: Label size ("small", "normal", "large", "title")
            variant: Label variant ("normal", "muted", "success", "warning", "error")
            custom_colors: Optional custom color overrides

        Returns:
            Dictionary of style properties
        """
        styles = {"bg": Colors.BACKGROUND, "font": self._get_font_for_size(size), "anchor": "w"}

        # Variant-specific colors
        if variant == "normal":
            styles["fg"] = Colors.TEXT
        elif variant == "muted":
            styles["fg"] = Colors.TEXT_MUTED
        elif variant == "success":
            styles["fg"] = "#28a745"
        elif variant == "warning":
            styles["fg"] = "#ffc107"
        elif variant == "error":
            styles["fg"] = "#dc3545"

        # Apply custom colors if provided
        if custom_colors:
            styles.update(custom_colors)

        return styles

    def get_frame_style(
        self, variant: str = "normal", custom_colors: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Get frame styling configuration.

        Args:
            variant: Frame variant ("normal", "card", "panel")
            custom_colors: Optional custom color overrides

        Returns:
            Dictionary of style properties
        """
        styles = {"bg": Colors.BACKGROUND}

        if variant == "card":
            styles.update({"relief": "solid", "borderwidth": 1, "bg": Colors.CARD_BG})
        elif variant == "panel":
            styles.update({"relief": "groove", "borderwidth": 2, "bg": Colors.PANEL_BG})

        # Apply custom colors if provided
        if custom_colors:
            styles.update(custom_colors)

        return styles

    def get_entry_style(
        self, size: str = "normal", custom_colors: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Get entry widget styling configuration.

        Args:
            size: Entry size ("small", "normal", "large")
            custom_colors: Optional custom color overrides

        Returns:
            Dictionary of style properties
        """
        styles = {
            "bg": "white",
            "fg": Colors.TEXT,
            "insertbackground": Colors.TEXT,
            "selectbackground": Colors.BUTTON,
            "selectforeground": Colors.BUTTON_TEXT,
            "relief": "solid",
            "borderwidth": 1,
            "font": self._get_font_for_size(size),
        }

        # Apply custom colors if provided
        if custom_colors:
            styles.update(custom_colors)

        return styles

    def apply_widget_style(self, widget: tk.Widget, style_dict: Dict[str, Any]) -> None:
        """
        Apply a style dictionary to a widget.

        Args:
            widget: Widget to style
            style_dict: Style configuration dictionary
        """
        try:
            widget.configure(**style_dict)
        except tk.TclError as e:
            print(f"Warning: Could not apply style to {type(widget).__name__}: {e}")

    def style_button(
        self,
        button: tk.Button,
        size: str = "normal",
        variant: str = "primary",
        custom_colors: Optional[Dict[str, str]] = None,
    ) -> None:
        """
        Apply styling to a button widget.

        Args:
            button: Button widget to style
            size: Button size
            variant: Button variant
            custom_colors: Optional custom color overrides
        """
        style = self.get_button_style(size, variant, custom_colors)
        self.apply_widget_style(button, style)

    def style_label(
        self,
        label: tk.Label,
        size: str = "normal",
        variant: str = "normal",
        custom_colors: Optional[Dict[str, str]] = None,
    ) -> None:
        """
        Apply styling to a label widget.

        Args:
            label: Label widget to style
            size: Label size
            variant: Label variant
            custom_colors: Optional custom color overrides
        """
        style = self.get_label_style(size, variant, custom_colors)
        self.apply_widget_style(label, style)

    def style_frame(
        self,
        frame: tk.Frame,
        variant: str = "normal",
        custom_colors: Optional[Dict[str, str]] = None,
    ) -> None:
        """
        Apply styling to a frame widget.

        Args:
            frame: Frame widget to style
            variant: Frame variant
            custom_colors: Optional custom color overrides
        """
        style = self.get_frame_style(variant, custom_colors)
        self.apply_widget_style(frame, style)

    def style_entry(
        self, entry: tk.Entry, size: str = "normal", custom_colors: Optional[Dict[str, str]] = None
    ) -> None:
        """
        Apply styling to an entry widget.

        Args:
            entry: Entry widget to style
            size: Entry size
            custom_colors: Optional custom color overrides
        """
        style = self.get_entry_style(size, custom_colors)
        self.apply_widget_style(entry, style)

    def create_styled_button(
        self,
        parent: tk.Widget,
        text: str,
        command: Optional[callable] = None,
        size: str = "normal",
        variant: str = "primary",
        **kwargs,
    ) -> tk.Button:
        """
        Create a pre-styled button.

        Args:
            parent: Parent widget
            text: Button text
            command: Button command
            size: Button size
            variant: Button variant
            **kwargs: Additional button options

        Returns:
            Styled button widget
        """
        style = self.get_button_style(size, variant)
        style.update(kwargs)

        button = tk.Button(parent, text=text, command=command, **style)
        return button

    def create_styled_label(
        self, parent: tk.Widget, text: str, size: str = "normal", variant: str = "normal", **kwargs
    ) -> tk.Label:
        """
        Create a pre-styled label.

        Args:
            parent: Parent widget
            text: Label text
            size: Label size
            variant: Label variant
            **kwargs: Additional label options

        Returns:
            Styled label widget
        """
        style = self.get_label_style(size, variant)
        style.update(kwargs)

        label = tk.Label(parent, text=text, **style)
        return label

    def create_styled_frame(self, parent: tk.Widget, variant: str = "normal", **kwargs) -> tk.Frame:
        """
        Create a pre-styled frame.

        Args:
            parent: Parent widget
            variant: Frame variant
            **kwargs: Additional frame options

        Returns:
            Styled frame widget
        """
        style = self.get_frame_style(variant)
        style.update(kwargs)

        frame = tk.Frame(parent, **style)
        return frame

    def create_styled_entry(self, parent: tk.Widget, size: str = "normal", **kwargs) -> tk.Entry:
        """
        Create a pre-styled entry.

        Args:
            parent: Parent widget
            size: Entry size
            **kwargs: Additional entry options

        Returns:
            Styled entry widget
        """
        style = self.get_entry_style(size)
        style.update(kwargs)

        entry = tk.Entry(parent, **style)
        return entry

    def _get_font_for_size(self, size: str) -> font.Font:
        """
        Get font object for specified size.

        Args:
            size: Font size name

        Returns:
            Font object
        """
        cache_key = f"font_{size}"
        if cache_key in self._style_cache:
            return self._style_cache[cache_key]

        if size == "small":
            font_obj = font.Font(
                family=FontConfig.DEFAULT_FAMILY, size=FontConfig.SMALL_SIZE, weight="normal"
            )
        elif size == "large":
            font_obj = font.Font(
                family=FontConfig.DEFAULT_FAMILY, size=FontConfig.LARGE_SIZE, weight="normal"
            )
        elif size == "title":
            font_obj = font.Font(
                family=FontConfig.DEFAULT_FAMILY, size=FontConfig.TITLE_SIZE, weight="bold"
            )
        else:  # normal
            font_obj = font.Font(
                family=FontConfig.DEFAULT_FAMILY, size=FontConfig.DEFAULT_SIZE, weight="normal"
            )

        self._style_cache[cache_key] = font_obj
        return font_obj


# Global style manager instance
style_manager = StyleManager()


def get_style_manager() -> StyleManager:
    """Get the global style manager instance."""
    return style_manager


def initialize_application_styles(root: tk.Tk) -> None:
    """
    Initialize application-wide styles.

    Args:
        root: Root window
    """
    style_manager.initialize_ttk_styles(root)


def create_title_label(parent: tk.Widget, text: str, **kwargs) -> tk.Label:
    """
    Create a title label with standard styling.

    Args:
        parent: Parent widget
        text: Title text
        **kwargs: Additional options

    Returns:
        Styled title label
    """
    return style_manager.create_styled_label(parent, text, size="title", variant="normal", **kwargs)


def create_section_label(parent: tk.Widget, text: str, **kwargs) -> tk.Label:
    """
    Create a section label with standard styling.

    Args:
        parent: Parent widget
        text: Section text
        **kwargs: Additional options

    Returns:
        Styled section label
    """
    return style_manager.create_styled_label(parent, text, size="large", variant="normal", **kwargs)


def create_primary_button(parent: tk.Widget, text: str, command: callable, **kwargs) -> tk.Button:
    """
    Create a primary action button.

    Args:
        parent: Parent widget
        text: Button text
        command: Button command
        **kwargs: Additional options

    Returns:
        Styled primary button
    """
    return style_manager.create_styled_button(parent, text, command, variant="primary", **kwargs)


def create_secondary_button(parent: tk.Widget, text: str, command: callable, **kwargs) -> tk.Button:
    """
    Create a secondary action button.

    Args:
        parent: Parent widget
        text: Button text
        command: Button command
        **kwargs: Additional options

    Returns:
        Styled secondary button
    """
    return style_manager.create_styled_button(parent, text, command, variant="secondary", **kwargs)


def create_success_button(parent: tk.Widget, text: str, command: callable, **kwargs) -> tk.Button:
    """
    Create a success (green) button.

    Args:
        parent: Parent widget
        text: Button text
        command: Button command
        **kwargs: Additional options

    Returns:
        Styled success button
    """
    return style_manager.create_styled_button(parent, text, command, variant="success", **kwargs)


def create_danger_button(parent: tk.Widget, text: str, command: callable, **kwargs) -> tk.Button:
    """
    Create a danger (red) button.

    Args:
        parent: Parent widget
        text: Button text
        command: Button command
        **kwargs: Additional options

    Returns:
        Styled danger button
    """
    return style_manager.create_styled_button(parent, text, command, variant="danger", **kwargs)


def create_card_frame(parent: tk.Widget, **kwargs) -> tk.Frame:
    """
    Create a card-style frame.

    Args:
        parent: Parent widget
        **kwargs: Additional options

    Returns:
        Styled card frame
    """
    return style_manager.create_styled_frame(parent, variant="card", **kwargs)


def create_panel_frame(parent: tk.Widget, **kwargs) -> tk.Frame:
    """
    Create a panel-style frame.

    Args:
        parent: Parent widget
        **kwargs: Additional options

    Returns:
        Styled panel frame
    """
    return style_manager.create_styled_frame(parent, variant="panel", **kwargs)
