#!/usr/bin/env python3
"""Check split, GMR fields, novelty labels, and source alignment."""

import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/processed/semantic_existence"


def load(name):
    return [json.loads(s) for s in (DATA / name).read_text().splitlines() if s]


def main():
    inventory = json.loads((DATA / "semantic_inventory.json").read_text())
    held_actions = set(inventory["heldout_actions"])
    held_pairs = set(inventory["heldout_compositions"])
    train_pairs = set(inventory["action_object_compositions"])
    splits = {s: load(f"{s}_candidates.jsonl") for s in ("train", "val", "test")}
    videos = defaultdict(set)
    qids = set()
    for split, rows in splits.items():
        for row in rows:
            videos[split].add(row["video_id"])
            assert row["qid"] not in qids, row["qid"]
            qids.add(row["qid"])
            assert row["exist_label"] == int(row["partition"].endswith("+")), row["qid"]
            assert bool(row["relevant_windows"]) == bool(row["exist_label"]), row["qid"]
            assert row["semantic_status"] == ("unseen" if row["partition"].startswith("U") else "seen"), row["qid"]
            graph = row["semantic_graph"]
            pair = f"{graph['action']}|{graph['object']}"
            if row["partition"].startswith("U"):
                assert graph["action"] in held_actions or pair in held_pairs, row["qid"]
            else:
                assert pair in train_pairs, row["qid"]
            if row["exist_label"] == 0:
                assert row["verification_status"] == "needs_video_review", row["qid"]
                assert row["query"].lower() != row["source_query"].lower(), row["qid"]
                assert row["semantic_edit_distance"] == 1, row["qid"]
    assert videos["train"].isdisjoint(videos["val"])
    assert videos["train"].isdisjoint(videos["test"])
    assert videos["val"].isdisjoint(videos["test"])
    train_pos = [r for r in splits["train"] if r["exist_label"]]
    assert all(r["semantic_graph"]["action"] not in held_actions for r in train_pos)
    assert all(f"{r['semantic_graph']['action']}|{r['semantic_graph']['object']}" not in held_pairs for r in train_pos)
    positives = {r["qid"]: r for r in splits["test"] if r["exist_label"]}
    negatives = {r["qid"]: r for r in splits["test"] if not r["exist_label"]}
    pairs = load("matched_u_pairs.jsonl")
    assert len({r["positive_qid"] for r in pairs}) == len(pairs)
    assert len({r["negative_qid"] for r in pairs}) == len(pairs)
    for item in pairs:
        pos = positives[item["positive_qid"]]
        neg = negatives[item["negative_qid"]]
        assert pos["partition"] == "U+" and neg["partition"] == "U-"
        assert pos["video_id"] == neg["video_id"]
        assert neg["source_qid"] == pos["qid"]
    print(json.dumps({"validated_rows": {k: len(v) for k, v in splits.items()},
                      "matched_u_pairs": len(pairs), "video_split_overlap": 0}, indent=2))


if __name__ == "__main__":
    main()
