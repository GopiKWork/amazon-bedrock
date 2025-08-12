"""
Image Resizer Preprocessor
==========================

Preprocessor for resizing images to standard dimensions.
"""

from typing import Dict, Any, Tuple
import logging
from PIL import Image as PILImage
import io

from .base import Preprocessor
from ..utils.image_processing import ImageProcessor

logger = logging.getLogger(__name__)


class ImageResizer(Preprocessor):
    """
    Image resizing preprocessor with configurable dimensions.
    
    This preprocessor resizes images to standard dimensions while preserving
    aspect ratio or forcing specific dimensions based on configuration.
    """
    
    def __init__(self, 
                 target_size: Tuple[int, int] = (256, 256),
                 preserve_aspect_ratio: bool = True,
                 resample_method: int = PILImage.LANCZOS):
        """
        Initialize ImageResizer preprocessor.
        
        Args:
            target_size: Target dimensions (width, height)
            preserve_aspect_ratio: Whether to preserve aspect ratio
            resample_method: PIL resampling method
        """
        self.target_size = target_size
        self.preserve_aspect_ratio = preserve_aspect_ratio
        self.resample_method = resample_method
        
        logger.debug(f"Initialized ImageResizer: target_size={target_size}, preserve_aspect={preserve_aspect_ratio}")
    
    @property
    def processor_name(self) -> str:
        """Return the processor name."""
        return "image_resizer"
    
    def get_supported_keys(self) -> list[str]:
        """Image resizer supports 'image' key."""
        return ['image']
    
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """
        Validate that data contains a valid image.
        
        Args:
            data: Input data dictionary
            
        Returns:
            True if data contains valid image
        """
        if 'image' not in data:
            return False
        
        image = data['image']
        return self._is_valid_image(image)
    
    def _is_valid_image(self, image) -> bool:
        """
        Check if image data is valid and can be processed.
        
        Args:
            image: Image data (file path, PIL Image, or bytes)
            
        Returns:
            True if image is valid
        """
        return ImageProcessor.is_valid_image(image)
    
    def _load_image(self, image) -> PILImage.Image:
        """
        Load image from various formats into PIL Image.
        
        Args:
            image: Image data (file path, PIL Image, or bytes)
            
        Returns:
            PIL Image object
            
        Raises:
            ValueError: If image format is unsupported
        """
        return ImageProcessor.load_image(image)
    
    def _resize_image(self, image: PILImage.Image) -> PILImage.Image:
        """
        Resize image according to configuration.
        
        Args:
            image: PIL Image to resize
            
        Returns:
            Resized PIL Image
        """
        return ImageProcessor.resize_image(
            image, 
            self.target_size, 
            preserve_aspect_ratio=self.preserve_aspect_ratio,
            resample_method=self.resample_method
        )
    
    def _image_to_bytes(self, image: PILImage.Image, format: str = 'JPEG') -> bytes:
        """
        Convert PIL Image to bytes.
        
        Args:
            image: PIL Image to convert
            format: Output format
            
        Returns:
            Image data as bytes
        """
        return ImageProcessor.image_to_bytes(image, resize=False, format=format)
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process and resize image in data.
        
        Args:
            data: Input data dictionary containing 'image' key
            
        Returns:
            Data dictionary with resized image
            
        Raises:
            ValueError: If image is invalid or processing fails
        """
        if not self.should_process(data):
            logger.debug("No image to process, returning data unchanged")
            return data
        
        if not self.validate_data(data):
            raise ValueError("Invalid image data for resizing")
        
        image = data['image']
        logger.debug(f"Processing image resize: target_size={self.target_size}")
        
        try:
            # Load image
            pil_image = self._load_image(image)
            original_size = pil_image.size
            
            # Resize image
            resized_image = self._resize_image(pil_image)
            
            # Prepare result data
            result = data.copy()
            
            # Determine output format based on input
            if isinstance(image, str):
                # Keep as file path - save resized image to temp location or return PIL Image
                result['image'] = resized_image
            elif isinstance(image, PILImage.Image):
                # Return as PIL Image
                result['image'] = resized_image
            elif isinstance(image, bytes):
                # Return as bytes
                result['image'] = self._image_to_bytes(resized_image)
            
            # Add preprocessing metadata
            result = self._add_preprocessing_metadata(result)
            
            # Add resize-specific metadata
            result['_resize_info'] = {
                'original_size': original_size,
                'target_size': self.target_size,
                'preserve_aspect_ratio': self.preserve_aspect_ratio,
                'actual_size': resized_image.size
            }
            
            logger.debug(f"Image resized successfully: {original_size} -> {resized_image.size}")
            return result
            
        except Exception as e:
            logger.error(f"Image resize failed: {e}")
            raise ValueError(f"Image resize processing failed: {e}") from e