"""
Data service layer for S3 Vector Browser
"""

import sys
import os
from typing import List, Dict, Any, Optional
from botocore.exceptions import ClientError
import boto3

# Add parent directories to path to import s3_vector_ops
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from s3_vector_ops import (
    create_s3_vectors_client, 
    list_indexes, 
    list_vector_buckets,
    get_vector_bucket_details,
    get_index_details,
    query_vectors_for_listing,
    delete_vector_bucket,
    delete_index as delete_index_op,
    delete_vectors,
    search_vectors
)

try:
    from .models import VectorBucket, VectorIndex, VectorItem
    from .exceptions import (
        AWSConnectionError, ResourceNotFoundError, PermissionDeniedError,
        ServiceUnavailableError, DataLoadingError
    )
    from .config import AWS_REGION, ERROR_MESSAGES
except ImportError:
    from models import VectorBucket, VectorIndex, VectorItem
    from exceptions import (
        AWSConnectionError, ResourceNotFoundError, PermissionDeniedError,
        ServiceUnavailableError, DataLoadingError
    )
    # Import from the local config file in the s3_vector_browser directory
    import importlib.util
    spec = importlib.util.spec_from_file_location("config", os.path.join(os.path.dirname(__file__), "config.py"))
    config_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config_module)
    AWS_REGION = config_module.AWS_REGION
    ERROR_MESSAGES = config_module.ERROR_MESSAGES


