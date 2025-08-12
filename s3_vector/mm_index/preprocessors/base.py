"""
Preprocessor Base Classes
========================

Abstract base classes for implementing data preprocessors.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class Preprocessor(ABC):
    """
    Abstract base class for data preprocessors.
    
    Preprocessors transform input data before it's processed by pattern strategies.
    They can be chained together to create complex preprocessing pipelines.
    """
    
    @abstractmethod
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process and transform data.
        
        Args:
            data: Input data dictionary to transform
            
        Returns:
            Transformed data dictionary
            
        Raises:
            ValueError: If input data is invalid
            RuntimeError: If preprocessing fails
        """
        pass
    
    @property
    @abstractmethod
    def processor_name(self) -> str:
        """
        Return the unique name of this preprocessor.
        
        Returns:
            String identifier for this preprocessor
        """
        pass
    
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """
        Validate input data for this preprocessor.
        
        Args:
            data: Input data dictionary to validate
            
        Returns:
            True if data is valid for this preprocessor
            
        Note:
            Default implementation returns True. Override in subclasses
            to add preprocessor-specific validation logic.
        """
        return True
    
    def get_supported_keys(self) -> list[str]:
        """
        Get list of data keys this preprocessor can handle.
        
        Returns:
            List of supported data keys
            
        Note:
            Default implementation returns empty list. Override in subclasses
            to specify which data keys this preprocessor supports.
        """
        return []
    
    def should_process(self, data: Dict[str, Any]) -> bool:
        """
        Determine if this preprocessor should process the given data.
        
        Args:
            data: Input data dictionary
            
        Returns:
            True if this preprocessor should process the data
            
        Note:
            Default implementation checks if any supported keys are present.
            Override for custom logic.
        """
        supported_keys = self.get_supported_keys()
        if not supported_keys:
            return True  # Process all data if no specific keys are supported
        
        return any(key in data for key in supported_keys)
    
    def _add_preprocessing_metadata(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add metadata about preprocessing operations.
        
        Args:
            data: Data dictionary to add metadata to
            
        Returns:
            Data dictionary with preprocessing metadata
        """
        result = data.copy()
        
        # Track preprocessing operations
        if '_preprocessed_by' not in result:
            result['_preprocessed_by'] = []
        
        if self.processor_name not in result['_preprocessed_by']:
            result['_preprocessed_by'].append(self.processor_name)
        
        return result
    
    def __str__(self) -> str:
        """String representation of the preprocessor."""
        return f"{self.__class__.__name__}(processor_name='{self.processor_name}')"
    
    def __repr__(self) -> str:
        """Detailed string representation of the preprocessor."""
        return (f"{self.__class__.__name__}("
                f"processor_name='{self.processor_name}', "
                f"supported_keys={self.get_supported_keys()})")