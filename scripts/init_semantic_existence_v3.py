#!/usr/bin/env python3
"""Initialize the resumable Semantic Existence v3 construction workspace."""

from __future__ import annotations

import json
import random
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "data/processed/semantic_existence_v3"
DOC_PROGRESS = ROOT / "docs/semantic_existence_v3_construction/progress.json"
GROUPS = ("A1", "A2_alt", "A3", "C1", "C2_alt")
SPLITS = ("train", "val", "test")
RAW_ROOT = ROOT.parent / "data/raw/charades_sta"
RAW_FILES = {
    "train": RAW_ROOT / "charades_pos_train.jsonl",
    "test": RAW_ROOT / "charades_pos_test.jsonl",
}


def read_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    temp.replace(path)


def atomic_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)


def main() -> None:
    all_positive: dict[str, dict] = {}
    positives_by_video: dict[str, list[dict]] = defaultdict(list)
    raw_counts = {}
    for split, path in RAW_FILES.items():
        rows = read_jsonl(path)
        raw_counts[split] = len(rows)
        for row in rows:
            qid = row["qid"]
            if qid in all_positive and all_positive[qid] != row:
                raise ValueError(f"Conflicting raw positive qid: {qid}")
            all_positive[qid] = row
            positives_by_video[row["vid"]].append(row)

    candidates: dict[str, dict] = {}
    memberships: dict[str, list[dict]] = defaultdict(list)
    video_assignments: dict[str, set[str]] = defaultdict(set)
    old_occurrences = 0
    for group in GROUPS:
        for split in SPLITS:
            path = ROOT / f"data/release/semantic_existence_v2/{group}/{split}.jsonl"
            for row in read_jsonl(path):
                video_assignments[row["vid"]].add(split)
                if row.get("exist_label") != 0:
                    continue
                old_occurrences += 1
                qid = row["qid"]
                identity = {key: row.get(key) for key in (
                    "qid", "source_qid", "vid", "query", "source_query", "source_windows", "duration",
                    "construction_type", "source_split",
                )}
                if qid in candidates and candidates[qid]["identity"] != identity:
                    raise ValueError(f"Conflicting candidate qid across releases: {qid}")
                if qid not in candidates:
                    source = all_positive.get(row["source_qid"])
                    if source is None:
                        raise ValueError(f"Missing source GT {row['source_qid']} for {qid}")
                    if (row["vid"] != source["vid"] or
                        row["source_windows"] != source["relevant_windows"] or
                        row["source_query"] != source["query"] or
                        row["duration"] != source["duration"]):
                        raise ValueError(f"Source GT mismatch for {qid}")
                    candidates[qid] = {
                        "candidate_qid": qid,
                        "source_qid": row["source_qid"],
                        "vid": row["vid"],
                        "source_query": source["query"],
                        "candidate_query": row["query"],
                        "source_windows": source["relevant_windows"],
                        "duration": source["duration"],
                        "source_split": row.get("source_split"),
                        "construction_type": row.get("construction_type"),
                        "source_positive": source,
                        "identity": identity,
                    }
                memberships[qid].append({"group": group, "split": split, "partition": row["partition"]})

    seed_rows = read_jsonl(ROOT / "docs/semantic_existence_v3_construction/known_exclusions.jsonl")
    if len(seed_rows) != 13 or len({r["candidate_qid"] for r in seed_rows}) != 13:
        raise ValueError("Expected exactly 13 unique seed exclusions")
    seed_ids = {r["candidate_qid"] for r in seed_rows}
    if not seed_ids <= candidates.keys():
        raise ValueError(f"Seed exclusions absent from candidates: {sorted(seed_ids - candidates.keys())}")

    # Every video must have one consistent v2 split assignment.
    bad_videos = {vid: sorted(splits) for vid, splits in video_assignments.items() if len(splits) != 1}
    if bad_videos:
        raise ValueError(f"Video has inconsistent v2 split assignments: {list(bad_videos.items())[:5]}")
    video_split = {vid: next(iter(splits)) for vid, splits in video_assignments.items()}
    raw_train_videos = {r["vid"] for r in all_positive.values() if r["qid"].startswith("train")}
    unassigned = sorted(raw_train_videos - video_split.keys())
    random.Random(3407).shuffle(unassigned)
    val_count = round(len(unassigned) * 0.1)
    for i, vid in enumerate(unassigned):
        video_split[vid] = "val" if i < val_count else "train"
    for row in all_positive.values():
        if row["qid"].startswith("test"):
            previous = video_split.get(row["vid"])
            if previous not in (None, "test"):
                raise ValueError(f"Raw test video has non-test v2 assignment: {row['vid']}={previous}")
            video_split[row["vid"]] = "test"

    for subdir in ("inputs", "legacy", "review", "review/batches", "positives", "ontology", "master", "selection", "generation"):
        (WORK / subdir).mkdir(parents=True, exist_ok=True)
    candidate_rows = []
    for qid, row in sorted(candidates.items()):
        row.pop("identity")
        row["memberships"] = memberships[qid]
        candidate_rows.append(row)
    write_jsonl(WORK / "legacy/candidates.jsonl", candidate_rows)
    write_jsonl(WORK / "legacy/memberships.jsonl", [
        {"candidate_qid": qid, **member}
        for qid in sorted(memberships) for member in memberships[qid]
    ])
    write_jsonl(WORK / "review/pending.jsonl", [r for r in candidate_rows if r["candidate_qid"] not in seed_ids])
    write_jsonl(WORK / "review/decisions.jsonl", seed_rows)
    write_jsonl(WORK / "review/quarantine.jsonl", [])
    write_jsonl(WORK / "positives/raw.jsonl", sorted(all_positive.values(), key=lambda r: r["qid"]))
    write_jsonl(WORK / "inputs/video_splits.jsonl", [
        {"vid": vid, "split": split, "assignment_source": "v2_existing" if vid in video_assignments else "seed_3407_unassigned_train"}
        for vid, split in sorted(video_split.items())
    ])
    inventory = json.loads((ROOT / "docs/semantic_existence_v3_construction/input_inventory.json").read_text(encoding="utf-8"))
    atomic_json(WORK / "inputs/inventory.json", inventory)
    now = datetime.now(timezone.utc).isoformat()
    state = {
        "schema_version": 1, "updated_at": now, "state": "P0_complete",
        "protocol": "docs/semantic_existence_v3_construction/protocol.json",
        "legacy_negative_unique_qids": len(candidates),
        "legacy_negative_occurrences": old_occurrences,
        "seed_exclusions_imported": len(seed_ids),
        "legacy_decisions_finalized": len(seed_ids),
        "legacy_pending": len(candidates) - len(seed_ids),
        "positive_rows": len(all_positive),
        "positive_unique_queries": len({r["query"] for r in all_positive.values()}),
        "video_assignments": len(video_split),
        "unassigned_train_videos": len(unassigned),
        "unassigned_train_validation_videos": val_count,
        "next_stage": "P1_positive_event_normalization",
        "last_batch": {"candidate_qids": sorted(seed_ids), "decisions": {"exclude": len(seed_ids)}, "artifacts": ["review/decisions.jsonl"]},
        "open_issues": [],
    }
    atomic_json(WORK / "state.json", state)
    atomic_json(DOC_PROGRESS, {
        "schema_version": 1, "updated_at": now, "state": "P0_complete",
        "plan": "docs/20261009_SEMANTIC_EXISTENCE_V3_DATA_CONSTRUCTION_PLAN.md",
        "completed": ["v2_bounded_audit", "construction_plan_and_startup_artifacts", "13_known_equivalent_negatives_marked_exclude_in_seed_ledger", "P0_inputs_verified_queue_initialized_seed_decisions_imported"],
        "not_completed": ["full_positive_event_normalization", "full_per_candidate_semantic_review", "new_builder_and_validator", "new_counterfactual_generation", "v3_release"],
        "legacy_negative_total": len(candidates), "legacy_negative_seed_exclusions": len(seed_ids),
        "legacy_negative_pending": len(candidates) - len(seed_ids),
        "legacy_negative_occurrences": old_occurrences,
        "positive_rows": len(all_positive), "video_assignments": len(video_split),
        "next_stage": "P1_positive_event_normalization",
        "work_root": "data/processed/semantic_existence_v3", "release_root": "data/release/semantic_existence_v3",
        "existing_releases_modified": False, "do_not_infer_progress_from_chat_history": True,
        "user_preferences": {"sha_verification": False, "file_hashes": False, "multiple_training_seeds": False, "single_fixed_seed": 3407, "preset_scale_gates": False},
        "last_batch": state["last_batch"],
    })
    print(json.dumps({k: state[k] for k in ("state", "legacy_negative_unique_qids", "legacy_negative_occurrences", "seed_exclusions_imported", "legacy_pending", "positive_rows", "video_assignments", "unassigned_train_videos", "unassigned_train_validation_videos", "next_stage")}, indent=2))


if __name__ == "__main__":
    main()
