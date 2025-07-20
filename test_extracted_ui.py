#!/usr/bin/env python3
"""Test extracted UI components to ensure they work correctly."""

import sys
import tkinter as tk
from tkinter import font
from pathlib import Path

# Add the src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from clynboozle.ui import MainMenuFrame, TeamSetupFrame, GameBoardFrame
from clynboozle.config.settings import WindowConfig, ColorConfig


class MockApp:
    """Mock application for testing UI components."""
    
    def __init__(self, root):
        self.root = root
        self.bg_color = ColorConfig.PRIMARY_BG
        
        # Mock question manager
        class MockQuestionManager:
            def __init__(self):
                self.current_set = None
        
        self.question_manager = MockQuestionManager()
        
        # Base font sizes and widget dimensions
        self.base_sizes = {
            "title_bold": (36, "bold"),
            "button_bold": (18, "bold"),
            "label": (16, "normal"),
            "small_label": (14, "normal"),
            "small_label_bold": (14, "bold"),
            "entry": (14, "normal"),
        }
        
        # Mock fonts
        self.fonts = {}
        for key, (size, weight) in self.base_sizes.items():
            self.fonts[key] = font.Font(family="Arial", size=size, weight=weight)
    
    def _get_font_size(self, base_size):
        """Mock font size scaling."""
        return base_size
    
    def _get_widget_size(self, base_width, base_height):
        """Mock widget size scaling."""
        return base_width, base_height


def test_team_setup():
    """Test the TeamSetupFrame component."""
    print("Testing TeamSetupFrame...")
    
    root = tk.Tk()
    app = MockApp(root)
    
    team_setup = TeamSetupFrame(root, app, initial_names=["Team Alpha", "Team Beta"])
    team_setup.pack(fill=tk.BOTH, expand=True)
    
    # Set up callbacks
    team_setup.set_callbacks(
        on_back=lambda: print("Back clicked!"),
        on_start_game=lambda teams: print(f"Starting game with teams: {teams}"),
        on_change_question_set=lambda: print("Change question set clicked!")
    )
    
    print("TeamSetupFrame created successfully! Test window opened. Try changing team count.")
    root.mainloop()


if __name__ == "__main__":
    test_team_setup()
