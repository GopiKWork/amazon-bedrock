"""
Audit Logger
============

Comprehensive logging and audit system for tracking pipeline operations.
"""

import logging
import time
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


class AuditLogger:
    """
    Comprehensive logging and audit system.
    
    The AuditLogger tracks all pipeline operations, performance metrics,
    and errors with structured logging and correlation IDs for tracing.
    """
    
    def __init__(self, 
                 log_level: str = 'INFO',
                 enable_performance_tracking: bool = True,
                 enable_structured_logging: bool = True):
        """
        Initialize AuditLogger.
        
        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
            enable_performance_tracking: Whether to track timing metrics
            enable_structured_logging: Whether to use structured JSON logging
        """
        self.log_level = log_level
        self.enable_performance_tracking = enable_performance_tracking
        self.enable_structured_logging = enable_structured_logging
        
        # Initialize logger
        self.logger = logging.getLogger('mm_ingestor_audit')
        self.logger.setLevel(getattr(logging, log_level))
        
        # Create handler if not already present
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            
            if enable_structured_logging:
                formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
            else:
                formatter = logging.Formatter(
                    '%(asctime)s - %(levelname)s - %(message)s'
                )
            
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        
        # Performance tracking
        self.operation_times: Dict[str, List[float]] = {}
        self.active_operations: Dict[str, float] = {}
        
        # Session tracking (for compatibility with batch logger)
        self.session_id = str(uuid.uuid4())
        
        logger.info(f"AuditLogger initialized: level={log_level}, performance={enable_performance_tracking}, session_id={self.session_id}")
    
    def _generate_correlation_id(self) -> str:
        """Generate a unique correlation ID for tracing operations."""
        return str(uuid.uuid4())[:8]
    
    def _log_structured(self, level: str, message: str, **kwargs):
        """
        Log with structured data.
        
        Args:
            level: Log level
            message: Log message
            **kwargs: Additional structured data
        """
        if self.enable_structured_logging:
            log_data = {
                'timestamp': datetime.utcnow().isoformat(),
                'message': message,
                **kwargs
            }
            log_message = json.dumps(log_data)
        else:
            log_message = message
            if kwargs:
                log_message += f" | {kwargs}"
        
        getattr(self.logger, level.lower())(log_message)
    
    def start_operation(self, operation_name: str, **context) -> str:
        """
        Start tracking an operation.
        
        Args:
            operation_name: Name of the operation
            **context: Additional context data
            
        Returns:
            Correlation ID for this operation
        """
        correlation_id = self._generate_correlation_id()
        
        if self.enable_performance_tracking:
            self.active_operations[correlation_id] = time.time()
        
        self._log_structured(
            'info',
            f"Operation started: {operation_name}",
            operation=operation_name,
            correlation_id=correlation_id,
            **context
        )
        
        return correlation_id
    
    def end_operation(self, correlation_id: str, operation_name: str, success: bool = True, **context):
        """
        End tracking an operation.
        
        Args:
            correlation_id: Correlation ID from start_operation
            operation_name: Name of the operation
            success: Whether the operation succeeded
            **context: Additional context data
        """
        duration = None
        if self.enable_performance_tracking and correlation_id in self.active_operations:
            start_time = self.active_operations.pop(correlation_id)
            duration = time.time() - start_time
            
            # Track operation times for statistics
            if operation_name not in self.operation_times:
                self.operation_times[operation_name] = []
            self.operation_times[operation_name].append(duration)
        
        level = 'info' if success else 'error'
        status = 'completed' if success else 'failed'
        
        log_context = {
            'operation': operation_name,
            'correlation_id': correlation_id,
            'status': status,
            **context
        }
        
        if duration is not None:
            log_context['duration_seconds'] = round(duration, 3)
        
        self._log_structured(
            level,
            f"Operation {status}: {operation_name}",
            **log_context
        )
    
    def log_ingestion_start(self, doc_id: str, pattern: str, data_size: int, correlation_id: Optional[str] = None):
        """
        Log the start of an ingestion operation.
        
        Args:
            doc_id: Document ID being ingested
            pattern: Pattern strategy being used
            data_size: Size of data being processed
            correlation_id: Optional correlation ID
        """
        if not correlation_id:
            correlation_id = self._generate_correlation_id()
        
        self._log_structured(
            'info',
            f"Starting ingestion: {doc_id}",
            operation='ingestion',
            doc_id=doc_id,
            pattern=pattern,
            data_size=data_size,
            correlation_id=correlation_id
        )
        
        return correlation_id
    
    def log_pattern_processing(self, doc_id: str, pattern: str, duration: float, embedding_dimension: Optional[int] = None, correlation_id: Optional[str] = None):
        """
        Log pattern processing completion.
        
        Args:
            doc_id: Document ID processed
            pattern: Pattern strategy used
            duration: Processing duration in seconds
            embedding_dimension: Optional dimension of generated embeddings
            correlation_id: Optional correlation ID
        """
        log_data = {
            'operation': 'pattern_processing',
            'doc_id': doc_id,
            'pattern': pattern,
            'duration': round(duration, 3),
            'session_id': getattr(self, 'session_id', 'unknown'),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if embedding_dimension:
            log_data['embedding_dimension'] = embedding_dimension
            
        if correlation_id:
            log_data['correlation_id'] = correlation_id
        
        self._log_structured('info', f"Pattern processed: {doc_id}", **log_data)
    
    def log_preprocessing(self, doc_id: str, preprocessors: List[str], duration: float, correlation_id: Optional[str] = None):
        """
        Log preprocessing completion.
        
        Args:
            doc_id: Document ID processed
            preprocessors: List of preprocessors applied
            duration: Processing duration in seconds
            correlation_id: Optional correlation ID
        """
        self._log_structured(
            'info',
            f"Preprocessing completed: {doc_id}",
            operation='preprocessing',
            doc_id=doc_id,
            preprocessors=preprocessors,
            duration_seconds=round(duration, 3),
            correlation_id=correlation_id
        )
    
    def log_batch_start(self, batch_size: int, pattern: str) -> str:
        """
        Log the start of batch processing.
        
        Args:
            batch_size: Number of items in batch
            pattern: Pattern strategy being used
            
        Returns:
            Correlation ID for batch operation
        """
        correlation_id = self._generate_correlation_id()
        
        self._log_structured(
            'info',
            f"Starting batch processing: {batch_size} items",
            operation='batch_processing',
            batch_size=batch_size,
            pattern=pattern,
            correlation_id=correlation_id
        )
        
        if self.enable_performance_tracking:
            self.active_operations[correlation_id] = time.time()
        
        return correlation_id
    
    def log_batch_completion(self, 
                           correlation_id: str,
                           total_items: int, 
                           successful_items: int,
                           pattern: str, 
                           duration: Optional[float] = None):
        """
        Log batch processing completion.
        
        Args:
            correlation_id: Correlation ID from batch start
            total_items: Total number of items processed
            successful_items: Number of successfully processed items
            pattern: Pattern strategy used
            duration: Optional duration (calculated if not provided)
        """
        if duration is None and self.enable_performance_tracking and correlation_id in self.active_operations:
            start_time = self.active_operations.pop(correlation_id)
            duration = time.time() - start_time
        
        failed_items = total_items - successful_items
        success_rate = (successful_items / total_items) * 100 if total_items > 0 else 0
        throughput = total_items / duration if duration and duration > 0 else 0
        
        log_context = {
            'operation': 'batch_processing',
            'correlation_id': correlation_id,
            'total_items': total_items,
            'successful_items': successful_items,
            'failed_items': failed_items,
            'success_rate_percent': round(success_rate, 2),
            'pattern': pattern
        }
        
        if duration:
            log_context.update({
                'duration_seconds': round(duration, 3),
                'throughput_items_per_second': round(throughput, 2)
            })
        
        level = 'info' if failed_items == 0 else 'warning'
        self._log_structured(
            level,
            f"Batch processing completed: {successful_items}/{total_items} successful",
            **log_context
        )
    
    def log_error(self, doc_id: str, error: Exception, context: Dict[str, Any], correlation_id: Optional[str] = None):
        """
        Log errors with full context.
        
        Args:
            doc_id: Document ID that failed
            error: Exception that occurred
            context: Additional context information
            correlation_id: Optional correlation ID
        """
        import traceback
        
        error_context = {
            'operation': 'error',
            'doc_id': doc_id,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'traceback': traceback.format_exc(),
            **context
        }
        
        if correlation_id:
            error_context['correlation_id'] = correlation_id
        
        self._log_structured(
            'error',
            f"Error processing document: {doc_id}",
            **error_context
        )
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Get performance statistics for tracked operations.
        
        Returns:
            Dictionary with performance statistics
        """
        if not self.enable_performance_tracking:
            return {'performance_tracking': 'disabled'}
        
        stats = {}
        for operation, times in self.operation_times.items():
            if times:
                stats[operation] = {
                    'count': len(times),
                    'total_time': round(sum(times), 3),
                    'average_time': round(sum(times) / len(times), 3),
                    'min_time': round(min(times), 3),
                    'max_time': round(max(times), 3)
                }
        
        return stats
    
    def reset_performance_stats(self):
        """Reset all performance statistics."""
        self.operation_times.clear()
        self.active_operations.clear()
        logger.info("Performance statistics reset")
    
    def log_ingestion_complete(self, doc_id: str, total_duration: float, success: bool, **context):
        """
        Log completion of ingestion operation (compatibility method).
        
        Args:
            doc_id: Document ID
            total_duration: Total processing duration
            success: Whether operation was successful
            **context: Additional context data
        """
        log_data = {
            'operation': 'ingestion_complete',
            'doc_id': doc_id,
            'duration': round(total_duration, 3),
            'success': success,
            'session_id': self.session_id,
            'timestamp': datetime.utcnow().isoformat(),
            **context
        }
        
        level = 'info' if success else 'error'
        self._log_structured(level, f"Ingestion complete: {doc_id}", **log_data)
    
    def get_session_summary(self) -> Dict[str, Any]:
        """
        Get summary of current session metrics (compatibility method).
        
        Returns:
            Dictionary with session summary
        """
        return {
            'session_id': self.session_id,
            'active_operations': len(self.active_operations),
            'operations': list(self.active_operations.keys()),
            'performance_stats': self.get_performance_stats()
        }

    def __str__(self) -> str:
        """String representation of the audit logger."""
        return f"AuditLogger(level={self.log_level}, performance_tracking={self.enable_performance_tracking}, session_id={self.session_id})"