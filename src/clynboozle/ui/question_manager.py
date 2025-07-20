"""Question manager UI component for ClynBoozle."""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from typing import Any, Callable, Optional, List, Dict
import logging

from ..config.settings import ColorConfig, WindowConfig, FontConfig, ComponentSizes
from ..services.question_set_service import QuestionSetService, QuestionSet
from ..models.question import Question, MediaReference
from .base_frame import BaseFrame
from .media_browser import MediaBrowserDialog


class QuestionManagerFrame(BaseFrame):
    """
    Question manager frame for creating and editing question sets.

    Features:
    - List of question sets with selection
    - Question list with add/edit/delete
    - Import/export functionality
    - Save/load operations
    """

    def __init__(
        self,
        master: tk.Widget,
        app: Any,
        question_set_service: QuestionSetService,
        **kwargs,
    ) -> None:
        """
        Initialize the question manager frame.

        Args:
            master: Parent widget
            app: Main application instance
            question_set_service: Service for managing question sets
            **kwargs: Additional arguments passed to BaseFrame
        """
        self.question_set_service = question_set_service
        self.logger = logging.getLogger(__name__)

        # Current state
        self.current_set_name: Optional[str] = None
        self.selected_question_index: Optional[int] = None

        # Callbacks
        self.on_back: Optional[Callable[[], None]] = None
        self.on_use_set: Optional[Callable[[str], None]] = None

        # UI References
        self.set_listbox: Optional[tk.Listbox] = None
        self.question_tree: Optional[ttk.Treeview] = None
        self.set_name_var: Optional[tk.StringVar] = None

        super().__init__(master, app, **kwargs)

    def build_ui(self) -> None:
        """Build the question manager UI elements."""
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
            header_frame, "Question Set Manager", color=ColorConfig.GOLD
        )
        title_label.pack(side=tk.LEFT, pady=WindowConfig.PADDING_MEDIUM)

        # Header buttons frame
        header_btn_frame = tk.Frame(header_frame, bg=ColorConfig.PRIMARY_BG)
        header_btn_frame.pack(side=tk.RIGHT, pady=WindowConfig.PADDING_MEDIUM)

        # New Set button container
        new_set_container = tk.Frame(header_btn_frame, bg=ColorConfig.PRIMARY_BG)
        new_set_container.pack(side=tk.LEFT, padx=(0, 5))

        self.new_set_frame, self.new_set_label = self.create_clickable_frame(
            new_set_container,
            "New Set",
            ColorConfig.SUCCESS_COLOR,
            row=0,
            col=0,
            command=self._handle_new_set,
            width=100,
            height=35,
            font=(FontConfig.FAMILY, FontConfig.SMALL_SIZE, "bold"),
        )

        # Import Set button container
        import_container = tk.Frame(header_btn_frame, bg=ColorConfig.PRIMARY_BG)
        import_container.pack(side=tk.LEFT, padx=5)

        self.import_frame, self.import_label = self.create_clickable_frame(
            import_container,
            "Import",
            ColorConfig.PRIMARY_COLOR,
            row=0,
            col=1,
            command=self._handle_import_set,
            width=100,
            height=35,
            font=(FontConfig.FAMILY, FontConfig.SMALL_SIZE, "bold"),
        )

        # Export Set button container
        export_container = tk.Frame(header_btn_frame, bg=ColorConfig.PRIMARY_BG)
        export_container.pack(side=tk.LEFT, padx=5)

        self.export_frame, self.export_label = self.create_clickable_frame(
            export_container,
            "Export",
            ColorConfig.WARNING_COLOR,
            row=0,
            col=2,
            command=self._handle_export_set,
            width=100,
            height=35,
            font=(FontConfig.FAMILY, FontConfig.SMALL_SIZE, "bold"),
        )

    def _build_content(self) -> None:
        """Build the main content area."""
        content_frame = tk.Frame(self, bg=ColorConfig.PRIMARY_BG)
        content_frame.grid(row=1, column=0, sticky="nsew", padx=WindowConfig.PADDING_LARGE)

        # Configure content grid - left panel (sets) and right panel (questions)
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=0)  # Question sets list
        content_frame.grid_columnconfigure(1, weight=1)  # Questions panel

        self._build_sets_panel(content_frame)
        self._build_questions_panel(content_frame)

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
            text="Question Sets",
            font=(FontConfig.FAMILY, FontConfig.LABEL_SIZE, "bold"),
            bg=ColorConfig.SECONDARY_BG,
            fg=ColorConfig.PRIMARY_TEXT,
        )
        sets_title.pack(side=tk.LEFT)

        # Delete set button frame
        delete_btn_container = tk.Frame(sets_header, bg=ColorConfig.SECONDARY_BG)
        delete_btn_container.pack(side=tk.RIGHT)

        self.delete_set_frame, self.delete_set_label = self.create_clickable_frame(
            delete_btn_container,
            "Delete",
            ColorConfig.ERROR_COLOR,
            row=0,
            col=0,
            command=self._handle_delete_set,
            width=70,
            height=25,
            font=(FontConfig.FAMILY, 10, "bold"),
        )

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
            selectforeground=ColorConfig.PRIMARY_TEXT,
            font=(FontConfig.FAMILY, FontConfig.SMALL_SIZE),
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

    def _build_questions_panel(self, parent: tk.Widget) -> None:
        """Build the questions editing panel."""
        questions_frame = tk.Frame(parent, bg=ColorConfig.SECONDARY_BG, relief=tk.RAISED, bd=1)
        questions_frame.grid(row=0, column=1, sticky="nsew", pady=10)
        questions_frame.grid_rowconfigure(1, weight=1)
        questions_frame.grid_columnconfigure(0, weight=1)

        # Questions panel header
        questions_header = tk.Frame(questions_frame, bg=ColorConfig.SECONDARY_BG)
        questions_header.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        questions_header.grid_columnconfigure(0, weight=1)

        # Set name display
        self.set_name_var = tk.StringVar(value="No Set Selected")
        set_name_label = tk.Label(
            questions_header,
            textvariable=self.set_name_var,
            font=(FontConfig.FAMILY, FontConfig.LABEL_SIZE, "bold"),
            bg=ColorConfig.SECONDARY_BG,
            fg=ColorConfig.PRIMARY_TEXT,
        )
        set_name_label.grid(row=0, column=0, sticky="w")

        # Question action buttons
        q_buttons_frame = tk.Frame(questions_header, bg=ColorConfig.SECONDARY_BG)
        q_buttons_frame.grid(row=0, column=1, sticky="e")

        # Add question button container
        add_q_container = tk.Frame(q_buttons_frame, bg=ColorConfig.SECONDARY_BG)
        add_q_container.pack(side=tk.LEFT, padx=(0, 5))

        self.add_q_frame, self.add_q_label = self.create_clickable_frame(
            add_q_container,
            "Add Question",
            ColorConfig.SUCCESS_COLOR,
            row=0,
            col=0,
            command=self._handle_add_question,
            width=120,
            height=30,
            font=(FontConfig.FAMILY, 11, "bold"),
        )

        # Edit question button container
        edit_q_container = tk.Frame(q_buttons_frame, bg=ColorConfig.SECONDARY_BG)
        edit_q_container.pack(side=tk.LEFT, padx=5)

        self.edit_q_frame, self.edit_q_label = self.create_clickable_frame(
            edit_q_container,
            "Edit",
            ColorConfig.PRIMARY_COLOR,
            row=0,
            col=1,
            command=self._handle_edit_question,
            width=60,
            height=30,
            font=(FontConfig.FAMILY, 11, "bold"),
        )

        # Delete question button container
        delete_q_container = tk.Frame(q_buttons_frame, bg=ColorConfig.SECONDARY_BG)
        delete_q_container.pack(side=tk.LEFT, padx=5)

        self.delete_q_frame, self.delete_q_label = self.create_clickable_frame(
            delete_q_container,
            "Delete",
            ColorConfig.ERROR_COLOR,
            row=0,
            col=2,
            command=self._handle_delete_question,
            width=60,
            height=30,
            font=(FontConfig.FAMILY, 11, "bold"),
        )

        # Questions treeview
        questions_list_frame = tk.Frame(questions_frame, bg=ColorConfig.SECONDARY_BG)
        questions_list_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        questions_list_frame.grid_rowconfigure(0, weight=1)
        questions_list_frame.grid_columnconfigure(0, weight=1)

        # Create treeview with columns
        columns = ("question", "answer", "points", "media")
        self.question_tree = ttk.Treeview(questions_list_frame, columns=columns, show="headings")

        # Define column headings and widths
        self.question_tree.heading("question", text="Question")
        self.question_tree.heading("answer", text="Answer")
        self.question_tree.heading("points", text="Points")
        self.question_tree.heading("media", text="Media")

        self.question_tree.column("question", width=300, stretch=True)
        self.question_tree.column("answer", width=150, stretch=True)
        self.question_tree.column("points", width=60, stretch=False)
        self.question_tree.column("media", width=80, stretch=False)

        self.question_tree.grid(row=0, column=0, sticky="nsew")

        # Scrollbar for questions tree
        q_scrollbar = ttk.Scrollbar(
            questions_list_frame, orient=tk.VERTICAL, command=self.question_tree.yview
        )
        q_scrollbar.grid(row=0, column=1, sticky="ns")
        self.question_tree.configure(yscrollcommand=q_scrollbar.set)

        # Bind selection event
        self.question_tree.bind("<<TreeviewSelect>>", self._on_question_selection_changed)
        self.question_tree.bind("<Double-1>", lambda e: self._handle_edit_question())

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
            "Back",
            ColorConfig.SECONDARY_COLOR,
            row=0,
            col=0,
            command=self._handle_back,
            width=100,
            height=40,
            font=(FontConfig.FAMILY, FontConfig.BUTTON_SIZE, "bold"),
        )

        # Right side buttons container
        right_buttons = tk.Frame(footer_frame, bg=ColorConfig.PRIMARY_BG)
        right_buttons.pack(side=tk.RIGHT)

        # Save button container
        save_container = tk.Frame(right_buttons, bg=ColorConfig.PRIMARY_BG)
        save_container.pack(side=tk.LEFT, padx=5)

        self.save_frame, self.save_label = self.create_clickable_frame(
            save_container,
            "Save",
            ColorConfig.SUCCESS_COLOR,
            row=0,
            col=0,
            command=self._handle_save,
            width=100,
            height=40,
            font=(FontConfig.FAMILY, FontConfig.BUTTON_SIZE, "bold"),
        )

        # Use Set button container
        use_set_container = tk.Frame(right_buttons, bg=ColorConfig.PRIMARY_BG)
        use_set_container.pack(side=tk.LEFT, padx=(5, 0))

        self.use_set_frame, self.use_set_label = self.create_clickable_frame(
            use_set_container,
            "Use This Set",
            ColorConfig.PRIMARY_COLOR,
            row=0,
            col=0,
            command=self._handle_use_set,
            width=150,
            height=40,
            font=(FontConfig.FAMILY, FontConfig.BUTTON_SIZE, "bold"),
        )

    def set_callbacks(
        self,
        on_back: Optional[Callable[[], None]] = None,
        on_use_set: Optional[Callable[[str], None]] = None,
    ) -> None:
        """Set navigation callbacks."""
        self.on_back = on_back
        self.on_use_set = on_use_set

    def _refresh_question_sets(self) -> None:
        """Refresh the question sets list."""
        if not self.set_listbox:
            return

        # Clear current list
        self.set_listbox.delete(0, tk.END)

        # Get all question sets
        question_sets = self.question_set_service.get_all_question_sets()

        # Add to listbox
        for set_name, question_set in question_sets.items():
            display_name = f"{question_set.name} ({len(question_set.questions)} questions)"
            self.set_listbox.insert(tk.END, display_name)
            # Store the actual set name as data (we'll use index to map back)

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
                    self._load_questions_for_set(current_name)

    def _refresh_questions(self) -> None:
        """Refresh the questions list for the current set."""
        if not self.question_tree or not self.current_set_name:
            return

        # Clear current items
        for item in self.question_tree.get_children():
            self.question_tree.delete(item)

        # Get current question set
        question_set = self.question_set_service.get_question_set(self.current_set_name)
        if not question_set:
            return

        # Update set name display
        if self.set_name_var:
            self.set_name_var.set(question_set.name)

        # Add questions to tree
        for i, question in enumerate(question_set.questions):
            # Create media indicators
            media_indicators = []
            if question.has_tile_image():
                media_indicators.append("📷")
            if question.has_question_image():
                media_indicators.append("🖼️")
            if question.has_question_audio():
                media_indicators.append("🔊")

            media_text = " ".join(media_indicators) if media_indicators else ""

            # Truncate long text for display
            question_text = question.question
            if len(question_text) > 50:
                question_text = question_text[:47] + "..."

            answer_text = question.answer
            if len(answer_text) > 30:
                answer_text = answer_text[:27] + "..."

            self.question_tree.insert(
                "", tk.END, values=(question_text, answer_text, question.points, media_text)
            )

    def _on_set_selection_changed(self, event: tk.Event) -> None:
        """Handle question set selection change."""
        if not self.set_listbox:
            return

        selection = self.set_listbox.curselection()
        if not selection:
            return

        index = selection[0]
        question_sets = self.question_set_service.get_all_question_sets()
        set_names = list(question_sets.keys())

        if 0 <= index < len(set_names):
            set_name = set_names[index]
            self._load_questions_for_set(set_name)

    def _on_question_selection_changed(self, event: tk.Event) -> None:
        """Handle question selection change."""
        if not self.question_tree:
            return

        selection = self.question_tree.selection()
        if selection:
            # Get index of selected item
            children = self.question_tree.get_children()
            self.selected_question_index = children.index(selection[0])
        else:
            self.selected_question_index = None

    def _load_questions_for_set(self, set_name: str) -> None:
        """Load questions for the specified set."""
        self.current_set_name = set_name
        self.question_set_service.set_current_question_set(set_name)
        self._refresh_questions()

    # Event handlers
    def _handle_new_set(self) -> None:
        """Handle new question set creation."""
        name = tk.simpledialog.askstring(
            "New Question Set", "Enter name for the new question set:", parent=self
        )

        if name and name.strip():
            try:
                set_name = self.question_set_service.create_question_set(name.strip())
                self._refresh_question_sets()
                self.logger.info(f"Created new question set: {name}")

                # Select the new set
                question_sets = self.question_set_service.get_all_question_sets()
                set_names = list(question_sets.keys())
                if set_name in set_names:
                    index = set_names.index(set_name)
                    self.set_listbox.selection_set(index)
                    self._load_questions_for_set(set_name)

            except Exception as e:
                messagebox.showerror("Error", f"Failed to create question set: {e}")

    def _handle_delete_set(self) -> None:
        """Handle question set deletion."""
        if not self.current_set_name:
            messagebox.showwarning("No Selection", "Please select a question set to delete.")
            return

        question_set = self.question_set_service.get_question_set(self.current_set_name)
        if not question_set:
            return

        # Confirm deletion
        if messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete the question set '{question_set.name}'?\n\nThis action cannot be undone.",
        ):
            try:
                self.question_set_service.delete_question_set(self.current_set_name)
                self.current_set_name = None
                self.selected_question_index = None
                self._refresh_question_sets()
                self.logger.info(f"Deleted question set: {question_set.name}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete question set: {e}")

    def _handle_import_set(self) -> None:
        """Handle question set import."""
        file_path = filedialog.askopenfilename(
            title="Import Question Set",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
            parent=self,
        )

        if file_path:
            try:
                from pathlib import Path

                set_name = self.question_set_service.import_question_set(Path(file_path))
                self._refresh_question_sets()

                # Select the imported set
                question_sets = self.question_set_service.get_all_question_sets()
                set_names = list(question_sets.keys())
                if set_name in set_names:
                    index = set_names.index(set_name)
                    self.set_listbox.selection_set(index)
                    self._load_questions_for_set(set_name)

                messagebox.showinfo("Success", "Question set imported successfully!")
                self.logger.info(f"Imported question set from: {file_path}")
            except Exception as e:
                messagebox.showerror("Import Error", f"Failed to import question set: {e}")

    def _handle_export_set(self) -> None:
        """Handle question set export."""
        if not self.current_set_name:
            messagebox.showwarning("No Selection", "Please select a question set to export.")
            return

        question_set = self.question_set_service.get_question_set(self.current_set_name)
        if not question_set:
            return

        file_path = filedialog.asksaveasfilename(
            title="Export Question Set",
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
            initialvalue=f"{question_set.name}.json",
            parent=self,
        )

        if file_path:
            try:
                from pathlib import Path

                self.question_set_service.export_question_set(
                    self.current_set_name, Path(file_path)
                )
                messagebox.showinfo("Success", "Question set exported successfully!")
                self.logger.info(f"Exported question set to: {file_path}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export question set: {e}")

    def _handle_add_question(self) -> None:
        """Handle adding a new question."""
        if not self.current_set_name:
            messagebox.showwarning("No Set Selected", "Please select a question set first.")
            return

        # For now, show a simple dialog - will be replaced with full editor
        self._show_simple_question_dialog()

    def _handle_edit_question(self) -> None:
        """Handle editing the selected question."""
        if not self.current_set_name or self.selected_question_index is None:
            messagebox.showwarning("No Selection", "Please select a question to edit.")
            return

        # For now, show a simple dialog - will be replaced with full editor
        self._show_simple_question_dialog(edit_index=self.selected_question_index)

    def _handle_delete_question(self) -> None:
        """Handle deleting the selected question."""
        if not self.current_set_name or self.selected_question_index is None:
            messagebox.showwarning("No Selection", "Please select a question to delete.")
            return

        question_set = self.question_set_service.get_question_set(self.current_set_name)
        if not question_set:
            return

        question = question_set.get_question(self.selected_question_index)
        if not question:
            return

        # Confirm deletion
        if messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete this question?\n\n'{question.question[:100]}...'",
        ):
            try:
                question_set.remove_question(self.selected_question_index)
                self.selected_question_index = None
                self._refresh_questions()
                self.logger.info("Deleted question")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete question: {e}")

    def _handle_save(self) -> None:
        """Handle saving the current question set."""
        if not self.current_set_name:
            messagebox.showwarning("No Set Selected", "Please select a question set to save.")
            return

        question_set = self.question_set_service.get_question_set(self.current_set_name)
        if not question_set:
            return

        try:
            self.question_set_service.save_question_set(question_set, self.current_set_name)
            messagebox.showinfo("Success", "Question set saved successfully!")
            self.logger.info(f"Saved question set: {question_set.name}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save question set: {e}")

    def _handle_use_set(self) -> None:
        """Handle using the selected question set."""
        if not self.current_set_name:
            messagebox.showwarning("No Set Selected", "Please select a question set to use.")
            return

        if self.on_use_set:
            self.on_use_set(self.current_set_name)

    def _handle_back(self) -> None:
        """Handle back button click."""
        if self.on_back:
            self.on_back()

    def _show_simple_question_dialog(self, edit_index: Optional[int] = None) -> None:
        """Show a comprehensive question editing dialog with media support."""
        # Create dialog window
        dialog = tk.Toplevel(self)
        dialog.title("Add Question" if edit_index is None else "Edit Question")
        dialog.configure(bg=ColorConfig.PRIMARY_BG)
        dialog.transient(self)
        dialog.grab_set()

        # Set size and center immediately to avoid positioning jump
        dialog_width = 700
        dialog_height = 600
        screen_width = dialog.winfo_screenwidth()
        screen_height = dialog.winfo_screenheight()
        x = (screen_width // 2) - (dialog_width // 2)
        y = (screen_height // 2) - (dialog_height // 2)
        dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")

        # Ensure dialog appears on top
        dialog.lift()
        dialog.focus_force()

        # Get existing question data if editing
        existing_question = None
        if edit_index is not None:
            question_set = self.question_set_service.get_question_set(self.current_set_name)
            if question_set:
                existing_question = question_set.get_question(edit_index)

        # Media references for tracking selections
        tile_image_ref = None
        question_image_ref = None
        question_audio_ref = None

        # Extract existing media references if editing
        if existing_question:
            if isinstance(existing_question.tile_image, MediaReference):
                tile_image_ref = existing_question.tile_image
            if isinstance(existing_question.question_image, MediaReference):
                question_image_ref = existing_question.question_image
            if isinstance(existing_question.question_audio, MediaReference):
                question_audio_ref = existing_question.question_audio

        # Create scrollable frame
        canvas = tk.Canvas(dialog, bg=ColorConfig.PRIMARY_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=ColorConfig.PRIMARY_BG)

        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Enable trackpad/mouse wheel scrolling
        def _on_mousewheel(event):
            # For macOS, event.delta contains the scroll amount
            # Negative delta means scroll down, positive means scroll up
            scroll_amount = int(-1 * (event.delta / 120))
            canvas.yview_scroll(scroll_amount, "units")

        # Bind mouse wheel events to canvas for trackpad support
        canvas.bind("<MouseWheel>", _on_mousewheel)  # Windows/Linux
        canvas.bind("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))  # Linux scroll up
        canvas.bind("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))  # Linux scroll down

        # Make sure canvas can receive focus for scroll events
        canvas.focus_set()

        canvas.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        scrollbar.pack(side="right", fill="y", pady=20)

        # Main content frame
        main_frame = scrollable_frame

        # Title
        title_text = "Add New Question" if edit_index is None else "Edit Question"
        tk.Label(
            main_frame,
            text=title_text,
            font=(FontConfig.FAMILY, FontConfig.TITLE_SIZE, "bold"),
            bg=ColorConfig.PRIMARY_BG,
            fg=ColorConfig.GOLD,
        ).pack(pady=(0, 20))

        # Question text
        tk.Label(
            main_frame,
            text="Question:",
            font=(FontConfig.FAMILY, FontConfig.LABEL_SIZE),
            bg=ColorConfig.PRIMARY_BG,
            fg=ColorConfig.PRIMARY_TEXT,
        ).pack(anchor="w")

        question_text = tk.Text(
            main_frame,
            height=4,
            font=(FontConfig.FAMILY, FontConfig.SMALL_SIZE),
            bg=ColorConfig.ENTRY_BG,
            fg=ColorConfig.PRIMARY_TEXT,
            wrap=tk.WORD,
        )
        question_text.pack(fill=tk.X, pady=(5, 15))

        # Answer
        tk.Label(
            main_frame,
            text="Answer:",
            font=(FontConfig.FAMILY, FontConfig.LABEL_SIZE),
            bg=ColorConfig.PRIMARY_BG,
            fg=ColorConfig.PRIMARY_TEXT,
        ).pack(anchor="w")

        answer_var = tk.StringVar()
        answer_entry = tk.Entry(
            main_frame,
            textvariable=answer_var,
            font=(FontConfig.FAMILY, FontConfig.SMALL_SIZE),
            bg=ColorConfig.ENTRY_BG,
            fg=ColorConfig.PRIMARY_TEXT,
        )
        answer_entry.pack(fill=tk.X, pady=(5, 15))

        # Points
        tk.Label(
            main_frame,
            text="Points:",
            font=(FontConfig.FAMILY, FontConfig.LABEL_SIZE),
            bg=ColorConfig.PRIMARY_BG,
            fg=ColorConfig.PRIMARY_TEXT,
        ).pack(anchor="w")

        points_var = tk.StringVar(value="10")
        points_frame = tk.Frame(main_frame, bg=ColorConfig.PRIMARY_BG)
        points_frame.pack(fill=tk.X, pady=(5, 20))

        points_combo = ttk.Combobox(
            points_frame,
            textvariable=points_var,
            values=["5", "10", "15", "20", "25", "30", "50", "100"],
            width=10,
            font=(FontConfig.FAMILY, FontConfig.SMALL_SIZE),
            state="readonly",
        )
        points_combo.pack(side=tk.LEFT)

        # Media section separator
        separator = tk.Frame(main_frame, height=2, bg=ColorConfig.SECONDARY_COLOR)
        separator.pack(fill=tk.X, pady=20)

        # Media section title
        tk.Label(
            main_frame,
            text="Media Files (Optional)",
            font=(FontConfig.FAMILY, FontConfig.LABEL_SIZE, "bold"),
            bg=ColorConfig.PRIMARY_BG,
            fg=ColorConfig.GOLD,
        ).pack(pady=(0, 15))

        # Tile Image section
        tile_frame = tk.Frame(main_frame, bg=ColorConfig.SECONDARY_BG, relief=tk.RAISED, bd=1)
        tile_frame.pack(fill=tk.X, pady=(0, 10), padx=5)

        tk.Label(
            tile_frame,
            text="Tile Image:",
            font=(FontConfig.FAMILY, FontConfig.LABEL_SIZE),
            bg=ColorConfig.SECONDARY_BG,
            fg=ColorConfig.PRIMARY_TEXT,
        ).pack(anchor="w", padx=10, pady=(10, 5))

        tile_info_var = tk.StringVar(value="No tile image selected")
        tile_info_label = tk.Label(
            tile_frame,
            textvariable=tile_info_var,
            font=(FontConfig.FAMILY, FontConfig.SMALL_SIZE),
            bg=ColorConfig.SECONDARY_BG,
            fg=ColorConfig.MUTED_TEXT,
        )
        tile_info_label.pack(anchor="w", padx=10)

        def select_tile_image():
            nonlocal tile_image_ref
            if hasattr(self.app, "media_service"):
                browser = MediaBrowserDialog(
                    dialog, self.app.media_service, "image", "Select Tile Image"
                )
                result = browser.show()
                if result:
                    tile_image_ref = result
                    tile_info_var.set(f"Selected: {result.filename}")

        def clear_tile_image():
            nonlocal tile_image_ref
            tile_image_ref = None
            tile_info_var.set("No tile image selected")

        tile_buttons = tk.Frame(tile_frame, bg=ColorConfig.SECONDARY_BG)
        tile_buttons.pack(fill=tk.X, padx=10, pady=(5, 10))

        # Select tile image button container
        select_tile_container = tk.Frame(tile_buttons, bg=ColorConfig.SECONDARY_BG)
        select_tile_container.pack(side=tk.LEFT, padx=(0, 5))

        select_tile_frame, select_tile_label = self.create_clickable_frame(
            select_tile_container,
            "Select Image",
            ColorConfig.PRIMARY_COLOR,
            row=0,
            col=0,
            command=select_tile_image,
            width=100,
            height=30,
            font=(FontConfig.FAMILY, FontConfig.SMALL_SIZE, "bold"),
        )

        # Clear tile image button container
        clear_tile_container = tk.Frame(tile_buttons, bg=ColorConfig.SECONDARY_BG)
        clear_tile_container.pack(side=tk.LEFT)

        clear_tile_frame, clear_tile_label = self.create_clickable_frame(
            clear_tile_container,
            "Clear",
            ColorConfig.SECONDARY_COLOR,
            row=0,
            col=0,
            command=clear_tile_image,
            width=60,
            height=30,
            font=(FontConfig.FAMILY, FontConfig.SMALL_SIZE, "bold"),
        )

        # Question Image section
        question_img_frame = tk.Frame(
            main_frame, bg=ColorConfig.SECONDARY_BG, relief=tk.RAISED, bd=1
        )
        question_img_frame.pack(fill=tk.X, pady=(0, 10), padx=5)

        tk.Label(
            question_img_frame,
            text="Question Image:",
            font=(FontConfig.FAMILY, FontConfig.LABEL_SIZE),
            bg=ColorConfig.SECONDARY_BG,
            fg=ColorConfig.PRIMARY_TEXT,
        ).pack(anchor="w", padx=10, pady=(10, 5))

        question_img_info_var = tk.StringVar(value="No question image selected")
        question_img_info_label = tk.Label(
            question_img_frame,
            textvariable=question_img_info_var,
            font=(FontConfig.FAMILY, FontConfig.SMALL_SIZE),
            bg=ColorConfig.SECONDARY_BG,
            fg=ColorConfig.MUTED_TEXT,
        )
        question_img_info_label.pack(anchor="w", padx=10)

        def select_question_image():
            nonlocal question_image_ref
            if hasattr(self.app, "media_service"):
                browser = MediaBrowserDialog(
                    dialog, self.app.media_service, "image", "Select Question Image"
                )
                result = browser.show()
                if result:
                    question_image_ref = result
                    question_img_info_var.set(f"Selected: {result.filename}")

        def clear_question_image():
            nonlocal question_image_ref
            question_image_ref = None
            question_img_info_var.set("No question image selected")

        question_img_buttons = tk.Frame(question_img_frame, bg=ColorConfig.SECONDARY_BG)
        question_img_buttons.pack(fill=tk.X, padx=10, pady=(5, 10))

        # Select question image button container
        select_question_img_container = tk.Frame(question_img_buttons, bg=ColorConfig.SECONDARY_BG)
        select_question_img_container.pack(side=tk.LEFT, padx=(0, 5))

        select_question_img_frame, select_question_img_label = self.create_clickable_frame(
            select_question_img_container,
            "Select Image",
            ColorConfig.PRIMARY_COLOR,
            row=0,
            col=0,
            command=select_question_image,
            width=100,
            height=30,
            font=(FontConfig.FAMILY, FontConfig.SMALL_SIZE, "bold"),
        )

        # Clear question image button container
        clear_question_img_container = tk.Frame(question_img_buttons, bg=ColorConfig.SECONDARY_BG)
        clear_question_img_container.pack(side=tk.LEFT)

        clear_question_img_frame, clear_question_img_label = self.create_clickable_frame(
            clear_question_img_container,
            "Clear",
            ColorConfig.SECONDARY_COLOR,
            row=0,
            col=0,
            command=clear_question_image,
            width=60,
            height=30,
            font=(FontConfig.FAMILY, FontConfig.SMALL_SIZE, "bold"),
        )

        # Question Audio section
        audio_frame = tk.Frame(main_frame, bg=ColorConfig.SECONDARY_BG, relief=tk.RAISED, bd=1)
        audio_frame.pack(fill=tk.X, pady=(0, 20), padx=5)

        tk.Label(
            audio_frame,
            text="Question Audio:",
            font=(FontConfig.FAMILY, FontConfig.LABEL_SIZE),
            bg=ColorConfig.SECONDARY_BG,
            fg=ColorConfig.PRIMARY_TEXT,
        ).pack(anchor="w", padx=10, pady=(10, 5))

        audio_info_var = tk.StringVar(value="No question audio selected")
        audio_info_label = tk.Label(
            audio_frame,
            textvariable=audio_info_var,
            font=(FontConfig.FAMILY, FontConfig.SMALL_SIZE),
            bg=ColorConfig.SECONDARY_BG,
            fg=ColorConfig.MUTED_TEXT,
        )
        audio_info_label.pack(anchor="w", padx=10)

        def select_question_audio():
            nonlocal question_audio_ref
            if hasattr(self.app, "media_service"):
                browser = MediaBrowserDialog(
                    dialog, self.app.media_service, "audio", "Select Question Audio"
                )
                result = browser.show()
                if result:
                    question_audio_ref = result
                    audio_info_var.set(f"Selected: {result.filename}")

        def clear_question_audio():
            nonlocal question_audio_ref
            question_audio_ref = None
            audio_info_var.set("No question audio selected")

        audio_buttons = tk.Frame(audio_frame, bg=ColorConfig.SECONDARY_BG)
        audio_buttons.pack(fill=tk.X, padx=10, pady=(5, 10))

        # Select audio button container
        select_audio_container = tk.Frame(audio_buttons, bg=ColorConfig.SECONDARY_BG)
        select_audio_container.pack(side=tk.LEFT, padx=(0, 5))

        select_audio_frame, select_audio_label = self.create_clickable_frame(
            select_audio_container,
            "Select Audio",
            ColorConfig.PRIMARY_COLOR,
            row=0,
            col=0,
            command=select_question_audio,
            width=100,
            height=30,
            font=(FontConfig.FAMILY, FontConfig.SMALL_SIZE, "bold"),
        )

        # Clear audio button container
        clear_audio_container = tk.Frame(audio_buttons, bg=ColorConfig.SECONDARY_BG)
        clear_audio_container.pack(side=tk.LEFT)

        clear_audio_frame, clear_audio_label = self.create_clickable_frame(
            clear_audio_container,
            "Clear",
            ColorConfig.SECONDARY_COLOR,
            row=0,
            col=0,
            command=clear_question_audio,
            width=60,
            height=30,
            font=(FontConfig.FAMILY, FontConfig.SMALL_SIZE, "bold"),
        )

        # Fill in existing data if editing
        if existing_question:
            question_text.insert("1.0", existing_question.question)
            answer_var.set(existing_question.answer)
            points_var.set(str(existing_question.points))

            # Update media display
            if tile_image_ref:
                tile_info_var.set(f"Selected: {tile_image_ref.filename}")
            if question_image_ref:
                question_img_info_var.set(f"Selected: {question_image_ref.filename}")
            if question_audio_ref:
                audio_info_var.set(f"Selected: {question_audio_ref.filename}")

        # Buttons
        button_frame = tk.Frame(main_frame, bg=ColorConfig.PRIMARY_BG)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(20, 0))
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=0)
        button_frame.grid_columnconfigure(2, weight=0)

        def save_question():
            q_text = question_text.get("1.0", tk.END).strip()
            a_text = answer_var.get().strip()
            p_value = points_var.get()

            if not q_text or not a_text:
                messagebox.showerror("Validation Error", "Question and answer are required.")
                return

            try:
                points = int(p_value)
                question = Question(
                    question=q_text,
                    answer=a_text,
                    points=points,
                    tile_image=tile_image_ref,
                    question_image=question_image_ref,
                    question_audio=question_audio_ref,
                )

                question_set = self.question_set_service.get_question_set(self.current_set_name)
                if question_set:
                    if edit_index is not None:
                        question_set.update_question(edit_index, question)
                    else:
                        question_set.add_question(question)

                    self._refresh_questions()
                    dialog.destroy()

            except ValueError:
                messagebox.showerror("Validation Error", "Points must be a valid number.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save question: {e}")

        # Cancel button container
        cancel_container = tk.Frame(button_frame, bg=ColorConfig.PRIMARY_BG)
        cancel_container.grid(row=0, column=1, padx=(0, 5))

        cancel_frame, cancel_label = self.create_clickable_frame(
            cancel_container,
            "Cancel",
            ColorConfig.SECONDARY_COLOR,
            row=0,
            col=0,
            command=dialog.destroy,
            width=80,
            height=35,
            font=(FontConfig.FAMILY, FontConfig.SMALL_SIZE, "bold"),
        )

        # Save button container
        save_container = tk.Frame(button_frame, bg=ColorConfig.PRIMARY_BG)
        save_container.grid(row=0, column=2, padx=(5, 0))

        save_frame, save_label = self.create_clickable_frame(
            save_container,
            "Save",
            ColorConfig.SUCCESS_COLOR,
            row=0,
            col=0,
            command=save_question,
            width=80,
            height=35,
            font=(FontConfig.FAMILY, FontConfig.SMALL_SIZE, "bold"),
        )

        # Focus on question text
        question_text.focus_set()

    def resize_widgets(self) -> None:
        """Resize widgets for the current window size."""
        # This will be implemented when the full UI is complete
        pass
