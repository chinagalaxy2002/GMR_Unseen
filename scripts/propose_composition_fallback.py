#!/usr/bin/env python3
"""Propose a composition cohort when a first cohort fails candidate pair coverage."""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

from build_semantic_existence import ACTION_NEIGHBORS


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--selection", type=Path, required=True)
    parser.add_argument("--failed-spec", required=True)
    parser.add_argument("--id", default="C2_alt")
    args = parser.parse_args()
    if (args.selection / "frozen_selection_manifest.json").exists():
        raise SystemExit("Selection is frozen; create a new version instead of adding a fallback")
    initial = json.loads((args.selection / "split_specs.json").read_text())
    failed = next(s for s in initial if s["id"] == args.failed_spec)
    if failed["axis"] != "composition":
        raise ValueError("Only composition cohorts support this fallback")
    excluded_actions = {p.split("|", 1)[0] for s in initial if s["axis"] == "composition"
                        for p in s["held_compositions"]}
    candidates = {r["semantic"]: r for r in csv.DictReader((args.selection / "composition_candidates.csv").open())}
    by_pair = defaultdict(list)
    for action, neighbors in ACTION_NEIGHBORS.items():
        if action in excluded_actions:
            continue
        for neighbor in neighbors:
            if neighbor in excluded_actions or action >= neighbor:
                continue
            objects = sorted({key.split("|", 1)[1] for key in candidates if key.startswith(action + "|")}
                             & {key.split("|", 1)[1] for key in candidates if key.startswith(neighbor + "|")})
            for obj in objects:
                left, right = (candidates[f"{a}|{obj}"] for a in (action, neighbor))
                if all(8 <= int(r["test_positives"]) <= 60 and int(r["train_positives"]) >= 15 and
                       int(r["remaining_train_object_positives"]) >= 10 for r in (left, right)):
                    by_pair[(action, neighbor)].append((int(left["test_positives"]) +
                                                          int(right["test_positives"]), obj))
    possibilities = []
    for (left, right), objects in by_pair.items():
        objects.sort(reverse=True)
        if len(objects) < 2:
            continue
        chosen = objects[:2]
        held = sorted(f"{action}|{obj}" for _, obj in chosen for action in (left, right))
        counts = [int(candidates[p]["test_positives"]) for p in held]
        total = sum(counts)
        if total >= 80 and max(counts) / total <= 0.65:
            possibilities.append((total, left, right, held))
    if not possibilities:
        raise SystemExit("No eligible fallback cohort")
    possibilities.sort(key=lambda x: (-x[0], x[1], x[2]))
    total, left, right, held = possibilities[0]
    spec = {"schema_version": 1, "id": args.id, "axis": "composition",
            "selection_family": f"{left}+{right}", "held_actions": [],
            "held_compositions": held, "projected_test_positives": total,
            "fallback_for": args.failed_spec,
            "fallback_reason": "first cohort failed candidate matched-pair gate before model evaluation"}
    (args.selection / f"{args.id}.json").write_text(json.dumps(spec, indent=2, sort_keys=True) + "\n")
    (args.selection / "composition_fallback_audit.json").write_text(json.dumps({
        "failed_spec": args.failed_spec, "selected": spec,
        "eligible_alternatives": [{"test_positives": t, "actions": [a, b], "held": h}
                                  for t, a, b, h in possibilities],
    }, indent=2) + "\n")
    print(json.dumps(spec, indent=2))


if __name__ == "__main__":
    main()
