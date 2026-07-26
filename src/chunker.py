import re                           # sentence splitting
from ingest import ingest           # reuse our ingestion module


def split_sentences(text):
    """Split text into sentences (simple punctuation-based rule)."""
    # Split wherever . ! or ? is followed by whitespace.
    # Not perfect ("e.g. foo" splits wrongly) but good enough, and simple.
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return  [s.strip() for s in sentences if s.strip()]   # drop empties

def chunk_text(text, target_words=200, overlap_words=40):
    """Group sentences into ~target_words chunks with overlap between them."""
    sentences = split_sentences(text)
    chunks = []
    current = []              # sentences in the chunk being built
    count = 0                 # word count of the chunk being built

    for sentence in sentences:
        words = len(sentence.split())

        if words > target_words:                 # pathological "sentence"
            if current:                          # close the chunk in progress
                chunks.append(" ".join(current))
                current, count = [], 0
            pieces = sentence.split()            # hard-split the monster
            for start in range(0, len(pieces), target_words):
                piece = pieces[start:start + target_words]
                if len(piece) >= 20:             # skip tiny leftover slices
                    chunks.append(" ".join(piece))
            continue                             # skip normal handling

        # FIX 1: close-before-overflow — check BEFORE adding the sentence
        if current and count + words > target_words:
            chunks.append(" ".join(current))     # close the full chunk
            tail = []                            # build the overlap tail
            tail_count = 0
            for s in reversed(current):
                tail_count += len(s.split())
                tail.insert(0, s)
                if tail_count >= overlap_words:
                    break
            current = tail
            count = tail_count

        current.append(sentence)                 # always: add the sentence
        count += words

    # FIX 2: keep the leftover only if it's substantial
    if current and count >= 20:
        chunks.append(" ".join(current))
    return chunks

def chunk_documents(docs):
    """Turn document dictrs into chunk dicts with citation metadata."""
    all_chunks = []
    for doc in docs:
        pieces = chunk_text(doc["text"])
        for i, piece in enumerate(pieces):          # i = 0, 1, 2, ... per document
            all_chunks.append({
                "source": doc["source"],
                "chunk_id": i,
                "total_chunks": len(pieces),
                "text": piece,
            })
    return all_chunks

if __name__ == "__main__":
    docs = ingest()
    chunks = chunk_documents(docs)

    biggest = max(chunks, key=lambda c: len(c["text"].split()))
    print(f"\n--- Biggest chunk: {biggest['source']}, chunk {biggest['chunk_id']} ---")
    print(biggest["text"][:600])

    print(f"\n{len(docs)} documents -> {len(chunks)} chunks\n")

    sizes = [len(c["text"].split()) for c in chunks]        # word count per chunk
    print(f"words/chunk min: {min(sizes)} max: {max(sizes)} avg: {sum(sizes)//len(sizes)}")

    print("\n--- Sample chunk (nist_sp_800_61, chunk 10) ---")
    for c in chunks:
        if c["source"] == "nist_sp_800_61" and c["chunk_id"] == 10:
            print(c["text"])
