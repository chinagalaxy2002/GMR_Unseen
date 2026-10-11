#!/usr/bin/env python3
"""Independently validate a Soccer-GMR unseen release against source annotations."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from soccer_gmr_unseen_common import (
    ACTION_GROUPS,
    COMPOSITION_ACTIONS,
    EXPECTED_CLEAN_COUNTS,
    EXPECTED_COMPOSITION_TEAMS,
    EXPECTED_SOURCE_COUNTS,
    WORLD_CUP_SOURCE,
    composition_candidates,
    derive_cleaning,
    load_jsonl,
    normalize_vid,
    partition_row,
    train_exclusion_reason,
    worldcup_teams,
    write_json,
)


EXPECTED_QUADRANTS = {
    "A1_soccer": {"train": [4650, 7384, 0, 0], "val": [587, 911, 108, 149], "test": [818, 1111, 122, 195], "excluded": 1970, "val_seen": 1498},
    "A2_soccer": {"train": [4777, 7470, 0, 0], "val": [625, 914, 70, 146], "test": [833, 1136, 107, 170], "excluded": 1757, "val_seen": 1539},
    "A3_soccer": {"train": [4822, 7543, 0, 0], "val": [624, 927, 71, 133], "test": [812, 1158, 128, 148], "excluded": 1639, "val_seen": 1551},
    "C1_soccer": {"train": [4145, 7252, 0, 0], "val": [603, 914, 92, 146], "test": [839, 1132, 101, 174], "excluded": 2607, "val_seen": 1517},
    "C2_soccer": {"train": [4607, 7593, 0, 0], "val": [627, 915, 68, 145], "test": [867, 1163, 73, 143], "excluded": 1804, "val_seen": 1542},
}
PARTITIONS = ("S+", "S-", "U+", "U-")


def qid_key(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def row_index(rows: list[dict[str, Any]], label: str) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for row in rows:
        key = qid_key(row.get("qid"))
        if key in result:
            raise ValueError(f"Duplicate qid in {label}: {row.get('qid')}")
        result[key] = row
    return result


def check(checks: list[dict[str, Any]], name: str, ok: bool, detail: Any = None) -> None:
    checks.append({"name": name, "status": "pass" if ok else "fail", "detail": detail})


def counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "total": len(rows),
        "positive": sum(bool(row.get("relevant_windows")) for row in rows),
        "negative": sum(not bool(row.get("relevant_windows")) for row in rows),
        "videos": len({row.get("vid") for row in rows}),
    }


def quadrant_counts(rows: list[dict[str, Any]]) -> list[int]:
    return [sum(row.get("partition") == label for row in rows) for label in PARTITIONS]


def detailed_group_statistics(
    group: str,
    group_spec: dict[str, Any],
    split_rows: dict[str, list[dict[str, Any]]],
    excluded: list[dict[str, Any]],
    val_seen: list[dict[str, Any]],
    pairs: list[dict[str, Any]],
    expanded: list[dict[str, Any]],
    clean_train_total: int,
) -> tuple[dict[str, Any], dict[str, Any]]:
    splits: dict[str, Any] = {}
    inventory: dict[str, Any] = {"group": group, "by_split": {}}
    for split, rows in split_rows.items():
        parts: dict[str, Any] = {}
        for partition in PARTITIONS:
            subset = [row for row in rows if row.get("partition") == partition]
            parts[partition] = {
                "count": len(subset),
                "positive": sum(row.get("exist_label") == 1 for row in subset),
                "negative": sum(row.get("exist_label") == 0 for row in subset),
                "videos": len({normalize_vid(str(row.get("vid", ""))) for row in subset}),
                "generic_actor": sum(row.get("semantic_actor") is None for row in subset),
                "single_window": sum(len(row.get("relevant_windows", [])) == 1 for row in subset if row.get("exist_label") == 1),
                "multi_window": sum(len(row.get("relevant_windows", [])) > 1 for row in subset if row.get("exist_label") == 1),
            }
        by_action = {}
        for action in sorted({str(row.get("semantic_action")) for row in rows}):
            subset = [row for row in rows if row.get("semantic_action") == action]
            by_action[action] = {"count": len(subset), "positive": sum(row.get("exist_label") == 1 for row in subset), "negative": sum(row.get("exist_label") == 0 for row in subset)}
        by_actor = {}
        for actor in sorted({str(row.get("semantic_actor") or "<unspecified>") for row in rows}):
            subset = [row for row in rows if (row.get("semantic_actor") or "<unspecified>") == actor]
            by_actor[actor] = {"count": len(subset), "positive": sum(row.get("exist_label") == 1 for row in subset), "negative": sum(row.get("exist_label") == 0 for row in subset)}
        splits[split] = {
            "total": len(rows),
            "positive": sum(row.get("exist_label") == 1 for row in rows),
            "negative": sum(row.get("exist_label") == 0 for row in rows),
            "quadrants": parts,
            "by_action": by_action,
            "by_actor": by_actor,
        }
        inventory["by_split"][split] = {"by_action": by_action, "by_actor": by_actor, "generic_actor": parts}
    reason_counts = dict(sorted(Counter(row["exclusion_reason"] for row in excluded).items()))
    splits["train"].update({"excluded_train": len(excluded), "pre_exclusion_total": clean_train_total})
    result = {
        "group": group,
        "axis": group_spec["axis"],
        "held_actions": group_spec["held_actions"],
        "held_combinations": group_spec["held_combinations"],
        "splits": splits,
        "train_exclusion_count": len(excluded),
        "train_exclusion_by_reason": reason_counts,
        "val_seen_count": len(val_seen),
        "matched_u_pair_count": len(pairs),
        "matched_u_expanded_query_count": len(expanded),
    }
    return result, inventory


def recompute_source_statistics(source_splits: dict[str, list[dict[str, Any]]], full_rows: list[dict[str, Any]]) -> dict[str, Any]:
    source_totals: Counter[str] = Counter()
    split_values: dict[str, Any] = {}
    for split, rows in source_splits.items():
        by_source = {}
        for source in sorted({str(row.get("dataset_source")) for row in rows}):
            subset = [row for row in rows if str(row.get("dataset_source")) == source]
            item = counts(subset)
            item["normalized_videos"] = len({normalize_vid(str(row.get("vid", ""))) for row in subset})
            by_source[source] = item
            source_totals[source] += len(subset)
        selected = [row for row in rows if row.get("dataset_source") == WORLD_CUP_SOURCE]
        selected_stats = counts(selected)
        selected_stats["normalized_videos"] = len({normalize_vid(str(row.get("vid", ""))) for row in selected})
        split_values[split] = {"by_dataset_source": by_source, "worldcup2022": selected_stats}
    excluded = {}
    for source in sorted(source_totals):
        if source != WORLD_CUP_SOURCE:
            excluded[source] = counts([row for row in full_rows if str(row.get("dataset_source")) == source])
    return {
        "input_directory": "data/label/Full",
        "split_files_are_authoritative": True,
        "full_file_role": "consistency_check_only",
        "full_matches_split_union": True,
        "full_total": len(full_rows),
        "full_positive": sum(bool(row.get("relevant_windows")) for row in full_rows),
        "full_negative": sum(not bool(row.get("relevant_windows")) for row in full_rows),
        "dataset_source_total": dict(sorted(source_totals.items())),
        "excluded_sources": excluded,
        "splits": split_values,
        "worldcup_total": counts([row for row in full_rows if row.get("dataset_source") == WORLD_CUP_SOURCE]),
    }


def load_sources(source: Path) -> tuple[dict[str, list[dict[str, Any]]], list[dict[str, Any]]]:
    splits = {split: load_jsonl(source / f"{split}.jsonl") for split in ("train", "val", "test")}
    full = load_jsonl(source / "full.jsonl")
    split_index = row_index([row for split in splits.values() for row in split], "source split union")
    full_index = row_index(full, "source full")
    if split_index != full_index:
        raise ValueError("Source full.jsonl differs from the train/val/test union")
    return splits, full


def validate(args: argparse.Namespace) -> dict[str, Any]:
    release = args.release.resolve()
    source_dir = args.source.resolve()
    checks: list[dict[str, Any]] = []
    errors: list[str] = []
    try:
        source_splits, full = load_sources(source_dir)
        worldcup_by_split = {split: [row for row in rows if row.get("dataset_source") == WORLD_CUP_SOURCE] for split, rows in source_splits.items()}
        all_worldcup = [row for split in ("train", "val", "test") for row in worldcup_by_split[split]]
        raw_counts = {split: counts(rows) for split, rows in worldcup_by_split.items()}
        expected_raw = {split: EXPECTED_SOURCE_COUNTS[split] for split in EXPECTED_SOURCE_COUNTS}
        check(checks, "WorldCup source counts match plan", raw_counts == expected_raw, {"expected": expected_raw, "observed": raw_counts})
        check(checks, "Only WorldCup records enter release source pool", all(row.get("dataset_source") == WORLD_CUP_SOURCE for row in all_worldcup), len(all_worldcup))

        # Recompute all row-level semantic and data-quality decisions from the source files.
        teams = worldcup_teams(all_worldcup)
        tagged = []
        for split in ("train", "val", "test"):
            tagged.extend({**row, "source_split": split} for row in worldcup_by_split[split])
        expected_clean, expected_quarantine = derive_cleaning(tagged, teams)
        expected_clean_by_split = {split: [row for row in expected_clean if row["source_split"] == split] for split in ("train", "val", "test")}
        expected_quarantine_by_split = {split: [row for row in expected_quarantine if row["source_split"] == split] for split in ("train", "val", "test")}

        master_rows = load_jsonl(release / "master/worldcup_clean.jsonl")
        quarantine_rows = load_jsonl(release / "review/quarantine.jsonl")
        master_index = row_index(master_rows, "master clean")
        quarantine_index = row_index(quarantine_rows, "quarantine")
        expected_clean_index = row_index(expected_clean, "recomputed clean")
        expected_quarantine_index = row_index(expected_quarantine, "recomputed quarantine")
        check(checks, "Clean and quarantined qids partition source pool", set(master_index).isdisjoint(quarantine_index) and set(master_index) | set(quarantine_index) == {qid_key(row["qid"]) for row in all_worldcup}, {"clean": len(master_index), "quarantine": len(quarantine_index), "source": len(all_worldcup)})
        check(checks, "Clean rows exactly match recomputed clean qids", set(master_index) == set(expected_clean_index), {"expected": len(expected_clean_index), "observed": len(master_index)})
        check(checks, "Quarantine rows exactly match recomputed qids", set(quarantine_index) == set(expected_quarantine_index), {"expected": len(expected_quarantine_index), "observed": len(quarantine_index)})
        for label, actual_index, expected_index in (("master", master_index, expected_clean_index), ("quarantine", quarantine_index, expected_quarantine_index)):
            mismatches = []
            for key in set(actual_index) & set(expected_index):
                actual = actual_index[key]
                expected = expected_index[key]
                for field, value in expected.items():
                    if actual.get(field) != value:
                        mismatches.append({"qid": actual.get("qid"), "field": field, "actual": actual.get(field), "expected": value})
                        if len(mismatches) >= 5:
                            break
                if len(mismatches) >= 5:
                    break
            check(checks, f"{label} source fields and derived audit fields are preserved", not mismatches, mismatches)
            raw_mismatches = []
            for key in set(actual_index) & set(expected_index):
                for field, value in expected_index[key].items():
                    if field not in {"source_split", "semantic_action", "semantic_actor", "actor_specified", "event_mentions", "normalized_action_type", "quarantine_reasons", "exist_label"} and actual_index[key].get(field) != value:
                        raw_mismatches.append({"qid": actual_index[key].get("qid"), "field": field})
                        break
                if len(raw_mismatches) >= 5:
                    break
            check(checks, f"{label} original annotation fields unchanged", not raw_mismatches, raw_mismatches)

        actual_clean_counts = {
            split: {
                "positive": counts(expected_clean_by_split[split])["positive"],
                "negative": counts(expected_clean_by_split[split])["negative"],
                "total": counts(expected_clean_by_split[split])["total"],
                "quarantine": len(expected_quarantine_by_split[split]),
            }
            for split in expected_clean_by_split
        }
        expected_clean_counts = {split: EXPECTED_CLEAN_COUNTS[split] for split in EXPECTED_CLEAN_COUNTS}
        check(checks, "Recomputed clean and quarantine counts match plan", actual_clean_counts == expected_clean_counts, {"expected": expected_clean_counts, "observed": actual_clean_counts})

        recorded_source_stats = json.loads((release / "source_statistics.json").read_text(encoding="utf-8"))
        computed_source_stats = recompute_source_statistics(source_splits, full)
        check(checks, "Published source statistics recompute from source JSONL", recorded_source_stats == computed_source_stats, None if recorded_source_stats == computed_source_stats else {"recorded_worldcup_total": recorded_source_stats.get("worldcup_total"), "computed_worldcup_total": computed_source_stats["worldcup_total"]})
        recorded_audit = json.loads((release / "audit_summary.json").read_text(encoding="utf-8"))
        qid_reason_counts: Counter[str] = Counter()
        for row in expected_quarantine:
            qid_reason_counts.update(set(row["quarantine_reasons"]))
        expected_quarantine_split_stats = {
            split: {"total": len(rows), "positive": sum(row["exist_label"] == 1 for row in rows), "negative": sum(row["exist_label"] == 0 for row in rows)}
            for split, rows in expected_quarantine_by_split.items()
        }
        expected_clean_split_stats = {split: counts(rows) for split, rows in expected_clean_by_split.items()}
        audit_matches = (
            recorded_audit.get("source_rows") == len(all_worldcup)
            and recorded_audit.get("clean_rows") == len(expected_clean)
            and recorded_audit.get("quarantine_rows") == len(expected_quarantine)
            and recorded_audit.get("clean_plus_quarantine_closes_source") is True
            and recorded_audit.get("quarantine_qids_by_reason") == dict(sorted(qid_reason_counts.items()))
            and recorded_audit.get("quarantine_reason_occurrences") == dict(sorted(qid_reason_counts.items()))
            and recorded_audit.get("quarantine_by_split") == expected_quarantine_split_stats
            and recorded_audit.get("clean_by_split") == expected_clean_split_stats
        )
        check(checks, "Published cleaning audit recomputes from source qids and reasons", audit_matches, {"recorded_clean": recorded_audit.get("clean_rows"), "computed_clean": len(expected_clean), "recorded_quarantine": recorded_audit.get("quarantine_rows"), "computed_quarantine": len(expected_quarantine)})

        normalized_vid_splits: dict[str, set[str]] = {}
        for split, rows in worldcup_by_split.items():
            normalized_vid_splits[split] = {normalize_vid(str(row.get("vid", ""))) for row in rows}
        overlap = {f"{a}/{b}": sorted(normalized_vid_splits[a] & normalized_vid_splits[b])[:10] for i, a in enumerate(("train", "val", "test")) for b in ("val", "test")[i:] if a != b}
        check(checks, "Normalized video ids retain single source split", all(not values for values in overlap.values()), overlap)

        candidate_rows, computed_teams = composition_candidates(expected_clean_by_split["train"])
        specs = json.loads((release / "selection/split_specs.json").read_text(encoding="utf-8"))
        expected_group_names = set(ACTION_GROUPS) | set(COMPOSITION_ACTIONS)
        check(checks, "Five group specifications are present", set(specs.get("groups", {})) == expected_group_names, sorted(specs.get("groups", {})))
        check(checks, "Composition teams recompute from clean train support", computed_teams == EXPECTED_COMPOSITION_TEAMS and specs.get("observed_teams") == computed_teams, {"plan_expected": EXPECTED_COMPOSITION_TEAMS, "computed": computed_teams})
        with (release / "selection/train_composition_candidates.csv").open(encoding="utf-8", newline="") as stream:
            recorded_candidates = list(csv.DictReader(stream))
        normalized_recorded = []
        for row in recorded_candidates:
            normalized_recorded.append({
                "action": row["action"], "team": row["team"],
                "train_positive": int(row["train_positive"]), "train_negative": int(row["train_negative"]),
                "eligible": row["eligible"].lower() == "true",
                "eligible_rank": int(row["eligible_rank"]) if row["eligible_rank"] else None,
                "selected_C1_soccer": row["selected_C1_soccer"].lower() == "true",
                "selected_C2_soccer": row["selected_C2_soccer"].lower() == "true",
            })
        check(checks, "Train composition candidate ledger matches recomputation", recorded_candidates and normalized_recorded == candidate_rows, {"expected_rows": len(candidate_rows), "recorded_rows": len(recorded_candidates)})

        clean_by_split = {split: [master_index[qid_key(row["qid"])] for row in expected_clean_by_split[split]] for split in ("train", "val", "test")}
        group_qids: dict[str, dict[str, set[str]]] = {}
        group_computed: dict[str, dict[str, Any]] = {}
        for group in sorted(expected_group_names):
            group_spec = specs["groups"].get(group, {})
            if group in ACTION_GROUPS:
                held_actions = ACTION_GROUPS[group]["held_actions"]
                combinations: set[tuple[str, str]] = set()
                check(checks, f"{group} action specification matches plan", group_spec.get("axis") == "action" and group_spec.get("held_actions") == held_actions, group_spec)
            else:
                held_actions = COMPOSITION_ACTIONS[group]
                combinations = {(action, actor) for action, actors in computed_teams[group].items() for actor in actors}
                check(checks, f"{group} composition specification matches recomputation", group_spec.get("axis") == "action_actor_composition" and group_spec.get("held_actions") == held_actions and {tuple(x) for x in group_spec.get("held_combinations", [])} == combinations, group_spec)
            group_dir = release / "splits" / group
            expected_assigned = {split: [partition_row(row, group, held_actions, combinations) for row in clean_by_split[split]] for split in ("train", "val", "test")}
            output_rows = {split: load_jsonl(group_dir / f"{split}.jsonl") for split in ("train", "val", "test")}
            exclusions: list[dict[str, Any]] = []
            expected_train: list[dict[str, Any]] = []
            for row in expected_assigned["train"]:
                reason = train_exclusion_reason(row, group, held_actions, combinations)
                if reason:
                    expected_exclusion = dict(row)
                    expected_exclusion["expected_partition"] = row["partition"]
                    expected_exclusion["exclusion_reason"] = reason
                    exclusions.append(expected_exclusion)
                else:
                    expected_train.append(row)
            expected_outputs = {"train": expected_train, "val": expected_assigned["val"], "test": expected_assigned["test"]}
            sets: dict[str, set[str]] = {}
            for split in ("train", "val", "test"):
                actual = row_index(output_rows[split], f"{group} {split}")
                expected = row_index(expected_outputs[split], f"expected {group} {split}")
                sets[split] = set(actual)
                check(checks, f"{group} {split} qids match independently assigned source rows", set(actual) == set(expected), {"expected": len(expected), "actual": len(actual)})
                mismatches = []
                for key in set(actual) & set(expected):
                    for field, value in expected[key].items():
                        if actual[key].get(field) != value:
                            mismatches.append({"qid": actual[key].get("qid"), "field": field, "actual": actual[key].get(field), "expected": value})
                            break
                    if len(mismatches) >= 5:
                        break
                check(checks, f"{group} {split} labels and source annotation fields match", not mismatches, mismatches)
                check(checks, f"{group} {split} contains only WorldCup source rows", all(row.get("dataset_source") == WORLD_CUP_SOURCE for row in output_rows[split]), None)
            actual_excluded = load_jsonl(group_dir / "excluded_train.jsonl")
            actual_excluded_index = row_index(actual_excluded, f"{group} exclusions")
            expected_exclusion_index = row_index(exclusions, f"expected {group} exclusions")
            check(checks, f"{group} training exclusion ledger matches all rule-based exclusions", set(actual_excluded_index) == set(expected_exclusion_index), {"expected": len(exclusions), "actual": len(actual_excluded)})
            reason_mismatch = [{"qid": actual_excluded_index[key].get("qid"), "expected": expected_exclusion_index[key].get("exclusion_reason"), "actual": actual_excluded_index[key].get("exclusion_reason")} for key in set(actual_excluded_index) & set(expected_exclusion_index) if actual_excluded_index[key].get("exclusion_reason") != expected_exclusion_index[key].get("exclusion_reason")]
            check(checks, f"{group} exclusion reasons are accurate", not reason_mismatch, reason_mismatch[:5])
            val_seen = load_jsonl(group_dir / "val_seen.jsonl")
            expected_seen = [row for row in expected_assigned["val"] if row["semantic_status"] == "seen"]
            val_seen_index = row_index(val_seen, f"{group} val_seen")
            expected_seen_index = row_index(expected_seen, f"expected {group} val_seen")
            check(checks, f"{group} val_seen is exactly seen validation subset", set(val_seen_index) == set(expected_seen_index), {"expected": len(expected_seen), "actual": len(val_seen)})
            check(checks, f"{group} training contains only S+/S-", all(row.get("partition") in {"S+", "S-"} for row in output_rows["train"]), None)

            expected_quadrants = EXPECTED_QUADRANTS[group]
            actual_quadrants = {split: quadrant_counts(output_rows[split]) for split in ("train", "val", "test")}
            expected_quadrant_counts = {split: expected_quadrants[split] for split in ("train", "val", "test")}
            check(checks, f"{group} four-quadrant counts match plan", actual_quadrants == expected_quadrant_counts, {"expected": expected_quadrant_counts, "observed": actual_quadrants})
            check(checks, f"{group} exclusion and val_seen counts match plan", len(actual_excluded) == expected_quadrants["excluded"] and len(val_seen) == expected_quadrants["val_seen"], {"excluded": len(actual_excluded), "val_seen": len(val_seen)})
            if group in ACTION_GROUPS:
                held = set(held_actions)
                check(checks, f"{group} held action absent from retained train", all(row.get("semantic_action") not in held for row in output_rows["train"]), None)
            else:
                train_rows = output_rows["train"]
                no_held_combo = all((row.get("semantic_action"), row.get("semantic_actor")) not in combinations for row in train_rows)
                no_generic_held_action = all(not (row.get("semantic_actor") is None and row.get("semantic_action") in held_actions) for row in train_rows)
                check(checks, f"{group} held combinations and generic held-action queries absent from train", no_held_combo and no_generic_held_action, None)
                components_supported = True
                unsupported = []
                for action, actor in combinations:
                    has_action_elsewhere = any(row["exist_label"] == 1 and row.get("semantic_action") == action and row.get("semantic_actor") != actor for row in train_rows)
                    has_actor_elsewhere = any(row["exist_label"] == 1 and row.get("semantic_actor") == actor and row.get("semantic_action") != action for row in train_rows)
                    if not has_action_elsewhere or not has_actor_elsewhere:
                        components_supported = False
                        unsupported.append({"action": action, "actor": actor, "action_elsewhere": has_action_elsewhere, "actor_elsewhere": has_actor_elsewhere})
                check(checks, f"{group} held action and team components have positive train support", components_supported, unsupported[:10])

            # Recompute the optional same-clip/same-action U pair ledger and expansion.
            by_key: dict[tuple[str, str], dict[int, list[dict[str, Any]]]] = defaultdict(lambda: {0: [], 1: []})
            test_index = row_index(output_rows["test"], f"{group} test pair source")
            for row in output_rows["test"]:
                if row.get("semantic_status") == "unseen":
                    by_key[(normalize_vid(str(row.get("vid", ""))), str(row.get("semantic_action")))][int(row["exist_label"])].append(row)
            expected_pairs = []
            expected_expanded: dict[str, tuple[str, str]] = {}
            for key in sorted(by_key):
                positives = sorted(by_key[key][1], key=lambda row: qid_key(row.get("qid")))
                negatives = sorted(by_key[key][0], key=lambda row: qid_key(row.get("qid")))
                for pos, neg in zip(positives, negatives):
                    pair_id = f"{group}_pair_{len(expected_pairs) + 1:05d}"
                    expected_pairs.append({"pair_id": pair_id, "positive_qid": pos.get("qid"), "negative_qid": neg.get("qid"), "vid": pos.get("vid"), "normalized_vid": key[0], "semantic_action": key[1], "pair_type": "same_clip_same_action_observational", "same_source_positive": False})
                    expected_expanded[qid_key(pos.get("qid"))] = (pair_id, "positive")
                    expected_expanded[qid_key(neg.get("qid"))] = (pair_id, "negative")
            actual_pairs = load_jsonl(group_dir / "matched_u_pairs.jsonl")
            actual_expanded = load_jsonl(group_dir / "test_matched_u.jsonl")
            check(checks, f"{group} matched pair ledger matches deterministic same-clip pairing", actual_pairs == expected_pairs, {"expected": len(expected_pairs), "actual": len(actual_pairs)})
            expanded_index = row_index(actual_expanded, f"{group} matched test subset") if actual_expanded else {}
            check(checks, f"{group} matched test expansion has each paired qid once", set(expanded_index) == set(expected_expanded), {"expected": len(expected_expanded), "actual": len(expanded_index)})
            expansion_errors = []
            for key, (pair_id, role) in expected_expanded.items():
                row = expanded_index.get(key)
                if row is None or row.get("matched_pair_id") != pair_id or row.get("matched_role") != role or key not in test_index:
                    expansion_errors.append(key)
            check(checks, f"{group} matched test rows reference valid unseen positive/negative rows", not expansion_errors, expansion_errors[:5])
            recomputed_stats, recomputed_inventory = detailed_group_statistics(
                group,
                group_spec,
                output_rows,
                actual_excluded,
                val_seen,
                actual_pairs,
                actual_expanded,
                len(expected_assigned["train"]),
            )
            recorded_stats = json.loads((group_dir / "statistics.json").read_text(encoding="utf-8"))
            recorded_inventory = json.loads((group_dir / "semantic_inventory.json").read_text(encoding="utf-8"))
            check(checks, f"{group} published statistics recompute from files", recorded_stats == recomputed_stats, {"recorded_exclusions": recorded_stats.get("train_exclusion_count"), "computed_exclusions": recomputed_stats["train_exclusion_count"]})
            check(checks, f"{group} semantic inventory recomputes from files", recorded_inventory == recomputed_inventory, None if recorded_inventory == recomputed_inventory else "inventory mismatch")
            group_qids[group] = sets
            group_computed[group] = {"quadrants": actual_quadrants, "excluded": len(actual_excluded), "val_seen": len(val_seen), "pairs": len(actual_pairs)}

        for split in ("val", "test"):
            values = [group_qids[group][split] for group in sorted(expected_group_names)]
            check(checks, f"All five groups share the same clean {split} qid set", all(value == values[0] for value in values[1:]) and values[0] == {qid_key(row["qid"]) for row in clean_by_split[split]}, len(values[0]))

        required_files = [
            "README.md", "construction_protocol.json", "source_statistics.json", "audit_summary.json",
            "selection/semantic_rules.json", "selection/split_specs.json", "selection/train_composition_candidates.csv",
            "master/worldcup_clean.jsonl", "review/quarantine.jsonl",
        ]
        for group in sorted(expected_group_names):
            required_files.extend(f"splits/{group}/{name}" for name in ("train.jsonl", "val.jsonl", "val_seen.jsonl", "test.jsonl", "excluded_train.jsonl", "matched_u_pairs.jsonl", "test_matched_u.jsonl", "semantic_inventory.json", "statistics.json"))
        missing = [path for path in required_files if not (release / path).is_file()]
        check(checks, "Required release files are present", not missing, missing)
        hash_named = [str(path.relative_to(release)) for path in release.rglob("*") if path.is_file() and any(token in path.name.casefold() for token in ("sha256", "checksum", "hash_manifest"))]
        check(checks, "No checksum or hash manifest was generated", not hash_named, hash_named)

        # Update summary after all independent checks. The validator does not use a builder success flag.
        failures = [entry for entry in checks if entry["status"] != "pass"]
        report = {
            "status": "pass" if not failures else "fail",
            "validator": "scripts/validate_soccer_gmr_unseen.py",
            "validated_against_source": str(source_dir),
            "mechanical_checks_passed": not failures,
            "manual_video_review_performed": False,
            "check_count": len(checks),
            "passed_check_count": len(checks) - len(failures),
            "failed_check_count": len(failures),
            "checks": checks,
            "observed_group_statistics": group_computed,
            "known_validation_scope": [
                "No video-level annotation review was performed.",
                "Cross-split clip ids are checked; temporal overlaps between distinct clips are intentionally ignored.",
                "No model training or performance evaluation was run.",
            ],
        }
        write_json(release / "validation_report.json", report)
        return report
    except Exception as exc:
        errors.append(str(exc))
        report = {
            "status": "fail",
            "validator": "scripts/validate_soccer_gmr_unseen.py",
            "validated_against_source": str(source_dir),
            "mechanical_checks_passed": False,
            "manual_video_review_performed": False,
            "check_count": len(checks),
            "passed_check_count": sum(item["status"] == "pass" for item in checks),
            "failed_check_count": 1,
            "checks": checks,
            "errors": errors,
        }
        if release.exists():
            write_json(release / "validation_report.json", report)
        return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path("data/label/Full"))
    parser.add_argument("--release", type=Path, default=Path("data/release/soccer_gmr_unseen_v1"))
    args = parser.parse_args()
    report = validate(args)
    print(f"{report['status'].upper()}: {report.get('passed_check_count', 0)}/{report.get('check_count', 0)} checks passed")
    if report["status"] != "pass":
        for item in report.get("checks", []):
            if item["status"] != "pass":
                print(f"FAIL {item['name']}: {item.get('detail')}")
        for error in report.get("errors", []):
            print(f"ERROR: {error}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()

