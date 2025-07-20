"""
Test script to validate the base UI components work correctly.
"""

import sys
import tkinter as tk
from pathlib import Path

# Add the src directory to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from clynboozle.ui import BaseFrame, MessageDialog, InputDialog
from clynboozle.config.settings import WindowConfig, ColorConfig, FontConfig


class TestFrame(BaseFrame):
    """Test implementation of BaseFrame."""
    
    def __init__(self, master, app):
        """Initialize the test frame."""
        super().__init__(master, app)
        # build_ui() is already called by BaseFrame.__init__()
    
    def build_ui(self) -> None:
        """Build the test UI."""
        # Create content frame
        self.content_frame = tk.Frame(self, bg=ColorConfig.SECONDARY_BG)
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title = self.create_title_label(self.content_frame, "Base UI Components Test")
        title.pack(pady=WindowConfig.PADDING_LARGE)
        
        # Button test area
        button_frame = tk.Frame(self.content_frame, bg=ColorConfig.SECONDARY_BG)
        button_frame.pack(pady=WindowConfig.PADDING_MEDIUM)
        
        # Test buttons
        primary_btn = self.create_styled_button(
            button_frame,
            "Test Message Dialog",
            command=self.test_message_dialog,
            bg_color=ColorConfig.PRIMARY_COLOR
        )
        primary_btn.pack(side="left", padx=WindowConfig.PADDING_SMALL)
        
        secondary_btn = self.create_styled_button(
            button_frame,
            "Test Input Dialog",
            command=self.test_input_dialog,
            bg_color=ColorConfig.SECONDARY_COLOR
        )
        secondary_btn.pack(side="left", padx=WindowConfig.PADDING_SMALL)
        
        # Simple test frame (not clickable for now)
        test_frame = tk.Frame(
            self.content_frame,
            bg=ColorConfig.TERTIARY_BG,
            width=200,
            height=100,
            relief="raised",
            borderwidth=2
        )
        test_frame.pack(pady=WindowConfig.PADDING_MEDIUM)
        test_frame.pack_propagate(False)  # Keep the size
        
        click_label = tk.Label(
            test_frame,
            text="Test Frame Area",
            bg=ColorConfig.TERTIARY_BG,
            fg=ColorConfig.PRIMARY_TEXT,
            font=(FontConfig.FAMILY, FontConfig.BUTTON_SIZE)
        )
        click_label.pack(expand=True)
        
        # Status label
        self.status_label = tk.Label(
            self.content_frame,
            text="Ready for testing...",
            bg=ColorConfig.SECONDARY_BG,
            fg=ColorConfig.SECONDARY_TEXT,
            font=(FontConfig.FAMILY, FontConfig.SMALL_SIZE)
        )
        self.status_label.pack(pady=WindowConfig.PADDING_LARGE)
    
    def test_message_dialog(self) -> None:
        """Test the message dialog."""
        dialog = MessageDialog(
            self.root,
            "Test Message",
            "This is a test message dialog.\n\nIt supports multiple lines and auto-sizing.",
            buttons=["OK", "Cancel", "Maybe"]
        )
        
        def handle_result(result):
            self.status_label.configure(text=f"Message dialog result: {result}")
        
        dialog.set_result_callback(handle_result)
        dialog.show_modal()
    
    def test_input_dialog(self) -> None:
        """Test the input dialog."""
        dialog = InputDialog(
            self.root,
            "Test Input",
            "Please enter some text:",
            initial_value="Default text",
            placeholder="Type here..."
        )
        
        def handle_result(result):
            if result:
                self.status_label.configure(text=f"Input dialog result: '{result}'")
            else:
                self.status_label.configure(text="Input dialog was cancelled")
        
        dialog.set_result_callback(handle_result)
        dialog.show_modal()


def test_base_components():
    """Test the base UI components."""
    print("Testing base UI components...")
    
    # Create root window
    root = tk.Tk()
    root.title("ClynBoozle UI Component Test")
    root.geometry("600x400")
    
    # Create a simple mock app object
    class MockApp:
        def __init__(self):
            self.root = root
    
    mock_app = MockApp()
    
    # Create test frame
    test_frame = TestFrame(root, mock_app)
    test_frame.pack(fill="both", expand=True)
    
    print("UI components loaded successfully!")
    print("Test window opened. Try the buttons to test dialogs.")
    print("Close the window to end the test.")
    
    # Run the main loop
    root.mainloop()
    
    print("Base UI components test completed.")


if __name__ == "__main__":
    test_base_components()
