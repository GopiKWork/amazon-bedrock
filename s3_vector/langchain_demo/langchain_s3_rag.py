#!/usr/bin/env python3
"""
LangChain S3 Vector Store RAG
============================

This script shows how to use the S3VectorStore with LangChain
to create a Retrieval-Augmented Generation (RAG) pipeline using
Amazon Bedrock Nova Pro model.

Features:
- Document ingestion into S3 vector store
- LangChain retriever creation from vector store
- RAG chain with Bedrock Nova Pro
- Automotive domain question answering

Usage:
    python langchain/langchain_s3_rag.py

Requirements:
    - AWS credentials configured
    - LangChain and LangChain AWS packages installed
    - Existing S3 vector bucket with automotive data
"""

import logging
import sys
import os

# Add project root directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# LangChain imports
try:
    from langchain_aws import ChatBedrock
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.runnables import RunnablePassthrough
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.documents import Document
except ImportError as e:
    print(f"Error importing LangChain packages: {e}")
    print("Please install required packages:")
    print("pip install langchain langchain-aws langchain-core")
    sys.exit(1)

# Project imports
from langchain_community.vectorstores import S3VectorStore
from config import REGION_NAME, NOVA_PRO_MODEL_ID, get_bucket_name
import boto3

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_sample_documents():
    """Create sample automotive documents for demonstration."""
    return [
        Document(
            page_content="The 2019 Honda Accord is equipped with a 1.5L turbocharged engine that may experience intermittent starting issues due to fuel injector problems. Common symptoms include rough idle, delayed starts, and occasional stalling. The repair typically involves cleaning or replacing fuel injectors and updating the ECU software.",
            metadata={
                "manufacturer": "Honda",
                "model": "Accord",
                "year": 2019,
                "issue_type": "engine",
                "severity": "medium"
            }
        ),
        Document(
            page_content="BMW X3 brake pad replacement requires specific OEM parts and proper bedding procedure. Front brake pads typically last 30,000-50,000 miles. Signs of wear include squealing, grinding, or reduced braking performance. Always replace pads in pairs and resurface or replace rotors if thickness is below specification.",
            metadata={
                "manufacturer": "BMW",
                "model": "X3",
                "issue_type": "brake",
                "severity": "low",
                "maintenance": True
            }
        ),
        Document(
            page_content="Ford F-150 transmission problems often manifest as shuddering during acceleration, especially in 2018 models. This is commonly caused by torque converter issues or transmission fluid contamination. Repair involves transmission fluid flush, torque converter replacement, and software updates. Labor time is typically 8-12 hours.",
            metadata={
                "manufacturer": "Ford",
                "model": "F-150",
                "year": 2018,
                "issue_type": "transmission",
                "severity": "high"
            }
        ),
        Document(
            page_content="Tesla Model 3 suspension issues in 2021 models include premature wear of control arm bushings and shock absorber mounts. Symptoms include clunking noises over bumps and uneven tire wear. Tesla has issued service bulletins for these components and extended warranty coverage for affected vehicles.",
            metadata={
                "manufacturer": "Tesla",
                "model": "Model 3",
                "year": 2021,
                "issue_type": "suspension",
                "severity": "medium",
                "warranty_covered": True
            }
        ),
        Document(
            page_content="Toyota Prius hybrid battery replacement on 2017 models requires specialized tools and safety procedures. The high-voltage battery typically lasts 8-10 years or 100,000-150,000 miles. Symptoms of battery failure include reduced fuel economy, warning lights, and inability to start in electric mode. Replacement cost ranges from $3,000-$4,500 including labor.",
            metadata={
                "manufacturer": "Toyota",
                "model": "Prius",
                "year": 2017,
                "issue_type": "electrical",
                "component": "hybrid_battery",
                "severity": "high"
            }
        )
    ]


def setup_vector_store():
    """Set up the S3 vector store with sample data."""
    try:
        logger.info("Setting up S3 vector store...")
        
        # Get bucket name
        sts_client = boto3.client('sts', region_name=REGION_NAME)
        account_id = sts_client.get_caller_identity()['Account']
        bucket_name = get_bucket_name(account_id)
        
        # Create sample documents
        sample_docs = create_sample_documents()
        
        # Create vector store from documents
        vector_store = S3VectorStore.from_documents(
            documents=sample_docs,
            bucket_name=bucket_name,
            index_name="langchain-demo-index"
        )
        
        logger.info(f"Successfully created vector store with {len(sample_docs)} documents")
        return vector_store
        
    except Exception as e:
        logger.error(f"Failed to setup vector store: {e}")
        raise


def create_rag_chain(vector_store):
    """Create a RAG chain using the vector store and Bedrock Nova."""
    try:
        logger.info("Creating RAG chain with Bedrock Nova...")
        
        # Create retriever from vector store
        retriever = vector_store.as_retriever(
            search_kwargs={"k": 3}  # Retrieve top 3 most relevant documents
        )
        
        # Initialize Bedrock Nova model
        llm = ChatBedrock(
            model_id=NOVA_PRO_MODEL_ID,
            region_name=REGION_NAME,
            model_kwargs={
                "inferenceConfig": {
                    "maxTokens": 1000,
                    "temperature": 0.3,
                    "topP": 0.9
                }
            }
        )
        
        # Create prompt template
        prompt = ChatPromptTemplate.from_template("""
You are an expert automotive technical advisor. Use the following context to answer the question accurately and professionally.

Context:
{context}

Question: {question}

Provide a detailed technical answer based on the context. Include specific information about:
- Root cause analysis
- Repair procedures
- Parts requirements
- Labor estimates
- Warranty considerations (if applicable)

Answer:""")
        
        # Create the RAG chain
        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)
        
        rag_chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )
        
        logger.info("Successfully created RAG chain")
        return rag_chain
        
    except Exception as e:
        logger.error(f"Failed to create RAG chain: {e}")
        raise


def run_sample_queries(rag_chain):
    """Run sample queries through the RAG chain."""
    
    sample_queries = [
        "What causes starting issues in 2019 Honda Accord?",
        "How do I replace brake pads on a BMW X3?",
        "What are the symptoms of Ford F-150 transmission problems?",
        "How much does it cost to replace a Toyota Prius hybrid battery?",
        "What suspension issues affect Tesla Model 3?"
    ]
    
    print("\nLangChain S3 Vector Store RAG")
    print("Using Amazon Bedrock Nova Pro with S3 vector retrieval")
    
    for i, query in enumerate(sample_queries, 1):
        print(f"\n{i}. Query: {query}")
        print("-" * 60)
        
        try:
            # Get response from RAG chain
            response = rag_chain.invoke(query)
            print(f"Response:\n{response}")
            
        except Exception as e:
            print(f"Error processing query: {e}")
        
        print("-" * 60)


def main():
    """Main function to run the LangChain S3 RAG."""
    try:
        print("Initializing LangChain S3 Vector Store RAG...")
        
        # Setup vector store
        vector_store = setup_vector_store()
        
        # Create RAG chain
        rag_chain = create_rag_chain(vector_store)
        
        # Run sample queries
        run_sample_queries(rag_chain)
        
        print("\nRAG processing completed successfully!")
        
        return True
        
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        print(f"\nProcessing failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    
    if not success:
        sys.exit(1)