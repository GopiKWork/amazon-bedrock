"""
Mock data service for development/testing when S3 Vectors is not available
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from models import VectorBucket, VectorIndex, VectorItem

class MockS3VectorDataService:
    """Mock implementation of S3VectorDataService for development"""
    
    def __init__(self, region_name: str = 'us-west-2'):
        self.region_name = region_name
        
        # Mock data
        self.mock_buckets = [
            VectorBucket(
                name="automotive-vectors-dev",
                arn=f"arn:aws:s3vectors:{region_name}:XXXXXXXXXXXX:bucket/automotive-vectors-dev",
                creation_time=datetime(2024, 1, 15, 10, 30, 0),
                region=region_name,
                supported_actions=["view_details", "delete"]
            ),
            VectorBucket(
                name="demo-vectors",
                arn=f"arn:aws:s3vectors:{region_name}:XXXXXXXXXXXX:bucket/demo-vectors",
                creation_time=datetime(2024, 2, 1, 14, 20, 0),
                region=region_name,
                supported_actions=["view_details", "delete"]
            )
        ]
        
        self.mock_indexes = {
            "automotive-vectors-dev": [
                VectorIndex(
                    name="expert-knowledge",
                    arn=f"arn:aws:s3vectors:{region_name}:XXXXXXXXXXXX:index/expert-knowledge",
                    creation_time=datetime(2024, 1, 15, 11, 0, 0),
                    dimension=1536,
                    distance_metric="cosine",
                    data_type="float32",
                    item_count=1250,
                    supported_actions=["view_details", "query", "delete"],
                    bucket_name="automotive-vectors-dev"
                ),
                VectorIndex(
                    name="dealer-interactions",
                    arn=f"arn:aws:s3vectors:{region_name}:XXXXXXXXXXXX:index/dealer-interactions",
                    creation_time=datetime(2024, 1, 16, 9, 15, 0),
                    dimension=1536,
                    distance_metric="cosine",
                    data_type="float32",
                    item_count=850,
                    supported_actions=["view_details", "query", "delete"],
                    bucket_name="automotive-vectors-dev"
                )
            ],
            "demo-vectors": [
                VectorIndex(
                    name="sample-index",
                    arn=f"arn:aws:s3vectors:{region_name}:XXXXXXXXXXXX:index/sample-index",
                    creation_time=datetime(2024, 2, 1, 15, 0, 0),
                    dimension=768,
                    distance_metric="euclidean",
                    data_type="float32",
                    item_count=100,
                    supported_actions=["view_details", "query", "delete"],
                    bucket_name="demo-vectors"
                )
            ]
        }
        
        self.mock_items = {
            ("automotive-vectors-dev", "expert-knowledge"): [
                VectorItem(
                    id="tsb-honda-2019-001",
                    vector_data=None,
                    metadata={
                        "title": "2019 Honda Accord Starting Issues",
                        "category": "TSB",
                        "make": "Honda",
                        "model": "Accord",
                        "year": 2019,
                        "issue_type": "starting_problems"
                    },
                    creation_time=datetime(2024, 1, 15, 10, 0, 0),
                    supported_actions=["view_details", "delete"],
                    bucket_name="automotive-vectors-dev",
                    index_name="expert-knowledge"
                ),
                VectorItem(
                    id="repair-guide-brake-001",
                    vector_data=None,
                    metadata={
                        "title": "Brake Pad Replacement Guide",
                        "category": "repair_guide",
                        "component": "brakes",
                        "difficulty": "intermediate",
                        "estimated_time": "2-3 hours"
                    },
                    creation_time=datetime(2024, 1, 16, 14, 30, 0),
                    supported_actions=["view_details", "delete"],
                    bucket_name="automotive-vectors-dev",
                    index_name="expert-knowledge"
                )
            ],
            ("automotive-vectors-dev", "dealer-interactions"): [
                VectorItem(
                    id="dealer-query-001",
                    vector_data=None,
                    metadata={
                        "dealer_id": "BMW_SOUTH_001",
                        "query_type": "parts_availability",
                        "region": "South",
                        "specialization": "electric_vehicles"
                    },
                    creation_time=datetime(2024, 1, 17, 9, 45, 0),
                    supported_actions=["view_details", "delete"],
                    bucket_name="automotive-vectors-dev",
                    index_name="dealer-interactions"
                )
            ],
            ("demo-vectors", "sample-index"): [
                VectorItem(
                    id="sample-001",
                    vector_data=None,
                    metadata={
                        "type": "demo",
                        "description": "Sample vector item"
                    },
                    creation_time=datetime(2024, 2, 1, 16, 0, 0),
                    supported_actions=["view_details", "delete"],
                    bucket_name="demo-vectors",
                    index_name="sample-index"
                )
            ]
        }
    
    def list_buckets(self) -> List[VectorBucket]:
        """List all vector buckets"""
        return self.mock_buckets
    
    def list_indexes(self, bucket_name: str) -> List[VectorIndex]:
        """List indexes in a bucket"""
        return self.mock_indexes.get(bucket_name, [])
    
    def list_items(self, bucket_name: str, index_name: str, limit: int = 50, offset: int = 0) -> List[VectorItem]:
        """List items in an index"""
        items = self.mock_items.get((bucket_name, index_name), [])
        return items[offset:offset + limit]
    
    def get_bucket_details(self, bucket_name: str) -> Dict[str, Any]:
        """Get bucket details"""
        bucket = next((b for b in self.mock_buckets if b.name == bucket_name), None)
        if not bucket:
            raise Exception(f"Bucket {bucket_name} not found")
        
        return {
            "name": bucket.name,
            "arn": bucket.arn,
            "creation_time": bucket.creation_time.isoformat(),
            "region": bucket.region,
            "index_count": len(self.mock_indexes.get(bucket_name, [])),
            "total_items": sum(len(items) for key, items in self.mock_items.items() if key[0] == bucket_name)
        }
    
    def get_index_details(self, bucket_name: str, index_name: str) -> Dict[str, Any]:
        """Get index details"""
        indexes = self.mock_indexes.get(bucket_name, [])
        index = next((i for i in indexes if i.name == index_name), None)
        if not index:
            raise Exception(f"Index {index_name} not found in bucket {bucket_name}")
        
        return {
            "name": index.name,
            "arn": index.arn,
            "creation_time": index.creation_time.isoformat(),
            "dimension": index.dimension,
            "distance_metric": index.distance_metric,
            "data_type": index.data_type,
            "item_count": index.item_count
        }
    
    def get_item_details(self, bucket_name: str, index_name: str, item_id: str) -> Dict[str, Any]:
        """Get item details"""
        items = self.mock_items.get((bucket_name, index_name), [])
        item = next((i for i in items if i.id == item_id), None)
        if not item:
            raise Exception(f"Item {item_id} not found")
        
        return {
            "id": item.id,
            "metadata": item.metadata,
            "vector_dimension": 1536,  # Mock dimension
            "last_updated": datetime.now().isoformat()
        }
    
    def query_vectors(self, bucket_name: str, index_name: str, query_vector: List[float], 
                     max_results: int = 10, metadata_filters: Optional[Dict[str, Any]] = None) -> List[VectorItem]:
        """Query vectors (mock implementation)"""
        items = self.mock_items.get((bucket_name, index_name), [])
        # Return items with mock similarity scores
        return items[:max_results]
    
    def delete_bucket(self, bucket_name: str) -> bool:
        """Delete a bucket (mock)"""
        return True
    
    def delete_index(self, bucket_name: str, index_name: str) -> bool:
        """Delete an index (mock)"""
        return True
    
    def delete_item(self, bucket_name: str, index_name: str, item_id: str) -> bool:
        """Delete an item (mock)"""
        return True
    
    def get_s3_object_content(self, bucket_name: str, object_key: str) -> Dict[str, Any]:
        """Get content from S3 object (mock)"""
        print(f"📥 [MOCK] Fetching S3 object: s3://{bucket_name}/{object_key}")
        
        # Simulate different types of content based on file extension
        if object_key.endswith('.txt'):
            return {
                "success": True,
                "content_type": "text/plain",
                "size": 156,
                "is_text": True,
                "is_image": False,
                "object_key": object_key,
                "bucket_name": bucket_name,
                "content": "This is a sample text file content from the S3 object.\n\nIt contains multiple lines of text that would typically be stored in an S3 bucket and referenced by vector metadata.\n\nThis is mock data for demonstration purposes."
            }
        elif object_key.endswith(('.jpg', '.jpeg', '.png', '.gif')):
            # Mock image content (1x1 pixel PNG in base64)
            mock_image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
            return {
                "success": True,
                "content_type": "image/png",
                "size": 67,
                "is_text": False,
                "is_image": True,
                "object_key": object_key,
                "bucket_name": bucket_name,
                "content_base64": mock_image_base64
            }
        elif object_key.endswith('.json'):
            return {
                "success": True,
                "content_type": "application/json",
                "size": 98,
                "is_text": True,
                "is_image": False,
                "object_key": object_key,
                "bucket_name": bucket_name,
                "content": '{\n  "sample": "data",\n  "type": "mock",\n  "description": "This is mock JSON content from S3"\n}'
            }
        else:
            return {
                "success": False,
                "error": "Mock service: Unsupported file type for content preview",
                "content_type": "application/octet-stream",
                "size": 0
            }