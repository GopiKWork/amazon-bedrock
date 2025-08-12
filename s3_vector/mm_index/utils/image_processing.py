"""
Image Processing Utilities
==========================

Centralized image processing utilities for the MM Index library.
Consolidates common image operations used across different components.
"""

import base64
import io
import pathlib
import logging
from typing import Union, Tuple, Optional
from PIL import Image as PILImage

logger = logging.getLogger(__name__)


class ImageProcessor:
    """
    Centralized image processing utilities.
    
    This class provides static methods for common image operations
    used throughout the MM Index library, eliminating code duplication.
    """
    
    @staticmethod
    def load_image(image: Union[str, bytes, PILImage.Image]) -> PILImage.Image:
        """
        Load image from various formats into PIL Image.
        
        Args:
            image: Image data (file path, PIL Image, or bytes)
            
        Returns:
            PIL Image object
            
        Raises:
            ValueError: If image format is unsupported
        """
        try:
            if isinstance(image, str):
                # Image file path
                return PILImage.open(image)
            elif isinstance(image, PILImage.Image):
                # Already a PIL Image
                return image
            elif isinstance(image, bytes):
                # Raw image bytes
                return PILImage.open(io.BytesIO(image))
            else:
                raise ValueError(f"Unsupported image type: {type(image)}")
        except Exception as e:
            raise ValueError(f"Failed to load image: {e}") from e
    
    @staticmethod
    def is_valid_image(image: Union[str, bytes, PILImage.Image]) -> bool:
        """
        Check if image data is valid and can be processed.
        
        Args:
            image: Image data (file path, PIL Image, or bytes)
            
        Returns:
            True if image is valid
        """
        try:
            if isinstance(image, str):
                # File path - basic validation
                return len(image) > 0 and pathlib.Path(image).exists()
            elif isinstance(image, PILImage.Image):
                # PIL Image
                return True
            elif isinstance(image, bytes):
                # Raw bytes - try to open as image
                PILImage.open(io.BytesIO(image))
                return True
            else:
                return False
        except Exception:
            return False
    
    @staticmethod
    def resize_image(image: PILImage.Image, 
                    size: Tuple[int, int], 
                    preserve_aspect_ratio: bool = True,
                    resample_method = PILImage.LANCZOS) -> PILImage.Image:
        """
        Resize image according to specifications.
        
        Args:
            image: PIL Image to resize
            size: Target size as (width, height)
            preserve_aspect_ratio: Whether to preserve aspect ratio
            resample_method: PIL resampling method
            
        Returns:
            Resized PIL Image
        """
        original_size = image.size
        target_width, target_height = size
        
        if original_size == size:
            logger.debug("Image already at target size, no resizing needed")
            return image
        
        if preserve_aspect_ratio:
            # Calculate size preserving aspect ratio
            original_width, original_height = original_size
            aspect_ratio = original_width / original_height
            
            if aspect_ratio > (target_width / target_height):
                # Width is the limiting factor
                new_width = target_width
                new_height = int(target_width / aspect_ratio)
            else:
                # Height is the limiting factor
                new_height = target_height
                new_width = int(target_height * aspect_ratio)
            
            # Resize to calculated dimensions
            resized = image.resize((new_width, new_height), resample_method)
            
            # Create new image with target size and paste resized image
            final_image = PILImage.new('RGB', size, (0, 0, 0))
            
            # Center the resized image
            x_offset = (target_width - new_width) // 2
            y_offset = (target_height - new_height) // 2
            final_image.paste(resized, (x_offset, y_offset))
            
            logger.debug(f"Resized with aspect ratio: {original_size} -> {size} (actual: {new_width}x{new_height})")
            return final_image
        else:
            # Force exact dimensions
            resized = image.resize(size, resample_method)
            logger.debug(f"Resized to exact dimensions: {original_size} -> {size}")
            return resized
    
    @staticmethod
    def image_to_bytes(image: Union[str, bytes, PILImage.Image], 
                      resize: bool = False, 
                      size: Tuple[int, int] = (256, 256),
                      format: str = 'JPEG') -> bytes:
        """
        Convert image to bytes with optional resizing.
        
        Args:
            image: Image data (file path, PIL Image, or bytes)
            resize: Whether to resize the image
            size: Target size for resizing
            format: Output format
            
        Returns:
            Image data as bytes
        """
        # Load image
        pil_image = ImageProcessor.load_image(image)
        
        # Resize if requested
        if resize:
            pil_image = ImageProcessor.resize_image(pil_image, size, preserve_aspect_ratio=False)
        
        # Convert to bytes
        buffer = io.BytesIO()
        pil_image.save(buffer, format=format)
        return buffer.getvalue()
    
    @staticmethod
    def image_to_base64(image: Union[str, bytes, PILImage.Image], 
                       resize: bool = False, 
                       size: Tuple[int, int] = (256, 256)) -> str:
        """
        Convert image to base64 string with optional resizing.
        
        Args:
            image: Image data (file path, PIL Image, or bytes)
            resize: Whether to resize the image
            size: Target size for resizing
            
        Returns:
            Base64 encoded image string
        """
        # Convert to bytes first
        img_bytes = ImageProcessor.image_to_bytes(image, resize=resize, size=size)
        
        # Encode to base64
        return base64.b64encode(img_bytes).decode("utf-8")
    
    @staticmethod
    def image_to_base64_with_type(image: Union[str, bytes, PILImage.Image], 
                                 resize: bool = False, 
                                 size: Tuple[int, int] = (256, 256)) -> Tuple[str, str]:
        """
        Convert image to base64 string and determine media type.
        
        Args:
            image: Image data (file path, PIL Image, or bytes)
            resize: Whether to resize the image
            size: Target size for resizing
            
        Returns:
            Tuple of (base64_string, media_type)
        """
        if isinstance(image, str):
            # Image file path - determine type from extension
            ext = pathlib.Path(image).suffix[1:].lower()
            if ext == 'jpg':
                ext = 'jpeg'
            media_type = f"image/{ext}"
            
            # Load and process
            pil_image = ImageProcessor.load_image(image)
            if resize:
                pil_image = ImageProcessor.resize_image(pil_image, size, preserve_aspect_ratio=False)
            
            buffer = io.BytesIO()
            pil_image.save(buffer, format=ext.upper())
            img_data = buffer.getvalue()
            
            return base64.b64encode(img_data).decode("utf-8"), media_type
            
        elif isinstance(image, PILImage.Image):
            # PIL Image object
            if resize:
                image = ImageProcessor.resize_image(image, size, preserve_aspect_ratio=False)
            
            buffer = io.BytesIO()
            format_name = image.format or 'JPEG'
            image.save(buffer, format=format_name)
            img_data = buffer.getvalue()
            
            media_type = f"image/{format_name.lower()}"
            return base64.b64encode(img_data).decode("utf-8"), media_type
            
        elif isinstance(image, bytes):
            # Raw image bytes - assume JPEG
            if resize:
                pil_image = ImageProcessor.load_image(image)
                pil_image = ImageProcessor.resize_image(pil_image, size, preserve_aspect_ratio=False)
                buffer = io.BytesIO()
                pil_image.save(buffer, format='JPEG')
                image = buffer.getvalue()
            
            return base64.b64encode(image).decode("utf-8"), "image/jpeg"
        else:
            raise ValueError(f"Unsupported image type: {type(image)}")
    
    @staticmethod
    def get_image_format(image: Union[str, PILImage.Image]) -> str:
        """
        Get the format of an image.
        
        Args:
            image: Image data (file path or PIL Image)
            
        Returns:
            Image format string (e.g., 'JPEG', 'PNG')
        """
        if isinstance(image, str):
            # File path - determine from extension
            ext = pathlib.Path(image).suffix[1:].upper()
            return 'JPEG' if ext == 'JPG' else ext
        elif isinstance(image, PILImage.Image):
            # PIL Image
            return image.format or 'JPEG'
        else:
            raise ValueError(f"Cannot determine format for image type: {type(image)}")