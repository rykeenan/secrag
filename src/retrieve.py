import chromadb
from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"
DB_PATH = "chroma_db"
COLLECTION = "secrag"


def retrieve(query, k=5):
    """Return the k chunks most similar in meaning to the query."""
    model = SentenceTransformer(MODEL_NAME)
    client = chromadb.PersistentClient(path=DB_PATH)
    collection = client.get_collection(COLLECTION)

    query_vector = model.encode([query]).tolist()       # embed the question

    results = collection.query(
        query_embeddings=query_vector,
        n_results=k,
    )

    # ChromaDB returns parallel lists: zip them into one dict per hit:
    hits = []
    for text, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        hits.append({
            "source": meta["source"],
            "chunk_id": meta["chunk_id"],
            "distance": round(dist, 3),         # lower = more similar
            "text": text,
        })
    return hits

if __name__ == "__main__":
    import sys
    query = " ".join(sys.argv[1:]) or "What are the first steps in ransomware containment?"

    print(f"Query: {query}\n")
    for i, hit in enumerate(retrieve(query), start=1):
        print(f"--- Hit {i}: {hit['source']} (chunk {hit['chunk_id']}, distance {hit['distance']}) ---")
        print(hit["text"][:600])
        print()