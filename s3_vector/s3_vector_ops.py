"""
S3 Vector Operations
===================

Real S3 Vector operations using AWS S3 Vectors client.
"""

import time
import boto3
from botocore.exceptions import ClientError
from typing import List, Dict, Any, Optional
from tqdm import tqdm


class MetadataLimitExceededError(ValueError):
    """Raised when metadata exceeds the configured limit."""
    
    def __init__(self, vector_id: str, actual_count: int, max_allowed: int):
        self.vector_id = vector_id
        self.actual_count = actual_count
        self.max_allowed = max_allowed
        super().__init__(
            f"Vector '{vector_id}' has {actual_count} metadata tags, "
            f"but maximum allowed is {max_allowed}"
        )


def validate_metadata_limits(metadata: Dict[str, Any], max_tags: int, vector_id: str) -> None:
    """
    Validate metadata tag count against S3 Vector Store limits.
    
    Args:
        metadata: Metadata dictionary to validate
        max_tags: Maximum number of metadata tags allowed
        vector_id: Vector ID for error reporting
        
    Raises:
        MetadataLimitExceededError: If metadata exceeds the limit
        TypeError: If metadata is not a dictionary
    """
    if not isinstance(metadata, dict):
        raise TypeError(f"Vector '{vector_id}' metadata must be a dictionary, got {type(metadata)}")
    
    actual_count = len(metadata)
    if actual_count > max_tags:
        raise MetadataLimitExceededError(vector_id, actual_count, max_tags)


def create_s3_vectors_client(region_name: str = 'us-west-2'):
    """Create S3 Vectors client for vector operations."""
    return boto3.client('s3vectors', region_name=region_name)


def create_vector_bucket(s3_vectors_client, bucket_name: Optional[str] = None) -> str:
    """Create an S3 vector bucket."""
    if bucket_name is None:
        # Get AWS account ID
        from config import get_bucket_name
        sts_client = boto3.client('sts', region_name=s3_vectors_client.meta.region_name)
        account_id = sts_client.get_caller_identity()['Account']
        bucket_name = get_bucket_name(account_id)
    
    try:
        # Check if vector bucket already exists using S3 Vectors API
        s3_vectors_client.get_vector_bucket(vectorBucketName=bucket_name)
        print(f"Using existing vector bucket: {bucket_name}")
        return bucket_name
    except ClientError as e:
        if e.response['Error']['Code'] != 'NoSuchBucket':
            print(f"Exception: {e}")
            raise
    
    # Create vector bucket using S3 Vectors API
    try:
        s3_vectors_client.create_vector_bucket(
            vectorBucketName=bucket_name
        )
        print(f"Created new bucket: {bucket_name}")
    except ClientError as create_error:
        if create_error.response['Error']['Code'] == 'ConflictException':
            print(f"Using existing bucket: {bucket_name}")
        else:
            raise
    
    return bucket_name


def create_vector_index(s3_vectors_client, bucket_name: str, index_name: str, 
                       dimension: int = None, distance_metric: str = None) -> str:
    """Create a vector index in the bucket."""
    # Import config constants
    from config import VECTOR_DIMENSION, DISTANCE_METRIC, NON_FILTERABLE_METADATA_KEYS
    
    # Use defaults from config if not provided
    if dimension is None:
        dimension = VECTOR_DIMENSION
    if distance_metric is None:
        distance_metric = DISTANCE_METRIC
    
    try:
        s3_vectors_client.create_index(
            vectorBucketName=bucket_name,
            indexName=index_name,
            dimension=dimension,
            distanceMetric=distance_metric.lower(),
            dataType='float32',
            metadataConfiguration={
                'nonFilterableMetadataKeys': NON_FILTERABLE_METADATA_KEYS
            }
        )
        print(f"Created index: {index_name}")
    except ClientError as index_error:
        if index_error.response['Error']['Code'] == 'ConflictException':
            print(f"Using existing index: {index_name}")
        else:
            raise
    return index_name


