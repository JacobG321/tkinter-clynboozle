"""Question set selector UI component for pre-game setup."""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Any, Callable, Optional, Dict
import logging

from ..config.settings import ColorConfig, WindowConfig, FontConfig
from ..services.question_set_service import QuestionSetService, QuestionSet
from .base_frame import BaseFrame


class QuestionSetSelectorFrame(BaseFrame):
    """
    Question set selector for pre-game setup.
    
    This is different from QuestionManagerFrame - this is specifically for
    selecting a question set to play with, not for managing/editing sets.
    
    Features:
    - List of available question sets
    - Preview of selected set (question count, etc.)
    - Select and continue to game
    - Back to team setup
    """

    def __init__(
        self,
        master: tk.Widget,
        app: Any,
        question_set_service: QuestionSetService,
        **kwargs,
    ) -> None:
        """
        Initialize the question set selector frame.

        Args:
            master: Parent widget
            app: Main application instance
            question_set_service: Service for managing question sets
            **kwargs: Additional arguments passed to BaseFrame
        """
        self.question_set_service = question_set_service
        self.logger = logging.getLogger(__name__)

        # Current state
        self.selected_set_name: Optional[str] = None

        # Callbacks
        self.on_back: Optional[Callable[[], None]] = None
        self.on_select_set: Optional[Callable[[str], None]] = None

        # UI References
        self.set_listbox: Optional[tk.Listbox] = None
        self.preview_text: Optional[tk.Text] = None

        super().__init__(master, app, **kwargs)

    def build_ui(self) -> None:
        """Build the question set selector UI elements."""
        # Configure main grid
        self.grid_rowconfigure(0, weight=0)  # Header
        self.grid_rowconfigure(1, weight=1)  # Content
        self.grid_rowconfigure(2, weight=0)  # Footer
        self.grid_columnconfigure(0, weight=1)

        self._build_header()
        self._build_content()
        self._build_footer()

        # Load initial data
        self._refresh_question_sets()

    def _build_header(self) -> None:
        """Build the header section."""
        header_frame = tk.Frame(self, bg=ColorConfig.PRIMARY_BG)
        header_frame.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=WindowConfig.PADDING_LARGE,
            pady=WindowConfig.PADDING_MEDIUM,
        )

        # Title
        title_label = self.create_title_label(
            header_frame, "Select Question Set", color=ColorConfig.GOLD
        )
        title_label.pack(pady=WindowConfig.PADDING_MEDIUM)

        # Instructions
        instructions = tk.Label(
            header_frame,
            text="Choose a question set for your game:",
            font=(FontConfig.FAMILY, FontConfig.LABEL_SIZE),
            bg=ColorConfig.PRIMARY_BG,
            fg=ColorConfig.MUTED_TEXT,
        )
        instructions.pack(pady=(0, 10))

    def _build_content(self) -> None:
        """Build the main content area."""
        content_frame = tk.Frame(self, bg=ColorConfig.PRIMARY_BG)
        content_frame.grid(row=1, column=0, sticky="nsew", padx=WindowConfig.PADDING_LARGE)

        # Configure content grid - left panel (sets) and right panel (preview)
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)  # Question sets list
        content_frame.grid_columnconfigure(1, weight=1)  # Preview panel

        self._build_sets_panel(content_frame)
        self._build_preview_panel(content_frame)

    def _build_sets_panel(self, parent: tk.Widget) -> None:
        """Build the question sets selection panel."""
        sets_frame = tk.Frame(parent, bg=ColorConfig.SECONDARY_BG, relief=tk.RAISED, bd=1)
        sets_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=10)
        sets_frame.grid_rowconfigure(1, weight=1)
        sets_frame.grid_columnconfigure(0, weight=1)

        # Sets panel header
        sets_header = tk.Frame(sets_frame, bg=ColorConfig.SECONDARY_BG)
        sets_header.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        sets_title = tk.Label(
            sets_header,
            text="Available Question Sets",
            font=(FontConfig.FAMILY, FontConfig.LABEL_SIZE, "bold"),
            bg=ColorConfig.SECONDARY_BG,
            fg=ColorConfig.PRIMARY_TEXT,
        )
        sets_title.pack(side=tk.LEFT)

        # Question sets listbox with scrollbar
        sets_list_frame = tk.Frame(sets_frame, bg=ColorConfig.SECONDARY_BG)
        sets_list_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        sets_list_frame.grid_rowconfigure(0, weight=1)
        sets_list_frame.grid_columnconfigure(0, weight=1)

        self.set_listbox = tk.Listbox(
            sets_list_frame,
            bg=ColorConfig.ENTRY_BG,
            fg=ColorConfig.PRIMARY_TEXT,
            selectbackground=ColorConfig.PRIMARY_COLOR,
            selectforeground="white",
            font=(FontConfig.FAMILY, FontConfig.SMALL_SIZE),
            activestyle="none",  # Remove active styling
        )
        self.set_listbox.grid(row=0, column=0, sticky="nsew")

        # Scrollbar for sets list
        sets_scrollbar = ttk.Scrollbar(
            sets_list_frame, orient=tk.VERTICAL, command=self.set_listbox.yview
        )
        sets_scrollbar.grid(row=0, column=1, sticky="ns")
        self.set_listbox.configure(yscrollcommand=sets_scrollbar.set)

        # Bind selection event
        self.set_listbox.bind("<<ListboxSelect>>", self._on_set_selection_changed)
        self.set_listbox.bind("<Double-Button-1>", self._on_double_click)

    def _build_preview_panel(self, parent: tk.Widget) -> None:
        """Build the question set preview panel."""
        preview_frame = tk.Frame(parent, bg=ColorConfig.SECONDARY_BG, relief=tk.RAISED, bd=1)
        preview_frame.grid(row=0, column=1, sticky="nsew", pady=10)
        preview_frame.grid_rowconfigure(1, weight=1)
        preview_frame.grid_columnconfigure(0, weight=1)

        # Preview panel header
        preview_header = tk.Frame(preview_frame, bg=ColorConfig.SECONDARY_BG)
        preview_header.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        preview_title = tk.Label(
            preview_header,
            text="Question Set Preview",
            font=(FontConfig.FAMILY, FontConfig.LABEL_SIZE, "bold"),
            bg=ColorConfig.SECONDARY_BG,
            fg=ColorConfig.PRIMARY_TEXT,
        )
        preview_title.pack(side=tk.LEFT)

        # Preview content area
        preview_content_frame = tk.Frame(preview_frame, bg=ColorConfig.SECONDARY_BG)
        preview_content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        preview_content_frame.grid_rowconfigure(0, weight=1)
        preview_content_frame.grid_columnconfigure(0, weight=1)

        # Preview text area with scrollbar
        self.preview_text = tk.Text(
            preview_content_frame,
            bg=ColorConfig.ENTRY_BG,
            fg=ColorConfig.PRIMARY_TEXT,
            font=(FontConfig.FAMILY, FontConfig.SMALL_SIZE),
            wrap=tk.WORD,
            state=tk.DISABLED,  # Read-only
        )
        self.preview_text.grid(row=0, column=0, sticky="nsew")

        # Scrollbar for preview text
        preview_scrollbar = ttk.Scrollbar(
            preview_content_frame, orient=tk.VERTICAL, command=self.preview_text.yview
        )
        preview_scrollbar.grid(row=0, column=1, sticky="ns")
        self.preview_text.configure(yscrollcommand=preview_scrollbar.set)

        # Initial preview message
        self._update_preview(None)

    def _build_footer(self) -> None:
        """Build the footer with action buttons."""
        footer_frame = tk.Frame(self, bg=ColorConfig.PRIMARY_BG)
        footer_frame.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=WindowConfig.PADDING_LARGE,
            pady=WindowConfig.PADDING_MEDIUM,
        )

        # Back button container
        back_container = tk.Frame(footer_frame, bg=ColorConfig.PRIMARY_BG)
        back_container.pack(side=tk.LEFT)

        self.back_frame, self.back_label = self.create_clickable_frame(
            back_container,
            "Back to Team Setup",
            ColorConfig.SECONDARY_COLOR,
            row=0,
            col=0,
            command=self._handle_back,
            width=150,
            height=40,
            font=(FontConfig.FAMILY, FontConfig.BUTTON_SIZE, "bold"),
        )

        # Right side buttons container
        right_buttons = tk.Frame(footer_frame, bg=ColorConfig.PRIMARY_BG)
        right_buttons.pack(side=tk.RIGHT)

        # Select and Continue button container
        select_container = tk.Frame(right_buttons, bg=ColorConfig.PRIMARY_BG)
        select_container.pack(side=tk.LEFT)

        self.select_frame, self.select_label = self.create_clickable_frame(
            select_container,
            "Select & Continue",
            ColorConfig.SUCCESS_COLOR,
            row=0,
            col=0,
            command=self._handle_select_set,
            width=150,
            height=40,
            font=(FontConfig.FAMILY, FontConfig.BUTTON_SIZE, "bold"),
        )

    def set_callbacks(
        self,
        on_back: Optional[Callable[[], None]] = None,
        on_select_set: Optional[Callable[[str], None]] = None,
    ) -> None:
        """Set navigation callbacks."""
        self.on_back = on_back
        self.on_select_set = on_select_set

    def _refresh_question_sets(self) -> None:
        """Refresh the question sets list."""
        if not self.set_listbox:
            return

        # Clear current list
        self.set_listbox.delete(0, tk.END)

        # Get all question sets
        question_sets = self.question_set_service.get_all_question_sets()

        if not question_sets:
            self.set_listbox.insert(tk.END, "No question sets available")
            self.set_listbox.configure(state=tk.DISABLED)
            return

        self.set_listbox.configure(state=tk.NORMAL)

        # Add to listbox
        for set_name, question_set in question_sets.items():
            display_name = f"{question_set.name} ({len(question_set.questions)} questions)"
            self.set_listbox.insert(tk.END, display_name)

        # Select current set if available
        current_set = self.question_set_service.get_current_question_set()
        if current_set:
            current_name = None
            for set_name, question_set in question_sets.items():
                if question_set == current_set:
                    current_name = set_name
                    break

            if current_name:
                set_names = list(question_sets.keys())
                if current_name in set_names:
                    index = set_names.index(current_name)
                    self.set_listbox.selection_set(index)
                    self.selected_set_name = current_name
                    self._update_preview(current_name)

    def _on_set_selection_changed(self, event: tk.Event) -> None:
        """Handle question set selection change."""
        if not self.set_listbox:
            return

        selection = self.set_listbox.curselection()
        if not selection:
            self.selected_set_name = None
            self._update_preview(None)
            return

        index = selection[0]
        question_sets = self.question_set_service.get_all_question_sets()
        set_names = list(question_sets.keys())

        if 0 <= index < len(set_names):
            set_name = set_names[index]
            self.selected_set_name = set_name
            self._update_preview(set_name)

    def _on_double_click(self, event: tk.Event) -> None:
        """Handle double-click on a question set."""
        if self.selected_set_name:
            self._handle_select_set()

    def _update_preview(self, set_name: Optional[str]) -> None:
        """Update the preview panel with question set information."""
        if not self.preview_text:
            return

        # Enable text widget for updating
        self.preview_text.configure(state=tk.NORMAL)
        self.preview_text.delete(1.0, tk.END)

        if not set_name:
            self.preview_text.insert(tk.END, "Select a question set to see details...")
        else:
            question_set = self.question_set_service.get_question_set(set_name)
            if question_set:
                # Build preview content
                preview_content = []
                preview_content.append(f"Name: {question_set.name}")
                preview_content.append(f"Questions: {len(question_set.questions)}")
                
                if question_set.questions:
                    # Calculate total points
                    total_points = sum(q.points for q in question_set.questions)
                    preview_content.append(f"Total Points: {total_points}")
                    
                    # Point distribution
                    point_counts = {}
                    for q in question_set.questions:
                        point_counts[q.points] = point_counts.get(q.points, 0) + 1
                    
                    if point_counts:
                        preview_content.append("\nPoint Distribution:")
                        for points, count in sorted(point_counts.items()):
                            preview_content.append(f"  {points} points: {count} questions")
                    
                    # Media summary
                    with_images = sum(1 for q in question_set.questions if q.has_tile_image() or q.has_question_image())
                    with_audio = sum(1 for q in question_set.questions if q.has_question_audio())
                    
                    if with_images > 0 or with_audio > 0:
                        preview_content.append("\nMedia:")
                        if with_images > 0:
                            preview_content.append(f"  Questions with images: {with_images}")
                        if with_audio > 0:
                            preview_content.append(f"  Questions with audio: {with_audio}")
                    
                    # Sample questions
                    preview_content.append("\nSample Questions:")
                    for i, question in enumerate(question_set.questions[:3]):  # Show first 3
                        q_text = question.question
                        if len(q_text) > 60:
                            q_text = q_text[:57] + "..."
                        preview_content.append(f"  {i+1}. {q_text} ({question.points} pts)")
                    
                    if len(question_set.questions) > 3:
                        preview_content.append(f"  ... and {len(question_set.questions) - 3} more")
                else:
                    preview_content.append("\nThis question set is empty.")

                self.preview_text.insert(tk.END, "\n".join(preview_content))

        # Disable text widget (read-only)
        self.preview_text.configure(state=tk.DISABLED)

    def _handle_back(self) -> None:
        """Handle back button click."""
        if self.on_back:
            self.on_back()

    def _handle_select_set(self) -> None:
        """Handle select set button click."""
        if not self.selected_set_name:
            messagebox.showwarning("No Selection", "Please select a question set to continue.")
            return

        # Verify the question set is valid
        question_set = self.question_set_service.get_question_set(self.selected_set_name)
        if not question_set or not question_set.questions:
            messagebox.showerror(
                "Invalid Question Set", 
                "The selected question set is empty or invalid. Please choose a different set."
            )
            return

        # Set as current question set
        self.question_set_service.set_current_question_set(self.selected_set_name)

        if self.on_select_set:
            self.on_select_set(self.selected_set_name)

    def resize_widgets(self) -> None:
        """Resize widgets for the current window size."""
        # This will be implemented when needed for responsive design
        pass