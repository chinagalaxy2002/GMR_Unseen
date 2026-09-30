"""Read-only audit of exact-text crossed labels in frozen training releases."""
import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path


def audit(path):
    raw = path.read_bytes()
    rows = [json.loads(line) for line in raw.splitlines() if line.strip()]
    by_id = {r["qid"]: r for r in rows}
    labels = defaultdict(set)
    lookup = defaultdict(list)
    for row in rows:
        assert row["partition"] in ("S+", "S-")
        key = (row["query"], int(row["exist_label"]))
        lookup[key].append(row)
        labels[(row["vid"], row["query"])].add(int(row["exist_label"]))
    conflicts = [k for k, v in labels.items() if len(v) > 1]
    positive_sources = 0
    reference_sources = 0
    both_absent_sources = 0
    crossed_sources = 0
    source_texts = set()
    semantic_pairs = set()
    quartets = set()
    examples = []
    for neg in rows:
        if neg["exist_label"]:
            continue
        pos = by_id.get(neg.get("source_qid"))
        if not pos or not pos["exist_label"] or pos["vid"] != neg["vid"]:
            continue
        positive_sources += 1
        qa, qb, va = pos["query"], neg["query"], pos["vid"]
        refs = [r for r in lookup[(qa, 0)] if r["vid"] != va]
        if refs:
            reference_sources += 1
            source_texts.add(qa)
        if any(labels[(r["vid"], qb)] == {0} for r in refs):
            both_absent_sources += 1
        valid = [r for r in refs if labels[(r["vid"], qb)] == {1}]
        if valid:
            crossed_sources += 1
            semantic_pairs.add(tuple(sorted((qa, qb))))
        for ref in valid:
            vb = ref["vid"]
            if any(len(labels[(v, q)]) != 1 for v in (va, vb) for q in (qa, qb)):
                continue
            # Semantic/video cells, not annotation qids, define independent units here.
            unit = (tuple(sorted((va, vb))), tuple(sorted((qa, qb))))
            quartets.add(unit)
            if len(examples) < 3:
                pb = next(r for r in lookup[(qb, 1)] if r["vid"] == vb)
                examples.append({"positive_a_qid": pos["qid"], "negative_a_qid": neg["qid"],
                                 "negative_b_qid": ref["qid"], "positive_b_qid": pb["qid"]})
    return {
        "train_sha256": hashlib.sha256(raw).hexdigest(),
        "train_rows": len(rows),
        "negative_rows": sum(not r["exist_label"] for r in rows),
        "same_video_source_pairs": positive_sources,
        "pairs_with_positive_query_absent_in_other_video": reference_sources,
        "distinct_reference_source_texts": len(source_texts),
        "pairs_with_both_queries_absent_in_reference": both_absent_sources,
        "pairs_with_reversed_labels_in_other_video": crossed_sources,
        "distinct_crossed_query_pairs": len(semantic_pairs),
        "distinct_crossed_video_query_quartets": len(quartets),
        "conflicting_video_query_cells": len(conflicts),
        "example_qids": examples,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--release-root", default="data/release/semantic_existence_v2")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = {
        "method": "Exact query string equality; training S+/S- only; no semantic paraphrase matching",
        "scope": "Counts audit existing labels, not independent video verification or method performance",
        "splits": {s: audit(Path(args.release_root) / s / "train.jsonl")
                   for s in ("A1", "A2_alt", "A3", "C1", "C2_alt")},
    }
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    for split, data in result["splits"].items():
        print(split, {k: data[k] for k in ("same_video_source_pairs", "pairs_with_reversed_labels_in_other_video",
                                          "distinct_crossed_query_pairs", "distinct_crossed_video_query_quartets",
                                          "conflicting_video_query_cells")})
