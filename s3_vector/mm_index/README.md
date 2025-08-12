# MM Index - Pattern-Based Multimodal Indexing

A flexible multimodal indexing system with pattern-based processing strategies for handling text, images, and structured data together. This package provides the core functionality used in the automotive showcase demos.

## 🚀 Quick Start

```python
from mm_index import MMIngestor

# Create ingestor with default AWS components
mm_ingestor = MMIngestor(index_name='my-index')

# Ingest with different patterns
doc_id = mm_ingestor.ingest(
    content={
        'text': "Automotive damage assessment report",
        'image': "path/to/damage.jpg"
    },
    metadata={'vehicle': '2021 Honda Civic', 'damage_type': 'bumper'},
    pattern="hybrid"  # text, hybrid, full_embedding, describe, summarize
)

# Search with metadata filtering
results = mm_ingestor.search(
    query={'text': "Honda bumper damage"},
    metadata_filters={'vehicle': '2021 Honda Civic'},
    top_k=5
)
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                MMIngestor                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐         │
│  │ PreprocessorChain│    │  PatternEngine  │    │   AuditLogger   │         │
│  │                 │    │                 │    │                 │         │
│  │ • ImageResizer  │───▶│ • TextPattern   │───▶│ • Correlation   │         │
│  │ • Custom...     │    │ • HybridPattern │    │ • Error Tracking│         │
│  │                 │    │ • FullEmbedding │    │                 │         │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘         │
│           │                       │                       │                 │
│           ▼                       ▼                       ▼                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐         │
│  │ BatchProcessor  │    │  Vector Store   │    │  Object Store   │         │
│  │                 │    │   (Pluggable)   │    │   (Pluggable)   │         │
│  │ • Chunking      │    │                 │    │                 │         │
│  │ • Parallel      │    │ • S3VectorStore │    │ • S3ObjectStore │         │
│  │ • Audit Logs    │    │                 │    │                 │         │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘         │
│                                   │                       │                 │
│                          ┌─────────────────┐    ┌─────────────────┐         │
│                          │   AI Models     │    │   Validation    │         │
│                          │   (Pluggable)   │    │                 │         │
│                          │                 │    │ • Dimensions    │         │
│                          │ • TitanEmbed    │    │ • Metadata      │         │
│                          │ • NovaProLLM    │    │ • Data Types    │         │
│                          └─────────────────┘    └─────────────────┘         │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 🎯 Core Components

### **Pattern Engine**
Different processing strategies for different data types and use cases:

- **TextPattern**: Pure text embedding and indexing
- **HybridPattern**: Text embeddings with object storage for images
- **FullEmbeddingPattern**: Unified multimodal embeddings for cross-modal search
- **DescribePattern**: Converts images to text descriptions then creates embeddings
- **SummarizePattern**: Condenses long text into summaries then creates embeddings

### **Preprocessor Chain**
Configurable data preprocessing pipeline:

- **ImageResizer**: Standardize image dimensions with aspect ratio preservation
- **Custom Preprocessors**: Extensible preprocessing for specific use cases

### **Batch Processing**
Handle multiple documents efficiently:

- **Chunked Processing**: Process large datasets in manageable batches
- **Parallel Processing**: Configurable worker threads for throughput
- **Error Handling**: Continue processing when individual documents fail

### **Audit System**
Track operations and performance:

- **Correlation Tracking**: End-to-end operation tracing
- **Error Context**: Comprehensive error logging with context
- **Operation Metrics**: Track ingestion and search operations

## 📦 Installation

```bash
# Core dependencies
pip install boto3 pillow numpy sentence-transformers

# AWS credentials
aws configure
```

## 🔄 Extensible Interface

The mm_index library uses an extensible content-based interface that supports current and future media types:

```python
# Extensible interface - supports any media type
doc_id = mm_ingestor.ingest(
    content={
        'text': "Description text",
        'image': "path/to/image.jpg",
        'video': "path/to/video.mp4",  # Future support
        'audio': "path/to/audio.wav",  # Future support
        'document': "path/to/doc.pdf"  # Future support
    },
    metadata={'category': 'multimodal'},
    pattern="multimodal"
)

# Search with extensible interface
results = mm_ingestor.search(
    query={
        'text': "search query",
        'image': "reference.jpg"
    },
    top_k=10
)
```

### Benefits of the Extensible Interface

- **Future-proof**: Easy to add new media types (video, audio, documents) without breaking changes
- **Clean API**: Consistent interface for all media types
- **Flexible**: Support for complex multimodal scenarios
- **Extensible**: Simple to add custom media type handlers

## 🔧 Configuration

### Basic Setup
```python
from mm_index import MMIngestor, ImageResizer

# Default configuration
mm_ingestor = MMIngestor(index_name='my-index')

# Custom preprocessors
mm_ingestor.add_preprocessor(ImageResizer(target_size=(512, 384)))
```

### Advanced Configuration
```python
from mm_index import MMIngestor
from mm_index.vector_stores import S3VectorStore
from mm_index.models import TitanEmbeddingModel

# Custom components
vector_store = S3VectorStore(region_name='us-west-2')
embedding_model = TitanEmbeddingModel()

