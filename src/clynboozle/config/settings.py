"""Application settings and configuration constants."""

from typing import Dict, Tuple, Set
import os

# =============================================================================
# Application Information
# =============================================================================
APP_NAME = "ClynBoozle"
APP_VERSION = "2.0.0"


# =============================================================================
# Color Scheme
# =============================================================================
class Colors:
    """Application color constants."""

    # Main colors
    BACKGROUND = "#333333"  # Dark gray background
    BUTTON = "#666666"  # Medium gray for buttons

    # Accent colors
    GOLD = "#FFD700"  # Title and highlights
    GREEN = "#4CAF50"  # Success/Play buttons
    BLUE = "#2196F3"  # Info/Manage buttons
    RED = "#F44336"  # Error/Delete buttons
    ORANGE = "#FF9800"  # Warning/Orange buttons

    # Text colors
    WHITE = "white"
    BLACK = "black"
    LIGHT_GRAY = "#888888"
    DARK_GRAY = "#444444"
    MEDIUM_GRAY = "#666666"

    # Extended colors for styling system
    TEXT = WHITE  # Primary text color
    TEXT_MUTED = LIGHT_GRAY  # Muted text color
    BUTTON_TEXT = WHITE  # Button text color
    BUTTON_HOVER = "#777777"  # Button hover state
    BUTTON_ACTIVE = "#555555"  # Button active/pressed state

    # UI element colors
    SEPARATOR = MEDIUM_GRAY  # Visual separators
    TOOLTIP_BG = "#1f1f1f"  # Tooltip background
    TOOLTIP_TEXT = WHITE  # Tooltip text
    CARD_BG = "#3a3a3a"  # Card/container backgrounds
    PANEL_BG = "#404040"  # Panel backgrounds


# =============================================================================
# Modern Color Configuration
# =============================================================================
class ColorConfig:
    """Modern UI color constants for consistent theming."""

    # Background colors
    PRIMARY_BG = "#2d2d30"  # Dark background
    SECONDARY_BG = "#3c3c3c"  # Slightly lighter background
    TERTIARY_BG = "#464647"  # Component backgrounds

    # Text colors
    PRIMARY_TEXT = "#ffffff"  # Main text
    SECONDARY_TEXT = "#cccccc"  # Secondary text
    MUTED_TEXT = "#999999"  # Muted/disabled text

    # Button and interaction colors
    PRIMARY_COLOR = "#007acc"  # Primary action color (blue)
    SECONDARY_COLOR = "#666666"  # Secondary actions
    SUCCESS_COLOR = "#4caf50"  # Success/positive actions
    WARNING_COLOR = "#ff9800"  # Warning actions
    ERROR_COLOR = "#f44336"  # Error/destructive actions

    # Hover and focus states
    HOVER_COLOR = "#005a9e"  # Hover state for buttons
    FOCUS_COLOR = "#007acc"  # Focus ring color

    # Input/form colors
    ENTRY_BG = "#1e1e1e"  # Input field background
    ENTRY_BORDER = "#464647"  # Input field border

    # Game-specific colors
    GOLD = "#ffd700"  # Highlights and titles
    TILE_COLOR = "#555555"  # Game tile color
    TILE_HOVER = "#666666"  # Game tile hover


# =============================================================================
# Window Configuration
# =============================================================================
class WindowConfig:
    """Window sizing and layout constants."""

    # Minimum window dimensions
    MIN_WIDTH = 800
    MIN_HEIGHT = 600

    # Initial window dimensions
    INITIAL_WIDTH = 800
    INITIAL_HEIGHT = 600

    # Default window dimensions (for scaling calculations)
    DEFAULT_WIDTH = 800
    DEFAULT_HEIGHT = 600

    # Padding and spacing
    DEFAULT_PADDING = 20
    SMALL_PADDING = 10
    LARGE_PADDING = 30

    # Modern padding constants
    PADDING_SMALL = 5
    PADDING_MEDIUM = 10
    PADDING_LARGE = 20
    PADDING_XLARGE = 30

    # Button sizing
    DEFAULT_BUTTON_WIDTH = 250
    DEFAULT_BUTTON_HEIGHT = 60
    MIN_BUTTON_WIDTH = 150
    MIN_BUTTON_HEIGHT = 40


# =============================================================================
# Font Configuration
# =============================================================================
class FontConfig:
    """Font family and sizing constants."""

    # Font family
    FAMILY = "Arial"
    DEFAULT_FAMILY = FAMILY  # Alias for consistency

    # Standard sizes
    TITLE_SIZE = 36
    BUTTON_SIZE = 18
    LABEL_SIZE = 16
    SMALL_SIZE = 14
    TILE_SIZE = 20

    # Additional size aliases for styling system
    DEFAULT_SIZE = LABEL_SIZE  # Default text size
    LARGE_SIZE = 20  # Large text size

    # Base font sizes (will be scaled based on window size)
    BASE_SIZES = {
        "title_bold": (36, "bold"),
        "button_bold": (18, "bold"),
        "label": (16, "normal"),
        "small_label": (14, "normal"),
        "small_label_bold": (14, "bold"),
        "entry": (14, "normal"),
        "tile": (20, "normal"),
        "score": (14, "normal"),
        "score_bold": (14, "bold"),
        "menu_button": (12, "normal"),
    }

    # Minimum font size
    MIN_SIZE = 8


