#!/usr/bin/env python3
"""
Default Provider for MM Index Components
========================================

Provides default implementations for common MM Index components,
making it easy to get started with sensible defaults.
"""

import logging
from typing import Optional
import boto3
from botocore.exceptions import ClientError
from .base_classes import BaseVectorStore, BaseObjectStore, BaseEmbeddingModel, BaseMultimodalLLM, BaseLLM

logger = logging.getLogger(__name__)


class DefaultProvider:
    """Provides default implementations for common MM Index components."""
    
    @staticmethod
    def _ensure_s3_bucket_exists(bucket_name: str, region_name: str = 'us-west-2') -> bool:
        """
        Ensure a regular S3 bucket exists, create if it doesn't.
        
        Args:
            bucket_name: Name of the S3 bucket
            region_name: AWS region
            
        Returns:
            True if bucket exists or was created successfully
        """
        try:
            s3_client = boto3.client('s3', region_name=region_name)
            
            # Check if bucket exists
            try:
                s3_client.head_bucket(Bucket=bucket_name)
                logger.debug(f"S3 bucket {bucket_name} already exists")
                return True
            except ClientError as e:
                if e.response['Error']['Code'] == '404':
                    # Bucket doesn't exist, create it
                    try:
                        if region_name == 'us-east-1':
                            # us-east-1 doesn't need LocationConstraint
                            s3_client.create_bucket(Bucket=bucket_name)
                        else:
                            s3_client.create_bucket(
                                Bucket=bucket_name,
                                CreateBucketConfiguration={'LocationConstraint': region_name}
                            )
                        logger.info(f"Created S3 bucket: {bucket_name}")
                        return True
                    except ClientError as create_error:
                        logger.error(f"Failed to create S3 bucket {bucket_name}: {create_error}")
                        return False
                else:
                    logger.error(f"Error checking S3 bucket {bucket_name}: {e}")
                    return False
        except Exception as e:
            logger.error(f"Unexpected error with S3 bucket {bucket_name}: {e}")
            return False
    
    @staticmethod
    def get_default_vector_store(region_name: str = 'us-west-2', 
                               vector_dimension: int = 384,
                               distance_metric: str = 'cosine',
                               max_metadata_tags: int = 10,
                               s3_prefix: str = 'indexing-patterns') -> BaseVectorStore:
        """
        Get default S3VectorStore with standard configuration.
        
        Args:
            region_name: AWS region for S3 Vector service
            vector_dimension: Target vector dimension
            distance_metric: Distance metric for similarity search
            max_metadata_tags: Maximum metadata tags per vector
            s3_prefix: S3 prefix for organizing data
            
        Returns:
            Configured S3VectorStore instance
        """
        try:
            from .vector_stores import S3VectorStore
            return S3VectorStore(
                region_name=region_name,
                vector_dimension=vector_dimension,
                distance_metric=distance_metric,
                max_metadata_tags=max_metadata_tags,
                s3_prefix=s3_prefix
            )
        except ImportError as e:
            logger.error(f"Failed to import S3VectorStore: {e}")
            raise RuntimeError("S3VectorStore not available for default provider")
    
    @staticmethod
    def get_default_object_store(region_name: str = 'us-west-2',
                               s3_uri: Optional[str] = None) -> BaseObjectStore:
        """
        Get default S3ObjectStore with standard configuration.
        
        Args:
            region_name: AWS region for S3 service
            s3_uri: S3 URI for object storage (auto-generated if not provided)
            
        Returns:
            Configured S3ObjectStore instance
        """
        try:
            from .stores import S3ObjectStore
            
            # Auto-generate S3 URI if not provided
            if not s3_uri:
                try:
                    sts_client = boto3.client('sts', region_name=region_name)
                    account_id = sts_client.get_caller_identity()['Account']
                    # Use same naming convention as the demo
                    vector_bucket_name = f"automotive-vectors-showcase-{account_id}"
                    object_bucket_name = f"{vector_bucket_name}-object"
                    
                    # Ensure the object bucket exists
                    if DefaultProvider._ensure_s3_bucket_exists(object_bucket_name, region_name):
                        s3_uri = f"s3://{object_bucket_name}/objects/"
                    else:
                        logger.warning(f"Could not create object bucket {object_bucket_name}, using default")
                        s3_uri = "s3://your-bucket-name/objects/"
                except Exception as e:
                    logger.warning(f"Could not auto-generate S3 URI: {e}")
                    s3_uri = "s3://your-bucket-name/objects/"
            
            return S3ObjectStore(s3_uri=s3_uri, region_name=region_name)
        except ImportError as e:
            logger.error(f"Failed to import S3ObjectStore: {e}")
            raise RuntimeError("S3ObjectStore not available for default provider")
    
    @staticmethod
    def get_default_embedding_model(region_name: str = 'us-west-2',
                                  embedding_dimension: int = 384) -> BaseEmbeddingModel:
        """
        Get default TitanEmbeddingModel with standard configuration.
        
        Args:
            region_name: AWS region for Bedrock service
            embedding_dimension: Target embedding dimension
            
        Returns:
            Configured TitanEmbeddingModel instance
        """
        try:
            from .models import TitanEmbeddingModel
            return TitanEmbeddingModel(
                region_name=region_name,
                embedding_dimension=embedding_dimension
            )
        except ImportError as e:
            logger.error(f"Failed to import TitanEmbeddingModel: {e}")
            raise RuntimeError("TitanEmbeddingModel not available for default provider")
    
    @staticmethod
    def get_default_multimodal_llm(region_name: str = 'us-west-2') -> BaseMultimodalLLM:
        """
        Get default NovaProMultimodalLLM with standard configuration.
        
        Args:
            region_name: AWS region for Bedrock service
            
        Returns:
            Configured NovaProMultimodalLLM instance
        """
        try:
            from .models import NovaProMultimodalLLM
            return NovaProMultimodalLLM(region_name=region_name)
        except ImportError as e:
            logger.error(f"Failed to import NovaProMultimodalLLM: {e}")
            raise RuntimeError("NovaProMultimodalLLM not available for default provider")
    
    @staticmethod
    def get_default_llm(region_name: str = 'us-west-2') -> BaseLLM:
        """
        Get default NovaProLLM with standard configuration.
        
        Args:
            region_name: AWS region for Bedrock service
            
        Returns:
            Configured NovaProLLM instance
        """
        try:
            from .models import NovaProLLM
            return NovaProLLM(region_name=region_name)
        except ImportError as e:
            logger.error(f"Failed to import NovaProLLM: {e}")
            raise RuntimeError("NovaProLLM not available for default provider")
    
    @staticmethod
    def create_default_mm_ingestor(index_name: str,
                                 region_name: str = 'us-west-2',
                                 vector_dimension: int = 384,
                                 include_multimodal_llm: bool = False,
                                 include_llm: bool = False):
        """
        Create a complete MMIngestor with all default components.
        
        Args:
            index_name: Name of the vector index
            region_name: AWS region for all services
            vector_dimension: Target vector dimension
            include_multimodal_llm: Whether to include multimodal LLM
            include_llm: Whether to include text LLM
            
        Returns:
            Configured MMIngestor instance with default components
        """
        try:
            from .mm_ingestor import MMIngestor
            
            # Create default components
            vector_store = DefaultProvider.get_default_vector_store(
                region_name=region_name,
                vector_dimension=vector_dimension
            )
            object_store = DefaultProvider.get_default_object_store(region_name=region_name)
            embedding_model = DefaultProvider.get_default_embedding_model(
                region_name=region_name,
                embedding_dimension=vector_dimension
            )
            
            # Optional components
            multimodal_llm = None
            if include_multimodal_llm:
                multimodal_llm = DefaultProvider.get_default_multimodal_llm(region_name=region_name)
            
            llm = None
            if include_llm:
                llm = DefaultProvider.get_default_llm(region_name=region_name)
            
            return MMIngestor(
                index_name=index_name,
                vector_store=vector_store,
                object_store=object_store,
                embedding_model=embedding_model,
                multimodal_llm=multimodal_llm,
                llm=llm,
                region_name=region_name
            )
        except ImportError as e:
            logger.error(f"Failed to import MMIngestor: {e}")
            raise RuntimeError("MMIngestor not available for default provider")
    
