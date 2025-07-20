"""User interface messages and error strings."""


# =============================================================================
# Application Messages
# =============================================================================
class AppMessages:
    """Main application messages."""

    TITLE = "ClynBoozle"
    SETUP_TITLE = "ClynBoozle Setup"

    # Main menu buttons
    PLAY_GAME = "Play Game"
    MANAGE_QUESTION_SETS = "Manage Question Sets"
    QUIT = "Quit"


# =============================================================================
# Team Setup Messages
# =============================================================================
class TeamSetupMessages:
    """Team setup screen messages."""

    QUESTION_SET_LABEL = "Question Set: {}"
    CHANGE_QUESTION_SET = "Change Question Set"
    NUMBER_OF_TEAMS = "Number of Teams:"
    TEAM_NAMES = "Team Names:"
    TEAM_LABEL = "Team {}:"
    BACK = "Back"
    START_GAME = "Start Game"


# =============================================================================
# Game Messages
# =============================================================================
class GameMessages:
    """In-game messages."""

    GAME_MENU = "Game Menu"
    MENU = "Menu"
    CONTINUE_GAME = "Continue Game"
    NEW_GAME = "New Game"
    CHANGE_QUESTION_SET = "Change Question Set"
    MAIN_MENU = "Main Menu"

    # Game over messages
    GAME_OVER = "GAME OVER!"
    WINNER = "Winner: {}"
    SCORE = "Score: {} points"
    FINAL_SCORES = "Final Scores:"
    PLAY_AGAIN = "Play Again"

    # Question dialog
    REVEAL_ANSWER = "Reveal Answer"
    ANSWER_PREFIX = "Answer: {}"
    CORRECT = "✓ Correct"
    WRONG = "✗ Wrong"
    CLICK_TO_ENLARGE = "Click image to enlarge"
    ENLARGED_IMAGE_TITLE = "Enlarged Image"


# =============================================================================
# Question Set Manager Messages
# =============================================================================
class QuestionSetMessages:
    """Question set manager messages."""

    MANAGER_TITLE = "Question Set Manager"
    QUESTION_SETS = "Question Sets"
    NEW_SET = "New Set"
    LOAD_SET = "Load Set"
    MANAGE_MEDIA = "Manage Media"
    RENAME = "Rename"
    DELETE = "Delete"
    ADD_QUESTION = "Add Question"
    EDIT_QUESTION = "Edit Question"
    REMOVE_QUESTION = "Remove Question"
    SAVE_SET = "Save Set"

    # New set dialog
    NEW_SET_PROMPT = "Enter name for the new question set:"

    # Question form labels
    QUESTION_LABEL = "Question:"
    ANSWER_LABEL = "Answer:"
    POINTS_LABEL = "Points:"
    TILE_IMAGE_LABEL = "Tile Image:"
    QUESTION_IMAGE_LABEL = "Question Image:"
    QUESTION_AUDIO_LABEL = "Question Audio:"

    # Buttons
    BROWSE = "Browse"
    CLEAR = "Clear"
    CANCEL = "Cancel"
    SAVE = "Save"


# =============================================================================
# Media Browser Messages
# =============================================================================
class MediaMessages:
    """Media browser and management messages."""

    MEDIA_LIBRARY = "Media Library"
    IMAGES = "Images"
    AUDIO = "Audio"
    MEDIA_FILES = "Media Files"
    PREVIEW = "Preview"
    INFORMATION = "Information"
    NO_MEDIA_SELECTED = "No media selected"
    NO_MEDIA_FOUND = "No media files found"

    # Media info labels
    FILENAME = "Filename: {}"
    TYPE = "Type: {}"
    SIZE = "Size: {}"
    UPLOAD_DATE = "Upload Date: {}"
    DIMENSIONS = "Dimensions: {}x{}"
    DESCRIPTION = "Description: {}"

    # Buttons
    REFRESH = "Refresh"
    SELECT = "Select"
    DELETE_SELECTED = "Delete Selected"

    # Audio controls
    PLAY = "Play"
    PAUSE = "Pause"
    RESUME = "Resume"
    STOP = "Stop"
    AUDIO_PREFIX = "Audio: {}"
    DRAG_TO_SEEK = "Drag slider to seek position"


# =============================================================================
# Error Messages
# =============================================================================
class ErrorMessages:
    """Error and warning messages."""

    # General errors
    UNKNOWN_ERROR = "An unknown error occurred."
    FILE_NOT_FOUND = "File not found: {}"
    INVALID_FILE_FORMAT = "Invalid file format: {}"
    PERMISSION_DENIED = "Permission denied: {}"

    # Question set errors
    NO_QUESTIONS = "Please create or select a question set first."
    INVALID_QUESTION_SET = "Invalid question set file: {}"
    SAVE_FAILED = "Failed to save question set: {}"
    LOAD_FAILED = "Failed to load question set: {}"
    DELETE_FAILED = "Failed to delete question set: {}"

    # Media errors
    MEDIA_LOAD_ERROR = "Failed to load media file: {}"
    MEDIA_SAVE_ERROR = "Failed to save media file: {}"
    MEDIA_DELETE_ERROR = "Failed to delete media file: {}"
    AUDIO_INIT_ERROR = "Failed to initialize audio system: {}"
    IMAGE_PROCESS_ERROR = "Failed to process image: {}"

    # Validation errors
    INVALID_TEAM_NAME = "Invalid team name. Please use alphanumeric characters only."
    INVALID_POINTS = "Points must be between {} and {}."
    EMPTY_QUESTION = "Question cannot be empty."
    EMPTY_ANSWER = "Answer cannot be empty."
    DUPLICATE_TEAM_NAME = "Team name already exists. Please use a unique name."

    # Database errors
    DATABASE_CORRUPT = "Media database is corrupted and will be reset."
    DATABASE_SAVE_ERROR = "Failed to save media database: {}"


# =============================================================================
# Confirmation Messages
# =============================================================================
class ConfirmationMessages:
    """Confirmation dialog messages."""

    DELETE_QUESTION_SET = "Are you sure you want to delete the question set '{}'?"
    DELETE_MEDIA = "Are you sure you want to delete the selected media file?"
    END_GAME = "Are you sure you want to end the current game?"
    UNSAVED_CHANGES = "You have unsaved changes. Do you want to save before continuing?"
    OVERWRITE_FILE = "File already exists. Do you want to overwrite it?"


# =============================================================================
# Success Messages
# =============================================================================
class SuccessMessages:
    """Success notification messages."""

    QUESTION_SET_SAVED = "Question set '{}' saved successfully."
    QUESTION_SET_LOADED = "Question set '{}' loaded successfully."
    MEDIA_UPLOADED = "Media file uploaded successfully."
    MEDIA_DELETED = "Media file deleted successfully."


# =============================================================================
# File Size Formatting
# =============================================================================
class FormatMessages:
    """Formatting helper messages."""

    BYTES = "B"
    KILOBYTES = "KB"
    MEGABYTES = "MB"
    GIGABYTES = "GB"

    TIME_FORMAT = "{:02d}:{:02d}"
