# LangChain S3 Vector Store RAG Demo

This demo shows how to use the S3VectorStore with LangChain to create a Retrieval-Augmented Generation (RAG) pipeline using Amazon Bedrock Nova Pro model for automotive technical support.

## What This Demo Shows

**Automotive Use Case:**
- **Use Case**: AI-powered technical support system that can answer complex automotive questions
- **Business Value**: Provide instant, accurate technical guidance to service technicians and customers

**Technical Operations:**
- Integration with popular LangChain framework for building AI applications
- Custom S3VectorStore integration with LangChain's retrieval interface
- Retrieval-Augmented Generation (RAG) pattern implementation
- Connection to Amazon Bedrock Nova Pro for natural language responses
- Automotive technical knowledge base with inline sample documents

## Files

- `langchain_demo.ipynb` - Interactive Jupyter notebook with RAG implementation
- `langchain/langchain_s3_rag.py` - Python script version
- `config.py` - Configuration constants
- `utils.py` - Utility functions
- `requirements.txt` - Python dependencies

## Running the Demo

### Option 1: Python Script
```bash
uv run langchain_s3_rag.py
```

### Option 2: Jupyter Notebook (Recommended for Data Scientists)
```bash
# First ensure Jupyter is installed
uv pip install -r requirements.txt

# Then launch with uv run to use correct environment
uv run jupyter lab langchain_demo.ipynb
```

## What You'll See

The demo creates a technical knowledge base with automotive repair information and demonstrates:

- **Question**: "What causes starting issues in 2019 Honda Accord?"
- **Answer**: Detailed technical response including root cause analysis, repair procedures, parts requirements, and labor estimates

Sample automotive documents include:
- Honda Accord fuel injector problems
- BMW X3 brake pad replacement procedures
- Ford F-150 transmission issues
- Tesla Model 3 suspension problems
- Toyota Prius hybrid battery replacement

## Key Concepts Demonstrated

1. **RAG Pipeline**: Retrieval-Augmented Generation combining search with language generation
2. **LangChain Integration**: Using popular AI framework for production applications
3. **Document Retrieval**: Semantic search to find relevant technical documentation
4. **Context Augmentation**: Providing retrieved documents as context to the language model
5. **Bedrock Nova Integration**: Using AWS's advanced language model for responses
6. **Automotive Domain**: Specialized technical knowledge for automotive applications

## Technical Architecture

```
Question → Vector Search → Retrieve Docs → Augment Context → Generate Answer
    ↓           ↓              ↓              ↓              ↓
  "Honda      S3 Vector    Technical      Bedrock Nova    Detailed
  starting    Store        Documents      Pro Model       Technical
  issues"     Search       Retrieved      with Context    Response
```

## Prerequisites

- AWS credentials configured with S3 Vector and Bedrock permissions
- Access to Amazon Bedrock Nova Pro model
- LangChain packages installed
- Understanding of RAG concepts

## Sample Queries

The demo includes these automotive technical questions:
- Starting issues in Honda Accord
- Brake pad replacement procedures
- Transmission problem symptoms
- Hybrid battery replacement costs
- Suspension issue diagnostics

## Next Steps

After running this demo:
1. Add more automotive technical documents
2. Implement conversation memory for multi-turn interactions
3. Add metadata filtering for specific manufacturers or years
4. Create custom prompts for different technical scenarios
5. Build production-ready automotive support applications

## Benefits for Automotive Industry

- **Instant Technical Support**: Immediate access to repair procedures and diagnostics
- **Consistent Information**: Standardized responses based on official documentation
- **Scalable Knowledge**: Easy to update and expand technical knowledge base
- **Cost Reduction**: Reduce time spent searching for technical information
- **Training Support**: Help new technicians learn from documented expertise