# =============================================================================
# UI Component Sizes
# =============================================================================
class ComponentSizes:
    """UI component sizing constants."""

    # Main menu button sizes
    MAIN_MENU_BUTTON_WIDTH = 250
    MAIN_MENU_BUTTON_HEIGHT = 60

    # Team setup component sizes
    TEAM_NUM_BUTTON_SIZE = 40
    CHANGE_SET_BUTTON_WIDTH = 180
    CHANGE_SET_BUTTON_HEIGHT = 40
    BOTTOM_BUTTON_WIDTH = 150
    BOTTOM_BUTTON_HEIGHT = 50

    # Game board component sizes
    MENU_BUTTON_WIDTH = 100
    MENU_BUTTON_HEIGHT = 30

    # Minimum widget sizes
    MIN_WIDGET_WIDTH = 10
    MIN_WIDGET_HEIGHT = 10


# =============================================================================
# File Paths and Directories
# =============================================================================
class Paths:
    """File path and directory constants."""

    # Directory names
    QUESTION_SETS_DIR = "question_sets"
    UPLOADS_DIR = "uploads"
    MEDIA_DB_FILE = "media_database.json"

    # Subdirectories in uploads
    IMAGES_SUBDIR = "images"
    AUDIO_SUBDIR = "audio"
    THUMBNAILS_SUBDIR = "thumbnails"

    @classmethod
    def get_question_sets_dir(cls, base_dir: str) -> str:
        """Get the full path to question sets directory."""
        return os.path.join(base_dir, cls.QUESTION_SETS_DIR)

    @classmethod
    def get_uploads_dir(cls, base_dir: str) -> str:
        """Get the full path to uploads directory."""
        return os.path.join(base_dir, cls.UPLOADS_DIR)

    @classmethod
    def get_media_db_path(cls, base_dir: str) -> str:
        """Get the full path to media database file."""
        return os.path.join(cls.get_uploads_dir(base_dir), cls.MEDIA_DB_FILE)


# =============================================================================
# Game Configuration
# =============================================================================
class GameConfig:
    """Game logic and default values."""

    # Default team configuration
    DEFAULT_TEAMS = ["Team 1", "Team 2", "Team 3"]
    MIN_TEAMS = 2
    MAX_TEAMS = 6

    # Audio configuration
    AUDIO_FREQUENCY = 22050
    AUDIO_SIZE = -16
    AUDIO_CHANNELS = 2
    AUDIO_BUFFER = 512

    # Position update interval for audio (milliseconds)
    AUDIO_UPDATE_INTERVAL = 100

    # Resize debounce delay (milliseconds)
    RESIZE_DELAY = 50


# =============================================================================
# Validation Constants
# =============================================================================
class Validation:
    """Data validation constants."""

    # Filename sanitization
    SAFE_FILENAME_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-_"

    # Maximum lengths
    MAX_TEAM_NAME_LENGTH = 50
    MAX_QUESTION_LENGTH = 1000
    MAX_ANSWER_LENGTH = 500
    MAX_DESCRIPTION_LENGTH = 200

    # Point value constraints
    MIN_POINTS = 1
    MAX_POINTS = 1000

    # Filename sanitization
    SAFE_FILENAME_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-_"

    # Maximum lengths
    MAX_TEAM_NAME_LENGTH = 50
    MAX_QUESTION_LENGTH = 1000
    MAX_ANSWER_LENGTH = 500
    MAX_DESCRIPTION_LENGTH = 200

    # Point value constraints
    MIN_POINTS = 1
    MAX_POINTS = 1000


# =============================================================================
# Media Configuration
# =============================================================================
class MediaConfig:
    """Media processing and storage configuration."""

    # Image sizes for different use cases
    IMAGE_SIZES = {
        "tile": (120, 80),  # For game board tiles
        "tile_2x": (240, 160),  # For high-DPI displays
        "question": (400, 300),  # For question display
        "question_large": (800, 600),  # For full-screen question display
        "thumbnail": (100, 100),  # For management interface
    }

    # Supported file formats
    AUDIO_FORMATS = {".wav", ".mp3", ".ogg", ".flac", ".aac"}
    IMAGE_FORMATS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"}

    # Image processing settings
    DEFAULT_IMAGE_QUALITY = 85
    THUMBNAIL_QUALITY = 80
    MAX_IMAGE_SIZE = (2048, 2048)  # Maximum dimensions for uploaded images
