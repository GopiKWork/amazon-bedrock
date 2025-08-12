"""
MM Index Package
===============

Multi-Modal Index with pluggable components for vector storage, object storage, and AI models.
"""

from .mm_ingestor import MMIngestor
from .base_classes import BaseVectorStore, BaseEmbeddingModel, BaseMultimodalLLM, BaseLLM, BaseObjectStore
from .validation import VectorDimensionManager, MetadataLimiter
from .default_provider import DefaultProvider
from .patterns import PatternStrategy, PatternEngine, TextPattern, HybridPattern, FullEmbedPattern, DescribePattern, SummarizePattern
from .preprocessors import Preprocessor, PreprocessorChain, ImageResizer, OCRProcessor
from .batch import BatchProcessor, AuditLogger

__all__ = [
    'MMIngestor',
    'BaseVectorStore',
    'BaseEmbeddingModel', 
    'BaseMultimodalLLM',
    'BaseLLM',
    'BaseObjectStore',
    'VectorDimensionManager',
    'MetadataLimiter',
    'DefaultProvider',
    'PatternStrategy',
    'PatternEngine',
    'TextPattern',
    'HybridPattern',
    'FullEmbedPattern',
    'DescribePattern',
    'SummarizePattern',
    'Preprocessor',
    'PreprocessorChain',
    'ImageResizer',
    'OCRProcessor',
    'BatchProcessor',
    'AuditLogger'
]