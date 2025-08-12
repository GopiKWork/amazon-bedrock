"""
Base Abstract Classes for Indexing Patterns
==========================================

Defines the core interfaces for vector stores, embedding models, LLMs, and object stores.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union


"""
Base Abstract Classes for Indexing Patterns
==========================================

Defines all core interfaces for vector stores, embedding models, LLMs, and object stores.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class BaseVectorStore(ABC):
    """Abstract base class for core vector store operations."""
    
    @abstractmethod
    def create_index(self, index_name: str, dimension: int, distance_metric: str = "cosine") -> bool:
        """
        Create a vector index.
        
        Args:
            index_name: Name of the index to create
            dimension: Vector dimension
            distance_metric: Distance metric for similarity search
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def ingest_vectors(self, index_name: str, vectors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Ingest vectors into the index.
        
        Args:
            index_name: Name of the target index
            vectors: List of vector data with id, vector, and metadata
            
        Returns:
            Ingestion result with success/failure information
        """
        pass
    
    @abstractmethod
    def search_vectors(self, index_name: str, query_vector: List[float], 
                      metadata_filters: Optional[Dict[str, Any]] = None, 
                      top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Search for similar vectors.
        
        Args:
            index_name: Name of the index to search
            query_vector: Query vector for similarity search
            metadata_filters: Optional metadata filters
            top_k: Number of top results to return
            
        Returns:
            List of search results with similarity scores and metadata
        """
        pass
    
    @abstractmethod
    def delete_vectors(self, index_name: str, vector_ids: List[str]) -> bool:
        """
        Delete vectors from the index.
        
        Args:
            index_name: Name of the index
            vector_ids: List of vector IDs to delete
            
        Returns:
            True if successful, False otherwise
        """
        pass

class BaseEmbeddingModel(ABC):
    """Abstract base class for embedding model implementations."""
    
    @abstractmethod
    def generate_embeddings(self, text: Optional[str] = None, image = None) -> List[float]:
        """
        Generate vector embeddings from text and/or image content.
        
        Args:
            text: Text content to embed
            image: Image content to embed
            
        Returns:
            Vector embedding as list of floats
        """
        pass


class BaseMultimodalLLM(ABC):
    """Abstract base class for multimodal LLM implementations."""
    
    @abstractmethod
    def generate_text_description(self, image) -> str:
        """
        Generate detailed text description from image.
        
        Args:
            image: Image content to describe
            
        Returns:
            Detailed text description of the image
        """
        pass


class BaseLLM(ABC):
    """Abstract base class for LLM implementations."""
    
    @abstractmethod
    def generate_summary(self, text: str) -> str:
        """
        Generate concise summary from raw text.
        
        Args:
            text: Raw text content to summarize
            
        Returns:
            Concise summary of the input text
        """
        pass


class BaseObjectStore(ABC):
    """Abstract base class for object storage implementations."""
    
    @abstractmethod
    def store_object(self, key: str, content: bytes, content_type: str = 'binary/octet-stream') -> str:
        """
        Store an object and return its URI.
        
        Args:
            key: Object key/path
            content: Object content as bytes
            content_type: MIME type of the content
            
        Returns:
            URI of the stored object
        """
        pass
    
    @abstractmethod
    def retrieve_object(self, uri: str) -> bytes:
        """
        Retrieve an object by its URI.
        
        Args:
            uri: Object URI
            
        Returns:
            Object content as bytes
        """
        pass
    
    @abstractmethod
    def delete_object(self, uri: str) -> bool:
        """
        Delete an object by its URI.
        
        Args:
            uri: Object URI
            
        Returns:
            True if successful, False otherwise
        """
        pass