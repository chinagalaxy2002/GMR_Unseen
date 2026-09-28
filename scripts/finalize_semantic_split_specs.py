#!/usr/bin/env python3
"""Freeze feasibility-based replacements before any model test predictions."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--selection", type=Path, required=True)
    parser.add_argument("--replace", action="append", default=[], metavar="FAILED=FALLBACK")
    args = parser.parse_args()
    root = args.selection
    if (root / "frozen_selection_manifest.json").exists():
        raise SystemExit("Selection is already frozen; create a new version for revisions")
    initial_path = root / "split_specs.initial.json"
    trial_path = root / "candidate_feasibility.initial.json"
    if not initial_path.exists() or not trial_path.exists():
        raise FileNotFoundError("Initial split specs and initial candidate feasibility audit are required")
    initial = json.loads(initial_path.read_text())
    trial = {r["id"]: r for r in json.loads(trial_path.read_text())}
    replacements = dict(item.split("=", 1) for item in args.replace)
    if len(replacements) != len(args.replace):
        raise ValueError("Duplicate replacement IDs")
    final = []
    for spec in initial:
        if spec["id"] in replacements:
            if trial[spec["id"]]["passes_all_gates"]:
                raise ValueError(f"Cannot replace an initially passing split: {spec['id']}")
            fallback = json.loads((root / f"{replacements[spec['id']]}.json").read_text())
            if fallback.get("fallback_for") != spec["id"] or fallback["axis"] != spec["axis"]:
                raise ValueError(f"Fallback lineage or axis mismatch: {spec['id']}")
            final.append(fallback)
        else:
            if not trial[spec["id"]]["passes_all_gates"]:
                raise ValueError(f"Failed initial split requires a recorded replacement: {spec['id']}")
            final.append(spec)
    if set(replacements) - {s["id"] for s in initial}:
        raise ValueError("Unknown initial split in replacement")
    if len({s["id"] for s in final}) != len(final):
        raise ValueError("Duplicate final split ID")
    final_path = root / "split_specs.json"
    final_path.write_text(json.dumps(final, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    manifest = {"phase": "frozen_before_model_results", "replacements": replacements,
                "selection_rules_sha256": sha256(root / "selection_rules.json"),
                "initial_specs_sha256": sha256(initial_path),
                "initial_candidate_feasibility_sha256": sha256(trial_path),
                "final_specs_sha256": sha256(final_path),
                "per_spec_sha256": {s["id"]: sha256(root / f"{s['id']}.json") for s in final}}
    (root / "frozen_selection_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"final_ids": [s["id"] for s in final], "replacements": replacements,
                      "manifest": str(root / 'frozen_selection_manifest.json')}, indent=2))


if __name__ == "__main__":
    main()
