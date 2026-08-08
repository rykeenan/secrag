import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / "src"))
from retrieve import retrieve

GOLDEN = "eval/golden_set.json"

questions = json.load(open(GOLDEN, encoding="utf-8"))

for q in questions:
    if q["source"] is None:
        continue
    results = retrieve(q["question"], k=10)
    print(f"\nQ: {q['question'][:70]}")
    print(f"   recorded: {q['source']}#{q['chunk_id']}")
    for i, r in enumerate(results, start=1):
        if r["source"] == q["source"]:
            print(f"   [{i}] {r['source']}#{r['chunk_id']}  {r['text'][:80]}")