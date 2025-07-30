from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import boto3
import json
import random
from config import (
    AWS_REGION, BEDROCK_MODEL_ID, EMBEDDING_MODEL_NAME, 
    CHROMA_DB_PATH, COLLECTION_NAME, MAX_TOKENS, TEMPERATURE, 
    TOP_K_RESULTS, SAMPLE_QUESTIONS
)

# Custom Bedrock LLM class that works with LangChain
class BedrockNovaLLM:
    def __init__(self):
        self.client = boto3.client('bedrock-runtime', region_name=AWS_REGION)
        self.model_id = BEDROCK_MODEL_ID
    
    def invoke(self, prompt: str) -> str:
        request_body = {
            "messages": [
                {
                    "role": "user",
                    "content": [{"text": prompt}]
                }
            ],
            "inferenceConfig": {
                "maxTokens": MAX_TOKENS,
                "temperature": TEMPERATURE
            }
        }
        
        response = self.client.invoke_model(
            modelId=self.model_id,
            body=json.dumps(request_body)
        )
        
        response_body = json.loads(response['body'].read())
        return response_body['output']['message']['content'][0]['text']

def setup_langchain_rag():
    # Initialize embeddings
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    
    # Connect to existing ChromaDB using LangChain Chroma
    vectorstore = Chroma(
        persist_directory=CHROMA_DB_PATH,
        embedding_function=embeddings,
        collection_name=COLLECTION_NAME
    )
    
    # Create retriever from vectorstore
    retriever = vectorstore.as_retriever(search_kwargs={"k": TOP_K_RESULTS})
    
    # Initialize Bedrock LLM
    llm = BedrockNovaLLM()
    
    # Create prompt template
    template = """You are an expert automotive technician and customer service representative.
Use the provided context from car manufacturing documentation to answer questions accurately and helpfully.
Focus on practical advice and safety considerations. If the context doesn't contain relevant information,
say so clearly.

Context: {context}

Question: {question}

Answer:"""
    
    prompt = PromptTemplate.from_template(template)
    
    # Format documents function
    def format_docs(docs):
        formatted = []
        for doc in docs:
            metadata = doc.metadata
            content = doc.page_content
            formatted.append(f"Title: {metadata.get('title', 'N/A')}\nCategory: {metadata.get('category', 'N/A')}\nContent: {content}")
        return "\n\n".join(formatted)
    
    # Create RAG chain using LangChain pipe operators
    rag_chain = (
        {
            "context": retriever | RunnableLambda(format_docs),
            "question": RunnablePassthrough()
        }
        | prompt
        | RunnableLambda(lambda x: llm.invoke(x.text))
    )
    
    return rag_chain

def run_langchain_rag_demo():
    # Setup components for showing retrieved docs
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    vectorstore = Chroma(
        persist_directory=CHROMA_DB_PATH,
        embedding_function=embeddings,
        collection_name=COLLECTION_NAME
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": TOP_K_RESULTS})
    
    # Setup RAG chain
    rag_chain = setup_langchain_rag()
    
    # Choose a random question
    question = random.choice(SAMPLE_QUESTIONS)
    
    print("LangChain RAG Demo with Pipe Operators and AWS Bedrock Nova Pro")
    print("=" * 65)
    print(f"\nUser Question: {question}")
    print("=" * 65)
    
    # Retrieve and show documents
    retrieved_docs = retriever.invoke(question)
    print("\nRetrieved Documents:")
    print("-" * 30)
    for i, doc in enumerate(retrieved_docs, 1):
        content_preview = doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
        print(f"{i}. Title: {doc.metadata.get('title', 'N/A')}")
        print(f"   Category: {doc.metadata.get('category', 'N/A')}")
        print(f"   Content: {content_preview}")
        print()
    
    # Use the RAG chain with LangChain pipe operators
    response = rag_chain.invoke(question)
    
    print("Final Response:")
    print("-" * 30)
    print(response)
    print("=" * 65)

if __name__ == "__main__":
    run_langchain_rag_demo()