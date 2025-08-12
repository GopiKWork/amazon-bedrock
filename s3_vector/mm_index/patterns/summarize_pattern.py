"""
Summarize Pattern Strategy
=========================

Pattern strategy for text summarization using LLM.
"""

import uuid
from typing import Dict, Any, Optional, Tuple
import numpy as np
import logging

from .base import PatternStrategy
from ..base_classes import BaseEmbeddingModel, BaseLLM, BaseObjectStore

logger = logging.getLogger(__name__)


class SummarizePattern(PatternStrategy):
    """
    Text summarization pattern strategy.
    
    This pattern takes long text, generates a summary using an LLM,
    and then creates embeddings from that summary.
    """
    
    def __init__(self, embedding_model: BaseEmbeddingModel, llm: BaseLLM, object_store: BaseObjectStore, min_text_length: int = 1000):
        """
        Initialize SummarizePattern.
        
        Args:
            embedding_model: Model for generating text embeddings
            llm: LLM for text summarization
            object_store: Storage for original text objects
            min_text_length: Minimum text length to trigger summarization
        """
        self.embedding_model = embedding_model
        self.llm = llm
        self.object_store = object_store
        self.min_text_length = min_text_length
        logger.debug(f"Initialized SummarizePattern with {type(embedding_model).__name__}, {type(llm).__name__}, and {type(object_store).__name__}")
    
    @property
    def pattern_name(self) -> str:
        """Return the pattern name."""
        return "summarize"
    
    def get_required_keys(self) -> list[str]:
        """Summarize pattern requires 'text' key."""
        return ['text']
    
    def get_optional_keys(self) -> list[str]:
        """Summarize pattern has no optional keys."""
        return []
    
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """
        Validate that data contains valid long text.
        
        Args:
            data: Input data dictionary
            
        Returns:
            True if data is valid for summarize pattern
        """
        if 'text' not in data:
            return False
        
        text = data['text']
        if not isinstance(text, str):
            return False
        
        if not text.strip():
            return False
        
        # Text must be long enough for summarization
        if len(text) < self.min_text_length:
            return False
        
        # Check if LLM is available
        if not self.llm:
            logger.warning("Summarize pattern requires LLM but none provided")
            return False
        
        return True
    
    def _store_original_text(self, text: str, doc_id: str) -> str:
        """
        Store original text in object store.
        
        Args:
            text: Original text content
            doc_id: Document ID for generating storage key
            
        Returns:
            Object URI for stored text
            
        Raises:
            RuntimeError: If text storage fails
        """
        try:
            # Convert text to bytes
            text_bytes = text.encode('utf-8')
            
            # Generate storage key
            key = f"original_texts/{doc_id}.txt"
            
            # Store in object store
            object_uri = self.object_store.store_object(
                key=key,
                content=text_bytes,
                content_type='text/plain'
            )
            
            logger.debug(f"Stored original text for summarize pattern: {key} -> {object_uri}")
            return object_uri
            
        except Exception as e:
            logger.error(f"Failed to store original text for doc_id {doc_id}: {e}")
            raise RuntimeError(f"Text storage failed: {e}") from e
    
    def process(self, 
                data: Dict[str, Any], 
                metadata: Optional[Dict[str, Any]] = None) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Process text data to generate summary and embeddings.
        
        Args:
            data: Dictionary containing 'text' key with long text content
            metadata: Optional metadata dictionary
            
        Returns:
            Tuple of (embeddings, enriched_metadata)
            
        Raises:
            RuntimeError: If processing fails
        """
        if metadata is None:
            metadata = {}
        
        try:
            text = data['text']
            
            # Generate summary from text
            logger.debug(f"Generating summary for text: {len(text)} characters")
            summary = self.llm.generate_summary(text)
            
            if not summary or not summary.strip():
                raise RuntimeError("Generated summary is empty")
            
            logger.debug(f"Generated summary: {len(summary)} characters")
            
            # Generate embeddings from summary
            embeddings = self.embedding_model.generate_embeddings(text=summary)
            
            # Convert to numpy array
            embedding_array = np.array(embeddings, dtype=np.float32)
            
            # Generate document ID if not in metadata
            doc_id = (metadata or {}).get('doc_id', str(uuid.uuid4()))
            
            # Enrich metadata
            enriched_metadata = metadata.copy()
            enriched_metadata.update({
                'pattern': self.pattern_name,
                'summary': summary,
                'summary_length': len(summary),
                'original_text_length': len(text),
                'compression_ratio': round(len(summary) / len(text), 3),
                'processing_type': 'text_summarization'
            })
            
            # Store original text in object store
            try:
                text_uri = self._store_original_text(text, doc_id)
                enriched_metadata['__text_ref'] = text_uri
                enriched_metadata['original_text_stored'] = True
                    
            except Exception as e:
                logger.warning(f"Failed to store original text, continuing without it: {e}")
                enriched_metadata['original_text_stored'] = False
                enriched_metadata['text_storage_error'] = str(e)
            
            logger.info(f"Summarize pattern completed: {len(text)} chars → {len(summary)} chars (ratio: {enriched_metadata['compression_ratio']}), text_stored={enriched_metadata.get('original_text_stored', False)}")
            
            return embedding_array, enriched_metadata
            
        except Exception as e:
            logger.error(f"Summarize pattern processing failed: {e}")
            raise RuntimeError(f"Summarize pattern processing failed: {e}") from e