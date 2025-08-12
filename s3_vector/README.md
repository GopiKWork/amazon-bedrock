# S3 Vector Store Automotive Showcase

A comprehensive implementation demonstrating how AWS S3 Vector Store can be used for automotive industry applications, including damage assessment, technical support, and dealer interactions.

## Automotive Industry Use Case

### The Challenge
The automotive industry manages vast amounts of diverse data that is difficult to search and connect:

- **Insurance Claims Processing**: Insurance companies receive thousands of damage photos, repair estimates, and claim documents that need to be reviewed, categorized, and processed manually
- **Technical Support**: Service technicians need to find relevant information from scattered sources including Technical Service Bulletins (TSBs), diagnostic procedures, repair manuals, and parts catalogs
- **Dealer Network Management**: Automotive manufacturers need to route customers to dealers with the right expertise, certifications, and capabilities for specific vehicle types and services
- **Knowledge Management**: Field technicians and customer service representatives need instant access to expert knowledge but information is spread across multiple systems and formats

*TSB = Technical Service Bulletin: Official communications from vehicle manufacturers to dealers about known issues, repairs, and updates*

### The S3 Vector Store Solution
This showcase demonstrates how vector search technology can address these challenges by:

- **Semantic Search**: Find relevant information using natural language queries instead of exact keyword matching
- **Multimodal Processing**: Search across text documents, images, and structured data simultaneously
- **Intelligent Matching**: Connect customer problems with similar historical cases and relevant technical documentation
- **Unified Knowledge Base**: Bring together information from multiple sources into a single searchable system

## Prerequisites

### AWS Setup
You need AWS credentials configured with the following IAM permissions:

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
                "s3vectors:DeleteVectorBucket",
                "s3vectors:ListIndexes",
                "s3vectors:CreateIndex",
                "s3vectors:GetIndex",
                "s3vectors:DeleteIndex",
                "s3vectors:QueryVectors",
                "s3vectors:GetVectors",
                "s3vectors:PutVectors",
                "s3vectors:ListVectors",
                "s3vectors:DeleteVectors",
                "s3:CreateBucket",
                "s3:GetBucketLocation",
                "s3:ListBucket",
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream",
                "sts:GetCallerIdentity"
            ],
            "Resource": "*"
        }
    ]
}
```

Configure AWS credentials:
```bash
aws configure
```

### Python Environment Setup
Install uv (Python package manager):
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or on macOS with Homebrew
brew install uv

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Create and activate virtual environment:
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
```

### Jupyter Setup (for Interactive Notebooks)
To ensure Jupyter works correctly with all dependencies:
```bash
# Run the setup script to configure Jupyter
chmod +x setup_jupyter.sh
./setup_jupyter.sh

# Or manually install Jupyter requirements
uv pip install -r requirements.txt
```

## Demo Walkthrough

This solution includes three demos progressing from simple to complex:

### 1. Simple Demo - Basic Vector Operations

**Python Script:**
```bash
uv run simple_demo/simple_demo.py
```

**Jupyter Notebook (Recommended for Data Scientists):**
```bash
uv run jupyter lab simple_demo/simple_demo.ipynb
```

**What this demonstrates:**
- **Use Case**: Basic dealer network search and routing
- **Technical Operations**: 
  - Creates an S3 Vector index
  - Ingests dealer information with metadata (region, specialties, certifications)
  - Generates embeddings using sentence-transformers
  - Performs semantic search with metadata filtering
- **What you'll see**: Search for dealers by specialty (e.g., "Toyota hybrid specialists") and see how vector search finds relevant matches even when exact keywords don't match

### 2. LangChain RAG - Conversational AI Integration

**Python Script:**
```bash
uv run langchain_demo/langchain_s3_rag.py
```

**Jupyter Notebook (Recommended for Data Scientists):**
```bash
uv run jupyter lab langchain_demo/langchain_demo.ipynb
```

**What this demonstrates:**
- **Use Case**: Integration with popular AI frameworks for building conversational applications
- **Technical Operations**:
  - Uses LangChain framework with custom S3VectorStore integration
  - Implements Retrieval-Augmented Generation (RAG) pattern
  - Connects to Amazon Bedrock Nova Pro for natural language responses
  - Creates and uses inline sample automotive documents (no external data files needed)
- **What you'll see**: Question-answering system that retrieves relevant automotive information and generates comprehensive responses

