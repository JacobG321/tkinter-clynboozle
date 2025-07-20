import os
import uuid
import shutil
from PIL import Image, ImageTk
from typing import Optional, Dict, Tuple
import json
from datetime import datetime


class MediaManager:
    """WordPress-style media management system for ClynBoozle"""
    
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.uploads_dir = os.path.join(base_dir, "uploads")
        self.media_db_file = os.path.join(self.uploads_dir, "media_database.json")
        
        # Image sizes for different use cases
        self.image_sizes = {
            "tile": (120, 80),           # For game board tiles
            "tile_2x": (240, 160),       # For high-DPI displays
            "question": (400, 300),      # For question display
            "question_large": (800, 600), # For full-screen question display
            "thumbnail": (100, 100),     # For management interface
        }
        
        # Audio formats supported
        self.audio_formats = {'.wav', '.mp3', '.ogg', '.flac', '.aac'}
        self.image_formats = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'}
        
        self._ensure_directories()
        self._load_media_database()
    
    def _ensure_directories(self):
        """Create necessary directories if they don't exist"""
        os.makedirs(self.uploads_dir, exist_ok=True)
        
        # Create subdirectories for different media types
        for subdir in ['images', 'audio', 'thumbnails']:
            os.makedirs(os.path.join(self.uploads_dir, subdir), exist_ok=True)
            
        # Create subdirectories for different image sizes
        images_dir = os.path.join(self.uploads_dir, 'images')
        for size_name in self.image_sizes.keys():
            os.makedirs(os.path.join(images_dir, size_name), exist_ok=True)
    
    def _load_media_database(self):
        """Load the media database from JSON file"""
        self.media_db = {}
        if os.path.exists(self.media_db_file):
            try:
                with open(self.media_db_file, 'r') as f:
                    self.media_db = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.media_db = {}
    
    def _save_media_database(self):
        """Save the media database to JSON file"""
        try:
            with open(self.media_db_file, 'w') as f:
                json.dump(self.media_db, f, indent=2)
        except IOError as e:
            print(f"Error saving media database: {e}")
    
    def _generate_media_id(self) -> str:
        """Generate a unique media ID"""
        return str(uuid.uuid4())
    
    def _get_file_extension(self, filename: str) -> str:
        """Get the file extension in lowercase"""
        return os.path.splitext(filename)[1].lower()
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe storage"""
        # Remove path and keep only the filename
        filename = os.path.basename(filename)
        # Replace spaces and special characters
        safe_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-_"
        sanitized = "".join(c if c in safe_chars else "_" for c in filename)
        return sanitized
    
    def _create_image_sizes(self, source_path: str, media_id: str, original_ext: str) -> Dict[str, str]:
        """Create different sized versions of an image"""
        size_paths = {}
        
        try:
            with Image.open(source_path) as img:
                # Convert to RGB if necessary (for PNG with transparency, etc.)
                if img.mode in ('RGBA', 'LA', 'P'):
                    # Create a white background for transparent images
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Create each size
                for size_name, (width, height) in self.image_sizes.items():
                    # Calculate the aspect ratio preserving resize
                    img_copy = img.copy()
                    img_copy.thumbnail((width, height), Image.Resampling.LANCZOS)
                    
                    # Create a new image with the exact dimensions (centered)
                    new_img = Image.new('RGB', (width, height), (255, 255, 255))
                    
                    # Calculate position to center the image
                    x = (width - img_copy.width) // 2
                    y = (height - img_copy.height) // 2
                    new_img.paste(img_copy, (x, y))
                    
                    # Save the resized image
                    size_filename = f"{media_id}_{size_name}{original_ext}"
                    size_path = os.path.join(self.uploads_dir, 'images', size_name, size_filename)
                    
                    # Use appropriate format and quality
                    if original_ext.lower() in ['.jpg', '.jpeg']:
                        new_img.save(size_path, 'JPEG', quality=85, optimize=True)
                    else:
                        new_img.save(size_path, 'PNG', optimize=True)
                    
                    size_paths[size_name] = size_path
                
                # Create thumbnail for management interface
                thumb_img = img.copy()
                thumb_img.thumbnail((100, 100), Image.Resampling.LANCZOS)
                thumb_filename = f"{media_id}_thumb{original_ext}"
                thumb_path = os.path.join(self.uploads_dir, 'thumbnails', thumb_filename)
                
                if original_ext.lower() in ['.jpg', '.jpeg']:
                    thumb_img.save(thumb_path, 'JPEG', quality=80, optimize=True)
                else:
                    thumb_img.save(thumb_path, 'PNG', optimize=True)
                
                size_paths['thumbnail'] = thumb_path
                
        except Exception as e:
            print(f"Error creating image sizes: {e}")
            return {}
        
        return size_paths
    
    def add_image(self, source_path: str, description: str = "") -> Optional[str]:
        """Add an image to the media library"""
        if not os.path.exists(source_path):
            return None
        
        # Check if it's a valid image format
        ext = self._get_file_extension(source_path)
        if ext not in self.image_formats:
            return None
        
        try:
            # Generate unique ID and sanitized filename
            media_id = self._generate_media_id()
            original_filename = os.path.basename(source_path)
            sanitized_filename = self._sanitize_filename(original_filename)
            
            # Copy original file to uploads directory
            original_dest = os.path.join(self.uploads_dir, 'images', f"{media_id}_original{ext}")
            shutil.copy2(source_path, original_dest)
            
            # Create different sizes
            size_paths = self._create_image_sizes(original_dest, media_id, ext)
            
            if not size_paths:
                # Clean up if size creation failed
                if os.path.exists(original_dest):
                    os.remove(original_dest)
                return None
            
            # Get image dimensions
            with Image.open(original_dest) as img:
                width, height = img.size
            
            # Add to database
            self.media_db[media_id] = {
                'id': media_id,
                'type': 'image',
                'original_filename': original_filename,
                'sanitized_filename': sanitized_filename,
                'description': description,
                'upload_date': datetime.now().isoformat(),
                'file_size': os.path.getsize(original_dest),
                'dimensions': {'width': width, 'height': height},
                'extension': ext,
                'original_path': original_dest,
                'size_paths': size_paths
            }
            
            self._save_media_database()
            return media_id
            
        except Exception as e:
            print(f"Error adding image: {e}")
            return None
    
    def add_audio(self, source_path: str, description: str = "") -> Optional[str]:
        """Add an audio file to the media library"""
        if not os.path.exists(source_path):
            return None
        
        # Check if it's a valid audio format
        ext = self._get_file_extension(source_path)
        if ext not in self.audio_formats:
            return None
        
        try:
            # Generate unique ID and sanitized filename
            media_id = self._generate_media_id()
            original_filename = os.path.basename(source_path)
            sanitized_filename = self._sanitize_filename(original_filename)
            
            # Copy file to uploads directory
            dest_filename = f"{media_id}{ext}"
            dest_path = os.path.join(self.uploads_dir, 'audio', dest_filename)
            shutil.copy2(source_path, dest_path)
            
            # Add to database
            self.media_db[media_id] = {
                'id': media_id,
                'type': 'audio',
                'original_filename': original_filename,
                'sanitized_filename': sanitized_filename,
                'description': description,
                'upload_date': datetime.now().isoformat(),
                'file_size': os.path.getsize(dest_path),
                'extension': ext,
                'path': dest_path
            }
            
            self._save_media_database()
            return media_id
            
        except Exception as e:
            print(f"Error adding audio: {e}")
            return None
    
    def get_media_info(self, media_id: str) -> Optional[Dict]:
        """Get media information by ID"""
        return self.media_db.get(media_id)
    
    def get_image_path(self, media_id: str, size: str = "original") -> Optional[str]:
        """Get the path to a specific size of an image"""
        media_info = self.media_db.get(media_id)
        if not media_info or media_info['type'] != 'image':
            return None
        
        if size == "original":
            return media_info.get('original_path')
        
        size_paths = media_info.get('size_paths', {})
        path = size_paths.get(size)
        
        # Check if file actually exists
        if path and os.path.exists(path):
            return path
        
        return None
    
    def get_audio_path(self, media_id: str) -> Optional[str]:
        """Get the path to an audio file"""
        media_info = self.media_db.get(media_id)
        if not media_info or media_info['type'] != 'audio':
            return None
        
        path = media_info.get('path')
        if path and os.path.exists(path):
            return path
        
        return None
    
    def load_image_for_display(self, media_id: str, size: str = "thumbnail") -> Optional[ImageTk.PhotoImage]:
        """Load an image for display in Tkinter"""
        image_path = self.get_image_path(media_id, size)
        if not image_path:
            return None
        
        try:
            img = Image.open(image_path)
            return ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Error loading image for display: {e}")
            return None
    
    def delete_media(self, media_id: str) -> bool:
        """Delete a media item and all its files"""
        media_info = self.media_db.get(media_id)
        if not media_info:
            return False
        
        try:
            if media_info['type'] == 'image':
                # Delete original file
                original_path = media_info.get('original_path')
                if original_path and os.path.exists(original_path):
                    os.remove(original_path)
                
                # Delete all size variants
                size_paths = media_info.get('size_paths', {})
                for path in size_paths.values():
                    if os.path.exists(path):
                        os.remove(path)
            
            elif media_info['type'] == 'audio':
                # Delete audio file
                path = media_info.get('path')
                if path and os.path.exists(path):
                    os.remove(path)
            
            # Remove from database
            del self.media_db[media_id]
            self._save_media_database()
            return True
            
        except Exception as e:
            print(f"Error deleting media: {e}")
            return False
    
    def get_all_media(self, media_type: Optional[str] = None) -> Dict[str, Dict]:
        """Get all media items, optionally filtered by type"""
        if media_type:
            return {
                media_id: info for media_id, info in self.media_db.items()
                if info.get('type') == media_type
            }
        return self.media_db.copy()
    
    def cleanup_orphaned_files(self):
        """Remove files that are no longer referenced in the database"""
        referenced_files = set()
        
        # Collect all referenced files
        for media_info in self.media_db.values():
            if media_info['type'] == 'image':
                original_path = media_info.get('original_path')
                if original_path:
                    referenced_files.add(original_path)
                
                size_paths = media_info.get('size_paths', {})
                for path in size_paths.values():
                    referenced_files.add(path)
            
            elif media_info['type'] == 'audio':
                path = media_info.get('path')
                if path:
                    referenced_files.add(path)
        
        # Find and remove orphaned files
        for root, dirs, files in os.walk(self.uploads_dir):
            for file in files:
                if file == 'media_database.json':
                    continue
                
                file_path = os.path.join(root, file)
                if file_path not in referenced_files:
                    try:
                        os.remove(file_path)
                        print(f"Removed orphaned file: {file_path}")
                    except Exception as e:
                        print(f"Error removing orphaned file {file_path}: {e}")
    
    def get_storage_stats(self) -> Dict:
        """Get storage statistics"""
        stats = {
            'total_items': len(self.media_db),
            'images': 0,
            'audio': 0,
            'total_size': 0
        }
        
        for media_info in self.media_db.values():
            if media_info['type'] == 'image':
                stats['images'] += 1
            elif media_info['type'] == 'audio':
                stats['audio'] += 1
            
            stats['total_size'] += media_info.get('file_size', 0)
        
        return stats
