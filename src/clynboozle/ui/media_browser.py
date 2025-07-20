"""Media browser dialog for selecting media files."""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Optional, Callable, Dict, Any, List, Tuple
from pathlib import Path

from ..config.settings import ColorConfig, FontConfig, WindowConfig
from ..services.media_service import MediaService, MediaInfo
from ..models.question import MediaReference
from .base_frame import BaseFrame


class MediaBrowserDialog:
    """A dialog for browsing and selecting media files from the media library."""

    def __init__(
        self,
        parent: tk.Widget,
        media_service: MediaService,
        media_type: str = "image",
        title: str = "Select Media",
    ) -> None:
        """
        Initialize the media browser dialog.

        Args:
            parent: Parent widget
            media_service: Media service instance
            media_type: Type of media to browse ("image" or "audio")
            title: Dialog title
        """
        self.parent = parent
        self.media_service = media_service
        self.media_type = media_type
        self.title = title
        self.result: Optional[MediaReference] = None

        # UI components
        self.dialog: Optional[tk.Toplevel] = None
        self.media_listbox: Optional[tk.Listbox] = None
        self.preview_label: Optional[tk.Label] = None
        self.info_frame: Optional[tk.Frame] = None
        self.info_text: Optional[tk.Text] = None

        # Data
        self.media_items: List[MediaInfo] = []
        self.selected_media: Optional[MediaInfo] = None

    def create_clickable_frame(
        self,
        parent: tk.Widget,
        text: str,
        bg_color: str,
        row: int,
        col: int,
        command: Optional[Callable[[], None]] = None,
        width: int = 120,
        height: int = 40,
        font: Tuple[str, int, str] = (FontConfig.FAMILY, FontConfig.BUTTON_SIZE, "bold"),
        fg_color: str = ColorConfig.PRIMARY_TEXT,
        hover_color: Optional[str] = None,
        sticky: str = "",
        padx: int = 0,
        pady: int = 0,
    ) -> Tuple[tk.Frame, tk.Label]:
        """
        Create a clickable frame that looks and behaves like a button.

        This is a simplified version of BaseFrame.create_clickable_frame
        specifically for the MediaBrowserDialog.
        """
        if hover_color is None:
            # Create a slightly darker version of bg_color for hover
            hover_color = self._darken_color(bg_color)

        frame = tk.Frame(
            parent, bg=bg_color, relief=tk.RAISED, bd=1, width=width, height=height, cursor="hand2"
        )
        frame.grid(row=row, column=col, sticky=sticky, padx=padx, pady=pady)
        frame.grid_propagate(False)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        label = tk.Label(frame, text=text, font=font, bg=bg_color, fg=fg_color, cursor="hand2")
        label.grid(row=0, column=0, sticky="nsew")

        # Bind click events
        if command:
            frame.bind("<Button-1>", lambda e: command())
            label.bind("<Button-1>", lambda e: command())

        # Bind hover effects
        def on_enter(event):
            frame.configure(bg=hover_color, relief=tk.RAISED, bd=2)
            label.configure(bg=hover_color)

        def on_leave(event):
            frame.configure(bg=bg_color, relief=tk.RAISED, bd=1)
            label.configure(bg=bg_color)

        frame.bind("<Enter>", on_enter)
        frame.bind("<Leave>", on_leave)
        label.bind("<Enter>", on_enter)
        label.bind("<Leave>", on_leave)

        return frame, label

    def _disable_select_button(self) -> None:
        """Disable the select button by changing its appearance and removing click handler."""
        if hasattr(self, "select_frame") and hasattr(self, "select_label"):
            # Change to muted colors
            disabled_color = ColorConfig.MUTED_TEXT
            self.select_frame.configure(bg=disabled_color, cursor="")
            self.select_label.configure(bg=disabled_color, fg=ColorConfig.SECONDARY_BG, cursor="")

            # Remove click bindings
            self.select_frame.unbind("<Button-1>")
            self.select_label.unbind("<Button-1>")
            self.select_frame.unbind("<Enter>")
            self.select_frame.unbind("<Leave>")
            self.select_label.unbind("<Enter>")
            self.select_label.unbind("<Leave>")

    def _enable_select_button(self) -> None:
        """Enable the select button by restoring its appearance and click handler."""
        if hasattr(self, "select_frame") and hasattr(self, "select_label"):
            # Restore normal colors
            normal_color = ColorConfig.PRIMARY_COLOR
            hover_color = self._darken_color(normal_color)

            self.select_frame.configure(bg=normal_color, cursor="hand2")
            self.select_label.configure(
                bg=normal_color, fg=ColorConfig.PRIMARY_TEXT, cursor="hand2"
            )

            # Restore click bindings
            self.select_frame.bind("<Button-1>", lambda e: self._on_select())
            self.select_label.bind("<Button-1>", lambda e: self._on_select())

            # Restore hover effects
            def on_enter(event):
                self.select_frame.configure(bg=hover_color, relief=tk.RAISED, bd=2)
                self.select_label.configure(bg=hover_color)

            def on_leave(event):
                self.select_frame.configure(bg=normal_color, relief=tk.RAISED, bd=1)
                self.select_label.configure(bg=normal_color)

            self.select_frame.bind("<Enter>", on_enter)
            self.select_frame.bind("<Leave>", on_leave)
            self.select_label.bind("<Enter>", on_enter)
            self.select_label.bind("<Leave>", on_leave)

    def _darken_color(self, color: str, factor: float = 0.8) -> str:
        """Darken a hex color by the given factor."""
        try:
            # Remove '#' if present
            color = color.lstrip("#")

            # Convert to RGB
            r = int(color[0:2], 16)
            g = int(color[2:4], 16)
            b = int(color[4:6], 16)

            # Darken
            r = int(r * factor)
            g = int(g * factor)
            b = int(b * factor)

            # Convert back to hex
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            # Fallback to original color if parsing fails
            return color

    def show(self) -> Optional[MediaReference]:
        """
        Show the media browser dialog and return selected media reference.

        Returns:
            MediaReference if media was selected, None if cancelled
        """
        self._create_dialog()
        self._setup_ui()
        self._load_media_list()

        # Center and focus the dialog properly
        self._center_dialog()

        # Make modal with proper focus
        self.dialog.transient(self.parent)
        self.dialog.grab_set()

        # Ensure dialog is on top and focused
        self.dialog.lift()
        self.dialog.focus_force()
        self.dialog.attributes("-topmost", True)  # Bring to front
        self.dialog.after(
            100, lambda: self.dialog.attributes("-topmost", False)
        )  # Remove topmost after showing

        # Wait for dialog to close
        self.parent.wait_window(self.dialog)

        return self.result

    def _create_dialog(self) -> None:
        """Create the main dialog window."""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(self.title)
        self.dialog.configure(bg=ColorConfig.PRIMARY_BG)
        self.dialog.resizable(True, True)

        # Set initial size and center immediately
        width, height = 900, 600
        screen_width = self.dialog.winfo_screenwidth()
        screen_height = self.dialog.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")

        # Configure grid
        self.dialog.grid_columnconfigure(0, weight=1)
        self.dialog.grid_columnconfigure(1, weight=1)
        self.dialog.grid_rowconfigure(1, weight=1)

        # Handle close button
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_cancel)

    def _setup_ui(self) -> None:
        """Setup the user interface."""
        self._create_header()
        self._create_content_area()
        self._create_footer()

    def _create_header(self) -> None:
        """Create the header with title and upload button."""
        header_frame = tk.Frame(self.dialog, bg=ColorConfig.PRIMARY_BG)
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        header_frame.grid_columnconfigure(0, weight=1)

        # Title
        title_label = tk.Label(
            header_frame,
            text=f"Media Library - {self.media_type.title()}s",
            font=(FontConfig.FAMILY, FontConfig.TITLE_SIZE, "bold"),
            bg=ColorConfig.PRIMARY_BG,
            fg=ColorConfig.GOLD,
        )
        title_label.grid(row=0, column=0, sticky="w")

        # Buttons frame
        buttons_frame = tk.Frame(header_frame, bg=ColorConfig.PRIMARY_BG)
        buttons_frame.grid(row=0, column=1, sticky="e")
        buttons_frame.grid_columnconfigure(0, weight=0)
        buttons_frame.grid_columnconfigure(1, weight=0)

        # Upload button container
        upload_container = tk.Frame(buttons_frame, bg=ColorConfig.PRIMARY_BG)
        upload_container.grid(row=0, column=0, padx=(0, 5))

        upload_frame, upload_label = self.create_clickable_frame(
            upload_container,
            f"Upload {self.media_type.title()}",
            ColorConfig.SUCCESS_COLOR,
            row=0,
            col=0,
            command=self._handle_upload,
            width=140,
            height=30,
            font=(FontConfig.FAMILY, FontConfig.SMALL_SIZE, "bold"),
        )

        # Refresh button container
        refresh_container = tk.Frame(buttons_frame, bg=ColorConfig.PRIMARY_BG)
        refresh_container.grid(row=0, column=1)

        refresh_frame, refresh_label = self.create_clickable_frame(
            refresh_container,
            "Refresh",
            ColorConfig.SECONDARY_COLOR,
            row=0,
            col=0,
            command=self._load_media_list,
            width=80,
            height=30,
            font=(FontConfig.FAMILY, FontConfig.SMALL_SIZE, "bold"),
        )

    def _create_content_area(self) -> None:
        """Create the main content area with media list and preview."""
        # Left side - Media list
        self._create_media_list()

        # Right side - Preview and info
        self._create_preview_area()

    def _create_media_list(self) -> None:
        """Create the media list on the left side."""
        list_frame = tk.Frame(self.dialog, bg=ColorConfig.SECONDARY_BG, relief=tk.RAISED, bd=1)
        list_frame.grid(row=1, column=0, sticky="nsew", padx=(10, 5), pady=(0, 10))
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(1, weight=1)

        # List header
        list_header = tk.Label(
            list_frame,
            text="Media Files",
            font=(FontConfig.FAMILY, FontConfig.LABEL_SIZE, "bold"),
            bg=ColorConfig.SECONDARY_BG,
            fg=ColorConfig.PRIMARY_TEXT,
        )
        list_header.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 5))

        # Create listbox with scrollbar
        list_container = tk.Frame(list_frame, bg=ColorConfig.SECONDARY_BG)
        list_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        list_container.grid_columnconfigure(0, weight=1)
        list_container.grid_rowconfigure(0, weight=1)

        self.media_listbox = tk.Listbox(
            list_container,
            bg=ColorConfig.ENTRY_BG,
            fg=ColorConfig.PRIMARY_TEXT,
            selectbackground=ColorConfig.PRIMARY_COLOR,
            selectforeground=ColorConfig.PRIMARY_TEXT,
            font=(FontConfig.FAMILY, FontConfig.SMALL_SIZE),
        )
        self.media_listbox.grid(row=0, column=0, sticky="nsew")

        # Scrollbar
        scrollbar = ttk.Scrollbar(
            list_container, orient=tk.VERTICAL, command=self.media_listbox.yview
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.media_listbox.configure(yscrollcommand=scrollbar.set)

        # Bind selection events
        self.media_listbox.bind("<<ListboxSelect>>", self._on_media_selection_changed)
        self.media_listbox.bind("<Double-1>", lambda e: self._on_select())

    def _create_preview_area(self) -> None:
        """Create the preview area on the right side."""
        preview_frame = tk.Frame(self.dialog, bg=ColorConfig.SECONDARY_BG, relief=tk.RAISED, bd=1)
        preview_frame.grid(row=1, column=1, sticky="nsew", padx=(5, 10), pady=(0, 10))
        preview_frame.grid_columnconfigure(0, weight=1)
        preview_frame.grid_rowconfigure(1, weight=1)

        # Preview header
        preview_header = tk.Label(
            preview_frame,
            text="Preview",
            font=(FontConfig.FAMILY, FontConfig.LABEL_SIZE, "bold"),
            bg=ColorConfig.SECONDARY_BG,
            fg=ColorConfig.PRIMARY_TEXT,
        )
        preview_header.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 5))

        # Preview content area
        preview_content = tk.Frame(preview_frame, bg=ColorConfig.SECONDARY_BG)
        preview_content.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 5))
        preview_content.grid_columnconfigure(0, weight=1)
        preview_content.grid_rowconfigure(0, weight=1)

        # Preview label for images
        self.preview_label = tk.Label(
            preview_content,
            bg=ColorConfig.SECONDARY_BG,
            fg=ColorConfig.MUTED_TEXT,
            text="Select a media file to preview",
            font=(FontConfig.FAMILY, FontConfig.SMALL_SIZE),
        )
        self.preview_label.grid(row=0, column=0, sticky="nsew")

        # Info area
        info_header = tk.Label(
            preview_frame,
            text="Information",
            font=(FontConfig.FAMILY, FontConfig.LABEL_SIZE, "bold"),
            bg=ColorConfig.SECONDARY_BG,
            fg=ColorConfig.PRIMARY_TEXT,
        )
        info_header.grid(row=2, column=0, sticky="w", padx=10, pady=(10, 5))

        # Info text area
        info_container = tk.Frame(preview_frame, bg=ColorConfig.SECONDARY_BG)
        info_container.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 10))
        info_container.grid_columnconfigure(0, weight=1)

        self.info_text = tk.Text(
            info_container,
            height=6,
            bg=ColorConfig.ENTRY_BG,
            fg=ColorConfig.PRIMARY_TEXT,
            font=(FontConfig.FAMILY, FontConfig.SMALL_SIZE),
            wrap=tk.WORD,
            state=tk.DISABLED,
        )
        self.info_text.grid(row=0, column=0, sticky="ew")

        # Info scrollbar
        info_scrollbar = ttk.Scrollbar(
            info_container, orient=tk.VERTICAL, command=self.info_text.yview
        )
        info_scrollbar.grid(row=0, column=1, sticky="ns")
        self.info_text.configure(yscrollcommand=info_scrollbar.set)

    def _create_footer(self) -> None:
        """Create the footer with action buttons."""
        footer_frame = tk.Frame(self.dialog, bg=ColorConfig.PRIMARY_BG)
        footer_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        footer_frame.grid_columnconfigure(0, weight=1)

        # Buttons frame
        buttons_frame = tk.Frame(footer_frame, bg=ColorConfig.PRIMARY_BG)
        buttons_frame.pack(side=tk.RIGHT)
        buttons_frame.grid_columnconfigure(0, weight=0)
        buttons_frame.grid_columnconfigure(1, weight=0)

        # Cancel button container
        cancel_container = tk.Frame(buttons_frame, bg=ColorConfig.PRIMARY_BG)
        cancel_container.grid(row=0, column=0, padx=(0, 5))

        cancel_frame, cancel_label = self.create_clickable_frame(
            cancel_container,
            "Cancel",
            ColorConfig.SECONDARY_COLOR,
            row=0,
            col=0,
            command=self._on_cancel,
            width=80,
            height=35,
            font=(FontConfig.FAMILY, FontConfig.BUTTON_SIZE, "bold"),
        )

        # Select button container
        select_container = tk.Frame(buttons_frame, bg=ColorConfig.PRIMARY_BG)
        select_container.grid(row=0, column=1)

        self.select_frame, self.select_label = self.create_clickable_frame(
            select_container,
            "Select",
            ColorConfig.PRIMARY_COLOR,
            row=0,
            col=0,
            command=self._on_select,
            width=80,
            height=35,
            font=(FontConfig.FAMILY, FontConfig.BUTTON_SIZE, "bold"),
        )

        # Initially disable the select button by changing colors and removing command
        self._disable_select_button()

    def _center_dialog(self) -> None:
        """Center the dialog on the parent window."""
        self.dialog.update_idletasks()

        # Get dialog size
        dialog_width = self.dialog.winfo_width()
        dialog_height = self.dialog.winfo_height()

        # Get parent window position and size
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()

        # Calculate centered position
        x = parent_x + (parent_width // 2) - (dialog_width // 2)
        y = parent_y + (parent_height // 2) - (dialog_height // 2)

        # Ensure dialog stays on screen
        x = max(0, x)
        y = max(0, y)

        self.dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")

    def _load_media_list(self) -> None:
        """Load and display the media list."""
        if not self.media_listbox:
            return

        # Clear current list
        self.media_listbox.delete(0, tk.END)
        self.media_items = []

        # Get media items of the specified type
        try:
            media_items = self.media_service.get_all_media(self.media_type)
            self.media_items = sorted(media_items, key=lambda x: x.upload_date, reverse=True)

            # Add to listbox
            for media_info in self.media_items:
                display_name = media_info.original_filename
                if media_info.description:
                    display_name += f" - {media_info.description[:50]}..."

                self.media_listbox.insert(tk.END, display_name)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load media list: {e}")

    def _on_media_selection_changed(self, event: tk.Event) -> None:
        """Handle media selection change."""
        if not self.media_listbox:
            return

        selection = self.media_listbox.curselection()
        if not selection:
            self.selected_media = None
            self._disable_select_button()
            self._clear_preview()
            return

        index = selection[0]
        if 0 <= index < len(self.media_items):
            self.selected_media = self.media_items[index]
            self._enable_select_button()
            self._update_preview()

    def _update_preview(self) -> None:
        """Update the preview area with selected media."""
        if not self.selected_media:
            self._clear_preview()
            return

        # Update preview image/placeholder
        if self.selected_media.media_type == "image":
            # Try to load image preview
            photo = self.media_service.load_image_for_display(self.selected_media.id, "thumbnail")
            if photo:
                self.preview_label.configure(image=photo, text="")
                self.preview_label.image = photo  # Keep a reference
            else:
                self.preview_label.configure(image="", text="[Image Preview Not Available]")
        else:
            # Audio placeholder
            self.preview_label.configure(image="", text="🔊 Audio File")

        # Update info text
        self._update_info_text()

    def _update_info_text(self) -> None:
        """Update the information text area."""
        if not self.info_text or not self.selected_media:
            return

        self.info_text.configure(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)

        # Format media information
        info_lines = [
            f"Filename: {self.selected_media.original_filename}",
            f"Type: {self.selected_media.media_type.title()}",
            f"Size: {self._format_file_size(self.selected_media.file_size)}",
            f"Upload Date: {self.selected_media.upload_date[:10]}",
        ]

        if self.selected_media.media_type == "image" and self.selected_media.dimensions:
            dims = self.selected_media.dimensions
            info_lines.append(f"Dimensions: {dims['width']} x {dims['height']}")

        if self.selected_media.description:
            info_lines.append(f"Description: {self.selected_media.description}")

        self.info_text.insert(tk.END, "\\n".join(info_lines))
        self.info_text.configure(state=tk.DISABLED)

    def _clear_preview(self) -> None:
        """Clear the preview area."""
        if self.preview_label:
            self.preview_label.configure(image="", text="Select a media file to preview")
            # Clear image reference
            self.preview_label.image = None

        if self.info_text:
            self.info_text.configure(state=tk.NORMAL)
            self.info_text.delete(1.0, tk.END)
            self.info_text.configure(state=tk.DISABLED)

    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format."""
        for unit in ["B", "KB", "MB", "GB"]:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"

    def _handle_upload(self) -> None:
        """Handle upload new media file."""
        # Determine file types based on media type
        if self.media_type == "image":
            file_types = [
                ("Image Files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp"),
                ("All Files", "*.*"),
            ]
        else:  # audio
            file_types = [
                ("Audio Files", "*.wav *.mp3 *.ogg *.flac *.aac"),
                ("All Files", "*.*"),
            ]

        # Show file dialog
        file_path = filedialog.askopenfilename(
            title=f"Select {self.media_type.title()} File",
            filetypes=file_types,
            parent=self.dialog,
        )

        if not file_path:
            return

        try:
            # Add media to library
            if self.media_type == "image":
                media_id = self.media_service.add_image(file_path)
            else:
                media_id = self.media_service.add_audio(file_path)

            # Refresh the list
            self._load_media_list()

            # Find and select the newly added item
            for i, media_info in enumerate(self.media_items):
                if media_info.id == media_id:
                    self.media_listbox.selection_set(i)
                    self.media_listbox.see(i)
                    self._on_media_selection_changed(None)
                    break

            messagebox.showinfo("Success", f"{self.media_type.title()} uploaded successfully!")

        except Exception as e:
            messagebox.showerror("Upload Error", f"Failed to upload {self.media_type}: {e}")

    def _on_select(self) -> None:
        """Handle select button click."""
        if not self.selected_media:
            return

        # Create MediaReference
        self.result = MediaReference(
            media_id=self.selected_media.id,
            media_type=self.selected_media.media_type,
            filename=self.selected_media.original_filename,
            description=self.selected_media.description,
        )

        self.dialog.destroy()

    def _on_cancel(self) -> None:
        """Handle cancel button click."""
        self.result = None
        self.dialog.destroy()
