"""
Storage Implementations
======================

Concrete implementations for object storage.
"""

from .s3_object_store import S3ObjectStore

__all__ = [
    'S3ObjectStore'
]