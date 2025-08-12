"""
Describe Pattern Strategy
========================

Pattern strategy for image description using multimodal LLM.
"""

import uuid
from typing import Dict, Any, Optional, Tuple
import numpy as np
import logging
from PIL import Image as PILImage
import io

from .base import PatternStrategy
from ..base_classes import BaseEmbeddingModel, BaseMultimodalLLM, BaseObjectStore

logger = logging.getLogger(__name__)


class DescribePattern(PatternStrategy):
    """
    Image description pattern strategy.
    
    This pattern takes an image, generates a text description using a 
    multimodal LLM, and then creates embeddings from that description.
    """
    
    def __init__(self, embedding_model: BaseEmbeddingModel, multimodal_llm: BaseMultimodalLLM, object_store: BaseObjectStore):
        """
        Initialize DescribePattern.
        
        Args:
            embedding_model: Model for generating text embeddings
            multimodal_llm: Multimodal LLM for image description
            object_store: Storage for image objects
        """
        self.embedding_model = embedding_model
        self.multimodal_llm = multimodal_llm
        self.object_store = object_store
        logger.debug(f"Initialized DescribePattern with {type(embedding_model).__name__}, {type(multimodal_llm).__name__}, and {type(object_store).__name__}")
    
    @property
    def pattern_name(self) -> str:
        """Return the pattern name."""
        return "describe"
    
    def get_required_keys(self) -> list[str]:
        """Describe pattern requires 'image' key."""
        return ['image']
    
    def get_optional_keys(self) -> list[str]:
        """Describe pattern accepts optional 'text' key."""
        return ['text']
    
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """
        Validate that data contains valid image.
        
        Args:
            data: Input data dictionary
            
        Returns:
            True if data is valid for describe pattern
        """
        if 'image' not in data:
            return False
        
        if not data['image']:
            return False
        
        # Check if multimodal LLM is available
        if not self.multimodal_llm:
            logger.warning("Describe pattern requires multimodal LLM but none provided")
            return False
        
        return True
    
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
            key = f"describe_images/{doc_id}.{extension}"
            
            # Store in object store
            object_uri = self.object_store.store_object(
                key=key,
                content=image_bytes,
                content_type=f'image/{extension}'
            )
            
            logger.debug(f"Stored image for describe pattern: {key} -> {object_uri}")
            return object_uri
            
        except Exception as e:
            logger.error(f"Failed to process image for doc_id {doc_id}: {e}")
            raise RuntimeError(f"Image processing failed: {e}") from e
    
    def process(self, 
                data: Dict[str, Any], 
                metadata: Optional[Dict[str, Any]] = None) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Process image data to generate description and embeddings.
        
        Args:
            data: Dictionary containing 'image' key and optional 'text' key
            metadata: Optional metadata dictionary
            
        Returns:
            Tuple of (embeddings, enriched_metadata)
            
        Raises:
            RuntimeError: If processing fails
        """
        if metadata is None:
            metadata = {}
        
        try:
            # Generate description from image
            logger.debug("Generating image description using multimodal LLM")
            description = self.multimodal_llm.generate_text_description(data['image'])
            
            if not description or not description.strip():
                raise RuntimeError("Generated description is empty")
            
            logger.debug(f"Generated description: {len(description)} characters")
            
            # Generate embeddings from description
            embeddings = self.embedding_model.generate_embeddings(text=description)
            
            # Convert to numpy array
            embedding_array = np.array(embeddings, dtype=np.float32)
            
            # Generate document ID if not in metadata
            doc_id = (metadata or {}).get('doc_id', str(uuid.uuid4()))
            
            # Enrich metadata
            enriched_metadata = metadata.copy()
            enriched_metadata.update({
                'pattern': self.pattern_name,
                'description': description,
                'description_length': len(description),
                'has_image': True,
                'processing_type': 'image_description'
            })
            
            # Store image in object store
            try:
                image_uri = self._process_image(data['image'], doc_id)
                enriched_metadata['__img_ref'] = image_uri
                enriched_metadata['image_stored'] = True
                
                # Add image metadata
                if isinstance(data['image'], PILImage.Image):
                    enriched_metadata['image_size'] = data['image'].size
                    enriched_metadata['image_mode'] = data['image'].mode
                elif isinstance(data['image'], bytes):
                    enriched_metadata['image_bytes'] = len(data['image'])
                    
            except Exception as e:
                logger.warning(f"Failed to store image, continuing without it: {e}")
                enriched_metadata['image_stored'] = False
                enriched_metadata['image_error'] = str(e)
            
            # Add original text if provided
            if 'text' in data and data['text']:
                enriched_metadata['original_text'] = data['text']
                enriched_metadata['original_text_length'] = len(data['text'])
            
            logger.info(f"Describe pattern completed: {len(description)} char description, {len(embeddings)} dim embeddings, image_stored={enriched_metadata.get('image_stored', False)}")
            
            return embedding_array, enriched_metadata
            
        except Exception as e:
            logger.error(f"Describe pattern processing failed: {e}")
            raise RuntimeError(f"Describe pattern processing failed: {e}") from e