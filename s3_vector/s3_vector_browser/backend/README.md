# S3 Vector Browser - Backend API

FastAPI backend server providing REST API endpoints for S3 Vector operations.

## 🏗️ Architecture

```
FastAPI Backend
├── api_server.py          # Main FastAPI application (moved to backend/)
├── data_service.py        # S3 Vectors data access layer
├── mock_data_service.py   # Mock service for development
├── models.py              # Data models (VectorBucket, VectorIndex, VectorItem)
├── exceptions.py          # Custom exception classes
├── config.py              # Configuration constants
├── run_api.py             # API server launcher

└── requirements.txt       # Backend dependencies
```

## 🚀 Quick Start

### Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Start API Server
```bash
# Start with real S3 Vectors (if available)
python run_api.py

# Force mock mode for development
USE_MOCK_DATA=true python run_api.py
```

The API will be available at:
- **Base URL**: `http://localhost:8000`
- **API Documentation**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/health`

## 📚 API Endpoints

### Health & Status
- `GET /health` - Health check and service type info

### Buckets
- `GET /api/buckets` - List all vector buckets
- `GET /api/buckets/{bucket_name}/details` - Get bucket details
- `DELETE /api/buckets/{bucket_name}` - Delete a bucket

### Indexes
- `GET /api/buckets/{bucket_name}/indexes` - List indexes in a bucket
- `GET /api/buckets/{bucket_name}/indexes/{index_name}/details` - Get index details
- `DELETE /api/buckets/{bucket_name}/indexes/{index_name}` - Delete an index

### Items
- `GET /api/buckets/{bucket_name}/indexes/{index_name}/items` - List items in an index
- `GET /api/buckets/{bucket_name}/indexes/{index_name}/items/{item_id}/details` - Get item details
- `DELETE /api/buckets/{bucket_name}/indexes/{index_name}/items/{item_id}` - Delete an item

### Query
- `POST /api/buckets/{bucket_name}/indexes/{index_name}/query` - Query vectors

## 🔧 Configuration

### Environment Variables
- `USE_MOCK_DATA=true` - Force mock mode
- `FORCE_REAL_S3VECTORS=true` - Force real S3 Vectors (fail if unavailable)
- `AWS_REGION` - AWS region (default: us-west-2)

### Service Modes
1. **Real Mode**: Uses actual S3 Vectors service
2. **Mock Mode**: Uses mock data for development (automatic fallback)

## 🧪 Testing

### Test Service Availability
Service availability testing has been moved to development utilities.

This will show:
- boto3 version
- Available AWS services
- S3 Vectors service availability
- Your AWS credentials status

## 🛠️ Development

### Adding New Endpoints
1. Add endpoint to `api_server.py`
2. Add corresponding method to `data_service.py`
3. Update mock service if needed
4. Test with both real and mock data

### Error Handling
- All endpoints include proper HTTP status codes
- Structured error responses with details
- Automatic fallback to mock mode when S3 Vectors unavailable

## 📦 Dependencies

See `requirements.txt`:
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `pydantic` - Data validation
- `boto3` - AWS SDK
- `python-multipart` - Form data support