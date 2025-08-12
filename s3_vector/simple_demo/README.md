# Simple S3 Vector Demo

This demo demonstrates basic AWS S3 Vector capabilities with a simple automotive industry use case. It creates a small vector index with inline sample data and demonstrates core functionality.

## What This Demo Shows

**Automotive Use Case:**
- **Use Case**: Basic dealer network search and routing
- **Business Value**: Help customers find dealers with specific expertise and certifications

**Technical Operations:**
- Creates an S3 Vector index with automotive dealer data
- Ingests dealer information with rich metadata (region, specialties, certifications)
- Generates embeddings using sentence-transformers
- Performs semantic search with metadata filtering
- Demonstrates different filter types (equality, numeric, boolean)

## Files

- `simple_demo.py` - Python script version
- `simple_demo.ipynb` - Interactive Jupyter notebook version
- `config.py` - Configuration constants
- `utils.py` - Utility functions
- `requirements.txt` - Python dependencies

## Running the Demo

### Option 1: Python Script
```bash
uv run simple_demo.py
```

### Option 2: Jupyter Notebook (Recommended for Data Scientists)
```bash
# First ensure Jupyter is installed
uv pip install -r requirements.txt

# Then launch with uv run to use correct environment
uv run jupyter lab simple_demo.ipynb
```

## What You'll See

The demo creates sample dealer data and shows how vector search can find relevant dealers even when exact keywords don't match. For example:

- Search for "Toyota hybrid specialists" finds dealers with electric vehicle expertise
- Filter by region to find local dealers
- Search by establishment date to find experienced dealers
- Filter by certification status for quality assurance

## Key Concepts Demonstrated

1. **Vector Embeddings**: Text descriptions converted to numerical vectors that capture semantic meaning
2. **Similarity Search**: Find semantically similar content using vector distance calculations
3. **Metadata Filtering**: Combine semantic search with structured data filters
4. **Index Management**: Create and manage vector indexes in S3 Vector Store
5. **Scalable Architecture**: Foundation that can handle thousands of dealers and complex queries

## Prerequisites

- AWS credentials configured with S3 Vector permissions
- Python virtual environment with required packages
- Basic understanding of vector search concepts

## Next Steps

After running this demo:
1. Try the LangChain demo for RAG integration
2. Explore multimodal patterns with images
3. Use the S3 Vector Browser for visual data exploration
4. Scale up with real dealer data