def ingest_vectors(s3_vectors_client, bucket_name: str, index_name: str, 
                  vector_data: List[Dict[str, Any]], batch_size: int = None) -> Dict[str, Any]:
    """Bulk ingest vectors into the S3 Vector index."""
    # Import config constants
    from config import DEFAULT_BATCH_SIZE, MAX_METADATA_TAGS
    
    # Use default batch size if not provided
    if batch_size is None:
        batch_size = DEFAULT_BATCH_SIZE
    
    # Validate metadata limits for all vectors before ingestion
    for vector_item in vector_data:
        vector_id = vector_item.get('id', 'unknown')
        metadata = vector_item.get('metadata', {})
        validate_metadata_limits(metadata, MAX_METADATA_TAGS, vector_id)
    
    successful_ingestions = 0
    failed_ingestions = 0
    ingestion_errors = []
    ingested_vector_ids = []
    
    # Process in batches
    for i in tqdm(range(0, len(vector_data), batch_size), desc="Ingesting vectors"):
        batch = vector_data[i:i + batch_size]
        
        # Prepare batch for ingestion - using correct format from AWS docs
        batch_vectors = []
        for vector_item in batch:
            vector_entry = {
                'key': vector_item['id'],
                'data': {'float32': vector_item['vector']},  # Correct format from AWS docs
                'metadata': vector_item['metadata']
            }
            batch_vectors.append(vector_entry)
        
        # S3 Vectors API call
        try:
            response = s3_vectors_client.put_vectors(
                vectorBucketName=bucket_name,
                indexName=index_name,
                vectors=batch_vectors
            )
            
            # All vectors in batch are successful if no exception
            successful_ingestions += len(batch)
            ingested_vector_ids.extend([v['id'] for v in vector_data[i:i + batch_size]])
            
        except Exception as e:
            print(f"Ingestion failure: {e}")
            failed_ingestions += len(batch)
            error_msg = f"Batch {i//batch_size + 1} failed: {str(e)}"
            ingestion_errors.append(error_msg)
    
    # Summary
    total_vectors = len(vector_data)
    success_rate = (successful_ingestions / total_vectors) * 100 if total_vectors > 0 else 0
    
    return {
        'total_vectors': total_vectors,
        'successful_ingestions': successful_ingestions,
        'failed_ingestions': failed_ingestions,
        'success_rate': success_rate,
        'errors': ingestion_errors,
        'ingested_vector_ids': ingested_vector_ids
    }


def search_vectors(s3_vectors_client, bucket_name: str, index_name: str, 
                  query_vector: List[float], metadata_filters: Dict[str, Any] = None,
                  max_results: int = 10) -> List[Dict[str, Any]]:
    """Perform similarity search on vectors."""
    # Prepare query parameters - based on AWS documentation examples
    query_params = {
        'vectorBucketName': bucket_name,
        'indexName': index_name,
        'queryVector': {'float32': query_vector},  # Correct format from AWS docs
        'topK': max_results,
        'returnDistance': True,
        'returnMetadata': True
    }
    
    # Add filter only if provided - using simple key-value format from AWS docs
    if metadata_filters:
        query_params['filter'] = metadata_filters
    
    response = s3_vectors_client.query_vectors(**query_params)
    
    # Process response
    results = []
    if 'vectors' in response:
        for vector_result in response['vectors']:
            result = {
                'id': vector_result['key'],
                'similarity_score': 1.0 - vector_result.get('distance', 0.0),  # Convert distance to similarity
                'metadata': vector_result.get('metadata', {}),
                'distance': vector_result.get('distance', 0.0)
            }
            results.append(result)
    
    return results


def delete_vectors(s3_vectors_client, bucket_name: str, index_name: str, 
                  vector_ids: List[str]) -> Dict[str, Any]:
    """Delete specific vectors by their IDs."""
    try:
        response = s3_vectors_client.delete_vectors(
            vectorBucketName=bucket_name,
            indexName=index_name,
            keys=vector_ids
        )
        
        # S3 Vectors delete API returns success if no exception
        successful_deletions = len(vector_ids)
        failed_deletions = 0
        deletion_errors = []
        
    except Exception as e:
        successful_deletions = 0
        failed_deletions = len(vector_ids)
        deletion_errors = [f"Delete operation failed: {str(e)}"]
    
    total_requested = len(vector_ids)
    success_rate = (successful_deletions / total_requested) * 100 if total_requested > 0 else 0
    
    return {
        'total_requested': total_requested,
        'successful_deletions': successful_deletions,
        'failed_deletions': failed_deletions,
        'success_rate': success_rate,
        'errors': deletion_errors
    }


