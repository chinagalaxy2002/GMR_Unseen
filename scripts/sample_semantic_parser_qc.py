#!/usr/bin/env python3
"""Sample held-out original positives for human semantic-parse review."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.open() if line.strip()]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--selection", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    specs = json.loads((args.selection / "split_specs.json").read_text())
    rules = json.loads((args.selection / "selection_rules.json").read_text())
    sampled = []
    for spec in specs:
        path = args.work_root / spec["id"] / "test_positives.jsonl"
        if not path.exists():
            continue
        groups = defaultdict(list)
        for row in read_jsonl(path):
            if row["partition"] != "U+":
                continue
            graph = row["semantic_graph"]
            semantic = graph["action"] if spec["axis"] == "action" else graph["action"] + "|" + graph["object"]
            groups[semantic].append(row)
        for semantic, rows in sorted(groups.items()):
            rows.sort(key=lambda r: hashlib.sha256(str(r["qid"]).encode()).hexdigest())
            for row in rows[:rules["parser_qc_sample_per_semantic"]]:
                graph = row["semantic_graph"]
                sampled.append({"split_id": spec["id"], "semantic": semantic,
                                "qid": row["qid"], "video_id": row["video_id"],
                                "query": row["query"], "parsed_action": graph["action"],
                                "parsed_object": graph["object"],
                                "object_role": graph["object_role"], "relation": graph["relation"],
                                "decision": "", "reviewer": "", "notes": ""})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists() and any(row.get("decision", "").strip() for row in
                                    csv.DictReader(args.output.open(newline=""))):
        raise FileExistsError("Parser QC template contains decisions; refusing to overwrite it")
    with args.output.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(sampled[0]) if sampled else [])
        if sampled:
            writer.writeheader()
            writer.writerows(sampled)
    print(json.dumps({"samples": len(sampled), "output": str(args.output)}, indent=2))


if __name__ == "__main__":
    main()
