"""
Pattern Engine
==============

Central engine for managing and executing pattern strategies.
"""

from typing import Dict, Any, Optional, Tuple, List
import numpy as np
import logging

from .base import PatternStrategy
from .text_pattern import TextPattern
from .hybrid_pattern import HybridPattern
from .full_embed_pattern import FullEmbedPattern
from .describe_pattern import DescribePattern
from .summarize_pattern import SummarizePattern
from ..base_classes import BaseEmbeddingModel, BaseObjectStore, BaseMultimodalLLM, BaseLLM

logger = logging.getLogger(__name__)


class PatternEngine:
    """
    Central engine for managing pattern strategies.
    
    The PatternEngine manages registration, discovery, and execution of
    pattern strategies. It provides a unified interface for processing
    data using different patterns while maintaining extensibility.
    """
    
    def __init__(self, 
                 embedding_model: BaseEmbeddingModel,
                 object_store: BaseObjectStore,
                 multimodal_llm: Optional[BaseMultimodalLLM] = None,
                 llm: Optional[BaseLLM] = None):
        """
        Initialize PatternEngine with required components.
        
        Args:
            embedding_model: Model for generating embeddings
            object_store: Storage for objects (images, etc.)
            multimodal_llm: Optional multimodal LLM for advanced patterns
            llm: Optional text LLM for advanced patterns
        """
        self.embedding_model = embedding_model
        self.object_store = object_store
        self.multimodal_llm = multimodal_llm
        self.llm = llm
        
        # Registry of available patterns
        self.patterns: Dict[str, PatternStrategy] = {}
        
        # Register default patterns
        self._register_default_patterns()
        
        logger.info(f"PatternEngine initialized with {len(self.patterns)} patterns: {list(self.patterns.keys())}")
    
    def _register_default_patterns(self):
        """Register built-in pattern strategies."""
        try:
            # Text pattern - always available
            text_pattern = TextPattern(self.embedding_model)
            self.register_pattern(text_pattern)
            
            # Hybrid pattern - requires object store
            if self.object_store:
                hybrid_pattern = HybridPattern(self.embedding_model, self.object_store)
                self.register_pattern(hybrid_pattern)
            
            # Full embedding pattern - uses embedding model for multimodal
            full_embed_pattern = FullEmbedPattern(self.embedding_model)
            self.register_pattern(full_embed_pattern)
            
            # Describe pattern - requires multimodal LLM and object store
            if self.multimodal_llm and self.object_store:
                describe_pattern = DescribePattern(self.embedding_model, self.multimodal_llm, self.object_store)
                self.register_pattern(describe_pattern)
            
            # Summarize pattern - requires text LLM and object store
            if self.llm and self.object_store:
                summarize_pattern = SummarizePattern(self.embedding_model, self.llm, self.object_store)
                self.register_pattern(summarize_pattern)
            
            logger.debug("Registered default patterns successfully")
            
        except Exception as e:
            logger.error(f"Failed to register default patterns: {e}")
            raise RuntimeError(f"Pattern registration failed: {e}") from e
    
    def register_pattern(self, pattern: PatternStrategy):
        """
        Register a new pattern strategy.
        
        Args:
            pattern: Pattern strategy to register
            
        Raises:
            ValueError: If pattern name conflicts with existing pattern
            TypeError: If pattern is not a PatternStrategy instance
        """
        if not isinstance(pattern, PatternStrategy):
            raise TypeError(f"Pattern must be instance of PatternStrategy, got {type(pattern)}")
        
        pattern_name = pattern.pattern_name
        
        if pattern_name in self.patterns:
            logger.warning(f"Overriding existing pattern: {pattern_name}")
        
        self.patterns[pattern_name] = pattern
        logger.debug(f"Registered pattern: {pattern_name}")
    
    def unregister_pattern(self, pattern_name: str):
        """
        Unregister a pattern strategy.
        
        Args:
            pattern_name: Name of pattern to unregister
            
        Raises:
            KeyError: If pattern name doesn't exist
        """
        if pattern_name not in self.patterns:
            raise KeyError(f"Pattern not found: {pattern_name}")
        
        del self.patterns[pattern_name]
        logger.debug(f"Unregistered pattern: {pattern_name}")
    
    def get_pattern(self, pattern_name: str) -> PatternStrategy:
        """
        Get a registered pattern strategy.
        
        Args:
            pattern_name: Name of pattern to retrieve
            
        Returns:
            Pattern strategy instance
            
        Raises:
            KeyError: If pattern name doesn't exist
        """
        if pattern_name not in self.patterns:
            available_patterns = list(self.patterns.keys())
            raise KeyError(f"Pattern '{pattern_name}' not found. Available patterns: {available_patterns}")
        
        return self.patterns[pattern_name]
    
    def list_patterns(self) -> List[str]:
        """
        List all registered pattern names.
        
        Returns:
            List of pattern names
        """
        return list(self.patterns.keys())
    
    def get_pattern_info(self, pattern_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a pattern.
        
        Args:
            pattern_name: Name of pattern
            
        Returns:
            Dictionary with pattern information
            
        Raises:
            KeyError: If pattern name doesn't exist
        """
        pattern = self.get_pattern(pattern_name)
        
        return {
            'name': pattern.pattern_name,
            'class': pattern.__class__.__name__,
            'required_keys': pattern.get_required_keys(),
            'optional_keys': pattern.get_optional_keys(),
            'description': pattern.__class__.__doc__ or "No description available"
        }
    
    def validate_data_for_pattern(self, data: Dict[str, Any], pattern_name: str) -> bool:
        """
        Validate data for a specific pattern.
        
        Args:
            data: Input data to validate
            pattern_name: Name of pattern to validate against
            
        Returns:
            True if data is valid for the pattern
            
        Raises:
            KeyError: If pattern name doesn't exist
        """
        pattern = self.get_pattern(pattern_name)
        return pattern.validate_data(data)
    
    def process(self, 
                data: Dict[str, Any], 
                pattern_name: str, 
                metadata: Optional[Dict[str, Any]] = None) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Process data using specified pattern.
        
        Args:
            data: Input data dictionary
            pattern_name: Name of pattern to use
            metadata: Optional metadata dictionary
            
        Returns:
            Tuple of (embeddings, enriched_metadata)
            
        Raises:
            KeyError: If pattern name doesn't exist
            ValueError: If data is invalid for the pattern
            RuntimeError: If processing fails
        """
        logger.debug(f"Processing with pattern: {pattern_name}")
        
        # Get pattern strategy
        pattern = self.get_pattern(pattern_name)
        
        # Validate data
        if not pattern.validate_data(data):
            raise ValueError(f"Data validation failed for pattern '{pattern_name}'. "
                           f"Required keys: {pattern.get_required_keys()}, "
                           f"Optional keys: {pattern.get_optional_keys()}")
        
        try:
            # Process using pattern
            embeddings, enriched_metadata = pattern.process(data, metadata)
            
            # Add engine metadata
            enriched_metadata['engine_version'] = '1.0'
            enriched_metadata['available_patterns'] = self.list_patterns()
            
            logger.debug(f"Successfully processed with pattern: {pattern_name}")
            
            return embeddings, enriched_metadata
            
        except Exception as e:
            logger.error(f"Pattern processing failed for '{pattern_name}': {e}")
            raise RuntimeError(f"Pattern processing failed: {e}") from e
    
    def get_recommended_pattern(self, data: Dict[str, Any]) -> str:
        """
        Recommend the best pattern for given data.
        
        Args:
            data: Input data dictionary
            
        Returns:
            Recommended pattern name
        """
        has_text = 'text' in data and isinstance(data['text'], str) and data['text'].strip()
        has_image = 'image' in data
        
        if has_text and has_image:
            # Both text and image - prefer hybrid for storage or full_embedding for unified representation
            if 'hybrid' in self.patterns:
                return 'hybrid'
            elif 'full_embedding' in self.patterns:
                return 'full_embedding'
        elif has_text:
            # Text only
            return 'text'
        elif has_image:
            # Image only - use full_embedding
            if 'full_embedding' in self.patterns:
                return 'full_embedding'
        
        # Default to text pattern
        return 'text'
    
    def __str__(self) -> str:
        """String representation of the engine."""
        return f"PatternEngine(patterns={list(self.patterns.keys())})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the engine."""
        return (f"PatternEngine("
                f"patterns={list(self.patterns.keys())}, "
                f"embedding_model={type(self.embedding_model).__name__}, "
                f"object_store={type(self.object_store).__name__ if self.object_store else None})")