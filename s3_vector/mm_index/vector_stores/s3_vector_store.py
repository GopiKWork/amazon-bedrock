"""
S3 Vector Store Implementation
=============================

Concrete implementation for AWS S3 Vector Store.
"""

from typing import List, Dict, Any, Optional
from ..base_classes import BaseVectorStore


class S3VectorStore(BaseVectorStore):
    """Concrete implementation for AWS S3 Vector Store."""
    
    def __init__(self, region_name: str = "us-west-2", 
                 vector_dimension: int = 384,
                 distance_metric: str = 'cosine',
                 max_metadata_tags: int = 10,
                 s3_prefix: str = 'indexing-patterns'):
        """
        Initialize S3 Vector Store.
        
        Args:
            region_name: AWS region for S3 Vector service
            vector_dimension: Target vector dimension (256, 384, or 1024)
            distance_metric: Distance metric for similarity search
            max_metadata_tags: Maximum metadata tags per vector (S3 limit is 10)
            s3_prefix: S3 prefix for organizing data
        """
        self.region_name = region_name
        self.vector_dimension = vector_dimension
        self.distance_metric = distance_metric
        self.max_metadata_tags = max_metadata_tags
        self.s3_prefix = s3_prefix
        
        # Validate S3-specific constraints
        if vector_dimension not in [256, 384, 1024]:
            raise ValueError(f"S3 Vector Store supports dimensions 256, 384, or 1024. Got: {vector_dimension}")
        
        import s3_vector_ops
        self.s3_vectors_client = s3_vector_ops.create_s3_vectors_client(region_name)
    
    def validate_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and limit metadata to comply with S3 Vector Store constraints.
        
        Args:
            metadata: Original metadata dictionary
            
        Returns:
            Limited metadata dictionary with at most max_metadata_tags entries
        """
        if not metadata:
            return {}
        
        if len(metadata) <= self.max_metadata_tags:
            return metadata
        
        # Priority tags for S3 Vector Store
        priority_tags = [
            'damage_id', 'vehicle_make', 'vehicle_model', 'damage_type',
            'strategy', 'severity', 'estimated_cost', 'doc_id'
        ]
        
        # Start with priority tags that exist in the metadata
        limited_metadata = {}
        remaining_slots = self.max_metadata_tags
        
        # First, add priority tags if they exist
        for tag in priority_tags:
            if tag in metadata and remaining_slots > 0:
                limited_metadata[tag] = metadata[tag]
                remaining_slots -= 1
        
        # Then add remaining tags until we hit the limit
        for key, value in metadata.items():
            if key not in limited_metadata and remaining_slots > 0:
                limited_metadata[key] = value
                remaining_slots -= 1
        
        return limited_metadata
    
    def get_max_metadata_tags(self) -> int:
        """Get the maximum number of metadata tags supported by S3 Vector Store."""
        return self.max_metadata_tags
    
    def get_vector_dimension(self) -> int:
        """Get the configured vector dimension."""
        return self.vector_dimension
    
    def get_distance_metric(self) -> str:
        """Get the configured distance metric."""
        return self.distance_metric
    
    def create_index(self, index_name: str, dimension: int = None, distance_metric: str = None) -> bool:
        """Create a vector index in S3 Vector Store."""
        try:
            import s3_vector_ops
            # Use instance configuration if not provided
            actual_dimension = dimension or self.vector_dimension
            actual_distance_metric = distance_metric or self.distance_metric
            
            # Extract bucket name from index_name (format: bucket_name/index_name)
            if '/' in index_name:
                bucket_name, actual_index_name = index_name.split('/', 1)
            else:
                raise ValueError("S3 Vector index_name must be in format 'bucket_name/index_name'")
            
            # Create bucket and index
            s3_vector_ops.create_vector_bucket(self.s3_vectors_client, bucket_name)
            s3_vector_ops.create_vector_index(self.s3_vectors_client, bucket_name, actual_index_name)
            return True
        except Exception:
            return False
    
    def ingest_vectors(self, index_name: str, vectors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Ingest vectors into S3 Vector Store."""
        try:
            import s3_vector_ops
            # Extract bucket name from index_name
            if '/' in index_name:
                bucket_name, actual_index_name = index_name.split('/', 1)
            else:
                raise ValueError("S3 Vector index_name must be in format 'bucket_name/index_name'")
            
            # Validate metadata for each vector
            validated_vectors = []
            for vector in vectors:
                validated_vector = vector.copy()
                if 'metadata' in validated_vector:
                    validated_vector['metadata'] = self.validate_metadata(validated_vector['metadata'])
                validated_vectors.append(validated_vector)
            
            return s3_vector_ops.ingest_vectors(
                self.s3_vectors_client, bucket_name, actual_index_name, validated_vectors
            )
        except Exception as e:
            return {"successful_ingestions": 0, "errors": [str(e)]}
    
    def search_vectors(self, index_name: str, query_vector: List[float], 
                      metadata_filters: Optional[Dict[str, Any]] = None, 
                      top_k: int = 10) -> List[Dict[str, Any]]:
        """Search vectors in S3 Vector Store."""
        try:
            import s3_vector_ops
            # Extract bucket name from index_name
            if '/' in index_name:
                bucket_name, actual_index_name = index_name.split('/', 1)
            else:
                raise ValueError("S3 Vector index_name must be in format 'bucket_name/index_name'")
            
            return s3_vector_ops.search_vectors(
                self.s3_vectors_client, bucket_name, actual_index_name, 
                query_vector, metadata_filters, top_k
            )
        except Exception:
            return []
    
    def delete_vectors(self, index_name: str, vector_ids: List[str]) -> bool:
        """Delete vectors from S3 Vector Store."""
        try:
            import s3_vector_ops
            # Extract bucket name from index_name
            if '/' in index_name:
                bucket_name, actual_index_name = index_name.split('/', 1)
            else:
                raise ValueError("S3 Vector index_name must be in format 'bucket_name/index_name'")
            
            s3_vector_ops.delete_vectors(
                self.s3_vectors_client, bucket_name, actual_index_name, vector_ids
            )
            return True
        except Exception:
            return False