"""Custom exception classes for ClynBoozle application."""


class ClynBoozleError(Exception):
    """Base exception class for ClynBoozle application."""

    pass


class ValidationError(ClynBoozleError):
    """Raised when data validation fails."""

    pass


class MediaLoadError(ClynBoozleError):
    """Raised when media files cannot be loaded or processed."""

    pass


class QuestionSetError(ClynBoozleError):
    """Raised when question set operations fail."""

    pass


class GameStateError(ClynBoozleError):
    """Raised when game state operations fail."""

    pass


class AudioError(ClynBoozleError):
    """Raised when audio operations fail."""

    pass


class FileOperationError(ClynBoozleError):
    """Raised when file operations fail."""

    pass
