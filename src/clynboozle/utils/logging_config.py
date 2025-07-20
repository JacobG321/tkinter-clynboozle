"""Logging configuration for ClynBoozle application."""

import logging
import logging.handlers
import os
from pathlib import Path
from typing import Optional

# Note: Paths import removed as it's not currently used in this module


class LoggingConfig:
    """Centralized logging configuration for the application."""

    DEFAULT_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

    @classmethod
    def setup_logging(
        cls,
        log_level: str = "INFO",
        log_to_file: bool = True,
        log_file_path: Optional[str] = None,
        max_file_size: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
    ) -> None:
        """
        Set up application-wide logging configuration.

        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_to_file: Whether to log to a file
            log_file_path: Custom log file path (optional)
            max_file_size: Maximum size of log file before rotation
            backup_count: Number of backup files to keep
        """
        # Convert string level to logging constant
        numeric_level = getattr(logging, log_level.upper(), logging.INFO)

        # Create root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(numeric_level)

        # Clear any existing handlers
        root_logger.handlers.clear()

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(numeric_level)
        console_formatter = logging.Formatter(cls.DEFAULT_FORMAT, cls.DEFAULT_DATE_FORMAT)
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)

        # File handler (if enabled)
        if log_to_file:
            log_file = log_file_path or cls._get_default_log_file()
            cls._ensure_log_directory(log_file)

            file_handler = logging.handlers.RotatingFileHandler(
                log_file, maxBytes=max_file_size, backupCount=backup_count
            )
            file_handler.setLevel(numeric_level)
            file_formatter = logging.Formatter(cls.DEFAULT_FORMAT, cls.DEFAULT_DATE_FORMAT)
            file_handler.setFormatter(file_formatter)
            root_logger.addHandler(file_handler)

        # Set specific loggers to appropriate levels
        cls._configure_library_loggers()

        # Log configuration complete
        logger = logging.getLogger(__name__)
        logger.info(f"Logging configured: level={log_level}, file_logging={log_to_file}")

    @classmethod
    def _get_default_log_file(cls) -> str:
        """Get the default log file path."""
        # Try to use application directory, fall back to temp
        try:
            app_dir = Path(__file__).parent.parent.parent.parent
            logs_dir = app_dir / "logs"
            return str(logs_dir / "clynboozle.log")
        except Exception:
            # Fallback to system temp directory
            import tempfile

            return os.path.join(tempfile.gettempdir(), "clynboozle.log")

    @classmethod
    def _ensure_log_directory(cls, log_file_path: str) -> None:
        """Ensure the log directory exists."""
        log_dir = os.path.dirname(log_file_path)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)

    @classmethod
    def _configure_library_loggers(cls) -> None:
        """Configure logging levels for third-party libraries."""
        # Reduce noise from PIL/Pillow
        logging.getLogger("PIL").setLevel(logging.WARNING)
        logging.getLogger("pillow").setLevel(logging.WARNING)

        # Reduce noise from pygame
        logging.getLogger("pygame").setLevel(logging.WARNING)

        # Set our application loggers to INFO by default
        logging.getLogger("clynboozle").setLevel(logging.INFO)

    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """
        Get a logger for a specific module or class.

        Args:
            name: Name for the logger (usually __name__)

        Returns:
            Configured logger instance
        """
        return logging.getLogger(name)

    @classmethod
    def setup_dev_logging(cls) -> None:
        """Quick setup for development with debug logging."""
        cls.setup_logging(log_level="DEBUG", log_to_file=True)

    @classmethod
    def setup_production_logging(cls) -> None:
        """Setup for production with info logging and rotation."""
        cls.setup_logging(
            log_level="INFO", log_to_file=True, max_file_size=50 * 1024 * 1024, backup_count=10
        )

    @classmethod
    def disable_logging(cls) -> None:
        """Disable all logging (for testing)."""
        logging.disable(logging.CRITICAL)

    @classmethod
    def enable_logging(cls) -> None:
        """Re-enable logging after disable_logging()."""
        logging.disable(logging.NOTSET)


# Convenience functions for common patterns
def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return LoggingConfig.get_logger(name)


def setup_logging(log_level: str = "INFO") -> None:
    """Quick logging setup."""
    LoggingConfig.setup_logging(log_level=log_level)
