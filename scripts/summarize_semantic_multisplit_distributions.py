#!/usr/bin/env python3
"""Summarize test query length and object/action composition by quadrant."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from statistics import mean, median


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.open() if line.strip()]


def summarize(rows: list[dict]) -> dict:
    lengths = [len(row["query"].split()) for row in rows]
    objects = Counter(row["semantic_graph"]["object"] for row in rows)
    actions = Counter(row["semantic_graph"]["action"] for row in rows)
    return {
        "n": len(rows),
        "query_word_count": {
            "mean": round(mean(lengths), 3) if lengths else None,
            "median": median(lengths) if lengths else None,
            "min": min(lengths) if lengths else None,
            "max": max(lengths) if lengths else None,
        },
        "distinct_objects": len(objects),
        "top_objects": [{"object": name, "n": count, "share": round(count / len(rows), 4)}
                        for name, count in objects.most_common(10)] if rows else [],
        "distinct_actions": len(actions),
        "top_actions": [{"action": name, "n": count, "share": round(count / len(rows), 4)}
                        for name, count in actions.most_common(10)] if rows else [],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--release-root", type=Path, required=True)
    parser.add_argument("--split-ids", nargs="+", default=["A1", "A2_alt", "A3", "C1", "C2_alt"])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = {}
    for split in args.split_ids:
        test = read_jsonl(args.release_root / split / "test.jsonl")
        result[split] = {part: summarize([row for row in test if row["partition"] == part])
                         for part in ("S+", "S-", "U+", "U-")}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({split: {part: stats[part]["n"] for part in stats} for split, stats in result.items()},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
