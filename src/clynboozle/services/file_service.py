"""File service for ClynBoozle application."""

from typing import Any, Dict, List, Optional
import os
import json
import shutil
from pathlib import Path

from ..config.settings import Paths, Validation
from ..utils.exceptions import FileOperationError


class FileService:
    """Service for handling file I/O operations."""

    def __init__(self, base_dir: str) -> None:
        """Initialize the file service with base directory."""
        self.base_dir = Path(base_dir)
        self._ensure_base_directory()

    def _ensure_base_directory(self) -> None:
        """Ensure base directory exists."""
        try:
            self.base_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise FileOperationError(f"Failed to create base directory: {e}")

    def get_question_sets_dir(self) -> Path:
        """Get the question sets directory path."""
        path = self.base_dir / Paths.QUESTION_SETS_DIR
        path.mkdir(exist_ok=True)
        return path

    def get_uploads_dir(self) -> Path:
        """Get the uploads directory path."""
        path = self.base_dir / Paths.UPLOADS_DIR
        path.mkdir(exist_ok=True)
        return path

    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe storage."""
        # Remove path and keep only the filename
        filename = os.path.basename(filename)

        # Replace invalid characters
        sanitized = "".join(c if c in Validation.SAFE_FILENAME_CHARS else "_" for c in filename)

        # Remove multiple consecutive underscores
        while "__" in sanitized:
            sanitized = sanitized.replace("__", "_")

        # Remove leading/trailing underscores
        sanitized = sanitized.strip("_")

        # Ensure filename is not empty
        if not sanitized:
            sanitized = "file"

        return sanitized

    def read_json_file(self, file_path: Path) -> Any:
        """Read and parse JSON file."""
        if not file_path.exists():
            raise FileOperationError(f"File not found: {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise FileOperationError(f"Invalid JSON in file {file_path}: {e}")
        except OSError as e:
            raise FileOperationError(f"Failed to read file {file_path}: {e}")

    def write_json_file(self, file_path: Path, data: Any, indent: int = 2) -> None:
        """Write data to JSON file."""
        try:
            # Ensure parent directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=indent, ensure_ascii=False)
        except OSError as e:
            raise FileOperationError(f"Failed to write file {file_path}: {e}")
        except (TypeError, ValueError) as e:
            raise FileOperationError(f"Failed to serialize data to JSON: {e}")

    def copy_file(self, source: Path, destination: Path) -> None:
        """Copy file from source to destination."""
        if not source.exists():
            raise FileOperationError(f"Source file not found: {source}")

        try:
            # Ensure destination directory exists
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        except OSError as e:
            raise FileOperationError(f"Failed to copy file: {e}")

    def move_file(self, source: Path, destination: Path) -> None:
        """Move file from source to destination."""
        if not source.exists():
            raise FileOperationError(f"Source file not found: {source}")

        try:
            # Ensure destination directory exists
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(source, destination)
        except OSError as e:
            raise FileOperationError(f"Failed to move file: {e}")

    def delete_file(self, file_path: Path) -> None:
        """Delete a file."""
        if not file_path.exists():
            return  # Already deleted

        try:
            file_path.unlink()
        except OSError as e:
            raise FileOperationError(f"Failed to delete file {file_path}: {e}")

    def create_directory(self, dir_path: Path) -> None:
        """Create directory with all parent directories."""
        try:
            dir_path.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise FileOperationError(f"Failed to create directory {dir_path}: {e}")

    def list_files(
        self, directory: Path, pattern: str = "*", recursive: bool = False
    ) -> List[Path]:
        """List files in directory matching pattern."""
        if not directory.exists():
            return []

        try:
            if recursive:
                return list(directory.rglob(pattern))
            else:
                return list(directory.glob(pattern))
        except OSError as e:
            raise FileOperationError(f"Failed to list files in {directory}: {e}")

    def get_file_size(self, file_path: Path) -> int:
        """Get file size in bytes."""
        if not file_path.exists():
            raise FileOperationError(f"File not found: {file_path}")

        try:
            return file_path.stat().st_size
        except OSError as e:
            raise FileOperationError(f"Failed to get file size: {e}")

    def file_exists(self, file_path: Path) -> bool:
        """Check if file exists."""
        return file_path.exists() and file_path.is_file()

    def directory_exists(self, dir_path: Path) -> bool:
        """Check if directory exists."""
        return dir_path.exists() and dir_path.is_dir()

    def get_unique_filename(self, directory: Path, base_name: str) -> str:
        """Get a unique filename in the directory."""
        if not (directory / base_name).exists():
            return base_name

        name, ext = os.path.splitext(base_name)
        counter = 1

        while (directory / f"{name}_{counter}{ext}").exists():
            counter += 1

        return f"{name}_{counter}{ext}"

    def backup_file(self, file_path: Path, backup_suffix: str = ".bak") -> Path:
        """Create a backup of the file."""
        if not file_path.exists():
            raise FileOperationError(f"File not found: {file_path}")

        backup_path = file_path.with_suffix(file_path.suffix + backup_suffix)

        # If backup already exists, create a numbered backup
        if backup_path.exists():
            counter = 1
            while True:
                numbered_backup = file_path.with_suffix(
                    f"{file_path.suffix}{backup_suffix}.{counter}"
                )
                if not numbered_backup.exists():
                    backup_path = numbered_backup
                    break
                counter += 1

        self.copy_file(file_path, backup_path)
        return backup_path

    def read_text_file(self, file_path: Path, encoding: str = "utf-8") -> str:
        """Read text file content."""
        if not file_path.exists():
            raise FileOperationError(f"File not found: {file_path}")

        try:
            with open(file_path, "r", encoding=encoding) as f:
                return f.read()
        except OSError as e:
            raise FileOperationError(f"Failed to read file {file_path}: {e}")

    def write_text_file(self, file_path: Path, content: str, encoding: str = "utf-8") -> None:
        """Write text content to file."""
        try:
            # Ensure parent directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, "w", encoding=encoding) as f:
                f.write(content)
        except OSError as e:
            raise FileOperationError(f"Failed to write file {file_path}: {e}")

    def cleanup_empty_directories(self, root_dir: Path) -> None:
        """Remove empty directories recursively."""
        try:
            for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
                dir_path = Path(dirpath)

                # Skip if directory contains files
                if filenames:
                    continue

                # Skip if directory contains non-empty subdirectories
                if any((dir_path / dirname).exists() for dirname in dirnames):
                    continue

                # Skip the root directory itself
                if dir_path == root_dir:
                    continue

                try:
                    dir_path.rmdir()
                except OSError:
                    pass  # Directory might not be empty due to hidden files

        except OSError as e:
            raise FileOperationError(f"Failed to cleanup directories: {e}")

    def get_directory_size(self, directory: Path) -> int:
        """Get total size of directory in bytes."""
        if not directory.exists():
            return 0

        total_size = 0
        try:
            for file_path in directory.rglob("*"):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
        except OSError as e:
            raise FileOperationError(f"Failed to calculate directory size: {e}")

        return total_size
