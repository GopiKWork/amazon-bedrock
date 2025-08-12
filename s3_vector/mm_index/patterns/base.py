"""
Pattern Strategy Base Classes
=============================

Abstract base classes for implementing pattern-based embedding strategies.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Tuple
import numpy as np
import logging

logger = logging.getLogger(__name__)


class PatternStrategy(ABC):
    """
    Abstract base class for embedding pattern strategies.
    
    Pattern strategies define how different types of multimodal data
    should be processed to generate embeddings and enriched metadata.
    """
    
    @abstractmethod
    def process(self, 
                data: Dict[str, Any], 
                metadata: Optional[Dict[str, Any]] = None) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Generate embeddings and enriched metadata according to pattern.
        
        Args:
            data: The raw input data (text, image, etc.)
                Expected keys depend on pattern implementation:
                - 'text': Text content (str)
                - 'image': Image data (file path, PIL Image, or bytes)
                - Other pattern-specific keys
            metadata: Optional pre-existing metadata dictionary
            
        Returns:
            Tuple containing:
            - Embedding: numpy ndarray with generated embeddings
            - Metadata: Dictionary with enriched metadata including:
                - 'pattern': Name of the pattern used
                - 'processed_at': ISO timestamp of processing
                - Pattern-specific metadata
                - Object store references (if applicable)
                
        Raises:
            ValueError: If required data is missing or invalid
            RuntimeError: If embedding generation fails
        """
        pass
    
    @property
    @abstractmethod
    def pattern_name(self) -> str:
        """
        Return the unique name of this pattern.
        
        Returns:
            String identifier for this pattern (e.g., 'text', 'hybrid', 'full_embedding')
        """
        pass
    
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """
        Validate input data for this pattern.
        
        Args:
            data: Input data dictionary to validate
            
        Returns:
            True if data is valid for this pattern, False otherwise
            
        Note:
            Default implementation returns True. Override in subclasses
            to add pattern-specific validation logic.
        """
        return True
    
    def get_required_keys(self) -> list[str]:
        """
        Get list of required keys in data dictionary.
        
        Returns:
            List of required keys for this pattern
            
        Note:
            Default implementation returns empty list. Override in subclasses
            to specify required data keys.
        """
        return []
    
    def get_optional_keys(self) -> list[str]:
        """
        Get list of optional keys in data dictionary.
        
        Returns:
            List of optional keys for this pattern
            
        Note:
            Default implementation returns empty list. Override in subclasses
            to specify optional data keys.
        """
        return []
    
    def _enrich_metadata(self, 
                        base_metadata: Optional[Dict[str, Any]], 
                        additional_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Helper method to enrich metadata with pattern-specific information.
        
        Args:
            base_metadata: Original metadata dictionary (can be None)
            additional_metadata: Additional metadata to merge
            
        Returns:
            Enriched metadata dictionary
        """
        from datetime import datetime
        
        enriched = base_metadata.copy() if base_metadata else {}
        
        # Add pattern identification
        enriched['pattern'] = self.pattern_name
        enriched['processed_at'] = datetime.utcnow().isoformat()
        
        # Merge additional metadata
        enriched.update(additional_metadata)
        
        return enriched
    
    def _validate_required_keys(self, data: Dict[str, Any]) -> None:
        """
        Validate that all required keys are present in data.
        
        Args:
            data: Input data dictionary
            
        Raises:
            ValueError: If required keys are missing
        """
        required_keys = self.get_required_keys()
        missing_keys = [key for key in required_keys if key not in data]
        
        if missing_keys:
            raise ValueError(
                f"Pattern '{self.pattern_name}' requires keys {required_keys}, "
                f"but missing: {missing_keys}"
            )
    
    def __str__(self) -> str:
        """String representation of the pattern."""
        return f"{self.__class__.__name__}(pattern_name='{self.pattern_name}')"
    
    def __repr__(self) -> str:
        """Detailed string representation of the pattern."""
        return (f"{self.__class__.__name__}("
                f"pattern_name='{self.pattern_name}', "
                f"required_keys={self.get_required_keys()}, "
                f"optional_keys={self.get_optional_keys()})")