#!/usr/bin/env python3
"""Find an identical seen-negative training pool across candidate split builds."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.open() if line.strip()]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--split-ids", nargs="+", required=True)
    parser.add_argument("--reviewed", action="store_true")
    parser.add_argument("--max-rows", type=int, help="Deterministic cap for the common pool")
    parser.add_argument("--allowed-qids-from", type=Path,
                        help="Restrict reviewed pool to previously selected candidate qids")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    negative_maps = {}
    positive_ids = {}
    for split_id in args.split_ids:
        rows = read_jsonl(args.work_root / split_id /
                          ("train_reviewed.jsonl" if args.reviewed else "train_candidates.jsonl"))
        positive_ids[split_id] = {r["qid"] for r in rows if r["partition"] == "S+"}
        negative_maps[split_id] = {r["qid"]: r for r in rows if r["partition"] == "S-"}
    common = set.intersection(*(set(m) for m in negative_maps.values()))
    common_sources = set.intersection(*positive_ids.values())
    allowed = ({r["qid"] for r in read_jsonl(args.allowed_qids_from)} if args.allowed_qids_from else None)
    records = []
    for qid in sorted(common):
        if allowed is not None and qid not in allowed:
            continue
        rows = [negative_maps[s][qid] for s in args.split_ids]
        if rows[0]["source_qid"] not in common_sources:
            continue
        fingerprint = ("video_id", "query", "source_qid", "exist_label")
        if any(tuple(r[k] for k in fingerprint) != tuple(rows[0][k] for k in fingerprint) for r in rows[1:]):
            raise ValueError(f"Shared qid has inconsistent content: {qid}")
        records.append(rows[0])
    eligible_count = len(records)
    if args.max_rows is not None:
        if args.max_rows <= 0:
            raise ValueError("--max-rows must be positive")
        records.sort(key=lambda r: hashlib.sha256(("3407|" + r["qid"]).encode()).hexdigest())
        records = records[:args.max_rows]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w") as f:
        for row in records:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    summary = {
        "split_ids": args.split_ids,
        "common_seen_negative_candidates": len(records),
        "eligible_common_seen_negative_candidates": eligible_count,
        "sampling_rule": "lowest SHA-256(3407|qid)" if args.max_rows is not None else "all eligible",
        "common_positive_sources": len(common_sources),
        "verification_status_counts": dict(Counter(r["verification_status"] for r in records)),
        "common_actions": dict(Counter(r["semantic_graph"]["action"] for r in records)),
        "common_objects": dict(Counter(r["semantic_graph"]["object"] for r in records)),
        "per_split": {},
    }
    for split_id in args.split_ids:
        all_negatives = list(negative_maps[split_id].values())
        summary["per_split"][split_id] = {
            "all_seen_negative_candidates": len(all_negatives),
            "outside_common_pool": len(all_negatives) - len(records),
            "actions": dict(Counter(r["semantic_graph"]["action"] for r in all_negatives)),
            "objects": dict(Counter(r["semantic_graph"]["object"] for r in all_negatives)),
        }
    args.output.with_suffix(".audit.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"split_ids": args.split_ids, "common_seen_negative_candidates": len(records),
                      "output": str(args.output)}, indent=2))


if __name__ == "__main__":
    main()
