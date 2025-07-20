"""Image service for ClynBoozle application using PIL."""

from typing import Optional, Tuple, Dict, Any
import os
from PIL import Image, ImageTk
import tkinter as tk

from ..config.settings import MediaConfig
from ..utils.exceptions import MediaLoadError


class ImageService:
    """Service for handling image loading, resizing, and caching."""

    def __init__(self) -> None:
        """Initialize the image service."""
        self._image_cache: Dict[str, ImageTk.PhotoImage] = {}
        self._pil_cache: Dict[str, Image.Image] = {}
        self._max_cache_size = 50  # Maximum number of cached images

    def load_image(self, image_path: str) -> Image.Image:
        """Load PIL Image from file path."""
        if not os.path.exists(image_path):
            raise MediaLoadError(f"Image file not found: {image_path}")

        # Check cache first
        if image_path in self._pil_cache:
            return self._pil_cache[image_path].copy()

        try:
            img = Image.open(image_path)

            # Convert to RGB if necessary
            if img.mode in ("RGBA", "LA", "P"):
                # Create white background for transparent images
                background = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                if img.mode in ("RGBA", "LA"):
                    background.paste(img, mask=img.split()[-1])
                    img = background
            elif img.mode != "RGB":
                img = img.convert("RGB")

            # Cache the image if we have space
            if len(self._pil_cache) < self._max_cache_size:
                self._pil_cache[image_path] = img.copy()

            return img

        except Exception as e:
            raise MediaLoadError(f"Failed to load image: {e}")

    def load_image_for_display(
        self,
        image_path: str,
        target_size: Optional[Tuple[int, int]] = None,
        maintain_aspect: bool = True,
    ) -> ImageTk.PhotoImage:
        """Load image and convert to PhotoImage for Tkinter display."""
        cache_key = f"{image_path}_{target_size}_{maintain_aspect}"

        # Check cache first
        if cache_key in self._image_cache:
            return self._image_cache[cache_key]

        try:
            img = self.load_image(image_path)

            # Resize if target size specified
            if target_size:
                img = self.resize_image(img, target_size, maintain_aspect)

            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(img)

            # Cache the PhotoImage if we have space
            if len(self._image_cache) < self._max_cache_size:
                self._image_cache[cache_key] = photo

            return photo

        except Exception as e:
            raise MediaLoadError(f"Failed to load image for display: {e}")

    def resize_image(
        self,
        img: Image.Image,
        target_size: Tuple[int, int],
        maintain_aspect: bool = True,
        center: bool = True,
    ) -> Image.Image:
        """Resize image to target size."""
        target_width, target_height = target_size

        if target_width <= 0 or target_height <= 0:
            raise MediaLoadError("Target size must be positive")

        try:
            if maintain_aspect:
                # Calculate aspect ratio preserving resize
                img_copy = img.copy()
                img_copy.thumbnail((target_width, target_height), Image.Resampling.LANCZOS)

                if center:
                    # Create new image with exact target dimensions and center the resized image
                    new_img = Image.new("RGB", (target_width, target_height), (255, 255, 255))
                    x = (target_width - img_copy.width) // 2
                    y = (target_height - img_copy.height) // 2
                    new_img.paste(img_copy, (x, y))
                    return new_img
                else:
                    return img_copy
            else:
                # Stretch to exact dimensions
                return img.resize((target_width, target_height), Image.Resampling.LANCZOS)

        except Exception as e:
            raise MediaLoadError(f"Failed to resize image: {e}")

    def create_thumbnail(self, img: Image.Image, size: Tuple[int, int] = (100, 100)) -> Image.Image:
        """Create a thumbnail of the image."""
        try:
            thumb = img.copy()
            thumb.thumbnail(size, Image.Resampling.LANCZOS)
            return thumb
        except Exception as e:
            raise MediaLoadError(f"Failed to create thumbnail: {e}")

    def save_image(
        self, img: Image.Image, output_path: str, quality: int = 85, optimize: bool = True
    ) -> None:
        """Save image to file."""
        try:
            # Determine format from file extension
            file_ext = os.path.splitext(output_path)[1].lower()

            if file_ext in [".jpg", ".jpeg"]:
                # Ensure RGB mode for JPEG
                if img.mode != "RGB":
                    img = img.convert("RGB")
                img.save(output_path, "JPEG", quality=quality, optimize=optimize)
            elif file_ext == ".png":
                img.save(output_path, "PNG", optimize=optimize)
            else:
                # Default to PNG
                img.save(output_path, "PNG", optimize=optimize)

        except Exception as e:
            raise MediaLoadError(f"Failed to save image: {e}")

    def get_image_info(self, image_path: str) -> Dict[str, Any]:
        """Get image information (dimensions, format, etc.)."""
        if not os.path.exists(image_path):
            raise MediaLoadError(f"Image file not found: {image_path}")

        try:
            with Image.open(image_path) as img:
                return {
                    "width": img.width,
                    "height": img.height,
                    "mode": img.mode,
                    "format": img.format,
                    "size": os.path.getsize(image_path),
                }
        except Exception as e:
            raise MediaLoadError(f"Failed to get image info: {e}")

    def create_image_sizes(
        self,
        source_path: str,
        output_dir: str,
        filename_prefix: str,
        sizes: Optional[Dict[str, Tuple[int, int]]] = None,
    ) -> Dict[str, str]:
        """Create multiple sizes of an image."""
        if sizes is None:
            sizes = MediaConfig.IMAGE_SIZES

        img = self.load_image(source_path)
        file_ext = os.path.splitext(source_path)[1]
        size_paths = {}

        try:
            for size_name, (width, height) in sizes.items():
                resized_img = self.resize_image(img, (width, height))
                size_filename = f"{filename_prefix}_{size_name}{file_ext}"
                size_path = os.path.join(output_dir, size_name, size_filename)

                # Ensure directory exists
                os.makedirs(os.path.dirname(size_path), exist_ok=True)

                # Save with appropriate quality
                quality = MediaConfig.JPEG_QUALITY if file_ext.lower() in [".jpg", ".jpeg"] else 90
                self.save_image(resized_img, size_path, quality=quality)
                size_paths[size_name] = size_path

            return size_paths

        except Exception as e:
            raise MediaLoadError(f"Failed to create image sizes: {e}")

    def clear_cache(self) -> None:
        """Clear all cached images."""
        self._image_cache.clear()
        self._pil_cache.clear()

    def clear_cache_for_path(self, image_path: str) -> None:
        """Clear cache entries for a specific image path."""
        # Remove PIL cache entry
        self._pil_cache.pop(image_path, None)

        # Remove PhotoImage cache entries (they contain the path in the key)
        keys_to_remove = [key for key in self._image_cache.keys() if key.startswith(image_path)]
        for key in keys_to_remove:
            self._image_cache.pop(key, None)

    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        return {
            "pil_cache_size": len(self._pil_cache),
            "photo_cache_size": len(self._image_cache),
            "max_cache_size": self._max_cache_size,
        }

    def set_max_cache_size(self, size: int) -> None:
        """Set maximum cache size."""
        if size < 0:
            raise ValueError("Cache size cannot be negative")

        self._max_cache_size = size

        # Trim cache if it's too large
        while len(self._pil_cache) > size:
            # Remove oldest entry (not LRU, just first in dict)
            oldest_key = next(iter(self._pil_cache))
            self._pil_cache.pop(oldest_key)

        while len(self._image_cache) > size:
            oldest_key = next(iter(self._image_cache))
            self._image_cache.pop(oldest_key)
