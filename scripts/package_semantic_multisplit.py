#!/usr/bin/env python3
"""Package reviewed v2 splits with a shared seen-negative pool and provenance."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import zipfile
from collections import Counter
from pathlib import Path


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.open() if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        while block := f.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--selection", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--release-root", type=Path, required=True)
    parser.add_argument("--shared-action", type=Path, required=True)
    parser.add_argument("--shared-composition", type=Path, required=True)
    parser.add_argument("--source-train", type=Path, required=True)
    parser.add_argument("--source-test", type=Path, required=True)
    parser.add_argument("--video-archive", type=Path, required=True)
    args = parser.parse_args()
    frozen = json.loads((args.selection / "frozen_selection_manifest.json").read_text())
    if sha256(args.selection / "selection_rules.json") != frozen["selection_rules_sha256"] or \
            sha256(args.selection / "split_specs.json") != frozen["final_specs_sha256"]:
        raise ValueError("Frozen selection rules or split specs changed")
    specs = json.loads((args.selection / "split_specs.json").read_text())
    for spec in specs:
        if sha256(args.selection / f"{spec['id']}.json") != frozen["per_spec_sha256"][spec["id"]]:
            raise ValueError(f"Frozen split spec changed: {spec['id']}")
    feasibility = {r["id"]: r for r in json.loads((args.selection / "reviewed_feasibility.json").read_text())}
    shared = {"action": read_jsonl(args.shared_action),
              "composition": read_jsonl(args.shared_composition)}
    for axis, rows in shared.items():
        if not rows or any(r["partition"] != "S-" or
                           r["verification_status"] not in {"manual_video_review_confirmed", "user_attested_video_review"}
                           for r in rows):
            raise ValueError(f"Shared {axis} pool is empty or contains unreviewed negatives")
    with zipfile.ZipFile(args.video_archive) as archive:
        video_names = set(archive.namelist())
    summaries = []
    for spec in specs:
        split_id = spec["id"]
        if split_id not in feasibility or not feasibility[split_id]["passes_all_gates"]:
            raise ValueError(f"Reviewed quality gate failed or missing: {split_id}")
        work = args.work_root / split_id
        out = args.release_root / split_id
        if out.exists() and any(out.iterdir()):
            raise FileExistsError(f"Release directory already populated: {out}")
        train_reviewed = read_jsonl(work / "train_reviewed.jsonl")
        train_positive = [r for r in train_reviewed if r["partition"] == "S+"]
        train_negative_ids = {r["qid"] for r in train_reviewed if r["partition"] == "S-"}
        common = shared[spec["axis"]]
        if any(r["qid"] not in train_negative_ids for r in common):
            raise ValueError(f"Shared negative is not reviewed/eligible in {split_id}")
        train = train_positive + common
        val = read_jsonl(work / "val_reviewed.jsonl")
        test = read_jsonl(work / "test_reviewed.jsonl")
        quarantined = {}
        for name, rows in (("train", train), ("val", val), ("test", test)):
            quarantined[name] = [r["qid"] for r in rows if r["semantic_graph"]["action"] == "dress" and
                                 r["semantic_graph"]["object"] == "front"]
        train = [r for r in train if r["qid"] not in set(quarantined["train"])]
        val = [r for r in val if r["qid"] not in set(quarantined["val"])]
        test = [r for r in test if r["qid"] not in set(quarantined["test"])]
        if not all(Counter(r["partition"] for r in rows)[p] > 0 for rows, parts in
                   ((train, ("S+", "S-")), (val, ("S+", "S-"))) for p in parts):
            raise ValueError(f"Training or seen validation quadrant is empty in {split_id}")
        pairs = read_jsonl(work / "matched_u_pairs_reviewed.jsonl")
        test_by_qid = {r["qid"]: r for r in test}
        if len(test_by_qid) != len(test):
            raise ValueError(f"Duplicate test qid in {split_id}")
        for item in pairs:
            pos, neg = test_by_qid[item["positive_qid"]], test_by_qid[item["negative_qid"]]
            if pos["novelty_type"] != neg["novelty_type"] or pos["video_id"] != neg["video_id"]:
                raise ValueError(f"Invalid pair in {split_id}: {item['pair_id']}")
        all_rows = train + val + test
        if any(r["exist_label"] == 0 and r["verification_status"] not in
               {"manual_video_review_confirmed", "user_attested_video_review"}
               for r in all_rows):
            raise ValueError(f"Unreviewed negative in {split_id}")
        out.mkdir(parents=True)
        for name, rows in (("train.jsonl", train), ("val.jsonl", val), ("test.jsonl", test),
                           ("matched_u_pairs.jsonl", pairs),
                           ("test_matched_u.jsonl", [test_by_qid[qid] for p in pairs
                                                      for qid in (p["positive_qid"], p["negative_qid"])])):
            write_jsonl(out / name, rows)
        for name in ("semantic_inventory.json", "review_report.json", "split_spec_provenance.json"):
            shutil.copy2(work / name, out / name)
        (out / "statistics.json").write_text(json.dumps({
            "split_counts": {name: dict(Counter(r["partition"] for r in rows))
                             for name, rows in (("train", train), ("val", val), ("test", test))},
            "matched_u_pairs_reviewed": len(pairs),
            "shared_seen_train_negatives": len(common),
            "quarantined_parser_error_qids": quarantined,
            "quality_gates": feasibility[split_id],
        }, ensure_ascii=False, indent=2) + "\n")
        missing = sorted({r["video_id"] for r in all_rows
                          if f"Charades_v1_480/{r['video_id']}.mp4" not in video_names})
        manifest = {
            "split_id": split_id, "axis": spec["axis"],
            "input_sha256": {str(p.resolve()): sha256(p) for p in
                             (args.source_train, args.source_test, args.selection / f"{split_id}.json",
                              args.selection / "selection_rules.json",
                              args.shared_action if spec["axis"] == "action" else args.shared_composition)},
            "missing_release_videos_in_archive": missing,
            "release_sha256": {p.name: sha256(p) for p in out.iterdir() if p.is_file()},
        }
        (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
        (out / "HANDOFF.md").write_text(
            f"# {split_id} semantic existence v2\n\n"
            f"Held semantics: `{json.dumps(spec, ensure_ascii=False)}`. "
            "New negative rows use the dataset owner's attestation for the exact reviewed batch; "
            "no per-qid review log is available. Exact reused v1 rows retain their original batch-attestation provenance. "
            "See `review_report.json`, `statistics.json`, and `manifest.json` for provenance.\n")
        summaries.append({"id": split_id, "train": len(train), "val": len(val),
                          "test": len(test), "pairs": len(pairs), "missing_videos": len(missing)})
    print(json.dumps(summaries, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