def cleanup_resources(s3_vectors_client, bucket_name: str, index_name: str) -> bool:
    """Clean up S3 Vector resources."""
    try:
        # Delete vector index
        s3_vectors_client.delete_index(
            vectorBucketName=bucket_name,
            indexName=index_name
        )
        
        # Delete vector bucket
        s3_vectors_client.delete_vector_bucket(
            vectorBucketName=bucket_name
        )
        
        return True
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchBucket':
            return True
        raise


def list_indexes(s3_vectors_client, bucket_name: str, prefix: str = None, max_results: int = None) -> List[Dict[str, Any]]:
    """
    List all vector indexes in an S3 vector bucket.
    
    Args:
        s3_vectors_client: S3 Vectors client
        bucket_name: Name of the vector bucket
        prefix: Optional prefix to filter index names
        max_results: Maximum number of results to return
        
    Returns:
        List of index information dictionaries
        
    Raises:
        ClientError: If the operation fails
    """
    try:
        # Prepare parameters
        params = {
            'vectorBucketName': bucket_name
        }
        
        if prefix:
            params['prefix'] = prefix
        if max_results:
            params['maxResults'] = max_results
        
        # List indexes with pagination support
        all_indexes = []
        next_token = None
        
        while True:
            if next_token:
                params['nextToken'] = next_token
            
            response = s3_vectors_client.list_indexes(**params)
            
            # Add indexes from this page
            indexes = response.get('indexes', [])
            all_indexes.extend(indexes)
            
            # Check for more pages
            next_token = response.get('nextToken')
            if not next_token:
                break
        
        return all_indexes
        
    except ClientError as e:
        print(f"Error listing indexes in bucket {bucket_name}: {e}")
        raise


def get_index_names(s3_vectors_client, bucket_name: str, prefix: str = None) -> List[str]:
    """
    Get just the index names from a vector bucket.
    
    Args:
        s3_vectors_client: S3 Vectors client
        bucket_name: Name of the vector bucket
        prefix: Optional prefix to filter index names
        
    Returns:
        List of index names
    """
    try:
        indexes = list_indexes(s3_vectors_client, bucket_name, prefix)
        return [idx['indexName'] for idx in indexes]
    except Exception as e:
        print(f"Error getting index names: {e}")
        return []


def delete_index(s3_vectors_client, bucket_name: str, index_name: str) -> bool:
    """
    Delete a specific vector index.
    
    Args:
        s3_vectors_client: S3 Vectors client
        bucket_name: Name of the vector bucket
        index_name: Name of the index to delete
        
    Returns:
        True if successful, False otherwise
    """
    try:
        s3_vectors_client.delete_index(
            vectorBucketName=bucket_name,
            indexName=index_name
        )
        print(f"Successfully deleted index: {index_name}")
        return True
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchIndex':
            print(f"Index {index_name} does not exist")
            return True
        else:
            print(f"Error deleting index {index_name}: {e}")
            return False
    except Exception as e:
        print(f"Unexpected error deleting index {index_name}: {e}")
        return False


