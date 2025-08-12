"""
LangChain Community Vector Stores
================================

Vector store implementations for various backends.
"""

from .s3_vectors import S3VectorStore

__all__ = ["S3VectorStore"]