import chromadb             # local vector database
from sentence_transformers import SentenceTransformer  # embedding model
from ingest import ingest
from chunker import chunk_documents

MODEL_NAME = "all-MiniLM-L6-v2"
DB_PATH = "chroma_db"           # small, fast, runs locally
COLLECTION = "secrag"           # name of our chunk collection

def build_index():
    """Embed all chunks and store them in ChromaDB. Safe to re-run."""
    print("Loading embedding model (first run downloads ~90MB)...")
    model = SentenceTransformer(MODEL_NAME)

    client = chromadb.PersistentClient(path=DB_PATH)   # opens or creates the DB folder

    # Delete the old collection if its exists, so re-run start clean:
    try:
        client.delete_collection(COLLECTION)
    except Exception:
        pass                                # didn't exist yet -> fine

    collection = client.create_collection(COLLECTION, metadata={"hnsw:space": "cosine"})

    print("Ingesting and chunking documents...")
    docs = ingest()
    chunks = chunk_documents(docs)
    print(f"Embedding {len(chunks)} chunks...")

    texts = [c["text"] for c in chunks]         # just the text for every chunk
    ids = [f"{c['source']}_{c['chunk_id']}" for c in chunks]     # unique ID per chunk
    metadatas = [
        {"source": c["source"], "chunk_id": c["chunk_id"], "total_chunks": c["total_chunks"]}
        for c in chunks
    ]
    
    embeddings = model.encode(texts, show_progress_bar=True)    # text -> vectors

    collection.add(
        ids=ids,
        embeddings=embeddings.tolist(),
        documents=texts,
        metadatas=metadatas,
    )

    print(f"\nDone. Collection '{COLLECTION}' holds {collection.count()} chunks.")

if __name__ == "__main__":
    build_index()
