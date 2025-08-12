"""
Text Pattern Strategy
====================

Pattern strategy for text-only embedding generation.
"""

from typing import Dict, Any, Optional, Tuple
import numpy as np
import logging

from .base import PatternStrategy
from ..base_classes import BaseEmbeddingModel

logger = logging.getLogger(__name__)


class TextPattern(PatternStrategy):
    """
    Text-only embedding pattern strategy.
    
    This pattern processes text content to generate embeddings without
    any multimodal components. It's the simplest and most efficient
    pattern for pure text data.
    """
    
    def __init__(self, embedding_model: BaseEmbeddingModel):
        """
        Initialize TextPattern with embedding model.
        
        Args:
            embedding_model: Model for generating text embeddings
        """
        self.embedding_model = embedding_model
        logger.debug(f"Initialized TextPattern with {type(embedding_model).__name__}")
    
    @property
    def pattern_name(self) -> str:
        """Return the pattern name."""
        return "text"
    
    def get_required_keys(self) -> list[str]:
        """Text pattern requires 'text' key."""
        return ['text']
    
    def get_optional_keys(self) -> list[str]:
        """Text pattern has no optional keys."""
        return []
    
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """
        Validate that data contains valid text.
        
        Args:
            data: Input data dictionary
            
        Returns:
            True if data is valid for text pattern
        """
        if 'text' not in data:
            return False
        
        text = data['text']
        if not isinstance(text, str):
            return False
        
        if not text.strip():
            return False
        
        return True
    
    def process(self, 
                data: Dict[str, Any], 
                metadata: Optional[Dict[str, Any]] = None) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Process text data to generate embeddings.
        
        Args:
            data: Dictionary containing 'text' key with string content
            metadata: Optional metadata dictionary
            
        Returns:
            Tuple of (embeddings, enriched_metadata)
            
        Raises:
            ValueError: If text is missing or invalid
            RuntimeError: If embedding generation fails
        """
        # Validate required keys
        self._validate_required_keys(data)
        
        # Validate data format
        if not self.validate_data(data):
            raise ValueError("Invalid text data: must be non-empty string")
        
        text = data['text']
        logger.debug(f"Processing text pattern: {len(text)} characters")
        
        try:
            # Generate embeddings using the embedding model
            embeddings = self.embedding_model.generate_embeddings(text=text)
            
            if not embeddings:
                raise RuntimeError("Embedding model returned empty embeddings")
            
            # Convert to numpy array
            embedding_array = np.array(embeddings, dtype=np.float32)
            
            # Enrich metadata with text-specific information
            additional_metadata = {
                'text_length': len(text),
                'text_word_count': len(text.split()),
                'embedding_dimension': len(embeddings),
                'text_preview': text[:100] + '...' if len(text) > 100 else text
            }
            
            enriched_metadata = self._enrich_metadata(metadata, additional_metadata)
            
            logger.debug(f"Generated text embeddings: dimension={len(embeddings)}")
            
            return embedding_array, enriched_metadata
            
        except Exception as e:
            logger.error(f"Failed to process text pattern: {e}")
            raise RuntimeError(f"Text pattern processing failed: {e}") from e