mm_ingestor = MMIngestor(
    index_name='advanced-index',
    vector_store=vector_store,
    embedding_model=embedding_model,
    vector_dimension=1024
)
```

## 🚀 Usage Examples

### Single Document Ingestion
```python
# Text only
doc_id = mm_ingestor.ingest(
    content={'text': "Technical documentation content"},
    metadata={'category': 'technical', 'version': '1.0'},
    pattern="text"
)

# With image preprocessing
doc_id = mm_ingestor.ingest(
    content={
        'text': "Damage assessment report",
        'image': "damage_photo.jpg"  # Auto-resized and processed
    },
    metadata={'vehicle': 'Honda Civic', 'severity': 'minor'},
    pattern="hybrid"
)

# Future extensibility - video and audio support
doc_id = mm_ingestor.ingest(
    content={
        'text': "Incident report",
        'image': "scene.jpg",
        'video': "incident.mp4",  # Future support
        'audio': "witness.wav"   # Future support
    },
    metadata={'incident_id': 'INC-2024-001'},
    pattern="multimodal"  # Future pattern
)
```

### Batch Processing
```python
# Batch ingestion for multiple documents
batch_data = [
    {'text': 'Document 1', 'image': 'image1.jpg'},
    {'text': 'Document 2', 'image': 'image2.jpg'},
    {'text': 'Document 3', 'video': 'video3.mp4'},  # Future support
    # ... more documents with various media types
]

batch_metadata = [
    {'category': 'automotive', 'type': 'damage'},
    {'category': 'automotive', 'type': 'maintenance'},
    {'category': 'automotive', 'type': 'incident'},
    # ... corresponding metadata
]

doc_ids = mm_ingestor.batch_ingest(
    data_list=batch_data,
    pattern="hybrid",
    metadata_list=batch_metadata
)
```

### Search and Retrieval
```python
# Semantic search with metadata filtering
results = mm_ingestor.search(
    query={'text': "Honda bumper damage collision"},
    metadata_filters={
        'vehicle': 'Honda Civic',
        'severity': 'minor'
    },
    top_k=10
)

# Multimodal search (future capability)
results = mm_ingestor.search(
    query={
        'text': "collision damage",
        'image': "reference_damage.jpg"
    },
    metadata_filters={'vehicle_type': 'sedan'},
    top_k=5
)

# Process results
for result in results:
    print(f"Document: {result['id']}")
    print(f"Score: {result['similarity_score']:.3f}")
    
    # Access original content if stored
    if 'original_image' in result:
        print("Original image available")
    if 'original_text' in result:
        print("Original text available")
```

## 🔍 Pattern Strategies

| Pattern | Use Case | Input | Output | Best For |
|---------|----------|-------|--------|----------|
| **text** | Pure text documents | Text only | Text embeddings | Reports, documentation |
| **hybrid** | Text + images, mixed media | Text + Image | Text embeddings + object refs | Damage claims, technical docs |
| **full_embedding** | Unified multimodal search | Text + Image | Multimodal embeddings | Cross-modal search |
| **describe** | Image-to-text search | Image (+ Text) | Text embeddings from description | Photo analysis |
| **summarize** | Long document search | Long Text | Text embeddings from summary | Large documents |

## 🔧 Extensibility

### Custom Patterns
```python
from mm_index.patterns import PatternStrategy

class CustomPattern(PatternStrategy):
    @property
    def pattern_name(self):
        return "custom"
    
    def process(self, data, metadata):
        # Custom processing logic
        return embeddings, enriched_metadata

# Register custom pattern
mm_ingestor.pattern_engine.register_pattern(CustomPattern())
```

### Custom Preprocessors
```python
from mm_index.preprocessors import Preprocessor

class CustomPreprocessor(Preprocessor):
    @property
    def processor_name(self):
        return "custom_processor"
    
    def process(self, data):
        # Custom preprocessing logic
        return processed_data

mm_ingestor.add_preprocessor(CustomPreprocessor())
```

## 🔗 AWS Services Integration

### Required Services
- **Amazon Bedrock**: Titan Embedding, Nova Pro models
- **S3 Vector Store**: Vector storage and search
- **S3**: Object storage for images and large text

### Required IAM Permissions

#### Basic Permissions
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3vectors:ListVectorBuckets",
                "s3vectors:CreateVectorBucket",
                "s3vectors:GetVectorBucket",
                "s3vectors:CreateIndex",
                "s3vectors:GetIndex",
                "s3vectors:QueryVectors",
                "s3vectors:GetVectors",
                "s3vectors:PutVectors",
                "s3:CreateBucket",
                "s3:GetObject",
                "s3:PutObject",
                "s3:ListBucket",
                "bedrock:InvokeModel",
                "sts:GetCallerIdentity"
            ],
            "Resource": "*"
        }
    ]
}
```

## 📚 Examples

See the main project demos for complete usage examples:

- **[Automotive Demo](../multimodal_patterns/automotive_damage_demo.py)**: Real automotive damage assessment
- **[Simple Demo](../simple_demo.py)**: Basic vector operations
- **[Strands Agent](../strands/strands_agent_automotive.py)**: Intelligent agent integration

## 🤝 Extending MM Index

1. **Patterns**: Extend `PatternStrategy` for new processing strategies
2. **Preprocessors**: Extend `Preprocessor` for data transformation
3. **Stores**: Implement `BaseVectorStore` or `BaseObjectStore` interfaces
4. **Models**: Implement AI model interfaces for new providers

This package provides the foundation for building multimodal AI applications with flexible processing strategies and AWS service integration.