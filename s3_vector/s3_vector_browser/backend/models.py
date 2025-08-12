"""
Data models for S3 Vector Browser
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any, Optional


@dataclass
class VectorBucket:
    """Represents an S3 Vector Bucket"""
    name: str
    arn: str
    creation_time: datetime
    region: str
    supported_actions: List[str]
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> 'VectorBucket':
        """Create VectorBucket from AWS API response"""
        # Handle both timestamp and datetime objects
        creation_time_raw = data.get('creationTime', 0)
        if isinstance(creation_time_raw, datetime):
            creation_time = creation_time_raw
        elif isinstance(creation_time_raw, (int, float)):
            creation_time = datetime.fromtimestamp(creation_time_raw)
        else:
            creation_time = datetime.now()
        
        return cls(
            name=data.get('vectorBucketName', ''),
            arn=data.get('vectorBucketArn', ''),
            creation_time=creation_time,
            region=data.get('region', 'us-west-2'),
            supported_actions=['view_details']
        )


@dataclass
class VectorIndex:
    """Represents a Vector Index within a bucket"""
    name: str
    arn: str
    creation_time: datetime
    dimension: int
    distance_metric: str
    data_type: str
    item_count: Optional[int]
    supported_actions: List[str]
    bucket_name: str
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any], bucket_name: str) -> 'VectorIndex':
        """Create VectorIndex from AWS API response"""
        # Handle both timestamp and datetime objects
        creation_time_raw = data.get('creationTime', 0)
        if isinstance(creation_time_raw, datetime):
            creation_time = creation_time_raw
        elif isinstance(creation_time_raw, (int, float)):
            creation_time = datetime.fromtimestamp(creation_time_raw)
        else:
            creation_time = datetime.now()
        
        # Handle missing or null values gracefully
        dimension = data.get('dimension', 0)
        if dimension is None:
            dimension = 0
            
        distance_metric = data.get('distanceMetric', 'Unknown')
        if not distance_metric:
            distance_metric = 'Unknown'
            
        data_type = data.get('dataType', 'float32')
        if not data_type:
            data_type = 'float32'
        
        return cls(
            name=data.get('indexName', ''),
            arn=data.get('indexArn', ''),
            creation_time=creation_time,
            dimension=dimension,
            distance_metric=distance_metric,
            data_type=data_type,
            item_count=data.get('itemCount'),
            supported_actions=['view_details'],
            bucket_name=bucket_name
        )


@dataclass
class VectorItem:
    """Represents a Vector Item within an index"""
    id: str
    vector_data: Optional[List[float]]
    metadata: Dict[str, Any]
    creation_time: Optional[datetime]
    supported_actions: List[str]
    bucket_name: str
    index_name: str
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any], bucket_name: str, index_name: str) -> 'VectorItem':
        """Create VectorItem from AWS API response"""
        # Handle both timestamp and datetime objects
        creation_time_raw = data.get('creationTime')
        creation_time = None
        if creation_time_raw:
            if isinstance(creation_time_raw, datetime):
                creation_time = creation_time_raw
            elif isinstance(creation_time_raw, (int, float)):
                creation_time = datetime.fromtimestamp(creation_time_raw)
        
        return cls(
            id=data.get('key', data.get('id', '')),
            vector_data=data.get('data', {}).get('float32'),
            metadata=data.get('metadata', {}),
            creation_time=creation_time,
            supported_actions=[],
            bucket_name=bucket_name,
            index_name=index_name
        )


@dataclass
class AppState:
    """Application state management"""
    current_view: str = "buckets"  # "buckets", "indexes", "items"
    selected_bucket: Optional[str] = None
    selected_index: Optional[str] = None
    selected_item: Optional[str] = None
    breadcrumbs: List[Dict[str, str]] = None
    loading_state: Dict[str, bool] = None
    error_state: Dict[str, str] = None
    
    def __post_init__(self):
        if self.breadcrumbs is None:
            self.breadcrumbs = []
        if self.loading_state is None:
            self.loading_state = {}
        if self.error_state is None:
            self.error_state = {}


@dataclass
class BreadcrumbItem:
    """Represents a breadcrumb navigation item"""
    label: str
    view: str
    bucket_name: Optional[str] = None
    index_name: Optional[str] = None