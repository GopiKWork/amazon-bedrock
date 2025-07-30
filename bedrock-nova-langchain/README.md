# LangChain RAG Demo with AWS Bedrock Nova Pro

A comprehensive Python proof-of-concept demonstrating how to build RAG (Retrieval-Augmented Generation) applications using both custom implementations and LangChain framework with AWS Bedrock Nova Pro model. The demo focuses on car manufacturing industry content and showcases different approaches to building RAG systems.

## Features

- **Two RAG Implementations**: Custom RAG and LangChain-based RAG with pipe operators
- **AWS Bedrock Integration**: Uses Nova Pro model with cross-regional inference
- **Local Vector Store**: ChromaDB with sentence transformers embeddings
- **Rich Car Manufacturing Dataset**: 25 comprehensive documents covering repair, warranty, maintenance, safety, and technical topics
- **Interactive Demo**: Random question selection with detailed output showing retrieved chunks
- **Centralized Configuration**: All constants managed in a single config file

## Project Structure

```
├── config.py                      # Centralized configuration constants
├── car_manufacturing_data.json    # Sample car manufacturing content (25 items)
├── setup_local_vector_store.py    # Creates ChromaDB vector store with embeddings
├── custom_rag.py                  # Hand-built RAG implementation using direct boto3 calls
├── langchain_demo.py              # LangChain RAG with pipe operators and proper integrations
├── rag_demo.ipynb                 # Interactive Jupyter notebook with both RAG implementations
├── requirements.txt               # Python dependencies
├── .env.example                   # Example environment variables file
└── README.md                      # This file
```

## Setup

1. **Create virtual environment with UV**:
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. **Install dependencies**:
```bash
uv pip install -r requirements.txt
```

3. **Set AWS credentials**:

**Option A: Environment Variables**
```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-west-2
```

**Option B: Using .env file**
```bash
# Copy the example file and fill in your credentials
cp .env.example .env
# Edit .env with your actual AWS credentials
```

## Usage

You can run this demo in two ways: **Python Scripts** or **Jupyter Notebook**

### Option 1: Python Scripts

#### 1. Create the Vector Store
First, create the local ChromaDB vector store with car manufacturing content:
```bash
uv run python setup_local_vector_store.py
```

#### 2. Run RAG Demonstrations

**Custom RAG Implementation**:
```bash
uv run python custom_rag.py
```

**LangChain RAG Implementation**:
```bash
uv run python langchain_demo.py
```

### Option 2: Jupyter Notebook (Interactive Experience)

For an interactive experience with detailed explanations, use the Jupyter notebook:

```bash
# Start Jupyter Lab with UV
uv run --with jupyter jupyter lab rag_demo.ipynb
```

The notebook contains three main sections:
1. **Setup ChromaDB** - Executes the setup script using `!python setup_local_vector_store.py`
2. **Custom RAG Demo** - Interactive custom RAG implementation
3. **LangChain RAG Demo** - Interactive LangChain implementation with pipe operators

Each section can be run independently and provides the same functionality as the Python scripts but with enhanced interactivity and documentation.

## Demo Output

Both demos will display:
1. **User Question**: Randomly selected from 8 sample questions
2. **Retrieved Documents**: Top 3 matching chunks from the vector store with titles, categories, and content previews
3. **Final Response**: AI-generated answer using the retrieved context

Example output:
```
User Question: What should I do if my car engine overheats?
==================================================

Retrieved Documents:
------------------------------
1. Title: Engine Overheating Prevention and Solutions
   Category: repair
   Content: Engine overheating is one of the most common and potentially damaging issues...

Final Response:
------------------------------
If your car engine overheats, you should immediately take the following steps...
```

## Configuration

All settings are centralized in `config.py`:
- **AWS Region**: us-west-2
- **Bedrock Model**: us.amazon.nova-pro-v1:0
- **Embedding Model**: all-MiniLM-L6-v2
- **Vector Store Settings**: ChromaDB path, collection name, search parameters
- **Sample Questions**: 8 car manufacturing related questions

## Key Differences Between Implementations

### Custom RAG (`custom_rag.py`)
- Direct boto3 Bedrock runtime client
- Manual ChromaDB operations
- Custom document formatting
- Simple functional approach

### LangChain RAG (`langchain_demo.py`)
- Official LangChain integrations (`langchain-chroma`, `langchain-huggingface`)
- Pipe operators for chain composition
- LangChain's Runnable interface
- Proper prompt templates and output parsers

## Dependencies

- **langchain**: Core LangChain framework
- **langchain-chroma**: ChromaDB integration for LangChain
- **langchain-huggingface**: HuggingFace embeddings integration
- **chromadb**: Vector database for document storage
- **sentence-transformers**: Local embedding model
- **boto3**: AWS SDK for Bedrock integration
- **jupyter**: For running the interactive notebook (optional)

## Sample Questions

The demo includes 8 sample questions covering:
- Engine overheating procedures
- Brake system warranty and maintenance
- Oil change intervals
- Transmission fluid maintenance
- Air filter replacement
- Cooling system maintenance

## Notes

- **Telemetry Disabled**: ChromaDB telemetry is disabled to avoid console warnings
- **Content Preview**: Retrieved documents show first 200 characters for readability
- **Random Selection**: Each run picks a different question for variety
- **Cross-Regional Inference**: Uses AWS Bedrock's cross-regional inference for better availability