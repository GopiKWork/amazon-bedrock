# Configuration constants for the RAG demo

# AWS Configuration
AWS_REGION = "us-west-2"
BEDROCK_MODEL_ID = "us.amazon.nova-pro-v1:0"

# Embedding Configuration
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# ChromaDB Configuration
CHROMA_DB_PATH = "./chroma_db"
COLLECTION_NAME = "car_manufacturing"

# Model Parameters
MAX_TOKENS = 1000
TEMPERATURE = 0.7
TOP_K_RESULTS = 3

# Sample Questions
SAMPLE_QUESTIONS = [
    "What should I do if my car engine overheats?",
    "How long is the warranty on brake pads?",
    "What are the recommended oil change intervals?",
    "How do I know if my transmission fluid needs changing?",
    "What are the signs of brake system problems?",
    "How often should I replace my air filter?",
    "What causes transmission fluid to leak?",
    "How do I maintain my vehicle's cooling system?"
]