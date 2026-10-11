#!/usr/bin/env python3
"""Build the Soccer-GMR WorldCup semantic-unseen four-quadrant release."""

from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
import sys
import tempfile
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
    write_jsonl,
)


def qid_key(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def count_rows(rows: list[dict[str, Any]]) -> dict[str, int]:
    positives = sum(bool(row.get("relevant_windows")) for row in rows)
    vids = {row.get("vid") for row in rows}
    return {"positive": positives, "negative": len(rows) - positives, "total": len(rows), "videos": len(vids)}


def load_sources(source_dir: Path) -> tuple[dict[str, list[dict[str, Any]]], list[dict[str, Any]]]:
    split_names = ("train", "val", "test")
    splits = {name: load_jsonl(source_dir / f"{name}.jsonl") for name in split_names}
    full_rows = load_jsonl(source_dir / "full.jsonl")
    all_split_rows = [row for name in split_names for row in splits[name]]
    split_qids = [qid_key(row.get("qid")) for row in all_split_rows]
    if len(set(split_qids)) != len(split_qids):
        raise ValueError("Source train/val/test contain duplicate qid values")
    full_qids = [qid_key(row.get("qid")) for row in full_rows]
    if len(set(full_qids)) != len(full_qids):
        raise ValueError("Source full.jsonl contains duplicate qid values")
    by_qid_split = {qid_key(row.get("qid")): row for row in all_split_rows}
    by_qid_full = {qid_key(row.get("qid")): row for row in full_rows}
    if by_qid_split != by_qid_full:
        split_only = sorted(set(by_qid_split) - set(by_qid_full))[:5]
        full_only = sorted(set(by_qid_full) - set(by_qid_split))[:5]
        changed = sorted(key for key in set(by_qid_split) & set(by_qid_full) if by_qid_split[key] != by_qid_full[key])[:5]
        raise ValueError(f"full.jsonl does not match split union: split_only={split_only}, full_only={full_only}, changed={changed}")
    return splits, full_rows


def source_stats(splits: dict[str, list[dict[str, Any]]], full_rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_split: dict[str, Any] = {}
    all_source_counts: Counter[str] = Counter()
    excluded_sources: dict[str, Any] = {}
    for split, rows in splits.items():
        source_counter: dict[str, Any] = {}
        for source in sorted({str(row.get("dataset_source")) for row in rows}):
            subset = [row for row in rows if str(row.get("dataset_source")) == source]
            values = count_rows(subset)
            values["normalized_videos"] = len({normalize_vid(str(row.get("vid", ""))) for row in subset})
            source_counter[source] = values
            all_source_counts[source] += len(subset)
        selected = [row for row in rows if row.get("dataset_source") == WORLD_CUP_SOURCE]
        selected_stats = count_rows(selected)
        selected_stats["normalized_videos"] = len({normalize_vid(str(row.get("vid", ""))) for row in selected})
        by_split[split] = {"by_dataset_source": source_counter, "worldcup2022": selected_stats}
    for source in sorted(all_source_counts):
        if source != WORLD_CUP_SOURCE:
            subset = [row for row in full_rows if str(row.get("dataset_source")) == source]
            excluded_sources[source] = count_rows(subset)
    return {
        "input_directory": "data/label/Full",
        "split_files_are_authoritative": True,
        "full_file_role": "consistency_check_only",
        "full_matches_split_union": True,
        "full_total": len(full_rows),
        "full_positive": sum(bool(row.get("relevant_windows")) for row in full_rows),
        "full_negative": sum(not bool(row.get("relevant_windows")) for row in full_rows),
        "dataset_source_total": dict(sorted(all_source_counts.items())),
        "excluded_sources": excluded_sources,
        "splits": by_split,
        "worldcup_total": count_rows([row for row in full_rows if row.get("dataset_source") == WORLD_CUP_SOURCE]),
    }


def add_split(rows: list[dict[str, Any]], split: str) -> list[dict[str, Any]]:
    result = []
    for row in rows:
        enriched = dict(row)
        enriched["source_split"] = split
        result.append(enriched)
    return result


def expected_comparison(actual: dict[str, Any], expected: dict[str, Any]) -> dict[str, Any]:
    result = {}
    for split, expected_values in expected.items():
        observed = actual.get(split, {})
        differences = {key: {"expected": value, "observed": observed.get(key)} for key, value in expected_values.items() if observed.get(key) != value}
        result[split] = {"matches_plan": not differences, "differences": differences}
    return result


def build_group(
    stage: Path,
    group_name: str,
    clean_by_split: dict[str, list[dict[str, Any]]],
    held_actions: list[str],
    held_combinations: set[tuple[str, str]],
    group_spec: dict[str, Any],
) -> dict[str, Any]:
    group_dir = stage / "splits" / group_name
    group_dir.mkdir(parents=True, exist_ok=True)
    per_split: dict[str, list[dict[str, Any]]] = {}
    excluded: list[dict[str, Any]] = []
    for split in ("train", "val", "test"):
        assigned = [partition_row(row, group_name, held_actions, held_combinations) for row in clean_by_split[split]]
        per_split[split] = assigned
        if split == "train":
            retained = []
            for row in assigned:
                reason = train_exclusion_reason(row, group_name, held_actions, held_combinations)
                if reason is None:
                    if row["semantic_status"] != "seen":
                        raise AssertionError(f"Unseen training query was not excluded in {group_name}: {row.get('qid')}")
                    retained.append(row)
                else:
                    record = dict(row)
                    record["expected_partition"] = row["partition"]
                    record["exclusion_reason"] = reason
                    excluded.append(record)
            write_jsonl(group_dir / "train.jsonl", retained)
        elif split == "val":
            write_jsonl(group_dir / "val.jsonl", assigned)
            write_jsonl(group_dir / "val_seen.jsonl", [row for row in assigned if row["semantic_status"] == "seen"])
        else:
            write_jsonl(group_dir / "test.jsonl", assigned)
    write_jsonl(group_dir / "excluded_train.jsonl", excluded)

    test_rows = per_split["test"]
    pair_buckets: dict[tuple[str, str], dict[int, list[dict[str, Any]]]] = defaultdict(lambda: {0: [], 1: []})
    for row in test_rows:
        if row["semantic_status"] == "unseen":
            key = (normalize_vid(str(row.get("vid", ""))), str(row.get("semantic_action")))
            pair_buckets[key][int(row["exist_label"])].append(row)
    pairs: list[dict[str, Any]] = []
    expanded: list[dict[str, Any]] = []
    for key in sorted(pair_buckets):
        bucket = pair_buckets[key]
        positive = sorted(bucket[1], key=lambda row: qid_key(row.get("qid")))
        negative = sorted(bucket[0], key=lambda row: qid_key(row.get("qid")))
        for positive_row, negative_row in zip(positive, negative):
            pair_id = f"{group_name}_pair_{len(pairs) + 1:05d}"
            pairs.append({
                "pair_id": pair_id,
                "positive_qid": positive_row.get("qid"),
                "negative_qid": negative_row.get("qid"),
                "vid": positive_row.get("vid"),
                "normalized_vid": key[0],
                "semantic_action": key[1],
                "pair_type": "same_clip_same_action_observational",
                "same_source_positive": False,
            })
            pos_copy = dict(positive_row)
            pos_copy.update({"matched_pair_id": pair_id, "matched_role": "positive"})
            neg_copy = dict(negative_row)
            neg_copy.update({"matched_pair_id": pair_id, "matched_role": "negative"})
            expanded.extend((pos_copy, neg_copy))
    write_jsonl(group_dir / "matched_u_pairs.jsonl", pairs)
    write_jsonl(group_dir / "test_matched_u.jsonl", expanded)

    statistics, inventory = summarize_group(per_split, excluded, pairs, expanded, group_spec)
    write_json(group_dir / "statistics.json", statistics)
    write_json(group_dir / "semantic_inventory.json", inventory)
    return statistics


def summarize_group(
    per_split: dict[str, list[dict[str, Any]]],
    excluded: list[dict[str, Any]],
    pairs: list[dict[str, Any]],
    expanded: list[dict[str, Any]],
    spec: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    by_split: dict[str, Any] = {}
    inventory: dict[str, Any] = {"group": spec["group"], "by_split": {}}
    for split, rows in per_split.items():
        if split == "train":
            rows = [row for row in rows if train_exclusion_reason(row, spec["group"], spec["held_actions"], set(map(tuple, spec["held_combinations"]))) is None]
        parts: dict[str, Any] = {}
        for partition in ("S+", "S-", "U+", "U-"):
            subset = [row for row in rows if row["partition"] == partition]
            parts[partition] = {
                "count": len(subset),
                "positive": sum(row["exist_label"] == 1 for row in subset),
                "negative": sum(row["exist_label"] == 0 for row in subset),
                "videos": len({normalize_vid(str(row.get("vid", ""))) for row in subset}),
                "generic_actor": sum(row.get("semantic_actor") is None for row in subset),
                "single_window": sum(len(row.get("relevant_windows", [])) == 1 for row in subset if row["exist_label"]),
                "multi_window": sum(len(row.get("relevant_windows", [])) > 1 for row in subset if row["exist_label"]),
            }
        action_dist: dict[str, Any] = {}
        for action in sorted({str(row.get("semantic_action")) for row in rows}):
            selected = [row for row in rows if row.get("semantic_action") == action]
            action_dist[action] = {"count": len(selected), "positive": sum(row["exist_label"] == 1 for row in selected), "negative": sum(row["exist_label"] == 0 for row in selected)}
        actor_dist: dict[str, Any] = {}
        for actor in sorted({str(row.get("semantic_actor") or "<unspecified>") for row in rows}):
            selected = [row for row in rows if (row.get("semantic_actor") or "<unspecified>") == actor]
            actor_dist[actor] = {"count": len(selected), "positive": sum(row["exist_label"] == 1 for row in selected), "negative": sum(row["exist_label"] == 0 for row in selected)}
        by_split[split] = {
            "total": len(rows),
            "positive": sum(row["exist_label"] == 1 for row in rows),
            "negative": sum(row["exist_label"] == 0 for row in rows),
            "quadrants": parts,
            "by_action": action_dist,
            "by_actor": actor_dist,
        }
        inventory["by_split"][split] = {"by_action": action_dist, "by_actor": actor_dist, "generic_actor": parts}
    train_rows = per_split["train"]
    train_retained = [row for row in train_rows if train_exclusion_reason(row, spec["group"], spec["held_actions"], set(map(tuple, spec["held_combinations"]))) is None]
    by_split["train"]["total"] = len(train_retained)
    by_split["train"]["positive"] = sum(row["exist_label"] == 1 for row in train_retained)
    by_split["train"]["negative"] = sum(row["exist_label"] == 0 for row in train_retained)
    by_split["train"]["excluded_train"] = len(excluded)
    by_split["train"]["pre_exclusion_total"] = len(train_rows)
    return ({
        "group": spec["group"],
        "axis": spec["axis"],
        "held_actions": spec["held_actions"],
        "held_combinations": spec["held_combinations"],
        "splits": by_split,
        "train_exclusion_count": len(excluded),
        "train_exclusion_by_reason": dict(sorted(Counter(row["exclusion_reason"] for row in excluded).items())),
        "val_seen_count": sum(row["semantic_status"] == "seen" for row in per_split["val"]),
        "matched_u_pair_count": len(pairs),
        "matched_u_expanded_query_count": len(expanded),
    }, inventory)


def make_readme(raw_stats: dict[str, dict[str, int]], clean_stats: dict[str, dict[str, int]], group_statistics: dict[str, dict[str, Any]]) -> str:
    clean_table = "\n".join(
        f"| {split} | {raw_stats[split]['positive']} | {raw_stats[split]['negative']} | {raw_stats[split]['total']} | {values['positive']} | {values['negative']} | {values['total']} | {values['quarantine']} |"
        for split, values in clean_stats.items()
    )
    group_rows = []
    for group, statistics in group_statistics.items():
        split_values = statistics["splits"]
        fmt = lambda split: "/".join(str(split_values[split]["quadrants"][part]["count"]) for part in ("S+", "S-", "U+", "U-"))
        reasons = statistics["train_exclusion_by_reason"]
        reason_note = ", ".join(f"{name} {count}" for name, count in reasons.items()) or "none"
        group_rows.append(f"| {group} | {fmt('train')} | {fmt('val')} | {fmt('test')} | {statistics['train_exclusion_count']} ({reason_note}) | {statistics['val_seen_count']} | {statistics['matched_u_pair_count']} |")
    group_table = "\n".join(group_rows)
    return f"""# Soccer-GMR WorldCup Semantic-Unseen v1

This release contains mechanically cleaned annotations from `data/label/Full/`, filtered to `dataset_source == \"worldcup2022\"`. It preserves the source `qid`, `vid`, `query`, `duration`, `relevant_windows`, `moment`, action and match metadata. It does not include videos, features, model outputs, or checksums.

## Protocol

Each of five independent groups has a `train.jsonl` containing only S+/S−, a four-quadrant `val.jsonl`, a Seen-only `val_seen.jsonl` for checkpoint and threshold selection, and a four-quadrant `test.jsonl`. Use `val_seen.jsonl` for all model and threshold selection. `excluded_train.jsonl` records clean original training queries withheld by that group's semantic rule. `review/quarantine.jsonl` contains source rows removed by mechanical quality rules, with all detected reasons.

## Recomputed counts

| Source split | Raw + | Raw − | Raw total | Clean + | Clean − | Clean total | Quarantined |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
{clean_table}

Quadrant counts below use the order S+/S−/U+/U−. Counts are queries; the same validation and test qids appear in all five groups with group-specific partitions.

| Group | Train | Val | Test | Train exclusions | val_seen | Test U pairs |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
{group_table}

The action groups hold out dribble (A1), shot (A2), or interception (A3). The composition groups hold out eight action–team combinations for each of two actions, selected by the predeclared train-only support ranking; the exact lists and candidate counts are in `selection/`. Generic-actor queries in composition-group validation and test are S because they do not name a held-out action–team relation. They are excluded from composition-group training when their action is held out.

`matched_u_pairs.jsonl` and `test_matched_u.jsonl` are optional observational diagnostics. A pair shares a normalized clip identifier and action but is not a source-positive edit or a counterfactual pair.

## Construction and validation

From the repository root:

```bash
python scripts/build_soccer_gmr_unseen.py --source data/label/Full --output data/release/soccer_gmr_unseen_v1
python scripts/validate_soccer_gmr_unseen.py --source data/label/Full --release data/release/soccer_gmr_unseen_v1
```

See `construction_protocol.json`, `source_statistics.json`, `audit_summary.json`, and `validation_report.json` for the recorded rules, recomputed counts, cleaning audit, and independent validation results.

## Limitations

The source train/val/test assignment is preserved, and clip overlap across those sets is not analyzed or repaired. This does not establish match-level or complete visual independence. All data come from WorldCup 2022, but team, match, and query-template biases may remain. Negative labels and positive windows are inherited from source annotation and were not reviewed against videos for this release; mechanical checks cannot establish annotation truth. The action and action–team groups control different semantic axes, and generic-actor queries limit interpretation of composition splits. C2 has a small test U+ subset (73 queries); see per-group statistics. This release contains no experiment results and does not imply that any model was trained.
"""


def build(args: argparse.Namespace) -> None:
    source_dir = args.source.resolve()
    output_dir = args.output.resolve()
    if output_dir.exists():
        raise FileExistsError(f"Refusing to overwrite existing output: {output_dir}")
    splits, full_rows = load_sources(source_dir)
    worldcup_by_split = {name: [row for row in rows if row.get("dataset_source") == WORLD_CUP_SOURCE] for name, rows in splits.items()}
    raw_stats = {split: count_rows(rows) for split, rows in worldcup_by_split.items()}
    raw_compare = expected_comparison(raw_stats, EXPECTED_SOURCE_COUNTS)
    all_worldcup = [row for split in ("train", "val", "test") for row in worldcup_by_split[split]]
    teams = worldcup_teams(all_worldcup)
    clean, quarantine = derive_cleaning([row for split in ("train", "val", "test") for row in add_split(worldcup_by_split[split], split)], teams)
    clean_by_split = {split: [row for row in clean if row["source_split"] == split] for split in ("train", "val", "test")}
    quarantine_by_split = {split: [row for row in quarantine if row["source_split"] == split] for split in ("train", "val", "test")}
    clean_stats = {split: {**count_rows(rows), "quarantine": len(quarantine_by_split[split])} for split, rows in clean_by_split.items()}
    clean_compare = expected_comparison(clean_stats, EXPECTED_CLEAN_COUNTS)

    candidates, composition_teams = composition_candidates(clean_by_split["train"])
    candidate_differences = {}
    for group, expected_actions in EXPECTED_COMPOSITION_TEAMS.items():
        observed = composition_teams.get(group, {})
        if observed != expected_actions:
            candidate_differences[group] = {"expected": expected_actions, "observed": observed}

    staging_parent = output_dir.parent
    staging_parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=f".{output_dir.name}.building-", dir=staging_parent))
    try:
        (stage / "selection").mkdir(parents=True, exist_ok=True)
        (stage / "master").mkdir(parents=True, exist_ok=True)
        (stage / "review").mkdir(parents=True, exist_ok=True)
        write_jsonl(stage / "master" / "worldcup_clean.jsonl", clean)
        write_jsonl(stage / "review" / "quarantine.jsonl", quarantine)
        write_json(stage / "source_statistics.json", source_stats(splits, full_rows))

        reason_qids: Counter[str] = Counter()
        reason_rows: Counter[str] = Counter()
        for row in quarantine:
            for reason in row["quarantine_reasons"]:
                reason_qids[reason] += 1
                reason_rows[reason] += 1
        audit = {
            "source_rows": len(all_worldcup),
            "clean_rows": len(clean),
            "quarantine_rows": len(quarantine),
            "clean_plus_quarantine_closes_source": len(clean) + len(quarantine) == len(all_worldcup),
            "quarantine_qids_by_reason": dict(sorted(reason_qids.items())),
            "quarantine_reason_occurrences": dict(sorted(reason_rows.items())),
            "quarantine_by_split": {split: {"total": len(rows), "positive": sum(row["exist_label"] == 1 for row in rows), "negative": sum(row["exist_label"] == 0 for row in rows)} for split, rows in quarantine_by_split.items()},
            "clean_by_split": {split: count_rows(rows) for split, rows in clean_by_split.items()},
            "source_expected_comparison": raw_compare,
            "clean_expected_comparison": clean_compare,
            "composition_candidate_expected_comparison": candidate_differences,
            "manual_video_review_performed": False,
        }
        write_json(stage / "audit_summary.json", audit)

        with (stage / "selection" / "train_composition_candidates.csv").open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=["action", "team", "train_positive", "train_negative", "eligible", "eligible_rank", "selected_C1_soccer", "selected_C2_soccer"])
            writer.writeheader()
            writer.writerows(candidates)
        rules = {
            "action_parser": "casefold; normalize hyphen/underscore and whitespace; remove an explicit trailing 'by players from TEAM'; longest event phrases first; aliases and recognized non-WorldCup events listed below",
            "event_aliases": {canonical: forms for canonical, forms in __import__("soccer_gmr_unseen_common").EVENT_ALIASES.items()},
            "accepted_worldcup_actions": sorted({row.get("normalized_action_type") for row in clean if row.get("normalized_action_type")}),
            "cleaning_rules": ["query event must parse to one event and match normalized action_type", "duration and every relevant window must be valid", "same normalized video/event/actor positive-negative conflicts are quarantined", "generic empty-window query conflicts with any same-video/event positive", "all rows in an exact normalized-video/query duplicate group are quarantined"],
            "label_source": "exist_label = bool(relevant_windows); moment is retained but does not override relevant_windows",
        }
        write_json(stage / "selection" / "semantic_rules.json", rules)

        group_specs: dict[str, dict[str, Any]] = {}
        for name, spec in ACTION_GROUPS.items():
            group_specs[name] = {"group": name, "axis": spec["axis"], "held_actions": spec["held_actions"], "held_combinations": []}
        for name, actions in COMPOSITION_ACTIONS.items():
            combos = sorted((action, team) for action, teams_for_action in composition_teams.get(name, {}).items() for team in teams_for_action)
            group_specs[name] = {"group": name, "axis": "action_actor_composition", "held_actions": actions, "held_combinations": [list(combo) for combo in combos], "held_teams_by_action": composition_teams.get(name, {})}
        write_json(stage / "selection" / "split_specs.json", {
            "selection_rule": "From clean train only, for each predeclared action retain action-team pairs with >=10 positive and >=10 negative rows; rank by (-min(pos, neg), -pos, -neg, team_name), take first eight.",
            "expected_plan_teams": EXPECTED_COMPOSITION_TEAMS,
            "observed_teams": composition_teams,
            "matches_expected_plan_teams": not candidate_differences,
            "differences_from_plan": candidate_differences,
            "groups": group_specs,
            "train_protocol": "Use only clean S+/S- rows; exclude every U query. For composition groups also exclude all generic-actor train queries for held actions.",
            "validation_protocol": "Keep all four quadrants in val and test; val_seen is exactly the S+/S- subset of val.",
        })

        group_statistics = {}
        for name, spec in group_specs.items():
            group_statistics[name] = build_group(stage, name, clean_by_split, spec["held_actions"], {tuple(pair) for pair in spec["held_combinations"]}, spec)

        protocol = {
            "release": "soccer_gmr_unseen_v1",
            "source": "data/label/Full/{train,val,test,full}.jsonl",
            "source_filter": {"dataset_source": WORLD_CUP_SOURCE, "excluded_sources": ["SoccerReplay1988", "sportsmoments"]},
            "split_policy": "Preserve source train/val/test; full.jsonl is used only to check equivalence to their union.",
            "cross_split_clip_overlap_policy": "Ignored as instructed; no competition-level repartition or temporal-overlap repair.",
            "label_policy": "Preserve source qid, vid, query, duration, relevant_windows and metadata. exist_label is derived from bool(relevant_windows); never auto-correct labels or windows.",
            "training": "Each group trains on S+/S- only. val_seen contains only S+/S- and is the only validation subset for model/checkpoint/threshold selection.",
            "heldout_composition_selection": "Clean train support only; no val/test statistics or model outputs used.",
            "checksums": "Not generated by request.",
            "manual_video_review_performed": False,
            "build_command": "python scripts/build_soccer_gmr_unseen.py --source data/label/Full --output data/release/soccer_gmr_unseen_v1",
            "validation_command": "python scripts/validate_soccer_gmr_unseen.py --source data/label/Full --release data/release/soccer_gmr_unseen_v1",
            "groups": group_specs,
        }
        write_json(stage / "construction_protocol.json", protocol)
        (stage / "README.md").write_text(make_readme(raw_stats, clean_stats, group_statistics), encoding="utf-8")
        if output_dir.exists():
            raise FileExistsError(f"Refusing to overwrite existing output: {output_dir}")
        os.replace(stage, output_dir)
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path("data/label/Full"))
    parser.add_argument("--output", type=Path, default=Path("data/release/soccer_gmr_unseen_v1"))
    args = parser.parse_args()
    try:
        build(args)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
    print(f"Built release at {args.output}")


if __name__ == "__main__":
    main()

