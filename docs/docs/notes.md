# SecRAG — Build Notes & Findings

## Architecture (the one-sentence version)
Question -> embed with all-MiniLM-L6-v2 -> ChromaDB finds nearest chunks (cosine distance)
-> chunks + strict system prompt -> Claude Haiku -> cited answer or honest refusal.

## Design decisions
- ~200-word chunks: embedding model truncates at ~256 tokens; bigger chunks would be half-invisible.
- 40-word overlap: ideas spanning a chunk boundary survive intact in one chunk.
- No LangChain/LlamaIndex: pipeline built by hand to understand every stage.
- Rebuild-from-scratch indexing (delete + recreate collection): idempotent, no duplicates.
- Cosine distance set explicitly (ChromaDB default is L2; caused a distance-scale surprise).
- API key in .env, gitignored; never in code (found: key leaks on GitHub get scraped in minutes).

## Errors faced & fixes (presentation gold)
1. Monster chunks (501 words) — text without sentence punctuation (tables/TOCs); fixed by hard-splitting oversized "sentences."
2. Chunk overshoot (369 words) — size checked AFTER adding sentence; fixed with close-before-overflow check.
3. Fragment chunks (4 words) — leftover slices; fixed with minimum-size filters (20 words).
4. TOC pollution in retrieval — dot-leader chunks outranked real content because TOCs repeat every keyword;
   fixed with regex line filter at ingestion + periods-per-word is_junk() chunk filter. Verified before/after.
5. DuplicateIDError from ChromaDB — malformed f-string quotes turned dict lookups into literal text.
6. 404 model not found — typo'd model name; proved API auth worked (else it'd be 401).

## Findings from testing
- Vocabulary mismatch: "containment" query retrieved reporting/detection chunks; rephrasing with the
  corpus's own vocabulary ("respond and recover") retrieved better. Known RAG failure mode.
  Mitigations: higher k (5->8), multi-phrasing eval questions, hybrid BM25+vector retrieval (future).
- Anti-hallucination guard verified: "capital of France" -> clean refusal, no invented answer.
- Distance bands: relevant hits ~0.54-0.94; irrelevant ~1.82-1.88. Future: refusal threshold ~1.2.

## Glossary (terms I can now use precisely)
embedding, vector database, semantic search, cosine distance, top-k retrieval, chunking, overlap,
grounding, hallucination, system prompt, idempotent, RAG.