### 3. Multimodal Damage Assessment - Insurance Claims

**Python Script:**
```bash
uv run multimodal_patterns/automotive_damage_demo.py
```

**Jupyter Notebook (Recommended for Visual Analysis):**
```bash
uv run jupyter lab multimodal_patterns/multimodal_demo.ipynb
```

**What this demonstrates:**
- **Use Case**: Automated insurance claim processing with damage photos
- **Technical Operations**:
  - Processes real automotive damage photos alongside text descriptions
  - Uses 5 different AI processing patterns:
    - **Text Pattern**: Processes written damage descriptions
    - **Hybrid Pattern**: Combines photos with text descriptions
    - **Full Embedding Pattern**: Creates unified understanding of images and text
    - **Describe Pattern**: Generates text descriptions from photos
    - **Summarize Pattern**: Condenses lengthy reports into key points
- **What you'll see**: Real damage cases (Honda Civic bumper damage, BMW collision, etc.) being processed and made searchable. In the notebook version, you can see the actual damage photos and interact with the results.

### 4. S3 Vector Browser - Visual Management Interface
```bash
cd s3_vector_browser

# Option A: Streamlit Interface (Simple)
streamlit run streamlit_app.py

# Option B: JavaScript Interface (Advanced)
# Start backend API server
python backend/api_server.py

# Open frontend in browser
open frontend-js/index.html
```

**What this demonstrates:**
- **Use Case**: Visual management and exploration of vector data for technical teams and administrators
- **Technical Operations**:
  - **Web-based Interface**: Browse vector buckets, indexes, and items through intuitive UI
  - **Real-time Search**: Search through vector metadata with highlighting and filtering
  - **S3 Content Viewing**: Click on S3 URIs in metadata to view actual file contents (text, images, documents)
  - **Vector Operations**: Create, delete, and manage vector resources through the interface
  - **Dual Frontend Options**: Choose between simple Streamlit or advanced JavaScript interface
- **What you'll see**: 
  - Complete visual overview of your vector data
  - Search and filter capabilities across all automotive data
  - Direct content viewing of damage photos, technical documents, and reports
  - Administrative tools for managing vector indexes and data
- **Key Benefits**: Provides non-technical users with easy access to vector data and enables quick data exploration and validation

### 5. Cleanup (Optional)
After running the demos, you can clean up the AWS resources to avoid ongoing costs:

#### **Complete Cleanup (All Resources)**
```bash
# Clean up all AWS resources created by the demos
uv run cleanup.py

# Dry run to see what would be deleted (recommended first)
uv run cleanup.py --dry-run
```

#### **Selective Cleanup Options**
```bash
# List all vector indexes without deleting
uv run cleanup.py --list-only

# Delete only vector indexes (keep S3 buckets)
uv run cleanup.py --vectors-only

# Delete only S3 objects (keep buckets and indexes)
uv run cleanup.py --objects-only

# Delete specific vector indexes
uv run cleanup.py --vectors-only --index-names automotive-interactions-index automotive-expert-knowledge-index

# Use different AWS region
uv run cleanup.py --region us-east-1
```

#### **What Gets Cleaned Up**
- **Vector Indexes**: All S3 Vector Store indexes created by demos
- **S3 Vector Buckets**: Buckets containing vector data
- **S3 Object Storage**: Images and documents stored during multimodal processing
- **Note**: Amazon Bedrock usage is pay-per-use, no cleanup needed

#### **Safety Features**
- **Dry Run Mode**: Use `--dry-run` to preview what would be deleted
- **Selective Cleanup**: Choose specific resources to clean up
- **Error Handling**: Script continues even if some resources fail to delete

**Important**: Only clean up if you're done experimenting with the demos, as you'll need to re-run the setup steps to use them again.



## Project Structure

