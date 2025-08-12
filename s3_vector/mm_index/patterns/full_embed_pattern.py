"""
Full Embedding Pattern Strategy
===============================

Pattern strategy for unified multimodal embeddings from text and image.
"""

from typing import Dict, Any, Optional, Tuple
import numpy as np
import logging
from PIL import Image as PILImage
import io

from .base import PatternStrategy
from ..base_classes import BaseEmbeddingModel

logger = logging.getLogger(__name__)


class FullEmbedPattern(PatternStrategy):
    """
    Full embedding pattern strategy for multimodal data.
    
    This pattern generates unified embeddings from both text and image
    content using a multimodal embedding model. Both text and image
    contribute to the final embedding representation.
    """
    
    def __init__(self, embedding_model: BaseEmbeddingModel):
        """
        Initialize FullEmbedPattern with multimodal embedding model.
        
        Args:
            embedding_model: Model capable of generating multimodal embeddings
        """
        self.embedding_model = embedding_model
        logger.debug(f"Initialized FullEmbedPattern with {type(embedding_model).__name__}")
    
    @property
    def pattern_name(self) -> str:
        """Return the pattern name."""
        return "full_embedding"
    
    def get_required_keys(self) -> list[str]:
        """Full embedding pattern requires at least text or image."""
        return []  # At least one of text or image is required, validated in validate_data
    
    def get_optional_keys(self) -> list[str]:
        """Full embedding pattern accepts both text and image."""
        return ['text', 'image']
    
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """
        Validate that data contains at least text or image.
        
        Args:
            data: Input data dictionary
            
        Returns:
            True if data is valid for full embedding pattern
        """
        has_text = 'text' in data and isinstance(data['text'], str) and data['text'].strip()
        has_image = 'image' in data and self._is_valid_image(data['image'])
        
        # Must have at least one of text or image
        return has_text or has_image
    
    def _is_valid_image(self, image) -> bool:
        """
        Check if image data is valid.
        
        Args:
            image: Image data (file path, PIL Image, or bytes)
            
        Returns:
            True if image is valid
        """
        try:
            if isinstance(image, str):
                # File path
                return len(image) > 0
            elif isinstance(image, PILImage.Image):
                # PIL Image
                return True
            elif isinstance(image, bytes):
                # Raw bytes
                return len(image) > 0
            else:
                return False
        except Exception:
            return False
    
    def _prepare_image_data(self, image):
        """
        Prepare image data for embedding model.
        
        Args:
            image: Image data (file path, PIL Image, or bytes)
            
        Returns:
            Image data in format expected by embedding model
            
        Raises:
            ValueError: If image format is unsupported
        """
        try:
            if isinstance(image, str):
                # Image file path - return as is for embedding model
                return image
            elif isinstance(image, PILImage.Image):
                # PIL Image - return as is for embedding model
                return image
            elif isinstance(image, bytes):
                # Raw bytes - return as is for embedding model
                return image
            else:
                raise ValueError(f"Unsupported image type: {type(image)}")
        except Exception as e:
            raise ValueError(f"Failed to prepare image data: {e}") from e
    
    def process(self, 
                data: Dict[str, Any], 
                metadata: Optional[Dict[str, Any]] = None) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Process multimodal data to generate unified embeddings.
        
        Args:
            data: Dictionary containing 'text' and/or 'image' keys
            metadata: Optional metadata dictionary
            
        Returns:
            Tuple of (embeddings, enriched_metadata)
            
        Raises:
            ValueError: If no valid text or image is provided
            RuntimeError: If embedding generation fails
        """
        # Validate data format
        if not self.validate_data(data):
            raise ValueError("Invalid full embedding data: must have at least valid text or image")
        
        text = data.get('text')
        image = data.get('image')
        
        logger.debug(f"Processing full embedding pattern: has_text={text is not None}, has_image={image is not None}")
        
        try:
            # Prepare inputs for embedding model
            embedding_text = text if text and text.strip() else None
            embedding_image = None
            
            if image is not None:
                try:
                    embedding_image = self._prepare_image_data(image)
                except Exception as e:
                    logger.warning(f"Failed to prepare image data, using text only: {e}")
                    embedding_image = None
            
            # Generate multimodal embeddings
            embeddings = self.embedding_model.generate_embeddings(
                text=embedding_text,
                image=embedding_image
            )
            
            if not embeddings:
                raise RuntimeError("Embedding model returned empty embeddings")
            
            # Convert to numpy array
            embedding_array = np.array(embeddings, dtype=np.float32)
            
            # Prepare enriched metadata
            additional_metadata = {
                'embedding_dimension': len(embeddings),
                'has_text': embedding_text is not None,
                'has_image': embedding_image is not None,
                'multimodal': embedding_text is not None and embedding_image is not None
            }
            
            # Add text-specific metadata
            if embedding_text:
                additional_metadata.update({
                    'text_length': len(embedding_text),
                    'text_word_count': len(embedding_text.split()),
                    'text_preview': embedding_text[:100] + '...' if len(embedding_text) > 100 else embedding_text
                })
            
            # Add image-specific metadata
            if embedding_image:
                additional_metadata['image_processed'] = True
                
                # Add image metadata if available
                if isinstance(image, PILImage.Image):
                    additional_metadata.update({
                        'image_size': image.size,
                        'image_mode': image.mode,
                        'image_format': image.format
                    })
                elif isinstance(image, bytes):
                    additional_metadata['image_bytes'] = len(image)
                elif isinstance(image, str):
                    additional_metadata['image_path'] = image
            
            enriched_metadata = self._enrich_metadata(metadata, additional_metadata)
            
            logger.debug(f"Generated full embeddings: dimension={len(embeddings)}, multimodal={additional_metadata['multimodal']}")
            
            return embedding_array, enriched_metadata
            
        except Exception as e:
            logger.error(f"Failed to process full embedding pattern: {e}")
            raise RuntimeError(f"Full embedding pattern processing failed: {e}") from e