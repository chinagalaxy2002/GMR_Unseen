#!/usr/bin/env python3
"""Select another action pair after a first cohort fails candidate pair coverage."""

from __future__ import annotations

import argparse
import csv
import itertools
import json
from collections import defaultdict
from pathlib import Path

from select_semantic_split_specs import FAMILIES


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--selection", type=Path, required=True)
    parser.add_argument("--failed-spec", required=True)
    parser.add_argument("--id", default="A2_alt")
    args = parser.parse_args()
    if (args.selection / "frozen_selection_manifest.json").exists():
        raise SystemExit("Selection is frozen; create a new version instead of adding a fallback")
    original = json.loads((args.selection / "split_specs.json").read_text())
    failed = next(s for s in original if s["id"] == args.failed_spec)
    if failed["axis"] != "action":
        raise ValueError("Only action cohorts support this fallback")
    family = failed["selection_family"]
    actions = {r["semantic"]: r for r in csv.DictReader((args.selection / "action_candidates.csv").open())}
    pairs = list(csv.DictReader((args.selection / "composition_candidates.csv").open()))
    by_action = defaultdict(dict)
    for r in pairs:
        action, obj = r["semantic"].split("|", 1)
        by_action[action][obj] = int(r["test_positives"])
    eligible = []
    for action in FAMILIES[family]:
        r = actions.get(action)
        if r and int(r["train_positives"]) >= 100 and int(r["test_positives"]) >= 50 and \
                int(r["test_videos"]) >= 30 and int(r["distinct_objects"]) >= 10 and \
                float(r["top_object_share"]) <= 0.7:
            eligible.append(action)
    alternatives = []
    for left, right in itertools.combinations(eligible, 2):
        if {left, right} == set(failed["held_actions"]):
            continue
        counts = [int(actions[a]["test_positives"]) for a in (left, right)]
        total = sum(counts)
        if max(counts) / total > 0.7:
            continue
        shared_object_positives = sum(min(by_action[left].get(obj, 0), by_action[right].get(obj, 0))
                                      for obj in set(by_action[left]) & set(by_action[right]))
        alternatives.append((shared_object_positives, total, left, right))
    if not alternatives:
        raise SystemExit("No eligible action fallback")
    alternatives.sort(key=lambda x: (-x[0], -x[1], x[2], x[3]))
    score, total, left, right = alternatives[0]
    spec = {"schema_version": 1, "id": args.id, "axis": "action",
            "selection_family": family, "held_actions": sorted((left, right)),
            "held_compositions": [], "projected_test_positives": total,
            "shared_object_proxy": score, "fallback_for": args.failed_spec,
            "fallback_reason": "first cohort failed candidate matched-pair gate before model evaluation"}
    (args.selection / f"{args.id}.json").write_text(json.dumps(spec, indent=2, sort_keys=True) + "\n")
    (args.selection / "action_fallback_audit.json").write_text(json.dumps({
        "failed_spec": args.failed_spec, "selected": spec,
        "alternatives": [{"shared_object_proxy": a, "test_positives": b, "actions": [c, d]}
                         for a, b, c, d in alternatives],
    }, indent=2) + "\n")
    print(json.dumps(spec, indent=2))


if __name__ == "__main__":
    main()
