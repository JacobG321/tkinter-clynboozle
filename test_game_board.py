#!/usr/bin/env python3
"""Test the GameBoardFrame component."""

import sys
import tkinter as tk
from tkinter import font
from pathlib import Path

# Add the src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from clynboozle.ui import GameBoardFrame
from clynboozle.config.settings import WindowConfig, ColorConfig


class MockApp:
    """Mock application for testing GameBoardFrame."""
    
    def __init__(self, root):
        self.root = root
        self.bg_color = ColorConfig.PRIMARY_BG
        self.button_color = ColorConfig.SECONDARY_BG
        
        # Add some sample questions
        self.questions = [
            {"points": 100, "question": "Test question 1"},
            {"points": 200, "question": "Test question 2"},
            {"points": 300, "question": "Test question 3"},
            {"points": 400, "question": "Test question 4"},
            {"points": 500, "question": "Test question 5"},
            {"points": 600, "question": "Test question 6"},
        ]
        self.grid_rows = 2
        self.grid_cols = 3
        self.current_team = "Team A"
        
        # Mock fonts
        self.fonts = {
            "tile": font.Font(family="Arial", size=20),
            "score": font.Font(family="Arial", size=14),
            "score_bold": font.Font(family="Arial", size=14, weight="bold"),
            "menu_button": font.Font(family="Arial", size=12),
        }
        
        # Mock media manager
        class MockMediaManager:
            def get_image_path(self, media_id, size_type):
                return None
        
        self.media_manager = MockMediaManager()
    
    def calculate_grid_dimensions(self):
        """Mock grid calculation."""
        self.grid_rows = 2
        self.grid_cols = 3
    
    def reveal_question(self, idx):
        """Mock question reveal."""
        print(f"Revealing question {idx}: {self.questions[idx]['question']}")
    
    def show_game_menu(self):
        """Mock game menu."""
        print("Showing game menu")
    
    def next_team(self, first_turn=False):
        """Mock team cycling."""
        if first_turn:
            print("Starting with first team")
        else:
            print("Moving to next team")
    
    def _get_font_size(self, base_size):
        """Mock font size scaling."""
        return base_size
    
    def _get_widget_size(self, base_width, base_height):
        """Mock widget size scaling."""
        return base_width, base_height


def test_game_board():
    """Test the GameBoardFrame component."""
    print("Testing GameBoardFrame...")
    
    root = tk.Tk()
    app = MockApp(root)
    
    # Create sample teams for testing
    teams = {
        "Team A": 0,
        "Team B": 100,
        "Team C": 250
    }
    
    frame = GameBoardFrame(root, app, teams)
    frame.pack(fill=tk.BOTH, expand=True)
    
    print("GameBoardFrame created successfully! Test window opened. Try clicking tiles.")
    root.mainloop()


if __name__ == "__main__":
    test_game_board()
