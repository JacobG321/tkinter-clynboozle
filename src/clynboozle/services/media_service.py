"""Media management service for ClynBoozle application."""

from __future__ import annotations
from typing import Dict, Optional, Tuple, Set, Any, List, TYPE_CHECKING
from pathlib import Path
from dataclasses import dataclass, field
import uuid
import shutil
import json
from datetime import datetime

try:
    from PIL import Image, ImageTk
except ImportError:
    Image = None
    ImageTk = None

from ..config.settings import Paths, MediaConfig, Validation
from ..utils.exceptions import MediaLoadError, ValidationError


@dataclass
class MediaInfo:
    """Represents information about a media file."""

    id: str
    media_type: str  # "image" or "audio"
    original_filename: str
    sanitized_filename: str
    description: str = ""
    upload_date: str = field(default_factory=lambda: datetime.now().isoformat())
    file_size: int = 0
    extension: str = ""
    original_path: Optional[str] = None
    size_paths: Dict[str, str] = field(default_factory=dict)
    dimensions: Optional[Dict[str, int]] = None
    audio_path: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "type": self.media_type,
            "original_filename": self.original_filename,
            "sanitized_filename": self.sanitized_filename,
            "description": self.description,
            "upload_date": self.upload_date,
            "file_size": self.file_size,
            "extension": self.extension,
            "original_path": self.original_path,
            "size_paths": self.size_paths,
            "dimensions": self.dimensions,
            "path": self.audio_path,  # For backward compatibility
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> MediaInfo:
        """Create MediaInfo from dictionary."""
        return cls(
            id=data["id"],
            media_type=data["type"],
            original_filename=data["original_filename"],
            sanitized_filename=data["sanitized_filename"],
            description=data.get("description", ""),
            upload_date=data.get("upload_date", datetime.now().isoformat()),
            file_size=data.get("file_size", 0),
            extension=data.get("extension", ""),
            original_path=data.get("original_path"),
            size_paths=data.get("size_paths", {}),
            dimensions=data.get("dimensions"),
            audio_path=data.get("path"),  # For backward compatibility
        )


@dataclass
class StorageStats:
    """Storage statistics for media library."""

    total_items: int = 0
    images: int = 0
    audio: int = 0
    total_size: int = 0


