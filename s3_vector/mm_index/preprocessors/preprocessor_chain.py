"""
Preprocessor Chain
=================

Chain of preprocessors applied in sequence.
"""

from typing import Dict, Any, List
import logging

from .base import Preprocessor

logger = logging.getLogger(__name__)


class PreprocessorChain:
    """
    Chain of preprocessors applied in sequence.
    
    The PreprocessorChain manages a sequence of preprocessors that are
    applied to data in order. Each preprocessor can transform the data
    before passing it to the next preprocessor in the chain.
    """
    
    def __init__(self):
        """Initialize empty preprocessor chain."""
        self.preprocessors: List[Preprocessor] = []
        logger.debug("Initialized empty PreprocessorChain")
    
    def add_preprocessor(self, preprocessor: Preprocessor):
        """
        Add a preprocessor to the end of the chain.
        
        Args:
            preprocessor: Preprocessor to add to the chain
            
        Raises:
            TypeError: If preprocessor is not a Preprocessor instance
        """
        if not isinstance(preprocessor, Preprocessor):
            raise TypeError(f"Expected Preprocessor instance, got {type(preprocessor)}")
        
        self.preprocessors.append(preprocessor)
        logger.debug(f"Added preprocessor to chain: {preprocessor.processor_name}")
    
    def remove_preprocessor(self, processor_name: str):
        """
        Remove a preprocessor from the chain by name.
        
        Args:
            processor_name: Name of preprocessor to remove
            
        Raises:
            ValueError: If preprocessor with given name is not found
        """
        for i, preprocessor in enumerate(self.preprocessors):
            if preprocessor.processor_name == processor_name:
                removed = self.preprocessors.pop(i)
                logger.debug(f"Removed preprocessor from chain: {processor_name}")
                return
        
        raise ValueError(f"Preprocessor '{processor_name}' not found in chain")
    
    def clear(self):
        """Remove all preprocessors from the chain."""
        count = len(self.preprocessors)
        self.preprocessors.clear()
        logger.debug(f"Cleared preprocessor chain ({count} preprocessors removed)")
    
    def get_preprocessor_names(self) -> List[str]:
        """
        Get list of preprocessor names in the chain.
        
        Returns:
            List of preprocessor names in order
        """
        return [p.processor_name for p in self.preprocessors]
    
    def list_preprocessors(self) -> List[str]:
        """
        Alias for get_preprocessor_names for convenience.
        
        Returns:
            List of preprocessor names in order
        """
        return self.get_preprocessor_names()
    
    def has_preprocessor(self, processor_name: str) -> bool:
        """
        Check if chain contains a preprocessor with given name.
        
        Args:
            processor_name: Name of preprocessor to check
            
        Returns:
            True if preprocessor is in the chain
        """
        return processor_name in self.get_preprocessor_names()
    
    def get_preprocessor(self, processor_name: str) -> Preprocessor:
        """
        Get a preprocessor from the chain by name.
        
        Args:
            processor_name: Name of preprocessor to get
            
        Returns:
            Preprocessor instance
            
        Raises:
            ValueError: If preprocessor with given name is not found
        """
        for preprocessor in self.preprocessors:
            if preprocessor.processor_name == processor_name:
                return preprocessor
        
        raise ValueError(f"Preprocessor '{processor_name}' not found in chain")
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply all preprocessors in sequence.
        
        Args:
            data: Input data dictionary
            
        Returns:
            Data dictionary after all preprocessing
            
        Raises:
            RuntimeError: If any preprocessor fails
        """
        if not self.preprocessors:
            logger.debug("No preprocessors in chain, returning data unchanged")
            return data
        
        logger.debug(f"Processing data through chain of {len(self.preprocessors)} preprocessors")
        
        result = data.copy()
        
        for i, preprocessor in enumerate(self.preprocessors):
            try:
                # Check if preprocessor should process this data
                if not preprocessor.should_process(result):
                    logger.debug(f"Skipping preprocessor {preprocessor.processor_name} (no applicable data)")
                    continue
                
                # Apply preprocessor
                logger.debug(f"Applying preprocessor {i+1}/{len(self.preprocessors)}: {preprocessor.processor_name}")
                result = preprocessor.process(result)
                
            except Exception as e:
                logger.error(f"Preprocessor '{preprocessor.processor_name}' failed: {e}")
                raise RuntimeError(f"Preprocessing failed at step {i+1} ({preprocessor.processor_name}): {e}") from e
        
        # Add chain metadata
        if '_preprocessing_chain' not in result:
            result['_preprocessing_chain'] = []
        
        result['_preprocessing_chain'] = self.get_preprocessor_names()
        
        logger.debug(f"Preprocessing chain completed successfully")
        return result
    
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """
        Validate data against all preprocessors in the chain.
        
        Args:
            data: Input data dictionary
            
        Returns:
            True if data is valid for all applicable preprocessors
        """
        for preprocessor in self.preprocessors:
            if preprocessor.should_process(data) and not preprocessor.validate_data(data):
                logger.warning(f"Data validation failed for preprocessor: {preprocessor.processor_name}")
                return False
        
        return True
    
    def get_applicable_preprocessors(self, data: Dict[str, Any]) -> List[str]:
        """
        Get list of preprocessors that would be applied to the given data.
        
        Args:
            data: Input data dictionary
            
        Returns:
            List of preprocessor names that would process this data
        """
        applicable = []
        for preprocessor in self.preprocessors:
            if preprocessor.should_process(data):
                applicable.append(preprocessor.processor_name)
        
        return applicable
    
    def __len__(self) -> int:
        """Return number of preprocessors in the chain."""
        return len(self.preprocessors)
    
    def __str__(self) -> str:
        """String representation of the chain."""
        return f"PreprocessorChain({len(self.preprocessors)} preprocessors)"
    
    def __repr__(self) -> str:
        """Detailed string representation of the chain."""
        names = self.get_preprocessor_names()
        return f"PreprocessorChain(preprocessors={names})"