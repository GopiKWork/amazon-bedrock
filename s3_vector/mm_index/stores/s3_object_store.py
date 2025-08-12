"""
S3 Object Store Implementation
=============================

S3-based object storage implementation.
"""

import boto3
from botocore.exceptions import ClientError
from typing import Dict, Any

from ..base_classes import BaseObjectStore
from ..config import DEFAULT_REGION


class S3ObjectStore(BaseObjectStore):
    """S3 object storage implementation."""
    
    def __init__(self, s3_uri: str, region_name: str = None):
        """
        Initialize S3 object store.
        
        Args:
            s3_uri: S3 URI in format s3://bucket-name/prefix/
            region_name: AWS region name (defaults to config.DEFAULT_REGION)
        """
        self.region_name = region_name or DEFAULT_REGION
        
        # Parse S3 URI
        if not s3_uri.startswith('s3://'):
            raise ValueError(f"Invalid S3 URI format: {s3_uri}. Must start with 's3://'")
        
        uri_parts = s3_uri[5:].rstrip('/').split('/', 1)
        self.bucket_name = uri_parts[0]
        self.prefix = uri_parts[1] if len(uri_parts) > 1 else ""
        
        # Initialize S3 client
        self.s3_client = boto3.client('s3', region_name=self.region_name)
    
    def _generate_key(self, key: str) -> str:
        """Generate full S3 key with prefix."""
        if self.prefix:
            return f"{self.prefix}/{key}"
        return key
    
    def store_object(self, key: str, content: bytes, content_type: str = 'binary/octet-stream') -> str:
        """
        Store an object in S3 and return its URI.
        
        Args:
            key: Object key/path
            content: Object content as bytes
            content_type: MIME type of the content
            
        Returns:
            S3 URI of the stored object
        """
        full_key = self._generate_key(key)
        
        self.s3_client.put_object(
            Bucket=self.bucket_name,
            Key=full_key,
            Body=content,
            ContentType=content_type
        )
        
        return f"s3://{self.bucket_name}/{full_key}"
    
    def retrieve_object(self, uri: str) -> bytes:
        """
        Retrieve an object from S3 by its URI.
        
        Args:
            uri: S3 URI of the object
            
        Returns:
            Object content as bytes
        """
        # Parse S3 URI
        if not uri.startswith('s3://'):
            raise ValueError(f"Invalid S3 URI: {uri}")
        
        uri_parts = uri[5:].split('/', 1)
        bucket = uri_parts[0]
        key = uri_parts[1] if len(uri_parts) > 1 else ""
        
        try:
            response = self.s3_client.get_object(Bucket=bucket, Key=key)
            return response['Body'].read()
        except ClientError:
            return b""  # Return empty bytes if object not found
    
    def delete_object(self, uri: str) -> bool:
        """
        Delete an object from S3 by its URI.
        
        Args:
            uri: S3 URI of the object
            
        Returns:
            True if successful, False otherwise
        """
        # Parse S3 URI
        if not uri.startswith('s3://'):
            return False
        
        uri_parts = uri[5:].split('/', 1)
        bucket = uri_parts[0]
        key = uri_parts[1] if len(uri_parts) > 1 else ""
        
        try:
            self.s3_client.delete_object(Bucket=bucket, Key=key)
            return True
        except ClientError:
            return False