```
├── config.py                      # Configuration constants
├── simple_demo/                   # Demo 1: Basic S3 vector operations
│   ├── simple_demo.py             # Python script version
│   ├── simple_demo.ipynb          # Jupyter notebook version
│   ├── README.md                  # Demo documentation
│   ├── config.py                  # Configuration constants
│   ├── utils.py                   # Utility functions
│   └── requirements.txt           # Python dependencies
├── langchain_demo/                # Demo 2: LangChain RAG integration
│   ├── langchain_demo.ipynb       # Jupyter notebook version
│   ├── langchain_s3_rag.py        # Python script version
│   ├── langchain_community/       # Custom S3VectorStore
│   ├── README.md                  # Demo documentation
│   ├── config.py                  # Configuration constants
│   ├── utils.py                   # Utility functions
│   └── requirements.txt           # Python dependencies
├── multimodal_patterns/           # Demo 3: Automotive damage assessment
│   ├── automotive_damage_demo.py  # Python script version
│   ├── multimodal_demo.ipynb      # Jupyter notebook version
│   ├── images/                    # Sample damage photos
│   └── README.md                  # Demo documentation

├── s3_vector_browser/             # Visual management interface
│   ├── streamlit_app.py           # Simple Streamlit interface
│   ├── backend/                   # FastAPI backend server
│   │   ├── api_server.py          # REST API endpoints
│   │   ├── data_service.py        # S3 Vector operations
│   │   └── mock_data_service.py   # Development mock data
│   └── frontend-js/               # Advanced JavaScript interface
│       ├── index.html             # Main application page
│       ├── js/                    # JavaScript modules
│       └── css/                   # Styling and themes
├── data/                          # Sample automotive data
│   ├── automotive_expert_knowledge.json # Technical knowledge base
│   ├── dealer_oem_interaction.json      # Dealer-OEM interaction data
│   ├── multimodal_damage_data.json      # Damage assessment cases
│   └── dealer_issue_escalation.txt      # Customer service scenarios
├── mm_index/                      # Core multimodal indexing package
└── requirements.txt               # Python dependencies
```

## Troubleshooting

**AWS Credentials Not Found**
```bash
aws configure
# Or set environment variables:
export AWS_ACCESS_KEY_ID=your_access_key_here
export AWS_SECRET_ACCESS_KEY=your_secret_key_here

```

**Missing Data Files**
The required data files should already be present in the `data/` folder. If any are missing, please check the repository.

**Vector Bucket Not Found**
Run the simple demo first to create the necessary AWS resources:
```bash
uv run simple_demo.py
```



## What Each Demo Teaches

1. **Simple Demo**: Foundation of vector search - indexing, embedding generation, and semantic search. Available as both Python script and interactive Jupyter notebook.
2. **LangChain RAG**: Integrating vector search with popular AI frameworks for real applications. Jupyter notebook shows step-by-step RAG pipeline construction.
3. **Multimodal Demo**: Advanced AI processing combining text and images for damage assessment. Jupyter notebook displays actual damage photos and interactive search results.
4. **S3 Vector Browser**: Visual management interface for exploring and administering vector data with advanced search and content viewing capabilities

## Running Jupyter Notebooks

All demos now include Jupyter notebook versions optimized for data scientists and interactive exploration.

### First, ensure Jupyter is installed in your virtual environment:
```bash
# Make sure you're in the virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install/update requirements including Jupyter
uv pip install -r requirements.txt
```

### Then launch Jupyter Lab with the correct environment:
```bash
# Launch Jupyter Lab for any demo (use uv run to ensure correct environment)
# IMPORTANT: Run these commands from the main project directory (s3_vector/)
uv run jupyter lab simple_demo/simple_demo.ipynb
uv run jupyter lab langchain_demo/langchain_demo.ipynb  
uv run jupyter lab multimodal_patterns/multimodal_demo.ipynb

# Or start Jupyter Lab and navigate to the notebooks
uv run jupyter lab
```

### Troubleshooting Jupyter Issues:
If you get `ModuleNotFoundError` in Jupyter notebooks:

1. **Ensure you're using uv run**: Always launch Jupyter with `uv run jupyter lab`
2. **Reinstall requirements**: Run `uv pip install -r requirements.txt` 
3. **Check kernel**: In Jupyter, go to Kernel → Change Kernel → Select Python 3
4. **Restart kernel**: In Jupyter, go to Kernel → Restart Kernel
5. **For multimodal demo**: The notebook uses a `setup_imports.py` helper script to configure paths correctly

The notebooks provide:
- **Visual Analysis**: See actual damage photos and search results
- **Interactive Exploration**: Modify queries and parameters in real-time
- **Step-by-Step Learning**: Understand each component of the AI pipeline
- **Rich Documentation**: Detailed explanations and business context
- **Immediate Feedback**: Run cells individually to understand each step

This showcase provides a complete example of how vector search technology can transform automotive operations, from basic search to advanced multimodal processing, with programmatic APIs, visual management interfaces, and interactive learning environments.