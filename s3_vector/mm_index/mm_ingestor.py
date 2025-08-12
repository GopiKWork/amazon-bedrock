"""
Multi-Modal Ingestor (mm_ingestor.py)
=====================================

High-level orchestration class that combines vector stores, object stores, 
and AI models to provide multi-modal indexing capabilities.
"""

import uuid
import logging
import time
from typing import List, Dict, Any, Optional

from .base_classes import BaseVectorStore
from .base_classes import BaseEmbeddingModel, BaseMultimodalLLM, BaseLLM, BaseObjectStore
from .validation import VectorDimensionManager, MetadataLimiter, create_dimension_manager, create_metadata_limiter
from .patterns import PatternEngine
from .preprocessors import PreprocessorChain, ImageResizer
from .batch import BatchProcessor, AuditLogger

logger = logging.getLogger(__name__)


class MMIngestor:
    """
    Multi-Modal Ingestor that orchestrates vector storage, object storage, and AI models.
    
    This class provides a high-level interface for multi-modal data ingestion using
    flexible pattern strategies, allowing different processing approaches for various
    data types and use cases.
    
    This class provides a high-level interface for multimodal data ingestion using
    flexible pattern strategies for different data types and use cases.
    """
    
    def __init__(self,
                 index_name: str,
                 vector_store: Optional[BaseVectorStore] = None,
                 object_store: Optional[BaseObjectStore] = None,
                 embedding_model: Optional[BaseEmbeddingModel] = None,
                 multimodal_llm: Optional[BaseMultimodalLLM] = None,
                 llm: Optional[BaseLLM] = None,
                 region_name: str = 'us-west-2',
                 vector_dimension: int = 384):
        """
        Initialize MMIngestor with pluggable components.
        
        Args:
            index_name: Name of the vector index
            vector_store: Vector store implementation (optional, defaults to S3VectorStore)
            object_store: Object store implementation (optional, defaults to S3ObjectStore)
            embedding_model: Embedding model for generating vectors (optional, defaults to TitanEmbeddingModel)
            multimodal_llm: Optional multimodal LLM for image description
            llm: Optional LLM for text summarization
            region_name: AWS region for default components
            vector_dimension: Target vector dimension for default components
        """
        # Use defaults if not provided
        from .default_provider import DefaultProvider
        
        self.vector_store = vector_store or DefaultProvider.get_default_vector_store(
            region_name=region_name, vector_dimension=vector_dimension
        )
        self.object_store = object_store or DefaultProvider.get_default_object_store(
            region_name=region_name
        )
        self.embedding_model = embedding_model or DefaultProvider.get_default_embedding_model(
            region_name=region_name, embedding_dimension=vector_dimension
        )
        
        # Initialize multimodal LLM and LLM by default for describe and summarize patterns
        try:
            self.multimodal_llm = multimodal_llm or DefaultProvider.get_default_multimodal_llm(
                region_name=region_name
            )
        except Exception as e:
            logger.warning(f"Failed to initialize multimodal LLM: {e}. Describe pattern will not be available.")
            self.multimodal_llm = None
        
        try:
            self.llm = llm or DefaultProvider.get_default_llm(
                region_name=region_name
            )
        except Exception as e:
            logger.warning(f"Failed to initialize LLM: {e}. Summarize pattern will not be available.")
            self.llm = None
        self.index_name = index_name
        self.region_name = region_name
        
        # Initialize validation components (keep generic ones)
        self.dimension_manager = create_dimension_manager(target_dimension=vector_dimension)
        # Priority tags that should be preserved for object retrieval
        priority_tags = ['__img_ref', '__text_ref', 'pattern', 'damage_id', 'vehicle_make', 'vehicle_model', 'damage_type']
        self.metadata_limiter = create_metadata_limiter(max_tags=10, max_value_bytes=2048, priority_tags=priority_tags)
        
        # Initialize pattern engine for flexible processing strategies
        self.pattern_engine = PatternEngine(
            embedding_model=self.embedding_model,
            object_store=self.object_store,
            multimodal_llm=self.multimodal_llm,
            llm=self.llm
        )
        
        # Initialize preprocessor chain
        self.preprocessor_chain = PreprocessorChain()
        
        # Add default preprocessors
        self._setup_default_preprocessors()
        
        # Initialize audit logger
        self.audit_logger = AuditLogger()
        
        # Initialize batch processor
        self.batch_processor = BatchProcessor(
            pattern_engine=self.pattern_engine,
            vector_store=self.vector_store,
            audit_logger=self.audit_logger
        )
        
        # Ensure index exists - let vector store handle its own configuration
        self.vector_store.create_index(index_name=index_name)
        
        logger.info(f"MMIngestor initialized: index={index_name}, vector_dim={vector_dimension}, region={region_name}")
    
    def _setup_default_preprocessors(self):
        """Setup default preprocessors for common use cases."""
        # Add image resizer for standardizing image dimensions
        image_resizer = ImageResizer(target_size=(256, 256), preserve_aspect_ratio=True)
        self.preprocessor_chain.add_preprocessor(image_resizer)
        
        logger.debug(f"Added default preprocessors: {self.preprocessor_chain.get_preprocessor_names()}")
    
    def add_preprocessor(self, preprocessor):
        """
        Add a custom preprocessor to the chain.
        
        Args:
            preprocessor: Preprocessor instance to add
        """
        self.preprocessor_chain.add_preprocessor(preprocessor)
        logger.info(f"Added custom preprocessor: {preprocessor.processor_name}")
    
    def remove_preprocessor(self, processor_name: str):
        """
        Remove a preprocessor from the chain.
        
        Args:
            processor_name: Name of preprocessor to remove
        """
        self.preprocessor_chain.remove_preprocessor(processor_name)
        logger.info(f"Removed preprocessor: {processor_name}")
    
    def get_preprocessors(self) -> List[str]:
        """
        Get list of active preprocessors.
        
        Returns:
            List of preprocessor names
        """
        return self.preprocessor_chain.get_preprocessor_names()
    
    def ingest(self, 
               content: Dict[str, Any],
               metadata: Optional[Dict[str, Any]] = None,
               pattern: str = "text") -> str:
        """
        Ingest data using specified pattern.
        
        Args:
            content: Dictionary containing content with keys like 'text', 'image', 'video', 'audio', etc.
                    Supports extensible media types for future enhancements.
            metadata: Additional metadata for the document
            pattern: Pattern to use - 'text', 'hybrid', 'full_embedding', 'describe', 'summarize'
            
        Returns:
            Document ID of the ingested document
            
        Raises:
            ValueError: If pattern is not supported or required parameters are missing
        """
        
        # Generate document ID
        doc_id = str(uuid.uuid4())
        
        # Validate content parameter
        if not isinstance(content, dict):
            raise ValueError("Content must be a dictionary with media type keys")
        
        # Use content directly
        data = content.copy()
        
        # Prepare metadata
        doc_metadata = metadata.copy() if metadata else {}
        doc_metadata['doc_id'] = doc_id
        
        # Start audit logging
        correlation_id = self.audit_logger.log_ingestion_start(
            doc_id=doc_id,
            pattern=pattern,
            data_size=len(str(data))
        )
        
        try:
            # Apply preprocessing
            start_time = time.time()
            processed_data = self.preprocessor_chain.process(data)
            preprocessing_duration = time.time() - start_time
            
            if self.preprocessor_chain.get_preprocessor_names():
                self.audit_logger.log_preprocessing(
                    doc_id=doc_id,
                    preprocessors=self.preprocessor_chain.get_preprocessor_names(),
                    duration=preprocessing_duration,
                    correlation_id=correlation_id
                )
            
            # Process using pattern engine
            start_time = time.time()
            embeddings, enriched_metadata = self.pattern_engine.process(
                data=processed_data,
                pattern_name=pattern,
                metadata=doc_metadata
            )
            pattern_duration = time.time() - start_time
            
            self.audit_logger.log_pattern_processing(
                doc_id=doc_id,
                pattern=pattern,
                duration=pattern_duration,
                embedding_dimension=len(embeddings),
                correlation_id=correlation_id
            )
            
            # Prepare vector data for ingestion
            vector_data = self._prepare_vector_data(doc_id, embeddings, enriched_metadata)
            
            # Ingest into vector store
            result = self.vector_store.ingest_vectors(self.index_name, [vector_data])
            
            if result['successful_ingestions'] == 0:
                raise RuntimeError(f"Failed to ingest document: {result['errors']}")
            
            # Log successful completion
            self.audit_logger.end_operation(
                correlation_id=correlation_id,
                operation_name='ingestion',
                success=True,
                doc_id=doc_id,
                pattern=pattern
            )
            
            logger.debug(f"Successfully ingested document {doc_id} using pattern '{pattern}'")
            return doc_id
            
        except Exception as e:
            # Log error
            self.audit_logger.log_error(
                doc_id=doc_id,
                error=e,
                context={'pattern': pattern, 'data_keys': list(data.keys())},
                correlation_id=correlation_id
            )
            
            self.audit_logger.end_operation(
                correlation_id=correlation_id,
                operation_name='ingestion',
                success=False,
                doc_id=doc_id,
                pattern=pattern,
                error=str(e)
            )
            
            logger.error(f"Failed to ingest document using pattern '{pattern}': {e}")
            raise
    
    def batch_ingest(self,
                     data_list: List[Dict[str, Any]],
                     pattern: str,
                     metadata_list: Optional[List[Dict[str, Any]]] = None) -> List[str]:
        """
        Batch ingestion for high throughput use cases.
        
        Args:
            data_list: List of data dictionaries, each containing media type keys like 'text', 'image', 'video', 'audio', etc.
            pattern: Pattern strategy to use for all items
            metadata_list: Optional list of metadata dictionaries (one per data item)
            
        Returns:
            List of document IDs in the same order as input data
            
        Raises:
            ValueError: If data_list is empty or pattern is invalid
            RuntimeError: If batch processing fails
        """
        # Apply preprocessing to all data items
        processed_data_list = []
        for data in data_list:
            processed_data = self.preprocessor_chain.process(data)
            processed_data_list.append(processed_data)
        
        # Delegate to BatchProcessor for efficient processing
        return self.batch_processor.process_batch(
            data_list=processed_data_list,
            pattern=pattern,
            index_name=self.index_name,
            metadata_list=metadata_list
        )
    
    def search(self,
               query: Optional[Dict[str, Any]] = None,
               metadata_filters: Optional[Dict[str, Any]] = None,
               top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Search for similar documents.
        
        Args:
            query: Dictionary containing query content with keys like 'text', 'image', etc.
                  Supports extensible media types for future enhancements.
            metadata_filters: Key-value pairs for filtering results
            top_k: Number of top results to return
            
        Returns:
            List of search results with similarity scores and metadata
        """
        # Prepare query parameters with extensible interface
        query_text = None
        query_image = None
        
        # Extensible interface
        if query is not None:
            if not isinstance(query, dict):
                raise ValueError("Query must be a dictionary with media type keys")
            query_text = query.get('text')
            query_image = query.get('image')
        
        # Generate query embeddings
        query_embeddings = self.embedding_model.generate_embeddings(text=query_text, image=query_image)
        
        # Validate query vector dimensions
        validated_query_embeddings = self.dimension_manager.validate_and_transform(query_embeddings)
        
        logger.debug(f"Search query: text={bool(query_text)}, image={bool(query_image)}, query_dim={len(validated_query_embeddings)}")
        
        # Perform vector search
        search_results = self.vector_store.search_vectors(
            index_name=self.index_name,
            query_vector=validated_query_embeddings,
            metadata_filters=metadata_filters,
            top_k=top_k
        )
        
        # Augment results with original content from object store
        augmented_results = []
        for result in search_results:
            augmented_result = result.copy()
            
            # Retrieve original image if reference exists
            if '__img_ref' in result.get('metadata', {}):
                img_uri = result['metadata']['__img_ref']
                try:
                    img_data = self.object_store.retrieve_object(img_uri)
                    if img_data:
                        augmented_result['original_image'] = img_data
                except Exception as e:
                    logger.warning(f"Failed to retrieve image {img_uri}: {e}")
            
            # Retrieve original text if reference exists
            if '__text_ref' in result.get('metadata', {}):
                text_uri = result['metadata']['__text_ref']
                try:
                    text_data = self.object_store.retrieve_object(text_uri)
                    if text_data:
                        augmented_result['original_text'] = text_data.decode('utf-8')
                except Exception as e:
                    logger.warning(f"Failed to retrieve text {text_uri}: {e}")
            
            augmented_results.append(augmented_result)
        
        return augmented_results
    
    def _process_image(self, image, doc_id: str, content_type: str = 'images') -> str:
        """Process and store image using object store, return object URI."""
        if isinstance(image, str):
            # Image file path
            with open(image, 'rb') as f:
                image_bytes = f.read()
            extension = image.split('.')[-1] if '.' in image else 'jpg'
        elif hasattr(image, 'read'):
            # File-like object
            image_bytes = image.read()
            extension = 'jpg'
        elif isinstance(image, bytes):
            # Raw bytes
            image_bytes = image
            extension = 'jpg'
        else:
            # PIL Image or other format
            import io
            from PIL import Image as PILImage
            if isinstance(image, PILImage.Image):
                buffer = io.BytesIO()
                image.save(buffer, format='JPEG')
                image_bytes = buffer.getvalue()
                extension = 'jpg'
            else:
                raise ValueError(f"Unsupported image type: {type(image)}")
        
        # Store in object store
        key = f"{content_type}/{doc_id}.{extension}"
        return self.object_store.store_object(key, image_bytes, f'image/{extension}')
    
    def _prepare_vector_data(self, doc_id: str, embeddings: List[float], 
                           metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare vector data for ingestion with validation."""
        # Validate and transform vector dimensions
        validated_embeddings = self.dimension_manager.validate_and_transform(embeddings)
        
        # Apply metadata limiting for S3 Vector Store compliance
        limited_metadata = self.metadata_limiter.limit_metadata(metadata)
        
        logger.debug(f"Prepared vector data: doc_id={doc_id}, vector_dim={len(validated_embeddings)}, metadata_tags={len(metadata)}")
        
        return {
            'id': doc_id,
            'vector': validated_embeddings,
            'metadata': limited_metadata
        }


