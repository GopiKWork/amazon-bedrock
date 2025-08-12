# S3 Vector Browser

A comprehensive, modern web application for browsing and managing AWS S3 Vector buckets, indexes, and items. Features a robust FastAPI backend with multiple frontend options: a beautiful JavaScript SPA and a functional Streamlit interface.

### **Advanced Search & Filtering
- **Real-time Search**: Search through vector items and metadata as you type
- **Smart Highlighting**: Search terms are highlighted in results with yellow background
- **Deep Metadata Search**: Searches through nested metadata objects and all data types
- **No Results Handling**: Clear messaging and easy search reset when no matches found

### **S3 Content Viewing
- **Direct Content Access**: Click S3 URIs in metadata to view actual file contents
- **Multi-format Support**: 
  - **Text Files**: Display content in scrollable text boxes (.txt, .json, .csv, etc.)
  - **Images**: Render images directly in modal with responsive sizing (.jpg, .png, .gif, etc.)
  - **Binary Files**: Show file information and external links
- **Error Handling**: Graceful handling of missing files, access errors, and size limits
- **Content Actions**: Copy URI, copy content (for text), open in AWS Console

### Enhanced User Experience
- **Mobile Responsive**: Optimized for all screen sizes with adaptive layouts
- **Loading States**: Clear loading indicators for all operations
- **Error Recovery**: User-friendly error messages with actionable suggestions
- **Breadcrumb Navigation**: Easy navigation between buckets, indexes, and items
- **Action Confirmations**: Safe delete operations with confirmation dialogs



## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- AWS credentials configured
- Access to AWS S3 Vectors service (or use mock mode for development)

### JavaScript Interface

1. **Start the backend API server:**
   ```bash
   # Install backend dependencies
   pip install -r requirements.txt
   
   # Start FastAPI backend
   python backend/api_server.py
   ```

2. **Open the frontend:**
   ```bash
   # Option 1: Direct file access
   open frontend-js/index.html
   
   # Option 2: Local server (recommended)
   cd frontend-js
   python -m http.server 8080
   # Then open: http://localhost:8080
   ```


## Backend API Endpoints

The FastAPI backend provides comprehensive REST endpoints:

### Health & Status
- `GET /health` - Service health check with region and service type info
- `GET /docs` - Interactive API documentation (Swagger UI)

### Buckets
- `GET /api/buckets` - List all vector buckets with metadata
- `GET /api/buckets/{bucket}/details` - Get detailed bucket information
- `DELETE /api/buckets/{bucket}` - Delete bucket (with confirmation)

### Indexes
- `GET /api/buckets/{bucket}/indexes` - List indexes in bucket
- `GET /api/buckets/{bucket}/indexes/{index}/details` - Get index details
- `DELETE /api/buckets/{bucket}/indexes/{index}` - Delete index

### Items
- `GET /api/buckets/{bucket}/indexes/{index}/items` - List vector items with pagination
- `GET /api/buckets/{bucket}/indexes/{index}/items/{item}/details` - Get item details
- `DELETE /api/buckets/{bucket}/indexes/{index}/items/{item}` - Delete vector item

### Vector Operations
- `POST /api/buckets/{bucket}/indexes/{index}/query` - Query vectors with similarity search

### **🆕 S3 Content Access**
- `GET /api/s3-content?s3_uri={uri}` - **New!** Fetch and display S3 object content
  - Supports text files (txt, json, csv, etc.)
  - Supports images (jpg, png, gif, etc.) 
  - Handles binary files with metadata
  - Includes error handling and size limits

## 🎯 Usage

### Basic Navigation

1. **Bucket View**: Start by viewing all your S3 vector buckets
   - Click any bucket row to view its indexes
   - Use action buttons to manage buckets
   - View bucket metadata and creation dates

2. **Index View**: Browse indexes within a selected bucket
   - Click any index row to view its items
   - See index specifications (dimensions, distance metrics)
   - Use breadcrumbs to navigate back

3. **Item View**: Explore vector items within an index
   - **Search Items**: Use the search box to find items by ID or metadata
   - Click expand arrows to view detailed metadata
   - **Click S3 URIs**: View actual file contents directly in the browser

### Advanced Search Features

- **Real-time Filtering**: Search updates results as you type
- **Deep Metadata Search**: Searches through all metadata fields and nested objects
- **Search Highlighting**: Matching terms are highlighted in yellow
- **Smart Results**: Shows "X of Y items" when filtering
- **Easy Reset**: Clear search with one click

### S3 Content Viewing

- **Text Files**: Click S3 URIs to view content in scrollable text boxes
- **Images**: View images directly in the modal with responsive sizing
- **JSON/CSV**: Formatted display with proper syntax
- **Copy Actions**: Copy URI or content to clipboard
- **Error Handling**: Clear messages for missing or inaccessible files

### Traditional Features

- **Metadata Viewing**: Click expand arrows to see detailed metadata
- **Action Buttons**: Delete operations with confirmation dialogs
- **Error Recovery**: Built-in error handling with retry mechanisms
- **Responsive Design**: Works on desktop, tablet, and mobile devices

### Environment Variables

- `AWS_REGION`: AWS region to use (default: us-west-2)
- `AWS_ACCESS_KEY_ID`: Your AWS access key
- `AWS_SECRET_ACCESS_KEY`: Your AWS secret key
- `USE_MOCK_DATA`: Set to "true" for development without AWS (default: false)