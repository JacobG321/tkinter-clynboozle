import tkinter as tk
from tkinter import ttk, messagebox

class MediaBrowserDialog:
    """A dialog for browsing and managing media files"""
    
    def __init__(self, parent, media_manager, media_type="image", title="Select Media"):
        self.parent = parent
        self.media_manager = media_manager
        self.media_type = media_type  # "image" or "audio"
        self.title = title
        self.result = None
        
        self.dialog = None
        self.media_list = None
        self.preview_frame = None
        self.preview_label = None
        self.info_label = None
        
    def show(self):
        """Show the media browser dialog and return selected media info or None"""
        self._create_dialog()
        self._setup_ui()
        self._load_media_list()
        
        # Center the dialog
        self._center_on_parent()
        
        # Make modal
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        self.dialog.focus_set()
        
        # Wait for dialog to close
        self.parent.wait_window(self.dialog)
        
        return self.result
    
    def _create_dialog(self):
        """Create the main dialog window"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(self.title)
        self.dialog.geometry("800x600")
        self.dialog.configure(bg="#333333")
        self.dialog.resizable(True, True)
        
        # Configure grid
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.columnconfigure(1, weight=1)
        self.dialog.rowconfigure(1, weight=1)
    
    def _setup_ui(self):
        """Setup the user interface"""
        bg_color = "#333333"
        
        # Header
        header_frame = tk.Frame(self.dialog, bg=bg_color)
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        
        title_label = tk.Label(
            header_frame,
            text=f"Media Library - {self.media_type.title()}s",
            font=("Arial", 16, "bold"),
            bg=bg_color,
            fg="#FFD700"
        )
        title_label.pack(side=tk.LEFT)
        
        # Refresh button
        refresh_btn = tk.Button(
            header_frame,
            text="Refresh",
            command=self._load_media_list,
            bg="#666666",
            fg="white",
            font=("Arial", 10)
        )
        refresh_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Left side - Media list
        list_frame = tk.Frame(self.dialog, bg=bg_color)
        list_frame.grid(row=1, column=0, sticky="nsew", padx=(10, 5), pady=(0, 10))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # List header
        list_header = tk.Label(
            list_frame,
            text="Media Files",
            font=("Arial", 12, "bold"),
            bg=bg_color,
            fg="white"
        )
        list_header.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        # Create listbox with scrollbar
        list_container = tk.Frame(list_frame, bg=bg_color)
        list_container.grid(row=1, column=0, sticky="nsew")
        list_container.columnconfigure(0, weight=1)
        list_container.rowconfigure(0, weight=1)
        
        scrollbar = tk.Scrollbar(list_container)
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        self.media_list = tk.Listbox(
            list_container,
            bg="#444444",
            fg="white",
            font=("Arial", 10),
            selectbackground="#2196F3",
            yscrollcommand=scrollbar.set
        )
        self.media_list.grid(row=0, column=0, sticky="nsew")
        scrollbar.config(command=self.media_list.yview)
        
        # Bind selection event
        self.media_list.bind("<<ListboxSelect>>", self._on_media_select)
        
        # Right side - Preview and info
        preview_frame = tk.Frame(self.dialog, bg=bg_color)
        preview_frame.grid(row=1, column=1, sticky="nsew", padx=(5, 10), pady=(0, 10))
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(1, weight=1)
        
        # Preview header
        preview_header = tk.Label(
            preview_frame,
            text="Preview",
            font=("Arial", 12, "bold"),
            bg=bg_color,
            fg="white"
        )
        preview_header.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        # Preview area
        self.preview_frame = tk.Frame(
            preview_frame,
            bg="#444444",
            relief="sunken",
            bd=1
        )
        self.preview_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
        
        self.preview_label = tk.Label(
            self.preview_frame,
            text="No media selected",
            bg="#444444",
            fg="white",
            font=("Arial", 12)
        )
        self.preview_label.pack(expand=True, fill=tk.BOTH)
        
        # Info area
        info_frame = tk.Frame(preview_frame, bg=bg_color)
        info_frame.grid(row=2, column=0, sticky="ew")
        info_frame.columnconfigure(0, weight=1)
        
        info_header = tk.Label(
            info_frame,
            text="Information",
            font=("Arial", 10, "bold"),
            bg=bg_color,
            fg="white"
        )
        info_header.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        self.info_label = tk.Label(
            info_frame,
            text="",
            bg=bg_color,
            fg="white",
            font=("Arial", 9),
            justify=tk.LEFT,
            anchor="nw"
        )
        self.info_label.grid(row=1, column=0, sticky="ew")
        
        # Bottom buttons
        button_frame = tk.Frame(self.dialog, bg=bg_color)
        button_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        
        # Delete button
        delete_btn = tk.Button(
            button_frame,
            text="Delete Selected",
            command=self._delete_media,
            bg="#F44336",
            fg="white",
            font=("Arial", 10)
        )
        delete_btn.pack(side=tk.LEFT)
        
        # Cancel button
        cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            command=self._cancel,
            bg="#666666",
            fg="white",
            font=("Arial", 10)
        )
        cancel_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Select button
        select_btn = tk.Button(
            button_frame,
            text="Select",
            command=self._select_media,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10)
        )
        select_btn.pack(side=tk.RIGHT, padx=(5, 0))
    
    def _load_media_list(self):
        """Load the list of media files"""
        # Clear existing items
        self.media_list.delete(0, tk.END)
        
        # Get media of the specified type
        media_items = self.media_manager.get_all_media(self.media_type)
        
        # Store media info for easy access
        self.media_data = {}
        
        for media_id, media_info in media_items.items():
            filename = media_info.get("original_filename", "Unknown")
            self.media_list.insert(tk.END, filename)
            self.media_data[filename] = media_info
        
        if not media_items:
            self.media_list.insert(tk.END, "No media files found")
    
    def _on_media_select(self, event):
        """Handle media selection"""
        selection = self.media_list.curselection()
        if not selection:
            return
        
        filename = self.media_list.get(selection[0])
        if filename == "No media files found":
            return
        
        media_info = self.media_data.get(filename)
        if not media_info:
            return
        
        self._update_preview(media_info)
        self._update_info(media_info)
    
    def _update_preview(self, media_info):
        """Update the preview area"""
        if media_info["type"] == "image":
            # Show image preview
            try:
                media_id = media_info["id"]
                preview_image = self.media_manager.load_image_for_display(media_id, "thumbnail")
                if preview_image:
                    self.preview_label.configure(image=preview_image, text="")
                    self.preview_label.image = preview_image  # Keep a reference
                else:
                    self.preview_label.configure(image="", text="Preview not available")
            except Exception as e:
                self.preview_label.configure(image="", text=f"Error loading preview: {e}")
        
        elif media_info["type"] == "audio":
            # Show audio file icon or info
            self.preview_label.configure(image="", text="🎵 Audio File")
    
    def _update_info(self, media_info):
        """Update the information area"""
        info_text = f"Filename: {media_info.get('original_filename', 'Unknown')}\n"
        info_text += f"Type: {media_info.get('type', 'Unknown').title()}\n"
        info_text += f"Size: {self._format_file_size(media_info.get('file_size', 0))}\n"
        info_text += f"Upload Date: {media_info.get('upload_date', 'Unknown')[:10]}\n"
        
        if media_info["type"] == "image":
            dimensions = media_info.get("dimensions", {})
            if dimensions:
                info_text += f"Dimensions: {dimensions.get('width', '?')} x {dimensions.get('height', '?')}\n"
        
        description = media_info.get("description", "")
        if description:
            info_text += f"Description: {description}\n"
        
        self.info_label.configure(text=info_text)
    
    def _format_file_size(self, size_bytes):
        """Format file size in human readable form"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    def _get_selected_media(self):
        """Get the currently selected media info"""
        selection = self.media_list.curselection()
        if not selection:
            return None
        
        filename = self.media_list.get(selection[0])
        if filename == "No media files found":
            return None
        
        return self.media_data.get(filename)
    
    def _select_media(self):
        """Select the current media and close dialog"""
        media_info = self._get_selected_media()
        if not media_info:
            messagebox.showwarning("No Selection", "Please select a media file first.")
            return
        
        # Return media reference format
        self.result = {
            "media_id": media_info["id"],
            "filename": media_info.get("original_filename", ""),
            "type": "media_reference"
        }
        
        self.dialog.destroy()
    
    def _delete_media(self):
        """Delete the selected media file"""
        media_info = self._get_selected_media()
        if not media_info:
            messagebox.showwarning("No Selection", "Please select a media file first.")
            return
        
        # Confirm deletion
        filename = media_info.get("original_filename", "Unknown")
        if not messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete '{filename}'?\n\n"
            "This will remove the file from the media library and "
            "any questions using this file will no longer display it."
        ):
            return
        
        # Delete the media
        success = self.media_manager.delete_media(media_info["id"])
        if success:
            messagebox.showinfo("Deleted", f"'{filename}' has been deleted.")
            self._load_media_list()  # Refresh the list
            # Clear preview
            self.preview_label.configure(image="", text="No media selected")
            self.info_label.configure(text="")
        else:
            messagebox.showerror("Error", f"Failed to delete '{filename}'.")
    
    def _cancel(self):
        """Cancel and close dialog"""
        self.result = None
        self.dialog.destroy()
    
    def _center_on_parent(self):
        """Center the dialog on its parent window"""
        self.dialog.update_idletasks()
        
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        dialog_width = self.dialog.winfo_width()
        dialog_height = self.dialog.winfo_height()
        
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.dialog.geometry(f"+{x}+{y}")


def show_media_browser(parent, media_manager, media_type="image", title="Select Media"):
    """Convenience function to show the media browser dialog"""
    browser = MediaBrowserDialog(parent, media_manager, media_type, title)
    return browser.show()