class S3VectorDataService:
    """Service class for interacting with S3 Vector resources"""
    
    def __init__(self, region_name: str = AWS_REGION):
        """Initialize the data service with AWS clients"""
        self.region_name = region_name
        try:
            self.s3_vectors_client = create_s3_vectors_client(region_name)
        except Exception as e:
            raise AWSConnectionError(f"Failed to create S3 Vectors client: {str(e)}")
    
    def _handle_client_error(self, e: ClientError, operation: str, resource_name: str = None) -> None:
        """
        Centralized error handling for AWS ClientError exceptions
        
        Args:
            e: The ClientError exception
            operation: Description of the operation that failed
            resource_name: Optional resource name for context
        """
        error_code = e.response['Error']['Code']
        
        if error_code == 'AccessDeniedException':
            raise PermissionDeniedError(ERROR_MESSAGES['permission_denied'])
        elif error_code == 'ServiceUnavailableException':
            raise ServiceUnavailableError(ERROR_MESSAGES['service_unavailable'])
        elif error_code in ['NoSuchBucket', 'NoSuchIndex']:
            resource_type = 'bucket' if 'Bucket' in error_code else 'index'
            message = f"Vector {resource_type}"
            if resource_name:
                message += f" '{resource_name}'"
            message += " not found"
            raise ResourceNotFoundError(message)
        else:
            raise DataLoadingError(f"Failed to {operation}: {str(e)}")
    
    def list_vector_buckets(self, prefix: Optional[str] = None, max_results: int = 100) -> List[VectorBucket]:
        """
        List all vector buckets owned by the authenticated user
        
        Args:
            prefix: Optional prefix to filter bucket names
            max_results: Maximum number of buckets to return
            
        Returns:
            List of VectorBucket objects
            
        Raises:
            AWSConnectionError: If unable to connect to AWS
            PermissionDeniedError: If user lacks permission
            ServiceUnavailableError: If service is unavailable
        """
        try:
            # Use s3_vector_ops function
            buckets_data = list_vector_buckets(self.s3_vectors_client, prefix, max_results)
            
            all_buckets = []
            for bucket_data in buckets_data:
                try:
                    bucket = VectorBucket.from_api_response(bucket_data)
                    all_buckets.append(bucket)
                except Exception as e:
                    print(f"Warning: Failed to parse bucket data {bucket_data}: {e}")
                    continue
            
            return all_buckets
            
        except ClientError as e:
            self._handle_client_error(e, "list vector buckets")
        except Exception as e:
            raise DataLoadingError(f"Unexpected error listing buckets: {str(e)}")
    
    def get_bucket_details(self, bucket_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific vector bucket
        
        Args:
            bucket_name: Name of the vector bucket
            
        Returns:
            Dictionary with bucket details
        """
        try:
            # Use s3_vector_ops function
            return get_vector_bucket_details(self.s3_vectors_client, bucket_name)
        except ClientError as e:
            self._handle_client_error(e, "get bucket details", bucket_name)
    
    def list_indexes(self, bucket_name: str, prefix: Optional[str] = None, max_results: Optional[int] = None) -> List[VectorIndex]:
        """
        List all indexes in a vector bucket
        
        Args:
            bucket_name: Name of the vector bucket
            prefix: Optional prefix to filter index names
            max_results: Maximum number of indexes to return
            
        Returns:
            List of VectorIndex objects
        """
        try:
            # Use s3_vector_ops function to get basic index list
            indexes_data = list_indexes(self.s3_vectors_client, bucket_name, prefix, max_results)
            
            indexes = []
            for index_data in indexes_data:
                try:
                    # Get detailed information for each index
                    index_name = index_data.get('indexName', '')
                    if index_name:
                        try:
                            # Get full index details using s3_vector_ops function
                            detailed_index_response = get_index_details(self.s3_vectors_client, bucket_name, index_name)
                            # Extract the actual index data from the nested response
                            detailed_index = detailed_index_response.get('index', detailed_index_response)
                            # Merge the data
                            full_index_data = {**index_data, **detailed_index}
                            index = VectorIndex.from_api_response(full_index_data, bucket_name)
                            indexes.append(index)
                        except Exception as detail_error:
                            print(f"Warning: Could not get details for index {index_name}: {detail_error}")
                            # Fall back to basic data
                            index = VectorIndex.from_api_response(index_data, bucket_name)
                            indexes.append(index)
                    else:
                        print(f"Warning: Index data missing name: {index_data}")
                except Exception as e:
                    print(f"Warning: Failed to parse index data {index_data}: {e}")
                    continue
            
            return indexes
            
        except ClientError as e:
            self._handle_client_error(e, "list indexes", bucket_name)
        except Exception as e:
            raise DataLoadingError(f"Unexpected error listing indexes: {str(e)}")
    
    def get_supported_actions(self, resource_type: str, resource_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get list of supported actions for a resource
        
        Args:
            resource_type: Type of resource ('bucket', 'index', 'item')
            resource_data: Resource data dictionary
            
        Returns:
            List of action dictionaries with name, label, and type
        """
        actions = []
        
        if resource_type == 'bucket':
            actions = [
                {'name': 'view_details', 'label': '👁️ View Details', 'type': 'info'}
            ]
        elif resource_type == 'index':
            actions = [
                {'name': 'view_details', 'label': '👁️ View Details', 'type': 'info'}
            ]
        elif resource_type == 'item':
            actions = []  # No actions for items - double-click shows metadata
        
        return actions
    
    def get_index_details(self, bucket_name: str, index_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific vector index
        
        Args:
            bucket_name: Name of the vector bucket
            index_name: Name of the vector index
            
        Returns:
            Dictionary with index details
        """
        try:
            # Use s3_vector_ops function
            return get_index_details(self.s3_vectors_client, bucket_name, index_name)
        except ClientError as e:
            self._handle_client_error(e, "get index details", f"{bucket_name}/{index_name}")
    
    def delete_bucket(self, bucket_name: str) -> bool:
        """
        Delete a vector bucket
        
        Args:
            bucket_name: Name of the vector bucket to delete
            
        Returns:
            True if successful
        """
        try:
            # Use s3_vector_ops function
            return delete_vector_bucket(self.s3_vectors_client, bucket_name)
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NoSuchBucket':
                return True  # Already deleted
            else:
                self._handle_client_error(e, "delete bucket", bucket_name)
    
    def delete_index(self, bucket_name: str, index_name: str) -> bool:
        """
        Delete a vector index
        
        Args:
            bucket_name: Name of the vector bucket
            index_name: Name of the vector index to delete
            
        Returns:
            True if successful
        """
        try:
            # Use s3_vector_ops function
            return delete_index_op(self.s3_vectors_client, bucket_name, index_name)
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NoSuchIndex':
                return True  # Already deleted
            else:
                self._handle_client_error(e, "delete index", f"{bucket_name}/{index_name}")
    
    def list_items(self, bucket_name: str, index_name: str, max_results: int = 30, 
                   next_token: Optional[str] = None) -> Dict[str, Any]:
        """
        List vector items in an index with pagination
        
        Args:
            bucket_name: Name of the vector bucket
            index_name: Name of the vector index
            max_results: Maximum number of items to return
            next_token: Pagination token for next page
            
        Returns:
            Dictionary with items list and pagination info
        """
        try:
            # Use s3_vector_ops function for querying vectors
            query_result = query_vectors_for_listing(
                self.s3_vectors_client, bucket_name, index_name, max_results, next_token
            )
            
            # Process items
            items = []
            vectors_data = query_result.get('vectors', [])
            
            for vector_data in vectors_data:
                try:
                    item = VectorItem.from_api_response(vector_data, bucket_name, index_name)
                    items.append(item)
                except Exception as e:
                    print(f"Warning: Failed to parse item data {vector_data}: {e}")
                    continue
            
            return {
                'items': items,
                'next_token': query_result.get('next_token'),
                'total_count': query_result.get('total_count', len(items))
            }
            
        except ClientError as e:
            self._handle_client_error(e, "list items", f"{bucket_name}/{index_name}")
        except Exception as e:
            raise DataLoadingError(f"Unexpected error listing items: {str(e)}")
    
    def get_item_metadata(self, bucket_name: str, index_name: str, item_id: str) -> Dict[str, Any]:
        """
        Get metadata for a specific vector item
        
        Args:
            bucket_name: Name of the vector bucket
            index_name: Name of the vector index
            item_id: ID of the vector item
            
        Returns:
            Dictionary with item metadata
        """
        try:
            # Since filtering doesn't seem to work reliably, let's get all items
            # and find the one we want. This is not ideal for large indexes but works.
            items_result = self.list_items(bucket_name, index_name, max_results=30)
            items = items_result.get('items', [])
            
            # Find the item with the matching ID
            for item in items:
                if item.id == item_id:
                    return {
                        'id': item.id,
                        'metadata': item.metadata,
                        'vector_data': item.vector_data,
                        'creation_time': item.creation_time
                    }
            
            # If not found in first batch, try multiple random queries using s3_vector_ops
            # This leverages the existing search_vectors function
            try:
                index_details_response = get_index_details(self.s3_vectors_client, bucket_name, index_name)
                index_details = index_details_response.get('index', index_details_response)
                dimension = index_details.get('dimension', 1536)
                
                # Try a few different random vectors to get different results
                import random
                for attempt in range(3):
                    random_vector = [random.uniform(-1.0, 1.0) for _ in range(dimension)]
                    
                    # Use the search_vectors function from s3_vector_ops
                    search_results = search_vectors(
                        self.s3_vectors_client, bucket_name, index_name, 
                        random_vector, max_results=30
                    )
                    
                    # Check if our item is in this batch
                    for result in search_results:
                        if result.get('id') == item_id:
                            return {
                                'id': result.get('id', item_id),
                                'metadata': result.get('metadata', {}),
                                'vector_data': None,  # Not returned in search results
                                'distance': result.get('distance')
                            }
                
            except Exception as e:
                print(f"Warning: Extended search failed: {e}")
            
            # If still not found, raise error
            raise ResourceNotFoundError(f"Item '{item_id}' not found in index '{index_name}'")
            
        except ResourceNotFoundError:
            raise
        except Exception as e:
            raise DataLoadingError(f"Unexpected error getting item metadata: {str(e)}")
    
    def delete_item(self, bucket_name: str, index_name: str, item_id: str) -> bool:
        """
        Delete a vector item
        
        Args:
            bucket_name: Name of the vector bucket
            index_name: Name of the vector index
            item_id: ID of the vector item to delete
            
        Returns:
            True if successful
        """
        try:
            # Use s3_vector_ops function
            result = delete_vectors(self.s3_vectors_client, bucket_name, index_name, [item_id])
            return result['successful_deletions'] > 0
        except ClientError as e:
            self._handle_client_error(e, "delete item", f"{bucket_name}/{index_name}/{item_id}")
    
    def get_s3_object_content(self, bucket_name: str, object_key: str) -> Dict[str, Any]:
        """
        Get content from S3 object
        
        Args:
            bucket_name: Name of the S3 bucket
            object_key: Key of the S3 object
            
        Returns:
            Dictionary containing object content and metadata
        """
        print(f"📥 Fetching S3 object: s3://{bucket_name}/{object_key}")
        
        try:
            import boto3
            from botocore.exceptions import ClientError
            import base64
            import mimetypes
            
            # Create S3 client
            s3_client = boto3.client('s3', region_name=self.region_name)
            
            # Get object metadata first
            try:
                head_response = s3_client.head_object(Bucket=bucket_name, Key=object_key)
                content_type = head_response.get('ContentType', 'application/octet-stream')
                content_length = head_response.get('ContentLength', 0)
            except ClientError as e:
                if e.response['Error']['Code'] == '404':
                    raise Exception(f"S3 object not found: s3://{bucket_name}/{object_key}")
                else:
                    raise Exception(f"Error accessing S3 object: {str(e)}")
            
            # Determine content type if not set
            if content_type == 'application/octet-stream':
                guessed_type, _ = mimetypes.guess_type(object_key)
                if guessed_type:
                    content_type = guessed_type
            
            # Check if content is too large (limit to 10MB)
            max_size = 10 * 1024 * 1024  # 10MB
            if content_length > max_size:
                return {
                    "success": False,
                    "error": f"File too large ({content_length} bytes). Maximum size is {max_size} bytes.",
                    "content_type": content_type,
                    "size": content_length
                }
            
            # Get object content
            try:
                response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
                content = response['Body'].read()
            except ClientError as e:
                raise Exception(f"Error reading S3 object: {str(e)}")
            
            # Determine if content is text or binary
            is_text = content_type.startswith('text/') or content_type in [
                'application/json', 'application/xml', 'application/javascript',
                'application/csv', 'application/yaml'
            ]
            
            is_image = content_type.startswith('image/')
            
            result = {
                "success": True,
                "content_type": content_type,
                "size": len(content),
                "is_text": is_text,
                "is_image": is_image,
                "object_key": object_key,
                "bucket_name": bucket_name
            }
            
            if is_text:
                # Try to decode as text
                try:
                    text_content = content.decode('utf-8')
                    result["content"] = text_content
                except UnicodeDecodeError:
                    try:
                        text_content = content.decode('latin-1')
                        result["content"] = text_content
                    except UnicodeDecodeError:
                        # If can't decode as text, treat as binary
                        result["is_text"] = False
                        result["content_base64"] = base64.b64encode(content).decode('utf-8')
            elif is_image:
                # Encode image as base64
                result["content_base64"] = base64.b64encode(content).decode('utf-8')
            else:
                # For other binary content, provide base64
                result["content_base64"] = base64.b64encode(content).decode('utf-8')
            
            print(f"Successfully fetched S3 content: {content_type}, {len(content)} bytes")
            return result
            
        except Exception as e:
            print(f"Error fetching S3 content: {str(e)}")
            raise e