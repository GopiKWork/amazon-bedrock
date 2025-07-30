import json
import chromadb
from sentence_transformers import SentenceTransformer
from config import EMBEDDING_MODEL_NAME, CHROMA_DB_PATH, COLLECTION_NAME

def load_car_data():
    with open('car_manufacturing_data.json', 'r') as file:
        data = json.load(file)
    return data['documents']

def create_vector_store():
    # Initialize ChromaDB client with telemetry disabled
    settings = chromadb.config.Settings(
        anonymized_telemetry=False
    )
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH, settings=settings)
    
    # Create or get collection
    collection = client.get_or_create_collection(name=COLLECTION_NAME)
    
    # Initialize sentence transformer model
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    
    # Load car manufacturing data
    documents = load_car_data()
    
    # Prepare data for ChromaDB
    texts = []
    metadatas = []
    ids = []
    
    for doc in documents:
        texts.append(doc['content'])
        metadatas.append({
            'title': doc['title'],
            'category': doc['category']
        })
        ids.append(doc['id'])
    
    # Generate embeddings
    embeddings = model.encode(texts)
    
    # Add documents to collection
    collection.add(
        embeddings=embeddings.tolist(),
        documents=texts,
        metadatas=metadatas,
        ids=ids
    )
    
    print(f"Successfully added {len(documents)} documents to ChromaDB")
    return collection

if __name__ == "__main__":
    create_vector_store()