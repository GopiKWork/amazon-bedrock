"""
Vector Store Implementations
===========================

Concrete implementations of vector stores for different backends.
"""

from .s3_vector_store import S3VectorStore

__all__ = ['S3VectorStore']