class MediaService:
    """WordPress-style media management system for ClynBoozle."""

    # Supported file formats
    AUDIO_FORMATS: Set[str] = {".wav", ".mp3", ".ogg", ".flac", ".aac"}
    IMAGE_FORMATS: Set[str] = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"}

    def __init__(self, base_dir: Optional[str] = None) -> None:
        """Initialize the media service.

        Args:
            base_dir: Base directory for media storage. If None, uses default from config.
        """
        self.base_dir = Path(base_dir) if base_dir else Path(Paths.UPLOADS_DIR)
        self.uploads_dir = self.base_dir / "uploads"
        self.media_db_file = self.uploads_dir / "media_database.json"

        # Image sizes for different use cases
        self.image_sizes = MediaConfig.IMAGE_SIZES

        self._media_db: Dict[str, MediaInfo] = {}

        self._ensure_directories()
        self._load_media_database()

    def _ensure_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        self.uploads_dir.mkdir(parents=True, exist_ok=True)

        # Create subdirectories for different media types
        for subdir in ["images", "audio", "thumbnails"]:
            (self.uploads_dir / subdir).mkdir(exist_ok=True)

        # Create subdirectories for different image sizes
        images_dir = self.uploads_dir / "images"
        for size_name in self.image_sizes.keys():
            (images_dir / size_name).mkdir(exist_ok=True)

    def _load_media_database(self) -> None:
        """Load the media database from JSON file."""
        self._media_db = {}

        if not self.media_db_file.exists():
            return

        try:
            with open(self.media_db_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Convert dictionary data to MediaInfo objects
            for media_id, media_data in data.items():
                try:
                    self._media_db[media_id] = MediaInfo.from_dict(media_data)
                except (KeyError, TypeError, ValueError) as e:
                    # Skip corrupted entries but log the issue
                    print(f"Warning: Skipping corrupted media entry {media_id}: {e}")

        except (json.JSONDecodeError, OSError) as e:
            raise MediaLoadError(f"Failed to load media database: {e}")

    def _save_media_database(self) -> None:
        """Save the media database to JSON file."""
        try:
            # Convert MediaInfo objects to dictionaries
            data = {media_id: info.to_dict() for media_id, info in self._media_db.items()}

            with open(self.media_db_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        except OSError as e:
            raise MediaLoadError(f"Failed to save media database: {e}")

    def _generate_media_id(self) -> str:
        """Generate a unique media ID."""
        while True:
            media_id = str(uuid.uuid4())
            if media_id not in self._media_db:
                return media_id

    def _get_file_extension(self, filename: str) -> str:
        """Get the file extension in lowercase."""
        return Path(filename).suffix.lower()

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe storage."""
        # Get just the filename without path
        safe_name = Path(filename).name

        # Keep only safe characters
        safe_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-_")
        sanitized = "".join(c if c in safe_chars else "_" for c in safe_name)

        # Ensure it's not empty and doesn't start with a dot
        if not sanitized or sanitized.startswith("."):
            sanitized = f"file_{uuid.uuid4().hex[:8]}{Path(filename).suffix}"

        return sanitized

    def _validate_image_file(self, file_path: Path) -> None:
        """Validate that a file is a valid image."""
        if not file_path.exists():
            raise ValidationError(f"File not found: {file_path}")

        if self._get_file_extension(str(file_path)) not in self.IMAGE_FORMATS:
            raise ValidationError(f"Unsupported image format: {file_path.suffix}")

        if Image is None:
            raise MediaLoadError("PIL/Pillow not available for image processing")

        try:
            with Image.open(file_path) as img:
                img.verify()  # Verify it's a valid image
        except Exception as e:
            raise ValidationError(f"Invalid image file: {e}")

    def _validate_audio_file(self, file_path: Path) -> None:
        """Validate that a file is a valid audio file."""
        if not file_path.exists():
            raise ValidationError(f"File not found: {file_path}")

        if self._get_file_extension(str(file_path)) not in self.AUDIO_FORMATS:
            raise ValidationError(f"Unsupported audio format: {file_path.suffix}")

    def _create_image_sizes(
        self, source_path: Path, media_id: str, original_ext: str
    ) -> Dict[str, str]:
        """Create different sized versions of an image."""
        if Image is None:
            raise MediaLoadError("PIL/Pillow not available for image processing")

        size_paths = {}

        try:
            with Image.open(source_path) as img:
                # Convert to RGB if necessary
                if img.mode in ("RGBA", "LA", "P"):
                    # Create a white background for transparent images
                    background = Image.new("RGB", img.size, (255, 255, 255))
                    if img.mode == "P":
                        img = img.convert("RGBA")
                    background.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
                    img = background
                elif img.mode != "RGB":
                    img = img.convert("RGB")

                # Create each size
                for size_name, (width, height) in self.image_sizes.items():
                    img_copy = img.copy()
                    img_copy.thumbnail((width, height), Image.Resampling.LANCZOS)

                    # Create a new image with exact dimensions (centered)
                    new_img = Image.new("RGB", (width, height), (255, 255, 255))

                    # Calculate position to center the image
                    x = (width - img_copy.width) // 2
                    y = (height - img_copy.height) // 2
                    new_img.paste(img_copy, (x, y))

                    # Save the resized image
                    size_filename = f"{media_id}_{size_name}{original_ext}"
                    size_path = self.uploads_dir / "images" / size_name / size_filename

                    # Use appropriate format and quality
                    if original_ext.lower() in [".jpg", ".jpeg"]:
                        new_img.save(size_path, "JPEG", quality=85, optimize=True)
                    else:
                        new_img.save(size_path, "PNG", optimize=True)

                    size_paths[size_name] = str(size_path)

                # Create thumbnail for management interface
                thumb_img = img.copy()
                thumb_img.thumbnail((100, 100), Image.Resampling.LANCZOS)
                thumb_filename = f"{media_id}_thumb{original_ext}"
                thumb_path = self.uploads_dir / "thumbnails" / thumb_filename

                if original_ext.lower() in [".jpg", ".jpeg"]:
                    thumb_img.save(thumb_path, "JPEG", quality=80, optimize=True)
                else:
                    thumb_img.save(thumb_path, "PNG", optimize=True)

                size_paths["thumbnail"] = str(thumb_path)

        except Exception as e:
            raise MediaLoadError(f"Failed to create image sizes: {e}")

        return size_paths

    def add_image(self, source_path: str, description: str = "") -> str:
        """Add an image to the media library.

        Args:
            source_path: Path to the source image file
            description: Optional description for the image

        Returns:
            The media ID of the added image

        Raises:
            ValidationError: If the file is invalid
            MediaLoadError: If processing fails
        """
        source = Path(source_path)
        self._validate_image_file(source)

        # Generate unique ID and prepare filenames
        media_id = self._generate_media_id()
        original_filename = source.name
        sanitized_filename = self._sanitize_filename(original_filename)
        ext = self._get_file_extension(original_filename)

        try:
            # Copy original file to uploads directory
            original_dest = self.uploads_dir / "images" / f"{media_id}_original{ext}"
            shutil.copy2(source, original_dest)

            # Create different sizes
            size_paths = self._create_image_sizes(original_dest, media_id, ext)

            # Get image dimensions
            with Image.open(original_dest) as img:
                width, height = img.size

            # Create media info
            media_info = MediaInfo(
                id=media_id,
                media_type="image",
                original_filename=original_filename,
                sanitized_filename=sanitized_filename,
                description=description,
                file_size=original_dest.stat().st_size,
                dimensions={"width": width, "height": height},
                extension=ext,
                original_path=str(original_dest),
                size_paths=size_paths,
            )

            # Add to database
            self._media_db[media_id] = media_info
            self._save_media_database()

            return media_id

        except Exception as e:
            # Clean up on failure
            if original_dest.exists():
                original_dest.unlink()
            raise MediaLoadError(f"Failed to add image: {e}")

    def add_audio(self, source_path: str, description: str = "") -> str:
        """Add an audio file to the media library.

        Args:
            source_path: Path to the source audio file
            description: Optional description for the audio

        Returns:
            The media ID of the added audio

        Raises:
            ValidationError: If the file is invalid
            MediaLoadError: If processing fails
        """
        source = Path(source_path)
        self._validate_audio_file(source)

        # Generate unique ID and prepare filenames
        media_id = self._generate_media_id()
        original_filename = source.name
        sanitized_filename = self._sanitize_filename(original_filename)
        ext = self._get_file_extension(original_filename)

        try:
            # Copy file to uploads directory
            dest_filename = f"{media_id}{ext}"
            dest_path = self.uploads_dir / "audio" / dest_filename
            shutil.copy2(source, dest_path)

            # Create media info
            media_info = MediaInfo(
                id=media_id,
                media_type="audio",
                original_filename=original_filename,
                sanitized_filename=sanitized_filename,
                description=description,
                file_size=dest_path.stat().st_size,
                extension=ext,
                audio_path=str(dest_path),
            )

            # Add to database
            self._media_db[media_id] = media_info
            self._save_media_database()

            return media_id

        except Exception as e:
            # Clean up on failure
            if dest_path.exists():
                dest_path.unlink()
            raise MediaLoadError(f"Failed to add audio: {e}")

    def get_media_info(self, media_id: str) -> Optional[MediaInfo]:
        """Get media information by ID."""
        return self._media_db.get(media_id)

    def get_image_path(self, media_id: str, size: str = "original") -> Optional[str]:
        """Get the path to a specific size of an image."""
        media_info = self._media_db.get(media_id)
        if not media_info or media_info.media_type != "image":
            return None

        if size == "original":
            path = media_info.original_path
        else:
            path = media_info.size_paths.get(size)

        # Check if file actually exists
        if path and Path(path).exists():
            return path

        return None

    def get_audio_path(self, media_id: str) -> Optional[str]:
        """Get the path to an audio file."""
        media_info = self._media_db.get(media_id)
        if not media_info or media_info.media_type != "audio":
            return None

        path = media_info.audio_path
        if path and Path(path).exists():
            return path

        return None

    def load_image_for_display(self, media_id: str, size: str = "thumbnail") -> Optional[Any]:
        """Load an image for display in Tkinter.

        Returns None if PIL/Pillow is not available or image cannot be loaded.
        """
        if ImageTk is None:
            return None

        image_path = self.get_image_path(media_id, size)
        if not image_path:
            return None

        try:
            img = Image.open(image_path)
            return ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Warning: Could not load image for display: {e}")
            return None

    def delete_media(self, media_id: str) -> bool:
        """Delete a media item and all its files."""
        media_info = self._media_db.get(media_id)
        if not media_info:
            return False

        try:
            if media_info.media_type == "image":
                # Delete original file
                if media_info.original_path:
                    original_path = Path(media_info.original_path)
                    if original_path.exists():
                        original_path.unlink()

                # Delete all size variants
                for path_str in media_info.size_paths.values():
                    path = Path(path_str)
                    if path.exists():
                        path.unlink()

            elif media_info.media_type == "audio":
                # Delete audio file
                if media_info.audio_path:
                    audio_path = Path(media_info.audio_path)
                    if audio_path.exists():
                        audio_path.unlink()

            # Remove from database
            del self._media_db[media_id]
            self._save_media_database()
            return True

        except Exception as e:
            print(f"Warning: Error deleting media {media_id}: {e}")
            return False

    def get_all_media(self, media_type: Optional[str] = None) -> List[MediaInfo]:
        """Get all media items, optionally filtered by type."""
        if media_type:
            return [info for info in self._media_db.values() if info.media_type == media_type]
        return list(self._media_db.values())

    def cleanup_orphaned_files(self) -> int:
        """Remove files that are no longer referenced in the database.

        Returns:
            Number of files removed
        """
        referenced_files = set()

        # Collect all referenced files
        for media_info in self._media_db.values():
            if media_info.media_type == "image":
                if media_info.original_path:
                    referenced_files.add(media_info.original_path)

                for path in media_info.size_paths.values():
                    referenced_files.add(path)

            elif media_info.media_type == "audio":
                if media_info.audio_path:
                    referenced_files.add(media_info.audio_path)

        # Find and remove orphaned files
        removed_count = 0
        for root, dirs, files in self.uploads_dir.rglob("*"):
            if root.is_file() and str(root) not in referenced_files:
                if root.name != "media_database.json":
                    try:
                        root.unlink()
                        removed_count += 1
                        print(f"Removed orphaned file: {root}")
                    except Exception as e:
                        print(f"Warning: Error removing orphaned file {root}: {e}")

        return removed_count

    def get_storage_stats(self) -> StorageStats:
        """Get storage statistics."""
        stats = StorageStats()

        for media_info in self._media_db.values():
            stats.total_items += 1

            if media_info.media_type == "image":
                stats.images += 1
            elif media_info.media_type == "audio":
                stats.audio += 1

            stats.total_size += media_info.file_size

        return stats

    def validate_database_integrity(self) -> List[str]:
        """Validate database integrity and return list of issues found."""
        issues = []

        for media_id, media_info in self._media_db.items():
            # Check if referenced files exist
            if media_info.media_type == "image":
                if media_info.original_path and not Path(media_info.original_path).exists():
                    issues.append(f"Missing original image file for {media_id}")

                for size_name, path in media_info.size_paths.items():
                    if not Path(path).exists():
                        issues.append(f"Missing {size_name} image file for {media_id}")

            elif media_info.media_type == "audio":
                if media_info.audio_path and not Path(media_info.audio_path).exists():
                    issues.append(f"Missing audio file for {media_id}")

        return issues
