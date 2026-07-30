import os 
from dotenv import load_dotenv                          # reads .env into environment
from anthropic import Anthropic
from retrieve import retrieve

load_dotenv()                                           # makes ANTHROPIC_API_KEY available

MODEL = "claude-haiku-4-5-20251001"                      # cheap, fast, fine for development

SYSTEM_PROMPT = """You are SecRAG, a security knowledge assistant. Answer questions using ONLY the provided context chunks. Rules:

1. Base every claim on the context. Do not use outside knowledge.
2. Cite the source after each claim, in brackets: [source, chunk N]
3. If the context does not contain the answer, say exactly:
    "I don't have enough information in my knowledge base to answer that."
    Do not guess. Do not answer from general knowledge.
4. Keep answers concise and factual."""

def build_context(hits):
    """Format retrieved chunks into a labeled context block."""
    parts = []
    for h in hits:
        parts.append(f"[{h['source']}, chunk {h['chunk_id']}]\n{h['text']}")
    return "\n\n---\n\n".join(parts)

def answer(query, k=8):
    """Retrieve relevant chunks, then ask Claude to answer from them."""
    hits = retrieve(query, k=k)
    context = build_context(hits)

    client = Anthropic()                # reads the API key automatically

    response = client.messages.create(
        model=MODEL,
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"Context chunks:\n\n{context}\n\nQuestion: {query}",
        }],
    )
    return response.content[0].text, hits


if __name__ == "__main__":
    import sys
    query = " ".join(sys.argv[1:]) or "What are the first steps in ransomware containment?"

    print(f"Question: {query}\n")
    text, hits = answer(query)
    print(text)
    print("\n--- Retrieved sources ---")
    for h in hits:
        print(f" {h['source']} chunk {h['chunk_id']} (distance {h['distance']})")