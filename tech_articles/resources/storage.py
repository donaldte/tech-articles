"""Storage utilities for media file handling with AWS S3."""
from __future__ import annotations

import mimetypes
import os
from io import BytesIO
from typing import TYPE_CHECKING

from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image

if TYPE_CHECKING:
    from django.core.files.uploadedfile import UploadedFile


class MediaStorage:
    """Handle media file storage operations with S3."""
    
    @staticmethod
    def get_file_type(mime_type: str) -> str:
        """Determine file type from MIME type."""
        if mime_type.startswith("image/"):
            return "image"
        elif mime_type.startswith("video/"):
            return "video"
        elif mime_type.startswith("audio/"):
            return "audio"
        elif mime_type in [
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/vnd.ms-excel",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/vnd.ms-powerpoint",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        ]:
            return "document"
        return "other"
    
    @staticmethod
    def generate_file_key(file_name: str, folder_path: str = "") -> str:
        """Generate unique S3 key for file."""
        import uuid
        from django.utils.text import slugify
        
        # Extract extension
        name, ext = os.path.splitext(file_name)
        # Create unique name
        unique_name = f"{slugify(name)}-{uuid.uuid4().hex[:8]}{ext}"
        
        if folder_path:
            return f"media/{folder_path}/{unique_name}"
        return f"media/{unique_name}"
    
    @staticmethod
    def save_to_s3(file_obj: UploadedFile, file_key: str) -> str:
        """Save file to S3 and return the key."""
        from django.core.files.storage import default_storage
        
        # Save file using Django's storage backend
        saved_path = default_storage.save(file_key, file_obj)
        return saved_path
    
    @staticmethod
    def delete_from_s3(file_key: str) -> bool:
        """Delete file from S3."""
        from django.core.files.storage import default_storage
        
        try:
            if default_storage.exists(file_key):
                default_storage.delete(file_key)
                return True
            return False
        except Exception:
            return False
    
    @staticmethod
    def get_file_url(file_key: str) -> str:
        """Get public URL for file (CloudFront or S3)."""
        from django.core.files.storage import default_storage
        
        return default_storage.url(file_key)


class ImageOptimizer:
    """Optimize and resize images."""
    
    # Image quality settings
    THUMBNAIL_SIZE = (300, 300)
    OPTIMIZED_SIZE = (1920, 1080)
    QUALITY = 85
    THUMBNAIL_QUALITY = 80
    
    @staticmethod
    def get_image_dimensions(image_file: UploadedFile) -> tuple[int, int]:
        """Get image width and height."""
        try:
            image = Image.open(image_file)
            width, height = image.size
            image_file.seek(0)  # Reset file pointer
            return width, height
        except Exception:
            return 0, 0
    
    @staticmethod
    def optimize_image(
        image_file: UploadedFile,
        max_size: tuple[int, int] = None,
        quality: int = None,
    ) -> InMemoryUploadedFile:
        """Optimize image by resizing and compressing."""
        if max_size is None:
            max_size = ImageOptimizer.OPTIMIZED_SIZE
        if quality is None:
            quality = ImageOptimizer.QUALITY
        
        try:
            # Open image
            image = Image.open(image_file)
            
            # Convert RGBA to RGB if necessary
            if image.mode in ("RGBA", "LA", "P"):
                background = Image.new("RGB", image.size, (255, 255, 255))
                if image.mode == "P":
                    image = image.convert("RGBA")
                channels = image.split()
                background.paste(image, mask=channels[-1] if len(channels) > 3 else None)
                image = background
            elif image.mode != "RGB":
                image = image.convert("RGB")
            
            # Resize if necessary
            if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Save to BytesIO
            output = BytesIO()
            image.save(output, format="JPEG", quality=quality, optimize=True)
            output.seek(0)
            
            # Create InMemoryUploadedFile
            return InMemoryUploadedFile(
                output,
                "ImageField",
                f"{os.path.splitext(image_file.name)[0]}.jpg",
                "image/jpeg",
                output.getbuffer().nbytes,
                None,
            )
        except Exception as e:
            # If optimization fails, return original
            image_file.seek(0)
            return image_file
    
    @staticmethod
    def create_thumbnail(
        image_file: UploadedFile,
        size: tuple[int, int] = None,
        quality: int = None,
    ) -> InMemoryUploadedFile:
        """Create thumbnail version of image."""
        if size is None:
            size = ImageOptimizer.THUMBNAIL_SIZE
        if quality is None:
            quality = ImageOptimizer.THUMBNAIL_QUALITY
        
        return ImageOptimizer.optimize_image(image_file, max_size=size, quality=quality)
    
    @staticmethod
    def is_valid_image(file_obj: UploadedFile) -> bool:
        """Check if file is a valid image."""
        try:
            image = Image.open(file_obj)
            image.verify()
            file_obj.seek(0)
            return True
        except Exception:
            return False


def validate_file_size(file_obj: UploadedFile, max_size_mb: int = 50) -> tuple[bool, str]:
    """Validate file size."""
    max_size_bytes = max_size_mb * 1024 * 1024
    if file_obj.size > max_size_bytes:
        return False, f"File size exceeds {max_size_mb}MB limit"
    return True, ""


def validate_file_type(file_obj: UploadedFile, allowed_types: list[str] = None) -> tuple[bool, str]:
    """Validate file MIME type."""
    if allowed_types is None:
        # Default allowed types
        allowed_types = [
            "image/jpeg",
            "image/png",
            "image/gif",
            "image/webp",
            "video/mp4",
            "video/webm",
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ]
    
    mime_type = file_obj.content_type
    if mime_type not in allowed_types:
        return False, f"File type {mime_type} is not allowed"
    return True, ""
