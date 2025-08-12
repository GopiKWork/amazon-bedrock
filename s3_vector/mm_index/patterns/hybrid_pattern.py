"""
Hybrid Pattern Strategy
======================

Pattern strategy for hybrid text + image processing with object storage.
"""

import uuid
from typing import Dict, Any, Optional, Tuple
import numpy as np
import logging
from PIL import Image as PILImage
import io

from .base import PatternStrategy
from ..base_classes import BaseEmbeddingModel, BaseObjectStore

logger = logging.getLogger(__name__)


class HybridPattern(PatternStrategy):
    """
    Hybrid text + image pattern strategy.
    
    This pattern processes text content for embeddings while storing
    images in object storage and maintaining references in metadata.
    The embeddings are generated from text only, but images are preserved
    for retrieval and display.
    """
    
    def __init__(self, embedding_model: BaseEmbeddingModel, object_store: BaseObjectStore):
        """
        Initialize HybridPattern with embedding model and object store.
        
        Args:
            embedding_model: Model for generating text embeddings
            object_store: Storage for image objects
        """
        self.embedding_model = embedding_model
        self.object_store = object_store
        logger.debug(f"Initialized HybridPattern with {type(embedding_model).__name__} and {type(object_store).__name__}")
    
    @property
    def pattern_name(self) -> str:
        """Return the pattern name."""
        return "hybrid"
    
    def get_required_keys(self) -> list[str]:
        """Hybrid pattern requires 'text' key."""
        return ['text']
    
    def get_optional_keys(self) -> list[str]:
        """Hybrid pattern optionally accepts 'image' key."""
        return ['image']
    
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """
        Validate that data contains valid text and optionally valid image.
        
        Args:
            data: Input data dictionary
            
        Returns:
            True if data is valid for hybrid pattern
        """
        # Text is required
        if 'text' not in data:
            return False
        
        text = data['text']
        if not isinstance(text, str) or not text.strip():
            return False
        
        # Image is optional but must be valid if present
        if 'image' in data:
            image = data['image']
            if not self._is_valid_image(image):
                return False
        
        return True
    
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
    
    def _process_image(self, image, doc_id: str) -> str:
        """
        Process and store image using object store.
        
        Args:
            image: Image data (file path, PIL Image, or bytes)
            doc_id: Document ID for generating storage key
            
        Returns:
            Object URI for stored image
            
        Raises:
            RuntimeError: If image processing or storage fails
        """
        try:
            # Convert image to bytes
            if isinstance(image, str):
                # Image file path
                with open(image, 'rb') as f:
                    image_bytes = f.read()
                extension = image.split('.')[-1] if '.' in image else 'jpg'
            elif isinstance(image, PILImage.Image):
                # PIL Image object
                buffer = io.BytesIO()
                format_name = image.format or 'JPEG'
                image.save(buffer, format=format_name)
                image_bytes = buffer.getvalue()
                extension = format_name.lower()
            elif isinstance(image, bytes):
                # Raw bytes
                image_bytes = image
                extension = 'jpg'  # Default extension
            else:
                raise ValueError(f"Unsupported image type: {type(image)}")
            
            # Generate storage key
            key = f"images/{doc_id}.{extension}"
            
            # Store in object store
            object_uri = self.object_store.store_object(
                key=key,
                content=image_bytes,
                content_type=f'image/{extension}'
            )
            
            logger.debug(f"Stored image: {key} -> {object_uri}")
            return object_uri
            
        except Exception as e:
            logger.error(f"Failed to process image for doc_id {doc_id}: {e}")
            raise RuntimeError(f"Image processing failed: {e}") from e
    
    def process(self, 
                data: Dict[str, Any], 
                metadata: Optional[Dict[str, Any]] = None) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Process hybrid text + image data.
        
        Args:
            data: Dictionary containing 'text' key and optionally 'image' key
            metadata: Optional metadata dictionary
            
        Returns:
            Tuple of (embeddings, enriched_metadata)
            
        Raises:
            ValueError: If required data is missing or invalid
            RuntimeError: If processing fails
        """
        # Validate required keys
        self._validate_required_keys(data)
        
        # Validate data format
        if not self.validate_data(data):
            raise ValueError("Invalid hybrid data: text must be non-empty string, image must be valid if provided")
        
        text = data['text']
        image = data.get('image')
        
        logger.debug(f"Processing hybrid pattern: text={len(text)} chars, has_image={image is not None}")
        
        try:
            # Generate embeddings from text only
            embeddings = self.embedding_model.generate_embeddings(text=text)
            
            if not embeddings:
                raise RuntimeError("Embedding model returned empty embeddings")
            
            # Convert to numpy array
            embedding_array = np.array(embeddings, dtype=np.float32)
            
            # Prepare enriched metadata
            additional_metadata = {
                'text_length': len(text),
                'text_word_count': len(text.split()),
                'embedding_dimension': len(embeddings),
                'has_image': image is not None,
                'text_preview': text[:100] + '...' if len(text) > 100 else text
            }
            
            # Process image if provided
            if image is not None:
                # Generate document ID if not in metadata
                doc_id = (metadata or {}).get('doc_id', str(uuid.uuid4()))
                
                try:
                    # Store image and get reference
                    image_uri = self._process_image(image, doc_id)
                    additional_metadata['__img_ref'] = image_uri
                    additional_metadata['image_stored'] = True
                    
                    # Add image metadata
                    if isinstance(image, PILImage.Image):
                        additional_metadata['image_size'] = image.size
                        additional_metadata['image_mode'] = image.mode
                    elif isinstance(image, bytes):
                        additional_metadata['image_bytes'] = len(image)
                    
                except Exception as e:
                    logger.warning(f"Failed to store image, continuing without it: {e}")
                    additional_metadata['image_stored'] = False
                    additional_metadata['image_error'] = str(e)
            
            enriched_metadata = self._enrich_metadata(metadata, additional_metadata)
            
            logger.debug(f"Generated hybrid embeddings: dimension={len(embeddings)}, image_stored={additional_metadata.get('image_stored', False)}")
            
            return embedding_array, enriched_metadata
            
        except Exception as e:
            logger.error(f"Failed to process hybrid pattern: {e}")
            raise RuntimeError(f"Hybrid pattern processing failed: {e}") from e