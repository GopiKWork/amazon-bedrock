import chromadb
from sentence_transformers import SentenceTransformer
import boto3
import json
import random
from config import (
    AWS_REGION, BEDROCK_MODEL_ID, EMBEDDING_MODEL_NAME, 
    CHROMA_DB_PATH, COLLECTION_NAME, MAX_TOKENS, TEMPERATURE, 
    TOP_K_RESULTS, SAMPLE_QUESTIONS
)

def connect_to_vector_store():
    # Initialize ChromaDB client with telemetry disabled
    settings = chromadb.config.Settings(
        anonymized_telemetry=False
    )
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH, settings=settings)
    collection = client.get_collection(name=COLLECTION_NAME)
    return collection

def retrieve_relevant_context(query, collection, model):
    # Generate embedding for the query
    query_embedding = model.encode([query])
    
    # Search for similar documents
    results = collection.query(
        query_embeddings=query_embedding.tolist(),
        n_results=TOP_K_RESULTS
    )
    
    # Format retrieved context and return both formatted and raw results
    context_docs = []
    retrieved_docs = []
    
    for i in range(len(results['documents'][0])):
        doc_text = results['documents'][0][i]
        metadata = results['metadatas'][0][i]
        
        # Store raw doc info for printing
        retrieved_docs.append({
            'title': metadata['title'],
            'category': metadata['category'],
            'content': doc_text[:200] + "..." if len(doc_text) > 200 else doc_text
        })
        
        # Format for context
        context_docs.append(f"Title: {metadata['title']}\nCategory: {metadata['category']}\nContent: {doc_text}")
    
    return "\n\n".join(context_docs), retrieved_docs

def query_bedrock_with_context(query, context):
    # Initialize Bedrock runtime client
    bedrock_runtime = boto3.client(
        service_name='bedrock-runtime',
        region_name=AWS_REGION
    )
    
    # Create system prompt
    system_prompt = """You are an expert automotive technician and customer service representative. 
    Use the provided context from car manufacturing documentation to answer questions accurately and helpfully. 
    Focus on practical advice and safety considerations. If the context doesn't contain relevant information, 
    say so clearly."""
    
    # Prepare the request body for Nova Pro
    request_body = {
        "messages": [
            {
                "role": "user",
                "content": [{"text": system_prompt}]
            },
            {
                "role": "user", 
                "content": [{"text": f"Context:\n{context}\n\nQuestion: {query}"}]
            }
        ],
        "inferenceConfig": {
            "maxTokens": MAX_TOKENS,
            "temperature": TEMPERATURE
        }
    }
    
    # Call Bedrock Nova Pro
    response = bedrock_runtime.invoke_model(
        modelId=BEDROCK_MODEL_ID,
        body=json.dumps(request_body)
    )
    
    # Parse response
    response_body = json.loads(response['body'].read())
    return response_body['output']['message']['content'][0]['text']

def run_rag_demo():
    # Initialize components
    collection = connect_to_vector_store()
    embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    
    # Choose a random question
    question = random.choice(SAMPLE_QUESTIONS)
    
    print("Custom RAG Demo with AWS Bedrock Nova Pro")
    
    # Retrieve relevant context and docs
    context, retrieved_docs = retrieve_relevant_context(question, collection, embedding_model)

    print("=" * 50)
    print(f"\nUser Question: {question}")
    print("=" * 50)

    
    # Print retrieved documents
    print("\nRetrieved Documents:")
    print("-" * 30)
    for i, doc in enumerate(retrieved_docs, 1):
        print(f"{i}. Title: {doc['title']}")
        print(f"   Category: {doc['category']}")
        print(f"   Content: {doc['content']}")
        print()
    
    # Query Bedrock with context
    response = query_bedrock_with_context(question, context)
    
    print("Final Response:")
    print("-" * 30)
    print(response)
    print("=" * 50)

if __name__ == "__main__":
    run_rag_demo()