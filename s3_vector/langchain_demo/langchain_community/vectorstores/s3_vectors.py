#!/usr/bin/env python3
"""
S3 Vector Store for LangChain
============================

This module provides a LangChain-compatible vector store implementation
using AWS S3 as the backend storage. It integrates with the existing
s3_vector_ops module to provide familiar LangChain interfaces.

This is a sample implementation demonstrating integration patterns.
Official AWS support for S3 vector stores in LangChain may be available in the future.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple, Union
import warnings

# LangChain imports
try:
    from langchain_core.vectorstores import VectorStore
    from langchain_core.documents import Document
    from langchain_core.embeddings import Embeddings
    from langchain_core.retrievers import BaseRetriever
except ImportError:
    # Fallback for different LangChain versions
    try:
        from langchain.vectorstores.base import VectorStore
        from langchain.schema import Document
        from langchain.embeddings.base import Embeddings
        from langchain.schema.retriever import BaseRetriever
    except ImportError:
        raise ImportError(
            "LangChain is required for this module. "
            "Install with: pip install langchain langchain-core"
        )

# Add parent directories to path for imports
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

# AWS and project imports
import boto3
from sentence_transformers import SentenceTransformer

# Project imports
import s3_vector_ops
from config import (
    REGION_NAME,
    EMBEDDING_MODEL_NAME,
    get_bucket_name
)

# Suppress warnings
warnings.filterwarnings("ignore", message=".*encoder_attention_mask.*", category=FutureWarning)

# Configure logging
logger = logging.getLogger(__name__)


class S3VectorStore(VectorStore):
    """
    LangChain VectorStore implementation using AWS S3 as the backend.
    
    This class provides a LangChain-compatible interface for storing and
    retrieving documents using AWS S3 vector search capabilities.
    """
    
    def __init__(
        self,
        bucket_name: str,
        index_name: str,
        embedding: Optional[Embeddings] = None,
        region_name: str = REGION_NAME,
        **kwargs: Any
    ):
        """
        Initialize the S3 Vector Store.
        
        Args:
            bucket_name: Name of the S3 bucket for vector storage
            index_name: Name of the vector index
            embedding: LangChain Embeddings instance (optional, will use default if not provided)
            region_name: AWS region name
            **kwargs: Additional configuration parameters
        """
        self.bucket_name = bucket_name
        self.index_name = index_name
        self.region_name = region_name
        
        # Initialize embedding model
        if embedding is not None:
            self.embedding = embedding
            self._embedding_model = None  # Will use LangChain embedding
        else:
            # Use default sentence transformer
            self._embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
            self.embedding = None
        
        # Initialize S3 vector client
        self.s3_vectors_client = s3_vector_ops.create_s3_vectors_client(region_name)
        
        # Verify bucket exists
        try:
            self.s3_vectors_client.get_vector_bucket(vectorBucketName=bucket_name)
            logger.info(f"Connected to S3 vector bucket: {bucket_name}")
        except Exception as e:
            logger.warning(f"Could not verify bucket {bucket_name}: {e}")
        
        # Ensure index exists
        self._ensure_index_exists()
    
    def _ensure_index_exists(self):
        """Ensure the vector index exists, create it if it doesn't."""
        try:
            # Try to check if index exists by attempting a query
            # This is a simple way to verify index existence
            logger.info(f"Verifying index exists: {self.index_name}")
            
            # Create index if it doesn't exist
            s3_vector_ops.create_vector_index(
                s3_vectors_client=self.s3_vectors_client,
                bucket_name=self.bucket_name,
                index_name=self.index_name
            )
            
            logger.info(f"Index verified/created: {self.index_name}")
            
        except Exception as e:
            logger.warning(f"Could not verify/create index {self.index_name}: {e}")
    
    def _embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
        """
        if self.embedding is not None:
            # Use LangChain embedding
            return self.embedding.embed_documents(texts)
        else:
            # Use sentence transformer
            embeddings = self._embedding_model.encode(texts)
            return [embedding.tolist() for embedding in embeddings]
    
    def _embed_query(self, text: str) -> List[float]:
        """
        Generate embedding for a single query text.
        
        Args:
            text: Query text to embed
            
        Returns:
            Embedding vector
        """
        if self.embedding is not None:
            # Use LangChain embedding
            return self.embedding.embed_query(text)
        else:
            # Use sentence transformer
            embedding = self._embedding_model.encode([text])[0]
            return embedding.tolist()
    
    def add_texts(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any
    ) -> List[str]:
        """
        Add texts to the vector store.
        
        Args:
            texts: List of text strings to add
            metadatas: Optional list of metadata dictionaries
            **kwargs: Additional parameters
            
        Returns:
            List of document IDs
        """
        try:
            logger.info(f"Adding {len(texts)} texts to S3 vector store")
            
            # Generate embeddings
            embeddings = self._embed_texts(texts)
            
            # Prepare metadata
            if metadatas is None:
                metadatas = [{}] * len(texts)
            elif len(metadatas) != len(texts):
                raise ValueError("Number of metadatas must match number of texts")
            
            # Prepare documents for S3 vector operations
            documents = []
            doc_ids = []
            
            for i, (text, embedding, metadata) in enumerate(zip(texts, embeddings, metadatas)):
                doc_id = f"doc_{i}_{hash(text) % 1000000}"
                doc_ids.append(doc_id)
                
                # Add text to metadata for retrieval
                full_metadata = metadata.copy()
                full_metadata['text'] = text
                full_metadata['doc_id'] = doc_id
                
                documents.append({
                    'id': doc_id,
                    'vector': embedding,
                    'metadata': full_metadata
                })
            
            # Add to S3 vector store
            s3_vector_ops.ingest_vectors(
                s3_vectors_client=self.s3_vectors_client,
                bucket_name=self.bucket_name,
                index_name=self.index_name,
                vector_data=documents
            )
            
            logger.info(f"Successfully added {len(texts)} texts to S3 vector store")
            return doc_ids
            
        except Exception as e:
            logger.error(f"Failed to add texts to S3 vector store: {e}")
            raise
    
    def similarity_search(
        self,
        query: str,
        k: int = 4,
        filter: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> List[Document]:
        """
        Perform similarity search and return documents.
        
        Args:
            query: Query string
            k: Number of results to return
            filter: Optional metadata filter
            **kwargs: Additional search parameters
            
        Returns:
            List of LangChain Document objects
        """
        try:
            logger.info(f"Performing similarity search for: {query}")
            
            # Generate query embedding
            query_embedding = self._embed_query(query)
            
            # Perform search
            search_results = s3_vector_ops.search_vectors(
                s3_vectors_client=self.s3_vectors_client,
                bucket_name=self.bucket_name,
                index_name=self.index_name,
                query_vector=query_embedding,
                metadata_filters=filter,
                max_results=k
            )
            
            # Convert to LangChain Documents
            documents = []
            for result in search_results:
                metadata = result.get('metadata', {})
                text = metadata.pop('text', '')  # Remove text from metadata
                
                # Create LangChain Document
                doc = Document(
                    page_content=text,
                    metadata=metadata
                )
                documents.append(doc)
            
            logger.info(f"Found {len(documents)} similar documents")
            return documents
            
        except Exception as e:
            logger.error(f"Similarity search failed: {e}")
            raise
    
    def similarity_search_with_score(
        self,
        query: str,
        k: int = 4,
        filter: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> List[Tuple[Document, float]]:
        """
        Perform similarity search and return documents with scores.
        
        Args:
            query: Query string
            k: Number of results to return
            filter: Optional metadata filter
            **kwargs: Additional search parameters
            
        Returns:
            List of tuples (Document, similarity_score)
        """
        try:
            logger.info(f"Performing similarity search with scores for: {query}")
            
            # Generate query embedding
            query_embedding = self._embed_query(query)
            
            # Perform search
            search_results = s3_vector_ops.search_vectors(
                s3_vectors_client=self.s3_vectors_client,
                bucket_name=self.bucket_name,
                index_name=self.index_name,
                query_vector=query_embedding,
                metadata_filters=filter,
                max_results=k
            )
            
            # Convert to LangChain Documents with scores
            documents_with_scores = []
            for result in search_results:
                metadata = result.get('metadata', {})
                text = metadata.pop('text', '')  # Remove text from metadata
                score = result.get('similarity_score', 0.0)
                
                # Create LangChain Document
                doc = Document(
                    page_content=text,
                    metadata=metadata
                )
                documents_with_scores.append((doc, score))
            
            logger.info(f"Found {len(documents_with_scores)} similar documents with scores")
            return documents_with_scores
            
        except Exception as e:
            logger.error(f"Similarity search with scores failed: {e}")
            raise
    
    @classmethod
    def from_texts(
        cls,
        texts: List[str],
        embedding: Optional[Embeddings] = None,
        metadatas: Optional[List[Dict[str, Any]]] = None,
        bucket_name: Optional[str] = None,
        index_name: str = "default-index",
        **kwargs: Any
    ) -> "S3VectorStore":
        """
        Create S3VectorStore from a list of texts.
        
        Args:
            texts: List of text strings
            embedding: LangChain Embeddings instance
            metadatas: Optional list of metadata dictionaries
            bucket_name: S3 bucket name (will auto-generate if not provided)
            index_name: Vector index name
            **kwargs: Additional parameters
            
        Returns:
            S3VectorStore instance
        """
        # Auto-generate bucket name if not provided
        if bucket_name is None:
            sts_client = boto3.client('sts', region_name=REGION_NAME)
            account_id = sts_client.get_caller_identity()['Account']
            bucket_name = get_bucket_name(account_id)
        
        # Create vector store instance
        vector_store = cls(
            bucket_name=bucket_name,
            index_name=index_name,
            embedding=embedding,
            **kwargs
        )
        
        # Add texts
        vector_store.add_texts(texts, metadatas)
        
        return vector_store
    
    @classmethod
    def from_documents(
        cls,
        documents: List[Document],
        embedding: Optional[Embeddings] = None,
        bucket_name: Optional[str] = None,
        index_name: str = "default-index",
        **kwargs: Any
    ) -> "S3VectorStore":
        """
        Create S3VectorStore from a list of LangChain Documents.
        
        Args:
            documents: List of LangChain Document objects
            embedding: LangChain Embeddings instance
            bucket_name: S3 bucket name (will auto-generate if not provided)
            index_name: Vector index name
            **kwargs: Additional parameters
            
        Returns:
            S3VectorStore instance
        """
        texts = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        
        return cls.from_texts(
            texts=texts,
            embedding=embedding,
            metadatas=metadatas,
            bucket_name=bucket_name,
            index_name=index_name,
            **kwargs
        )