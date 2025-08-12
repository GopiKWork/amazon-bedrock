"""
Batch Processor
===============

High-throughput batch processing engine for MM Index.
"""

import time
import uuid
from typing import Dict, Any, List, Optional, Tuple
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from ..audit.audit_logger import AuditLogger
from ..patterns.pattern_engine import PatternEngine
from ..base_classes import BaseVectorStore

logger = logging.getLogger(__name__)


class BatchProcessor:
    """
    High-throughput batch processing engine.
    
    Processes large volumes of data efficiently using chunking,
    parallel processing, and optimized vector store operations.
    """
    
    def __init__(self, 
                 pattern_engine: PatternEngine,
                 vector_store: BaseVectorStore,
                 audit_logger: AuditLogger,
                 batch_size: int = 100,
                 max_workers: int = 4,
                 enable_parallel: bool = True):
        """
        Initialize BatchProcessor.
        
        Args:
            pattern_engine: Pattern engine for processing data
            vector_store: Vector store for ingestion
            audit_logger: Logger for audit trails
            batch_size: Size of processing chunks
            max_workers: Maximum number of parallel workers
            enable_parallel: Whether to enable parallel processing
        """
        self.pattern_engine = pattern_engine
        self.vector_store = vector_store
        self.audit_logger = audit_logger
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.enable_parallel = enable_parallel
        
        logger.info(f"BatchProcessor initialized: batch_size={batch_size}, max_workers={max_workers}, parallel={enable_parallel}")
    
    def process_batch(self,
                      data_list: List[Dict[str, Any]],
                      pattern: str,
                      index_name: str,
                      metadata_list: Optional[List[Dict[str, Any]]] = None) -> List[str]:
        """
        Process a batch of data items efficiently.
        
        Args:
            data_list: List of data items to process
            pattern: Pattern strategy to use
            index_name: Vector index name
            metadata_list: Optional metadata for each item
            
        Returns:
            List of document IDs
            
        Raises:
            ValueError: If input validation fails
            RuntimeError: If batch processing fails
        """
        if not data_list:
            raise ValueError("data_list cannot be empty")
        
        if metadata_list and len(metadata_list) != len(data_list):
            raise ValueError("metadata_list length must match data_list length")
        
        batch_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Log batch start
        correlation_id = self.audit_logger.log_batch_start(len(data_list), pattern)
        
        try:
            # Process in chunks for memory efficiency
            all_doc_ids = []
            successful_items = 0
            failed_items = 0
            
            for i in range(0, len(data_list), self.batch_size):
                chunk_data = data_list[i:i + self.batch_size]
                chunk_metadata = metadata_list[i:i + self.batch_size] if metadata_list else None
                
                chunk_doc_ids, chunk_success, chunk_failed = self._process_chunk(
                    chunk_data, pattern, index_name, chunk_metadata, batch_id, i
                )
                
                all_doc_ids.extend(chunk_doc_ids)
                successful_items += chunk_success
                failed_items += chunk_failed
                
                # Progress logging (removed - not essential)
            
            # Log batch completion
            duration = time.time() - start_time
            self.audit_logger.log_batch_completion(
                correlation_id=correlation_id,
                total_items=len(data_list),
                successful_items=successful_items,
                pattern=pattern,
                duration=duration
            )
            
            logger.info(f"Batch processing completed: {successful_items}/{len(data_list)} items successful in {duration:.2f}s")
            
            return all_doc_ids
            
        except Exception as e:
            duration = time.time() - start_time
            self.audit_logger.log_error(
                doc_id=batch_id,
                error=e,
                context={'operation': 'batch_processing', 'total_items': len(data_list), 'duration': duration}
            )
            raise RuntimeError(f"Batch processing failed: {e}") from e
    
    def _process_chunk(self,
                      chunk_data: List[Dict[str, Any]],
                      pattern: str,
                      index_name: str,
                      chunk_metadata: Optional[List[Dict[str, Any]]],
                      batch_id: str,
                      chunk_offset: int) -> Tuple[List[str], int, int]:
        """
        Process a single chunk of data.
        
        Args:
            chunk_data: Data items in this chunk
            pattern: Pattern strategy to use
            index_name: Vector index name
            chunk_metadata: Metadata for chunk items
            batch_id: Batch identifier
            chunk_offset: Offset of this chunk in the batch
            
        Returns:
            Tuple of (doc_ids, successful_count, failed_count)
        """
        if self.enable_parallel and len(chunk_data) > 1:
            return self._process_chunk_parallel(chunk_data, pattern, index_name, chunk_metadata, batch_id, chunk_offset)
        else:
            return self._process_chunk_sequential(chunk_data, pattern, index_name, chunk_metadata, batch_id, chunk_offset)
    
    def _process_chunk_sequential(self,
                                chunk_data: List[Dict[str, Any]],
                                pattern: str,
                                index_name: str,
                                chunk_metadata: Optional[List[Dict[str, Any]]],
                                batch_id: str,
                                chunk_offset: int) -> Tuple[List[str], int, int]:
        """
        Process chunk sequentially.
        
        Returns:
            Tuple of (doc_ids, successful_count, failed_count)
        """
        doc_ids = []
        vector_data_list = []
        successful_count = 0
        failed_count = 0
        
        # Process each item in the chunk
        for i, data in enumerate(chunk_data):
            try:
                doc_id = str(uuid.uuid4())
                doc_ids.append(doc_id)
                
                # Get metadata for this item
                item_metadata = chunk_metadata[i].copy() if chunk_metadata else {}
                item_metadata.update({
                    'doc_id': doc_id,
                    'batch_id': batch_id,
                    'batch_index': chunk_offset + i
                })
                
                # Log ingestion start
                data_size = sum(len(str(v)) for v in data.values())
                self.audit_logger.log_ingestion_start(doc_id, pattern, data_size)
                
                # Process using pattern engine
                start_time = time.time()
                embeddings, enriched_metadata = self.pattern_engine.process(
                    data=data,
                    pattern_name=pattern,
                    metadata=item_metadata
                )
                processing_duration = time.time() - start_time
                
                # Log pattern processing
                self.audit_logger.log_pattern_processing(
                    doc_id=doc_id, 
                    pattern=pattern, 
                    duration=processing_duration, 
                    embedding_dimension=len(embeddings)
                )
                
                # Prepare vector data
                vector_data = {
                    'id': doc_id,
                    'vector': embeddings.tolist() if hasattr(embeddings, 'tolist') else list(embeddings),
                    'metadata': enriched_metadata
                }
                vector_data_list.append(vector_data)
                successful_count += 1
                
            except Exception as e:
                failed_count += 1
                self.audit_logger.log_error(
                    doc_id=doc_ids[-1] if doc_ids else f"chunk_{chunk_offset}_{i}",
                    error=e,
                    context={'chunk_offset': chunk_offset, 'item_index': i, 'pattern': pattern, 'operation': 'chunk_processing'}
                )
                logger.warning(f"Failed to process item {chunk_offset + i}: {e}")
        
        # Batch ingest into vector store
        if vector_data_list:
            try:
                result = self.vector_store.ingest_vectors(index_name, vector_data_list)
                
                # Log vector ingestion results
                for i, doc_id in enumerate(doc_ids[:len(vector_data_list)]):
                    vector_data = vector_data_list[i]
                    success = i < result.get('successful_ingestions', 0)
                    self.audit_logger.log_vector_ingestion(
                        doc_id=doc_id,
                        vector_dimension=len(vector_data['vector']),
                        metadata_tags=len(vector_data['metadata']),
                        success=success
                    )
                
                if result.get('successful_ingestions', 0) < len(vector_data_list):
                    failed_ingestions = len(vector_data_list) - result.get('successful_ingestions', 0)
                    logger.warning(f"Vector store ingestion partially failed: {failed_ingestions} items")
                    
            except Exception as e:
                logger.error(f"Vector store ingestion failed for chunk: {e}")
                # Mark all items as failed
                failed_count = len(chunk_data)
                successful_count = 0
        
        return doc_ids, successful_count, failed_count
    
    def _process_chunk_parallel(self,
                              chunk_data: List[Dict[str, Any]],
                              pattern: str,
                              index_name: str,
                              chunk_metadata: Optional[List[Dict[str, Any]]],
                              batch_id: str,
                              chunk_offset: int) -> Tuple[List[str], int, int]:
        """
        Process chunk in parallel using ThreadPoolExecutor.
        
        Returns:
            Tuple of (doc_ids, successful_count, failed_count)
        """
        doc_ids = []
        vector_data_list = []
        successful_count = 0
        failed_count = 0
        
        # Create futures for parallel processing
        with ThreadPoolExecutor(max_workers=min(self.max_workers, len(chunk_data))) as executor:
            # Submit all items for processing
            futures = []
            for i, data in enumerate(chunk_data):
                doc_id = str(uuid.uuid4())
                doc_ids.append(doc_id)
                
                item_metadata = chunk_metadata[i].copy() if chunk_metadata else {}
                item_metadata.update({
                    'doc_id': doc_id,
                    'batch_id': batch_id,
                    'batch_index': chunk_offset + i
                })
                
                future = executor.submit(
                    self._process_single_item,
                    data, pattern, doc_id, item_metadata
                )
                futures.append((future, doc_id, chunk_offset + i))
            
            # Collect results
            for future, doc_id, item_index in futures:
                try:
                    vector_data = future.result()
                    if vector_data:
                        vector_data_list.append(vector_data)
                        successful_count += 1
                    else:
                        failed_count += 1
                except Exception as e:
                    failed_count += 1
                    self.audit_logger.log_error(
                        doc_id=doc_id,
                        error=e,
                        context={'item_index': item_index, 'pattern': pattern, 'operation': 'parallel_processing'}
                    )
        
        # Batch ingest into vector store
        if vector_data_list:
            try:
                result = self.vector_store.ingest_vectors(index_name, vector_data_list)
                
                # Update success/failure counts based on vector store results
                actual_successful = result.get('successful_ingestions', 0)
                if actual_successful < len(vector_data_list):
                    additional_failures = len(vector_data_list) - actual_successful
                    successful_count -= additional_failures
                    failed_count += additional_failures
                    
            except Exception as e:
                logger.error(f"Vector store ingestion failed for parallel chunk: {e}")
                failed_count = len(chunk_data)
                successful_count = 0
        
        return doc_ids, successful_count, failed_count
    
    def _process_single_item(self,
                           data: Dict[str, Any],
                           pattern: str,
                           doc_id: str,
                           metadata: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Process a single item (used in parallel processing).
        
        Args:
            data: Data to process
            pattern: Pattern strategy
            doc_id: Document ID
            metadata: Item metadata
            
        Returns:
            Vector data dictionary or None if processing failed
        """
        try:
            # Log ingestion start
            data_size = sum(len(str(v)) for v in data.values())
            self.audit_logger.log_ingestion_start(doc_id, pattern, data_size)
            
            # Process using pattern engine
            start_time = time.time()
            embeddings, enriched_metadata = self.pattern_engine.process(
                data=data,
                pattern_name=pattern,
                metadata=metadata
            )
            processing_duration = time.time() - start_time
            
            # Log pattern processing
            self.audit_logger.log_pattern_processing(
                doc_id=doc_id, 
                pattern=pattern, 
                duration=processing_duration, 
                embedding_dimension=len(embeddings)
            )
            
            # Return vector data
            return {
                'id': doc_id,
                'vector': embeddings.tolist() if hasattr(embeddings, 'tolist') else list(embeddings),
                'metadata': enriched_metadata
            }
            
        except Exception as e:
            logger.warning(f"Failed to process item {doc_id}: {e}")
            return None