def list_vector_buckets(s3_vectors_client, prefix: str = None, max_results: int = 100) -> List[Dict[str, Any]]:
    """
    List all vector buckets owned by the authenticated user.
    
    Args:
        s3_vectors_client: S3 Vectors client
        prefix: Optional prefix to filter bucket names
        max_results: Maximum number of buckets to return
        
    Returns:
        List of bucket information dictionaries
        
    Raises:
        ClientError: If the operation fails
    """
    try:
        # Prepare request parameters
        params = {
            'maxResults': min(max_results, 500)  # AWS API limit
        }
        if prefix:
            params['prefix'] = prefix
        
        # List buckets with pagination support
        all_buckets = []
        next_token = None
        
        while True:
            if next_token:
                params['nextToken'] = next_token
            
            response = s3_vectors_client.list_vector_buckets(**params)
            
            # Process bucket data
            buckets = response.get('vectorBuckets', [])
            all_buckets.extend(buckets)
            
            # Check for more pages
            next_token = response.get('nextToken')
            if not next_token:
                break
        
        return all_buckets
        
    except ClientError as e:
        print(f"Error listing vector buckets: {e}")
        raise


def get_vector_bucket_details(s3_vectors_client, bucket_name: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific vector bucket.
    
    Args:
        s3_vectors_client: S3 Vectors client
        bucket_name: Name of the vector bucket
        
    Returns:
        Dictionary with bucket details
        
    Raises:
        ClientError: If the operation fails
    """
    try:
        response = s3_vectors_client.get_vector_bucket(vectorBucketName=bucket_name)
        return response
    except ClientError as e:
        print(f"Error getting bucket details for {bucket_name}: {e}")
        raise


def get_index_details(s3_vectors_client, bucket_name: str, index_name: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific vector index.
    
    Args:
        s3_vectors_client: S3 Vectors client
        bucket_name: Name of the vector bucket
        index_name: Name of the vector index
        
    Returns:
        Dictionary with index details
        
    Raises:
        ClientError: If the operation fails
    """
    try:
        response = s3_vectors_client.get_index(
            vectorBucketName=bucket_name,
            indexName=index_name
        )
        return response
    except ClientError as e:
        print(f"Error getting index details for {bucket_name}/{index_name}: {e}")
        raise


def query_vectors_for_listing(s3_vectors_client, bucket_name: str, index_name: str, 
                             max_results: int = 30, next_token: str = None) -> Dict[str, Any]:
    """
    Query vectors for listing purposes (using random query vector).
    This is a workaround since there's no direct list_items API.
    
    Args:
        s3_vectors_client: S3 Vectors client
        bucket_name: Name of the vector bucket
        index_name: Name of the vector index
        max_results: Maximum number of items to return
        next_token: Pagination token for next page
        
    Returns:
        Dictionary with query results and pagination info
        
    Raises:
        ClientError: If the operation fails
    """
    try:
        # Get index details to understand dimension
        index_details_response = get_index_details(s3_vectors_client, bucket_name, index_name)
        index_details = index_details_response.get('index', index_details_response)
        dimension = index_details.get('dimension', 1536)
        
        # Create a small random query vector instead of zeros
        import random
        random_vector = [random.uniform(-0.1, 0.1) for _ in range(dimension)]
        
        # Query parameters
        params = {
            'vectorBucketName': bucket_name,
            'indexName': index_name,
            'topK': min(max_results, 30),  # API limit is 30
            'returnMetadata': True,
            'returnDistance': False,
            'queryVector': {'float32': random_vector}
        }
        
        if next_token:
            params['nextToken'] = next_token
        
        response = s3_vectors_client.query_vectors(**params)
        
        return {
            'vectors': response.get('vectors', []),
            'next_token': response.get('nextToken'),
            'total_count': len(response.get('vectors', []))
        }
        
    except ClientError as e:
        print(f"Error querying vectors for listing in {bucket_name}/{index_name}: {e}")
        raise


def delete_vector_bucket(s3_vectors_client, bucket_name: str) -> bool:
    """
    Delete a vector bucket.
    
    Args:
        s3_vectors_client: S3 Vectors client
        bucket_name: Name of the vector bucket to delete
        
    Returns:
        True if successful
        
    Raises:
        ClientError: If the operation fails
    """
    try:
        s3_vectors_client.delete_vector_bucket(vectorBucketName=bucket_name)
        print(f"Successfully deleted bucket: {bucket_name}")
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchBucket':
            print(f"Bucket {bucket_name} does not exist")
            return True  # Already deleted
        else:
            print(f"Error deleting bucket {bucket_name}: {e}")
            raise