import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / "src"))   # let us import from src/
from retrieve import retrieve

K = 8                                    # how many chunks retrieval returns


def evaluate(golden_path="eval/golden_set.json", k=K):
    questions = json.load(open(golden_path, encoding="utf-8"))

    answerable = [q for q in questions if q["source"] is not None]
    refusals   = [q for q in questions if q["source"] is None]

    hits = 0
    reciprocal_ranks = []
    rows = []

    for q in answerable:
        results = retrieve(q["question"], k=k)

        if q["source"] == results[0]["source"]:
            found = any(q["text_start"] in r["text"] for r in results if r["source"] == q["source"])
            if not found:
                print(f"\nFINGERPRINT MISS: {q['question'][:50]}")
                print(f"  looking for: {q['text_start']!r}")
                for r in results:
                    if r["source"] == q["source"]:
                        print(f"  chunk #{r['chunk_id']}: {r['text'][:120]!r}")

        rank = None                       # position of the golden chunk, if found
        for i, r in enumerate(results, start=1):
            ...

        rank = None                       # position of the golden chunk, if found
        for i, r in enumerate(results, start=1):
            if r["source"] == q["source"] and q["text_start"] in r["text"]:
                rank = i
                break

        if rank:
            hits += 1
            reciprocal_ranks.append(1 / rank)
        else:
            reciprocal_ranks.append(0)

        rows.append({
            "question": q["question"],
            "expected": f"{q['source']}#{q['chunk_id']}",
            "rank": rank,
            "top_hit": f"{results[0]['source']}#{results[0]['chunk_id']}",
            "top_distance": results[0]["distance"],
        })

    hit_rate = hits / len(answerable)
    mrr = sum(reciprocal_ranks) / len(answerable)

    print(f"\n{'='*70}")
    print(f"Questions: {len(answerable)} answerable, {len(refusals)} refusal tests")
    print(f"Hit rate@{k}: {hit_rate:.1%}   ({hits}/{len(answerable)})")
    print(f"MRR:         {mrr:.3f}")
    print(f"{'='*70}\n")

    print(f"{'rank':<6}{'expected':<32}{'top hit':<32}{'question'}")
    for r in sorted(rows, key=lambda x: (x["rank"] is None, x["rank"] or 0)):
        rank_str = str(r["rank"]) if r["rank"] else "MISS"
        print(f"{rank_str:<6}{r['expected']:<32}{r['top_hit']:<32}{r['question'][:50]}")

    return hit_rate, mrr, rows


if __name__ == "__main__":
    evaluate()