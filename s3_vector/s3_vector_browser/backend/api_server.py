#!/usr/bin/env python3
"""
FastAPI backend server for S3 Vector Browser
Provides REST API endpoints for both Streamlit and Node.js frontends
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
import os
import sys
import boto3
import base64
from datetime import datetime
from urllib.parse import urlparse

# Add parent directories to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from .data_service import S3VectorDataService
    from .mock_data_service import MockS3VectorDataService
    from .models import VectorBucket, VectorIndex, VectorItem
    from .exceptions import (
        AWSConnectionError, ResourceNotFoundError, PermissionDeniedError,
        ServiceUnavailableError, DataLoadingError
    )
    from .config import AWS_REGION
except ImportError:
    from data_service import S3VectorDataService
    from mock_data_service import MockS3VectorDataService
    from models import VectorBucket, VectorIndex, VectorItem
    from exceptions import (
        AWSConnectionError, ResourceNotFoundError, PermissionDeniedError,
        ServiceUnavailableError, DataLoadingError
    )
    from config import AWS_REGION

# Pydantic models for API requests/responses
class BucketResponse(BaseModel):
    name: str
    arn: str
    creation_time: datetime
    region: str
    supported_actions: List[str]

class IndexResponse(BaseModel):
    name: str
    arn: str
    creation_time: datetime
    dimension: int
    distance_metric: str
    data_type: str
    item_count: Optional[int]
    supported_actions: List[str]

class ItemResponse(BaseModel):
    id: str
    metadata: Dict[str, Any]
    similarity_score: Optional[float]
    supported_actions: List[str]

class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None

class QueryRequest(BaseModel):
    query_vector: List[float]
    max_results: int = 10
    metadata_filters: Optional[Dict[str, Any]] = None

# Initialize FastAPI app
app = FastAPI(
    title="S3 Vector Browser API",
    description="REST API for browsing and managing AWS S3 Vector buckets, indexes, and items",
    version="1.0.0"
)

# Add CORS middleware for Node.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global data service instance
data_service = None

@app.on_event("startup")
async def startup_event():
    """Initialize data service on startup"""
    global data_service
    
    # Show boto3 version info
    import boto3
    print(f"📦 boto3 version: {boto3.__version__}")
    
    # Check available services
    session = boto3.Session()
    available_services = session.get_available_services()
    s3vectors_available = 's3vectors' in available_services
    print(f"S3 Vectors service available in boto3: {s3vectors_available}")
    print(f"Available regions for session: {session.get_available_regions('s3') if not s3vectors_available else session.get_available_regions('s3vectors')}")
    
    # Check if we should force real mode (default is to use mock when S3 Vectors unavailable)
    force_real = os.getenv("FORCE_REAL_S3VECTORS", "false").lower() == "true"
    use_mock = os.getenv("USE_MOCK_DATA", "auto").lower()
    
    if use_mock == "true":
        print(f"🧪 Using mock data service for development (forced by USE_MOCK_DATA=true)")
        data_service = MockS3VectorDataService(region_name=AWS_REGION)
        return
    
    if not s3vectors_available and not force_real:
        print(f"S3 Vectors service not available in boto3 {boto3.__version__}")
        print(f"Automatically using mock data service for development...")
        print(f"   To force real S3 Vectors: set FORCE_REAL_S3VECTORS=true")
        data_service = MockS3VectorDataService(region_name=AWS_REGION)
        return
    elif not s3vectors_available and force_real:
        print(f"S3 Vectors service not available but FORCE_REAL_S3VECTORS=true")
        print(f"   Cannot proceed without S3 Vectors service")
        data_service = None
        return
    
    try:
        data_service = S3VectorDataService(region_name=AWS_REGION)
        print(f"Real S3 Vectors data service initialized successfully for region: {AWS_REGION}")
    except Exception as e:
        print(f"Failed to initialize real S3 Vectors service: {e}")
        print(f"Error details: {type(e).__name__}: {str(e)}")
        print(f"")
        print(f"Falling back to mock data service for development...")
        
        try:
            data_service = MockS3VectorDataService(region_name=AWS_REGION)
            print(f"Mock data service initialized successfully")
        except Exception as mock_error:
            print(f"Failed to initialize mock service: {mock_error}")
            data_service = None

def handle_service_error(error: Exception) -> HTTPException:
    """Convert service errors to HTTP exceptions"""
    if isinstance(error, AWSConnectionError):
        return HTTPException(status_code=503, detail=f"AWS connection error: {str(error)}")
    elif isinstance(error, ResourceNotFoundError):
        return HTTPException(status_code=404, detail=f"Resource not found: {str(error)}")
    elif isinstance(error, PermissionDeniedError):
        return HTTPException(status_code=403, detail=f"Permission denied: {str(error)}")
    elif isinstance(error, ServiceUnavailableError):
        return HTTPException(status_code=503, detail=f"Service unavailable: {str(error)}")
    else:
        return HTTPException(status_code=500, detail=f"Internal server error: {str(error)}")

# API Endpoints

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    if data_service is None:
        return {
            "status": "unhealthy", 
            "region": AWS_REGION,
            "error": "Data service not initialized"
        }
    
    service_type = "mock" if isinstance(data_service, MockS3VectorDataService) else "real"
    return {
        "status": "healthy", 
        "region": AWS_REGION,
        "service_type": service_type,
        "message": f"Using {service_type} S3 Vectors service"
    }

@app.get("/api/buckets", response_model=List[BucketResponse])
async def list_buckets():
    """List all vector buckets"""
    if data_service is None:
        raise HTTPException(
            status_code=503, 
            detail="S3 Vectors service not available. Check region and service availability."
        )
    
    try:
        print(f"Calling data_service.list_vector_buckets()...")
        buckets = data_service.list_vector_buckets()
        print(f"Got {len(buckets)} buckets from data service")
        
        response_buckets = []
        for bucket in buckets:
            print(f"📦 Processing bucket: {bucket.name}")
            response_buckets.append(
                BucketResponse(
                    name=bucket.name,
                    arn=bucket.arn,
                    creation_time=bucket.creation_time,
                    region=bucket.region,
                    supported_actions=bucket.supported_actions
                )
            )
        
        print(f"Returning {len(response_buckets)} bucket responses")
        return response_buckets
        
    except Exception as e:
        print(f"Error in list_buckets: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise handle_service_error(e)

@app.get("/api/buckets/{bucket_name}/indexes", response_model=List[IndexResponse])
async def list_indexes(bucket_name: str):
    """List indexes in a specific bucket"""
    if data_service is None:
        raise HTTPException(status_code=503, detail="S3 Vectors service not available")
    
    try:
        indexes = data_service.list_indexes(bucket_name)
        return [
            IndexResponse(
                name=index.name,
                arn=index.arn,
                creation_time=index.creation_time,
                dimension=index.dimension,
                distance_metric=index.distance_metric,
                data_type=index.data_type,
                item_count=index.item_count,
                supported_actions=index.supported_actions
            )
            for index in indexes
        ]
    except Exception as e:
        raise handle_service_error(e)

@app.get("/api/buckets/{bucket_name}/indexes/{index_name}/items", response_model=List[ItemResponse])
async def list_items(
    bucket_name: str, 
    index_name: str,
    limit: int = Query(default=50, le=1000),
    offset: int = Query(default=0, ge=0)
):
    """List items in a specific index"""
    if data_service is None:
        raise HTTPException(status_code=503, detail="S3 Vectors service not available")
    
    try:
        print(f"Calling list_items for bucket={bucket_name}, index={index_name}, limit={limit}")
        
        # The data service list_items returns a dict with 'items' key
        result = data_service.list_items(bucket_name, index_name, max_results=limit)
        print(f"Got result type: {type(result)}")
        print(f"Result keys: {result.keys() if isinstance(result, dict) else 'Not a dict'}")
        
        items = result.get('items', [])
        print(f"📦 Got {len(items)} items")
        
        response_items = []
        for i, item in enumerate(items):
            print(f"Processing item {i}: {type(item)}")
            try:
                response_items.append(
                    ItemResponse(
                        id=item.id,
                        metadata=item.metadata,
                        similarity_score=None,  # VectorItem doesn't have similarity_score
                        supported_actions=item.supported_actions
                    )
                )
            except Exception as item_error:
                print(f"Error processing item {i}: {item_error}")
                print(f"   Item data: {item}")
                continue
        
        print(f"Returning {len(response_items)} item responses")
        return response_items
        
    except Exception as e:
        print(f"Error in list_items: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise handle_service_error(e)

@app.get("/api/buckets/{bucket_name}/details")
async def get_bucket_details(bucket_name: str):
    """Get detailed information about a bucket"""
    if data_service is None:
        raise HTTPException(status_code=503, detail="S3 Vectors service not available")
    
    try:
        details = data_service.get_bucket_details(bucket_name)
        return details
    except Exception as e:
        raise handle_service_error(e)

@app.get("/api/buckets/{bucket_name}/indexes/{index_name}/details")
async def get_index_details(bucket_name: str, index_name: str):
    """Get detailed information about an index"""
    if data_service is None:
        raise HTTPException(status_code=503, detail="S3 Vectors service not available")
    
    try:
        details = data_service.get_index_details(bucket_name, index_name)
        return details
    except Exception as e:
        raise handle_service_error(e)

@app.get("/api/buckets/{bucket_name}/indexes/{index_name}/items/{item_id}/details")
async def get_item_details(bucket_name: str, index_name: str, item_id: str):
    """Get detailed information about an item"""
    if data_service is None:
        raise HTTPException(status_code=503, detail="S3 Vectors service not available")
    
    try:
        # Use get_item_metadata method from data service
        details = data_service.get_item_metadata(bucket_name, index_name, item_id)
        return details
    except Exception as e:
        raise handle_service_error(e)

@app.post("/api/buckets/{bucket_name}/indexes/{index_name}/query", response_model=List[ItemResponse])
async def query_vectors(bucket_name: str, index_name: str, query: QueryRequest):
    """Query vectors in an index"""
    try:
        results = data_service.query_vectors(
            bucket_name=bucket_name,
            index_name=index_name,
            query_vector=query.query_vector,
            max_results=query.max_results,
            metadata_filters=query.metadata_filters
        )
        return [
            ItemResponse(
                id=item.id,
                metadata=item.metadata,
                similarity_score=item.similarity_score,
                supported_actions=item.supported_actions
            )
            for item in results
        ]
    except Exception as e:
        raise handle_service_error(e)

@app.delete("/api/buckets/{bucket_name}")
async def delete_bucket(bucket_name: str):
    """Delete a vector bucket"""
    try:
        result = data_service.delete_bucket(bucket_name)
        return {"success": True, "message": f"Bucket {bucket_name} deleted successfully"}
    except Exception as e:
        raise handle_service_error(e)

@app.delete("/api/buckets/{bucket_name}/indexes/{index_name}")
async def delete_index(bucket_name: str, index_name: str):
    """Delete an index"""
    try:
        result = data_service.delete_index(bucket_name, index_name)
        return {"success": True, "message": f"Index {index_name} deleted successfully"}
    except Exception as e:
        raise handle_service_error(e)

@app.delete("/api/buckets/{bucket_name}/indexes/{index_name}/items/{item_id}")
async def delete_item(bucket_name: str, index_name: str, item_id: str):
    """Delete a vector item"""
    try:
        result = data_service.delete_item(bucket_name, index_name, item_id)
        return {"success": True, "message": f"Item {item_id} deleted successfully"}
    except Exception as e:
        raise handle_service_error(e)

@app.get("/api/s3-content")
async def get_s3_content(s3_uri: str):
    """Get content from S3 URI"""
    try:
        print(f"📥 Fetching S3 content for: {s3_uri}")
        
        # Parse S3 URI
        if not s3_uri.startswith('s3://'):
            raise HTTPException(status_code=400, detail="Invalid S3 URI format")
        
        # Remove s3:// prefix and split bucket/key
        s3_path = s3_uri[5:]  # Remove 's3://'
        parts = s3_path.split('/', 1)
        
        if len(parts) != 2:
            raise HTTPException(status_code=400, detail="Invalid S3 URI format")
        
        bucket_name, object_key = parts
        
        # Get S3 object content
        content_info = data_service.get_s3_object_content(bucket_name, object_key)
        
        print(f"Successfully fetched S3 content: {content_info.get('content_type', 'unknown')}")
        return content_info
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching S3 content: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch S3 content: {str(e)}")

def main():
    """Main entry point for the API server"""
    import argparse
    
    parser = argparse.ArgumentParser(description="S3 Vector Browser API Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    
    args = parser.parse_args()
    
    print(f"🚀 Starting S3 Vector Browser API Server...")
    print(f"📍 Region: {AWS_REGION}")
    print(f"🌐 URL: http://{args.host}:{args.port}")
    print(f"📚 Docs: http://{args.host}:{args.port}/docs")
    print("-" * 50)
    
    uvicorn.run(
        "api_server:app",
        host=args.host,
        port=args.port,
        reload=args.reload
    )

if __name__ == "__main__":
    main()