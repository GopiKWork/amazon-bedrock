"""
Multimodal Patterns Package
============================

Automotive damage assessment examples and utilities using the mm_index core package.

Usage:
    from mm_index import MMIndex
    from mm_index.vector_stores import S3VectorStore
    from mm_index.stores import S3ObjectStore
    from mm_index.models import TitanEmbeddingModel
    
    # Create components
    vector_store = S3VectorStore(region_name='us-west-2')
    object_store = S3ObjectStore('s3://my-bucket/objects/')
    embedding_model = TitanEmbeddingModel()
    
    # Create MMIndex
    index = MMIndex(vector_store, object_store, embedding_model, 'my-bucket/my-index')
    
    # Ingest and search
    doc_id = index.ingest(content={"text": "A red car", "image": "car.jpg"}, pattern="hybrid")
    results = index.search(query={"text": "red vehicle"}, top_k=5)

Example:
    Run the consolidated automotive demo:
    python multimodal_patterns/automotive_damage_demo.py
"""

# Configuration - import from mm_index core
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    from mm_index.config import SUPPORTED_INDEXING_STRATEGIES as SUPPORTED_INDEXING_PATTERNS
except ImportError:
    # Fallback if mm_index not available
    SUPPORTED_INDEXING_PATTERNS = ['text', 'hybrid', 'full_embedding', 'generate_text', 'summarize']

__all__ = [
    'SUPPORTED_INDEXING_PATTERNS'
]